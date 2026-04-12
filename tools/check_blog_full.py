#!/usr/bin/env python3
"""
Check full blog page - scroll through entire page
"""

import time
from playwright.sync_api import sync_playwright

def check_blog():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        print("Navigating to blog page...")
        page.goto("https://purebrain.ai/blog/", timeout=60000)
        time.sleep(5)

        # Get page height
        height = page.evaluate("document.body.scrollHeight")
        print(f"Page height: {height}px")

        # Take screenshots at different scroll positions
        positions = [0, 500, 1000, 1500, 2000, 2500, 3000]
        for i, pos in enumerate(positions):
            page.evaluate(f"window.scrollTo(0, {pos})")
            time.sleep(1)
            page.screenshot(path=f"/tmp/wp_blog_full_{i:02d}_{pos}.png")
            print(f"Screenshot at {pos}px: /tmp/wp_blog_full_{i:02d}_{pos}.png")

        # Check for any article or post elements
        articles = page.locator('article').count()
        posts = page.locator('.post').count()
        blog_items = page.locator('.blog-post, .entry, .hentry').count()

        print(f"\nFound elements:")
        print(f"  article tags: {articles}")
        print(f"  .post classes: {posts}")
        print(f"  blog items: {blog_items}")

        # Get page title
        title = page.title()
        print(f"  Page title: {title}")

        # Check what modules/sections exist
        divi_modules = page.locator('[class*="et_pb_"]').count()
        print(f"  Divi modules: {divi_modules}")

        print("\nDone!")
        time.sleep(3)
        browser.close()

if __name__ == "__main__":
    check_blog()
