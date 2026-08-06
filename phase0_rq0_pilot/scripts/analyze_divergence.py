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

# キーワード引数を集計する対象の関数・メソッド名（bareのNameまたは属性呼び出しのattr名で判定）
TARGET_KW_FUNCS = [
    "read_csv", "to_csv", "to_datetime", "groupby", "sort_values", "open",
    "fillna", "dropna", "astype", "round", "merge", "mkdir", "move",
]

# 位置引数を集計する対象の関数・メソッド名
TARGET_POS_FUNCS = [
    "to_period", "groupby", "sort_values", "read_csv", "to_csv", "to_datetime", "astype",
]

# 欠損値処理として検出する呼び出し名（pandas系）
MISSING_VALUE_CALL_NAMES = {"dropna", "fillna", "isna", "notna"}


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


def import_module_roots(tree):
    """`import X` / `import X as Y` の 束縛名 -> 実際のモジュールルート名 の対応
    （`import requests as req` のようなエイリアス越しの判定に使う）
    """
    mapping = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                bound = alias.asname or alias.name.split(".")[0]
                mapping[bound] = alias.name.split(".")[0]
    return mapping


def defined_function_names(tree):
    """コード内で `def` により定義された関数・メソッド名の集合（自作関数の呼び出し除外に使う）"""
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            names.add(node.name)
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


def call_base_name(call_node):
    """呼び出しの「末尾の名前」（Nameならその名前、属性アクセスならattr名）"""
    func = call_node.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def unparse_safe(node):
    try:
        return ast.unparse(node)
    except Exception:
        return "<非リテラル>"


def subscript_string_value(node):
    """Subscriptノードの添字が文字列リテラルならその値を返す（Python 3.8以前のast.Indexラップにも対応）"""
    s = node.slice
    if s.__class__.__name__ == "Index":
        s = s.value
    if isinstance(s, ast.Constant) and isinstance(s.value, str):
        return s.value
    return None


def match_kw_target(call_node, base, module_roots):
    """この呼び出しがキーワード引数集計の対象（TARGET_KW_FUNCS / requests.get）かどうかを判定し、
    対象なら表示用のラベル文字列を返す。対象外なら None。
    """
    func = call_node.func
    if base == "get" and isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name) \
            and module_roots.get(func.value.id) == "requests":
        return "requests.get"
    if base in TARGET_KW_FUNCS:
        return base
    return None


def extract_facts(code: str):
    """1サンプル分のコードから各カテゴリの事実集合(set of str)を返す。
    パース不能なら (None, "PARSE_ERROR: ...") を返す。
    """
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return None, f"PARSE_ERROR: {e}"

    imported_names = imported_root_names(tree)
    module_roots = import_module_roots(tree)
    defined_names = defined_function_names(tree)

    imports = set()
    calls = set()
    open_encoding = set()
    exceptions = set()
    none_checks = set()
    output = set()
    kwarg_calls = []  # list of (target_label, {kwarg_name: value_str})
    kwarg_noargs = set()  # 追跡対象の関数が引数なしで呼ばれた場合の "target(引数なし)"
    positional_args = set()  # 追跡対象の関数の位置引数（TARGET_POS_FUNCS）
    subscript_literals = set()  # 添字アクセスの文字列リテラル（読み書き問わず）
    assigned_columns = set()  # 代入（Storeコンテキスト）で作られる列名リテラル

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            try:
                imports.add(ast.unparse(node))
            except Exception:
                pass

        if isinstance(node, ast.Call):
            func = node.func
            is_user_defined = isinstance(func, ast.Name) and func.id in defined_names
            if is_user_defined:
                continue

            label = call_label(node, imported_names)
            calls.add(label)
            base = call_base_name(node)

            if label == "open":
                enc_kw = next((kw for kw in node.keywords if kw.arg == "encoding"), None)
                if enc_kw is not None:
                    val = unparse_safe(enc_kw.value)
                    open_encoding.add(f"encoding={val}")
                elif len(node.args) > 3:
                    val = unparse_safe(node.args[3])
                    open_encoding.add(f"encoding={val} (位置引数)")
                else:
                    open_encoding.add("encoding指定なし")

            if label == ".get" and len(node.args) >= 2:
                none_checks.add(".get()に第2引数(デフォルト値)あり")

            if base in MISSING_VALUE_CALL_NAMES:
                none_checks.add(f"{base}()呼び出しあり")

            for kw in node.keywords:
                if kw.arg == "errors" and isinstance(kw.value, ast.Constant) and kw.value.value == "coerce":
                    none_checks.add("errors='coerce'使用")

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
                        digits = f"非リテラル({unparse_safe(digit_node)})"
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

            kw_target = match_kw_target(node, base, module_roots)
            if kw_target is not None:
                kwdict = {kw.arg: unparse_safe(kw.value) for kw in node.keywords if kw.arg is not None}
                kwarg_calls.append((kw_target, kwdict))

            is_noarg_call = not node.args and not node.keywords
            if is_noarg_call and kw_target is not None:
                kwarg_noargs.add(f"{kw_target}(引数なし)")

            if base in TARGET_POS_FUNCS:
                if node.args:
                    args_repr = ", ".join(unparse_safe(a) for a in node.args)
                    positional_args.add(f"{base}({args_repr})")
                elif not node.keywords:
                    positional_args.add(f"{base}(引数なし)")

        if isinstance(node, ast.Subscript):
            key = subscript_string_value(node)
            if key is not None:
                subscript_literals.add(repr(key))
                if isinstance(node.ctx, ast.Store):
                    assigned_columns.add(repr(key))

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
        "kwarg_calls": kwarg_calls,
        "kwarg_noargs": kwarg_noargs,
        "positional_args": positional_args,
        "subscript_literals": subscript_literals,
        "assigned_columns": assigned_columns,
    }, None


# ---------- キーワード引数の集計（タスク単位でサンプル横断が必要なため別関数） ----------

def build_kwarg_fact_sets(per_sample_kwarg_calls):
    """per_sample_kwarg_calls: サンプルごとの [(target_label, {kwname: valstr}), ...] のリスト
    戻り値: サンプルごとの表示用事実集合(set of str)のリスト。
    「対象関数がそのサンプルで呼ばれていない」場合はそのサンプルでは何も追加しない
    （「指定なし」は「呼ばれてはいるが当該キーワードが無い」ことを意味する）。
    """
    target_kwnames = {}
    for sample_calls in per_sample_kwarg_calls:
        for target, kwdict in sample_calls:
            target_kwnames.setdefault(target, set()).update(kwdict.keys())

    fact_sets = []
    for sample_calls in per_sample_kwarg_calls:
        calls_by_target = {}
        for target, kwdict in sample_calls:
            calls_by_target.setdefault(target, []).append(kwdict)

        facts = set()
        for target, kwnames in target_kwnames.items():
            calls = calls_by_target.get(target)
            if not calls:
                continue
            for kwname in kwnames:
                present_values = {c[kwname] for c in calls if kwname in c}
                if present_values:
                    for v in present_values:
                        facts.add(f"{target}({kwname}={v})")
                else:
                    facts.add(f"{target}({kwname}指定なし)")
        fact_sets.append(facts)
    return fact_sets


# ---------- 集計・Markdown整形 ----------

def make_table(category_label, per_sample_sets, n_total):
    counts = {}
    sample_indices = {}
    for idx, facts in enumerate(per_sample_sets, start=1):
        for f in facts:
            counts[f] = counts.get(f, 0) + 1
            sample_indices.setdefault(f, []).append(idx)
    lines = [f"### {category_label}", "", "| 特徴 | 件数 | サンプル番号 |", "|---|---|---|"]
    if not counts:
        lines.append("| (該当なし) | - | - |")
    else:
        for label, cnt in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
            samples_str = ",".join(str(i) for i in sample_indices[label])
            lines.append(f"| `{label}` | {cnt}/{n_total} | [{samples_str}] |")
    lines.append("")
    return "\n".join(lines)


CATEGORY_TITLES = [
    ("imports", "importしているモジュール"),
    ("calls", "呼んでいる関数・メソッド（自作関数を除く）"),
    ("positional_args", "主要な呼び出しの位置引数"),
    ("kwargs", "主要な関数呼び出しのキーワード引数"),
    ("subscript_literals", "添字アクセスの文字列リテラル"),
    ("assigned_columns", "代入で作られる列名のリテラル"),
    ("open_encoding", "open()のencoding引数"),
    ("exceptions", "try/exceptの有無と捕捉例外"),
    ("none_checks", "欠損・Noneのチェック"),
    ("output", "出力方法（print / f-string / round桁数など）"),
]


def analyze_task(task_id, samples):
    """samples: list of code strings"""
    raw_keys = [
        "imports", "calls", "positional_args", "subscript_literals", "assigned_columns",
        "open_encoding", "exceptions", "none_checks", "output",
    ]
    per_category = {key: [] for key in raw_keys}
    per_sample_kwarg_calls = []
    per_sample_kwarg_noargs = []
    parse_errors = []
    n = len(samples)
    for idx, code in enumerate(samples, start=1):
        facts, err = extract_facts(code)
        if err is not None:
            parse_errors.append(f"sample{idx:02d}: {err}")
            for key in raw_keys:
                per_category[key].append(set())
            per_sample_kwarg_calls.append([])
            per_sample_kwarg_noargs.append(set())
            continue
        for key in raw_keys:
            per_category[key].append(facts[key])
        per_sample_kwarg_calls.append(facts["kwarg_calls"])
        per_sample_kwarg_noargs.append(facts["kwarg_noargs"])

    kwargs_from_values = build_kwarg_fact_sets(per_sample_kwarg_calls)
    per_category["kwargs"] = [
        values | noargs for values, noargs in zip(kwargs_from_values, per_sample_kwarg_noargs)
    ]

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
