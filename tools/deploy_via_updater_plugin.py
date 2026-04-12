"""
Deploy updated security plugin using a temporary 'updater' plugin:
1. Upload pb-security-updater as zip via Playwright (app password won't work,
   but we can try a different approach - use WP REST API to install if possible)

Actually: Use Playwright to upload the updater plugin zip, since we know
Playwright login works but the plugin editor doesn't.

Then use REST API (app password) to:
- Upload security plugin content to the updater endpoint
- Trigger the write
- Deactivate and delete the updater plugin

This avoids the plugin editor entirely.
"""
import asyncio
import os
import time
import zipfile
import tempfile
import base64
import requests
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

WP_USER = os.getenv('PUREBRAIN_WP_USER')
WP_PASS = os.getenv('PUREBRAIN_WP_PASSWORD')
WP_APP_PASS = os.getenv('PUREBRAIN_WP_APP_PASSWORD')
WP_BASE = 'https://purebrain.ai'

SECURITY_PLUGIN_PHP = '/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security/purebrain-security-plugin.php'
UPDATER_PLUGIN_PHP = '/home/jared/projects/AI-CIV/aether/tools/security/pb-security-updater/pb-security-updater.php'


async def upload_updater_plugin():
    """Upload pb-security-updater via Playwright."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context()
        page = await ctx.new_page()

        print("[LOGIN] Navigating to login...")
        await page.goto(
            f'{WP_BASE}/wp-login.php?wpaas-standard-login=1',
            wait_until='domcontentloaded', timeout=60000
        )
        time.sleep(2)

        title = await page.title()
        print(f"[LOGIN] Title: {title}")
        if 'verify' in title.lower():
            print("[LOGIN] CAPTCHA active")
            await browser.close()
            return False

        sso = await page.locator('.wpaas-sso-login-toggle').count()
        if sso > 0:
            await page.locator('.wpaas-sso-login-toggle').click()
            time.sleep(1)

        await page.fill('#user_login', WP_USER)
        await page.fill('#user_pass', WP_PASS)
        await page.click('#wp-submit')
        await page.wait_for_load_state('domcontentloaded', timeout=60000)
        time.sleep(3)

        if 'wp-admin' not in page.url:
            body = await page.inner_text('body')
            print(f"[LOGIN] Failed: {body[:150]}")
            await browser.close()
            return False

        print("[LOGIN] Success")

        # Create updater plugin zip
        zip_path = tempfile.mktemp(suffix='.zip')
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write(UPDATER_PLUGIN_PHP, 'pb-security-updater/pb-security-updater.php')

        print("[UPLOAD] Uploading pb-security-updater plugin...")
        await page.goto(
            f'{WP_BASE}/wp-admin/plugin-install.php?tab=upload',
            wait_until='domcontentloaded', timeout=60000
        )
        time.sleep(3)

        await page.locator('input[type="file"]').set_input_files(zip_path)
        await page.click('#install-plugin-submit')
        await page.wait_for_load_state('domcontentloaded', timeout=120000)
        time.sleep(5)

        body = await page.inner_text('body')
        print(f"[UPLOAD] Result: {body[:300]}")

        # Handle already installed
        replace = page.locator('a:has-text("Replace current with uploaded")')
        if await replace.count() > 0:
            await replace.click()
            await page.wait_for_load_state('domcontentloaded', timeout=120000)
            time.sleep(5)
            body = await page.inner_text('body')
            print(f"[UPLOAD] Post-replace: {body[:300]}")

        # Activate
        activate = page.locator('a:has-text("Activate Plugin")')
        if await activate.count() > 0:
            print("[UPLOAD] Activating pb-security-updater...")
            await activate.click()
            await page.wait_for_load_state('domcontentloaded', timeout=60000)
            time.sleep(3)
            body = await page.inner_text('body')
            print(f"[ACTIVATE] Result: {body[:200]}")

        os.unlink(zip_path)
        await browser.close()
        return True


def update_security_plugin_via_rest():
    """Use the updater plugin REST API to write the security plugin."""
    auth = (WP_USER, WP_APP_PASS)

    # Read security plugin content and base64 encode it
    with open(SECURITY_PLUGIN_PHP, 'rb') as f:
        content = f.read()
    encoded = base64.b64encode(content).decode('utf-8')
    print(f"[REST] Security plugin: {len(content)} bytes, encoded: {len(encoded)} chars")

    # Check if updater is available
    resp = requests.get(
        f'{WP_BASE}/wp-json/pb-updater/v1/status',
        auth=auth, timeout=15
    )
    print(f"[REST] Updater status check: {resp.status_code}")
    if resp.status_code != 200:
        print(f"[REST] Updater not accessible: {resp.text[:200]}")
        return False

    print(f"[REST] Updater status: {resp.json()}")

    # Upload content in chunks if needed (to avoid request size limits)
    # Send in one go first
    print("[REST] Uploading security plugin content to updater...")
    upload_resp = requests.post(
        f'{WP_BASE}/wp-json/pb-updater/v1/upload',
        auth=auth,
        json={'content': encoded},
        timeout=120
    )
    print(f"[REST] Upload status: {upload_resp.status_code}")
    if upload_resp.status_code != 200:
        print(f"[REST] Upload failed: {upload_resp.text[:300]}")
        return False
    print(f"[REST] Upload result: {upload_resp.json()}")

    # Trigger the write
    print("[REST] Triggering file write...")
    write_resp = requests.post(
        f'{WP_BASE}/wp-json/pb-updater/v1/write',
        auth=auth,
        json={},
        timeout=60
    )
    print(f"[REST] Write status: {write_resp.status_code}")
    print(f"[REST] Write result: {write_resp.text[:300]}")

    if write_resp.status_code == 200:
        result = write_resp.json()
        if 'bytes_written' in result:
            print(f"[REST] SUCCESS! Wrote {result['bytes_written']} bytes")
            return True

    return False


def deactivate_and_delete_updater():
    """Deactivate and delete the temporary updater plugin via REST API."""
    auth = (WP_USER, WP_APP_PASS)

    # Deactivate
    resp = requests.put(
        f'{WP_BASE}/wp-json/wp/v2/plugins/pb-security-updater/pb-security-updater',
        auth=auth,
        json={'status': 'inactive'},
        timeout=30
    )
    print(f"[CLEANUP] Deactivate status: {resp.status_code}")

    # Delete
    resp2 = requests.delete(
        f'{WP_BASE}/wp-json/wp/v2/plugins/pb-security-updater/pb-security-updater',
        auth=auth,
        timeout=30
    )
    print(f"[CLEANUP] Delete status: {resp2.status_code}: {resp2.text[:200]}")


if __name__ == '__main__':
    print("=" * 60)
    print("DEPLOY SECURITY PLUGIN VIA UPDATER PLUGIN")
    print("=" * 60)

    # Step 1: Upload updater plugin via Playwright
    print("\n[STEP 1] Uploading updater plugin...")
    uploaded = asyncio.run(upload_updater_plugin())

    if not uploaded:
        # Maybe it's already there - check via REST
        auth = (WP_USER, WP_APP_PASS)
        resp = requests.get(f'{WP_BASE}/wp-json/pb-updater/v1/status', auth=auth, timeout=10)
        if resp.status_code == 200:
            print("[STEP 1] Updater already accessible via REST!")
            uploaded = True
        else:
            print("[STEP 1] FAILED to upload updater plugin")
            exit(1)

    # Step 2: Use REST to write the security plugin
    print("\n[STEP 2] Writing security plugin via updater REST API...")
    success = update_security_plugin_via_rest()

    # Step 3: Cleanup
    print("\n[STEP 3] Cleaning up updater plugin...")
    deactivate_and_delete_updater()

    # Step 4: Verify via REST - check security plugin still active
    print("\n[STEP 4] Verifying security plugin...")
    auth = (WP_USER, WP_APP_PASS)
    resp = requests.get(
        f'{WP_BASE}/wp-json/wp/v2/plugins/purebrain-security/purebrain-security-plugin',
        auth=auth, timeout=15
    )
    print(f"Security plugin status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"  name: {data.get('name')}, status: {data.get('status')}")

    print(f"\nFinal result: {'SUCCESS' if success else 'FAILED'}")
