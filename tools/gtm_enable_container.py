#!/usr/bin/env python3
"""
Enable GTM Container Code - Fixed radio button targeting
The radio name is: gtm4wp-options[container-on]
Value 1 = ON, Value 0 = OFF
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
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        # Login
        print("Logging in...")
        page.goto("https://purebrain.ai/wp-login.php", wait_until='domcontentloaded', timeout=60000)
        time.sleep(2)

        toggle = page.query_selector('a:has-text("Log in with username and password")')
        if toggle:
            toggle.click()
            time.sleep(2)

        page.fill('#user_login', WP_USER)
        page.fill('#user_pass', WP_PASS)
        page.click('#wp-submit')
        time.sleep(6)

        if 'wp-admin' not in page.url:
            print("Login failed")
            browser.close()
            return

        print("Login successful!")

        # Go to GTM settings
        print("Going to GTM settings...")
        page.goto("https://purebrain.ai/wp-admin/options-general.php?page=gtm4wp-settings",
                  wait_until='domcontentloaded', timeout=60000)
        time.sleep(3)
        screenshot(page, "01_gtm_settings")

        # Click the "On" radio for container-on using the correct selector
        print("Enabling Container ON...")

        # The ID is: gtm4wp-options[container-on]_1
        on_radio = page.query_selector('#gtm4wp-options\\[container-on\\]_1')
        if on_radio:
            print("Found the ON radio button!")
            on_radio.click()
            time.sleep(1)
            print(f"Checked: {on_radio.is_checked()}")
        else:
            # Try alternative selector
            print("Trying alternative selector...")
            on_radio = page.query_selector('input[name="gtm4wp-options[container-on]"][value="1"]')
            if on_radio:
                print("Found via name selector!")
                on_radio.click()
                time.sleep(1)
            else:
                # Last resort: JavaScript
                print("Using JavaScript to enable...")
                page.evaluate('''() => {
                    const r = document.querySelector('input[name="gtm4wp-options[container-on]"][value="1"]');
                    if (r) {
                        r.checked = true;
                        r.click();
                    }
                }''')
                time.sleep(1)

        screenshot(page, "02_after_enable")

        # Save
        print("Saving settings...")
        save_btn = page.query_selector('input[type="submit"]')
        if save_btn:
            save_btn.click()
            time.sleep(5)

        screenshot(page, "03_after_save")

        # Verify the setting
        page.reload()
        time.sleep(3)

        on_checked = page.evaluate('''() => {
            const r = document.querySelector('input[name="gtm4wp-options[container-on]"][value="1"]');
            return r ? r.checked : null;
        }''')
        print(f"Container ON is checked: {on_checked}")
        screenshot(page, "04_verified")

        if on_checked:
            print("\n*** Container code is now ENABLED! ***\n")

        # Check frontend
        print("Checking frontend...")
        page.goto("https://purebrain.ai/", wait_until='domcontentloaded', timeout=60000)
        time.sleep(5)
        screenshot(page, "05_frontend")

        html = page.content()
        head = page.evaluate('() => document.head.innerHTML')

        if GTM_ID in html or GTM_ID in head:
            print(f"\n{'='*60}")
            print(f"SUCCESS! GTM {GTM_ID} IS ACTIVE ON THE SITE!")
            print(f"{'='*60}")
        elif 'googletagmanager' in html.lower() or 'googletagmanager' in head.lower():
            print("GTM script found on page!")
            import re
            ids = re.findall(r'GTM-[A-Z0-9]+', html + head)
            print(f"Container IDs found: {set(ids)}")
        else:
            print("GTM not visible yet. May need cache clear or few minutes.")

        browser.close()

if __name__ == "__main__":
    main()
