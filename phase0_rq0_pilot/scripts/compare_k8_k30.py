# -*- coding: utf-8 -*-
"""Phase 0a：k=8時点とk=30時点の構造的差分（structural_diff_k8.md / structural_diff.md）の対比。

事実の対比のみを行う（解釈・分類は行わない）。annotation_sheet.csv には触れない。

出力:
  1. k=8では8/8だったが、k=30では割れた特徴の一覧
  2. k=30で新たに現れた特徴（k=8のどのサンプルにも無かったもの）
  3. 各特徴の件数の変化（k=8時点の件数 → k=30時点の件数、両方に存在する特徴のみ）

使い方:
  python compare_k8_k30.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "outputs" / "divergence"
K8_PATH = OUT_DIR / "structural_diff_k8.md"
K30_PATH = OUT_DIR / "structural_diff.md"
OUT_PATH = OUT_DIR / "k8_vs_k30.md"

TASK_RE = re.compile(r"^## (\S+)\s*$")
CATEGORY_RE = re.compile(r"^### (.+?)\s*$")
ROW_RE = re.compile(r"^\| `(.+?)` \| (\d+)/(\d+) \| \[.*?\] \|\s*$")
PARSE_ERROR_RE = re.compile(r"^⚠ 構文解析に失敗したサンプル: (\d+/\d+件)\s*$")


def parse_structural_diff(path):
    """戻り値: {task_id: {category_title: {feature_label: (count, total)}}}, {task_id: parse_error_note or None}"""
    tasks = {}
    parse_notes = {}
    task_id = None
    category = None
    for line in path.read_text(encoding="utf-8").splitlines():
        m_task = TASK_RE.match(line)
        if m_task:
            task_id = m_task.group(1)
            tasks[task_id] = {}
            parse_notes[task_id] = None
            category = None
            continue
        if task_id is None:
            continue
        m_err = PARSE_ERROR_RE.match(line)
        if m_err:
            parse_notes[task_id] = m_err.group(1)
            continue
        m_cat = CATEGORY_RE.match(line)
        if m_cat:
            category = m_cat.group(1)
            tasks[task_id].setdefault(category, {})
            continue
        m_row = ROW_RE.match(line)
        if m_row and category is not None:
            label, count, total = m_row.group(1), int(m_row.group(2)), int(m_row.group(3))
            tasks[task_id][category][label] = (count, total)
    return tasks, parse_notes


def fmt_ratio(pair):
    if pair is None:
        return "-"
    count, total = pair
    return f"{count}/{total}"


def build_task_section(task_id, k8_categories, k30_categories, k30_parse_note):
    lines = [f"## {task_id}", ""]
    if k30_parse_note:
        lines.append(f"（参考: k=30側で構文解析に失敗したサンプルが{k30_parse_note}ある）")
        lines.append("")

    all_categories = sorted(set(k8_categories) | set(k30_categories))

    # 1. k=8で8/8だったが、k=30では割れた特徴
    split_rows = []
    for cat in all_categories:
        k8_feats = k8_categories.get(cat, {})
        k30_feats = k30_categories.get(cat, {})
        for label, (count8, total8) in k8_feats.items():
            if count8 != total8:
                continue  # k=8時点で8/8ではない
            k30_pair = k30_feats.get(label)
            if k30_pair is not None and k30_pair[0] == k30_pair[1]:
                continue  # k=30でも全件一致のまま（割れていない）
            split_rows.append((cat, label, (count8, total8), k30_pair))

    lines.append("### 1. k=8では8/8だったが、k=30では割れた特徴")
    lines.append("")
    lines.append("| カテゴリ | 特徴 | k=8 | k=30 |")
    lines.append("|---|---|---|---|")
    if not split_rows:
        lines.append("| (該当なし) | - | - | - |")
    else:
        for cat, label, k8_pair, k30_pair in sorted(split_rows, key=lambda r: (r[0], r[1])):
            lines.append(f"| {cat} | `{label}` | {fmt_ratio(k8_pair)} | {fmt_ratio(k30_pair)} |")
    lines.append("")

    # 2. k=30で新たに現れた特徴（k=8のどのサンプルにも無かったもの）
    new_rows = []
    for cat in all_categories:
        k8_feats = k8_categories.get(cat, {})
        k30_feats = k30_categories.get(cat, {})
        for label, pair in k30_feats.items():
            if label not in k8_feats:
                new_rows.append((cat, label, pair))

    lines.append("### 2. k=30で新たに現れた特徴（k=8のどのサンプルにも無かったもの）")
    lines.append("")
    lines.append("| カテゴリ | 特徴 | k=30 |")
    lines.append("|---|---|---|")
    if not new_rows:
        lines.append("| (該当なし) | - | - |")
    else:
        for cat, label, pair in sorted(new_rows, key=lambda r: (r[0], r[1])):
            lines.append(f"| {cat} | `{label}` | {fmt_ratio(pair)} |")
    lines.append("")

    # 3. 各特徴の件数の変化（k=8とk=30の両方に存在する特徴のみ）
    change_rows = []
    for cat in all_categories:
        k8_feats = k8_categories.get(cat, {})
        k30_feats = k30_categories.get(cat, {})
        for label, k8_pair in k8_feats.items():
            k30_pair = k30_feats.get(label)
            if k30_pair is None:
                continue
            change_rows.append((cat, label, k8_pair, k30_pair))

    lines.append("### 3. 各特徴の件数の変化（k=8・k=30の両方に存在する特徴）")
    lines.append("")
    lines.append("| カテゴリ | 特徴 | k=8 | k=30 |")
    lines.append("|---|---|---|---|")
    if not change_rows:
        lines.append("| (該当なし) | - | - | - |")
    else:
        for cat, label, k8_pair, k30_pair in sorted(change_rows, key=lambda r: (r[0], r[1])):
            lines.append(f"| {cat} | `{label}` | {fmt_ratio(k8_pair)} | {fmt_ratio(k30_pair)} |")
    lines.append("")

    return "\n".join(lines)


def main():
    if not K8_PATH.exists():
        sys.exit(f"{K8_PATH} が見つかりません。")
    if not K30_PATH.exists():
        sys.exit(f"{K30_PATH} が見つかりません。")

    k8_tasks, _ = parse_structural_diff(K8_PATH)
    k30_tasks, k30_parse_notes = parse_structural_diff(K30_PATH)

    all_task_ids = sorted(set(k8_tasks) | set(k30_tasks))

    out_sections = [
        "# k=8 vs k=30 構造的差分の対比",
        "",
        f"`{K8_PATH.name}`（k=8）と `{K30_PATH.name}`（k=30）を機械的に対比した結果。"
        "事実の対比のみ（解釈・分類は annotation_sheet.csv 側で行う）。",
        "",
    ]
    for task_id in all_task_ids:
        out_sections.append(build_task_section(
            task_id,
            k8_tasks.get(task_id, {}),
            k30_tasks.get(task_id, {}),
            k30_parse_notes.get(task_id),
        ))

    text = "\n".join(out_sections)
    OUT_PATH.write_text(text, encoding="utf-8")
    print(text)
    print(f"\n書き出し: {OUT_PATH}", file=sys.stderr)


if __name__ == "__main__":
    main()
