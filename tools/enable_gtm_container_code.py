#!/usr/bin/env python3
"""
Enable GTM Container Code on PureBrain.ai
The GTM ID is already set, but Container code is OFF - need to turn it ON
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
        print("Logging in to WordPress...")
        page.goto(WP_URL, wait_until='domcontentloaded', timeout=60000)
        time.sleep(2)

        # Click to show username form (GoDaddy)
        toggle = page.query_selector('a:has-text("Log in with username and password")')
        if toggle:
            toggle.click()
            time.sleep(2)

        page.fill('#user_login', WP_USER)
        page.fill('#user_pass', WP_PASS)
        page.click('#wp-submit')
        time.sleep(5)
        print("Logged in!")

        # Go to GTM settings
        print("Going to GTM settings...")
        page.goto("https://purebrain.ai/wp-admin/options-general.php?page=gtm4wp-settings",
                  wait_until='domcontentloaded', timeout=60000)
        time.sleep(3)
        screenshot(page, "01_gtm_settings_before")

        # Find and enable "Container code ON"
        print("Looking for Container code ON/OFF setting...")

        # Method 1: Try clicking the "On" label text
        on_label = page.query_selector('label:has-text("On")')
        if on_label:
            print("Found 'On' label, clicking...")
            on_label.click()
            time.sleep(1)
        else:
            # Method 2: Find by input name pattern
            # The plugin uses gtm4wp-options[gtm-code-on] or similar
            print("Looking for radio input directly...")

            # Get all radio inputs and find the one for "code on"
            all_radios = page.query_selector_all('input[type="radio"]')
            print(f"Found {len(all_radios)} radio inputs")

            for i, radio in enumerate(all_radios):
                name = radio.get_attribute('name') or ''
                value = radio.get_attribute('value') or ''
                radio_id = radio.get_attribute('id') or ''

                # Debug: print all radio info
                print(f"  Radio {i}: name='{name}', value='{value}', id='{radio_id}'")

                # The "On" option typically has value="1" for the code-on setting
                if 'code' in name.lower() and value == '1':
                    print(f"  >> Clicking this one (container code ON)")
                    radio.click()
                    time.sleep(1)
                    break

        screenshot(page, "02_after_clicking_on")

        # Save settings
        print("Saving settings...")
        save_btn = page.query_selector('input[type="submit"]')
        if save_btn:
            save_btn.click()
            time.sleep(5)
            print("Settings saved!")
        else:
            print("Could not find save button!")

        screenshot(page, "03_after_save")

        # Verify the setting stuck
        page.reload()
        time.sleep(3)
        screenshot(page, "04_after_reload")

        # Check current state
        code_radios = page.query_selector_all('input[type="radio"][name*="code"]')
        for radio in code_radios:
            value = radio.get_attribute('value')
            checked = radio.is_checked()
            print(f"Container code radio value={value}, checked={checked}")

        # Verify on frontend
        print("\nVerifying GTM on frontend...")
        page.goto("https://purebrain.ai/", wait_until='domcontentloaded', timeout=60000)
        time.sleep(3)

        page_source = page.content()
        screenshot(page, "05_frontend")

        if GTM_ID in page_source:
            print(f"\n*** SUCCESS! GTM {GTM_ID} is now active on purebrain.ai! ***")
        elif 'googletagmanager' in page_source.lower():
            print("GTM script found - checking head section...")
            head = page.evaluate('() => document.head.innerHTML')
            if GTM_ID in head:
                print(f"\n*** SUCCESS! GTM {GTM_ID} found in <head>! ***")
            else:
                print("GTM found but different container ID")
        else:
            print("GTM not yet visible - may need cache clear")
            print("Checking page source for any GTM references...")
            if 'gtm' in page_source.lower():
                print("Found 'gtm' reference in page")
            else:
                print("No GTM references found")

        browser.close()

if __name__ == "__main__":
    main()
