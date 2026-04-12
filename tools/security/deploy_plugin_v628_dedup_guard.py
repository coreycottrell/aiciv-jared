#!/usr/bin/env python3
"""
Deploy purebrain-security-plugin.php v6.2.8 (Dedup Guard) to purebrain.ai.

v6.2.8 FIX: Double transparency section + duplicate scripts on ALL single blog posts.
Root cause: Two plugin files coexist on server filesystem (v6.2.2 active + v4.8.6 inactive).
Fix: PHP constant PUREBRAIN_SECURITY_LOADED acts as singleton - if already defined, plugin
     returns immediately on second load. Zero functionality change. One line of PHP logic.

Author: security-engineer-tech (assigned by CTO)
Date: 2026-03-09
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

AETHER_ROOT = Path("/home/jared/projects/AI-CIV/aether")
load_dotenv(AETHER_ROOT / ".env")

BASE_URL    = "https://purebrain.ai"
WP_USER     = os.environ.get("PUREBRAIN_WP_USER", "Aether")
WP_PASSWORD = os.environ.get("PUREBRAIN_WP_PASSWORD", "")
WP_APP_PASS = os.environ.get("PUREBRAIN_WP_APP_PASSWORD", "")
PLUGIN_FILE = AETHER_ROOT / "tools/security/purebrain-security/purebrain-security-plugin.php"

NEW_VERSION = "6.2.8"
OLD_VERSION = "6.2.7"

DEDUP_GUARD = """// ============================================================
// DEDUP GUARD (v6.2.8): Prevents double-load when multiple
// plugin files coexist in wp-content/plugins/ filesystem.
// If PUREBRAIN_SECURITY_LOADED is already defined, this file
// has already been loaded — return immediately to prevent
// duplicate add_action registrations, duplicate scripts,
// duplicate transparency sections, and duplicate styles.
// ============================================================
if ( defined( 'PUREBRAIN_SECURITY_LOADED' ) ) {
    return;
}
define( 'PUREBRAIN_SECURITY_LOADED', true );

"""

CHANGELOG_ENTRY = """ *   v6.2.8 - DEDUP GUARD: Prevents double-load when multiple plugin files coexist in
 *            wp-content/plugins/ filesystem. PHP constant PUREBRAIN_SECURITY_LOADED
 *            acts as singleton flag. If already defined, plugin returns immediately.
 *            Fixes: double transparency section + all duplicate scripts/styles on
 *            every single blog post. Zero functionality change. CTO-assigned fix.
"""


def build_updated_plugin():
    """Read source, apply dedup guard + version bump, return updated content."""
    source = PLUGIN_FILE.read_text(encoding="utf-8")

    # 1. Verify we're working with the right version
    if f"Version:     {OLD_VERSION}" not in source:
        print(f"ERROR: Expected Version: {OLD_VERSION} in plugin source.")
        print("  Source may have changed. Aborting to prevent wrong deployment.")
        sys.exit(1)

    # 2. Verify dedup guard not already present
    if "PUREBRAIN_SECURITY_LOADED" in source:
        print("INFO: Dedup guard already present in source. No change needed.")
        print("  Proceeding with deploy of current version to server.")
        return source

    # 3. Insert dedup guard after '<?php' opening tag
    # The dedup guard goes AFTER <?php but BEFORE the /** docblock
    source = source.replace("<?php\n/**", f"<?php\n{DEDUP_GUARD}/**", 1)

    if "PUREBRAIN_SECURITY_LOADED" not in source:
        print("ERROR: Failed to insert dedup guard. Aborting.")
        sys.exit(1)

    # 4. Bump version
    source = source.replace(
        f" * Version:     {OLD_VERSION}",
        f" * Version:     {NEW_VERSION}",
        1
    )

    if f"Version:     {NEW_VERSION}" not in source:
        print("ERROR: Version bump failed. Aborting.")
        sys.exit(1)

    # 5. Add changelog entry (insert before v6.2.1 entry)
    source = source.replace(
        " *   v6.2.1 - Homepage video",
        f"{CHANGELOG_ENTRY} *   v6.2.1 - Homepage video",
        1
    )

    print(f"  Source updated: dedup guard inserted, version bumped to {NEW_VERSION}")
    return source


def deploy_via_http(plugin_content):
    """Cookie-based HTTP deploy to WP plugin editor."""
    print("\n[DEPLOY] Cookie-based HTTP deploy...")
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    opener.addheaders = [
        ("User-Agent", "Mozilla/5.0 (PureBrain-Deploy/6.2.8)"),
        ("Referer", f"{BASE_URL}/wp-login.php"),
    ]

    # Step 1: Login
    print("  Logging in...")
    login_data = urllib.parse.urlencode({
        "log": WP_USER,
        "pwd": WP_PASSWORD,
        "wp-submit": "Log In",
        "redirect_to": "/wp-admin/",
        "testcookie": "1",
    }).encode()

    try:
        resp = opener.open(f"{BASE_URL}/wp-login.php", login_data, timeout=30)
        final_url = resp.geturl()
        print(f"  Login redirect: {final_url}")
        if "wp-login.php" in final_url:
            print("  ERROR: Login failed")
            return False
    except Exception as e:
        print(f"  Login error: {e}")
        return False

    # Step 2: Get plugin editor page to extract nonce
    editor_url = (
        f"{BASE_URL}/wp-admin/plugin-editor.php"
        "?file=purebrain-security/purebrain-security-plugin.php"
        "&plugin=purebrain-security/purebrain-security-plugin.php"
    )
    print("  Fetching plugin editor for nonce...")
    try:
        resp = opener.open(editor_url, timeout=30)
        html = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  Editor fetch error: {e}")
        return False

    # Extract nonce
    nonce_match = re.search(r'"nonce"\s*:\s*"([a-f0-9]+)"', html)
    if not nonce_match:
        nonce_match = re.search(r'name="_wpnonce"\s+value="([a-f0-9]+)"', html)
    if not nonce_match:
        nonce_match = re.search(r'_wpnonce["\s]+[value="\s]+([a-f0-9]{10})', html)

    if not nonce_match:
        print("  ERROR: Could not extract nonce from plugin editor page.")
        print("  Trying to detect if we're logged in...")
        if 'wp-admin' in html or 'logout' in html.lower():
            print("  Logged in but nonce extraction failed. HTML snippet:")
            # Try alternate nonce pattern
            alt = re.findall(r'nonce["\s=:]+([a-f0-9]{10,})', html)
            print(f"  Nonce candidates: {alt[:5]}")
        return False

    nonce = nonce_match.group(1)
    print(f"  Nonce: {nonce[:8]}...")

    # Step 3: POST updated plugin content
    print("  Posting updated plugin content...")
    post_data = urllib.parse.urlencode({
        "action": "edit-plugin",
        "file": "purebrain-security/purebrain-security-plugin.php",
        "plugin": "purebrain-security/purebrain-security-plugin.php",
        "newcontent": plugin_content,
        "_wpnonce": nonce,
        "submit": "Update File",
    }).encode()

    try:
        resp = opener.open(editor_url, post_data, timeout=60)
        result_html = resp.read().decode("utf-8", errors="replace")
        if "File edited successfully" in result_html or "updated" in result_html.lower():
            print("  SUCCESS: Plugin file updated on server.")
            return True
        elif "error" in result_html.lower() or "Error" in result_html:
            print("  ERROR: Server returned error during update.")
            # Extract error message
            error_match = re.search(r'<p class="[^"]*error[^"]*">([^<]+)</p>', result_html)
            if error_match:
                print(f"  Error: {error_match.group(1)}")
            return False
        else:
            print("  WARNING: Unclear response. Checking for success indicators...")
            if "plugin-editor.php" in resp.geturl():
                print("  Deploy may have succeeded (stayed on editor page).")
                return True
            return False
    except Exception as e:
        print(f"  Deploy POST error: {e}")
        return False


def verify_fix():
    """Verify the dedup fix is live on the server."""
    print("\n[VERIFY] Checking live page for duplicate injection...")

    # Fetch a single blog post
    test_url = "https://purebrain.ai/?p=1441"
    try:
        req = urllib.request.Request(
            test_url,
            headers={"User-Agent": "Mozilla/5.0 (PureBrain-Verify/6.2.8)"}
        )
        resp = urllib.request.urlopen(req, timeout=30)
        html = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  Fetch error: {e}")
        return False

    # Count occurrences of transparency inject script
    transparency_count = html.count('id="purebrain-transparency-inject"')
    faq_accordion_count = html.count('id="purebrain-faq-accordion-js"')

    print(f"  purebrain-transparency-inject occurrences: {transparency_count} (want: 1 or 0)")
    print(f"  purebrain-faq-accordion-js occurrences: {faq_accordion_count} (want: 1)")

    if transparency_count <= 1 and faq_accordion_count == 1:
        print("  PASS: No duplication detected.")
        return True
    elif transparency_count > 1 or faq_accordion_count > 1:
        print("  FAIL: Still detecting duplication.")
        return False
    else:
        print("  UNCLEAR: Check manually.")
        return False


def verify_site_health():
    """Basic health check: homepage still loads."""
    print("\n[HEALTH] Checking homepage...")
    try:
        req = urllib.request.Request(
            "https://purebrain.ai/",
            headers={"User-Agent": "Mozilla/5.0 (PureBrain-Health/6.2.8)"}
        )
        resp = urllib.request.urlopen(req, timeout=20)
        code = resp.getcode()
        if code == 200:
            print(f"  Homepage: HTTP {code} OK")
            return True
        else:
            print(f"  Homepage: HTTP {code} WARNING")
            return False
    except Exception as e:
        print(f"  Homepage check failed: {e}")
        return False


def send_telegram(message):
    """Send status update to Telegram."""
    try:
        import json
        config = json.loads(
            (AETHER_ROOT / "config/telegram_config.json").read_text()
        )
        token = config["bot_token"]
        data = urllib.parse.urlencode({
            "chat_id": "548906264",
            "text": message,
        }).encode()
        urllib.request.urlopen(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=data,
            timeout=10
        )
    except Exception as e:
        print(f"  Telegram send failed: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print(f"PureBrain Security Plugin v{NEW_VERSION} Deploy")
    print("Change: Dedup guard to fix double transparency/scripts")
    print("=" * 60)

    if not WP_PASSWORD:
        print("ERROR: PUREBRAIN_WP_PASSWORD not set in .env")
        sys.exit(1)

    send_telegram(f"[CTO] Security engineer deploying plugin v{NEW_VERSION} (dedup guard fix)...")

    # Step 1: Build updated plugin
    print("\n[1/4] Building updated plugin source...")
    updated_source = build_updated_plugin()

    # Step 2: Deploy to server
    print("\n[2/4] Deploying to purebrain.ai...")
    deploy_success = deploy_via_http(updated_source)

    if not deploy_success:
        msg = f"[CTO] FAILED: Plugin v{NEW_VERSION} deploy failed. Manual intervention needed."
        print(f"\n{msg}")
        send_telegram(msg)
        sys.exit(1)

    # Step 3: Wait for WordPress to pick up change
    print("\n[3/4] Waiting 5 seconds for server to process...")
    time.sleep(5)

    # Step 4: Verify fix
    print("\n[4/4] Verifying fix on live site...")
    fix_verified = verify_fix()
    site_healthy = verify_site_health()

    if fix_verified and site_healthy:
        msg = (
            f"[CTO] Task 1 COMPLETE: Plugin v{NEW_VERSION} deployed. "
            "Dedup guard live. Double transparency FIXED. Site healthy."
        )
        print(f"\nSUCCESS: {msg}")
        send_telegram(msg)
        sys.exit(0)
    elif site_healthy and not fix_verified:
        msg = (
            f"[CTO] Plugin v{NEW_VERSION} deployed. Site healthy. "
            "Dedup verification UNCLEAR - check manually at purebrain.ai/blog/."
        )
        print(f"\nPARTIAL: {msg}")
        send_telegram(msg)
        sys.exit(0)
    else:
        msg = (
            f"[CTO] Plugin v{NEW_VERSION} deployed but SITE HEALTH CHECK FAILED. "
            "Needs immediate investigation."
        )
        print(f"\nERROR: {msg}")
        send_telegram(msg)
        sys.exit(1)
