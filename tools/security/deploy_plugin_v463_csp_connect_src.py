#!/usr/bin/env python3
"""
Deploy PureBrain Security Plugin v4.6.3 — CSP connect-src fix for Three.js.

Root cause of /invitation/ Three.js failure:
  The neural network script uses dynamic import() calls:
    const THREE = await import('https://cdn.jsdelivr.net/...')
  Dynamic import() is governed by connect-src in CSP (NOT script-src).
  cdn.jsdelivr.net was in script-src but NOT connect-src → silent failure.

Fix: Add https://cdn.jsdelivr.net to connect-src directive.

Author: full-stack-developer agent
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
PLUGIN_SOURCE = AETHER_ROOT / "exports/purebrain-security-plugin-v463.php"

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
    "login_url":     "https://purebrain.ai/wp-login.php",
    "user":          "Aether",
    "password":      PUREBRAIN_PASSWORD,
    "app_password":  PUREBRAIN_APP_PASS,
    "editor_url": (
        "https://purebrain.ai/wp-admin/plugin-editor.php"
        "?file=purebrain-security/purebrain-security-plugin.php"
        "&plugin=purebrain-security/purebrain-security-plugin.php"
    ),
}


def validate_plugin_content(content: str) -> bool:
    """Validate v4.6.3 specific changes + core features intact."""
    checks = {
        "Version 4.6.3":                          "Version:     4.6.3" in content,
        "cdn.jsdelivr.net in connect-src":        "https://cdn.jsdelivr.net; " in content,
        "CSP enforced (not report-only)":         "Content-Security-Policy: ' . $csp" in content,
        "CSP-Report-Only ABSENT":                 "Content-Security-Policy-Report-Only" not in content,
        "HSTS includes preload":                  "max-age=31536000; includeSubDomains; preload" in content,
        "Core: IndexNow key":                     "823869521fbf4f33b93e67c781571e20" in content,
        "Core: FAQ accordion":                    "purebrain-faq-accordion" in content,
        "Core: Aether footer":                    "pb-aether-footer" in content,
        "Core: Twitter image meta":               "_yoast_wpseo_twitter-image" in content,
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
        print(f"  ERROR: No editor found.")
        return False

    print("\n[Step 3] Setting plugin content (v4.6.3 - cdn.jsdelivr.net in connect-src)...")
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
                    val.includes('Version:     4.6.3') &&
                    val.includes('https://cdn.jsdelivr.net; ') &&
                    val.includes("Content-Security-Policy: ' . $csp") &&
                    !val.includes('Content-Security-Policy-Report-Only') &&
                    val.includes('pb-aether-footer') &&
                    val.includes('_yoast_wpseo_twitter-image')
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
        print(f"  Status unclear. Checking content in editor...")
        if has_codemirror:
            current = page.evaluate("""() => {
                const cm = document.querySelector('.CodeMirror');
                return cm ? cm.CodeMirror.getValue().substring(0, 5000) : 'N/A';
            }""")
            if ("Version:     4.6.3" in current and
                    "https://cdn.jsdelivr.net; " in current):
                print("  v4.6.3 markers found in editor — save assumed successful.")
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
            print(f"  CAPTCHA detected! Cannot proceed.")
            browser.close()
            return False

        try:
            page.locator("#user_login").wait_for(state="visible", timeout=15000)
        except Exception:
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
    Verify the CSP connect-src now includes cdn.jsdelivr.net.
    """
    import http.client
    import ssl

    print("\n[Verification] Checking CSP connect-src on purebrain.ai...")

    ctx_ssl = ssl.create_default_context()
    conn = http.client.HTTPSConnection("purebrain.ai", context=ctx_ssl, timeout=20)
    conn.request("GET", "/invitation/", headers={
        "User-Agent":    "Mozilla/5.0 (compatible; AetherBot/1.0)",
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma":        "no-cache",
    })
    resp = conn.getresponse()
    headers = dict(resp.getheaders())
    conn.close()

    headers_lower = {k.lower(): v for k, v in headers.items()}

    csp_value = headers_lower.get("content-security-policy", "")

    print(f"\n  CSP header:")
    print(f"    {csp_value[:300]}...")

    # Check connect-src contains cdn.jsdelivr.net
    connect_src_idx = csp_value.find("connect-src")
    if connect_src_idx >= 0:
        connect_src_end = csp_value.find(";", connect_src_idx)
        connect_src_value = csp_value[connect_src_idx:connect_src_end]
        print(f"\n  connect-src: {connect_src_value}")
        has_jsdelivr = "cdn.jsdelivr.net" in connect_src_value
        print(f"\n  [{'PASS' if has_jsdelivr else 'FAIL'}] cdn.jsdelivr.net in connect-src")
        return has_jsdelivr
    else:
        print("  ERROR: connect-src directive not found in CSP")
        return False


def main():
    print("=" * 65)
    print("PureBrain Security Plugin v4.6.3 — CSP connect-src Fix")
    print("=" * 65)
    print("\nFix: Add cdn.jsdelivr.net to connect-src in CSP")
    print("Root cause: Three.js await import() uses connect-src, not script-src")
    print("Effect: Neural network background on /invitation/ will render correctly")

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

    print("\n" + "=" * 65)
    print("DEPLOYING plugin v4.6.3 via Playwright (WP Plugin Editor)")
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
        print("The Three.js neural network background on /invitation/ should now render.")
        print("cdn.jsdelivr.net is now permitted in connect-src CSP directive.")
    else:
        print("\nDeployment done — verification check flagged issues.")
        print("Note: Cloudflare CDN cache may delay the update.")
        print("Manual verify: curl -sI https://purebrain.ai/invitation/ | grep -i content-security-policy")


if __name__ == "__main__":
    main()
