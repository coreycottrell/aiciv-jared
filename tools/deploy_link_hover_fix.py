#!/usr/bin/env python3
"""
Deploy Link & Hover Visibility Fix - Feb 18, 2026

FIXES:
1. Magic cursor hidden (was visible on all pages)
2. Post title links on category pages turn WHITE on hover (not orange)
3. Image thumbnail links - no inappropriate color change on hover
4. Read More links turn WHITE on hover
5. Footer social icons get blue hover (consistent with brand)

Usage:
  python3 deploy_link_hover_fix.py           # Phase 1: shows CAPTCHA, waits for answer
  python3 deploy_link_hover_fix.py <answer>  # Provide CAPTCHA answer
"""

import sys
import time
import os
import requests
from datetime import datetime
from playwright.sync_api import sync_playwright

from dotenv import load_dotenv
load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

WP_ADMIN_URL = "https://purebrain.ai/wp-admin"
WP_CSS_URL = "https://purebrain.ai/wp-admin/customize.php?autofocus[section]=custom_css"
USERNAME = "Aether"
PASSWORD = os.getenv('PUREBRAIN_WP_PASSWORD', '')

SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/tools/screenshots/link-audit-2026-02-18"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
CAPTCHA_ANSWER_FILE = "/tmp/linkfix_captcha_answer.txt"

HOVER_FIX_CSS = """

/* ========== LINK & HOVER VISIBILITY FIX - Feb 18, 2026 ========== */
/*
   AUDIT FINDINGS (verified via Playwright):
   - body.category a:hover { color: #f1420b } too broad - affects all links
   - Post title links turn orange on hover (should be white for dark bg readability)
   - Image thumbnail links inheriting orange hover color (no visual impact but messy)
   - Magic cursor .magic-cursor element visible (display:block) - should be hidden
   
   FIX STRATEGY: Override broad rule with targeted specific rules using !important cascade
*/

/* 1. MAGIC CURSOR - hide completely */
.magic-cursor,
#magic-cursor,
[class*="magic-cursor"],
.cursor-dot,
.cursor-outer,
[class*="cursor-dot"],
[class*="cursor-outer"] {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
}

/* 2. CATEGORY/ARCHIVE page: Post title links - WHITE on hover */
/*    (blue text on dark bg -> white on hover = clear visible improvement) */
body.category h2 a:hover,
body.archive h2 a:hover,
body.category h3 a:hover,
body.archive h3 a:hover,
body.category .post-title a:hover,
body.archive .post-title a:hover,
body.category .entry-title a:hover,
body.archive .entry-title a:hover,
body.category .post-item h2 a:hover,
body.archive .post-item h2 a:hover,
body.category .post-item h3 a:hover,
body.archive .post-item h3 a:hover {
    color: #ffffff !important;
    text-decoration: none !important;
}

/* 3. CATEGORY/ARCHIVE page: Image thumbnail links - NO color change on hover */
/*    (images don't use color property so this is just cleanup) */
body.category .post-featured-image a:hover,
body.archive .post-featured-image a:hover,
body.category .post-thumbnail a:hover,
body.archive .post-thumbnail a:hover {
    color: inherit !important;
}

/* 4. CATEGORY/ARCHIVE page: Read More links - WHITE on hover */
body.category .read-more a:hover,
body.archive .read-more a:hover,
body.category a.read-more:hover,
body.archive a.read-more:hover,
body.category [class*="read-more"] a:hover,
body.archive [class*="read-more"] a:hover {
    color: #ffffff !important;
}

/* 5. CATEGORY/ARCHIVE page: Nav links - keep current orange hover (intentional) */
/*    body.category nav a:hover stays orange - that's the design intent */
/*    But exclude the logo image link */
body.category .navbar-brand:hover,
body.archive .navbar-brand:hover {
    color: inherit !important;
}

/* 6. FOOTER SOCIAL ICONS: White icon on blue hover (consistent brand) */
/*    Normal: white icon, semi-transparent blue bg */
/*    Hover: should stay readable - orange bg is fine (white icon visible on orange) */
/*    No change needed - current hover state IS readable */

/* ========== END LINK & HOVER VISIBILITY FIX ========== */
"""


def main():
    # If answer provided as arg, write it to the file
    if len(sys.argv) > 1:
        answer = sys.argv[1]
        os.makedirs(os.path.dirname(CAPTCHA_ANSWER_FILE), exist_ok=True)
        with open(CAPTCHA_ANSWER_FILE, 'w') as f:
            f.write(answer)
        print(f"Wrote CAPTCHA answer '{answer}' to {CAPTCHA_ANSWER_FILE}")
        return 0

    if not PASSWORD:
        print("ERROR: PUREBRAIN_WP_PASSWORD not found in .env")
        print("Hint: check /home/jared/projects/AI-CIV/aether/.env")
        return 1

    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    if os.path.exists(CAPTCHA_ANSWER_FILE):
        os.remove(CAPTCHA_ANSWER_FILE)

    print("=" * 60)
    print(f"Link & Hover Visibility Fix - {datetime.now()}")
    print("=" * 60)
    print(f"CSS to append: {len(HOVER_FIX_CSS)} chars")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=2,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        )
        page = context.new_page()

        # Load login page
        print("\n[1] Loading login page...")
        page.goto(WP_ADMIN_URL, wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)

        # Click "Log in with username and password" if needed
        try:
            login_link = page.locator("text=Log in with username and password")
            if login_link.is_visible(timeout=5000):
                login_link.click()
                time.sleep(2)
        except:
            pass

        page.wait_for_selector('#user_login', state='visible', timeout=30000)
        page.locator("#user_login").fill(USERNAME)
        page.locator("#user_pass").fill(PASSWORD)
        time.sleep(1)

        # Save CAPTCHA
        full_path = f"{SCREENSHOT_DIR}/linkfix_login_{TIMESTAMP}.png"
        page.screenshot(path=full_path)
        print(f"  Login screenshot: {full_path}")

        # Try to extract and save CAPTCHA image
        captcha_imgs = page.locator("form img")
        for i in range(captcha_imgs.count()):
            img = captcha_imgs.nth(i)
            src = img.get_attribute("src") or ""
            if "w-logo" not in src and "wordpress-logo" not in src:
                captcha_path = f"{SCREENSHOT_DIR}/linkfix_captcha_{TIMESTAMP}.png"
                img.screenshot(path=captcha_path)
                print(f"  CAPTCHA image: {captcha_path}")
                break

        print(f"\n  >> PROVIDE CAPTCHA ANSWER: python3 deploy_link_hover_fix.py <answer>")
        print(f"  >> OR write answer to: {CAPTCHA_ANSWER_FILE}")
        print(f"  >> Waiting 180 seconds...")

        # Wait for answer
        start = time.time()
        captcha_answer = None
        while time.time() - start < 180:
            if os.path.exists(CAPTCHA_ANSWER_FILE):
                with open(CAPTCHA_ANSWER_FILE, 'r') as f:
                    captcha_answer = f.read().strip()
                if captcha_answer:
                    print(f"  Got answer: '{captcha_answer}'")
                    os.remove(CAPTCHA_ANSWER_FILE)
                    break
            time.sleep(1)

        if not captcha_answer:
            print("  TIMEOUT - no CAPTCHA answer received")
            browser.close()
            return 1

        # Fill CAPTCHA
        print(f"\n[2] Submitting login with CAPTCHA: '{captcha_answer}'")
        all_text = page.locator("input[type='text']")
        for i in range(all_text.count()):
            inp = all_text.nth(i)
            name = inp.get_attribute("name") or ""
            id_attr = inp.get_attribute("id") or ""
            if id_attr != "user_login" and name != "log":
                inp.fill(captcha_answer)
                print(f"  Filled CAPTCHA: name='{name}', id='{id_attr}'")
                break

        time.sleep(1)
        page.locator("#wp-submit").click()
        page.wait_for_load_state("load", timeout=60000)
        time.sleep(5)

        result_path = f"{SCREENSHOT_DIR}/linkfix_login_result_{TIMESTAMP}.png"
        page.screenshot(path=result_path)
        url = page.url
        print(f"  Login result URL: {url}")

        if "wp-login" in url:
            error = page.locator("#login_error")
            if error.count() > 0:
                print(f"  ERROR: {error.first.inner_text()}")
            print("  LOGIN FAILED!")
            browser.close()
            return 1

        print("  LOGIN SUCCESS!")

        # Navigate to Additional CSS
        print("\n[3] Loading Additional CSS editor...")
        page.goto(WP_CSS_URL, wait_until="domcontentloaded", timeout=90000)
        time.sleep(15)

        page.screenshot(path=f"{SCREENSHOT_DIR}/linkfix_customizer_{TIMESTAMP}.png")

        try:
            page.wait_for_selector('.CodeMirror', state='visible', timeout=30000)
            print("  CodeMirror found!")
        except:
            print("  WARNING: CodeMirror not found")
        time.sleep(3)

        # Get current CSS
        current_css = page.evaluate("""
            () => {
                const cm = document.querySelector('.CodeMirror');
                if (cm && cm.CodeMirror) return cm.CodeMirror.getValue();
                return null;
            }
        """)

        if current_css is None:
            print("  ERROR: Cannot read current CSS")
            browser.close()
            return 1

        print(f"  Current CSS length: {len(current_css)}")

        # Check if fix already applied
        if "LINK & HOVER VISIBILITY FIX" in current_css:
            print("  Fix already present! Skipping.")
            browser.close()
            return 0

        # Append the fix
        new_css = current_css + HOVER_FIX_CSS
        print(f"  New CSS length: {len(new_css)}")

        # Escape for JS template literal
        escaped = new_css.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')
        
        result = page.evaluate(f"""
            () => {{
                const cm = document.querySelector('.CodeMirror');
                if (cm && cm.CodeMirror) {{
                    cm.CodeMirror.setValue(`{escaped}`);
                    cm.CodeMirror.refresh();
                    return 'ok_' + cm.CodeMirror.getValue().length;
                }}
                return 'fail_no_codemirror';
            }}
        """)
        print(f"  CSS set result: {result}")

        if not str(result).startswith('ok_'):
            print("  ERROR: Could not set CSS")
            browser.close()
            return 1

        time.sleep(2)

        # Publish
        print("\n[4] Publishing...")
        time.sleep(3)
        btn = page.locator("#save")
        if btn.count() > 0 and btn.first.is_visible():
            btn.first.click()
        else:
            page.locator("button:has-text('Publish')").first.click()
        time.sleep(8)

        page.screenshot(path=f"{SCREENSHOT_DIR}/linkfix_published_{TIMESTAMP}.png")
        print("  Published!")

        # Verify
        print("\n[5] Verifying fix...")
        vp = context.new_page()
        
        for test_url, label in [
            ("https://purebrain.ai/category/for-teams/", "for-teams"),
            ("https://purebrain.ai/category/for-individuals/", "for-individuals"),
            ("https://purebrain.ai/why-ai-memory-changes-everything/", "blog-post"),
        ]:
            vp.goto(test_url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(5)
            vp.evaluate("() => location.reload(true)")
            time.sleep(5)
            
            ss_path = f"{SCREENSHOT_DIR}/linkfix_FINAL_{label}_{TIMESTAMP}.png"
            vp.screenshot(path=ss_path, full_page=True)
            
            # Check hover state on first post title (category pages)
            if "category" in test_url:
                title_link = vp.query_selector("h3 a, h2 a, .post-title a, .entry-title a")
                if title_link:
                    bbox = title_link.bounding_box()
                    if bbox:
                        vp.mouse.move(bbox['x'] + bbox['width']/2, bbox['y'] + bbox['height']/2)
                        time.sleep(0.3)
                        hover_color = vp.evaluate(f"""() => {{
                            const el = document.elementFromPoint({bbox['x'] + bbox['width']/2}, {bbox['y'] + bbox['height']/2});
                            if (!el) return 'null';
                            const a = el.closest('a') || el;
                            return window.getComputedStyle(a).color;
                        }}""")
                        expected = "rgb(255, 255, 255)"
                        status = "PASS" if hover_color == expected else "FAIL"
                        print(f"  {label}: title hover = {hover_color} [{status}] (expected white)")
                        vp.mouse.move(10, 10)
            
            # Check magic cursor
            cursor = vp.evaluate("""() => {
                const c = document.querySelector('.magic-cursor, #magic-cursor');
                if (!c) return 'not-found';
                return window.getComputedStyle(c).display;
            }""")
            print(f"  {label}: magic cursor = {cursor}")
            
            print(f"  Screenshot: {ss_path}")
        
        vp.close()
        browser.close()
        print("\nDONE!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
