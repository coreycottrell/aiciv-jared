#!/usr/bin/env python3
"""
Fix DOMContentLoaded timing issue on purebrain.ai/pay-test/ (Page ID 439)

Root cause: The main chat script (55,925 chars) runs as an inline <script> tag
WITHOUT a DOMContentLoaded wrapper. The line:
    const chatMessages = document.getElementById('chatMessages');
captures null because the DOM isn't ready when the script evaluates
(due to nested HTML documents in the Elementor widget).

Fix: Wrap the entire main chat script body in a DOMContentLoaded listener.

Credentials: Aether / FlFr2VOtlHiHaJWjzW96OHUJ
Page ID: 439 (/pay-test/)
"""

import json
import re
import requests
import sys
import time

WP_BASE = "https://purebrain.ai"
WP_USER = "Aether"
WP_PASS = "FlFr2VOtlHiHaJWjzW96OHUJ"
PAGE_ID = 439

# Identifier string unique to the main chat script
MAIN_SCRIPT_MARKER = "// IMMERSIVE FLOWING BACKGROUND SYSTEM"


def fetch_page_data():
    """Fetch page 439 with full Elementor data."""
    print(f"Fetching page {PAGE_ID} from {WP_BASE}...")
    url = f"{WP_BASE}/wp-json/wp/v2/pages/{PAGE_ID}?context=edit"
    resp = requests.get(url, auth=(WP_USER, WP_PASS), timeout=30)
    resp.raise_for_status()
    data = resp.json()
    print(f"Page: {data.get('title', {}).get('rendered', '?')} (slug: {data.get('slug', '?')})")

    meta = data.get("meta", {})
    elementor_data_raw = meta.get("_elementor_data", "")
    if not elementor_data_raw:
        raise ValueError("No _elementor_data found in page meta")

    elementor_data = json.loads(elementor_data_raw)
    print(f"Elementor data: {len(elementor_data_raw):,} chars, {len(elementor_data)} top-level containers")
    return elementor_data, elementor_data_raw, data


def find_html_widget(elementor_data):
    """Navigate to the single HTML widget containing the page content."""
    container = elementor_data[0]
    html_widget = container["elements"][0]
    if html_widget.get("widgetType") != "html":
        raise ValueError(f"Expected html widget at [0][0], got: {html_widget.get('widgetType')}")
    return html_widget


def apply_domcontentloaded_fix(html_content):
    """
    Find the main chat script and wrap its content in DOMContentLoaded.

    Returns (updated_html, was_changed, reason)
    """
    # Build regex to find the exact script tag containing the marker
    script_pattern = re.compile(r'(<script([^>]*)>)(.*?)(</script>)', re.DOTALL | re.IGNORECASE)
    matches = list(script_pattern.finditer(html_content))

    print(f"Total <script> tags found: {len(matches)}")

    main_script_match = None
    for i, m in enumerate(matches):
        body = m.group(3)
        if MAIN_SCRIPT_MARKER in body:
            print(f"  Found main chat script at position {i+1}: {len(body):,} chars")
            main_script_match = m
            break

    if main_script_match is None:
        return html_content, False, "Main chat script not found (marker not present)"

    open_tag = main_script_match.group(1)
    attrs = main_script_match.group(2)
    body = main_script_match.group(3)
    close_tag = main_script_match.group(4)

    # Safety check: don't double-wrap
    if "DOMContentLoaded" in body:
        return html_content, False, "Script already has DOMContentLoaded wrapper - no change needed"

    print(f"  Script attrs: '{attrs.strip()}'")
    print(f"  Body length: {len(body):,} chars")
    print(f"  Body starts with: {repr(body[:80])}")
    print(f"  Body ends with: {repr(body[-80:])}")

    # Wrap the body in DOMContentLoaded
    # Preserve original indentation by using a clean wrapper
    wrapped_body = f"\ndocument.addEventListener('DOMContentLoaded', function() {{\n{body}\n}});\n"

    # Reconstruct the full script tag
    new_script_tag = open_tag + wrapped_body + close_tag

    # Replace in html_content - use the exact matched string as the search key
    original_script_tag = main_script_match.group(0)
    if original_script_tag not in html_content:
        return html_content, False, "ERROR: Could not locate original script tag in HTML for replacement"

    updated_html = html_content.replace(original_script_tag, new_script_tag, 1)

    # Verify the replacement happened
    if updated_html == html_content:
        return html_content, False, "ERROR: html_content unchanged after replacement"

    # Verify the fix is in place
    if "DOMContentLoaded" not in updated_html:
        return html_content, False, "ERROR: DOMContentLoaded not found in updated HTML"

    new_count = updated_html.count("DOMContentLoaded")
    old_count = html_content.count("DOMContentLoaded")
    print(f"  DOMContentLoaded count: before={old_count}, after={new_count}")

    return updated_html, True, f"SUCCESS: Wrapped main chat script ({len(body):,} chars) in DOMContentLoaded"


def update_page(elementor_data, page_content_raw):
    """Push updated Elementor JSON back to WordPress via REST API."""
    print(f"\nUpdating page {PAGE_ID} via REST API...")
    url = f"{WP_BASE}/wp-json/wp/v2/pages/{PAGE_ID}"
    new_elementor_json = json.dumps(elementor_data)
    print(f"  New Elementor JSON size: {len(new_elementor_json):,} chars")
    payload = {
        "meta": {
            "_elementor_data": new_elementor_json
        }
    }
    resp = requests.post(url, auth=(WP_USER, WP_PASS), json=payload, timeout=120)
    resp.raise_for_status()
    result = resp.json()
    print(f"  HTTP status: {resp.status_code}")
    print(f"  Page modified: {result.get('modified', 'unknown')}")
    return result


def clear_all_caches():
    """
    Clear all cache layers for the page.

    The WordPress + Elementor + GoDaddy + Cloudflare stack has multiple cache layers:
    1. Elementor PHP cache (object cache / APCu) - cleared by DELETE /elementor/v1/cache
    2. GoDaddy gateway cache - auto-clears when Elementor cache is cleared
    3. Cloudflare CDN - re-fetches from origin after Elementor cache clear + page touch

    NOTE: Playwright-based approaches may be more reliable if REST API is insufficient.
    """
    print("\nClearing cache layers...")

    # Layer 1: Elementor PHP cache
    for attempt in range(3):
        resp = requests.delete(
            f"{WP_BASE}/wp-json/elementor/v1/cache",
            auth=(WP_USER, WP_PASS),
            timeout=15
        )
        print(f"  Elementor cache DELETE (attempt {attempt+1}): HTTP {resp.status_code}")
        if resp.status_code == 200:
            break
        time.sleep(1)

    # Layer 2+3: Touch page to update modified timestamp (helps Cloudflare re-fetch)
    time.sleep(2)
    touch_resp = requests.post(
        f"{WP_BASE}/wp-json/wp/v2/pages/{PAGE_ID}",
        auth=(WP_USER, WP_PASS),
        json={"status": "publish"},
        timeout=30
    )
    print(f"  Page touch: HTTP {touch_resp.status_code}, modified={touch_resp.json().get('modified', '?')}")


def verify_live_page():
    """Verify DOMContentLoaded wrapper is present in the live page source."""
    print("\nVerifying live page (https://purebrain.ai/pay-test/)...")
    resp = requests.get("https://purebrain.ai/pay-test/", timeout=30)
    content = resp.text
    cf_status = resp.headers.get("CF-Cache-Status", "?")
    gd_status = resp.headers.get("x-gateway-cache-status", "?")
    print(f"  HTTP status: {resp.status_code}")
    print(f"  Cache: CF={cf_status}, GD={gd_status}")
    print(f"  Page size: {len(content):,} chars")

    # Find the IMMERSIVE script and check for DOMContentLoaded wrapper
    script_pattern = re.compile(r'<script([^>]*)>(.*?)</script>', re.DOTALL | re.IGNORECASE)
    for m in script_pattern.finditer(content):
        body = m.group(2)
        if MAIN_SCRIPT_MARKER in body:
            has_dcl = "DOMContentLoaded" in body
            print(f"  Main chat script: {len(body):,} chars")
            print(f"  Has DOMContentLoaded: {has_dcl}")
            if has_dcl:
                dcl_pos = body.find("DOMContentLoaded")
                print(f"  DCL position in body: {dcl_pos} (expected ~28)")
                print(f"  DCL context: {repr(body[max(0,dcl_pos-20):dcl_pos+60])}")
                return True
            else:
                print("  WARNING: No DOMContentLoaded wrapper in main chat script!")
                return False

    print("  WARNING: IMMERSIVE marker not found in live page - may be cached or error")
    return False


def check_other_scripts_for_issues(html_content):
    """
    Check other scripts for the same bare-DOM-capture pattern
    (const/let/var at top level capturing getElementById).
    """
    print("\n--- Checking other scripts for bare DOM captures ---")
    script_pattern = re.compile(r'<script([^>]*)>(.*?)</script>', re.DOTALL | re.IGNORECASE)
    matches = list(script_pattern.finditer(html_content))

    issues = []
    for i, m in enumerate(matches):
        attrs = m.group(1).strip()
        body = m.group(2).strip()

        # Skip external scripts (src attribute)
        if 'src=' in attrs.lower():
            continue

        # Skip the main chat script (already being fixed)
        if MAIN_SCRIPT_MARKER in body:
            continue

        # Skip already-wrapped scripts
        if "DOMContentLoaded" in body:
            continue

        # Look for top-level bare DOM element captures
        # Pattern: var/const/let at the start of a line (not inside a function)
        # This is a heuristic - we check if getElementById is called outside any function wrapper
        bare_captures = re.findall(
            r'(?:^|\n)[ \t]*(?:const|let|var)\s+(\w+)\s*=\s*document\.getElementById\([^\)]+\)',
            body
        )

        if bare_captures:
            print(f"  Script {i+1} (len={len(body):,}): bare DOM captures = {bare_captures}")
            issues.append({
                "index": i+1,
                "length": len(body),
                "captures": bare_captures,
                "first_100": body[:100]
            })

    if not issues:
        print("  No other scripts have bare top-level DOM element captures.")
    else:
        print(f"\n  FOUND {len(issues)} other script(s) with potential timing issues:")
        for issue in issues:
            print(f"    Script {issue['index']}: variables {issue['captures']}")
            print(f"    Starts with: {repr(issue['first_100'])}")

    return issues


def main():
    print("=" * 65)
    print("pay-test DOMContentLoaded Fix")
    print(f"Page: https://purebrain.ai/pay-test/ (ID {PAGE_ID})")
    print("=" * 65)

    # Step 1: Fetch page
    try:
        elementor_data, original_raw, page_data = fetch_page_data()
    except Exception as e:
        print(f"FAILED to fetch page: {e}")
        sys.exit(1)

    # Step 2: Get HTML widget
    try:
        html_widget = find_html_widget(elementor_data)
    except ValueError as e:
        print(f"FAILED to find HTML widget: {e}")
        sys.exit(1)

    original_html = html_widget["settings"]["html"]
    print(f"HTML widget content: {len(original_html):,} chars")

    # Step 3: Apply the fix
    print("\n--- Applying DOMContentLoaded fix ---")
    updated_html, was_changed, reason = apply_domcontentloaded_fix(original_html)
    print(f"Result: {reason}")

    if not was_changed:
        if "already has" in reason:
            print("Fix already applied. No update needed.")
            # Still check other scripts
            check_other_scripts_for_issues(original_html)
            sys.exit(0)
        else:
            print("ERROR: Fix could not be applied.")
            sys.exit(1)

    # Step 4: Check other scripts for the same issue
    check_other_scripts_for_issues(updated_html)

    # Step 5: Update Elementor data structure
    html_widget["settings"]["html"] = updated_html
    elementor_data[0]["elements"][0] = html_widget

    # Step 6: Verify the change looks correct before pushing
    new_count = updated_html.count("DOMContentLoaded")
    old_count = original_html.count("DOMContentLoaded")
    print(f"\nPre-push sanity check:")
    print(f"  HTML size: {len(original_html):,} -> {len(updated_html):,} chars")
    print(f"  DOMContentLoaded count: {old_count} -> {new_count}")
    print(f"  IMMERSIVE marker still present: {'IMMERSIVE FLOWING BACKGROUND SYSTEM' in updated_html}")

    # Step 7: Push update
    try:
        update_page(elementor_data, original_raw)
    except Exception as e:
        print(f"FAILED to update page: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Step 7.5: Clear all cache layers (CRITICAL)
    # Without this, Elementor PHP cache serves old version even after DB update
    try:
        clear_all_caches()
    except Exception as e:
        print(f"WARNING: Cache clear failed: {e}")
        print("  The fix may still be in DB but not visible until caches expire.")

    # Step 8: Verify live page
    print("\nWaiting 10 seconds for caches to propagate...")
    time.sleep(10)
    live_ok = verify_live_page()

    print("\n" + "=" * 65)
    if live_ok:
        print("SUCCESS: DOMContentLoaded fix is live on purebrain.ai/pay-test/")
        print("  - Main chat script now runs after DOM is fully loaded")
        print("  - chatMessages, canvas, etc. will correctly capture DOM elements")
        print("  - showTyping() TypeError should be resolved")
    else:
        print("FIX APPLIED but live verification inconclusive (may be cached).")
        print("  - The REST API update succeeded")
        print("  - If page still shows stale content, clear Elementor/server cache")
        print("  - You can verify by viewing page source and searching for:")
        print("    \"DOMContentLoaded\" followed by \"IMMERSIVE FLOWING BACKGROUND SYSTEM\"")
    print("=" * 65)

    return live_ok


if __name__ == "__main__":
    main()
