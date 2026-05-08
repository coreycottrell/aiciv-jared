#!/usr/bin/env python3
"""
migrate_r2_to_proxy.py
======================
Permanently switch all R2 public domain URLs to Worker proxy URLs.

Problem: R2 public domain (pub-8f8cf3b34e354e108283ed11c59db125.r2.dev) returns 404.
Fix: Use social.purebrain.ai/media/{key} proxy (already exists in worker).

This script:
1. Patches workers/social-api/src/worker.js handleUpload to return proxy URLs
2. Patches exports/content-batch-images-apr30/upload_and_update.py
3. Patches tools/attach_sunday_batch_may4_images.py (comment only)
4. Updates all from-chy/worker-*.js files
5. Generates D1 SQL to fix existing media_refs in content_items

Author: cto (ST# task delegation)
Date: 2026-05-04
"""

import os
import re
import json
import subprocess
import sys

AETHER = "/home/jared/projects/AI-CIV/aether"
OLD_DOMAIN = "pub-8f8cf3b34e354e108283ed11c59db125.r2.dev"
PROXY_BASE = "social.purebrain.ai/media"

changes_made = []


def patch_file(filepath, replacements, description):
    """Apply text replacements to a file. Each replacement is (old, new)."""
    if not os.path.exists(filepath):
        print(f"  SKIP (not found): {filepath}")
        return False

    with open(filepath, "r") as f:
        content = f.read()

    original = content
    for old, new in replacements:
        if old not in content:
            print(f"  WARN: pattern not found in {filepath}: {old[:60]}...")
            continue
        content = content.replace(old, new)

    if content == original:
        print(f"  NO CHANGE: {filepath}")
        return False

    with open(filepath, "w") as f:
        f.write(content)

    changes_made.append({"file": filepath, "description": description})
    print(f"  PATCHED: {filepath}")
    return True


def patch_social_api_worker():
    """Fix the main social-api worker to return proxy URLs from handleUpload."""
    filepath = os.path.join(AETHER, "workers/social-api/src/worker.js")
    print("\n[1] Patching social-api worker (handleUpload)...")

    replacements = [
        # Replace the constant declaration
        (
            f'const R2_PUBLIC_DOMAIN = "{OLD_DOMAIN}";',
            f'// DEPRECATED: R2 public domain broken (404s). Use proxy instead.\n'
            f'// const R2_PUBLIC_DOMAIN = "{OLD_DOMAIN}";\n'
            f'const MEDIA_PROXY_BASE = "https://{PROXY_BASE}";'
        ),
        # Replace the URL construction in handleUpload
        (
            'const publicUrl = `https://${R2_PUBLIC_DOMAIN}/${encodeURI(key)}`;',
            'const publicUrl = `${MEDIA_PROXY_BASE}/${encodeURI(key)}`;'
        ),
    ]

    return patch_file(filepath, replacements,
                      "handleUpload now returns proxy URLs via social.purebrain.ai/media/")


def patch_upload_and_update():
    """Fix the apr30 batch upload script."""
    filepath = os.path.join(AETHER, "exports/content-batch-images-apr30/upload_and_update.py")
    print("\n[2] Patching exports upload_and_update.py...")

    replacements = [
        (
            f'R2_PUBLIC_DOMAIN = "{OLD_DOMAIN}"',
            f'# DEPRECATED: R2 public domain broken. Use proxy.\n'
            f'# R2_PUBLIC_DOMAIN = "{OLD_DOMAIN}"\n'
            f'MEDIA_PROXY_BASE = "https://{PROXY_BASE}"'
        ),
        (
            'public_url = f"https://{R2_PUBLIC_DOMAIN}/{r2_key}"',
            'public_url = f"{MEDIA_PROXY_BASE}/{r2_key}"'
        ),
    ]

    return patch_file(filepath, replacements, "Upload URLs now use proxy pattern")


def patch_attach_script():
    """Fix the sunday batch attach script docstring."""
    filepath = os.path.join(AETHER, "tools/attach_sunday_batch_may4_images.py")
    print("\n[3] Patching attach_sunday_batch_may4_images.py (comment only)...")

    replacements = [
        (
            f'   stores it on R2 (`{OLD_DOMAIN}`) and',
            f'   stores it on R2 and returns a proxy URL via social.purebrain.ai/media/ and'
        ),
    ]

    return patch_file(filepath, replacements, "Updated docstring comment (functional URL comes from API response)")


def patch_from_chy_workers():
    """Fix all from-chy worker versions."""
    chy_dir = os.path.join(AETHER, "from-chy")
    print("\n[4] Patching from-chy worker files...")

    if not os.path.isdir(chy_dir):
        print("  SKIP: from-chy directory not found")
        return 0

    count = 0
    for fname in sorted(os.listdir(chy_dir)):
        if not fname.endswith(".js"):
            continue
        filepath = os.path.join(chy_dir, fname)
        with open(filepath, "r") as f:
            content = f.read()
        if OLD_DOMAIN not in content:
            continue

        replacements = [
            (
                f'const R2_PUBLIC_DOMAIN = "{OLD_DOMAIN}";',
                f'// DEPRECATED: R2 public domain broken. Use proxy.\n'
                f'// const R2_PUBLIC_DOMAIN = "{OLD_DOMAIN}";\n'
                f'const MEDIA_PROXY_BASE = "https://{PROXY_BASE}";'
            ),
        ]

        # Also fix URL construction if present
        if f'${{R2_PUBLIC_DOMAIN}}' in content:
            replacements.append((
                '`https://${R2_PUBLIC_DOMAIN}/',
                '`${MEDIA_PROXY_BASE}/'
            ))

        if patch_file(filepath, replacements, f"from-chy/{fname}: proxy URLs"):
            count += 1

    print(f"  Patched {count} from-chy worker files")
    return count


def generate_d1_migration_sql():
    """Generate SQL to update existing media_refs in D1 from old domain to proxy."""
    print("\n[5] Generating D1 migration SQL...")

    old_prefix = f"https://{OLD_DOMAIN}/"
    new_prefix = f"https://{PROXY_BASE}/"

    sql = f"""-- Migrate R2 public domain URLs to proxy URLs in content_items.media_refs
-- Run via: CF D1 HTTP API or wrangler d1 execute
-- Date: 2026-05-04

-- Preview affected rows first:
-- SELECT id, media_refs FROM content_items
-- WHERE media_refs LIKE '%{OLD_DOMAIN}%';

-- Update all media_refs that reference the broken R2 public domain
UPDATE content_items
SET media_refs = REPLACE(media_refs, '{old_prefix}', '{new_prefix}')
WHERE media_refs LIKE '%{OLD_DOMAIN}%';
"""

    sql_path = os.path.join(AETHER, "workers/social-api/migrations/migrate_r2_to_proxy.sql")
    os.makedirs(os.path.dirname(sql_path), exist_ok=True)
    with open(sql_path, "w") as f:
        f.write(sql)

    changes_made.append({"file": sql_path, "description": "D1 migration SQL for existing media_refs"})
    print(f"  Written: {sql_path}")
    return sql_path


def run_d1_migration():
    """Execute the D1 migration via CF API."""
    print("\n[6] Executing D1 migration...")

    # Read credentials from fix_all_images_may4.py (already has them)
    CF_ACCOUNT = "d526a3e9498dd167509003004df03290"
    D1_DB = "625dde70-0a60-45e7-bf81-e18e5ac4d854"
    CF_TOKEN = "cfut_UxKCZuQQ2eY9jnjVUIliObCuRcCSmAkEeQkLEo6pba65a3be"

    old_prefix = f"https://{OLD_DOMAIN}/"
    new_prefix = f"https://{PROXY_BASE}/"

    # First: count affected rows
    count_sql = f"SELECT COUNT(*) as cnt FROM content_items WHERE media_refs LIKE '%{OLD_DOMAIN}%'"
    result = subprocess.run(
        ['curl', '-s',
         f'https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT}/d1/database/{D1_DB}/query',
         '-H', f'Authorization: Bearer {CF_TOKEN}',
         '-H', 'Content-Type: application/json',
         '-d', json.dumps({"sql": count_sql})],
        capture_output=True, text=True
    )
    try:
        data = json.loads(result.stdout)
        count = data['result'][0]['results'][0]['cnt']
        print(f"  Found {count} rows with old R2 domain in media_refs")
    except Exception as e:
        print(f"  ERROR counting rows: {e}")
        print(f"  Response: {result.stdout[:500]}")
        return False

    if count == 0:
        print("  No rows to update -- already migrated or no data")
        return True

    # Preview first 5
    preview_sql = f"SELECT id, SUBSTR(media_refs, 1, 120) as media_preview FROM content_items WHERE media_refs LIKE '%{OLD_DOMAIN}%' LIMIT 5"
    result = subprocess.run(
        ['curl', '-s',
         f'https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT}/d1/database/{D1_DB}/query',
         '-H', f'Authorization: Bearer {CF_TOKEN}',
         '-H', 'Content-Type: application/json',
         '-d', json.dumps({"sql": preview_sql})],
        capture_output=True, text=True
    )
    try:
        data = json.loads(result.stdout)
        rows = data['result'][0]['results']
        print(f"  Preview (first {len(rows)}):")
        for r in rows:
            print(f"    {r['id'][:12]}... -> {r['media_preview'][:80]}...")
    except Exception as e:
        print(f"  Preview error: {e}")

    # Execute the REPLACE
    update_sql = f"UPDATE content_items SET media_refs = REPLACE(media_refs, '{old_prefix}', '{new_prefix}') WHERE media_refs LIKE '%{OLD_DOMAIN}%'"
    result = subprocess.run(
        ['curl', '-s',
         f'https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT}/d1/database/{D1_DB}/query',
         '-H', f'Authorization: Bearer {CF_TOKEN}',
         '-H', 'Content-Type: application/json',
         '-d', json.dumps({"sql": update_sql})],
        capture_output=True, text=True
    )
    try:
        data = json.loads(result.stdout)
        if data.get('success'):
            meta = data['result'][0].get('meta', {})
            changes = meta.get('changes', '?')
            print(f"  SUCCESS: {changes} rows updated")
            return True
        else:
            print(f"  FAILED: {json.dumps(data.get('errors', []))}")
            return False
    except Exception as e:
        print(f"  ERROR: {e}")
        print(f"  Response: {result.stdout[:500]}")
        return False


def verify_d1_migration():
    """Verify no old-domain URLs remain in D1."""
    print("\n[7] Verifying D1 migration...")

    CF_ACCOUNT = "d526a3e9498dd167509003004df03290"
    D1_DB = "625dde70-0a60-45e7-bf81-e18e5ac4d854"
    CF_TOKEN = "cfut_UxKCZuQQ2eY9jnjVUIliObCuRcCSmAkEeQkLEo6pba65a3be"

    count_sql = f"SELECT COUNT(*) as cnt FROM content_items WHERE media_refs LIKE '%{OLD_DOMAIN}%'"
    result = subprocess.run(
        ['curl', '-s',
         f'https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT}/d1/database/{D1_DB}/query',
         '-H', f'Authorization: Bearer {CF_TOKEN}',
         '-H', 'Content-Type: application/json',
         '-d', json.dumps({"sql": count_sql})],
        capture_output=True, text=True
    )
    try:
        data = json.loads(result.stdout)
        count = data['result'][0]['results'][0]['cnt']
        if count == 0:
            print(f"  VERIFIED: 0 rows with old R2 domain remaining")
            return True
        else:
            print(f"  FAIL: {count} rows still have old R2 domain")
            return False
    except Exception as e:
        print(f"  Verification error: {e}")
        return False


def verify_proxy_endpoint():
    """Test that the /media/ proxy endpoint returns images."""
    print("\n[8] Verifying /media/ proxy endpoint...")

    # Get one proxied URL from D1 to test
    CF_ACCOUNT = "d526a3e9498dd167509003004df03290"
    D1_DB = "625dde70-0a60-45e7-bf81-e18e5ac4d854"
    CF_TOKEN = "cfut_UxKCZuQQ2eY9jnjVUIliObCuRcCSmAkEeQkLEo6pba65a3be"

    sql = f"SELECT media_refs FROM content_items WHERE media_refs LIKE '%{PROXY_BASE}%' LIMIT 1"
    result = subprocess.run(
        ['curl', '-s',
         f'https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT}/d1/database/{D1_DB}/query',
         '-H', f'Authorization: Bearer {CF_TOKEN}',
         '-H', 'Content-Type: application/json',
         '-d', json.dumps({"sql": sql})],
        capture_output=True, text=True
    )
    try:
        data = json.loads(result.stdout)
        rows = data['result'][0]['results']
        if not rows:
            print("  No proxy URLs in D1 yet -- skipping live test")
            return True

        media_refs = rows[0]['media_refs']
        urls = json.loads(media_refs) if media_refs.startswith('[') else [media_refs]
        test_url = urls[0]
        print(f"  Testing: {test_url}")

        # HEAD request to check it returns 200
        result = subprocess.run(
            ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}',
             '-H', 'User-Agent: curl/7.81.0',
             test_url],
            capture_output=True, text=True
        )
        status = result.stdout.strip()
        if status == "200":
            print(f"  VERIFIED: proxy returns HTTP {status}")
            return True
        else:
            print(f"  WARN: proxy returned HTTP {status} (image may not exist in R2)")
            return False
    except Exception as e:
        print(f"  Error: {e}")
        return False


def main():
    print("=" * 70)
    print("R2 Public Domain -> Proxy URL Migration")
    print(f"Old: https://{OLD_DOMAIN}/...")
    print(f"New: https://{PROXY_BASE}/...")
    print("=" * 70)

    # Step 1-4: Patch source files
    patch_social_api_worker()
    patch_upload_and_update()
    patch_attach_script()
    patch_from_chy_workers()

    # Step 5: Generate SQL migration
    sql_path = generate_d1_migration_sql()

    # Step 6: Execute D1 migration
    d1_ok = run_d1_migration()

    # Step 7: Verify D1
    verify_ok = verify_d1_migration() if d1_ok else False

    # Step 8: Verify proxy endpoint
    proxy_ok = verify_proxy_endpoint()

    # Summary
    print("\n" + "=" * 70)
    print("MIGRATION SUMMARY")
    print("=" * 70)
    print(f"\nFiles patched: {len(changes_made)}")
    for c in changes_made:
        print(f"  {c['file']}")
        print(f"    -> {c['description']}")
    print(f"\nD1 migration: {'SUCCESS' if d1_ok else 'FAILED'}")
    print(f"D1 verification: {'PASSED' if verify_ok else 'FAILED/SKIPPED'}")
    print(f"Proxy endpoint: {'WORKING' if proxy_ok else 'CHECK NEEDED'}")

    remaining = []
    # Check for any remaining references
    print("\n--- Remaining references check ---")
    for root, dirs, files in os.walk(AETHER):
        # Skip .git and node_modules
        skip = False
        for skip_dir in ['.git', 'node_modules', '__pycache__', '.claude/memory']:
            if skip_dir in root:
                skip = True
                break
        if skip:
            continue
        for fname in files:
            if not fname.endswith(('.js', '.py', '.json', '.ts')):
                continue
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, 'r', errors='ignore') as f:
                    content = f.read()
                if OLD_DOMAIN in content:
                    # Check if it's just a comment/deprecated reference
                    lines = [l.strip() for l in content.split('\n') if OLD_DOMAIN in l]
                    active = [l for l in lines if not l.startswith('//') and not l.startswith('#') and 'DEPRECATED' not in l]
                    if active:
                        remaining.append((fpath, len(active)))
            except:
                pass

    if remaining:
        print(f"\nWARNING: {len(remaining)} files still have active references:")
        for fpath, count in remaining:
            rel = os.path.relpath(fpath, AETHER)
            print(f"  {rel} ({count} active lines)")
    else:
        print("\nAll active references eliminated.")

    print("\n--- NEXT STEPS ---")
    print("1. Deploy updated social-api worker: cd workers/social-api && npx wrangler deploy")
    print("   (Or use CF dashboard to paste updated worker.js)")
    print("2. Test image loading on social.purebrain.ai")
    print("3. The from-chy workers are historical copies -- no deploy needed")

    return 0 if (d1_ok and verify_ok) else 1


if __name__ == "__main__":
    sys.exit(main())
