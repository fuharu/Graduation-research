# -*- coding: utf-8 -*-
"""RQ0パイロット：マッチングシート生成と採点
使い方:
  python score_coverage.py make-sheet   # outputs/elicit/*.json -> outputs/matching_sheet.csv
  （人手で matched_gold_id / wrong 列を記入。プロトコル§4の判定テストに従う）
  python score_coverage.py score        # シート＋gold -> outputs/rq0_results.md
"""
import csv, json, random, statistics, sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ELICIT_DIR = ROOT / "outputs" / "elicit"
SHEET = ROOT / "outputs" / "matching_sheet.csv"
RESULT = ROOT / "outputs" / "rq0_results.md"


def load_gold():
    gold = {}
    for p in sorted((ROOT / "tasks").glob("task*.json")):
        t = json.loads(p.read_text(encoding="utf-8"))
        gold[t["id"]] = t["gold"]
    return gold


def make_sheet():
    rows = []
    for p in sorted(ELICIT_DIR.glob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        run_id = p.stem
        if not d.get("assumptions"):
            rows.append([run_id, d["task"], d["prompt"], d["model"], d["rep"],
                         0, "(PARSE_FAIL)", "", "", "", ""])
            continue
        for i, a in enumerate(d["assumptions"]):
            rows.append([run_id, d["task"], d["prompt"], d["model"], d["rep"],
                         i, a["statement"], a.get("importance", "?"), "", "", ""])
    SHEET.parent.mkdir(parents=True, exist_ok=True)
    with open(SHEET, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["run_id", "task", "prompt", "model", "rep", "idx",
                    "statement", "importance",
                    "matched_gold_id", "wrong", "note"])
        w.writerows(rows)
    print(f"{SHEET} を生成（{len(rows)}行）。matched_gold_id列を記入してください。")
    print("記入規則: 一致するgoldのID（複数はセミコロン区切り G1;G2）／一致なしは空欄／"
          "タスク記述と矛盾する誤前提は wrong 列に 1")


def bootstrap_ci(values, n=10000, seed=42):
    if not values:
        return (float("nan"), float("nan"))
    rng = random.Random(seed)
    meds = []
    for _ in range(n):
        sample = [rng.choice(values) for _ in values]
        meds.append(statistics.median(sample))
    meds.sort()
    return meds[int(0.025 * n)], meds[int(0.975 * n)]


def score():
    gold = load_gold()
    runs = defaultdict(lambda: {"covered": set(), "n_elicited": 0,
                                "n_matched": 0, "n_wrong": 0})
    meta = {}
    with open(SHEET, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            key = r["run_id"]
            meta[key] = (r["task"], r["prompt"], r["model"])
            if r["statement"] == "(PARSE_FAIL)":
                continue
            runs[key]["n_elicited"] += 1
            ids = [g.strip() for g in r["matched_gold_id"].split(";") if g.strip()]
            if ids:
                runs[key]["covered"].update(ids)
                runs[key]["n_matched"] += 1
            if r["wrong"].strip() == "1":
                runs[key]["n_wrong"] += 1

    per_run = []
    for key, v in runs.items():
        task, prompt, model = meta[key]
        g = gold.get(task, [])
        crit = {x["id"] for x in g if x["importance"] == "critical"}
        allg = {x["id"] for x in g}
        per_run.append({
            "task": task, "prompt": prompt, "model": model,
            "crit_recall": len(v["covered"] & crit) / len(crit) if crit else float("nan"),
            "recall": len(v["covered"] & allg) / len(allg) if allg else float("nan"),
            "precision": v["n_matched"] / v["n_elicited"] if v["n_elicited"] else 0.0,
            "wrong_rate": v["n_wrong"] / v["n_elicited"] if v["n_elicited"] else 0.0,
        })

    # セル（prompt×model）ごと：タスク内で反復を中央値集約→タスク横断で中央値＋CI
    lines = ["# RQ0 採点結果", "",
             "| prompt | model | critical再現率(中央値) | 95%CI | 全体再現率 | 適合率 | wrong率 |",
             "|---|---|---|---|---|---|---|"]
    cells = defaultdict(lambda: defaultdict(list))
    for r in per_run:
        cells[(r["prompt"], r["model"])][r["task"]].append(r)
    best = None
    for (prompt, model), by_task in sorted(cells.items()):
        task_meds = [statistics.median(x["crit_recall"] for x in rs)
                     for rs in by_task.values()]
        med = statistics.median(task_meds)
        lo, hi = bootstrap_ci(task_meds)
        rec = statistics.median(statistics.median(x["recall"] for x in rs)
                                for rs in by_task.values())
        prec = statistics.median(statistics.median(x["precision"] for x in rs)
                                 for rs in by_task.values())
        wr = statistics.median(statistics.median(x["wrong_rate"] for x in rs)
                               for rs in by_task.values())
        lines.append(f"| {prompt} | {model} | {med:.2f} | [{lo:.2f},{hi:.2f}] "
                     f"| {rec:.2f} | {prec:.2f} | {wr:.2f} |")
        if best is None or med > best[0]:
            best = (med, prompt, model)

    lines += ["", f"**最良セル**: {best[1]} × {best[2]} critical再現率={best[0]:.2f}", "",
              "## 分岐判定（プロトコル§6）",
              f"- {'≥0.70 → 続行' if best[0] >= 0.70 else '0.50–0.70 → ハイブリッド化' if best[0] >= 0.50 else '<0.50 → 台帳は人間付与に設計変更・教員と相談'}",
              "",
              "注意: タスク3件のためCIは非常に広い。分岐判定は中央値で行い、CIは参考値として報告。"]
    RESULT.write_text("\n".join(lines), encoding="utf-8")
    print(RESULT)
    print("\n".join(lines[-8:]))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "make-sheet":
        make_sheet()
    elif cmd == "score":
        score()
    else:
        sys.exit(__doc__)
