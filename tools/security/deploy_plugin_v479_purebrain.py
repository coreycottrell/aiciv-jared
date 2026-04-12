#!/usr/bin/env python3
"""
Deploy purebrain-security-plugin v4.7.9 to purebrain.ai.

v4.7.9 FIX: Demo video modal X close button missing on some mobile devices.
Root cause: .video-modal__close uses position:absolute + top:-50px which clips
off-screen when modal content starts near the top of viewport on small devices.
Fix: Plugin injects position:fixed + top:16px/right:16px + visible dark circle
background + 44x44px tap target + z-index:10010.
Pages: 11 (homepage), 689 (pay-test-2), 688 (pay-test-sandbox-2)

Author: dept-systems-technology
Date: 2026-03-01
"""

import os
import re
import sys
import time
from pathlib import Path

AETHER_ROOT = Path("/home/jared/projects/AI-CIV/aether")
PLUGIN_FILE = AETHER_ROOT / "exports/purebrain-security-plugin-v479.php"
SCREENSHOT_DIR = AETHER_ROOT / "exports/screenshots"
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

# --- Credentials -----------------------------------------------------------
env_text = (AETHER_ROOT / ".env").read_text()


def _env(key):
    m = re.search(rf"^{key}='([^']+)'", env_text, re.MULTILINE)
    if m:
        return m.group(1).strip()
    m = re.search(rf"^{key}=([^\n]+)", env_text, re.MULTILINE)
    return m.group(1).strip() if m else ""


PUREBRAIN_PASSWORD = _env("PUREBRAIN_WP_PASSWORD")
PUREBRAIN_APP_PASS = _env("PUREBRAIN_WP_APP_PASSWORD")

SITE = {
    "name":          "purebrain.ai",
    "admin_url":     "https://purebrain.ai/wp-admin",
    "login_url":     "https://purebrain.ai/wp-login.php",
    "user":          "Aether",
    "password":      PUREBRAIN_PASSWORD,
    "app_password":  PUREBRAIN_APP_PASS,
    "editor_url": (
        "https://purebrain.ai/wp-admin/plugin-editor.php"
        "?file=purebrain-security/purebrain-security-plugin.php"
        "&plugin=purebrain-security/purebrain-security-plugin.php"
    ),
    "screenshot_deploy": str(SCREENSHOT_DIR / "plugin_v479_purebrain_deploy.png"),
    "screenshot_verify": str(SCREENSHOT_DIR / "plugin_v479_purebrain_verify.png"),
}

TARGET_VERSION = "4.7.9"
TARGET_MARKER  = "pb-video-modal-close-fix"


def deploy_via_playwright(site, plugin_content):
    from playwright.sync_api import sync_playwright

    print(f"\n=== Deploying plugin v{TARGET_VERSION} to {site['name']} ===")
    print(f"Plugin file: {PLUGIN_FILE}")
    print(f"Content size: {len(plugin_content):,} chars")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1400, "height": 900})
        page = context.new_page()

        # Step 1: Login
        print(f"\n[1] Logging in to {site['admin_url']}...")
        page.goto(site["login_url"], wait_until="networkidle", timeout=60000)

        # GoDaddy SSO bypass
        sso = page.locator(".wpaas-sso-login-toggle")
        if sso.count() > 0 and sso.is_visible():
            print("  GoDaddy SSO detected - clicking username/password toggle")
            sso.click()
            page.wait_for_load_state("networkidle")

        page.locator("#user_login").wait_for(state="visible", timeout=15000)
        page.fill("#user_login", site["user"])
        page.fill("#user_pass", site["password"])
        page.click("#wp-submit")
        page.wait_for_load_state("networkidle")

        if "wp-login.php" in page.url:
            print("  ERROR: Login failed. Check PUREBRAIN_WP_PASSWORD in .env")
            page.screenshot(path=site["screenshot_deploy"])
            browser.close()
            return False

        print("  Login successful.")

        # Step 2: Plugin Editor
        print(f"\n[2] Opening Plugin Editor...")
        page.goto(site["editor_url"], wait_until="networkidle", timeout=30000)
        print(f"  URL: {page.url}")

        has_cm  = page.locator(".CodeMirror").count() > 0
        has_raw = page.locator("#newcontent").count() > 0

        if not has_cm and not has_raw:
            body = page.inner_text("body")
            print("  ERROR: Plugin editor not found.")
            if "higher level of permission" in body:
                print("  REASON: Insufficient permissions.")
            elif "disabled" in body.lower():
                print("  REASON: Plugin editing disabled (DISALLOW_FILE_EDIT).")
            else:
                print(f"  Page excerpt: {body[:400]}")
            page.screenshot(path=site["screenshot_deploy"])
            browser.close()
            return False

        # Step 3: Set content
        print(f"\n[3] Setting plugin content ({len(plugin_content):,} chars)...")

        if has_cm:
            print("  Using CodeMirror editor...")
            page.evaluate(
                "content => { var cm = document.querySelector('.CodeMirror').CodeMirror; cm.setValue(content); }",
                plugin_content
            )
            print("  CodeMirror content set.")
        else:
            print("  Using raw textarea...")
            page.fill("#newcontent", plugin_content)
            print("  Textarea content set.")

        # Step 4: Save
        print(f"\n[4] Saving plugin file...")
        submit_btn = page.locator("#submit")
        if submit_btn.count() == 0:
            submit_btn = page.locator("input[type='submit']").first
        submit_btn.click()
        # Use domcontentloaded — large plugin files cause networkidle to timeout
        try:
            page.wait_for_load_state("domcontentloaded", timeout=60000)
        except Exception:
            pass
        # Give extra time for the PHP to process and page to settle
        time.sleep(5)

        # Step 5: Verify save
        print(f"\n[5] Verifying save result...")
        page.screenshot(path=site["screenshot_deploy"])
        try:
            body = page.inner_text("body")
        except Exception:
            body = ""

        if "File edited successfully" in body or "updated successfully" in body.lower():
            print("  SUCCESS: Plugin file saved.")
            browser.close()
            return True
        elif "Parse error" in body or "syntax error" in body.lower():
            print("  ERROR: PHP parse/syntax error detected. File NOT saved.")
            print(f"  Excerpt: {body[:300]}")
            browser.close()
            return False
        else:
            print(f"  WARNING: Could not confirm save. Checking page text...")
            print(f"  Excerpt: {body[:300]}")
            browser.close()
            return "error" not in body.lower() and "parse" not in body.lower()


def verify_live(site):
    """Fetch homepage and check for the fix CSS marker."""
    import urllib.request

    print(f"\n[VERIFY] Checking live CSS injection on {site['name']}...")
    try:
        req = urllib.request.Request(
            "https://purebrain.ai",
            headers={"User-Agent": "Mozilla/5.0 (PureBrain-Deploy-Verify/4.7.9)"}
        )
        resp = urllib.request.urlopen(req, timeout=20)
        html = resp.read().decode("utf-8", errors="ignore")

        if TARGET_MARKER in html:
            print(f"  VERIFIED: '{TARGET_MARKER}' found in live HTML.")
            if "position: fixed" in html or "position:fixed" in html:
                print("  VERIFIED: position:fixed rule present in response.")
            return True
        else:
            print(f"  WARNING: '{TARGET_MARKER}' NOT found in live HTML yet.")
            print("  (May be Cloudflare cache — wait 30s and check manually)")
            return False
    except Exception as e:
        print(f"  Verification request failed: {e}")
        return False


if __name__ == "__main__":
    # Validate plugin file
    if not PLUGIN_FILE.exists():
        print(f"ERROR: Plugin file not found: {PLUGIN_FILE}")
        sys.exit(1)

    plugin_content = PLUGIN_FILE.read_text()

    # Sanity checks
    if f"Version:     {TARGET_VERSION}" not in plugin_content:
        print(f"ERROR: Plugin does not declare version {TARGET_VERSION}. Aborting.")
        sys.exit(1)

    if TARGET_MARKER not in plugin_content:
        print(f"ERROR: Plugin does not contain marker '{TARGET_MARKER}'. Aborting.")
        sys.exit(1)

    if not PUREBRAIN_PASSWORD:
        print("ERROR: PUREBRAIN_WP_PASSWORD not set in .env")
        sys.exit(1)

    print(f"Plugin v{TARGET_VERSION} validated.")
    print(f"  Source: {PLUGIN_FILE}")
    print(f"  Size: {len(plugin_content):,} chars / {len(plugin_content.splitlines())} lines")
    print(f"  Marker '{TARGET_MARKER}': FOUND")
    print(f"  Fix: position:fixed top:16px right:16px + z-index:10010 + 44px tap target")
    print(f"  Pages: 11 (homepage), 689 (pay-test-2), 688 (pay-test-sandbox-2)")

    success = deploy_via_playwright(SITE, plugin_content)

    print("\n" + "=" * 60)
    if success:
        print(f"DEPLOYMENT: v{TARGET_VERSION} deployed successfully.")
        time.sleep(3)
        verify_live(SITE)
        print(f"\nScreenshot: {SITE['screenshot_deploy']}")
    else:
        print(f"DEPLOYMENT FAILED: v{TARGET_VERSION} was NOT deployed.")
        print("\nManual fallback:")
        print("  WP Admin > Appearance > Editor > purebrain-security-plugin.php")
        print(f"  Paste from: {PLUGIN_FILE}")
        sys.exit(1)
