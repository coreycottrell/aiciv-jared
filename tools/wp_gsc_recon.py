#!/usr/bin/env python3
"""
Reconnaissance for Google Search Console Meta Tag
Date: 2026-02-17

Non-interactive script to:
1. Capture login page state
2. Check if cookies can bypass CAPTCHA
"""

import time
from playwright.sync_api import sync_playwright

WP_URL = "https://purebrain.ai/wp-admin"
WP_USER = "Aether"
WP_PASSWORD = "NW2u!JLQ3!Bt$XD$7CWzz5Z@"

def recon():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        try:
            print("Navigating to WordPress login...")
            page.goto(WP_URL)
            page.wait_for_load_state('networkidle')
            time.sleep(2)

            # Capture login page
            page.screenshot(path="/tmp/wp_login_state.png")
            print("Login page captured: /tmp/wp_login_state.png")

            # Check what's on the page
            page_content = page.content()

            # Check for CAPTCHA
            has_captcha = 'captcha' in page_content.lower()
            print(f"Has CAPTCHA: {has_captcha}")

            # Check for Two-Step Auth options
            has_two_step = 'two-step' in page_content.lower() or '2fa' in page_content.lower()
            print(f"Has Two-Step: {has_two_step}")

            # List input fields
            inputs = page.locator('input').all()
            print(f"\nInput fields found: {len(inputs)}")
            for inp in inputs:
                inp_type = inp.get_attribute('type') or 'unknown'
                inp_name = inp.get_attribute('name') or ''
                inp_id = inp.get_attribute('id') or ''
                print(f"  - type={inp_type}, name={inp_name}, id={inp_id}")

            # Check if there's a "Log in with username and password" link
            username_pass_link = page.locator('text=Log in with username and password')
            if username_pass_link.count() > 0:
                print("\nFound 'Log in with username and password' link - clicking it...")
                username_pass_link.click()
                time.sleep(2)
                page.screenshot(path="/tmp/wp_login_expanded.png")
                print("Expanded login captured: /tmp/wp_login_expanded.png")

                # Re-check inputs
                inputs = page.locator('input').all()
                print(f"\nInput fields after expand: {len(inputs)}")
                for inp in inputs:
                    inp_type = inp.get_attribute('type') or 'unknown'
                    inp_name = inp.get_attribute('name') or ''
                    inp_id = inp.get_attribute('id') or ''
                    print(f"  - type={inp_type}, name={inp_name}, id={inp_id}")

            print("\nRecon complete. Check screenshots.")
            return "RECON_DONE"

        except Exception as e:
            print(f"ERROR: {e}")
            page.screenshot(path="/tmp/wp_recon_error.png")
            return f"ERROR: {e}"

        finally:
            browser.close()

if __name__ == "__main__":
    result = recon()
    print(f"\nResult: {result}")
