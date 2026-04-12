#!/usr/bin/env python3
"""
ChatGPT Search Feature Research Script
Documents the search functionality in ChatGPT for competitive analysis

This script:
1. Navigates to ChatGPT (headless mode for WSL2)
2. Takes screenshots at each step
3. Documents the interface structure
"""

from playwright.sync_api import sync_playwright
import time
import os
from datetime import datetime

# Screenshot directory
SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/docs/chatgpt-search-research"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def take_screenshot(page, step_name):
    """Take and save screenshot with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"{SCREENSHOT_DIR}/{step_name}_{timestamp}.png"
    page.screenshot(path=path, full_page=True)
    print(f"  Screenshot: {path}")
    return path

def run_research():
    with sync_playwright() as p:
        # Launch browser in headless mode (required for WSL2 without X server)
        browser = p.chromium.launch(
            headless=True
        )

        context = browser.new_context(
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()

        print("\n" + "="*60)
        print("CHATGPT SEARCH FEATURE RESEARCH")
        print("="*60)

        # Step 1: Navigate to ChatGPT
        print("\n[STEP 1] Navigating to ChatGPT...")
        page.goto("https://chatgpt.com", wait_until="networkidle", timeout=60000)
        time.sleep(3)
        take_screenshot(page, "01_chatgpt_homepage")

        # Get page HTML structure for analysis
        print("\n[STEP 2] Analyzing page structure...")
        page_content = page.content()

        # Look for search-related elements
        search_elements = page.query_selector_all('[placeholder*="search" i], [aria-label*="search" i], button:has-text("Search")')
        print(f"  Found {len(search_elements)} potential search elements")

        # Get all interactive elements
        buttons = page.query_selector_all('button')
        print(f"  Found {len(buttons)} button elements")

        inputs = page.query_selector_all('input')
        print(f"  Found {len(inputs)} input elements")

        take_screenshot(page, "02_structure_analysis")

        # Check if we need to log in
        login_btn = page.query_selector('button:has-text("Log in"), a:has-text("Log in")')
        if login_btn:
            print("\n[STEP 3] Login required - documenting login page...")
            take_screenshot(page, "03_login_required")
        else:
            print("\n[STEP 3] No login button found - may already show interface")
            take_screenshot(page, "03_main_interface")

        # Save HTML for offline analysis
        html_path = f"{SCREENSHOT_DIR}/page_structure.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(page_content)
        print(f"\n  Page HTML saved: {html_path}")

        browser.close()

        print("\n" + "="*60)
        print("RESEARCH COMPLETE - SCREENSHOTS CAPTURED")
        print("="*60)
        print(f"\nScreenshots saved to: {SCREENSHOT_DIR}")
        print("\nNote: Without login, we can only capture the login page.")
        print("For full research, need to use browser with existing session.")

if __name__ == "__main__":
    run_research()
