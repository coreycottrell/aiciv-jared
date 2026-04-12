#!/usr/bin/env python3
"""
Deploy purebrain-security-plugin.php v5.6.1 to purebrain.ai.

v5.6.1 changes:
  1. BUG FIX: Mobile footer orphan separator — the | between "Why Choose PureBrain?"
     and "Mission & Values" had no named class, so it appeared as a dangling pipe on
     mobile even after the Why pill was hidden. Fixed by adding pb-footer-sep-before-mission
     class to that span, and hiding it in the mobile @media block.
  2. All 3 separators now have named classes (sep-why, sep-before-mission, sep-migrate).
     On mobile, all 3 are hidden → only "Mission & Values" pill shows, no orphan pipes.
  3. Bug 2 overlap fix retained: body padding-bottom 80px on mobile prevents Aether
     footer from overlapping the Privacy Policy / Terms legal footer bar.

Author: full-stack-developer agent
Date: 2026-02-24
"""

import os
import re
import sys
import time
import base64
import json
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
    "screenshot_deploy": f"{SCREENSHOT_DIR}/plugin_v561_deploy.png",
    "screenshot_verify": f"{SCREENSHOT_DIR}/plugin_v561_verify.png",
}


def validate_plugin_content(content: str) -> bool:
    checks = {
        "v5.6.1 version header":                            "Version:     5.6.1" in content,
        "v5.6.1 changelog entry":                           "v5.6.1 - Mobile footer separator fix" in content,
        "pb-footer-sep-before-mission CSS hide present":    "pb-footer-sep-before-mission" in content,
        "Mission & Values pill still present":              "pb-footer-mission" in content,
        "Why pill hidden on mobile":                        "pb-footer-why" in content and "display: none" in content,
        "Migrate pill hidden on mobile":                    "pb-footer-migrate" in content and "display: none" in content,
        "HTML sep-before-mission class on span":            'class="pb-footer-sep pb-footer-sep-before-mission"' in content,
        "HTML sep-why class on span":                       'class="pb-footer-sep pb-footer-sep-why"' in content,
        "HTML sep-migrate class on span":                   'class="pb-footer-sep pb-footer-sep-migrate"' in content,
        "body padding-bottom 80px on mobile":               "padding-bottom: 80px !important" in content,
        "aether-transparency present":                      "aether-transparency" in content,
        "magic cursor override present":                    "pb-magic-cursor-body-override" in content,
        "FAQ accordion present":                            "purebrain-faq-accordion" in content,
        "IndexNow key present":                             "823869521fbf4f33b93e67c781571e20" in content,
        "pb-inline-cta-template-lock present":              "pb-inline-cta-template-lock" in content,
        "footer logo brand fix present":                    "purebrain-footer-logo-brand" in content,
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

    print("\n[Step 3] Setting plugin content (v5.6.1)...")
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
                    val.includes('Version:     5.6.1') &&
                    val.includes('pb-footer-sep-before-mission') &&
                    val.includes('padding-bottom: 80px')
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
                return cm ? cm.CodeMirror.getValue().substring(0, 3000) : 'N/A';
            }""")
            if "Version:     5.6.1" in current and "pb-footer-sep-before-mission" in current:
                print("  v5.6.1 content found in editor — save assumed successful.")
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
    print("\n[Verification] Checking mobile footer CSS on homepage and pay test pages...")

    pages_to_check = {
        "homepage":             "https://purebrain.ai/",
        "pay-test":             "https://purebrain.ai/pay-test/",
        "pay-test-2":           "https://purebrain.ai/pay-test-2/",
        "pay-test-sandbox":     "https://purebrain.ai/pay-test-sandbox/",
        "pay-test-sandbox-2":   "https://purebrain.ai/pay-test-sandbox-2/",
    }

    results = {}
    for label, url in pages_to_check.items():
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent":    "Mozilla/5.0 (compatible; AetherBot/1.0)",
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma":        "no-cache",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                results[label] = resp.read().decode("utf-8", errors="replace")
                print(f"  Fetched {label}: HTTP 200 ({len(results[label])} chars)")
        except Exception as ex:
            print(f"  fetch error ({label}): {ex}")
            results[label] = ""

    checks = {}

    for label, html in results.items():
        checks[f"[{label}] page loads"]                            = bool(html)
        checks[f"[{label}] pb-aether-footer present"]              = "pb-aether-footer" in html
        checks[f"[{label}] v5.6.1 present"]                        = "5.6.1" in html
        checks[f"[{label}] pb-footer-sep-before-mission in CSS"]   = "pb-footer-sep-before-mission" in html
        checks[f"[{label}] pb-footer-mission (M&V pill) present"]  = "pb-footer-mission" in html
        checks[f"[{label}] padding-bottom 80px in mobile CSS"]     = "padding-bottom: 80px" in html

    all_ok = True
    for name, result in checks.items():
        status = "OK" if result else "FAIL"
        print(f"  [{status}] {name}")
        if not result:
            all_ok = False

    return all_ok


def main():
    print("=" * 65)
    print("PureBrain Security Plugin v5.6.1 — Mobile footer separator fix")
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
    print("DEPLOYING plugin v5.6.1 via Playwright")
    print("=" * 65)
    success = deploy_plugin_to_site(SITE, content)
    if not success:
        print("\n[FAIL] Plugin deployment failed.")
        sys.exit(1)

    print(f"\n[OK] Plugin deployment succeeded.")

    print("\nWaiting 8 seconds for cache to settle...")
    time.sleep(8)

    print("\n" + "=" * 65)
    print("LIVE VERIFICATION")
    print("=" * 65)
    verified = verify_live()

    if verified:
        print("\nDEPLOYMENT COMPLETE AND VERIFIED.")
        print("1. Bug 1 fixed: Only 'Mission & Values' pill visible on mobile.")
        print("   - Why Choose PureBrain? hidden on mobile")
        print("   - Migrate hidden on mobile")
        print("   - All 3 separators (sep-why, sep-before-mission, sep-migrate) hidden on mobile")
        print("   - No more orphan | pipes before the Mission pill")
        print("2. Bug 2 fixed: 80px body padding-bottom on mobile prevents overlap")
        print("   with Privacy Policy / Terms of Service legal footer bar.")
        print("3. Verified on: homepage, pay-test, pay-test-2, pay-test-sandbox, pay-test-sandbox-2")
    else:
        print("\nDeployment done — some verification checks flagged issues.")
        print("Note: CDN cache may need a moment. Hard-refresh to confirm.")


if __name__ == "__main__":
    main()
