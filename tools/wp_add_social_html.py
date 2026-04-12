#!/usr/bin/env python3
"""
Add social icons to the footer using Elementor's HTML widget or by editing
the footer section directly.

Since Elementor Pro (with Social Icons widget) is not available, we'll use
an HTML approach with Font Awesome icons.
"""

import asyncio
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

# Configuration
WP_ADMIN_URL = "https://purebrain.ai/wp-admin"
WP_USERNAME = "Aether"
WP_PASSWORD = "b&JJRfs)6yuSWJCc7WiFY)G8"
HOMEPAGE_ID = "11"

SOCIAL_HTML = '''
<div class="footer-social-icons" style="display: flex; gap: 15px; justify-content: center; margin-top: 20px;">
    <a href="https://www.linkedin.com/company/purebrain-ai/" target="_blank" rel="noopener noreferrer" style="color: #fff; font-size: 24px;" aria-label="LinkedIn">
        <i class="fab fa-linkedin"></i>
    </a>
    <a href="https://www.facebook.com/PureBrainAI/" target="_blank" rel="noopener noreferrer" style="color: #fff; font-size: 24px;" aria-label="Facebook">
        <i class="fab fa-facebook"></i>
    </a>
    <a href="https://x.com/PureBrainAI" target="_blank" rel="noopener noreferrer" style="color: #fff; font-size: 24px;" aria-label="X/Twitter">
        <i class="fab fa-x-twitter"></i>
    </a>
    <a href="https://www.instagram.com/purebrain.ai/" target="_blank" rel="noopener noreferrer" style="color: #fff; font-size: 24px;" aria-label="Instagram">
        <i class="fab fa-instagram"></i>
    </a>
</div>
'''

SCREENSHOT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/wp-add-social")
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

        # Check if the footer HTML can be edited through WP File Manager
        print("[NAV] Checking if we can edit the footer via File Manager...")

        await page.goto(f"{WP_ADMIN_URL}/admin.php?page=wp_file_manager", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(5000)

        await page.screenshot(path=ss("01_file_manager"))
        print(f"[SCREENSHOT] File Manager")

        # Check if File Manager loaded
        page_title = await page.title()
        if "File Manager" in page_title:
            print("[INFO] WP File Manager is available")

            # Navigate to theme folder
            # Look for wp-content/themes in the file tree
            print("[ACTION] Looking for theme files...")

            # The File Manager plugin uses a specific interface
            # Try to navigate to themes folder
            themes_path = "wp-content/themes/artistics/template-parts"

            # First check if there's a child theme
            child_theme_path = "wp-content/themes/artistics-child"

            await page.screenshot(path=ss("02_file_manager_view"))
            print(f"[SCREENSHOT] File Manager view")

        # Alternative approach: Edit via Elementor
        print("\n[NAV] Opening Elementor to find footer section...")

        elementor_url = f"https://purebrain.ai/?p={HOMEPAGE_ID}&elementor"
        await page.goto(elementor_url, wait_until="domcontentloaded", timeout=120000)
        await page.wait_for_timeout(15000)  # Wait longer for Elementor

        # Close any popups
        try:
            skip_buttons = await page.query_selector_all("button:has-text('Skip'), .dialog-close-button, [aria-label='Close'], .eicon-close")
            for btn in skip_buttons:
                try:
                    await btn.click(timeout=2000)
                except:
                    pass
            await page.wait_for_timeout(1000)
        except:
            pass

        await page.screenshot(path=ss("03_elementor_loaded"))
        print(f"[SCREENSHOT] Elementor loaded")

        # Scroll down in the Elementor preview to see the footer
        print("[ACTION] Scrolling to footer in preview...")

        # Try to scroll the preview iframe
        try:
            await page.evaluate("""
                () => {
                    const iframe = document.getElementById('elementor-preview-iframe');
                    if (iframe && iframe.contentWindow) {
                        iframe.contentWindow.scrollTo(0, iframe.contentDocument.body.scrollHeight);
                    }
                }
            """)
            await page.wait_for_timeout(2000)
        except:
            pass

        await page.screenshot(path=ss("04_scrolled"))
        print(f"[SCREENSHOT] Scrolled view")

        # Find the footer section in the preview
        print("[ACTION] Trying to click on footer section...")

        # Use frame locator for iframe content
        preview_frame = page.frame_locator("#elementor-preview-iframe")

        # Try to click on the footer
        try:
            footer = preview_frame.locator("footer, .footer").first
            await footer.click()
            await page.wait_for_timeout(2000)
            print("[SUCCESS] Clicked on footer!")

            await page.screenshot(path=ss("05_footer_clicked"))
            print(f"[SCREENSHOT] Footer clicked")
        except Exception as e:
            print(f"[WARN] Could not click footer: {e}")

        # Get the element panel
        print("\n[ACTION] Checking element/section settings...")

        # Look at what's in the element panel
        panel_content = await page.evaluate("""
            () => {
                const panel = document.querySelector('#elementor-panel-content-wrapper, .elementor-panel-content');
                return panel ? panel.innerHTML.substring(0, 2000) : 'Panel not found';
            }
        """)
        print(f"[DEBUG] Panel content preview: {panel_content[:500]}...")

        # Check the navigator for the page structure
        print("\n[ACTION] Opening Navigator...")

        # Try keyboard shortcut
        await page.keyboard.press("Control+i")
        await page.wait_for_timeout(2000)

        await page.screenshot(path=ss("06_navigator"))
        print(f"[SCREENSHOT] Navigator")

        # Get list of sections
        navigator_items = await page.query_selector_all(".elementor-navigator__element .elementor-navigator__element__title, .elementor-navigator__item__title")
        print(f"\n[INFO] Navigator items: {len(navigator_items)}")
        for item in navigator_items[:15]:
            text = await item.inner_text()
            print(f"  - {text}")

        # Try to find a section at the bottom (footer area)
        print("\n[ACTION] Looking for bottom/footer section...")

        # Get all containers/sections
        containers = await page.query_selector_all(".elementor-navigator__element--container, .elementor-navigator__element--section")
        print(f"[INFO] Found {len(containers)} containers/sections")

        if containers:
            # Click on the last one (likely footer)
            last_container = containers[-1]
            await last_container.click()
            await page.wait_for_timeout(2000)

            await page.screenshot(path=ss("07_last_section_selected"))
            print(f"[SCREENSHOT] Last section selected")

            # Check what's selected
            selected_info = await page.evaluate("""
                () => {
                    const selected = document.querySelector('.elementor-navigator__element--active');
                    if (selected) {
                        return selected.innerText.substring(0, 100);
                    }
                    return 'Nothing selected';
                }
            """)
            print(f"[INFO] Selected: {selected_info}")

        await browser.close()

        print("\n" + "="*60)
        print("INVESTIGATION COMPLETE")
        print("="*60)
        print(f"\nScreenshots saved to: {SCREENSHOT_DIR}")
        print("\n" + "="*60)
        print("RECOMMENDED SOLUTION")
        print("="*60)
        print("""
Since Elementor Pro is not available (no Social Icons widget),
the best approach is to:

1. **MANUAL APPROACH (Recommended)**:
   - Open https://purebrain.ai/wp-admin/post.php?post=11&action=elementor
   - Navigate to the footer section
   - Add an HTML widget
   - Paste the social icons HTML (Font Awesome)
   - Publish

2. **THEME CUSTOMIZER APPROACH**:
   The social URLs are already configured in Customizer:
   - LinkedIn: https://www.linkedin.com/company/purebrain-ai/
   - Facebook: https://www.facebook.com/PureBrainAI/
   - X/Twitter: https://x.com/PureBrainAI
   - Instagram: https://www.instagram.com/purebrain.ai/

   But the Elementor Canvas page doesn't use the theme's footer.php,
   so these URLs won't display automatically.

3. **ALTERNATIVE: Edit template-parts/footer.php**:
   The theme already has social icon code, but since the page uses
   Elementor Canvas template, the theme footer is bypassed.

BLOCKING ISSUE:
The footer is built WITH Elementor inside the page content.
To add social icons, you need to either:
- Edit the page in Elementor (add HTML widget)
- Change page template from "Elementor Canvas" to use theme footer
- Add custom code to display social icons in the Elementor footer section
""")


if __name__ == "__main__":
    asyncio.run(main())
