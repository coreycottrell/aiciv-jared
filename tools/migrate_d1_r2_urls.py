#!/usr/bin/env python3
"""
Migrate D1 content_items.media_refs from broken R2 public domain to proxy URLs.

Usage:
  python3 tools/migrate_d1_r2_urls.py          # preview + execute
  python3 tools/migrate_d1_r2_urls.py --dry-run # preview only
"""

import json
import subprocess
import sys

CF_ACCOUNT = "d526a3e9498dd167509003004df03290"
D1_DB = "625dde70-0a60-45e7-bf81-e18e5ac4d854"
CF_TOKEN = "[REDACTED-2026-05-09-LEAK-CFUT]"

OLD_PREFIX = "https://pub-8f8cf3b34e354e108283ed11c59db125.r2.dev/"
NEW_PREFIX = "https://social.purebrain.ai/media/"
OLD_DOMAIN = "pub-8f8cf3b34e354e108283ed11c59db125.r2.dev"


def d1_query(sql, params=None):
    """Execute D1 query via CF API."""
    payload = {"sql": sql}
    if params:
        payload["params"] = params
    result = subprocess.run(
        ['curl', '-s',
         f'https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT}/d1/database/{D1_DB}/query',
         '-H', f'Authorization: Bearer {CF_TOKEN}',
         '-H', 'Content-Type: application/json',
         '-d', json.dumps(payload)],
        capture_output=True, text=True
    )
    data = json.loads(result.stdout)
    if not data.get('success'):
        print(f"  D1 ERROR: {json.dumps(data.get('errors', []))}")
        return None
    return data['result'][0]


def main():
    dry_run = '--dry-run' in sys.argv

    print("=" * 60)
    print("D1 Media Refs Migration: R2 Public -> Proxy")
    if dry_run:
        print("  MODE: DRY RUN (no changes)")
    print("=" * 60)

    # Count affected rows
    print("\n[1] Counting affected rows...")
    result = d1_query(f"SELECT COUNT(*) as cnt FROM content_items WHERE media_refs LIKE '%{OLD_DOMAIN}%'")
    if not result:
        return 1
    count = result['results'][0]['cnt']
    print(f"  Found {count} rows with old R2 domain")

    if count == 0:
        print("  Nothing to migrate.")
        return 0

    # Preview
    print(f"\n[2] Preview (up to 10 rows)...")
    result = d1_query(
        f"SELECT id, status, content_type, media_refs FROM content_items "
        f"WHERE media_refs LIKE '%{OLD_DOMAIN}%' LIMIT 10"
    )
    if result:
        for row in result['results']:
            media = row['media_refs'][:80] if row['media_refs'] else 'NULL'
            print(f"  {row['id'][:12]}... [{row['status']:10}] {row['content_type']:12} {media}...")

    # Show what the replacement will look like
    print(f"\n[3] Replacement:")
    print(f"  OLD: {OLD_PREFIX}<key>")
    print(f"  NEW: {NEW_PREFIX}<key>")

    if dry_run:
        print("\n  DRY RUN -- no changes applied.")
        return 0

    # Execute
    print(f"\n[4] Executing UPDATE...")
    result = d1_query(
        f"UPDATE content_items SET media_refs = REPLACE(media_refs, '{OLD_PREFIX}', '{NEW_PREFIX}') "
        f"WHERE media_refs LIKE '%{OLD_DOMAIN}%'"
    )
    if not result:
        print("  FAILED")
        return 1
    changes = result.get('meta', {}).get('changes', '?')
    print(f"  Updated {changes} rows")

    # Verify
    print(f"\n[5] Verification...")
    result = d1_query(f"SELECT COUNT(*) as cnt FROM content_items WHERE media_refs LIKE '%{OLD_DOMAIN}%'")
    if result:
        remaining = result['results'][0]['cnt']
        if remaining == 0:
            print(f"  VERIFIED: 0 rows with old domain remaining")
        else:
            print(f"  WARNING: {remaining} rows still have old domain")
            return 1

    # Test a proxy URL
    print(f"\n[6] Testing proxy endpoint...")
    result = d1_query(
        f"SELECT media_refs FROM content_items WHERE media_refs LIKE '%social.purebrain.ai/media%' LIMIT 1"
    )
    if result and result['results']:
        media = result['results'][0]['media_refs']
        try:
            urls = json.loads(media) if media.startswith('[') else [media]
            test_url = urls[0]
            print(f"  Testing: {test_url}")
            check = subprocess.run(
                ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}',
                 '-H', 'User-Agent: curl/7.81.0', test_url],
                capture_output=True, text=True
            )
            status = check.stdout.strip()
            print(f"  HTTP {status}")
            if status == "200":
                print(f"  Proxy WORKING")
            else:
                print(f"  Proxy returned non-200 (image may not exist in R2 bucket)")
        except Exception as e:
            print(f"  Test error: {e}")

    print(f"\n{'=' * 60}")
    print("MIGRATION COMPLETE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
