#!/usr/bin/env python3
"""
Google Drive Cleanup Script - 2026-04-04
Tasks:
1. Organize loose files in Blog subfolder into proper dated subfolders
2. Create "PureBrain Company Page Posts" subfolder under Content Posted (Live)
3. Deduplicate Aether AI Influencer folder
"""
import sys
sys.path.insert(0, '/home/jared/projects/AI-CIV/aether')

from tools.gdrive_manager import GDriveManager

g = GDriveManager(verbose=False)
svc = g.service

BLOG_FOLDER = '1trWAzRF8nkPs128W3TlxQZe9fPXc35Wv'
CONTENT_POSTED_LIVE = '1LyCBPXG43WXnXUcTkA5t7m8td0U5yAYx'
INFLUENCER_FOLDER = '1CkqoiLEJZwRJ16BLsnAFeH0ga6_w5JiM'


def move_file(file_id, old_parent_id, new_parent_id):
    """Move a file from one folder to another."""
    svc.files().update(
        fileId=file_id,
        addParents=new_parent_id,
        removeParents=old_parent_id,
        fields='id, parents'
    ).execute()


def create_folder(name, parent_id):
    """Create a folder and return its ID."""
    metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id]
    }
    folder = svc.files().create(body=metadata, fields='id').execute()
    return folder['id']


def delete_file(file_id):
    """Move a file to trash."""
    svc.files().update(fileId=file_id, body={'trashed': True}).execute()


# ============================================================
# TASK 1: Blog folder cleanup
# ============================================================
print("=" * 60)
print("TASK 1: Blog Folder Cleanup")
print("=" * 60)

items = g.list_files(BLOG_FOLDER)
folders = {i['name']: i['id'] for i in items if 'folder' in i.get('mimeType', '')}
files = [i for i in items if 'folder' not in i.get('mimeType', '')]

print(f"\nFound {len(folders)} existing subfolders, {len(files)} loose files\n")

# Build mapping of file prefix -> target folder
# Strategy: match file name prefix to folder name
def find_matching_folder(filename, folders):
    """Find the best matching folder for a loose file."""
    fname_lower = filename.lower().replace(' ', '-')

    # Direct prefix match patterns
    match_rules = [
        # "prompting-is-dead-*" -> "Prompting is dead blog post" folder
        ('prompting-is-dead', 'Prompting is dead blog post'),
        # "the-ai-that-gets-smarter-*" -> existing dated folder
        ('the-ai-that-gets-smarter-when-you-push-back', '2026-03-20--the-ai-that-gets-smarter-when-you-push-back'),
        # "the-ai-that-knows-you-before-you-speak-*" -> folder
        ('the-ai-that-knows-you-before-you-speak', 'the-ai-that-knows-you-before-you-speak-2026-03-15'),
        # "the-ai-relationship-you-cant-take-with-you-*"
        ('the-ai-relationship-you-cant-take-with-you', None),  # needs new folder
        # "your-ai-agent-works-in-a-demo-*"
        ('your-ai-agent-works-in-a-demo', None),  # needs new folder
        # "your-ai-has-no-idea-who-you-are"
        ('your-ai-has-no-idea-who-you-are', None),  # multiple folders exist
    ]

    # Try exact folder name prefix matching
    for folder_name in folders:
        folder_slug = folder_name.lower().replace(' ', '-')
        # Check if filename starts with a significant part of folder name
        # Remove date prefix from folder for matching
        folder_key = folder_slug
        for prefix_len in [10]:  # skip date prefix like "2026-03-20--"
            if len(folder_slug) > 13 and folder_slug[10:12] == '--':
                folder_key = folder_slug[12:]
            elif len(folder_slug) > 11 and folder_slug[4] == '-' and folder_slug[7] == '-':
                # "2026-03-20-slug" format
                parts = folder_slug.split('-', 3)
                if len(parts) > 3:
                    folder_key = parts[3]

        if fname_lower.startswith(folder_key) and len(folder_key) > 10:
            return folder_name
        if folder_key.startswith(fname_lower.split('-banner')[0].split('-blog')[0].split('-bluesky')[0].split('-linkedin')[0].split('-bsky')[0].split('-package')[0]) and len(fname_lower.split('-banner')[0]) > 10:
            return folder_name

    return None

# Analyze each loose file
moves = []  # (file_id, file_name, target_folder_name, target_folder_id_or_None)
new_folders_needed = {}  # slug -> list of (file_id, file_name)
orphans = []

for f in files:
    fname = f['name']
    fid = f['id']

    # Get file creation date for folder naming
    meta = svc.files().get(fileId=fid, fields='createdTime').execute()
    created = meta['createdTime'][:10]  # YYYY-MM-DD

    # Extract the slug (everything before the asset type suffix)
    slug = fname.lower()
    for ext in ['.png', '.jpg', '.jpeg', '.md', '.pdf']:
        slug = slug.replace(ext, '')
    # Remove common suffixes
    for suffix in ['-banner', '-blog-post', '-blog', '-bluesky-thread', '-linkedin-newsletter',
                   '-linkedin-post', '-bsky-square-compressed', '-bsky-square',
                   '-package-summary', '-banner-prompt', ' - banner-prompt',
                   ' - blog', ' - bluesky-thread', ' - linkedin-newsletter', ' - linkedin-post',
                   ' - bluesky thread', ' - linkedin newsletter', ' - linkedin post', ' - blog post']:
        if slug.endswith(suffix):
            slug = slug[:len(slug)-len(suffix)]
    slug = slug.strip().strip('-')

    # Try to find matching folder
    matched = None
    for folder_name, folder_id in folders.items():
        fn_lower = folder_name.lower().replace(' ', '-')
        # Strip date prefix
        fn_key = fn_lower
        if len(fn_lower) > 13 and fn_lower[10:12] == '--':
            fn_key = fn_lower[12:]
        elif len(fn_lower) > 11 and fn_lower[4] == '-':
            parts = fn_lower.split('-', 3)
            if len(parts) > 3:
                fn_key = parts[3]

        if slug == fn_key or fn_key.startswith(slug) or slug.startswith(fn_key):
            if len(min(slug, fn_key)) > 8:  # Ensure meaningful match
                matched = (folder_name, folder_id)
                break

    if matched:
        moves.append((fid, fname, matched[0], matched[1]))
    else:
        # Group by slug for new folder creation
        if slug not in new_folders_needed:
            new_folders_needed[slug] = {'date': created, 'files': []}
        new_folders_needed[slug]['files'].append((fid, fname))

# Print plan
print("--- FILES TO MOVE INTO EXISTING FOLDERS ---")
for fid, fname, target, tid in moves:
    print(f"  {fname} -> [{target}]")

print(f"\n--- NEW FOLDERS NEEDED ({len(new_folders_needed)}) ---")
for slug, info in new_folders_needed.items():
    folder_name = f"{info['date']}--{slug}"
    print(f"  Will create: {folder_name}")
    for fid, fname in info['files']:
        print(f"    + {fname}")

# Special cases: files that are truly misc
misc_files = ['Blog Promotion', 'Creator AI Sprint 3 Report', 'Remove_logo_in_2k_202602130835.jpeg',
              'Turn_the_description_2k_202602101739.jpeg', 'investor-data-room-authoring-the-field.md',
              'linkedin-image-2026-04-02.png', 'linkedin-post-tuesday-agent-management-2026-02-25.md']

print("\n--- EXECUTING MOVES ---")

# Execute moves to existing folders
for fid, fname, target, tid in moves:
    print(f"  Moving '{fname}' -> '{target}'")
    move_file(fid, BLOG_FOLDER, tid)

# Create new folders and move files
created_folders = {}
for slug, info in new_folders_needed.items():
    folder_name = f"{info['date']}--{slug}"

    # Check if any file in this group is actually a misc/orphan
    file_names = [fn for _, fn in info['files']]
    is_orphan = False
    for mf in misc_files:
        if any(mf.lower() in fn.lower() for fn in file_names):
            is_orphan = True
            break

    if len(info['files']) == 1 and is_orphan:
        # Single orphan file -> _cleanup folder
        if '_cleanup' not in created_folders:
            cleanup_id = create_folder('_cleanup', BLOG_FOLDER)
            created_folders['_cleanup'] = cleanup_id
            print(f"  Created folder: _cleanup")
        for fid, fname in info['files']:
            print(f"  Moving orphan '{fname}' -> '_cleanup'")
            move_file(fid, BLOG_FOLDER, created_folders['_cleanup'])
    else:
        # Create proper subfolder
        new_id = create_folder(folder_name, BLOG_FOLDER)
        created_folders[folder_name] = new_id
        print(f"  Created folder: {folder_name}")
        for fid, fname in info['files']:
            print(f"    Moving '{fname}' into new folder")
            move_file(fid, BLOG_FOLDER, new_id)


# ============================================================
# TASK 2: Create PureBrain Company Page Posts subfolder
# ============================================================
print("\n" + "=" * 60)
print("TASK 2: Create PureBrain Company Page Posts Subfolder")
print("=" * 60)

# Check if it already exists
existing = g.list_files(CONTENT_POSTED_LIVE)
exists = any(i['name'] == 'PureBrain Company Page Posts' for i in existing)

if exists:
    print("Folder 'PureBrain Company Page Posts' already exists!")
else:
    new_id = create_folder('PureBrain Company Page Posts', CONTENT_POSTED_LIVE)
    print(f"Created 'PureBrain Company Page Posts' with ID: {new_id}")


# ============================================================
# TASK 3: Deduplicate Aether AI Influencer folder
# ============================================================
print("\n" + "=" * 60)
print("TASK 3: Deduplicate Aether AI Influencer Folder")
print("=" * 60)

items = g.list_files(INFLUENCER_FOLDER)
# Get full metadata for all files
files_with_meta = []
for item in items:
    if 'folder' in item.get('mimeType', ''):
        continue
    meta = svc.files().get(
        fileId=item['id'],
        fields='id,name,size,createdTime,modifiedTime,mimeType'
    ).execute()
    files_with_meta.append(meta)

# Group by name
from collections import defaultdict
by_name = defaultdict(list)
for f in files_with_meta:
    by_name[f['name']].append(f)

print(f"\nTotal files: {len(files_with_meta)}")
print(f"Unique names: {len(by_name)}")
duplicates_found = {k: v for k, v in by_name.items() if len(v) > 1}
print(f"Names with duplicates: {len(duplicates_found)}")

print("\n--- DUPLICATE ANALYSIS ---")
to_delete = []
to_rename = []

for name, copies in duplicates_found.items():
    sizes = [c.get('size', '0') for c in copies]
    print(f"\n  '{name}' ({len(copies)} copies)")
    for c in copies:
        print(f"    ID: {c['id']} | Size: {c.get('size', 'N/A')} | Created: {c['createdTime']} | Modified: {c['modifiedTime']}")

    if len(set(sizes)) == 1:
        # Same size = true duplicate
        print(f"    -> SAME SIZE ({sizes[0]} bytes) = TRUE DUPLICATE")
        # Keep the newer one (or first), delete the older
        sorted_copies = sorted(copies, key=lambda x: x['createdTime'])
        keep = sorted_copies[-1]  # Keep newest
        for c in sorted_copies[:-1]:
            to_delete.append((c['id'], c['name'], c.get('size', 'N/A')))
            print(f"    -> WILL DELETE: {c['id']} (created {c['createdTime']})")
        print(f"    -> KEEPING: {keep['id']} (created {keep['createdTime']})")
    else:
        # Different sizes = not true duplicate
        print(f"    -> DIFFERENT SIZES = NOT duplicate, will rename newer")
        sorted_copies = sorted(copies, key=lambda x: x['createdTime'])
        for i, c in enumerate(sorted_copies[1:], 1):
            base = name.rsplit('.', 1)
            if len(base) == 2:
                new_name = f"{base[0]}-v{i+1}.{base[1]}"
            else:
                new_name = f"{name}-v{i+1}"
            to_rename.append((c['id'], name, new_name))
            print(f"    -> WILL RENAME: {c['id']} to '{new_name}'")

print("\n--- EXECUTING DEDUP ---")

for fid, fname, size in to_delete:
    print(f"  Trashing: '{fname}' (id={fid}, size={size})")
    delete_file(fid)

for fid, old_name, new_name in to_rename:
    print(f"  Renaming: '{old_name}' -> '{new_name}' (id={fid})")
    svc.files().update(fileId=fid, body={'name': new_name}).execute()

print(f"\nDeleted {len(to_delete)} true duplicates, renamed {len(to_rename)} same-name-different-size files")

print("\n" + "=" * 60)
print("ALL TASKS COMPLETE")
print("=" * 60)
