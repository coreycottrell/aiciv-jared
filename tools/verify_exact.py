#!/usr/bin/env python3
"""Determine exact characters in old text and build replacement."""
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

# Extract exact old text from the content using known boundaries
ANCHOR = "logged into Telegram"
END_MARKER = "<br><br>Now"

idx = content.find(ANCHOR)
start = content.rfind("First,", max(0, idx-100), idx)
end = content.find(END_MARKER, idx)

old_text = content[start:end]
print(f"=== EXACT OLD TEXT (post_content) ===")
print(f"Length: {len(old_text)}")
print(f"Repr: {repr(old_text)}")
print()

# Print each char
print("Character-by-character:")
for i, ch in enumerate(old_text):
    if ord(ch) < 32:
        print(f"  [{i}] CONTROL ord={ord(ch)}")
    else:
        print(f"  [{i}] {repr(ch)} ord={ord(ch)}")
