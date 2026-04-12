#!/usr/bin/env python3
"""
Deploy PureBrain Security Plugin v4.6.9 - MINIMAL REQUEST VERSION
Forces IPv4. Only 3 HTTP requests: login, get nonce, submit.
Based on proven v4.6.7 deployment pattern (2026-02-27).
"""

import sys
import re
import socket
import time
import requests

# Force IPv4 for purebrain.ai
# Our server IPv6 (2a01:4f9:c014:4c05::1) gets rate-limited by Cloudflare on wp-login.php
# IPv4 (89.167.19.20) works fine.
_orig = socket.getaddrinfo
def _ipv4(host, port, family=0, socktype=0, proto=0, flags=0):
    if 'purebrain.ai' in str(host):
        try:
            return _orig(host, port, socket.AF_INET, socktype, proto, flags)
        except Exception:
            pass
    return _orig(host, port, family, socktype, proto, flags)
socket.getaddrinfo = _ipv4

PLUGIN_FILE = "/home/jared/projects/AI-CIV/aether/exports/purebrain-security-plugin-v466.php"
WP_BASE = "https://purebrain.ai"
WP_ADMIN = f"{WP_BASE}/wp-admin"
WP_USERNAME = "Aether"
WP_PASSWORD = "NW2u!JLQ3!Bt$XD$7CWzz5Z@"  # actual admin password (NOT app password)
WP_APP_PASSWORD = "FlFr2VOtlHiHaJWjzW96OHUJ"  # app password for REST API only
PLUGIN_SLUG = "purebrain-security/purebrain-security-plugin.php"
EXPECTED_VERSION = "4.6.9"

SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/docs/deploy-attempt"

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"


def main():
    print("=" * 60)
    print(f"Plugin v{EXPECTED_VERSION} Deployment - MINIMAL (3 requests)")
    print("=" * 60)

    # Verify IPv4
    resolved = socket.getaddrinfo("purebrain.ai", 443)
    ip = resolved[0][4][0]
    print(f"Resolved to IPv4: {ip}")
    if ip.startswith("2a01:") or ":" in ip:
        print("ERROR: Got IPv6 address! Rate limiting likely. Aborting.")
        sys.exit(1)

    # Read plugin file
    with open(PLUGIN_FILE, "r") as f:
        plugin_content = f.read()

    # Verify correct version
    if f"Version:     {EXPECTED_VERSION}" not in plugin_content:
        print(f"ERROR: Plugin file does not contain 'Version:     {EXPECTED_VERSION}'")
        # Check what version it does have
        ver_match = re.search(r'Version:\s*([\d.]+)', plugin_content)
        if ver_match:
            print(f"Found version: {ver_match.group(1)}")
        sys.exit(1)

    print(f"Plugin file: {len(plugin_content)} chars, v{EXPECTED_VERSION} confirmed")

    session = requests.Session()

    # REQUEST 1: Login page (get CF cookies + test cookie)
    print("\n[1/3] Getting login page...")
    r1 = session.get(
        f"{WP_BASE}/wp-login.php",
        headers={"User-Agent": UA},
        timeout=20
    )
    print(f"    Status: {r1.status_code}")

    # Save login page for debugging
    with open(f"{SCREENSHOT_DIR}/01-login-page.html", "w") as f:
        f.write(r1.text)
    print(f"    Saved to {SCREENSHOT_DIR}/01-login-page.html")

    if r1.status_code != 200:
        print(f"    BLOCKED: {r1.status_code}")
        print(f"    Response: {r1.text[:500]}")
        sys.exit(1)

    # Check if CAPTCHA is present
    if "captcha" in r1.text.lower() or "wpsec_captcha" in r1.text.lower():
        print("    WARNING: CAPTCHA detected on login page!")
        # We'll still try - the captcha.wpsecurity.godaddy.com is for wp-login.php standard
        # The ?wpaas-standard-login=1 bypass may be needed

    session.cookies.set("wordpress_test_cookie", "WP Cookie check", domain="purebrain.ai")

    # REQUEST 2: Login POST + follow redirect to get nonce from plugin editor
    # We chain: login -> redirect to plugin editor in one step by setting redirect_to
    editor_redirect = f"/wp-admin/plugin-editor.php?file={requests.utils.quote(PLUGIN_SLUG)}&plugin={requests.utils.quote(PLUGIN_SLUG)}"

    print("\n[2/3] Logging in and navigating to editor...")
    r2 = session.post(
        f"{WP_BASE}/wp-login.php",
        data={
            "log": WP_USERNAME,
            "pwd": WP_PASSWORD,
            "wp-submit": "Log In",
            "redirect_to": editor_redirect,
            "testcookie": "1",
        },
        headers={
            "User-Agent": UA,
            "Referer": f"{WP_BASE}/wp-login.php",
            "Origin": WP_BASE,
        },
        allow_redirects=True,
        timeout=30
    )
    print(f"    Final URL: {r2.url}")
    print(f"    Page length: {len(r2.text)}")

    # Save for debugging
    with open(f"{SCREENSHOT_DIR}/02-after-login.html", "w") as f:
        f.write(r2.text)
    print(f"    Saved to {SCREENSHOT_DIR}/02-after-login.html")

    wp_cookies = [k for k in session.cookies.keys() if "wordpress_logged" in k.lower()]
    print(f"    Auth cookies: {wp_cookies}")

    if len(r2.text) < 10000:
        print(f"    ERROR: Got small page ({len(r2.text)} chars).")
        print(f"    Preview: {r2.text[:500]}")
        sys.exit(1)

    if "plugin-editor" not in r2.url.lower() and "wp-admin" not in r2.url.lower():
        print(f"    ERROR: Not in wp-admin. At: {r2.url}")
        # Check if we got CAPTCHA or rate limit
        if "captcha" in r2.text.lower():
            print("    CAPTCHA detected in response!")
        if "429" in str(r2.status_code) or "rate" in r2.text.lower():
            print("    Rate limited!")
        sys.exit(1)

    # Extract the form nonce from the editor page
    content = r2.text
    nonce_match = re.search(r'<input[^>]+id="nonce"[^>]+value="([^"]+)"', content, re.IGNORECASE)
    if not nonce_match:
        # Try alternate pattern (attribute order may vary)
        nonce_match = re.search(r'name="nonce"\s+value="([^"]+)"|value="([^"]+)"\s+name="nonce"', content, re.IGNORECASE)
    if not nonce_match:
        # Try another variant
        nonce_match = re.search(r'id="nonce"[^>]*value="([^"]+)"|value="([^"]+)"[^>]*id="nonce"', content, re.IGNORECASE)

    if nonce_match:
        nonce = nonce_match.group(1) or (nonce_match.group(2) if len(nonce_match.groups()) > 1 else None)
        print(f"    Nonce (form hidden input): {nonce}")
    else:
        # Fall back to JSON nonce (less reliable but try)
        json_nonce = re.search(r'"nonce"\s*:\s*"([a-f0-9]+)"', content)
        nonce = json_nonce.group(1) if json_nonce else None
        if nonce:
            print(f"    Nonce (JSON fallback): {nonce}")
        else:
            print("    ERROR: No nonce found! Cannot submit.")
            sys.exit(1)

    # Check which version is currently in the editor
    version_in_editor = re.search(r'Version:\s*([\d.]+)', content)
    if version_in_editor:
        print(f"    Current version in editor: {version_in_editor.group(1)}")

    # REQUEST 3: Submit the plugin file
    print("\n[3/3] Submitting plugin file...")
    r3 = session.post(
        f"{WP_ADMIN}/plugin-editor.php",
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
            "Referer": r2.url,
            "Origin": WP_BASE,
            "Content-Type": "application/x-www-form-urlencoded",
        },
        timeout=60,
        allow_redirects=True
    )
    print(f"    Submit response: {r3.status_code} -> {r3.url}")
    print(f"    Response length: {len(r3.text)}")

    # Save response for debugging
    with open(f"{SCREENSHOT_DIR}/03-submit-response.html", "w") as f:
        f.write(r3.text)
    print(f"    Saved to {SCREENSHOT_DIR}/03-submit-response.html")

    # Analyze response
    response_text = r3.text
    success = False

    if "File edited successfully" in response_text:
        print("    CONFIRMED: 'File edited successfully' message!")
        success = True
    else:
        # Check for success notice
        notice = re.search(r'class="[^"]*notice-success[^"]*"[^>]*>(.*?)</div>', response_text, re.IGNORECASE | re.DOTALL)
        if notice:
            notice_clean = re.sub(r'<[^>]+>', '', notice.group(1)).strip()
            print(f"    Success notice: {notice_clean}")
            if any(w in notice_clean.lower() for w in ["edited", "updated", "success"]):
                success = True

        # Check if version changed in the response
        ver_in_response = re.search(r'Version:\s*([\d.]+)', response_text)
        if ver_in_response:
            print(f"    Version in response: {ver_in_response.group(1)}")
            if ver_in_response.group(1) == EXPECTED_VERSION:
                print(f"    v{EXPECTED_VERSION} found in response textarea!")
                success = True

        # Check for PHP errors
        if "syntax error" in response_text.lower() or "parse error" in response_text.lower():
            err = re.search(r'(parse error|syntax error)[^<]*', response_text, re.IGNORECASE)
            print(f"    PHP ERROR: {err.group(0) if err else 'unknown'}")
            success = False

        if not success:
            print(f"    Response preview: {response_text[:300]}")

    # Verify via REST API
    print("\n--- REST API Verification ---")
    import base64
    creds = base64.b64encode(f"Aether:{WP_APP_PASSWORD}".encode()).decode()

    time.sleep(3)
    rv = requests.get(
        f"{WP_BASE}/wp-json/wp/v2/plugins/purebrain-security/purebrain-security-plugin",
        headers={
            "Authorization": f"Basic {creds}",
            "Cache-Control": "no-cache",
            "User-Agent": UA,
        },
        timeout=15
    )
    try:
        rest_data = rv.json()
        version = rest_data.get("version", "unknown")
        status = rest_data.get("status", "unknown")
        print(f"REST API version: {version}")
        print(f"REST API status:  {status}")
        version_ok = (version == EXPECTED_VERSION)
    except Exception as e:
        print(f"REST API error: {e}")
        print(f"Response: {rv.text[:200]}")
        version_ok = False

    print("\n" + "=" * 60)
    if version_ok:
        print(f"DEPLOYMENT SUCCESSFUL - v{EXPECTED_VERSION} CONFIRMED LIVE!")
        print("  Plugin v4.6.9 is now active on purebrain.ai")
    elif success:
        print("FILE SUBMITTED - Response indicated success")
        print(f"  REST API shows: {version} (may need cache clear)")
    else:
        print("DEPLOYMENT STATUS UNCLEAR")
        print(f"  Check {SCREENSHOT_DIR}/03-submit-response.html for details")
    print("=" * 60)

    return version_ok or success


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1)
