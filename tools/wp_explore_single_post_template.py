#!/usr/bin/env python3
"""
Explore the Single Post template in Elementor Theme Builder.
"""

import asyncio
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

WP_URL = "https://purebrain.ai/wp-admin"
WP_USERNAME = "Aether"
WP_PASSWORD = "b&JJRfs)6yuSWJCc7WiFY)G8"
SCREENSHOT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/wp-social-links")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

def screenshot_path(name: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return str(SCREENSHOT_DIR / f"{timestamp}_{name}.png")

async def save_screenshot(page, name: str, full_page: bool = False):
    path = screenshot_path(name)
    await page.screenshot(path=path, full_page=full_page)
    print(f"[SCREENSHOT] {path}")
    return path

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )

        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()

        # Login
        print("[NAV] Logging in...")
        await page.goto(WP_URL, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(3000)

        # Click username/password option
        try:
            link = await page.query_selector("text='Log in with username and password'")
            if link:
                await link.click()
                await page.wait_for_timeout(2000)
        except:
            pass

        await page.wait_for_selector("#user_login", state="visible", timeout=10000)
        await page.fill("#user_login", WP_USERNAME)
        await page.fill("#user_pass", WP_PASSWORD)
        await page.click("#wp-submit")
        await page.wait_for_timeout(5000)
        print("[SUCCESS] Logged in")

        # Go to Theme Builder
        print("[NAV] Going to Elementor Theme Builder...")
        await page.goto(f"{WP_URL}/admin.php?page=elementor-app#/site-editor/templates/single-post", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(5000)
        await save_screenshot(page, "theme_builder_single_post")

        # Click on Single Post in sidebar
        print("[NAV] Looking for Single Post template...")
        try:
            single_post = await page.query_selector("text='Single Post'")
            if single_post:
                await single_post.click()
                await page.wait_for_timeout(3000)
                await save_screenshot(page, "single_post_template_clicked")
        except Exception as e:
            print(f"[INFO] {e}")

        # Look for any template or add new
        await page.goto(f"{WP_URL}/admin.php?page=elementor-app", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(5000)
        await save_screenshot(page, "elementor_app_main")

        # Try to click Single Post
        try:
            single_post_card = await page.query_selector("[data-testid='single-post'], text='Single Post'")
            if single_post_card:
                await single_post_card.click()
                await page.wait_for_timeout(3000)
                await save_screenshot(page, "single_post_selected")
        except Exception as e:
            print(f"[INFO] {e}")

        # Go to Elementor library templates
        print("[NAV] Checking Elementor library for single post templates...")
        await page.goto(f"{WP_URL}/edit.php?post_type=elementor_library&tabs_group=theme&elementor_library_type=single-post", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(3000)
        await save_screenshot(page, "elementor_single_post_templates")

        # Check if there are any single post templates
        content = await page.content()
        if "No templates found" in content or "No items found" in content:
            print("[INFO] No single post templates exist yet - need to create one")
        else:
            print("[INFO] Single post templates may exist")

        # Try checking the current active theme for single post handling
        print("[NAV] Checking theme files for single-post template...")
        await page.goto(f"{WP_URL}/theme-editor.php?file=single.php", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(3000)
        await save_screenshot(page, "theme_single_php")

        # Check current theme
        await page.goto(f"{WP_URL}/themes.php", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(3000)
        await save_screenshot(page, "current_theme")

        await browser.close()
        print("[DONE]")

if __name__ == "__main__":
    asyncio.run(main())
