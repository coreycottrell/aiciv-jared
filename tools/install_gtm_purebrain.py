#!/usr/bin/env python3
"""
Install Google Tag Manager on PureBrain.ai WordPress
GTM Container ID: GTM-WTDXL4VJ
"""

import os
import time
from datetime import datetime
from playwright.sync_api import sync_playwright

SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/tools/screenshots"
WP_URL = "https://purebrain.ai/wp-admin/"
WP_USER = "Aether"
WP_PASS = "NW2u!JLQ3!Bt$XD$7CWzz5Z@"
GTM_ID = "GTM-WTDXL4VJ"

def screenshot(page, name):
    """Take a screenshot with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"{SCREENSHOT_DIR}/{timestamp}_{name}.png"
    page.screenshot(path=path, full_page=False)
    print(f"Screenshot saved: {path}")
    return path

def safe_goto(page, url, timeout=60000):
    """Navigate with fallback wait strategies"""
    try:
        page.goto(url, wait_until='domcontentloaded', timeout=timeout)
        time.sleep(2)  # Give extra time for dynamic content
    except Exception as e:
        print(f"Navigation warning: {e}")
        time.sleep(3)

def main():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    with sync_playwright() as p:
        # Launch headless browser
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        print("Step 1: Navigating to WordPress admin...")
        safe_goto(page, WP_URL)
        screenshot(page, "01_login_page")

        # Check for GoDaddy login page
        godaddy_toggle = page.query_selector('a:has-text("Log in with username and password")')
        if godaddy_toggle:
            print("GoDaddy login detected - clicking to show username/password form...")
            godaddy_toggle.click()
            time.sleep(2)
            screenshot(page, "02_username_form")

        # Login
        print("Step 2: Logging in...")
        login_field = page.wait_for_selector('#user_login', state='visible', timeout=30000)
        login_field.fill(WP_USER)
        page.fill('#user_pass', WP_PASS)
        page.click('#wp-submit')
        time.sleep(5)
        screenshot(page, "03_after_login")

        if 'wp-admin' not in page.url or 'login' in page.url.lower():
            print("Login failed!")
            browser.close()
            return

        print("Login successful!")

        # Go to GTM settings
        print("Step 3: Going to GTM settings page...")
        safe_goto(page, "https://purebrain.ai/wp-admin/options-general.php?page=gtm4wp-settings")
        time.sleep(2)
        screenshot(page, "04_gtm_settings")

        # Verify we're on the GTM page
        if 'Google Tag Manager' not in page.content():
            print("Not on GTM page!")
            browser.close()
            return

        # Find and fill GTM ID
        print("Step 4: Configuring GTM ID...")
        text_inputs = page.query_selector_all('input[type="text"]')
        gtm_input = None
        for inp in text_inputs:
            name = inp.get_attribute('name') or ''
            if 'gtm' in name.lower():
                gtm_input = inp
                print(f"Found GTM input: name={name}")
                break

        if gtm_input:
            gtm_input.click()
            gtm_input.fill('')
            gtm_input.fill(GTM_ID)
            print(f"Entered GTM ID: {GTM_ID}")
        else:
            print("Could not find GTM ID input!")

        # Enable Container code (set to "On")
        print("Step 5: Enabling container code...")
        # The "On" radio button for Container code ON/OFF
        # Looking at the HTML, it's likely a radio with value "1" or text "On"
        radio_inputs = page.query_selector_all('input[type="radio"]')
        for radio in radio_inputs:
            name = radio.get_attribute('name') or ''
            value = radio.get_attribute('value') or ''
            # Find the "On" option for gtm4wp_option_code_on/off
            if 'code' in name.lower() and value == '1':
                print(f"Found container code ON radio: name={name}, value={value}")
                radio.click()
                break
            # Alternative: check parent label text
            try:
                parent = radio.evaluate_handle('el => el.parentElement')
                if parent:
                    label_text = page.evaluate('el => el.innerText || ""', parent)
                    if 'on' in label_text.lower() and 'code' in name.lower():
                        print(f"Found ON radio by label")
                        radio.click()
                        break
            except:
                pass

        screenshot(page, "05_settings_configured")

        # Save settings
        print("Step 6: Saving settings...")
        save_btn = page.query_selector('input[type="submit"]')
        if save_btn:
            save_btn.click()
            time.sleep(5)
            screenshot(page, "06_settings_saved")

        # Scroll down to see if there are more settings to configure
        page.evaluate('window.scrollTo(0, 0)')
        time.sleep(1)
        screenshot(page, "07_after_save_top")

        # Check the current state of container code setting
        page.reload()
        time.sleep(3)

        # Get current state of radio buttons
        code_on = page.query_selector('input[type="radio"][name*="code"][value="1"]')
        code_off = page.query_selector('input[type="radio"][name*="code"][value="0"]')

        if code_on:
            is_on = code_on.is_checked()
            print(f"Container code is {'ON' if is_on else 'OFF'}")
            if not is_on:
                print("Attempting to turn ON container code...")
                code_on.click()
                time.sleep(1)
                save_btn = page.query_selector('input[type="submit"]')
                if save_btn:
                    save_btn.click()
                    time.sleep(5)

        screenshot(page, "08_final_state")

        # Verify on frontend
        print("Step 7: Verifying GTM on frontend...")
        safe_goto(page, "https://purebrain.ai/")
        time.sleep(3)

        page_source = page.content()
        screenshot(page, "09_frontend")

        if GTM_ID in page_source:
            print(f"\n*** SUCCESS: GTM {GTM_ID} is active on the site! ***")
        elif 'googletagmanager' in page_source.lower():
            print("GTM code found but checking for container ID...")
            # Search more specifically
            import re
            gtm_matches = re.findall(r'GTM-[A-Z0-9]+', page_source)
            if gtm_matches:
                print(f"Found GTM containers: {gtm_matches}")
        else:
            print("GTM code not found on frontend yet")
            print("This may be due to:")
            print("  1. Container code is OFF in settings")
            print("  2. Caching - try clearing cache")
            print("  3. GTM needs a few minutes to propagate")

        browser.close()
        print("\n" + "="*60)
        print("GTM Installation Process Complete!")
        print(f"Container ID: {GTM_ID}")
        print(f"Screenshots: {SCREENSHOT_DIR}")
        print("="*60)

if __name__ == "__main__":
    main()
