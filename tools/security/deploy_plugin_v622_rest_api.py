#!/usr/bin/env python3
"""
Deploy purebrain-security-plugin.php v6.2.2 via WP REST API (no Playwright needed).

Uses the WP File Manager plugin REST endpoint OR the wp/v2/plugin REST API
to update the plugin file content directly, bypassing browser UI issues.

Strategy:
1. Try WP File Manager API (if WP File Manager plugin is active)
2. Try direct file write via authenticated WP REST API
3. Fall back to Playwright if both fail

Author: cto
Date: 2026-03-05
"""

import re
import sys
import time
import base64
import urllib.request
import urllib.parse
import urllib.error
import json
from pathlib import Path

AETHER_ROOT = Path("/home/jared/projects/AI-CIV/aether")
PLUGIN_FILE = AETHER_ROOT / "tools/security/purebrain-security/purebrain-security-plugin.php"

# --- Credentials -----------------------------------------------------------
env_text = (AETHER_ROOT / ".env").read_text()


def _env(key):
    m = re.search(rf"^{key}='([^']+)'", env_text, re.MULTILINE)
    if m:
        return m.group(1).strip()
    m = re.search(rf"^{key}=([^\n]+)", env_text, re.MULTILINE)
    return m.group(1).strip() if m else ""


WP_USER = "Aether"
WP_APP_PASS = _env("PUREBRAIN_WP_APP_PASSWORD")  # "ZGuh 1W8k WpWM c9iy kqyd buPr"
WP_PASSWORD = _env("PUREBRAIN_WP_PASSWORD")

BASE_URL = "https://purebrain.ai"

TARGET_VERSION = "6.2.2"
TARGET_MARKER  = "body.page-id-689.tt-magic-cursor"

# Build basic auth header with app password
credentials = f"{WP_USER}:{WP_APP_PASS}"
auth_b64 = base64.b64encode(credentials.encode()).decode()
AUTH_HEADER = f"Basic {auth_b64}"


def wp_api_request(path, method="GET", data=None):
    """Make an authenticated WP REST API request."""
    url = f"{BASE_URL}/wp-json{path}"
    headers = {
        "Authorization": AUTH_HEADER,
        "Content-Type": "application/json",
        "User-Agent": "PureBrain-Deploy/6.2.2",
    }

    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return json.loads(resp.read().decode()), resp.getcode()
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        return {"error": str(e), "body": error_body}, e.code
    except Exception as e:
        return {"error": str(e)}, 0


def check_auth():
    """Verify WP REST API auth is working."""
    print("\n[AUTH] Verifying WP REST API authentication...")
    result, code = wp_api_request("/wp/v2/users/me")
    if code == 200:
        print(f"  Auth OK. User: {result.get('name', '?')} (ID: {result.get('id', '?')})")
        return True
    else:
        print(f"  Auth FAILED (HTTP {code}): {result}")
        return False


def try_plugin_editor_api(plugin_content):
    """
    Try deploying via the WP plugin-editor REST endpoint.
    WordPress has a /wp/v2/themes/editor endpoint concept but not plugins natively.
    We use the purebrain custom REST endpoint if available.
    """
    print("\n[METHOD 1] Trying custom plugin update endpoint...")
    result, code = wp_api_request(
        "/purebrain/v1/update-plugin",
        method="POST",
        data={
            "plugin": "purebrain-security/purebrain-security-plugin.php",
            "content": plugin_content
        }
    )
    if code == 200 and result.get("success"):
        print(f"  SUCCESS via custom endpoint.")
        return True
    print(f"  Not available (HTTP {code}) — expected if not implemented.")
    return False


def try_wp_filesystem_via_ajax(plugin_content):
    """
    Try using the WordPress AJAX plugin editor save mechanism directly.
    This mimics what the browser does when clicking 'Update File'.
    """
    import urllib.request, urllib.parse, urllib.error, http.cookiejar

    print("\n[METHOD 2] Trying WP Admin AJAX plugin editor save...")

    # Need cookies from a real login, not app password
    # Build cookie jar
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

    login_url = f"{BASE_URL}/wp-login.php"
    login_data = urllib.parse.urlencode({
        "log": WP_USER,
        "pwd": WP_PASSWORD,
        "wp-submit": "Log In",
        "redirect_to": "/wp-admin/",
        "testcookie": "1"
    }).encode()

    try:
        resp = opener.open(login_url, login_data, timeout=30)
        resp_url = resp.geturl()
        print(f"  Login response URL: {resp_url}")

        if "wp-admin" not in resp_url and "wp-login" in resp_url:
            print("  Login may have failed.")
            return False

        print("  Login successful (redirected to wp-admin).")

        # Get the plugin editor page to extract nonce
        editor_url = (
            f"{BASE_URL}/wp-admin/plugin-editor.php"
            "?file=purebrain-security/purebrain-security-plugin.php"
            "&plugin=purebrain-security/purebrain-security-plugin.php"
        )
        resp = opener.open(editor_url, timeout=30)
        html = resp.read().decode("utf-8", errors="ignore")

        # Extract nonce
        nonce_match = re.search(r'"nonce":"([^"]+)"', html)
        if not nonce_match:
            nonce_match = re.search(r'name="_wpnonce"[^>]+value="([^"]+)"', html)
        if not nonce_match:
            nonce_match = re.search(r"_wpnonce['\"]?\s*:\s*['\"]([^'\"]+)['\"]", html)

        if not nonce_match:
            print("  Could not extract nonce from editor page.")
            return False

        nonce = nonce_match.group(1)
        print(f"  Nonce extracted: {nonce[:10]}...")

        # Post the file content
        post_data = urllib.parse.urlencode({
            "_wpnonce": nonce,
            "newcontent": plugin_content,
            "action": "edit-theme-plugin-file",
            "file": "purebrain-security/purebrain-security-plugin.php",
            "plugin": "purebrain-security/purebrain-security-plugin.php",
            "scrollto": "0",
            "docs-list": "",
        }).encode()

        save_url = f"{BASE_URL}/wp-admin/admin-ajax.php"
        req = urllib.request.Request(
            save_url,
            data=post_data,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": editor_url,
            }
        )
        resp = opener.open(req, timeout=30)
        result = resp.read().decode()
        print(f"  AJAX response: {result[:200]}")

        if '"success":true' in result or "true" == result.strip():
            print("  SUCCESS via AJAX plugin editor.")
            return True

        # Also try the form POST directly to plugin-editor.php
        print("  AJAX returned non-success. Trying direct form POST...")
        post_data2 = urllib.parse.urlencode({
            "_wpnonce": nonce,
            "newcontent": plugin_content,
            "action": "update",
            "file": "purebrain-security/purebrain-security-plugin.php",
            "plugin": "purebrain-security/purebrain-security-plugin.php",
            "scrollto": "0",
            "submit": "Update File",
        }).encode()

        req2 = urllib.request.Request(
            f"{BASE_URL}/wp-admin/plugin-editor.php",
            data=post_data2,
            headers={"Content-Type": "application/x-www-form-urlencoded", "Referer": editor_url}
        )
        resp2 = opener.open(req2, timeout=30)
        result2 = resp2.read().decode("utf-8", errors="ignore")

        if "File edited successfully" in result2 or "updated successfully" in result2.lower():
            print("  SUCCESS via form POST to plugin-editor.php.")
            return True

        print(f"  Form POST result snippet: {result2[1000:1300]}")
        return False

    except Exception as e:
        print(f"  AJAX method error: {e}")
        return False


def verify_live():
    """Check if v6.2.2 marker is live in HTML source."""
    print(f"\n[VERIFY] Checking live site for '{TARGET_MARKER}'...")
    urls = [
        "https://purebrain.ai/blog/",
        "https://purebrain.ai/pay-test-2/",
        "https://purebrain.ai/",
    ]
    found_count = 0
    for url in urls:
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (PureBrain-Deploy-Verify/6.2.2)"}
            )
            resp = urllib.request.urlopen(req, timeout=20)
            html = resp.read().decode("utf-8", errors="ignore")
            if TARGET_MARKER in html:
                print(f"  VERIFIED: {url} — marker found in HTML.")
                found_count += 1
            else:
                print(f"  NOT FOUND: {url} — marker missing (may be cache).")
        except Exception as e:
            print(f"  Error checking {url}: {e}")
    return found_count > 0


if __name__ == "__main__":
    if not PLUGIN_FILE.exists():
        print(f"ERROR: Plugin file not found: {PLUGIN_FILE}")
        sys.exit(1)

    plugin_content = PLUGIN_FILE.read_text()

    if TARGET_VERSION not in plugin_content:
        print(f"ERROR: Plugin does not contain version {TARGET_VERSION}. Aborting.")
        sys.exit(1)

    if TARGET_MARKER not in plugin_content:
        print(f"ERROR: Plugin does not contain marker '{TARGET_MARKER}'. Aborting.")
        sys.exit(1)

    print(f"Plugin v{TARGET_VERSION} validated.")
    print(f"  Size: {len(plugin_content):,} chars")
    print(f"  Marker: '{TARGET_MARKER}' — FOUND")
    print(f"  WP User: {WP_USER}")
    print(f"  App Password: {WP_APP_PASS[:6]}...")

    # Step 1: Verify auth
    if not check_auth():
        print("\nERROR: Authentication failed. Cannot deploy.")
        sys.exit(1)

    # Step 2: Try methods in order
    success = False

    # Method 1: Custom REST endpoint (probably not available)
    if not success:
        success = try_plugin_editor_api(plugin_content)

    # Method 2: Cookie-based AJAX
    if not success:
        success = try_wp_filesystem_via_ajax(plugin_content)

    print("\n" + "=" * 60)
    if success:
        print(f"DEPLOYMENT: v{TARGET_VERSION} deployed successfully.")
        time.sleep(3)
        verify_live()
    else:
        print(f"DEPLOYMENT FAILED via REST/AJAX methods.")
        print("\nFalling back to Playwright deploy script:")
        print(f"  python3 {AETHER_ROOT}/tools/security/deploy_plugin_v622_purebrain.py")
        sys.exit(1)
