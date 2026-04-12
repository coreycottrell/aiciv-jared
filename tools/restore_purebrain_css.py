#!/usr/bin/env python3
"""
Restore working CSS to purebrain.ai Additional CSS
Uses Playwright with visible browser (headless=False)
"""

import asyncio
from playwright.async_api import async_playwright
import os
from datetime import datetime

# CSS to restore
CSS_CONTENT = """/* PT Orange Magic Cursor */
#ball {
background: #f1420b !important;
}

/* PT Orange Preloader Spinner - Double Size */
.theme-preloader .loading-container,
.theme-preloader .loading-container .loading {
height: 200px !important;
width: 200px !important;
}

.theme-preloader .loading-container .loading {
border-color: transparent #f1420b transparent #f1420b !important;
}

.theme-preloader .loading-container #loading-icon {
max-width: 132px !important;
}"""

# WordPress credentials
WP_URL = "https://purebrain.ai/wp-admin"
WP_USER = "Aether"
WP_PASSWORD = "b&JJRfs)6yuSWJCc7WiFY)G8"

SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots"

async def main():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    async with async_playwright() as p:
        # Launch visible browser
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        print("Step 1: Navigating to WordPress login...")
        await page.goto(f"{WP_URL}/", wait_until="networkidle", timeout=60000)

        # Take screenshot of login page
        login_screenshot = f"{SCREENSHOT_DIR}/01_login_page_{timestamp}.png"
        await page.screenshot(path=login_screenshot, full_page=True)
        print(f"Screenshot saved: {login_screenshot}")

        # Click "Log in with username and password" link to reveal standard form
        print("Step 2: Clicking 'Log in with username and password' link...")
        try:
            login_with_pass = await page.wait_for_selector('text="Log in with username and password"', timeout=5000)
            await login_with_pass.click()
            await asyncio.sleep(2)
        except Exception as e:
            print(f"Link not found, login form may already be visible: {e}")

        # Take screenshot after clicking
        login2_screenshot = f"{SCREENSHOT_DIR}/02_login_form_{timestamp}.png"
        await page.screenshot(path=login2_screenshot, full_page=True)
        print(f"Screenshot saved: {login2_screenshot}")

        # Fill login form
        print("Step 3: Filling login form...")
        await page.fill("#user_login", WP_USER)
        await page.fill("#user_pass", WP_PASSWORD)
        await page.click("#wp-submit")

        # Wait for dashboard
        await page.wait_for_load_state("networkidle", timeout=60000)
        await asyncio.sleep(2)

        dashboard_screenshot = f"{SCREENSHOT_DIR}/03_dashboard_{timestamp}.png"
        await page.screenshot(path=dashboard_screenshot, full_page=True)
        print(f"Screenshot saved: {dashboard_screenshot}")

        # Navigate to Customizer Additional CSS
        print("Step 4: Navigating to Appearance > Customize...")
        await page.goto("https://purebrain.ai/wp-admin/customize.php?return=%2Fwp-admin%2F",
                       wait_until="networkidle", timeout=90000)
        await asyncio.sleep(5)  # Customizer is slow to load

        customizer_screenshot = f"{SCREENSHOT_DIR}/04_customizer_{timestamp}.png"
        await page.screenshot(path=customizer_screenshot, full_page=True)
        print(f"Screenshot saved: {customizer_screenshot}")

        # Click on Additional CSS panel
        print("Step 5: Clicking Additional CSS...")
        # Try to find and click Additional CSS
        try:
            # Look for Additional CSS in the menu
            additional_css = await page.wait_for_selector('text="Additional CSS"', timeout=10000)
            await additional_css.click()
            await asyncio.sleep(2)
        except Exception as e:
            print(f"Trying alternative selector... {e}")
            # Try by section ID
            try:
                await page.click("#accordion-section-custom_css")
                await asyncio.sleep(2)
            except:
                print("Could not find Additional CSS panel automatically")

        css_panel_screenshot = f"{SCREENSHOT_DIR}/05_css_panel_{timestamp}.png"
        await page.screenshot(path=css_panel_screenshot, full_page=True)
        print(f"Screenshot saved: {css_panel_screenshot}")

        # Find the CSS textarea and clear it
        print("Step 6: Clearing existing CSS and pasting new CSS...")
        try:
            # The customizer uses CodeMirror, need to interact with it
            # First clear the existing content
            css_textarea = await page.query_selector("textarea.wp-customizer-code-textarea, #customize-control-custom_css textarea, .CodeMirror")

            if css_textarea:
                # Try CodeMirror approach
                await page.evaluate("""
                    () => {
                        const cm = document.querySelector('.CodeMirror');
                        if (cm && cm.CodeMirror) {
                            cm.CodeMirror.setValue('');
                        }
                    }
                """)
                await asyncio.sleep(1)

                # Set the new CSS
                await page.evaluate(f"""
                    (css) => {{
                        const cm = document.querySelector('.CodeMirror');
                        if (cm && cm.CodeMirror) {{
                            cm.CodeMirror.setValue(css);
                        }}
                    }}
                """, CSS_CONTENT)
            else:
                print("Could not find CSS editor")

        except Exception as e:
            print(f"Error editing CSS: {e}")

        await asyncio.sleep(2)
        css_edited_screenshot = f"{SCREENSHOT_DIR}/06_css_edited_{timestamp}.png"
        await page.screenshot(path=css_edited_screenshot, full_page=True)
        print(f"Screenshot saved: {css_edited_screenshot}")

        # Click Publish button
        print("Step 7: Publishing changes...")
        try:
            publish_btn = await page.wait_for_selector("#save, #publish, button:has-text('Publish')", timeout=5000)
            await publish_btn.click()
            await asyncio.sleep(3)
        except Exception as e:
            print(f"Could not find publish button: {e}")

        publish_screenshot = f"{SCREENSHOT_DIR}/07_published_{timestamp}.png"
        await page.screenshot(path=publish_screenshot, full_page=True)
        print(f"Screenshot saved: {publish_screenshot}")

        # Now visit the blog page to verify
        print("Step 8: Visiting blog page to verify...")
        await page.goto("https://purebrain.ai/blog/", wait_until="networkidle", timeout=60000)
        await asyncio.sleep(5)  # Wait for any animations/preloader

        blog_screenshot = f"{SCREENSHOT_DIR}/08_blog_page_{timestamp}.png"
        await page.screenshot(path=blog_screenshot, full_page=True)
        print(f"Screenshot saved: {blog_screenshot}")

        print("\nDone! Check screenshots in:", SCREENSHOT_DIR)

        # Keep browser open for manual inspection
        print("\nBrowser will stay open for 30 seconds for manual inspection...")
        await asyncio.sleep(30)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
