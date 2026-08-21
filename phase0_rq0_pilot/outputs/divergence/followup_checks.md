# フォローアップ機械照会（task03、判断・解釈なし）

## 1. mkdir/makedirs の直前ガード（対象パス一致 + 先行行のis_file/isfile/exists分岐）

該当 12/30 [1,4,5,8,10,13,15,19,23,24,26,28]

（構文解析失敗のため判定対象外: [12, 22] — 詳細は3節）

## 2. .glob / .rglob 呼び出し（前後3行）

### sample20

```python
     48:     
     49:     # Gather file information
     50:     files_to_move = []
>>   51:     for file_path in folder.glob('*'):
     52:         if file_path.is_file():
     53:             ext = file_path.suffix
     54:             category = get_category(ext)
```

## 3. 構文解析エラーのサンプル（先頭20行 + 例外メッセージ）

### sample12

例外メッセージ: `SyntaxError: invalid syntax (<unknown>, line 1)`

```python
   1: ```python
   2: #!/usr/bin/env python3
   3: import anthropic
   4: import json
   5: import os
   6: import shutil
   7: from pathlib import Path
   8: import subprocess
   9: import sys
  10: 
  11: 
  12: def create_file_organizer_tool():
  13:     """Create the file organizer tool specification"""
  14:     return {
  15:         "name": "organize_files",
  16:         "description": "Organize files in a directory into subdirectories based on file extensions",
  17:         "input_schema": {
  18:             "type": "object",
  19:             "properties": {
  20:                 "source_dir": {
```

### sample22

例外メッセージ: `SyntaxError: invalid syntax (<unknown>, line 1)`

```python
   1: ```python
   2: #!/usr/bin/env python3
   3: import anthropic
   4: import argparse
   5: import json
   6: import os
   7: import shutil
   8: from pathlib import Path
   9: 
  10: def categorize_file(filename: str) -> str:
  11:     """ファイルを拡張子に基づいてカテゴリ分類"""
  12:     extension = Path(filename).suffix.lower()
  13:     
  14:     image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico', '.tiff'}
  15:     doc_extensions = {'.pdf', '.doc', '.docx', '.txt', '.xlsx', '.xls', '.ppt', '.pptx', '.odt', '.rtf'}
  16:     archive_extensions = {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.iso'}
  17:     
  18:     if extension in image_extensions:
  19:         return 'images'
  20:     elif extension in doc_extensions:
```
