#!/usr/bin/env python3
"""
Set Yoast SEO noindex on 4 dev pages via WordPress Gutenberg sidebar.

The Yoast SEO section appears in the right sidebar (Page panel) as a
collapsed section called "Yoast SEO". We need to:
1. Open the sidebar (click the settings icon if needed)
2. Go to "Page" tab
3. Expand "Yoast SEO" section
4. Click "Advanced" tab inside Yoast
5. Set robots to noindex
6. Save

Pages to noindex:
- /pay-test/           (ID=439)
- /pay-test-sandbox/   (ID=468)
- /elementor-150/      (ID=150)
- /paypal-buttons-embed/ (ID=311)

Usage:
    xvfb-run python3 tools/set_yoast_noindex_playwright.py
"""

import base64
import os
import sys
import time
import re
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

ENV_PATH = "/home/jared/projects/AI-CIV/aether/.env"
load_dotenv(ENV_PATH)

WP_BASE_URL = "https://purebrain.ai"
WP_ADMIN_URL = f"{WP_BASE_URL}/wp-admin"
WP_USER = "Aether"
WP_PASSWORD = os.getenv("PUREBRAIN_WP_PASSWORD", "").strip("'\"")
WP_APP_PASSWORD = os.getenv("PUREBRAIN_WP_APP_PASSWORD", "").strip("'\"")

SCREENSHOT_DIR = Path("/home/jared/projects/AI-CIV/aether/tools/screenshots/noindex-fix2")
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

# Dev pages to noindex
DEV_PAGES = [
    (439, "pay-test"),
    (468, "pay-test-sandbox"),
    (150, "elementor-150"),
    (311, "paypal-buttons-embed"),
]


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def ss(page, name):
    path = str(SCREENSHOT_DIR / f"{name}_{TIMESTAMP}.png")
    try:
        page.screenshot(path=path, timeout=15000)
        log(f"  Screenshot: {path}")
    except Exception as e:
        log(f"  Screenshot failed: {e}")
    return path


def check_robots_via_api(page_id):
    """Check current robots meta via Yoast get_head API."""
    credentials = f"{WP_USER}:{WP_APP_PASSWORD}"
    encoded = base64.b64encode(credentials.encode()).decode()
    headers = {"Authorization": f"Basic {encoded}"}
    try:
        resp = requests.get(
            f"{WP_BASE_URL}/wp-json/yoast/v1/get_head?url={WP_BASE_URL}/?p={page_id}",
            headers=headers, timeout=10
        )
        if resp.status_code == 200:
            head = resp.json().get("html", "")
            match = re.search(r'<meta name="robots" content="([^"]+)"', head)
            return match.group(1) if match else "NOT FOUND"
    except Exception as e:
        return f"Error: {e}"
    return "API Error"


def wp_login(page):
    """Login to WordPress admin. Returns True on success."""
    log("Navigating to wp-admin...")
    page.goto(WP_ADMIN_URL, wait_until="domcontentloaded", timeout=60000)
    time.sleep(3)
    ss(page, "login_01_initial")

    # GoDaddy SSO bypass
    try:
        sso_link = page.locator("text=Log in with username and password")
        if sso_link.is_visible(timeout=5000):
            log("  GoDaddy SSO detected - clicking username/password link...")
            sso_link.click()
            time.sleep(2)
    except Exception:
        pass

    try:
        page.wait_for_selector("#user_login", state="visible", timeout=30000)
    except Exception:
        log("  ERROR: Login form not found")
        return False

    log("  Filling credentials...")
    page.locator("#user_login").fill(WP_USER)
    page.locator("#user_pass").fill(WP_PASSWORD)
    time.sleep(1)

    log("  Submitting...")
    page.locator("#wp-submit").click()
    page.wait_for_load_state("load", timeout=60000)
    time.sleep(4)
    ss(page, "login_04_result")

    current_url = page.url
    if "wp-admin" in current_url or "dashboard" in current_url:
        log(f"  LOGIN SUCCESS! URL: {current_url}")
        return True

    log(f"  LOGIN FAILED. URL: {current_url}")
    return False


def ensure_sidebar_open(page):
    """Make sure the right sidebar is open and on the Page tab."""
    # Check if sidebar is visible
    sidebar = page.locator(".interface-complementary-area, .edit-post-sidebar")
    if not sidebar.is_visible(timeout=2000):
        log("  Sidebar not visible - trying to open it...")
        # Click the settings icon (gear icon) in top right
        settings_btn = page.locator(
            "button[aria-label='Settings'], "
            "button.interface-pinned-items button, "
            "button[aria-label='Show or hide the settings panel']"
        ).first
        if settings_btn.is_visible(timeout=3000):
            settings_btn.click()
            time.sleep(2)

    # Click "Page" tab if it exists (not "Block")
    page_tab = page.locator("button[aria-label='Page'], button[data-label='Page']").first
    if page_tab.is_visible(timeout=3000):
        page_tab.click()
        time.sleep(1)
    else:
        # Try finding tab by text
        page_tab_text = page.locator(".components-tab-panel__tabs button:has-text('Page')").first
        if page_tab_text.is_visible(timeout=2000):
            page_tab_text.click()
            time.sleep(1)


def expand_yoast_and_set_noindex(page, slug):
    """
    Find and expand the Yoast SEO sidebar panel, navigate to Advanced,
    set noindex, and save.
    """
    # Step 1: Make sure sidebar is open
    ensure_sidebar_open(page)
    time.sleep(1)

    # Step 2: Find and expand "Yoast SEO" section in the sidebar
    # The Yoast SEO panel is a collapsed section - we need to click it
    # Looking for: a button or div with "Yoast SEO" text
    log("  Looking for Yoast SEO panel in sidebar...")

    yoast_panel = page.locator(
        ".components-panel__body:has(.components-panel__body-title button:has-text('Yoast SEO')), "
        ".components-panel__body button:has-text('Yoast SEO')"
    ).first

    # Try to find the Yoast SEO toggle button
    yoast_toggle = page.locator(
        "button.components-panel__body-toggle:has-text('Yoast SEO'), "
        ".components-panel__body-toggle[aria-label*='Yoast'], "
        "button:has-text('Yoast SEO')"
    ).first

    if yoast_toggle.is_visible(timeout=5000):
        # Check if already expanded
        aria_expanded = yoast_toggle.get_attribute("aria-expanded")
        log(f"  Found Yoast SEO toggle, aria-expanded={aria_expanded}")
        if aria_expanded != "true":
            yoast_toggle.click()
            time.sleep(2)
            log("  Expanded Yoast SEO panel")
        ss(page, f"edit_{slug}_02_yoast_expanded")
    else:
        log("  Yoast toggle button not found by standard selectors")
        # Take screenshot to see what's there
        ss(page, f"edit_{slug}_02_sidebar_state")

        # Try evaluating what's in the sidebar
        sidebar_text = page.evaluate("""
            () => {
                const sidebar = document.querySelector('.interface-complementary-area, .edit-post-sidebar');
                return sidebar ? sidebar.innerText.slice(0, 1000) : 'SIDEBAR NOT FOUND';
            }
        """)
        log(f"  Sidebar content: {sidebar_text[:300]}")

        # Try clicking anything that has Yoast in text
        yoast_any = page.locator("*:has-text('Yoast SEO')").last
        if yoast_any.is_visible(timeout=3000):
            log("  Clicking last element with Yoast SEO text...")
            yoast_any.click()
            time.sleep(2)
            ss(page, f"edit_{slug}_02b_after_yoast_click")

    # Step 3: Look for Yoast content - may need to scroll within sidebar
    # The Yoast panel in Gutenberg sidebar shows tabs: SEO, Readability, Schema, Social, Advanced
    log("  Looking for Yoast Advanced tab...")

    # Yoast tabs are usually links with specific classes or aria-labels
    advanced_selectors = [
        "a[href='#wpseo-advanced']",
        "button:has-text('Advanced')",
        "a:has-text('Advanced')",
        ".wpseo-meta-section-link:has-text('Advanced')",
        "[data-tab-id='advanced']",
        ".yoast-seo-advanced",
    ]

    advanced_tab_found = False
    for sel in advanced_selectors:
        try:
            el = page.locator(sel).first
            if el.is_visible(timeout=2000):
                el.click()
                time.sleep(2)
                log(f"  Clicked Advanced tab via: {sel}")
                ss(page, f"edit_{slug}_03_advanced")
                advanced_tab_found = True
                break
        except Exception:
            continue

    if not advanced_tab_found:
        # Look for Yoast content on the whole page - might be in a metabox at bottom
        log("  Scrolling to find Yoast content below editor...")
        page.evaluate("window.scrollTo(0, 99999)")
        time.sleep(2)
        ss(page, f"edit_{slug}_03_scrolled")

        # Check for classic metabox
        yoast_mb = page.locator("#wpseo_meta, #yoast-seo").first
        if yoast_mb.is_visible(timeout=3000):
            yoast_mb.scroll_into_view_if_needed()
            time.sleep(1)
            # Look for advanced tab within metabox
            adv_link = yoast_mb.locator("a[href='#wpseo-advanced'], a:has-text('Advanced')").first
            if adv_link.is_visible(timeout=2000):
                adv_link.click()
                time.sleep(1)
                ss(page, f"edit_{slug}_03b_metabox_advanced")
                advanced_tab_found = True

    # Step 4: Find the robots/noindex select
    log("  Looking for robots index dropdown...")

    robots_selectors = [
        "select#wpseo-robots-index",
        "select[id*='robots-index']",
        "select[name*='robots']",
        "select[id*='noindex']",
        "#wpseo_noindex",
        "select#wpseo_noindex",
    ]

    for sel in robots_selectors:
        try:
            el = page.locator(sel).first
            if el.is_visible(timeout=3000):
                current = el.input_value()
                options = page.evaluate(f"""
                    () => {{
                        const s = document.querySelector('{sel}');
                        if (!s) return [];
                        return Array.from(s.options).map(o => ({{v: o.value, t: o.text}}));
                    }}
                """)
                log(f"  Found robots select: {sel}, current='{current}', options={options}")

                # Select "No" (noindex) - Yoast uses value "2" for noindex
                try:
                    el.select_option(value="2")
                    log("  Selected value='2' (noindex)")
                except Exception:
                    try:
                        el.select_option(label="No")
                        log("  Selected label='No'")
                    except Exception as e2:
                        log(f"  Error selecting noindex: {e2}")
                        return False

                time.sleep(1)
                ss(page, f"edit_{slug}_04_noindex_selected")

                # Save the page
                log("  Saving page (Update button)...")
                save_selectors = [
                    "button.editor-post-publish-button",
                    "button[aria-label='Update']",
                    "button:has-text('Update')",
                    "input#publish",
                    "input#save-post",
                ]
                for save_sel in save_selectors:
                    try:
                        save_btn = page.locator(save_sel).first
                        if save_btn.is_visible(timeout=3000):
                            save_btn.click()
                            time.sleep(5)
                            ss(page, f"edit_{slug}_05_saved")
                            log("  Saved!")
                            return True
                    except Exception:
                        continue

                log("  WARNING: Could not find save button")
                return False

        except Exception:
            continue

    # If we couldn't find robots select, take diagnostic screenshot
    ss(page, f"edit_{slug}_04_no_robots_dropdown")
    log("  ERROR: Could not find robots dropdown")

    # Diagnostic: show all select elements on page
    selects = page.evaluate("""
        () => Array.from(document.querySelectorAll('select')).map(s => ({
            id: s.id, name: s.name, class: s.className.slice(0, 50)
        }))
    """)
    log(f"  All selects on page: {selects}")

    return False


def set_noindex_for_page(page, page_id, slug):
    """Navigate to edit page, set Yoast noindex."""
    log(f"\n--- Processing /{slug}/ (ID={page_id}) ---")

    # Check current state
    current_robots = check_robots_via_api(page_id)
    log(f"  Current robots (API): {current_robots}")

    if "noindex" in current_robots:
        log(f"  Already noindexed! Skipping.")
        return True

    # Navigate to Gutenberg editor
    edit_url = f"{WP_ADMIN_URL}/post.php?post={page_id}&action=edit"
    log(f"  Navigating to: {edit_url}")
    page.goto(edit_url, wait_until="domcontentloaded", timeout=60000)
    time.sleep(5)
    ss(page, f"edit_{slug}_01_loaded")

    # Dismiss welcome modal if present
    try:
        for dismiss_sel in [
            "button[aria-label='Close']",
            "button:has-text('Skip')",
            "button:has-text('Close')",
        ]:
            btn = page.locator(dismiss_sel).first
            if btn.is_visible(timeout=2000):
                btn.click()
                time.sleep(1)
                break
    except Exception:
        pass

    success = expand_yoast_and_set_noindex(page, slug)

    if success:
        # Wait for save and verify
        time.sleep(3)
        new_robots = check_robots_via_api(page_id)
        log(f"  Post-save robots (API): {new_robots}")
        if "noindex" in new_robots:
            log(f"  VERIFIED: /{slug}/ is now noindexed!")
        else:
            log(f"  NOTE: API shows '{new_robots}' - noindex may take effect after cache clear")

    return success


def main():
    log("=" * 60)
    log("Set Yoast Noindex on Dev Pages - Playwright v2")
    log(f"Started: {datetime.now()}")
    log("=" * 60)

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    results = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=2,
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
        )
        pw_page = context.new_page()
        pw_page.set_default_timeout(30000)

        try:
            if not wp_login(pw_page):
                log("FATAL: Login failed")
                browser.close()
                return 1

            for page_id, slug in DEV_PAGES:
                try:
                    success = set_noindex_for_page(pw_page, page_id, slug)
                    results[slug] = "success" if success else "failed"
                except Exception as e:
                    log(f"  ERROR on /{slug}/: {e}")
                    import traceback
                    traceback.print_exc()
                    results[slug] = f"error: {e}"
                    try:
                        ss(pw_page, f"edit_{slug}_ERROR")
                    except Exception:
                        pass

        except Exception as e:
            log(f"FATAL: {e}")
            import traceback
            traceback.print_exc()
        finally:
            browser.close()

    log("\n" + "=" * 60)
    log("FINAL RESULTS")
    log("=" * 60)
    for slug, result in results.items():
        log(f"  /{slug}/: {result}")

    log("\n[Final Robots Verification via API]")
    for page_id, slug in DEV_PAGES:
        robots = check_robots_via_api(page_id)
        log(f"  /{slug}/ (ID={page_id}): {robots}")

    log(f"\nScreenshots in: {SCREENSHOT_DIR}")
    log("DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
