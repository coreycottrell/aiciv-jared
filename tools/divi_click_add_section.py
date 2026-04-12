#!/usr/bin/env python3
"""
WordPress Divi - Click Add Section in Visual Builder
Uses precise coordinate clicking based on the visible interface.

Usage:
    python3 tools/divi_click_add_section.py
"""

import asyncio
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

# Configuration
WP_URL = "https://jareddsanborn.com/wp-admin"
WP_USERNAME = "jared@eyefuelpr.nyc"
WP_PASSWORD = "New1Jared88887"
SCREENSHOT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/divi-blog-setup")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

def screenshot_path(name: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return str(SCREENSHOT_DIR / f"add_{timestamp}_{name}.png")

async def save_screenshot(page, name: str, full_page: bool = False):
    path = screenshot_path(name)
    await page.screenshot(path=path, full_page=full_page)
    print(f"[SCREENSHOT] {path}")
    return path

async def main():
    print("=" * 60)
    print("Divi Visual Builder - Add Blog Section")
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
            print("\n[2] Opening Visual Builder...")
            await page.goto("https://jareddsanborn.com/?et_fb=1&PageSpeed=off", wait_until="domcontentloaded")
            await page.wait_for_timeout(15000)
            await save_screenshot(page, "02_visual_builder")

            # Scroll down to a section near the bottom
            print("\n[3] Scrolling to lower sections...")
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.6)")
            await page.wait_for_timeout(2000)
            await save_screenshot(page, "03_scrolled")

            # Click on a section to select it (click in center of visible area)
            print("\n[4] Clicking to select a section...")
            await page.mouse.click(960, 500)
            await page.wait_for_timeout(2000)
            await save_screenshot(page, "04_section_clicked")

            # In Divi, once a section is selected, there should be a blue "+" button
            # at the bottom of the section to add a new section below
            # Based on the screenshots, this appears near the section boundary

            # Look for the add section button (blue circle with +)
            print("\n[5] Looking for add section button...")

            # Try various selectors for the add section button
            add_selectors = [
                ".et-fb-button--add-section",
                ".et_pb_section_add_main",
                "[data-action='add_section']",
                ".et-fb-section--add-below",
                "button[class*='add-section']",
            ]

            for selector in add_selectors:
                try:
                    btn = await page.query_selector(selector)
                    if btn:
                        await btn.click()
                        print(f"[SUCCESS] Clicked: {selector}")
                        await page.wait_for_timeout(2000)
                        await save_screenshot(page, "05_add_section_clicked")
                        break
                except:
                    continue

            # If no button found, try clicking at coordinates where it would appear
            # The add section button typically appears at the bottom center of a selected section
            print("\n[6] Trying coordinate-based click for add button...")
            # Move mouse to bottom of visible section
            await page.mouse.move(960, 900)
            await page.wait_for_timeout(500)
            await save_screenshot(page, "06_hover_bottom")

            # Click where the + button should appear
            await page.mouse.click(960, 900)
            await page.wait_for_timeout(2000)
            await save_screenshot(page, "07_after_bottom_click")

            # Look for section type chooser (Regular, Specialty, Fullwidth)
            print("\n[7] Looking for section type chooser...")
            type_selectors = [
                ".et-fb-section-regular",
                "[data-type='regular']",
                "button:has-text('Regular')",
                ".et_pb_section_regular",
            ]

            for selector in type_selectors:
                try:
                    btn = await page.query_selector(selector)
                    if btn:
                        await btn.click()
                        print(f"[SUCCESS] Selected Regular section: {selector}")
                        await page.wait_for_timeout(2000)
                        await save_screenshot(page, "08_regular_selected")
                        break
                except:
                    continue

            # Now look for the module inserter
            print("\n[8] Looking for module inserter...")
            await page.wait_for_timeout(2000)

            # Try to find and click the "insert module" button
            module_selectors = [
                ".et-fb-button--add-module",
                ".et_pb_insert_module",
                "[data-action='add_module']",
                "button[class*='add-module']",
            ]

            for selector in module_selectors:
                try:
                    btn = await page.query_selector(selector)
                    if btn:
                        await btn.click()
                        print(f"[SUCCESS] Clicked add module: {selector}")
                        await page.wait_for_timeout(2000)
                        await save_screenshot(page, "09_add_module")
                        break
                except:
                    continue

            # If module panel is open, search for Blog
            print("\n[9] Searching for Blog module...")
            try:
                search_input = await page.query_selector("input[type='search'], input[placeholder*='Search']")
                if search_input:
                    await search_input.fill("Blog")
                    await page.wait_for_timeout(1500)
                    await save_screenshot(page, "10_blog_search")

                    # Click on Blog module
                    blog = await page.query_selector("[data-type='et_pb_blog'], .et_pb_blog, :text('Blog') >> nth=0")
                    if blog:
                        await blog.click()
                        await page.wait_for_timeout(3000)
                        await save_screenshot(page, "11_blog_added")
                        print("[SUCCESS] Blog module added!")
            except Exception as e:
                print(f"[WARNING] Could not add Blog module: {e}")

            # Try to save
            print("\n[10] Attempting to save...")
            try:
                # Look for save button in Divi toolbar
                save_btn = await page.query_selector(".et-fb-button--save, [data-action='save'], button:has-text('Save')")
                if save_btn:
                    await save_btn.click()
                    await page.wait_for_timeout(5000)
                    await save_screenshot(page, "12_saved")
                    print("[SUCCESS] Page saved!")
            except:
                # Try keyboard shortcut
                await page.keyboard.press("Control+s")
                await page.wait_for_timeout(3000)

            await save_screenshot(page, "13_final_state", full_page=True)

            print("\n" + "=" * 60)
            print("AUTOMATION COMPLETE")
            print("=" * 60)
            print("Screenshots saved to:", SCREENSHOT_DIR)

        except Exception as e:
            print(f"[ERROR] {e}")
            import traceback
            traceback.print_exc()
            await save_screenshot(page, "error")

        finally:
            await browser.close()

        # List screenshots
        print("\nScreenshots created:")
        for f in sorted(SCREENSHOT_DIR.glob("add_*.png")):
            print(f"  {f}")

if __name__ == "__main__":
    asyncio.run(main())
