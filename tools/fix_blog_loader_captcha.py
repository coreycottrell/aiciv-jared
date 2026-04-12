#!/usr/bin/env python3
"""
Fix Blog Loader Color - With CAPTCHA Support
Date: 2026-02-17

This script:
1. Opens browser, navigates to login
2. Fills username/password
3. Saves CAPTCHA screenshot to /tmp/captcha_to_solve.png
4. Waits for /tmp/captcha_answer.txt to appear (or uses command line arg)
5. Reads answer and submits
6. Navigates to Customizer and updates CSS

Usage:
1. Run this script
2. It will create /tmp/captcha_to_solve.png
3. Create /tmp/captcha_answer.txt with the CAPTCHA text OR
4. Pass CAPTCHA as command line arg: python3 fix_blog_loader_captcha.py "captchatext"
"""

import time
import sys
import os
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

WP_URL = "https://purebrain.ai/wp-admin"
WP_CSS_URL = "https://purebrain.ai/wp-admin/customize.php?autofocus[section]=custom_css"
WP_USER = os.getenv('PUREBRAIN_WP_USER', 'Aether')
WP_PASSWORD = os.getenv('PUREBRAIN_WP_PASSWORD', 'NW2u!JLQ3!Bt$XD$7CWzz5Z@')

CAPTCHA_IMAGE = "/tmp/captcha_to_solve.png"
CAPTCHA_ANSWER_FILE = "/tmp/captcha_answer.txt"

CSS_FILE = "/home/jared/projects/AI-CIV/aether/exports/purebrain-complete-styling.css"
SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/sandbox/blog-loader-fix"

def ensure_dirs():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def take_screenshot(page, name):
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    path = f"{SCREENSHOT_DIR}/{timestamp}_{name}.png"
    page.screenshot(path=path)
    print(f"Screenshot: {path}")
    return path

def wait_for_captcha_answer(timeout=300):
    """Wait for the captcha answer file to be created"""
    start = time.time()
    while time.time() - start < timeout:
        if os.path.exists(CAPTCHA_ANSWER_FILE):
            with open(CAPTCHA_ANSWER_FILE, 'r') as f:
                answer = f.read().strip()
            if answer:
                os.remove(CAPTCHA_ANSWER_FILE)  # Clean up
                return answer
        time.sleep(1)
        elapsed = int(time.time() - start)
        if elapsed % 10 == 0:
            print(f"Waiting for CAPTCHA answer... ({elapsed}s / {timeout}s)")
    return None

def load_css():
    with open(CSS_FILE, 'r') as f:
        return f.read()

def main(captcha_arg=None):
    ensure_dirs()

    # Clean up old files
    for f in [CAPTCHA_IMAGE, CAPTCHA_ANSWER_FILE]:
        if os.path.exists(f):
            os.remove(f)

    css_content = load_css()
    print(f"Loaded CSS: {len(css_content)} characters")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        try:
            # Step 1: Navigate to login
            print("=" * 60)
            print("STEP 1: Navigating to WordPress login")
            print("=" * 60)

            page.goto(WP_URL, wait_until='domcontentloaded', timeout=60000)
            time.sleep(3)
            take_screenshot(page, "01_login_page")

            # Click username/password option
            username_pass_link = page.query_selector('text="Log in with username and password"')
            if username_pass_link:
                print("Clicking username/password option...")
                username_pass_link.click()
                time.sleep(2)

            # Fill form
            print(f"Filling login as: {WP_USER}")
            page.fill('#user_login', WP_USER)
            page.fill('#user_pass', WP_PASSWORD)

            # Check for CAPTCHA
            captcha_input = page.query_selector('input[name="captcha_code"]')
            if not captcha_input:
                # Try other names
                captcha_selectors = [
                    'input[name="wpsec_captcha_answer"]',
                    'input[type="text"]:not(#user_login)',
                ]
                for sel in captcha_selectors:
                    captcha_input = page.query_selector(sel)
                    if captcha_input:
                        break

            if captcha_input:
                # Capture CAPTCHA screenshot
                captcha_path = take_screenshot(page, "02_captcha")

                print(f"\n{'*'*60}")
                print(f"CAPTCHA DETECTED!")
                print(f"Screenshot saved: {captcha_path}")
                print(f"Also saved to: {CAPTCHA_IMAGE}")
                print(f"{'*'*60}")

                # Copy to /tmp for easy access
                page.screenshot(path=CAPTCHA_IMAGE)

                if captcha_arg:
                    captcha_answer = captcha_arg
                    print(f"Using command line CAPTCHA: {captcha_answer}")
                else:
                    print(f"\nTo continue, create file: {CAPTCHA_ANSWER_FILE}")
                    print(f"with the CAPTCHA text as the content.")
                    print(f"\nExample: echo 'abc123' > {CAPTCHA_ANSWER_FILE}")
                    print(f"\nWaiting up to 300 seconds for answer...")

                    captcha_answer = wait_for_captcha_answer(300)

                if not captcha_answer:
                    print("TIMEOUT: No CAPTCHA answer provided")
                    return "TIMEOUT"

                print(f"Using CAPTCHA answer: {captcha_answer}")

                # Fill CAPTCHA - find all text inputs except user_login
                text_inputs = page.query_selector_all('input[type="text"]')
                for inp in text_inputs:
                    inp_id = inp.get_attribute('id') or ''
                    if inp_id != 'user_login':
                        inp.fill(captcha_answer)
                        break

            take_screenshot(page, "03_credentials_filled")

            # Submit login
            print("Submitting login...")
            page.click('#wp-submit')
            page.wait_for_load_state('load', timeout=60000)
            time.sleep(5)

            take_screenshot(page, "04_after_login")
            print(f"After login URL: {page.url}")

            # Check for login errors
            error_box = page.query_selector('#login_error')
            if error_box:
                error_text = error_box.inner_text()
                print(f"LOGIN ERROR: {error_text}")
                if "CAPTCHA" in error_text.upper():
                    print("\n*** CAPTCHA was incorrect. Need to retry. ***")
                return "LOGIN_FAILED"

            # Check success
            if "wp-admin" not in page.url or "login" in page.url.lower():
                print("Login may have failed")
                return "LOGIN_FAILED"

            print("SUCCESS: Logged into WordPress!")

            # Step 2: Navigate to Customizer
            print("\n" + "=" * 60)
            print("STEP 2: Navigating to Additional CSS")
            print("=" * 60)

            page.goto(WP_CSS_URL, wait_until='load', timeout=90000)
            time.sleep(8)  # Customizer needs time

            take_screenshot(page, "05_customizer_loading")

            # Wait for customizer
            try:
                page.wait_for_selector('#customize-controls', state='visible', timeout=30000)
            except:
                print("Warning: customize-controls not visible")

            time.sleep(5)
            take_screenshot(page, "06_customizer_loaded")

            # Step 3: Update CSS
            print("\n" + "=" * 60)
            print("STEP 3: Updating CSS")
            print("=" * 60)

            codemirror = page.query_selector('.CodeMirror')
            if codemirror:
                print("Found CodeMirror editor")
                codemirror.click()
                time.sleep(1)

                # Use JavaScript to replace content
                print("Replacing CSS content...")
                page.evaluate(f'''() => {{
                    const cm = document.querySelector('.CodeMirror').CodeMirror;
                    cm.setValue({repr(css_content)});
                }}''')
                time.sleep(2)
                take_screenshot(page, "07_css_updated")
                print("CSS content updated!")
            else:
                print("ERROR: CodeMirror editor not found!")
                take_screenshot(page, "07_error_no_editor")
                return "EDITOR_NOT_FOUND"

            # Step 4: Publish
            print("\n" + "=" * 60)
            print("STEP 4: Publishing")
            print("=" * 60)

            time.sleep(3)
            publish_btn = page.query_selector('#save')
            if publish_btn and publish_btn.is_visible():
                take_screenshot(page, "08_before_publish")
                publish_btn.click()
                print("Clicked Publish button")
                time.sleep(5)
                take_screenshot(page, "09_after_publish")
                print("CSS Published!")
            else:
                print("Publish button not found, trying keyboard shortcut")
                page.keyboard.press('Control+Shift+s')
                time.sleep(5)
                take_screenshot(page, "09_after_keyboard_save")

            # Step 5: Verify - visit blog page
            print("\n" + "=" * 60)
            print("STEP 5: Verifying on blog page")
            print("=" * 60)

            page.goto("https://purebrain.ai/blog", wait_until='domcontentloaded', timeout=60000)
            # Capture quickly to see loader
            take_screenshot(page, "10_blog_initial")

            time.sleep(0.5)
            take_screenshot(page, "10b_blog_loading")

            # Wait for full load
            page.wait_for_load_state('load', timeout=60000)
            time.sleep(3)
            take_screenshot(page, "11_blog_loaded")

            print("\nSUCCESS! CSS updated with blog loader fix.")
            print(f"Verify visually: {SCREENSHOT_DIR}/")

            return "SUCCESS"

        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            take_screenshot(page, "error_exception")
            return f"ERROR: {e}"

        finally:
            browser.close()

if __name__ == "__main__":
    captcha = sys.argv[1] if len(sys.argv) > 1 else None
    result = main(captcha_arg=captcha)
    print(f"\nFinal Result: {result}")
    sys.exit(0 if result == "SUCCESS" else 1)
