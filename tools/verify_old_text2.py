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

# Let's find the text by the unique anchor we know exists and extract exact bytes
ANCHOR = "make sure you"
idx = content.find(ANCHOR)
print("=== EXACT BYTES in post_content around 'make sure you' ===")
# Print character by character for the relevant section
segment = content[idx:idx+300]
print(f"Segment repr: {repr(segment)}")
print()

# Also print each character's code to see exactly what's there
print("Character analysis of first 50 chars of segment:")
for i, ch in enumerate(segment[:50]):
    print(f"  [{i}] {repr(ch)} = ord {ord(ch)}")
