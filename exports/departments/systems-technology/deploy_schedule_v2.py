#!/usr/bin/env python3
"""Deploy Social Schedule v2 + Sheet Sync v2 to BaaS server.

1. Backs up current files
2. Copies new modules to /opt/baas/
3. Patches baas_server_simple.py to use new modules
4. Migrates existing scheduled_posts.json to v2 format
5. Restarts the BaaS service

Author: dept-systems-technology
Date: 2026-04-06
"""

import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime

BAAS_DIR = '/opt/baas'
TIMESTAMP = datetime.now().strftime('%Y%m%d_%H%M%S')


def backup(filepath):
    if os.path.exists(filepath):
        bak = f'{filepath}.bak.{TIMESTAMP}'
        shutil.copy2(filepath, bak)
        print(f'  Backed up: {filepath} -> {bak}')
        return bak
    return None


def migrate_scheduled_posts():
    """Migrate existing scheduled_posts.json to v2 format (add new fields)."""
    filepath = os.path.join(BAAS_DIR, 'scheduled_posts.json')
    if not os.path.exists(filepath):
        print('  No scheduled_posts.json found, starting fresh')
        return

    with open(filepath) as f:
        posts = json.load(f)

    migrated = 0
    for post_id, post in posts.items():
        changed = False

        # Add baas_id if missing
        if 'baas_id' not in post:
            post['baas_id'] = post.get('id', post_id)
            changed = True

        # Add new v2 fields with defaults
        defaults = {
            'content_type': 'standalone',
            'drive_folder_url': '',
            'drive_file_ids': {},
            'spreadsheet_row': None,
            'publish_status': post.get('status', 'draft'),
            'banner_url': post.get('banner_image', ''),
            'linkedin_post_url': '',
            'auto_publish': False,
        }

        for k, v in defaults.items():
            if k not in post:
                post[k] = v
                changed = True

        # Ensure updated_at exists
        if 'updated_at' not in post:
            post['updated_at'] = post.get('created_at', datetime.utcnow().isoformat())
            changed = True

        if changed:
            migrated += 1

    with open(filepath, 'w') as f:
        json.dump(posts, f, indent=2, default=str)

    print(f'  Migrated {migrated}/{len(posts)} posts to v2 format')


def patch_baas_server():
    """Patch baas_server_simple.py to use v2 schedule module."""
    filepath = os.path.join(BAAS_DIR, 'baas_server_simple.py')

    with open(filepath) as f:
        content = f.read()

    # 1. Replace sheet_sync import with sheet_sync_v2
    content = content.replace(
        'from sheet_sync import extend_sheet_sync_router',
        'from sheet_sync_v2 import extend_sheet_sync_router, sync_post_to_sheet'
    )

    # 2. Add import for social_schedule_v2 (after the sheet_sync import)
    if 'from social_schedule_v2 import' not in content:
        content = content.replace(
            'from sheet_sync_v2 import extend_sheet_sync_router, sync_post_to_sheet',
            'from sheet_sync_v2 import extend_sheet_sync_router, sync_post_to_sheet\n'
            'from social_schedule_v2 import create_schedule_router, set_sync_callback'
        )

    # 3. Replace the inline schedule endpoints with the v2 router
    # Find the section between "# ── SOCIAL SCHEDULE ENDPOINTS ──" and the next section
    schedule_start = content.find('# ── SOCIAL SCHEDULE ENDPOINTS ──')
    if schedule_start == -1:
        # Try alternate marker
        schedule_start = content.find("# ── SOCIAL SCHEDULE ENDPOINTS")

    if schedule_start != -1:
        # Find where the inline schedule section ends
        # It ends right before @app.get('/health')
        health_marker = content.find("@app.get('/health')", schedule_start)
        if health_marker != -1:
            # Remove the inline schedule section
            old_section = content[schedule_start:health_marker]
            new_section = '''# ── SOCIAL SCHEDULE v2 (Router-based) ──
_schedule_router = create_schedule_router(sessions, auth)
set_sync_callback(sync_post_to_sheet)
app.include_router(_schedule_router)

# Legacy compat: /social/scheduled -> redirect to v2
@app.get("/social/scheduled")
async def social_list_scheduled_compat(x_api_key: str = Header(None)):
    """Legacy endpoint - returns posts from v2 schedule store."""
    auth(x_api_key)
    from social_schedule_v2 import _load_scheduled
    posts = _load_scheduled()
    return {"posts": list(posts.values()), "count": len(posts)}

'''
            content = content[:schedule_start] + new_section + content[health_marker:]
            print('  Replaced inline schedule endpoints with v2 router')
        else:
            print('  WARNING: Could not find health endpoint marker')
    else:
        print('  WARNING: Could not find inline schedule section')

    with open(filepath, 'w') as f:
        f.write(content)

    print(f'  Patched {filepath}')


def main():
    print(f'\n=== Deploy Social Schedule v2 — {TIMESTAMP} ===\n')

    # Step 1: Back up
    print('Step 1: Backing up...')
    backup(os.path.join(BAAS_DIR, 'baas_server_simple.py'))
    backup(os.path.join(BAAS_DIR, 'sheet_sync.py'))
    backup(os.path.join(BAAS_DIR, 'scheduled_posts.json'))

    # Step 2: Copy new modules
    print('\nStep 2: Copying new modules...')
    src_dir = os.path.dirname(os.path.abspath(__file__))
    for fname in ['social_schedule_v2.py', 'sheet_sync_v2.py']:
        src = os.path.join(src_dir, fname)
        dst = os.path.join(BAAS_DIR, fname)
        shutil.copy2(src, dst)
        print(f'  Copied: {fname} -> {dst}')

    # Step 3: Migrate data
    print('\nStep 3: Migrating scheduled_posts.json...')
    migrate_scheduled_posts()

    # Step 4: Patch server
    print('\nStep 4: Patching baas_server_simple.py...')
    patch_baas_server()

    # Step 5: Restart service
    print('\nStep 5: Restarting purebrain-baas service...')
    result = subprocess.run(['systemctl', 'restart', 'purebrain-baas'],
                          capture_output=True, text=True)
    if result.returncode == 0:
        print('  Service restarted successfully')
    else:
        print(f'  WARNING: Service restart failed: {result.stderr}')
        return 1

    # Step 6: Wait and verify
    print('\nStep 6: Verifying...')
    time.sleep(3)
    try:
        import httpx
        resp = httpx.get('http://127.0.0.1:8901/health', timeout=10)
        health = resp.json()
        print(f'  Health: {health.get("status")} v{health.get("version")}')
        print(f'  Features: {len(health.get("features", []))} loaded')
    except Exception as e:
        print(f'  Health check failed: {e}')
        # Check logs
        result = subprocess.run(['journalctl', '-u', 'purebrain-baas', '-n', '20', '--no-pager'],
                              capture_output=True, text=True)
        print(f'  Recent logs:\n{result.stdout[-500:]}')
        return 1

    # Step 7: Test schedule endpoint
    print('\nStep 7: Testing schedule v2 endpoints...')
    try:
        import httpx
        headers = {'X-API-Key': 'aether-baas-key-001', 'Content-Type': 'application/json'}

        # Test GET /social/schedule
        resp = httpx.get('http://127.0.0.1:8901/social/schedule', headers=headers, timeout=10)
        data = resp.json()
        print(f'  GET /social/schedule: {resp.status_code} — {data.get("count", 0)} posts')

        # Test GET /social/schedule/stats
        resp = httpx.get('http://127.0.0.1:8901/social/schedule/stats', headers=headers, timeout=10)
        print(f'  GET /social/schedule/stats: {resp.status_code}')

        # Test GET /social/schedule/calendar
        resp = httpx.get('http://127.0.0.1:8901/social/schedule/calendar', headers=headers, timeout=10)
        print(f'  GET /social/schedule/calendar: {resp.status_code}')

        # Test GET /social/schedule/sync-status
        resp = httpx.get('http://127.0.0.1:8901/social/schedule/sync-status', headers=headers, timeout=10)
        print(f'  GET /social/schedule/sync-status: {resp.status_code}')

        # Test legacy compat
        resp = httpx.get('http://127.0.0.1:8901/social/scheduled', headers=headers, timeout=10)
        print(f'  GET /social/scheduled (legacy): {resp.status_code}')

    except Exception as e:
        print(f'  Endpoint tests failed: {e}')

    print(f'\n=== Deployment complete ===\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
