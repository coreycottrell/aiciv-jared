#!/usr/bin/env python3
"""
Deploy PureBrain Security Plugin v4.6.5 — Calculator page 777 dark background nuclear fix.

3-layer approach:
Layer 1: wp_head priority 1 (fires FIRST) - CSS in <head> before anything
Layer 2: wp_head priority 999 (fires LAST) - CSS in <head> after everything
Layer 3: JS at DOMContentLoaded + load event - inline style override

Author: dept-systems-technology (ST#)
Date: 2026-02-27
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
PLUGIN_SOURCE = AETHER_ROOT / "exports/purebrain-security-plugin-v465.php"

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
    "name":      "purebrain.ai",
    "login_url": "https://purebrain.ai/wp-login.php",
    "user":      "Aether",
    "password":  PUREBRAIN_PASSWORD,
    "app_password": PUREBRAIN_APP_PASS,
    "editor_url": (
        "https://purebrain.ai/wp-admin/plugin-editor.php"
        "?file=purebrain-security/purebrain-security-plugin.php"
        "&plugin=purebrain-security/purebrain-security-plugin.php"
    ),
}


def validate_plugin_content(content: str) -> bool:
    checks = {
        "Version 4.6.5":                   "Version:     4.6.5" in content,
        "Layer 1 CSS injected":            "pb-calc-dark-bg-layer1" in content,
        "Layer 2 CSS injected":            "pb-calc-dark-bg-layer2" in content,
        "Layer 3 JS injected":             "pb-calc-dark-bg-js" in content,
        "applyDarkBg function":            "applyDarkBg" in content,
        "is_page(777) check":              "is_page( 777 )" in content,
        "Dark bg color correct":           "#080a12" in content,
        "CSP 89.167.19.20 still present":  "https://89.167.19.20:8443;" in content,
        "Core: Aether footer":             "pb-aether-footer" in content,
        "Core: FAQ accordion":             "purebrain-faq-accordion" in content,
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
        print("  ERROR: No editor found.")
        return False

    print("\n[Step 3] Setting plugin content (v4.6.5 - dark bg nuclear fix)...")
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
                    val.includes('Version:     4.6.5') &&
                    val.includes('pb-calc-dark-bg-layer1') &&
                    val.includes('pb-calc-dark-bg-layer2') &&
                    val.includes('pb-calc-dark-bg-js') &&
                    val.includes('applyDarkBg') &&
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

    page_text = page.inner_text("body")

    if "File edited successfully" in page_text or "updated successfully" in page_text.lower():
        print("  SUCCESS: Plugin file saved!")
        return True
    elif "Parse error" in page_text or "syntax error" in page_text.lower():
        print(f"  ERROR: PHP syntax error!\n  {page_text[:400]}")
        return False
    else:
        print("  Status unclear. Checking content in editor...")
        if has_codemirror:
            current = page.evaluate("""() => {
                const cm = document.querySelector('.CodeMirror');
                return cm ? cm.CodeMirror.getValue().substring(0, 5000) : 'N/A';
            }""")
            if ("Version:     4.6.5" in current and
                    "pb-calc-dark-bg-layer1" in current):
                print("  v4.6.5 markers found in editor — save assumed successful.")
                return True
        return False


def deploy_plugin_to_site(site: dict, content: str) -> bool:
    from playwright.sync_api import sync_playwright

    print(f"\n{'='*65}")
    print(f"DEPLOYING PLUGIN TO: {site['name']}")
    print(f"{'='*65}")

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
            print("  CAPTCHA detected! Cannot proceed.")
            browser.close()
            return False

        try:
            page.locator("#user_login").wait_for(state="visible", timeout=15000)
        except Exception:
            print("  ERROR: Login form not visible.")
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
            print(f"  ERROR: Login failed. URL: {page.url}")
            browser.close()
            return False

        print("  Login successful!")

        success = deploy_via_plugin_editor(page, site, content)

        if success:
            credentials = base64.b64encode(
                f"{site['user']}:{site['app_password']}".encode()
            ).decode()

            print("\n[Step 5] Clearing Elementor cache...")
            cache_req = urllib.request.Request(
                "https://purebrain.ai/wp-json/elementor/v1/cache",
                method="DELETE",
                headers={
                    "Authorization": f"Basic {credentials}",
                    "Content-Type":  "application/json",
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
    import urllib.request
    import ssl

    print("\n[Verification] Checking live page 777 for dark bg fix markers...")
    ctx_ssl = ssl.create_default_context()
    req = urllib.request.Request(
        "https://purebrain.ai/ai-tool-stack-calculator/",
        headers={
            "User-Agent":    "Mozilla/5.0 (compatible; AetherBot/1.0)",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma":        "no-cache",
        }
    )
    with urllib.request.urlopen(req, context=ctx_ssl, timeout=30) as resp:
        body = resp.read().decode("utf-8", errors="replace")

    checks = {
        "Layer1 CSS present":    "pb-calc-dark-bg-layer1" in body,
        "Layer2 CSS present":    "pb-calc-dark-bg-layer2" in body,
        "Layer3 JS present":     "pb-calc-dark-bg-js" in body,
        "applyDarkBg function":  "applyDarkBg" in body,
        "#080a12 bg present":    "#080a12" in body,
        "v4.6.5 NOT in page":    "Version:     4.6.5" not in body,  # Plugin version shouldn't appear in page output
    }

    all_ok = True
    for name, result in checks.items():
        status = "PASS" if result else "FAIL"
        print(f"  [{status}] {name}")
        if not result and name != "v4.6.5 NOT in page":
            all_ok = False

    # Also check cache status header
    import http.client
    conn = http.client.HTTPSConnection("purebrain.ai", context=ctx_ssl, timeout=20)
    conn.request("HEAD", "/ai-tool-stack-calculator/", headers={
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    })
    resp = conn.getresponse()
    hdrs = dict(resp.getheaders())
    conn.close()
    cf_cache = hdrs.get("cf-cache-status") or hdrs.get("Cf-Cache-Status") or "unknown"
    print(f"  Cloudflare cache status: {cf_cache}")

    return all_ok


def main():
    print("=" * 65)
    print("PureBrain Security Plugin v4.6.5 — Dark BG Nuclear Fix")
    print("=" * 65)
    print("\nFix: 3-layer approach ensures page-777 shows dark (#080a12) background")
    print("Layer 1: wp_head priority 1 CSS")
    print("Layer 2: wp_head priority 999 CSS")
    print("Layer 3: JS setProperty on DOMContentLoaded + load + 500ms/1500ms delays")

    if not PLUGIN_SOURCE.exists():
        print(f"ERROR: Plugin file not found: {PLUGIN_SOURCE}")
        sys.exit(1)

    content = PLUGIN_SOURCE.read_text()
    print(f"\nPlugin file: {PLUGIN_SOURCE}")
    print(f"Content length: {len(content)} chars\n")

    print("--- Validating plugin content ---")
    if not validate_plugin_content(content):
        print("\nERROR: Plugin validation failed. Aborting.")
        sys.exit(1)
    print("All validation checks passed.\n")

    success = deploy_plugin_to_site(SITE, content)
    if not success:
        print("\n[FAIL] Plugin deployment failed.")
        sys.exit(1)

    print("\n[OK] Plugin deployment succeeded.")
    print("\nWaiting 8 seconds for cache to settle...")
    time.sleep(8)

    print("\n" + "=" * 65)
    print("LIVE VERIFICATION")
    print("=" * 65)
    verified = verify_live()

    if verified:
        print("\nDEPLOYMENT COMPLETE AND VERIFIED.")
        print("Calculator page 777 should now show dark background on all browsers.")
        print("3-layer approach ensures persistence against theme/plugin CSS overrides.")
    else:
        print("\nDeployment done — some verification checks flagged issues.")
        print("Try hard-refresh: https://purebrain.ai/ai-tool-stack-calculator/")


if __name__ == "__main__":
    main()
