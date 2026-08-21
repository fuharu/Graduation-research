# -*- coding: utf-8 -*-
"""Phase 0a：特定の観点についての機械照会（該当サンプル番号の一覧のみ。判断・解釈はしない）。

outputs/divergence/*.json の code フィールドをASTで解析し、指定された7項目について
「該当するサンプルが存在するか」をタスクごとに照会する。

使い方:
  python targeted_checks.py            # 全タスクを照会し、標準出力 + targeted_checks.md に書き出す
"""
import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "outputs" / "divergence"
OUT_PATH = OUT_DIR / "targeted_checks.md"


def call_base_name(call_node):
    """呼び出しの「末尾の名前」（Nameならその名前、属性アクセスならattr名）"""
    func = call_node.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def is_call_to(call_node, module_roots, module_name, func_name):
    """`module.func_name(...)` 呼び出しかどうか（importのエイリアスを考慮）"""
    func = call_node.func
    if not isinstance(func, ast.Attribute):
        return False
    if func.attr != func_name:
        return False
    value = func.value
    if isinstance(value, ast.Name):
        return module_roots.get(value.id) == module_name
    return False


def import_module_roots(tree):
    mapping = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                bound = alias.asname or alias.name.split(".")[0]
                mapping[bound] = alias.name.split(".")[0]
    return mapping


def has_kwarg(call_node, *names):
    return any(kw.arg in names for kw in call_node.keywords)


# ---------- 各項目の判定関数 ----------
# 引数: tree, module_roots  戻り値: bool

def check_read_csv_header_or_names(tree, module_roots):
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and is_call_to(node, module_roots, "pd", "read_csv"):
            if has_kwarg(node, "header", "names"):
                return True
    return False


def check_to_datetime_format_or_errors(tree, module_roots):
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and is_call_to(node, module_roots, "pd", "to_datetime"):
            if has_kwarg(node, "format", "errors"):
                return True
    return False


MISSING_VALUE_NAMES = {"dropna", "fillna", "isna", "notna"}


def check_missing_value_handling(tree, module_roots):
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            base = call_base_name(node)
            if base in MISSING_VALUE_NAMES:
                return True
            if is_call_to(node, module_roots, "pd", "to_numeric"):
                return True
            if base == "astype" and node.args:
                arg = node.args[0]
                if isinstance(arg, ast.Name) and arg.id == "float":
                    return True
    return False


def check_requests_get_timeout(tree, module_roots):
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and is_call_to(node, module_roots, "requests", "get"):
            if has_kwarg(node, "timeout"):
                return True
    return False


TARGET_KEYS = {"daily", "time"}


def check_key_existence_precheck(tree, module_roots):
    for node in ast.walk(tree):
        # `'daily' in x` / `'time' in x`（またはその逆）
        if isinstance(node, ast.Compare):
            for op, comparator in zip(node.ops, node.comparators):
                if isinstance(op, (ast.In, ast.NotIn)):
                    left, right = node.left, comparator
                    for side in (left, right):
                        if isinstance(side, ast.Constant) and side.value in TARGET_KEYS:
                            return True
        # `.get('daily')` / `.get('time')`
        if isinstance(node, ast.Call):
            base = call_base_name(node)
            if base == "get" and node.args:
                arg = node.args[0]
                if isinstance(arg, ast.Constant) and arg.value in TARGET_KEYS:
                    return True
        # try/except KeyError
        if isinstance(node, ast.Try):
            for handler in node.handlers:
                t = handler.type
                names = []
                if isinstance(t, ast.Name):
                    names = [t.id]
                elif isinstance(t, ast.Tuple):
                    names = [e.id for e in t.elts if isinstance(e, ast.Name)]
                if "KeyError" in names:
                    return True
    return False


def _is_isfile_call(node):
    return isinstance(node, ast.Call) and call_base_name(node) in ("is_file", "isfile")


def check_isfile_precheck_before_mkdir_or_move(tree, module_roots):
    # 「分岐」= is_file()/os.path.isfile() の呼び出しが if文またはif式（三項演算子）の条件節に現れる
    for node in ast.walk(tree):
        if isinstance(node, (ast.If, ast.IfExp)):
            for sub in ast.walk(node.test):
                if _is_isfile_call(sub):
                    return True
    return False


def check_isfile_filter_on_iterdir_or_glob(tree, module_roots):
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            test = node.test
            for sub in ast.walk(test):
                if isinstance(sub, ast.Call) and call_base_name(sub) == "is_file":
                    return True
        # 内包表記での if 節も対象
        if isinstance(node, (ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp)):
            for gen in node.generators:
                for cond in gen.ifs:
                    for sub in ast.walk(cond):
                        if isinstance(sub, ast.Call) and call_base_name(sub) == "is_file":
                            return True
    return False


CHECKS = {
    "task01": [
        ("1. pd.read_csv に header= または names= を渡している", check_read_csv_header_or_names),
        ("2. pd.to_datetime に format= または errors= を渡している", check_to_datetime_format_or_errors),
        ("3. dropna/fillna/isna/notna/astype(float)/pd.to_numeric のいずれかを使っている",
         check_missing_value_handling),
    ],
    "task02": [
        ("4. requests.get に timeout= を渡している", check_requests_get_timeout),
        ("5. 'daily'/'time' キーの存在を事前確認している（in / .get() / except KeyError）",
         check_key_existence_precheck),
    ],
    "task03": [
        ("6. mkdir/shutil.move の前に対象パスがファイルとして存在しないか確認している"
         "（is_file / os.path.isfile）", check_isfile_precheck_before_mkdir_or_move),
        ("7. iterdir/glob の結果を is_file() で絞り込んでいる", check_isfile_filter_on_iterdir_or_glob),
    ],
}


def run_checks_for_task(task_id, samples):
    """samples: list of (sample_no, code)"""
    n = len(samples)
    results = {}
    for label, fn in CHECKS.get(task_id, []):
        matched = []
        for sample_no, code in samples:
            try:
                tree = ast.parse(code)
            except SyntaxError:
                continue
            module_roots = import_module_roots(tree)
            if fn(tree, module_roots):
                matched.append(sample_no)
        results[label] = (matched, n)
    return results


def main():
    files = sorted(OUT_DIR.glob("task*__*.json"))
    if not files:
        sys.exit("outputs/divergence/ にサンプルがありません。先に run_divergence.py run を実行。")

    by_task = {}
    for p in files:
        d = json.loads(p.read_text(encoding="utf-8"))
        by_task.setdefault(d["task"], []).append((d["sample"], d["code"]))
    for task_id in by_task:
        by_task[task_id].sort(key=lambda t: t[0])

    out_lines = ["# 特定観点の機械照会（該当サンプル番号のみ）", "",
                 "判断・解釈は行わない。各項目について該当サンプル番号を列挙するのみ。", ""]

    for task_id in sorted(CHECKS):
        out_lines.append(f"## {task_id}")
        out_lines.append("")
        samples = by_task.get(task_id, [])
        results = run_checks_for_task(task_id, samples)
        for label, fn in CHECKS[task_id]:
            matched, n = results[label]
            samples_str = ",".join(str(s) for s in matched)
            out_lines.append(f"- {label}: 該当 {len(matched)}/{n} [{samples_str}]")
        out_lines.append("")

    text = "\n".join(out_lines)
    OUT_PATH.write_text(text, encoding="utf-8")
    print(text)
    print(f"\n書き出し: {OUT_PATH}", file=sys.stderr)


if __name__ == "__main__":
    main()
