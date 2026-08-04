# -*- coding: utf-8 -*-
"""Phase 0a：構造的差分の機械集計
outputs/divergence/*.json の code フィールドをASTで解析し、タスクごとに
「8サンプル中何件がその特徴を持つか」を集計する。解釈・分類は行わない（事実の集計のみ）。

使い方:
  python analyze_divergence.py            # 全タスクを集計し、標準出力 + structural_diff.md に書き出す
"""
import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "outputs" / "divergence"


# ---------- AST からの事実抽出 ----------

def imported_root_names(tree):
    """`import X` / `import X as Y` で束縛される名前の集合（属性呼び出しの単純判定に使う）"""
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                bound = alias.asname or alias.name.split(".")[0]
                names.add(bound)
    return names


def call_label(call_node, imported_names):
    func = call_node.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        cur = func.value
        while isinstance(cur, ast.Attribute):
            cur = cur.value
        if isinstance(cur, ast.Name) and cur.id in imported_names:
            try:
                return ast.unparse(func)
            except Exception:
                return "." + func.attr
        return "." + func.attr
    try:
        return ast.unparse(func)
    except Exception:
        return "<call>"


def extract_facts(code: str):
    """1サンプル分のコードから各カテゴリの事実集合(set of str)を返す。
    パース不能なら (None, "PARSE_ERROR: ...") を返す。
    """
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return None, f"PARSE_ERROR: {e}"

    imported_names = imported_root_names(tree)

    imports = set()
    calls = set()
    open_encoding = set()
    exceptions = set()
    none_checks = set()
    output = set()

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            try:
                imports.add(ast.unparse(node))
            except Exception:
                pass

        if isinstance(node, ast.Call):
            label = call_label(node, imported_names)
            calls.add(label)

            if label == "open":
                enc_kw = next((kw for kw in node.keywords if kw.arg == "encoding"), None)
                if enc_kw is not None:
                    try:
                        val = ast.unparse(enc_kw.value)
                    except Exception:
                        val = "<非リテラル>"
                    open_encoding.add(f"encoding={val}")
                elif len(node.args) > 3:
                    try:
                        val = ast.unparse(node.args[3])
                    except Exception:
                        val = "<非リテラル>"
                    open_encoding.add(f"encoding={val} (位置引数)")
                else:
                    open_encoding.add("encoding指定なし")

            if label == ".get" and len(node.args) >= 2:
                none_checks.add(".get()に第2引数(デフォルト値)あり")

            if label == "print":
                output.add("print()呼び出しあり")

            if label == ".format":
                output.add(".format()呼び出しあり")

            if label == "round":
                if len(node.args) >= 2:
                    digit_node = node.args[1]
                    if isinstance(digit_node, ast.Constant):
                        digits = str(digit_node.value)
                    else:
                        try:
                            digits = f"非リテラル({ast.unparse(digit_node)})"
                        except Exception:
                            digits = "非リテラル"
                else:
                    ndigits_kw = next((kw for kw in node.keywords if kw.arg == "ndigits"), None)
                    if ndigits_kw is not None:
                        if isinstance(ndigits_kw.value, ast.Constant):
                            digits = str(ndigits_kw.value.value)
                        else:
                            digits = "非リテラル"
                    else:
                        digits = "引数なし"
                output.add(f"round()の桁数指定: {digits}")

        if isinstance(node, ast.Try):
            exceptions.add("try/exceptあり")
            for handler in node.handlers:
                if handler.type is None:
                    exceptions.add("except: (bare except)")
                elif isinstance(handler.type, ast.Tuple):
                    for elt in handler.type.elts:
                        try:
                            exceptions.add(f"except: {ast.unparse(elt)}")
                        except Exception:
                            pass
                else:
                    try:
                        exceptions.add(f"except: {ast.unparse(handler.type)}")
                    except Exception:
                        pass

        if isinstance(node, ast.Compare):
            for op, comparator in zip(node.ops, node.comparators):
                if isinstance(op, (ast.Is, ast.IsNot, ast.Eq, ast.NotEq)) and \
                        isinstance(comparator, ast.Constant) and comparator.value is None:
                    none_checks.add("Noneとの比較 (is None / == None 等)")
            if isinstance(node.left, ast.Constant) and node.left.value is None:
                none_checks.add("Noneとの比較 (is None / == None 等)")

        if isinstance(node, ast.JoinedStr):
            output.add("f-string使用")

        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod) and \
                isinstance(node.left, ast.Constant) and isinstance(node.left.value, str):
            output.add("%文字列フォーマット使用")

    return {
        "imports": imports,
        "calls": calls,
        "open_encoding": open_encoding,
        "exceptions": exceptions,
        "none_checks": none_checks,
        "output": output,
    }, None


# ---------- 集計・Markdown整形 ----------

def make_table(category_label, per_sample_sets, n_total):
    counts = {}
    for facts in per_sample_sets:
        for f in facts:
            counts[f] = counts.get(f, 0) + 1
    lines = [f"### {category_label}", "", "| 特徴 | 件数(/{}件) |".format(n_total), "|---|---|"]
    if not counts:
        lines.append("| (該当なし) | - |")
    else:
        for label, cnt in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
            lines.append(f"| `{label}` | {cnt} |")
    lines.append("")
    return "\n".join(lines)


CATEGORY_TITLES = [
    ("imports", "importしているモジュール"),
    ("calls", "呼んでいる関数・メソッド"),
    ("open_encoding", "open()のencoding引数"),
    ("exceptions", "try/exceptの有無と捕捉例外"),
    ("none_checks", "欠損・Noneのチェック"),
    ("output", "出力方法（print / f-string / round桁数など）"),
]


def analyze_task(task_id, samples):
    """samples: list of code strings"""
    per_category = {key: [] for key, _ in CATEGORY_TITLES}
    parse_errors = []
    n = len(samples)
    for idx, code in enumerate(samples, start=1):
        facts, err = extract_facts(code)
        if err is not None:
            parse_errors.append(f"sample{idx:02d}: {err}")
            for key, _ in CATEGORY_TITLES:
                per_category[key].append(set())
            continue
        for key, _ in CATEGORY_TITLES:
            per_category[key].append(facts[key])

    lines = [f"## {task_id}", ""]
    if parse_errors:
        lines.append(f"⚠ 構文解析に失敗したサンプル: {len(parse_errors)}/{n}件")
        for pe in parse_errors:
            lines.append(f"- {pe}")
        lines.append("")
    for key, title in CATEGORY_TITLES:
        lines.append(make_table(title, per_category[key], n))
    return "\n".join(lines)


def main():
    files = sorted(OUT_DIR.glob("task*__*.json"))
    if not files:
        sys.exit("outputs/divergence/ にサンプルがありません。先に run_divergence.py run を実行。")

    by_task = {}
    for p in files:
        d = json.loads(p.read_text(encoding="utf-8"))
        by_task.setdefault(d["task"], []).append(d["code"])

    out_sections = ["# 分岐分析：構造的差分の機械集計", "",
                     "各カテゴリは事実の集計のみ（解釈・分類は annotation_sheet.csv 側で行う）。", ""]
    for task_id in sorted(by_task):
        out_sections.append(analyze_task(task_id, by_task[task_id]))

    text = "\n".join(out_sections)
    out_path = OUT_DIR / "structural_diff.md"
    out_path.write_text(text, encoding="utf-8")
    print(text)
    print(f"\n書き出し: {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
