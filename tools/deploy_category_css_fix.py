#!/usr/bin/env python3
"""
Deploy Category Page CSS Fix to purebrain.ai
Feb 18, 2026 - Fix category/archive pages (white text on dark bg)

Strategy:
1. Login to WordPress admin
2. Navigate to Customizer > Additional CSS
3. GET current CSS from CodeMirror
4. CHECK if fix already applied
5. APPEND new CSS block at the bottom
6. SET the full CSS back
7. Publish
8. Verify category page, homepage, and blog
"""

import sys
import time
import os
from datetime import datetime
from playwright.sync_api import sync_playwright

# WordPress credentials
from dotenv import load_dotenv
load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

WP_ADMIN_URL = "https://purebrain.ai/wp-admin"
WP_CSS_URL = "https://purebrain.ai/wp-admin/customize.php?autofocus[section]=custom_css"
USERNAME = "Aether"
PASSWORD = os.getenv('PUREBRAIN_WP_PASSWORD', '')

SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/tools/screenshots"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

# The CSS to append
CATEGORY_CSS_FIX = """

/* === CATEGORY PAGE FIX (Feb 18) === */
body.category,
body.archive {
  color: #ffffff !important;
  background: #0a0a0a !important;
}
body.category a,
body.archive a {
  color: #2a93c1 !important;
}
body.category a:hover,
body.archive a:hover {
  color: #f1420b !important;
}
body.category h1,
body.category h2,
body.category .page-title,
body.archive h1,
body.archive h2,
body.archive .page-title {
  color: #ffffff !important;
}
body.category .nav-links a,
body.archive .nav-links a {
  color: #2a93c1 !important;
}
/* === END CATEGORY PAGE FIX === */"""

DUPLICATE_CHECK_STRING = "CATEGORY PAGE FIX"


def screenshot(page, label):
    """Take a screenshot with consistent naming."""
    path = f"{SCREENSHOT_DIR}/catfix_{label}_{TIMESTAMP}.png"
    page.screenshot(path=path, full_page=False)
    print(f"  Screenshot: {path}")
    return path


def main():
    if not PASSWORD:
        print("ERROR: PUREBRAIN_WP_PASSWORD not found in .env")
        return 1

    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    print("=" * 60)
    print("PureBrain.ai Category Page CSS Fix Deployment")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"CSS to append: {len(CATEGORY_CSS_FIX)} characters")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        # ============ STEP 1: LOGIN ============
        print("\n=== STEP 1: Logging into WordPress ===")

        page.goto(WP_ADMIN_URL, wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)
        screenshot(page, "01_login_page")

        # Check for GoDaddy SSO
        try:
            login_link = page.locator("text=Log in with username and password")
            if login_link.is_visible(timeout=5000):
                print("  Found GoDaddy SSO - clicking 'Log in with username and password'...")
                login_link.click()
                time.sleep(2)
        except:
            print("  Standard WordPress login form")

        # Wait for login form
        try:
            page.wait_for_selector('#user_login', state='visible', timeout=30000)
        except:
            print("  WARNING: #user_login not visible, trying to proceed anyway...")
            screenshot(page, "01b_login_form_issue")

        # Fill credentials
        username_field = page.locator("#user_login")
        password_field = page.locator("#user_pass")

        if username_field.count() > 0:
            username_field.fill(USERNAME)
            password_field.fill(PASSWORD)

            # Check for CAPTCHA
            captcha_input = page.locator('input[name="captcha_code"]')
            if captcha_input.count() > 0 and captcha_input.is_visible():
                screenshot(page, "02_captcha_detected")
                print("\n*** CAPTCHA DETECTED ***")
                print("  Cannot proceed automatically. Please login manually.")
                browser.close()
                return 1

            # Submit login
            page.locator("#wp-submit").click()
            page.wait_for_load_state("load", timeout=60000)
            time.sleep(5)

            screenshot(page, "02_after_login")

            # Verify login success
            current_url = page.url
            print(f"  Current URL: {current_url}")
            if "wp-login" in current_url:
                print("  ERROR: Still on login page - login failed")
                screenshot(page, "02_login_failed")
                browser.close()
                return 1
            else:
                print("  Login successful!")
        else:
            print("  ERROR: Could not find login fields")
            screenshot(page, "02_no_login_fields")
            browser.close()
            return 1

        # ============ STEP 2: NAVIGATE TO ADDITIONAL CSS ============
        print("\n=== STEP 2: Navigating to Additional CSS ===")

        page.goto(WP_CSS_URL, wait_until="domcontentloaded", timeout=90000)
        print("  Waiting for Customizer to load (15 seconds)...")
        time.sleep(15)

        screenshot(page, "03_customizer")

        # Wait for CodeMirror
        try:
            page.wait_for_selector('.CodeMirror', state='visible', timeout=30000)
            print("  CodeMirror editor found!")
        except:
            print("  WARNING: CodeMirror not found after 30s, trying to proceed...")
            screenshot(page, "03b_no_codemirror")

        time.sleep(3)

        # ============ STEP 3: GET CURRENT CSS ============
        print("\n=== STEP 3: Getting current CSS ===")

        current_css = page.evaluate("""
            () => {
                const cm = document.querySelector('.CodeMirror');
                if (cm && cm.CodeMirror) {
                    return cm.CodeMirror.getValue();
                }
                return null;
            }
        """)

        if current_css is None:
            print("  ERROR: Could not read current CSS from CodeMirror!")
            screenshot(page, "04_no_css_read")
            browser.close()
            return 1

        print(f"  Current CSS length: {len(current_css)} characters")
        print(f"  Current CSS lines: {len(current_css.splitlines())}")

        # ============ STEP 4: CHECK FOR DUPLICATE ============
        print("\n=== STEP 4: Checking for duplicate ===")

        if DUPLICATE_CHECK_STRING in current_css:
            print(f"  '{DUPLICATE_CHECK_STRING}' already found in CSS!")
            print("  Skipping deployment - fix already applied.")
            screenshot(page, "04_already_present")

            # Still verify the page
            print("\n  Verifying category page anyway...")
            verify_page = context.new_page()
            verify_page.goto("https://purebrain.ai/category/for-teams/", wait_until="domcontentloaded", timeout=30000)
            time.sleep(5)
            verify_page.screenshot(
                path=f"{SCREENSHOT_DIR}/catfix_verify_category_{TIMESTAMP}.png",
                full_page=False
            )
            print(f"  Screenshot: {SCREENSHOT_DIR}/catfix_verify_category_{TIMESTAMP}.png")
            verify_page.close()
            browser.close()
            return 0

        print("  Fix not yet applied - proceeding with deployment.")

        # ============ STEP 5: APPEND CSS ============
        print("\n=== STEP 5: Appending category fix CSS ===")

        full_css = current_css + CATEGORY_CSS_FIX
        print(f"  New total CSS length: {len(full_css)} characters (+{len(CATEGORY_CSS_FIX)} appended)")

        # Set the CSS via CodeMirror API - pass as argument, not template literal
        result = page.evaluate("""(css) => {
            const cm = document.querySelector('.CodeMirror');
            if (cm && cm.CodeMirror) {
                cm.CodeMirror.setValue(css);
                cm.CodeMirror.refresh();
                return 'success_' + cm.CodeMirror.getValue().length + '_chars';
            }
            return 'failed_no_codemirror';
        }""", full_css)

        print(f"  CSS set result: {result}")

        if not result.startswith("success"):
            print("  ERROR: Failed to set CSS!")
            screenshot(page, "05_css_set_failed")
            browser.close()
            return 1

        time.sleep(2)
        screenshot(page, "05_css_updated")

        # ============ STEP 6: PUBLISH ============
        print("\n=== STEP 6: Publishing changes ===")

        time.sleep(3)

        # Try multiple publish button selectors
        publish_btn = page.locator("#save, button#save, #customize-save-button-wrapper button")
        if publish_btn.count() > 0 and publish_btn.first.is_visible():
            print(f"  Found publish button")
            publish_btn.first.click()
            print("  Clicked Publish!")
            time.sleep(8)
        else:
            # Try text-based selector
            pub_text = page.locator("button:has-text('Publish'), input[value='Publish']")
            if pub_text.count() > 0:
                pub_text.first.click()
                print("  Clicked Publish (text selector)!")
                time.sleep(8)
            else:
                print("  Publish button not found, trying Ctrl+Shift+S...")
                page.keyboard.press("Control+Shift+s")
                time.sleep(8)

        screenshot(page, "06_published")

        # Check if publish was successful (button should show "Published")
        publish_status = page.evaluate("""
            () => {
                const btn = document.querySelector('#save');
                if (btn) return btn.textContent.trim() + ' | disabled=' + btn.disabled;
                return 'no save button found';
            }
        """)
        print(f"  Publish status: {publish_status}")

        # ============ STEP 7: VERIFY ============
        print("\n=== STEP 7: Verifying pages ===")

        verify_page = context.new_page()

        # Verify category page (the main target)
        print("  Verifying category page: /category/for-teams/ ...")
        verify_page.goto("https://purebrain.ai/category/for-teams/", wait_until="domcontentloaded", timeout=30000)
        time.sleep(5)
        # Force cache bypass
        verify_page.evaluate("() => { location.reload(true); }")
        time.sleep(5)
        cat_screenshot = f"{SCREENSHOT_DIR}/catfix_07_verify_category_{TIMESTAMP}.png"
        verify_page.screenshot(path=cat_screenshot, full_page=True)
        print(f"  Screenshot: {cat_screenshot}")

        # Check computed styles on category page
        cat_styles = verify_page.evaluate("""
            () => {
                const body = document.body;
                const bodyStyles = getComputedStyle(body);
                const h1 = document.querySelector('h1, .page-title');
                const links = document.querySelectorAll('article a, .entry-title a');
                return {
                    bodyColor: bodyStyles.color,
                    bodyBg: bodyStyles.backgroundColor,
                    bodyClasses: body.className,
                    h1Text: h1 ? h1.textContent.substring(0, 50) : 'no h1',
                    h1Color: h1 ? getComputedStyle(h1).color : 'n/a',
                    linkCount: links.length,
                    firstLinkColor: links.length > 0 ? getComputedStyle(links[0]).color : 'n/a'
                };
            }
        """)
        print(f"  Category page styles: {cat_styles}")

        # Verify homepage
        print("  Verifying homepage...")
        verify_page.goto("https://purebrain.ai/", wait_until="domcontentloaded", timeout=30000)
        time.sleep(5)
        verify_page.evaluate("() => { location.reload(true); }")
        time.sleep(5)
        home_screenshot = f"{SCREENSHOT_DIR}/catfix_08_verify_homepage_{TIMESTAMP}.png"
        verify_page.screenshot(path=home_screenshot, full_page=False)
        print(f"  Screenshot: {home_screenshot}")

        # Verify blog listing
        print("  Verifying blog page...")
        verify_page.goto("https://purebrain.ai/blog/", wait_until="domcontentloaded", timeout=30000)
        time.sleep(5)
        verify_page.evaluate("() => { location.reload(true); }")
        time.sleep(5)
        blog_screenshot = f"{SCREENSHOT_DIR}/catfix_09_verify_blog_{TIMESTAMP}.png"
        verify_page.screenshot(path=blog_screenshot, full_page=False)
        print(f"  Screenshot: {blog_screenshot}")

        verify_page.close()
        browser.close()

        print(f"\n{'=' * 60}")
        print("DEPLOYMENT COMPLETE")
        print(f"{'=' * 60}")
        print(f"CSS appended: {len(CATEGORY_CSS_FIX)} characters")
        print(f"Total CSS: {len(full_css)} characters")
        print(f"Screenshots saved to: {SCREENSHOT_DIR}/")
        print(f"\nVerify visually:")
        print(f"  Category: https://purebrain.ai/category/for-teams/")
        print(f"  Homepage: https://purebrain.ai/")
        print(f"  Blog:     https://purebrain.ai/blog/")
        print(f"\nKey screenshots:")
        print(f"  Category: {cat_screenshot}")
        print(f"  Homepage: {home_screenshot}")
        print(f"  Blog:     {blog_screenshot}")

        return 0


if __name__ == "__main__":
    sys.exit(main())
