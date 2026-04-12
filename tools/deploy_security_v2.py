"""
Deploy updated security plugin to purebrain.ai.
Uses explicit waits and cookies persistence across requests.
"""
import asyncio
import os
import time
import re
import requests
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

WP_USER = os.getenv('PUREBRAIN_WP_USER') or os.getenv('WORDPRESS_USER') or 'admin'
WP_PASS = (
    os.getenv('PUREBRAIN_WP_APP_PASSWORD') or
    os.getenv('PUREBRAIN_WP_PASSWORD') or
    os.getenv('WORDPRESS_APP_PASSWORD') or
    ''
)
WP_BASE = 'https://purebrain.ai'
SECURITY_PLUGIN_PHP = '/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security/purebrain-security-plugin.php'

print(f"WP_USER: {WP_USER}")
print(f"WP_PASS set: {bool(WP_PASS)}, length: {len(WP_PASS)}")


async def get_cookies_via_playwright():
    """Log in via Playwright and return cookies for use with requests."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        print("[LOGIN] Going to login page...")
        await page.goto(
            f'{WP_BASE}/wp-login.php?wpaas-standard-login=1',
            wait_until='domcontentloaded', timeout=60000
        )
        time.sleep(3)

        print(f"[LOGIN] Title: {await page.title()}")
        print(f"[LOGIN] URL: {page.url}")

        # Check for SSO toggle
        sso_toggle = page.locator('.wpaas-sso-login-toggle')
        if await sso_toggle.count() > 0:
            print("[LOGIN] SSO toggle present - clicking...")
            await sso_toggle.click()
            time.sleep(2)

        # Wait for the login form fields
        await page.wait_for_selector('#user_login', timeout=10000)
        print("[LOGIN] Login form visible")

        await page.fill('#user_login', WP_USER)
        await page.fill('#user_pass', WP_PASS)
        await page.click('#wp-submit')

        # Wait for redirect to wp-admin
        await page.wait_for_load_state('domcontentloaded', timeout=60000)
        time.sleep(3)

        print(f"[LOGIN] After submit URL: {page.url}")

        if 'wp-admin' not in page.url:
            print("[LOGIN] Not in wp-admin. Checking for error...")
            body = await page.inner_text('body')
            print(f"[LOGIN] Body snippet: {body[:300]}")
            await browser.close()
            return None, None

        print("[LOGIN] Successfully in wp-admin!")

        # Grab cookies
        cookies = await context.cookies()
        cookie_dict = {c['name']: c['value'] for c in cookies}
        print(f"[LOGIN] Got {len(cookies)} cookies")

        # Navigate to plugin editor to get nonce
        print("[EDITOR] Loading plugin editor via Playwright...")
        await page.goto(
            f'{WP_BASE}/wp-admin/plugin-editor.php'
            '?file=purebrain-security-plugin%2Fpurebrain-security-plugin.php'
            '&plugin=purebrain-security-plugin%2Fpurebrain-security-plugin.php',
            wait_until='domcontentloaded', timeout=60000
        )
        time.sleep(6)

        print(f"[EDITOR] Title: {await page.title()}")
        print(f"[EDITOR] URL: {page.url}")

        # Check if editing is available
        body = await page.inner_text('body')
        if 'not allowed' in body.lower() or 'disabled' in body.lower():
            print(f"[EDITOR] Editing blocked: {body[:200]}")

        cm_count = await page.locator('.CodeMirror').count()
        submit_count = await page.locator('#submit').count()
        textarea_count = await page.locator('#newcontent').count()
        print(f"[EDITOR] CodeMirror: {cm_count}, #submit: {submit_count}, #newcontent: {textarea_count}")

        # Take page HTML snapshot for diagnosis
        html = await page.content()
        # Find the form and nonce
        nonce_match = re.search(r'name="_wpnonce" value="([a-f0-9]+)"', html)
        nonce = nonce_match.group(1) if nonce_match else None
        print(f"[EDITOR] Nonce found: {bool(nonce)}")
        if nonce:
            print(f"[EDITOR] Nonce: {nonce[:8]}...")

        with open(SECURITY_PLUGIN_PHP, 'r') as f:
            security_code = f.read()

        # Try to use the editor directly
        if cm_count > 0:
            print("[EDITOR] Using CodeMirror...")
            await page.evaluate('''(code) => {
                const cm = document.querySelector('.CodeMirror');
                if (cm && cm.CodeMirror) {
                    cm.CodeMirror.setValue(code);
                    cm.CodeMirror.save();
                }
            }''', security_code)
            time.sleep(2)

            # Also set the hidden textarea directly
            await page.evaluate('''(code) => {
                const ta = document.querySelector('#newcontent');
                if (ta) ta.value = code;
            }''', security_code)

        elif textarea_count > 0:
            print("[EDITOR] Using textarea directly...")
            await page.evaluate('''(code) => {
                document.querySelector('#newcontent').value = code;
            }''', security_code)

        # Find and click submit
        submit_clicked = False
        for sel in ['#submit', 'input[name="submit"]', 'input[type="submit"]']:
            btn = page.locator(sel)
            if await btn.count() > 0:
                print(f"[EDITOR] Clicking {sel}...")
                await btn.first.click()
                await page.wait_for_load_state('domcontentloaded', timeout=60000)
                time.sleep(3)
                submit_clicked = True
                break

        if submit_clicked:
            result_body = await page.inner_text('body')
            if 'File edited successfully' in result_body:
                print("[EDITOR] SUCCESS via Playwright")
                await browser.close()
                return cookie_dict, nonce

        await browser.close()
        return cookie_dict, nonce


def submit_via_requests(cookie_dict, nonce):
    """Use requests with cookies + nonce to POST to plugin editor."""
    if not nonce:
        print("[REQUESTS] No nonce available, cannot submit")
        return 'NO_NONCE'

    with open(SECURITY_PLUGIN_PHP, 'r') as f:
        content = f.read()

    session = requests.Session()

    # Set cookies
    for name, value in cookie_dict.items():
        session.cookies.set(name, value, domain='purebrain.ai')

    print(f"[REQUESTS] Submitting with {len(cookie_dict)} cookies, nonce={nonce[:8]}...")

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
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': f'{WP_BASE}/wp-admin/plugin-editor.php?file=purebrain-security-plugin%2Fpurebrain-security-plugin.php',
            'Origin': WP_BASE,
        },
        timeout=120,
        allow_redirects=True
    )

    print(f"[REQUESTS] Status: {resp.status_code}, URL: {resp.url}")

    text = resp.text
    if 'File edited successfully' in text:
        print("[REQUESTS] SUCCESS: File edited successfully!")
        return 'SUCCESS'
    elif 'edited' in text.lower() and 'success' in text.lower():
        print("[REQUESTS] LIKELY SUCCESS")
        return 'LIKELY_SUCCESS'
    else:
        # Diagnose
        for phrase in ['error', 'success', 'nonce', 'invalid', 'notice', 'updated']:
            if phrase in text.lower():
                idx = text.lower().index(phrase)
                snippet = text[max(0, idx-30):idx+120]
                clean = re.sub(r'<[^>]+>', '', snippet).strip()
                if clean:
                    print(f"  '{phrase}': {clean}")
        return 'UNCERTAIN'


async def playwright_full_submit():
    """Single Playwright session: login + navigate to editor + submit form directly."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Login
        await page.goto(
            f'{WP_BASE}/wp-login.php?wpaas-standard-login=1',
            wait_until='domcontentloaded', timeout=60000
        )
        time.sleep(3)

        sso_toggle = page.locator('.wpaas-sso-login-toggle')
        if await sso_toggle.count() > 0:
            await sso_toggle.click()
            time.sleep(2)

        await page.wait_for_selector('#user_login', timeout=10000)
        await page.fill('#user_login', WP_USER)
        await page.fill('#user_pass', WP_PASS)
        await page.click('#wp-submit')
        await page.wait_for_load_state('domcontentloaded', timeout=60000)
        time.sleep(3)

        if 'wp-admin' not in page.url:
            print(f"[FULL] Login failed. URL: {page.url}")
            await browser.close()
            return 'LOGIN_FAILED'

        print(f"[FULL] Logged in. URL: {page.url}")

        # Load plugin editor
        await page.goto(
            f'{WP_BASE}/wp-admin/plugin-editor.php'
            '?file=purebrain-security-plugin%2Fpurebrain-security-plugin.php'
            '&plugin=purebrain-security-plugin%2Fpurebrain-security-plugin.php',
            wait_until='domcontentloaded', timeout=60000
        )
        time.sleep(8)

        html = await page.content()
        title = await page.title()
        print(f"[FULL] Editor page title: {title}")

        # Check if DISALLOW_FILE_EDIT is set
        if 'DISALLOW_FILE_EDIT' in html or 'File editing has been disabled' in html:
            print("[FULL] DISALLOW_FILE_EDIT is true — cannot use plugin editor")
            await browser.close()
            return 'FILE_EDIT_DISABLED'

        # Check for the editor
        cm_count = await page.locator('.CodeMirror').count()
        ta_count = await page.locator('#newcontent').count()
        submit_count = await page.locator('#submit').count()
        print(f"[FULL] cm:{cm_count} ta:{ta_count} submit:{submit_count}")

        # Debug: print all form fields
        inputs = await page.locator('input, textarea, button').all()
        print(f"[FULL] Total form elements: {len(inputs)}")
        for inp in inputs[:15]:
            id_val = await inp.get_attribute('id') or ''
            name_val = await inp.get_attribute('name') or ''
            type_val = await inp.get_attribute('type') or ''
            print(f"  input: id={id_val} name={name_val} type={type_val}")

        with open(SECURITY_PLUGIN_PHP, 'r') as f:
            security_code = f.read()

        if cm_count > 0:
            await page.evaluate('''(code) => {
                const cm = document.querySelector('.CodeMirror');
                if (cm && cm.CodeMirror) {
                    cm.CodeMirror.setValue(code);
                    cm.CodeMirror.save();
                }
                const ta = document.querySelector('#newcontent');
                if (ta) ta.value = code;
            }''', security_code)
            time.sleep(2)
        elif ta_count > 0:
            await page.evaluate('''(code) => {
                document.querySelector('#newcontent').value = code;
            }''', security_code)
            time.sleep(1)
        else:
            # No editor found — is the page showing the file selection, not the editor?
            # Check for plugin file selector
            select_count = await page.locator('select[name="file"]').count()
            print(f"[FULL] select[name=file]: {select_count}")
            if select_count > 0:
                # Select the main file
                await page.select_option('select[name="file"]', 'purebrain-security-plugin/purebrain-security-plugin.php')
                await page.click('#submit')
                await page.wait_for_load_state('domcontentloaded', timeout=60000)
                time.sleep(5)
                cm_count2 = await page.locator('.CodeMirror').count()
                ta_count2 = await page.locator('#newcontent').count()
                print(f"[FULL] After file select — cm:{cm_count2} ta:{ta_count2}")

                if cm_count2 > 0:
                    await page.evaluate('''(code) => {
                        const cm = document.querySelector('.CodeMirror');
                        if (cm && cm.CodeMirror) {
                            cm.CodeMirror.setValue(code);
                            cm.CodeMirror.save();
                        }
                        const ta = document.querySelector('#newcontent');
                        if (ta) ta.value = code;
                    }''', security_code)
                    time.sleep(2)
                elif ta_count2 > 0:
                    await page.evaluate('''(code) => {
                        document.querySelector('#newcontent').value = code;
                    }''', security_code)
                    time.sleep(1)

        # Click submit
        for sel in ['#submit', 'input[name="submit"]', 'input[type="submit"][value*="Update"]', 'input[type="submit"]']:
            btn = page.locator(sel)
            if await btn.count() > 0:
                print(f"[FULL] Clicking {sel}...")
                await btn.first.click()
                await page.wait_for_load_state('domcontentloaded', timeout=60000)
                time.sleep(4)
                result_body = await page.inner_text('body')
                if 'File edited successfully' in result_body:
                    print("[FULL] SUCCESS!")
                    await browser.close()
                    return 'SUCCESS'
                print(f"[FULL] Post-submit URL: {page.url}")
                print(f"[FULL] Result snippet: {result_body[:300]}")
                await browser.close()
                return 'SUBMITTED_UNCERTAIN'

        print("[FULL] Could not find submit button")
        await browser.close()
        return 'NO_SUBMIT'


if __name__ == '__main__':
    print("=" * 60)
    print("SECURITY PLUGIN UPDATE — ATTEMPT 2")
    print("=" * 60)

    # Try the full Playwright session approach
    result = asyncio.run(playwright_full_submit())
    print(f"\nResult: {result}")

    if result not in ('SUCCESS',):
        print("\nTrying get-cookies + requests approach...")
        cookies, nonce = asyncio.run(get_cookies_via_playwright())
        if cookies and nonce:
            r2 = submit_via_requests(cookies, nonce)
            print(f"Requests result: {r2}")
        else:
            print("Could not get cookies/nonce for requests approach")
