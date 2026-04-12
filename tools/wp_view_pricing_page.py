#!/usr/bin/env python3
"""
View the PureBrain 3.0 pricing page to see current content
"""

import time
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

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
    print("Viewing PureBrain.ai 3.0 pricing page (frontend)...")
    print()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # Navigate directly to the pricing page - use domcontentloaded instead of networkidle
        page_url = "https://purebrain.ai/purebrain-ai-3-0/"
        print(f"Navigating to: {page_url}")
        page.goto(page_url, wait_until="domcontentloaded", timeout=60000)

        # Wait a bit for JS to render
        time.sleep(5)

        # Take initial screenshot
        screenshot(page, "frontend_01_top")

        # Scroll through page capturing content
        for i in range(10):
            page.evaluate("window.scrollBy(0, 800)")
            time.sleep(1)
            screenshot(page, f"frontend_{i+2:02d}_scroll")

        # Print page title
        print(f"Page title: {page.title()}")

        # Try to extract pricing content
        print("\nExtracting visible text content related to pricing...")

        # Look for pricing text
        pricing_text = page.locator('text=/\\$[0-9]+/')
        if pricing_text.count() > 0:
            print(f"Found {pricing_text.count()} price elements")
            for i in range(min(pricing_text.count(), 10)):
                try:
                    text = pricing_text.nth(i).inner_text()
                    print(f"  Price {i+1}: {text}")
                except:
                    pass

        browser.close()

if __name__ == "__main__":
    main()
