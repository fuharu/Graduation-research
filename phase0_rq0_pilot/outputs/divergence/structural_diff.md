# 分岐分析：構造的差分の機械集計

各カテゴリは事実の集計のみ（解釈・分類は annotation_sheet.csv 側で行う）。

## task01

### importしているモジュール

| 特徴 | 件数(/8件) |
|---|---|
| `import pandas as pd` | 8 |

### 呼んでいる関数・メソッド

| 特徴 | 件数(/8件) |
|---|---|
| `.groupby` | 8 |
| `.reset_index` | 8 |
| `.sum` | 8 |
| `.to_csv` | 8 |
| `.to_period` | 8 |
| `pd.read_csv` | 8 |
| `pd.to_datetime` | 8 |
| `print` | 8 |
| `.astype` | 7 |
| `.head` | 4 |
| `.sort_values` | 1 |

### open()のencoding引数

| 特徴 | 件数(/8件) |
|---|---|
| (該当なし) | - |

### try/exceptの有無と捕捉例外

| 特徴 | 件数(/8件) |
|---|---|
| (該当なし) | - |

### 欠損・Noneのチェック

| 特徴 | 件数(/8件) |
|---|---|
| (該当なし) | - |

### 出力方法（print / f-string / round桁数など）

| 特徴 | 件数(/8件) |
|---|---|
| `print()呼び出しあり` | 8 |

## task02

### importしているモジュール

| 特徴 | 件数(/8件) |
|---|---|
| `import requests` | 8 |
| `import sys` | 8 |
| `from datetime import datetime` | 7 |

### 呼んでいる関数・メソッド

| 特徴 | 件数(/8件) |
|---|---|
| `.json` | 8 |
| `.raise_for_status` | 8 |
| `.write` | 8 |
| `float` | 8 |
| `len` | 8 |
| `main` | 8 |
| `open` | 8 |
| `print` | 8 |
| `requests.get` | 8 |
| `sys.exit` | 8 |
| `zip` | 7 |
| `get_weather` | 6 |
| `fetch_weather` | 2 |
| `.append` | 1 |
| `.join` | 1 |
| `.strftime` | 1 |
| `.strptime` | 1 |
| `create_markdown_table` | 1 |
| `range` | 1 |

### open()のencoding引数

| 特徴 | 件数(/8件) |
|---|---|
| `encoding='utf-8'` | 7 |
| `encoding指定なし` | 1 |

### try/exceptの有無と捕捉例外

| 特徴 | 件数(/8件) |
|---|---|
| `except: ValueError` | 8 |
| `try/exceptあり` | 8 |

### 欠損・Noneのチェック

| 特徴 | 件数(/8件) |
|---|---|
| (該当なし) | - |

### 出力方法（print / f-string / round桁数など）

| 特徴 | 件数(/8件) |
|---|---|
| `f-string使用` | 8 |
| `print()呼び出しあり` | 8 |

## task03

### importしているモジュール

| 特徴 | 件数(/8件) |
|---|---|
| `from pathlib import Path` | 8 |
| `import os` | 8 |
| `import shutil` | 8 |
| `import argparse` | 7 |
| `from collections import defaultdict` | 6 |
| `import sys` | 5 |
| `from anthropic import Anthropic` | 2 |

### 呼んでいる関数・メソッド

| 特徴 | 件数(/8件) |
|---|---|
| `.exists` | 8 |
| `.is_dir` | 8 |
| `.iterdir` | 8 |
| `.lower` | 8 |
| `.mkdir` | 8 |
| `Path` | 8 |
| `main` | 8 |
| `organize_files` | 8 |
| `print` | 8 |
| `shutil.move` | 8 |
| `str` | 8 |
| `.add_argument` | 7 |
| `.append` | 7 |
| `.parse_args` | 7 |
| `argparse.ArgumentParser` | 7 |
| `get_unique_filename` | 7 |
| `.is_file` | 6 |
| `defaultdict` | 6 |
| `len` | 5 |
| `sorted` | 5 |
| `.items` | 4 |
| `.keys` | 4 |
| `get_file_category` | 4 |
| `.create` | 2 |
| `.lstrip` | 2 |
| `.upper` | 2 |
| `.values` | 2 |
| `Anthropic` | 2 |
| `get_category` | 2 |
| `sys.exit` | 2 |
| `.join` | 1 |
| `.relative_to` | 1 |
| `.resolve` | 1 |
| `.split` | 1 |
| `.startswith` | 1 |
| `.strip` | 1 |
| `ask_claude` | 1 |
| `categorize_file` | 1 |
| `input` | 1 |
| `interactive_mode` | 1 |
| `os.path.exists` | 1 |
| `os.path.join` | 1 |
| `os.path.splitext` | 1 |
| `set` | 1 |
| `setup_directories` | 1 |
| `sum` | 1 |

### open()のencoding引数

| 特徴 | 件数(/8件) |
|---|---|
| (該当なし) | - |

### try/exceptの有無と捕捉例外

| 特徴 | 件数(/8件) |
|---|---|
| `except: Exception` | 4 |
| `try/exceptあり` | 4 |
| `except: KeyboardInterrupt` | 1 |

### 欠損・Noneのチェック

| 特徴 | 件数(/8件) |
|---|---|
| (該当なし) | - |

### 出力方法（print / f-string / round桁数など）

| 特徴 | 件数(/8件) |
|---|---|
| `f-string使用` | 8 |
| `print()呼び出しあり` | 8 |
