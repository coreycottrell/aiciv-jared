#!/usr/bin/env python3
"""
Upload 23 branded images via social API and update D1 content items.
Uses social API /api/uploads (multipart form) + D1 HTTP API for updates.
"""

import os
import sys
import json
import time
import urllib.request
import subprocess

FINAL_DIR = "/home/jared/projects/AI-CIV/aether/exports/content-batch-images-apr30"

# Social API auth
SOCIAL_TOKEN = "37f487bb435751044824e1186e547873ebdf5c1975e7f3013dab19368c9a97e4"
SOCIAL_API = "https://social.purebrain.ai"

# D1 credentials
CF_ACCOUNT_ID = "d526a3e9498dd167509003004df03290"
D1_DB_ID = "625dde70-0a60-45e7-bf81-e18e5ac4d854"
CF_TOKEN = "[REDACTED-2026-05-09-LEAK-CFUT]"

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

# content_id -> image_index mapping (27 items, 23 unique images, image 6 reused 5x)
CONTENT_MAPPING = [
    ("b1186428-3d95-4248-aed5-f22934af6bc4", 0),
    ("dc15ff2d-baa9-4773-a5b3-2899875613fe", 1),
    ("f6c200b2-33a2-47d7-a05f-575b0142ab79", 2),
    ("24655b0f-1b1f-428a-baae-fd5eb71fe05c", 3),
    ("f248863a-6279-4946-92b4-58cdcceb6fff", 4),
    ("ffd90388-9bb0-4ae0-b38b-71e396b8ccb3", 5),
    ("cdf90973-2ea4-4ca0-879b-f267ca70fef6", 6),
    ("4bbcc589-4536-4b0a-a9bc-e71804d05d0c", 7),
    ("4689b557-6e18-4e1c-83b2-1cf5c0e697a3", 8),
    ("54667875-b3b8-46c0-9390-c2bc2ab4a872", 9),
    ("61964a3b-dc4b-4f27-8a0c-c19978ad364d", 6),
    ("de9894ad-5821-4308-8279-e78ffb50d120", 10),
    ("6e2572fa-fc02-4152-9bb1-c8dc55916602", 11),
    ("46ea9d5d-b9bb-49c4-b3cc-efbccca422e7", 12),
    ("0293ca0e-e7e4-45d3-8669-fd4bb9d38a6a", 6),
    ("1c731067-9c87-4593-b408-1497d2d8aa70", 13),
    ("5db8e855-c3dc-4e39-a5aa-513545034b9b", 14),
    ("b829a2e8-e66b-4e5a-814e-742978afe8cd", 15),
    ("399fdd62-9f5d-4632-b49d-6691bf5c1371", 6),
    ("54a2e116-c6a0-40df-a118-c746ef49e5d1", 16),
    ("cac2f57f-760f-4fa9-86f5-596447f7f34f", 17),
    ("cb8c303d-c3b4-4c0b-892c-b3e578bc572b", 18),
    ("f96ef5bc-580a-443f-a40f-e009e03abc78", 6),
    ("046ca6b5-fa6e-4320-9f46-7b988c4b3141", 19),
    ("3a88cf9b-fa84-4df6-918d-fb42d700ecc1", 20),
    ("e1b01cc2-6107-4fdd-b024-235ed4790fd7", 21),
    ("9b0ffb32-5056-4bb2-889e-7b416b3ecfc1", 22),
]


def upload_image_to_r2(slug):
    """Upload image via social API /api/uploads (multipart form), return R2 key."""
    filename = f"{slug}-standalone.jpg"
    filepath = os.path.join(FINAL_DIR, filename)

    if not os.path.exists(filepath):
        print(f"  [SKIP] Missing: {filepath}")
        return None

    # Use curl for multipart upload (more reliable than urllib for multipart)
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
            print(f"  [OK] {slug} -> key={data['key']}")
            return data
        else:
            print(f"  [ERR] {slug}: {data}")
            return None
    except json.JSONDecodeError:
        print(f"  [ERR] {slug}: Non-JSON response: {result.stdout[:200]}")
        return None


def update_d1(content_id, media_refs_value):
    """Update a content item's media_refs in D1."""
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
    print("STEP 1: Upload 23 unique images to R2 via social API")
    print("=" * 60)

    r2_data = {}  # slug -> upload response data
    upload_success = 0

    for i, slug in enumerate(IMAGES):
        print(f"\n  [{i+1}/23] {slug}")
        data = upload_image_to_r2(slug)
        if data:
            r2_data[slug] = data
            upload_success += 1
        time.sleep(0.3)  # Small delay

    print(f"\n\nUploaded: {upload_success}/23")

    print("\n" + "=" * 60)
    print("STEP 2: Update 27 content items in D1")
    print("=" * 60)

    d1_success = 0
    d1_failed = 0

    for content_id, img_idx in CONTENT_MAPPING:
        slug = IMAGES[img_idx]
        if slug not in r2_data:
            print(f"  [SKIP] {content_id} - no upload for {slug}")
            d1_failed += 1
            continue

        data = r2_data[slug]
        # Use the public_url or key from the upload response
        public_url = data.get("public_url", data.get("url", ""))
        if not public_url:
            key = data.get("key", "")
            public_url = f"https://social.purebrain.ai/media/{key}"

        media_refs = json.dumps([public_url])
        changes = update_d1(content_id, media_refs)
        if changes >= 0:
            print(f"  [OK] {content_id} -> {slug} ({changes} rows)")
            d1_success += 1
        else:
            d1_failed += 1

    print("\n" + "=" * 60)
    print(f"FINAL: {upload_success} R2 uploads, {d1_success} D1 updates, {d1_failed} D1 failures")
    print("=" * 60)

    # Save R2 data for reference
    with open(os.path.join(FINAL_DIR, "r2_upload_results.json"), "w") as f:
        json.dump(r2_data, f, indent=2)
    print(f"\nR2 keys saved to: {FINAL_DIR}/r2_upload_results.json")


if __name__ == "__main__":
    main()
