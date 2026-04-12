#!/usr/bin/env python3
"""
WordPress Admin Reconnaissance - Pure Brain 2.0
Navigate to wp-admin, login, find and analyze the Pure Brain 2.0 draft page
"""

import os
import sys
from datetime import datetime
from playwright.sync_api import sync_playwright

# Create screenshots directory
SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/sandbox/wp_recon"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# Credentials from .env
WP_URL = "https://purebrain.ai/wp-admin/"
WP_USER = "Aether"
WP_PASS = "b&JJRfs)6yuSWJCc7WiFY)G8"

def screenshot(page, name):
    """Take a screenshot with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"{SCREENSHOT_DIR}/{timestamp}_{name}.png"
    page.screenshot(path=path, full_page=True)
    print(f"Screenshot saved: {path}")
    return path

def main():
    with sync_playwright() as p:
        # Launch browser (headless for server environment)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()

        print(f"Navigating to {WP_URL}...")
        page.goto(WP_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)
        screenshot(page, "01_login_page")

        # Check if we're on GoDaddy SSO login page
        # Need to click "Log in with username and password" to reveal traditional form
        password_login_link = page.get_by_text("Log in with username and password")
        if password_login_link.count() > 0:
            print("Found GoDaddy SSO page, clicking username/password option...")
            password_login_link.click()
            page.wait_for_timeout(2000)
            screenshot(page, "02_username_form")

        # Check if we're on login page
        if page.locator("#user_login").is_visible():
            print("On login page, entering credentials...")
            page.fill("#user_login", WP_USER)
            page.fill("#user_pass", WP_PASS)
            screenshot(page, "03_credentials_filled")

            # Click login and wait for navigation (not network idle)
            print("Clicking Log In button...")
            page.click("#wp-submit")

            # Wait for navigation or timeout, don't require network idle
            try:
                page.wait_for_url("**/wp-admin/**", timeout=15000)
            except Exception as e:
                print(f"URL wait timeout: {e}")

            page.wait_for_timeout(3000)
            screenshot(page, "04_after_login")
        else:
            print("Login form not visible, checking current state...")
            screenshot(page, "02_current_state")

        # Check current state
        print(f"Current URL: {page.url}")

        # Check if login successful or error
        error_msg = page.locator("#login_error")
        if error_msg.count() > 0 and error_msg.is_visible():
            print(f"Login error detected!")
            screenshot(page, "04_login_error")
            error_text = error_msg.text_content()
            print(f"Error: {error_text}")
        else:
            print("No login error visible")

        # Navigate to Pages
        print("\nNavigating to Pages...")
        page.goto("https://purebrain.ai/wp-admin/edit.php?post_type=page", wait_until="domcontentloaded")
        page.wait_for_timeout(3000)
        screenshot(page, "05_pages_list")

        # Check if we got redirected back to login
        if "wp-login" in page.url:
            print("Redirected to login - credentials may be incorrect or session issue")
            # Try with App Password instead
            print("\nTrying with Application Password...")
            password_login_link = page.get_by_text("Log in with username and password")
            if password_login_link.count() > 0:
                password_login_link.click()
                page.wait_for_timeout(2000)

            page.fill("#user_login", WP_USER)
            page.fill("#user_pass", "I9jppb5dpNyfdQihehsBV0k7")  # App password
            page.click("#wp-submit")
            page.wait_for_timeout(5000)
            screenshot(page, "05b_app_password_attempt")

            page.goto("https://purebrain.ai/wp-admin/edit.php?post_type=page", wait_until="domcontentloaded")
            page.wait_for_timeout(3000)
            screenshot(page, "05c_pages_after_app_password")

        # Try searching for Pure Brain 2.0
        print("\nSearching for 'Pure Brain 2.0'...")
        search_box = page.locator("#post-search-input")
        if search_box.count() > 0 and search_box.is_visible():
            search_box.fill("Pure Brain 2.0")
            page.click("#search-submit")
            page.wait_for_timeout(3000)
            screenshot(page, "06_search_results")

            # Check if we found results
            pages_table = page.locator("#the-list")
            if pages_table.count() > 0:
                rows = pages_table.locator("tr").all()
                print(f"Found {len(rows)} search results")
                for i, row in enumerate(rows[:5]):  # First 5 results
                    title_elem = row.locator(".row-title")
                    if title_elem.count() > 0:
                        title = title_elem.text_content()
                        print(f"  Result {i+1}: {title}")

                # Click first result to open editor
                first_row = pages_table.locator("tr").first
                title_link = first_row.locator(".row-title")
                if title_link.count() > 0:
                    print(f"Clicking to edit: {title_link.text_content()}")
                    title_link.click()
                    page.wait_for_timeout(5000)  # Wait for editor to load
                    screenshot(page, "07_page_editor")

                    # Analyze the editor
                    analyze_editor(page)

                    # Take another screenshot scrolled down
                    page.evaluate("window.scrollBy(0, 500)")
                    screenshot(page, "08_page_content_scrolled")
        else:
            print("Search box not found, checking page list directly...")
            screenshot(page, "06_no_search_box")

            # Try to list visible pages
            pages_table = page.locator("#the-list")
            if pages_table.count() > 0:
                rows = pages_table.locator("tr").all()
                print(f"Found {len(rows)} pages in list")
                for i, row in enumerate(rows[:10]):
                    title_elem = row.locator(".row-title")
                    if title_elem.count() > 0:
                        title = title_elem.text_content()
                        print(f"  Page {i+1}: {title}")
                        if "pure brain" in title.lower():
                            print(f"    ^ Found target page!")

        # Also check drafts specifically
        print("\nChecking draft pages...")
        page.goto("https://purebrain.ai/wp-admin/edit.php?post_type=page&post_status=draft", wait_until="domcontentloaded")
        page.wait_for_timeout(3000)
        screenshot(page, "09_drafts_list")

        pages_table = page.locator("#the-list")
        if pages_table.count() > 0:
            rows = pages_table.locator("tr").all()
            print(f"Found {len(rows)} draft pages")
            for i, row in enumerate(rows[:10]):
                title_elem = row.locator(".row-title")
                if title_elem.count() > 0:
                    title = title_elem.text_content()
                    print(f"  Draft {i+1}: {title}")

        # Print current URL for debugging
        print(f"\nFinal URL: {page.url}")
        print(f"Page Title: {page.title()}")

        browser.close()

def analyze_editor(page):
    """Analyze what page builder/editor is being used"""
    print("\n--- Editor Analysis ---")

    # Check for various editors
    is_gutenberg = page.locator(".edit-post-visual-editor, .block-editor").count() > 0
    is_elementor = page.locator("#elementor").count() > 0 or "elementor" in page.url
    has_divi = page.locator("[class*='et_pb']").count() > 0
    is_classic = page.locator("#wp-content-wrap").count() > 0

    # Check URL patterns
    url = page.url
    if "action=elementor" in url:
        is_elementor = True

    if is_gutenberg:
        print("Editor: Gutenberg (Block Editor)")

        # List blocks
        blocks = page.locator(".block-editor-block-list__layout > .wp-block").all()
        if blocks:
            print(f"  Blocks found: {len(blocks)}")
            for i, block in enumerate(blocks[:10]):
                block_type = block.get_attribute("data-type")
                if block_type:
                    print(f"    Block {i+1}: {block_type}")

    elif is_elementor:
        print("Editor: Elementor")
    elif has_divi:
        print("Editor: Divi Builder")
    elif is_classic:
        print("Editor: Classic Editor")
    else:
        print("Editor: Unknown or custom")

    # Get page title
    title_input = page.locator(".editor-post-title__input, #title, [aria-label='Add title']")
    if title_input.count() > 0:
        try:
            title = title_input.first.input_value()
            print(f"Page Title: {title}")
        except:
            # For contenteditable elements
            title = title_input.first.text_content()
            print(f"Page Title: {title}")

    # Get page status
    status_btn = page.locator(".editor-post-status, .edit-post-post-status")
    if status_btn.count() > 0:
        print(f"Status element found")

    # Get page URL/slug
    permalink = page.locator(".editor-post-url__link, #sample-permalink a")
    if permalink.count() > 0:
        print(f"Permalink: {permalink.first.text_content()}")

if __name__ == "__main__":
    main()
