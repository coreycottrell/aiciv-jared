#!/usr/bin/env python3
"""
Check WordPress settings - simplified
"""

import time
from playwright.sync_api import sync_playwright

WP_USER = "Aether"
WP_PASSWORD = "b&JJRfs)6yuSWJCc7WiFY)G8"

def check_settings():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        # Login
        print("Logging in...")
        page.goto("https://purebrain.ai/wp-admin", timeout=60000)
        time.sleep(3)

        # Click username/password option
        try:
            link = page.locator('text=Log in with username and password')
            if link.count() > 0:
                link.click()
                time.sleep(2)
        except:
            pass

        page.fill('#user_login', WP_USER)
        page.fill('#user_pass', WP_PASSWORD)
        page.click('#wp-submit')
        time.sleep(5)

        # Check Reading Settings
        print("Checking Reading Settings...")
        page.goto("https://purebrain.ai/wp-admin/options-reading.php", timeout=60000)
        time.sleep(5)
        page.screenshot(path="/tmp/wp_reading_settings.png")
        print("Screenshot: /tmp/wp_reading_settings.png")

        # Check Posts
        print("Checking Posts list...")
        page.goto("https://purebrain.ai/wp-admin/edit.php", timeout=60000)
        time.sleep(5)
        page.screenshot(path="/tmp/wp_posts_list.png")
        print("Screenshot: /tmp/wp_posts_list.png")

        # Check Pages
        print("Checking Pages list...")
        page.goto("https://purebrain.ai/wp-admin/edit.php?post_type=page", timeout=60000)
        time.sleep(5)
        page.screenshot(path="/tmp/wp_pages_list.png")
        print("Screenshot: /tmp/wp_pages_list.png")

        print("\nDone!")
        time.sleep(3)
        browser.close()

if __name__ == "__main__":
    check_settings()
