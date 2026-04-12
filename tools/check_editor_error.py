"""Check what the WordPress error page says when navigating to plugin editor."""
import asyncio
import os
import time
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

WP_USER = os.getenv('PUREBRAIN_WP_USER')
WP_PASS = os.getenv('PUREBRAIN_WP_PASSWORD')
WP_BASE = 'https://purebrain.ai'


async def check():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto(
            f'{WP_BASE}/wp-login.php?wpaas-standard-login=1',
            wait_until='domcontentloaded', timeout=60000
        )
        time.sleep(2)

        await page.wait_for_selector('#user_login', timeout=10000)
        await page.fill('#user_login', WP_USER)
        await page.fill('#user_pass', WP_PASS)
        await page.click('#wp-submit')
        await page.wait_for_load_state('domcontentloaded', timeout=60000)
        time.sleep(2)

        print(f"[LOGIN] URL: {page.url}")

        # Try to access the plugin editor
        await page.goto(
            f'{WP_BASE}/wp-admin/plugin-editor.php',
            wait_until='domcontentloaded', timeout=60000
        )
        time.sleep(3)

        title = await page.title()
        body = await page.inner_text('body')
        html = await page.content()

        print(f"[EDITOR] Title: {title}")
        print(f"[EDITOR] Body: {body[:600]}")
        print(f"[EDITOR] Has DISALLOW_FILE_EDIT: {'DISALLOW_FILE_EDIT' in html}")
        print(f"[EDITOR] Has 'not allowed': {'not allowed' in body.lower()}")
        print(f"[EDITOR] Has 'disabled': {'disabled' in body.lower()}")
        print(f"[EDITOR] Has 'file editing': {'file editing' in body.lower()}")

        await browser.close()


asyncio.run(check())
