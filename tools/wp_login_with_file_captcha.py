#!/usr/bin/env python3
"""
WordPress Login with File-Based CAPTCHA Input
Date: 2026-02-17

This script:
1. Opens browser, navigates to login
2. Fills username/password
3. Saves CAPTCHA screenshot to /tmp/captcha_to_solve.png
4. Waits for /tmp/captcha_answer.txt to appear
5. Reads answer and submits
6. Proceeds with CSS addition

Usage:
1. Run this script
2. It will create /tmp/captcha_to_solve.png
3. Create /tmp/captcha_answer.txt with the CAPTCHA text
4. Script will auto-continue
"""

import time
import sys
import os
from playwright.sync_api import sync_playwright

WP_URL = "https://purebrain.ai/wp-admin"
WP_USER = "Aether"
WP_PASSWORD = "NW2u!JLQ3!Bt$XD$7CWzz5Z@"

CAPTCHA_IMAGE = "/tmp/captcha_to_solve.png"
CAPTCHA_ANSWER_FILE = "/tmp/captcha_answer.txt"

TOOLTIP_CSS = """/* TOOLTIP SYSTEM - 2026-02-17 */
.feature-tooltip {
    position: relative;
    cursor: help;
    border-bottom: 1px dotted rgba(255,255,255,0.4);
}
.feature-tooltip::after {
    content: attr(data-tooltip);
    position: absolute;
    bottom: 125%;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(20, 20, 30, 0.98);
    color: #fff;
    padding: 12px 16px;
    border-radius: 8px;
    font-size: 0.85rem;
    width: 280px;
    opacity: 0;
    visibility: hidden;
    transition: all 0.2s ease;
    z-index: 1000;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    border: 1px solid rgba(42, 147, 193, 0.3);
}
.feature-tooltip:hover::after {
    opacity: 1;
    visibility: visible;
}
.jargon { color: #2a93c1; font-weight: 500; }
.jargon-orange { color: #f1420b; font-weight: 500; }
"""

def wait_for_captcha_answer(timeout=120):
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
            print(f"Waiting for CAPTCHA answer... ({elapsed}s)")
    return None

def main():
    # Clean up old files
    for f in [CAPTCHA_IMAGE, CAPTCHA_ANSWER_FILE]:
        if os.path.exists(f):
            os.remove(f)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        try:
            # Step 1: Navigate to login
            print("=" * 60)
            print("STEP 1: Navigating to WordPress login")
            print("=" * 60)

            page.goto(f"{WP_URL}")
            page.wait_for_load_state('networkidle')
            time.sleep(2)

            # Click username/password option
            username_pass_link = page.locator('text=Log in with username and password')
            if username_pass_link.count() > 0:
                print("Clicking username/password option...")
                username_pass_link.click()
                time.sleep(2)

            # Fill form
            print(f"Filling login as: {WP_USER}")
            page.locator('#user_login').fill(WP_USER)
            page.locator('#user_pass').fill(WP_PASSWORD)

            # Capture CAPTCHA
            page.screenshot(path=CAPTCHA_IMAGE)
            print(f"\n{'*'*60}")
            print(f"CAPTCHA IMAGE SAVED: {CAPTCHA_IMAGE}")
            print(f"{'*'*60}")
            print(f"\nTo continue, create file: {CAPTCHA_ANSWER_FILE}")
            print(f"with the CAPTCHA text as the content.")
            print(f"\nExample: echo 'abc123' > {CAPTCHA_ANSWER_FILE}")
            print(f"\nWaiting up to 120 seconds for answer...")

            # Wait for answer
            captcha_answer = wait_for_captcha_answer(120)

            if not captcha_answer:
                print("TIMEOUT: No CAPTCHA answer provided")
                browser.close()
                return "TIMEOUT"

            print(f"Got CAPTCHA answer: {captcha_answer}")

            # Fill CAPTCHA
            captcha_input = page.locator('input[name="wpsec_captcha_answer"]')
            if captcha_input.count() == 0:
                # Fallback
                text_inputs = page.locator('input[type="text"]').all()
                for inp in text_inputs:
                    inp_id = inp.get_attribute('id') or ''
                    if inp_id != 'user_login':
                        inp.fill(captcha_answer)
                        break
            else:
                captcha_input.fill(captcha_answer)

            page.screenshot(path="/tmp/captcha_filled.png")
            print("CAPTCHA filled, submitting...")

            # Submit
            page.locator('input[value="Log In"]').click()
            page.wait_for_load_state('networkidle')
            time.sleep(3)

            page.screenshot(path="/tmp/after_login.png")
            print(f"After login URL: {page.url}")

            # Check success
            if "wp-admin" in page.url and "login" not in page.url.lower():
                print("SUCCESS: Logged into WordPress!")
            else:
                print("Login may have failed. Check /tmp/after_login.png")
                if "incorrect" in page.content().lower():
                    return "LOGIN_FAILED"

            # Step 2: Add CSS
            print("\n" + "=" * 60)
            print("STEP 2: Adding tooltip CSS to Additional CSS")
            print("=" * 60)

            page.goto("https://purebrain.ai/wp-admin/customize.php?autofocus[section]=custom_css")
            page.wait_for_load_state('networkidle')
            time.sleep(5)

            page.screenshot(path="/tmp/customizer.png")

            if "customize.php" not in page.url:
                print("ERROR: Not on customizer page")
                return "NOT_LOGGED_IN"

            # Add CSS via CodeMirror
            css_area = page.locator('.CodeMirror')
            if css_area.count() > 0:
                css_area.first.click()
                time.sleep(1)
                page.keyboard.press('Control+End')
                page.keyboard.press('Enter')
                page.keyboard.press('Enter')

                for line in TOOLTIP_CSS.split('\n'):
                    page.keyboard.type(line)
                    page.keyboard.press('Enter')

                print("CSS added to editor")

            time.sleep(2)
            page.screenshot(path="/tmp/css_added.png")

            # Publish
            print("Publishing...")
            publish_btn = page.locator('#save')
            if publish_btn.count() > 0:
                publish_btn.click()
                time.sleep(3)

            page.screenshot(path="/tmp/css_published.png")
            print("CSS Published!")

            # View page
            print("\n" + "=" * 60)
            print("STEP 3: Viewing the page")
            print("=" * 60)

            page.goto("https://purebrain.ai/purebrain-3/")
            page.wait_for_load_state('networkidle')
            time.sleep(3)

            page.screenshot(path="/tmp/purebrain3_final.png", full_page=True)
            print("Final page screenshot: /tmp/purebrain3_final.png")

            return "SUCCESS"

        except Exception as e:
            print(f"ERROR: {e}")
            page.screenshot(path="/tmp/error.png")
            return f"ERROR: {e}"

        finally:
            browser.close()

if __name__ == "__main__":
    result = main()
    print(f"\nFinal Result: {result}")
