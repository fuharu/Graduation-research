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
