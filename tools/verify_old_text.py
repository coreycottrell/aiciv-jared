#!/usr/bin/env python3
"""Verify the exact old text string against page 688 content."""
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

# The exact string we want to replace, constructed byte by byte.
# From the repr output we saw:
#   `First, make sure you\'re logged into Telegram. If you\'re not sure, visit
#    <a href=\"https://web.telegram.org/\" target=\"_blank\" rel=\"noopener\"
#    style=\"color:var(--light-blue);\">web.telegram.org</a> to confirm you\'re signed in.`
#
# In Python string terms:
#   \'  = backslash + apostrophe  -> literal characters \ and '
#   \"  = backslash + double-quote -> literal characters \ and "
#
OLD = "First, make sure you\\'re logged into Telegram. If you\\'re not sure, visit <a href=\\\"https://web.telegram.org/\\\" target=\\\"_blank\\\" rel=\\\"noopener\\\" style=\\\"color:var(--light-blue);\\\">web.telegram.org</a> to confirm you\\'re signed in."

print(f"OLD string repr: {repr(OLD)}")
print(f"OLD string length: {len(OLD)}")
print()

count_pc = content.count(OLD)
count_ed = elementor.count(OLD)
print(f"Occurrences in post_content: {count_pc}")
print(f"Occurrences in _elementor_data: {count_ed}")

if count_pc > 0:
    idx = content.find(OLD)
    print(f"\nContext in post_content (50 chars before/after):")
    print(repr(content[max(0,idx-50):idx+len(OLD)+50]))

if count_ed > 0:
    idx2 = elementor.find(OLD)
    print(f"\nContext in _elementor_data (50 chars before/after):")
    print(repr(elementor[max(0,idx2-50):idx2+len(OLD)+50]))
