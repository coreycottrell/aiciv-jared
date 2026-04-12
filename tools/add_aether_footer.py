#!/usr/bin/env python3
"""
Add AETHER footer text to all public PureBrain pages via WordPress REST API.

Footer text: "Built by AETHER (an AI) for PureBrain.ai, PureMarketing.ai & PureTechnology.ai"
Style: 12px, muted gray #555, centered, subtle padding.

Idempotent: checks for existing "aether_footer" ID before inserting.
"""

import os
import json
import base64
import time
import requests
from dotenv import load_dotenv

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

WP_USER = "Aether"
WP_PASS = os.getenv("PUREBRAIN_WP_APP_PASSWORD")
BASE_URL = "https://purebrain.ai/wp-json/wp/v2"

auth_str = f"{WP_USER}:{WP_PASS}"
auth_b64 = base64.b64encode(auth_str.encode()).decode()

HEADERS = {
    "Authorization": f"Basic {auth_b64}",
    "Content-Type": "application/json",
    "User-Agent": "PureBrain-Aether/1.0"
}

# All pages to update: (page_id, page_name)
PAGES = [
    (11,   "Homepage"),
    (439,  "pay-test"),
    (468,  "pay-test-sandbox"),
    (689,  "pay-test-2"),
    (688,  "pay-test-sandbox-2"),
    (777,  "Calculator"),
    (620,  "AI Partnership Audit"),
    (1116, "AI Adoption Review"),
    (752,  "Compare hub"),
    (753,  "vs ChatGPT"),
    (754,  "vs Claude"),
    (755,  "vs Copilot"),
    (756,  "vs Custom GPTs"),
    (757,  "vs DeepSeek"),
    (758,  "vs Gemini"),
    (759,  "vs Jasper"),
    (760,  "vs Perplexity"),
]

FOOTER_HTML = (
    '<p style="text-align:center;font-size:12px;color:#555;'
    'margin:0;padding:10px 0;">'
    'Built by AETHER (an AI) for PureBrain.ai, PureMarketing.ai &amp; PureTechnology.ai'
    '</p>'
)

def make_footer_section(page_id):
    """Build a minimal Elementor section JSON object for the footer."""
    return {
        "id": f"aether_footer_{page_id}",
        "elType": "section",
        "isInner": False,
        "settings": {
            "padding": {
                "unit": "px",
                "top": "20",
                "right": "0",
                "bottom": "20",
                "left": "0",
                "isLinked": False
            },
            "background_background": "classic",
            "background_color": "transparent"
        },
        "elements": [
            {
                "id": f"aether_footer_col_{page_id}",
                "elType": "column",
                "isInner": False,
                "settings": {
                    "_column_size": 100,
                    "_inline_size": None
                },
                "elements": [
                    {
                        "id": f"aether_footer_txt_{page_id}",
                        "elType": "widget",
                        "widgetType": "text-editor",
                        "isInner": False,
                        "settings": {
                            "editor": FOOTER_HTML,
                            "align": "center"
                        },
                        "elements": []
                    }
                ]
            }
        ]
    }


def get_page_elementor_data(page_id):
    """Fetch page meta and return parsed _elementor_data list, or None on error."""
    url = f"{BASE_URL}/pages/{page_id}?context=edit"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    if resp.status_code != 200:
        print(f"  ERROR fetching page {page_id}: HTTP {resp.status_code}")
        return None, None

    page_data = resp.json()
    raw_elem = page_data.get("meta", {}).get("_elementor_data", "")

    if not raw_elem or raw_elem == "[]" or raw_elem == "":
        print(f"  Page {page_id} has no Elementor data (raw: {repr(raw_elem[:80])})")
        return page_data, []

    try:
        parsed = json.loads(raw_elem)
        return page_data, parsed
    except json.JSONDecodeError as e:
        print(f"  ERROR: Could not parse _elementor_data for page {page_id}: {e}")
        return page_data, None


def footer_already_exists(elements_list, page_id):
    """Check if aether_footer already present anywhere in the structure."""
    serialized = json.dumps(elements_list)
    return f"aether_footer_{page_id}" in serialized or "aether_footer" in serialized


def update_page_elementor_data(page_id, updated_elements):
    """PUT the updated _elementor_data back to WordPress."""
    new_json_str = json.dumps(updated_elements, ensure_ascii=False)

    # Validate round-trip before deploying
    try:
        json.loads(new_json_str)
    except json.JSONDecodeError as e:
        print(f"  ERROR: JSON validation failed before deploy: {e}")
        return False

    payload = {
        "meta": {
            "_elementor_data": new_json_str
        }
    }

    url = f"{BASE_URL}/pages/{page_id}"
    resp = requests.post(url, headers=HEADERS, json=payload, timeout=30)

    if resp.status_code in (200, 201):
        return True
    else:
        print(f"  ERROR updating page {page_id}: HTTP {resp.status_code} - {resp.text[:200]}")
        return False


def clear_elementor_cache():
    """Clear Elementor's PHP rendering cache."""
    url = "https://purebrain.ai/wp-json/elementor/v1/cache"
    resp = requests.delete(url, headers=HEADERS, timeout=30)
    if resp.status_code in (200, 204):
        print("  Elementor cache cleared successfully.")
        return True
    else:
        print(f"  WARNING: Cache clear returned HTTP {resp.status_code} - {resp.text[:100]}")
        return False


def process_page(page_id, page_name):
    """Process a single page: fetch, check, append footer, update."""
    print(f"\n[Page {page_id}] {page_name}")

    page_data, elements = get_page_elementor_data(page_id)
    if elements is None:
        print(f"  SKIPPED - could not retrieve valid Elementor data")
        return "error"

    if footer_already_exists(elements, page_id):
        print(f"  SKIPPED - aether_footer already present (idempotent check passed)")
        return "skipped"

    footer_section = make_footer_section(page_id)
    elements.append(footer_section)

    # Validate the new structure
    test_str = json.dumps(elements, ensure_ascii=False)
    try:
        json.loads(test_str)
    except json.JSONDecodeError as e:
        print(f"  ERROR: New JSON invalid after appending footer: {e}")
        return "error"

    success = update_page_elementor_data(page_id, elements)
    if success:
        print(f"  SUCCESS - footer appended ({len(test_str)} chars total)")
        return "updated"
    else:
        return "error"


def main():
    print("=" * 60)
    print("AETHER Footer Deployment")
    print("Target: All public PureBrain pages")
    print("=" * 60)

    results = {
        "updated": [],
        "skipped": [],
        "error": []
    }

    for page_id, page_name in PAGES:
        status = process_page(page_id, page_name)
        results[status].append((page_id, page_name))
        time.sleep(0.5)  # Be gentle with the API

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Updated:  {len(results['updated'])} pages")
    for pid, pname in results["updated"]:
        print(f"  - [{pid}] {pname}")

    print(f"Skipped (already has footer): {len(results['skipped'])} pages")
    for pid, pname in results["skipped"]:
        print(f"  - [{pid}] {pname}")

    print(f"Errors:   {len(results['error'])} pages")
    for pid, pname in results["error"]:
        print(f"  - [{pid}] {pname}")

    # Clear Elementor cache once after all updates
    if results["updated"]:
        print("\nClearing Elementor cache...")
        clear_elementor_cache()
    else:
        print("\nNo pages updated - skipping cache clear.")

    return results


if __name__ == "__main__":
    main()
