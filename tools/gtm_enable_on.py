#!/usr/bin/env python3
"""
Enable GTM Container Code on PureBrain.ai - Slow and careful approach
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
        # Use persistent context to handle cookies better
        browser = p.chromium.launch(headless=True, slow_mo=500)  # Slow motion
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = context.new_page()

        # Login slowly
        print("Step 1: Navigating to login page...")
        page.goto("https://purebrain.ai/wp-login.php", wait_until='networkidle', timeout=60000)
        time.sleep(3)
        screenshot(page, "step01_login")

        # Check for CAPTCHA
        if 'verify' in page.content().lower() or 'captcha' in page.content().lower():
            print("CAPTCHA detected - need to wait longer or use different IP")
            screenshot(page, "captcha_detected")
            browser.close()
            return False

        # Check for GoDaddy toggle
        toggle = page.query_selector('a:has-text("Log in with username and password")')
        if toggle:
            print("Clicking GoDaddy toggle...")
            toggle.click()
            time.sleep(3)
            screenshot(page, "step02_toggle_clicked")

        # Fill login form slowly
        print("Step 2: Filling login form...")
        user_input = page.wait_for_selector('#user_login', state='visible', timeout=30000)
        for char in WP_USER:
            user_input.type(char, delay=100)
            time.sleep(0.05)

        time.sleep(1)

        pass_input = page.query_selector('#user_pass')
        for char in WP_PASS:
            pass_input.type(char, delay=50)
            time.sleep(0.03)

        time.sleep(2)
        screenshot(page, "step03_form_filled")

        # Submit
        print("Step 3: Submitting login...")
        page.click('#wp-submit')
        time.sleep(8)  # Wait longer for login
        screenshot(page, "step04_after_login")

        # Check if login succeeded
        if 'wp-admin' not in page.url:
            print(f"Login may have failed. URL: {page.url}")
            if 'captcha' in page.content().lower() or 'verify' in page.content().lower():
                print("CAPTCHA appeared after login attempt")
            screenshot(page, "login_issue")
            browser.close()
            return False

        print("Login successful!")

        # Navigate to GTM settings
        print("Step 4: Going to GTM settings...")
        time.sleep(3)  # Wait before navigation
        page.goto("https://purebrain.ai/wp-admin/options-general.php?page=gtm4wp-settings",
                  wait_until='domcontentloaded', timeout=60000)
        time.sleep(5)
        screenshot(page, "step05_gtm_settings")

        # Find the Container code ON radio
        print("Step 5: Looking for Container code ON/OFF...")

        # Look for the radio buttons
        # In GTM4WP, the setting name is: gtm4wp-options[gtm-code-on]
        radios = page.query_selector_all('input[type="radio"]')
        print(f"Found {len(radios)} radio buttons")

        # Find the "On" radio for container code
        on_clicked = False
        for radio in radios:
            name = radio.get_attribute('name') or ''
            value = radio.get_attribute('value') or ''
            radio_id = radio.get_attribute('id') or ''

            if 'code' in name.lower():
                print(f"  Found code radio: name={name}, value={value}, id={radio_id}")

                if value == '1':  # "On" is typically value "1"
                    is_checked = radio.is_checked()
                    print(f"    Currently checked: {is_checked}")

                    if not is_checked:
                        print("    Clicking to enable...")
                        # Try clicking the radio itself
                        radio.click()
                        time.sleep(1)

                        # Verify it's now checked
                        if radio.is_checked():
                            print("    SUCCESS: Radio is now checked!")
                            on_clicked = True
                        else:
                            print("    Click may not have worked, trying label...")
                            # Try clicking associated label
                            label = page.query_selector(f'label[for="{radio_id}"]')
                            if label:
                                label.click()
                                time.sleep(1)
                    else:
                        print("    Already ON!")
                        on_clicked = True

        if not on_clicked:
            # Alternative: Try JavaScript to set the value
            print("Trying JavaScript approach...")
            page.evaluate('''() => {
                const radios = document.querySelectorAll('input[type="radio"]');
                for (let r of radios) {
                    if (r.name && r.name.toLowerCase().includes('code') && r.value === '1') {
                        r.checked = true;
                        r.dispatchEvent(new Event('change', { bubbles: true }));
                        return true;
                    }
                }
                return false;
            }''')
            time.sleep(1)

        screenshot(page, "step06_settings_updated")

        # Save settings
        print("Step 6: Saving settings...")
        save_btn = page.query_selector('input[type="submit"], input.button-primary')
        if save_btn:
            save_btn.click()
            time.sleep(5)
            screenshot(page, "step07_after_save")
            print("Settings saved!")

        # Verify on reload
        print("Step 7: Verifying settings...")
        page.reload()
        time.sleep(5)
        screenshot(page, "step08_verify_settings")

        # Check the state
        radios = page.query_selector_all('input[type="radio"]')
        for radio in radios:
            name = radio.get_attribute('name') or ''
            value = radio.get_attribute('value') or ''
            if 'code' in name.lower():
                checked = radio.is_checked()
                print(f"Radio {name}={value}: checked={checked}")

        # Verify on frontend
        print("\nStep 8: Verifying GTM on frontend...")
        page.goto("https://purebrain.ai/", wait_until='networkidle', timeout=60000)
        time.sleep(5)

        page_source = page.content()
        screenshot(page, "step09_frontend")

        # Check for GTM
        if GTM_ID in page_source:
            print(f"\n{'='*60}")
            print(f"SUCCESS! GTM {GTM_ID} is ACTIVE on purebrain.ai!")
            print(f"{'='*60}")
            return True
        elif 'googletagmanager.com' in page_source:
            print("GTM script found! Checking for container ID...")
            import re
            ids = re.findall(r'GTM-[A-Z0-9]+', page_source)
            print(f"Found GTM IDs: {ids}")
            if GTM_ID in ids:
                print(f"\nSUCCESS! {GTM_ID} confirmed!")
                return True
        else:
            print("GTM not visible on frontend yet")
            print("Possible reasons:")
            print("  1. Container code still OFF")
            print("  2. Page caching")
            print("  3. Need to clear browser/CDN cache")
            return False

        browser.close()

if __name__ == "__main__":
    main()
