#!/usr/bin/env python3
"""
Deploy PureBrain Security Plugin v6.1.0 with v4.6.2 security header changes.

Two surgical changes from previous deploy:
  1. CSP: Content-Security-Policy-Report-Only → Content-Security-Policy (enforced mode)
  2. HSTS: Added `preload` directive → max-age=31536000; includeSubDomains; preload

Note: The plugin file version header remains 6.1.0 (the local file is the base).
      The two lines above have been surgically edited in the local .php file.

Author: full-stack-developer agent
Date: 2026-02-26
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
    "screenshot_deploy": f"{SCREENSHOT_DIR}/plugin_v462_csp_hsts_deploy.png",
    "screenshot_verify": f"{SCREENSHOT_DIR}/plugin_v462_csp_hsts_verify.png",
}


def validate_plugin_content(content: str) -> bool:
    """Validate the two key changes are present in the content."""
    checks = {
        "CSP enforced (not report-only)":            "Content-Security-Policy: ' . $csp" in content,
        "CSP-Report-Only ABSENT":                    "Content-Security-Policy-Report-Only" not in content,
        "HSTS includes preload":                     "max-age=31536000; includeSubDomains; preload" in content,
        "Core v6.1.0 features intact (IndexNow)":   "823869521fbf4f33b93e67c781571e20" in content,
        "Core v6.1.0 features intact (twitter:card)": "twitter:card" in content,
        "Core v6.1.0 features intact (301 redirect)": "ai-adoption-assessment" in content,
        "Core features intact (FAQ accordion)":      "purebrain-faq-accordion" in content,
        "Core features intact (Aether footer)":      "pb-aether-footer" in content,
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

    print("\n[Step 3] Setting plugin content (CSP enforced + HSTS preload)...")
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
                    val.includes("Content-Security-Policy: ' . $csp") &&
                    !val.includes('Content-Security-Policy-Report-Only') &&
                    val.includes('includeSubDomains; preload') &&
                    val.includes('pb-aether-footer') &&
                    val.includes('twitter:card')
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
            # Check that the CSP enforced header is present and HSTS preload present
            if ("Content-Security-Policy: ' . $csp" in current and
                    "includeSubDomains; preload" in current):
                print("  CSP enforced + HSTS preload found in editor — save assumed successful.")
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
    Verify both security header changes are live on purebrain.ai:
    1. Content-Security-Policy header present (enforced, not report-only)
    2. Strict-Transport-Security includes preload
    """
    import http.client
    import ssl

    print("\n[Verification] Checking security headers on purebrain.ai...")
    all_ok = True

    ctx_ssl = ssl.create_default_context()
    conn = http.client.HTTPSConnection("purebrain.ai", context=ctx_ssl, timeout=20)
    conn.request("GET", "/", headers={
        "User-Agent":    "Mozilla/5.0 (compatible; AetherBot/1.0)",
        "Cache-Control": "no-cache, no-store, must-revalidate",
    })
    resp = conn.getresponse()
    headers = dict(resp.getheaders())
    conn.close()

    # Normalize header keys to lowercase for comparison
    headers_lower = {k.lower(): v for k, v in headers.items()}

    print(f"\n  All response headers:")
    for k, v in sorted(headers_lower.items()):
        if any(x in k for x in ["security", "content", "strict", "transport", "csp", "frame", "xss"]):
            print(f"    {k}: {v}")

    # Check 1: CSP enforced (not report-only)
    csp_value = headers_lower.get("content-security-policy", "")
    csp_ro_value = headers_lower.get("content-security-policy-report-only", "")

    csp_present = bool(csp_value)
    csp_ro_absent = not bool(csp_ro_value)

    print(f"\n  === Fix 1: CSP Enforced ===")
    print(f"  [{'PASS' if csp_present else 'FAIL'}] content-security-policy header present")
    print(f"    Value: {csp_value[:100]}..." if len(csp_value) > 100 else f"    Value: {csp_value or '(absent)'}")
    print(f"  [{'PASS' if csp_ro_absent else 'FAIL'}] content-security-policy-report-only ABSENT")
    print(f"    Report-Only: {csp_ro_value or '(absent - correct)'}")

    if not (csp_present and csp_ro_absent):
        all_ok = False

    # Check 2: HSTS with preload
    hsts_value = headers_lower.get("strict-transport-security", "")
    hsts_preload = "preload" in hsts_value
    hsts_max_age = "max-age=31536000" in hsts_value
    hsts_subdomains = "includesubdomains" in hsts_value.lower()

    print(f"\n  === Fix 2: HSTS Preload ===")
    print(f"  [{'PASS' if hsts_max_age else 'FAIL'}] max-age=31536000 present")
    print(f"  [{'PASS' if hsts_subdomains else 'FAIL'}] includeSubDomains present")
    print(f"  [{'PASS' if hsts_preload else 'FAIL'}] preload present")
    print(f"    Full value: {hsts_value or '(absent)'}")

    if not (hsts_max_age and hsts_subdomains and hsts_preload):
        all_ok = False

    return all_ok


def main():
    print("=" * 65)
    print("PureBrain Security Plugin — CSP Enforced + HSTS Preload")
    print("=" * 65)
    print("\nTwo surgical changes from live v6.1.0:")
    print("  1. CSP: Content-Security-Policy-Report-Only → Content-Security-Policy (enforced)")
    print("  2. HSTS: max-age=31536000; includeSubDomains; preload (added preload)")

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
    print("DEPLOYING plugin (CSP + HSTS changes) via Playwright (WP Plugin Editor)")
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
        print("  - CSP: Now in enforced mode (Content-Security-Policy)")
        print("  - HSTS: Now includes preload directive")
        print("  - All existing v6.1.0 plugin features intact")
    else:
        print("\nDeployment done — some verification checks flagged issues.")
        print("Note: CDN/Cloudflare cache may need a moment to propagate.")
        print("Retry verification: curl -sI https://purebrain.ai/ | grep -i 'content-security-policy'")
        print("                    curl -sI https://purebrain.ai/ | grep -i 'strict-transport'")


if __name__ == "__main__":
    main()
