#!/usr/bin/env python3
"""
WordPress Elementor Pricing Page Update Script
Updates PureBrain 3.0 pricing tier features via Elementor

Usage: python3 wp_elementor_pricing_update.py
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Configuration
WP_URL = "https://purebrain.ai/wp-admin/"
WP_USERNAME = "Aether"
WP_PASSWORD = "NW2u!JLQ3!Bt$XD$7CWzz5Z@"

# Screenshot directory
SCREENSHOT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/wp-pricing-screenshots")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

# Pricing tier updates - the exact text to use for each tier
PRICING_UPDATES = {
    "awakened": {
        "price": "$79",
        "features": [
            "Unlimited Agents",
            "24/7 persistent deployment - always-on infrastructure",
            "Inherits wisdom via RAG knowledge base",
            "Comms hub access (skills sync)",
            "Community support + knowledge base",
            "API documentation + prompt engineering guides"
        ]
    },
    "bonded": {
        "price": "$149",
        "features": [
            "Everything in Awakened, plus:",
            "Managed service: proactive monitoring & maintenance",
            "Automated health checks + performance analytics",
            "Priority skills sync + enhanced API rate limits",
            "24h SLA support response",
            "Social integrations: Telegram + Bluesky setup",
            "Autonomous workflows (scheduled tasks)"
        ]
    },
    "partnered": {
        "price": "$499",
        "features": [
            "Everything in Bonded, plus:",
            "1 hour/month AI strategy consulting",
            "1 custom agent build/month",
            "Same-day SLA support",
            "Prompt library + automation templates",
            "Beta access to new capabilities"
        ]
    },
    "unified": {
        "price": "$999",
        "features": [
            "Everything in Partnered, plus:",
            "4 hours/month executive AI consulting",
            "Unlimited custom agents built to spec",
            "Full enterprise integrations (CRM, ERP, custom APIs)",
            "Dedicated success manager",
            "99.9% SLA + SOC 2 compliance",
            "Private cloud deployment option"
        ]
    }
}

def screenshot(page, name: str):
    """Take a screenshot with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{name}.png"
    filepath = SCREENSHOT_DIR / filename
    page.screenshot(path=str(filepath), full_page=True)
    print(f"Screenshot saved: {filepath}")
    return filepath

def wait_and_click(page, selector: str, timeout: int = 10000):
    """Wait for element and click it"""
    page.wait_for_selector(selector, timeout=timeout)
    page.click(selector)

def login_to_wordpress(page):
    """Log into WordPress admin"""
    print("Navigating to WordPress admin...")
    page.goto(WP_URL, wait_until="networkidle")

    # Take initial screenshot
    screenshot(page, "01_login_page")

    # Check if we see GoDaddy login button
    godaddy_selector = 'text="Log in with username and password"'
    if page.locator(godaddy_selector).count() > 0:
        print("Found GoDaddy login page, clicking 'Log in with username and password'...")
        page.click(godaddy_selector)
        time.sleep(2)
        screenshot(page, "02_after_godaddy_click")

    # Wait for login form
    print("Waiting for login form...")
    page.wait_for_selector('#user_login', timeout=15000)

    # Enter credentials
    print("Entering credentials...")
    page.fill('#user_login', WP_USERNAME)
    page.fill('#user_pass', WP_PASSWORD)

    screenshot(page, "03_credentials_entered")

    # Click login button
    print("Clicking login button...")
    page.click('#wp-submit')

    # Wait for dashboard to load
    print("Waiting for dashboard...")
    time.sleep(5)

    # Check if CAPTCHA appeared or if we got in
    screenshot(page, "04_after_login")

    # Check for dashboard elements
    if page.locator('#adminmenu').count() > 0:
        print("Successfully logged in to WordPress admin!")
        return True
    else:
        print("Login may have failed or needs CAPTCHA. Check screenshots.")
        return False

def navigate_to_purebrain3_page(page):
    """Navigate to the PureBrain 3.0 pricing page"""
    print("Navigating to Pages...")

    # Click on Pages in sidebar
    page.click('#menu-pages')
    time.sleep(2)

    # Click All Pages
    page.click('a[href="edit.php?post_type=page"]')
    time.sleep(3)

    screenshot(page, "05_pages_list")

    # Search for purebrain-3 page
    print("Searching for purebrain.ai 3.0...")
    page.fill('#post-search-input', 'purebrain.ai 3.0')
    page.click('#search-submit')
    time.sleep(3)

    screenshot(page, "06_search_results")

    # Look specifically for the "PureBrain.ai 3.0" page
    print("Looking for PureBrain.ai 3.0 page...")

    # Try to find the exact page
    page_selector = 'a.row-title:has-text("PureBrain.ai 3.0")'
    matches = page.locator(page_selector)

    if matches.count() > 0:
        print(f"Found PureBrain.ai 3.0 page!")
        # Hover to show row actions
        matches.first.hover()
        time.sleep(1)
        screenshot(page, "07_page_hover")
        return True
    else:
        # Try broader search
        print("Exact match not found, trying broader search...")
        page.fill('#post-search-input', '3.0')
        page.click('#search-submit')
        time.sleep(3)
        screenshot(page, "07_broader_search")

        matches = page.locator('a.row-title:has-text("3.0")')
        if matches.count() > 0:
            matches.first.hover()
            time.sleep(1)
            screenshot(page, "07_page_hover_broad")
            return True

    return False

def open_elementor_editor(page):
    """Open the Elementor editor for the current page"""
    print("Looking for Edit with Elementor button...")

    # Look for Edit with Elementor in row actions
    elementor_selectors = [
        'span.edit_with_elementor a',
        'a:has-text("Edit with Elementor")',
        '.elementor-edit-link',
        'a[href*="elementor"]'
    ]

    for selector in elementor_selectors:
        matches = page.locator(selector)
        if matches.count() > 0:
            print(f"Found Elementor link with: {selector}")
            matches.first.click()
            print("Waiting for Elementor to load (this may take up to 60 seconds)...")
            time.sleep(15)  # Initial wait
            screenshot(page, "08_elementor_loading")
            return True

    # If not found in row, try clicking Edit first
    print("Elementor link not found in row, clicking Edit first...")
    page.click('span.edit a')
    time.sleep(3)

    # Now look for Edit with Elementor button in the editor
    page.wait_for_selector('a:has-text("Edit with Elementor")', timeout=10000)
    page.click('a:has-text("Edit with Elementor")')
    print("Waiting for Elementor to load (this may take up to 60 seconds)...")
    time.sleep(15)

    screenshot(page, "08_elementor_editor")
    return True

def wait_for_elementor_loaded(page, timeout=90):
    """Wait for Elementor to fully load by checking for loaded content"""
    print(f"Waiting up to {timeout}s for Elementor to fully load...")

    iframe_selector = '#elementor-preview-iframe'

    # Wait for iframe
    page.wait_for_selector(iframe_selector, timeout=60000)

    start_time = time.time()
    while time.time() - start_time < timeout:
        # Take periodic screenshots
        elapsed = int(time.time() - start_time)
        if elapsed % 10 == 0:
            screenshot(page, f"loading_{elapsed}s")

        # Check if content is loaded in iframe
        frame = page.frame_locator(iframe_selector)

        # Look for any real content (not loading spinner)
        try:
            # Check for body content
            body = frame.locator('body')
            if body.count() > 0:
                # Check for text content that indicates loaded state
                content_check = frame.locator('text=/\\$[0-9]+/')  # Look for dollar amounts
                if content_check.count() > 0:
                    print("Content loaded! Found pricing text.")
                    return True

                # Also check for common elements
                for check_text in ['PUREBRAIN', 'PureBrain', 'pricing', 'Pricing']:
                    if frame.locator(f'text="{check_text}"').count() > 0:
                        print(f"Content loaded! Found: {check_text}")
                        return True
        except:
            pass

        time.sleep(2)

    print("Timeout waiting for Elementor content to load")
    return False

def explore_page_content(page):
    """Explore and capture the page content by scrolling"""
    print("Exploring page content...")

    iframe_selector = '#elementor-preview-iframe'
    frame = page.frame_locator(iframe_selector)

    # Get the iframe element for scrolling
    iframe_element = page.locator(iframe_selector)

    screenshot(page, "explore_01_initial")

    # Scroll through the page in the iframe
    for i in range(10):
        try:
            # Use JavaScript to scroll within the iframe
            page.evaluate("""
                (scrollAmount) => {
                    const iframe = document.querySelector('#elementor-preview-iframe');
                    if (iframe && iframe.contentDocument) {
                        iframe.contentDocument.documentElement.scrollTop += scrollAmount;
                    }
                }
            """, 500)
            time.sleep(1)
            screenshot(page, f"explore_{i+2:02d}_scroll")
        except Exception as e:
            print(f"Scroll error: {e}")
            break

    return True

def update_pricing_features(page):
    """Update the pricing tier features"""
    print("Preparing to update pricing features...")

    # Output the text to copy for manual editing
    print()
    print("=" * 60)
    print("PRICING TIER FEATURES TO UPDATE:")
    print("=" * 60)

    for tier, data in PRICING_UPDATES.items():
        print(f"\n{'=' * 40}")
        print(f"=== {tier.upper()} ({data['price']}) ===")
        print(f"{'=' * 40}")
        # Print features as bullet list for easy copying
        features_text = "\n".join([f"• {f}" for f in data['features']])
        print(features_text)
        print()

    return True

def main():
    print("=" * 60)
    print("WordPress Elementor Pricing Page Update")
    print("PureBrain.ai 3.0 Page")
    print("=" * 60)
    print()
    print(f"Target URL: {WP_URL}")
    print(f"Screenshots will be saved to: {SCREENSHOT_DIR}")
    print()

    with sync_playwright() as p:
        # Launch browser in HEADLESS mode (no X server needed)
        print("Launching browser (headless mode)...")
        browser = p.chromium.launch(
            headless=True,   # Headless for WSL2 compatibility
            slow_mo=100      # Slow down actions for stability
        )

        # Create browser context with larger viewport
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        page = context.new_page()

        try:
            # Step 1: Login to WordPress
            login_result = login_to_wordpress(page)
            if not login_result:
                print("WARNING: Login may have failed. Check screenshots for CAPTCHA.")
                screenshot(page, "error_login_failed")
                print("Continuing anyway to capture state...")

            # Step 2: Navigate to the pricing page
            if not navigate_to_purebrain3_page(page):
                print("ERROR: Could not find PureBrain.ai 3.0 page!")
                screenshot(page, "error_page_not_found")

            # Step 3: Open Elementor editor
            open_elementor_editor(page)

            # Step 4: Wait for Elementor to fully load
            wait_for_elementor_loaded(page)

            # Step 5: Explore page content with scrolling
            explore_page_content(page)

            # Step 6: Output features to update
            update_pricing_features(page)

            # Final screenshot
            screenshot(page, "final_state")

            print()
            print("=" * 60)
            print("AUTOMATION COMPLETE")
            print()
            print("Screenshots saved to:", SCREENSHOT_DIR)
            print()
            print("=" * 60)

        except PlaywrightTimeout as e:
            print(f"Timeout error: {e}")
            screenshot(page, "error_timeout")
        except Exception as e:
            print(f"Error: {e}")
            screenshot(page, "error_exception")
            raise
        finally:
            browser.close()

if __name__ == "__main__":
    main()
