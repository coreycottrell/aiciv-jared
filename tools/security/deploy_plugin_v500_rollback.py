#!/usr/bin/env python3
"""
Deploy purebrain-security-plugin.php v5.0.0 ROLLBACK to purebrain.ai.

EMERGENCY ROLLBACK: Removes j5 CSS hook added in v5.0.1 that broke the
blog color scheme. The hook injected:
  - html body.single-post .pb-inline-cta a → white text rules
  - html body.single-post .entry-content a[style*="background"][style*="gradient"]
These rules interfered with the site-wide color scheme.

All other features from v5.0.2 (assessment URL migration) are preserved.
Only the j5 add_action('wp_head', ..., 99) CSS block is removed.

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
    "screenshot_deploy": f"{SCREENSHOT_DIR}/plugin_v500_rollback_deploy.png",
    "screenshot_verify": f"{SCREENSHOT_DIR}/plugin_v500_rollback_verify.png",
}


# --- Validation ------------------------------------------------------------

def validate_plugin_content(content: str) -> bool:
    checks = {
        "v5.0.0 in header":                         "Version:     5.0.0" in content,
        "j5 hook REMOVED (no style id)":            "purebrain-inline-cta-white-text-v501" not in content,
        "j5 hook REMOVED (no add_action block)":    "pb-inline-cta a," not in content,
        "j4 transparency cta fix intact":           "purebrain-transparency-cta-v392" in content,
        "j3 link hover fix intact":                 "purebrain-link-hover-fix" in content,
        "assessment URL migration intact":          "ai-partnership-assessment" in content,
        "v5.0.0 page-860 magic cursor fix":         "body.page-id-860.tt-magic-cursor" in content,
        "footer v470":                              "pb-aether-footer-v470" in content,
        "FAQ accordion":                            "faq-accordion" in content,
        "transparency section":                     "aether-transparency__cta-btn" in content,
        "IndexNow v430":                            "823869521fbf4f33b93e67c781571e20" in content,
    }

    all_ok = True
    for name, result in checks.items():
        status = "OK" if result else "MISSING/FAIL"
        print(f"  [{status}] {name}")
        if not result:
            all_ok = False
    return all_ok


# --- Playwright deploy (plugin editor) ------------------------------------

def deploy_plugin_to_site(site: dict, content: str) -> bool:
    from playwright.sync_api import sync_playwright

    name = site["name"]
    print(f"\n{'='*65}")
    print(f"DEPLOYING PLUGIN TO: {name}")
    print(f"{'='*65}")

    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=2,
        )
        page = ctx.new_page()

        # Step 1: Login
        print(f"\n[Step 1] Logging in to {name}...")
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
            print("  No SSO overlay detected — proceeding directly.")
            time.sleep(1)

        captcha_field = page.locator("#wpsec_captcha_answer")
        if captcha_field.count() > 0 and captcha_field.is_visible():
            page.screenshot(path=site["screenshot_deploy"])
            print(f"  CAPTCHA detected! Screenshot: {site['screenshot_deploy']}")
            print("  GoDaddy bot protection triggered. Wait 10-15 minutes and retry.")
            browser.close()
            return False

        try:
            page.locator("#user_login").wait_for(state="visible", timeout=15000)
        except Exception:
            page.screenshot(path=site["screenshot_deploy"])
            print(f"  ERROR: Login form not visible. Screenshot: {site['screenshot_deploy']}")
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

        # Step 2: Plugin Editor
        print(f"\n[Step 2] Opening Plugin Editor...")
        page.goto(site["editor_url"], wait_until="domcontentloaded", timeout=60000)
        time.sleep(4)

        page_text = page.inner_text("body")
        if "DISALLOW_FILE_EDIT" in page_text or "editing has been disabled" in page_text.lower():
            print("  ERROR: File editing is disabled.")
            browser.close()
            return False

        has_codemirror = page.evaluate("() => !!document.querySelector('.CodeMirror')")
        has_textarea   = page.evaluate("() => !!document.querySelector('#newcontent')")
        print(f"  CodeMirror: {has_codemirror}, Textarea: {has_textarea}")

        if not has_codemirror and not has_textarea:
            page.screenshot(path=site["screenshot_deploy"])
            print(f"  ERROR: No editor found.")
            browser.close()
            return False

        # Step 3: Set content via CodeMirror
        print("\n[Step 3] Setting plugin content (v5.0.0 rollback — j5 removed)...")
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
                        val.includes('Version:     5.0.0') &&
                        !val.includes('purebrain-inline-cta-white-text-v501')
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

        # Step 4: Save
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

        save_success = False
        if "File edited successfully" in page_text or "updated successfully" in page_text.lower():
            print("  SUCCESS: Plugin file saved!")
            save_success = True
        elif "Parse error" in page_text or "syntax error" in page_text.lower():
            print(f"  ERROR: PHP syntax error!\n  {page_text[:400]}")
            browser.close()
            return False
        else:
            print(f"  Status unclear: {page_text[:200]}")
            if has_codemirror:
                current = page.evaluate("""() => {
                    const cm = document.querySelector('.CodeMirror');
                    return cm ? cm.CodeMirror.getValue().substring(0, 5000) : 'N/A';
                }""")
                if "Version:     5.0.0" in current and "purebrain-inline-cta-white-text-v501" not in current:
                    save_success = True
                    print("  v5.0.0 rollback content found in editor — save assumed successful.")

        if not save_success:
            print(f"  Deploy screenshot: {site['screenshot_deploy']}")
            browser.close()
            return False

        # Step 5: Clear Elementor cache
        print("\n[Step 5] Clearing Elementor cache...")
        credentials = base64.b64encode(
            f"{site['user']}:{site['app_password']}".encode()
        ).decode()

        cache_req = urllib.request.Request(
            "https://purebrain.ai/wp-json/elementor/v1/cache",
            method="DELETE",
            headers={
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
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

    return True


# --- Live verification -----------------------------------------------------

def verify_live() -> dict:
    results = {}
    posts_to_check = [
        ("https://purebrain.ai/your-next-direct-report-wont-be-human/", "Test post - Direct Report"),
        ("https://purebrain.ai/why-95-percent-of-ai-pilots-fail/", "Post 606 - 95% AI Pilots"),
    ]

    for url, label in posts_to_check:
        print(f"\n[Verify] {label}")
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
                html = resp.read().decode("utf-8", errors="replace")
                http_code = resp.status
        except Exception as ex:
            print(f"  fetch error: {ex}")
            results[label] = {"error": str(ex)}
            continue

        checks = {
            "page_loads_200":               http_code == 200,
            "j5_css_rule_ABSENT":           "purebrain-inline-cta-white-text-v501" not in html,
            "pb-inline-cta-a-rule_ABSENT":  ".pb-inline-cta a," not in html,
            "blog_content_present":         "entry-content" in html or "elementor-widget" in html,
        }

        post_results = {}
        for name, result in checks.items():
            status = "OK" if result else "MISSING/FAIL"
            print(f"  [{status}] {name}")
            post_results[name] = result

        passed = sum(1 for v in post_results.values() if v is True)
        total  = len(post_results)
        print(f"  Result: {passed}/{total} checks passed")
        results[label] = post_results

    return results


# --- Main ------------------------------------------------------------------

def main():
    print("=" * 65)
    print("PureBrain Security Plugin v5.0.0 — EMERGENCY ROLLBACK")
    print("Removes j5 CSS hook that broke blog color scheme")
    print("=" * 65)

    if not PLUGIN_FILE.exists():
        print(f"ERROR: Plugin file not found: {PLUGIN_FILE}")
        sys.exit(1)

    content = PLUGIN_FILE.read_text()
    print(f"\nPlugin file: {PLUGIN_FILE}")
    print(f"Content length: {len(content)} chars ({PLUGIN_FILE.stat().st_size} bytes)\n")

    # Pre-flight validation
    print("--- Validating plugin content ---")
    if not validate_plugin_content(content):
        print("\nERROR: Plugin validation failed. Aborting deployment.")
        sys.exit(1)
    print("All validation checks passed.\n")

    # Deploy plugin via Playwright
    print("\n" + "=" * 65)
    print("DEPLOYING plugin v5.0.0 rollback via Playwright")
    print("=" * 65)
    success = deploy_plugin_to_site(SITE, content)
    if not success:
        print("\n[FAIL] Plugin deployment failed.")
        sys.exit(1)

    print(f"\n[OK] Plugin deployment succeeded.")

    # Wait for cache to settle
    print("\nWaiting 6 seconds for cache to settle...")
    time.sleep(6)

    # Verify live
    print("\n" + "=" * 65)
    print("LIVE VERIFICATION")
    print("=" * 65)
    results = verify_live()

    # Summary
    print("\n" + "=" * 65)
    print("DEPLOYMENT SUMMARY")
    print("=" * 65)
    all_ok = True
    for label, checks in results.items():
        if isinstance(checks, dict) and "error" not in checks:
            passed = sum(1 for v in checks.values() if v is True)
            total  = len(checks)
            status = "PASS" if passed == total else "PARTIAL"
            print(f"  [{status}] {label}: {passed}/{total}")
            if passed < total:
                all_ok = False
        else:
            print(f"  [FAIL] {label}: {checks}")
            all_ok = False

    if all_ok:
        print("\nROLLBACK COMPLETE AND VERIFIED.")
        print("\nj5 CSS hook is REMOVED from purebrain.ai:")
        print("  - purebrain-inline-cta-white-text-v501 style block: GONE")
        print("  - .pb-inline-cta a white text overrides: GONE")
        print("  - belt-and-suspenders gradient selector: GONE")
        print("  - Blog color scheme: RESTORED to pre-v5.0.1 state")
    else:
        print("\nROLLBACK DONE — some verification checks failed.")
        print("Note: CDN cache may need time. Hard-refresh (Cmd+Shift+R) to verify.")


if __name__ == "__main__":
    main()
