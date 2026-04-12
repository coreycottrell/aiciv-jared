#!/usr/bin/env python3
"""Deactivate pb-video-handler plugin via WP Admin Playwright."""
import asyncio
from playwright.async_api import async_playwright

WP_USER = "purebrain@puremarketing.ai"
WP_PASS = "ij34utJdGCOst1*RcSvubXjb"
WP_ADMIN = "https://purebrain.ai/wp-admin"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Login
        print("[1] Logging in...")
        await page.goto(f"{WP_ADMIN}/plugins.php?wpaas-standard-login=1", wait_until="networkidle", timeout=30000)

        # Fill login form — wait for it to be visible (GoDaddy SSO overlay may delay)
        try:
            await page.wait_for_selector('#user_login', state='visible', timeout=15000)
        except:
            # Maybe GoDaddy SSO page, try clicking through
            await page.screenshot(path="/tmp/wp-login-debug.png")
            print("[1b] Login form not visible, checking for SSO...")
            # Try waiting longer or navigating directly
            await page.goto(f"https://purebrain.ai/wp-login.php?wpaas-standard-login=1", wait_until="networkidle", timeout=30000)
            await page.wait_for_selector('#user_login', state='visible', timeout=15000)

        await page.fill('#user_login', WP_USER)
        await page.fill('#user_pass', WP_PASS)
        await page.click('#wp-submit')
        await page.wait_for_load_state('networkidle', timeout=30000)
        print("[2] Logged in")

        # Navigate to plugins page
        await page.goto(f"{WP_ADMIN}/plugins.php", wait_until="networkidle", timeout=30000)
        print("[3] On plugins page")

        # Find pb-video-handler and deactivate it
        # Look for the deactivate link for this plugin
        deactivate_link = page.locator('tr[data-plugin*="pb-video-handler"] .deactivate a, tr[data-slug="pb-video-handler"] .deactivate a')
        count = await deactivate_link.count()

        if count > 0:
            print("[4] Found deactivate link, clicking...")
            await deactivate_link.first.click()
            await page.wait_for_load_state('networkidle', timeout=30000)
            print("[5] Plugin deactivated!")
        else:
            # Try finding by text content
            print("[4] Looking for plugin by text...")
            rows = page.locator('tr.active')
            row_count = await rows.count()
            for i in range(row_count):
                row = rows.nth(i)
                text = await row.text_content()
                if 'video-handler' in text.lower() or 'pb-video' in text.lower():
                    deact = row.locator('.deactivate a')
                    if await deact.count() > 0:
                        print(f"[4b] Found plugin row, deactivating...")
                        await deact.first.click()
                        await page.wait_for_load_state('networkidle', timeout=30000)
                        print("[5] Plugin deactivated!")
                        break
            else:
                print("[4c] Plugin not found or already inactive")
                # Take screenshot for debug
                await page.screenshot(path="/tmp/wp-plugins-page.png")

        await browser.close()

asyncio.run(main())
