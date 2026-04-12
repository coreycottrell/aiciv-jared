#!/usr/bin/env python3
"""
Verify footer social icons are displaying correctly on purebrain.ai
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

        print("[NAV] Going to purebrain.ai...")
        await page.goto("https://purebrain.ai", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(5000)

        # Take full page screenshot
        full_path = screenshot_path("full_page")
        await page.screenshot(path=full_path, full_page=True)
        print(f"[SCREENSHOT] Full page: {full_path}")

        # Scroll to the very bottom
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(2000)

        # Take viewport screenshot at bottom
        bottom_path = screenshot_path("footer_viewport")
        await page.screenshot(path=bottom_path)
        print(f"[SCREENSHOT] Footer viewport: {bottom_path}")

        # Look for footer element specifically
        footer = await page.query_selector("footer")
        if footer:
            # Screenshot just the footer element
            footer_path = screenshot_path("footer_element")
            await footer.screenshot(path=footer_path)
            print(f"[SCREENSHOT] Footer element: {footer_path}")

            # Get footer HTML
            footer_html = await footer.inner_html()
            print("\n[FOOTER HTML]")
            print(footer_html)
        else:
            print("[WARN] Footer element not found")

        # Look for social links
        social_links = await page.query_selector_all("footer a[href*='facebook'], footer a[href*='linkedin'], footer a[href*='twitter'], footer a[href*='instagram'], footer a[href*='youtube'], footer a[href*='x.com']")
        print(f"\n[INFO] Found {len(social_links)} social links in footer")

        for link in social_links:
            href = await link.get_attribute("href")
            print(f"  - {href}")

        # Also check any social icon classes
        social_icons = await page.query_selector_all("footer .social-icon, footer .social-link, footer [class*='social'], footer i[class*='fa-']")
        print(f"\n[INFO] Found {len(social_icons)} elements with social-related classes")

        await browser.close()
        print("\n[DONE]")

if __name__ == "__main__":
    asyncio.run(main())
