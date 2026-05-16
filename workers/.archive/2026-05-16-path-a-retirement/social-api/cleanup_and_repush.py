#!/usr/bin/env python3
"""
Delete the 35 items pushed earlier today (with header contamination)
and re-push with clean bodies.
"""
import json
import os
import urllib.request
import urllib.error
import ssl
import sys
import re

BASE = "https://social.purebrain.ai"
EMAIL = "jared@puretechnology.nyc"
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


def login():
    code, resp = http_json("POST", f"{BASE}/api/login", {"email": EMAIL, "password": PASSWORD})
    if code != 200:
        print(f"Login failed: {code} {resp}")
        sys.exit(1)
    return resp["token"]


def cleanup_old(token):
    """Delete the 35 items from earlier push (saved IDs)."""
    ids_path = "/home/jared/exports/portal-files/sunday-batch-may4-10/created-ids.json"
    with open(ids_path) as f:
        data = json.load(f)
    ids = data.get("ids", [])
    print(f"Deleting {len(ids)} items from prior push...")
    deleted = 0
    for cid in ids:
        code, _ = http_json("DELETE", f"{BASE}/api/content/{cid}", token=token)
        if code in (200, 204):
            deleted += 1
    print(f"  Deleted {deleted}/{len(ids)}\n")


# ----- Body cleanup helpers -----

def _strip_first_line_metadata(text):
    """Remove the first line if it's a date/header annotation, plus following metadata."""
    lines = text.split("\n")
    # Skip leading blank lines
    while lines and not lines[0].strip():
        lines.pop(0)
    # If first line looks like a header (starts with day name or "Mon May" or contains ** etc.), drop until we find prose
    while lines:
        line = lines[0].strip()
        if not line:
            lines.pop(0)
            continue
        # Drop date-only headers
        if re.match(r"^(Mon|Tue|Wed|Thu|Fri|Sat|Sun)(day)?\s+May\s+\d", line):
            lines.pop(0)
            continue
        if re.match(r"^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s+May\s+\d", line):
            lines.pop(0)
            continue
        # Drop **Title**:, **Subject**:, **Slug**:, **Audio**:, **CTA Links**: lines
        if re.match(r"^\*\*(Title|Subject|Slug|Audio|CTA Links?)\*\*:?", line):
            lines.pop(0)
            continue
        # Drop "(paired with ...)", "(promotes ...)" sub-headers
        if re.match(r"^\(.*\)$", line) or "(paired with" in line or "(promotes" in line:
            lines.pop(0)
            continue
        # Drop horizontal rules at start
        if line == "---":
            lines.pop(0)
            continue
        # Drop "Mon May 4 Slot 2 [Theme C — ...]" annotations
        if re.match(r"^.{0,30}\sSlot\s+\d+\s*\[Theme", line) or "Slot " in line and "[Theme" in line:
            lines.pop(0)
            continue
        # Found prose, stop stripping
        break
    return "\n".join(lines).strip()


def load_blog_bodies():
    path = "/home/jared/exports/portal-files/sunday-batch-may4-10/01-BLOG-POSTS.md"
    with open(path) as f:
        text = f.read()
    parts = re.split(r"\n## BLOG (\d+) —", text)
    blogs = {}
    for i in range(1, len(parts), 2):
        idx = int(parts[i])
        body = parts[i + 1]
        body = body.split("\n---\n\n## BLOG")[0]
        body = body.split("\n**END OF BLOG POSTS**")[0]
        # Strip metadata header
        body = _strip_first_line_metadata(body.strip())
        blogs[idx] = body
    return blogs


def load_newsletter_bodies():
    path = "/home/jared/exports/portal-files/sunday-batch-may4-10/02-LINKEDIN-NEWSLETTERS.md"
    with open(path) as f:
        text = f.read()
    parts = re.split(r"\n## NEWSLETTER (\d+) —", text)
    nl = {}
    for i in range(1, len(parts), 2):
        idx = int(parts[i])
        body = parts[i + 1]
        body = body.split("\n---\n\n## NEWSLETTER")[0]
        body = body.split("\n---\n\n**Format compliance**")[0]
        body = _strip_first_line_metadata(body.strip())
        nl[idx] = body
    return nl


def load_li_post_bodies():
    path = "/home/jared/exports/portal-files/sunday-batch-may4-10/03-LINKEDIN-POSTS.md"
    with open(path) as f:
        text = f.read()
    promos = {}
    a_parts = re.split(r"\n## POST A(\d+) —", text)
    for i in range(1, len(a_parts), 2):
        idx = int(a_parts[i])
        body = a_parts[i + 1]
        body = body.split("\n---\n\n## POST")[0]
        body = body.split("\n# PART B")[0]
        body = _strip_first_line_metadata(body.strip())
        promos[idx] = body

    standalones = {}
    b_parts = re.split(r"\n## POST B(\d+) —", text)
    for i in range(1, len(b_parts), 2):
        idx = int(b_parts[i])
        body = b_parts[i + 1]
        body = body.split("\n---\n\n## POST")[0]
        body = body.split("\n---\n\n**Format compliance check**")[0]
        body = _strip_first_line_metadata(body.strip())
        standalones[idx] = body
    return promos, standalones


def main():
    token = login()
    print(f"Login OK.\n")

    # Step 1: Delete old contaminated items
    cleanup_old(token)

    # Step 2: Get LI account
    code, resp = http_json("GET", f"{BASE}/api/social_accounts", token=token)
    li = next((a for a in resp.get("accounts", []) if a["platform"] == "linkedin"), None)
    li_id = li["id"]
    print(f"LinkedIn account: {li_id}\n")

    # Step 3: Build & push fresh items with cleaned bodies
    blogs = load_blog_bodies()
    nls = load_newsletter_bodies()
    promos, standalones = load_li_post_bodies()

    print(f"Loaded clean: {len(blogs)} blogs, {len(nls)} newsletters, "
          f"{len(promos)} promos, {len(standalones)} standalones")

    # Quick sanity on first chars
    print(f"Sample blog 1 starts with: {blogs[1][:80]!r}")
    print(f"Sample NL 1 starts with: {nls[1][:80]!r}")
    print(f"Sample promo 1 starts with: {promos[1][:80]!r}")
    print(f"Sample standalone 1 starts with: {standalones[1][:80]!r}\n")

    days = [
        ("Mon May 4",  "2026-05-04"),
        ("Tue May 5",  "2026-05-05"),
        ("Wed May 6",  "2026-05-06"),
        ("Thu May 7",  "2026-05-07"),
        ("Fri May 8",  "2026-05-08"),
        ("Sat May 9",  "2026-05-09"),
        ("Sun May 10", "2026-05-10"),
    ]
    standalone_slots = {
        1: (None, 1),
        2: (2, 3),
        3: (4, 5),
        4: (6, 7),
        5: (8, 9),
        6: (10, 11),
        7: (12, 13),
    }

    items = []
    for day_idx, (day_label, date_str) in enumerate(days, start=1):
        if day_idx in blogs:
            items.append({
                "platform": "linkedin", "content_type": "blog", "status": "draft",
                "scheduled_at": f"{date_str}T12:30:00Z",
                "body": blogs[day_idx], "social_account_id": li_id,
                "metadata": {"batch": "sunday-may4-10", "day": day_label, "kind": "blog", "blog_index": day_idx},
            })
        if day_idx in nls:
            items.append({
                "platform": "linkedin", "content_type": "newsletter", "status": "draft",
                "scheduled_at": f"{date_str}T12:30:00Z",
                "body": nls[day_idx], "social_account_id": li_id,
                "metadata": {"batch": "sunday-may4-10", "day": day_label, "kind": "newsletter", "newsletter_index": day_idx, "paired_blog": day_idx},
            })
        if day_idx in promos:
            items.append({
                "platform": "linkedin", "content_type": "post", "status": "draft",
                "scheduled_at": f"{date_str}T17:00:00Z",
                "body": promos[day_idx], "social_account_id": li_id,
                "metadata": {"batch": "sunday-may4-10", "day": day_label, "kind": "post-blog-promo", "promo_index": day_idx, "promotes_blog": day_idx},
            })
        slot1, slot2 = standalone_slots.get(day_idx, (None, None))
        if slot1 is not None and slot1 in standalones:
            items.append({
                "platform": "linkedin", "content_type": "standalone", "status": "draft",
                "scheduled_at": f"{date_str}T15:00:00Z",
                "body": standalones[slot1], "social_account_id": li_id,
                "metadata": {"batch": "sunday-may4-10", "day": day_label, "kind": "post-standalone", "standalone_index": slot1, "slot": 1},
            })
        if slot2 is not None and slot2 in standalones:
            items.append({
                "platform": "linkedin", "content_type": "standalone", "status": "draft",
                "scheduled_at": f"{date_str}T19:00:00Z",
                "body": standalones[slot2], "social_account_id": li_id,
                "metadata": {"batch": "sunday-may4-10", "day": day_label, "kind": "post-standalone", "standalone_index": slot2, "slot": 2},
            })

    if 14 in standalones:
        items.append({
            "platform": "linkedin", "content_type": "standalone", "status": "draft",
            "scheduled_at": None,
            "body": standalones[14], "social_account_id": li_id,
            "metadata": {"batch": "sunday-may4-10", "kind": "post-standalone-reserve", "standalone_index": 14, "note": "flex/reserve"},
        })

    print(f"\nPushing {len(items)} items (clean):")
    pushed = 0
    failed = []
    new_ids = []
    for i, item in enumerate(items, start=1):
        kind = item["metadata"]["kind"]
        day = item["metadata"].get("day", "?")
        print(f"  [{i}/{len(items)}] {kind} ({day})... ", end="", flush=True)
        code, resp = http_json("POST", f"{BASE}/api/content", item, token=token)
        if code in (200, 201):
            cid = resp.get("item", {}).get("id") or resp.get("id")
            pushed += 1
            if cid:
                new_ids.append(cid)
            print(f"OK ({cid[:8] if cid else '?'})")
        else:
            print(f"FAIL [{code}] {str(resp)[:120]}")
            failed.append((i, code, resp))

    with open("/home/jared/exports/portal-files/sunday-batch-may4-10/created-ids.json", "w") as f:
        json.dump({"ids": new_ids, "count": len(new_ids), "pushed_at": "2026-05-03"}, f, indent=2)

    print(f"\nDone. Pushed {pushed}/{len(items)}.")
    print(f"Review: https://surf.purebrain.ai/social.html")


if __name__ == "__main__":
    main()
