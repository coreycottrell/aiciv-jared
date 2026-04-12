#!/usr/bin/env python3
"""
Check Theme Customizer for social media options.
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

        # Go to Customizer
        print("[NAV] Going to Theme Customizer...")
        await page.goto(f"{WP_URL}/customize.php", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(8000)
        await save_screenshot(page, "customizer_1_main")

        # Look for social-related panels
        # Click through various panels
        panels_to_check = [
            "General Options",
            "Footer Options",
            "Blog Options",
            "Social",
            "social",
            "Footer"
        ]

        for panel_name in panels_to_check:
            try:
                # Try different selector strategies
                panel = await page.query_selector(f"text='{panel_name}'")
                if not panel:
                    panel = await page.query_selector(f"button:has-text('{panel_name}')")
                if not panel:
                    panel = await page.query_selector(f"h3:has-text('{panel_name}')")
                if not panel:
                    panel = await page.query_selector(f".accordion-section-title:has-text('{panel_name}')")

                if panel:
                    print(f"[FOUND] Panel: {panel_name}")
                    await panel.click()
                    await page.wait_for_timeout(2000)
                    await save_screenshot(page, f"customizer_panel_{panel_name.lower().replace(' ', '_')}")

                    # Look for sub-sections
                    content = await page.content()
                    if "social" in content.lower():
                        print(f"[INFO] '{panel_name}' panel contains social-related options")

                    # Go back
                    back = await page.query_selector(".customize-section-back, .customize-panel-back")
                    if back:
                        await back.click()
                        await page.wait_for_timeout(1000)
            except Exception as e:
                print(f"[INFO] Panel '{panel_name}' not found or error: {e}")

        # Also check the Artistics theme settings if there's a dedicated page
        print("[NAV] Checking Artistics theme settings...")
        await page.goto(f"{WP_URL}/admin.php?page=artistics", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(3000)
        await save_screenshot(page, "artistics_theme_settings")

        # Check for theme options page
        await page.goto(f"{WP_URL}/themes.php?page=artistics-options", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(3000)
        await save_screenshot(page, "artistics_options_page")

        await browser.close()
        print("[DONE]")

if __name__ == "__main__":
    asyncio.run(main())
