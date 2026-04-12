#!/usr/bin/env python3
"""
Interactive WordPress Login with CAPTCHA
Date: 2026-02-17

This script will:
1. Navigate to login page
2. Show the CAPTCHA in the terminal (as path to image)
3. Wait for CAPTCHA input
4. Complete login
5. Then proceed with adding CSS
"""

import time
import sys
from playwright.sync_api import sync_playwright

# Credentials (updated 2026-02-17)
WP_URL = "https://purebrain.ai/wp-admin"
WP_USER = "Aether"
WP_PASSWORD = "NW2u!JLQ3!Bt$XD$7CWzz5Z@"

# The tooltip CSS to add
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

def interactive_login_and_css():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        try:
            # Step 1: Go to login
            print("Step 1: Navigating to WordPress login...")
            page.goto(f"{WP_URL}")
            page.wait_for_load_state('networkidle')
            time.sleep(2)

            # Click "Log in with username and password" if present
            username_pass_link = page.locator('text=Log in with username and password')
            if username_pass_link.count() > 0:
                print("Clicking username/password option...")
                username_pass_link.click()
                time.sleep(2)

            # Fill username and password
            page.locator('#user_login').fill(WP_USER)
            page.locator('#user_pass').fill(WP_PASSWORD)

            # Capture the page with CAPTCHA
            captcha_path = "/tmp/captcha_to_solve.png"
            page.screenshot(path=captcha_path)
            print(f"\n{'='*60}")
            print(f"CAPTCHA SCREENSHOT SAVED: {captcha_path}")
            print(f"{'='*60}")
            print("\nPlease look at the CAPTCHA image and enter the text.")
            print("The image is at: " + captcha_path)

            # Wait for user input
            captcha_solution = input("\nEnter CAPTCHA text: ").strip()

            if not captcha_solution:
                print("No CAPTCHA entered. Exiting.")
                browser.close()
                return "NO_CAPTCHA"

            # Fill CAPTCHA
            captcha_input = page.locator('input[name="wpsec_captcha_answer"]')
            if captcha_input.count() > 0:
                captcha_input.fill(captcha_solution)
            else:
                # Try to find any text input that's not username/password
                text_inputs = page.locator('input[type="text"]').all()
                for inp in text_inputs:
                    inp_id = inp.get_attribute('id') or ''
                    inp_name = inp.get_attribute('name') or ''
                    if inp_id != 'user_login' and inp_name != 'log':
                        inp.fill(captcha_solution)
                        break

            page.screenshot(path="/tmp/captcha_filled.png")
            print("CAPTCHA filled. Submitting...")

            # Submit
            page.locator('input[value="Log In"]').click()
            page.wait_for_load_state('networkidle')
            time.sleep(3)

            page.screenshot(path="/tmp/after_login.png")

            # Check if login succeeded
            if "wp-admin" in page.url and "login" not in page.url.lower():
                print("SUCCESS: Logged into WordPress!")
            else:
                page_content = page.content()
                if "incorrect" in page_content.lower():
                    print("ERROR: Login failed (incorrect CAPTCHA or credentials)")
                    return "LOGIN_FAILED"
                print(f"Current URL: {page.url}")

            # Step 2: Add CSS to customizer
            print("\nStep 2: Adding tooltip CSS...")
            page.goto("https://purebrain.ai/wp-admin/customize.php?autofocus[section]=custom_css")
            page.wait_for_load_state('networkidle')
            time.sleep(5)

            page.screenshot(path="/tmp/customizer.png")

            if "customize.php" not in page.url:
                print("ERROR: Not on customizer. Screenshot: /tmp/customizer.png")
                return "NOT_ON_CUSTOMIZER"

            # Add CSS
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

                print("CSS typed into editor")

            time.sleep(2)
            page.screenshot(path="/tmp/css_added.png")

            # Publish
            print("Publishing...")
            page.locator('#save').click()
            time.sleep(3)
            page.screenshot(path="/tmp/css_published.png")
            print("CSS Published!")

            # View the page
            print("\nStep 3: Viewing PureBrain 3.0 page...")
            page.goto("https://purebrain.ai/purebrain-3/")
            page.wait_for_load_state('networkidle')
            time.sleep(3)

            page.screenshot(path="/tmp/purebrain3_page.png", full_page=True)
            print("Page screenshot: /tmp/purebrain3_page.png")

            return "SUCCESS"

        except Exception as e:
            print(f"ERROR: {e}")
            page.screenshot(path="/tmp/error.png")
            return f"ERROR: {e}"

        finally:
            browser.close()

if __name__ == "__main__":
    result = interactive_login_and_css()
    print(f"\nResult: {result}")
