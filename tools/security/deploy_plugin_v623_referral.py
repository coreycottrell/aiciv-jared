#!/usr/bin/env python3
"""
Deploy purebrain-security-plugin.php v6.2.3 (Referral System Merged) to purebrain.ai.

This deploys the security plugin with the embedded PureBrain Referral System.

Changes in v6.2.3:
- MERGED: Full PureBrain Referral System (was a separate plugin)
- REST API: /wp-json/pb-referral/v1/{dashboard,register,click,convert,lookup}
- DB: Creates wp_pb_referrals and wp_pb_referral_users tables on first load
- URL rewrite: /r/XXXXXXXX -> /?ref=XXXXXXXX
- Seed data: Jared pre-seeded with code JAREDSB0 + 2 demo referrals
- Bypass: refer-and-earn page (ID 1298) added to portal bypass list
"""

import os
import re
import sys
import time
import base64
import urllib.parse
import urllib.request
import http.cookiejar
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / '.env')

BASE_URL    = "https://purebrain.ai"
WP_USER     = os.environ.get("PUREBRAIN_WP_USER", "Aether")
WP_PASSWORD = os.environ.get("PUREBRAIN_WP_PASSWORD", "")
WP_APP_PASS = os.environ.get("PUREBRAIN_WP_APP_PASSWORD", "")
PLUGIN_FILE = Path(__file__).parent / "purebrain-security" / "purebrain-security-plugin.php"

def _env(key):
    val = os.environ.get(key, "")
    if not val:
        print(f"ERROR: {key} not set in .env")
        sys.exit(1)
    return val

def check_referral_routes():
    """Verify referral API is live after deploy."""
    import requests
    r = requests.get(f"{BASE_URL}/wp-json/", timeout=15)
    if r.ok:
        routes = list(r.json().get('routes', {}).keys())
        referral = [x for x in routes if 'referral' in x]
        return referral
    return []


def deploy_via_http(plugin_content):
    """Cookie-based HTTP deploy."""
    print("\n[METHOD 1] Cookie-based HTTP deploy...")
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    opener.addheaders = [
        ('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'),
        ('Referer', f'{BASE_URL}/wp-login.php'),
    ]

    # Login
    login_data = urllib.parse.urlencode({
        'log': WP_USER,
        'pwd': WP_PASSWORD,
        'wp-submit': 'Log In',
        'redirect_to': '/wp-admin/',
        'testcookie': '1'
    }).encode()

    try:
        resp = opener.open(f"{BASE_URL}/wp-login.php", login_data, timeout=30)
        final_url = resp.geturl()
        print(f"  Login redirect: {final_url}")
        if "wp-login.php" in final_url:
            print("  ERROR: Login failed")
            return False

        # Get plugin editor with nonce
        time.sleep(2)
        resp2 = opener.open(
            f"{BASE_URL}/wp-admin/plugin-editor.php?file=purebrain-security%2Fpurebrain-security-plugin.php&plugin=purebrain-security%2Fpurebrain-security-plugin.php",
            timeout=30
        )
        editor_html = resp2.read().decode('utf-8', errors='replace')

        if resp2.getcode() == 429:
            print("  ERROR: Rate limited (429)")
            return False

        nonce_match = re.search(r'name="_wpnonce"\s+value="([^"]+)"', editor_html)
        if not nonce_match:
            print("  ERROR: No nonce found in plugin editor")
            return False

        nonce = nonce_match.group(1)
        print(f"  Nonce: {nonce[:10]}...")

        # Submit update
        post_data = urllib.parse.urlencode({
            'newcontent': plugin_content,
            '_wpnonce': nonce,
            '_wp_http_referer': '/wp-admin/plugin-editor.php?file=purebrain-security%2Fpurebrain-security-plugin.php&plugin=purebrain-security%2Fpurebrain-security-plugin.php',
            'action': 'edit-plugin-file-save',
            'file': 'purebrain-security/purebrain-security-plugin.php',
            'plugin': 'purebrain-security/purebrain-security-plugin.php',
            'docs-list': '',
            'submit': 'Update File'
        }).encode()

        resp3 = opener.open(f"{BASE_URL}/wp-admin/plugin-editor.php", post_data, timeout=60)
        result_html = resp3.read().decode('utf-8', errors='replace')

        if 'updated' in result_html.lower() or 'File edited successfully' in result_html:
            print("  SUCCESS: Plugin updated via HTTP")
            return True
        elif 'wp_plugin_error' in result_html or 'PHP' in result_html:
            err = re.search(r'id="wp_plugin_error"[^>]*>(.*?)</div>', result_html, re.DOTALL)
            if err:
                print(f"  PHP error: {re.sub('<[^>]+>', '', err.group(1)).strip()[:200]}")
            return False
        else:
            print(f"  Unknown result — page size {len(result_html)} chars")
            return False

    except Exception as e:
        print(f"  HTTP error: {e}")
        return False


def deploy_via_playwright(plugin_content):
    """Playwright browser deploy."""
    print("\n[METHOD 2] Playwright browser deploy...")
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  Playwright not installed. Run: pip install playwright && playwright install chromium")
        return False

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1400, "height": 900})
        page = ctx.new_page()
        page.goto(f"{BASE_URL}/wp-login.php", wait_until="networkidle", timeout=60000)

        sso = page.locator(".wpaas-sso-login-toggle")
        if sso.count() > 0 and sso.is_visible():
            print("  GoDaddy SSO toggle found — clicking...")
            sso.click()
            page.wait_for_load_state("networkidle")

        page.locator("#user_login").wait_for(state="visible", timeout=15000)
        page.fill("#user_login", WP_USER)
        page.fill("#user_pass", WP_PASSWORD)
        page.click("#wp-submit")
        page.wait_for_load_state("networkidle")

        if "wp-login.php" in page.url:
            print("  ERROR: Login failed")
            browser.close()
            return False

        print("  Login OK")
        page.goto(
            f"{BASE_URL}/wp-admin/plugin-editor.php?file=purebrain-security%2Fpurebrain-security-plugin.php&plugin=purebrain-security%2Fpurebrain-security-plugin.php",
            wait_until="networkidle", timeout=30000
        )

        ta = page.locator("#newcontent")
        if ta.count() == 0:
            print("  ERROR: No textarea found in plugin editor")
            browser.close()
            return False

        # Set value via JS (faster for large content)
        page.evaluate("content => { var ta = document.getElementById('newcontent'); if(ta) ta.value = content; }", plugin_content)
        page.click("[name='submit']")
        page.wait_for_load_state("networkidle")

        success = 'updated' in page.url.lower() or 'File edited' in page.content()
        print(f"  Result: {'SUCCESS' if success else 'uncertain — check manually'}")
        browser.close()
        return success


def main():
    print("=" * 60)
    print("PureBrain Security Plugin Deploy — v6.2.3 (Referral System)")
    print("=" * 60)

    plugin_content = PLUGIN_FILE.read_text()
    print(f"Plugin size: {len(plugin_content):,} chars")

    # Verify key markers
    assert 'PUREBRAIN REFERRAL SYSTEM' in plugin_content, "Referral system not found in plugin!"
    assert 'pb_ref_api_dashboard' in plugin_content, "Referral API functions missing!"
    assert 'pb_referral_ensure_tables' in plugin_content, "DB setup missing!"
    print("Plugin validation: PASSED")

    # Check if already deployed
    existing_routes = check_referral_routes()
    if existing_routes:
        print(f"\nReferral routes already live: {existing_routes}")
        print("Plugin may already be deployed. Verifying...")

    # Try deployment methods
    success = deploy_via_http(plugin_content)
    if not success:
        print("\nMethod 1 failed. Trying Playwright...")
        success = deploy_via_playwright(plugin_content)

    if success:
        print("\n" + "=" * 60)
        print("DEPLOY SUCCESS")
        print("Verifying referral API routes...")
        time.sleep(3)
        routes = check_referral_routes()
        if routes:
            print(f"Referral routes live: {routes}")
            print("\nTest the API:")
            print(f"  GET {BASE_URL}/wp-json/pb-referral/v1/dashboard?code=JAREDSB0")
        else:
            print("Note: Routes not yet visible (may need WP cache flush)")
    else:
        print("\n" + "=" * 60)
        print("ALL DEPLOY METHODS FAILED")
        print("\nManual deploy instructions:")
        print(f"  1. Go to: {BASE_URL}/wp-admin/plugin-editor.php")
        print("  2. Select: PureBrain Security > purebrain-security-plugin.php")
        print(f"  3. Paste content from: {PLUGIN_FILE}")
        print("  4. Click 'Update File'")
        print("\nOR copy via FTP/SFTP to:")
        print("  /wp-content/plugins/purebrain-security/purebrain-security-plugin.php")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
