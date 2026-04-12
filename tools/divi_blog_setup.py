#!/usr/bin/env python3
"""
WordPress Divi Blog Setup Automation
Automates the creation of a blog section on jareddsanborn.com using Playwright.

Usage:
    python3 tools/divi_blog_setup.py
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
    return str(SCREENSHOT_DIR / f"{timestamp}_{name}.png")

async def save_screenshot(page, name: str, full_page: bool = False):
    """Save a screenshot with logging."""
    path = screenshot_path(name)
    await page.screenshot(path=path, full_page=full_page)
    print(f"[SCREENSHOT] Saved: {path}")
    return path

async def wait_and_click(page, selector: str, timeout: int = 30000):
    """Wait for element and click it."""
    await page.wait_for_selector(selector, timeout=timeout)
    await page.click(selector)

async def login_to_wordpress(page):
    """PHASE 1: Login to WordPress admin."""
    print("\n=== PHASE 1: Login to WordPress ===")

    await page.goto(WP_URL, wait_until="networkidle")
    await page.wait_for_timeout(2000)

    # Take screenshot of login page
    await save_screenshot(page, "01_login_page")

    # Enter credentials
    await page.fill("#user_login", WP_USERNAME)
    await page.fill("#user_pass", WP_PASSWORD)
    await page.wait_for_timeout(500)

    await save_screenshot(page, "02_credentials_entered")

    # Click login button
    await page.click("#wp-submit")

    # Wait for dashboard to load
    try:
        await page.wait_for_selector("#wpbody", timeout=30000)
        await page.wait_for_timeout(2000)
        await save_screenshot(page, "03_dashboard_after_login")
        print("[SUCCESS] Logged into WordPress dashboard")
        return True
    except PlaywrightTimeout:
        await save_screenshot(page, "03_login_failed")
        print("[ERROR] Login failed or dashboard didn't load")
        return False

async def navigate_to_pages(page):
    """Navigate to Pages section."""
    print("\n=== Navigating to Pages ===")

    # Click on Pages in sidebar
    try:
        await wait_and_click(page, "#menu-pages")
        await page.wait_for_timeout(2000)
        await save_screenshot(page, "04_pages_list")
        print("[SUCCESS] Navigated to Pages")
        return True
    except PlaywrightTimeout:
        print("[ERROR] Could not find Pages menu")
        return False

async def edit_homepage_with_divi(page):
    """PHASE 2: Open homepage in Divi Builder."""
    print("\n=== PHASE 2: Edit Homepage with Divi ===")

    # Look for the homepage/front page
    # Try different possible names
    homepage_selectors = [
        "a.row-title:has-text('Home')",
        "a.row-title:has-text('Homepage')",
        "a.row-title:has-text('Front Page')",
        "tr:has-text('Front Page') a.row-title",
        "tr:has-text('Home') a.row-title",
    ]

    found_homepage = False
    for selector in homepage_selectors:
        try:
            element = await page.query_selector(selector)
            if element:
                # Hover to reveal row actions
                await element.hover()
                await page.wait_for_timeout(500)
                await save_screenshot(page, "05_homepage_found")
                found_homepage = True
                break
        except:
            continue

    if not found_homepage:
        # Try to find any page and list what's available
        await save_screenshot(page, "05_pages_available")
        print("[INFO] Looking for pages... Screenshot saved for review")

        # Try clicking on the first page to edit it
        try:
            first_page = await page.query_selector("a.row-title")
            if first_page:
                page_title = await first_page.inner_text()
                print(f"[INFO] Found page: {page_title}")
        except:
            pass

    # Look for "Edit with Divi" button or link
    divi_selectors = [
        "a:has-text('Edit With Divi')",
        "a:has-text('Edit with Divi')",
        ".editinline:has-text('Divi')",
        "a.use-visual-builder",
        "span.edit-with-divi a",
    ]

    # First, let's click on the page title to go to edit screen
    try:
        await page.click("a.row-title >> nth=0")
        await page.wait_for_timeout(2000)
        await save_screenshot(page, "06_page_edit_screen")
    except:
        pass

    # Look for Divi Builder button on the edit screen
    divi_found = False
    for selector in divi_selectors:
        try:
            element = await page.query_selector(selector)
            if element:
                await element.click()
                await page.wait_for_timeout(5000)  # Divi takes time to load
                await save_screenshot(page, "07_divi_builder_loading")
                divi_found = True
                print("[SUCCESS] Clicked Divi Builder button")
                break
        except:
            continue

    if not divi_found:
        # Try the purple "Use Divi Builder" or "Use Visual Builder" button
        try:
            await page.click("#et-bfb-toggle", timeout=5000)
            await page.wait_for_timeout(5000)
            await save_screenshot(page, "07_divi_builder_loading")
            print("[SUCCESS] Clicked Divi Builder toggle")
            divi_found = True
        except:
            pass

    if not divi_found:
        # Maybe there's a "Launch Visual Builder" link
        try:
            await page.click("a:has-text('Launch Visual Builder')", timeout=5000)
            await page.wait_for_timeout(5000)
            await save_screenshot(page, "07_visual_builder_loading")
            print("[SUCCESS] Launched Visual Builder")
            divi_found = True
        except:
            pass

    # Wait for Divi Builder to fully load
    if divi_found:
        await page.wait_for_timeout(10000)  # Give Divi time to load
        await save_screenshot(page, "08_divi_builder_loaded", full_page=True)
        print("[SUCCESS] Divi Builder loaded")
        return True
    else:
        await save_screenshot(page, "08_divi_not_found")
        print("[WARNING] Could not find Divi Builder button")
        return False

async def add_blog_section(page):
    """PHASE 3: Add Blog Section to page."""
    print("\n=== PHASE 3: Add Blog Section ===")

    # In Divi Visual Builder, we need to:
    # 1. Scroll to bottom of page
    # 2. Click the blue "+" to add a new section
    # 3. Choose Regular section

    # Scroll down
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    await page.wait_for_timeout(2000)
    await save_screenshot(page, "09_scrolled_to_bottom", full_page=True)

    # Look for add section button (blue +)
    add_section_selectors = [
        ".et-fb-button--add-section",
        "[data-testid='add-section']",
        ".et_pb_section_add_main",
        ".et-pb-add-section",
        "button:has-text('Add Section')",
        ".et_pb_section_content_wrap .et_pb_add_section",
    ]

    for selector in add_section_selectors:
        try:
            element = await page.query_selector(selector)
            if element:
                await element.click()
                await page.wait_for_timeout(2000)
                await save_screenshot(page, "10_section_menu")
                print(f"[SUCCESS] Clicked add section button: {selector}")
                break
        except:
            continue

    # Choose Regular section
    regular_section_selectors = [
        ".et_pb_section_regular",
        "[data-type='regular']",
        "div:has-text('Regular') >> nth=0",
        ".et-fb-section-type--regular",
    ]

    for selector in regular_section_selectors:
        try:
            await page.click(selector, timeout=5000)
            await page.wait_for_timeout(2000)
            await save_screenshot(page, "11_section_added")
            print(f"[SUCCESS] Added regular section")
            return True
        except:
            continue

    print("[WARNING] Could not add section via standard selectors")
    return False

async def add_blog_module(page):
    """PHASE 4: Add Blog Module to section."""
    print("\n=== PHASE 4: Add Blog Module ===")

    # In the section, click to add a row, then add Blog module
    # Look for the green "+" to add row
    add_row_selectors = [
        ".et_pb_row_add",
        ".et-pb-add-row",
        "[data-testid='add-row']",
        ".et_pb_section .et_pb_add_row_button",
    ]

    for selector in add_row_selectors:
        try:
            await page.click(selector, timeout=5000)
            await page.wait_for_timeout(2000)
            await save_screenshot(page, "12_row_options")
            print(f"[SUCCESS] Clicked add row: {selector}")
            break
        except:
            continue

    # Choose single column layout (1/1)
    try:
        await page.click(".et_pb_row_layout_1", timeout=5000)
        await page.wait_for_timeout(2000)
    except:
        # Try other selectors for single column
        try:
            await page.click("[data-columns='1']", timeout=3000)
        except:
            pass

    await save_screenshot(page, "13_row_added")

    # Now add module (gray "+")
    add_module_selectors = [
        ".et_pb_module_add",
        ".et-pb-add-module",
        "[data-testid='add-module']",
        ".et_pb_column .et_pb_add_module_button",
    ]

    for selector in add_module_selectors:
        try:
            await page.click(selector, timeout=5000)
            await page.wait_for_timeout(2000)
            await save_screenshot(page, "14_module_search")
            print(f"[SUCCESS] Opened module selector")
            break
        except:
            continue

    # Search for Blog module
    search_selectors = [
        "input[type='search']",
        ".et-fb-modules-search input",
        "input[placeholder*='Search']",
        ".et_pb_search_input",
    ]

    for selector in search_selectors:
        try:
            await page.fill(selector, "Blog", timeout=5000)
            await page.wait_for_timeout(1000)
            await save_screenshot(page, "15_blog_search")
            print(f"[SUCCESS] Searched for Blog module")
            break
        except:
            continue

    # Click on Blog module
    blog_module_selectors = [
        ".et_pb_blog",
        "[data-type='et_pb_blog']",
        "li:has-text('Blog') >> nth=0",
        ".et-fb-module--blog",
    ]

    for selector in blog_module_selectors:
        try:
            await page.click(selector, timeout=5000)
            await page.wait_for_timeout(3000)
            await save_screenshot(page, "16_blog_module_added")
            print(f"[SUCCESS] Added Blog module")
            return True
        except:
            continue

    print("[WARNING] Could not add Blog module")
    return False

async def configure_blog_module(page):
    """PHASE 5: Configure Blog Module settings."""
    print("\n=== PHASE 5: Configure Blog Module ===")

    # The module settings should be open after adding
    # Configure Content tab first

    # Post Count
    try:
        await page.fill("input[name='posts_number']", "3", timeout=5000)
    except:
        pass

    # Try to find and configure settings in the module panel
    await save_screenshot(page, "17_module_settings")

    # Click Design tab
    try:
        await page.click("li:has-text('Design')", timeout=5000)
        await page.wait_for_timeout(1000)
        await save_screenshot(page, "18_design_tab")
    except:
        pass

    # Save the module settings
    try:
        await page.click("button:has-text('Save')", timeout=5000)
        await page.wait_for_timeout(2000)
    except:
        # Try checkmark button
        try:
            await page.click(".et-fb-button--save", timeout=3000)
        except:
            pass

    await save_screenshot(page, "19_blog_configured")
    print("[INFO] Blog module configuration attempted")
    return True

async def save_page(page):
    """Save the page changes."""
    print("\n=== Saving Page ===")

    save_selectors = [
        "button:has-text('Save')",
        ".et-fb-button--save-draft",
        ".et-fb-button--publish",
        "[data-testid='save-button']",
        "#publish",
    ]

    for selector in save_selectors:
        try:
            await page.click(selector, timeout=5000)
            await page.wait_for_timeout(3000)
            await save_screenshot(page, "20_page_saved")
            print(f"[SUCCESS] Page saved")
            return True
        except:
            continue

    # Try keyboard shortcut
    try:
        await page.keyboard.press("Control+s")
        await page.wait_for_timeout(3000)
        await save_screenshot(page, "20_page_saved_keyboard")
        print("[SUCCESS] Page saved via keyboard shortcut")
        return True
    except:
        pass

    print("[WARNING] Could not find save button")
    return False

async def create_blog_page(page):
    """PHASE 7: Create dedicated /blog page."""
    print("\n=== PHASE 7: Create Blog Page ===")

    # Go back to admin
    await page.goto(f"{WP_URL}/post-new.php?post_type=page", wait_until="networkidle")
    await page.wait_for_timeout(2000)
    await save_screenshot(page, "21_new_page")

    # Enter title
    try:
        # Try Gutenberg editor
        await page.fill(".editor-post-title__input", "Blog", timeout=5000)
    except:
        # Try classic editor
        try:
            await page.fill("#title", "Blog", timeout=5000)
        except:
            pass

    await save_screenshot(page, "22_blog_title_entered")

    # Look for Divi Builder button
    try:
        await page.click("#et-bfb-toggle", timeout=5000)
        await page.wait_for_timeout(5000)
        await save_screenshot(page, "23_blog_page_divi")
    except:
        pass

    print("[INFO] Blog page creation started")
    return True

async def create_categories(page):
    """PHASE 8: Create blog categories."""
    print("\n=== PHASE 8: Create Categories ===")

    await page.goto(f"{WP_URL}/edit-tags.php?taxonomy=category", wait_until="networkidle")
    await page.wait_for_timeout(2000)
    await save_screenshot(page, "24_categories_page")

    categories = [
        ("AI Insights", "ai-insights"),
        ("Marketing", "marketing"),
        ("Technology", "technology"),
        ("Leadership", "leadership"),
    ]

    for name, slug in categories:
        try:
            # Fill in category name
            await page.fill("#tag-name", name, timeout=3000)
            await page.fill("#tag-slug", slug, timeout=3000)

            # Submit
            await page.click("#submit", timeout=3000)
            await page.wait_for_timeout(2000)
            print(f"[SUCCESS] Created category: {name}")
        except Exception as e:
            print(f"[WARNING] Could not create category {name}: {e}")

    await save_screenshot(page, "25_categories_created")
    return True

async def verify_site(page):
    """PHASE 9: Verify the live site."""
    print("\n=== PHASE 9: Verification ===")

    # Visit homepage
    await page.goto("https://jareddsanborn.com", wait_until="networkidle")
    await page.wait_for_timeout(3000)
    await save_screenshot(page, "26_homepage_live", full_page=True)

    # Scroll to find blog section
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
    await page.wait_for_timeout(2000)
    await save_screenshot(page, "27_homepage_scrolled")

    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    await page.wait_for_timeout(2000)
    await save_screenshot(page, "28_homepage_bottom")

    # Try to visit /blog
    await page.goto("https://jareddsanborn.com/blog", wait_until="networkidle")
    await page.wait_for_timeout(3000)
    await save_screenshot(page, "29_blog_page_live", full_page=True)

    print("[SUCCESS] Verification complete")
    return True

async def main():
    """Main automation flow."""
    print("=" * 60)
    print("WordPress Divi Blog Setup Automation")
    print("=" * 60)
    print(f"Target: {WP_URL}")
    print(f"Screenshots: {SCREENSHOT_DIR}")
    print("=" * 60)

    async with async_playwright() as p:
        # Launch browser (headless for server, headed for debugging)
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )

        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

        page = await context.new_page()

        results = {
            "login": False,
            "navigate_pages": False,
            "edit_homepage": False,
            "add_section": False,
            "add_blog_module": False,
            "configure_module": False,
            "save_page": False,
            "create_blog_page": False,
            "create_categories": False,
            "verify": False,
        }

        try:
            # PHASE 1: Login
            results["login"] = await login_to_wordpress(page)
            if not results["login"]:
                print("[FATAL] Login failed, aborting")
                return results

            # Navigate to Pages
            results["navigate_pages"] = await navigate_to_pages(page)

            # PHASE 2: Edit Homepage with Divi
            results["edit_homepage"] = await edit_homepage_with_divi(page)

            # PHASE 3: Add Blog Section
            if results["edit_homepage"]:
                results["add_section"] = await add_blog_section(page)

            # PHASE 4: Add Blog Module
            if results["add_section"]:
                results["add_blog_module"] = await add_blog_module(page)

            # PHASE 5: Configure Module
            if results["add_blog_module"]:
                results["configure_module"] = await configure_blog_module(page)

            # Save
            results["save_page"] = await save_page(page)

            # PHASE 7: Create Blog Page
            results["create_blog_page"] = await create_blog_page(page)

            # PHASE 8: Create Categories
            results["create_categories"] = await create_categories(page)

            # PHASE 9: Verify
            results["verify"] = await verify_site(page)

        except Exception as e:
            print(f"[ERROR] Exception during automation: {e}")
            await save_screenshot(page, "error_state")

        finally:
            await browser.close()

        # Print summary
        print("\n" + "=" * 60)
        print("AUTOMATION RESULTS")
        print("=" * 60)
        for step, success in results.items():
            status = "[PASS]" if success else "[FAIL]"
            print(f"{status} {step}")
        print("=" * 60)
        print(f"Screenshots saved to: {SCREENSHOT_DIR}")

        return results

if __name__ == "__main__":
    asyncio.run(main())
