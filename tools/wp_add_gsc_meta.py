#!/usr/bin/env python3
"""
Add Google Search Console Verification Meta Tag to WordPress
Date: 2026-02-17

This script will:
1. Login to WordPress (with CAPTCHA)
2. Try Option A: Customizer → Head Scripts
3. If not found, Try Option B: Install WPCode plugin
4. Add the verification meta tag
5. Verify it appears in page source
"""

import time
import sys
from playwright.sync_api import sync_playwright

# Credentials
WP_URL = "https://purebrain.ai/wp-admin"
WP_USER = "Aether"
WP_PASSWORD = "NW2u!JLQ3!Bt$XD$7CWzz5Z@"

# Google Search Console verification meta tag
GSC_META_TAG = '<meta name="google-site-verification" content="S4BWw-zZDnPzo2x3U7iPvdUTxqnUkqGlW1S9fb024O0" />'

def add_gsc_verification():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        try:
            # Step 1: Login
            print("Step 1: Navigating to WordPress login...")
            page.goto(WP_URL)
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
            captcha_path = "/tmp/captcha_gsc.png"
            page.screenshot(path=captcha_path)
            print(f"\n{'='*60}")
            print(f"CAPTCHA SCREENSHOT SAVED: {captcha_path}")
            print(f"{'='*60}")
            print("\nPlease look at the CAPTCHA image and enter the text.")

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
                text_inputs = page.locator('input[type="text"]').all()
                for inp in text_inputs:
                    inp_id = inp.get_attribute('id') or ''
                    inp_name = inp.get_attribute('name') or ''
                    if inp_id != 'user_login' and inp_name != 'log':
                        inp.fill(captcha_solution)
                        break

            # Submit
            page.locator('input[value="Log In"]').click()
            page.wait_for_load_state('networkidle')
            time.sleep(3)

            page.screenshot(path="/tmp/after_login_gsc.png")

            # Check if login succeeded
            if "wp-admin" in page.url and "login" not in page.url.lower():
                print("SUCCESS: Logged into WordPress!")
            else:
                print(f"Current URL: {page.url}")
                page_content = page.content()
                if "incorrect" in page_content.lower():
                    print("ERROR: Login failed")
                    return "LOGIN_FAILED"

            # Step 2: Try to find Header Scripts in Customizer
            print("\n" + "="*60)
            print("Step 2: Checking Customizer for Header Scripts...")
            print("="*60)

            page.goto("https://purebrain.ai/wp-admin/customize.php")
            page.wait_for_load_state('networkidle')
            time.sleep(5)

            page.screenshot(path="/tmp/customizer_gsc.png")
            print("Screenshot: /tmp/customizer_gsc.png")

            # Look for header scripts or custom code panels
            page_content = page.content().lower()
            if 'header' in page_content and 'script' in page_content:
                print("Found Header Scripts option!")
                # Try to click on it
                header_panel = page.locator('text=Header Scripts')
                if header_panel.count() > 0:
                    header_panel.first.click()
                    time.sleep(2)
                    page.screenshot(path="/tmp/header_scripts_panel.png")

            # Step 3: Try WPCode plugin approach
            print("\n" + "="*60)
            print("Step 3: Checking for WPCode plugin...")
            print("="*60)

            page.goto("https://purebrain.ai/wp-admin/plugins.php")
            page.wait_for_load_state('networkidle')
            time.sleep(3)

            page.screenshot(path="/tmp/plugins_list.png")
            plugins_content = page.content().lower()

            if 'wpcode' in plugins_content or 'insert headers' in plugins_content:
                print("WPCode or Headers plugin found!")
                # Navigate to WPCode settings
                page.goto("https://purebrain.ai/wp-admin/admin.php?page=wpcode-headers-footers")
                page.wait_for_load_state('networkidle')
                time.sleep(3)
                page.screenshot(path="/tmp/wpcode_settings.png")
            else:
                print("WPCode not installed. Checking for theme header option...")

            # Step 4: Check Theme Options / Divi
            print("\n" + "="*60)
            print("Step 4: Checking Divi Theme Options...")
            print("="*60)

            page.goto("https://purebrain.ai/wp-admin/admin.php?page=et_divi_options")
            page.wait_for_load_state('networkidle')
            time.sleep(3)

            page.screenshot(path="/tmp/divi_options.png")
            print("Screenshot: /tmp/divi_options.png")

            # Look for Integration tab
            integration_link = page.locator('text=Integration')
            if integration_link.count() > 0:
                print("Found Integration tab!")
                integration_link.first.click()
                time.sleep(2)
                page.screenshot(path="/tmp/divi_integration.png")
                print("Screenshot: /tmp/divi_integration.png")

                # Look for head code area
                head_code_area = page.locator('#et_divi\\[divi_integration_head\\]')
                if head_code_area.count() > 0:
                    print("Found Head code area! Adding meta tag...")
                    # Get current value
                    current_value = head_code_area.input_value()
                    if GSC_META_TAG not in current_value:
                        new_value = current_value + "\n" + GSC_META_TAG if current_value else GSC_META_TAG
                        head_code_area.fill(new_value)
                        page.screenshot(path="/tmp/meta_tag_added.png")
                        print("Meta tag added!")

                        # Save changes
                        save_button = page.locator('#epanel-save')
                        if save_button.count() > 0:
                            save_button.click()
                            time.sleep(3)
                            page.screenshot(path="/tmp/divi_saved.png")
                            print("Divi options saved!")
                    else:
                        print("Meta tag already exists!")

            # Step 5: Verify on frontend
            print("\n" + "="*60)
            print("Step 5: Verifying meta tag on frontend...")
            print("="*60)

            page.goto("https://purebrain.ai")
            page.wait_for_load_state('networkidle')
            time.sleep(3)

            page_source = page.content()

            if "google-site-verification" in page_source and "S4BWw-zZDnPzo2x3U7iPvdUTxqnUkqGlW1S9fb024O0" in page_source:
                print("\n" + "="*60)
                print("SUCCESS! Meta tag verified in page source!")
                print("="*60)
                return "VERIFIED"
            else:
                print("\nMeta tag NOT found in page source yet.")
                print("Screenshots saved for review.")
                return "NOT_VERIFIED"

        except Exception as e:
            print(f"ERROR: {e}")
            page.screenshot(path="/tmp/error_gsc.png")
            return f"ERROR: {e}"

        finally:
            browser.close()

if __name__ == "__main__":
    result = add_gsc_verification()
    print(f"\nFinal Result: {result}")
