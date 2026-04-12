"""
Deploy updated security plugin using PUREBRAIN_WP_PASSWORD (regular password) via Playwright.
Then extract nonce and submit via requests for efficiency.
"""
import asyncio
import os
import time
import re
import requests
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

WP_USER = os.getenv('PUREBRAIN_WP_USER')          # 'Aether'
WP_PASS = os.getenv('PUREBRAIN_WP_PASSWORD')       # Regular password (not app password)
WP_BASE = 'https://purebrain.ai'
PLUGIN_PHP = '/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security/purebrain-security-plugin.php'

print(f"WP_USER: {WP_USER}, WP_PASS set: {bool(WP_PASS)}, len: {len(WP_PASS or '')}")


async def deploy():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # ---------------------------------------------------------------
        # LOGIN with regular password
        # ---------------------------------------------------------------
        print("[LOGIN] Navigating...")
        await page.goto(
            f'{WP_BASE}/wp-login.php?wpaas-standard-login=1',
            wait_until='domcontentloaded', timeout=60000
        )
        time.sleep(3)

        sso_toggle = page.locator('.wpaas-sso-login-toggle')
        if await sso_toggle.count() > 0:
            print("[LOGIN] Clicking SSO toggle...")
            await sso_toggle.click()
            time.sleep(2)

        await page.wait_for_selector('#user_login', timeout=15000)
        await page.fill('#user_login', WP_USER)
        await page.fill('#user_pass', WP_PASS)
        await page.click('#wp-submit')
        await page.wait_for_load_state('domcontentloaded', timeout=60000)
        time.sleep(3)

        print(f"[LOGIN] URL: {page.url}")
        if 'wp-admin' not in page.url:
            body = await page.inner_text('body')
            print(f"[LOGIN] FAILED. Body: {body[:300]}")
            await browser.close()
            return 'LOGIN_FAILED'

        print("[LOGIN] SUCCESS")

        # ---------------------------------------------------------------
        # NAVIGATE TO PLUGIN EDITOR
        # ---------------------------------------------------------------
        print("[EDITOR] Loading plugin editor...")
        editor_url = (
            f'{WP_BASE}/wp-admin/plugin-editor.php'
            '?file=purebrain-security-plugin%2Fpurebrain-security-plugin.php'
            '&plugin=purebrain-security-plugin%2Fpurebrain-security-plugin.php'
        )
        await page.goto(editor_url, wait_until='domcontentloaded', timeout=60000)
        time.sleep(8)  # Wait for CodeMirror to fully load

        print(f"[EDITOR] Title: {await page.title()}")
        print(f"[EDITOR] URL: {page.url}")

        cm_count = await page.locator('.CodeMirror').count()
        ta_count = await page.locator('#newcontent').count()
        submit_count = await page.locator('#submit').count()
        print(f"[EDITOR] CodeMirror:{cm_count} textarea:{ta_count} submit:{submit_count}")

        # Check for blocking messages
        body = await page.inner_text('body')
        if 'not allowed' in body.lower() or 'disabled' in body.lower():
            print(f"[EDITOR] Blocked: {body[:300]}")
            await browser.close()
            return 'EDITING_BLOCKED'

        # Get HTML for nonce extraction
        html = await page.content()
        nonce_match = re.search(r'name="_wpnonce" value="([a-f0-9]+)"', html)
        nonce = nonce_match.group(1) if nonce_match else None
        print(f"[EDITOR] Nonce: {nonce[:8] if nonce else 'NOT FOUND'}...")

        # Get cookies for requests fallback
        cookies = await context.cookies()
        cookie_dict = {c['name']: c['value'] for c in cookies}
        print(f"[EDITOR] Cookies: {len(cookie_dict)}")

        with open(PLUGIN_PHP, 'r') as f:
            security_code = f.read()
        print(f"[EDITOR] Plugin code: {len(security_code)} chars")

        # Set editor content
        if cm_count > 0:
            print("[EDITOR] Setting CodeMirror content...")
            await page.evaluate('''(code) => {
                const cm = document.querySelector('.CodeMirror');
                if (cm && cm.CodeMirror) {
                    cm.CodeMirror.setValue(code);
                    cm.CodeMirror.save();
                }
                // Also set underlying textarea
                const ta = document.querySelector('#newcontent');
                if (ta) ta.value = code;
            }''', security_code)
            time.sleep(2)
        elif ta_count > 0:
            print("[EDITOR] Setting textarea content...")
            await page.evaluate('''(code) => {
                document.querySelector('#newcontent').value = code;
            }''', security_code)
            time.sleep(1)
        else:
            print("[EDITOR] No editor found — will try requests approach with nonce")

        # Try clicking submit
        clicked = False
        for sel in ['#submit', 'input[name="submit"]', 'input[type="submit"]']:
            btn = page.locator(sel)
            if await btn.count() > 0:
                print(f"[EDITOR] Clicking {sel}...")
                await btn.first.click()
                await page.wait_for_load_state('domcontentloaded', timeout=60000)
                time.sleep(4)
                clicked = True
                break

        if clicked:
            result_body = await page.inner_text('body')
            print(f"[EDITOR] Post-submit URL: {page.url}")
            if 'File edited successfully' in result_body:
                print("[EDITOR] SUCCESS via Playwright!")
                await browser.close()
                return 'SUCCESS'
            else:
                print(f"[EDITOR] Post-submit result: {result_body[:200]}")

        # ---------------------------------------------------------------
        # FALLBACK: Submit via requests using Playwright cookies + nonce
        # ---------------------------------------------------------------
        if nonce and cookie_dict:
            print("\n[REQUESTS FALLBACK] Attempting with cookies + nonce...")
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
            if 'File edited successfully' in resp.text:
                print("[REQUESTS] SUCCESS!")
                await browser.close()
                return 'SUCCESS_VIA_REQUESTS'
            else:
                for phrase in ['error', 'success', 'nonce', 'invalid', 'updated']:
                    if phrase in resp.text.lower():
                        idx = resp.text.lower().index(phrase)
                        snippet = re.sub(r'<[^>]+>', '', resp.text[max(0, idx-20):idx+100]).strip()
                        if snippet and len(snippet) > 3:
                            print(f"  {phrase}: {snippet}")
                await browser.close()
                return 'REQUESTS_UNCERTAIN'

        await browser.close()
        return 'NO_NONCE_OR_COOKIES'


if __name__ == '__main__':
    print("=" * 60)
    print("SECURITY PLUGIN FINAL DEPLOYMENT")
    print("=" * 60)
    result = asyncio.run(deploy())
    print(f"\nFinal result: {result}")
