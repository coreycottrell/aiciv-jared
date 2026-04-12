"""
Deploy updated security plugin.
Minimal approach: skip SSO toggle, rely on ?wpaas-standard-login=1 to show standard form.
Then use requests with cookies+nonce for the actual file upload.
"""
import asyncio
import os
import time
import re
import requests
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

WP_USER = os.getenv('PUREBRAIN_WP_USER')
WP_PASS = os.getenv('PUREBRAIN_WP_PASSWORD')
WP_APP_PASS = os.getenv('PUREBRAIN_WP_APP_PASSWORD')
WP_BASE = 'https://purebrain.ai'
PLUGIN_PHP = '/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security/purebrain-security-plugin.php'

print(f"WP_USER: {WP_USER}")
print(f"WP_PASS len: {len(WP_PASS or '')}")
print(f"WP_APP_PASS len: {len(WP_APP_PASS or '')}")


async def deploy():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # LOGIN - Try without clicking SSO toggle; ?wpaas-standard-login=1 should bypass SSO
        print("[LOGIN] Navigating to standard login URL...")
        await page.goto(
            f'{WP_BASE}/wp-login.php?wpaas-standard-login=1',
            wait_until='domcontentloaded', timeout=60000
        )
        time.sleep(4)

        print(f"[LOGIN] URL: {page.url}")
        print(f"[LOGIN] Title: {await page.title()}")

        # Debug: what's on the page?
        html = await page.content()
        user_login_count = await page.locator('#user_login').count()
        sso_count = await page.locator('.wpaas-sso-login-toggle').count()
        print(f"[LOGIN] #user_login: {user_login_count}, .wpaas-sso-login-toggle: {sso_count}")

        # If SSO toggle present, click it ONLY if #user_login is not visible
        if user_login_count == 0 and sso_count > 0:
            print("[LOGIN] user_login not visible, clicking SSO toggle...")
            await page.locator('.wpaas-sso-login-toggle').click()
            time.sleep(3)
            # After clicking, check what happened
            print(f"[LOGIN] After toggle URL: {page.url}")
            user_login_count = await page.locator('#user_login').count()
            print(f"[LOGIN] #user_login after toggle: {user_login_count}")

            if user_login_count == 0:
                # Navigate to the explicit standard login URL again
                print("[LOGIN] Trying explicit standard login URL again...")
                await page.goto(
                    f'{WP_BASE}/wp-login.php?wpaas-standard-login=1',
                    wait_until='domcontentloaded', timeout=60000
                )
                time.sleep(3)
                user_login_count = await page.locator('#user_login').count()
                print(f"[LOGIN] #user_login on second nav: {user_login_count}")

        if user_login_count == 0:
            # Try the form fill directly without waiting
            print("[LOGIN] Trying direct form fill...")
            try:
                await page.fill('#user_login', WP_USER, timeout=5000)
            except:
                # The standard login form has username/password as user_login/user_pass
                # Some GoDaddy managed WP uses different selectors
                print("[LOGIN] Direct fill failed, trying alternative approach")
                body_text = await page.inner_text('body')
                print(f"[LOGIN] Page body: {body_text[:500]}")
                await browser.close()
                return 'NO_LOGIN_FORM'

        # Fill credentials
        print(f"[LOGIN] Filling credentials for {WP_USER}...")
        await page.fill('#user_login', WP_USER)
        await page.fill('#user_pass', WP_PASS)
        await page.click('#wp-submit')
        await page.wait_for_load_state('domcontentloaded', timeout=60000)
        time.sleep(3)

        print(f"[LOGIN] Post-login URL: {page.url}")
        if 'wp-admin' not in page.url:
            body = await page.inner_text('body')
            print(f"[LOGIN] FAILED. Snippet: {body[:300]}")
            # Try with app password as regular password
            print("[LOGIN] Trying app password as password...")
            await page.goto(
                f'{WP_BASE}/wp-login.php?wpaas-standard-login=1',
                wait_until='domcontentloaded', timeout=60000
            )
            time.sleep(3)
            sso = await page.locator('.wpaas-sso-login-toggle').count()
            if sso > 0:
                await page.locator('.wpaas-sso-login-toggle').click()
                time.sleep(2)
            await page.fill('#user_login', WP_USER)
            await page.fill('#user_pass', WP_APP_PASS)
            await page.click('#wp-submit')
            await page.wait_for_load_state('domcontentloaded', timeout=60000)
            time.sleep(3)
            print(f"[LOGIN APP_PASS] URL: {page.url}")
            if 'wp-admin' not in page.url:
                await browser.close()
                return 'LOGIN_FAILED'

        print("[LOGIN] SUCCESS")

        # Navigate to plugin editor
        print("[EDITOR] Loading plugin editor...")
        editor_url = (
            f'{WP_BASE}/wp-admin/plugin-editor.php'
            '?file=purebrain-security-plugin%2Fpurebrain-security-plugin.php'
            '&plugin=purebrain-security-plugin%2Fpurebrain-security-plugin.php'
        )
        await page.goto(editor_url, wait_until='domcontentloaded', timeout=60000)
        time.sleep(10)

        print(f"[EDITOR] Title: {await page.title()}")

        html = await page.content()
        nonce_match = re.search(r'name="_wpnonce" value="([a-f0-9]+)"', html)
        nonce = nonce_match.group(1) if nonce_match else None
        print(f"[EDITOR] Nonce: {'found: ' + nonce[:8] if nonce else 'NOT FOUND'}")

        cm_count = await page.locator('.CodeMirror').count()
        ta_count = await page.locator('#newcontent').count()
        submit_count = await page.locator('#submit').count()
        print(f"[EDITOR] cm:{cm_count} ta:{ta_count} submit:{submit_count}")

        # Get cookies
        cookies = await context.cookies()
        cookie_dict = {c['name']: c['value'] for c in cookies}

        with open(PLUGIN_PHP, 'r') as f:
            security_code = f.read()

        # Set content if editor is available
        if cm_count > 0 or ta_count > 0:
            await page.evaluate('''(code) => {
                const cm = document.querySelector('.CodeMirror');
                if (cm && cm.CodeMirror) { cm.CodeMirror.setValue(code); cm.CodeMirror.save(); }
                const ta = document.querySelector('#newcontent');
                if (ta) ta.value = code;
            }''', security_code)
            time.sleep(2)

            for sel in ['#submit', 'input[name="submit"]', 'input[type="submit"]']:
                btn = page.locator(sel)
                if await btn.count() > 0:
                    await btn.first.click()
                    await page.wait_for_load_state('domcontentloaded', timeout=60000)
                    time.sleep(4)
                    result_body = await page.inner_text('body')
                    print(f"[EDITOR] Submit result URL: {page.url}")
                    if 'File edited successfully' in result_body:
                        print("[EDITOR] SUCCESS via Playwright!")
                        await browser.close()
                        return 'SUCCESS'
                    print(f"[EDITOR] Result: {result_body[:200]}")
                    break

        await browser.close()

        # Requests fallback
        if nonce and cookie_dict:
            print("\n[REQUESTS] Using cookies+nonce to submit...")
            session = requests.Session()
            for name, value in cookie_dict.items():
                session.cookies.set(name, value, domain='purebrain.ai')

            resp = session.post(
                f'{WP_BASE}/wp-admin/plugin-editor.php',
                data={
                    'newcontent': security_code,
                    'action': 'editedfile',
                    '_wpnonce': nonce,
                    '_wp_http_referer': '/wp-admin/plugin-editor.php?file=purebrain-security-plugin%2Fpurebrain-security-plugin.php&plugin=purebrain-security-plugin%2Fpurebrain-security-plugin.php',
                    'file': 'purebrain-security-plugin/purebrain-security-plugin.php',
                    'plugin': 'purebrain-security-plugin/purebrain-security-plugin.php',
                    'submit': 'Update File',
                },
                headers={'Referer': editor_url, 'Origin': WP_BASE},
                timeout=120, allow_redirects=True
            )
            print(f"[REQUESTS] Status: {resp.status_code}")
            if 'File edited successfully' in resp.text:
                print("[REQUESTS] SUCCESS!")
                return 'SUCCESS_VIA_REQUESTS'
            for phrase in ['error', 'success', 'nonce', 'invalid', 'updated', 'notice']:
                if phrase in resp.text.lower():
                    idx = resp.text.lower().index(phrase)
                    snippet = re.sub(r'<[^>]+>', '', resp.text[max(0, idx-20):idx+100]).strip()
                    if snippet and len(snippet) > 5:
                        print(f"  {phrase}: {snippet}")
            return 'REQUESTS_UNCERTAIN'

        return 'NO_NONCE'


if __name__ == '__main__':
    print("=" * 60)
    print("SECURITY PLUGIN DEPLOYMENT (DIRECT)")
    print("=" * 60)
    result = asyncio.run(deploy())
    print(f"\nResult: {result}")
