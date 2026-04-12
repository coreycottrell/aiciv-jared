#!/usr/bin/env python3
"""
DEPLOYMENT: Seed dedup JS fix — pay-test-script-chat-flow-v4.js
Updated file: /home/jared/projects/AI-CIV/aether/exports/pay-test-script-chat-flow-v4.js

Changes:
  1. _seedFiredStages client-side dedup object (per orderId:stage)
  2. uuid field on seed payload (orderId + stageNumber)

Target pages:
  - 1232 (pay-test-sandbox-3)  — PRIMARY / ACTIVE
  - 688  (pay-test-sandbox-2)
  - 689  (pay-test-2)

Strategy:
  - Fetch current page content + _elementor_data
  - Locate the embedded <script> block containing the v4 chat flow
  - Replace entire script block content with updated JS
  - Push BOTH content.raw and _elementor_data back
  - Clear Elementor cache
  - Verify script contains _seedFiredStages after deployment
"""

import json
import sys
import time
import urllib.request
import urllib.error
import base64
import re

WP_URL = "https://purebrain.ai"
WP_USER = "Aether"
WP_PASS = "ZGuh 1W8k WpWM c9iy kqyd buPr"

AUTH_HEADER = "Basic " + base64.b64encode(f"{WP_USER}:{WP_PASS}".encode()).decode()

JS_FILE = "/home/jared/projects/AI-CIV/aether/exports/pay-test-script-chat-flow-v4.js"

# Pages to update — sandbox-3 first (PRIMARY), then others
TARGET_PAGES = [
    {"id": 1232, "slug": "pay-test-sandbox-3"},
    {"id": 688,  "slug": "pay-test-sandbox-2"},
    {"id": 689,  "slug": "pay-test-2"},
]

# Marker used to identify the v4 chat flow script block
SCRIPT_MARKER_OLD = "Post-Payment Chat Flow"  # present in old AND new — used to locate block
SCRIPT_MARKER_NEW = "_seedFiredStages"         # present only in new version — used to verify


def wp_request(method, path, data=None):
    """Make authenticated WordPress REST API request using urllib."""
    url = f"{WP_URL}/wp-json/{path}"
    headers = {
        "Authorization": AUTH_HEADER,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
    }
    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        headers["Content-Length"] = str(len(body))

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            resp_body = resp.read().decode("utf-8")
            try:
                return resp.status, json.loads(resp_body) if resp_body.strip() else {}
            except json.JSONDecodeError:
                return resp.status, resp_body
    except urllib.error.HTTPError as e:
        body_txt = e.read().decode("utf-8")
        print(f"  HTTP Error {e.code}: {body_txt[:400]}")
        return e.code, body_txt
    except Exception as ex:
        print(f"  Request error: {ex}")
        return 0, str(ex)


def load_new_js():
    """Read the updated JS file."""
    with open(JS_FILE, "r", encoding="utf-8") as f:
        return f.read()


def replace_script_in_html(html_content, new_js):
    """
    Find the <script> block containing the v4 chat flow and replace its contents.

    The script block looks like:
      <script>
      /* === Post-Payment Chat Flow v4.x ... */
      ...
      </script>

    We do a regex replace on the content between <script> and </script>
    where the script contains our marker.
    """
    # Pattern: <script> ... Post-Payment Chat Flow ... </script>
    # Use DOTALL so . matches newlines
    pattern = r'(<script[^>]*>)([\s\S]*?Post-Payment Chat Flow[\s\S]*?)(</script>)'

    match = re.search(pattern, html_content)
    if not match:
        print("    WARNING: Script marker 'Post-Payment Chat Flow' NOT found in content")
        return None, False

    old_script_content = match.group(2)
    print(f"    Found script block ({len(old_script_content)} chars)")

    # Check if already updated
    if SCRIPT_MARKER_NEW in old_script_content:
        print(f"    Script already contains '{SCRIPT_MARKER_NEW}' — may already be updated")
        return html_content, True  # Signal already-updated

    # Build replacement
    open_tag = match.group(1)
    close_tag = match.group(3)
    new_html = html_content[:match.start()] + open_tag + "\n" + new_js + "\n" + close_tag + html_content[match.end():]

    print(f"    Replaced script block ({len(old_script_content)} -> {len(new_js)} chars)")
    return new_html, False


def deploy_page(page_id, slug, new_js):
    """Deploy the updated JS to a single page."""
    print(f"\n{'='*60}")
    print(f"PAGE {page_id}: {slug}")
    print(f"{'='*60}")

    # 1. Fetch current page
    print(f"  [1/5] Fetching page {page_id}...")
    status, data = wp_request("GET", f"wp/v2/pages/{page_id}?context=edit")
    if status != 200 or not isinstance(data, dict):
        print(f"  ERROR: Failed to fetch page {page_id} (status {status})")
        return False

    # 2. Extract content
    content_raw = data.get("content", {}).get("raw", "")
    elementor_data_str = data.get("meta", {}).get("_elementor_data", "")

    print(f"  content.raw length: {len(content_raw)}")
    print(f"  _elementor_data length: {len(elementor_data_str)}")

    if not content_raw:
        print("  ERROR: content.raw is empty")
        return False

    # 3. Check if script is in content.raw
    if SCRIPT_MARKER_OLD not in content_raw:
        print(f"  INFO: Marker '{SCRIPT_MARKER_OLD}' not found in content.raw")
        print(f"  This page may not embed the v4 script directly — skipping")
        return True  # Not an error — page might not use this script

    # 4. Update content.raw
    print(f"  [2/5] Updating content.raw...")
    new_content_raw, already_updated = replace_script_in_html(content_raw, new_js)
    if new_content_raw is None:
        print("  ERROR: Could not locate script block in content.raw")
        return False
    if already_updated:
        print(f"  content.raw: Already contains new dedup code — will still push to ensure sync")

    # 5. Update _elementor_data if present
    new_elementor_data_str = elementor_data_str
    elementor_updated = False
    if elementor_data_str and SCRIPT_MARKER_OLD in elementor_data_str:
        print(f"  [3/5] Updating _elementor_data...")
        # _elementor_data is JSON-encoded. The script content inside is double-escaped.
        # Strategy: find the script marker in the raw JSON string and replace the entire
        # script content between the JSON-escaped <script> and <\/script> tags.

        # In JSON, the script tags appear as <script> and <\/script>
        # Find the script block
        pattern_json = r'(<script[^>]*>)([\s\S]*?Post-Payment Chat Flow[\s\S]*?)(<\\/script>)'
        match_json = re.search(pattern_json, elementor_data_str)

        if match_json:
            old_js_in_json = match_json.group(2)
            print(f"    Found script in _elementor_data ({len(old_js_in_json)} chars)")

            # JSON-escape the new JS for embedding in _elementor_data
            # The JS needs to be JSON-string-escaped (escape quotes, newlines, etc.)
            new_js_json_escaped = json.dumps(new_js)[1:-1]  # Remove surrounding quotes

            new_elementor_data_str = (
                elementor_data_str[:match_json.start()]
                + match_json.group(1)
                + "\n" + new_js_json_escaped + "\n"
                + match_json.group(3)
                + elementor_data_str[match_json.end():]
            )
            print(f"    _elementor_data updated ({len(elementor_data_str)} -> {len(new_elementor_data_str)} chars)")
            elementor_updated = True
        else:
            # Try without escaped closing tag
            pattern_json2 = r'(<script[^>]*>)([\s\S]*?Post-Payment Chat Flow[\s\S]*?)(</script>)'
            match_json2 = re.search(pattern_json2, elementor_data_str)
            if match_json2:
                old_js_in_json = match_json2.group(2)
                print(f"    Found script in _elementor_data (unescaped close, {len(old_js_in_json)} chars)")
                new_js_json_escaped = json.dumps(new_js)[1:-1]
                new_elementor_data_str = (
                    elementor_data_str[:match_json2.start()]
                    + match_json2.group(1)
                    + "\n" + new_js_json_escaped + "\n"
                    + match_json2.group(3)
                    + elementor_data_str[match_json2.end():]
                )
                print(f"    _elementor_data updated ({len(elementor_data_str)} -> {len(new_elementor_data_str)} chars)")
                elementor_updated = True
            else:
                print(f"    WARNING: Script block not found in _elementor_data — will only update content.raw")
    else:
        print(f"  [3/5] _elementor_data: script marker not found or no elementor data — skipping")

    # 6. Push update
    print(f"  [4/5] Pushing update to WordPress...")
    update_payload = {
        "content": new_content_raw,
    }
    if elementor_updated:
        update_payload["meta"] = {"_elementor_data": new_elementor_data_str}

    push_status, push_data = wp_request("POST", f"wp/v2/pages/{page_id}", update_payload)
    if push_status not in (200, 201):
        print(f"  ERROR: Push failed (status {push_status})")
        if isinstance(push_data, str):
            print(f"  Response: {push_data[:300]}")
        return False
    print(f"  Push succeeded (status {push_status})")

    # 7. Clear Elementor cache
    print(f"  [5/5] Clearing Elementor cache...")
    cache_status, cache_data = wp_request("DELETE", "elementor/v1/cache")
    print(f"  Cache clear: status {cache_status} (empty body is normal)")

    # 8. Verify
    print(f"  [VERIFY] Re-fetching page to confirm deployment...")
    time.sleep(2)
    v_status, v_data = wp_request("GET", f"wp/v2/pages/{page_id}?context=edit")
    if v_status != 200:
        print(f"  VERIFY ERROR: Could not re-fetch page (status {v_status})")
        return False

    v_content = v_data.get("content", {}).get("raw", "")
    if SCRIPT_MARKER_NEW in v_content:
        print(f"  VERIFIED: '{SCRIPT_MARKER_NEW}' found in deployed content.raw")
        return True
    else:
        print(f"  VERIFY FAILED: '{SCRIPT_MARKER_NEW}' NOT found in deployed content.raw")
        return False


def main():
    print("=" * 60)
    print("SEED DEDUP JS DEPLOYMENT")
    print("Target: pay-test-script-chat-flow-v4.js")
    print("Fix: _seedFiredStages + uuid dedup guards")
    print("=" * 60)

    # Load new JS
    print(f"\nLoading updated JS from: {JS_FILE}")
    new_js = load_new_js()
    print(f"JS size: {len(new_js)} chars")

    if SCRIPT_MARKER_NEW not in new_js:
        print(f"ERROR: New JS does not contain '{SCRIPT_MARKER_NEW}' — wrong file?")
        sys.exit(1)
    print(f"Confirmed: '{SCRIPT_MARKER_NEW}' present in new JS")

    results = {}
    for page in TARGET_PAGES:
        success = deploy_page(page["id"], page["slug"], new_js)
        results[page["slug"]] = "SUCCESS" if success else "FAILED"
        if page["id"] != TARGET_PAGES[-1]["id"]:
            time.sleep(1)

    # Summary
    print(f"\n{'='*60}")
    print("DEPLOYMENT SUMMARY")
    print(f"{'='*60}")
    for slug, result in results.items():
        icon = "✓" if result == "SUCCESS" else "✗"
        print(f"  {icon} {slug}: {result}")

    all_ok = all(v == "SUCCESS" for v in results.values())
    if all_ok:
        print("\nALL PAGES DEPLOYED SUCCESSFULLY")
        sys.exit(0)
    else:
        print("\nSOME PAGES FAILED — check output above")
        sys.exit(1)


if __name__ == "__main__":
    main()
