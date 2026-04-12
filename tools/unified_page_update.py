#!/usr/bin/env python3
"""
Fetch Unified page (ID 1263) content, find the table, update it with new rows,
and push back to WordPress.
"""
import subprocess
import json
import re
import sys

WP_URL = "https://purebrain.ai"
PAGE_ID = "1263"
WP_USER = "Aether"
WP_PASS = "ZGuh 1W8k WpWM c9iy kqyd buPr"
HEADERS = [
    "-H", "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "-H", "Content-Type: application/json",
]

def wp_get(endpoint):
    result = subprocess.run([
        "curl", "-s",
        "-u", f"{WP_USER}:{WP_PASS}",
        *HEADERS,
        f"{WP_URL}/wp-json/wp/v2/{endpoint}"
    ], capture_output=True, text=True)
    return result.stdout

def wp_post(endpoint, data_json):
    result = subprocess.run([
        "curl", "-s", "-X", "POST",
        "-u", f"{WP_USER}:{WP_PASS}",
        *HEADERS,
        "-d", data_json,
        f"{WP_URL}/wp-json/wp/v2/{endpoint}"
    ], capture_output=True, text=True)
    return result.stdout

# ── 1. Fetch page ──────────────────────────────────────────────────────────────
print("Fetching page 1263...")
raw = wp_get(f"pages/{PAGE_ID}?context=edit&_fields=id,title,content")
data = json.loads(raw)
content_raw = data.get("content", {}).get("raw", "")
print(f"Content length: {len(content_raw)} chars")
print("\n--- FIRST 3000 CHARS ---")
print(content_raw[:3000])
print("\n--- SEARCHING FOR TABLE ---")
# Find table
if "<table" in content_raw.lower():
    idx = content_raw.lower().find("<table")
    print(content_raw[max(0,idx-100):idx+2000])
else:
    print("No <table> found in raw content.")
    # Check rendered
    rendered = data.get("content", {}).get("rendered", "")
    if "<table" in rendered.lower():
        print("Table found in RENDERED content (Elementor page)")
        idx = rendered.lower().find("<table")
        print(rendered[max(0,idx-100):idx+2000])
    else:
        print("No table in rendered either. Checking meta for elementor_data...")

# Check meta
meta = data.get("meta", {})
print(f"\nMeta keys: {list(meta.keys()) if meta else 'none'}")
