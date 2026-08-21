# -*- coding: utf-8 -*-
"""Phase 0a：既存サンプルの code フィールドを raw から再抽出して上書きする。

extract_code のバグ修正（run_divergence.py）を、新規生成を行わずに
既存の outputs/divergence/*.json に反映するための一回限りのツール。
raw フィールドは変更しない。code フィールドのみを上書きする。

使い方:
  python reextract_code.py            # 全件を再抽出して上書き、変更点を報告
  python reextract_code.py --dry-run  # 上書きせず、変更されるサンプルのみ表示
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "outputs" / "divergence"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_divergence import extract_code  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    files = sorted(OUT_DIR.glob("task*__*.json"))
    if not files:
        sys.exit("outputs/divergence/ にサンプルがありません。")

    changed = []
    unchanged = 0
    for p in files:
        d = json.loads(p.read_text(encoding="utf-8"))
        new_code = extract_code(d["raw"])
        if new_code != d["code"]:
            changed.append(p.name)
            if not args.dry_run:
                d["code"] = new_code
                p.write_text(
                    json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8"
                )
        else:
            unchanged += 1

    print(f"変更あり: {len(changed)}件 / 変更なし: {unchanged}件（全{len(files)}件）")
    for name in changed:
        print(f"  - {name}")
    if args.dry_run:
        print("（--dry-run のため書き込みは行っていません）")


if __name__ == "__main__":
    main()
