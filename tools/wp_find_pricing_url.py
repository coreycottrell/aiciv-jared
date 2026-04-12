#!/usr/bin/env python3
"""
Find the correct URL for PureBrain.ai 3.0 page and view it
"""

import time
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

# Configuration
WP_URL = "https://purebrain.ai/wp-admin/"
WP_USERNAME = "Aether"
WP_PASSWORD = "NW2u!JLQ3!Bt$XD$7CWzz5Z@"

# Screenshot directory
SCREENSHOT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/wp-pricing-screenshots")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

def screenshot(page, name: str):
    """Take a screenshot with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{name}.png"
    filepath = SCREENSHOT_DIR / filename
    page.screenshot(path=str(filepath), full_page=True)
    print(f"Screenshot saved: {filepath}")
    return filepath

def main():
    print("Finding PureBrain.ai 3.0 pricing page URL...")
    print()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # Login
        print("Logging in...")
        page.goto(WP_URL, wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)

        screenshot(page, "login_page")

        # Check for GoDaddy login
        godaddy_selector = 'text="Log in with username and password"'
        if page.locator(godaddy_selector).count() > 0:
            print("Clicking GoDaddy login option...")
            page.click(godaddy_selector)
            time.sleep(3)
            screenshot(page, "after_godaddy_click")

        # Wait longer for form
        print("Waiting for login form...")
        try:
            page.wait_for_selector('#user_login', timeout=30000)
            page.fill('#user_login', WP_USERNAME)
            page.fill('#user_pass', WP_PASSWORD)
            page.click('#wp-submit')
            time.sleep(5)
            screenshot(page, "after_login")
        except Exception as e:
            print(f"Login form issue: {e}")
            screenshot(page, "login_error")
            browser.close()
            return

        # Navigate to pages
        print("Navigating to Pages...")
        page.click('#menu-pages')
        time.sleep(2)
        page.click('a[href="edit.php?post_type=page"]')
        time.sleep(3)

        # Search for the page
        print("Searching for PureBrain.ai 3.0...")
        page.fill('#post-search-input', 'purebrain.ai 3.0')
        page.click('#search-submit')
        time.sleep(3)

        screenshot(page, "search_results")

        # Hover over the page to get row actions
        page_selector = 'a.row-title:has-text("PureBrain.ai 3.0")'
        matches = page.locator(page_selector)

        if matches.count() > 0:
            matches.first.hover()
            time.sleep(1)
            screenshot(page, "page_hover_view")

            # Look for View link and extract URL
            view_link = page.locator('span.view a').first
            view_url = view_link.get_attribute('href')
            print(f"\nFound View URL: {view_url}")

            # Click View to go to the page
            view_link.click()
            time.sleep(5)

            screenshot(page, "page_view_loaded")

            # Get final URL
            print(f"Final page URL: {page.url}")
            print(f"Page title: {page.title()}")

            # Scroll through the page
            for i in range(10):
                page.evaluate("window.scrollBy(0, 800)")
                time.sleep(1)
                screenshot(page, f"page_scroll_{i+1:02d}")
        else:
            print("Page not found!")

        browser.close()

if __name__ == "__main__":
    main()
