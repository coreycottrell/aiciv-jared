"""
Deploy updated security plugin using Playwright.
Strategy: Use the EXACT same login approach that worked in the original
successful deployment (deploy_plugin_update.py Step 1 failed because the
plugin editor editor had no submit button, but the LOGIN itself worked).

Root issue analysis:
- First run: logged in fine, but #submit wasn't found in plugin editor
- Likely: plugin editor loaded but CodeMirror wasn't ready / editor disabled

New strategy:
1. Login (same as working original)
2. Use requests with WP cookies to submit the plugin editor form (bypasses
   CodeMirror entirely by posting newcontent directly)
"""
import asyncio
import os
import time
import re
import requests
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

WP_USER = os.getenv('PUREBRAIN_WP_USER')          # Aether
WP_PASS = os.getenv('PUREBRAIN_WP_PASSWORD')       # Regular password
WP_BASE = 'https://purebrain.ai'
PLUGIN_PHP = '/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security/purebrain-security-plugin.php'

print(f"WP_USER: {WP_USER}, WP_PASS len: {len(WP_PASS or '')}")


async def get_wp_session():
    """Login via Playwright (same method as original working script) and return cookies."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        print("[LOGIN] Navigating to WP login page...")
        await page.goto(
            f'{WP_BASE}/wp-login.php?wpaas-standard-login=1',
            wait_until='domcontentloaded', timeout=60000
        )
        time.sleep(3)

        print(f"[LOGIN] Title: {await page.title()}, URL: {page.url}")

        # Check page state
        title = await page.title()
        if 'verify' in title.lower() or 'captcha' in title.lower():
            print(f"[LOGIN] CAPTCHA still active. Title: {title}")
            await browser.close()
            return None, None

        # Handle GoDaddy SSO toggle
        sso_toggle = page.locator('.wpaas-sso-login-toggle')
        if await sso_toggle.count() > 0:
            print("[LOGIN] SSO toggle present - clicking to reveal standard login form...")
            await sso_toggle.click()
            time.sleep(2)
            # Wait for the standard form to appear
            try:
                await page.wait_for_selector('#user_login', timeout=10000)
                print("[LOGIN] Standard form appeared after SSO toggle click")
            except:
                print("[LOGIN] Standard form did NOT appear after SSO click")
                print(f"[LOGIN] URL after toggle: {page.url}")
                # Navigate back to standard login
                await page.goto(
                    f'{WP_BASE}/wp-login.php?wpaas-standard-login=1',
                    wait_until='domcontentloaded', timeout=60000
                )
                time.sleep(2)

        user_login_count = await page.locator('#user_login').count()
        print(f"[LOGIN] #user_login count: {user_login_count}")

        if user_login_count == 0:
            print("[LOGIN] Login form not visible")
            body = await page.inner_text('body')
            print(f"[LOGIN] Body: {body[:300]}")
            await browser.close()
            return None, None

        await page.fill('#user_login', WP_USER)
        await page.fill('#user_pass', WP_PASS)
        await page.click('#wp-submit')
        await page.wait_for_load_state('domcontentloaded', timeout=60000)
        time.sleep(3)

        print(f"[LOGIN] Post-login URL: {page.url}")
        if 'wp-admin' not in page.url:
            body = await page.inner_text('body')
            print(f"[LOGIN] FAILED: {body[:200]}")
            await browser.close()
            return None, None

        print("[LOGIN] SUCCESS!")

        # Navigate to plugin editor to get nonce
        editor_url = (
            f'{WP_BASE}/wp-admin/plugin-editor.php'
            '?file=purebrain-security-plugin%2Fpurebrain-security-plugin.php'
            '&plugin=purebrain-security-plugin%2Fpurebrain-security-plugin.php'
        )
        await page.goto(editor_url, wait_until='domcontentloaded', timeout=60000)
        time.sleep(8)

        html = await page.content()
        title = await page.title()
        print(f"[EDITOR] Title: {title}")

        # Get nonce
        nonce_match = re.search(r'name="_wpnonce" value="([a-f0-9]+)"', html)
        nonce = nonce_match.group(1) if nonce_match else None
        print(f"[EDITOR] Nonce: {'found' if nonce else 'NOT FOUND'}")

        # Check for editing being disabled
        if 'DISALLOW_FILE_EDIT' in html or 'File editing has been disabled' in html:
            print("[EDITOR] DISALLOW_FILE_EDIT active — plugin editor is disabled!")
            await browser.close()
            return None, None

        cm = await page.locator('.CodeMirror').count()
        ta = await page.locator('#newcontent').count()
        sub = await page.locator('#submit').count()
        print(f"[EDITOR] cm:{cm} ta:{ta} sub:{sub}")

        # Get cookies
        cookies = await context.cookies()
        cookie_dict = {c['name']: c['value'] for c in cookies}
        print(f"[EDITOR] Cookies obtained: {len(cookie_dict)}")

        # If submit is available, try Playwright path first
        if (cm > 0 or ta > 0) and sub > 0:
            with open(PLUGIN_PHP, 'r') as f:
                code = f.read()

            await page.evaluate('''(code) => {
                const cm = document.querySelector('.CodeMirror');
                if (cm && cm.CodeMirror) { cm.CodeMirror.setValue(code); cm.CodeMirror.save(); }
                const ta = document.querySelector('#newcontent');
                if (ta) ta.value = code;
            }''', code)
            time.sleep(2)

            await page.locator('#submit').first.click()
            await page.wait_for_load_state('domcontentloaded', timeout=60000)
            time.sleep(3)

            result = await page.inner_text('body')
            if 'File edited successfully' in result:
                print("[EDITOR] SUCCESS via Playwright direct!")
                await browser.close()
                return None, 'PLAYWRIGHT_SUCCESS'

        await browser.close()
        return cookie_dict, nonce


def submit_plugin_via_requests(cookie_dict, nonce):
    """Use requests with WP session cookies to POST to plugin editor."""
    with open(PLUGIN_PHP, 'r') as f:
        content = f.read()

    session = requests.Session()
    for name, value in cookie_dict.items():
        session.cookies.set(name, value, domain='purebrain.ai')

    editor_url = (
        f'{WP_BASE}/wp-admin/plugin-editor.php'
        '?file=purebrain-security-plugin%2Fpurebrain-security-plugin.php'
        '&plugin=purebrain-security-plugin%2Fpurebrain-security-plugin.php'
    )

    print(f"[REQUESTS] Submitting plugin update ({len(content)} chars, nonce: {nonce[:8]}...)")

    resp = session.post(
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
        headers={
            'Referer': editor_url,
            'Origin': WP_BASE,
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        timeout=120,
        allow_redirects=True
    )

    print(f"[REQUESTS] Status: {resp.status_code}, URL: {resp.url}")
    text = resp.text

    if 'File edited successfully' in text:
        print("[REQUESTS] SUCCESS: File edited successfully!")
        return 'SUCCESS'

    # Diagnose
    print("[REQUESTS] Success message not found. Checking...")
    for phrase in ['error', 'success', 'nonce', 'invalid', 'updated', 'notice', 'edited']:
        if phrase in text.lower():
            idx = text.lower().index(phrase)
            snippet = re.sub(r'<[^>]+>', '', text[max(0, idx-30):idx+120]).strip()
            if snippet and len(snippet) > 3:
                print(f"  '{phrase}': {snippet}")

    return 'UNCERTAIN'


if __name__ == '__main__':
    print("=" * 60)
    print("SECURITY PLUGIN DEPLOYMENT v3")
    print("=" * 60)

    cookie_dict, nonce_or_status = asyncio.run(get_wp_session())

    if nonce_or_status == 'PLAYWRIGHT_SUCCESS':
        print("\nResult: SUCCESS (via Playwright direct)")
    elif cookie_dict and nonce_or_status:
        result = submit_plugin_via_requests(cookie_dict, nonce_or_status)
        print(f"\nResult: {result}")
    else:
        print(f"\nResult: FAILED - could not get session (nonce_or_status={nonce_or_status})")
