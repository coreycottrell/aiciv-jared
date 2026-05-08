#!/usr/bin/env python3
"""
Push Sunday Batch May 4-10, 2026 to social.purebrain.ai as drafts.

Total: 35 content pieces
- 7 blog posts (full body, Aether voice)
- 7 LinkedIn newsletters (paired with blogs, Jared voice, ~600 chars)
- 7 LinkedIn promo posts (one per day, drives traffic to blog)
- 14 LinkedIn standalones (2/day independent ideas)

All pushed via /api/content/bulk as status=draft.
Jared reviews + approves at https://surf.purebrain.ai/social.html
"""
import json
import os
import urllib.request
import urllib.error
import ssl
import sys

BASE = "https://social.purebrain.ai"
EMAIL = "jared@puretechnology.nyc"
# Password from env or fall back to known dev value (rotate before prod)
PASSWORD = os.environ.get("SOCIAL_API_PASSWORD", "PureBrain2026!")

ctx = ssl.create_default_context()


def http_json(method, url, body=None, token=None, timeout=30):
    headers = {
        "Content-Type": "application/json",
        "Origin": "https://social.purebrain.ai",
        "User-Agent": "curl/7.81.0",
        "Accept": "application/json",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read())
        except Exception:
            return e.code, {"error": str(e)}
    except Exception as e:
        return 0, {"error": str(e)}


def load_blog_bodies():
    """Parse blog bodies from the local markdown source-of-truth."""
    path = "/home/jared/exports/portal-files/sunday-batch-may4-10/01-BLOG-POSTS.md"
    with open(path) as f:
        text = f.read()
    # Split on "## BLOG N —" headers
    import re
    parts = re.split(r"\n## BLOG (\d+) —", text)
    blogs = {}
    # parts[0] is preamble, then alternating: index, body
    for i in range(1, len(parts), 2):
        idx = int(parts[i])
        body = parts[i + 1]
        # Strip trailing END section if present
        body = body.split("\n---\n\n## BLOG")[0]
        body = body.split("\n**END OF BLOG POSTS**")[0]
        blogs[idx] = body.strip()
    return blogs


def load_newsletter_bodies():
    path = "/home/jared/exports/portal-files/sunday-batch-may4-10/02-LINKEDIN-NEWSLETTERS.md"
    with open(path) as f:
        text = f.read()
    import re
    parts = re.split(r"\n## NEWSLETTER (\d+) —", text)
    nl = {}
    for i in range(1, len(parts), 2):
        idx = int(parts[i])
        body = parts[i + 1]
        body = body.split("\n---\n\n## NEWSLETTER")[0]
        body = body.split("\n---\n\n**Format compliance**")[0]
        nl[idx] = body.strip()
    return nl


def load_li_post_bodies():
    """Parse LinkedIn promo posts (A1-A7) and standalones (B1-B14)."""
    path = "/home/jared/exports/portal-files/sunday-batch-may4-10/03-LINKEDIN-POSTS.md"
    with open(path) as f:
        text = f.read()
    import re
    promos = {}
    # POST A1 — Mon May 4 etc.
    a_parts = re.split(r"\n## POST A(\d+) —", text)
    for i in range(1, len(a_parts), 2):
        idx = int(a_parts[i])
        body = a_parts[i + 1]
        body = body.split("\n---\n\n## POST")[0]
        body = body.split("\n# PART B")[0]
        promos[idx] = body.strip()

    standalones = {}
    b_parts = re.split(r"\n## POST B(\d+) —", text)
    for i in range(1, len(b_parts), 2):
        idx = int(b_parts[i])
        body = b_parts[i + 1]
        body = body.split("\n---\n\n## POST")[0]
        body = body.split("\n---\n\n**Format compliance check**")[0]
        standalones[idx] = body.strip()
    return promos, standalones


def main():
    # Login
    print("Logging in to social.purebrain.ai...")
    code, resp = http_json("POST", f"{BASE}/api/login", {"email": EMAIL, "password": PASSWORD})
    if code != 200:
        print(f"Login failed: {code} {resp}")
        sys.exit(1)
    token = resp["token"]
    print(f"Login OK. Token acquired.\n")

    # Load all bodies from source files
    blogs = load_blog_bodies()
    nls = load_newsletter_bodies()
    promos, standalones = load_li_post_bodies()

    print(f"Loaded: {len(blogs)} blogs, {len(nls)} newsletters, "
          f"{len(promos)} LI promos, {len(standalones)} standalones\n")

    # Schedule grid (UTC = ET + 4)
    # 12:30 UTC = 8:30 AM ET — blog + newsletter + promo (3 morning posts paired)
    # 15:00 UTC = 11:00 AM ET — standalone slot 1
    # 17:00 UTC = 1:00 PM ET — promo (alt slot if needed)
    # 19:00 UTC = 3:00 PM ET — standalone slot 2

    days = [
        ("Mon May 4",  "2026-05-04"),
        ("Tue May 5",  "2026-05-05"),
        ("Wed May 6",  "2026-05-06"),
        ("Thu May 7",  "2026-05-07"),
        ("Fri May 8",  "2026-05-08"),
        ("Sat May 9",  "2026-05-09"),
        ("Sun May 10", "2026-05-10"),
    ]

    # Standalone slot allocation per topic plan
    standalone_slots = {
        # day_idx (1-7): (slot1_id, slot2_id)
        1: (None, 1),    # Mon: slot1=blog promo, slot2=B1
        2: (2, 3),       # Tue: B2, B3
        3: (4, 5),       # Wed: B4, B5
        4: (6, 7),       # Thu: B6, B7
        5: (8, 9),       # Fri: B8, B9
        6: (10, 11),     # Sat: B10, B11
        7: (12, 13),     # Sun: B12, B13
        # B14 reserved as flex
    }

    items = []
    for day_idx, (day_label, date_str) in enumerate(days, start=1):
        # 1. Blog post (8:30 AM ET)
        if day_idx in blogs:
            items.append({
                "platform": "linkedin",
                "content_type": "blog",
                "status": "draft",
                "scheduled_at": f"{date_str}T12:30:00Z",
                "body": blogs[day_idx],
                "metadata": {
                    "batch": "sunday-may4-10",
                    "day": day_label,
                    "kind": "blog",
                    "blog_index": day_idx,
                },
            })

        # 2. Newsletter (paired, also 8:30 AM ET — newsletter goes out in same morning slot)
        if day_idx in nls:
            items.append({
                "platform": "linkedin",
                "content_type": "newsletter",
                "status": "draft",
                "scheduled_at": f"{date_str}T12:30:00Z",
                "body": nls[day_idx],
                "metadata": {
                    "batch": "sunday-may4-10",
                    "day": day_label,
                    "kind": "newsletter",
                    "newsletter_index": day_idx,
                    "paired_blog": day_idx,
                },
            })

        # 3. LinkedIn promo post (1:00 PM ET = 17:00 UTC)
        if day_idx in promos:
            items.append({
                "platform": "linkedin",
                "content_type": "post",
                "status": "draft",
                "scheduled_at": f"{date_str}T17:00:00Z",
                "body": promos[day_idx],
                "metadata": {
                    "batch": "sunday-may4-10",
                    "day": day_label,
                    "kind": "post-blog-promo",
                    "promo_index": day_idx,
                    "promotes_blog": day_idx,
                },
            })

        # 4-5. Standalones (slot1 11:00 AM ET = 15:00 UTC, slot2 3:00 PM ET = 19:00 UTC)
        slot1, slot2 = standalone_slots.get(day_idx, (None, None))
        if slot1 is not None and slot1 in standalones:
            items.append({
                "platform": "linkedin",
                "content_type": "post",
                "status": "draft",
                "scheduled_at": f"{date_str}T15:00:00Z",
                "body": standalones[slot1],
                "metadata": {
                    "batch": "sunday-may4-10",
                    "day": day_label,
                    "kind": "post-standalone",
                    "standalone_index": slot1,
                    "slot": 1,
                },
            })
        if slot2 is not None and slot2 in standalones:
            items.append({
                "platform": "linkedin",
                "content_type": "post",
                "status": "draft",
                "scheduled_at": f"{date_str}T19:00:00Z",
                "body": standalones[slot2],
                "metadata": {
                    "batch": "sunday-may4-10",
                    "day": day_label,
                    "kind": "post-standalone",
                    "standalone_index": slot2,
                    "slot": 2,
                },
            })

    # Reserve B14 — push as draft with no schedule (flex)
    if 14 in standalones:
        items.append({
            "platform": "linkedin",
            "content_type": "post",
            "status": "draft",
            "scheduled_at": None,
            "body": standalones[14],
            "metadata": {
                "batch": "sunday-may4-10",
                "kind": "post-standalone-reserve",
                "standalone_index": 14,
                "note": "flex/reserve — no scheduled time",
            },
        })

    print(f"Built {len(items)} content items for bulk push.\n")
    breakdown = {}
    for it in items:
        k = it["metadata"]["kind"]
        breakdown[k] = breakdown.get(k, 0) + 1
    print("Breakdown:")
    for k, v in sorted(breakdown.items()):
        print(f"  {k}: {v}")
    print()

    # Get LinkedIn social account ID
    code, resp = http_json("GET", f"{BASE}/api/social_accounts", token=token)
    if code != 200:
        print(f"Failed to list social accounts: {code} {resp}")
        sys.exit(1)
    li_account = next((a for a in resp.get("accounts", []) if a["platform"] == "linkedin"), None)
    if not li_account:
        print("No LinkedIn account found")
        sys.exit(1)
    li_account_id = li_account["id"]
    print(f"LinkedIn account: {li_account['account_handle']} ({li_account_id})\n")

    # Bulk endpoint not yet deployed — use single-create loop
    pushed = 0
    failed = []
    created_ids = []
    for i, item in enumerate(items, start=1):
        item["social_account_id"] = li_account_id
        kind = item["metadata"]["kind"]
        day = item["metadata"].get("day", "?")
        print(f"  [{i}/{len(items)}] {kind} ({day})... ", end="", flush=True)
        code, resp = http_json("POST", f"{BASE}/api/content", item, token=token)
        if code in (200, 201):
            cid = resp.get("item", {}).get("id") or resp.get("id")
            pushed += 1
            if cid:
                created_ids.append(cid)
            print(f"OK ({cid[:8] if cid else '?'})")
        else:
            print(f"FAIL [{code}] {str(resp)[:120]}")
            failed.append((i, code, resp))

    # Save created IDs for later image attachment
    with open("/home/jared/exports/portal-files/sunday-batch-may4-10/created-ids.json", "w") as f:
        json.dump({"ids": created_ids, "count": len(created_ids)}, f, indent=2)

    print(f"\nDone. Pushed {pushed}/{len(items)} items.")
    print(f"Created IDs saved to: /home/jared/exports/portal-files/sunday-batch-may4-10/created-ids.json")
    if failed:
        print(f"Failed: {len(failed)}")
        for f in failed[:5]:
            print(f"  idx {f[0]}: HTTP {f[1]}: {str(f[2])[:100]}")
        sys.exit(2)

    print(f"\nReview at: https://surf.purebrain.ai/social.html")
    print(f"All items status=draft until Jared approves.")


if __name__ == "__main__":
    main()
