#!/usr/bin/env python3
"""Fetch and display all pending_review content from social.purebrain.ai."""

import json
import requests

API = "https://social.purebrain.ai/api"
TOKEN = "pb_live_aether_social_2026"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}

resp = requests.get(f"{API}/content?status=pending_review&limit=500", headers=HEADERS)
print(f"Status: {resp.status_code}")
if resp.status_code != 200:
    print(f"Error: {resp.text[:500]}")
    exit(1)

data = resp.json()
items = data.get("items", [])
print(f"Total pending_review items: {len(items)}\n")

for i, item in enumerate(items):
    content_type = item.get("content_type", "post")
    media_refs = item.get("media_refs", "[]")
    if isinstance(media_refs, str):
        try:
            media_refs = json.loads(media_refs)
        except:
            media_refs = []
    has_image = bool(media_refs)
    title = item.get("title") or ""
    body_preview = (item.get("body") or "")[:60].replace("\n", " ")

    print(f"{i+1:3d}. ID: {item['id']}")
    print(f"     Type: {content_type} | Image: {'Yes' if has_image else 'No'} | Title: {title}")
    print(f"     Body: {body_preview}...")
    print()
