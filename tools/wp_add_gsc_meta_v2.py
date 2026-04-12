#!/usr/bin/env python3
"""
Add Google Search Console Verification Meta Tag to WordPress
Date: 2026-02-17

This script will:
1. Login to WordPress
2. Navigate to Divi Theme Options → Integration
3. Add the verification meta tag to the head
4. Verify it appears in page source
"""

import time
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
            print("Step 1: Logging into WordPress...")
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

            # Check for CAPTCHA
            captcha_input = page.locator('input[name="wpsec_captcha_answer"]')
            if captcha_input.count() > 0:
                print("ERROR: CAPTCHA detected - cannot proceed automatically")
                page.screenshot(path="/tmp/captcha_detected.png")
                return "CAPTCHA_NEEDED"

            # Submit
            print("Submitting login...")
            page.locator('#wp-submit').click()
            page.wait_for_load_state('networkidle')
            time.sleep(3)

            page.screenshot(path="/tmp/after_login.png")
            print(f"Current URL: {page.url}")

            # Check if login succeeded
            if "wp-admin" in page.url and "login" not in page.url.lower():
                print("SUCCESS: Logged into WordPress!")
            else:
                print("Login may have failed. Screenshot: /tmp/after_login.png")
                # Check for error messages
                error_msg = page.locator('#login_error')
                if error_msg.count() > 0:
                    print(f"Login error: {error_msg.text_content()}")
                    return "LOGIN_FAILED"

            # Step 2: Navigate to Divi Theme Options
            print("\n" + "="*60)
            print("Step 2: Navigating to Divi Theme Options...")
            print("="*60)

            page.goto("https://purebrain.ai/wp-admin/admin.php?page=et_divi_options")
            page.wait_for_load_state('networkidle')
            time.sleep(5)

            page.screenshot(path="/tmp/divi_options.png")
            print("Screenshot: /tmp/divi_options.png")
            print(f"Current URL: {page.url}")

            # Step 3: Click on Integration tab
            print("\n" + "="*60)
            print("Step 3: Looking for Integration tab...")
            print("="*60)

            # Look for Integration tab
            integration_link = page.locator('a[data-panel="integration"]')
            if integration_link.count() > 0:
                print("Found Integration tab (by data-panel)!")
                integration_link.click()
                time.sleep(2)
            else:
                # Try text match
                integration_link = page.locator('text=Integration')
                if integration_link.count() > 0:
                    print("Found Integration tab (by text)!")
                    integration_link.first.click()
                    time.sleep(2)
                else:
                    print("Integration tab not found - taking screenshot")
                    page.screenshot(path="/tmp/no_integration_tab.png")

            page.screenshot(path="/tmp/divi_integration.png")
            print("Screenshot: /tmp/divi_integration.png")

            # Step 4: Find and fill head code area
            print("\n" + "="*60)
            print("Step 4: Adding meta tag to head code...")
            print("="*60)

            # Look for head code textarea
            head_code_selectors = [
                '#et_divi\\[divi_integration_head\\]',
                'textarea[name="et_divi[divi_integration_head]"]',
                '#divi_integration_head',
                'textarea[id*="head"]'
            ]

            head_code_area = None
            for selector in head_code_selectors:
                try:
                    area = page.locator(selector)
                    if area.count() > 0:
                        head_code_area = area
                        print(f"Found head code area with selector: {selector}")
                        break
                except:
                    pass

            if head_code_area:
                # Get current value
                current_value = head_code_area.input_value()
                print(f"Current head code length: {len(current_value)} chars")

                if GSC_META_TAG in current_value:
                    print("Meta tag already exists!")
                else:
                    new_value = current_value + "\n" + GSC_META_TAG if current_value.strip() else GSC_META_TAG
                    head_code_area.fill(new_value)
                    print("Meta tag added to head code area!")

                page.screenshot(path="/tmp/meta_tag_added.png")
                print("Screenshot: /tmp/meta_tag_added.png")

                # Step 5: Save changes
                print("\n" + "="*60)
                print("Step 5: Saving changes...")
                print("="*60)

                save_button = page.locator('#epanel-save')
                if save_button.count() > 0:
                    save_button.click()
                    time.sleep(5)
                    page.screenshot(path="/tmp/divi_saved.png")
                    print("Divi options saved!")
                else:
                    # Try other save button selectors
                    save_btn = page.locator('input[value="Save Changes"], button:has-text("Save")')
                    if save_btn.count() > 0:
                        save_btn.first.click()
                        time.sleep(5)
                        page.screenshot(path="/tmp/divi_saved.png")
                        print("Changes saved!")
            else:
                print("Head code area not found!")
                page.screenshot(path="/tmp/no_head_code.png")

            # Step 6: Verify on frontend
            print("\n" + "="*60)
            print("Step 6: Verifying meta tag on frontend...")
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
            import traceback
            traceback.print_exc()
            page.screenshot(path="/tmp/error_gsc.png")
            return f"ERROR: {e}"

        finally:
            browser.close()

if __name__ == "__main__":
    result = add_gsc_verification()
    print(f"\nFinal Result: {result}")
