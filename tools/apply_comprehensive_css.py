#!/usr/bin/env python3
"""
Apply Comprehensive CSS to PureBrain.ai
Replaces existing Additional CSS with the full recommendations file
"""

import asyncio
from playwright.async_api import async_playwright
import os
from datetime import datetime

SCREENSHOT_DIR = "/tmp"

# WordPress credentials from .env
WP_URL = "https://purebrain.ai/wp-admin"
WP_USER = "Aether"
WP_PASS = "NW2u!JLQ3!Bt$XD$7CWzz5Z@"

# CSS file to apply
CSS_FILE = "/home/jared/projects/AI-CIV/aether/exports/PUREBRAIN-ALL-RECOMMENDATIONS-CSS-2026-02-17.css"

async def save_screenshot(page, label):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"purebrain-css-apply-{timestamp}-{label}.png"
    filepath = os.path.join(SCREENSHOT_DIR, filename)
    await page.screenshot(path=filepath, full_page=False)
    print(f"Saved: {filepath}")
    return filepath

async def apply_comprehensive_css():
    # Load CSS from file
    with open(CSS_FILE, 'r') as f:
        new_css = f.read()

    print(f"Loaded CSS file: {len(new_css)} characters, {len(new_css.splitlines())} lines")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        page.set_default_timeout(60000)

        print("=" * 60)
        print("APPLY COMPREHENSIVE CSS TO PUREBRAIN.AI")
        print("=" * 60)

        screenshots = []

        # Login to WordPress
        print("\n[1] Logging into WordPress...")
        await page.goto(WP_URL, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(2)
        screenshots.append(await save_screenshot(page, "01-login-page"))

        # Click "Log in with username and password" link if present
        print("\n[2] Checking for login link...")
        try:
            username_password_link = page.locator("text=Log in with username and password")
            if await username_password_link.is_visible(timeout=5000):
                await username_password_link.click()
                await asyncio.sleep(2)
                screenshots.append(await save_screenshot(page, "02-login-form"))
        except:
            print("  Direct login form displayed")

        # Now fill the login form
        print("\n[3] Filling login form...")
        await page.fill("#user_login", WP_USER)
        await page.fill("#user_pass", WP_PASS)
        screenshots.append(await save_screenshot(page, "03-form-filled"))

        await page.click("#wp-submit")
        await asyncio.sleep(3)
        screenshots.append(await save_screenshot(page, "04-after-login"))

        # Check if we're logged in
        print("\n[4] Checking login status...")
        dashboard = page.locator("#wpadminbar").first
        if await dashboard.is_visible(timeout=5000):
            print("  Successfully logged in!")
        else:
            print("  Login may have issues, checking page...")
            screenshots.append(await save_screenshot(page, "04b-login-check"))

        # Navigate directly to Additional CSS customizer
        print("\n[5] Navigating to Additional CSS...")
        await page.goto("https://purebrain.ai/wp-admin/customize.php?autofocus[section]=custom_css", wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(5)
        screenshots.append(await save_screenshot(page, "05-customizer"))

        # Wait for customizer to fully load
        await asyncio.sleep(3)

        # Check if CodeMirror editor is present
        print("\n[6] Looking for CSS editor...")
        cm_present = await page.locator(".CodeMirror").count()
        print(f"  CodeMirror found: {cm_present > 0}")

        # Get current CSS for reference
        current_css = ""
        try:
            if cm_present > 0:
                current_css = await page.evaluate("() => document.querySelector('.CodeMirror').CodeMirror.getValue()")
                print(f"  Current CSS length: {len(current_css)} chars")
            else:
                textarea = page.locator("#customize-control-custom_css textarea, textarea.wp-code-editor").first
                if await textarea.is_visible(timeout=3000):
                    current_css = await textarea.input_value()
                    print(f"  Current CSS length: {len(current_css)} chars")
        except Exception as e:
            print(f"  Error getting current CSS: {e}")

        print("\n  Current CSS preview (first 200 chars):")
        print(current_css[:200] if current_css else "  (empty or not accessible)")

        screenshots.append(await save_screenshot(page, "06-before-apply"))

        # Apply the new comprehensive CSS (REPLACE, not append)
        print("\n[7] Applying comprehensive CSS (REPLACING existing)...")
        try:
            if cm_present > 0:
                # Escape the CSS for JavaScript
                css_escaped = new_css.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')
                await page.evaluate(f'''
                    () => {{
                        const cm = document.querySelector('.CodeMirror').CodeMirror;
                        cm.setValue(`{css_escaped}`);
                    }}
                ''')
                print("  CSS applied via CodeMirror")
            else:
                textarea = page.locator("#customize-control-custom_css textarea, textarea.wp-code-editor").first
                await textarea.fill(new_css)
                print("  CSS applied via textarea")

            await asyncio.sleep(2)
            screenshots.append(await save_screenshot(page, "07-css-applied"))

        except Exception as e:
            print(f"  Error applying CSS: {e}")

        # Verify the CSS was applied
        print("\n[7b] Verifying CSS was applied...")
        try:
            if cm_present > 0:
                applied_css = await page.evaluate("() => document.querySelector('.CodeMirror').CodeMirror.getValue()")
                if "PUREBRAIN.AI - ALL UX RECOMMENDATIONS CSS" in applied_css:
                    print("  CSS content verified!")
                else:
                    print("  WARNING: CSS content may not have been applied correctly")
                    print(f"  Applied length: {len(applied_css)}")
        except Exception as e:
            print(f"  Verification error: {e}")

        # Click Publish button
        print("\n[8] Publishing changes...")
        try:
            # In customizer, the publish button has specific selectors
            publish_btn = page.locator("#save, .customize-save-button-wrapper input[type='submit'], button#save").first
            if await publish_btn.is_visible(timeout=5000):
                await publish_btn.click()
                await asyncio.sleep(3)
                screenshots.append(await save_screenshot(page, "08-after-publish"))
                print("  Published!")
            else:
                print("  Looking for customizer publish button...")
                # Try the customizer-specific publish
                publish_btn2 = page.locator("input[value='Publish'], #customize-save-button-wrapper input").first
                if await publish_btn2.is_visible(timeout=3000):
                    await publish_btn2.click()
                    await asyncio.sleep(3)
                    screenshots.append(await save_screenshot(page, "08-after-publish-alt"))
                    print("  Published via customizer!")
                else:
                    print("  WARNING: Could not find publish button")
                    screenshots.append(await save_screenshot(page, "08-no-publish-found"))

        except Exception as e:
            print(f"  Error publishing: {e}")
            screenshots.append(await save_screenshot(page, "08-publish-error"))

        # Verify by visiting the site
        print("\n[9] Verifying changes on live site...")
        await page.goto("https://purebrain.ai", wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(3)
        screenshots.append(await save_screenshot(page, "09-site-after-fix"))

        # Check page source for CSS
        print("\n[10] Checking if CSS is active on site...")
        page_source = await page.content()
        if "PUREBRAIN.AI - ALL UX RECOMMENDATIONS CSS" in page_source:
            print("  CSS header comment found in page source!")
        else:
            # Also check stylesheets
            css_links = await page.evaluate("() => Array.from(document.styleSheets).map(s => s.href).filter(h => h)")
            print(f"  Loaded stylesheets: {len(css_links)}")

        # Scroll to different areas to verify
        await page.evaluate("window.scrollTo(0, 1000)")
        await asyncio.sleep(2)
        screenshots.append(await save_screenshot(page, "10-mid-page"))

        await page.evaluate("window.scrollTo(0, 2500)")
        await asyncio.sleep(2)
        screenshots.append(await save_screenshot(page, "11-form-area"))

        print("\n" + "=" * 60)
        print("CSS APPLICATION COMPLETE")
        print("=" * 60)
        print(f"\nApplied CSS file: {CSS_FILE}")
        print(f"CSS length: {len(new_css)} characters")
        print(f"CSS lines: {len(new_css.splitlines())} lines")
        print("\nScreenshots saved:")
        for s in screenshots:
            print(f"  {s}")

        await browser.close()
        return screenshots

if __name__ == "__main__":
    asyncio.run(apply_comprehensive_css())
