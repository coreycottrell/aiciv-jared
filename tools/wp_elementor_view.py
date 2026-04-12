#!/usr/bin/env python3
"""
View PureBrain 2.0 page content directly through Elementor editor
"""

import os
import sys
from datetime import datetime
from playwright.sync_api import sync_playwright

# Create screenshots directory
SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/sandbox/wp_recon/elementor"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# Credentials from .env
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
        print("Logging into WordPress...")
        page.goto("https://purebrain.ai/wp-admin/", wait_until="domcontentloaded")
        page.wait_for_timeout(2000)

        # Handle GoDaddy SSO
        password_login_link = page.get_by_text("Log in with username and password")
        if password_login_link.count() > 0:
            password_login_link.click()
            page.wait_for_timeout(2000)

        if page.locator("#user_login").is_visible():
            page.fill("#user_login", WP_USER)
            page.fill("#user_pass", WP_PASS)
            page.click("#wp-submit")
            page.wait_for_timeout(5000)

        print(f"Logged in. URL: {page.url}")

        # Go directly to Elementor editor for PureBrain 2.0 (post ID 174)
        print("\nOpening PureBrain 2.0 in Elementor...")
        page.goto("https://purebrain.ai/wp-admin/post.php?post=174&action=elementor", wait_until="domcontentloaded")
        page.wait_for_timeout(10000)  # Elementor takes time to load
        screenshot(page, "01_elementor_loading")

        # Wait for Elementor to be ready
        print("Waiting for Elementor to load...")
        try:
            page.wait_for_selector("#elementor-panel", timeout=30000)
            print("Elementor panel loaded!")
        except:
            print("Elementor panel not found, checking alternative selectors...")

        page.wait_for_timeout(5000)
        screenshot(page, "02_elementor_ready")

        # Check what we can see
        print("\n=== Elementor Analysis ===")

        # Get the preview iframe using frame_locator
        frame = page.frame_locator("#elementor-preview-iframe")

        # Check for sections
        sections = frame.locator(".elementor-section")
        print(f"Sections found: {sections.count()}")

        # Check for widgets
        widgets = frame.locator(".elementor-widget")
        print(f"Widgets found: {widgets.count()}")

        # Check specific widget types
        headings = frame.locator(".elementor-heading-title")
        print(f"Headings: {headings.count()}")

        text = frame.locator(".elementor-text-editor")
        print(f"Text blocks: {text.count()}")

        buttons = frame.locator(".elementor-button")
        print(f"Buttons: {buttons.count()}")

        images = frame.locator(".elementor-image")
        print(f"Images: {images.count()}")

        # Look for pricing/payment elements
        print("\n=== Looking for pricing/payment elements ===")
        pricing_text = frame.locator("text=/price|pricing|\\$/i")
        print(f"Pricing text elements: {pricing_text.count()}")

        payment_text = frame.locator("text=/payment|checkout|subscribe|stripe/i")
        print(f"Payment text elements: {payment_text.count()}")

        plan_text = frame.locator("text=/plan|tier|monthly|yearly|annual/i")
        print(f"Plan/tier elements: {plan_text.count()}")

        # Scroll the preview iframe to capture full page
        print("\n=== Capturing full page content ===")

        # First, try scrolling within the preview
        preview_body = frame.locator("body")
        if preview_body.count() > 0:
            # Get body text content
            try:
                body_text = preview_body.first.text_content()
                print(f"\nPage text content ({len(body_text)} chars):")
                body_text = ' '.join(body_text.split())
                print(body_text[:3000])
            except:
                print("Could not get text content")

        # Take screenshots at different scroll positions by clicking in preview area
        screenshot(page, "03_view_top")

        # Click in preview area and scroll
        preview_area = page.locator("#elementor-preview")
        if preview_area.count() > 0:
            preview_area.click()

        # Use keyboard to scroll
        page.keyboard.press("End")
        page.wait_for_timeout(2000)
        screenshot(page, "04_view_bottom")

        page.keyboard.press("Home")
        page.wait_for_timeout(1000)
        page.keyboard.press("PageDown")
        page.wait_for_timeout(1000)
        screenshot(page, "05_view_middle1")

        page.keyboard.press("PageDown")
        page.wait_for_timeout(1000)
        screenshot(page, "06_view_middle2")

        page.keyboard.press("PageDown")
        page.wait_for_timeout(1000)
        screenshot(page, "07_view_middle3")

        page.keyboard.press("PageDown")
        page.wait_for_timeout(1000)
        screenshot(page, "08_view_middle4")

        # Also check via direct preview URL
        print("\n=== Checking Public Preview ===")
        page.goto("https://purebrain.ai/?page_id=174&preview=true", wait_until="domcontentloaded")
        page.wait_for_timeout(5000)
        screenshot(page, "09_preview_top")

        # Scroll preview
        page.evaluate("window.scrollTo(0, document.body.scrollHeight/4)")
        page.wait_for_timeout(1000)
        screenshot(page, "10_preview_25pct")

        page.evaluate("window.scrollTo(0, document.body.scrollHeight/2)")
        page.wait_for_timeout(1000)
        screenshot(page, "11_preview_50pct")

        page.evaluate("window.scrollTo(0, document.body.scrollHeight*3/4)")
        page.wait_for_timeout(1000)
        screenshot(page, "12_preview_75pct")

        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(1000)
        screenshot(page, "13_preview_bottom")

        print("\nDone!")
        browser.close()

if __name__ == "__main__":
    main()
