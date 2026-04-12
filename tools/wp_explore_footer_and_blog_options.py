#!/usr/bin/env python3
"""
Explore Footer Options and Blog Options in Theme Customizer.
Also check existing blog post editing to see social icons setup.
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

async def login(page):
    print("[NAV] Logging in...")
    await page.goto(WP_URL, wait_until="domcontentloaded", timeout=60000)
    await page.wait_for_timeout(3000)

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

        await login(page)

        # Go directly to Footer Options in Customizer
        print("[NAV] Going to Footer Options in Customizer...")
        # Use the deep link to footer options section
        await page.goto(f"{WP_URL}/customize.php?autofocus[section]=footer_options", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(8000)
        await save_screenshot(page, "footer_options_direct")

        # Try Blog Options section
        print("[NAV] Going to Blog Options...")
        await page.goto(f"{WP_URL}/customize.php?autofocus[section]=blog_options", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(5000)
        await save_screenshot(page, "blog_options_direct")

        # Try to explore the customizer panels more carefully
        print("[NAV] Full Customizer exploration...")
        await page.goto(f"{WP_URL}/customize.php", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(10000)

        # Get full panel content
        content = await page.content()

        # Check for any social-related text
        if "facebook" in content.lower():
            print("[FOUND] Facebook mentioned in customizer")
        if "twitter" in content.lower() or "x.com" in content.lower():
            print("[FOUND] Twitter/X mentioned in customizer")
        if "linkedin" in content.lower():
            print("[FOUND] LinkedIn mentioned in customizer")
        if "instagram" in content.lower():
            print("[FOUND] Instagram mentioned in customizer")
        if "social" in content.lower():
            print("[FOUND] Social mentioned in customizer")

        # Try clicking Footer Options panel
        try:
            footer_panel = await page.locator("li.accordion-section:has-text('Footer')").first
            if footer_panel:
                await footer_panel.click()
                await page.wait_for_timeout(3000)
                await save_screenshot(page, "footer_panel_expanded")
        except Exception as e:
            print(f"[INFO] Footer panel click error: {e}")

        # Now go to edit the existing blog post
        print("[NAV] Going to edit blog post...")
        await page.goto(f"{WP_URL}/edit.php", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(3000)

        # Click edit on the first post
        try:
            edit_link = await page.query_selector("a.row-title")
            if edit_link:
                await edit_link.click()
                await page.wait_for_timeout(5000)
                await save_screenshot(page, "post_editor")

                # Look for Elementor edit button
                elementor_btn = await page.query_selector("text='Edit with Elementor'")
                if elementor_btn:
                    print("[FOUND] Edit with Elementor button")
                    await elementor_btn.click()
                    await page.wait_for_timeout(10000)
                    await save_screenshot(page, "post_elementor_editor", full_page=True)
        except Exception as e:
            print(f"[ERROR] Post edit: {e}")

        # Check Yoast SEO settings for social
        print("[NAV] Checking Yoast SEO social settings...")
        await page.goto(f"{WP_URL}/admin.php?page=wpseo_social", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(3000)
        await save_screenshot(page, "yoast_social_settings")

        # Check Yoast settings main page
        await page.goto(f"{WP_URL}/admin.php?page=wpseo_dashboard", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(3000)
        await save_screenshot(page, "yoast_dashboard")

        await browser.close()
        print("[DONE]")

if __name__ == "__main__":
    asyncio.run(main())
