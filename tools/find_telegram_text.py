#!/usr/bin/env python3
import json
import sys
import subprocess

PAGE_IDS = [688, 689, 468, 439, 11]
USER = "Aether"
PASS = "FlFr2VOtlHiHaJWjzW96OHUJ"
SEARCH_TERMS = ['logged into Telegram', 'web.telegram.org', "make sure you're logged", "make sure you're", "Telegram"]

def fetch_page(page_id):
    url = f"https://purebrain.ai/wp-json/wp/v2/pages/{page_id}?context=edit"
    result = subprocess.run(
        ["curl", "-s", "-u", f"{USER}:{PASS}",
         "-H", "User-Agent: Mozilla/5.0 (compatible; WP REST API client)",
         url],
        capture_output=True, text=True
    )
    return result.stdout

for page_id in PAGE_IDS:
    raw = fetch_page(page_id)
    try:
        data = json.loads(raw)
    except Exception as e:
        print(f"PAGE {page_id}: JSON parse error - {e}")
        print(f"  Raw: {raw[:300]}")
        continue

    if 'code' in data and data.get('code') != 0:
        print(f"PAGE {page_id}: API error - {data}")
        continue

    content = data.get('content', {}).get('raw', '')
    meta = data.get('meta', {})
    elementor = meta.get('_elementor_data', '') or ''

    found_any = False
    for term in SEARCH_TERMS:
        idx = content.find(term)
        if idx != -1:
            found_any = True
            print(f"\n=== PAGE {page_id} | post_content | term='{term}' | idx={idx} ===")
            print(repr(content[max(0, idx-150):idx+300]))

        idx2 = elementor.find(term)
        if idx2 != -1:
            found_any = True
            print(f"\n=== PAGE {page_id} | _elementor_data | term='{term}' | idx={idx2} ===")
            print(repr(elementor[max(0, idx2-150):idx2+300]))

    if not found_any:
        print(f"\n=== PAGE {page_id}: 'Telegram' text NOT found ===")
        print(f"  post_content length: {len(content)}")
        print(f"  _elementor_data length: {len(elementor)}")
        print(f"  post_content preview: {repr(content[:300])}")
