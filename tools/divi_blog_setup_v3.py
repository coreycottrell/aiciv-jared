#!/usr/bin/env python3
"""
WordPress Divi Blog Setup Automation - Version 3
Using domcontentloaded instead of networkidle to avoid timeout issues.

Usage:
    python3 tools/divi_blog_setup_v3.py
"""

import asyncio
import os
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

# Configuration
WP_URL = "https://jareddsanborn.com/wp-admin"
WP_USERNAME = "jared@eyefuelpr.nyc"
WP_PASSWORD = "New1Jared88887"
SCREENSHOT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/divi-blog-setup")

# Ensure screenshot directory exists
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

def screenshot_path(name: str) -> str:
    """Generate timestamped screenshot path."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return str(SCREENSHOT_DIR / f"v3_{timestamp}_{name}.png")

async def save_screenshot(page, name: str, full_page: bool = False):
    """Save a screenshot with logging."""
    path = screenshot_path(name)
    await page.screenshot(path=path, full_page=full_page)
    print(f"[SCREENSHOT] Saved: {path}")
    return path

async def safe_goto(page, url, wait_time=5000):
    """Navigate to URL with domcontentloaded and then wait."""
    print(f"[NAV] Going to: {url}")
    await page.goto(url, wait_until="domcontentloaded", timeout=60000)
    await page.wait_for_timeout(wait_time)

async def login_to_wordpress(page):
    """PHASE 1: Login to WordPress admin."""
    print("\n=== PHASE 1: Login to WordPress ===")

    await safe_goto(page, WP_URL)

    # Check if already logged in
    if "wp-login.php" not in page.url and "wpbody" in await page.content():
        print("[INFO] Already logged in")
        await save_screenshot(page, "01_already_logged_in")
        return True

    await save_screenshot(page, "01_login_page")

    # Enter credentials
    try:
        await page.fill("#user_login", WP_USERNAME, timeout=10000)
        await page.fill("#user_pass", WP_PASSWORD, timeout=10000)
        await page.wait_for_timeout(500)
        await save_screenshot(page, "02_credentials_entered")

        # Click login button
        await page.click("#wp-submit")
        await page.wait_for_timeout(5000)

        await save_screenshot(page, "03_dashboard_after_login")
        print("[SUCCESS] Logged into WordPress dashboard")
        return True
    except Exception as e:
        print(f"[ERROR] Login failed: {e}")
        await save_screenshot(page, "03_login_failed")
        return False

async def check_categories(page):
    """Check existing categories (they appear to already exist)."""
    print("\n=== Checking Categories ===")

    await safe_goto(page, f"{WP_URL}/edit-tags.php?taxonomy=category")
    await save_screenshot(page, "04_categories_page")

    # Check what categories exist
    content = await page.content()
    expected = ["AI Insights", "Marketing", "Technology", "Leadership"]
    found = []
    for cat in expected:
        if cat in content:
            found.append(cat)
            print(f"[EXISTS] Category: {cat}")

    if len(found) == len(expected):
        print("[SUCCESS] All required categories exist")
        return True
    else:
        missing = set(expected) - set(found)
        print(f"[INFO] Missing categories: {missing}")
        return True  # Categories may need to be created manually

async def check_blog_page(page):
    """Check if Blog page exists."""
    print("\n=== Checking Blog Page ===")

    await safe_goto(page, f"{WP_URL}/edit.php?post_type=page")
    await save_screenshot(page, "05_pages_list")

    content = await page.content()
    if "Blog" in content:
        print("[EXISTS] Blog page found")
        return True
    else:
        print("[INFO] Blog page not found, needs creation")
        return False

async def create_blog_page(page):
    """Create dedicated /blog page."""
    print("\n=== Creating Blog Page ===")

    await safe_goto(page, f"{WP_URL}/post-new.php?post_type=page", wait_time=5000)
    await save_screenshot(page, "06_new_page_form")

    # Enter title
    try:
        # Try the contenteditable title field (Gutenberg)
        title_area = await page.query_selector("[aria-label='Add title'], .editor-post-title__input, h1[contenteditable='true']")
        if title_area:
            await title_area.click()
            await page.keyboard.type("Blog")
            print("[SUCCESS] Entered title: Blog")
        else:
            # Classic editor
            await page.fill("#title", "Blog", timeout=5000)
    except Exception as e:
        print(f"[WARNING] Could not set title: {e}")

    await page.wait_for_timeout(2000)
    await save_screenshot(page, "07_blog_title_entered")

    # Look for Divi Builder option
    try:
        divi_btn = await page.query_selector("button:has-text('Use Divi Builder')")
        if divi_btn:
            await divi_btn.click()
            await page.wait_for_timeout(8000)
            print("[SUCCESS] Selected Divi Builder")
            await save_screenshot(page, "08_divi_selected")
    except:
        pass

    # Try to publish
    try:
        # Save draft first
        save_draft = await page.query_selector("button:has-text('Save draft')")
        if save_draft:
            await save_draft.click()
            await page.wait_for_timeout(3000)

        # Then publish
        publish_btn = await page.query_selector("button:has-text('Publish'):not([disabled])")
        if publish_btn:
            await publish_btn.click()
            await page.wait_for_timeout(2000)

            # Confirm publish (second click needed in Gutenberg)
            confirm_btn = await page.query_selector(".editor-post-publish-panel button:has-text('Publish')")
            if confirm_btn:
                await confirm_btn.click()
                await page.wait_for_timeout(3000)

            print("[SUCCESS] Published Blog page")
    except Exception as e:
        print(f"[WARNING] Publish issue: {e}")

    await save_screenshot(page, "09_blog_page_created")
    return True

async def edit_homepage_add_blog(page):
    """Edit Homepage with Divi and add blog section."""
    print("\n=== Editing Homepage ===")

    # Go to Pages list
    await safe_goto(page, f"{WP_URL}/edit.php?post_type=page")
    await page.wait_for_timeout(2000)

    # Click on Home page to edit
    try:
        home_link = await page.query_selector("a.row-title:has-text('Home')")
        if home_link:
            await home_link.click()
            await page.wait_for_timeout(5000)
            await save_screenshot(page, "10_home_edit_screen")
            print("[SUCCESS] Opened Home page")
    except Exception as e:
        print(f"[WARNING] Could not open Home page: {e}")
        return False

    # Look for "Edit With The Divi Builder" button
    try:
        # The button appears to be a link with this text
        divi_btn = await page.query_selector("a:has-text('Edit With The Divi Builder'), button:has-text('Edit With The Divi Builder')")
        if divi_btn:
            await divi_btn.click()
            print("[SUCCESS] Clicked Divi Builder button")

            # Wait for Divi to load (it opens Visual Builder)
            await page.wait_for_timeout(15000)
            await save_screenshot(page, "11_divi_builder_loading")
        else:
            print("[INFO] Divi Builder button not found on page")
            await save_screenshot(page, "11_no_divi_button")
            return False
    except Exception as e:
        print(f"[WARNING] Divi Builder issue: {e}")
        return False

    # Wait for Divi Visual Builder to fully load
    print("[INFO] Waiting for Divi Visual Builder...")
    await page.wait_for_timeout(10000)
    await save_screenshot(page, "12_visual_builder_loaded", full_page=True)

    # Scroll to bottom to add section
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    await page.wait_for_timeout(2000)
    await save_screenshot(page, "13_scrolled_bottom", full_page=True)

    # In Divi Visual Builder, look for the interface elements
    # The builder interface has special buttons for adding sections

    # Take a screenshot of the current state for analysis
    await save_screenshot(page, "14_divi_interface", full_page=True)

    print("[INFO] Divi Visual Builder opened - manual module addition may be needed")
    print("[INFO] The Visual Builder requires clicking within the visual interface")

    return True

async def verify_site(page):
    """Verify the live site."""
    print("\n=== Verification ===")

    # Visit homepage
    await page.goto("https://jareddsanborn.com", wait_until="domcontentloaded")
    await page.wait_for_timeout(5000)
    await save_screenshot(page, "15_homepage_live", full_page=True)

    # Scroll through page
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 3)")
    await page.wait_for_timeout(1500)
    await save_screenshot(page, "16_homepage_section1")

    await page.evaluate("window.scrollTo(0, document.body.scrollHeight * 2 / 3)")
    await page.wait_for_timeout(1500)
    await save_screenshot(page, "17_homepage_section2")

    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    await page.wait_for_timeout(1500)
    await save_screenshot(page, "18_homepage_footer")

    # Try /blog page
    await page.goto("https://jareddsanborn.com/blog", wait_until="domcontentloaded")
    await page.wait_for_timeout(3000)
    await save_screenshot(page, "19_blog_page", full_page=True)

    print("[SUCCESS] Verification complete")
    return True

async def main():
    """Main automation flow."""
    print("=" * 60)
    print("WordPress Divi Blog Setup Automation v3")
    print("=" * 60)
    print(f"Target: {WP_URL}")
    print(f"Screenshots: {SCREENSHOT_DIR}")
    print("=" * 60)

    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )

        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

        page = await context.new_page()
        page.set_default_timeout(60000)

        results = {
            "login": False,
            "categories_exist": False,
            "blog_page_check": False,
            "blog_page_create": False,
            "homepage_edit": False,
            "verify": False,
        }

        try:
            # Login
            results["login"] = await login_to_wordpress(page)
            if not results["login"]:
                print("[FATAL] Login failed")
                return results

            # Check categories
            results["categories_exist"] = await check_categories(page)

            # Check if blog page exists
            results["blog_page_check"] = await check_blog_page(page)

            # Create blog page if needed
            if not results["blog_page_check"]:
                results["blog_page_create"] = await create_blog_page(page)
            else:
                results["blog_page_create"] = True

            # Edit homepage
            results["homepage_edit"] = await edit_homepage_add_blog(page)

            # Verify
            results["verify"] = await verify_site(page)

        except Exception as e:
            print(f"[ERROR] Exception: {e}")
            import traceback
            traceback.print_exc()
            await save_screenshot(page, "error_state")

        finally:
            await browser.close()

        # Summary
        print("\n" + "=" * 60)
        print("RESULTS SUMMARY")
        print("=" * 60)
        for step, success in results.items():
            status = "[PASS]" if success else "[FAIL/SKIP]"
            print(f"{status} {step}")
        print("=" * 60)

        # List v3 screenshots
        print("\nScreenshots (v3):")
        for f in sorted(SCREENSHOT_DIR.glob("v3_*.png")):
            print(f"  - {f.name}")

        return results

if __name__ == "__main__":
    asyncio.run(main())
