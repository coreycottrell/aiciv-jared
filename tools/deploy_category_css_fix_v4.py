#!/usr/bin/env python3
"""
Deploy Category Page CSS Fix to purebrain.ai - v4
Single browser session with CAPTCHA solving via file exchange.

The browser stays open while waiting for CAPTCHA answer.
Write the answer to /tmp/catfix_captcha_answer.txt to continue.

Usage:
  python3 deploy_category_css_fix_v4.py
  # Then in another terminal/tool: write CAPTCHA answer to the file
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
CAPTCHA_ANSWER_FILE = "/tmp/catfix_captcha_answer.txt"
CAPTCHA_SCREENSHOT = f"{SCREENSHOT_DIR}/catfix_CAPTCHA_{TIMESTAMP}.png"

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


def main():
    if not PASSWORD:
        print("ERROR: PUREBRAIN_WP_PASSWORD not found in .env")
        return 1

    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    # Clean up old answer file
    if os.path.exists(CAPTCHA_ANSWER_FILE):
        os.remove(CAPTCHA_ANSWER_FILE)

    print("=" * 60)
    print("PureBrain.ai Category Page CSS Fix - v4")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        )
        page = context.new_page()

        # ============ STEP 1: LOAD LOGIN PAGE ============
        print("\n[Step 1] Loading login page...")
        page.goto(WP_ADMIN_URL, wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)

        # Click "Log in with username and password"
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

        # ============ STEP 2: SAVE CAPTCHA ============
        print("\n[Step 2] Saving CAPTCHA screenshot...")
        page.screenshot(path=CAPTCHA_SCREENSHOT)
        print(f"  CAPTCHA screenshot: {CAPTCHA_SCREENSHOT}")
        print(f"  Waiting for answer in: {CAPTCHA_ANSWER_FILE}")
        print("  Write CAPTCHA text to that file to continue (timeout: 180s)...")

        # ============ STEP 3: WAIT FOR CAPTCHA ANSWER ============
        start = time.time()
        captcha_answer = None
        while time.time() - start < 180:
            if os.path.exists(CAPTCHA_ANSWER_FILE):
                with open(CAPTCHA_ANSWER_FILE, 'r') as f:
                    captcha_answer = f.read().strip()
                if captcha_answer:
                    print(f"  Got CAPTCHA answer: '{captcha_answer}'")
                    os.remove(CAPTCHA_ANSWER_FILE)
                    break
            time.sleep(1)

        if not captcha_answer:
            print("  TIMEOUT: No CAPTCHA answer in 180 seconds")
            browser.close()
            return 1

        # ============ STEP 4: FILL CAPTCHA AND LOGIN ============
        print(f"\n[Step 4] Filling CAPTCHA: '{captcha_answer}'")

        # Find the CAPTCHA input field
        captcha_filled = False
        all_text_inputs = page.locator("input[type='text']")
        for i in range(all_text_inputs.count()):
            inp = all_text_inputs.nth(i)
            name = inp.get_attribute("name") or ""
            id_attr = inp.get_attribute("id") or ""
            if id_attr != "user_login" and name != "log":
                inp.fill(captcha_answer)
                print(f"  Filled CAPTCHA in: name='{name}', id='{id_attr}'")
                captcha_filled = True
                break

        if not captcha_filled:
            print("  WARNING: Could not find CAPTCHA input!")

        time.sleep(1)

        # Submit login
        print("  Submitting login...")
        page.locator("#wp-submit").click()
        page.wait_for_load_state("load", timeout=60000)
        time.sleep(5)

        login_screenshot = f"{SCREENSHOT_DIR}/catfix_login_result_{TIMESTAMP}.png"
        page.screenshot(path=login_screenshot)
        print(f"  Screenshot: {login_screenshot}")

        current_url = page.url
        print(f"  Current URL: {current_url}")

        if "wp-login" in current_url:
            print("  LOGIN FAILED!")
            error_el = page.locator("#login_error")
            if error_el.count() > 0:
                print(f"  Error: {error_el.first.inner_text()}")
            browser.close()
            return 1

        print("  LOGIN SUCCESS!")

        # ============ STEP 5: NAVIGATE TO ADDITIONAL CSS ============
        print("\n[Step 5] Navigating to Additional CSS...")
        page.goto(WP_CSS_URL, wait_until="domcontentloaded", timeout=90000)
        print("  Waiting for Customizer (15s)...")
        time.sleep(15)

        customizer_screenshot = f"{SCREENSHOT_DIR}/catfix_customizer_{TIMESTAMP}.png"
        page.screenshot(path=customizer_screenshot)
        print(f"  Screenshot: {customizer_screenshot}")

        # Wait for CodeMirror
        try:
            page.wait_for_selector('.CodeMirror', state='visible', timeout=30000)
            print("  CodeMirror found!")
        except:
            print("  WARNING: CodeMirror not visible after 30s")

        time.sleep(3)

        # ============ STEP 6: GET CURRENT CSS ============
        print("\n[Step 6] Getting current CSS...")
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
            browser.close()
            return 1

        print(f"  Current CSS: {len(current_css)} characters ({len(current_css.splitlines())} lines)")

        # ============ STEP 7: CHECK + APPEND ============
        if DUPLICATE_CHECK in current_css:
            print(f"\n  '{DUPLICATE_CHECK}' already present!")
            print("  CSS fix already deployed. Skipping to verification.")
        else:
            print(f"\n[Step 7] Appending category fix CSS...")
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
                print("  ERROR: Failed to set CSS!")
                browser.close()
                return 1

            time.sleep(2)
            css_screenshot = f"{SCREENSHOT_DIR}/catfix_css_updated_{TIMESTAMP}.png"
            page.screenshot(path=css_screenshot)
            print(f"  Screenshot: {css_screenshot}")

            # ============ STEP 8: PUBLISH ============
            print("\n[Step 8] Publishing...")
            time.sleep(3)
            publish_btn = page.locator("#save")
            if publish_btn.count() > 0 and publish_btn.first.is_visible():
                publish_btn.first.click()
                print("  Clicked Publish!")
            else:
                pub = page.locator("button:has-text('Publish')")
                if pub.count() > 0:
                    pub.first.click()
                else:
                    page.keyboard.press("Control+Shift+s")
            time.sleep(8)

            pub_screenshot = f"{SCREENSHOT_DIR}/catfix_published_{TIMESTAMP}.png"
            page.screenshot(path=pub_screenshot)
            print(f"  Screenshot: {pub_screenshot}")

            pub_status = page.evaluate("""
                () => {
                    const btn = document.querySelector('#save');
                    return btn ? btn.textContent.trim() + ' | disabled=' + btn.disabled : 'no btn';
                }
            """)
            print(f"  Publish status: {pub_status}")

        # ============ STEP 9: VERIFY ============
        print("\n[Step 9] Verification...")
        vp = context.new_page()

        # Category page
        print("  Checking category page: /category/for-teams/")
        vp.goto("https://purebrain.ai/category/for-teams/", wait_until="domcontentloaded", timeout=30000)
        time.sleep(5)
        vp.evaluate("() => location.reload(true)")
        time.sleep(5)
        cat_path = f"{SCREENSHOT_DIR}/catfix_FINAL_category_{TIMESTAMP}.png"
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
                    h1Text: h1 ? h1.textContent.substring(0, 60) : 'no h1',
                    h1Color: h1 ? getComputedStyle(h1).color : 'n/a',
                    linkCount: links.length,
                    firstLinkColor: links.length > 0 ? getComputedStyle(links[0]).color : 'n/a'
                };
            }
        """)
        print(f"  Styles: {cat_styles}")

        # Homepage
        print("  Checking homepage...")
        vp.goto("https://purebrain.ai/", wait_until="domcontentloaded", timeout=30000)
        time.sleep(5)
        vp.evaluate("() => location.reload(true)")
        time.sleep(5)
        home_path = f"{SCREENSHOT_DIR}/catfix_FINAL_homepage_{TIMESTAMP}.png"
        vp.screenshot(path=home_path, full_page=False)
        print(f"  Screenshot: {home_path}")

        # Blog
        print("  Checking blog...")
        vp.goto("https://purebrain.ai/blog/", wait_until="domcontentloaded", timeout=30000)
        time.sleep(5)
        vp.evaluate("() => location.reload(true)")
        time.sleep(5)
        blog_path = f"{SCREENSHOT_DIR}/catfix_FINAL_blog_{TIMESTAMP}.png"
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


if __name__ == "__main__":
    sys.exit(main())
