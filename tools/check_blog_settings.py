#!/usr/bin/env python3
"""
Check WordPress blog settings
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
        page.goto("https://purebrain.ai/wp-admin")
        page.wait_for_load_state('networkidle')
        time.sleep(2)

        # Click username/password option
        try:
            page.locator('text=Log in with username and password').click()
            time.sleep(2)
        except:
            pass

        page.fill('#user_login', WP_USER)
        page.fill('#user_pass', WP_PASSWORD)
        page.click('#wp-submit')
        page.wait_for_load_state('networkidle')
        time.sleep(3)

        # Check Reading Settings
        print("\nChecking Reading Settings...")
        page.goto("https://purebrain.ai/wp-admin/options-reading.php")
        page.wait_for_load_state('networkidle')
        time.sleep(2)
        page.screenshot(path="/tmp/wp_reading_settings.png")
        print("Screenshot: /tmp/wp_reading_settings.png")

        # Check the Blog page in Pages list
        print("\nChecking Blog page in Pages list...")
        page.goto("https://purebrain.ai/wp-admin/edit.php?post_type=page")
        page.wait_for_load_state('networkidle')
        time.sleep(2)
        page.screenshot(path="/tmp/wp_pages_list.png")
        print("Screenshot: /tmp/wp_pages_list.png")

        # Try to edit the Blog page directly
        print("\nLooking for Blog page to edit...")
        # Search for Blog page
        page.fill('#post-search-input', 'Blog')
        page.click('#search-submit')
        time.sleep(2)
        page.screenshot(path="/tmp/wp_pages_blog_search.png")
        print("Screenshot: /tmp/wp_pages_blog_search.png")

        # Check Posts
        print("\nChecking Posts...")
        page.goto("https://purebrain.ai/wp-admin/edit.php")
        page.wait_for_load_state('networkidle')
        time.sleep(2)
        page.screenshot(path="/tmp/wp_posts_list.png")
        print("Screenshot: /tmp/wp_posts_list.png")

        print("\nDone!")
        time.sleep(3)
        browser.close()

if __name__ == "__main__":
    check_settings()
