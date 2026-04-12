#!/usr/bin/env python3
"""
Clear WordPress cache and verify GSC meta tag
Date: 2026-02-17
"""

import time
from playwright.sync_api import sync_playwright

WP_URL = "https://purebrain.ai/wp-admin"
WP_USER = "Aether"
WP_PASSWORD = "NW2u!JLQ3!Bt$XD$7CWzz5Z@"
GSC_VERIFICATION_CODE = "S4BWw-zZDnPzo2x3U7iPvdUTxqnUkqGlW1S9fb024O0"

def clear_cache_and_verify():
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

            # Look for cache plugins in toolbar
            page.screenshot(path="/tmp/admin_toolbar.png")
            admin_bar = page.locator('#wp-admin-bar-root-default').inner_html()
            print(f"Admin bar contains: {'cache' in admin_bar.lower()}")

            # Check for GoDaddy caching (they're on GoDaddy hosting)
            print("\nChecking for GoDaddy cache options...")
            godaddy_urls = [
                "https://purebrain.ai/wp-admin/admin.php?page=gd-caching",
                "https://purebrain.ai/wp-admin/admin.php?page=godaddy-caching"
            ]

            for url in godaddy_urls:
                try:
                    page.goto(url, wait_until='domcontentloaded')
                    time.sleep(2)
                    content = page.content().lower()
                    if "not allowed" not in content and "cache" in content:
                        print(f"Found caching page: {url}")
                        page.screenshot(path="/tmp/godaddy_cache.png")
                        # Try to clear cache
                        clear_btn = page.locator('button:has-text("Clear"), a:has-text("Clear"), input[value*="Clear"]')
                        if clear_btn.count() > 0:
                            clear_btn.first.click()
                            time.sleep(3)
                            print("Cache cleared!")
                        break
                except:
                    pass

            # Check WP Super Cache
            print("\nChecking WP Super Cache...")
            try:
                page.goto("https://purebrain.ai/wp-admin/options-general.php?page=wpsupercache", wait_until='domcontentloaded')
                time.sleep(2)
                content = page.content().lower()
                if "not allowed" not in content and "cache" in content:
                    print("WP Super Cache found!")
                    page.screenshot(path="/tmp/wp_super_cache.png")
            except:
                pass

            # Try clearing from admin bar
            print("\nLooking for cache clear in admin bar...")
            cache_clear = page.locator('#wp-admin-bar-gdh_flush_all a, #wp-admin-bar-supercache a, a:has-text("Flush Cache"), a:has-text("Clear Cache")')
            if cache_clear.count() > 0:
                print("Found cache clear button in toolbar!")
                cache_clear.first.click()
                time.sleep(3)
                print("Clicked clear cache")

            # Now test with cache-busting query parameter
            print("\nTesting frontend with cache bust...")
            cache_bust = str(int(time.time()))
            page.goto(f"https://purebrain.ai/?nocache={cache_bust}", wait_until='domcontentloaded')
            time.sleep(3)

            page_source = page.content()
            if "google-site-verification" in page_source:
                print("\nFOUND: google-site-verification in source!")
                if GSC_VERIFICATION_CODE in page_source:
                    print("SUCCESS: Correct verification code found!")
                    return "VERIFIED"
                else:
                    print("WARNING: Different verification code found")
            else:
                print("NOT FOUND: google-site-verification not in page source")

            # Save head section for analysis
            head_html = page.locator('head').inner_html()
            with open("/tmp/purebrain_head_after_cache.html", "w") as f:
                f.write(head_html)
            print("\nHead saved to /tmp/purebrain_head_after_cache.html")

            # Check if Yoast generates output
            if "yoast" in head_html.lower():
                print("Yoast output IS in head")
                # Check for webmaster section specifically
                if "webmaster" in head_html.lower() or "verification" in head_html.lower():
                    print("Webmaster/verification section found in Yoast output")
                else:
                    print("No webmaster section in Yoast output")
            else:
                print("No Yoast output detected in head")

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
    result = clear_cache_and_verify()
    print(f"\nResult: {result}")
