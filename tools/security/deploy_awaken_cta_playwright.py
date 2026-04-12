#!/usr/bin/env python3
"""Deploy pb-awaken-cta plugin via Playwright zip upload (same method as deploy_all_extractions.py)."""

import asyncio
import os
import sys
import zipfile
import tempfile
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

WP_USER = os.getenv('PUREBRAIN_WP_USER')
WP_PASS = os.getenv('PUREBRAIN_WP_PASSWORD')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


async def login(page):
    await page.goto(
        'https://purebrain.ai/wp-login.php?wpaas-standard-login=1',
        wait_until='domcontentloaded', timeout=60000
    )
    await asyncio.sleep(3)

    captcha_widget = page.locator('.g-recaptcha, .h-captcha, iframe[src*="captcha"]')
    if await captcha_widget.count() > 0:
        print("BLOCKED: Visual CAPTCHA widget present.")
        return False

    sso = page.locator('.wpaas-sso-login-toggle')
    if await sso.count() > 0 and await sso.is_visible():
        await sso.click()
        await asyncio.sleep(2)

    if not await page.locator('#user_login').is_visible():
        print("Login form not visible")
        return False

    await page.fill('#user_login', WP_USER)
    await page.fill('#user_pass', WP_PASS)
    await page.click('#wp-submit')
    await page.wait_for_load_state('domcontentloaded', timeout=60000)
    await asyncio.sleep(3)

    if 'wp-login' in page.url:
        return False

    print("LOGIN SUCCESS")
    return True


async def upload_plugin(page, plugin_name):
    plugin_file = os.path.join(BASE_DIR, plugin_name, f'{plugin_name}.php')
    if not os.path.exists(plugin_file):
        print(f"SKIP: {plugin_file} not found")
        return False

    zip_path = tempfile.mktemp(suffix='.zip')
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(plugin_file, f'{plugin_name}/{plugin_name}.php')

    try:
        await page.goto(
            'https://purebrain.ai/wp-admin/plugin-install.php?tab=upload',
            wait_until='domcontentloaded', timeout=60000
        )
        await asyncio.sleep(3)

        file_input = page.locator('input[type="file"]')
        if await file_input.count() == 0:
            print("No file input on upload page")
            return False

        await file_input.set_input_files(zip_path)
        await page.click('#install-plugin-submit')
        await page.wait_for_load_state('domcontentloaded', timeout=120000)
        await asyncio.sleep(3)

        content = await page.content()

        if 'already installed' in content.lower():
            print("Already installed — activating...")
            # Go to plugins page and activate
            await page.goto(
                'https://purebrain.ai/wp-admin/plugins.php',
                wait_until='domcontentloaded', timeout=60000
            )
            await asyncio.sleep(3)
            activate = page.locator(f'tr[data-slug="{plugin_name}"] .activate a')
            if await activate.count() > 0:
                await activate.click()
                await asyncio.sleep(3)
                print("Activated!")
            else:
                print("Already active or can't find activate link")
            return True
        elif 'installed successfully' in content.lower():
            activate = page.locator('a:has-text("Activate Plugin")')
            if await activate.count() > 0:
                await activate.click()
                await page.wait_for_load_state('domcontentloaded', timeout=60000)
                await asyncio.sleep(2)
                print("Installed + Activated!")
                return True
            else:
                print("Installed (activate manually)")
                return True
        else:
            body = await page.locator('.wrap').text_content() if await page.locator('.wrap').count() > 0 else ''
            print(f"Result: {body[:300]}")
            return False
    finally:
        os.unlink(zip_path)


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                       'AppleWebKit/537.36 Chrome/128.0.0.0 Safari/537.36'
        )
        page = await context.new_page()

        if not await login(page):
            await browser.close()
            sys.exit(1)

        print("\n--- pb-awaken-cta ---")
        ok = await upload_plugin(page, 'pb-awaken-cta')
        await browser.close()

        if ok:
            print("\nSUCCESS: pb-awaken-cta deployed!")
        else:
            print("\nFAILED: pb-awaken-cta deployment failed")
            sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
