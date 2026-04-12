#!/usr/bin/env python3
"""
Verify blog page after CSS clear
"""

import time
from playwright.sync_api import sync_playwright

def verify_blog():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        print("Navigating to blog page...")
        page.goto("https://purebrain.ai/blog/", timeout=60000)
        time.sleep(5)

        page.screenshot(path="/tmp/wp_blog_verify.png")
        print("Screenshot saved: /tmp/wp_blog_verify.png")

        # Scroll down to see more content
        page.evaluate("window.scrollBy(0, 500)")
        time.sleep(2)
        page.screenshot(path="/tmp/wp_blog_verify_scrolled.png")
        print("Screenshot saved: /tmp/wp_blog_verify_scrolled.png")

        print("Done!")
        time.sleep(5)
        browser.close()

if __name__ == "__main__":
    verify_blog()
