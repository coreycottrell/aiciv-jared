#!/usr/bin/env python3
"""
Deploy purebrain-referral-system.php v2.0.0 to purebrain.ai.

Phase 2 changes:
- Reward ledger table (wp_pb_reward_ledger)
- [pb_referral_register] shortcode with rate limiting
- [pb_referral_dashboard] shortcode with stats, history, referral link
- localStorage + cookie attribution injection on wp_footer
- Idempotent /convert endpoint
- Email notification on conversion (wp_mail)
- GET /rewards endpoint for ledger
- Rate limiting on /register (3/IP/hour)
- XSS protection in shortcode output (pbEscape helper)
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

# The standalone referral plugin file
PLUGIN_FILE = Path(__file__).parent / "purebrain-referral" / "purebrain-referral-system.php"
PLUGIN_SLUG = "purebrain-referral/purebrain-referral-system.php"
PLUGIN_URL_SLUG = "purebrain-referral%2Fpurebrain-referral-system.php"


def verify_plugin_content(content):
    checks = [
        ('Version 2.0.0', "Version:     2.0.0"),
        ('Reward ledger table', 'pb_reward_ledger'),
        ('Register shortcode', 'pb_referral_register'),
        ('Dashboard shortcode', 'pb_referral_dashboard'),
        ('Attribution script', 'pb_referral_inject_attribution_script'),
        ('Idempotency check', 'IDEMPOTENCY'),
        ('Rate limiting', 'rate_limited'),
        ('Email notification', 'pb_referral_notify_referrer_conversion'),
        ('Rewards endpoint', 'pb_referral_api_rewards'),
        ('XSS protection', 'pbEscape'),
    ]
    all_pass = True
    for name, marker in checks:
        found = marker in content
        status = "PASS" if found else "FAIL"
        print(f"  [{status}] {name}")
        if not found:
            all_pass = False
    return all_pass


def check_referral_routes():
    """Verify referral API is live after deploy."""
    try:
        import urllib.request as r
        req = urllib.request.Request(f"{BASE_URL}/wp-json/", headers={'User-Agent': 'Mozilla/5.0'})
        import json
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            routes = list(data.get('routes', {}).keys())
            return [x for x in routes if 'pb-referral' in x]
    except Exception as e:
        print(f"  Route check error: {e}")
        return []


def deploy_via_http(plugin_content):
    """Cookie-based WordPress plugin editor deploy."""
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

        time.sleep(2)

        # Get referral plugin editor with nonce
        editor_url = (
            f"{BASE_URL}/wp-admin/plugin-editor.php"
            f"?file={PLUGIN_URL_SLUG}&plugin={PLUGIN_URL_SLUG}"
        )
        resp2 = opener.open(editor_url, timeout=30)
        editor_html = resp2.read().decode('utf-8', errors='replace')

        if resp2.getcode() == 429:
            print("  ERROR: Rate limited (429)")
            return False

        nonce_match = re.search(r'name="_wpnonce"\s+value="([^"]+)"', editor_html)
        if not nonce_match:
            print("  ERROR: No nonce found in plugin editor")
            print(f"  Response snippet: {editor_html[:500]}")
            return False

        nonce = nonce_match.group(1)
        print(f"  Nonce: {nonce[:10]}...")

        # Submit update
        post_data = urllib.parse.urlencode({
            'newcontent': plugin_content,
            '_wpnonce': nonce,
            '_wp_http_referer': f'/wp-admin/plugin-editor.php?file={PLUGIN_URL_SLUG}&plugin={PLUGIN_URL_SLUG}',
            'action': 'edit-plugin-file-save',
            'file': PLUGIN_SLUG,
            'plugin': PLUGIN_SLUG,
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
                print(f"  PHP error: {re.sub('<[^>]+>', '', err.group(1)).strip()[:300]}")
            else:
                print(f"  Unknown result — response size {len(result_html)} chars")
            return False
        else:
            print(f"  Unknown result — page size {len(result_html)} chars")
            # Look for success indicators
            if 'File edited' in result_html or 'updated=true' in result_html:
                return True
            return False

    except Exception as e:
        print(f"  HTTP error: {e}")
        return False


def deploy_via_rest_api(plugin_content):
    """
    WordPress REST API does not support direct plugin file upload.
    This is a known limitation — custom plugin files cannot be
    deployed via REST API (only wordpress.org slugs work).
    This method is documented for future reference.
    """
    print("\n[METHOD 2] REST API — not supported for custom plugin files")
    print("  WordPress REST API /wp/v2/plugins only works with wordpress.org slugs.")
    print("  Skipping.")
    return False


def deploy_via_playwright(plugin_content):
    """Playwright browser deploy as fallback."""
    print("\n[METHOD 3] Playwright browser deploy...")
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

        # Handle GoDaddy SSO toggle if present
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
        editor_url = (
            f"{BASE_URL}/wp-admin/plugin-editor.php"
            f"?file={PLUGIN_URL_SLUG}&plugin={PLUGIN_URL_SLUG}"
        )
        page.goto(editor_url, wait_until="networkidle", timeout=30000)

        ta = page.locator("#newcontent")
        if ta.count() == 0:
            print("  ERROR: No textarea found in plugin editor")
            browser.close()
            return False

        # Set value via JS (faster for large content)
        page.evaluate(
            "content => { var ta = document.getElementById('newcontent'); if(ta) ta.value = content; }",
            plugin_content
        )
        page.click("[name='submit']")
        page.wait_for_load_state("networkidle")

        success = 'updated' in page.url.lower() or 'File edited' in page.content()
        print(f"  Result: {'SUCCESS' if success else 'uncertain — check manually'}")
        browser.close()
        return success


def verify_live_api():
    """Quick check that the API endpoints respond post-deploy."""
    import json
    tests = [
        ('Dashboard (Jared)', f"{BASE_URL}/wp-json/pb-referral/v1/dashboard?code=JAREDSB0"),
    ]
    for name, url in tests:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
                print(f"  [{name}] HTTP {resp.getcode()} — code: {data.get('referral_code', 'N/A')}")
        except Exception as e:
            print(f"  [{name}] ERROR: {e}")


def main():
    print("=" * 65)
    print("PureBrain Referral Plugin Deploy — v2.0.0 (Phase 2)")
    print("=" * 65)

    if not PLUGIN_FILE.exists():
        print(f"ERROR: Plugin file not found: {PLUGIN_FILE}")
        sys.exit(1)

    plugin_content = PLUGIN_FILE.read_text()
    print(f"\nPlugin file: {PLUGIN_FILE}")
    print(f"Plugin size: {len(plugin_content):,} chars ({len(plugin_content.splitlines())} lines)")

    print("\nValidation checks:")
    valid = verify_plugin_content(plugin_content)
    if not valid:
        print("\nERROR: Validation failed. Fix the plugin before deploying.")
        sys.exit(1)
    print("Validation: PASSED")

    print("\nChecking existing live routes...")
    existing_routes = check_referral_routes()
    if existing_routes:
        print(f"  Live referral routes: {existing_routes}")
    else:
        print("  No pb-referral routes detected yet (may not be deployed or plugin inactive)")

    print("\nDeploying...")
    success = deploy_via_http(plugin_content)
    if not success:
        print("\nMethod 1 failed. Trying Playwright...")
        success = deploy_via_playwright(plugin_content)

    if success:
        print("\n" + "=" * 65)
        print("DEPLOY SUCCESS — v2.0.0")
        print("=" * 65)
        print("\nWaiting 3s for WordPress to settle...")
        time.sleep(3)

        print("\nVerifying live API...")
        verify_live_api()

        print("\nReferral routes check:")
        routes = check_referral_routes()
        if routes:
            print(f"  Routes live: {routes}")
        else:
            print("  Routes not yet visible (may need WP rewrite flush or cache purge)")

        print("\nPhase 2 features now live:")
        print(f"  Dashboard:   {BASE_URL}/wp-json/pb-referral/v1/dashboard?code=JAREDSB0")
        print(f"  Register:    POST {BASE_URL}/wp-json/pb-referral/v1/register")
        print(f"  Convert:     POST {BASE_URL}/wp-json/pb-referral/v1/convert")
        print(f"  Rewards:     {BASE_URL}/wp-json/pb-referral/v1/rewards?code=JAREDSB0")
        print(f"\nShortcodes:")
        print("  [pb_referral_register]  — place on any page for link generation")
        print("  [pb_referral_dashboard] — place on members page for stats")

    else:
        print("\n" + "=" * 65)
        print("ALL DEPLOY METHODS FAILED")
        print("=" * 65)
        print("\nManual deploy instructions:")
        print(f"  1. Go to: {BASE_URL}/wp-admin/plugin-editor.php")
        print(f"  2. Select plugin: PureBrain Referral System > purebrain-referral-system.php")
        print(f"  3. Paste content from: {PLUGIN_FILE}")
        print("  4. Click 'Update File'")
        print("\nOR via SSH/SCP:")
        print("  scp tools/security/purebrain-referral/purebrain-referral-system.php \\")
        print("    user@server:/var/www/html/wp-content/plugins/purebrain-referral/purebrain-referral-system.php")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
