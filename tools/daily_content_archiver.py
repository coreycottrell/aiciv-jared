#!/usr/bin/env python3
"""
Daily Content Archiver - Uploads blog content to Google Drive

Creates and maintains "Aether-PureBrain content" folder with daily subfolders:
- YYYY-MM-DD-[slug]/
  - blog.md
  - linkedin-newsletter.md
  - linkedin-post.md
  - image.png
  - status.json (approved/pending/revised)

Usage:
    python3 tools/daily_content_archiver.py "Blog Title" --upload
    python3 tools/daily_content_archiver.py --list  # Show archive status
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.gdrive_manager import GDriveManager

MAIN_FOLDER_NAME = "Aether-PureBrain content"

def get_or_create_main_folder(gdrive):
    """Get or create the main content folder"""
    # Search for existing folder
    results = gdrive.service.files().list(
        q=f"name='{MAIN_FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
        spaces='drive',
        fields='files(id, name)'
    ).execute()
    
    files = results.get('files', [])
    if files:
        return files[0]['id']
    
    # Create folder
    folder_metadata = {
        'name': MAIN_FOLDER_NAME,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    folder = gdrive.service.files().create(
        body=folder_metadata,
        fields='id'
    ).execute()
    
    print(f"Created folder: {MAIN_FOLDER_NAME}")
    return folder.get('id')

def create_date_folder(gdrive, parent_id, date_str, slug):
    """Create a dated subfolder for content"""
    folder_name = f"{date_str}-{slug}"
    
    # Check if exists
    results = gdrive.service.files().list(
        q=f"name='{folder_name}' and '{parent_id}' in parents and trashed=false",
        spaces='drive',
        fields='files(id, name)'
    ).execute()
    
    files = results.get('files', [])
    if files:
        return files[0]['id'], folder_name
    
    # Create
    folder_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id]
    }
    folder = gdrive.service.files().create(
        body=folder_metadata,
        fields='id'
    ).execute()
    
    print(f"Created date folder: {folder_name}")
    return folder.get('id'), folder_name

def upload_file(gdrive, parent_id, local_path, drive_name=None):
    """Upload a file to Drive folder"""
    from googleapiclient.http import MediaFileUpload
    
    if not os.path.exists(local_path):
        print(f"File not found: {local_path}")
        return None
    
    filename = drive_name or os.path.basename(local_path)
    ext = os.path.splitext(local_path)[1].lower()
    
    mime_types = {
        '.md': 'text/markdown',
        '.txt': 'text/plain',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.json': 'application/json',
        '.html': 'text/html'
    }
    mime_type = mime_types.get(ext, 'application/octet-stream')
    
    # Check if exists (update instead of create duplicate)
    results = gdrive.service.files().list(
        q=f"name='{filename}' and '{parent_id}' in parents and trashed=false",
        spaces='drive',
        fields='files(id, name)'
    ).execute()
    
    media = MediaFileUpload(local_path, mimetype=mime_type, resumable=True)
    
    files = results.get('files', [])
    if files:
        # Update existing
        file = gdrive.service.files().update(
            fileId=files[0]['id'],
            media_body=media
        ).execute()
        print(f"  Updated: {filename}")
    else:
        # Create new
        file_metadata = {
            'name': filename,
            'parents': [parent_id]
        }
        file = gdrive.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        print(f"  Uploaded: {filename}")
    
    return file.get('id')

def archive_daily_content(title, date_str=None, status='pending'):
    """Archive today's content to Google Drive"""
    base_path = Path(__file__).parent.parent
    
    if date_str is None:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    # Generate slug from title
    slug = title.lower().replace(' ', '-').replace("'", "").replace('"', '')[:50]
    
    print(f"\n📁 Archiving content for: {date_str} - {title}")
    print("="*50)
    
    # Initialize GDrive
    gdrive = GDriveManager(verbose=False)
    
    # Get/create main folder
    main_folder_id = get_or_create_main_folder(gdrive)
    print(f"Main folder ID: {main_folder_id}")
    
    # Create date folder
    date_folder_id, folder_name = create_date_folder(gdrive, main_folder_id, date_str, slug)
    print(f"Date folder: {folder_name}")
    
    # Find and upload content files
    exports_dir = base_path / "exports"
    
    # Map expected files
    file_mappings = [
        (f"{date_str}-*-BLOG.md", "blog.md"),
        (f"{date_str}-*-LINKEDIN.md", "linkedin-newsletter.md"),
        (f"{date_str}-*-LINKEDIN-POST.md", "linkedin-post.md"),
    ]
    
    print("\nUploading files:")
    
    # Upload markdown files
    import glob
    for pattern, target_name in file_mappings:
        matches = glob.glob(str(exports_dir / pattern))
        if matches:
            upload_file(gdrive, date_folder_id, matches[0], target_name)
        else:
            print(f"  ⚠️ Not found: {pattern}")
    
    # Upload image
    graphics_dir = exports_dir / "graphics"
    image_pattern = f"{date_str}-*-FINAL.png"
    image_matches = glob.glob(str(graphics_dir / image_pattern))
    if image_matches:
        upload_file(gdrive, date_folder_id, image_matches[0], "image.png")
    else:
        print(f"  ⚠️ Image not found: {image_pattern}")
    
    # Create status file
    status_data = {
        'title': title,
        'date': date_str,
        'slug': slug,
        'status': status,
        'created_at': datetime.now().isoformat(),
        'files': ['blog.md', 'linkedin-newsletter.md', 'linkedin-post.md', 'image.png']
    }
    
    status_path = base_path / "exports" / f".content-status-{date_str}.json"
    with open(status_path, 'w') as f:
        json.dump(status_data, f, indent=2)
    upload_file(gdrive, date_folder_id, str(status_path), "status.json")
    os.remove(status_path)
    
    print("\n✅ Content archived successfully!")
    print(f"   Folder: {MAIN_FOLDER_NAME}/{folder_name}")
    
    return date_folder_id

def list_archive(gdrive=None):
    """List all archived content"""
    if gdrive is None:
        gdrive = GDriveManager(verbose=False)
    
    main_folder_id = get_or_create_main_folder(gdrive)
    
    results = gdrive.service.files().list(
        q=f"'{main_folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false",
        spaces='drive',
        fields='files(id, name, createdTime)',
        orderBy='name desc'
    ).execute()
    
    folders = results.get('files', [])
    
    print(f"\n📚 Content Archive ({len(folders)} entries)")
    print("="*50)
    
    for folder in folders[:20]:
        print(f"  📁 {folder['name']}")
    
    if len(folders) > 20:
        print(f"  ... and {len(folders) - 20} more")
    
    return folders

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Archive daily content to Google Drive')
    parser.add_argument('title', nargs='?', help='Blog post title')
    parser.add_argument('--list', action='store_true', help='List archive')
    parser.add_argument('--date', help='Date (YYYY-MM-DD)', default=None)
    parser.add_argument('--status', default='pending', help='Status: pending/approved/revised')
    
    args = parser.parse_args()
    
    if args.list:
        list_archive()
    elif args.title:
        archive_daily_content(args.title, args.date, args.status)
    else:
        print("Usage: python3 daily_content_archiver.py 'Blog Title' [--date YYYY-MM-DD]")
        print("       python3 daily_content_archiver.py --list")
