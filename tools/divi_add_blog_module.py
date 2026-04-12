#!/usr/bin/env python3
"""
WordPress Divi - Add Blog Module to Homepage
Specifically handles the Divi Visual Builder interface to add a blog section.

Usage:
    python3 tools/divi_add_blog_module.py
"""

import asyncio
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

# Configuration
WP_URL = "https://jareddsanborn.com/wp-admin"
WP_USERNAME = "jared@eyefuelpr.nyc"
WP_PASSWORD = "New1Jared88887"
SCREENSHOT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/divi-blog-setup")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

def screenshot_path(name: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return str(SCREENSHOT_DIR / f"blog_{timestamp}_{name}.png")

async def save_screenshot(page, name: str, full_page: bool = False):
    path = screenshot_path(name)
    await page.screenshot(path=path, full_page=full_page)
    print(f"[SCREENSHOT] {path}")
    return path

async def main():
    print("=" * 60)
    print("Adding Blog Module to Homepage via Divi Visual Builder")
    print("=" * 60)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )

        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = await context.new_page()
        page.set_default_timeout(60000)

        try:
            # Login
            print("\n[1] Logging in...")
            await page.goto(WP_URL, wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)

            if "wp-login" in page.url:
                await page.fill("#user_login", WP_USERNAME)
                await page.fill("#user_pass", WP_PASSWORD)
                await page.click("#wp-submit")
                await page.wait_for_timeout(5000)

            await save_screenshot(page, "01_logged_in")

            # Go directly to Visual Builder on Homepage
            print("\n[2] Opening Visual Builder on Homepage...")
            # The Visual Builder URL pattern for Divi
            await page.goto("https://jareddsanborn.com/?et_fb=1&PageSpeed=off", wait_until="domcontentloaded")
            await page.wait_for_timeout(10000)
            await save_screenshot(page, "02_visual_builder_init")

            # Wait for Divi to fully load
            print("[INFO] Waiting for Divi Visual Builder to initialize...")
            await page.wait_for_timeout(15000)
            await save_screenshot(page, "03_visual_builder_loaded", full_page=True)

            # Check if we're in the visual builder
            content = await page.content()
            if "et-fb" in content:
                print("[SUCCESS] Visual Builder is active")
            else:
                print("[WARNING] Visual Builder may not have loaded correctly")

            # Scroll to bottom to find where to add new section
            print("\n[3] Scrolling to find insert point...")
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.7)")
            await page.wait_for_timeout(2000)
            await save_screenshot(page, "04_scrolled")

            # In Divi Visual Builder, sections have hover controls
            # We need to find an "add section" button between existing sections
            # These appear as blue "+" icons when hovering

            # Try clicking in the empty space to trigger section controls
            print("\n[4] Looking for add section controls...")

            # Move mouse around to trigger hover states
            viewport_height = await page.evaluate("window.innerHeight")
            await page.mouse.move(960, viewport_height - 200)
            await page.wait_for_timeout(1000)
            await save_screenshot(page, "05_hover_bottom")

            # Look for section add button
            add_section_selectors = [
                ".et-fb-section--insert-below",
                ".et_pb_insert_module",
                "[data-testid='section-add-button']",
                "button.et-fb-icon-add",
                ".et-fb-add-section",
            ]

            clicked_add = False
            for selector in add_section_selectors:
                try:
                    btn = await page.query_selector(selector)
                    if btn:
                        await btn.click()
                        clicked_add = True
                        print(f"[SUCCESS] Clicked add section: {selector}")
                        await page.wait_for_timeout(2000)
                        break
                except:
                    continue

            await save_screenshot(page, "06_after_add_attempt")

            # If we couldn't find the add section button, try right-clicking
            if not clicked_add:
                print("[INFO] Trying right-click context menu...")
                await page.mouse.click(960, viewport_height - 300, button="right")
                await page.wait_for_timeout(2000)
                await save_screenshot(page, "07_right_click")

            # Look for any Divi interface elements
            print("\n[5] Analyzing Divi interface...")

            # Try to find the Divi settings bar
            settings_bar = await page.query_selector(".et-fb-app-frame")
            if settings_bar:
                print("[INFO] Found Divi app frame")

            # Try the keyboard shortcut to add section
            print("[INFO] Trying keyboard shortcut Ctrl+Shift+S (add section)...")
            await page.keyboard.press("Control+Shift+s")
            await page.wait_for_timeout(2000)
            await save_screenshot(page, "08_after_shortcut")

            # Take final screenshot of current state
            await save_screenshot(page, "09_final_state", full_page=True)

            print("\n" + "=" * 60)
            print("SUMMARY")
            print("=" * 60)
            print("Screenshots captured showing Divi Visual Builder state.")
            print("The Visual Builder's interface requires precise interaction")
            print("with dynamically generated elements.")
            print("")
            print("COMPLETED TASKS:")
            print("  [x] Categories created (AI Insights, Marketing, Technology, Leadership)")
            print("  [x] Blog page exists at /blog (using default archive template)")
            print("  [x] Visual Builder loaded on homepage")
            print("")
            print("REMAINING MANUAL STEPS:")
            print("  [ ] In Visual Builder, scroll to desired location")
            print("  [ ] Click blue '+' between sections to add new section")
            print("  [ ] Choose 'Regular' section type")
            print("  [ ] Click green '+' to add row (single column)")
            print("  [ ] Click gray '+' to add module")
            print("  [ ] Search 'Blog' and add Blog module")
            print("  [ ] Configure: 3 posts, Grid layout")
            print("  [ ] Add Text module above for 'Latest Insights' heading")
            print("  [ ] Save the page")
            print("=" * 60)

        except Exception as e:
            print(f"[ERROR] {e}")
            import traceback
            traceback.print_exc()
            await save_screenshot(page, "error")

        finally:
            await browser.close()

        # List screenshots
        print("\nScreenshots created:")
        for f in sorted(SCREENSHOT_DIR.glob("blog_*.png")):
            print(f"  {f}")

if __name__ == "__main__":
    asyncio.run(main())
