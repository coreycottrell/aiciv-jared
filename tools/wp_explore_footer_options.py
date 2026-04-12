#!/usr/bin/env python3
"""
Deep exploration of footer options in WordPress Customizer and Theme settings.
Focus on finding where to add social icons to the footer.
"""

import asyncio
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

# Configuration
WP_ADMIN_URL = "https://purebrain.ai/wp-admin"
WP_USERNAME = "Aether"
WP_PASSWORD = "b&JJRfs)6yuSWJCc7WiFY)G8"

SCREENSHOT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/wp-footer-explore")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

def screenshot_path(name: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return str(SCREENSHOT_DIR / f"{timestamp}_{name}.png")


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
        print("[NAV] Going to WordPress login...")
        await page.goto(f"{WP_ADMIN_URL}", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(2000)

        # Handle GoDaddy SSO
        username_link = await page.query_selector("a:has-text('Log in with username and password')")
        if username_link:
            print("[LOGIN] GoDaddy SSO detected - clicking username/password link...")
            await username_link.click()
            await page.wait_for_timeout(2000)

        # Fill login form
        print("[LOGIN] Entering credentials...")
        await page.wait_for_selector("#user_login", state="visible", timeout=10000)
        await page.fill("#user_login", WP_USERNAME)
        await page.fill("#user_pass", WP_PASSWORD)
        await page.click("#wp-submit")
        await page.wait_for_timeout(5000)

        print(f"[INFO] Current URL: {page.url}")

        # Step 1: Check active theme
        print("[NAV] Checking active theme...")
        await page.goto(f"{WP_ADMIN_URL}/themes.php", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(3000)

        path = screenshot_path("01_themes")
        await page.screenshot(path=path, full_page=True)
        print(f"[SCREENSHOT] {path}")

        # Get active theme name
        active_theme = await page.query_selector(".theme.active .theme-name")
        if active_theme:
            theme_name = await active_theme.inner_text()
            print(f"[INFO] Active theme: {theme_name}")

        # Step 2: Check WordPress Customizer - Footer Options section
        print("[NAV] Opening Customizer...")
        await page.goto(f"{WP_ADMIN_URL}/customize.php", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(5000)

        path = screenshot_path("02_customizer_main")
        await page.screenshot(path=path)
        print(f"[SCREENSHOT] {path}")

        # Get all accordion sections
        sections = await page.query_selector_all(".accordion-section")
        print(f"[INFO] Found {len(sections)} customizer sections")

        for section in sections:
            title_elem = await section.query_selector(".accordion-section-title")
            if title_elem:
                title = await title_elem.inner_text()
                section_id = await section.get_attribute("id")
                print(f"  - Section: {title} (id: {section_id})")

        # Step 3: Look for Footer Options section
        print("[NAV] Looking for Footer Options...")
        footer_section = await page.query_selector("[id*='footer'], [aria-label*='Footer'], .accordion-section:has-text('Footer')")
        if footer_section:
            print("[FOUND] Footer section in Customizer!")
            await footer_section.click()
            await page.wait_for_timeout(2000)

            path = screenshot_path("03_footer_section")
            await page.screenshot(path=path)
            print(f"[SCREENSHOT] {path}")
        else:
            print("[INFO] No explicit Footer section found")

        # Step 4: Check Additional CSS or Custom Code options
        print("[NAV] Checking Additional CSS...")
        css_section = await page.query_selector("#accordion-section-custom_css")
        if css_section:
            await css_section.click()
            await page.wait_for_timeout(2000)

            path = screenshot_path("04_additional_css")
            await page.screenshot(path=path)
            print(f"[SCREENSHOT] {path}")

        # Step 5: Check theme file editor for footer.php
        print("[NAV] Checking Theme File Editor for footer.php...")
        await page.goto(f"{WP_ADMIN_URL}/theme-editor.php", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(3000)

        path = screenshot_path("05_theme_editor")
        await page.screenshot(path=path, full_page=True)
        print(f"[SCREENSHOT] {path}")

        # Look for footer.php in the file list
        footer_file = await page.query_selector("a[href*='footer.php']")
        if footer_file:
            print("[FOUND] footer.php found!")
            await footer_file.click()
            await page.wait_for_timeout(3000)

            path = screenshot_path("06_footer_php")
            await page.screenshot(path=path, full_page=True)
            print(f"[SCREENSHOT] {path}")

            # Get footer.php content
            editor = await page.query_selector("#newcontent, textarea[name='newcontent']")
            if editor:
                content = await editor.input_value()
                print(f"\n[FOOTER.PHP CONTENT (first 3000 chars)]\n{content[:3000]}")

        # Step 6: Check pages for footer Elementor section
        print("[NAV] Checking pages for Elementor footer section...")
        await page.goto(f"{WP_ADMIN_URL}/edit.php?post_type=page", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(3000)

        path = screenshot_path("07_pages_list")
        await page.screenshot(path=path, full_page=True)
        print(f"[SCREENSHOT] {path}")

        # Step 7: Check if there's a way to add social icons via Customizer widgets
        print("[NAV] Checking Customizer widgets for footer...")
        await page.goto(f"{WP_ADMIN_URL}/customize.php?autofocus[panel]=widgets", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(5000)

        path = screenshot_path("08_customizer_widgets")
        await page.screenshot(path=path)
        print(f"[SCREENSHOT] {path}")

        # Step 8: Check if Social Icons widget exists
        print("[NAV] Checking available widgets...")
        await page.goto(f"{WP_ADMIN_URL}/widgets.php", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(3000)

        # Search for social in widgets
        page_content = await page.content()
        has_social_widget = "social" in page_content.lower()
        print(f"[INFO] Social widget available: {has_social_widget}")

        # Step 9: Check Yoast SEO social settings
        print("[NAV] Checking Yoast SEO social profiles...")
        await page.goto(f"{WP_ADMIN_URL}/admin.php?page=wpseo_social", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(3000)

        path = screenshot_path("09_yoast_social")
        await page.screenshot(path=path, full_page=True)
        print(f"[SCREENSHOT] {path}")

        # Check if page loaded
        page_title = await page.title()
        print(f"[INFO] Yoast social page title: {page_title}")

        # Step 10: Check for plugin options for social icons
        print("[NAV] Checking installed plugins...")
        await page.goto(f"{WP_ADMIN_URL}/plugins.php", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(3000)

        path = screenshot_path("10_plugins")
        await page.screenshot(path=path, full_page=True)
        print(f"[SCREENSHOT] {path}")

        # Look for social plugins
        plugins_content = await page.content()
        social_plugins = ["social icons", "social media", "social links", "simple social"]
        for sp in social_plugins:
            if sp in plugins_content.lower():
                print(f"[FOUND] Plugin containing '{sp}' is installed")

        await browser.close()

        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"Screenshots saved to: {SCREENSHOT_DIR}")


if __name__ == "__main__":
    asyncio.run(main())
