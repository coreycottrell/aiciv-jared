"""
Deploy updated security plugin by uploading as ZIP and replacing existing plugin.
Uses the same method that successfully uploaded pb-video-modal.
Login uses PUREBRAIN_WP_USER + PUREBRAIN_WP_PASSWORD (not app password).
"""
import asyncio
import os
import time
import zipfile
import tempfile
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

WP_USER = os.getenv('PUREBRAIN_WP_USER')
WP_PASS = os.getenv('PUREBRAIN_WP_PASSWORD')
WP_BASE = 'https://purebrain.ai'
PLUGIN_PHP = '/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security/purebrain-security-plugin.php'

print(f"WP_USER: {WP_USER}, WP_PASS set: {bool(WP_PASS)}")


async def deploy():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # -----------------------------------------------
        # LOGIN - same as original working script
        # -----------------------------------------------
        print("[LOGIN] Navigating...")
        await page.goto(
            f'{WP_BASE}/wp-login.php?wpaas-standard-login=1',
            wait_until='domcontentloaded', timeout=60000
        )
        time.sleep(2)

        sso_toggle = page.locator('.wpaas-sso-login-toggle')
        if await sso_toggle.count() > 0:
            await sso_toggle.click()
            time.sleep(1)

        await page.fill('#user_login', WP_USER)
        await page.fill('#user_pass', WP_PASS)
        await page.click('#wp-submit')
        await page.wait_for_load_state('domcontentloaded', timeout=60000)
        time.sleep(3)

        print(f"[LOGIN] URL: {page.url}")
        if 'wp-admin' not in page.url:
            body = await page.inner_text('body')
            print(f"[LOGIN] FAILED: {body[:200]}")
            await browser.close()
            return 'LOGIN_FAILED'

        print("[LOGIN] SUCCESS")

        # -----------------------------------------------
        # CREATE ZIP
        # -----------------------------------------------
        print("[ZIP] Creating plugin zip...")
        zip_path = tempfile.mktemp(suffix='.zip')
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write(PLUGIN_PHP, 'purebrain-security/purebrain-security-plugin.php')
        print(f"[ZIP] Created: {zip_path}")

        # -----------------------------------------------
        # UPLOAD ZIP
        # -----------------------------------------------
        print("[UPLOAD] Navigating to plugin upload page...")
        await page.goto(
            f'{WP_BASE}/wp-admin/plugin-install.php?tab=upload',
            wait_until='domcontentloaded', timeout=60000
        )
        time.sleep(3)

        file_input = page.locator('input[type="file"]')
        if await file_input.count() == 0:
            print("[UPLOAD] No file input found")
            await browser.close()
            return 'NO_FILE_INPUT'

        print("[UPLOAD] Setting file input...")
        await file_input.set_input_files(zip_path)
        await page.click('#install-plugin-submit')
        await page.wait_for_load_state('domcontentloaded', timeout=120000)
        time.sleep(5)

        page_content = await page.content()
        page_text = await page.inner_text('body')
        print(f"[UPLOAD] Result URL: {page.url}")
        print(f"[UPLOAD] Result text (first 400): {page_text[:400]}")

        # Handle "already installed" - need to replace
        if 'already installed' in page_text.lower() or 'already installed' in page_content.lower():
            print("[UPLOAD] Plugin already installed - looking for Replace option...")
            replace_btn = page.locator('a:has-text("Replace current with uploaded")')
            if await replace_btn.count() > 0:
                print("[UPLOAD] Clicking 'Replace current with uploaded'...")
                await replace_btn.click()
                await page.wait_for_load_state('domcontentloaded', timeout=120000)
                time.sleep(5)
                page_text = await page.inner_text('body')
                print(f"[UPLOAD] Post-replace text (first 400): {page_text[:400]}")
            else:
                print("[UPLOAD] No 'Replace current' button found")
                # Check for any action buttons
                all_links = await page.locator('a').all()
                for link in all_links[:20]:
                    txt = await link.inner_text()
                    if txt.strip():
                        print(f"  Link: {txt.strip()}")

        # Check result
        if 'Plugin updated successfully' in page_text or 'installed successfully' in page_text.lower():
            print("[UPLOAD] SUCCESS: Plugin updated/installed successfully!")
            result = 'SUCCESS'
        elif 'activate plugin' in page_text.lower():
            print("[UPLOAD] Installed but needs activation - it was deactivated by upload")
            activate_link = page.locator('a:has-text("Activate Plugin")')
            if await activate_link.count() > 0:
                await activate_link.click()
                await page.wait_for_load_state('domcontentloaded', timeout=60000)
                time.sleep(3)
                print("[UPLOAD] Plugin activated")
                result = 'SUCCESS_ACTIVATED'
            else:
                result = 'UPLOADED_NEEDS_ACTIVATION'
        else:
            print("[UPLOAD] Uncertain result")
            result = 'UNCERTAIN'

        # -----------------------------------------------
        # VERIFY: Check plugin is active
        # -----------------------------------------------
        print("[VERIFY] Checking plugins page...")
        await page.goto(
            f'{WP_BASE}/wp-admin/plugins.php',
            wait_until='domcontentloaded', timeout=60000
        )
        time.sleep(3)
        plugins_html = await page.content()

        security_active = False
        # Look for the active class on the security plugin row
        import re
        # Check if purebrain-security is in an 'active' row
        security_section = re.search(
            r'purebrain-security[^"]*"[^>]*>(.*?)</tr',
            plugins_html, re.DOTALL
        )
        if security_section:
            security_active = 'active' in security_section.group(0).lower()

        # Simpler check: look for deactivate link (means it's active)
        security_has_deactivate = bool(re.search(
            r'purebrain-security.*?deactivate|deactivate.*?purebrain-security',
            plugins_html, re.DOTALL | re.IGNORECASE
        ))
        print(f"[VERIFY] Security plugin has deactivate link (= active): {security_has_deactivate}")

        os.unlink(zip_path)
        await browser.close()
        return result


if __name__ == '__main__':
    print("=" * 60)
    print("SECURITY PLUGIN UPDATE VIA ZIP UPLOAD")
    print("=" * 60)
    result = asyncio.run(deploy())
    print(f"\nFinal result: {result}")
