# -*- coding: utf-8 -*-
"""
前提監視（Premise Guard）最小プロトタイプ
=====================================================================
研究企画「AIの前提を可視化し、前提が崩れたら設計に立ち返る仕組み」の
中核制御ループを、LLM 無し（決定的なモック）で実証するデモ。

実証したいこと：
  AIは与えられた前提に忠実に作業するため、前提が誤っていても
  気づかず誤った成果物を作り続ける（baseline）。
  これに対し、(1)仮定台帳に前提を明示し、(2)各ステップ前に証拠と突合して
  前提違反を検知し、(3)違反なら作業を止めて設計に立ち返る（guard）と、
  早期に誤りを捕まえ、下流の手戻りを減らせる。

ここでは「機構が成立するか」を決定的に示すのが目的（LLMの賢さ依存を排除）。
実タスク版は check/elicit を Bedrock 呼び出しに差し替えるだけ（末尾の注記参照）。
実行: python premise_guard_demo.py
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable


# ── データモデル ───────────────────────────────
@dataclass
class Assumption:
    id: str
    statement: str                       # 人間可読な前提（＝可視化対象）
    check: Callable[[dict], bool]        # check(evidence) -> 前提が成り立つか

@dataclass
class Step:
    id: str
    desc: str
    needs: list[str]                     # このステップが依拠する前提ID（＝前提→成果物リンク）

@dataclass
class Task:
    name: str
    goal: str
    assumptions: list[Assumption]
    steps: list[Step]
    evidence: dict                       # 実環境の事実（前提を裏切りうる）


# ── 可視化（仮定台帳と前提→成果物リンク） ──────────────
def render_ledger(task: Task) -> str:
    by_assum = {a.id: [] for a in task.assumptions}
    for s in task.steps:
        for aid in s.needs:
            by_assum.setdefault(aid, []).append(s.id)
    lines = [f"  [仮定台帳] {task.name} / 目的: {task.goal}"]
    for a in task.assumptions:
        supports = ", ".join(by_assum.get(a.id, [])) or "(未使用)"
        lines.append(f"   - {a.id}: {a.statement}  → 依存ステップ: {supports}")
    return "\n".join(lines)


# ── 実行モード ───────────────────────────────
def run_baseline(task: Task) -> dict:
    """前提を疑わず全ステップを実行。最後に成果物が正しいか判定。"""
    produced = []
    for s in task.steps:
        produced.append(s.id)             # 前提に忠実に作業を積む
    # 最終検証：依拠した前提が一つでも崩れていれば成果物は誤り
    used = {aid for s in task.steps for aid in s.needs}
    violated = [a for a in task.assumptions if a.id in used and not a.check(task.evidence)]
    correct = len(violated) == 0
    return {
        "mode": "baseline", "produced_steps": produced,
        "wasted_steps": 0 if correct else len(produced),   # 誤前提なら全手戻り
        "detected": False, "detect_step": None,
        "violated": [a.id for a in violated], "final_correct": correct,
    }

def run_guard(task: Task) -> dict:
    """各ステップ前に、必要な前提を証拠と突合。違反なら設計回帰（停止）。"""
    produced = []
    for i, s in enumerate(task.steps):
        # 前提モニタ：このステップが依拠する前提をチェック
        for aid in s.needs:
            a = next(x for x in task.assumptions if x.id == aid)
            if not a.check(task.evidence):
                return {                   # 設計回帰：崩れた前提を局所化して停止
                    "mode": "guard", "produced_steps": produced,
                    "wasted_steps": len(produced),     # 違反検知までの手戻りのみ
                    "detected": True, "detect_step": s.id,
                    "violated": [aid], "final_correct": False,
                    "message": f"前提違反 {aid}「{a.statement}」を {s.id} 直前で検知 → 設計に立ち返る",
                }
        produced.append(s.id)
    return {
        "mode": "guard", "produced_steps": produced, "wasted_steps": 0,
        "detected": False, "detect_step": None, "violated": [], "final_correct": True,
    }


# ── シナリオ（共通タスク：ユーザ記録から平均年齢を計算） ─────
def make_task(evidence: dict) -> Task:
    A = [
        Assumption("A1", "レコードに 'age' フィールドが存在する",
                   lambda ev: ev.get("field_name") == "age"),
        Assumption("A2", "'age' は整数（年齢・年単位）",
                   lambda ev: ev.get("age_type") == "int_years"),
    ]
    S = [
        Step("S1", "記録を読み込む",            needs=["A1"]),
        Step("S2", "age を整数として解析",       needs=["A1", "A2"]),
        Step("S3", "平均を計算",                needs=[]),
        Step("S4", "レポートを整形",            needs=[]),
    ]
    return Task("平均年齢の計算", "ユーザ記録から平均年齢を出す", A, S, evidence)

SCENARIOS = {
    "正常（前提が成立）":        {"field_name": "age",       "age_type": "int_years"},
    "誤前提：型が違う(文字列)":  {"field_name": "age",       "age_type": "string_words"},
    "誤前提：フィールド名が違う": {"field_name": "age_years", "age_type": "int_years"},
    "誤前提：単位が違う(月)":    {"field_name": "age",       "age_type": "int_months"},
}


def main():
    print("=" * 70)
    print("前提監視（Premise Guard）最小プロトタイプ — baseline vs guard")
    print("=" * 70)
    rows = []
    for name, ev in SCENARIOS.items():
        task = make_task(ev)
        print(f"\n■ シナリオ: {name}")
        print(render_ledger(task))
        b = run_baseline(task)
        g = run_guard(task)
        if g.get("message"):
            print("  [guard]", g["message"])
        print(f"  baseline: 成果物={b['produced_steps']} 手戻り={b['wasted_steps']} "
              f"検知={b['detected']} 最終正しい={b['final_correct']}")
        print(f"  guard   : 成果物={g['produced_steps']} 手戻り={g['wasted_steps']} "
              f"検知={g['detected']}({g['detect_step']}) 最終正しい={g['final_correct']}")
        rows.append((name, b, g))

    # ── 比較サマリ ──
    print("\n" + "=" * 70)
    print("比較サマリ（手戻りステップ数 = 誤前提の上で積んだ無駄な作業）")
    print(f"{'シナリオ':24} {'baseline手戻り':>14} {'guard手戻り':>12} {'guard検知点':>12}")
    saved_total = 0
    for name, b, g in rows:
        saved_total += (b["wasted_steps"] - g["wasted_steps"])
        print(f"{name:24} {b['wasted_steps']:>14} {g['wasted_steps']:>12} "
              f"{str(g['detect_step']):>12}")
    print(f"\n→ guard により削減できた手戻り合計: {saved_total} ステップ")
    print("→ 正常シナリオでは guard も停止せず（過剰中断なし）= 前提が成立する時は邪魔しない")

    print("""
注記（実タスク版への拡張）:
  - Assumption.check を Bedrock 呼び出しに差し替え＝「証拠(実データ/実行結果/取得情報)が
    前提に反するか」をLLMに判定させる（信頼度で起動閾値＝過剰中断を抑制：RQ3）。
  - 仮定台帳の生成も、タスク記述からLLMに前提を列挙させる（elicit）。
  - 設計回帰は人間への確認（HITL: pause→再確認→台帳更新→resume）に接続。
  - 本デモは制御ループが機能することの決定的確認。LLMの賢さに依存しない骨格。
""")


if __name__ == "__main__":
    main()
