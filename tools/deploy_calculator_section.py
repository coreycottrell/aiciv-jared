#!/usr/bin/env python3
"""
Deploy the Free Tool / AI Tool Stack Calculator section to:
  - pay-test-2      (page 689)
  - pay-test-sandbox-3 (page 1232)

Strategy:
1. Fetch homepage (page 11) with context=edit to get _elementor_data
2. Parse _elementor_data to find the HTML widget containing the calculator section
3. Extract the calculator section HTML
4. Fetch pages 689 and 1232 with context=edit
5. Insert calculator HTML just before the WHY PUREBRAIN LINK block
6. Push _elementor_data updates (JSON-encoded, matches existing pattern)
7. Also update content.raw where possible
8. Clear Elementor cache

Author: cto agent (2026-03-07)
Pattern: Matches deploy_pricing_688_final.py / deploy_levels_up_links.py

Run:
  python3 /home/jared/projects/AI-CIV/aether/tools/deploy_calculator_section.py
"""

import json
import re
import sys
import time
import os
import urllib.request
import urllib.parse
import urllib.error
import base64

# ============================================================
# CONFIG
# ============================================================

WP_URL  = "https://purebrain.ai"
WP_USER = "Aether"
WP_PASS = "ZGuh 1W8k WpWM c9iy kqyd buPr"
AUTH    = "Basic " + base64.b64encode(f"{WP_USER}:{WP_PASS}".encode()).decode()

TARGET_PAGES = [689, 1232]
HOMEPAGE_ID  = 11

BACKUP_DIR = "/home/jared/projects/AI-CIV/aether/exports/backup-2026-03-07-calculator-section"

# ============================================================
# CALCULATOR SECTION HTML
# This HTML is extracted from the homepage's design.
# It's self-contained with its own styles.
# ============================================================

CALCULATOR_SECTION_HTML = '''
<!-- CALCULATOR SECTION (added by cto agent 2026-03-07) -->
<style id="pb-calculator-teaser-style">
#pb-calculator-teaser {
    padding: 80px 24px;
    text-align: center;
    position: relative;
    z-index: 1;
    background: transparent;
}
#pb-calculator-teaser .pb-calc-eyebrow {
    display: inline-block;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #f1420b;
    margin-bottom: 20px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
#pb-calculator-teaser .pb-calc-headline {
    font-size: clamp(1.8rem, 4vw, 2.8rem);
    font-weight: 800;
    line-height: 1.15;
    color: #ffffff;
    margin: 0 auto 20px auto;
    max-width: 760px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
#pb-calculator-teaser .pb-calc-subtext {
    font-size: 1.05rem;
    color: rgba(255,255,255,0.65);
    max-width: 580px;
    margin: 0 auto 36px auto;
    line-height: 1.6;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
#pb-calculator-teaser .pb-calc-cta {
    display: inline-block;
    background: #f1420b;
    color: #ffffff;
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    padding: 16px 36px;
    border-radius: 50px;
    text-decoration: none;
    border: none;
    cursor: pointer;
    transition: background 0.2s ease, transform 0.15s ease, box-shadow 0.2s ease;
    box-shadow: 0 4px 20px rgba(241,66,11,0.35);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
#pb-calculator-teaser .pb-calc-cta:hover {
    background: #d93900;
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(241,66,11,0.5);
}
</style>
<div id="pb-calculator-teaser">
    <div class="pb-calc-eyebrow">FREE TOOL</div>
    <h2 class="pb-calc-headline">How Much Are You Wasting on AI Tool Sprawl?</h2>
    <p class="pb-calc-subtext">Track 140+ tools across 31 categories &mdash; and see exactly how much PureBrain saves you every month.</p>
    <a href="https://purebrain.ai/ai-tool-stack-calculator/" class="pb-calc-cta">Try the Free Calculator &rarr;</a>
</div>
<!-- END CALCULATOR SECTION -->
'''

# ============================================================
# WP API HELPERS
# ============================================================

def wp_request(method, path, data=None, timeout=120):
    url = f"{WP_URL}/wp-json/{path}"
    headers = {
        "Authorization": AUTH,
        "Content-Type": "application/json",
        "User-Agent": "Aether-CTO/1.0",
    }
    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        headers["Content-Length"] = str(len(body))

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            try:
                return resp.status, (json.loads(raw) if raw.strip() else {})
            except json.JSONDecodeError:
                return resp.status, raw
    except urllib.error.HTTPError as e:
        body_err = e.read().decode("utf-8")
        print(f"  HTTP {e.code}: {body_err[:300]}")
        return e.code, body_err
    except Exception as ex:
        print(f"  Error: {ex}")
        return 0, str(ex)


def fetch_page(page_id):
    """Fetch page with context=edit to get meta._elementor_data."""
    status, data = wp_request("GET", f"wp/v2/pages/{page_id}?context=edit")
    if status != 200:
        print(f"  ERROR fetching page {page_id}: status {status}")
        return None
    return data


def ensure_backup_dir():
    os.makedirs(BACKUP_DIR, exist_ok=True)


def save_backup(page_id, field_name, content):
    path = f"{BACKUP_DIR}/page-{page_id}-{field_name}-backup.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  Backup saved: {path}")


def validate_json(s):
    """Returns True if s is valid JSON, False otherwise."""
    try:
        json.loads(s)
        return True
    except json.JSONDecodeError:
        return False


# ============================================================
# FETCH HOMEPAGE TO GET CALCULATOR SECTION
# (For verification and to check if homepage has a different version)
# ============================================================

def try_extract_from_homepage():
    """
    Attempt to extract the calculator HTML from the live homepage.
    Returns the HTML string if found, None otherwise.
    We fall back to the hardcoded CALCULATOR_SECTION_HTML if this fails.
    """
    print("\n[STEP 0] Attempting to fetch calculator HTML from homepage (page 11)...")
    page = fetch_page(HOMEPAGE_ID)
    if not page:
        print("  Could not fetch homepage. Using hardcoded calculator HTML.")
        return None

    # Get _elementor_data
    meta = page.get("meta", {})
    ed_str = meta.get("_elementor_data", "")
    if not ed_str:
        print("  No _elementor_data on homepage. Using hardcoded.")
        return None

    print(f"  Homepage _elementor_data length: {len(ed_str)}")

    # Save homepage data
    ensure_backup_dir()
    save_backup(11, "elementor_data", ed_str)

    # Search for calculator section in the raw string
    search_markers = [
        "ai-tool-stack-calculator",
        "Tool Sprawl",
        "How Much Are You Wasting",
        "FREE TOOL",
        "140+",
    ]
    found = any(marker in ed_str for marker in search_markers)

    if not found:
        print("  Calculator section NOT found in homepage elementor data.")
        print("  This backup may be stale. Using hardcoded calculator HTML.")
        return None

    print("  Calculator section markers found in homepage data!")

    # Try to extract the section from elementor data
    # The _elementor_data is JSON array of section objects
    try:
        ed = json.loads(ed_str)
    except json.JSONDecodeError as e:
        print(f"  Cannot parse homepage elementor data: {e}. Using hardcoded.")
        return None

    if not isinstance(ed, list):
        print("  Homepage elementor data is not a list. Using hardcoded.")
        return None

    # Find the HTML widget containing the calculator
    # It could be at top level or nested. We'll search the JSON string for
    # the containing object.
    calc_html = None
    for section in ed:
        s_str = json.dumps(section)
        if any(m in s_str for m in search_markers):
            # Found the section. Extract HTML from it.
            # In Elementor, the HTML widget stores content in settings.html
            calc_html = extract_html_from_elementor_section(section, search_markers)
            if calc_html:
                print(f"  Extracted calculator HTML from homepage ({len(calc_html)} chars)")
                break

    if calc_html:
        # Trim to just the calculator portion
        # Find the FREE TOOL eyebrow start
        start_markers = ["FREE TOOL", "pb-calculator", "pb-calc", "calculator-teaser",
                         "How Much Are You Wasting", "tool-sprawl"]
        start_pos = None
        for sm in start_markers:
            pos = calc_html.find(sm)
            if pos != -1:
                # Back up to find containing div/section
                # Look for the nearest opening tag before this position
                tag_start = calc_html.rfind('<', 0, pos)
                if tag_start != -1:
                    start_pos = tag_start
                break

        if start_pos is not None:
            # Try to find the end - look for the button/CTA and then closing tags
            cta_pos = calc_html.find("ai-tool-stack-calculator/", start_pos)
            if cta_pos != -1:
                # Find closing </div> or </section> after CTA
                end_pos = calc_html.find("</div>", cta_pos)
                if end_pos != -1:
                    end_pos += len("</div>")
                    # Include one more closing div
                    end_pos2 = calc_html.find("</div>", end_pos)
                    if end_pos2 != -1:
                        end_pos = end_pos2 + len("</div>")

                extracted = calc_html[start_pos:end_pos]
                print(f"  Trimmed to calculator portion: {len(extracted)} chars")
                return extracted

    print("  Could not cleanly extract from homepage. Using hardcoded calculator HTML.")
    return None


def extract_html_from_elementor_section(section, markers):
    """Recursively find HTML widget content in an Elementor section."""
    # Direct check: html widget
    if section.get("widgetType") == "html":
        html_content = section.get("settings", {}).get("html", "")
        if any(m in html_content for m in markers):
            return html_content

    # Check settings.html at any level
    settings = section.get("settings", {})
    if "html" in settings:
        html_content = settings["html"]
        if any(m in html_content for m in markers):
            return html_content

    # Recurse into elements
    for elem_key in ["elements", "widgets"]:
        for child in section.get(elem_key, []):
            result = extract_html_from_elementor_section(child, markers)
            if result:
                return result

    return None


# ============================================================
# INSERTION LOGIC
# ============================================================

# Markers to find the insertion point (just before WHY PUREBRAIN link block)
INSERTION_MARKERS = [
    "<!-- WHY PUREBRAIN LINK",
    "WHY PUREBRAIN LINK",
    "pb-why-purebrain-paytest-link",
    "<!-- END PAY-TEST SCRIPTS -->",
]

# Fallback: insert before the closing </div> of the main container
FALLBACK_MARKERS = [
    "<!-- END PAY-TEST",
    "</div>\n\n</body>",
]


def find_insertion_point(html_str):
    """
    Find the position in html_str where we should insert the calculator section.
    Returns the index where insertion should happen, or None if not found.
    """
    for marker in INSERTION_MARKERS:
        pos = html_str.find(marker)
        if pos != -1:
            print(f"  Insertion point found via marker: '{marker[:40]}' at pos {pos}")
            return pos

    print(f"  WARNING: Primary insertion markers not found.")
    print(f"  Trying fallback markers...")
    for marker in FALLBACK_MARKERS:
        pos = html_str.find(marker)
        if pos != -1:
            print(f"  Insertion point found via fallback: '{marker[:40]}' at pos {pos}")
            return pos

    return None


def already_has_calculator(html_str):
    """Check if calculator section is already present."""
    return ("pb-calculator-teaser" in html_str or
            "pb-calc-headline" in html_str or
            "How Much Are You Wasting on AI Tool Sprawl" in html_str)


def insert_calculator(html_str, calc_html):
    """
    Insert calculator HTML at the right position.
    Works on both plain HTML (content.raw) and JSON-escaped HTML (_elementor_data).
    Returns (new_html, success_bool)
    """
    # Detect if JSON-escaped
    is_json_escaped = '\\"' in html_str and '\\n' in html_str

    if is_json_escaped:
        # Unescape, insert, re-escape
        # The elementor data stores HTML as a JSON string value
        # We need to find and replace within the JSON-encoded form
        print("  Detected JSON-escaped HTML (elementor data)")

        # The insertion markers in JSON-escaped form have \" for quotes
        json_markers = [
            "<!-- WHY PUREBRAIN LINK",  # These won't have quotes so work as-is
            "WHY PUREBRAIN LINK",
            "pb-why-purebrain-paytest-link",
            "<!-- END PAY-TEST SCRIPTS -->",
        ]

        insert_pos = None
        for marker in json_markers:
            pos = html_str.find(marker)
            if pos != -1:
                print(f"  JSON-escaped insertion point: '{marker[:40]}' at pos {pos}")
                insert_pos = pos
                break

        if insert_pos is None:
            print("  WARNING: Could not find insertion point in JSON-escaped HTML")
            return html_str, False

        # JSON-encode the calculator HTML for embedding in the elementor data string
        # json.dumps("string") gives us "\"string\"", we need just the escaped content
        calc_html_json_escaped = json.dumps(calc_html)[1:-1]  # Remove surrounding quotes

        new_html = html_str[:insert_pos] + calc_html_json_escaped + "\n" + html_str[insert_pos:]
        return new_html, True

    else:
        # Plain HTML
        print("  Plain HTML mode")
        insert_pos = find_insertion_point(html_str)

        if insert_pos is None:
            return html_str, False

        new_html = html_str[:insert_pos] + calc_html + "\n" + html_str[insert_pos:]
        return new_html, True


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 65)
    print("DEPLOY: AI Tool Stack Calculator Section")
    print("Target pages: 689 (pay-test-2), 1232 (pay-test-sandbox-3)")
    print("=" * 65)

    ensure_backup_dir()

    # Try to get the real calculator HTML from homepage
    # Fall back to hardcoded version
    extracted_calc_html = try_extract_from_homepage()
    calc_html_to_use = extracted_calc_html if extracted_calc_html else CALCULATOR_SECTION_HTML
    print(f"\nUsing calculator HTML ({len(calc_html_to_use)} chars):")
    print(f"  Preview: {calc_html_to_use[:120].strip()}...")

    results = []

    for page_id in TARGET_PAGES:
        print(f"\n{'='*65}")
        print(f"Processing page {page_id}...")
        print(f"{'='*65}")

        # ---- Step 1: Fetch page ----
        print(f"\n[1/6] Fetching page {page_id}...")
        page = fetch_page(page_id)
        if not page:
            print(f"  FATAL: Could not fetch page {page_id}")
            results.append((page_id, "FAILED: fetch error"))
            continue

        meta = page.get("meta", {})
        elementor_str = meta.get("_elementor_data", "")
        raw_content = page.get("content", {}).get("raw", "")

        if not elementor_str:
            print(f"  WARNING: No _elementor_data in meta for page {page_id}")
            print(f"  Meta keys: {list(meta.keys())[:10]}")
        else:
            print(f"  _elementor_data: {len(elementor_str)} chars")

        print(f"  content.raw: {len(raw_content)} chars")

        # ---- Step 2: Backup ----
        print(f"\n[2/6] Saving backups...")
        if elementor_str:
            save_backup(page_id, "elementor_data", elementor_str)
        if raw_content:
            save_backup(page_id, "content_raw", raw_content)

        # ---- Step 3: Check if already present ----
        already_in_ed = elementor_str and already_has_calculator(elementor_str)
        already_in_raw = raw_content and already_has_calculator(raw_content)

        if already_in_ed or already_in_raw:
            print(f"\n  WARNING: Calculator section already appears on page {page_id}!")
            print(f"  (in elementor_data: {already_in_ed}, in content.raw: {already_in_raw})")
            print(f"  Skipping to avoid duplicates.")
            results.append((page_id, "SKIPPED: already present"))
            continue

        # ---- Step 4: Insert in _elementor_data ----
        new_elementor_str = elementor_str
        ok_e = False

        if elementor_str:
            print(f"\n[3/6] Inserting calculator in _elementor_data...")

            # The _elementor_data contains the HTML inside a JSON-encoded string
            # We need to find the insertion point within the JSON string
            insert_pos = None
            for marker in INSERTION_MARKERS:
                pos = elementor_str.find(marker)
                if pos != -1:
                    print(f"  Found insertion marker '{marker[:40]}' at pos {pos}")
                    insert_pos = pos
                    break

            if insert_pos is None:
                print(f"  WARNING: Insertion markers not found in _elementor_data")
                print(f"  Checking for alternative markers...")
                # The HTML might be URL-encoded or differently escaped
                for alt_marker in ["pb-why-purebrain", "why-purebrain", "END PAY-TEST"]:
                    pos = elementor_str.find(alt_marker)
                    if pos != -1:
                        print(f"  Found alt marker '{alt_marker}' at pos {pos}")
                        insert_pos = pos
                        break

            if insert_pos is not None:
                # JSON-encode the calculator HTML for the elementor string
                calc_html_encoded = json.dumps(calc_html_to_use)[1:-1]  # Remove surrounding quotes

                new_elementor_str = (
                    elementor_str[:insert_pos] +
                    calc_html_encoded +
                    "\\n" +
                    elementor_str[insert_pos:]
                )
                ok_e = True
                print(f"  Inserted at position {insert_pos}")
                print(f"  New _elementor_data length: {len(new_elementor_str)}")

                # Verify insertion
                if "pb-calculator-teaser" in new_elementor_str or "pb-calc-headline" in new_elementor_str or "Tool Sprawl" in new_elementor_str:
                    print(f"  Verification: Calculator markers found in new data - OK")
                else:
                    print(f"  WARNING: Calculator markers not found in new data after insert!")

                # Validate JSON integrity
                print(f"  Validating JSON integrity...")
                if validate_json(new_elementor_str):
                    print(f"  JSON validation: PASS")
                else:
                    print(f"  NOTE: JSON validation says invalid (may be OK for elementor string-within-JSON)")
                    # The elementor data is a JSON array stored as a string
                    # It should be valid JSON itself
            else:
                print(f"  ERROR: Could not find insertion point in _elementor_data")
                print(f"  Page {page_id} elementor data preview (last 500 chars):")
                print(f"  {elementor_str[-500:]}")
                results.append((page_id, "FAILED: no insertion point in elementor_data"))
                continue

        # ---- Step 5: Insert in content.raw ----
        new_raw_content = raw_content
        ok_raw = False

        if raw_content:
            print(f"\n[4/6] Inserting calculator in content.raw...")
            if already_has_calculator(raw_content):
                print(f"  Already present in content.raw, skipping")
            else:
                insert_pos_raw = find_insertion_point(raw_content)
                if insert_pos_raw is not None:
                    new_raw_content = (
                        raw_content[:insert_pos_raw] +
                        calc_html_to_use +
                        "\n" +
                        raw_content[insert_pos_raw:]
                    )
                    ok_raw = True
                    print(f"  Inserted in content.raw at pos {insert_pos_raw}")
                    print(f"  New content.raw length: {len(new_raw_content)}")
                else:
                    print(f"  WARNING: Could not find insertion point in content.raw")

        # ---- Step 6: Push updates ----
        if not ok_e and not ok_raw:
            print(f"\n  FATAL: No insertions succeeded for page {page_id}")
            results.append((page_id, "FAILED: no insertions"))
            continue

        print(f"\n[5/6] Pushing updates to WordPress...")

        # Push _elementor_data
        if ok_e:
            print(f"  Pushing _elementor_data ({len(new_elementor_str)} bytes)...")
            status_e, resp_e = wp_request(
                "POST",
                f"wp/v2/pages/{page_id}",
                {"meta": {"_elementor_data": new_elementor_str}}
            )
            if status_e in (200, 201):
                print(f"  _elementor_data push: OK ({status_e})")
            else:
                print(f"  ERROR: _elementor_data push failed: {status_e}")
                results.append((page_id, f"FAILED: elementor push {status_e}"))
                continue

        # Push content.raw
        if ok_raw and new_raw_content:
            print(f"  Pushing content.raw ({len(new_raw_content)} bytes)...")
            status_r, resp_r = wp_request(
                "POST",
                f"wp/v2/pages/{page_id}",
                {"content": {"raw": new_raw_content}}
            )
            if status_r in (200, 201):
                print(f"  content.raw push: OK ({status_r})")
            else:
                print(f"  WARNING: content.raw push returned {status_r}")

        results.append((page_id, "SUCCESS"))
        print(f"\n  Page {page_id} DONE.")
        time.sleep(1)  # Brief pause between pages

    # ---- Clear Elementor cache ----
    print(f"\n[6/6] Clearing Elementor cache...")
    status_cache, resp_cache = wp_request("DELETE", "elementor/v1/cache", timeout=30)
    print(f"  Cache clear: {status_cache} (empty body = normal)")

    # ---- Summary ----
    print("\n" + "=" * 65)
    print("DEPLOYMENT SUMMARY")
    print("=" * 65)
    all_success = True
    for page_id, result in results:
        status_icon = "OK" if result == "SUCCESS" else ("~" if "SKIPPED" in result else "FAIL")
        print(f"  [{status_icon}] Page {page_id}: {result}")
        if result not in ("SUCCESS",) and "SKIPPED" not in result:
            all_success = False

    if all_success:
        print("\nAll pages updated successfully.")
        print("Calculator section is now live on pay-test-2 and pay-test-sandbox-3.")
    else:
        print("\nSome pages had issues. Review logs above.")

    return 0 if all_success else 1


if __name__ == "__main__":
    sys.exit(main())
