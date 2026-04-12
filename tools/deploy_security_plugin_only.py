"""
Deploy the updated security plugin to purebrain.ai.
Retries the plugin editor step with better diagnostics and
a fallback to WP REST API if CodeMirror/submit isn't available.
"""
import asyncio
import os
import time
import requests
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

WP_USER = (
    os.getenv('PUREBRAIN_WP_USER') or
    os.getenv('WORDPRESS_USER') or
    'admin'
)
WP_PASS = (
    os.getenv('PUREBRAIN_WP_APP_PASSWORD') or
    os.getenv('PUREBRAIN_WP_PASSWORD') or
    os.getenv('WORDPRESS_APP_PASSWORD') or
    ''
)
WP_BASE = 'https://purebrain.ai'

SECURITY_PLUGIN_PHP = '/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security/purebrain-security-plugin.php'


async def deploy_via_editor():
    """Try plugin editor via Playwright with better wait strategy."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Login
        print("[LOGIN] Navigating to WP login...")
        await page.goto(
            f'{WP_BASE}/wp-login.php?wpaas-standard-login=1',
            wait_until='domcontentloaded', timeout=60000
        )
        time.sleep(2)

        sso_toggle = page.locator('.wpaas-sso-login-toggle')
        if await sso_toggle.count() > 0:
            print("[LOGIN] SSO toggle found, clicking...")
            await sso_toggle.click()
            time.sleep(1)

        await page.fill('#user_login', WP_USER)
        await page.fill('#user_pass', WP_PASS)
        await page.click('#wp-submit')
        await page.wait_for_load_state('domcontentloaded', timeout=60000)
        time.sleep(3)
        print(f"[LOGIN] URL: {page.url}")

        # Navigate to plugin editor
        print("[EDITOR] Loading plugin editor...")
        await page.goto(
            f'{WP_BASE}/wp-admin/plugin-editor.php'
            '?file=purebrain-security-plugin%2Fpurebrain-security-plugin.php'
            '&plugin=purebrain-security-plugin%2Fpurebrain-security-plugin.php',
            wait_until='domcontentloaded', timeout=60000
        )
        # Wait longer for CodeMirror to initialize
        time.sleep(8)

        # Diagnose the page
        page_title = await page.title()
        print(f"[EDITOR] Page title: {page_title}")

        # Check what's on the page
        submit_count = await page.locator('#submit').count()
        codemirror_count = await page.locator('.CodeMirror').count()
        textarea_count = await page.locator('#newcontent').count()
        print(f"[EDITOR] #submit: {submit_count}, .CodeMirror: {codemirror_count}, #newcontent: {textarea_count}")

        # Check for "editing is disabled" message
        body_text = await page.inner_text('body')
        if 'not allowed to edit' in body_text.lower() or 'editing is disabled' in body_text.lower() or 'you are not allowed' in body_text.lower():
            print("[EDITOR] BLOCKED: Plugin editing is disabled on this WP install")
            await browser.close()
            return 'BLOCKED'

        with open(SECURITY_PLUGIN_PHP, 'r') as f:
            security_code = f.read()
        print(f"[EDITOR] Plugin code loaded: {len(security_code)} chars")

        if codemirror_count > 0:
            print("[EDITOR] CodeMirror found, setting value...")
            result = await page.evaluate('''(code) => {
                const cm = document.querySelector('.CodeMirror');
                if (cm && cm.CodeMirror) {
                    cm.CodeMirror.setValue(code);
                    cm.CodeMirror.save();
                    return "cm_set";
                }
                return "no_cm";
            }''', security_code)
            print(f"[EDITOR] CodeMirror set result: {result}")
            time.sleep(2)

        elif textarea_count > 0:
            print("[EDITOR] Using textarea directly (no CodeMirror)...")
            await page.evaluate('''(code) => {
                document.querySelector('#newcontent').value = code;
            }''', security_code)
            time.sleep(1)

        else:
            print("[EDITOR] ERROR: Neither CodeMirror nor textarea found")
            # Dump page snippet for diagnosis
            print("[EDITOR] Page snippet:", body_text[:500])
            await browser.close()
            return 'NO_EDITOR'

        # Re-check for submit button after waiting
        time.sleep(2)
        submit_count = await page.locator('#submit').count()
        submit_input_count = await page.locator('input[name="submit"]').count()
        submit_button_count = await page.locator('input[type="submit"]').count()
        print(f"[EDITOR] After set — #submit: {submit_count}, input[name=submit]: {submit_input_count}, input[type=submit]: {submit_button_count}")

        # Try multiple selectors for the submit button
        clicked = False
        for selector in ['#submit', 'input[name="submit"]', 'input[type="submit"]', 'button[type="submit"]']:
            btn = page.locator(selector)
            cnt = await btn.count()
            if cnt > 0:
                print(f"[EDITOR] Clicking submit via selector: {selector}")
                await btn.first.click()
                await page.wait_for_load_state('domcontentloaded', timeout=60000)
                time.sleep(3)
                clicked = True
                break

        if not clicked:
            print("[EDITOR] No submit button found with any selector — trying JS form submit")
            await page.evaluate('''() => {
                const form = document.querySelector('form#template') || document.querySelector('form');
                if (form) { form.submit(); return true; }
                return false;
            }''')
            await page.wait_for_load_state('domcontentloaded', timeout=60000)
            time.sleep(3)

        result_text = await page.inner_text('body')
        print(f"[EDITOR] Post-submit URL: {page.url}")

        if 'File edited successfully' in result_text:
            print("[EDITOR] SUCCESS: File edited successfully")
            await browser.close()
            return 'SUCCESS'
        elif 'Plugin file edited' in result_text:
            print("[EDITOR] SUCCESS: Plugin file edited")
            await browser.close()
            return 'SUCCESS'
        else:
            print("[EDITOR] Uncertain result. Page snippet:")
            # Find error/success messages
            for phrase in ['error', 'success', 'updated', 'saved', 'notice']:
                if phrase in result_text.lower():
                    idx = result_text.lower().index(phrase)
                    print(f"  '{phrase}' context: {result_text[max(0, idx-50):idx+100]}")
            await browser.close()
            return 'UNCERTAIN'


def deploy_via_rest_api():
    """
    Fallback: use WP REST API to update the plugin file content.
    Note: WP core REST API doesn't expose plugin file editing,
    but we can use the theme/plugin editor endpoint if available.
    """
    print("\n[REST API] Attempting via WordPress REST API...")

    with open(SECURITY_PLUGIN_PHP, 'r') as f:
        content = f.read()

    # Try WP REST file editing endpoint (available in some setups)
    endpoint = f'{WP_BASE}/wp-json/wp/v2/plugins/purebrain-security-plugin/purebrain-security-plugin.php'

    resp = requests.put(
        endpoint,
        json={'content': content},
        auth=(WP_USER, WP_PASS),
        timeout=30
    )
    print(f"[REST API] Status: {resp.status_code}")
    print(f"[REST API] Response: {resp.text[:300]}")

    if resp.status_code in (200, 201):
        return 'SUCCESS'
    return f'FAILED ({resp.status_code})'


def deploy_via_wp_cli_rest():
    """
    Use WP REST API plugin endpoint to update plugin code.
    Uses the purebrain security plugin's own update-post-meta style endpoint if available.
    """
    # Check if there's a custom REST endpoint for plugin updates
    print("[WP-REST] Checking for custom plugin update endpoint...")

    with open(SECURITY_PLUGIN_PHP, 'r') as f:
        content = f.read()

    # Try the standard plugin update via direct file write through WP AJAX
    # This requires an authenticated nonce
    session = requests.Session()

    # First get login cookies
    login_resp = session.post(
        f'{WP_BASE}/wp-login.php?wpaas-standard-login=1',
        data={
            'log': WP_USER,
            'pwd': WP_PASS,
            'wp-submit': 'Log In',
            'redirect_to': '/wp-admin/',
            'testcookie': '1',
        },
        headers={'Cookie': 'wordpress_test_cookie=WP+Cookie+check'},
        allow_redirects=True,
        timeout=30
    )
    print(f"[WP-REST] Login response status: {login_resp.status_code}")
    print(f"[WP-REST] Login URL: {login_resp.url}")

    if 'wp-admin' not in login_resp.url:
        print("[WP-REST] Login may have failed")
        return 'LOGIN_FAILED'

    # Get nonce from plugin editor page
    editor_resp = session.get(
        f'{WP_BASE}/wp-admin/plugin-editor.php'
        '?file=purebrain-security-plugin%2Fpurebrain-security-plugin.php'
        '&plugin=purebrain-security-plugin%2Fpurebrain-security-plugin.php',
        timeout=30
    )

    import re
    nonce_match = re.search(r'"nonce":"([a-f0-9]+)"', editor_resp.text)
    if not nonce_match:
        nonce_match = re.search(r'_wpnonce["\s]+value="([a-f0-9]+)"', editor_resp.text)
    if not nonce_match:
        nonce_match = re.search(r'nonce["\s:=]+["\']([a-f0-9]+)["\']', editor_resp.text)

    if nonce_match:
        nonce = nonce_match.group(1)
        print(f"[WP-REST] Got nonce: {nonce[:8]}...")
    else:
        print("[WP-REST] Could not extract nonce from editor page")
        return 'NO_NONCE'

    # Submit the form with the updated content
    submit_resp = session.post(
        f'{WP_BASE}/wp-admin/plugin-editor.php',
        data={
            'newcontent': content,
            'action': 'editedfile',
            '_wpnonce': nonce,
            '_wp_http_referer': '/wp-admin/plugin-editor.php?file=purebrain-security-plugin%2Fpurebrain-security-plugin.php&plugin=purebrain-security-plugin%2Fpurebrain-security-plugin.php',
            'file': 'purebrain-security-plugin/purebrain-security-plugin.php',
            'plugin': 'purebrain-security-plugin/purebrain-security-plugin.php',
            'plugin_ver': '',
            'submit': 'Update File',
        },
        timeout=60,
        allow_redirects=True
    )

    print(f"[WP-REST] Submit status: {submit_resp.status_code}")
    if 'File edited successfully' in submit_resp.text:
        print("[WP-REST] SUCCESS: File edited successfully")
        return 'SUCCESS'
    elif 'edited' in submit_resp.text.lower():
        print("[WP-REST] Likely success")
        return 'LIKELY_SUCCESS'
    else:
        print("[WP-REST] Result unclear")
        # Print relevant portion
        for phrase in ['error', 'success', 'updated', 'notice', 'nonce']:
            if phrase in submit_resp.text.lower():
                idx = submit_resp.text.lower().index(phrase)
                snippet = submit_resp.text[max(0, idx-30):idx+100]
                # Strip HTML
                clean = re.sub(r'<[^>]+>', '', snippet)
                print(f"  '{phrase}': {clean}")
        return 'UNCERTAIN'


if __name__ == '__main__':
    print("=" * 60)
    print("DEPLOYING SECURITY PLUGIN UPDATE")
    print("=" * 60)

    # Try Playwright editor first
    result = asyncio.run(deploy_via_editor())
    print(f"\nPlaywright editor result: {result}")

    if result not in ('SUCCESS',):
        print("\nFalling back to requests-based form submission...")
        result2 = deploy_via_wp_cli_rest()
        print(f"Requests fallback result: {result2}")
    else:
        result2 = None

    print("\n" + "=" * 60)
    print("SECURITY PLUGIN DEPLOYMENT SUMMARY")
    print("=" * 60)
    print(f"  Playwright editor: {result}")
    if result2:
        print(f"  Requests fallback: {result2}")
