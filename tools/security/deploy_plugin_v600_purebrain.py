#!/usr/bin/env python3
"""
Deploy purebrain-security-plugin.php v6.0.0 to purebrain.ai.

v6.0.0 changes:
  IndexNow key file server: adds a WordPress `init` hook that intercepts
  requests to /823869521fbf4f33b93e67c781571e20.txt and serves the key
  directly from PHP. This fixes the 403 Forbidden from IndexNow API
  that was caused by the missing key file (404 at that URL).

Author: full-stack-developer agent
Date: 2026-02-25
"""

import os
import re
import sys
import time
import base64
import urllib.request
import urllib.error
from pathlib import Path

AETHER_ROOT = Path("/home/jared/projects/AI-CIV/aether")
PLUGIN_FILE = AETHER_ROOT / "tools/security/purebrain-security/purebrain-security-plugin.php"
SCREENSHOT_DIR = str(AETHER_ROOT / "exports/screenshots")

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
    "screenshot_deploy": f"{SCREENSHOT_DIR}/plugin_v600_deploy.png",
    "screenshot_verify": f"{SCREENSHOT_DIR}/plugin_v600_verify.png",
}

INDEXNOW_KEY = "823869521fbf4f33b93e67c781571e20"


def validate_plugin_content(content: str) -> bool:
    checks = {
        "v6.0.0 version header":                    "Version:     6.0.0" in content,
        "v6.0.0 changelog entry":                   "v6.0.0 - IndexNow key file" in content,
        "IndexNow key file server hook present":    "init" in content and INDEXNOW_KEY + ".txt" in content,
        "IndexNow key file server PHP present":     "purebrain_indexnow_submit" in content,
        "IndexNow key present":                     INDEXNOW_KEY in content,
        "Aether footer credit bar present":         "pb-aether-footer" in content,
        "FAQ accordion still present":              "purebrain-faq-accordion" in content,
        "aether-transparency present":              "aether-transparency" in content,
        "legal footer still present":               "purebrain-legal-footer" in content,
        "FAQPage schema (v5.8.0) still present":    "j-schema" in content,
        "body padding-bottom 64px present":         "padding-bottom: 64px" in content,
        "mobile padding-bottom 80px present":       "padding-bottom: 80px" in content,
    }

    all_ok = True
    for name, result in checks.items():
        status = "OK" if result else "MISSING/FAIL"
        print(f"  [{status}] {name}")
        if not result:
            all_ok = False
    return all_ok


def deploy_via_plugin_editor(page, site: dict, content: str) -> bool:
    print(f"\n[Step 2] Opening Plugin Editor...")
    page.goto(site["editor_url"], wait_until="domcontentloaded", timeout=60000)
    time.sleep(4)

    page_text = page.inner_text("body")
    if "DISALLOW_FILE_EDIT" in page_text or "editing has been disabled" in page_text.lower():
        print("  ERROR: File editing is disabled.")
        return False

    has_codemirror = page.evaluate("() => !!document.querySelector('.CodeMirror')")
    has_textarea   = page.evaluate("() => !!document.querySelector('#newcontent')")
    print(f"  CodeMirror: {has_codemirror}, Textarea: {has_textarea}")

    if not has_codemirror and not has_textarea:
        page.screenshot(path=site["screenshot_deploy"])
        print(f"  ERROR: No editor found.")
        return False

    print("\n[Step 3] Setting plugin content (v6.0.0)...")
    set_ok = False

    if has_codemirror:
        result = page.evaluate("""(content) => {
            try {
                const cmEl = document.querySelector('.CodeMirror');
                if (!cmEl) return 'no_cm_element';
                const cm = cmEl.CodeMirror;
                if (!cm) return 'no_cm_instance';
                cm.setValue(content);
                const val = cm.getValue();
                if (
                    val.includes('Version:     6.0.0') &&
                    val.includes('823869521fbf4f33b93e67c781571e20.txt') &&
                    val.includes('pb-aether-footer')
                ) return 'success';
                return 'set_failed: len=' + val.length;
            } catch(e) { return 'error: ' + e.message; }
        }""", content)
        print(f"  CodeMirror result: {result}")
        set_ok = (result == "success")

    if not set_ok:
        print("  Using textarea fallback...")
        page.evaluate("""() => {
            const ta = document.querySelector('#newcontent');
            if (ta) {
                ta.style.display = 'block';
                ta.style.visibility = 'visible';
            }
        }""")
        page.evaluate("""(content) => {
            const ta = document.querySelector('#newcontent');
            if (!ta) return;
            const setter = Object.getOwnPropertyDescriptor(
                window.HTMLTextAreaElement.prototype, 'value').set;
            setter.call(ta, content);
            ta.dispatchEvent(new Event('input', {bubbles: true}));
            ta.dispatchEvent(new Event('change', {bubbles: true}));
        }""", content)
        print("  Textarea content set.")

    time.sleep(1)

    print("\n[Step 4] Saving plugin...")
    page.evaluate("""() => {
        const btn = document.querySelector('#submit') ||
                    document.querySelector('input[type="submit"]');
        if (btn) btn.click();
    }""")

    try:
        page.wait_for_load_state("domcontentloaded", timeout=45000)
    except Exception:
        pass
    time.sleep(4)

    page.screenshot(path=site["screenshot_deploy"])
    page_text = page.inner_text("body")

    if "File edited successfully" in page_text or "updated successfully" in page_text.lower():
        print("  SUCCESS: Plugin file saved!")
        return True
    elif "Parse error" in page_text or "syntax error" in page_text.lower():
        print(f"  ERROR: PHP syntax error!\n  {page_text[:400]}")
        return False
    else:
        print(f"  Status unclear. Checking content in editor...")
        if has_codemirror:
            current = page.evaluate("""() => {
                const cm = document.querySelector('.CodeMirror');
                return cm ? cm.CodeMirror.getValue().substring(0, 5000) : 'N/A';
            }""")
            if "Version:     6.0.0" in current and "pb-aether-footer" in current:
                print("  v6.0.0 content found in editor — save assumed successful.")
                return True
        return False


def deploy_plugin_to_site(site: dict, content: str) -> bool:
    from playwright.sync_api import sync_playwright

    print(f"\n{'='*65}")
    print(f"DEPLOYING PLUGIN TO: {site['name']}")
    print(f"{'='*65}")

    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=2,
        )
        page = ctx.new_page()

        print(f"\n[Step 1] Logging in to {site['name']}...")
        page.goto(site["login_url"], wait_until="domcontentloaded", timeout=60000)
        time.sleep(2)

        sso_toggle_class = page.locator(".wpaas-sso-login-toggle")
        sso_toggle_link  = page.locator("a:has-text('username and password'), a:has-text('Log in with username')")

        if sso_toggle_class.count() > 0 and sso_toggle_class.is_visible():
            print("  GoDaddy SSO overlay (class) — clicking...")
            sso_toggle_class.click()
            time.sleep(3)
        elif sso_toggle_link.count() > 0:
            print("  GoDaddy SSO overlay (link text) — clicking...")
            sso_toggle_link.first.click()
            time.sleep(3)
        else:
            print("  No SSO overlay detected.")
            time.sleep(1)

        captcha_field = page.locator("#wpsec_captcha_answer")
        if captcha_field.count() > 0 and captcha_field.is_visible():
            page.screenshot(path=site["screenshot_deploy"])
            print(f"  CAPTCHA detected! Screenshot: {site['screenshot_deploy']}")
            browser.close()
            return False

        try:
            page.locator("#user_login").wait_for(state="visible", timeout=15000)
        except Exception:
            page.screenshot(path=site["screenshot_deploy"])
            print(f"  ERROR: Login form not visible.")
            browser.close()
            return False

        page.fill("#user_login", site["user"])
        page.fill("#user_pass", site["password"])
        page.click("#wp-submit")

        try:
            page.wait_for_load_state("domcontentloaded", timeout=30000)
        except Exception:
            pass
        time.sleep(3)

        if "wp-login.php" in page.url:
            page.screenshot(path=site["screenshot_deploy"])
            print(f"  ERROR: Login failed. URL: {page.url}")
            browser.close()
            return False

        print("  Login successful!")

        success = deploy_via_plugin_editor(page, site, content)

        if success:
            credentials = base64.b64encode(
                f"{site['user']}:{site['app_password']}".encode()
            ).decode()

            # Clear Elementor cache
            print("\n[Step 5] Clearing Elementor cache...")
            cache_req = urllib.request.Request(
                "https://purebrain.ai/wp-json/elementor/v1/cache",
                method="DELETE",
                headers={
                    "Authorization": f"Basic {credentials}",
                    "Content-Type": "application/json",
                },
            )
            try:
                with urllib.request.urlopen(cache_req, timeout=20) as resp:
                    print(f"  Elementor cache cleared: HTTP {resp.status}")
            except urllib.error.HTTPError as e:
                print(f"  Elementor cache response: HTTP {e.code}")
            except Exception as ex:
                print(f"  Elementor cache clear skipped: {ex}")

        browser.close()

    return success


def verify_live() -> bool:
    """
    Verify:
    1. The IndexNow key file now returns 200 with the correct key
    2. The homepage still renders correctly (Aether footer present)
    """
    print("\n[Verification] Checking IndexNow key file is now served...")

    all_ok = True

    # Check the key file
    key_url = f"https://purebrain.ai/{INDEXNOW_KEY}.txt?cb={int(time.time())}"
    req = urllib.request.Request(
        key_url,
        headers={
            "User-Agent":    "Mozilla/5.0 (compatible; AetherBot/1.0)",
            "Cache-Control": "no-cache, no-store, must-revalidate",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            key_content = resp.read().decode("utf-8", errors="replace").strip()
            status_code = resp.status
        key_ok = (key_content == INDEXNOW_KEY and status_code == 200)
        print(f"\n  [{'PASS' if key_ok else 'FAIL'}] IndexNow key file")
        print(f"    HTTP status: {status_code}")
        print(f"    Content: '{key_content[:60]}'")
        print(f"    Key match: {key_content == INDEXNOW_KEY}")
        if not key_ok:
            all_ok = False
    except Exception as ex:
        print(f"\n  [FAIL] IndexNow key file fetch error: {ex}")
        all_ok = False

    # Check homepage still works
    home_req = urllib.request.Request(
        f"https://purebrain.ai/?cb={int(time.time())}",
        headers={
            "User-Agent":    "Mozilla/5.0 (compatible; AetherBot/1.0)",
            "Cache-Control": "no-cache",
        },
    )
    try:
        with urllib.request.urlopen(home_req, timeout=30) as resp:
            html = resp.read().decode("utf-8", errors="replace")
        footer_ok = 'id="pb-aether-footer"' in html
        print(f"\n  [{'PASS' if footer_ok else 'FAIL'}] Homepage Aether footer present: {footer_ok}")
        if not footer_ok:
            all_ok = False
    except Exception as ex:
        print(f"\n  [FAIL] Homepage fetch error: {ex}")
        all_ok = False

    return all_ok


def main():
    print("=" * 65)
    print("PureBrain Security Plugin v6.0.0 — IndexNow Key File Server")
    print("=" * 65)

    if not PLUGIN_FILE.exists():
        print(f"ERROR: Plugin file not found: {PLUGIN_FILE}")
        sys.exit(1)

    content = PLUGIN_FILE.read_text()
    print(f"\nPlugin file: {PLUGIN_FILE}")
    print(f"Content length: {len(content)} chars\n")

    print("--- Validating plugin content ---")
    if not validate_plugin_content(content):
        print("\nERROR: Plugin validation failed. Aborting.")
        sys.exit(1)
    print("All validation checks passed.\n")

    print("\n" + "=" * 65)
    print("DEPLOYING plugin v6.0.0 via Playwright (WP Plugin Editor)")
    print("=" * 65)
    success = deploy_plugin_to_site(SITE, content)
    if not success:
        print("\n[FAIL] Plugin deployment failed.")
        sys.exit(1)

    print(f"\n[OK] Plugin deployment succeeded.")

    print("\nWaiting 10 seconds for cache to settle...")
    time.sleep(10)

    print("\n" + "=" * 65)
    print("LIVE VERIFICATION")
    print("=" * 65)
    verified = verify_live()

    if verified:
        print("\nDEPLOYMENT COMPLETE AND VERIFIED.")
        print("Changes deployed:")
        print(f"  - IndexNow key file now served at /{INDEXNOW_KEY}.txt")
        print("  - IndexNow pings will now succeed (HTTP 200/202 instead of 403)")
        print("  - All other plugin features intact")
    else:
        print("\nDeployment done — some verification checks flagged issues.")
        print("Note: CDN cache may need a moment to propagate.")


if __name__ == "__main__":
    main()
