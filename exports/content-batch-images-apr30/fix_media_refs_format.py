#!/usr/bin/env python3
"""Fix media_refs to use raw R2 key format (matching week2 batch pattern)."""

import json
import urllib.request

CF_ACCOUNT_ID = "d526a3e9498dd167509003004df03290"
D1_DB_ID = "625dde70-0a60-45e7-bf81-e18e5ac4d854"
CF_TOKEN = "[REDACTED-2026-05-09-LEAK-CFUT]"

with open("/home/jared/projects/AI-CIV/aether/exports/content-batch-images-apr30/r2_upload_results.json") as f:
    r2_data = json.load(f)

IMAGES = [
    "ai-forgets-paying-twice", "junior-marketer-vs-ai", "context-problem-not-ai",
    "monday-morning-ai-briefing", "better-context-not-model", "day1-compound-effect",
    "gmail-newsletter-spam-fix", "ai-compound-effect-article", "10k-content-engine-149",
    "ai-works-247am", "ai-doesnt-sleep-3am", "name-your-ai-before-pay",
    "ai-forgot-everything", "cost-of-ai-amnesia-74k", "36-businesses-named-ai",
    "skeptic-to-coceo", "journey-to-coceo", "skeptics-timeline-with-ai",
    "blog-written-sunday", "20000-words-sunday-30min", "last-post-content-automation",
    "small-agencies-ai-partners", "small-agencies-build-own-ai",
]

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

success = 0
for content_id, img_idx in CONTENT_MAPPING:
    slug = IMAGES[img_idx]
    key = r2_data[slug]["key"]  # Raw R2 key, matching week2 format

    payload = {
        "sql": "UPDATE content_items SET media_refs = ?1 WHERE id = ?2",
        "params": [key, content_id]
    }
    req = urllib.request.Request(
        f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/d1/database/{D1_DB_ID}/query",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {CF_TOKEN}", "Content-Type": "application/json"},
    )
    resp = urllib.request.urlopen(req)
    result = json.loads(resp.read())
    changes = result.get("result", [{}])[0].get("meta", {}).get("changes", 0)
    if changes > 0:
        success += 1

print(f"Updated {success}/27 content items with raw R2 keys (matching week2 format)")
