#!/usr/bin/env python3
"""Verify exact old text - work with actual raw bytes from the page."""
import json
import subprocess

USER = "Aether"
PASS = "FlFr2VOtlHiHaJWjzW96OHUJ"

def fetch_page(page_id):
    url = f"https://purebrain.ai/wp-json/wp/v2/pages/{page_id}?context=edit"
    result = subprocess.run(
        ["curl", "-s", "-u", f"{USER}:{PASS}",
         "-H", "User-Agent: Mozilla/5.0 (compatible; WP REST API client)",
         url],
        capture_output=True, text=True
    )
    return result.stdout

raw = fetch_page(688)
data = json.loads(raw)
content = data.get('content', {}).get('raw', '')
elementor = data.get('meta', {}).get('_elementor_data', '') or ''

# Use the unique anchor "logged into Telegram" - we saw this at idx=394153
ANCHOR = "logged into Telegram"
idx = content.find(ANCHOR)
# Go back to find "First,"
start = content.rfind("First,", max(0, idx-100), idx)
print(f"BotFather section starts at: {start}")
segment = content[start:start+350]
print(f"\n=== EXACT BYTES (post_content) from 'First,' to +350 chars ===")
print(repr(segment))
print()

# Now do same for elementor
idx2 = elementor.find(ANCHOR)
start2 = elementor.rfind("First,", max(0, idx2-100), idx2)
segment2 = elementor[start2:start2+350]
print(f"=== EXACT BYTES (_elementor_data) from 'First,' to +350 chars ===")
print(repr(segment2))
