#!/usr/bin/env python3
"""
Add Google Search Console Verification Meta Tag to WordPress
Date: 2026-02-17 - Fast version with short timeouts
"""

import time
from playwright.sync_api import sync_playwright

WP_URL = "https://purebrain.ai/wp-admin"
WP_USER = "Aether"
WP_PASSWORD = "NW2u!JLQ3!Bt$XD$7CWzz5Z@"
GSC_META_TAG = '<meta name="google-site-verification" content="S4BWw-zZDnPzo2x3U7iPvdUTxqnUkqGlW1S9fb024O0" />'

def add_gsc_verification():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        page.set_default_timeout(15000)  # 15 second timeout

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

            page.screenshot(path="/tmp/after_login.png")
            print(f"URL after login: {page.url}")

            if "wp-admin" not in page.url:
                print("Login failed")
                return "LOGIN_FAILED"

            print("Logged in successfully!")

            # Check plugins
            print("\nChecking plugins page...")
            try:
                page.goto("https://purebrain.ai/wp-admin/plugins.php", wait_until='domcontentloaded')
                time.sleep(5)
                page.screenshot(path="/tmp/plugins.png")
                print("Plugins page captured")
            except Exception as e:
                print(f"Plugins page error: {e}")

            # Check for WPCode directly
            print("\nChecking WPCode...")
            try:
                page.goto("https://purebrain.ai/wp-admin/admin.php?page=wpcode-headers-footers", wait_until='domcontentloaded')
                time.sleep(3)
                page.screenshot(path="/tmp/wpcode.png")
                content = page.content().lower()
                if "not allowed" not in content:
                    print("WPCode accessible!")
                else:
                    print("WPCode not accessible")
            except Exception as e:
                print(f"WPCode check error: {e}")

            # Check Rank Math SEO (popular SEO plugin)
            print("\nChecking Rank Math...")
            try:
                page.goto("https://purebrain.ai/wp-admin/admin.php?page=rank-math", wait_until='domcontentloaded')
                time.sleep(3)
                page.screenshot(path="/tmp/rankmath.png")
                content = page.content().lower()
                if "not allowed" not in content and "rank math" in content:
                    print("Rank Math found!")
            except Exception as e:
                print(f"Rank Math check: {e}")

            # Check Yoast SEO
            print("\nChecking Yoast...")
            try:
                page.goto("https://purebrain.ai/wp-admin/admin.php?page=wpseo_dashboard", wait_until='domcontentloaded')
                time.sleep(3)
                page.screenshot(path="/tmp/yoast.png")
            except Exception as e:
                print(f"Yoast check: {e}")

            # Check admin menu items
            print("\nCapturing dashboard with menu...")
            page.goto("https://purebrain.ai/wp-admin/", wait_until='domcontentloaded')
            time.sleep(3)
            page.screenshot(path="/tmp/dashboard_menu.png", full_page=True)

            # Scan menu for interesting items
            menu_html = page.locator('#adminmenu').inner_html()
            interesting = ['header', 'seo', 'code', 'snippet', 'script', 'rankmath', 'yoast', 'custom', 'integration', 'wpcode']
            print("\nMenu items found:")
            for word in interesting:
                if word in menu_html.lower():
                    print(f"  Found '{word}' in menu!")

            # Check frontend for existing tag
            print("\nChecking frontend for meta tag...")
            page.goto("https://purebrain.ai", wait_until='domcontentloaded')
            time.sleep(3)

            page_source = page.content()
            if "google-site-verification" in page_source:
                print("Meta tag already exists!")
                # Extract the value
                import re
                match = re.search(r'google-site-verification["\s]+content="([^"]+)"', page_source)
                if match:
                    print(f"Existing value: {match.group(1)}")
                return "TAG_EXISTS"
            else:
                print("Meta tag NOT found in page source")
                return "TAG_NOT_FOUND"

        except Exception as e:
            print(f"ERROR: {e}")
            page.screenshot(path="/tmp/error.png")
            return f"ERROR: {e}"

        finally:
            browser.close()

if __name__ == "__main__":
    result = add_gsc_verification()
    print(f"\nResult: {result}")
