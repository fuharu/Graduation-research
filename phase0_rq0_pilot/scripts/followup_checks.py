# -*- coding: utf-8 -*-
"""Phase 0a: フォローアップ照会（判断・解釈を含まない機械照会）。

対象: outputs/divergence/task03__*.json

1. mkdir/os.makedirs の直前ガード: 同一関数内で、その mkdir/makedirs 呼び出しの
   対象パスと同一テキストの is_file()/os.path.isfile()/exists() を条件節に持つ
   if 文が、当該呼び出しと同じ行以前に存在するサンプルを列挙する。
   ループ要素に対する is_file()（イテレーション絞り込み）は対象外
   （対象パステキストが一致しない限りマッチしないため自動的に除外される）。
2. .glob / .rglob の呼び出し行を前後3行つきで列挙する。
3. ast.parse に失敗するサンプルの番号・先頭20行・例外メッセージを列挙する。

使い方:
  python followup_checks.py
"""
import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "outputs" / "divergence"
OUT_PATH = OUT_DIR / "followup_checks.md"


def call_base_name(call_node):
    func = call_node.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def import_module_roots(tree):
    mapping = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                bound = alias.asname or alias.name.split(".")[0]
                mapping[bound] = alias.name.split(".")[0]
        if isinstance(node, ast.ImportFrom) and node.module == "os.path":
            for alias in node.names:
                bound = alias.asname or alias.name
                mapping[bound] = "os.path." + alias.name
    return mapping


def unparse(node):
    try:
        return ast.unparse(node)
    except Exception:
        return None


def is_mkdir_call(node, module_roots):
    """Path.mkdir() または os.makedirs() 呼び出しかどうか。戻り値: 対象パスのASTノード or None"""
    if not isinstance(node, ast.Call):
        return None
    func = node.func
    if isinstance(func, ast.Attribute) and func.attr == "mkdir":
        return func.value
    if isinstance(func, ast.Attribute) and func.attr == "makedirs":
        value = func.value
        if isinstance(value, ast.Name) and module_roots.get(value.id) == "os":
            if node.args:
                return node.args[0]
    return None


def is_guard_call(node, module_roots):
    """is_file()/os.path.isfile()/exists() 呼び出しかどうか。戻り値: 対象パスのASTノード or None"""
    if not isinstance(node, ast.Call):
        return None
    func = node.func
    if isinstance(func, ast.Attribute) and func.attr in ("is_file", "exists"):
        return func.value
    if isinstance(func, ast.Attribute) and func.attr in ("isfile", "exists"):
        value = func.value
        if isinstance(value, ast.Attribute) and value.attr == "path":
            if isinstance(value.value, ast.Name) and module_roots.get(value.value.id) == "os":
                if node.args:
                    return node.args[0]
        if isinstance(value, ast.Name) and module_roots.get(value.id) == "os.path.isfile":
            if node.args:
                return node.args[0]
    return None


def find_enclosing_functions(tree):
    """トップレベル関数(FunctionDef/AsyncFunctionDef)ごとに、その中の全ノードを集める"""
    funcs = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            funcs.append(node)
    return funcs


def check_mkdir_immediate_guard(tree, module_roots):
    """mkdir/makedirsの対象パスに対するis_file/isfile/existsの分岐が同一関数内の
    先行行(if文の行 <= mkdir呼び出しの行)に存在するか"""
    funcs = find_enclosing_functions(tree)
    # モジュールレベルのコードも1つの「関数」として扱う（関数定義を除く直下の文）
    module_level_nodes = [n for n in ast.iter_child_nodes(tree)
                           if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef,
                                                  ast.Import, ast.ImportFrom))]

    def scope_nodes(scope_node):
        return list(ast.walk(scope_node))

    scopes = [(f"function:{f.name}", scope_nodes(f)) for f in funcs]
    if module_level_nodes:
        module_walk = []
        for n in module_level_nodes:
            module_walk.extend(ast.walk(n))
        scopes.append(("module", module_walk))

    for scope_name, nodes in scopes:
        mkdir_calls = []
        guard_ifs = []  # (path_text, lineno)
        for node in nodes:
            target = is_mkdir_call(node, module_roots)
            if target is not None:
                text = unparse(target)
                if text is not None:
                    mkdir_calls.append((text, node.lineno))
            if isinstance(node, (ast.If, ast.IfExp)):
                for sub in ast.walk(node.test):
                    guard_target = is_guard_call(sub, module_roots)
                    if guard_target is not None:
                        text = unparse(guard_target)
                        if text is not None:
                            guard_ifs.append((text, node.lineno))
        for mk_text, mk_line in mkdir_calls:
            for g_text, g_line in guard_ifs:
                if g_text == mk_text and g_line <= mk_line:
                    return True
    return False


def find_glob_calls(code):
    """.glob(...) / .rglob(...) の呼び出し行番号を返す（文字列検索、コメント含む可能性あり点に注意）"""
    lines = code.splitlines()
    hits = []
    for i, line in enumerate(lines, start=1):
        if ".glob(" in line or ".rglob(" in line:
            hits.append(i)
    return hits, lines


def main():
    files = sorted(OUT_DIR.glob("task03__*.json"))
    if not files:
        sys.exit("outputs/divergence/ に task03 のサンプルがありません。")

    samples = []
    for p in files:
        d = json.loads(p.read_text(encoding="utf-8"))
        samples.append((d["sample"], d["code"]))
    samples.sort(key=lambda t: t[0])

    out = []
    out.append("# フォローアップ機械照会（task03、判断・解釈なし）")
    out.append("")

    # ---------- 1. mkdir直前ガード ----------
    out.append("## 1. mkdir/makedirs の直前ガード（対象パス一致 + 先行行のis_file/isfile/exists分岐）")
    out.append("")
    matched = []
    parse_fail = []
    for sample_no, code in samples:
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            parse_fail.append(sample_no)
            continue
        module_roots = import_module_roots(tree)
        if check_mkdir_immediate_guard(tree, module_roots):
            matched.append(sample_no)
    samples_str = ",".join(str(s) for s in matched)
    out.append(f"該当 {len(matched)}/{len(samples)} [{samples_str}]")
    if parse_fail:
        out.append("")
        out.append(f"（構文解析失敗のため判定対象外: {parse_fail} — 詳細は3節）")
    out.append("")

    # ---------- 2. .glob / .rglob 呼び出し ----------
    out.append("## 2. .glob / .rglob 呼び出し（前後3行）")
    out.append("")
    for sample_no, code in samples:
        hits, lines = find_glob_calls(code)
        if not hits:
            continue
        out.append(f"### sample{sample_no:02d}")
        out.append("")
        for h in hits:
            start = max(1, h - 3)
            end = min(len(lines), h + 3)
            out.append("```python")
            for ln in range(start, end + 1):
                marker = ">>" if ln == h else "  "
                out.append(f"{marker} {ln:4d}: {lines[ln - 1]}")
            out.append("```")
            out.append("")

    # ---------- 3. パースエラー ----------
    out.append("## 3. 構文解析エラーのサンプル（先頭20行 + 例外メッセージ）")
    out.append("")
    for sample_no, code in samples:
        try:
            ast.parse(code)
        except SyntaxError as e:
            out.append(f"### sample{sample_no:02d}")
            out.append("")
            out.append(f"例外メッセージ: `{e.__class__.__name__}: {e}`")
            out.append("")
            lines = code.splitlines()
            out.append("```python")
            for ln in range(1, min(20, len(lines)) + 1):
                out.append(f"{ln:4d}: {lines[ln - 1]}")
            out.append("```")
            out.append("")

    text = "\n".join(out)
    OUT_PATH.write_text(text, encoding="utf-8")
    print(f"書き出し: {OUT_PATH}", file=sys.stderr)


if __name__ == "__main__":
    main()
