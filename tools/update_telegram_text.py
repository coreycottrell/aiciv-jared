#!/usr/bin/env python3
"""
Surgical text replacement: Update Telegram onboarding message on pay test pages.
Pages: 688, 689, 468, 439
Page 11: No chatbox Telegram text found - skipping.

This script replaces only the BotFather-section Telegram message.
Pages 468 and 439 also have a SEPARATE "Telegram Login Confirmation" section
with different text - that section is NOT touched.
"""

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

def update_page(page_id, post_content, elementor_data):
    """Send POST request to update both post_content and _elementor_data.
    Writes payload to a temp file to avoid OS argument length limits."""
    import tempfile
    import os

    payload = json.dumps({
        "content": post_content,
        "meta": {
            "_elementor_data": elementor_data
        }
    })

    # Write payload to temp file
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    tmp.write(payload)
    tmp.close()

    url = f"https://purebrain.ai/wp-json/wp/v2/pages/{page_id}"
    try:
        result = subprocess.run(
            ["curl", "-s", "-X", "POST",
             "-u", f"{USER}:{PASS}",
             "-H", "User-Agent: Mozilla/5.0 (compatible; WP REST API client)",
             "-H", "Content-Type: application/json",
             "-d", f"@{tmp.name}",
             url],
            capture_output=True, text=True
        )
        return result.stdout
    finally:
        os.unlink(tmp.name)

def clear_elementor_cache():
    """Clear Elementor cache."""
    result = subprocess.run(
        ["curl", "-s", "-X", "DELETE",
         "-u", f"{USER}:{PASS}",
         "-H", "User-Agent: Mozilla/5.0 (compatible; WP REST API client)",
         "https://purebrain.ai/wp-json/elementor/v1/cache"],
        capture_output=True, text=True
    )
    return result.stdout

# -----------------------------------------------------------------------
# OLD text - exactly as it appears in WordPress raw post_content.
# Character analysis confirmed:
#   - Apostrophes are literal ' (ord 39), no backslash prefix
#   - HTML attr quotes are backslash + doublequote: \" (ord 92 + ord 34)
# In Python string: \" = backslash-doublequote (need to write as \\\")
# -----------------------------------------------------------------------
OLD_TEXT = (
    'First, make sure you\'re logged into Telegram. If you\'re not sure, visit '
    '<a href=\\"https://web.telegram.org/\\" target=\\"_blank\\" rel=\\"noopener\\" '
    'style=\\"color:var(--light-blue);\\">'
    'web.telegram.org</a> to confirm you\'re signed in.'
)

# -----------------------------------------------------------------------
# NEW text - as requested by Jared.
# Keep same escaping style for HTML attrs (backslash + doublequote)
# but since single quotes don't need escaping in JS template literals,
# we can also use single-quote style per the request spec.
# Using single quotes on hrefs (per request) since they don't need escaping.
# -----------------------------------------------------------------------
NEW_TEXT = (
    "If you're on a desktop, visit "
    '<a href=\\"https://web.telegram.org\\" target=\\"_blank\\">web.telegram.org</a> '
    "to confirm you're signed in. "
    "If you're on your phone, "
    '<a href=\\"https://telegram.org/dl\\" target=\\"_blank\\">tap here</a> '
    "to download the Telegram app or open it."
)

print(f"OLD text repr: {repr(OLD_TEXT)}")
print(f"OLD text length: {len(OLD_TEXT)}")
print()
print(f"NEW text repr: {repr(NEW_TEXT)}")
print(f"NEW text length: {len(NEW_TEXT)}")
print()

# Quick sanity check: verify OLD_TEXT is NOT an empty or wrong string
assert "logged into Telegram" in OLD_TEXT, "OLD_TEXT sanity check failed"
assert "web.telegram.org" in NEW_TEXT, "NEW_TEXT sanity check failed"
assert "telegram.org/dl" in NEW_TEXT, "NEW_TEXT missing dl link"

for page_id in PAGE_IDS:
    print(f"\n{'='*60}")
    print(f"Processing page {page_id}...")
    raw = fetch_page(page_id)
    try:
        data = json.loads(raw)
    except Exception as e:
        print(f"  ERROR parsing JSON: {e}")
        print(f"  Raw (first 300): {raw[:300]}")
        continue

    post_content = data.get('content', {}).get('raw', '')
    meta = data.get('meta', {})
    elementor = meta.get('_elementor_data', '') or ''

    # Count occurrences
    old_count_pc = post_content.count(OLD_TEXT)
    old_count_ed = elementor.count(OLD_TEXT)
    print(f"  OLD text in post_content: {old_count_pc} occurrence(s)")
    print(f"  OLD text in _elementor_data: {old_count_ed} occurrence(s)")

    if old_count_pc == 0 and old_count_ed == 0:
        print(f"  SKIPPING: old text not found in either field on page {page_id}")
        # Debug: try to find what's there
        idx = post_content.find("logged into Telegram")
        if idx != -1:
            print(f"  DEBUG - 'logged into Telegram' found at {idx} but full OLD_TEXT doesn't match")
            print(f"  DEBUG - content around it: {repr(post_content[max(0,idx-50):idx+200])}")
        continue

    # Perform replacement in-memory
    new_post_content = post_content.replace(OLD_TEXT, NEW_TEXT)
    new_elementor = elementor.replace(OLD_TEXT, NEW_TEXT)

    # Verify replacement
    new_count_pc = new_post_content.count(NEW_TEXT)
    new_count_ed = new_elementor.count(NEW_TEXT)
    remaining_old_pc = new_post_content.count(OLD_TEXT)
    remaining_old_ed = new_elementor.count(OLD_TEXT)

    print(f"  After replacement:")
    print(f"    NEW text in post_content: {new_count_pc}")
    print(f"    NEW text in _elementor_data: {new_count_ed}")
    print(f"    OLD text remaining in post_content: {remaining_old_pc}")
    print(f"    OLD text remaining in _elementor_data: {remaining_old_ed}")

    if remaining_old_pc > 0 or remaining_old_ed > 0:
        print(f"  WARNING: old text still present after replacement!")

    # Push update
    print(f"  Pushing update to WordPress...")
    result_raw = update_page(page_id, new_post_content, new_elementor)
    try:
        resp = json.loads(result_raw)
        if 'id' in resp:
            print(f"  SUCCESS: Page {page_id} updated. Modified: {resp.get('modified', 'unknown')}")
        elif 'code' in resp:
            print(f"  API ERROR: {resp.get('code')} - {resp.get('message', '')[:200]}")
        else:
            print(f"  UNEXPECTED RESPONSE: {result_raw[:500]}")
    except Exception as e:
        print(f"  ERROR parsing update response: {e}")
        print(f"  Raw: {result_raw[:500]}")

print(f"\n{'='*60}")
print("Clearing Elementor cache...")
cache_result = clear_elementor_cache()
print(f"Cache clear result: {cache_result[:300]}")
print("\nAll done.")
