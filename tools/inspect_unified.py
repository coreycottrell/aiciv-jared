#!/usr/bin/env python3
"""
Inspect Unified page (ID 1263) - find the table and elementor data
"""
import subprocess
import json
import sys

WP_USER = "Aether"
WP_PASS = "ZGuh 1W8k WpWM c9iy kqyd buPr"

def fetch(url):
    r = subprocess.run([
        "curl", "-s",
        "-u", f"{WP_USER}:{WP_PASS}",
        "-H", "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        url
    ], capture_output=True, text=True, timeout=30)
    return r.stdout

# Fetch page with all meta
url = "https://purebrain.ai/wp-json/wp/v2/pages/1263?context=edit"
print("Fetching page 1263 full...")
raw = fetch(url)

try:
    data = json.loads(raw)
except json.JSONDecodeError as e:
    print(f"JSON error: {e}")
    print(f"Raw (first 500): {raw[:500]}")
    sys.exit(1)

content_raw = data.get("content", {}).get("raw", "")
content_rendered = data.get("content", {}).get("rendered", "")

print(f"Raw content length: {len(content_raw)}")
print(f"Rendered content length: {len(content_rendered)}")

# Search for table in raw
if "<table" in content_raw.lower():
    idx = content_raw.lower().find("<table")
    print(f"\nTABLE FOUND IN RAW at index {idx}")
    print(content_raw[max(0,idx-300):idx+4000])
else:
    print("\nNo table in raw content")
    print("RAW CONTENT (first 3000):")
    print(content_raw[:3000])

# Search for table in rendered
if "<table" in content_rendered.lower():
    idx = content_rendered.lower().find("<table")
    print(f"\nTABLE FOUND IN RENDERED at index {idx}")
    print(content_rendered[max(0,idx-300):idx+4000])

# Check meta for _elementor_data
meta = data.get("meta", {})
print(f"\nMeta keys: {list(meta.keys())}")
elementor = meta.get("_elementor_data", "")
if elementor:
    print(f"_elementor_data length: {len(elementor)}")
    # Search for table in elementor data
    if "table" in elementor.lower() or "replaces" in elementor.lower():
        # Find context around 'replaces'
        idx = elementor.lower().find("replaces")
        if idx > -1:
            print(f"\n'replaces' found in elementor_data at {idx}")
            print(elementor[max(0,idx-200):idx+2000])
    else:
        print("No table/replaces in elementor_data")
        # Look for dollar signs (pricing content)
        idx = elementor.lower().find("3,000")
        if idx > -1:
            print(f"\n'3,000' found at {idx}")
            print(elementor[max(0,idx-500):idx+3000])
else:
    print("No _elementor_data in meta")
