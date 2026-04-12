#!/usr/bin/env python3
"""
Deploy PureBrain Security Plugin v4.6.7 - MINIMAL REQUEST VERSION
Forces IPv4. Only 3 HTTP requests: login, get nonce, submit.
"""

import sys
import re
import socket
import time
import requests

# Force IPv4 for purebrain.ai
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
WP_PASSWORD = "NW2u!JLQ3!Bt$XD$7CWzz5Z@"
WP_APP_PASSWORD = "FlFr2VOtlHiHaJWjzW96OHUJ"
PLUGIN_SLUG = "purebrain-security/purebrain-security-plugin.php"

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"

def main():
    print("=" * 60)
    print("Plugin v4.6.7 Deployment - MINIMAL (3 requests)")
    print("=" * 60)

    # Verify IPv4
    resolved = socket.getaddrinfo("purebrain.ai", 443)
    ip = resolved[0][4][0]
    print(f"Resolved to IPv4: {ip}")

    # Read plugin
    with open(PLUGIN_FILE, "r") as f:
        plugin_content = f.read()
    assert "Version:     4.6.7" in plugin_content, "Wrong version!"
    print(f"Plugin file: {len(plugin_content)} chars, v4.6.7 confirmed")

    session = requests.Session()

    # REQUEST 1: Login page (get CF cookies + test cookie)
    print("\n[1/3] Getting login page...")
    r1 = session.get(
        f"{WP_BASE}/wp-login.php",
        headers={"User-Agent": UA},
        timeout=20
    )
    print(f"    Status: {r1.status_code}")
    if r1.status_code != 200:
        print(f"    BLOCKED: {r1.status_code}")
        sys.exit(1)
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

    wp_cookies = [k for k in session.cookies.keys() if "wordpress_logged" in k.lower()]
    print(f"    Auth cookies: {wp_cookies}")

    if len(r2.text) < 10000:
        print(f"    ERROR: Got small page ({len(r2.text)} chars). Preview: {r2.text[:200]}")
        sys.exit(1)

    if "plugin-editor" not in r2.url.lower() and "wp-admin" not in r2.url.lower():
        print(f"    ERROR: Not in wp-admin. At: {r2.url}")
        sys.exit(1)

    # Extract the form nonce from the editor page
    content = r2.text
    nonce_match = re.search(r'<input[^>]+id="nonce"[^>]+value="([^"]+)"', content, re.IGNORECASE)
    if not nonce_match:
        # Try alternate pattern
        nonce_match = re.search(r'name="nonce"[^>]+value="([^"]+)"|value="([^"]+)"[^>]+name="nonce"', content, re.IGNORECASE)

    if nonce_match:
        nonce = nonce_match.group(1) or nonce_match.group(2)
        print(f"    Nonce (form hidden input): {nonce}")
    else:
        # Fall back to JSON nonce
        json_nonce = re.search(r'"nonce"\s*:\s*"([a-f0-9]+)"', content)
        nonce = json_nonce.group(1) if json_nonce else None
        print(f"    Nonce (JSON fallback): {nonce}")

    if not nonce:
        print("    ERROR: No nonce found! Cannot submit.")
        with open("/tmp/editor_debug.html", "w") as f:
            f.write(content)
        print("    Editor page saved to /tmp/editor_debug.html")
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

    # Save response
    with open("/tmp/plugin_submit_v2.html", "w") as f:
        f.write(r3.text)

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
            if ver_in_response.group(1) == "4.6.7":
                print("    v4.6.7 found in response textarea!")
                success = True

        # Check for error
        if "syntax error" in response_text.lower() or "parse error" in response_text.lower():
            err = re.search(r'(parse error|syntax error)[^<]*', response_text, re.IGNORECASE)
            print(f"    PHP ERROR: {err.group(0) if err else 'unknown'}")
            success = False

    # Verify via REST API
    print("\n--- REST API Verification ---")
    import base64
    creds = base64.b64encode(f"Aether:{WP_APP_PASSWORD}".encode()).decode()

    time.sleep(3)
    rv = requests.get(
        f"{WP_BASE}/wp-json/wp/v2/plugins/purebrain-security/purebrain-security-plugin",
        headers={"Authorization": f"Basic {creds}", "Cache-Control": "no-cache"},
        timeout=15
    )
    rest_data = rv.json()
    version = rest_data.get("version", "unknown")
    print(f"REST API version: {version}")
    version_ok = (version == "4.6.7")

    print("\n" + "=" * 60)
    if version_ok:
        print("DEPLOYMENT SUCCESSFUL - v4.6.7 CONFIRMED LIVE!")
        print("  Brain video background will now be visible again.")
    elif success:
        print("FILE SUBMITTED - Response indicated success")
        print(f"  REST API shows: {version} (may need cache clear)")
    else:
        print("DEPLOYMENT STATUS UNCLEAR")
        print("  Check /tmp/plugin_submit_v2.html for details")
    print("=" * 60)

    return version_ok or success


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1)
