#!/usr/bin/env python3
"""
WordPress PureBrain 2.0 Page Deep Inspection
Directly access the PureBrain 2.0 draft page and analyze its content
"""

import os
import sys
from datetime import datetime
from playwright.sync_api import sync_playwright

# Create screenshots directory
SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/sandbox/wp_recon/purebrain20"
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
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()

        # Login
        print(f"Navigating to {WP_URL}...")
        page.goto(WP_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)

        # Handle GoDaddy SSO
        password_login_link = page.get_by_text("Log in with username and password")
        if password_login_link.count() > 0:
            print("Found GoDaddy SSO page, clicking username/password option...")
            password_login_link.click()
            page.wait_for_timeout(2000)

        if page.locator("#user_login").is_visible():
            print("Logging in...")
            page.fill("#user_login", WP_USER)
            page.fill("#user_pass", WP_PASS)
            page.click("#wp-submit")
            page.wait_for_timeout(5000)

        print(f"Current URL after login: {page.url}")

        # Go to drafts and find PureBrain 2.0
        print("\nNavigating to draft pages...")
        page.goto("https://purebrain.ai/wp-admin/edit.php?post_type=page&post_status=draft", wait_until="domcontentloaded")
        page.wait_for_timeout(3000)
        screenshot(page, "01_drafts_list")

        # Find PureBrain 2.0 and click it
        print("Looking for PureBrain 2.0...")
        pb20_link = page.locator("a.row-title:has-text('PureBrain 2.0')")
        if pb20_link.count() > 0:
            print("Found PureBrain 2.0! Clicking to open editor...")
            pb20_link.click()
            page.wait_for_timeout(5000)
            screenshot(page, "02_purebrain20_editor")

            # Analyze the editor
            print("\n=== PureBrain 2.0 Page Analysis ===")
            print(f"URL: {page.url}")

            # Check for Elementor
            is_elementor = page.locator("button:has-text('Edit with Elementor')").count() > 0
            edit_elementor_btn = page.locator("a:has-text('Edit with Elementor'), button:has-text('Edit with Elementor')")

            if is_elementor or edit_elementor_btn.count() > 0:
                print("Builder: ELEMENTOR")
                print("  'Edit with Elementor' button is present")

                # Get page info from sidebar
                page_info = {}

                # Status
                status_elem = page.locator(".editor-post-status button, .components-button:has-text('Draft')")
                if status_elem.count() > 0:
                    page_info['status'] = 'Draft (from sidebar)'

                # Template
                template_elem = page.locator("text=Elementor Canvas")
                if template_elem.count() > 0:
                    page_info['template'] = 'Elementor Canvas'

                print(f"  Page info: {page_info}")

                # Click "Edit with Elementor" to see actual content
                print("\nOpening Elementor editor...")
                if edit_elementor_btn.count() > 0:
                    edit_elementor_btn.first.click()
                    page.wait_for_timeout(10000)  # Elementor takes time to load
                    screenshot(page, "03_elementor_editor")

                    # Wait for Elementor to fully load
                    print("Waiting for Elementor to load fully...")
                    page.wait_for_timeout(5000)
                    screenshot(page, "04_elementor_loaded")

                    # Check what's in the Elementor editor
                    print("\n=== Elementor Content Analysis ===")

                    # Check for widgets/elements
                    widgets = page.locator(".elementor-widget")
                    print(f"Widgets found: {widgets.count()}")

                    # Check for sections
                    sections = page.locator(".elementor-section")
                    print(f"Sections found: {sections.count()}")

                    # Check for empty state
                    empty_state = page.locator(".elementor-add-section-drag-title")
                    if empty_state.count() > 0:
                        print("Page appears to be EMPTY - showing 'Drag widget here' prompt")

                    # Look for specific content types
                    headings = page.locator(".elementor-heading-title")
                    print(f"Heading elements: {headings.count()}")

                    text_widgets = page.locator(".elementor-text-editor")
                    print(f"Text widgets: {text_widgets.count()}")

                    buttons = page.locator(".elementor-button")
                    print(f"Buttons: {buttons.count()}")

                    forms = page.locator(".elementor-form")
                    print(f"Forms: {forms.count()}")

                    # Take full page scroll shots
                    print("\nCapturing full page content...")
                    page.evaluate("window.scrollTo(0, 0)")
                    screenshot(page, "05_content_top")

                    page.evaluate("window.scrollTo(0, document.body.scrollHeight/2)")
                    page.wait_for_timeout(1000)
                    screenshot(page, "06_content_middle")

                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    page.wait_for_timeout(1000)
                    screenshot(page, "07_content_bottom")

            else:
                print("Builder: Gutenberg (standard block editor)")

                # List blocks
                blocks = page.locator(".wp-block")
                print(f"Blocks found: {blocks.count()}")

            # Check for existing pricing/payment content
            print("\n=== Looking for existing pricing/payment content ===")
            pricing_text = page.locator("text=/pricing|price|\\$|payment|subscribe|plan/i")
            print(f"Pricing-related text elements: {pricing_text.count()}")

            stripe_elements = page.locator("text=/stripe|checkout|cart/i")
            print(f"Stripe/checkout elements: {stripe_elements.count()}")

        else:
            print("ERROR: Could not find PureBrain 2.0 page!")

            # List what we can see
            all_titles = page.locator("a.row-title").all()
            print("Available pages:")
            for title in all_titles:
                print(f"  - {title.text_content()}")

        # Try preview URL
        print("\n=== Checking Preview ===")
        # Go back to list
        page.goto("https://purebrain.ai/wp-admin/edit.php?post_type=page&post_status=draft", wait_until="domcontentloaded")
        page.wait_for_timeout(2000)

        # Hover to reveal Preview link
        pb20_row = page.locator("tr:has-text('PureBrain 2.0')")
        if pb20_row.count() > 0:
            pb20_row.hover()
            page.wait_for_timeout(500)
            screenshot(page, "08_row_hover")

            # Check for preview link
            preview_link = pb20_row.locator("a:has-text('Preview')")
            if preview_link.count() > 0:
                preview_url = preview_link.get_attribute("href")
                print(f"Preview URL: {preview_url}")

        print(f"\nFinal URL: {page.url}")
        browser.close()

if __name__ == "__main__":
    main()
