#!/usr/bin/env python3
"""
Find where the custom footer is defined (Elementor, page template, or plugin).
"""

import asyncio
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

# Configuration
WP_ADMIN_URL = "https://purebrain.ai/wp-admin"
WP_USERNAME = "Aether"
WP_PASSWORD = "b&JJRfs)6yuSWJCc7WiFY)G8"

SCREENSHOT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/wp-find-footer")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


async def main():
    async with async_playwright() as p:
        print("[INIT] Launching browser...")
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )

        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()

        # Login
        print("[NAV] Logging in...")
        await page.goto(f"{WP_ADMIN_URL}", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(2000)

        username_link = await page.query_selector("a:has-text('Log in with username and password')")
        if username_link:
            await username_link.click()
            await page.wait_for_timeout(2000)

        await page.wait_for_selector("#user_login", state="visible", timeout=10000)
        await page.fill("#user_login", WP_USERNAME)
        await page.fill("#user_pass", WP_PASSWORD)
        await page.click("#wp-submit")
        await page.wait_for_timeout(5000)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Check the homepage in Elementor
        print("[NAV] Checking Elementor pages for footer section...")

        # First, find the front page
        await page.goto(f"{WP_ADMIN_URL}/edit.php?post_type=page", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(3000)

        path = str(SCREENSHOT_DIR / f"{timestamp}_01_pages.png")
        await page.screenshot(path=path, full_page=True)
        print(f"[SCREENSHOT] {path}")

        # Get list of pages
        page_rows = await page.query_selector_all("tr.type-page")
        print(f"\n[INFO] Found {len(page_rows)} pages")

        for row in page_rows[:10]:
            title_elem = await row.query_selector(".row-title")
            if title_elem:
                title = await title_elem.inner_text()
                # Check for front page indicator
                post_state = await row.query_selector(".post-state")
                state = await post_state.inner_text() if post_state else ""
                print(f"  - {title} {state}")

        # Edit the front page with Elementor
        print("\n[NAV] Looking for Elementor 'Edit with Elementor' option...")

        # Find the front page (Home)
        front_page_link = await page.query_selector("a.row-title:has-text('Home'), a.row-title:has-text('Pure Brain')")
        if front_page_link:
            href = await front_page_link.get_attribute("href")
            # Extract post ID from href
            import re
            match = re.search(r'post=(\d+)', href)
            if match:
                post_id = match.group(1)
                print(f"[INFO] Front page post ID: {post_id}")

                # Go to Elementor editor
                elementor_url = f"https://purebrain.ai/?p={post_id}&elementor"
                await page.goto(elementor_url, wait_until="domcontentloaded", timeout=60000)
                await page.wait_for_timeout(8000)

                path = str(SCREENSHOT_DIR / f"{timestamp}_02_elementor_editor.png")
                await page.screenshot(path=path)
                print(f"[SCREENSHOT] {path}")

        # Check if there's a Footer section in Elementor Saved Templates
        print("\n[NAV] Checking Elementor Saved Templates...")
        await page.goto(f"{WP_ADMIN_URL}/edit.php?post_type=elementor_library", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(3000)

        path = str(SCREENSHOT_DIR / f"{timestamp}_03_elementor_templates.png")
        await page.screenshot(path=path, full_page=True)
        print(f"[SCREENSHOT] {path}")

        # Look for footer template
        template_rows = await page.query_selector_all("tr.type-elementor_library")
        print(f"\n[INFO] Found {len(template_rows)} Elementor templates")
        for row in template_rows:
            title_elem = await row.query_selector(".row-title")
            if title_elem:
                title = await title_elem.inner_text()
                print(f"  - {title}")

        # Search all content for the footer HTML pattern
        print("\n[NAV] Searching database for custom footer HTML...")

        # Check if there's Code Snippets plugin
        await page.goto(f"{WP_ADMIN_URL}/admin.php?page=snippets", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(3000)

        page_title = await page.title()
        if "snippets" in page_title.lower():
            path = str(SCREENSHOT_DIR / f"{timestamp}_04_code_snippets.png")
            await page.screenshot(path=path, full_page=True)
            print(f"[SCREENSHOT] {path}")
            print("[INFO] Code Snippets plugin found - checking for footer code...")

        # Check Custom CSS/JS plugin
        print("\n[NAV] Checking for Custom CSS/JS...")
        await page.goto(f"{WP_ADMIN_URL}/edit.php?post_type=custom-css-js", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(3000)

        path = str(SCREENSHOT_DIR / f"{timestamp}_05_custom_css_js.png")
        await page.screenshot(path=path, full_page=True)
        print(f"[SCREENSHOT] {path}")

        # Check WP File Manager for footer-related files
        print("\n[NAV] Checking WP File Manager for custom footer files...")
        await page.goto(f"{WP_ADMIN_URL}/admin.php?page=wp_file_manager", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(5000)

        path = str(SCREENSHOT_DIR / f"{timestamp}_06_file_manager.png")
        await page.screenshot(path=path)
        print(f"[SCREENSHOT] {path}")

        # View the page source to find where footer class comes from
        print("\n[NAV] Analyzing page source for footer origin...")
        await page.goto("https://purebrain.ai/", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(3000)

        # Search for footer__content in page source
        page_html = await page.content()

        # Look for clues about where this custom footer might come from
        if 'footer__content' in page_html:
            print("[FOUND] 'footer__content' class is present in page")

            # Search for potential source indicators
            patterns = [
                r'elementor-widget-[a-z-]+',
                r'data-elementor-[a-z-]+',
                r'class="[^"]*elementor[^"]*"',
                r'wp-block-[a-z-]+',
                r'<!-- Footer',
                r'custom-footer'
            ]
            import re
            for pattern in patterns:
                matches = re.findall(pattern, page_html[:50000])
                if matches:
                    print(f"  Pattern '{pattern}': {list(set(matches))[:5]}")

        # Check the homepage settings
        print("\n[NAV] Checking Reading Settings...")
        await page.goto(f"{WP_ADMIN_URL}/options-reading.php", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(3000)

        path = str(SCREENSHOT_DIR / f"{timestamp}_07_reading_settings.png")
        await page.screenshot(path=path)
        print(f"[SCREENSHOT] {path}")

        # Get homepage ID
        homepage_select = await page.query_selector("select[name='page_on_front']")
        if homepage_select:
            selected_value = await homepage_select.input_value()
            print(f"[INFO] Homepage ID: {selected_value}")

            # Edit this page
            await page.goto(f"{WP_ADMIN_URL}/post.php?post={selected_value}&action=edit", wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(3000)

            path = str(SCREENSHOT_DIR / f"{timestamp}_08_homepage_editor.png")
            await page.screenshot(path=path, full_page=True)
            print(f"[SCREENSHOT] {path}")

        await browser.close()

        print("\n" + "="*60)
        print("INVESTIGATION COMPLETE")
        print("="*60)
        print(f"\nScreenshots saved to: {SCREENSHOT_DIR}")


if __name__ == "__main__":
    asyncio.run(main())
