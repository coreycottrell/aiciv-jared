#!/usr/bin/env python3
"""
Check the template-parts/footer.php file to understand footer structure.
"""

import asyncio
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

# Configuration
WP_ADMIN_URL = "https://purebrain.ai/wp-admin"
WP_USERNAME = "Aether"
WP_PASSWORD = "b&JJRfs)6yuSWJCc7WiFY)G8"

SCREENSHOT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/wp-footer-template")
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

        # Go to Theme File Editor with template-parts/footer
        print("[NAV] Checking template-parts/footer.php...")

        # First try the direct URL
        await page.goto(f"{WP_ADMIN_URL}/theme-editor.php?file=template-parts%2Ffooter.php", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(3000)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = str(SCREENSHOT_DIR / f"{timestamp}_01_template_parts_footer.png")
        await page.screenshot(path=path, full_page=True)
        print(f"[SCREENSHOT] {path}")

        # Get the file content
        footer_content = await page.evaluate("""
            () => {
                const textarea = document.querySelector('#newcontent, textarea[name="newcontent"]');
                return textarea ? textarea.value : 'Not found';
            }
        """)

        if footer_content and footer_content != 'Not found':
            print(f"\n[TEMPLATE-PARTS/FOOTER.PHP CONTENT]\n{footer_content}")
        else:
            print("[WARN] template-parts/footer.php not found or not accessible")

            # Try to list available theme files
            print("\n[NAV] Listing theme files...")
            await page.goto(f"{WP_ADMIN_URL}/theme-editor.php", wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(3000)

            path = str(SCREENSHOT_DIR / f"{timestamp}_02_theme_files.png")
            await page.screenshot(path=path, full_page=True)
            print(f"[SCREENSHOT] {path}")

            # Get list of theme files
            file_links = await page.query_selector_all("#templateside a[href*='theme-editor']")
            print(f"\n[INFO] Found {len(file_links)} theme files")
            for link in file_links[:20]:
                href = await link.get_attribute("href")
                text = await link.inner_text()
                print(f"  - {text}: {href}")

        # Check WP File Manager plugin for better access
        print("\n[NAV] Checking WP File Manager...")
        await page.goto(f"{WP_ADMIN_URL}/admin.php?page=wp_file_manager", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(5000)

        path = str(SCREENSHOT_DIR / f"{timestamp}_03_file_manager.png")
        await page.screenshot(path=path, full_page=True)
        print(f"[SCREENSHOT] {path}")

        # Check page title to see if File Manager exists
        page_title = await page.title()
        print(f"[INFO] File Manager page title: {page_title}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
