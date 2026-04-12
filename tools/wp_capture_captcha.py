#!/usr/bin/env python3
"""
Step 1: Just capture the CAPTCHA and keep browser alive
Then run wp_submit_captcha.py with the solution
"""

import time
import sys
import pickle
from playwright.sync_api import sync_playwright

WP_URL = "https://purebrain.ai/wp-admin"
WP_USER = "Aether"
WP_PASSWORD = "NW2u!JLQ3!Bt$XD$7CWzz5Z@"

def capture_captcha():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        print("Navigating to login page...")
        page.goto(f"{WP_URL}")
        page.wait_for_load_state('networkidle')
        time.sleep(2)

        # Click "Log in with username and password"
        username_pass_link = page.locator('text=Log in with username and password')
        if username_pass_link.count() > 0:
            print("Clicking username/password option...")
            username_pass_link.click()
            time.sleep(2)

        # Fill username and password
        page.locator('#user_login').fill(WP_USER)
        page.locator('#user_pass').fill(WP_PASSWORD)

        # Take screenshot
        page.screenshot(path="/tmp/captcha_current.png")
        print("\n" + "="*60)
        print("CAPTCHA CAPTURED: /tmp/captcha_current.png")
        print("="*60)
        print("\nRun the script again with the CAPTCHA solution:")
        print("  python3 wp_solve_and_login.py <captcha>")

        # Save cookies for session continuity (won't help with CAPTCHA but good practice)
        cookies = context.cookies()
        with open('/tmp/wp_cookies.pkl', 'wb') as f:
            pickle.dump(cookies, f)

        browser.close()

if __name__ == "__main__":
    capture_captcha()
