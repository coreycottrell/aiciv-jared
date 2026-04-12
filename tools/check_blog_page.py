#!/usr/bin/env python3
"""
Check purebrain.ai/blog/ and take a full-page screenshot
"""

import asyncio
from playwright.async_api import async_playwright
import os
from datetime import datetime

SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots"

async def main():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        print("Navigating to purebrain.ai/blog/...")
        try:
            # Use domcontentloaded which is faster than networkidle
            await page.goto("https://purebrain.ai/blog/", wait_until="domcontentloaded", timeout=30000)
            # Wait a bit for dynamic content
            await asyncio.sleep(8)
        except Exception as e:
            print(f"Page load issue: {e}")
            # Continue anyway to capture what we can

        blog_screenshot = f"{SCREENSHOT_DIR}/blog_final_{timestamp}.png"
        await page.screenshot(path=blog_screenshot, full_page=True)
        print(f"Screenshot saved: {blog_screenshot}")

        # Also try scrolling down and taking another screenshot
        await page.evaluate("window.scrollBy(0, 800)")
        await asyncio.sleep(2)

        blog_scrolled = f"{SCREENSHOT_DIR}/blog_scrolled_{timestamp}.png"
        await page.screenshot(path=blog_scrolled, full_page=True)
        print(f"Scrolled screenshot saved: {blog_scrolled}")

        await browser.close()
        print("\nDone! Check screenshots.")

if __name__ == "__main__":
    asyncio.run(main())
