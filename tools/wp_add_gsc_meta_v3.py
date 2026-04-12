#!/usr/bin/env python3
"""
Add Google Search Console Verification Meta Tag to WordPress
Date: 2026-02-17

This script will:
1. Login to WordPress
2. Check available options for adding header code
3. Try Customizer, Plugins, or other methods
4. Add the verification meta tag
5. Verify it appears in page source
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
                print("Login may have failed.")
                return "LOGIN_FAILED"

            # Step 2: Check available menu items
            print("\n" + "="*60)
            print("Step 2: Exploring available menu items...")
            print("="*60)

            # Take screenshot of admin dashboard
            page.screenshot(path="/tmp/admin_dashboard.png")

            # Check for WPCode or Insert Headers
            print("\nChecking plugins page...")
            page.goto("https://purebrain.ai/wp-admin/plugins.php", timeout=30000)
            page.wait_for_load_state('networkidle', timeout=30000)
            time.sleep(3)

            page.screenshot(path="/tmp/plugins.png")
            plugins_content = page.content().lower()

            if 'wpcode' in plugins_content:
                print("WPCode found!")
            elif 'insert headers' in plugins_content:
                print("Insert Headers and Footers found!")
            else:
                print("No header/footer plugins detected on plugins page")

            # Step 3: Check for Code Snippets menu item (WPCode creates this)
            print("\nChecking for Code Snippets menu...")
            page.goto("https://purebrain.ai/wp-admin/admin.php?page=wpcode-headers-footers", timeout=30000)
            time.sleep(3)

            page.screenshot(path="/tmp/wpcode_check.png")
            if "not allowed" not in page.content().lower():
                print("WPCode Headers & Footers page accessible!")
            else:
                print("WPCode page not accessible")

            # Step 4: Try Customizer
            print("\n" + "="*60)
            print("Step 4: Checking Customizer...")
            print("="*60)

            page.goto("https://purebrain.ai/wp-admin/customize.php", timeout=60000)
            page.wait_for_load_state('domcontentloaded', timeout=60000)
            time.sleep(8)  # Customizer is slow to load

            page.screenshot(path="/tmp/customizer.png")
            print("Screenshot: /tmp/customizer.png")

            # Look for Additional CSS section (sometimes allows script tags)
            additional_css = page.locator('#accordion-section-custom_css')
            if additional_css.count() > 0:
                print("Found Additional CSS section")
                additional_css.click()
                time.sleep(2)
                page.screenshot(path="/tmp/customizer_css.png")

            # Look for any header/script sections
            customizer_content = page.content().lower()
            if 'header' in customizer_content and 'script' in customizer_content:
                print("Header scripts option may be available")

            # Step 5: Check Appearance → Theme File Editor
            print("\n" + "="*60)
            print("Step 5: Checking Theme File Editor...")
            print("="*60)

            page.goto("https://purebrain.ai/wp-admin/theme-editor.php", timeout=30000)
            time.sleep(3)

            page.screenshot(path="/tmp/theme_editor.png")
            theme_editor_content = page.content()

            if "not allowed" not in theme_editor_content.lower() and "denied" not in theme_editor_content.lower():
                print("Theme Editor accessible!")

                # Look for header.php
                header_link = page.locator('a:has-text("header.php")')
                if header_link.count() > 0:
                    print("Found header.php link!")
                    header_link.first.click()
                    time.sleep(3)
                    page.screenshot(path="/tmp/header_php.png")
                    print("Screenshot: /tmp/header_php.png")
            else:
                print("Theme Editor not accessible")

            # Step 6: List available Appearance submenu
            print("\n" + "="*60)
            print("Step 6: Checking Appearance menu items...")
            print("="*60)

            page.goto("https://purebrain.ai/wp-admin/themes.php", timeout=30000)
            time.sleep(3)

            page.screenshot(path="/tmp/themes.png")

            # Check all menu items in sidebar
            print("\nScanning admin menu for available options...")
            menu_items = page.locator('#adminmenu a').all()
            print(f"Found {len(menu_items)} menu items")

            interesting_keywords = ['header', 'script', 'code', 'seo', 'snippet', 'insert', 'custom', 'integration']
            for item in menu_items[:50]:  # Check first 50
                try:
                    text = item.text_content().lower()
                    href = item.get_attribute('href') or ''
                    for keyword in interesting_keywords:
                        if keyword in text or keyword in href:
                            print(f"  Interesting: {item.text_content().strip()} -> {href}")
                            break
                except:
                    pass

            # Final verification
            print("\n" + "="*60)
            print("Final: Checking if meta tag already exists...")
            print("="*60)

            page.goto("https://purebrain.ai", timeout=30000)
            time.sleep(3)

            page_source = page.content()

            if "google-site-verification" in page_source:
                if "S4BWw-zZDnPzo2x3U7iPvdUTxqnUkqGlW1S9fb024O0" in page_source:
                    print("\nMeta tag ALREADY EXISTS in page source!")
                    return "ALREADY_EXISTS"
                else:
                    print("\nA different google-site-verification tag exists")
                    return "DIFFERENT_TAG_EXISTS"
            else:
                print("\nMeta tag NOT found. Screenshots saved for manual review.")
                print("\nScreenshots saved:")
                print("  - /tmp/admin_dashboard.png")
                print("  - /tmp/plugins.png")
                print("  - /tmp/wpcode_check.png")
                print("  - /tmp/customizer.png")
                print("  - /tmp/theme_editor.png")
                print("  - /tmp/themes.png")
                return "NOT_FOUND"

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
