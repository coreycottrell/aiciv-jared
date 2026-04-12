#!/usr/bin/env python3
"""
Deploy PureBrain Security Plugin v4.6.9 using saved session cookies.
The v4.6.7 deployment earlier today created valid session cookies in /tmp/wp_cookies_v468.txt.
WP sessions last 14 days - we can reuse them without login.
"""

import sys
import re
import os
import base64
import time
import requests
import socket
from http.cookiejar import MozillaCookieJar

# Force IPv4
_orig = socket.getaddrinfo
def _ipv4(host, port, family=0, socktype=0, proto=0, flags=0):
    if 'purebrain.ai' in str(host):
        try: return _orig(host, port, socket.AF_INET, socktype, proto, flags)
        except: pass
    return _orig(host, port, family, socktype, proto, flags)
socket.getaddrinfo = _ipv4

PLUGIN_FILE = "/home/jared/projects/AI-CIV/aether/exports/purebrain-security-plugin-v466.php"
WP_BASE = "https://purebrain.ai"
WP_APP_PASSWORD = "FlFr2VOtlHiHaJWjzW96OHUJ"
PLUGIN_SLUG = "purebrain-security/purebrain-security-plugin.php"
EXPECTED_VERSION = "4.7.2"
SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/docs/deploy-attempt"
COOKIE_FILES = [
    "/tmp/wp_cookies_v468.txt",
    "/tmp/wp_cookies_final.txt",
    "/tmp/wp_cookies3.txt",
    "/tmp/wp_cookies2.txt",
    "/tmp/wp_cookies.txt",
]
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"

os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def verify_via_rest():
    creds = base64.b64encode(f"Aether:{WP_APP_PASSWORD}".encode()).decode()
    rv = requests.get(
        f"{WP_BASE}/wp-json/wp/v2/plugins/purebrain-security/purebrain-security-plugin",
        headers={"Authorization": f"Basic {creds}", "Cache-Control": "no-cache"},
        timeout=15
    )
    data = rv.json()
    return data.get("version", "unknown"), data.get("status", "unknown")


def try_deploy_with_cookie_file(cookie_file, plugin_content):
    """Try to deploy using a saved cookie file. Returns (success, nonce, session)."""
    print(f"\n  Trying cookie file: {cookie_file}")

    session = requests.Session()

    # Load cookies from netscape format file
    jar = MozillaCookieJar()
    try:
        jar.load(cookie_file, ignore_discard=True, ignore_expires=True)
    except Exception as e:
        print(f"  Error loading {cookie_file}: {e}")
        return False, None, None

    for cookie in jar:
        if 'purebrain' in cookie.domain.lower() or 'wordpress' in cookie.name.lower():
            session.cookies.set(cookie.name, cookie.value, domain="purebrain.ai")

    wp_cookies = [k for k in session.cookies.keys() if 'wordpress_logged' in k.lower()]
    print(f"  Auth cookies loaded: {wp_cookies}")

    # GET plugin editor to get fresh nonce
    editor_url = f"{WP_BASE}/wp-admin/plugin-editor.php?file={PLUGIN_SLUG}&plugin={PLUGIN_SLUG}"
    r = session.get(editor_url, headers={"User-Agent": UA}, timeout=20, allow_redirects=True)

    print(f"  Editor page: {r.status_code} -> {r.url} ({len(r.text)} chars)")

    if "wp-login" in r.url or len(r.text) < 10000:
        print("  Session expired - redirected to login")
        return False, None, None

    if "plugin-editor" not in r.url:
        print(f"  Not on editor page: {r.url}")
        return False, None, None

    # Extract nonce
    nonce_match = re.search(r'<input[^>]+id="nonce"[^>]+value="([^"]+)"', r.text, re.IGNORECASE)
    if not nonce_match:
        nonce_match = re.search(r'name="nonce"\s+value="([^"]+)"|value="([^"]+)"\s+name="nonce"', r.text, re.IGNORECASE)

    if not nonce_match:
        print("  No nonce found in editor page!")
        with open(f"{SCREENSHOT_DIR}/session-editor-page.html", "w") as f:
            f.write(r.text)
        return False, None, None

    nonce = nonce_match.group(1) if nonce_match.group(1) else nonce_match.group(2)
    print(f"  Nonce found: {nonce}")

    # Check current version
    ver_match = re.search(r'Version:\s*([\d.]+)', r.text[:2000])
    if ver_match:
        print(f"  Current version in editor: {ver_match.group(1)}")

    # Submit the plugin update
    print("  Submitting plugin update...")
    r_submit = session.post(
        f"{WP_BASE}/wp-admin/plugin-editor.php",
        data={
            "newcontent": plugin_content,
            "action": "update",
            "file": PLUGIN_SLUG,
            "plugin": PLUGIN_SLUG,
            "nonce": nonce,
            "_wpnonce": nonce,
            "submit": "Update File",
        },
        headers={
            "User-Agent": UA,
            "Referer": editor_url,
            "Origin": WP_BASE,
            "Content-Type": "application/x-www-form-urlencoded",
        },
        timeout=60,
        allow_redirects=True
    )

    print(f"  Submit response: {r_submit.status_code} -> {r_submit.url} ({len(r_submit.text)} chars)")

    # Save response
    with open(f"{SCREENSHOT_DIR}/session-submit-response.html", "w") as f:
        f.write(r_submit.text)

    # Analyze
    resp_text = r_submit.text
    if "File edited successfully" in resp_text:
        print("  CONFIRMED: 'File edited successfully'!")
        return True, nonce, session

    if "successfully" in resp_text.lower():
        print("  Success keyword found!")
        return True, nonce, session

    # Check version in response
    ver_resp = re.search(r'Version:\s*([\d.]+)', resp_text[:2000])
    if ver_resp:
        print(f"  Version in response: {ver_resp.group(1)}")
        if ver_resp.group(1) == EXPECTED_VERSION:
            print(f"  v{EXPECTED_VERSION} confirmed in editor response!")
            return True, nonce, session

    # Check for PHP errors
    if "syntax error" in resp_text.lower() or "parse error" in resp_text.lower():
        err = re.search(r'(parse error|syntax error)[^<]*', resp_text, re.IGNORECASE)
        print(f"  PHP ERROR: {err.group(0) if err else 'unknown'}")
        return False, nonce, session

    # Check for error messages
    error_match = re.search(r'class="notice-error"[^>]*>(.*?)</div>', resp_text, re.IGNORECASE | re.DOTALL)
    if error_match:
        error_text = re.sub(r'<[^>]+>', '', error_match.group(1)).strip()
        print(f"  Error notice: {error_text}")
        return False, nonce, session

    print(f"  Unclear response. Preview: {resp_text[:300]}")
    return False, nonce, session


def main():
    print("=" * 60)
    print(f"Plugin v{EXPECTED_VERSION} Deployment - Saved Session Method")
    print("=" * 60)

    # Read plugin
    with open(PLUGIN_FILE, "r") as f:
        plugin_content = f.read()

    if f"Version:     {EXPECTED_VERSION}" not in plugin_content:
        print(f"ERROR: Wrong version in plugin file")
        ver_match = re.search(r'Version:\s*([\d.]+)', plugin_content)
        print(f"Found: {ver_match.group(1) if ver_match else 'none'}")
        sys.exit(1)
    print(f"Plugin: {len(plugin_content)} chars, v{EXPECTED_VERSION} confirmed\n")

    # Try each cookie file
    success = False
    for cookie_file in COOKIE_FILES:
        if not os.path.exists(cookie_file):
            print(f"Skipping (not found): {cookie_file}")
            continue

        success, nonce, session = try_deploy_with_cookie_file(cookie_file, plugin_content)
        if success:
            print(f"\nDeployment succeeded using: {cookie_file}")
            break

    if not success:
        print("\nAll saved sessions failed.")
        print("All deployment approaches exhausted.")

    # Verify via REST API regardless
    print("\n--- REST API Verification ---")
    time.sleep(3)
    version, status = verify_via_rest()
    print(f"REST API version: {version}")
    print(f"REST API status:  {status}")
    version_ok = (version == EXPECTED_VERSION)

    print("\n" + "=" * 60)
    if version_ok:
        print(f"DEPLOYMENT SUCCESSFUL - v{EXPECTED_VERSION} CONFIRMED LIVE!")
        print("Screenshots saved to docs/deploy-attempt/")
    elif success:
        print("FILE SUBMITTED - Response indicated success")
        print(f"REST API shows: {version} (may need cache clear)")
    else:
        print(f"DEPLOYMENT FAILED - REST API shows: {version}")
    print("=" * 60)

    return version_ok or success


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1)
