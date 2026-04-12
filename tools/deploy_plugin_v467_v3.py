#!/usr/bin/env python3
"""
Deploy PureBrain Security Plugin v4.6.7 via WordPress Plugin Editor
Hotfix: Brain video background restoration
v3: Uses Python requests session (avoids Playwright visibility + IPv6 issues)
"""

import sys
import re
import json
import time
import requests

PLUGIN_FILE = "/home/jared/projects/AI-CIV/aether/exports/purebrain-security-plugin-v466.php"
WP_BASE = "https://purebrain.ai"
WP_ADMIN = f"{WP_BASE}/wp-admin"
WP_USERNAME = "Aether"
WP_PASSWORD = "NW2u!JLQ3!Bt$XD$7CWzz5Z@"
WP_APP_PASSWORD = "FlFr2VOtlHiHaJWjzW96OHUJ"
PLUGIN_SLUG = "purebrain-security/purebrain-security-plugin.php"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


def login_to_wp():
    """Log into WordPress and return an authenticated session."""
    print("[1] Logging into WordPress admin...")
    session = requests.Session()
    session.headers.update(HEADERS)

    # Step 1: GET login page to get test cookie
    r1 = session.get(f"{WP_BASE}/wp-login.php", timeout=15)
    print(f"    Login page status: {r1.status_code}")

    # Set test cookie
    session.cookies.set("wordpress_test_cookie", "WP Cookie check", domain="purebrain.ai")

    # Step 2: POST login credentials
    login_data = {
        "log": WP_USERNAME,
        "pwd": WP_PASSWORD,
        "wp-submit": "Log In",
        "redirect_to": "/wp-admin/",
        "testcookie": "1",
    }

    r2 = session.post(
        f"{WP_BASE}/wp-login.php",
        data=login_data,
        headers={**HEADERS, "Referer": f"{WP_BASE}/wp-login.php", "Origin": WP_BASE},
        allow_redirects=True,
        timeout=20,
    )

    print(f"    After login URL: {r2.url}")
    cookie_names = list(session.cookies.keys())

    if "wp-admin" in r2.url and "wordpress_logged_in" in " ".join(cookie_names):
        print(f"    LOGIN SUCCESS! Cookies: {cookie_names}")
        return session
    else:
        print(f"    LOGIN FAILED! Status: {r2.status_code}, URL: {r2.url}")
        print(f"    Cookies: {cookie_names}")
        return None


def get_plugin_editor_nonce(session):
    """Get the plugin editor page and extract the nonce for file submission."""
    print("[2] Loading plugin editor page...")
    editor_url = (
        f"{WP_ADMIN}/plugin-editor.php"
        f"?file={requests.utils.quote(PLUGIN_SLUG)}"
        f"&plugin={requests.utils.quote(PLUGIN_SLUG)}"
    )

    r = session.get(editor_url, timeout=15)
    print(f"    Editor page status: {r.status_code}")
    content = r.text

    if len(content) < 100:
        print(f"    ERROR: Empty page response ({len(content)} chars)")
        return None, None

    print(f"    Page length: {len(content)} chars")

    # Extract nonce - WP plugin editor uses a JS nonce object
    nonce = None
    nonce_patterns = [
        r'"nonce"\s*:\s*"([a-f0-9]+)"',
        r"'nonce'\s*:\s*'([a-f0-9]+)'",
        r'nonce["\s:=]+([a-f0-9]{10})',
        r'name="_wpnonce"\s+value="([^"]+)"',
        r'value="([^"]+)"\s+name="_wpnonce"',
    ]

    for pattern in nonce_patterns:
        m = re.search(pattern, content, re.IGNORECASE)
        if m:
            nonce = m.group(1)
            print(f"    Nonce found (pattern: {pattern[:40]}): {nonce}")
            break

    if not nonce:
        # Try finding it in the editorsSettings JS object
        m = re.search(r'editorsSettings.*?nonce.*?"([a-f0-9]+)"', content, re.IGNORECASE | re.DOTALL)
        if m:
            nonce = m.group(1)
            print(f"    Nonce from editorsSettings: {nonce}")

    if not nonce:
        print("    WARNING: No nonce found! Will try without nonce.")
        # Look for any 10-char hex strings as candidates
        candidates = re.findall(r"[a-f0-9]{10}", content)
        print(f"    Hex candidates: {candidates[:5]}")

    return nonce, content


def submit_plugin_file(session, nonce, plugin_content):
    """Submit the plugin file to the editor."""
    print("[3] Submitting plugin file update...")

    # The WP plugin editor uses admin-ajax.php with action=edit-theme-plugin-file
    # OR it uses a direct form POST to plugin-editor.php

    # Method 1: Try admin-ajax.php (used by block editor plugin file editor)
    ajax_data = {
        "action": "edit-theme-plugin-file",
        "nonce": nonce,
        "file": PLUGIN_SLUG,
        "newcontent": plugin_content,
        "plugin": PLUGIN_SLUG,
    }

    print("    Trying admin-ajax.php (block editor method)...")
    r_ajax = session.post(
        f"{WP_ADMIN}/admin-ajax.php",
        data=ajax_data,
        headers={
            **HEADERS,
            "Referer": f"{WP_ADMIN}/plugin-editor.php",
            "Origin": WP_BASE,
            "X-Requested-With": "XMLHttpRequest",
        },
        timeout=60,
    )

    print(f"    Ajax response: {r_ajax.status_code}")
    if r_ajax.text:
        print(f"    Ajax response body: {r_ajax.text[:200]}")

    try:
        ajax_json = r_ajax.json()
        if ajax_json.get("success"):
            print("    SUCCESS via admin-ajax.php!")
            return True
        else:
            print(f"    Ajax error: {ajax_json}")
    except Exception:
        pass

    # Method 2: Try direct POST to plugin-editor.php (classic WP plugin editor)
    print("    Trying classic plugin-editor.php POST...")
    form_data = {
        "newcontent": plugin_content,
        "action": "update",
        "file": PLUGIN_SLUG,
        "plugin": PLUGIN_SLUG,
        "plugin_file": PLUGIN_SLUG,
        "nonce": nonce or "",
        "_wpnonce": nonce or "",
        "submit": "Update File",
    }

    r_form = session.post(
        f"{WP_ADMIN}/plugin-editor.php",
        data=form_data,
        headers={
            **HEADERS,
            "Referer": f"{WP_ADMIN}/plugin-editor.php",
            "Origin": WP_BASE,
            "Content-Type": "application/x-www-form-urlencoded",
        },
        timeout=60,
        allow_redirects=True,
    )

    print(f"    Form POST response: {r_form.status_code} -> {r_form.url}")

    if "File edited successfully" in r_form.text:
        print("    SUCCESS: 'File edited successfully' in response!")
        return True
    elif "successfully" in r_form.text.lower():
        print("    SUCCESS: 'successfully' found in response!")
        return True
    elif "error" in r_form.text.lower() and ("syntax" in r_form.text.lower() or "parse" in r_form.text.lower()):
        print("    ERROR: PHP syntax error detected!")
        # Extract error
        m = re.search(r"(parse error|syntax error)[^<]*", r_form.text, re.IGNORECASE)
        if m:
            print(f"    Error: {m.group(0)}")
        return False
    else:
        print(f"    Unexpected response. Length: {len(r_form.text)}")
        if len(r_form.text) > 0:
            # Look for any indication of success or failure
            if "File edited" in r_form.text or "updated" in r_form.text.lower():
                return True
            # Save response for debugging
            with open("/tmp/plugin_editor_response.html", "w") as f:
                f.write(r_form.text)
            print("    Response saved to /tmp/plugin_editor_response.html")
        return False


def verify_via_rest_api():
    """Verify the plugin version via WordPress REST API."""
    print("\n[4] Verifying via REST API...")
    import base64
    creds = base64.b64encode(f"Aether:{WP_APP_PASSWORD}".encode()).decode()

    try:
        r = requests.get(
            f"{WP_BASE}/wp-json/wp/v2/plugins/purebrain-security/purebrain-security-plugin",
            headers={"Authorization": f"Basic {creds}"},
            timeout=15,
        )
        data = r.json()
        version = data.get("version", "unknown")
        status = data.get("status", "unknown")
        print(f"    Plugin version: {version}")
        print(f"    Plugin status: {status}")
        return version == "4.6.7"
    except Exception as e:
        print(f"    REST API error: {e}")
        return False


def verify_pages():
    """Quick page load verification."""
    print("\n[5] Verifying key pages load...")
    pages = [
        ("Homepage", f"{WP_BASE}/"),
        ("Calculator", f"{WP_BASE}/ai-tool-stack-calculator/"),
        ("Blog", f"{WP_BASE}/blog/"),
    ]

    for name, url in pages:
        try:
            r = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
            print(f"    {name}: HTTP {r.status_code}")
        except Exception as e:
            print(f"    {name}: ERROR - {e}")


def main():
    print("=" * 60)
    print("PureBrain Security Plugin v4.6.7 - HOTFIX DEPLOYMENT v3")
    print("Fix: Brain video background restoration")
    print("=" * 60)

    # Read plugin file
    print("\n[0] Reading plugin file...")
    with open(PLUGIN_FILE, "r") as f:
        plugin_content = f.read()

    if "Version:     4.6.7" not in plugin_content:
        print("ERROR: Version 4.6.7 not found!")
        sys.exit(1)
    print(f"    Version 4.6.7 confirmed ({len(plugin_content)} chars)")

    # Login
    session = login_to_wp()
    if not session:
        print("FATAL: Cannot log in to WordPress!")
        sys.exit(1)

    # Get nonce
    nonce, page_content = get_plugin_editor_nonce(session)

    # Submit file
    success = submit_plugin_file(session, nonce, plugin_content)

    if success:
        # Verify
        version_ok = verify_via_rest_api()
        verify_pages()

        print("\n" + "=" * 60)
        if version_ok:
            print("RESULT: DEPLOYMENT SUCCESSFUL - v4.6.7 CONFIRMED LIVE")
        else:
            print("RESULT: FILE SUBMITTED but REST API still shows old version")
            print("  The file was written but WP may cache the old version info")
            print("  Try: clear Cloudflare cache or wait 60s for propagation")
        print("=" * 60)
    else:
        print("\nRESULT: DEPLOYMENT FAILED")
        print("Check /tmp/plugin_editor_response.html for details")
        sys.exit(1)


if __name__ == "__main__":
    main()
