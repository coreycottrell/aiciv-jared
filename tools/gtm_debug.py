#!/usr/bin/env python3
"""Debug GTM settings - check current state and re-enable if needed"""

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
    page.screenshot(path=path, full_page=True)
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
        print("\nGoing to GTM settings...")
        page.goto("https://purebrain.ai/wp-admin/options-general.php?page=gtm4wp-settings",
                  wait_until='domcontentloaded', timeout=60000)
        time.sleep(3)

        # Get current state of all settings
        print("\nCurrent GTM settings:")

        # GTM ID
        gtm_input = page.query_selector('input[name="gtm4wp-options[gtm-code]"]')
        if gtm_input:
            current_id = gtm_input.input_value()
            print(f"  GTM ID: {current_id}")
        else:
            print("  GTM ID input not found!")

        # Container ON/OFF
        on_radio = page.query_selector('input[name="gtm4wp-options[container-on]"][value="1"]')
        off_radio = page.query_selector('input[name="gtm4wp-options[container-on]"][value="0"]')

        if on_radio:
            print(f"  Container ON checked: {on_radio.is_checked()}")
        if off_radio:
            print(f"  Container OFF checked: {off_radio.is_checked()}")

        screenshot(page, "debug_01_settings")

        # If container is OFF, turn it ON
        if on_radio and not on_radio.is_checked():
            print("\nContainer is OFF! Enabling...")
            on_radio.click()
            time.sleep(1)

            # Also make sure GTM ID is set
            if gtm_input:
                current = gtm_input.input_value()
                if not current:
                    print("GTM ID is empty! Setting it...")
                    gtm_input.fill(GTM_ID)

            # Save
            save_btn = page.query_selector('input[type="submit"]')
            if save_btn:
                save_btn.click()
                time.sleep(5)
                print("Settings saved!")

            screenshot(page, "debug_02_after_save")

            # Verify
            page.reload()
            time.sleep(3)
            on_radio = page.query_selector('input[name="gtm4wp-options[container-on]"][value="1"]')
            print(f"After save - Container ON: {on_radio.is_checked() if on_radio else 'N/A'}")

        # Check all tabs for any other required settings
        print("\nChecking other tabs...")

        tabs = ['Basic data', 'Events', 'Scroll tracking', 'Security', 'Integration', 'Advanced']
        for tab_name in tabs:
            tab = page.query_selector(f'a:has-text("{tab_name}")')
            if tab:
                tab.click()
                time.sleep(1)
                # Check for any required settings or warnings
                warnings = page.query_selector_all('.notice-warning, .notice-error')
                if warnings:
                    print(f"  {tab_name}: {len(warnings)} warnings/errors found")

        screenshot(page, "debug_03_tabs")

        # Check for cache plugins that might need clearing
        print("\nChecking for cache plugins...")
        page.goto("https://purebrain.ai/wp-admin/plugins.php", wait_until='domcontentloaded', timeout=60000)
        time.sleep(3)

        plugins_html = page.content().lower()
        cache_plugins = ['cache', 'rocket', 'litespeed', 'w3 total', 'super cache', 'fastest']
        for cp in cache_plugins:
            if cp in plugins_html:
                print(f"  Found cache plugin containing: {cp}")

        # Check Object Cache
        page.goto("https://purebrain.ai/wp-admin/options-general.php?page=developer", wait_until='domcontentloaded', timeout=30000)
        time.sleep(2)
        if 'object cache' in page.content().lower():
            print("  Object Cache settings found")

        screenshot(page, "debug_04_plugins")

        # Try to purge cache via GoDaddy
        print("\nAttempting to purge GoDaddy cache...")
        # Look for GoDaddy menu or cache options
        godaddy_menu = page.query_selector('#wp-admin-bar-starter-template-flush-cache, a:has-text("Flush Cache")')
        if godaddy_menu:
            godaddy_menu.click()
            time.sleep(3)
            print("  Cache flush clicked!")
        else:
            # Try GoDaddy menu in admin bar
            page.evaluate('''() => {
                const items = document.querySelectorAll('#wp-admin-bar-root-default a');
                for (let item of items) {
                    if (item.textContent.toLowerCase().includes('cache') ||
                        item.textContent.toLowerCase().includes('flush')) {
                        item.click();
                        return true;
                    }
                }
                return false;
            }''')

        screenshot(page, "debug_05_cache")

        browser.close()
        print("\nDebug complete. Check screenshots for details.")

if __name__ == "__main__":
    main()
