#!/usr/bin/env python3
"""
Deploy all remaining extraction plugins to purebrain.ai.

Uploads 9 standalone plugins via zip upload + activates them.
Then updates the security plugin via plugin editor.

Prerequisites:
- Working WP login (CAPTCHA must be cleared)
- .env with PUREBRAIN_WP_USER and PUREBRAIN_WP_PASSWORD

Usage: python3 deploy_all_extractions.py
"""

import asyncio
import os
import sys
import time
import zipfile
import tempfile
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

WP_USER = os.getenv('PUREBRAIN_WP_USER')
WP_PASS = os.getenv('PUREBRAIN_WP_PASSWORD')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PLUGINS_TO_DEPLOY = [
    'pb-cache-control',
    'pb-indexnow',
    'pb-page-metadata',
    'pb-lead-capture',
    'pb-social-sharing',
    'pb-footer-branding',
    'pb-content-gate',
    'pb-blog-faq',
    'pb-blog-styling',
]


async def login(page):
    """Login to WP admin. Returns True on success."""
    await page.goto(
        'https://purebrain.ai/wp-login.php?wpaas-standard-login=1',
        wait_until='domcontentloaded', timeout=60000
    )
    await asyncio.sleep(3)

    # Check for actual visible CAPTCHA widget (not just the word in GoDaddy JS)
    captcha_widget = page.locator('.g-recaptcha, .h-captcha, iframe[src*="captcha"]')
    if await captcha_widget.count() > 0:
        print("BLOCKED: Visual CAPTCHA widget present. Try again later.")
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
        err = page.locator('#login_error')
        if await err.count() > 0:
            print(f"Login failed: {await err.text_content()}")
        return False

    print("LOGIN SUCCESS!")
    return True


async def upload_plugin(page, plugin_name):
    """Upload and activate a single plugin via zip upload."""
    plugin_dir = os.path.join(BASE_DIR, plugin_name)
    plugin_file = os.path.join(plugin_dir, f'{plugin_name}.php')

    if not os.path.exists(plugin_file):
        print(f"  SKIP: {plugin_file} not found")
        return False

    # Create zip
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
            print(f"  No file input on upload page")
            return False

        await file_input.set_input_files(zip_path)
        await page.click('#install-plugin-submit')
        await page.wait_for_load_state('domcontentloaded', timeout=120000)
        await asyncio.sleep(3)

        content = await page.content()

        if 'already installed' in content.lower():
            print(f"  Already installed")
            return True
        elif 'installed successfully' in content.lower():
            activate = page.locator('a:has-text("Activate Plugin")')
            if await activate.count() > 0:
                await activate.click()
                await page.wait_for_load_state('domcontentloaded', timeout=60000)
                await asyncio.sleep(2)
                print(f"  Installed + Activated!")
                return True
            else:
                print(f"  Installed (activate manually)")
                return True
        else:
            body = await page.locator('.wrap').text_content() if await page.locator('.wrap').count() > 0 else ''
            print(f"  Unclear result: {body[:200]}")
            return False
    finally:
        os.unlink(zip_path)


async def update_security_plugin(page):
    """Update the security plugin via plugin editor."""
    security_file = os.path.join(BASE_DIR, 'purebrain-security', 'purebrain-security-plugin.php')

    await page.goto(
        'https://purebrain.ai/wp-admin/plugin-editor.php?'
        'file=purebrain-security-plugin%2Fpurebrain-security-plugin.php&'
        'plugin=purebrain-security-plugin%2Fpurebrain-security-plugin.php',
        wait_until='domcontentloaded', timeout=60000
    )
    await asyncio.sleep(5)

    cm = await page.evaluate('() => !!document.querySelector(".CodeMirror")')
    if not cm:
        print("Plugin editor not available (DISALLOW_FILE_EDIT may be set)")
        return False

    with open(security_file, 'r') as f:
        code = f.read()

    print(f"Setting {len(code)} chars ({code.count(chr(10))} lines)...")
    await page.evaluate(
        '(c) => document.querySelector(".CodeMirror").CodeMirror.setValue(c)', code
    )
    await asyncio.sleep(2)
    await page.click('#submit')
    await page.wait_for_load_state('domcontentloaded', timeout=60000)
    await asyncio.sleep(3)

    body = await page.content()
    if 'File edited successfully' in body:
        print("SECURITY PLUGIN UPDATED!")
        return True
    else:
        print("Update result unclear")
        return False


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                       'AppleWebKit/537.36 Chrome/128.0.0.0 Safari/537.36'
        )
        page = await context.new_page()

        # Step 1: Login
        if not await login(page):
            await browser.close()
            sys.exit(1)

        # Step 2: Upload and activate standalone plugins
        results = {}
        for plugin_name in PLUGINS_TO_DEPLOY:
            print(f"\n--- {plugin_name} ---")
            results[plugin_name] = await upload_plugin(page, plugin_name)

        # Step 3: Update security plugin
        print("\n--- Security Plugin Update ---")
        results['security-plugin'] = await update_security_plugin(page)

        # Step 4: Clear Elementor cache
        print("\n--- Clearing Elementor Cache ---")
        await page.goto(
            'https://purebrain.ai/wp-admin/admin-ajax.php?action=elementor_clear_cache',
            wait_until='domcontentloaded', timeout=30000
        )
        await asyncio.sleep(2)
        print("Cache cleared")

        await browser.close()

        # Summary
        print("\n" + "=" * 50)
        print("DEPLOYMENT SUMMARY")
        print("=" * 50)
        for name, ok in results.items():
            print(f"  {'PASS' if ok else 'FAIL'}: {name}")

        failures = [k for k, v in results.items() if not v]
        if failures:
            print(f"\n{len(failures)} FAILED: {', '.join(failures)}")
            sys.exit(1)
        else:
            print(f"\nAll {len(results)} deployments successful!")


if __name__ == '__main__':
    asyncio.run(main())
