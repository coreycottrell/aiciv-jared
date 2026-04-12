#!/usr/bin/env python3
"""
Add calculator section from homepage (page 11) to pay-test-2 (page 689) and pay-test-sandbox-3 (page 1232).
"""

import json
import re
import sys
import urllib.request
import urllib.error
import base64
from dotenv import load_dotenv
import os

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

WP_USER = "Aether"
WP_APP_PASS = os.getenv('PUREBRAIN_WP_APP_PASSWORD', '41w3 xWWZ 11em UXgj hjAF sx2T')
BASE_URL = "https://purebrain.ai/wp-json/wp/v2/pages"

creds = base64.b64encode(f"{WP_USER}:{WP_APP_PASS}".encode()).decode()
headers = {
    "Authorization": f"Basic {creds}",
    "Content-Type": "application/json",
}

def fetch_page(page_id, fields="_elementor_data,content"):
    url = f"{BASE_URL}/{page_id}?_fields=id,title,content,meta"
    print(f"[fetch] GET {url}")
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

def fetch_elementor_data(page_id):
    """Fetch elementor data via meta endpoint."""
    url = f"{BASE_URL}/{page_id}?_fields=id,title,meta,content"
    print(f"[fetch_elementor] GET {url}")
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode())
    return data

def push_elementor_data(page_id, elementor_data_str):
    """Push updated _elementor_data to a page."""
    url = f"{BASE_URL}/{page_id}"
    payload = json.dumps({"meta": {"_elementor_data": elementor_data_str}}).encode()
    print(f"[push] POST {url} ({len(payload)} bytes)")
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read().decode())
    return result

def clear_elementor_cache():
    """Clear Elementor cache."""
    url = "https://purebrain.ai/wp-json/elementor/v1/cache"
    print(f"[cache] DELETE {url}")
    req = urllib.request.Request(url, headers=headers, method="DELETE")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode()
            print(f"  Cache clear response: {resp.status} {body[:100]}")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  Cache clear HTTP {e.code}: {body[:200]}")

# -----------------------------------------------------------------------
# Step 1: Fetch homepage (page 11) and find calculator section
# -----------------------------------------------------------------------
print("\n=== Step 1: Fetching homepage (page 11) ===")
homepage = fetch_elementor_data(11)

# The _elementor_data is in meta
meta = homepage.get('meta', {})
ed_raw = meta.get('_elementor_data', '')

if not ed_raw:
    # Try content
    content = homepage.get('content', {}).get('raw', '')
    if content:
        print("  _elementor_data not in meta, checking content...")
        ed_raw = content
    else:
        print("ERROR: Could not find _elementor_data on homepage")
        sys.exit(1)

print(f"  Homepage _elementor_data length: {len(ed_raw)}")

# Save homepage data for inspection
with open('/tmp/homepage_elementor_data.json', 'w') as f:
    f.write(ed_raw)
print("  Saved to /tmp/homepage_elementor_data.json")

# -----------------------------------------------------------------------
# Step 2: Parse and find the calculator section
# -----------------------------------------------------------------------
print("\n=== Step 2: Finding calculator section in homepage ===")

# Parse the elementor data
try:
    ed = json.loads(ed_raw)
    print(f"  Parsed OK. Type: {type(ed)}, length: {len(ed) if isinstance(ed, list) else 'N/A'}")
except json.JSONDecodeError as e:
    print(f"  JSON parse error: {e}")
    # It might be double-encoded
    ed = json.loads(json.loads(ed_raw))

# Search for the calculator section - look for "FREE TOOL" or "calculator" or "wasting" in the data
ed_str = ed_raw

# Find the calculator section HTML
# The section should contain "FREE TOOL", "How Much Are You Wasting", "ai-tool-stack-calculator"
search_terms = ["FREE TOOL", "How Much Are You Wasting", "ai-tool-stack-calculator", "Tool Sprawl"]
for term in search_terms:
    if term in ed_str:
        print(f"  Found term: '{term}'")
    else:
        print(f"  NOT found: '{term}'")

# The elementor data is a JSON array of sections. Let's find which section contains the calculator.
def find_sections_with_text(sections, search_text, path=""):
    """Recursively find sections containing search_text."""
    results = []
    for i, section in enumerate(sections):
        current_path = f"{path}[{i}]"
        section_str = json.dumps(section)
        if search_text in section_str:
            results.append((current_path, section.get('id', ''), section.get('elType', '')))
            # Also recurse into elements
            for elem_key in ['elements', 'widgets']:
                sub = section.get(elem_key, [])
                if sub:
                    results.extend(find_sections_with_text(sub, search_text, current_path + f".{elem_key}"))
    return results

if isinstance(ed, list):
    results = find_sections_with_text(ed, "ai-tool-stack-calculator")
    print(f"\n  Sections containing 'ai-tool-stack-calculator':")
    for r in results[:10]:
        print(f"    {r}")

    if not results:
        # Try alternate search
        results = find_sections_with_text(ed, "Tool Sprawl")
        print(f"\n  Sections containing 'Tool Sprawl':")
        for r in results[:10]:
            print(f"    {r}")

# -----------------------------------------------------------------------
# Step 3: Extract the calculator top-level section
# -----------------------------------------------------------------------
print("\n=== Step 3: Extracting calculator section ===")

calculator_section = None
calc_index = None

if isinstance(ed, list):
    for i, section in enumerate(ed):
        section_str = json.dumps(section)
        if "ai-tool-stack-calculator" in section_str or "Tool Sprawl" in section_str or "How Much Are You Wasting" in section_str:
            calculator_section = section
            calc_index = i
            print(f"  Found calculator section at index {i}, id: {section.get('id', '')}, type: {section.get('elType', '')}")
            break

if calculator_section is None:
    print("  ERROR: Could not find calculator section in homepage!")
    print("  Searching for 'FREE TOOL' or 'wasting'...")
    for i, section in enumerate(ed):
        section_str = json.dumps(section)
        if "FREE TOOL" in section_str or "wasting" in section_str.lower():
            calculator_section = section
            calc_index = i
            print(f"  Found at index {i}")
            break

if calculator_section is None:
    print("  FATAL: Calculator section not found. Dumping first 3 section IDs:")
    for i, s in enumerate(ed[:3]):
        print(f"    [{i}] id={s.get('id','')} type={s.get('elType','')} settings_keys={list(s.get('settings',{}).keys())[:5]}")
    sys.exit(1)

calc_section_str = json.dumps(calculator_section)
print(f"  Calculator section JSON length: {len(calc_section_str)}")

# Save for inspection
with open('/tmp/calculator_section.json', 'w') as f:
    json.dump(calculator_section, f, indent=2)
print("  Saved to /tmp/calculator_section.json")

# -----------------------------------------------------------------------
# Step 4: Fetch pages 689 and 1232, insert calculator section
# -----------------------------------------------------------------------
print("\n=== Step 4: Fetching target pages ===")

for page_id in [689, 1232]:
    print(f"\n--- Processing page {page_id} ---")
    page = fetch_elementor_data(page_id)
    meta_p = page.get('meta', {})
    ed_raw_p = meta_p.get('_elementor_data', '')

    if not ed_raw_p:
        print(f"  WARNING: No _elementor_data in meta, trying content...")
        ed_raw_p = page.get('content', {}).get('raw', '')

    print(f"  Page {page_id} _elementor_data length: {len(ed_raw_p)}")

    # Save backup
    with open(f'/tmp/page_{page_id}_backup.json', 'w') as f:
        f.write(ed_raw_p)
    print(f"  Saved backup to /tmp/page_{page_id}_backup.json")

    # Parse
    try:
        ed_p = json.loads(ed_raw_p)
    except json.JSONDecodeError as e:
        print(f"  JSON parse error: {e}")
        sys.exit(1)

    print(f"  Parsed OK. {len(ed_p)} top-level sections")

    # Check if calculator section already exists on this page
    ed_p_str = json.dumps(ed_p)
    if "ai-tool-stack-calculator" in ed_p_str or "Tool Sprawl" in ed_p_str:
        print(f"  WARNING: Calculator section may already exist on page {page_id}!")

    # Find insertion point: between comparison pills section and "See Why PureBrain is Different" CTA
    # Look for sections containing these markers
    insertion_index = None

    # Strategy: find the comparison pills section and insert after it
    # OR find "See Why PureBrain is Different" and insert before it
    see_why_index = None
    comparison_index = None

    for i, section in enumerate(ed_p):
        s_str = json.dumps(section)
        if "See Why PureBrain is Different" in s_str or "see-why" in s_str or "comparison" in s_str.lower():
            if see_why_index is None:
                see_why_index = i
                print(f"  Found 'See Why' section at index {i}")
        if "comparison" in s_str.lower() and "pill" in s_str.lower():
            comparison_index = i
            print(f"  Found comparison pills section at index {i}")

    # If we found "See Why PureBrain is Different", insert before it
    if see_why_index is not None:
        insertion_index = see_why_index
        print(f"  Will insert calculator section BEFORE index {see_why_index} (See Why section)")
    elif comparison_index is not None:
        insertion_index = comparison_index + 1
        print(f"  Will insert calculator section AFTER index {comparison_index} (comparison pills)")
    else:
        # Default: insert near the end, before the last 2 sections
        insertion_index = len(ed_p) - 2
        print(f"  WARNING: Could not find exact insertion point. Inserting at index {insertion_index} (near end)")
        print(f"  Section types: {[(i, s.get('elType',''), list(s.get('settings',{}).keys())[:3]) for i, s in enumerate(ed_p)]}")

    # Insert calculator section
    ed_p.insert(insertion_index, calculator_section)
    print(f"  Inserted calculator section at index {insertion_index}")
    print(f"  New section count: {len(ed_p)}")

    # Serialize back to JSON
    new_ed_str = json.dumps(ed_p)

    # Validate JSON
    try:
        json.loads(new_ed_str)
        print(f"  JSON validation: PASS ({len(new_ed_str)} chars)")
    except json.JSONDecodeError as e:
        print(f"  JSON validation FAILED: {e}")
        sys.exit(1)

    # Push to WordPress
    print(f"  Pushing to page {page_id}...")
    result = push_elementor_data(page_id, new_ed_str)
    print(f"  Push result: page id={result.get('id')}, modified={result.get('modified')}")

# -----------------------------------------------------------------------
# Step 5: Clear Elementor cache
# -----------------------------------------------------------------------
print("\n=== Step 5: Clearing Elementor cache ===")
clear_elementor_cache()

print("\n=== DONE ===")
print("Calculator section added to pages 689 and 1232.")
print("Elementor cache cleared.")
