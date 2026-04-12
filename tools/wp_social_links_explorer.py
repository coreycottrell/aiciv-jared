#!/usr/bin/env python3
"""
WordPress Social Media Links Explorer
Explores options for adding social media profile links to single post template.

Target: purebrain.ai/wp-admin
Goal: Find best way to add LinkedIn, Facebook, X, Instagram, Bluesky links

Usage:
    python3 tools/wp_social_links_explorer.py
"""

import asyncio
import os
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

# Configuration
WP_URL = "https://purebrain.ai/wp-admin"
WP_USERNAME = "Aether"
WP_PASSWORD = "b&JJRfs)6yuSWJCc7WiFY)G8"
SCREENSHOT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/wp-social-links")

# Social links to add
SOCIAL_LINKS = {
    "linkedin": "https://www.linkedin.com/company/purebrain-ai/",
    "facebook": "https://www.facebook.com/PureBrainAI/",
    "twitter": "https://x.com/PureBrainAI",
    "instagram": "https://www.instagram.com/purebrain.ai/",
    "bluesky": "https://bsky.app/profile/jaredsanborn.bsky.social"
}

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

async def safe_goto(page, url, wait_time=5000):
    """Navigate to URL with domcontentloaded and then wait."""
    print(f"[NAV] Going to: {url}")
    await page.goto(url, wait_until="domcontentloaded", timeout=60000)
    await page.wait_for_timeout(wait_time)

async def login_to_wordpress(page):
    """Login to WordPress admin."""
    print("\n=== PHASE 1: Login to WordPress ===")

    await safe_goto(page, WP_URL)

    # Check if already logged in
    if "wp-login.php" not in page.url:
        content = await page.content()
        if "wpbody" in content or "dashboard" in content.lower():
            print("[INFO] Already logged in")
            await save_screenshot(page, "01_already_logged_in")
            return True

    await save_screenshot(page, "01_login_page")

    # GoDaddy login page - need to click "Log in with username and password" first
    try:
        # Look for the text link to show username/password form
        username_password_link = await page.query_selector("text='Log in with username and password'")
        if username_password_link:
            print("[INFO] Found GoDaddy login page - clicking username/password option")
            await username_password_link.click()
            await page.wait_for_timeout(2000)
            await save_screenshot(page, "01b_login_form_revealed")
    except Exception as e:
        print(f"[INFO] No GoDaddy login toggle found: {e}")

    # Now try the standard login form
    try:
        # Wait for login form to be visible
        await page.wait_for_selector("#user_login", state="visible", timeout=10000)

        await page.fill("#user_login", WP_USERNAME, timeout=10000)
        await page.fill("#user_pass", WP_PASSWORD, timeout=10000)
        await page.wait_for_timeout(500)
        await save_screenshot(page, "02_credentials_entered")

        # Click login button
        await page.click("#wp-submit")
        await page.wait_for_timeout(5000)

        await save_screenshot(page, "03_dashboard")
        print("[SUCCESS] Logged into WordPress dashboard")
        return True
    except Exception as e:
        print(f"[ERROR] Login failed: {e}")
        await save_screenshot(page, "03_login_failed")
        return False

async def explore_theme_customizer(page):
    """PHASE 2: Check Theme Customizer for social options."""
    print("\n=== PHASE 2: Explore Theme Customizer ===")

    # Go to Appearance > Customize
    await safe_goto(page, f"{WP_URL}/customize.php")
    await page.wait_for_timeout(3000)
    await save_screenshot(page, "04_customizer_main")

    # Look for social options in customizer panels
    content = await page.content()

    social_keywords = ["social", "footer", "header", "icons", "links", "follow"]
    found_panels = []

    # Try to find and click on panels that might have social settings
    for keyword in social_keywords:
        try:
            # Look for accordion items or panels containing the keyword
            selector = f"[class*='accordion-section']:has-text('{keyword}')"
            elements = await page.query_selector_all(selector)
            if elements:
                found_panels.append(keyword)
                print(f"[FOUND] Panel with '{keyword}' text")
        except Exception as e:
            pass

    # Try clicking on specific panel names
    panel_names = ["Social", "Social Media", "Social Links", "Footer", "Header", "Site Identity"]

    for panel_name in panel_names:
        try:
            panel = await page.query_selector(f"text='{panel_name}'")
            if panel:
                print(f"[FOUND] Panel: {panel_name}")
                await panel.click()
                await page.wait_for_timeout(2000)
                await save_screenshot(page, f"05_panel_{panel_name.lower().replace(' ', '_')}")

                # Go back to main customizer
                back_btn = await page.query_selector(".customize-section-back, .customize-panel-back")
                if back_btn:
                    await back_btn.click()
                    await page.wait_for_timeout(1000)
        except Exception as e:
            pass

    return found_panels

async def explore_elementor_theme_builder(page):
    """PHASE 3: Explore Elementor Theme Builder for single post template."""
    print("\n=== PHASE 3: Explore Elementor Theme Builder ===")

    # Navigate to Elementor > Theme Builder (if Elementor Pro is installed)
    # Try different paths
    elementor_paths = [
        f"{WP_URL}/admin.php?page=elementor-app",
        f"{WP_URL}/edit.php?post_type=elementor_library&tabs_group=theme",
        f"{WP_URL}/edit.php?post_type=elementor_library"
    ]

    for path in elementor_paths:
        try:
            await safe_goto(page, path)
            await page.wait_for_timeout(2000)

            # Check if page loaded successfully
            if "not found" not in (await page.content()).lower():
                await save_screenshot(page, f"06_elementor_{path.split('=')[-1][:20]}")
                print(f"[SUCCESS] Loaded: {path}")

                # Look for Single Post templates
                content = await page.content()
                if "single" in content.lower() or "post" in content.lower():
                    print("[FOUND] May have single post template options")
        except Exception as e:
            print(f"[INFO] Path not available: {path} - {e}")

    # Try Templates submenu
    await safe_goto(page, f"{WP_URL}/edit.php?post_type=elementor_library")
    await page.wait_for_timeout(3000)
    await save_screenshot(page, "07_elementor_templates")

async def explore_widgets(page):
    """PHASE 4: Explore Widgets area for social icons."""
    print("\n=== PHASE 4: Explore Widgets ===")

    await safe_goto(page, f"{WP_URL}/widgets.php")
    await page.wait_for_timeout(3000)
    await save_screenshot(page, "08_widgets_page")

    # Look for available widgets
    content = await page.content()

    social_widget_keywords = ["social", "icon", "follow", "media"]
    for keyword in social_widget_keywords:
        if keyword in content.lower():
            print(f"[FOUND] Widget area mentions '{keyword}'")

async def explore_theme_options(page):
    """PHASE 5: Look for theme-specific options (Hello Elementor, Astra, etc.)."""
    print("\n=== PHASE 5: Explore Theme Options ===")

    # Common theme option pages
    theme_paths = [
        f"{WP_URL}/admin.php?page=theme-options",
        f"{WP_URL}/themes.php?page=theme-options",
        f"{WP_URL}/admin.php?page=astra",
        f"{WP_URL}/admin.php?page=hello-theme",
        f"{WP_URL}/options-general.php"
    ]

    for path in theme_paths:
        try:
            await safe_goto(page, path)
            await page.wait_for_timeout(2000)

            content = await page.content()
            if "not found" not in content.lower() and "error" not in content.lower()[:500]:
                await save_screenshot(page, f"09_theme_{path.split('page=')[-1][:15] if 'page=' in path else 'general'}")
                print(f"[SUCCESS] Found theme options: {path}")
        except Exception as e:
            pass

async def check_plugins(page):
    """PHASE 6: Check installed plugins for social functionality."""
    print("\n=== PHASE 6: Check Installed Plugins ===")

    await safe_goto(page, f"{WP_URL}/plugins.php")
    await page.wait_for_timeout(3000)
    await save_screenshot(page, "10_plugins_page", full_page=True)

    content = await page.content()

    # Look for social-related plugins
    social_plugins = ["social", "share", "follow", "icon", "elementor"]
    found_plugins = []

    for plugin in social_plugins:
        if plugin in content.lower():
            print(f"[FOUND] Plugin mentioning '{plugin}'")
            found_plugins.append(plugin)

    return found_plugins

async def check_single_post_frontend(page):
    """PHASE 7: Check frontend single post to see current state."""
    print("\n=== PHASE 7: Check Single Post Frontend ===")

    # First find a blog post
    await safe_goto(page, f"{WP_URL}/edit.php")
    await page.wait_for_timeout(2000)
    await save_screenshot(page, "11_posts_list")

    # Try to get a post URL
    try:
        first_post_link = await page.query_selector(".row-title")
        if first_post_link:
            post_title = await first_post_link.text_content()
            print(f"[FOUND] First post: {post_title}")

            # Click view link
            view_link = await page.query_selector("a.row-actions:has-text('View')")
            if not view_link:
                # Try post permalink
                await first_post_link.click()
                await page.wait_for_timeout(3000)

                # Look for View Post link
                view_post = await page.query_selector("a:has-text('View Post')")
                if view_post:
                    await view_post.click()
                    await page.wait_for_timeout(3000)
                    await save_screenshot(page, "12_single_post_frontend", full_page=True)
    except Exception as e:
        print(f"[ERROR] Could not view post: {e}")

async def main():
    """Main exploration function."""
    print("=" * 60)
    print("WordPress Social Media Links Explorer")
    print("=" * 60)
    print(f"Target: {WP_URL}")
    print(f"Screenshots: {SCREENSHOT_DIR}")
    print()

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )

        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()

        try:
            # Phase 1: Login
            if not await login_to_wordpress(page):
                print("\n[FATAL] Login failed. Aborting.")
                return

            # Phase 2: Theme Customizer
            customizer_panels = await explore_theme_customizer(page)

            # Phase 3: Elementor Theme Builder
            await explore_elementor_theme_builder(page)

            # Phase 4: Widgets
            await explore_widgets(page)

            # Phase 5: Theme Options
            await explore_theme_options(page)

            # Phase 6: Plugins
            found_plugins = await check_plugins(page)

            # Phase 7: Frontend check
            await check_single_post_frontend(page)

            # Summary
            print("\n" + "=" * 60)
            print("EXPLORATION SUMMARY")
            print("=" * 60)
            print(f"Screenshots saved to: {SCREENSHOT_DIR}")
            print(f"Customizer panels found: {customizer_panels}")
            print(f"Social-related plugins: {found_plugins}")
            print()
            print("SOCIAL LINKS TO ADD:")
            for platform, url in SOCIAL_LINKS.items():
                print(f"  - {platform}: {url}")

        except Exception as e:
            print(f"\n[FATAL ERROR] {e}")
            await save_screenshot(page, "error_state")
            raise
        finally:
            await browser.close()
            print("\n[DONE] Browser closed.")

if __name__ == "__main__":
    asyncio.run(main())
