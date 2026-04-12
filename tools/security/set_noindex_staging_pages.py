#!/usr/bin/env python3
"""
Set Yoast SEO noindex on staging pages via WP Admin UI using Playwright.

Pages:
  - blog-old       (ID 95)  - originally referred to as purebrain-2-0 in task brief
  - purebrain-2-0  (ID 174) - actual purebrain-2-0 page
  - purebrain-3    (ID 338)
  - purebrain-4    (ID 383)
  - living-avatar  (ID 532)
"""

import os
import sys
import time
from playwright.sync_api import sync_playwright

# Load credentials from .env
import subprocess
env_out = subprocess.check_output(
    ['bash', '-c', 'source /home/jared/projects/AI-CIV/aether/.env && echo "PASS=$PUREBRAIN_WP_PASSWORD"'],
    text=True
)
WP_PASSWORD = None
for line in env_out.splitlines():
    if line.startswith('PASS='):
        WP_PASSWORD = line[5:].strip()
        break

if not WP_PASSWORD:
    print("ERROR: Could not read PUREBRAIN_WP_PASSWORD from .env")
    sys.exit(1)

WP_USER = "Aether"
WP_ADMIN_URL = "https://purebrain.ai/wp-admin"

# Pages to set noindex on
PAGES = [
    {"id": 95,  "name": "blog-old",      "slug": "blog-old"},
    {"id": 174, "name": "purebrain-2-0", "slug": "purebrain-2-0"},
    {"id": 338, "name": "purebrain-3",   "slug": "purebrain-3"},
    {"id": 383, "name": "purebrain-4",   "slug": "purebrain-4"},
    {"id": 532, "name": "living-avatar", "slug": "living-avatar"},
]

results = []

def set_noindex_for_page(page, wp_page_id, name):
    """Navigate to WP Admin page editor and set Yoast noindex."""
    edit_url = f"{WP_ADMIN_URL}/post.php?post={wp_page_id}&action=edit"
    print(f"\n  Navigating to edit page {wp_page_id} ({name})...")
    page.goto(edit_url, wait_until="domcontentloaded", timeout=30000)
    time.sleep(2)

    # Check if we're on the edit page
    if "post.php" not in page.url and "action=edit" not in page.url:
        print(f"  ERROR: Not on edit page. Current URL: {page.url}")
        return False

    # Check for Yoast SEO sidebar/panel
    # In the classic editor, Yoast adds a meta box below the editor
    # In block editor, it appears in the sidebar

    # Try to find and click Yoast's "Advanced" tab
    # Classic editor approach: look for Yoast SEO meta box

    # First check if this is block editor or classic editor
    is_block_editor = page.locator(".block-editor").is_visible(timeout=3000) if page.locator(".block-editor").count() > 0 else False

    if is_block_editor:
        print(f"  Block editor detected")
        # In block editor: Yoast SEO sidebar > Advanced tab
        # Look for Yoast tab in sidebar
        yoast_btn = page.locator('[data-label="Yoast SEO"], .yoast-icon-button, button:has-text("Yoast SEO")')
        if yoast_btn.count() > 0:
            yoast_btn.first.click()
            time.sleep(1)

        # Find Advanced tab in Yoast panel
        advanced_tab = page.locator('button:has-text("Advanced"), .yoast-tab:has-text("Advanced")')
        if advanced_tab.count() > 0:
            advanced_tab.first.click()
            time.sleep(1)
    else:
        print(f"  Classic editor or Elementor mode detected")
        # In classic editor: Yoast SEO meta box with tabs
        # Look for "Advanced" tab in Yoast meta box
        yoast_advanced = page.locator('#wpseo_meta .yoast-field-group:has-text("Advanced"), .wpseo-field-group a:has-text("Advanced"), #yoast-seo-meta-box-actions a:has-text("Advanced")')

        # More specific: Look for nav tabs in Yoast meta box
        advanced_tab = page.locator('#wpseo-settings-tabs .yoast-tab:has-text("Advanced"), .yoast-tab-advanced, a.yoast-tab[href*="advanced"]')
        if advanced_tab.count() > 0:
            advanced_tab.first.click()
            time.sleep(1)
        else:
            # Try clicking directly in the Yoast meta box area
            print(f"  Looking for Yoast meta box...")
            yoast_box = page.locator('#wpseo_meta, #yoast-seo-meta-box, .wpseo-metabox')
            if yoast_box.count() > 0:
                print(f"  Found Yoast meta box")
                # Click the Advanced or Settings tab
                tab = yoast_box.first.locator('a:has-text("Advanced"), button:has-text("Advanced")')
                if tab.count() > 0:
                    tab.first.click()
                    time.sleep(1)
                else:
                    print(f"  WARNING: Could not find Advanced tab in Yoast meta box")
            else:
                print(f"  WARNING: Yoast meta box not found on page")

    # Now find the "Allow search engines to show this Page in search results?" dropdown
    # Yoast uses select with id like "wpseo_noindex" or name "_yoast_wpseo_meta-robots-noindex"

    # Try multiple selectors for the noindex dropdown
    selectors = [
        'select[name="wpseo_meta[meta-robots-noindex]"]',
        'select#wpseo_noindex',
        'select[id*="noindex"]',
        'select[name*="noindex"]',
        'select.yoast-field-group__select[data-react-props*="noindex"]',
    ]

    noindex_select = None
    for sel in selectors:
        el = page.locator(sel)
        if el.count() > 0:
            noindex_select = el.first
            print(f"  Found noindex select with: {sel}")
            break

    if noindex_select is None:
        # Take a screenshot to debug
        screenshot_path = f"/home/jared/projects/AI-CIV/aether/exports/screenshots/noindex_debug_{wp_page_id}.png"
        page.screenshot(path=screenshot_path)
        print(f"  WARNING: noindex select not found. Screenshot saved to {screenshot_path}")
        print(f"  Page HTML snippet of Yoast area:")
        try:
            yoast_html = page.locator('#wpseo_meta').inner_html(timeout=2000)
            print(yoast_html[:500] if len(yoast_html) > 500 else yoast_html)
        except:
            pass
        return False

    # Select "Yes" (noindex) - value is typically "1" for noindex
    current_value = noindex_select.input_value()
    print(f"  Current noindex value: {current_value}")
    noindex_select.select_option("1")  # 1 = noindex
    time.sleep(0.5)
    new_value = noindex_select.input_value()
    print(f"  New noindex value: {new_value}")

    # Save/Update the page
    update_btn = page.locator('#publish, input[value="Update"], button:has-text("Update")')
    if update_btn.count() > 0:
        update_btn.first.click()
        print(f"  Clicked Update button...")
        time.sleep(3)
        print(f"  Page saved. Current URL: {page.url}")
        return True
    else:
        print(f"  WARNING: Could not find Update/Publish button")
        return False


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        viewport={"width": 1280, "height": 900}
    )
    wp_page = context.new_page()

    print("=== Logging into WordPress Admin ===")
    # GoDaddy hosting shows SSO login page first - use standard login bypass link
    wp_page.goto(f"{WP_ADMIN_URL}/wp-login.php?wpaas-standard-login=1", wait_until="domcontentloaded", timeout=20000)
    time.sleep(2)

    # Take screenshot to debug login page
    wp_page.screenshot(path="/home/jared/projects/AI-CIV/aether/exports/screenshots/wp_login_before.png")

    # Fill login form
    wp_page.fill("#user_login", WP_USER)
    wp_page.fill("#user_pass", WP_PASSWORD)
    wp_page.click("#wp-submit")
    time.sleep(3)

    # Take screenshot after login attempt
    wp_page.screenshot(path="/home/jared/projects/AI-CIV/aether/exports/screenshots/wp_login_after.png")
    print(f"After login attempt. URL: {wp_page.url}")

    # Handle 2FA if present (wpsec 2FA plugin)
    if "two-factor" in wp_page.url or "wpsec" in wp_page.content() or "verification" in wp_page.content().lower():
        print("2FA detected - checking for email/code input...")
        # The 2FA form might have a code input
        code_input = wp_page.locator('input[name="authcode"], input[name="code"], input[type="number"]')
        if code_input.count() > 0:
            print("2FA code input found - cannot proceed automatically (need manual code)")
            wp_page.screenshot(path="/home/jared/projects/AI-CIV/aether/exports/screenshots/wp_login_2fa.png")
            browser.close()
            print("ERROR: 2FA required. Run this script manually or use the mu-plugin approach.")
            sys.exit(1)

    if "wp-admin" in wp_page.url or "dashboard" in wp_page.url:
        print(f"Login successful. URL: {wp_page.url}")
    else:
        print(f"Login may have failed or 2FA required. URL: {wp_page.url}")
        wp_page.screenshot(path="/home/jared/projects/AI-CIV/aether/exports/screenshots/wp_login_debug.png")
        browser.close()
        sys.exit(1)

    # Process each page
    for p_info in PAGES:
        print(f"\n{'='*50}")
        print(f"Processing: {p_info['name']} (ID: {p_info['id']})")
        success = set_noindex_for_page(wp_page, p_info["id"], p_info["name"])
        results.append({
            "name": p_info["name"],
            "id": p_info["id"],
            "noindex_set": success,
        })

    browser.close()

print("\n\n=== RESULTS ===")
for r in results:
    status = "SUCCESS" if r["noindex_set"] else "FAILED"
    print(f"  {r['name']} (ID {r['id']}): {status}")

print("\nDone.")
