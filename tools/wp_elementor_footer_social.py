#!/usr/bin/env python3
"""
Add social media icons to the Elementor footer on purebrain.ai

This script:
1. Logs into WordPress admin
2. Navigates to Elementor Theme Builder
3. Finds and edits the footer template
4. Adds social icons widget with correct URLs
5. Takes screenshots at each step
"""

import asyncio
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

# Configuration
WP_ADMIN_URL = "https://purebrain.ai/wp-admin"
WP_USERNAME = "Aether"
WP_PASSWORD = "b&JJRfs)6yuSWJCc7WiFY)G8"

SOCIAL_LINKS = {
    "linkedin": "https://www.linkedin.com/company/purebrain-ai/",
    "facebook": "https://www.facebook.com/PureBrainAI/",
    "x-twitter": "https://x.com/PureBrainAI",
    "instagram": "https://www.instagram.com/purebrain.ai/",
}

SCREENSHOT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/wp-elementor-footer")
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

        # Step 1: Log into WordPress
        print("[NAV] Going to WordPress login...")
        await page.goto(f"{WP_ADMIN_URL}", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(2000)

        path = screenshot_path("01_login_page")
        await page.screenshot(path=path)
        print(f"[SCREENSHOT] {path}")

        # Check if GoDaddy SSO login is shown - need to click "Log in with username and password"
        print("[LOGIN] Checking for GoDaddy SSO...")
        try:
            username_link = await page.query_selector("a:has-text('Log in with username and password')")
            if username_link:
                print("[LOGIN] GoDaddy SSO detected - clicking username/password link...")
                await username_link.click()
                await page.wait_for_timeout(2000)

                path = screenshot_path("02_login_form_visible")
                await page.screenshot(path=path)
                print(f"[SCREENSHOT] {path}")
        except Exception as e:
            print(f"[INFO] No GoDaddy SSO or already showing form: {e}")

        # Fill login form
        print("[LOGIN] Entering credentials...")
        try:
            # Wait for login form to be visible
            await page.wait_for_selector("#user_login", state="visible", timeout=10000)

            await page.fill("#user_login", WP_USERNAME)
            await page.fill("#user_pass", WP_PASSWORD)

            path = screenshot_path("03_credentials_entered")
            await page.screenshot(path=path)
            print(f"[SCREENSHOT] {path}")

            await page.click("#wp-submit")
            await page.wait_for_timeout(5000)

            path = screenshot_path("04_after_login")
            await page.screenshot(path=path)
            print(f"[SCREENSHOT] {path}")

        except Exception as e:
            print(f"[ERROR] Login failed: {e}")
            path = screenshot_path("error_login")
            await page.screenshot(path=path)
            await browser.close()
            return

        # Step 2: Check if we're logged in
        current_url = page.url
        print(f"[INFO] Current URL after login: {current_url}")

        if "wp-admin" not in current_url:
            print("[ERROR] Login may have failed - not in wp-admin")
            path = screenshot_path("error_not_logged_in")
            await page.screenshot(path=path)

        # Step 3: Navigate to Elementor Theme Builder
        print("[NAV] Going to Elementor Theme Builder...")
        theme_builder_url = f"{WP_ADMIN_URL}/edit.php?post_type=elementor_library&tabs_group=theme"
        await page.goto(theme_builder_url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(3000)

        path = screenshot_path("05_theme_builder")
        await page.screenshot(path=path)
        print(f"[SCREENSHOT] {path}")

        # Step 4: Look for footer template
        print("[SEARCH] Looking for footer template...")

        # Check what's on this page
        page_title = await page.title()
        print(f"[INFO] Page title: {page_title}")

        # Look for footer in the template list
        footer_links = await page.query_selector_all("a[href*='elementor']")
        print(f"[INFO] Found {len(footer_links)} Elementor links")

        # Take full page screenshot
        path = screenshot_path("06_theme_builder_full")
        await page.screenshot(path=path, full_page=True)
        print(f"[SCREENSHOT] {path}")

        # Try to find the footer template specifically
        # Look for various patterns
        selectors_to_try = [
            "a:has-text('Footer')",
            "a:has-text('footer')",
            ".row-title:has-text('Footer')",
            ".row-title:has-text('footer')",
            "tr:has-text('Footer') .row-title",
        ]

        footer_found = False
        for selector in selectors_to_try:
            try:
                element = await page.query_selector(selector)
                if element:
                    text = await element.inner_text()
                    print(f"[FOUND] Footer element with selector '{selector}': {text}")
                    footer_found = True
                    break
            except:
                pass

        if not footer_found:
            print("[WARN] Footer template not found in Theme Builder. Checking Templates page...")

            # Try the regular templates page
            templates_url = f"{WP_ADMIN_URL}/edit.php?post_type=elementor_library"
            await page.goto(templates_url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(3000)

            path = screenshot_path("07_templates_page")
            await page.screenshot(path=path, full_page=True)
            print(f"[SCREENSHOT] {path}")

        # Step 5: Try Appearance > Widgets
        print("[NAV] Checking Appearance > Widgets...")
        widgets_url = f"{WP_ADMIN_URL}/widgets.php"
        await page.goto(widgets_url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(3000)

        path = screenshot_path("08_widgets_page")
        await page.screenshot(path=path, full_page=True)
        print(f"[SCREENSHOT] {path}")

        # Look for widget areas
        widget_areas = await page.query_selector_all(".widget-liquid-left, .widgets-holder-wrap")
        print(f"[INFO] Found {len(widget_areas)} widget areas")

        # Step 6: Try Elementor > Settings to check Elementor Pro status
        print("[NAV] Checking Elementor settings...")
        elementor_settings_url = f"{WP_ADMIN_URL}/admin.php?page=elementor"
        await page.goto(elementor_settings_url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(3000)

        path = screenshot_path("09_elementor_settings")
        await page.screenshot(path=path, full_page=True)
        print(f"[SCREENSHOT] {path}")

        # Check for Pro features
        page_content = await page.content()
        has_pro = "elementor-pro" in page_content.lower() or "pro features" in page_content.lower()
        print(f"[INFO] Elementor Pro detected: {has_pro}")

        # Step 7: Try WordPress Customizer
        print("[NAV] Checking WordPress Customizer...")
        customizer_url = "https://purebrain.ai/wp-admin/customize.php"
        await page.goto(customizer_url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(5000)

        path = screenshot_path("10_customizer")
        await page.screenshot(path=path)
        print(f"[SCREENSHOT] {path}")

        # Look for footer section in customizer
        customizer_sections = await page.query_selector_all("#accordion-section-sidebar-widgets-footer, #accordion-panel-footer, [id*='footer']")
        print(f"[INFO] Found {len(customizer_sections)} footer-related sections in customizer")

        # Step 8: Check Divi Theme options (since they might be using Divi)
        print("[NAV] Checking Divi Theme Options...")
        divi_url = f"{WP_ADMIN_URL}/admin.php?page=et_divi_options"
        await page.goto(divi_url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(3000)

        path = screenshot_path("11_divi_options")
        await page.screenshot(path=path, full_page=True)
        print(f"[SCREENSHOT] {path}")

        # Check if Divi page loaded
        page_title = await page.title()
        print(f"[INFO] Divi options page title: {page_title}")

        # Step 9: Look for social icons in Divi settings
        # Navigate through Divi menu if available
        divi_menu = await page.query_selector("#toplevel_page_et_divi_options, a:has-text('Divi')")
        if divi_menu:
            print("[INFO] Divi menu found - checking theme customizer...")

            # Try Divi Theme Customizer
            divi_customizer_url = f"{WP_ADMIN_URL}/customize.php?et_customizer_option_set=theme"
            await page.goto(divi_customizer_url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(5000)

            path = screenshot_path("12_divi_customizer")
            await page.screenshot(path=path)
            print(f"[SCREENSHOT] {path}")

        # Step 10: Check the actual footer HTML on the site
        print("[NAV] Checking live site footer...")
        await page.goto("https://purebrain.ai/", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(3000)

        # Scroll to footer
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(1000)

        path = screenshot_path("13_site_footer")
        await page.screenshot(path=path)
        print(f"[SCREENSHOT] {path}")

        # Get footer HTML
        footer = await page.query_selector("footer, #footer, .footer, #et-footer")
        if footer:
            footer_html = await footer.inner_html()
            print(f"\n[FOOTER HTML (first 2000 chars)]\n{footer_html[:2000]}")
        else:
            print("[WARN] Footer element not found")

        # Check for existing social icons
        social_icons = await page.query_selector_all("[class*='social'], a[href*='linkedin'], a[href*='facebook'], a[href*='twitter'], a[href*='instagram']")
        print(f"\n[INFO] Found {len(social_icons)} social-related elements in footer area")
        for icon in social_icons:
            href = await icon.get_attribute("href")
            classes = await icon.get_attribute("class")
            print(f"  - href: {href}, class: {classes}")

        await browser.close()

        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"Screenshots saved to: {SCREENSHOT_DIR}")
        print("\nReview the screenshots to determine:")
        print("1. Is Elementor Pro active (Theme Builder)?")
        print("2. Is Divi theme in use (Divi Options)?")
        print("3. Where is the footer configured (Widgets/Customizer/Theme Builder)?")
        print("4. What social icons, if any, already exist?")


if __name__ == "__main__":
    asyncio.run(main())
