# -*- coding: utf-8 -*-
"""Phase 0a：分岐分析（divergence analysis）
同一タスクを同一モデルにN回コード生成させ、実装が分岐する箇所＝暗黙前提を特定する。
※生成させるのはコードであり前提の列挙ではない（プロトコル§3手順0）。

使い方:
  python run_divergence.py run [--reps 8] [--temp 0.8]   # サンプル生成
  python run_divergence.py digest                        # タスク別ダイジェストmd＋注釈CSV生成
環境変数: run_elicit.py と同じ（BEDROCK_MODEL_IDS等）。MOCK=1 でAPI不要の動作確認。
"""
import argparse, csv, json, os, re, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TASKS_DIR = ROOT / "tasks"
OUT_DIR = ROOT / "outputs" / "divergence"

PROMPT = """次のタスクを満たすPythonコードを書いてください。
コードのみを出力し、説明文は不要です。1つのコードブロックにまとめてください。

## タスク
{TASK_DESCRIPTION}
"""

MOCK_SAMPLES = [
    "import json\nrecords = json.load(open('data.json'))\nvals = [r['age'] for r in records]\nprint(sum(vals)/len(vals))\n",
    "import json\nrecords = json.load(open('data.json', encoding='utf-8'))\nvals = [r.get('age') for r in records if r.get('age') is not None]\nprint(round(sum(vals)/len(vals), 1))\n",
    "import json, sys\ntry:\n    records = json.load(open('data.json'))\nexcept FileNotFoundError:\n    sys.exit('no data')\nvals = [int(r['age']) for r in records]\nprint(sum(vals)//len(vals))\n",
]


def extract_code(text: str):
    m = re.search(r"```(?:python)?\s*(.*?)```", text, re.S)
    return (m.group(1) if m else text).strip()


def get_providers():
    if os.environ.get("MOCK") == "1":
        counter = {"i": 0}
        def mock(prompt, temp):
            counter["i"] += 1
            return "```python\n" + MOCK_SAMPLES[counter["i"] % len(MOCK_SAMPLES)] + "```"
        return {"mock_model": mock}
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import run_elicit
    return run_elicit.PROVIDERS


def cmd_run(args):
    providers = get_providers()
    if not providers:
        sys.exit("プロバイダ未設定（BEDROCK_MODEL_IDS等。動作確認は MOCK=1）")
    tasks = [json.loads(p.read_text(encoding="utf-8"))
             for p in sorted(TASKS_DIR.glob("task*.json"))]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    n_total = len(tasks) * len(providers) * args.reps
    print(f"tasks={len(tasks)} models={list(providers)} reps={args.reps} -> {n_total} calls")
    done = 0
    for task in tasks:
        prompt = PROMPT.replace("{TASK_DESCRIPTION}", task["description"])
        for mname, fn in providers.items():
            for rep in range(1, args.reps + 1):
                fpath = OUT_DIR / f"{task['id']}__{mname}__sample{rep:02d}.json"
                if fpath.exists():
                    done += 1
                    continue
                try:
                    raw = fn(prompt, args.temp)
                except Exception as e:
                    print(f"[失敗] {fpath.name}: {e}")
                    continue
                code = extract_code(raw)
                fpath.write_text(json.dumps({
                    "task": task["id"], "model": mname, "sample": rep,
                    "temperature": args.temp,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "raw": raw, "code": code,
                }, ensure_ascii=False, indent=2), encoding="utf-8")
                done += 1
                print(f"[{done}/{n_total}] {fpath.name} ({len(code.splitlines())}行)")
                time.sleep(1)
    print("完了。次: python scripts/run_divergence.py digest")


def cmd_digest(args):
    files = sorted(OUT_DIR.glob("*.json"))
    if not files:
        sys.exit("outputs/divergence/ にサンプルがありません。先に run を実行。")
    by_task = {}
    for p in files:
        d = json.loads(p.read_text(encoding="utf-8"))
        by_task.setdefault(d["task"], []).append(d)
    for task, samples in by_task.items():
        lines = [f"# 分岐分析ダイジェスト: {task}", "",
                 "各サンプルを見比べ、実装が割れた箇所を annotation_sheet.csv に記録する。",
                 "観点例: 欠損の扱い／丸め／エンコーディング／エラー処理／出力形式／タイムゾーン", ""]
        for d in sorted(samples, key=lambda x: (x["model"], x["sample"])):
            lines += [f"## {d['model']} / sample {d['sample']:02d}",
                      "```python", d["code"], "```", ""]
        out = OUT_DIR / f"digest_{task}.md"
        out.write_text("\n".join(lines), encoding="utf-8")
        print(f"{out} ({len(samples)}サンプル)")
    sheet = OUT_DIR / "annotation_sheet.csv"
    if not sheet.exists():
        with open(sheet, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["task", "divergence_id", "description",
                        "assumption_statement", "alternatives",
                        "type_id", "importance", "monitorable",
                        "n_samples_affected", "note"])
            w.writerow(["task01", "D1", "（例）欠損ageの扱いがスキップ/エラー/0埋めに分岐",
                        "欠損ageのレコードは集計から除外してよい",
                        "全レコードにageが存在する前提で処理する / 欠損を0として扱う",
                        "IN-5", "minor", "yes", "5/8", "（例）判定理由をここに書く"])
        print(f"{sheet} を生成（記入例つき）。taxonomy_draft.md の型IDで分類する。")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_run = sub.add_parser("run")
    p_run.add_argument("--reps", type=int, default=8)
    p_run.add_argument("--temp", type=float, default=0.8)
    sub.add_parser("digest")
    args = ap.parse_args()
    (cmd_run if args.cmd == "run" else cmd_digest)(args)


if __name__ == "__main__":
    main()
