#!/usr/bin/env python3
"""
Fix ALL broken images on social.purebrain.ai
Root cause: R2 public domain (pub-...r2.dev) is disabled/broken.
Fix: Re-upload all local images, update media_refs to use proxy URLs.

Proxy format: https://social.purebrain.ai/media/{key}
"""

import json
import os
import subprocess
import time
import sys

# Auth
TOKEN = "0ac9fe92dc16a435275e0c1c0fc597f99c7a4492cc5a040cb34e68d84aa2afb0"
API = "https://social.purebrain.ai"
CF_ACCOUNT = "d526a3e9498dd167509003004df03290"
D1_DB = "625dde70-0a60-45e7-bf81-e18e5ac4d854"
CF_TOKEN = "cfut_UxKCZuQQ2eY9jnjVUIliObCuRcCSmAkEeQkLEo6pba65a3be"

# Image directories
IMG_DIRS = [
    "/home/jared/projects/AI-CIV/aether/exports/content-batch-images-apr30",
    "/home/jared/projects/AI-CIV/aether/exports/content-batch-images-may5",
    "/home/jared/projects/AI-CIV/aether/exports/content-batch-images-week2",
    "/home/jared/projects/AI-CIV/aether/exports/content-batch-images",
]

# Build a map of slug -> local file path
def build_local_image_map():
    """Map image slugs to their local file paths."""
    img_map = {}
    for d in IMG_DIRS:
        if not os.path.isdir(d):
            continue
        for f in os.listdir(d):
            if f.endswith(('.jpg', '.png', '.jpeg')):
                # Key by filename without extension for matching
                slug = f.rsplit('.', 1)[0]
                img_map[slug] = os.path.join(d, f)
                # Also key by just the main slug part (without -standalone suffix for banner matching)
                base = slug.replace('-standalone', '').replace('-banner', '')
                if base not in img_map:
                    img_map[base] = os.path.join(d, f)
    return img_map


def upload_image(filepath):
    """Upload image to R2 via social API, return new proxy URL."""
    result = subprocess.run(
        ['curl', '-s', API + '/api/uploads',
         '-H', f'Authorization: Bearer {TOKEN}',
         '-F', f'file=@{filepath}'],
        capture_output=True, text=True
    )
    try:
        data = json.loads(result.stdout)
        if 'key' in data:
            proxy_url = f"{API}/media/{data['key']}"
            return proxy_url, data['key']
    except:
        print(f"  ERROR uploading {filepath}: {result.stdout[:200]}")
    return None, None


def update_media_refs(content_id, new_url):
    """Update content item media_refs via D1 API."""
    media_json = json.dumps([new_url])
    sql = f'UPDATE content_items SET media_refs = ? WHERE id = ?'
    result = subprocess.run(
        ['curl', '-s',
         f'https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT}/d1/database/{D1_DB}/query',
         '-H', f'Authorization: Bearer {CF_TOKEN}',
         '-H', 'Content-Type: application/json',
         '-d', json.dumps({"sql": sql, "params": [media_json, content_id]})],
        capture_output=True, text=True
    )
    try:
        data = json.loads(result.stdout)
        return data.get('success', False)
    except:
        print(f"  ERROR updating {content_id}: {result.stdout[:200]}")
        return False


def get_broken_content():
    """Get all non-posted content with media_refs."""
    result = subprocess.run(
        ['curl', '-s',
         f'https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT}/d1/database/{D1_DB}/query',
         '-H', f'Authorization: Bearer {CF_TOKEN}',
         '-H', 'Content-Type: application/json',
         '-d', json.dumps({
             "sql": """SELECT id, status, content_type, media_refs, SUBSTR(body, 1, 100) as body_preview
                       FROM content_items
                       WHERE media_refs IS NOT NULL AND media_refs != '' AND media_refs != '[]'
                       AND status != 'posted'
                       ORDER BY status, content_type"""
         })],
        capture_output=True, text=True
    )
    data = json.loads(result.stdout)
    return data['result'][0]['results']


def extract_slug_from_media(media_ref):
    """Extract the image slug from a media_refs value."""
    if media_ref.startswith('['):
        try:
            arr = json.loads(media_ref)
            media_ref = arr[0] if arr else ''
        except:
            pass

    if not media_ref:
        return None

    # Get the filename part
    fname = media_ref.split('/')[-1]
    # Remove extension
    slug = fname.rsplit('.', 1)[0]
    # Remove timestamp prefix (e.g., "1777330826589-21f273b4-")
    parts = slug.split('-', 2)
    if len(parts) >= 3 and parts[0].isdigit():
        slug = parts[2]

    return slug


def main():
    print("=" * 60)
    print("SOCIAL.PUREBRAIN.AI IMAGE FIX")
    print("=" * 60)

    # Step 1: Build local image map
    print("\n[1] Building local image map...")
    img_map = build_local_image_map()
    print(f"  Found {len(img_map)} local images")

    # Step 2: Get broken content
    print("\n[2] Getting content with broken images...")
    items = get_broken_content()
    print(f"  Found {len(items)} items with media_refs")

    # Step 3: Match and fix
    print("\n[3] Matching, uploading, and fixing...")
    fixed = 0
    failed = 0
    upload_cache = {}  # slug -> proxy_url (avoid re-uploading same image)

    for item in items:
        cid = item['id']
        status = item['status']
        ctype = item['content_type']
        media = item['media_refs']
        body = item.get('body_preview', '')[:50]

        slug = extract_slug_from_media(media)
        if not slug:
            print(f"  SKIP {cid[:12]}... - could not extract slug from: {media[:60]}")
            failed += 1
            continue

        print(f"\n  [{status:15}] {ctype:18} {cid[:12]}...")
        print(f"    slug: {slug}")

        # Check if already uploaded
        if slug in upload_cache:
            proxy_url = upload_cache[slug]
            print(f"    CACHED: {proxy_url[:60]}")
        else:
            # Find local file
            local_path = img_map.get(slug)
            if not local_path:
                # Try variations
                for variant in [slug + '-standalone', slug + '-banner', slug.replace('-standalone', ''), slug.replace('-banner', '')]:
                    local_path = img_map.get(variant)
                    if local_path:
                        break

            if not local_path:
                print(f"    NO LOCAL FILE for slug: {slug}")
                failed += 1
                continue

            print(f"    local: {local_path}")
            proxy_url, key = upload_image(local_path)
            if not proxy_url:
                print(f"    UPLOAD FAILED")
                failed += 1
                continue

            upload_cache[slug] = proxy_url
            print(f"    uploaded: {proxy_url[:60]}")
            time.sleep(0.3)  # Rate limit

        # Update D1
        if update_media_refs(cid, proxy_url):
            print(f"    UPDATED in D1")
            fixed += 1
        else:
            print(f"    D1 UPDATE FAILED")
            failed += 1

    print("\n" + "=" * 60)
    print(f"RESULTS: {fixed} fixed, {failed} failed, {len(items)} total")
    print("=" * 60)

    # Save upload cache for reference
    cache_path = "/home/jared/projects/AI-CIV/aether/exports/content-batch-images-may5/upload_cache_may4.json"
    with open(cache_path, 'w') as f:
        json.dump(upload_cache, f, indent=2)
    print(f"\nUpload cache saved to: {cache_path}")


if __name__ == "__main__":
    main()
