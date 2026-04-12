#!/usr/bin/env python3
"""
Find where social icons appear on the site, if anywhere.
Check header, footer, sidebar, etc.
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

        # Take header screenshot
        header = await page.query_selector("header, .header, #header, nav")
        if header:
            header_path = screenshot_path("header")
            await header.screenshot(path=header_path)
            print(f"[SCREENSHOT] Header: {header_path}")

            header_html = await header.inner_html()
            print(f"\n[HEADER HTML (first 1000 chars)]\n{header_html[:1000]}")
        else:
            print("[WARN] Header not found")

        # Search the entire page for social-related links
        all_links = await page.query_selector_all("a[href*='facebook'], a[href*='linkedin'], a[href*='twitter'], a[href*='instagram'], a[href*='youtube'], a[href*='x.com']")
        print(f"\n[INFO] Found {len(all_links)} social links on the page")
        for link in all_links:
            href = await link.get_attribute("href")
            text = await link.inner_text()
            parent = await link.evaluate("el => el.closest('header, footer, aside, .widget, .social')?.className || 'unknown'")
            print(f"  - {href} (text: {text[:30] if text else 'none'}) [parent: {parent}]")

        # Check for any Font Awesome or similar icons
        icons = await page.query_selector_all("i[class*='fa-'], i[class*='icon-'], svg[class*='social'], .social-icon")
        print(f"\n[INFO] Found {len(icons)} icon elements")

        # Navigate to the blog page to check social sharing
        print("\n[NAV] Going to blog page...")
        await page.goto("https://purebrain.ai/blog/", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(3000)

        blog_path = screenshot_path("blog_page")
        await page.screenshot(path=blog_path)
        print(f"[SCREENSHOT] Blog: {blog_path}")

        # Check for social sharing on a blog post
        first_post = await page.query_selector(".post a, article a")
        if first_post:
            post_href = await first_post.get_attribute("href")
            if post_href:
                print(f"\n[NAV] Going to first blog post: {post_href}")
                await page.goto(post_href, wait_until="domcontentloaded", timeout=60000)
                await page.wait_for_timeout(3000)

                post_path = screenshot_path("blog_post")
                await page.screenshot(path=post_path, full_page=True)
                print(f"[SCREENSHOT] Blog post: {post_path}")

                # Look for social sharing buttons on the post
                share_buttons = await page.query_selector_all(".social-share, .sharing, [class*='share'], a[href*='facebook.com/sharer'], a[href*='twitter.com/intent']")
                print(f"\n[INFO] Found {len(share_buttons)} share buttons on post")
                for btn in share_buttons:
                    href = await btn.get_attribute("href")
                    cls = await btn.get_attribute("class")
                    print(f"  - class: {cls}, href: {href}")

        await browser.close()
        print("\n[DONE]")

if __name__ == "__main__":
    asyncio.run(main())
