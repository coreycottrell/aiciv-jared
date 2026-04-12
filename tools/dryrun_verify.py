#!/usr/bin/env python3
"""Dry run: verify OLD_TEXT matches on all target pages before applying changes."""
import json
import subprocess

USER = "Aether"
PASS = "FlFr2VOtlHiHaJWjzW96OHUJ"
PAGE_IDS = [688, 689, 468, 439]

def fetch_page(page_id):
    url = f"https://purebrain.ai/wp-json/wp/v2/pages/{page_id}?context=edit"
    result = subprocess.run(
        ["curl", "-s", "-u", f"{USER}:{PASS}",
         "-H", "User-Agent: Mozilla/5.0 (compatible; WP REST API client)",
         url],
        capture_output=True, text=True
    )
    return result.stdout

# The exact OLD_TEXT from the update script
OLD_TEXT = (
    'First, make sure you\'re logged into Telegram. If you\'re not sure, visit '
    '<a href=\\"https://web.telegram.org/\\" target=\\"_blank\\" rel=\\"noopener\\" '
    'style=\\"color:var(--light-blue);\\">'
    'web.telegram.org</a> to confirm you\'re signed in.'
)

NEW_TEXT = (
    "If you're on a desktop, visit "
    '<a href=\\"https://web.telegram.org\\" target=\\"_blank\\">web.telegram.org</a> '
    "to confirm you're signed in. "
    "If you're on your phone, "
    '<a href=\\"https://telegram.org/dl\\" target=\\"_blank\\">tap here</a> '
    "to download the Telegram app or open it."
)

print(f"OLD repr: {repr(OLD_TEXT)}")
print(f"NEW repr: {repr(NEW_TEXT)}")
print()

for page_id in PAGE_IDS:
    raw = fetch_page(page_id)
    data = json.loads(raw)
    content = data.get('content', {}).get('raw', '')
    elementor = data.get('meta', {}).get('_elementor_data', '') or ''

    pc_count = content.count(OLD_TEXT)
    ed_count = elementor.count(OLD_TEXT)

    print(f"Page {page_id}: post_content={pc_count}, _elementor_data={ed_count}", end="")

    if pc_count == 0 and ed_count == 0:
        # Debug
        idx = content.find("logged into Telegram")
        if idx != -1:
            # extract actual text and compare char by char with our OLD_TEXT
            anchor = "First, make sure"
            start = content.rfind(anchor, max(0, idx-200), idx+1)
            actual = content[start:start+len(OLD_TEXT)]
            print(f" -- NO MATCH! Actual vs OLD char diff:")
            for i, (a, b) in enumerate(zip(actual, OLD_TEXT)):
                if a != b:
                    print(f"   Diff at pos {i}: actual={repr(a)}(ord={ord(a)}) vs old={repr(b)}(ord={ord(b)})")
            if len(actual) != len(OLD_TEXT):
                print(f"   Length diff: actual={len(actual)} vs old={len(OLD_TEXT)}")
        else:
            print(f" -- 'logged into Telegram' not found at all")
    else:
        print(f" -- MATCH CONFIRMED")
