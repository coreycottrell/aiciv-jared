#!/usr/bin/env python3
"""Patch the blog + newsletter draft bodies to remove leftover **Title**/**Subject**/etc metadata."""
import json
import os
import urllib.request
import urllib.error
import ssl
import sys

sys.path.insert(0, os.path.dirname(__file__))
from cleanup_and_repush import http_json, login, load_blog_bodies, load_newsletter_bodies

BASE = "https://social.purebrain.ai"


def main():
    token = login()
    print("Login OK.")

    # Load created IDs
    with open("/home/jared/exports/portal-files/sunday-batch-may4-10/created-ids.json") as f:
        ids = json.load(f)["ids"]
    print(f"Loaded {len(ids)} IDs from latest push.")

    # Pull all current items, match by body fingerprint
    code, resp = http_json("GET", f"{BASE}/api/content?limit=100", token=token)
    if code != 200:
        print(f"List failed: {code} {resp}")
        sys.exit(1)
    all_items = resp.get("items", [])
    items_by_id = {i["id"]: i for i in all_items}

    blogs = load_blog_bodies()
    nls = load_newsletter_bodies()

    # Re-derive ordering: items in created-ids.json were pushed in this order:
    # day-loop: blog, newsletter, promo, [standalone1], [standalone2]
    # Day 1 (Mon): blog, newsletter, promo, standalone(slot2)  -> 4 items
    # Day 2 (Tue): blog, newsletter, promo, standalone(slot1), standalone(slot2)  -> 5 items
    # Day 3-7 same as Day 2  -> 5 each
    # Reserve: 1 item
    # Total: 4 + 5*6 + 1 = 35

    ordered_kinds = []
    days_count = [4, 5, 5, 5, 5, 5, 5]  # items per day
    blog_idx = 1
    nl_idx = 1
    for day_n, count in enumerate(days_count, start=1):
        # blog
        ordered_kinds.append(("blog", blog_idx))
        # newsletter
        ordered_kinds.append(("newsletter", nl_idx))
        # promo
        ordered_kinds.append(("promo", blog_idx))
        # standalones (count - 3 of them)
        for s in range(count - 3):
            ordered_kinds.append(("standalone", None))
        blog_idx += 1
        nl_idx += 1
    ordered_kinds.append(("reserve", None))

    assert len(ordered_kinds) == len(ids), f"mismatch: {len(ordered_kinds)} vs {len(ids)}"

    patched = 0
    for cid, (kind, idx) in zip(ids, ordered_kinds):
        if kind == "blog":
            new_body = blogs[idx]
        elif kind == "newsletter":
            new_body = nls[idx]
        else:
            continue  # promo + standalone already clean
        # PATCH the body
        code, resp = http_json("PATCH", f"{BASE}/api/content/{cid}", {"body": new_body}, token=token)
        if code in (200, 201):
            patched += 1
            print(f"  Patched {kind} idx={idx}: {cid[:8]}")
        else:
            print(f"  FAIL {kind} {cid[:8]}: [{code}] {resp}")
    print(f"\nPatched {patched} items (blogs + newsletters).")


if __name__ == "__main__":
    main()
