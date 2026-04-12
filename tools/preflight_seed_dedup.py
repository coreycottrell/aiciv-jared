#!/usr/bin/env python3
"""
PRE-FLIGHT: Check which pages contain the v4 chat flow script
and whether they already have the dedup fix.
"""
import json
import urllib.request
import urllib.error
import base64

WP_URL = "https://purebrain.ai"
WP_USER = "Aether"
WP_PASS = "ZGuh 1W8k WpWM c9iy kqyd buPr"
AUTH_HEADER = "Basic " + base64.b64encode(f"{WP_USER}:{WP_PASS}".encode()).decode()

PAGES = [
    {"id": 1232, "slug": "pay-test-sandbox-3"},
    {"id": 688,  "slug": "pay-test-sandbox-2"},
    {"id": 689,  "slug": "pay-test-2"},
]

MARKER_OLD = "Post-Payment Chat Flow"
MARKER_NEW = "_seedFiredStages"


def fetch_page(page_id):
    url = f"{WP_URL}/wp-json/wp/v2/pages/{page_id}?context=edit"
    headers = {"Authorization": AUTH_HEADER, "User-Agent": "Mozilla/5.0"}
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:200]
    except Exception as ex:
        return 0, str(ex)


for page in PAGES:
    print(f"\nChecking page {page['id']} ({page['slug']})...")
    status, data = fetch_page(page["id"])
    if status != 200:
        print(f"  FETCH ERROR: status {status}")
        continue

    content = data.get("content", {}).get("raw", "")
    elementor = data.get("meta", {}).get("_elementor_data", "")

    has_old = MARKER_OLD in content
    has_new = MARKER_NEW in content
    has_old_el = MARKER_OLD in elementor if elementor else False
    has_new_el = MARKER_NEW in elementor if elementor else False

    print(f"  content.raw ({len(content)} chars):")
    print(f"    '{MARKER_OLD}' present: {has_old}")
    print(f"    '{MARKER_NEW}' present: {has_new}")
    if has_old and not has_new:
        print(f"    STATUS: NEEDS UPDATE")
    elif has_new:
        print(f"    STATUS: ALREADY UPDATED")
    else:
        print(f"    STATUS: v4 script not embedded in content.raw")

    if elementor:
        print(f"  _elementor_data ({len(elementor)} chars):")
        print(f"    '{MARKER_OLD}' present: {has_old_el}")
        print(f"    '{MARKER_NEW}' present: {has_new_el}")
    else:
        print(f"  _elementor_data: empty/not present")
