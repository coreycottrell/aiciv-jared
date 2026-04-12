#!/usr/bin/env python3
"""
Find the Blog page in WordPress and get its ID.
"""

import sys
from playwright.sync_api import sync_playwright

# Configuration
WP_URL = "https://purebrain.ai/wp-admin"
WP_USER = "Aether"
WP_PASS = "b&JJRfs)6yuSWJCc7WiFY)G8"

SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots/blog_edit"

import os

def take_screenshot(page, name):
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    path = f"{SCREENSHOT_DIR}/{name}.png"
    page.screenshot(path=path)
    print(f"Screenshot saved: {path}")
    return path


def login(page):
    """Log into WordPress admin"""
    page.goto(WP_URL, wait_until="networkidle", timeout=30000)
    if page.url.endswith("/wp-login.php") or "wp-login" in page.url:
        link = page.locator('text="Log in with username and password"')
        if link.count() > 0:
            link.click()
            page.wait_for_timeout(1000)
        page.fill("#user_login", WP_USER)
        page.fill("#user_pass", WP_PASS)
        page.click("#wp-submit")
        page.wait_for_load_state("networkidle")
    print(f"Logged in. URL: {page.url}")


def main():
    print("=" * 60)
    print("Finding Blog Page in WordPress")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        try:
            # Login
            login(page)

            # Go to Pages list
            print("\n[Step 1] Going to Pages...")
            page.goto("https://purebrain.ai/wp-admin/edit.php?post_type=page",
                      wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(2000)
            take_screenshot(page, "pages_list")

            # Get all page titles and IDs
            print("\n[Step 2] Getting page list...")

            # Get page data from the table
            rows = page.locator('table.wp-list-table tbody tr').all()
            print(f"Found {len(rows)} pages")

            for row in rows:
                title_link = row.locator('.row-title')
                if title_link.count() > 0:
                    title = title_link.inner_text()
                    # Get the post ID from the row
                    row_id = row.get_attribute('id')
                    if row_id:
                        # ID format is "post-123"
                        post_id = row_id.replace('post-', '')
                        print(f"  Page: {title} (ID: {post_id})")

                        if 'blog' in title.lower():
                            print(f"\n  *** FOUND BLOG PAGE: {title} (ID: {post_id}) ***\n")

            # Let's also check Reading settings to see what page is set as Posts page
            print("\n[Step 3] Checking Reading Settings...")
            page.goto("https://purebrain.ai/wp-admin/options-reading.php",
                      wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(2000)
            take_screenshot(page, "reading_settings")

            # Check what's set for front page and posts page
            print("\nReading settings page captured.")

        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            browser.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
