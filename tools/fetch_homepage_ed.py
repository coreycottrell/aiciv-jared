#!/usr/bin/env python3
"""Fetch homepage elementor data and find calculator section."""

import json
import urllib.request
import base64
import os
import sys
from dotenv import load_dotenv

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

WP_USER = "Aether"
WP_APP_PASS = os.getenv('PUREBRAIN_WP_APP_PASSWORD', '41w3 xWWZ 11em UXgj hjAF sx2T')
BASE_URL = "https://purebrain.ai/wp-json/wp/v2/pages"

creds = base64.b64encode(f"{WP_USER}:{WP_APP_PASS}".encode()).decode()
headers = {
    "Authorization": f"Basic {creds}",
    "Content-Type": "application/json",
}

# Fetch page 11
url = f"{BASE_URL}/11?_fields=id,title,meta"
print(f"Fetching {url}...")
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=60) as resp:
    data = json.loads(resp.read().decode())

meta = data.get('meta', {})
print(f"Meta keys: {list(meta.keys())[:20]}")

ed_raw = meta.get('_elementor_data', '')
print(f"_elementor_data length: {len(ed_raw)}")

if ed_raw:
    # Save it
    with open('/tmp/homepage_ed.json', 'w') as f:
        f.write(ed_raw)
    print("Saved to /tmp/homepage_ed.json")

    # Try to parse
    try:
        ed = json.loads(ed_raw)
        print(f"Parsed: {type(ed)}, length: {len(ed)}")

        # Search for calculator
        for i, section in enumerate(ed):
            s_str = json.dumps(section)
            if any(term in s_str for term in ["calculator", "FREE TOOL", "Sprawl", "wasting", "140+"]):
                print(f"\nFound calculator-related section at index {i}:")
                print(f"  id: {section.get('id','')}")
                print(f"  elType: {section.get('elType','')}")
                print(f"  settings keys: {list(section.get('settings',{}).keys())[:10]}")
                # Save this section
                with open('/tmp/calc_section_found.json', 'w') as f:
                    json.dump(section, f, indent=2)
                print("  Saved to /tmp/calc_section_found.json")
                break
        else:
            print("\nNOT FOUND - dumping section summary:")
            for i, s in enumerate(ed):
                s_str = json.dumps(s)[:200]
                print(f"  [{i}] id={s.get('id','')} type={s.get('elType','')} preview={s_str[:100]}")
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        # Show first 500 chars
        print(f"First 500 chars: {ed_raw[:500]}")
else:
    print("_elementor_data is EMPTY in meta")
    # Check content
    url2 = f"{BASE_URL}/11?_fields=id,title,content"
    req2 = urllib.request.Request(url2, headers=headers)
    with urllib.request.urlopen(req2, timeout=60) as resp2:
        data2 = json.loads(resp2.read().decode())
    content = data2.get('content', {})
    print(f"Content rendered length: {len(content.get('rendered',''))}")
    print(f"Content raw length: {len(content.get('raw',''))}")

    raw = content.get('raw', '')
    if raw:
        with open('/tmp/homepage_content_raw.txt', 'w') as f:
            f.write(raw)
        print("Saved content.raw to /tmp/homepage_content_raw.txt")

        # Search in raw
        for term in ["calculator", "FREE TOOL", "Sprawl", "wasting", "140+"]:
            if term in raw:
                print(f"Found '{term}' in content.raw")
