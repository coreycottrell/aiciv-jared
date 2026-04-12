#!/usr/bin/env python3
"""
Edit the Elementor homepage to add social icons to the footer section.

The purebrain.ai homepage uses Elementor Canvas template, meaning the footer
is part of the page content, not the theme. We need to:
1. Open the page in Elementor editor
2. Find the footer section
3. Add Social Icons widget
4. Configure the icons with correct URLs
5. Publish
"""

import asyncio
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

# Configuration
WP_ADMIN_URL = "https://purebrain.ai/wp-admin"
WP_USERNAME = "Aether"
WP_PASSWORD = "b&JJRfs)6yuSWJCc7WiFY)G8"
HOMEPAGE_ID = "11"  # From previous investigation

SOCIAL_LINKS = [
    {"icon": "fab fa-linkedin", "url": "https://www.linkedin.com/company/purebrain-ai/"},
    {"icon": "fab fa-facebook", "url": "https://www.facebook.com/PureBrainAI/"},
    {"icon": "fab fa-x-twitter", "url": "https://x.com/PureBrainAI"},
    {"icon": "fab fa-instagram", "url": "https://www.instagram.com/purebrain.ai/"},
]

SCREENSHOT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/wp-elementor-edit")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def ss(name):
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

        print(f"[INFO] Logged in")

        # Go directly to Elementor editor for homepage
        print("[NAV] Opening homepage in Elementor editor...")
        elementor_url = f"https://purebrain.ai/?p={HOMEPAGE_ID}&elementor"
        await page.goto(elementor_url, wait_until="domcontentloaded", timeout=120000)
        await page.wait_for_timeout(10000)  # Wait for Elementor to load

        # Close any popups/modals
        try:
            close_btn = await page.query_selector(".dialog-close-button, .eicon-close, [aria-label='Close']")
            if close_btn:
                await close_btn.click()
                await page.wait_for_timeout(1000)
        except:
            pass

        # Skip the AI notification if present
        skip_btn = await page.query_selector("button:has-text('Skip'), a:has-text('Skip')")
        if skip_btn:
            await skip_btn.click()
            await page.wait_for_timeout(1000)

        await page.screenshot(path=ss("01_elementor_opened"))
        print(f"[SCREENSHOT] Elementor editor opened")

        # Scroll to the bottom of the preview to find the footer section
        print("[ACTION] Scrolling to footer section...")

        # First try scrolling in the preview iframe
        preview_frame = page.frame_locator("#elementor-preview-iframe")

        # Scroll to bottom of preview
        await page.evaluate("""
            () => {
                const iframe = document.getElementById('elementor-preview-iframe');
                if (iframe && iframe.contentDocument) {
                    const body = iframe.contentDocument.body;
                    body.scrollTop = body.scrollHeight;
                    window.scrollTo(0, document.body.scrollHeight);
                }
            }
        """)
        await page.wait_for_timeout(2000)

        await page.screenshot(path=ss("02_scrolled_to_footer"))
        print(f"[SCREENSHOT] Scrolled to footer area")

        # Try to click on the footer section in the preview
        print("[ACTION] Trying to select footer section...")

        # Look for footer element in the preview
        footer_selectors = [
            'iframe#elementor-preview-iframe >>> footer',
            'iframe#elementor-preview-iframe >>> .footer',
            'iframe#elementor-preview-iframe >>> [data-element_type="section"]:last-child',
        ]

        footer_section = None
        for selector in footer_selectors:
            try:
                # Use frame locator for iframe content
                elem = await preview_frame.locator('footer, .footer').first.element_handle()
                if elem:
                    footer_section = elem
                    print(f"[FOUND] Footer element")
                    break
            except:
                pass

        # Use Navigator panel to find footer
        print("[ACTION] Opening Navigator panel to find footer section...")

        # Click Navigator button or use keyboard shortcut
        navigator_btn = await page.query_selector("[data-hint='Navigator'], .elementor-panel-navigator-button")
        if navigator_btn:
            await navigator_btn.click()
            await page.wait_for_timeout(2000)
        else:
            # Try keyboard shortcut
            await page.keyboard.press("Control+i")
            await page.wait_for_timeout(2000)

        await page.screenshot(path=ss("03_navigator_panel"))
        print(f"[SCREENSHOT] Navigator panel")

        # List all sections/elements in navigator
        print("\n[DEBUG] Listing page structure...")
        elements = await page.query_selector_all(".elementor-navigator__element, .elementor-navigator__item")
        print(f"[INFO] Found {len(elements)} elements in navigator")

        for elem in elements[:30]:  # Limit to first 30
            text = await elem.inner_text()
            classes = await elem.get_attribute("class")
            print(f"  - {text.strip()[:50]} ({classes[:50] if classes else ''})")

        # Look for the footer section by name
        footer_nav_item = await page.query_selector(".elementor-navigator__element:has-text('footer'), .elementor-navigator__element:has-text('Footer')")
        if footer_nav_item:
            print("[FOUND] Footer section in navigator")
            await footer_nav_item.click()
            await page.wait_for_timeout(2000)

            await page.screenshot(path=ss("04_footer_selected"))
            print(f"[SCREENSHOT] Footer section selected")

        # Try to add a widget
        print("\n[ACTION] Preparing to add Social Icons widget...")

        # Open widgets panel
        widgets_tab = await page.query_selector("#elementor-panel-header-add-button, .elementor-panel-header-add-button")
        if widgets_tab:
            await widgets_tab.click()
            await page.wait_for_timeout(2000)

        await page.screenshot(path=ss("05_widgets_panel"))
        print(f"[SCREENSHOT] Widgets panel")

        # Search for Social Icons
        search_input = await page.query_selector("#elementor-panel-elements-search-input, input[placeholder*='Search']")
        if search_input:
            await search_input.fill("social icons")
            await page.wait_for_timeout(2000)

            await page.screenshot(path=ss("06_social_icons_search"))
            print(f"[SCREENSHOT] Social icons search results")

        # Check if Social Icons widget exists
        social_widget = await page.query_selector(".elementor-element:has-text('Social Icons'), .elementor-element-wrapper:has-text('Social Icons')")
        if social_widget:
            print("[FOUND] Social Icons widget available!")
        else:
            print("[WARN] Social Icons widget may require Elementor Pro")

            # Try alternative - Text widget with HTML
            print("[ACTION] Trying alternative approach - looking for any social widget...")
            await search_input.fill("social")
            await page.wait_for_timeout(2000)

            await page.screenshot(path=ss("07_social_search"))
            print(f"[SCREENSHOT] Social widget search")

        # Get the list of available widgets
        print("\n[DEBUG] Available widgets matching 'social':")
        widgets = await page.query_selector_all("#elementor-panel-elements-wrapper .elementor-element")
        for widget in widgets[:10]:
            title = await widget.get_attribute("title")
            text = await widget.inner_text()
            print(f"  - {title or text}")

        await browser.close()

        print("\n" + "="*60)
        print("ELEMENTOR EXPLORATION COMPLETE")
        print("="*60)
        print(f"\nScreenshots saved to: {SCREENSHOT_DIR}")
        print("\nFINDINGS:")
        print("1. Homepage uses Elementor Canvas template")
        print("2. Footer is part of page content, not theme")
        print("3. Need to edit page in Elementor to add social icons")
        print("\nNEXT STEPS:")
        print("- If Social Icons widget available: drag to footer section")
        print("- If not: use HTML/Text widget with Font Awesome icons")
        print("- Or: modify footer HTML directly in Elementor")


if __name__ == "__main__":
    asyncio.run(main())
