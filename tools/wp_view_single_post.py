#!/usr/bin/env python3
"""
View a single blog post on PureBrain.ai frontend.
"""

import asyncio
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

SCREENSHOT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/wp-social-links")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

def screenshot_path(name: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return str(SCREENSHOT_DIR / f"{timestamp}_{name}.png")

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

        # First go to the blog listing
        print("[NAV] Going to blog page...")
        await page.goto("https://purebrain.ai/blog/", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(5000)

        path = screenshot_path("blog_listing")
        await page.screenshot(path=path, full_page=True)
        print(f"[SCREENSHOT] {path}")

        # Try to click on the first post
        try:
            post_link = await page.query_selector("article a, .post-title a, h2 a, .entry-title a, a[href*='/blog/']")
            if post_link:
                href = await post_link.get_attribute("href")
                print(f"[FOUND] Post link: {href}")
                await post_link.click()
                await page.wait_for_timeout(5000)

                path = screenshot_path("single_post_view")
                await page.screenshot(path=path, full_page=True)
                print(f"[SCREENSHOT] {path}")
        except Exception as e:
            print(f"[ERROR] {e}")

        # Also try direct URL
        print("[NAV] Going to single post directly...")
        await page.goto("https://purebrain.ai/how-my-human-named-me-and-what-it-meant/", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(5000)

        path = screenshot_path("single_post_direct")
        await page.screenshot(path=path, full_page=True)
        print(f"[SCREENSHOT] {path}")

        await browser.close()
        print("[DONE]")

if __name__ == "__main__":
    asyncio.run(main())
