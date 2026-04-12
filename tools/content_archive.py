#!/usr/bin/env python3
"""
Content Archive - Simple local archive for daily content

Creates and maintains an organized archive:
- archive/YYYY-MM-DD-[slug]/
  - blog.md
  - linkedin-newsletter.md
  - linkedin-post.md
  - image.png
  - status.json (approved/pending/revised)

No Google Drive required - just organized local storage.
Sync to Drive manually or use Google Drive Desktop app.

Usage:
    python3 tools/content_archive.py "Blog Title" --archive
    python3 tools/content_archive.py --list
"""

import os
import sys
import json
import shutil
import glob
from datetime import datetime
from pathlib import Path

BASE_PATH = Path(__file__).parent.parent
ARCHIVE_DIR = BASE_PATH / "archive"
EXPORTS_DIR = BASE_PATH / "exports"

def slugify(title):
    """Convert title to URL-safe slug"""
    slug = title.lower()
    slug = slug.replace(' ', '-')
    slug = ''.join(c for c in slug if c.isalnum() or c == '-')
    slug = '-'.join(filter(None, slug.split('-')))  # Remove consecutive dashes
    return slug[:50]

def archive_daily_content(title, date_str=None, status='pending'):
    """Archive today's content to local archive folder"""

    if date_str is None:
        date_str = datetime.now().strftime('%Y-%m-%d')

    slug = slugify(title)
    folder_name = f"{date_str}-{slug}"
    archive_folder = ARCHIVE_DIR / folder_name

    print(f"\n📁 Archiving content: {folder_name}")
    print("=" * 50)

    # Create archive folder
    archive_folder.mkdir(parents=True, exist_ok=True)

    # File mappings: (pattern in exports/, target name in archive)
    file_mappings = [
        (f"{date_str}-*-BLOG.md", "blog.md"),
        (f"{date_str}-*-LINKEDIN.md", "linkedin-newsletter.md"),
        (f"{date_str}-*-LINKEDIN-POST.md", "linkedin-post.md"),
    ]

    archived_files = []

    # Copy markdown files
    for pattern, target_name in file_mappings:
        matches = glob.glob(str(EXPORTS_DIR / pattern))
        if matches:
            shutil.copy2(matches[0], archive_folder / target_name)
            print(f"  ✅ {target_name}")
            archived_files.append(target_name)
        else:
            print(f"  ⚠️  Not found: {pattern}")

    # Copy image
    graphics_dir = EXPORTS_DIR / "graphics"
    image_pattern = f"{date_str}-*-FINAL.png"
    image_matches = glob.glob(str(graphics_dir / image_pattern))
    if image_matches:
        shutil.copy2(image_matches[0], archive_folder / "image.png")
        print(f"  ✅ image.png")
        archived_files.append("image.png")
    else:
        print(f"  ⚠️  Image not found: {image_pattern}")

    # Create status file
    status_data = {
        'title': title,
        'date': date_str,
        'slug': slug,
        'status': status,
        'created_at': datetime.now().isoformat(),
        'files': archived_files
    }

    with open(archive_folder / "status.json", 'w') as f:
        json.dump(status_data, f, indent=2)
    print(f"  ✅ status.json")

    print(f"\n✅ Archive complete: {archive_folder}")
    return str(archive_folder)

def list_archive():
    """List all archived content"""

    if not ARCHIVE_DIR.exists():
        print("\n📚 No archive found yet.")
        return []

    folders = sorted([d for d in ARCHIVE_DIR.iterdir() if d.is_dir()], reverse=True)

    print(f"\n📚 Content Archive ({len(folders)} entries)")
    print("=" * 50)

    for folder in folders[:20]:
        status_file = folder / "status.json"
        if status_file.exists():
            with open(status_file) as f:
                status = json.load(f)
            marker = "✅" if status.get('status') == 'approved' else "⏳"
            print(f"  {marker} {folder.name}: {status.get('title', 'No title')}")
        else:
            print(f"  📁 {folder.name}")

    if len(folders) > 20:
        print(f"  ... and {len(folders) - 20} more")

    return folders

def update_status(date_or_slug, new_status):
    """Update status of an archived item"""

    if not ARCHIVE_DIR.exists():
        print("No archive found.")
        return False

    # Find matching folder
    for folder in ARCHIVE_DIR.iterdir():
        if not folder.is_dir():
            continue
        if date_or_slug in folder.name:
            status_file = folder / "status.json"
            if status_file.exists():
                with open(status_file) as f:
                    status = json.load(f)
                status['status'] = new_status
                status['updated_at'] = datetime.now().isoformat()
                with open(status_file, 'w') as f:
                    json.dump(status, f, indent=2)
                print(f"✅ Updated {folder.name} to '{new_status}'")
                return True

    print(f"❌ No archive found matching: {date_or_slug}")
    return False

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Archive daily content locally')
    parser.add_argument('title', nargs='?', help='Blog post title')
    parser.add_argument('--list', action='store_true', help='List archive')
    parser.add_argument('--date', help='Date (YYYY-MM-DD)', default=None)
    parser.add_argument('--status', default='pending',
                       choices=['pending', 'approved', 'revised'],
                       help='Status: pending/approved/revised')
    parser.add_argument('--update', metavar='DATE_OR_SLUG',
                       help='Update status of existing archive item')
    parser.add_argument('--set-status', metavar='STATUS',
                       help='New status for --update')

    args = parser.parse_args()

    if args.list:
        list_archive()
    elif args.update and args.set_status:
        update_status(args.update, args.set_status)
    elif args.title:
        archive_daily_content(args.title, args.date, args.status)
    else:
        print("Usage:")
        print("  Archive today's content:")
        print("    python3 tools/content_archive.py 'Blog Title'")
        print()
        print("  List archive:")
        print("    python3 tools/content_archive.py --list")
        print()
        print("  Mark as approved:")
        print("    python3 tools/content_archive.py --update 2026-02-14 --set-status approved")
