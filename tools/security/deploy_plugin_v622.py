#!/usr/bin/env python3
"""
Deploy purebrain-security-plugin.php v6.2.1 to purebrain.ai.

v6.2.1: HOMEPAGE VIDEO BACKGROUND FIX
- Root cause: body.tt-magic-cursor { background-color:#0a0e1a } applies to homepage
  and blocks the fixed-position video background (z-index:-1) from showing through.
  The pb-magic-cursor-body-override had no transparent override for body.home.
- Fix: adds body.home.tt-magic-cursor + body.page-id-11.tt-magic-cursor with
  background: transparent !important; allowing .video-background to show through.
  Also adds html { background: #080a12 } as dark fallback to prevent white flash.

Author: dept-systems-technology
Date: 2026-03-05
"""

import os
import re
import sys
import time
from pathlib import Path

AETHER_ROOT = Path("/home/jared/projects/AI-CIV/aether")
PLUGIN_FILE = AETHER_ROOT / "tools/security/purebrain-security/purebrain-security.php"
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
        "?file=purebrain-security/purebrain-security.php"
        "&plugin=purebrain-security/purebrain-security.php"
    ),
    "screenshot_deploy": str(SCREENSHOT_DIR / "plugin_v622_purebrain_deploy.png"),
    "screenshot_verify": str(SCREENSHOT_DIR / "plugin_v622_purebrain_verify.png"),
}

TARGET_VERSION = "6.2.2"
TARGET_MARKER  = "body.page-id-689.tt-magic-cursor"


def deploy_via_playwright(site, plugin_content):
    from playwright.sync_api import sync_playwright

    print(f"\n=== Deploying plugin v{TARGET_VERSION} to {site['name']} ===")
    print(f"Plugin file: {PLUGIN_FILE}")
    print(f"Content size: {len(plugin_content):,} chars")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1400, "height": 900})
        page = context.new_page()

        # -- Step 1: Login -------------------------------------------------------
        print(f"\n[1] Logging in to {site['admin_url']}...")
        page.goto(site["login_url"], wait_until="networkidle", timeout=60000)

        # GoDaddy SSO bypass
        sso = page.locator(".wpaas-sso-login-toggle")
        if sso.count() > 0 and sso.is_visible():
            print("  GoDaddy SSO detected — clicking username/password toggle")
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

        # -- Step 2: Plugin Editor -----------------------------------------------
        print(f"\n[2] Opening Plugin Editor...")
        page.goto(site["editor_url"], wait_until="networkidle", timeout=60000)
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
                print(f"  Page: {body[:400]}")
            page.screenshot(path=site["screenshot_deploy"])
            browser.close()
            return False

        # -- Step 3: Set content -------------------------------------------------
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

        # -- Step 4: Save --------------------------------------------------------
        print(f"\n[4] Saving plugin file...")
        submit_btn = page.locator("#submit")
        if submit_btn.count() == 0:
            submit_btn = page.locator("input[type='submit']").first
        submit_btn.click()
        page.wait_for_load_state("networkidle")
        time.sleep(1)

        # -- Step 5: Verify ------------------------------------------------------
        print(f"\n[5] Verifying save result...")
        page.screenshot(path=site["screenshot_deploy"])
        body = page.inner_text("body")

        if "File edited successfully" in body or "updated successfully" in body.lower():
            print(f"  SUCCESS: Plugin file saved.")
            browser.close()
            return True
        elif "Parse error" in body or "syntax error" in body.lower():
            print("  ERROR: PHP parse/syntax error detected. File NOT saved.")
            print(f"  Detail: {body[:400]}")
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
            headers={"User-Agent": "Mozilla/5.0 (PureBrain-Deploy-Verify/6.2.1)"}
        )
        resp = urllib.request.urlopen(req, timeout=20)
        html = resp.read().decode("utf-8", errors="ignore")

        if TARGET_MARKER in html:
            print(f"  VERIFIED: '{TARGET_MARKER}' found in live HTML.")
            return True
        else:
            print(f"  WARNING: '{TARGET_MARKER}' NOT found in live HTML yet.")
            print("  (May be Cloudflare cache — verify in browser shortly)")
            return False
    except Exception as e:
        print(f"  Verification request failed: {e}")
        return False


if __name__ == "__main__":
    if not PLUGIN_FILE.exists():
        print(f"ERROR: Plugin file not found: {PLUGIN_FILE}")
        sys.exit(1)

    plugin_content = PLUGIN_FILE.read_text()

    # Sanity checks
    if TARGET_VERSION not in plugin_content:
        print(f"ERROR: Plugin does not contain version {TARGET_VERSION}. Aborting.")
        sys.exit(1)

    if TARGET_MARKER not in plugin_content:
        print(f"ERROR: Plugin does not contain marker '{TARGET_MARKER}'. Aborting.")
        sys.exit(1)

    if not PUREBRAIN_PASSWORD:
        print("ERROR: PUREBRAIN_WP_PASSWORD not set in .env")
        sys.exit(1)

    print(f"Plugin v{TARGET_VERSION} validated.")
    print(f"  Size: {len(plugin_content):,} chars")
    print(f"  Marker: {TARGET_MARKER} — FOUND")

    success = deploy_via_playwright(SITE, plugin_content)

    print("\n" + "=" * 60)
    if success:
        print(f"DEPLOYMENT: v{TARGET_VERSION} deployed successfully.")
        time.sleep(3)
        verify_live(SITE)
        print(f"\nScreenshot: {SITE['screenshot_deploy']}")
    else:
        print(f"DEPLOYMENT FAILED: v{TARGET_VERSION} was NOT deployed.")
        print("\nManual options:")
        print("  1. WP Admin > Plugins > Plugin Editor > PureBrain Security")
        print(f"     Paste content from: {PLUGIN_FILE}")
        print("  2. WP File Manager > wp-content/plugins/purebrain-security/")
        print("     Edit purebrain-security-plugin.php directly")
        sys.exit(1)
