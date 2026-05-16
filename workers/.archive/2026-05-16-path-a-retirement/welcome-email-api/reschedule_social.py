#!/usr/bin/env python3
"""
Reschedule ALL social.purebrain.ai "pending_review" content items.

Schedule pattern (starting April 30, 2026):
- 8:30 AM ET (12:30 UTC): Blog post
- 11:00 AM ET (15:00 UTC): Standalone image post
- 1:00 PM ET (17:00 UTC): Standalone image post
- 3:00 PM ET (19:00 UTC): Standalone image post
- 5:00 PM ET (21:00 UTC): Standalone image post
- 8:00 PM ET (00:00 UTC next day): Text-only post

Usage:
  python3 reschedule_social.py                    # Uses pb_live_aether_social_2026 token
  python3 reschedule_social.py --token <TOKEN>    # Use specific token
  python3 reschedule_social.py --dry-run          # Preview without making changes

Author: marketing-automation-specialist
Date: 2026-04-27
"""

import json
import sys
import os
import requests
from datetime import datetime, timedelta

API = "https://social.purebrain.ai/api"

# Token priority: CLI arg > env var > default
TOKEN = "pb_live_aether_social_2026"
DRY_RUN = False

if "--token" in sys.argv:
    idx = sys.argv.index("--token")
    TOKEN = sys.argv[idx + 1]
if "--dry-run" in sys.argv:
    DRY_RUN = True

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}

# Daily schedule slots (UTC times)
DAILY_SLOTS = [
    {"time": "12:30", "type": "blog", "label": "8:30 AM ET - Blog"},
    {"time": "15:00", "type": "standalone_image", "label": "11:00 AM ET - Standalone image"},
    {"time": "17:00", "type": "standalone_image", "label": "1:00 PM ET - Standalone image"},
    {"time": "19:00", "type": "standalone_image", "label": "3:00 PM ET - Standalone image"},
    {"time": "21:00", "type": "standalone_image", "label": "5:00 PM ET - Standalone image"},
    {"time": "00:00", "type": "text_only", "label": "8:00 PM ET - Text-only", "next_day": True},
]


def fetch_pending_content():
    """Get all pending_review content."""
    resp = requests.get(f"{API}/content?status=pending_review&limit=500", headers=HEADERS)
    if resp.status_code == 401:
        print(f"ERROR: 401 Unauthorized. Token may be expired or invalid.")
        print(f"  Token used: {TOKEN[:10]}...")
        print(f"\nTo get a fresh token, login first:")
        print(f'  curl -s -X POST {API}/login -H "Content-Type: application/json" \\')
        print(f'    -d \'{{"email":"jared@puretechnology.nyc","password":"YOUR_PASSWORD"}}\' | python3 -c "import sys,json; print(json.load(sys.stdin)[\'token\'])"')
        print(f"\nThen re-run: python3 reschedule_social.py --token <TOKEN>")
        sys.exit(1)
    if resp.status_code != 200:
        print(f"ERROR fetching content: {resp.status_code} - {resp.text[:300]}")
        sys.exit(1)
    data = resp.json()
    return data.get("items", [])


def classify_item(item):
    """Classify content item into: blog, standalone_image, text_only."""
    content_type = (item.get("content_type") or "post").lower()
    media_refs = item.get("media_refs", "[]")

    if isinstance(media_refs, str):
        try:
            media_refs = json.loads(media_refs)
        except:
            media_refs = []

    has_image = len(media_refs) > 0 if media_refs else False

    if content_type == "blog":
        return "blog"
    elif has_image:
        return "standalone_image"
    else:
        return "text_only"


def schedule_item(item_id, scheduled_at):
    """Update item with scheduled_at and set status to 'scheduled'."""
    if DRY_RUN:
        return True

    payload = {
        "scheduled_at": scheduled_at,
        "status": "scheduled",
    }
    resp = requests.patch(f"{API}/content/{item_id}", headers=HEADERS, json=payload)
    if resp.status_code != 200:
        print(f"  ERROR scheduling {item_id}: {resp.status_code} - {resp.text[:200]}")
        return False
    return True


def main():
    if DRY_RUN:
        print("[DRY RUN MODE - No changes will be made]\n")

    print("Fetching pending_review content from social.purebrain.ai...")
    items = fetch_pending_content()
    print(f"Found {len(items)} pending_review items.\n")

    if not items:
        print("No items to schedule.")
        return

    # Classify items
    blogs = []
    image_posts = []
    text_posts = []

    for item in items:
        category = classify_item(item)
        if category == "blog":
            blogs.append(item)
        elif category == "standalone_image":
            image_posts.append(item)
        else:
            text_posts.append(item)

    print(f"Classification:")
    print(f"  Blogs: {len(blogs)}")
    print(f"  Standalone image posts: {len(image_posts)}")
    print(f"  Text-only posts: {len(text_posts)}")
    print()

    # Start scheduling from April 30, 2026
    start_date = datetime(2026, 4, 30)
    current_date = start_date

    scheduled_count = 0
    blog_idx = 0
    image_idx = 0
    text_idx = 0
    day_number = 0

    while blog_idx < len(blogs) or image_idx < len(image_posts) or text_idx < len(text_posts):
        date_str = current_date.strftime("%Y-%m-%d")
        print(f"\n--- {date_str} ---")

        for slot in DAILY_SLOTS:
            slot_type = slot["type"]
            slot_time = slot["time"]
            is_next_day = slot.get("next_day", False)

            if is_next_day:
                slot_date = current_date + timedelta(days=1)
            else:
                slot_date = current_date

            scheduled_at = f"{slot_date.strftime('%Y-%m-%d')}T{slot_time}:00Z"

            item = None
            if slot_type == "blog" and blog_idx < len(blogs):
                item = blogs[blog_idx]
                blog_idx += 1
            elif slot_type == "standalone_image" and image_idx < len(image_posts):
                item = image_posts[image_idx]
                image_idx += 1
            elif slot_type == "text_only" and text_idx < len(text_posts):
                item = text_posts[text_idx]
                text_idx += 1

            if item:
                title_preview = (item.get("title") or item.get("body", "")[:50]).strip().replace("\n", " ")
                if len(title_preview) > 50:
                    title_preview = title_preview[:50]
                success = schedule_item(item["id"], scheduled_at)
                status_str = "OK" if success else "FAILED"
                dry = " (dry)" if DRY_RUN else ""
                print(f"  [{status_str}{dry}] {slot['label']}: \"{title_preview}\"")
                if success:
                    scheduled_count += 1
            else:
                print(f"  [EMPTY] {slot['label']}: No {slot_type} content available")

        current_date += timedelta(days=1)
        day_number += 1

        if day_number > 30:
            print("\n[WARNING] Reached 30-day limit. Stopping.")
            break

    # Summary
    print(f"\n{'='*60}")
    print(f"SCHEDULING COMPLETE {'(DRY RUN)' if DRY_RUN else ''}")
    print(f"{'='*60}")
    print(f"Total items scheduled: {scheduled_count}")
    print(f"Days filled: {day_number}")
    print(f"Date range: {start_date.strftime('%Y-%m-%d')} to {(start_date + timedelta(days=day_number-1)).strftime('%Y-%m-%d')}")

    # Report shortages
    total_blog_slots = day_number
    total_image_slots = day_number * 4
    total_text_slots = day_number

    blog_shortage = max(0, total_blog_slots - len(blogs))
    image_shortage = max(0, total_image_slots - len(image_posts))
    text_shortage = max(0, total_text_slots - len(text_posts))

    if blog_shortage or image_shortage or text_shortage:
        print(f"\nCONTENT SHORTAGES (unfilled slots across {day_number} days):")
        if blog_shortage:
            print(f"  Blog posts needed: {blog_shortage} more")
        if image_shortage:
            print(f"  Standalone image posts needed: {image_shortage} more")
        if text_shortage:
            print(f"  Text-only posts needed: {text_shortage} more")
    else:
        print("\nAll slots filled successfully!")


if __name__ == "__main__":
    main()
