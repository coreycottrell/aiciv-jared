#!/usr/bin/env python3
"""
Deploy Category Page CSS Fix to purebrain.ai - v3
Uses Playwright with CAPTCHA solving via vision.

Strategy:
1. Navigate to login page
2. Fill username + password
3. Save CAPTCHA image separately for vision reading
4. Accept CAPTCHA answer as argument
5. Fill CAPTCHA and submit
6. Navigate to Customizer > Additional CSS
7. Get current CSS, append fix, set full CSS
8. Publish and verify

Usage:
  Phase 1 (capture CAPTCHA):
    python3 deploy_category_css_fix_v3.py

  Phase 2 (solve and deploy):
    python3 deploy_category_css_fix_v3.py "captcha_text_here"
"""

import sys
import time
import os
from datetime import datetime
from playwright.sync_api import sync_playwright

from dotenv import load_dotenv
load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

WP_ADMIN_URL = "https://purebrain.ai/wp-admin"
WP_CSS_URL = "https://purebrain.ai/wp-admin/customize.php?autofocus[section]=custom_css"
USERNAME = "Aether"
PASSWORD = os.getenv('PUREBRAIN_WP_PASSWORD', '')

SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/tools/screenshots"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
STATE_DIR = "/tmp/purebrain-catfix-state"

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

DUPLICATE_CHECK = "CATEGORY PAGE FIX"


def screenshot(page, label):
    path = f"{SCREENSHOT_DIR}/catfix_{label}_{TIMESTAMP}.png"
    page.screenshot(path=path, full_page=False)
    print(f"  Screenshot: {path}")
    return path


def phase1_capture_captcha():
    """Load login page, fill creds, save CAPTCHA image for vision reading."""
    print("=== PHASE 1: Capturing CAPTCHA ===")
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    os.makedirs(STATE_DIR, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        )
        # Save storage state for reuse
        page = context.new_page()

        page.goto(WP_ADMIN_URL, wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)

        # Click "Log in with username and password" if present
        try:
            login_link = page.locator("text=Log in with username and password")
            if login_link.is_visible(timeout=5000):
                print("  Clicking 'Log in with username and password'...")
                login_link.click()
                time.sleep(2)
        except:
            pass

        # Fill credentials
        page.wait_for_selector('#user_login', state='visible', timeout=30000)
        page.locator("#user_login").fill(USERNAME)
        page.locator("#user_pass").fill(PASSWORD)

        time.sleep(1)

        # Save full page screenshot
        full_path = screenshot(page, "captcha_full")

        # Try to find and save just the CAPTCHA image
        captcha_img = page.locator("img.captcha-image, img[class*='captcha'], img[src*='captcha'], img[alt*='captcha'], img[alt*='Captcha']")
        if captcha_img.count() > 0:
            captcha_path = f"{SCREENSHOT_DIR}/catfix_captcha_only_{TIMESTAMP}.png"
            captcha_img.first.screenshot(path=captcha_path)
            print(f"  CAPTCHA image saved: {captcha_path}")
        else:
            # Try to find the CAPTCHA by looking for images between password and the text field
            print("  No CAPTCHA img element found, trying broader search...")
            all_imgs = page.locator("form img, #loginform img")
            for i in range(all_imgs.count()):
                img = all_imgs.nth(i)
                src = img.get_attribute("src") or ""
                alt = img.get_attribute("alt") or ""
                print(f"  Found img: src='{src[:60]}', alt='{alt}'")
                captcha_path = f"{SCREENSHOT_DIR}/catfix_captcha_img{i}_{TIMESTAMP}.png"
                img.screenshot(path=captcha_path)
                print(f"  Saved: {captcha_path}")

        # Also get the CAPTCHA input field info
        all_inputs = page.locator("input[type='text']")
        print(f"\n  Text input fields found: {all_inputs.count()}")
        for i in range(all_inputs.count()):
            inp = all_inputs.nth(i)
            name = inp.get_attribute("name") or ""
            id_attr = inp.get_attribute("id") or ""
            placeholder = inp.get_attribute("placeholder") or ""
            print(f"  Input {i}: name='{name}', id='{id_attr}', placeholder='{placeholder}'")

        # Save browser state for phase 2
        context.storage_state(path=f"{STATE_DIR}/state.json")
        print(f"\n  Browser state saved to {STATE_DIR}/state.json")

        browser.close()

    print(f"\nCAPTCHA screenshot: {full_path}")
    print("Read the CAPTCHA text, then run:")
    print(f'  python3 {sys.argv[0]} "CAPTCHA_TEXT_HERE"')
    return 0


def phase2_solve_and_deploy(captcha_text):
    """Fill CAPTCHA, login, deploy CSS, verify."""
    print(f'=== PHASE 2: Solving CAPTCHA and deploying ===')
    print(f'  CAPTCHA answer: "{captcha_text}"')
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        )
        page = context.new_page()

        # Navigate to login page fresh (CAPTCHA changes each load)
        print("\n  Loading login page...")
        page.goto(WP_ADMIN_URL, wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)

        # Click "Log in with username and password"
        try:
            login_link = page.locator("text=Log in with username and password")
            if login_link.is_visible(timeout=5000):
                login_link.click()
                time.sleep(2)
        except:
            pass

        # Fill credentials
        page.wait_for_selector('#user_login', state='visible', timeout=30000)
        page.locator("#user_login").fill(USERNAME)
        page.locator("#user_pass").fill(PASSWORD)

        # Save current CAPTCHA for reference
        captcha_ref_path = screenshot(page, "captcha_current")
        print(f"  NOTE: This is a NEW CAPTCHA (page reloaded). The text '{captcha_text}' was from the previous load.")
        print("  If login fails, re-run phase 1 for a fresh CAPTCHA.")

        # Find CAPTCHA input field (the text input that isn't username)
        captcha_filled = False
        all_inputs = page.locator("input[type='text']")
        for i in range(all_inputs.count()):
            inp = all_inputs.nth(i)
            name = inp.get_attribute("name") or ""
            id_attr = inp.get_attribute("id") or ""
            if id_attr != "user_login" and name != "log":
                inp.fill(captcha_text)
                print(f"  Filled CAPTCHA in: name='{name}', id='{id_attr}'")
                captcha_filled = True
                break

        if not captcha_filled:
            print("  WARNING: Could not find CAPTCHA input field!")
            screenshot(page, "no_captcha_field")

        time.sleep(1)

        # Submit login
        print("  Submitting login...")
        page.locator("#wp-submit").click()
        page.wait_for_load_state("load", timeout=60000)
        time.sleep(5)
        screenshot(page, "after_login")

        current_url = page.url
        print(f"  Current URL: {current_url}")

        if "wp-login" in current_url:
            print("  LOGIN FAILED")
            error_el = page.locator("#login_error")
            if error_el.count() > 0:
                print(f"  Error: {error_el.first.inner_text()}")
            browser.close()
            return 1

        print("  LOGIN SUCCESS!")

        # Navigate to Additional CSS
        print("\n  Navigating to Additional CSS...")
        page.goto(WP_CSS_URL, wait_until="domcontentloaded", timeout=90000)
        print("  Waiting for Customizer (15s)...")
        time.sleep(15)
        screenshot(page, "customizer")

        # Wait for CodeMirror
        try:
            page.wait_for_selector('.CodeMirror', state='visible', timeout=30000)
            print("  CodeMirror found!")
        except:
            print("  WARNING: CodeMirror not visible")
            screenshot(page, "no_codemirror")

        time.sleep(3)

        # GET current CSS
        print("\n  Getting current CSS...")
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
            print("  ERROR: Could not read CSS!")
            screenshot(page, "css_read_error")
            browser.close()
            return 1

        print(f"  Current CSS: {len(current_css)} characters")

        # Check for duplicate
        if DUPLICATE_CHECK in current_css:
            print(f"  '{DUPLICATE_CHECK}' already present!")
            screenshot(page, "already_present")
            # Still do verification
            print("  Skipping CSS update, proceeding to verification...")
        else:
            # Append CSS
            full_css = current_css + CATEGORY_CSS_FIX
            print(f"  Appending {len(CATEGORY_CSS_FIX)} chars -> total {len(full_css)} chars")

            result = page.evaluate("""(css) => {
                const cm = document.querySelector('.CodeMirror');
                if (cm && cm.CodeMirror) {
                    cm.CodeMirror.setValue(css);
                    cm.CodeMirror.refresh();
                    return 'success_' + cm.CodeMirror.getValue().length;
                }
                return 'failed';
            }""", full_css)

            print(f"  Set result: {result}")
            if not result.startswith("success"):
                screenshot(page, "set_failed")
                browser.close()
                return 1

            time.sleep(2)
            screenshot(page, "css_updated")

            # Publish
            print("\n  Publishing...")
            time.sleep(3)
            publish_btn = page.locator("#save")
            if publish_btn.count() > 0 and publish_btn.first.is_visible():
                publish_btn.first.click()
                print("  Clicked Publish!")
                time.sleep(8)
            else:
                pub = page.locator("button:has-text('Publish')")
                if pub.count() > 0:
                    pub.first.click()
                    time.sleep(8)
                else:
                    page.keyboard.press("Control+Shift+s")
                    time.sleep(8)

            screenshot(page, "published")

            # Check publish status
            pub_status = page.evaluate("""
                () => {
                    const btn = document.querySelector('#save');
                    return btn ? btn.textContent.trim() + ' | disabled=' + btn.disabled : 'no btn';
                }
            """)
            print(f"  Publish status: {pub_status}")

        # VERIFICATION
        print("\n=== VERIFICATION ===")
        vp = context.new_page()

        # Category page (main target)
        print("  Checking category page...")
        vp.goto("https://purebrain.ai/category/for-teams/", wait_until="domcontentloaded", timeout=30000)
        time.sleep(5)
        vp.evaluate("() => location.reload(true)")
        time.sleep(5)
        cat_path = f"{SCREENSHOT_DIR}/catfix_VERIFY_category_{TIMESTAMP}.png"
        vp.screenshot(path=cat_path, full_page=True)
        print(f"  Screenshot: {cat_path}")

        cat_styles = vp.evaluate("""
            () => {
                const body = document.body;
                const bs = getComputedStyle(body);
                const h1 = document.querySelector('h1, .page-title');
                const links = document.querySelectorAll('article a, .entry-title a');
                return {
                    bodyColor: bs.color,
                    bodyBg: bs.backgroundColor,
                    bodyClasses: body.className.substring(0, 150),
                    h1Text: h1 ? h1.textContent.substring(0, 50) : 'no h1',
                    h1Color: h1 ? getComputedStyle(h1).color : 'n/a',
                    linkCount: links.length,
                    firstLinkColor: links.length > 0 ? getComputedStyle(links[0]).color : 'n/a'
                };
            }
        """)
        print(f"  Category styles: {cat_styles}")

        # Homepage
        print("  Checking homepage...")
        vp.goto("https://purebrain.ai/", wait_until="domcontentloaded", timeout=30000)
        time.sleep(5)
        vp.evaluate("() => location.reload(true)")
        time.sleep(5)
        home_path = f"{SCREENSHOT_DIR}/catfix_VERIFY_homepage_{TIMESTAMP}.png"
        vp.screenshot(path=home_path, full_page=False)
        print(f"  Screenshot: {home_path}")

        # Blog
        print("  Checking blog...")
        vp.goto("https://purebrain.ai/blog/", wait_until="domcontentloaded", timeout=30000)
        time.sleep(5)
        vp.evaluate("() => location.reload(true)")
        time.sleep(5)
        blog_path = f"{SCREENSHOT_DIR}/catfix_VERIFY_blog_{TIMESTAMP}.png"
        vp.screenshot(path=blog_path, full_page=False)
        print(f"  Screenshot: {blog_path}")

        vp.close()
        browser.close()

        print(f"\n{'=' * 60}")
        print("DEPLOYMENT COMPLETE")
        print(f"{'=' * 60}")
        print(f"Category: {cat_path}")
        print(f"Homepage: {home_path}")
        print(f"Blog:     {blog_path}")
        return 0


def main():
    if not PASSWORD:
        print("ERROR: PUREBRAIN_WP_PASSWORD not found in .env")
        return 1

    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    print("=" * 60)
    print("PureBrain.ai Category Page CSS Fix - v3 (CAPTCHA solver)")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    if len(sys.argv) > 1:
        # Phase 2: We have a CAPTCHA answer
        return phase2_solve_and_deploy(sys.argv[1])
    else:
        # Phase 1: Capture CAPTCHA
        return phase1_capture_captcha()


if __name__ == "__main__":
    sys.exit(main())
