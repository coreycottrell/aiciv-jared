#!/usr/bin/env python3
"""Clear WordPress cache and verify GTM"""

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

        # Look for cache flush options in admin bar
        print("\nLooking for cache clear options...")

        # Check admin bar for cache options
        page.goto("https://purebrain.ai/wp-admin/", wait_until='domcontentloaded', timeout=60000)
        time.sleep(3)
        screenshot(page, "01_dashboard")

        # Check for GoDaddy flush cache
        admin_bar = page.query_selector('#wpadminbar')
        if admin_bar:
            bar_html = admin_bar.inner_html()
            if 'flush' in bar_html.lower() or 'cache' in bar_html.lower():
                print("Found cache option in admin bar")

        # Try Object Cache page (GoDaddy sites often have this)
        print("\nChecking Object Cache...")
        page.goto("https://purebrain.ai/wp-admin/options-general.php?page=developer",
                  wait_until='domcontentloaded', timeout=30000)
        time.sleep(2)
        screenshot(page, "02_object_cache")

        # Look for flush button
        flush_btn = page.query_selector('button:has-text("Flush"), input[value*="Flush"], a:has-text("Flush")')
        if flush_btn:
            print("Found flush button, clicking...")
            flush_btn.click()
            time.sleep(3)
            screenshot(page, "03_after_flush")

        # Check GoDaddy menu
        print("\nChecking GoDaddy menu...")
        godaddy_menu = page.query_selector('#wp-admin-bar-starter-template')
        if godaddy_menu:
            godaddy_menu.hover()
            time.sleep(1)
            screenshot(page, "04_godaddy_menu")

            # Look for cache option in submenu
            cache_link = page.query_selector('#wp-admin-bar-starter-template a:has-text("Cache"), #wp-admin-bar-starter-template a:has-text("Flush")')
            if cache_link:
                cache_link.click()
                time.sleep(3)

        # Try direct URL if GoDaddy has a flush endpoint
        print("\nTrying GoDaddy cache flush endpoints...")

        # GoDaddy-managed WordPress often has this endpoint
        endpoints = [
            "https://purebrain.ai/wp-admin/admin.php?page=starter-cache-flush",
            "https://purebrain.ai/wp-admin/admin-post.php?action=starter_cache_flush",
        ]

        for ep in endpoints:
            try:
                page.goto(ep, wait_until='domcontentloaded', timeout=10000)
                time.sleep(2)
                if 'error' not in page.content().lower():
                    print(f"  Accessed: {ep}")
            except:
                pass

        # Now verify GTM on frontend with cache-busting
        print("\nVerifying GTM on frontend...")

        # Use a cache-busting URL parameter
        cache_bust = int(time.time())
        page.goto(f"https://purebrain.ai/?nocache={cache_bust}", wait_until='domcontentloaded', timeout=60000)
        time.sleep(5)
        screenshot(page, "05_frontend")

        html = page.content()
        head = page.evaluate('() => document.head.innerHTML')

        print(f"\nPage HTML length: {len(html)}")
        print(f"Head HTML length: {len(head)}")

        # Check for GTM
        if GTM_ID in html:
            print(f"\nSUCCESS: {GTM_ID} found in page!")
        elif 'googletagmanager.com' in html:
            print("\ngoogletagmanager.com found in page!")
            import re
            ids = re.findall(r'GTM-[A-Z0-9]+', html)
            print(f"Container IDs: {set(ids)}")
        else:
            print(f"\n{GTM_ID} NOT found in page")

            # Check if GTM script is present at all
            scripts = page.query_selector_all('script')
            gtm_scripts = []
            for s in scripts:
                src = s.get_attribute('src') or ''
                inner = s.inner_text() or ''
                if 'gtm' in src.lower() or 'gtm' in inner.lower() or 'tagmanager' in src.lower():
                    gtm_scripts.append(src or inner[:100])

            if gtm_scripts:
                print("Found GTM-related scripts:")
                for s in gtm_scripts[:3]:
                    print(f"  {s}")
            else:
                print("No GTM scripts found at all")
                print("\nThis could be because:")
                print("  1. CDN/edge caching (try again in a few minutes)")
                print("  2. WordPress object cache needs clearing")
                print("  3. Theme/plugin conflict")

        browser.close()

if __name__ == "__main__":
    main()
