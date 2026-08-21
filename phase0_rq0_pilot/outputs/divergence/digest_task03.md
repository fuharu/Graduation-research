# 分岐分析ダイジェスト: task03

各サンプルを見比べ、実装が割れた箇所を annotation_sheet.csv に記録する。
観点例: 欠損の扱い／丸め／エンコーディング／エラー処理／出力形式／タイムゾーン

## bedrock_claude-haiku-4-5-20251001-v1 / sample 01
```python
import os
import shutil
import argparse
from pathlib import Path
from collections import defaultdict

def organize_files(folder_path, dry_run=False):
    """
    Organize files in a folder into subdirectories based on file extensions.
    
    Args:
        folder_path: Path to the folder to organize
        dry_run: If True, only show the plan without actually moving files
    """
    
    # Define extension categories
    categories = {
        'images': {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico', '.tiff'},
        'docs': {'.pdf', '.doc', '.docx', '.txt', '.xlsx', '.xls', '.pptx', '.ppt', '.csv', '.md'},
        'archives': {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz'},
        'others': set()  # Catch-all category
    }
    
    folder = Path(folder_path)
    
    if not folder.exists() or not folder.is_dir():
        print(f"Error: {folder_path} is not a valid directory")
        return
    
    # Create subdirectories if they don't exist
    subdirs = {}
    for category in categories.keys():
        subdir = folder / category
        subdirs[category] = subdir
        if not dry_run and not subdir.exists():
            subdir.mkdir(parents=True, exist_ok=True)
    
    # Collect files to move
    moves = defaultdict(list)
    
    for item in folder.iterdir():
        # Skip subdirectories
        if item.is_dir():
            continue
        
        # Determine category
        ext = item.suffix.lower()
        category = 'others'
        
        for cat, extensions in categories.items():
            if ext in extensions:
                category = cat
                break
        
        # Get destination path
        dest_dir = subdirs[category]
        dest_path = dest_dir / item.name
        
        # Handle file name collisions
        if dest_path.exists():
            base_name = item.stem
            counter = 1
            while dest_path.exists():
                new_name = f"{base_name}_{counter}{item.suffix}"
                dest_path = dest_dir / new_name
                counter += 1
        
        moves[category].append({
            'source': item,
            'destination': dest_path,
            'original_name': item.name,
            'new_name': dest_path.name
        })
    
    # Display plan
    if not moves:
        print("No files to organize")
        return
    
    print("=" * 60)
    if dry_run:
        print("DRY RUN - Files will NOT be moved")
    print("=" * 60)
    
    total_files = 0
    for category in sorted(moves.keys()):
        files = moves[category]
        if files:
            print(f"\n{category.upper()}/ ({len(files)} file(s)):")
            for file_info in files:
                total_files += 1
                if file_info['original_name'] == file_info['new_name']:
                    print(f"  {file_info['original_name']}")
                else:
                    print(f"  {file_info['original_name']} → {file_info['new_name']}")
    
    print(f"\n{'=' * 60}")
    print(f"Total files to move: {total_files}")
    
    # Perform actual moves if not dry-run
    if not dry_run:
        for category in moves:
            for file_info in moves[category]:
                try:
                    shutil.move(str(file_info['source']), str(file_info['destination']))
                    print(f"✓ Moved: {file_info['original_name']} → {category}/")
                except Exception as e:
                    print(f"✗ Error moving {file_info['original_name']}: {e}")
        
        print(f"\nOrganization complete!")

def main():
    parser = argparse.ArgumentParser(
        description='Organize files in a folder into subdirectories by file type'
    )
    parser.add_argument(
        'folder',
        help='Path to the folder to organize'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without actually moving files'
    )
    
    args = parser.parse_args()
    
    organize_files(args.folder, dry_run=args.dry_run)

if __name__ == '__main__':
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 02
```python
import os
import sys
import shutil
from pathlib import Path
import argparse
from collections import defaultdict

def categorize_file(file_path):
    """ファイルを拡張子に基づいてカテゴリー分類"""
    extension = Path(file_path).suffix.lower()
    
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico'}
    doc_extensions = {'.pdf', '.doc', '.docx', '.txt', '.xlsx', '.xls', '.pptx', '.ppt', '.csv', '.md'}
    archive_extensions = {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.iso'}
    
    if extension in image_extensions:
        return 'images'
    elif extension in doc_extensions:
        return 'docs'
    elif extension in archive_extensions:
        return 'archives'
    else:
        return 'others'

def get_unique_filename(dest_dir, filename):
    """同名ファイルが存在する場合、連番を付けたファイル名を返す"""
    dest_path = os.path.join(dest_dir, filename)
    
    if not os.path.exists(dest_path):
        return filename
    
    name, ext = os.path.splitext(filename)
    counter = 1
    
    while os.path.exists(os.path.join(dest_dir, f"{name}_{counter}{ext}")):
        counter += 1
    
    return f"{name}_{counter}{ext}"

def organize_files(source_folder, dry_run=False):
    """フォルダ内のファイルを拡張子ごとにサブフォルダへ移動"""
    source_path = Path(source_folder).resolve()
    
    if not source_path.exists():
        print(f"エラー: フォルダが見つかりません: {source_folder}")
        return
    
    if not source_path.is_dir():
        print(f"エラー: ディレクトリではありません: {source_folder}")
        return
    
    categories = ['images', 'docs', 'archives', 'others']
    category_dirs = {cat: source_path / cat for cat in categories}
    
    if not dry_run:
        for cat_dir in category_dirs.values():
            cat_dir.mkdir(exist_ok=True)
    
    file_count = defaultdict(int)
    total_files = 0
    
    print(f"📁 処理対象フォルダ: {source_path}")
    print(f"{'🔍 シミュレーション' if dry_run else '⚙️  実行'} モード")
    print("-" * 60)
    
    for item in sorted(source_path.iterdir()):
        if item.is_file() and item.name != '.DS_Store':
            total_files += 1
            category = categorize_file(item)
            dest_dir = category_dirs[category]
            unique_name = get_unique_filename(str(dest_dir), item.name)
            dest_path = dest_dir / unique_name
            
            if unique_name != item.name:
                print(f"📄 {item.name} → {category}/{unique_name} (名前衝突で連番付与)")
            else:
                print(f"📄 {item.name} → {category}/")
            
            file_count[category] += 1
            
            if not dry_run:
                shutil.move(str(item), str(dest_path))
    
    print("-" * 60)
    print(f"📊 移動ファイル数: {total_files}")
    for category in categories:
        if file_count[category] > 0:
            print(f"   - {category}/: {file_count[category]} ファイル")

def main():
    parser = argparse.ArgumentParser(
        description="フォルダ内のファイルを拡張子ごとにサブフォルダへ移動します",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python solution.py /path/to/folder
  python solution.py /path/to/folder --dry-run
        """
    )
    
    parser.add_argument('folder', help='対象フォルダのパス')
    parser.add_argument('--dry-run', action='store_true', help='実際には移動せず計画のみ表示')
    
    args = parser.parse_args()
    
    organize_files(args.folder, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 03
```python
import argparse
import os
import shutil
from pathlib import Path
from anthropic import Anthropic

def setup_directories(base_folder):
    """Set up subdirectories for organizing files."""
    subdirs = {
        'images': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp', 'ico'],
        'docs': ['pdf', 'doc', 'docx', 'txt', 'xlsx', 'xls', 'ppt', 'pptx', 'csv', 'json', 'xml'],
        'archives': ['zip', 'rar', '7z', 'tar', 'gz', 'bz2'],
        'others': []
    }
    return subdirs

def get_category(extension, subdirs):
    """Determine the category for a file based on its extension."""
    ext_lower = extension.lower().lstrip('.')
    for category, extensions in subdirs.items():
        if category != 'others' and ext_lower in extensions:
            return category
    return 'others'

def get_unique_filename(dest_path):
    """Generate a unique filename if the file already exists."""
    if not dest_path.exists():
        return dest_path
    
    stem = dest_path.stem
    suffix = dest_path.suffix
    parent = dest_path.parent
    counter = 1
    
    while True:
        new_name = f"{stem}_{counter}{suffix}"
        new_path = parent / new_name
        if not new_path.exists():
            return new_path
        counter += 1

def organize_files(folder_path, dry_run=False):
    """Organize files in the specified folder."""
    base_path = Path(folder_path)
    
    if not base_path.exists():
        print(f"Error: Folder '{folder_path}' does not exist.")
        return
    
    if not base_path.is_dir():
        print(f"Error: '{folder_path}' is not a directory.")
        return
    
    subdirs = setup_directories(str(base_path))
    
    # Create subdirectories if not in dry-run mode
    if not dry_run:
        for subdir in subdirs.keys():
            subdir_path = base_path / subdir
            subdir_path.mkdir(exist_ok=True)
    
    # Plan and execute file movements
    client = Anthropic()
    conversation_history = []
    
    files_to_process = [f for f in base_path.iterdir() if f.is_file()]
    
    if not files_to_process:
        print("No files found to organize.")
        return
    
    # Initial analysis message
    file_list = "\n".join([f"- {f.name} ({f.suffix})" for f in files_to_process])
    initial_message = f"""I need to organize the following files in folder '{folder_path}':

{file_list}

The files should be organized into these categories:
- images/: jpg, jpeg, png, gif, bmp, svg, webp, ico
- docs/: pdf, doc, docx, txt, xlsx, xls, ppt, pptx, csv, json, xml
- archives/: zip, rar, 7z, tar, gz, bz2
- others/: everything else

Please analyze which files should go to which folder."""
    
    conversation_history.append({
        "role": "user",
        "content": initial_message
    })
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=conversation_history
    )
    
    analysis = response.content[0].text
    conversation_history.append({
        "role": "assistant",
        "content": analysis
    })
    
    print("File Organization Plan:")
    print("=" * 50)
    print(analysis)
    print("=" * 50)
    
    # Ask Claude to confirm the organization plan
    confirmation_message = "Please confirm this organization plan and list each file with its destination folder in a clear format."
    
    conversation_history.append({
        "role": "user",
        "content": confirmation_message
    })
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=conversation_history
    )
    
    plan = response.content[0].text
    conversation_history.append({
        "role": "assistant",
        "content": plan
    })
    
    print("\nDetailed Organization Plan:")
    print("-" * 50)
    print(plan)
    print("-" * 50)
    
    # Execute the organization
    movements = []
    for file_path in files_to_process:
        extension = file_path.suffix
        category = get_category(extension, subdirs)
        dest_folder = base_path / category
        
        if dry_run:
            print(f"[DRY RUN] Would move: {file_path.name} -> {category}/")
            movements.append((file_path.name, category))
        else:
            dest_folder.mkdir(exist_ok=True)
            dest_path = dest_folder / file_path.name
            dest_path = get_unique_filename(dest_path)
            shutil.move(str(file_path), str(dest_path))
            print(f"Moved: {file_path.name} -> {category}/{dest_path.name}")
            movements.append((file_path.name, category, dest_path.name))
    
    # Final summary from Claude
    if movements:
        summary_message = f"Great! I've organized the files. Here's a summary of the {len(movements)} files that were moved:\n"
        for movement in movements:
            if dry_run:
                summary_message += f"- {movement[0]} -> {movement[1]}/\n"
            else:
                if len(movement) == 3:
                    summary_message += f"- {movement[0]} -> {movement[1]}/ (as {movement[2]})\n"
        
        conversation_history.append({
            "role": "user",
            "content": f"Perfect! I've completed organizing the files. {summary_message}Can you provide a brief confirmation?"
        })
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=512,
            messages=conversation_history
        )
        
        print("\nFinal Summary:")
        print("-" * 50)
        print(response.content[0].text)

def main():
    parser = argparse.ArgumentParser(description="Organize files into folders by type")
    parser.add_argument("folder", help="Path to the folder to organize")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without actually moving files")
    
    args = parser.parse_args()
    
    organize_files(args.folder, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 04
```python
import os
import sys
import shutil
from pathlib import Path
from collections import defaultdict
import argparse

def get_file_category(filename: str) -> str:
    """ファイルの拡張子からカテゴリを決定"""
    ext = Path(filename).suffix.lower()
    
    image_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico', '.tiff'}
    doc_exts = {'.pdf', '.doc', '.docx', '.txt', '.xlsx', '.xls', '.ppt', '.pptx', '.odt'}
    archive_exts = {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.iso'}
    
    if ext in image_exts:
        return 'images'
    elif ext in doc_exts:
        return 'docs'
    elif ext in archive_exts:
        return 'archives'
    else:
        return 'others'

def get_unique_filename(dest_path: Path) -> Path:
    """同名ファイルが存在する場合、連番を付けた新しいパスを返す"""
    if not dest_path.exists():
        return dest_path
    
    stem = dest_path.stem
    suffix = dest_path.suffix
    parent = dest_path.parent
    
    counter = 1
    while True:
        new_name = f"{stem}_{counter}{suffix}"
        new_path = parent / new_name
        if not new_path.exists():
            return new_path
        counter += 1

def organize_files(folder_path: str, dry_run: bool = False):
    """指定フォルダ内のファイルを拡張子ごとにサブフォルダへ移動"""
    folder = Path(folder_path)
    
    if not folder.is_dir():
        print(f"エラー: '{folder_path}' はディレクトリではありません。")
        return
    
    categories = defaultdict(list)
    
    # ファイルをカテゴリ分類
    for item in folder.iterdir():
        if item.is_file():
            category = get_file_category(item.name)
            categories[category].append(item)
    
    if not categories:
        print(f"'{folder_path}' に移動対象のファイルがありません。")
        return
    
    operations = []
    
    # 移動操作を計画
    for category, files in sorted(categories.items()):
        category_folder = folder / category
        
        # サブフォルダを作成
        if not dry_run and not category_folder.exists():
            category_folder.mkdir(parents=True, exist_ok=True)
        
        for file_path in sorted(files):
            dest_path = category_folder / file_path.name
            dest_path = get_unique_filename(dest_path)
            operations.append((file_path, dest_path, category))
    
    # 計画を表示
    print(f"{'=' * 60}")
    print(f"ファイル整理計画 ({'ドライラン' if dry_run else '実行'})")
    print(f"{'=' * 60}")
    
    for src, dest, category in operations:
        rel_src = src.relative_to(folder)
        rel_dest = dest.relative_to(folder)
        print(f"[{category}] {rel_src} → {rel_dest}")
    
    print(f"{'=' * 60}")
    print(f"合計: {len(operations)} ファイル")
    
    # 実際に移動
    if not dry_run:
        print("\n移動を実行中...")
        for src, dest, _ in operations:
            try:
                shutil.move(str(src), str(dest))
            except Exception as e:
                print(f"エラー: {src} の移動に失敗しました: {e}")
        print("完了しました！")
    else:
        print("\n(ドライランモード: 実際には移動されていません)")

def main():
    parser = argparse.ArgumentParser(
        description='指定フォルダ内のファイルを拡張子ごとにサブフォルダへ移動'
    )
    parser.add_argument(
        'folder',
        help='整理対象のフォルダパス'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='実際には移動せず計画のみ表示'
    )
    
    args = parser.parse_args()
    
    organize_files(args.folder, dry_run=args.dry_run)

if __name__ == '__main__':
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 05
```python
import os
import sys
import shutil
from pathlib import Path
from anthropic import Anthropic

# Initialize Anthropic client
client = Anthropic()
conversation_history = []

# File extension categories
EXTENSION_CATEGORIES = {
    "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico"],
    "docs": [".pdf", ".doc", ".docx", ".txt", ".xlsx", ".xls", ".ppt", ".pptx", ".md"],
    "archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
    "others": []
}

def get_category(file_extension):
    """Determine file category based on extension."""
    ext = file_extension.lower()
    for category, extensions in EXTENSION_CATEGORIES.items():
        if category != "others" and ext in extensions:
            return category
    return "others"

def get_unique_filename(target_path):
    """Generate unique filename if file exists."""
    if not target_path.exists():
        return target_path
    
    base_path = target_path.parent
    stem = target_path.stem
    suffix = target_path.suffix
    
    counter = 1
    while True:
        new_name = f"{stem}_{counter}{suffix}"
        new_path = base_path / new_name
        if not new_path.exists():
            return new_path
        counter += 1

def organize_files(folder_path, dry_run=False):
    """Organize files in folder into category subfolders."""
    folder = Path(folder_path)
    
    if not folder.exists() or not folder.is_dir():
        print(f"Error: {folder_path} is not a valid directory")
        return
    
    # Create category subfolders if they don't exist
    subfolders = {}
    for category in EXTENSION_CATEGORIES.keys():
        subfolder = folder / category
        subfolders[category] = subfolder
        if not dry_run and not subfolder.exists():
            subfolder.mkdir(exist_ok=True)
    
    # Collect files to move
    moves = []
    for item in folder.iterdir():
        if item.is_file():
            ext = item.suffix
            category = get_category(ext)
            target_folder = subfolders[category]
            target_path = target_folder / item.name
            
            # Check for filename collision
            if target_path.exists():
                target_path = get_unique_filename(target_path)
            
            moves.append({
                "source": item,
                "destination": target_path,
                "category": category,
                "original_name": item.name,
                "new_name": target_path.name
            })
    
    # Display plan
    if not moves:
        print("No files to organize")
        return
    
    print(f"\n{'DRY RUN - ' if dry_run else ''}File Organization Plan:")
    print("=" * 60)
    
    for move in moves:
        if move["original_name"] != move["new_name"]:
            print(f"  {move['original_name']} → {move['category']}/{move['new_name']}")
        else:
            print(f"  {move['original_name']} → {move['category']}/")
    
    print("=" * 60)
    print(f"Total files: {len(moves)}")
    
    if not dry_run:
        for move in moves:
            shutil.move(str(move["source"]), str(move["destination"]))
        print("✓ Files organized successfully!")

def ask_claude(user_message):
    """Send message to Claude and get response."""
    conversation_history.append({
        "role": "user",
        "content": user_message
    })
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        system="""You are a helpful assistant for a file organization CLI tool. 
        You can help users understand how to use the tool, explain file categories, 
        and provide advice on file organization. Be concise and helpful.""",
        messages=conversation_history
    )
    
    assistant_message = response.content[0].text
    conversation_history.append({
        "role": "assistant",
        "content": assistant_message
    })
    
    return assistant_message

def interactive_mode():
    """Run interactive mode with Claude assistance."""
    print("File Organization CLI Tool - Interactive Mode")
    print("=" * 60)
    print("Commands:")
    print("  organize <folder_path> [--dry-run]  - Organize files in folder")
    print("  help                                 - Get help from Claude")
    print("  quit                                 - Exit")
    print("=" * 60)
    
    while True:
        try:
            user_input = input("\n> ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == "quit":
                print("Goodbye!")
                break
            
            if user_input.lower().startswith("organize"):
                parts = user_input.split()
                if len(parts) < 2:
                    print("Usage: organize <folder_path> [--dry-run]")
                    continue
                
                folder_path = parts[1]
                dry_run = "--dry-run" in parts
                
                organize_files(folder_path, dry_run)
            
            elif user_input.lower().startswith("help"):
                question = user_input[4:].strip()
                if not question:
                    question = "How do I use this file organization tool?"
                
                response = ask_claude(question)
                print(f"\nAssistant: {response}")
            
            else:
                # Treat as general question for Claude
                response = ask_claude(user_input)
                print(f"\nAssistant: {response}")
        
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        interactive_mode()
    else:
        # Command line mode
        if sys.argv[1].lower() in ["-h", "--help"]:
            print("File Organization CLI Tool")
            print("Usage: python solution.py [organize <folder_path> [--dry-run] | interactive]")
            print("\nExamples:")
            print("  python solution.py organize ~/Downloads")
            print("  python solution.py organize ~/Downloads --dry-run")
            print("  python solution.py interactive")
        elif sys.argv[1].lower() == "organize" and len(sys.argv) >= 3:
            folder_path = sys.argv[2]
            dry_run = "--dry-run" in sys.argv
            organize_files(folder_path, dry_run)
        elif sys.argv[1].lower() == "interactive":
            interactive_mode()
        else:
            print("Invalid command. Use -h for help.")

if __name__ == "__main__":
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 06
```python
import os
import sys
import shutil
from pathlib import Path
from collections import defaultdict
import argparse


def get_file_category(extension):
    """拡張子からカテゴリを判定"""
    extension = extension.lower().lstrip('.')
    
    image_exts = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp', 'ico'}
    doc_exts = {'pdf', 'doc', 'docx', 'txt', 'xlsx', 'xls', 'ppt', 'pptx', 'md'}
    archive_exts = {'zip', 'rar', '7z', 'tar', 'gz', 'bz2', 'iso'}
    
    if extension in image_exts:
        return 'images'
    elif extension in doc_exts:
        return 'docs'
    elif extension in archive_exts:
        return 'archives'
    else:
        return 'others'


def get_unique_filename(dest_path):
    """衝突時に連番を付けたファイル名を生成"""
    if not dest_path.exists():
        return dest_path
    
    stem = dest_path.stem
    suffix = dest_path.suffix
    parent = dest_path.parent
    counter = 1
    
    while True:
        new_name = f"{stem}_{counter}{suffix}"
        new_path = parent / new_name
        if not new_path.exists():
            return new_path
        counter += 1


def organize_files(source_dir, dry_run=False):
    """ファイルをカテゴリごとにサブフォルダへ移動"""
    source_path = Path(source_dir)
    
    if not source_path.is_dir():
        print(f"エラー: {source_dir} はディレクトリではありません")
        sys.exit(1)
    
    categories = defaultdict(list)
    
    # ファイルをスキャン
    for item in source_path.iterdir():
        if item.is_file():
            category = get_file_category(item.suffix)
            categories[category].append(item)
    
    # 移動計画を表示
    total_moves = 0
    for category in ['images', 'docs', 'archives', 'others']:
        if category in categories:
            print(f"\n【{category}/】に移動:")
            for file_path in categories[category]:
                dest_dir = source_path / category
                dest_path = dest_dir / file_path.name
                
                # 衝突チェック
                if dest_path.exists():
                    dest_path = get_unique_filename(dest_path)
                
                print(f"  {file_path.name} → {category}/{dest_path.name}")
                total_moves += 1
    
    if total_moves == 0:
        print("移動対象のファイルがありません")
        return
    
    print(f"\n合計: {total_moves}個のファイルを移動します")
    
    if dry_run:
        print("\n【ドライラン】実際には移動しません")
        return
    
    # 実際に移動
    print("\n移動を実行中...")
    for category in ['images', 'docs', 'archives', 'others']:
        if category in categories:
            dest_dir = source_path / category
            dest_dir.mkdir(exist_ok=True)
            
            for file_path in categories[category]:
                dest_path = dest_dir / file_path.name
                
                # 衝突チェック
                if dest_path.exists():
                    dest_path = get_unique_filename(dest_path)
                
                shutil.move(str(file_path), str(dest_path))
                print(f"✓ {file_path.name}")
    
    print("\n完了しました")


def main():
    parser = argparse.ArgumentParser(
        description='指定フォルダ内のファイルを拡張子ごとにサブフォルダへ移動します'
    )
    parser.add_argument(
        'folder',
        help='対象フォルダのパス'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='実際には移動せず計画のみ表示'
    )
    
    args = parser.parse_args()
    organize_files(args.folder, dry_run=args.dry_run)


if __name__ == '__main__':
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 07
```python
import os
import shutil
import argparse
from pathlib import Path
from collections import defaultdict

def get_file_category(filename):
    """ファイルの拡張子からカテゴリを判定"""
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico'}
    doc_extensions = {'.pdf', '.doc', '.docx', '.txt', '.xlsx', '.xls', '.ppt', '.pptx', '.csv', '.json', '.xml', '.md'}
    archive_extensions = {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.iso'}
    
    ext = Path(filename).suffix.lower()
    
    if ext in image_extensions:
        return 'images'
    elif ext in doc_extensions:
        return 'docs'
    elif ext in archive_extensions:
        return 'archives'
    else:
        return 'others'

def get_unique_filename(dest_path):
    """同名ファイルが存在する場合、連番を付けたファイル名を生成"""
    if not dest_path.exists():
        return dest_path
    
    stem = dest_path.stem
    suffix = dest_path.suffix
    parent = dest_path.parent
    counter = 1
    
    while True:
        new_name = f"{stem}_{counter}{suffix}"
        new_path = parent / new_name
        if not new_path.exists():
            return new_path
        counter += 1

def organize_files(folder_path, dry_run=False):
    """ファイルを拡張子ごとにサブフォルダへ移動"""
    folder_path = Path(folder_path)
    
    if not folder_path.exists():
        print(f"エラー: フォルダ '{folder_path}' が見つかりません")
        return
    
    if not folder_path.is_dir():
        print(f"エラー: '{folder_path}' はフォルダではありません")
        return
    
    # 移動計画を保存
    move_plan = defaultdict(list)
    
    # フォルダ内のファイルを処理
    for item in folder_path.iterdir():
        # サブフォルダはスキップ
        if item.is_dir():
            continue
        
        category = get_file_category(item.name)
        category_folder = folder_path / category
        dest_path = category_folder / item.name
        
        move_plan[category].append({
            'source': item,
            'dest': dest_path,
            'final_dest': get_unique_filename(dest_path)
        })
    
    if not move_plan:
        print("移動するファイルが見つかりません")
        return
    
    # 計画を表示
    print("=" * 60)
    print("ファイル移動計画:")
    print("=" * 60)
    
    total_files = 0
    for category in sorted(move_plan.keys()):
        print(f"\n[{category}/] フォルダへ移動:")
        for plan in move_plan[category]:
            source_name = plan['source'].name
            final_dest_name = plan['final_dest'].name
            
            if source_name != final_dest_name:
                print(f"  {source_name} -> {final_dest_name} (名前変更)")
            else:
                print(f"  {source_name}")
            total_files += 1
    
    print(f"\n合計: {total_files} ファイル")
    print("=" * 60)
    
    if dry_run:
        print("\n[DRY-RUN] 実際には移動しません")
        return
    
    # 実際に移動を実行
    print("\nファイルを移動中...")
    
    for category in move_plan.keys():
        category_folder = folder_path / category
        category_folder.mkdir(exist_ok=True)
        
        for plan in move_plan[category]:
            source = plan['source']
            final_dest = plan['final_dest']
            
            try:
                final_dest.parent.mkdir(exist_ok=True)
                shutil.move(str(source), str(final_dest))
                print(f"✓ {source.name} -> {category}/{final_dest.name}")
            except Exception as e:
                print(f"✗ {source.name} の移動に失敗: {e}")
    
    print("\n移動完了!")

def main():
    parser = argparse.ArgumentParser(
        description='指定フォルダ内のファイルを拡張子ごとにサブフォルダへ移動します'
    )
    parser.add_argument('folder', help='整理対象のフォルダパス')
    parser.add_argument('--dry-run', action='store_true', 
                        help='実際には移動せず、移動計画のみを表示します')
    
    args = parser.parse_args()
    
    organize_files(args.folder, dry_run=args.dry_run)

if __name__ == '__main__':
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 08
```python
#!/usr/bin/env python3
import os
import sys
import shutil
import argparse
from pathlib import Path
from collections import defaultdict

def get_file_category(filename):
    """Get the category for a file based on its extension."""
    ext = Path(filename).suffix.lower()
    
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico', '.tiff'}
    doc_extensions = {'.pdf', '.doc', '.docx', '.txt', '.xlsx', '.xls', '.pptx', '.ppt', '.odt', '.rtf'}
    archive_extensions = {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.iso'}
    
    if ext in image_extensions:
        return 'images'
    elif ext in doc_extensions:
        return 'docs'
    elif ext in archive_extensions:
        return 'archives'
    else:
        return 'others'

def get_unique_filename(destination_path):
    """Get a unique filename by adding a number if the file already exists."""
    if not destination_path.exists():
        return destination_path
    
    stem = destination_path.stem
    suffix = destination_path.suffix
    parent = destination_path.parent
    counter = 1
    
    while True:
        new_name = f"{stem}_{counter}{suffix}"
        new_path = parent / new_name
        if not new_path.exists():
            return new_path
        counter += 1

def organize_files(folder_path, dry_run=False):
    """Organize files in the specified folder by category."""
    folder = Path(folder_path)
    
    if not folder.is_dir():
        print(f"Error: '{folder_path}' is not a valid directory.")
        sys.exit(1)
    
    # Create category directories if they don't exist
    categories = ['images', 'docs', 'archives', 'others']
    category_dirs = {}
    
    for category in categories:
        cat_dir = folder / category
        category_dirs[category] = cat_dir
        if not dry_run and not cat_dir.exists():
            cat_dir.mkdir(parents=True, exist_ok=True)
    
    # Group files by category
    files_by_category = defaultdict(list)
    
    for item in folder.iterdir():
        if item.is_file():
            category = get_file_category(item.name)
            files_by_category[category].append(item)
    
    # Display and move files
    total_files = sum(len(files) for files in files_by_category.values())
    if total_files == 0:
        print(f"No files found in '{folder_path}'")
        return
    
    print(f"Found {total_files} files to organize:\n")
    
    moved_count = 0
    for category in categories:
        files = files_by_category[category]
        if files:
            print(f"{category.upper()}/ ({len(files)} files):")
            for file_path in sorted(files):
                destination_dir = category_dirs[category]
                destination_path = destination_dir / file_path.name
                
                # Check for file collision
                if destination_path.exists():
                    unique_path = get_unique_filename(destination_path)
                    new_name = unique_path.name
                    print(f"  {file_path.name} -> {new_name} (renamed due to collision)")
                    destination_path = unique_path
                else:
                    print(f"  {file_path.name}")
                
                if not dry_run:
                    shutil.move(str(file_path), str(destination_path))
                    moved_count += 1
            print()
    
    if dry_run:
        print(f"DRY RUN: Would move {total_files} files")
    else:
        print(f"Successfully moved {moved_count} files")

def main():
    parser = argparse.ArgumentParser(
        description='Organize files in a folder by category (images, docs, archives, others)'
    )
    parser.add_argument('folder', help='Path to the folder to organize')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without actually moving files')
    
    args = parser.parse_args()
    
    organize_files(args.folder, dry_run=args.dry_run)

if __name__ == '__main__':
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 09
```python
import os
import sys
import shutil
from pathlib import Path
import argparse
from collections import defaultdict

def get_category(extension: str) -> str:
    """ファイル拡張子からカテゴリを判定"""
    extension = extension.lower().lstrip('.')
    
    image_extensions = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp', 'ico', 'tiff'}
    doc_extensions = {'pdf', 'doc', 'docx', 'txt', 'xlsx', 'xls', 'ppt', 'pptx', 'odt', 'csv'}
    archive_extensions = {'zip', 'rar', '7z', 'tar', 'gz', 'bz2', 'xz'}
    
    if extension in image_extensions:
        return 'images'
    elif extension in doc_extensions:
        return 'docs'
    elif extension in archive_extensions:
        return 'archives'
    else:
        return 'others'

def get_unique_filename(target_dir: Path, filename: str) -> str:
    """同名ファイルが存在する場合、連番を付けた名前を返す"""
    target_path = target_dir / filename
    
    if not target_path.exists():
        return filename
    
    name, ext = os.path.splitext(filename)
    counter = 1
    
    while True:
        new_filename = f"{name}_{counter}{ext}"
        new_path = target_dir / new_filename
        if not new_path.exists():
            return new_filename
        counter += 1

def organize_files(folder_path: str, dry_run: bool = False):
    """指定フォルダ内のファイルをカテゴリ別に移動"""
    folder = Path(folder_path)
    
    if not folder.is_dir():
        print(f"エラー: '{folder_path}' はディレクトリではありません")
        return
    
    categories = defaultdict(list)
    
    # ファイルをスキャンしてカテゴリに分類
    for item in folder.iterdir():
        if item.is_file():
            ext = item.suffix
            if ext:
                category = get_category(ext)
            else:
                category = 'others'
            categories[category].append(item)
    
    # 移動計画を表示
    print("ファイル整理計画:")
    print("=" * 50)
    
    moves = []
    
    for category in ['images', 'docs', 'archives', 'others']:
        if category not in categories or not categories[category]:
            continue
            
        target_dir = folder / category
        print(f"\n{category}/ へ移動:")
        
        for file_path in categories[category]:
            unique_name = get_unique_filename(target_dir, file_path.name)
            
            if unique_name != file_path.name:
                print(f"  {file_path.name} → {unique_name}")
            else:
                print(f"  {file_path.name}")
            
            moves.append((file_path, target_dir, unique_name))
    
    if not moves:
        print("\n移動するファイルはありません")
        return
    
    print("\n" + "=" * 50)
    print(f"合計: {len(moves)} ファイルを移動します")
    
    if dry_run:
        print("\n[DRY RUN] 実際の移動は実行されていません")
        return
    
    # 実際にファイルを移動
    print("\nファイルを移動中...")
    
    for file_path, target_dir, unique_name in moves:
        # ターゲットディレクトリが存在しなければ作成
        target_dir.mkdir(exist_ok=True)
        
        target_path = target_dir / unique_name
        
        try:
            shutil.move(str(file_path), str(target_path))
            print(f"✓ {file_path.name} を {target_dir.name}/ に移動しました")
        except Exception as e:
            print(f"✗ {file_path.name} の移動に失敗しました: {e}")
    
    print("\n完了しました!")

def main():
    parser = argparse.ArgumentParser(
        description='指定フォルダ内のファイルを拡張子ごとにサブフォルダへ移動します'
    )
    parser.add_argument(
        'folder',
        help='整理対象のフォルダパス'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='実際には移動せず計画のみ表示します'
    )
    
    args = parser.parse_args()
    
    organize_files(args.folder, dry_run=args.dry_run)

if __name__ == '__main__':
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 10
```python
#!/usr/bin/env python3
import os
import shutil
import argparse
from pathlib import Path
from collections import defaultdict

def get_file_category(file_extension):
    """ファイル拡張子からカテゴリを決定"""
    extension = file_extension.lower().lstrip('.')
    
    image_extensions = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp', 'ico', 'tiff'}
    doc_extensions = {'txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'csv', 'json', 'xml', 'md'}
    archive_extensions = {'zip', 'rar', '7z', 'tar', 'gz', 'bz2', 'iso'}
    
    if extension in image_extensions:
        return 'images'
    elif extension in doc_extensions:
        return 'docs'
    elif extension in archive_extensions:
        return 'archives'
    else:
        return 'others'

def get_unique_filename(target_dir, filename):
    """同名ファイルが存在する場合、連番を付けた新しいファイル名を返す"""
    target_path = os.path.join(target_dir, filename)
    
    if not os.path.exists(target_path):
        return filename
    
    name, ext = os.path.splitext(filename)
    counter = 1
    
    while True:
        new_filename = f"{name}_{counter}{ext}"
        new_path = os.path.join(target_dir, new_filename)
        if not os.path.exists(new_path):
            return new_filename
        counter += 1

def organize_files(folder_path, dry_run=False):
    """フォルダ内のファイルを拡張子ごとにサブフォルダへ移動"""
    folder_path = Path(folder_path)
    
    if not folder_path.exists():
        print(f"エラー: フォルダ '{folder_path}' が見つかりません")
        return
    
    if not folder_path.is_dir():
        print(f"エラー: '{folder_path}' はフォルダではありません")
        return
    
    # 作成予定のサブフォルダ
    categories = ['images', 'docs', 'archives', 'others']
    
    # 移動計画を保存
    move_plan = defaultdict(list)
    
    # フォルダ内のファイルをスキャン
    for item in folder_path.iterdir():
        if item.is_file():
            # ドットファイルはスキップ
            if item.name.startswith('.'):
                continue
            
            # ファイルのカテゴリを決定
            category = get_file_category(item.suffix)
            move_plan[category].append(item.name)
    
    # 移動計画を表示
    print("=== ファイル整理計画 ===")
    print(f"対象フォルダ: {folder_path}")
    print(f"ドライラン: {'有効' if dry_run else '無効'}\n")
    
    if not any(move_plan.values()):
        print("移動対象のファイルがありません")
        return
    
    # 各カテゴリのファイルを表示・移動
    for category in categories:
        if category in move_plan:
            print(f"\n[{category}/] へ移動:")
            
            category_dir = folder_path / category
            
            # ドライランでない場合、フォルダを作成
            if not dry_run and not category_dir.exists():
                category_dir.mkdir(parents=True, exist_ok=True)
            
            for filename in move_plan[category]:
                source_file = folder_path / filename
                
                # 同名ファイルが存在する場合は連番を付ける
                if not dry_run and category_dir.exists():
                    unique_filename = get_unique_filename(str(category_dir), filename)
                else:
                    unique_filename = filename
                
                target_file = category_dir / unique_filename
                
                # ファイル情報を表示
                if unique_filename != filename:
                    print(f"  {filename} → {unique_filename}")
                else:
                    print(f"  {filename}")
                
                # ドライランでない場合、実際に移動
                if not dry_run:
                    shutil.move(str(source_file), str(target_file))
    
    print("\n" + "="*30)
    if dry_run:
        print("ドライラン完了。実際の移動は行われていません。")
    else:
        print("ファイル整理完了。")

def main():
    parser = argparse.ArgumentParser(
        description='指定フォルダ内のファイルを拡張子ごとにサブフォルダへ移動します'
    )
    parser.add_argument(
        'folder',
        help='整理対象のフォルダパス'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='実際には移動せず計画のみ表示'
    )
    
    args = parser.parse_args()
    
    organize_files(args.folder, dry_run=args.dry_run)

if __name__ == '__main__':
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 11
```python
import os
import shutil
import argparse
from pathlib import Path
from collections import defaultdict

def get_file_category(file_path):
    """ファイルの拡張子からカテゴリを決定"""
    ext = Path(file_path).suffix.lower()
    
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico', '.tiff'}
    doc_extensions = {'.pdf', '.doc', '.docx', '.txt', '.xlsx', '.xls', '.ppt', '.pptx', '.csv', '.json', '.xml', '.md'}
    archive_extensions = {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.iso'}
    
    if ext in image_extensions:
        return 'images'
    elif ext in doc_extensions:
        return 'docs'
    elif ext in archive_extensions:
        return 'archives'
    else:
        return 'others'

def get_unique_filename(dest_path):
    """同名ファイルの衝突を避けるため、必要に応じて連番を付ける"""
    if not dest_path.exists():
        return dest_path
    
    stem = dest_path.stem
    suffix = dest_path.suffix
    parent = dest_path.parent
    counter = 1
    
    while True:
        new_name = f"{stem}_{counter}{suffix}"
        new_path = parent / new_name
        if not new_path.exists():
            return new_path
        counter += 1

def organize_files(folder_path, dry_run=False):
    """指定フォルダ内のファイルをカテゴリごとにサブフォルダへ移動"""
    folder_path = Path(folder_path)
    
    if not folder_path.exists():
        print(f"エラー: フォルダ '{folder_path}' が見つかりません")
        return
    
    if not folder_path.is_dir():
        print(f"エラー: '{folder_path}' はフォルダではありません")
        return
    
    # ファイル移動計画を記録
    move_plan = defaultdict(list)
    
    # フォルダ内のすべてのファイルを処理
    for file_path in folder_path.iterdir():
        if file_path.is_file():
            category = get_file_category(file_path)
            move_plan[category].append(file_path)
    
    if not move_plan:
        print("移動対象のファイルがありません")
        return
    
    # 移動計画を表示
    print("=" * 50)
    print("ファイル整理計画")
    print("=" * 50)
    
    total_files = 0
    for category in ['images', 'docs', 'archives', 'others']:
        if category in move_plan:
            files = move_plan[category]
            print(f"\n[{category}/] へ移動:")
            for file_path in files:
                print(f"  - {file_path.name}")
                total_files += 1
    
    print(f"\n合計: {total_files} ファイル")
    print("=" * 50)
    
    if dry_run:
        print("\n※ ドライラン: 実際には移動されません")
        return
    
    # 実際にファイルを移動
    print("\nファイルを移動中...")
    
    for category, files in move_plan.items():
        # サブフォルダを作成
        subfolder = folder_path / category
        subfolder.mkdir(exist_ok=True)
        
        for file_path in files:
            try:
                dest_path = subfolder / file_path.name
                dest_path = get_unique_filename(dest_path)
                shutil.move(str(file_path), str(dest_path))
                print(f"✓ {file_path.name} → {category}/{dest_path.name}")
            except Exception as e:
                print(f"✗ {file_path.name} の移動に失敗: {e}")
    
    print("\n完了!")

def main():
    parser = argparse.ArgumentParser(description='指定フォルダ内のファイルをカテゴリごとにサブフォルダへ移動')
    parser.add_argument('folder', help='整理対象のフォルダパス')
    parser.add_argument('--dry-run', action='store_true', help='実際には移動せず計画のみ表示')
    
    args = parser.parse_args()
    
    organize_files(args.folder, dry_run=args.dry_run)

if __name__ == '__main__':
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 12
```python
#!/usr/bin/env python3
import anthropic
import json
import os
import shutil
from pathlib import Path
import subprocess
import sys


def create_file_organizer_tool():
    """Create the file organizer tool specification"""
    return {
        "name": "organize_files",
        "description": "Organize files in a directory into subdirectories based on file extensions",
        "input_schema": {
            "type": "object",
            "properties": {
                "source_dir": {
                    "type": "string",
                    "description": "The source directory path containing files to organize"
                },
                "dry_run": {
                    "type": "boolean",
                    "description": "If true, only show the plan without actually moving files",
                    "default": False
                }
            },
            "required": ["source_dir"]
        }
    }


def get_file_category(file_extension):
    """Determine the category folder for a file based on its extension"""
    file_extension = file_extension.lower()
    
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico', '.tiff'}
    doc_extensions = {'.pdf', '.doc', '.docx', '.txt', '.xlsx', '.xls', '.ppt', '.pptx', '.odt', '.rtf', '.csv'}
    archive_extensions = {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.iso', '.dmg'}
    
    if file_extension in image_extensions:
        return 'images'
    elif file_extension in doc_extensions:
        return 'docs'
    elif file_extension in archive_extensions:
        return 'archives'
    else:
        return 'others'


def get_unique_filename(target_path):
    """Generate a unique filename if the target path already exists"""
    if not target_path.exists():
        return target_path
    
    base_path = target_path.parent
    stem = target_path.stem
    suffix = target_path.suffix
    counter = 1
    
    while True:
        new_name = f"{stem}_{counter}{suffix}"
        new_path = base_path / new_name
        if not new_path.exists():
            return new_path
        counter += 1


def organize_files(source_dir, dry_run=False):
    """Organize files in the source directory"""
    source_path = Path(source_dir)
    
    if not source_path.exists():
        return {"error": f"Directory '{source_dir}' does not exist"}
    
    if not source_path.is_dir():
        return {"error": f"'{source_dir}' is not a directory"}
    
    # Create category directories
    categories = ['images', 'docs', 'archives', 'others']
    category_paths = {}
    
    for category in categories:
        category_path = source_path / category
        category_paths[category] = category_path
        if not dry_run and not category_path.exists():
            category_path.mkdir(parents=True, exist_ok=True)
    
    # Plan the file movements
    plan = []
    for item in source_path.iterdir():
        if item.is_file():
            file_extension = item.suffix
            if file_extension:
                category = get_file_category(file_extension)
                target_dir = category_paths[category]
                target_path = target_dir / item.name
                
                # Check for filename collision
                if target_path.exists():
                    target_path = get_unique_filename(target_path)
                
                plan.append({
                    "file": item.name,
                    "current_path": str(item),
                    "destination": str(target_path),
                    "category": category
                })
    
    # Execute the moves if not dry_run
    if not dry_run:
        for item in plan:
            src = Path(item["current_path"])
            dst = Path(item["destination"])
            shutil.move(str(src), str(dst))
    
    return {
        "dry_run": dry_run,
        "source_directory": str(source_path),
        "files_processed": len(plan),
        "plan": plan,
        "status": "Dry run completed - no files moved" if dry_run else "Files successfully organized"
    }


def process_tool_call(tool_name, tool_input):
    """Process a tool call and return the result"""
    if tool_name == "organize_files":
        return organize_files(
            source_dir=tool_input["source_dir"],
            dry_run=tool_input.get("dry_run", False)
        )
    return {"error": f"Unknown tool: {tool_name}"}


def main():
    """Main function to handle CLI arguments and coordinate with Claude"""
    if len(sys.argv) < 2:
        print("Usage: python solution.py <directory_path> [--dry-run]")
        print("Example: python solution.py ./my_files --dry-run")
        sys.exit(1)
    
    source_dir = sys.argv[1]
    dry_run = "--dry-run" in sys.argv
    
    # Initialize the Anthropic client
    client = anthropic.Anthropic()
    
    # Define the tool
    tool = create_file_organizer_tool()
    
    # Create the initial message
    user_message = f"Please organize files in the directory '{source_dir}' into subdirectories based on file type. " \
                   f"Use the organize_files tool with dry_run={dry_run}. " \
                   f"Categories should be: images/, docs/, archives/, and others/. " \
                   f"If a file would collide with an existing file, add a number suffix to the new filename."
    
    messages = [
        {"role": "user", "content": user_message}
    ]
    
    print(f"Organizing files in: {source_dir}")
    print(f"Dry run mode: {dry_run}")
    print("-" * 50)
    
    # Agentic loop
    while True:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            tools=[tool],
            messages=messages
        )
        
        # Check if we should stop
        if response.stop_reason == "end_turn":
            # Extract and print the final response
            for block in response.content:
                if hasattr(block, 'text'):
                    print(block.text)
            break
        
        # Process tool calls
        if response.stop_reason == "tool_use":
            # Add assistant response to messages
            messages.append({"role": "assistant", "content": response.content})
            
            # Process each tool call
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_result = process_tool_call(block.name, block.input)
                    
                    # Print the result
                    if "error" in tool_result:
                        print(f"Error: {tool_result['error']}")
                    else:
                        print(f"Status: {tool_result['status']}")
                        print(f"Files processed: {tool_result['files_processed']}")
                        if tool_result['plan']:
                            print("\nOrganization plan:")
                            for item in tool_result['plan']:
                                print(f"  {item['file']} -> {item['category']}/")
                                if item['destination'] != str(Path(tool_result['source_directory']) / item['category'] / item['file']):
                                    print(f"    (renamed to: {Path(item['destination']).name})")
                    
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(tool_result)
                    })
            
            # Add tool results to messages
            messages.append({"role": "user", "content": tool_results})
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 13
```python
#!/usr/bin/env python3
import os
import sys
import shutil
import argparse
from pathlib import Path
from anthropic import Anthropic

# Initialize the Anthropic client
client = Anthropic()

# Define file type mappings
FILE_TYPE_MAPPINGS = {
    'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico', '.tiff'],
    'docs': ['.pdf', '.doc', '.docx', '.txt', '.xlsx', '.xls', '.pptx', '.ppt', '.odt'],
    'archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.iso'],
    'others': []
}

def get_file_category(file_extension):
    """Determine the category of a file based on its extension."""
    ext = file_extension.lower()
    for category, extensions in FILE_TYPE_MAPPINGS.items():
        if ext in extensions:
            return category
    return 'others'

def get_unique_filename(target_dir, filename):
    """Generate a unique filename by adding a number if the file already exists."""
    filepath = os.path.join(target_dir, filename)
    if not os.path.exists(filepath):
        return filename
    
    name, ext = os.path.splitext(filename)
    counter = 1
    while os.path.exists(os.path.join(target_dir, f"{name}_{counter}{ext}")):
        counter += 1
    return f"{name}_{counter}{ext}"

def organize_files(folder_path, dry_run=False):
    """Organize files in the specified folder into category subdirectories."""
    folder_path = Path(folder_path).resolve()
    
    if not folder_path.exists():
        return f"Error: Folder '{folder_path}' does not exist."
    
    if not folder_path.is_dir():
        return f"Error: '{folder_path}' is not a directory."
    
    # Create category subdirectories if they don't exist
    categories = list(FILE_TYPE_MAPPINGS.keys())
    for category in categories:
        category_dir = folder_path / category
        if not dry_run and not category_dir.exists():
            category_dir.mkdir()
    
    # Collect files to move
    files_to_move = []
    for item in folder_path.iterdir():
        if item.is_file() and not item.name.startswith('.'):
            file_extension = item.suffix
            category = get_file_category(file_extension)
            target_dir = folder_path / category
            
            # Get unique filename if needed
            unique_name = get_unique_filename(str(target_dir), item.name)
            
            files_to_move.append({
                'source': str(item),
                'destination': str(target_dir / unique_name),
                'category': category,
                'original_name': item.name,
                'new_name': unique_name
            })
    
    # Display the plan
    result = f"Found {len(files_to_move)} files to organize:\n"
    result += "=" * 50 + "\n"
    
    for file_info in files_to_move:
        result += f"File: {file_info['original_name']}\n"
        result += f"  Category: {file_info['category']}\n"
        if file_info['original_name'] != file_info['new_name']:
            result += f"  New name: {file_info['new_name']} (renamed to avoid collision)\n"
        result += f"  Destination: {file_info['category']}/\n"
        result += "-" * 30 + "\n"
    
    # If not a dry run, actually move the files
    if not dry_run:
        for file_info in files_to_move:
            try:
                shutil.move(file_info['source'], file_info['destination'])
                result += f"✓ Moved: {file_info['original_name']}\n"
            except Exception as e:
                result += f"✗ Failed to move {file_info['original_name']}: {str(e)}\n"
    else:
        result += "\n[DRY RUN] No files were actually moved.\n"
    
    return result

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Organize files in a folder by file type into subdirectories"
    )
    parser.add_argument("folder", help="Path to the folder to organize")
    parser.add_argument("--dry-run", action="store_true", help="Show plan without actually moving files")
    
    args = parser.parse_args()
    
    # Use Claude for interactive conversation
    conversation_history = []
    
    # Initial message to Claude about the task
    initial_prompt = f"""I'm going to help organize files in a folder. The user wants to organize files from '{args.folder}' into subdirectories based on file type (images/, docs/, archives/, others/).

The --dry-run flag is {'enabled' if args.dry_run else 'disabled'}.

First, let me check what files are in the folder and show the organization plan."""
    
    conversation_history.append({
        "role": "user",
        "content": initial_prompt
    })
    
    # Get Claude's initial response
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        system="You are a helpful file organization assistant. You help users organize files into categories. Be concise and helpful.",
        messages=conversation_history
    )
    
    claude_response = response.content[0].text
    conversation_history.append({
        "role": "assistant",
        "content": claude_response
    })
    
    print("File Organization Assistant:")
    print(claude_response)
    print("\n" + "=" * 50 + "\n")
    
    # Perform the actual file organization
    organization_result = organize_files(args.folder, dry_run=args.dry_run)
    print(organization_result)
    
    # Add the result to conversation history for Claude to comment on
    conversation_history.append({
        "role": "user",
        "content": f"Here's the result of organizing the files:\n\n{organization_result}\n\nPlease provide a summary of what was done."
    })
    
    # Get Claude's final response
    final_response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=512,
        system="You are a helpful file organization assistant. Provide a brief, helpful summary of the file organization results.",
        messages=conversation_history
    )
    
    print("\nAssistant Summary:")
    print(final_response.content[0].text)

if __name__ == "__main__":
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 14
```python
import os
import shutil
import argparse
from pathlib import Path
from collections import defaultdict

def organize_files(source_dir, dry_run=False):
    """
    Organize files in a directory into subdirectories based on file extensions.
    
    Args:
        source_dir: Directory to organize
        dry_run: If True, only show what would be done without actually moving files
    """
    
    # Define file type mappings
    file_types = {
        'images': {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico', '.tiff'},
        'docs': {'.pdf', '.doc', '.docx', '.txt', '.xlsx', '.xls', '.pptx', '.ppt', '.odt', '.csv'},
        'archives': {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.iso'},
    }
    
    source_path = Path(source_dir)
    
    if not source_path.exists():
        print(f"Error: Directory '{source_dir}' does not exist.")
        return
    
    if not source_path.is_dir():
        print(f"Error: '{source_dir}' is not a directory.")
        return
    
    # Track what will be moved
    moves = defaultdict(list)
    
    # Scan files in source directory (non-recursive)
    for item in source_path.iterdir():
        if item.is_file():
            # Determine category
            category = 'others'
            file_ext = item.suffix.lower()
            
            for cat, extensions in file_types.items():
                if file_ext in extensions:
                    category = cat
                    break
            
            moves[category].append(item)
    
    # Create subdirectories and prepare moves
    for category in moves:
        category_dir = source_path / category
        
        if not dry_run:
            category_dir.mkdir(exist_ok=True)
        
        for file_path in moves[category]:
            target_path = category_dir / file_path.name
            
            # Handle file name collisions
            counter = 1
            base_name = file_path.stem
            extension = file_path.suffix
            
            while target_path.exists() and target_path != file_path:
                new_name = f"{base_name}_{counter}{extension}"
                target_path = category_dir / new_name
                counter += 1
            
            if dry_run:
                print(f"[DRY RUN] Would move: {file_path} -> {target_path}")
            else:
                print(f"Moving: {file_path} -> {target_path}")
                shutil.move(str(file_path), str(target_path))
    
    if dry_run:
        print("\n[DRY RUN] No files were actually moved.")
    else:
        print("\nFile organization completed.")
    
    # Print summary
    total_files = sum(len(files) for files in moves.values())
    print(f"\nSummary:")
    print(f"Total files processed: {total_files}")
    for category in sorted(moves.keys()):
        print(f"  {category}/: {len(moves[category])} files")

def main():
    parser = argparse.ArgumentParser(
        description="Organize files in a directory into subdirectories by file type."
    )
    parser.add_argument(
        "directory",
        help="Directory to organize"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without actually moving files"
    )
    
    args = parser.parse_args()
    
    organize_files(args.directory, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 15
```python
#!/usr/bin/env python3
import os
import sys
import shutil
import argparse
from pathlib import Path
from collections import defaultdict

def get_file_category(extension: str) -> str:
    """ファイル拡張子からカテゴリを決定"""
    extension = extension.lower()
    
    image_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico', '.tiff'}
    doc_exts = {'.pdf', '.doc', '.docx', '.txt', '.xlsx', '.xls', '.ppt', '.pptx', '.csv', '.json', '.xml', '.md'}
    archive_exts = {'.zip', '.tar', '.gz', '.rar', '.7z', '.bz2', '.xz'}
    
    if extension in image_exts:
        return 'images'
    elif extension in doc_exts:
        return 'docs'
    elif extension in archive_exts:
        return 'archives'
    else:
        return 'others'

def get_unique_filename(dest_path: Path) -> Path:
    """衝突時に連番を付けたユニークなパスを返す"""
    if not dest_path.exists():
        return dest_path
    
    stem = dest_path.stem
    suffix = dest_path.suffix
    parent = dest_path.parent
    counter = 1
    
    while True:
        new_name = f"{stem}_{counter}{suffix}"
        new_path = parent / new_name
        if not new_path.exists():
            return new_path
        counter += 1

def organize_files(folder_path: str, dry_run: bool = False) -> None:
    """指定フォルダ内のファイルをカテゴリ別サブフォルダに移動"""
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"エラー: フォルダ '{folder_path}' が見つかりません")
        sys.exit(1)
    
    if not folder.is_dir():
        print(f"エラー: '{folder_path}' はフォルダではありません")
        sys.exit(1)
    
    # カテゴリごとのファイル移動計画を作成
    moves = defaultdict(list)
    
    for item in folder.iterdir():
        if item.is_file() and not item.name.startswith('.'):
            extension = item.suffix
            category = get_file_category(extension)
            moves[category].append(item)
    
    if not moves:
        print("移動対象のファイルがありません")
        return
    
    # ドライランモードの場合、計画を表示
    if dry_run:
        print("=== ドライランモード: ファイル移動計画 ===\n")
    else:
        print("=== ファイル移動を開始 ===\n")
    
    total_files = 0
    for category, files in sorted(moves.items()):
        category_dir = folder / category
        
        print(f"[{category}/] ({len(files)}ファイル)")
        
        for file_path in sorted(files):
            # サブフォルダを作成（ドライランでない場合）
            if not dry_run and not category_dir.exists():
                category_dir.mkdir(parents=True, exist_ok=True)
            
            dest_path = category_dir / file_path.name
            
            # 衝突チェック
            if not dry_run:
                dest_path = get_unique_filename(dest_path)
            
            # ファイルサイズを取得
            file_size = file_path.stat().st_size
            size_str = format_size(file_size)
            
            if dest_path.name != file_path.name:
                print(f"  {file_path.name} → {dest_path.name} ({size_str})")
            else:
                print(f"  {file_path.name} ({size_str})")
            
            # 実際に移動（ドライランでない場合）
            if not dry_run:
                shutil.move(str(file_path), str(dest_path))
            
            total_files += 1
        
        print()
    
    if dry_run:
        print(f"合計: {total_files}ファイルを移動する予定です")
        print("実際に移動するには --dry-run オプションを削除してください")
    else:
        print(f"完了: {total_files}ファイルを移動しました")

def format_size(bytes_size: int) -> str:
    """バイト数をわかりやすいサイズ表記に変換"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024:
            return f"{bytes_size:.1f}{unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f}TB"

def main():
    parser = argparse.ArgumentParser(
        description="指定フォルダ内のファイルを拡張子ごとにサブフォルダへ移動します"
    )
    parser.add_argument(
        "folder",
        help="整理対象のフォルダパス"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="実際には移動せず、計画のみ表示します"
    )
    
    args = parser.parse_args()
    
    organize_files(args.folder, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 16
```python
import os
import sys
import shutil
from pathlib import Path
import argparse
from collections import defaultdict

def categorize_file(filename):
    """ファイルの拡張子に基づいてカテゴリを決定する"""
    ext = Path(filename).suffix.lower()
    
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico', '.tiff'}
    doc_extensions = {'.pdf', '.doc', '.docx', '.txt', '.xlsx', '.xls', '.ppt', '.pptx', '.odt', '.ods', '.odp'}
    archive_extensions = {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.iso', '.dmg'}
    
    if ext in image_extensions:
        return 'images'
    elif ext in doc_extensions:
        return 'docs'
    elif ext in archive_extensions:
        return 'archives'
    else:
        return 'others'

def get_unique_filename(destination_dir, filename):
    """衝突時に連番を付けたユニークなファイル名を生成"""
    dest_path = Path(destination_dir) / filename
    
    if not dest_path.exists():
        return filename
    
    stem = Path(filename).stem
    suffix = Path(filename).suffix
    counter = 1
    
    while True:
        new_filename = f"{stem}_{counter}{suffix}"
        new_path = Path(destination_dir) / new_filename
        if not new_path.exists():
            return new_filename
        counter += 1

def organize_files(folder_path, dry_run=False):
    """指定フォルダ内のファイルをカテゴリ別にサブフォルダへ移動"""
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"エラー: フォルダが見つかりません: {folder_path}")
        return
    
    if not folder.is_dir():
        print(f"エラー: ディレクトリではありません: {folder_path}")
        return
    
    categories = {'images', 'docs', 'archives', 'others'}
    operations = defaultdict(list)
    
    # ファイルを分類
    for item in folder.iterdir():
        if item.is_file():
            category = categorize_file(item.name)
            operations[category].append(item)
    
    # 操作を表示または実行
    if dry_run:
        print(f"\n【ドライラン】以下のファイルを移動します:")
        print(f"対象フォルダ: {folder_path}\n")
    else:
        print(f"\n【実行】以下のファイルを移動します:")
        print(f"対象フォルダ: {folder_path}\n")
    
    total_files = 0
    for category in sorted(categories):
        files = operations.get(category, [])
        if files:
            dest_dir = folder / category
            print(f"\n{category}/ フォルダへ移動:")
            
            for file_path in sorted(files):
                if not dry_run:
                    dest_dir.mkdir(exist_ok=True)
                
                unique_name = get_unique_filename(str(dest_dir), file_path.name)
                dest_path = dest_dir / unique_name
                
                if file_path.name == unique_name:
                    print(f"  {file_path.name}")
                else:
                    print(f"  {file_path.name} → {unique_name} (衝突回避)")
                
                if not dry_run:
                    shutil.move(str(file_path), str(dest_path))
                
                total_files += 1
    
    if total_files == 0:
        print("\n移動するファイルがありません")
    else:
        print(f"\n合計: {total_files} ファイル")
        if dry_run:
            print("※これはドライランです。実際には移動されていません。")

def main():
    parser = argparse.ArgumentParser(
        description='指定フォルダ内のファイルを拡張子ごとにサブフォルダへ移動します'
    )
    parser.add_argument(
        'folder',
        help='対象フォルダのパス'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='実際には移動せず、計画のみ表示します'
    )
    
    args = parser.parse_args()
    
    organize_files(args.folder, dry_run=args.dry_run)

if __name__ == '__main__':
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 17
```python
import os
import shutil
import argparse
from pathlib import Path
from collections import defaultdict

def get_category(extension):
    """ファイルの拡張子からカテゴリーを判定"""
    ext = extension.lower().lstrip('.')
    
    image_exts = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp', 'ico', 'tiff'}
    doc_exts = {'txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'md', 'json', 'xml', 'csv'}
    archive_exts = {'zip', 'rar', '7z', 'tar', 'gz', 'bz2', 'xz'}
    
    if ext in image_exts:
        return 'images'
    elif ext in doc_exts:
        return 'docs'
    elif ext in archive_exts:
        return 'archives'
    else:
        return 'others'

def get_unique_filename(dest_dir, filename):
    """同名ファイルが存在する場合は連番を付けたファイル名を返す"""
    dest_path = Path(dest_dir) / filename
    
    if not dest_path.exists():
        return filename
    
    name, ext = os.path.splitext(filename)
    counter = 1
    
    while True:
        new_filename = f"{name}_{counter}{ext}"
        new_path = Path(dest_dir) / new_filename
        if not new_path.exists():
            return new_filename
        counter += 1

def organize_files(folder_path, dry_run=False):
    """フォルダ内のファイルをカテゴリー別にサブフォルダへ移動"""
    folder_path = Path(folder_path)
    
    if not folder_path.exists():
        print(f"エラー: フォルダ '{folder_path}' が存在しません")
        return
    
    if not folder_path.is_dir():
        print(f"エラー: '{folder_path}' はフォルダではありません")
        return
    
    # ファイルをカテゴリー別に分類
    files_by_category = defaultdict(list)
    total_files = 0
    
    for item in folder_path.iterdir():
        if item.is_file():
            ext = item.suffix
            if ext:
                category = get_category(ext)
                files_by_category[category].append(item)
                total_files += 1
    
    if total_files == 0:
        print("移動するファイルがありません")
        return
    
    print(f"📁 フォルダ: {folder_path}")
    print(f"📊 合計ファイル数: {total_files}")
    print(f"🔄 ドライラン: {'はい' if dry_run else 'いいえ'}")
    print("-" * 60)
    
    total_moved = 0
    
    # カテゴリーごとにファイルを移動
    for category in sorted(files_by_category.keys()):
        category_dir = folder_path / category
        files = files_by_category[category]
        
        print(f"\n📂 カテゴリー: {category} ({len(files)} ファイル)")
        
        if not dry_run:
            category_dir.mkdir(exist_ok=True)
        
        for file_path in files:
            unique_filename = get_unique_filename(str(category_dir), file_path.name)
            dest_path = category_dir / unique_filename
            
            if file_path.name == unique_filename:
                print(f"  ✓ {file_path.name} → {category}/")
            else:
                print(f"  ✓ {file_path.name} → {category}/{unique_filename} (名前変更)")
            
            if not dry_run:
                shutil.move(str(file_path), str(dest_path))
            
            total_moved += 1
    
    print("\n" + "=" * 60)
    print(f"✅ 完了: {total_moved} ファイルを移動しました")

def main():
    parser = argparse.ArgumentParser(
        description='ファイルを拡張子ごとにサブフォルダへ整理するツール'
    )
    parser.add_argument(
        'folder',
        help='整理対象のフォルダパス'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='実際には移動せず計画のみ表示'
    )
    
    args = parser.parse_args()
    organize_files(args.folder, dry_run=args.dry_run)

if __name__ == '__main__':
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 18
```python
import os
import sys
import shutil
import argparse
from pathlib import Path
from collections import defaultdict

def get_file_category(extension):
    """ファイルの拡張子からカテゴリを決定"""
    extension = extension.lower()
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico', '.tiff'}
    doc_extensions = {'.pdf', '.doc', '.docx', '.txt', '.xlsx', '.xls', '.pptx', '.ppt', '.odt', '.csv'}
    archive_extensions = {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.iso'}
    
    if extension in image_extensions:
        return 'images'
    elif extension in doc_extensions:
        return 'docs'
    elif extension in archive_extensions:
        return 'archives'
    else:
        return 'others'

def get_unique_filename(target_path):
    """同名ファイルが存在する場合、連番を付けた新しいパスを返す"""
    if not target_path.exists():
        return target_path
    
    stem = target_path.stem
    suffix = target_path.suffix
    parent = target_path.parent
    counter = 1
    
    while True:
        new_name = f"{stem}_{counter}{suffix}"
        new_path = parent / new_name
        if not new_path.exists():
            return new_path
        counter += 1

def organize_files(folder_path, dry_run=False):
    """指定フォルダ内のファイルをカテゴリ別にサブフォルダへ移動"""
    folder = Path(folder_path)
    
    if not folder.is_dir():
        print(f"エラー: {folder_path} はディレクトリではありません")
        return
    
    # サブフォルダのリストを作成
    categories = ['images', 'docs', 'archives', 'others']
    
    # 移動計画を格納
    move_plan = defaultdict(list)
    
    # フォルダ内のすべてのファイルを処理
    for item in folder.iterdir():
        if item.is_file():
            extension = item.suffix
            if not extension:
                category = 'others'
            else:
                category = get_file_category(extension)
            
            target_dir = folder / category
            target_path = target_dir / item.name
            
            # ファイル名の衝突チェック
            if target_path.exists() or target_path in [Path(p) for p in move_plan[category]]:
                target_path = get_unique_filename(target_path)
            
            move_plan[category].append((item, target_path))
    
    # 計画を表示
    total_files = sum(len(files) for files in move_plan.values())
    print(f"移動計画: {total_files} 個のファイル")
    print("-" * 50)
    
    for category in categories:
        if move_plan[category]:
            print(f"\n【{category}/ へ移動】")
            for src, dst in move_plan[category]:
                if src.name == dst.name:
                    print(f"  {src.name} -> {category}/{src.name}")
                else:
                    print(f"  {src.name} -> {category}/{dst.name}")
    
    if dry_run:
        print("\n" + "=" * 50)
        print("ドライラン: 実際には移動しません")
        return
    
    # 実際にファイルを移動
    print("\n" + "=" * 50)
    print("ファイルを移動中...")
    
    for category in categories:
        if move_plan[category]:
            target_dir = folder / category
            target_dir.mkdir(exist_ok=True)
            
            for src, dst in move_plan[category]:
                try:
                    shutil.move(str(src), str(dst))
                    print(f"✓ {src.name} -> {category}/{dst.name}")
                except Exception as e:
                    print(f"✗ {src.name} の移動に失敗しました: {e}")
    
    print("\n完了しました")

def main():
    parser = argparse.ArgumentParser(
        description='指定フォルダ内のファイルを拡張子ごとにサブフォルダへ移動します'
    )
    parser.add_argument(
        'folder',
        nargs='?',
        default='.',
        help='対象フォルダのパス（デフォルト: カレントディレクトリ）'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='実際には移動せず計画のみ表示します'
    )
    
    args = parser.parse_args()
    
    organize_files(args.folder, dry_run=args.dry_run)

if __name__ == '__main__':
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 19
```python
#!/usr/bin/env python3

import argparse
import os
import shutil
from pathlib import Path
from collections import defaultdict

def get_file_category(file_path):
    """ファイルの拡張子からカテゴリを判定"""
    ext = Path(file_path).suffix.lower()
    
    image_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico', '.tiff'}
    doc_exts = {'.pdf', '.doc', '.docx', '.txt', '.xlsx', '.xls', '.ppt', '.pptx', '.odt', '.rtf', '.md'}
    archive_exts = {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.iso'}
    
    if ext in image_exts:
        return 'images'
    elif ext in doc_exts:
        return 'docs'
    elif ext in archive_exts:
        return 'archives'
    else:
        return 'others'

def get_unique_filename(target_path):
    """同名ファイルがある場合、連番を付けた新しいパスを返す"""
    if not target_path.exists():
        return target_path
    
    stem = target_path.stem
    suffix = target_path.suffix
    parent = target_path.parent
    counter = 1
    
    while True:
        new_name = f"{stem}_{counter}{suffix}"
        new_path = parent / new_name
        if not new_path.exists():
            return new_path
        counter += 1

def main():
    parser = argparse.ArgumentParser(
        description='指定フォルダ内のファイルを拡張子ごとにサブフォルダへ移動'
    )
    parser.add_argument('folder', help='対象フォルダのパス')
    parser.add_argument('--dry-run', action='store_true', help='実際には移動せず計画のみ表示')
    
    args = parser.parse_args()
    
    folder_path = Path(args.folder)
    
    if not folder_path.exists():
        print(f"エラー: フォルダ '{args.folder}' が見つかりません")
        return
    
    if not folder_path.is_dir():
        print(f"エラー: '{args.folder}' はフォルダではありません")
        return
    
    # 必要なサブフォルダを作成
    categories = ['images', 'docs', 'archives', 'others']
    subfolder_paths = {}
    
    for category in categories:
        subfolder = folder_path / category
        subfolder_paths[category] = subfolder
        if not args.dry_run and not subfolder.exists():
            subfolder.mkdir(exist_ok=True)
    
    # ファイル移動計画の集計
    move_plan = defaultdict(list)
    file_count = 0
    
    # フォルダ内のファイルを処理
    for file_path in folder_path.iterdir():
        # サブフォルダ自体は処理しない
        if file_path.is_dir():
            continue
        
        category = get_file_category(file_path)
        target_folder = subfolder_paths[category]
        target_path = target_folder / file_path.name
        
        # 同名ファイルがある場合は連番を付ける
        if target_path.exists():
            target_path = get_unique_filename(target_path)
        
        move_plan[category].append({
            'source': file_path,
            'target': target_path,
            'original_name': file_path.name,
            'new_name': target_path.name
        })
        file_count += 1
    
    # 移動計画を表示
    if file_count == 0:
        print("移動対象のファイルがありません")
        return
    
    print(f"{'[DRY-RUN] ' if args.dry_run else ''}移動計画:")
    print(f"総ファイル数: {file_count}")
    print()
    
    for category in categories:
        if move_plan[category]:
            print(f"📁 {category}/ ({len(move_plan[category])}ファイル)")
            for plan in move_plan[category]:
                if plan['original_name'] != plan['new_name']:
                    print(f"  • {plan['original_name']} → {plan['new_name']} (連番付与)")
                else:
                    print(f"  • {plan['original_name']}")
            print()
    
    # 実際に移動を実行
    if not args.dry_run:
        print("ファイルを移動中...")
        total_moved = 0
        for category in categories:
            for plan in move_plan[category]:
                try:
                    shutil.move(str(plan['source']), str(plan['target']))
                    total_moved += 1
                except Exception as e:
                    print(f"エラー: {plan['source']} の移動に失敗しました: {e}")
        
        print(f"✓ {total_moved}個のファイルを移動しました")
    else:
        print("(--dry-runオプションが指定されているため、実際には移動されません)")

if __name__ == '__main__':
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 20
```python
import os
import sys
import argparse
from pathlib import Path
from anthropic import Anthropic

# File type categories
FILE_CATEGORIES = {
    'images': {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico', '.tiff'},
    'docs': {'.pdf', '.doc', '.docx', '.txt', '.xlsx', '.xls', '.ppt', '.pptx', '.odt', '.csv'},
    'archives': {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz'},
}

def get_category(file_extension):
    """Determine the category for a file based on its extension."""
    ext = file_extension.lower()
    for category, extensions in FILE_CATEGORIES.items():
        if ext in extensions:
            return category
    return 'others'

def get_unique_filename(target_path):
    """Generate a unique filename if the target already exists."""
    if not target_path.exists():
        return target_path
    
    stem = target_path.stem
    suffix = target_path.suffix
    parent = target_path.parent
    counter = 1
    
    while True:
        new_name = f"{stem}_{counter}{suffix}"
        new_path = parent / new_name
        if not new_path.exists():
            return new_path
        counter += 1

def plan_file_moves(folder_path, dry_run=False):
    """Plan and execute file moves with Claude assistance."""
    client = Anthropic()
    conversation_history = []
    
    folder = Path(folder_path)
    if not folder.is_dir():
        print(f"Error: {folder_path} is not a valid directory")
        sys.exit(1)
    
    # Gather file information
    files_to_move = []
    for file_path in folder.glob('*'):
        if file_path.is_file():
            ext = file_path.suffix
            category = get_category(ext)
            files_to_move.append({
                'name': file_path.name,
                'path': file_path,
                'extension': ext,
                'category': category
            })
    
    if not files_to_move:
        print("No files found to move.")
        return
    
    # Create initial plan message
    file_info = "\n".join([
        f"- {f['name']} (extension: {f['extension']}, category: {f['category']})"
        for f in files_to_move
    ])
    
    initial_message = f"""I need to organize {len(files_to_move)} files in the folder '{folder_path}' into subdirectories by type.

Files to organize:
{file_info}

Categories:
- images: for image files (.jpg, .jpeg, .png, .gif, .bmp, .svg, .webp, .ico, .tiff)
- docs: for document files (.pdf, .doc, .docx, .txt, .xlsx, .xls, .ppt, .pptx, .odt, .csv)
- archives: for archive files (.zip, .rar, .7z, .tar, .gz, .bz2, .xz)
- others: for any other file types

Please review this organization plan and suggest any improvements or special considerations."""
    
    conversation_history.append({
        "role": "user",
        "content": initial_message
    })
    
    # Get Claude's review of the plan
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=conversation_history
    )
    
    claude_review = response.content[0].text
    conversation_history.append({
        "role": "assistant",
        "content": claude_review
    })
    
    print("=== Organization Plan Review ===")
    print(claude_review)
    print()
    
    # Ask Claude for confirmation and get the final plan
    confirmation_message = """Based on your review, please provide a clear summary of:
1. Which files will be moved to which directories
2. Any files that might need special handling
3. Any potential issues to be aware of

Format the response as a structured plan that I can execute."""
    
    conversation_history.append({
        "role": "user",
        "content": confirmation_message
    })
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=conversation_history
    )
    
    claude_plan = response.content[0].text
    conversation_history.append({
        "role": "assistant",
        "content": claude_plan
    })
    
    print("=== Detailed Organization Plan ===")
    print(claude_plan)
    print()
    
    # Execute the moves
    print("=== Execution Details ===")
    
    moves_executed = 0
    for file_info in files_to_move:
        category_folder = folder / file_info['category']
        
        if dry_run:
            print(f"[DRY RUN] Would move: {file_info['name']} -> {file_info['category']}/")
        else:
            # Create category folder if it doesn't exist
            category_folder.mkdir(exist_ok=True)
            
            # Get unique filename if collision
            target_path = get_unique_filename(category_folder / file_info['name'])
            
            # Move the file
            file_info['path'].rename(target_path)
            actual_name = target_path.name
            if actual_name != file_info['name']:
                print(f"Moved: {file_info['name']} -> {file_info['category']}/{actual_name} (renamed due to collision)")
            else:
                print(f"Moved: {file_info['name']} -> {file_info['category']}/")
            moves_executed += 1
    
    # Final summary
    print()
    if dry_run:
        print(f"[DRY RUN] Would organize {len(files_to_move)} files into {len(set(f['category'] for f in files_to_move))} categories")
    else:
        print(f"Successfully organized {moves_executed} files into categories")
    
    # Ask Claude for final recommendations
    if not dry_run:
        final_message = f"I've successfully organized {moves_executed} files into their respective categories. Are there any additional recommendations for file management or organization best practices I should consider?"
        
        conversation_history.append({
            "role": "user",
            "content": final_message
        })
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=512,
            messages=conversation_history
        )
        
        print("\n=== Additional Recommendations ===")
        print(response.content[0].text)

def main():
    parser = argparse.ArgumentParser(
        description='Organize files in a folder into category-based subdirectories with Claude assistance'
    )
    parser.add_argument('folder', help='Path to the folder containing files to organize')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be done without actually moving files')
    
    args = parser.parse_args()
    
    plan_file_moves(args.folder, dry_run=args.dry_run)

if __name__ == '__main__':
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 21
```python
import os
import sys
import shutil
from pathlib import Path
from anthropic import Anthropic

def main():
    client = Anthropic()
    conversation_history = []
    
    system_prompt = """You are a helpful assistant that helps users organize files in a folder by extension.
    
When the user wants to organize files, help them by:
1. Understanding the source folder path
2. Confirming the file organization rules:
   - images/: .jpg, .jpeg, .png, .gif, .bmp, .svg, .webp, .ico, .tiff
   - docs/: .pdf, .doc, .docx, .txt, .xlsx, .xls, .ppt, .pptx, .odt, .csv
   - archives/: .zip, .tar, .gz, .rar, .7z, .bz2, .xz
   - others/: everything else
3. Asking if they want a --dry-run first to see what would happen
4. Confirming before actually moving files
5. Providing feedback on what was done

Always be helpful and ask clarifying questions when needed. When the user is ready to proceed, provide the necessary Python code to execute the file organization."""
    
    print("File Organization Assistant")
    print("=" * 50)
    print("I'll help you organize files in a folder by extension.")
    print("Type 'quit' to exit.\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() == 'quit':
            print("Goodbye!")
            break
        
        if not user_input:
            continue
        
        conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=8096,
            system=system_prompt,
            messages=conversation_history
        )
        
        assistant_message = response.content[0].text
        conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })
        
        print(f"\nAssistant: {assistant_message}\n")
        
        if "execute" in assistant_message.lower() or "run" in assistant_message.lower():
            print("\n[Note: To actually execute file organization, please use the organize_files function directly]")

def organize_files(source_folder, dry_run=True):
    """
    Organize files in the specified folder into subfolders by extension.
    
    Args:
        source_folder: Path to the folder containing files to organize
        dry_run: If True, only show what would be done without actually moving files
    """
    
    file_categories = {
        'images': {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico', '.tiff'},
        'docs': {'.pdf', '.doc', '.docx', '.txt', '.xlsx', '.xls', '.ppt', '.pptx', '.odt', '.csv'},
        'archives': {'.zip', '.tar', '.gz', '.rar', '.7z', '.bz2', '.xz'},
    }
    
    source_path = Path(source_folder)
    
    if not source_path.exists():
        print(f"Error: Folder '{source_folder}' does not exist.")
        return
    
    if not source_path.is_dir():
        print(f"Error: '{source_folder}' is not a directory.")
        return
    
    files_to_move = []
    
    for file_path in source_path.iterdir():
        if file_path.is_file():
            extension = file_path.suffix.lower()
            
            category = 'others'
            for cat, exts in file_categories.items():
                if extension in exts:
                    category = cat
                    break
            
            files_to_move.append((file_path, category))
    
    if not files_to_move:
        print(f"No files found in '{source_folder}'")
        return
    
    print(f"\n{'DRY RUN - ' if dry_run else ''}File Organization Plan:")
    print("=" * 60)
    
    moves_by_category = {}
    for file_path, category in files_to_move:
        if category not in moves_by_category:
            moves_by_category[category] = []
        moves_by_category[category].append(file_path)
    
    for category in sorted(moves_by_category.keys()):
        print(f"\n{category.upper()}/")
        for file_path in sorted(moves_by_category[category]):
            print(f"  → {file_path.name}")
    
    if dry_run:
        print(f"\n{len(files_to_move)} file(s) would be organized.")
        print("Run with dry_run=False to actually move the files.")
        return
    
    print(f"\nMoving {len(files_to_move)} file(s)...")
    
    moved_count = 0
    for file_path, category in files_to_move:
        category_folder = source_path / category
        category_folder.mkdir(exist_ok=True)
        
        target_path = category_folder / file_path.name
        
        counter = 1
        while target_path.exists():
            name_parts = file_path.name.rsplit('.', 1)
            if len(name_parts) == 2:
                target_path = category_folder / f"{name_parts[0]}_{counter}.{name_parts[1]}"
            else:
                target_path = category_folder / f"{file_path.name}_{counter}"
            counter += 1
        
        try:
            shutil.move(str(file_path), str(target_path))
            print(f"  ✓ Moved '{file_path.name}' to '{category}/'")
            moved_count += 1
        except Exception as e:
            print(f"  ✗ Failed to move '{file_path.name}': {e}")
    
    print(f"\n{moved_count} file(s) successfully organized!")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        folder = sys.argv[1]
        dry_run = "--dry-run" in sys.argv or "-d" in sys.argv
        organize_files(folder, dry_run=dry_run)
    else:
        main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 22
```python
#!/usr/bin/env python3
import anthropic
import argparse
import json
import os
import shutil
from pathlib import Path

def categorize_file(filename: str) -> str:
    """ファイルを拡張子に基づいてカテゴリ分類"""
    extension = Path(filename).suffix.lower()
    
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico', '.tiff'}
    doc_extensions = {'.pdf', '.doc', '.docx', '.txt', '.xlsx', '.xls', '.ppt', '.pptx', '.odt', '.rtf'}
    archive_extensions = {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.iso'}
    
    if extension in image_extensions:
        return 'images'
    elif extension in doc_extensions:
        return 'docs'
    elif extension in archive_extensions:
        return 'archives'
    else:
        return 'others'

def get_unique_filename(target_path: Path) -> Path:
    """同名ファイルが存在する場合、連番を付けた新しいパスを返す"""
    if not target_path.exists():
        return target_path
    
    stem = target_path.stem
    suffix = target_path.suffix
    parent = target_path.parent
    counter = 1
    
    while True:
        new_name = f"{stem}_{counter}{suffix}"
        new_path = parent / new_name
        if not new_path.exists():
            return new_path
        counter += 1

def plan_file_moves(folder_path: str, dry_run: bool = True) -> dict:
    """ファイル移動計画を作成"""
    folder = Path(folder_path)
    
    if not folder.exists():
        return {"error": f"フォルダが見つかりません: {folder_path}"}
    
    if not folder.is_dir():
        return {"error": f"ディレクトリではありません: {folder_path}"}
    
    plan = {
        "source_folder": str(folder),
        "dry_run": dry_run,
        "moves": [],
        "summary": {
            "total_files": 0,
            "moved_files": 0,
            "categories": {}
        }
    }
    
    # フォルダ内のファイルを列挙
    for item in folder.iterdir():
        if item.is_file():
            plan["summary"]["total_files"] += 1
            category = categorize_file(item.name)
            
            if category not in plan["summary"]["categories"]:
                plan["summary"]["categories"][category] = 0
            plan["summary"]["categories"][category] += 1
            
            target_dir = folder / category
            target_path = target_dir / item.name
            unique_path = get_unique_filename(target_path)
            
            move_info = {
                "source": str(item),
                "destination": str(unique_path),
                "category": category,
                "filename": item.name,
                "renamed": item.name != unique_path.name
            }
            
            plan["moves"].append(move_info)
            plan["summary"]["moved_files"] += 1
    
    return plan

def execute_moves(plan: dict) -> dict:
    """計画に基づいてファイルを移動"""
    results = {
        "executed": not plan.get("dry_run", True),
        "success_count": 0,
        "error_count": 0,
        "errors": []
    }
    
    if plan.get("dry_run"):
        results["message"] = "ドライラン: 実際には移動されていません"
        return results
    
    for move in plan["moves"]:
        try:
            source = Path(move["source"])
            destination = Path(move["destination"])
            
            # ターゲットディレクトリを作成
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            # ファイルを移動
            shutil.move(str(source), str(destination))
            results["success_count"] += 1
        except Exception as e:
            results["error_count"] += 1
            results["errors"].append({
                "file": move["filename"],
                "error": str(e)
            })
    
    return results

def main():
    parser = argparse.ArgumentParser(
        description="指定フォルダ内のファイルを拡張子ごとにサブフォルダへ移動します"
    )
    parser.add_argument("folder", help="処理対象フォルダのパス")
    parser.add_argument("--dry-run", action="store_true", help="実行計画のみ表示し、実際には移動しません")
    parser.add_argument("--execute", action="store_true", help="計画を実行してファイルを移動します")
    
    args = parser.parse_args()
    
    # 計画を作成
    plan = plan_file_moves(args.folder, dry_run=not args.execute)
    
    if "error" in plan:
        print(f"エラー: {plan['error']}")
        return
    
    # Claude APIを使用して計画を分析・最適化
    client = anthropic.Anthropic()
    
    analysis_prompt = f"""次のファイル移動計画を分析してください:
    
計画内容:
- 対象フォルダ: {plan['source_folder']}
- ドライラン: {plan['dry_run']}
- 総ファイル数: {plan['summary']['total_files']}
- カテゴリ分類: {json.dumps(plan['summary']['categories'], ensure_ascii=False)}

以下の質問に答えてください:
1. この分類が適切か判断してください
2. 潜在的な問題があるか指摘してください
3. 実行前に確認すべき項目を提案してください

簡潔に日本語で回答してください。"""
    
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": analysis_prompt}
        ]
    )
    
    analysis = message.content[0].text
    
    # 結果を表示
    print("=" * 60)
    print("ファイル移動計画")
    print("=" * 60)
    print(f"対象フォルダ: {plan['source_folder']}")
    print(f"モード: {'ドライラン (実行なし)' if plan['dry_run'] else '実行モード'}")
    print()
    
    print("分類結果:")
    print("-" * 40)
    for category, count in plan['summary']['categories'].items():
        print(f"  {category}/: {count}ファイル")
    print()
    
    print("移動予定:")
    print("-" * 40)
    for move in plan['moves'][:10]:  # 最初の10個を表示
        renamed_msg = f" (→ {move['filename']}に変更)" if move['renamed'] else ""
        print(f"  {move['filename']} → {move['category']}/{move['destination'].split('/')[-1]}{renamed_msg}")
    
    if len(plan['moves']) > 10:
        print(f"  ... 他 {len(plan['moves']) - 10}ファイル")
    print()
    
    print("Claude による分析:")
    print("-" * 40)
    print(analysis)
    print()
    
    if not plan['dry_run']:
        # 実行
        print("ファイルを移動中...")
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 23
```python
#!/usr/bin/env python3
import os
import sys
import shutil
import argparse
from pathlib import Path
from collections import defaultdict

def get_file_category(extension):
    """ファイルの拡張子からカテゴリを決定"""
    extension = extension.lower().lstrip('.')
    
    image_exts = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp', 'ico', 'tiff'}
    doc_exts = {'pdf', 'doc', 'docx', 'txt', 'xlsx', 'xls', 'pptx', 'ppt', 'csv', 'rtf', 'odt'}
    archive_exts = {'zip', 'rar', '7z', 'tar', 'gz', 'bz2', 'iso'}
    
    if extension in image_exts:
        return 'images'
    elif extension in doc_exts:
        return 'docs'
    elif extension in archive_exts:
        return 'archives'
    else:
        return 'others'

def get_unique_path(destination_path):
    """同名ファイルが存在する場合、連番を付けた新しいパスを返す"""
    if not destination_path.exists():
        return destination_path
    
    stem = destination_path.stem
    suffix = destination_path.suffix
    parent = destination_path.parent
    
    counter = 1
    while True:
        new_name = f"{stem}_{counter}{suffix}"
        new_path = parent / new_name
        if not new_path.exists():
            return new_path
        counter += 1

def organize_files(folder_path, dry_run=False):
    """フォルダ内のファイルを拡張子ごとにサブフォルダへ移動"""
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"エラー: フォルダ '{folder_path}' が見つかりません")
        return False
    
    if not folder.is_dir():
        print(f"エラー: '{folder_path}' はフォルダではありません")
        return False
    
    # サブフォルダを作成
    categories = {'images', 'docs', 'archives', 'others'}
    for category in categories:
        category_folder = folder / category
        if not category_folder.exists():
            if not dry_run:
                category_folder.mkdir(parents=True, exist_ok=True)
                print(f"作成: {category_folder}")
            else:
                print(f"[DRY-RUN] 作成: {category_folder}")
    
    # ファイルを移動
    operations = defaultdict(list)
    
    for file_path in folder.iterdir():
        # サブフォルダは除外
        if file_path.is_dir():
            continue
        
        # 隠しファイルは除外
        if file_path.name.startswith('.'):
            continue
        
        extension = file_path.suffix
        category = get_file_category(extension)
        destination_folder = folder / category
        destination_path = destination_folder / file_path.name
        
        # 同名ファイルの衝突処理
        if destination_path.exists():
            destination_path = get_unique_path(destination_path)
        
        operations[category].append({
            'source': file_path,
            'destination': destination_path,
            'original_name': file_path.name,
            'new_name': destination_path.name
        })
    
    # 操作を表示・実行
    total_files = sum(len(files) for files in operations.values())
    
    if total_files == 0:
        print("移動するファイルがありません")
        return True
    
    print(f"\n{'[DRY-RUN] ' if dry_run else ''}計画: {total_files} 個のファイルを移動します\n")
    
    for category in sorted(operations.keys()):
        files = operations[category]
        print(f"【{category}】({len(files)}個)")
        
        for op in files:
            if op['original_name'] == op['new_name']:
                print(f"  {op['original_name']} → {category}/")
            else:
                print(f"  {op['original_name']} → {category}/{op['new_name']} (名前変更)")
            
            if not dry_run:
                try:
                    shutil.move(str(op['source']), str(op['destination']))
                except Exception as e:
                    print(f"    エラー: {e}")
                    return False
        
        print()
    
    if not dry_run:
        print(f"✓ {total_files} 個のファイルを移動しました")
    else:
        print("[DRY-RUN] 実際には移動しません")
    
    return True

def main():
    parser = argparse.ArgumentParser(
        description='フォルダ内のファイルを拡張子ごとにサブフォルダへ移動します'
    )
    parser.add_argument(
        'folder',
        help='対象フォルダのパス'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='実際には移動せず、計画のみ表示します'
    )
    
    args = parser.parse_args()
    
    success = organize_files(args.folder, dry_run=args.dry_run)
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 24
```python
import argparse
import os
import shutil
from pathlib import Path
from collections import defaultdict

def get_extension_category(extension):
    """ファイルの拡張子からカテゴリを決定する"""
    extension = extension.lower().lstrip('.')
    
    image_extensions = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp', 'ico', 'tiff'}
    doc_extensions = {'pdf', 'doc', 'docx', 'txt', 'xls', 'xlsx', 'ppt', 'pptx', 'odt'}
    archive_extensions = {'zip', 'rar', '7z', 'tar', 'gz', 'bz2', 'xz'}
    
    if extension in image_extensions:
        return 'images'
    elif extension in doc_extensions:
        return 'docs'
    elif extension in archive_extensions:
        return 'archives'
    else:
        return 'others'

def get_unique_filename(target_path):
    """同名ファイルがある場合は連番を付ける"""
    if not target_path.exists():
        return target_path
    
    stem = target_path.stem
    suffix = target_path.suffix
    parent = target_path.parent
    
    counter = 1
    while True:
        new_name = f"{stem}_{counter}{suffix}"
        new_path = parent / new_name
        if not new_path.exists():
            return new_path
        counter += 1

def organize_files(folder_path, dry_run=False):
    """指定フォルダ内のファイルを拡張子ごとにサブフォルダへ移動"""
    folder = Path(folder_path)
    
    if not folder.is_dir():
        print(f"エラー: {folder_path} はフォルダではありません")
        return
    
    # サブフォルダを作成
    subfolder_categories = ['images', 'docs', 'archives', 'others']
    subfolder_paths = {}
    
    for category in subfolder_categories:
        subfolder_path = folder / category
        subfolder_paths[category] = subfolder_path
        if not dry_run and not subfolder_path.exists():
            subfolder_path.mkdir(parents=True, exist_ok=True)
    
    # ファイルを移動
    files_moved = defaultdict(list)
    
    for file_path in folder.iterdir():
        if file_path.is_file():
            extension = file_path.suffix
            category = get_extension_category(extension)
            target_folder = subfolder_paths[category]
            
            target_path = target_folder / file_path.name
            target_path = get_unique_filename(target_path)
            
            files_moved[category].append({
                'from': str(file_path),
                'to': str(target_path),
                'original_name': file_path.name,
                'new_name': target_path.name
            })
            
            if not dry_run:
                shutil.move(str(file_path), str(target_path))
    
    # 結果を表示
    if dry_run:
        print("=== ドライラン: 以下のファイルが移動されます ===\n")
    else:
        print("=== ファイルの移動が完了しました ===\n")
    
    total_files = 0
    for category in subfolder_categories:
        if files_moved[category]:
            print(f"【{category.upper()}】")
            for file_info in files_moved[category]:
                if file_info['original_name'] != file_info['new_name']:
                    print(f"  {file_info['original_name']} → {file_info['new_name']}")
                else:
                    print(f"  {file_info['original_name']}")
                total_files += 1
            print()
    
    if total_files == 0:
        print("移動するファイルはありません")
    else:
        print(f"合計: {total_files} 個のファイルが移動されました")

def main():
    parser = argparse.ArgumentParser(
        description='指定フォルダ内のファイルを拡張子ごとにサブフォルダへ移動します',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python solution.py /path/to/folder              # ファイルを移動
  python solution.py /path/to/folder --dry-run    # 移動計画のみ表示
        """
    )
    
    parser.add_argument(
        'folder',
        help='対象フォルダのパス'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='実際には移動せず計画のみ表示'
    )
    
    args = parser.parse_args()
    
    organize_files(args.folder, dry_run=args.dry_run)

if __name__ == '__main__':
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 25
```python
import os
import sys
import argparse
import shutil
from pathlib import Path
from collections import defaultdict


def get_subfolder_for_extension(ext):
    """ファイルの拡張子からサブフォルダを決定"""
    ext = ext.lower()
    
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico', '.tiff'}
    doc_extensions = {'.pdf', '.doc', '.docx', '.txt', '.xlsx', '.xls', '.ppt', '.pptx', '.odt', '.csv'}
    archive_extensions = {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.iso'}
    
    if ext in image_extensions:
        return 'images'
    elif ext in doc_extensions:
        return 'docs'
    elif ext in archive_extensions:
        return 'archives'
    else:
        return 'others'


def get_unique_filename(target_dir, filename):
    """ファイル名が重複する場合は連番を付ける"""
    filepath = os.path.join(target_dir, filename)
    
    if not os.path.exists(filepath):
        return filename
    
    # ファイル名を分割
    name, ext = os.path.splitext(filename)
    counter = 1
    
    while True:
        new_filename = f"{name}_{counter}{ext}"
        new_filepath = os.path.join(target_dir, new_filename)
        if not os.path.exists(new_filepath):
            return new_filename
        counter += 1


def organize_files(folder_path, dry_run=False):
    """指定フォルダ内のファイルを拡張子ごとにサブフォルダへ移動"""
    
    folder_path = Path(folder_path)
    
    if not folder_path.exists():
        print(f"エラー: フォルダ '{folder_path}' が見つかりません")
        return
    
    if not folder_path.is_dir():
        print(f"エラー: '{folder_path}' はフォルダではありません")
        return
    
    # サブフォルダの作成計画
    subfolders = {'images', 'docs', 'archives', 'others'}
    
    # ファイル移動計画を保存
    move_plan = defaultdict(list)
    
    # ファイルをスキャン
    for item in folder_path.iterdir():
        if item.is_file():
            ext = item.suffix
            subfolder = get_subfolder_for_extension(ext)
            move_plan[subfolder].append(item.name)
    
    if not move_plan:
        print("移動するファイルがありません")
        return
    
    # 計画を表示
    print("=" * 60)
    print("ファイル移動計画")
    print("=" * 60)
    
    total_files = 0
    for subfolder in sorted(move_plan.keys()):
        files = move_plan[subfolder]
        print(f"\n[{subfolder}/] へ移動:")
        for filename in sorted(files):
            print(f"  - {filename}")
        print(f"  合計: {len(files)} ファイル")
        total_files += len(files)
    
    print(f"\n合計移動ファイル数: {total_files}")
    
    if dry_run:
        print("\n[DRY-RUN モード] 実際の移動は行いません")
        return
    
    # 実際にファイルを移動
    print("\n" + "=" * 60)
    print("ファイルを移動中...")
    print("=" * 60)
    
    for subfolder, files in move_plan.items():
        subfolder_path = folder_path / subfolder
        
        # サブフォルダを作成
        subfolder_path.mkdir(exist_ok=True)
        
        for filename in files:
            source_path = folder_path / filename
            
            # ユニークなファイル名を取得
            unique_filename = get_unique_filename(str(subfolder_path), filename)
            target_path = subfolder_path / unique_filename
            
            try:
                shutil.move(str(source_path), str(target_path))
                if unique_filename != filename:
                    print(f"✓ {filename} → {subfolder}/{unique_filename}")
                else:
                    print(f"✓ {filename} → {subfolder}/")
            except Exception as e:
                print(f"✗ {filename} の移動に失敗: {e}")
    
    print("\n完了!")


def main():
    parser = argparse.ArgumentParser(
        description='指定フォルダ内のファイルを拡張子ごとにサブフォルダへ移動'
    )
    parser.add_argument(
        'folder',
        help='対象フォルダのパス'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='実際には移動せず計画のみ表示'
    )
    
    args = parser.parse_args()
    
    organize_files(args.folder, dry_run=args.dry_run)


if __name__ == '__main__':
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 26
```python
import os
import sys
import shutil
import argparse
from pathlib import Path
from collections import defaultdict

def get_file_category(extension):
    """ファイルの拡張子からカテゴリを判定"""
    extension = extension.lower()
    
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico', '.tiff'}
    doc_extensions = {'.txt', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.odt', '.csv', '.md'}
    archive_extensions = {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.iso'}
    
    if extension in image_extensions:
        return 'images'
    elif extension in doc_extensions:
        return 'docs'
    elif extension in archive_extensions:
        return 'archives'
    else:
        return 'others'

def get_unique_filename(target_dir, filename):
    """同名ファイルがある場合は連番を付けた名前を返す"""
    path = Path(target_dir) / filename
    
    if not path.exists():
        return filename
    
    name, ext = os.path.splitext(filename)
    counter = 1
    
    while True:
        new_filename = f"{name}_{counter}{ext}"
        new_path = Path(target_dir) / new_filename
        if not new_path.exists():
            return new_filename
        counter += 1

def organize_files(folder_path, dry_run=False):
    """指定フォルダ内のファイルをカテゴリ別に整理"""
    folder_path = Path(folder_path)
    
    if not folder_path.exists():
        print(f"エラー: フォルダ '{folder_path}' が見つかりません")
        return
    
    if not folder_path.is_dir():
        print(f"エラー: '{folder_path}' はフォルダではありません")
        return
    
    # カテゴリフォルダを作成
    categories = ['images', 'docs', 'archives', 'others']
    category_dirs = {}
    
    for category in categories:
        category_path = folder_path / category
        category_dirs[category] = category_path
        if not category_path.exists() and not dry_run:
            category_path.mkdir(parents=True, exist_ok=True)
    
    # ファイルを分類
    file_moves = defaultdict(list)
    file_count = 0
    
    for item in folder_path.iterdir():
        # フォルダやサブフォルダは除外
        if item.is_dir():
            continue
        
        # 隠しファイルは除外
        if item.name.startswith('.'):
            continue
        
        extension = item.suffix
        category = get_file_category(extension)
        
        target_dir = category_dirs[category]
        unique_filename = get_unique_filename(str(target_dir), item.name)
        
        file_moves[category].append({
            'source': item,
            'filename': item.name,
            'target_filename': unique_filename,
            'target_dir': target_dir
        })
        file_count += 1
    
    # 移動計画を表示
    if file_count == 0:
        print(f"移動するファイルがありません")
        return
    
    print(f"{'[DRY RUN]' if dry_run else '[実行]'} {file_count} 個のファイルを整理します\n")
    
    total_moved = 0
    for category in categories:
        if file_moves[category]:
            print(f"📁 {category}/ へ移動:")
            for move_info in file_moves[category]:
                source_path = move_info['source']
                target_filename = move_info['target_filename']
                
                if move_info['filename'] == target_filename:
                    print(f"  • {move_info['filename']}")
                else:
                    print(f"  • {move_info['filename']} → {target_filename}")
                
                if not dry_run:
                    target_path = move_info['target_dir'] / target_filename
                    shutil.move(str(source_path), str(target_path))
                
                total_moved += 1
            print()
    
    if dry_run:
        print(f"✓ ドライラン完了: {total_moved} 個のファイルが移動されます")
    else:
        print(f"✓ 完了: {total_moved} 個のファイルが移動されました")

def main():
    parser = argparse.ArgumentParser(
        description='指定フォルダ内のファイルを拡張子ごとにサブフォルダへ移動します',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用例:
  python solution.py /path/to/folder              # ファイルを移動
  python solution.py /path/to/folder --dry-run    # 計画のみ表示
        '''
    )
    
    parser.add_argument(
        'folder',
        help='整理対象のフォルダパス'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='実際には移動せず計画のみ表示'
    )
    
    args = parser.parse_args()
    
    organize_files(args.folder, dry_run=args.dry_run)

if __name__ == '__main__':
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 27
```python
import os
import sys
import argparse
import shutil
from pathlib import Path
from collections import defaultdict

def get_file_category(file_extension):
    """ファイル拡張子からカテゴリを決定"""
    extension = file_extension.lower().lstrip('.')
    
    image_extensions = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp', 'ico', 'tiff'}
    doc_extensions = {'pdf', 'doc', 'docx', 'txt', 'xlsx', 'xls', 'ppt', 'pptx', 'csv', 'json', 'xml', 'md'}
    archive_extensions = {'zip', 'rar', '7z', 'tar', 'gz', 'bz2', 'xz'}
    
    if extension in image_extensions:
        return 'images'
    elif extension in doc_extensions:
        return 'docs'
    elif extension in archive_extensions:
        return 'archives'
    else:
        return 'others'

def get_unique_filename(dest_path):
    """衝突時に連番を付けた一意なファイル名を生成"""
    if not dest_path.exists():
        return dest_path
    
    stem = dest_path.stem
    suffix = dest_path.suffix
    parent = dest_path.parent
    counter = 1
    
    while True:
        new_name = f"{stem}_{counter}{suffix}"
        new_path = parent / new_name
        if not new_path.exists():
            return new_path
        counter += 1

def organize_files(folder_path, dry_run=False):
    """フォルダ内のファイルをカテゴリ別に整理"""
    folder = Path(folder_path)
    
    if not folder.is_dir():
        print(f"エラー: {folder_path} はディレクトリではありません")
        sys.exit(1)
    
    # サブフォルダを作成（dry-runでない場合）
    categories = {'images', 'docs', 'archives', 'others'}
    subfolders = {cat: folder / cat for cat in categories}
    
    if not dry_run:
        for subfolder in subfolders.values():
            subfolder.mkdir(exist_ok=True)
    
    # ファイルを分類
    operations = defaultdict(list)
    
    for item in folder.iterdir():
        if item.is_file():
            category = get_file_category(item.suffix)
            dest_folder = subfolders[category]
            dest_path = dest_folder / item.name
            dest_path = get_unique_filename(dest_path)
            
            operations[category].append({
                'src': item,
                'dest': dest_path,
                'original_name': item.name,
                'new_name': dest_path.name
            })
    
    # 計画を表示
    if not operations:
        print("移動するファイルがありません")
        return
    
    print("=" * 60)
    print(f"{'ドライラン' if dry_run else '実行'} - ファイル移動計画")
    print("=" * 60)
    
    total_files = 0
    for category in ['images', 'docs', 'archives', 'others']:
        if category in operations:
            print(f"\n【{category}/】")
            for op in operations[category]:
                total_files += 1
                src_rel = op['src'].relative_to(folder)
                dest_rel = op['dest'].relative_to(folder)
                
                if op['original_name'] != op['new_name']:
                    print(f"  {src_rel} → {dest_rel} (連番付与)")
                else:
                    print(f"  {src_rel} → {dest_rel}")
    
    print("\n" + "=" * 60)
    print(f"合計: {total_files} ファイル")
    
    # 実際に移動（dry-runでない場合）
    if not dry_run:
        print("\n移動を実行中...")
        for category in operations:
            for op in operations[category]:
                shutil.move(str(op['src']), str(op['dest']))
                print(f"✓ 移動完了: {op['src'].name} → {op['dest'].relative_to(folder)}")
        print("\n完了しました")

def main():
    parser = argparse.ArgumentParser(
        description='指定フォルダ内のファイルを拡張子ごとにサブフォルダへ移動'
    )
    parser.add_argument(
        'folder',
        help='対象フォルダのパス'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='実際には移動せず計画のみ表示'
    )
    
    args = parser.parse_args()
    
    organize_files(args.folder, dry_run=args.dry_run)

if __name__ == '__main__':
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 28
```python
import os
import sys
import shutil
from pathlib import Path
import argparse
from collections import defaultdict

def get_category(file_extension):
    """Get category folder for file extension"""
    extension = file_extension.lower().lstrip('.')
    
    image_extensions = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp', 'ico', 'tiff'}
    doc_extensions = {'pdf', 'doc', 'docx', 'txt', 'xlsx', 'xls', 'ppt', 'pptx', 'odt', 'ods', 'odp'}
    archive_extensions = {'zip', 'rar', '7z', 'tar', 'gz', 'bz2', 'xz'}
    
    if extension in image_extensions:
        return 'images'
    elif extension in doc_extensions:
        return 'docs'
    elif extension in archive_extensions:
        return 'archives'
    else:
        return 'others'

def get_unique_filename(target_path):
    """Generate unique filename if file exists"""
    if not target_path.exists():
        return target_path
    
    stem = target_path.stem
    suffix = target_path.suffix
    parent = target_path.parent
    counter = 1
    
    while True:
        new_name = f"{stem}_{counter}{suffix}"
        new_path = parent / new_name
        if not new_path.exists():
            return new_path
        counter += 1

def organize_files(source_folder, dry_run=False):
    """Organize files in source folder into category subfolders"""
    source_path = Path(source_folder)
    
    if not source_path.exists():
        print(f"Error: Folder '{source_folder}' does not exist.")
        sys.exit(1)
    
    if not source_path.is_dir():
        print(f"Error: '{source_folder}' is not a directory.")
        sys.exit(1)
    
    # Create category folders if they don't exist
    categories = {'images', 'docs', 'archives', 'others'}
    category_paths = {}
    
    for category in categories:
        cat_path = source_path / category
        category_paths[category] = cat_path
        if not dry_run and not cat_path.exists():
            cat_path.mkdir(exist_ok=True)
    
    # Collect files to move
    moves = defaultdict(list)
    total_files = 0
    
    for item in source_path.iterdir():
        if item.is_file():
            if item.name.startswith('.'):
                continue
            
            total_files += 1
            file_extension = item.suffix
            category = get_category(file_extension)
            target_folder = category_paths[category]
            target_path = target_folder / item.name
            
            # Check for name collision
            if target_path.exists():
                target_path = get_unique_filename(target_path)
            
            moves[category].append({
                'source': item,
                'target': target_path,
                'original_name': item.name,
                'new_name': target_path.name
            })
    
    # Display plan
    print("=" * 60)
    print(f"File Organization Plan for: {source_folder}")
    print(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")
    print("=" * 60)
    
    if total_files == 0:
        print("No files to organize.")
        return
    
    total_moves = sum(len(files) for files in moves.values())
    print(f"Total files found: {total_files}")
    print(f"Files to move: {total_moves}\n")
    
    for category in sorted(moves.keys()):
        files = moves[category]
        print(f"\n{category.upper()} ({len(files)} files):")
        print("-" * 40)
        
        for move in files:
            if move['original_name'] == move['new_name']:
                print(f"  {move['original_name']} -> {category}/")
            else:
                print(f"  {move['original_name']} -> {category}/{move['new_name']} (renamed)")
    
    # Execute moves if not dry run
    if not dry_run:
        print("\n" + "=" * 60)
        print("Executing moves...")
        print("=" * 60)
        
        total_moved = 0
        for category in moves:
            for move in moves[category]:
                try:
                    shutil.move(str(move['source']), str(move['target']))
                    print(f"✓ Moved: {move['original_name']} -> {category}/")
                    total_moved += 1
                except Exception as e:
                    print(f"✗ Failed to move {move['original_name']}: {e}")
        
        print(f"\nSuccessfully moved {total_moved} files.")
    else:
        print("\n" + "=" * 60)
        print("This is a dry run. No files were actually moved.")
        print("Use without --dry-run to execute the moves.")
        print("=" * 60)

def main():
    parser = argparse.ArgumentParser(
        description='Organize files into category subfolders (images/, docs/, archives/, others/)'
    )
    parser.add_argument('folder', help='Source folder to organize')
    parser.add_argument('--dry-run', action='store_true', help='Show plan without executing moves')
    
    args = parser.parse_args()
    
    organize_files(args.folder, dry_run=args.dry_run)

if __name__ == '__main__':
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 29
```python
import os
import shutil
import argparse
from pathlib import Path
from collections import defaultdict

def get_file_category(extension):
    """ファイル拡張子からカテゴリを判定"""
    extension = extension.lower()
    
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico', '.tiff'}
    doc_extensions = {'.pdf', '.doc', '.docx', '.txt', '.xlsx', '.xls', '.ppt', '.pptx', '.odt', '.csv'}
    archive_extensions = {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.iso'}
    
    if extension in image_extensions:
        return 'images'
    elif extension in doc_extensions:
        return 'docs'
    elif extension in archive_extensions:
        return 'archives'
    else:
        return 'others'

def get_unique_filename(target_dir, filename):
    """ファイル名の衝突を避けるため、必要に応じて連番を付ける"""
    target_path = os.path.join(target_dir, filename)
    
    if not os.path.exists(target_path):
        return filename
    
    # ファイル名と拡張子を分割
    name, ext = os.path.splitext(filename)
    
    # 連番を付けて重複を避ける
    counter = 1
    while os.path.exists(os.path.join(target_dir, f"{name}_{counter}{ext}")):
        counter += 1
    
    return f"{name}_{counter}{ext}"

def organize_files(folder_path, dry_run=False):
    """指定フォルダ内のファイルを拡張子ごとに整理"""
    
    if not os.path.isdir(folder_path):
        print(f"エラー: {folder_path} はディレクトリではありません")
        return
    
    # ファイル移動計画を保存
    move_plan = defaultdict(list)
    
    # フォルダ内のすべてのファイルをスキャン
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        
        # ディレクトリはスキップ
        if os.path.isdir(item_path):
            continue
        
        # 拡張子を取得
        _, ext = os.path.splitext(item)
        if not ext:
            ext = ''
        
        # カテゴリを判定
        category = get_file_category(ext)
        
        # 移動計画に追加
        move_plan[category].append(item)
    
    # 移動計画を表示
    print(f"\n📁 ファイル整理計画 - {folder_path}")
    print("=" * 60)
    
    total_files = 0
    for category in ['images', 'docs', 'archives', 'others']:
        if category in move_plan:
            files = move_plan[category]
            total_files += len(files)
            print(f"\n📂 {category}/ へ移動するファイル ({len(files)}個):")
            for filename in sorted(files):
                print(f"  → {filename}")
    
    print(f"\n合計: {total_files}個のファイルを整理します")
    print("=" * 60)
    
    # dry-run の場合はここで終了
    if dry_run:
        print("\n⚠️  --dry-run モードです。実際には移動されません。")
        return
    
    # 実際にファイルを移動
    print("\n移動を実行中...")
    
    for category, files in move_plan.items():
        # サブフォルダを作成
        subfolder = os.path.join(folder_path, category)
        os.makedirs(subfolder, exist_ok=True)
        
        # ファイルを移動
        for filename in files:
            src_path = os.path.join(folder_path, filename)
            
            # 衝突を避けるため、必要に応じて連番を付ける
            unique_filename = get_unique_filename(subfolder, filename)
            dst_path = os.path.join(subfolder, unique_filename)
            
            try:
                shutil.move(src_path, dst_path)
                if unique_filename != filename:
                    print(f"  ✓ {filename} → {category}/{unique_filename}")
                else:
                    print(f"  ✓ {filename} → {category}/")
            except Exception as e:
                print(f"  ✗ エラー: {filename} - {str(e)}")
    
    print("\n✅ ファイル整理が完了しました！")

def main():
    parser = argparse.ArgumentParser(
        description='指定フォルダ内のファイルを拡張子ごとにサブフォルダへ移動します'
    )
    parser.add_argument(
        'folder',
        help='整理対象のフォルダパス'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='実際には移動せず、計画のみ表示します'
    )
    
    args = parser.parse_args()
    
    organize_files(args.folder, dry_run=args.dry_run)

if __name__ == '__main__':
    main()
```

## bedrock_claude-haiku-4-5-20251001-v1 / sample 30
```python
import os
import sys
import shutil
from pathlib import Path
from anthropic import Anthropic

def organize_files_cli():
    """ファイル整理用のCLIツール with Claude AI assistant"""
    
    client = Anthropic()
    conversation_history = []
    
    # システムプロンプト
    system_prompt = """You are a helpful file organization assistant. You help users organize files in directories by extension.
    
When a user asks to organize files, help them by:
1. Understanding the directory path they want to organize
2. Helping them decide on --dry-run option
3. Confirming the file organization plan before execution
4. Providing feedback on the organization results

File categories are:
- images: jpg, jpeg, png, gif, bmp, svg, webp, ico
- docs: pdf, doc, docx, txt, xls, xlsx, ppt, pptx, csv, json, xml, md
- archives: zip, rar, 7z, tar, gz, bz2
- others: all other files

For file conflicts, add numbers to the filename (e.g., file.txt -> file_1.txt)."""
    
    print("File Organization Assistant")
    print("=" * 50)
    print("このツールを使用してファイルを拡張子ごとに整理できます。")
    print("'help' でコマンド一覧を表示します。")
    print("'exit' で終了します。")
    print("=" * 50)
    
    def categorize_file(filename):
        """ファイルを拡張子に基づいてカテゴリ分け"""
        ext = Path(filename).suffix.lower()[1:]
        
        image_exts = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp', 'ico'}
        doc_exts = {'pdf', 'doc', 'docx', 'txt', 'xls', 'xlsx', 'ppt', 'pptx', 'csv', 'json', 'xml', 'md'}
        archive_exts = {'zip', 'rar', '7z', 'tar', 'gz', 'bz2'}
        
        if ext in image_exts:
            return 'images'
        elif ext in doc_exts:
            return 'docs'
        elif ext in archive_exts:
            return 'archives'
        else:
            return 'others'
    
    def get_unique_filename(dest_path, filename):
        """衝突時に連番を付けたファイル名を生成"""
        if not dest_path.exists():
            return filename
        
        stem = Path(filename).stem
        suffix = Path(filename).suffix
        counter = 1
        
        while (dest_path / filename).exists():
            filename = f"{stem}_{counter}{suffix}"
            counter += 1
        
        return filename
    
    def organize_directory(directory, dry_run=True):
        """ディレクトリ内のファイルを整理"""
        dir_path = Path(directory)
        
        if not dir_path.exists():
            return f"エラー: ディレクトリ '{directory}' が見つかりません。"
        
        if not dir_path.is_dir():
            return f"エラー: '{directory}' はディレクトリではありません。"
        
        # ファイル一覧を取得
        files_to_move = []
        for item in dir_path.iterdir():
            if item.is_file():
                category = categorize_file(item.name)
                files_to_move.append((item, category))
        
        if not files_to_move:
            return "整理するファイルが見つかりません。"
        
        # 計画を立てる
        plan = []
        plan.append(f"\n{'=' * 50}")
        plan.append(f"ファイル整理計画 (dry_run={dry_run})")
        plan.append(f"{'=' * 50}")
        plan.append(f"対象ディレクトリ: {dir_path.absolute()}\n")
        
        # カテゴリごとにファイルをグループ化
        by_category = {}
        for file_path, category in files_to_move:
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(file_path)
        
        # 各カテゴリのファイルを処理
        total_moved = 0
        for category in sorted(by_category.keys()):
            plan.append(f"[{category}/] フォルダ:")
            category_dir = dir_path / category
            
            for file_path in sorted(by_category[category]):
                new_filename = get_unique_filename(category_dir, file_path.name)
                plan.append(f"  {file_path.name} -> {category}/{new_filename}")
                
                if not dry_run:
                    category_dir.mkdir(exist_ok=True)
                    dest_path = category_dir / new_filename
                    shutil.move(str(file_path), str(dest_path))
                
                total_moved += 1
        
        plan.append(f"\n合計 {total_moved} ファイルを移動します。")
        plan.append(f"{'=' * 50}\n")
        
        return "\n".join(plan)
    
    def process_command(user_input):
        """ユーザー入力を処理"""
        user_input_lower = user_input.lower().strip()
        
        if user_input_lower == 'help':
            help_text = """
利用可能なコマンド:
  organize <directory> [--dry-run]  - ディレクトリ内のファイルを整理
  organize <directory>              - 実際にファイルを移動
  organize <directory> --dry-run    - 計画のみ表示
  help                               - このヘルプを表示
  exit                               - プログラムを終了

例:
  organize ./Downloads
  organize ./Downloads --dry-run
"""
            return help_text
        
        elif user_input_lower == 'exit':
            return None
        
        elif user_input_lower.startswith('organize '):
            parts = user_input.split()
            if len(parts) < 2:
                return "エラー: ディレクトリパスを指定してください。\n例: organize ./Downloads"
            
            directory = parts[1]
            dry_run = '--dry-run' in parts
            
            result = organize_directory(directory, dry_run=dry_run)
            return result
        
        else:
            # Claude AIに相談
            conversation_history.append({
                "role": "user",
                "content": user_input
            })
            
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                system=system_prompt,
                messages=conversation_history
            )
            
            assistant_message = response.content[0].text
            conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            return assistant_message
    
    # メインループ
    while True:
        try:
            user_input = input("\n> ").strip()
            
            if not user_input:
                continue
            
            result = process_command(user_input)
            
            if result is None:
                print("さようなら!")
                break
            
            print(result)
        
        except KeyboardInterrupt:
            print("\n\nプログラムを中断します。")
            break
        except Exception as e:
            print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    organize_files_cli()
```
