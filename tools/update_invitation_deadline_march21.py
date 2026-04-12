#!/usr/bin/env python3
"""
Update /invitation/ page (WP page 987) deadline from March 18 to March 21, 2026.

Changes:
  1. Countdown target: 2026-03-19T04:59:59Z → 2026-03-22T04:59:59Z
     (Friday March 21 EOD Eastern = Saturday March 22 04:59:59 UTC)
  2. Comment: 'March 18, 2026 EOD Eastern...' → updated text
  3. Hero text: 'Closes Wednesday' → 'Closes Friday'
  4. Pricing section: 'March 18th, EOD Eastern' → 'March 21st, EOD Eastern'
  5. Fallback CLAIMED = 12 → 15 (current real count)
  6. Hardcoded span: pb-claimed-count '12' → '15'

CF WAF blocks REST API, so we use Playwright via WP admin.
"""
import re
import sys
import time
from pathlib import Path

AETHER_ROOT = Path("/home/jared/projects/AI-CIV/aether")
PAGE_ID = 987
PAGE_TITLE = "Access Invitation"
LOGIN_URL = "https://purebrain.ai/wp-login.php?wpaas-standard-login=1"

# Load credentials
env_text = (AETHER_ROOT / ".env").read_text()

def _env(key):
    m = re.search(rf"^{key}='([^']+)'", env_text, re.MULTILINE)
    if m:
        return m.group(1).strip()
    m = re.search(rf'^{key}=([^\n]+)', env_text, re.MULTILINE)
    return m.group(1).strip() if m else ""

WP_USER = _env("PUREBRAIN_WP_USER")
WP_PASS = _env("PUREBRAIN_WP_PASSWORD")

print("=" * 65)
print("Invitation Page Deadline Update — March 18 → March 21, 2026")
print("=" * 65)
print(f"Page ID: {PAGE_ID}")
print(f"WP User: {WP_USER}")
print()

# ---- Step 1: Fetch live page HTML ----
print("Step 1: Fetching live /invitation/ page HTML...")
import urllib.request
req = urllib.request.Request(
    "https://purebrain.ai/invitation/",
    headers={"User-Agent": "Mozilla/5.0 (Aether deploy script)"}
)
with urllib.request.urlopen(req, timeout=30) as resp:
    live_html = resp.read().decode("utf-8")
print(f"  Fetched: {len(live_html):,} chars")

# Verify all target strings are present
REPLACEMENTS = [
    (
        "2026-03-19T04:59:59Z",
        "2026-03-22T04:59:59Z",
        "countdown target date"
    ),
    (
        "March 18, 2026 EOD Eastern (= March 19 04:59:59 UTC)",
        "March 21, 2026 EOD Eastern (= March 22 04:59:59 UTC)",
        "comment text"
    ),
    (
        "Closes Wednesday",
        "Closes Friday",
        "hero closing day text"
    ),
    (
        "March 18th, EOD Eastern",
        "March 21st, EOD Eastern",
        "pricing section deadline"
    ),
    (
        "var CLAIMED = 12;",
        "var CLAIMED = 15;",
        "fallback spots claimed count"
    ),
    (
        'pb-claimed-count">12</span>',
        'pb-claimed-count">15</span>',
        "visible spots counter HTML"
    ),
]

print()
print("Step 2: Verifying target strings...")
all_found = True
for old, new, label in REPLACEMENTS:
    count = live_html.count(old)
    status = "OK" if count == 1 else ("MISSING" if count == 0 else f"MULTI ({count}x)")
    print(f"  [{status}] {label}: {repr(old[:60])}")
    if count != 1:
        all_found = False

if not all_found:
    print()
    print("ERROR: One or more target strings not found or duplicated. Aborting.")
    sys.exit(1)

print("  All 6 strings found exactly once. Proceeding.")

# ---- Step 3: Apply replacements ----
print()
print("Step 3: Applying replacements...")
updated_html = live_html
for old, new, label in REPLACEMENTS:
    updated_html = updated_html.replace(old, new, 1)
    print(f"  Replaced [{label}]")

# Verify replacements applied
print()
print("Step 4: Verifying replacements...")
for old, new, label in REPLACEMENTS:
    old_count = updated_html.count(old)
    new_count = updated_html.count(new)
    if old_count == 0 and new_count >= 1:
        print(f"  OK: {label}")
    else:
        print(f"  PROBLEM: {label} — old_count={old_count}, new_count={new_count}")

# Save updated HTML locally
out_path = AETHER_ROOT / "exports/invitation-page-march21-deadline.html"
out_path.write_text(updated_html)
print()
print(f"  Saved updated HTML to: {out_path}")
print(f"  Size: {len(updated_html):,} chars")

# Extract just the post_content (everything inside <body> tags)
# For page 987: content is stored as raw HTML in post_content
body_match = re.search(r'<body[^>]*>(.*?)</body>', updated_html, re.DOTALL)
if not body_match:
    print("ERROR: Could not extract body content")
    sys.exit(1)

# Actually, WP page 987 stores the FULL page HTML (including head/CSS) in post_content
# wrapped in <!-- wp:html --> block
# We need to send the full content as it appears in the post

# Strip the outer WP theme wrapper - but since page 987 IS the full self-contained HTML,
# we wrap it in wp:html block
# Check if the live HTML is self-contained (starts with <!DOCTYPE or has <html>)
# Based on memory: page 987 content is post_content only, NOT elementor_data
# The raw post_content should be the <!-- wp:html --> wrapped version

# For the Playwright approach, we just need to paste the content into the text editor
# The live HTML we fetched IS what gets rendered, so we can use it directly
# But we need to wrap it properly for WP

# The approach: use WP admin Classic Editor to paste the full HTML
# Page 987 uses Classic Editor (no _elementor_data)
print()
print("=" * 65)
print("Step 5: Deploying via WP Admin Playwright...")
print("=" * 65)

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# We'll post the full updated HTML as the page content
# Strip outer html/body tags since WP wraps in its own template
# Actually page 987 uses elementor_canvas so there's no WP theme wrapper
# The post_content IS the full self-contained HTML

# For the text editor approach, we insert the HTML block
post_content = f"<!-- wp:html -->\n{updated_html}\n<!-- /wp:html -->"

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    page = ctx.new_page()

    # Login
    print("\n[5.1] Logging in...")
    page.goto(LOGIN_URL, timeout=30000)
    try:
        page.wait_for_load_state("networkidle", timeout=20000)
    except PlaywrightTimeout:
        pass

    page.fill("#user_login", WP_USER)
    page.fill("#user_pass", WP_PASS)
    page.click("#wp-submit")
    try:
        page.wait_for_load_state("networkidle", timeout=30000)
    except PlaywrightTimeout:
        pass

    if "wp-login" in page.url:
        print("ERROR: Login failed")
        browser.close()
        sys.exit(1)
    print(f"  Logged in. URL: {page.url}")

    # Navigate to page 987 edit
    edit_url = f"https://purebrain.ai/wp-admin/post.php?post={PAGE_ID}&action=edit"
    print(f"\n[5.2] Opening page {PAGE_ID} for edit...")
    page.goto(edit_url, timeout=30000)
    try:
        page.wait_for_load_state("networkidle", timeout=25000)
    except PlaywrightTimeout:
        pass
    time.sleep(2)
    print(f"  Editor URL: {page.url}")

    # Detect editor type
    is_classic = page.query_selector("#content") is not None
    is_block = (
        page.query_selector(".block-editor") is not None
        or page.query_selector(".edit-post-header") is not None
    )
    print(f"  Classic editor: {is_classic}")
    print(f"  Block editor: {is_block}")

    if is_block:
        print("\n[5.3] Block editor detected — switching to code editor...")
        # Use keyboard shortcut or menu to switch to code editor
        try:
            # Try the Options menu → Code editor
            page.keyboard.press("Control+Shift+Alt+m")
            time.sleep(1)
        except Exception:
            pass

        # Look for the code editor textarea
        code_editor = page.query_selector(".editor-post-text-editor, textarea.wp-block-code, #post-content-0")
        if code_editor:
            code_editor.fill(post_content)
            print(f"  Content set in code editor ({len(post_content):,} chars)")
        else:
            print("  WARNING: Could not find code editor textarea")
            # Take screenshot for debugging
            page.screenshot(path="/tmp/invitation_edit_debug.png")
            print("  Debug screenshot saved to /tmp/invitation_edit_debug.png")

    elif is_classic:
        print("\n[5.3] Classic editor detected — setting content via JS...")
        # Switch to Text/HTML mode if in Visual mode
        text_tab = page.query_selector("#content-html")
        if text_tab:
            text_tab.click()
            time.sleep(0.5)

        content_area = page.query_selector("#content")
        if content_area:
            # Use evaluate to set value directly (avoid timeout with large content)
            escaped = post_content.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
            page.evaluate(f"""
                var ta = document.getElementById('content');
                if (ta) {{
                    ta.value = `{escaped}`;
                    ta.dispatchEvent(new Event('input', {{bubbles: true}}));
                    ta.dispatchEvent(new Event('change', {{bubbles: true}}));
                }}
            """)
            time.sleep(0.5)
            # Verify it was set
            current_val = page.evaluate("document.getElementById('content') ? document.getElementById('content').value.length : 0")
            print(f"  Content textarea value length: {current_val:,}")
            if current_val < 1000:
                print("  WARNING: Content might not have been set properly")
        else:
            print("  ERROR: Could not find #content textarea")
            browser.close()
            sys.exit(1)
    else:
        print("  ERROR: Could not detect editor type")
        browser.close()
        sys.exit(1)

    # Save/Update the page
    print("\n[5.4] Saving page...")
    # Click the Update/Publish button
    update_btn = (
        page.query_selector("#publish")
        or page.query_selector('button:has-text("Update")')
        or page.query_selector('input[value="Update"]')
    )
    if update_btn:
        update_btn.click()
        try:
            page.wait_for_load_state("networkidle", timeout=30000)
        except PlaywrightTimeout:
            pass
        time.sleep(2)
        print(f"  After save URL: {page.url}")
        print("  Page saved successfully.")
    else:
        print("  ERROR: Could not find Update button")
        browser.close()
        sys.exit(1)

    browser.close()

# ---- Step 6: Verify live page ----
print()
print("Step 6: Verifying live page...")
time.sleep(3)  # Brief pause for CF cache propagation
req2 = urllib.request.Request(
    "https://purebrain.ai/invitation/",
    headers={"User-Agent": "Mozilla/5.0 (Aether verification)", "Cache-Control": "no-cache"}
)
with urllib.request.urlopen(req2, timeout=30) as resp:
    verify_html = resp.read().decode("utf-8")

verify_checks = [
    ("2026-03-22T04:59:59Z", "countdown target (Friday)"),
    ("Closes Friday", "hero closing day"),
    ("March 21st, EOD Eastern", "pricing section deadline"),
]
all_pass = True
for target, label in verify_checks:
    found = target in verify_html
    status = "PASS" if found else "FAIL"
    print(f"  [{status}] {label}: {repr(target)}")
    if not found:
        all_pass = False

old_checks = [
    ("2026-03-19T04:59:59Z", "old countdown date gone"),
    ("Closes Wednesday", "old Wednesday text gone"),
    ("March 18th", "old March 18 text gone"),
]
for target, label in old_checks:
    not_found = target not in verify_html
    status = "PASS" if not_found else "FAIL (still present!)"
    print(f"  [{status}] {label}")
    if not not_found:
        all_pass = False

print()
if all_pass:
    print("ALL CHECKS PASSED. Invitation page deadline updated to March 21.")
else:
    print("SOME CHECKS FAILED. Manual verification needed.")
    print("CF cache purge may be required — run CF cache flush.")

print()
print("Done.")
