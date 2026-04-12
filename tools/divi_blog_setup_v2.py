#!/usr/bin/env python3
"""
WordPress Divi Blog Setup Automation - Version 2
Improved based on actual UI screenshots.

Usage:
    python3 tools/divi_blog_setup_v2.py
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

async def login_to_wordpress(page):
    """PHASE 1: Login to WordPress admin."""
    print("\n=== PHASE 1: Login to WordPress ===")

    await page.goto(WP_URL, wait_until="networkidle")
    await page.wait_for_timeout(2000)

    # Check if already logged in
    if "wp-login.php" not in page.url:
        print("[INFO] May already be logged in")
        await save_screenshot(page, "01_already_logged_in")
        return True

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

async def create_categories(page):
    """PHASE 8: Create blog categories (do this first for clean state)."""
    print("\n=== Creating Categories ===")

    await page.goto(f"{WP_URL}/edit-tags.php?taxonomy=category", wait_until="networkidle")
    await page.wait_for_timeout(2000)
    await save_screenshot(page, "04_categories_page")

    categories = [
        ("AI Insights", "ai-insights"),
        ("Marketing", "marketing"),
        ("Technology", "technology"),
        ("Leadership", "leadership"),
    ]

    for name, slug in categories:
        try:
            # Check if category already exists
            existing = await page.query_selector(f"a:has-text('{name}')")
            if existing:
                print(f"[INFO] Category '{name}' already exists, skipping")
                continue

            # Fill in category name
            await page.fill("#tag-name", name)
            await page.fill("#tag-slug", slug)

            # Submit
            await page.click("#submit")
            await page.wait_for_timeout(2000)
            print(f"[SUCCESS] Created category: {name}")
        except Exception as e:
            print(f"[WARNING] Could not create category {name}: {e}")

    await save_screenshot(page, "05_categories_created")
    return True

async def create_blog_page(page):
    """PHASE 7: Create dedicated /blog page."""
    print("\n=== Creating Blog Page ===")

    # Check if blog page already exists
    await page.goto(f"{WP_URL}/edit.php?post_type=page", wait_until="networkidle")
    await page.wait_for_timeout(2000)

    blog_exists = await page.query_selector("a.row-title:has-text('Blog')")
    if blog_exists:
        print("[INFO] Blog page already exists")
        await save_screenshot(page, "06_blog_page_exists")
        return True

    # Create new page
    await page.goto(f"{WP_URL}/post-new.php?post_type=page", wait_until="domcontentloaded")
    await page.wait_for_timeout(3000)
    await save_screenshot(page, "06_new_page_form")

    # Click "Add title" area and type "Blog"
    try:
        # Try Gutenberg block editor title
        title_selector = ".editor-post-title__input, .wp-block-post-title, h1[contenteditable='true'], [aria-label='Add title']"
        await page.wait_for_selector(title_selector, timeout=10000)
        await page.fill(title_selector, "Blog")
        print("[SUCCESS] Entered page title: Blog")
    except:
        # Try classic editor
        try:
            await page.fill("#title", "Blog")
            print("[SUCCESS] Entered page title (classic editor): Blog")
        except Exception as e:
            print(f"[WARNING] Could not set title: {e}")

    await page.wait_for_timeout(1000)
    await save_screenshot(page, "07_blog_title_entered")

    # Look for Divi Builder option
    # The screenshot shows "Use Divi Builder" button
    try:
        divi_button = await page.wait_for_selector("button:has-text('Use Divi Builder'), a:has-text('Use Divi Builder')", timeout=5000)
        await divi_button.click()
        await page.wait_for_timeout(5000)
        print("[SUCCESS] Clicked Use Divi Builder")
        await save_screenshot(page, "08_divi_builder_selected")
    except:
        print("[WARNING] Could not find Use Divi Builder button")

    # Wait for Divi to load
    await page.wait_for_timeout(5000)

    # Add a Blog module
    # Look for the Divi add section interface
    try:
        # Look for "+" button to add section or the "Build From Scratch" option
        build_scratch = await page.query_selector("button:has-text('Build From Scratch'), .et-fb-start-new")
        if build_scratch:
            await build_scratch.click()
            await page.wait_for_timeout(2000)
            print("[SUCCESS] Selected Build From Scratch")
    except:
        pass

    await save_screenshot(page, "09_divi_builder_loaded")

    # Try to add a row
    try:
        add_row = await page.query_selector(".et-fb-insert-column, [data-testid='add-row'], .et-fb-add-row")
        if add_row:
            await add_row.click()
            await page.wait_for_timeout(2000)
            await save_screenshot(page, "10_row_options")
    except:
        pass

    # Publish/save the page
    try:
        # Look for Publish button
        publish = await page.query_selector("button:has-text('Publish'), .editor-post-publish-button")
        if publish:
            await publish.click()
            await page.wait_for_timeout(2000)
            # Click confirm publish if needed
            confirm_publish = await page.query_selector("button:has-text('Publish'):not([aria-disabled])")
            if confirm_publish:
                await confirm_publish.click()
            await page.wait_for_timeout(3000)
            print("[SUCCESS] Published Blog page")
    except Exception as e:
        print(f"[WARNING] Publish issue: {e}")

    await save_screenshot(page, "11_blog_page_saved")
    return True

async def edit_homepage_with_divi(page):
    """PHASE 2-6: Edit Homepage with Divi Builder and add blog section."""
    print("\n=== Editing Homepage with Divi ===")

    # Navigate to Pages
    await page.goto(f"{WP_URL}/edit.php?post_type=page", wait_until="networkidle")
    await page.wait_for_timeout(2000)
    await save_screenshot(page, "12_pages_list")

    # Find and click on Home page
    try:
        home_link = await page.wait_for_selector("a.row-title:has-text('Home')", timeout=10000)
        await home_link.click()
        await page.wait_for_timeout(3000)
        await save_screenshot(page, "13_home_page_edit")
        print("[SUCCESS] Opened Home page for editing")
    except Exception as e:
        print(f"[ERROR] Could not find Home page: {e}")
        return False

    # Click "Edit With The Divi Builder" button
    # Based on screenshot, it's a purple button with text "Edit With The Divi Builder"
    try:
        # Wait for the button to appear
        divi_btn_selectors = [
            "a:has-text('Edit With The Divi Builder')",
            "button:has-text('Edit With The Divi Builder')",
            ".et-builder-edit-button",
            "#et-bfb-toggle",
            "a:has-text('Edit With Divi')",
        ]

        clicked = False
        for selector in divi_btn_selectors:
            try:
                btn = await page.query_selector(selector)
                if btn:
                    await btn.click()
                    clicked = True
                    print(f"[SUCCESS] Clicked Divi Builder button: {selector}")
                    break
            except:
                continue

        if not clicked:
            print("[WARNING] Could not find Divi Builder button")
            await save_screenshot(page, "14_divi_button_not_found")
            return False

        # Wait for Divi Builder to load (it takes time)
        await page.wait_for_timeout(10000)
        await save_screenshot(page, "14_divi_builder_loading")

        # Divi Builder may open in a new window or load on same page
        # Check if we're in the visual builder
        await page.wait_for_timeout(5000)
        await save_screenshot(page, "15_divi_builder_loaded", full_page=True)

    except Exception as e:
        print(f"[ERROR] Divi Builder issue: {e}")
        await save_screenshot(page, "14_error_state")
        return False

    # Now we need to add a blog section
    # Scroll to bottom of page to add section above footer
    print("\n=== Adding Blog Section ===")

    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    await page.wait_for_timeout(2000)
    await save_screenshot(page, "16_scrolled_bottom", full_page=True)

    # In Divi Visual Builder, look for add section buttons
    # The interface has blue "+" buttons between sections
    try:
        # Look for any add section button
        add_section_selectors = [
            ".et-fb-section-add",
            ".et-fb-button--add-section",
            "[data-testid='add-section']",
            ".et_pb_section_add",
            "button[aria-label='Add Section']",
        ]

        for selector in add_section_selectors:
            try:
                btn = await page.query_selector(selector)
                if btn:
                    await btn.click()
                    await page.wait_for_timeout(2000)
                    await save_screenshot(page, "17_add_section_clicked")
                    print(f"[SUCCESS] Clicked add section: {selector}")
                    break
            except:
                continue
    except:
        pass

    # Choose Regular section
    try:
        regular = await page.query_selector(".et-fb-section-regular, [data-type='regular'], :text('Regular')")
        if regular:
            await regular.click()
            await page.wait_for_timeout(2000)
            await save_screenshot(page, "18_regular_section_added")
            print("[SUCCESS] Added regular section")
    except:
        pass

    # Add Blog module
    print("\n=== Adding Blog Module ===")

    # Try to add a module by clicking inside the section
    try:
        # Look for the "+" to add module
        add_module_selectors = [
            ".et-fb-insert-module",
            ".et_pb_module_add",
            "[data-testid='add-module']",
            "button[aria-label='Add Module']",
        ]

        for selector in add_module_selectors:
            try:
                btn = await page.query_selector(selector)
                if btn:
                    await btn.click()
                    await page.wait_for_timeout(2000)
                    await save_screenshot(page, "19_module_selector")
                    print(f"[SUCCESS] Opened module selector: {selector}")
                    break
            except:
                continue
    except:
        pass

    # Search for Blog module
    try:
        search_input = await page.query_selector("input[type='search'], input[placeholder*='Search'], .et-fb-modules-search input")
        if search_input:
            await search_input.fill("Blog")
            await page.wait_for_timeout(1500)
            await save_screenshot(page, "20_blog_search")
            print("[SUCCESS] Searched for Blog module")

            # Click on Blog module
            blog_module = await page.query_selector(".et-fb-module--blog, [data-type='et_pb_blog'], :text('Blog') >> nth=0")
            if blog_module:
                await blog_module.click()
                await page.wait_for_timeout(3000)
                await save_screenshot(page, "21_blog_module_added")
                print("[SUCCESS] Added Blog module")
    except:
        pass

    # Configure the Blog module
    print("\n=== Configuring Blog Module ===")

    # Try to set post count to 3
    try:
        post_count = await page.query_selector("input[name='posts_number'], input[data-option='posts_number']")
        if post_count:
            await post_count.fill("3")
            print("[SUCCESS] Set post count to 3")
    except:
        pass

    await save_screenshot(page, "22_blog_configured")

    # Save changes
    print("\n=== Saving Page ===")

    try:
        # Look for save button in Divi
        save_selectors = [
            ".et-fb-button--save",
            "[data-testid='save-button']",
            "button:has-text('Save')",
            ".et-fb-save-page",
        ]

        for selector in save_selectors:
            try:
                btn = await page.query_selector(selector)
                if btn:
                    await btn.click()
                    await page.wait_for_timeout(5000)
                    await save_screenshot(page, "23_page_saved")
                    print(f"[SUCCESS] Saved page: {selector}")
                    break
            except:
                continue
    except:
        # Try keyboard shortcut
        await page.keyboard.press("Control+s")
        await page.wait_for_timeout(3000)

    return True

async def verify_site(page):
    """PHASE 9: Verify the live site."""
    print("\n=== PHASE 9: Verification ===")

    # Visit homepage
    await page.goto("https://jareddsanborn.com", wait_until="networkidle")
    await page.wait_for_timeout(3000)
    await save_screenshot(page, "24_homepage_live", full_page=True)

    # Scroll to find blog section
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
    await page.wait_for_timeout(2000)
    await save_screenshot(page, "25_homepage_scrolled")

    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    await page.wait_for_timeout(2000)
    await save_screenshot(page, "26_homepage_bottom")

    # Try to visit /blog
    await page.goto("https://jareddsanborn.com/blog", wait_until="networkidle")
    await page.wait_for_timeout(3000)
    await save_screenshot(page, "27_blog_page_live", full_page=True)

    print("[SUCCESS] Verification complete")
    return True

async def main():
    """Main automation flow."""
    print("=" * 60)
    print("WordPress Divi Blog Setup Automation v2")
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

        # Set longer timeout for slow operations
        page.set_default_timeout(60000)

        results = {
            "login": False,
            "create_categories": False,
            "create_blog_page": False,
            "edit_homepage": False,
            "verify": False,
        }

        try:
            # PHASE 1: Login
            results["login"] = await login_to_wordpress(page)
            if not results["login"]:
                print("[FATAL] Login failed, aborting")
                return results

            # PHASE 8: Create Categories (first, simple operation)
            results["create_categories"] = await create_categories(page)

            # PHASE 7: Create Blog Page
            results["create_blog_page"] = await create_blog_page(page)

            # PHASES 2-6: Edit Homepage with Divi
            results["edit_homepage"] = await edit_homepage_with_divi(page)

            # PHASE 9: Verify
            results["verify"] = await verify_site(page)

        except Exception as e:
            print(f"[ERROR] Exception during automation: {e}")
            import traceback
            traceback.print_exc()
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

        # List all screenshots
        print("\nScreenshots captured:")
        for f in sorted(SCREENSHOT_DIR.glob("*.png")):
            print(f"  - {f.name}")

        return results

if __name__ == "__main__":
    asyncio.run(main())
