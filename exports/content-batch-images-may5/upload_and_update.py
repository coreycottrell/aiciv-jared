#!/usr/bin/env python3
"""
Upload 5 May 5 branded images via social API to R2, then update D1 content items.
"""

import os
import json
import time
import urllib.request
import subprocess

FINAL_DIR = "/home/jared/projects/AI-CIV/aether/exports/content-batch-images-may5"

# Social API auth
SOCIAL_TOKEN = "37f487bb435751044824e1186e547873ebdf5c1975e7f3013dab19368c9a97e4"
SOCIAL_API = "https://social.purebrain.ai"

# D1 credentials
CF_ACCOUNT_ID = "d526a3e9498dd167509003004df03290"
D1_DB_ID = "625dde70-0a60-45e7-bf81-e18e5ac4d854"
CF_TOKEN = "cfut_UxKCZuQQ2eY9jnjVUIliObCuRcCSmAkEeQkLEo6pba65a3be"

# Slug -> content_id mapping
ITEMS = [
    {"slug": "naming-your-ai", "content_id": "0809586c-59e3-4a49-91ba-83d4f24e3edd"},
    {"slug": "ai-partnerships-fail", "content_id": "c8849424-0982-44b5-956b-628fb9c180e8"},
    {"slug": "small-biz-ai-roi", "content_id": "2acde37e-4ce5-4af0-a041-92437cc13bfa"},
    {"slug": "tools-vs-partners", "content_id": "35d44a38-4129-4209-a1a1-365886a603f2"},
    {"slug": "149-per-month", "content_id": "a870ce79-9b61-44db-b7f7-4348c4ecf8ad"},
]


def upload_image_to_r2(slug):
    """Upload image via social API /api/uploads, return response data."""
    filepath = os.path.join(FINAL_DIR, f"{slug}-standalone.jpg")
    if not os.path.exists(filepath):
        print(f"  [SKIP] Missing: {filepath}")
        return None

    result = subprocess.run(
        [
            "curl", "-s",
            "-X", "POST",
            f"{SOCIAL_API}/api/uploads",
            "-H", f"Authorization: Bearer {SOCIAL_TOKEN}",
            "-F", f"file=@{filepath};type=image/jpeg",
        ],
        capture_output=True, text=True
    )

    try:
        data = json.loads(result.stdout)
        if "key" in data:
            print(f"  [R2 OK] {slug} -> key={data['key']}")
            return data
        else:
            print(f"  [R2 ERR] {slug}: {data}")
            return None
    except json.JSONDecodeError:
        print(f"  [R2 ERR] {slug}: Non-JSON: {result.stdout[:200]}")
        return None


def update_d1(content_id, media_refs_value):
    """Update content item media_refs in D1."""
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/d1/database/{D1_DB_ID}/query"
    payload = {
        "sql": "UPDATE content_items SET media_refs = ?1 WHERE id = ?2",
        "params": [media_refs_value, content_id]
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {CF_TOKEN}",
            "Content-Type": "application/json",
        },
    )
    try:
        resp = urllib.request.urlopen(req)
        result = json.loads(resp.read())
        if result.get("success"):
            changes = result.get("result", [{}])[0].get("meta", {}).get("changes", 0)
            return changes
        return -1
    except Exception as e:
        print(f"  [D1 ERR] {content_id}: {e}")
        return -1


def main():
    print("=" * 60)
    print("MAY 5 BATCH: Upload 5 images to R2 + Update D1")
    print("=" * 60)

    r2_success = 0
    d1_success = 0

    for i, item in enumerate(ITEMS):
        slug = item["slug"]
        cid = item["content_id"]
        print(f"\n[{i+1}/5] {slug} ({cid})")

        # Upload to R2
        data = upload_image_to_r2(slug)
        if not data:
            continue
        r2_success += 1

        # Build media_refs
        public_url = data.get("public_url", data.get("url", ""))
        if not public_url:
            key = data.get("key", "")
            public_url = f"https://social.purebrain.ai/media/{key}"

        media_refs = json.dumps([public_url])

        # Update D1
        changes = update_d1(cid, media_refs)
        if changes >= 0:
            print(f"  [D1 OK] {cid} -> {changes} row(s) updated")
            d1_success += 1
        else:
            print(f"  [D1 FAIL] {cid}")

        time.sleep(0.3)

    print("\n" + "=" * 60)
    print(f"DONE: {r2_success}/5 R2 uploads, {d1_success}/5 D1 updates")
    print("=" * 60)


if __name__ == "__main__":
    main()
