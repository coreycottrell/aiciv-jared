#!/usr/bin/env python3
"""
Final attempt to enable GTM Container Code on PureBrain.ai
With better CAPTCHA detection
"""

import os
import time
from datetime import datetime
from playwright.sync_api import sync_playwright

SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/tools/screenshots"
WP_USER = "Aether"
WP_PASS = "NW2u!JLQ3!Bt$XD$7CWzz5Z@"
GTM_ID = "GTM-WTDXL4VJ"

def screenshot(page, name):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"{SCREENSHOT_DIR}/{timestamp}_{name}.png"
    page.screenshot(path=path, full_page=False)
    print(f"Screenshot: {path}")
    return path

def main():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = context.new_page()

        # Login
        print("Step 1: Navigating to login page...")
        page.goto("https://purebrain.ai/wp-login.php", wait_until='domcontentloaded', timeout=60000)
        time.sleep(3)
        screenshot(page, "01_login")

        # Check for actual CAPTCHA (reCAPTCHA checkbox, not just 'verify' text)
        captcha_element = page.query_selector('iframe[src*="recaptcha"], .g-recaptcha, #recaptcha')
        if captcha_element:
            print("Real CAPTCHA detected - cannot proceed automatically")
            browser.close()
            return False

        # Check for GoDaddy toggle
        toggle = page.query_selector('a:has-text("Log in with username and password")')
        if toggle:
            print("Clicking GoDaddy toggle...")
            toggle.click()
            time.sleep(2)
            screenshot(page, "02_toggle")

        # Fill login
        print("Step 2: Logging in...")
        page.fill('#user_login', WP_USER)
        page.fill('#user_pass', WP_PASS)
        screenshot(page, "03_credentials")

        page.click('#wp-submit')
        time.sleep(8)
        screenshot(page, "04_after_login")

        # Verify login
        if 'wp-admin' not in page.url:
            print(f"Login issue - URL: {page.url}")
            # Check for CAPTCHA on this page
            if page.query_selector('iframe[src*="recaptcha"]'):
                print("CAPTCHA appeared - rate limited")
                browser.close()
                return False
            browser.close()
            return False

        print("Logged in successfully!")

        # Go to GTM settings
        print("Step 3: GTM Settings...")
        page.goto("https://purebrain.ai/wp-admin/options-general.php?page=gtm4wp-settings",
                  wait_until='domcontentloaded', timeout=60000)
        time.sleep(4)
        screenshot(page, "05_gtm_page")

        # Scroll down to see the Container code ON/OFF section
        page.evaluate('window.scrollBy(0, 300)')
        time.sleep(1)
        screenshot(page, "06_scrolled")

        # Find and click the "On" radio button
        print("Step 4: Enabling Container code...")

        # Get the name of the radio input from the page
        radio_info = page.evaluate('''() => {
            const radios = document.querySelectorAll('input[type="radio"]');
            const info = [];
            for (let r of radios) {
                info.push({
                    name: r.name,
                    value: r.value,
                    id: r.id,
                    checked: r.checked
                });
            }
            return info;
        }''')

        print(f"Radio buttons found: {len(radio_info)}")
        for r in radio_info:
            print(f"  {r}")

        # Enable the container code
        result = page.evaluate('''() => {
            // Find radio for container code ON
            const radios = document.querySelectorAll('input[type="radio"]');
            for (let r of radios) {
                // GTM4WP uses name like "gtm4wp-options[gtm-code-on]" with values "0" and "1"
                if (r.name && r.name.includes('code') && r.value === '1') {
                    r.checked = true;
                    r.click();
                    return {success: true, name: r.name, value: r.value};
                }
            }
            return {success: false};
        }''')

        print(f"Enable result: {result}")
        time.sleep(1)
        screenshot(page, "07_after_enable")

        # Save
        print("Step 5: Saving...")
        page.click('input[type="submit"]')
        time.sleep(5)
        screenshot(page, "08_saved")

        # Check for success message
        if 'saved' in page.content().lower() or 'updated' in page.content().lower():
            print("Settings saved successfully!")

        # Verify settings
        page.reload()
        time.sleep(3)

        # Get current state
        current_state = page.evaluate('''() => {
            const radios = document.querySelectorAll('input[type="radio"]');
            for (let r of radios) {
                if (r.name && r.name.includes('code') && r.checked) {
                    return {name: r.name, value: r.value};
                }
            }
            return null;
        }''')
        print(f"Current container code state: {current_state}")
        screenshot(page, "09_verified_settings")

        # Check frontend
        print("\nStep 6: Checking frontend...")
        page.goto("https://purebrain.ai/", wait_until='networkidle', timeout=60000)
        time.sleep(3)
        screenshot(page, "10_frontend")

        # Get page source and check for GTM
        html = page.content()

        if GTM_ID in html:
            print(f"\n{'='*60}")
            print(f"SUCCESS! GTM {GTM_ID} IS NOW ACTIVE!")
            print(f"{'='*60}")
            return True

        # Check specifically in head
        head_html = page.evaluate('() => document.head.innerHTML')
        if GTM_ID in head_html or 'googletagmanager' in head_html:
            print("GTM code found in <head>!")
            if GTM_ID in head_html:
                print(f"SUCCESS! Container {GTM_ID} verified!")
                return True
            else:
                print("GTM script present but may be different container")

        # Check for any gtm references
        import re
        gtm_refs = re.findall(r'GTM-[A-Z0-9]+', html)
        if gtm_refs:
            print(f"Found GTM references: {gtm_refs}")
        else:
            print("No GTM container IDs found in page source")
            print("\nContainer code may still be OFF. Check WordPress admin manually at:")
            print("https://purebrain.ai/wp-admin/options-general.php?page=gtm4wp-settings")
            print("\nMake sure 'Container code ON/OFF' is set to 'On'")

        browser.close()
        return False

if __name__ == "__main__":
    success = main()
    print(f"\nResult: {'SUCCESS' if success else 'NEEDS MANUAL COMPLETION'}")
