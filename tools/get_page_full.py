#!/usr/bin/env python3
"""Fetch and save page content for surgical analysis."""
import json
import sys
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

page_id = int(sys.argv[1])
raw = fetch_page(page_id)
data = json.loads(raw)

content = data.get('content', {}).get('raw', '')
meta = data.get('meta', {})
elementor = meta.get('_elementor_data', '') or ''

# Find the BotFather deep link section and show wider context
MARKER = "BotFather deep link"
idx = content.find(MARKER)
if idx != -1:
    snippet = content[max(0, idx-50):idx+600]
    print("=== POST_CONTENT BotFather section ===")
    print(repr(snippet))
    print()

idx2 = elementor.find(MARKER)
if idx2 != -1:
    snippet2 = elementor[max(0, idx2-50):idx2+600]
    print("=== _ELEMENTOR_DATA BotFather section ===")
    print(repr(snippet2))
