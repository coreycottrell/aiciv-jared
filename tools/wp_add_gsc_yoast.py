#!/usr/bin/env python3
"""
Add Google Search Console Meta Tag via Yoast SEO
Date: 2026-02-17

Yoast SEO has a "Webmaster Tools" section where you can add Google Site Verification
"""

import time
from playwright.sync_api import sync_playwright

WP_URL = "https://purebrain.ai/wp-admin"
WP_USER = "Aether"
WP_PASSWORD = "NW2u!JLQ3!Bt$XD$7CWzz5Z@"

# Just the verification CODE (not full meta tag - Yoast wraps it)
GSC_VERIFICATION_CODE = "S4BWw-zZDnPzo2x3U7iPvdUTxqnUkqGlW1S9fb024O0"

def add_via_yoast():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        page.set_default_timeout(20000)

        try:
            # Login
            print("Logging in...")
            page.goto(WP_URL)
            time.sleep(3)

            username_pass_link = page.locator('text=Log in with username and password')
            if username_pass_link.count() > 0:
                username_pass_link.click()
                time.sleep(2)

            page.locator('#user_login').fill(WP_USER)
            page.locator('#user_pass').fill(WP_PASSWORD)
            page.locator('#wp-submit').click()
            time.sleep(5)

            if "wp-admin" not in page.url:
                print("Login failed")
                return "LOGIN_FAILED"

            print("Logged in!")

            # Try Yoast SEO Settings - Webmaster Tools
            print("\nNavigating to Yoast Settings...")

            # Yoast moved their settings in recent versions
            yoast_urls = [
                "https://purebrain.ai/wp-admin/admin.php?page=wpseo_page_settings#/site-connections",
                "https://purebrain.ai/wp-admin/admin.php?page=wpseo_dashboard#/site-connections",
                "https://purebrain.ai/wp-admin/admin.php?page=wpseo_page_settings",
                "https://purebrain.ai/wp-admin/admin.php?page=wpseo_tools",
                "https://purebrain.ai/wp-admin/admin.php?page=wpseo_dashboard"
            ]

            for url in yoast_urls:
                print(f"\nTrying: {url}")
                try:
                    page.goto(url, wait_until='domcontentloaded')
                    time.sleep(3)
                    page.screenshot(path=f"/tmp/yoast_{url.split('=')[-1][:20]}.png")

                    content = page.content().lower()
                    if "not allowed" in content:
                        print("  Not accessible")
                        continue

                    # Check for Google verification field
                    if "google" in content and ("verification" in content or "site connections" in content):
                        print("  Found Google verification section!")
                        break
                except Exception as e:
                    print(f"  Error: {e}")

            # Look for the Site Connections or Webmaster Tools
            print("\nLooking for Site Connections link...")
            site_conn = page.locator('a:has-text("Site connections"), a:has-text("Webmaster")')
            if site_conn.count() > 0:
                print("Found Site Connections!")
                site_conn.first.click()
                time.sleep(3)
                page.screenshot(path="/tmp/yoast_site_connections.png")

            # Look for Google input field
            print("\nLooking for Google verification input...")
            google_input_selectors = [
                'input[name*="google"]',
                'input[id*="google"]',
                'input[placeholder*="Google"]',
                '#googleverify',
                '#google-verification-code',
                'input[aria-label*="Google"]'
            ]

            google_input = None
            for selector in google_input_selectors:
                try:
                    inp = page.locator(selector)
                    if inp.count() > 0:
                        google_input = inp.first
                        print(f"  Found input: {selector}")
                        break
                except:
                    pass

            if google_input:
                current_value = google_input.input_value()
                print(f"  Current value: '{current_value}'")

                if GSC_VERIFICATION_CODE in current_value:
                    print("  Verification code already set!")
                else:
                    google_input.fill(GSC_VERIFICATION_CODE)
                    print("  Verification code entered!")
                    page.screenshot(path="/tmp/yoast_code_entered.png")

                    # Save
                    save_btn = page.locator('button:has-text("Save"), input[value="Save"]')
                    if save_btn.count() > 0:
                        save_btn.first.click()
                        time.sleep(3)
                        print("  Saved!")
                        page.screenshot(path="/tmp/yoast_saved.png")
            else:
                print("  Google verification input not found")
                page.screenshot(path="/tmp/yoast_no_input.png")

            # Verify on frontend
            print("\nVerifying on frontend...")
            page.goto("https://purebrain.ai", wait_until='domcontentloaded')
            time.sleep(3)

            page_source = page.content()
            if "google-site-verification" in page_source and GSC_VERIFICATION_CODE in page_source:
                print("SUCCESS! Meta tag verified!")
                return "VERIFIED"
            else:
                print("Meta tag not found yet")
                return "NOT_VERIFIED"

        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            page.screenshot(path="/tmp/error.png")
            return f"ERROR: {e}"

        finally:
            browser.close()

if __name__ == "__main__":
    result = add_via_yoast()
    print(f"\nResult: {result}")
