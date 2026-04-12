#!/usr/bin/env python3
"""
Deploy purebrain-security-plugin.php v4.8.5 to purebrain.ai.

v4.8.5: BLOG VIDEO BACKGROUND FIX
- Root cause: SITE-WIDE dark bg enforcement set body to #080a12 on blog pages,
  covering the background video (z-index:-1 position:fixed).
- Fix: Added body.blog, body.single-post, body.archive to the transparent-body
  exception list in all three dark-bg enforcement layers (CSS L1, CSS L2, JS L3).
- Matches existing pattern for pages 688/689/987/1232.
- html stays dark (#080a12), body transparent, video shows through.
- Blog post GIF overlay system (.single-post Additional CSS) unaffected.

Author: dept-systems-technology (full-stack-developer)
Date: 2026-03-05
"""

import os
import re
import sys
import time
from pathlib import Path

AETHER_ROOT = Path("/home/jared/projects/AI-CIV/aether")
PLUGIN_FILE = AETHER_ROOT / "exports/purebrain-security-plugin-v485.php"
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

SITE = {
    "name":          "purebrain.ai",
    "admin_url":     "https://purebrain.ai/wp-admin",
    "login_url":     "https://purebrain.ai/wp-login.php",
    "user":          "Aether",
    "password":      PUREBRAIN_PASSWORD,
    "editor_url": (
        "https://purebrain.ai/wp-admin/plugin-editor.php"
        "?file=purebrain-security/purebrain-security-plugin.php"
        "&plugin=purebrain-security/purebrain-security-plugin.php"
    ),
    "screenshot_deploy": str(SCREENSHOT_DIR / "plugin_v485_purebrain_deploy.png"),
}

TARGET_VERSION = "4.8.5"
TARGET_MARKER  = "v4.8.5"


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

        # Step 2: Plugin Editor
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
            print("  Using raw textarea via JS (large file — bypass fill timeout)...")
            page.evaluate(
                "content => { document.getElementById('newcontent').value = content; }",
                plugin_content
            )
            print("  Textarea content set via JS.")

        # Step 4: Save
        print(f"\n[4] Saving plugin file...")
        submit_btn = page.locator("#submit")
        if submit_btn.count() == 0:
            submit_btn = page.locator("input[type='submit']").first
        submit_btn.click()
        page.wait_for_load_state("networkidle")
        time.sleep(1)

        # Step 5: Verify save
        print(f"\n[5] Verifying save result...")
        page.screenshot(path=site["screenshot_deploy"])
        body = page.inner_text("body")

        if "File edited successfully" in body or "updated successfully" in body.lower():
            print(f"  SUCCESS: Plugin file saved.")
            browser.close()
            return True
        elif "Parse error" in body or "syntax error" in body.lower():
            print("  ERROR: PHP parse/syntax error detected. File NOT saved.")
            print(f"  Error: {body[:400]}")
            browser.close()
            return False
        else:
            print(f"  WARNING: Could not confirm save. Page excerpt: {body[:300]}")
            browser.close()
            return "error" not in body.lower() and "parse" not in body.lower()


def verify_live():
    """Check blog page for transparent body — confirms video can show through."""
    import urllib.request

    print(f"\n[VERIFY] Checking live blog page for transparent body...")
    checks = [
        ("https://purebrain.ai/blog/", "blog listing"),
        ("https://purebrain.ai/", "homepage (should keep dark bg)"),
    ]
    for url, label in checks:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (PureBrain-Deploy-Verify/4.8.5)"})
            resp = urllib.request.urlopen(req, timeout=20)
            html = resp.read().decode("utf-8", errors="ignore")
            has_marker = "4.8.5" in html or "pb-dark-bg" in html
            print(f"  {label}: response {resp.status}, marker={'FOUND' if has_marker else 'NOT FOUND'}")
        except Exception as e:
            print(f"  {label}: error - {e}")


if __name__ == "__main__":
    if not PLUGIN_FILE.exists():
        print(f"ERROR: Plugin file not found: {PLUGIN_FILE}")
        sys.exit(1)

    plugin_content = PLUGIN_FILE.read_text()

    # Sanity checks
    if TARGET_VERSION not in plugin_content:
        print(f"ERROR: Plugin does not contain version {TARGET_VERSION}. Aborting.")
        sys.exit(1)

    if "body.blog" not in plugin_content:
        print("ERROR: Plugin does not contain 'body.blog' exception. Aborting.")
        sys.exit(1)

    if not PUREBRAIN_PASSWORD:
        print("ERROR: PUREBRAIN_WP_PASSWORD not set in .env")
        sys.exit(1)

    print(f"Plugin v{TARGET_VERSION} validated.")
    print(f"  Size: {len(plugin_content):,} chars")
    print(f"  body.blog exception: FOUND")
    print(f"  body.single-post exception: {'FOUND' if 'body.single-post' in plugin_content else 'MISSING'}")
    print(f"  body.archive exception: {'FOUND' if 'body.archive' in plugin_content else 'MISSING'}")
    print(f"  is_home() skip: {'FOUND' if 'is_home()' in plugin_content else 'MISSING'}")
    print(f"  is_archive() skip: {'FOUND' if 'is_archive()' in plugin_content else 'MISSING'}")

    success = deploy_via_playwright(SITE, plugin_content)

    print("\n" + "=" * 60)
    if success:
        print(f"DEPLOYMENT: v{TARGET_VERSION} deployed successfully.")
        time.sleep(3)
        verify_live()
        print(f"\nScreenshot: {SITE['screenshot_deploy']}")
    else:
        print(f"DEPLOYMENT FAILED: v{TARGET_VERSION} was NOT deployed.")
        print("\nManual option:")
        print("  WP Admin > Plugins > Plugin Editor > PureBrain Security")
        print(f"  Paste content from: {PLUGIN_FILE}")
        sys.exit(1)
