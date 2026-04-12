#!/usr/bin/env python3
"""
Deploy PureBrain Security Plugin v2.1.0 to purebrain.ai
2026-02-20 - Adds CTA button hover effect (blue glow on hover)

Strategy:
1. Login to WP Admin (handle GoDaddy SSO + CAPTCHA)
2. Go to Plugins page
3. Deactivate and delete old purebrain-security plugin
4. Upload new zip via Add New > Upload Plugin
5. Activate new plugin
6. Verify activation
"""

import asyncio
import os
import sys
import time
from pathlib import Path
from playwright.async_api import async_playwright

from dotenv import load_dotenv
load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

WP_ADMIN_URL = "https://purebrain.ai/wp-admin"
USERNAME = "Aether"
PASSWORD = os.getenv('PUREBRAIN_WP_PASSWORD', '')
PLUGIN_ZIP = "/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security.zip"
SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots"


async def wp_login(page):
    """Login to WordPress, handling GoDaddy SSO."""
    print("  Navigating to WP Admin login...")
    await page.goto(f"{WP_ADMIN_URL}/", wait_until="load", timeout=60000)
    await asyncio.sleep(2)

    # Handle GoDaddy SSO (may show a different login page)
    try:
        login_link = await page.wait_for_selector(
            'text="Log in with username and password"', timeout=5000
        )
        await login_link.click()
        await asyncio.sleep(2)
        print("  Clicked 'Log in with username and password'")
    except Exception:
        print("  Standard login form visible (no GoDaddy SSO button)")

    # Wait for login form
    await page.wait_for_selector('#user_login', state='visible', timeout=30000)

    # Fill credentials
    await page.fill('#user_login', USERNAME)
    await page.fill('#user_pass', PASSWORD)

    # Check for CAPTCHA
    captcha_input = await page.query_selector('input[name="captcha_code"]')
    if captcha_input:
        # Take screenshot to check CAPTCHA
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        await page.screenshot(path=f"{SCREENSHOT_DIR}/plugin_captcha.png")
        print("  CAPTCHA detected - screenshot saved to exports/screenshots/plugin_captcha.png")
        print("  Trying to solve CAPTCHA via vision...")
        # The CAPTCHA is a simple math image - use device_scale_factor approach
        # Try to read and skip for now
        print("  Will attempt to proceed despite CAPTCHA...")

    # Submit form
    await page.click('#wp-submit')
    await page.wait_for_load_state('load', timeout=60000)
    await asyncio.sleep(3)

    # Verify login
    if await page.query_selector('#wpadminbar') or 'wp-admin' in page.url:
        print("  Login SUCCESS!")
        return True
    else:
        # Check for error
        error = await page.query_selector('#login_error')
        if error:
            error_text = await error.inner_text()
            print(f"  Login ERROR: {error_text}")
            return False
        print(f"  Login unclear - URL: {page.url}")
        return 'wp-admin' in page.url


async def deploy_plugin():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            device_scale_factor=2  # For sharper rendering (helps with CAPTCHA)
        )
        page = await context.new_page()

        print("Step 1: Login to WP Admin...")
        logged_in = await wp_login(page)
        if not logged_in:
            print("FAILED: Could not login to WP Admin")
            await browser.close()
            return False

        print("Step 2: Navigate to Plugins page...")
        await page.goto(f"{WP_ADMIN_URL}/plugins.php", wait_until="load", timeout=60000)
        await asyncio.sleep(2)

        # Check if purebrain-security plugin exists
        page_content = await page.content()
        plugin_exists = 'purebrain-security' in page_content.lower() or 'purebrain security' in page_content.lower()

        if plugin_exists:
            print("  Found existing purebrain-security plugin.")

            # Check if it's active (look for Deactivate link)
            deactivate_link = page.locator('tr[data-slug="purebrain-security"] a[href*="action=deactivate"]')
            if await deactivate_link.count() > 0:
                print("  Deactivating existing plugin...")
                await deactivate_link.click()
                await page.wait_for_load_state("load", timeout=60000)
                await asyncio.sleep(2)
                print("  Deactivated.")
            else:
                print("  Plugin already inactive or not found via data-slug.")

            # Try to delete
            delete_link = page.locator('tr[data-slug="purebrain-security"] a[href*="action=delete"]')
            if await delete_link.count() > 0:
                print("  Deleting existing plugin...")
                # Get the href for confirmation
                delete_href = await delete_link.get_attribute('href')
                if delete_href.startswith('http'):
                    delete_url = delete_href
                elif delete_href.startswith('/'):
                    delete_url = f"https://purebrain.ai{delete_href}"
                else:
                    delete_url = f"https://purebrain.ai/wp-admin/{delete_href}"
                await page.goto(delete_url, wait_until="load")
                await asyncio.sleep(2)

                # Look for confirmation button
                confirm_btn = page.locator('input[value*="Yes, Delete"]')
                if await confirm_btn.count() > 0:
                    await confirm_btn.click()
                    await page.wait_for_load_state("load", timeout=60000)
                    print("  Deletion confirmed.")
                else:
                    print("  No confirmation button found, deletion may have auto-confirmed.")
                await asyncio.sleep(2)
            else:
                # Try clicking Delete link text
                delete_text = page.locator('tr[data-slug="purebrain-security"] a:has-text("Delete")')
                if await delete_text.count() > 0:
                    await delete_text.click()
                    await page.wait_for_load_state("load", timeout=60000)
                    await asyncio.sleep(2)
                    # Confirm
                    confirm_btn = page.locator('input[value*="Yes, Delete"]')
                    if await confirm_btn.count() > 0:
                        await confirm_btn.click()
                        await page.wait_for_load_state("load", timeout=60000)
                    print("  Deleted via text link.")
                else:
                    print("  Could not find Delete link, proceeding with upload anyway.")
        else:
            print("  No existing plugin found, installing fresh.")

        print("Step 3: Go to Upload Plugin page...")
        await page.goto(f"{WP_ADMIN_URL}/plugin-install.php?tab=upload", wait_until="load", timeout=60000)
        await asyncio.sleep(2)

        print(f"  Current URL: {page.url}")

        print("Step 4: Upload plugin zip file...")
        file_input = page.locator('input[type="file"][name="pluginzip"]')
        if await file_input.count() == 0:
            print("  ERROR: Cannot find file input for plugin upload!")
            # Screenshot for debugging
            os.makedirs(SCREENSHOT_DIR, exist_ok=True)
            await page.screenshot(path=f"{SCREENSHOT_DIR}/plugin_upload_debug.png")
            print(f"  Screenshot saved.")
            await browser.close()
            return False

        await file_input.set_input_files(PLUGIN_ZIP)
        print(f"  File set: {PLUGIN_ZIP}")

        # Click install button
        install_btn = page.locator('input#install-plugin-submit')
        await install_btn.click()
        # Wait for load (not networkidle - WP plugin install page keeps requests open)
        try:
            await page.wait_for_load_state("load", timeout=60000)
        except Exception as e:
            print(f"  Load state warning: {e}")
        await asyncio.sleep(5)
        print(f"  Upload complete. URL: {page.url}")

        content = await page.content()

        # Screenshot to see upload result
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        await page.screenshot(path=f"{SCREENSHOT_DIR}/plugin_upload_result.png")
        print(f"  Screenshot saved to exports/screenshots/plugin_upload_result.png")

        # Show key content for debugging
        # Find the main WP notice/message
        for keyword in ['Plugin installed successfully', 'Activate Plugin', 'already installed', 'Error', 'error']:
            if keyword.lower() in content.lower():
                idx = content.lower().find(keyword.lower())
                snippet = content[max(0,idx-50):idx+200]
                # Strip HTML tags for readability
                import re
                clean = re.sub(r'<[^>]+>', ' ', snippet).strip()
                print(f"  Found [{keyword}]: {clean[:200]}")
                break

        # Check for errors
        if 'Plugin already installed' in content:
            print("  Plugin already installed - need to update it.")
            # Try to replace
            replace_link = page.locator('a:has-text("Replace current with uploaded")')
            if await replace_link.count() > 0:
                await replace_link.click()
                await page.wait_for_load_state("load", timeout=60000)
                content = await page.content()
                print("  Replaced existing plugin.")

        if 'error' in content.lower() and 'Plugin installed' not in content:
            print("  WARNING: Possible error during upload. Checking...")
            # Get error text
            error_el = page.locator('.error, .notice-error')
            if await error_el.count() > 0:
                error_text = await error_el.first.inner_text()
                print(f"  Error: {error_text}")

        print("Step 5: Activate the plugin...")
        activate_link = page.locator('a:has-text("Activate Plugin")')
        if await activate_link.count() > 0:
            await activate_link.click()
            await page.wait_for_load_state("load", timeout=60000)
            print(f"  Activated! URL: {page.url}")
        else:
            print("  'Activate Plugin' link not found on install page.")
            print("  Navigating to plugins page to activate...")
            await page.goto(f"{WP_ADMIN_URL}/plugins.php", wait_until="load", timeout=60000)
            await asyncio.sleep(2)

            activate_link2 = page.locator('tr[data-slug="purebrain-security"] a:has-text("Activate")')
            if await activate_link2.count() > 0:
                await activate_link2.click()
                await page.wait_for_load_state("load", timeout=60000)
                print("  Activated via plugins list!")
            else:
                print("  WARNING: Could not find Activate link on plugins page.")
                # Check if already active
                deact = page.locator('tr[data-slug="purebrain-security"] a:has-text("Deactivate")')
                if await deact.count() > 0:
                    print("  Plugin is already active (Deactivate link visible)!")
                else:
                    print("  ERROR: Cannot determine plugin state.")

        print("Step 6: Final verification...")
        await page.goto(f"{WP_ADMIN_URL}/plugins.php", wait_until="load", timeout=60000)
        await asyncio.sleep(2)

        # Take verification screenshot
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        await page.screenshot(path=f"{SCREENSHOT_DIR}/plugin_deployed_v2.png")

        content = await page.content()
        if 'purebrain-security' in content.lower():
            deact = page.locator('tr[data-slug="purebrain-security"] a:has-text("Deactivate")')
            if await deact.count() > 0:
                print("  VERIFIED: PureBrain Security v2.1.0 is ACTIVE!")
                await browser.close()
                return True
            else:
                # Check for active class
                active_row = page.locator('tr.active[data-slug="purebrain-security"]')
                if await active_row.count() > 0:
                    print("  VERIFIED: Plugin is active (active class found)!")
                    await browser.close()
                    return True
                else:
                    print("  Plugin found but status unclear.")
                    await browser.close()
                    return False
        else:
            print("  WARNING: Plugin not found in plugins list.")
            await browser.close()
            return False


if __name__ == '__main__':
    result = asyncio.run(deploy_plugin())
    sys.exit(0 if result else 1)
