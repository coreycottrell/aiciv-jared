#!/usr/bin/env python3
"""
Upload 23 branded images to R2 (purebrain-uploads bucket) and update D1 content items.
"""

import os
import sys
import json
import time
import urllib.request

import boto3

# --- Config ---
FINAL_DIR = "/home/jared/projects/AI-CIV/aether/exports/content-batch-images-apr30"

# R2 credentials
R2_ACCESS_KEY = "6c0d119663825c37e74c915df3a38864"
R2_SECRET_KEY = "30c40c061fd2a920824fae3fbc05db69fc1d39199d5821fa9841e08223b73136"
CF_ACCOUNT_ID = "d526a3e9498dd167509003004df03290"
R2_BUCKET = "purebrain-uploads"
# DEPRECATED 2026-05-04: R2 public domain broken. Use proxy.
# R2_PUBLIC_DOMAIN = "pub-8f8cf3b34e354e108283ed11c59db125.r2.dev"
MEDIA_PROXY_BASE = "https://social.purebrain.ai/media"

# D1 credentials
D1_DB_ID = "625dde70-0a60-45e7-bf81-e18e5ac4d854"
CF_TOKEN = "cfut_UxKCZuQQ2eY9jnjVUIliObCuRcCSmAkEeQkLEo6pba65a3be"

# User ID for R2 key prefix (from previous batch)
USER_ID = "f15527f5-559c-4799-92e3-4b2de2e27897"

# Image slug -> filename mapping
IMAGES = [
    "ai-forgets-paying-twice",
    "junior-marketer-vs-ai",
    "context-problem-not-ai",
    "monday-morning-ai-briefing",
    "better-context-not-model",
    "day1-compound-effect",
    "gmail-newsletter-spam-fix",
    "ai-compound-effect-article",
    "10k-content-engine-149",
    "ai-works-247am",
    "ai-doesnt-sleep-3am",
    "name-your-ai-before-pay",
    "ai-forgot-everything",
    "cost-of-ai-amnesia-74k",
    "36-businesses-named-ai",
    "skeptic-to-coceo",
    "journey-to-coceo",
    "skeptics-timeline-with-ai",
    "blog-written-sunday",
    "20000-words-sunday-30min",
    "last-post-content-automation",
    "small-agencies-ai-partners",
    "small-agencies-build-own-ai",
]

# Content item ID -> image index (0-based) mapping
# Image 7 (gmail-newsletter-spam-fix, index 6) is reused for gmail items
CONTENT_MAPPING = [
    ("b1186428-3d95-4248-aed5-f22934af6bc4", 0),   # ai-forgets-paying-twice
    ("dc15ff2d-baa9-4773-a5b3-2899875613fe", 1),   # junior-marketer-vs-ai
    ("f6c200b2-33a2-47d7-a05f-575b0142ab79", 2),   # context-problem-not-ai
    ("24655b0f-1b1f-428a-baae-fd5eb71fe05c", 3),   # monday-morning-ai-briefing
    ("f248863a-6279-4946-92b4-58cdcceb6fff", 4),   # better-context-not-model
    ("ffd90388-9bb0-4ae0-b38b-71e396b8ccb3", 5),   # day1-compound-effect
    ("cdf90973-2ea4-4ca0-879b-f267ca70fef6", 6),   # gmail-newsletter-spam-fix
    ("4bbcc589-4536-4b0a-a9bc-e71804d05d0c", 7),   # ai-compound-effect-article
    ("4689b557-6e18-4e1c-83b2-1cf5c0e697a3", 8),   # 10k-content-engine-149
    ("54667875-b3b8-46c0-9390-c2bc2ab4a872", 9),   # ai-works-247am
    ("61964a3b-dc4b-4f27-8a0c-c19978ad364d", 6),   # gmail reuse
    ("de9894ad-5821-4308-8279-e78ffb50d120", 10),  # ai-doesnt-sleep-3am
    ("6e2572fa-fc02-4152-9bb1-c8dc55916602", 11),  # name-your-ai-before-pay
    ("46ea9d5d-b9bb-49c4-b3cc-efbccca422e7", 12),  # ai-forgot-everything
    ("0293ca0e-e7e4-45d3-8669-fd4bb9d38a6a", 6),   # gmail reuse
    ("1c731067-9c87-4593-b408-1497d2d8aa70", 13),  # cost-of-ai-amnesia-74k
    ("5db8e855-c3dc-4e39-a5aa-513545034b9b", 14),  # 36-businesses-named-ai
    ("b829a2e8-e66b-4e5a-814e-742978afe8cd", 15),  # skeptic-to-coceo
    ("399fdd62-9f5d-4632-b49d-6691bf5c1371", 6),   # gmail reuse
    ("54a2e116-c6a0-40df-a118-c746ef49e5d1", 16),  # journey-to-coceo
    ("cac2f57f-760f-4fa9-86f5-596447f7f34f", 17),  # skeptics-timeline-with-ai
    ("cb8c303d-c3b4-4c0b-892c-b3e578bc572b", 18),  # blog-written-sunday
    ("f96ef5bc-580a-443f-a40f-e009e03abc78", 6),   # gmail reuse
    ("046ca6b5-fa6e-4320-9f46-7b988c4b3141", 19),  # 20000-words-sunday-30min
    ("3a88cf9b-fa84-4df6-918d-fb42d700ecc1", 20),  # last-post-content-automation
    ("e1b01cc2-6107-4fdd-b024-235ed4790fd7", 21),  # small-agencies-ai-partners
    ("9b0ffb32-5056-4bb2-889e-7b416b3ecfc1", 22),  # small-agencies-build-own-ai
]


def upload_to_r2():
    """Upload all 23 images to R2 and return slug->r2_key mapping."""
    endpoint = f"https://{CF_ACCOUNT_ID}.r2.cloudflarestorage.com"

    s3 = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=R2_ACCESS_KEY,
        aws_secret_access_key=R2_SECRET_KEY,
        region_name="auto",
    )

    r2_keys = {}

    for i, slug in enumerate(IMAGES):
        filename = f"{slug}-standalone.jpg"
        filepath = os.path.join(FINAL_DIR, filename)

        if not os.path.exists(filepath):
            print(f"  [SKIP] File missing: {filepath}")
            continue

        timestamp = int(time.time() * 1000)
        import uuid
        rand = str(uuid.uuid4())[:8]
        key = f"{USER_ID}/{timestamp}-{rand}-{filename}"

        print(f"  [{i+1}/23] Uploading {filename} -> {key}")
        s3.upload_file(
            filepath,
            R2_BUCKET,
            key,
            ExtraArgs={"ContentType": "image/jpeg"},
        )

        r2_keys[slug] = key
        # Small delay to avoid hammering
        time.sleep(0.5)

    return r2_keys


def update_d1(r2_keys):
    """Update content items in D1 with R2 media URLs."""
    success = 0
    failed = 0

    for content_id, img_idx in CONTENT_MAPPING:
        slug = IMAGES[img_idx]
        if slug not in r2_keys:
            print(f"  [SKIP] No R2 key for {slug}")
            failed += 1
            continue

        r2_key = r2_keys[slug]
        public_url = f"{MEDIA_PROXY_BASE}/{r2_key}"
        media_refs = json.dumps([public_url])

        # Use D1 HTTP API
        sql = f"UPDATE content_items SET media_refs = ? WHERE id = ?"
        url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/d1/database/{D1_DB_ID}/query"

        payload = {
            "sql": "UPDATE content_items SET media_refs = ?1 WHERE id = ?2",
            "params": [media_refs, content_id]
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
                print(f"  [OK] {content_id} -> {slug} ({changes} row(s) updated)")
                success += 1
            else:
                print(f"  [ERR] {content_id}: {result.get('errors', 'unknown error')}")
                failed += 1
        except Exception as e:
            print(f"  [ERR] {content_id}: {e}")
            failed += 1

    return success, failed


def main():
    print("=" * 60)
    print("STEP 1: Upload 23 images to R2")
    print("=" * 60)

    r2_keys = upload_to_r2()
    print(f"\nUploaded {len(r2_keys)} images to R2")

    print("\n" + "=" * 60)
    print("STEP 2: Update 27 content items in D1")
    print("=" * 60)

    success, failed = update_d1(r2_keys)

    print("\n" + "=" * 60)
    print(f"FINAL: {len(r2_keys)} R2 uploads, {success} D1 updates, {failed} failures")
    print("=" * 60)

    # Print R2 keys for reference
    print("\nR2 Keys:")
    for slug, key in r2_keys.items():
        print(f"  {slug}: {key}")


if __name__ == "__main__":
    main()
