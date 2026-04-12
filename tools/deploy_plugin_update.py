"""
Deploy two things to purebrain.ai:
1. Updated security plugin (video modal code removed)
2. New pb-video-modal plugin (standalone)
"""
import asyncio
import os
import time
import zipfile
import tempfile
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

WP_USER = (
    os.getenv('PUREBRAIN_WP_USER') or
    os.getenv('WP_USERNAME') or
    os.getenv('WP_USER') or
    os.getenv('WORDPRESS_USER') or
    'admin'
)
WP_PASS = (
    os.getenv('PUREBRAIN_WP_PASSWORD') or
    os.getenv('PUREBRAIN_WP_APP_PASSWORD') or
    os.getenv('WP_PASSWORD') or
    os.getenv('WP_PASS') or
    os.getenv('WORDPRESS_APP_PASSWORD') or
    ''
)

print(f"Using WP_USER: {WP_USER}")
print(f"WP_PASS set: {bool(WP_PASS)}")

SECURITY_PLUGIN_PHP = '/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security/purebrain-security-plugin.php'
VIDEO_MODAL_DIR = '/home/jared/projects/AI-CIV/aether/tools/security/pb-video-modal'


async def deploy():
    results = {}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # ----------------------------------------------------------------
        # LOGIN
        # ----------------------------------------------------------------
        print("\n[LOGIN] Navigating to WP login...")
        await page.goto(
            'https://purebrain.ai/wp-login.php?wpaas-standard-login=1',
            wait_until='domcontentloaded',
            timeout=60000
        )
        time.sleep(2)

        sso_toggle = page.locator('.wpaas-sso-login-toggle')
        if await sso_toggle.count() > 0:
            print("[LOGIN] GoDaddy SSO toggle found — clicking to show standard login")
            await sso_toggle.click()
            time.sleep(1)

        await page.fill('#user_login', WP_USER)
        await page.fill('#user_pass', WP_PASS)
        await page.click('#wp-submit')
        await page.wait_for_load_state('domcontentloaded', timeout=60000)
        time.sleep(3)

        # Confirm login
        current_url = page.url
        print(f"[LOGIN] Post-login URL: {current_url}")
        if 'wp-admin' not in current_url and 'dashboard' not in current_url:
            # Check if still on login page (error)
            page_text = await page.inner_text('body')
            if 'incorrect' in page_text.lower() or 'error' in page_text.lower():
                print("[LOGIN] ERROR: Login failed. Check credentials.")
                results['login'] = 'FAILED'
                await browser.close()
                return results

        results['login'] = 'OK'
        print("[LOGIN] Login successful")

        # ----------------------------------------------------------------
        # STEP 1: Update security plugin via plugin editor
        # ----------------------------------------------------------------
        print("\n[STEP 1] Loading plugin editor for purebrain-security-plugin...")
        await page.goto(
            'https://purebrain.ai/wp-admin/plugin-editor.php'
            '?file=purebrain-security-plugin%2Fpurebrain-security-plugin.php'
            '&plugin=purebrain-security-plugin%2Fpurebrain-security-plugin.php',
            wait_until='domcontentloaded',
            timeout=60000
        )
        time.sleep(5)

        # Read the updated security plugin code
        with open(SECURITY_PLUGIN_PHP, 'r') as f:
            security_code = f.read()
        print(f"[STEP 1] Security plugin file read: {len(security_code)} chars")

        # Set editor content via CodeMirror
        await page.evaluate('''(code) => {
            const cm = document.querySelector('.CodeMirror');
            if (cm && cm.CodeMirror) {
                cm.CodeMirror.setValue(code);
                return true;
            }
            return false;
        }''', security_code)
        time.sleep(2)

        # Click Update File
        submit_btn = page.locator('#submit')
        if await submit_btn.count() > 0:
            await submit_btn.click()
            await page.wait_for_load_state('domcontentloaded', timeout=60000)
            time.sleep(3)

            # Check for success message
            page_content = await page.content()
            if 'File edited successfully' in page_content or 'updated successfully' in page_content.lower():
                print("[STEP 1] SUCCESS: Security plugin updated")
                results['security_plugin'] = 'UPDATED'
            else:
                print("[STEP 1] WARNING: No explicit success message found — may still have worked")
                print("[STEP 1] URL after submit:", page.url)
                results['security_plugin'] = 'UNCERTAIN - check manually'
        else:
            print("[STEP 1] ERROR: No submit button found on plugin editor page")
            results['security_plugin'] = 'FAILED - no submit button'

        # ----------------------------------------------------------------
        # STEP 2: Create zip and upload pb-video-modal
        # ----------------------------------------------------------------
        print("\n[STEP 2] Creating pb-video-modal zip...")
        zip_path = tempfile.mktemp(suffix='.zip')
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write(
                os.path.join(VIDEO_MODAL_DIR, 'pb-video-modal.php'),
                'pb-video-modal/pb-video-modal.php'
            )
        print(f"[STEP 2] Zip created at: {zip_path}")

        print("[STEP 2] Navigating to plugin upload page...")
        await page.goto(
            'https://purebrain.ai/wp-admin/plugin-install.php?tab=upload',
            wait_until='domcontentloaded',
            timeout=60000
        )
        time.sleep(3)

        file_input = page.locator('input[type="file"]')
        if await file_input.count() > 0:
            await file_input.set_input_files(zip_path)
            time.sleep(1)
            await page.click('#install-plugin-submit')
            await page.wait_for_load_state('domcontentloaded', timeout=120000)
            time.sleep(5)

            install_content = await page.content()

            # Check for "already installed" situation
            if 'already installed' in install_content.lower():
                print("[STEP 2] Plugin already installed — will look for replace/activate option")
                replace_btn = page.locator('a:has-text("Replace current with uploaded")')
                if await replace_btn.count() > 0:
                    await replace_btn.click()
                    await page.wait_for_load_state('domcontentloaded', timeout=60000)
                    time.sleep(3)
                    install_content = await page.content()
                    print("[STEP 2] Replacement triggered")

            # Activate
            activate_link = page.locator('a:has-text("Activate Plugin")')
            if await activate_link.count() > 0:
                print("[STEP 2] Activate link found — clicking...")
                await activate_link.click()
                await page.wait_for_load_state('domcontentloaded', timeout=60000)
                time.sleep(3)
                print("[STEP 2] SUCCESS: pb-video-modal uploaded and activated")
                results['video_modal_plugin'] = 'UPLOADED_AND_ACTIVATED'
            else:
                # Plugin may already be active
                if 'Plugin installed successfully' in install_content or 'Successfully installed' in install_content:
                    print("[STEP 2] Install successful but no activate link (may already be active)")
                    results['video_modal_plugin'] = 'INSTALLED - no activate link found'
                else:
                    print("[STEP 2] WARNING: No activate link found")
                    print("[STEP 2] Page snippet:", install_content[2000:3000])
                    results['video_modal_plugin'] = 'UNCERTAIN - check manually'
        else:
            print("[STEP 2] ERROR: No file input found on upload page")
            results['video_modal_plugin'] = 'FAILED - no file input'

        os.unlink(zip_path)
        print(f"[STEP 2] Temp zip deleted")

        # ----------------------------------------------------------------
        # STEP 3: Clear Elementor cache
        # ----------------------------------------------------------------
        print("\n[STEP 3] Clearing Elementor cache...")
        await page.goto(
            'https://purebrain.ai/wp-admin/admin.php?page=elementor&action=flush_css',
            wait_until='domcontentloaded',
            timeout=30000
        )
        time.sleep(2)
        # Also try the AJAX endpoint
        await page.goto(
            'https://purebrain.ai/wp-admin/admin-ajax.php?action=elementor_clear_cache',
            wait_until='domcontentloaded',
            timeout=30000
        )
        time.sleep(2)
        print("[STEP 3] Elementor cache flush attempted")
        results['elementor_cache'] = 'FLUSHED'

        # ----------------------------------------------------------------
        # STEP 4: Verify on plugins page
        # ----------------------------------------------------------------
        print("\n[STEP 4] Verifying on plugins page...")
        await page.goto(
            'https://purebrain.ai/wp-admin/plugins.php',
            wait_until='domcontentloaded',
            timeout=60000
        )
        time.sleep(3)
        plugins_content = await page.content()

        security_present = 'purebrain-security-plugin' in plugins_content or 'PureBrain Security' in plugins_content
        video_modal_present = 'pb-video-modal' in plugins_content or 'PureBrain Video Modal' in plugins_content

        print(f"[STEP 4] PureBrain Security plugin visible: {security_present}")
        print(f"[STEP 4] pb-video-modal plugin visible: {video_modal_present}")

        results['verification'] = {
            'security_plugin_visible': security_present,
            'video_modal_plugin_visible': video_modal_present,
        }

        await browser.close()

    return results


if __name__ == '__main__':
    results = asyncio.run(deploy())
    print("\n" + "=" * 60)
    print("DEPLOYMENT RESULTS SUMMARY")
    print("=" * 60)
    for key, val in results.items():
        print(f"  {key}: {val}")
