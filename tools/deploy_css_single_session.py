#!/usr/bin/env python3
"""
Deploy CSS - Single session with CAPTCHA answer from file.
Phase 1: Load login, save CAPTCHA, wait for answer file
Phase 2: Fill CAPTCHA, login, deploy CSS, verify

Usage:
  python3 deploy_css_single_session.py           # Phase 1: saves CAPTCHA
  # Write answer to /tmp/purebrain-css-fix-2026-02-18/captcha_answer.txt
  # Script continues automatically when file appears
"""

import sys
import time
import os
import json
from playwright.sync_api import sync_playwright

WP_URL = "https://purebrain.ai"
USERNAME = "Aether"
PASSWORD = "NW2u!JLQ3!Bt$XD$7CWzz5Z@"
CSS_FILE = "/home/jared/projects/AI-CIV/aether/exports/purebrain-complete-styling.css"
SCREENSHOT_DIR = "/tmp/purebrain-css-fix-2026-02-18"
CAPTCHA_IMG = f"{SCREENSHOT_DIR}/captcha_current.png"
CAPTCHA_ANSWER_FILE = f"{SCREENSHOT_DIR}/captcha_answer.txt"


def main():
    # If answer provided as arg, write it to the file
    if len(sys.argv) > 1:
        answer = sys.argv[1]
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        with open(CAPTCHA_ANSWER_FILE, 'w') as f:
            f.write(answer)
        print(f"Wrote CAPTCHA answer '{answer}' to {CAPTCHA_ANSWER_FILE}")
        return 0

    with open(CSS_FILE, 'r') as f:
        new_css = f.read()
    print(f"CSS loaded: {len(new_css)} chars")
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    # Clean up old answer file
    if os.path.exists(CAPTCHA_ANSWER_FILE):
        os.remove(CAPTCHA_ANSWER_FILE)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        # === PHASE 1: Get to login form ===
        print("\n=== PHASE 1: Loading login page ===")
        page.goto(f"{WP_URL}/wp-admin", wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)

        # Click "Log in with username and password"
        try:
            login_link = page.locator("text=Log in with username and password")
            if login_link.is_visible(timeout=3000):
                login_link.click()
                time.sleep(2)
        except:
            pass

        # Fill credentials
        page.locator("input#user_login").fill(USERNAME)
        page.locator("input#user_pass").fill(PASSWORD)

        # Save CAPTCHA screenshot
        page.screenshot(path=CAPTCHA_IMG)
        print(f"CAPTCHA saved to: {CAPTCHA_IMG}")
        print(f"Waiting for answer in: {CAPTCHA_ANSWER_FILE}")
        print("Write the CAPTCHA text to that file to continue...")

        # Wait for answer file (poll every 2 seconds, timeout 120s)
        start = time.time()
        captcha_answer = None
        while time.time() - start < 120:
            if os.path.exists(CAPTCHA_ANSWER_FILE):
                with open(CAPTCHA_ANSWER_FILE, 'r') as f:
                    captcha_answer = f.read().strip()
                if captcha_answer:
                    print(f"Got CAPTCHA answer: {captcha_answer}")
                    os.remove(CAPTCHA_ANSWER_FILE)
                    break
            time.sleep(2)

        if not captcha_answer:
            print("TIMEOUT: No CAPTCHA answer received in 120 seconds")
            browser.close()
            return 1

        # === PHASE 2: Fill CAPTCHA and login ===
        print("\n=== PHASE 2: Logging in ===")

        # Find and fill CAPTCHA field
        all_text_inputs = page.locator("input[type='text']")
        captcha_filled = False
        for i in range(all_text_inputs.count()):
            inp = all_text_inputs.nth(i)
            name = inp.get_attribute("name") or ""
            id_attr = inp.get_attribute("id") or ""
            if "user_login" not in id_attr and name != "log":
                inp.fill(captcha_answer)
                print(f"Filled CAPTCHA field: name='{name}', id='{id_attr}'")
                captcha_filled = True
                break

        if not captcha_filled:
            print("WARNING: Could not find CAPTCHA field!")

        time.sleep(1)

        # Submit
        print("Submitting login...")
        page.locator("input#wp-submit, input[type='submit']").first.click()
        time.sleep(5)

        page.screenshot(path=f"{SCREENSHOT_DIR}/login_result.png")
        current_url = page.url
        print(f"After login URL: {current_url}")

        if "wp-login" in current_url:
            error_el = page.locator("#login_error")
            if error_el.count() > 0:
                print(f"Login ERROR: {error_el.first.inner_text()}")
            browser.close()
            return 1

        print("LOGIN SUCCESS!")

        # === PHASE 3: Deploy CSS ===
        print("\n=== PHASE 3: Deploying CSS ===")
        page.goto(
            f"{WP_URL}/wp-admin/customize.php?autofocus[section]=custom_css",
            wait_until="domcontentloaded",
            timeout=60000
        )
        time.sleep(12)

        page.screenshot(path=f"{SCREENSHOT_DIR}/customizer_loaded.png")

        # Replace CSS
        escaped_css = new_css.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')

        result = page.evaluate(f"""
            () => {{
                const cm = document.querySelector('.CodeMirror');
                if (cm && cm.CodeMirror) {{
                    cm.CodeMirror.setValue(`{escaped_css}`);
                    cm.CodeMirror.refresh();
                    return 'codemirror_' + cm.CodeMirror.getValue().length;
                }}
                if (typeof wp !== 'undefined' && wp.customize) {{
                    try {{
                        const keys = Object.keys(wp.customize.settings.settings);
                        const cssKey = keys.find(k => k.includes('custom_css'));
                        if (cssKey) {{
                            wp.customize(cssKey).set(`{escaped_css}`);
                            return 'wp_customize_' + cssKey;
                        }}
                    }} catch(e) {{
                        return 'error_' + e.message;
                    }}
                }}
                return 'failed';
            }}
        """)
        print(f"CSS update: {result}")

        if 'failed' in str(result):
            page.screenshot(path=f"{SCREENSHOT_DIR}/css_failed.png")
            browser.close()
            return 1

        time.sleep(3)

        # Publish
        print("Publishing...")
        publish_btn = page.locator("#save")
        if publish_btn.count() > 0:
            publish_btn.first.click()
        else:
            page.locator("button:has-text('Publish')").first.click()
        time.sleep(5)

        page.screenshot(path=f"{SCREENSHOT_DIR}/published.png")
        print("Published!")

        # === PHASE 4: Verify ===
        print("\n=== PHASE 4: Verification ===")
        vp = context.new_page()

        # Homepage
        vp.goto(f"{WP_URL}", wait_until="domcontentloaded", timeout=30000)
        time.sleep(8)
        vp.evaluate("() => location.reload(true)")
        time.sleep(5)
        vp.screenshot(path=f"{SCREENSHOT_DIR}/FINAL_homepage.png", full_page=False)
        body_bg = vp.evaluate("() => getComputedStyle(document.body).backgroundColor")
        print(f"Homepage body bg: {body_bg}")

        # Blog
        vp.goto(f"{WP_URL}/blog/", wait_until="domcontentloaded", timeout=30000)
        time.sleep(5)
        vp.screenshot(path=f"{SCREENSHOT_DIR}/FINAL_blog.png", full_page=False)

        # Blog post
        vp.goto(f"{WP_URL}/why-ai-memory-changes-everything/", wait_until="domcontentloaded", timeout=30000)
        time.sleep(5)
        vp.screenshot(path=f"{SCREENSHOT_DIR}/FINAL_blogpost.png", full_page=False)
        social = vp.evaluate("""
            () => {
                const c = document.querySelectorAll('.post-social-sharing');
                return Array.from(c).map(e => ({
                    display: getComputedStyle(e).display,
                    visibility: getComputedStyle(e).visibility,
                    height: getComputedStyle(e).height
                }));
            }
        """)
        print(f"Social sharing: {json.dumps(social)}")

        vp.evaluate("() => window.scrollTo(0, document.body.scrollHeight * 0.7)")
        time.sleep(2)
        vp.screenshot(path=f"{SCREENSHOT_DIR}/FINAL_blogpost_scrolled.png", full_page=False)

        browser.close()
        print(f"\nDONE! Screenshots in: {SCREENSHOT_DIR}/")
        return 0


if __name__ == "__main__":
    sys.exit(main())
