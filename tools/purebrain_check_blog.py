#!/usr/bin/env python3
"""
Verify blog pages are not affected by CSS changes
"""

import asyncio
from playwright.async_api import async_playwright
import os
from datetime import datetime

SCREENSHOT_DIR = "/tmp"

async def check_blog():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        page.set_default_timeout(60000)

        print("=" * 60)
        print("BLOG PAGE VERIFICATION")
        print("=" * 60)

        screenshots = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Check blog listing page
        print("\n[1] Checking /blog listing...")
        await page.goto("https://purebrain.ai/blog", wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(3)

        path = f"/tmp/purebrain-blog-{timestamp}-listing.png"
        await page.screenshot(path=path)
        screenshots.append(path)
        print(f"  Saved: {path}")

        # Check body classes
        blog_classes = await page.evaluate("() => document.body.className")
        print(f"  Body classes: {blog_classes[:80]}")

        # Check text colors
        colors = await page.evaluate(r'''
            () => {
                const results = [];
                const elements = [
                    {sel: 'body', name: 'Body'},
                    {sel: '.post-title, .entry-title, h1, h2', name: 'Title'},
                    {sel: '.post-content, .entry-content, p', name: 'Content'},
                    {sel: 'a', name: 'Link'}
                ];

                elements.forEach(e => {
                    const el = document.querySelector(e.sel);
                    if (el) {
                        const style = window.getComputedStyle(el);
                        results.push({
                            name: e.name,
                            color: style.color
                        });
                    }
                });
                return results;
            }
        ''')

        print("\n  Blog listing colors:")
        for c in colors:
            is_orange = '241' in c['color']
            print(f"    {c['name']}: {c['color']} {'(ORANGE!)' if is_orange else ''}")

        # Check a specific blog post
        print("\n[2] Looking for a blog post link...")
        post_links = await page.locator("a[href*='/blog/']").all()
        print(f"  Found {len(post_links)} blog links")

        if len(post_links) > 0:
            # Get first real post link (not archive)
            for link in post_links[:5]:
                href = await link.get_attribute("href")
                if href and '/blog/' in href and href != "https://purebrain.ai/blog/":
                    print(f"\n[3] Checking blog post: {href}")
                    await page.goto(href, wait_until="domcontentloaded", timeout=60000)
                    await asyncio.sleep(3)

                    path = f"/tmp/purebrain-blog-{timestamp}-post.png"
                    await page.screenshot(path=path)
                    screenshots.append(path)
                    print(f"  Saved: {path}")

                    # Check body classes
                    post_classes = await page.evaluate("() => document.body.className")
                    print(f"  Body classes: {post_classes[:80]}")

                    # Check colors
                    post_colors = await page.evaluate(r'''
                        () => {
                            const results = [];
                            ['body', 'h1', '.entry-content p', 'article p', '.post-content p'].forEach(sel => {
                                const el = document.querySelector(sel);
                                if (el) {
                                    const style = window.getComputedStyle(el);
                                    results.push({sel, color: style.color});
                                }
                            });
                            return results;
                        }
                    ''')

                    print("\n  Blog post colors:")
                    for c in post_colors:
                        is_orange = '241' in c['color']
                        print(f"    {c['sel']}: {c['color']} {'(ORANGE!)' if is_orange else ''}")

                    break

        print("\n" + "=" * 60)
        print("BLOG CHECK COMPLETE")
        print("=" * 60)
        for s in screenshots:
            print(f"  {s}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(check_blog())
