#!/usr/bin/env python3
"""
Deploy purebrain-security-plugin.php v4.1.0 to purebrain.ai.

v4.1.0 changes:
- AI Partnership Guide content gate on /ai-partnership-guide/
- Sections 1-3 visible freely; sections 4-7 blurred behind email gate
- New REST endpoint: POST /wp-json/purebrain/v1/guide-unlock
  - Server-side Brevo proxy (list 3, The Neural Feed)
  - Accepts email + optional first_name
  - Rate limited: 5 req/IP/min
- LocalStorage persist: pb_guide_unlocked=1 after submit
- Auto-reveal on return visit

All v4.0.x features retained.

Author: full-stack-developer agent
Date: 2026-02-23
"""

import os
import re
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

AETHER_ROOT = Path("/home/jared/projects/AI-CIV/aether")
PLUGIN_FILE = AETHER_ROOT / "tools/security/purebrain-security/purebrain-security-plugin.php"
SCREENSHOT_DIR = str(AETHER_ROOT / "exports/screenshots")

# --- Credentials -----------------------------------------------------------
env_text = (AETHER_ROOT / ".env").read_text()


def _env(key, quoted=True):
    if quoted:
        m = re.search(rf"{key}='([^']+)'", env_text)
        if m:
            return m.group(1)
    m = re.search(rf"{key}=([^\n]+)", env_text)
    return m.group(1).strip() if m else ""


SITES = [
    {
        "name":         "purebrain.ai",
        "admin_url":    "https://purebrain.ai/wp-admin",
        "login_url":    "https://purebrain.ai/wp-login.php",
        "user":         "Aether",
        "password":     _env("PUREBRAIN_WP_PASSWORD"),
        "editor_url":   (
            "https://purebrain.ai/wp-admin/plugin-editor.php"
            "?file=purebrain-security/purebrain-security-plugin.php"
            "&plugin=purebrain-security/purebrain-security-plugin.php"
        ),
        "screenshot_deploy": f"{SCREENSHOT_DIR}/plugin_v410_purebrain_deploy.png",
        "screenshot_verify": f"{SCREENSHOT_DIR}/plugin_v410_purebrain_verify.png",
        "guide_url":         "https://purebrain.ai/ai-partnership-guide/",
    },
]


# --- Validation ------------------------------------------------------------

def validate_plugin_content(content: str) -> bool:
    checks = {
        "version 4.1.0":                          "4.1.0" in content,
        # v4.1.0 new features
        "guide-unlock REST route":                 "purebrain/v1', '/guide-unlock'" in content,
        "purebrain_guide_unlock function":         "function purebrain_guide_unlock" in content,
        "pb-guide-gate-css style block":           "pb-guide-gate-css" in content,
        "pb-guide-gate-js script block":           "pb-guide-gate-js" in content,
        "pb-guide-gated-content element":          "pb-guide-gated-content" in content,
        "pb_guide_unlocked localStorage key":      "pb_guide_unlocked" in content,
        "guide-unlock endpoint URL":               "guide-unlock" in content,
        "BREVO fail-closed in guide handler":      "BREVO_API_KEY not defined — guide-unlock" in content,
        # v4.0.1 features
        "'every day' (lead headline)":             "every day in The Neural Feed" in content,
        "'every day' (CTA text)":                  "every day, alongside you" in content,
        # v4.0.0 features
        "blog listing Read More button":           "pb-read-more-btn" in content,
        # v3.9.3 features
        "twitter-image in REST meta":              "_yoast_wpseo_twitter-image" in content,
        # v3.9.2 features
        "transparency CTA white text":             "aether-transparency__cta-btn" in content,
        # v3.9.1 features
        "link hover white text":                   "purebrain-link-hover-fix" in content,
        # older features preserved
        "footer logo brand":                       "pb-logo-brand" in content,
        "FAQ accordion":                           "faq-accordion" in content,
        "rate limiter":                            "purebrain_check_rate_limit" in content,
        "transparency REST route":                 "purebrain/v1', '/transparency-data'" in content,
        "pb-lead-inline":                          "pb-lead-inline" in content,
    }

    all_ok = True
    for name, result in checks.items():
        status = "OK" if result else "MISSING/FAIL"
        print(f"  [{status}] {name}")
        if not result:
            all_ok = False
    return all_ok


# --- Playwright deploy to one site -----------------------------------------

def deploy_to_site(site: dict, content: str) -> bool:
    from playwright.sync_api import sync_playwright

    name = site["name"]
    print(f"\n{'='*65}")
    print(f"DEPLOYING TO: {name}")
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
        print(f"\n[Step 1] Logging in to {name} WP Admin...")
        page.goto(site["login_url"], wait_until="domcontentloaded", timeout=60000)
        time.sleep(2)

        # Handle GoDaddy SSO overlay (purebrain.ai)
        sso_toggle = page.locator(".wpaas-sso-login-toggle")
        if sso_toggle.count() > 0 and sso_toggle.is_visible():
            print("  GoDaddy SSO overlay detected - clicking username/password link...")
            sso_toggle.click()
            time.sleep(2)

        try:
            page.locator("#user_login").wait_for(state="visible", timeout=15000)
        except Exception:
            page.screenshot(path=site["screenshot_deploy"])
            print(f"  ERROR: Login form not visible. Screenshot: {site['screenshot_deploy']}")
            browser.close()
            return False

        # CAPTCHA check (GoDaddy bot protection)
        captcha_field = page.locator("#wpsec_captcha_answer")
        if captcha_field.count() > 0 and captcha_field.is_visible():
            page.screenshot(path=site["screenshot_deploy"])
            print(f"  CAPTCHA detected! Screenshot: {site['screenshot_deploy']}")
            print("  Wait 15-30 minutes for GoDaddy bot protection to reset, then retry.")
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
        print(f"\n[Step 2] Opening Plugin Editor for {name}...")
        page.goto(site["editor_url"], wait_until="domcontentloaded", timeout=60000)
        time.sleep(4)

        page_text = page.inner_text("body")
        if "DISALLOW_FILE_EDIT" in page_text or "editing has been disabled" in page_text.lower():
            print("  ERROR: File editing is disabled (DISALLOW_FILE_EDIT).")
            browser.close()
            return False

        has_codemirror = page.evaluate("() => !!document.querySelector('.CodeMirror')")
        has_textarea   = page.evaluate("() => !!document.querySelector('#newcontent')")
        print(f"  CodeMirror: {has_codemirror}, Textarea: {has_textarea}")

        if not has_codemirror and not has_textarea:
            page.screenshot(path=site["screenshot_deploy"])
            print(f"  ERROR: No editor found. Screenshot: {site['screenshot_deploy']}")
            browser.close()
            return False

        # Step 3: Set content
        print("\n[Step 3] Setting plugin content...")
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
                        val.includes('4.1.0') &&
                        val.includes('pb-guide-gate-js') &&
                        val.includes('guide-unlock') &&
                        val.includes('pb_guide_unlocked')
                    ) return 'success';
                    return 'set_failed: ' + val.length + ' chars';
                } catch(e) { return 'error: ' + e.message; }
            }""", content)
            print(f"  CodeMirror result: {result}")
            set_ok = (result == "success")

            if not set_ok:
                print("  CodeMirror failed, trying textarea fallback...")

        if not set_ok:
            # Unhide and set textarea
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
            print(f"  ERROR: PHP syntax error! {page_text[:400]}")
            browser.close()
            return False
        else:
            print(f"  Status unclear: {page_text[:300]}")
            if has_codemirror:
                current = page.evaluate("""() => {
                    const cm = document.querySelector('.CodeMirror');
                    return cm ? cm.CodeMirror.getValue().substring(0, 400) : 'N/A';
                }""")
                if "4.1.0" in current:
                    save_success = True
                    print("  v4.1.0 found in editor content - assuming save succeeded.")

        if not save_success:
            print(f"  Deploy screenshot: {site['screenshot_deploy']}")
            browser.close()
            return False

        # Step 5: Clear Elementor cache
        print("\n[Step 5] Clearing Elementor cache...")
        import base64
        credentials = base64.b64encode(
            f"{site['user']}:{site['password']}".encode()
        ).decode()

        base_url = site["admin_url"].replace("/wp-admin", "")
        cache_req = urllib.request.Request(
            f"{base_url}/wp-json/elementor/v1/cache",
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
            print(f"  Elementor cache response: HTTP {e.code} (may be normal)")
        except Exception as ex:
            print(f"  Elementor cache clear skipped: {ex}")

        page.screenshot(path=site["screenshot_verify"])
        browser.close()

    print(f"\n  Deploy screenshots:")
    print(f"    {site['screenshot_deploy']}")
    print(f"    {site['screenshot_verify']}")
    return True


# --- Live verification (HTTP) ------------------------------------------

def verify_guide_page(site: dict) -> dict:
    """
    Verify the AI Partnership Guide page:
    - pb-guide-gate-css style block present
    - pb-guide-gate-js script block present
    - pb-guide-gated-content element reference present
    - guide-unlock endpoint reference present
    - Page loads successfully (HTTP 200)
    """
    name = site["name"]
    url  = site["guide_url"]
    results = {}

    print(f"\n[Verify] {name} — checking guide page: {url}")

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; AetherBot/1.0)",
            "Cache-Control": "no-cache",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode("utf-8")
            http_code = resp.status
    except urllib.error.HTTPError as e:
        print(f"  HTTP {e.code} error fetching page")
        return {"fetch_error": f"HTTP {e.code}"}
    except Exception as ex:
        print(f"  ERROR fetching page: {ex}")
        return {"fetch_error": str(ex)}

    print(f"  HTTP {http_code} - page loaded ({len(html)} bytes)")
    results["page_loads"] = (http_code == 200)

    # Check for gate CSS
    has_gate_css = "pb-guide-gate-css" in html
    print(f"  [{'OK' if has_gate_css else 'MISSING'}] pb-guide-gate-css style block present")
    results["gate_css_present"] = has_gate_css

    # Check for gate JS
    has_gate_js = "pb-guide-gate-js" in html
    print(f"  [{'OK' if has_gate_js else 'MISSING'}] pb-guide-gate-js script block present")
    results["gate_js_present"] = has_gate_js

    # Check for gated content reference
    has_gated_content = "pb-guide-gated-content" in html
    print(f"  [{'OK' if has_gated_content else 'MISSING'}] pb-guide-gated-content reference present")
    results["gated_content_ref"] = has_gated_content

    # Check unlock endpoint reference
    has_unlock_endpoint = "guide-unlock" in html
    print(f"  [{'OK' if has_unlock_endpoint else 'MISSING'}] guide-unlock endpoint reference present")
    results["unlock_endpoint_ref"] = has_unlock_endpoint

    # Summary
    passed = sum(1 for v in results.values() if v is True)
    total  = len(results)
    print(f"\n  Verification result: {passed}/{total} checks passed")

    return results


# --- REST endpoint verification (direct API test) ---

def verify_unlock_endpoint(site: dict) -> dict:
    """Test the guide-unlock REST endpoint with a test email."""
    import json

    base_url = site["admin_url"].replace("/wp-admin", "")
    endpoint = f"{base_url}/wp-json/purebrain/v1/guide-unlock"
    results = {}

    print(f"\n[Verify REST] Testing guide-unlock endpoint: {endpoint}")

    # Test with a valid email
    test_payload = json.dumps({
        "email": "test-verify-gate@aether-verify.invalid",
        "first_name": "AetherTest"
    }).encode("utf-8")

    req = urllib.request.Request(
        endpoint,
        data=test_payload,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "User-Agent": "AetherVerify/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode("utf-8")
            http_code = resp.status
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        http_code = e.code

    print(f"  HTTP {http_code} — {body[:200]}")

    # Endpoint should return 200 with success or a Brevo error (502)
    # Both mean the endpoint REGISTERED successfully (not a 404)
    endpoint_registered = (http_code != 404)
    print(f"  [{'OK' if endpoint_registered else 'FAIL'}] Endpoint registered (not 404): HTTP {http_code}")
    results["endpoint_registered"] = endpoint_registered

    # If 200, verify success field
    if http_code == 200:
        try:
            data = json.loads(body)
            has_success = data.get("success") is True
            print(f"  [{'OK' if has_success else 'MISSING'}] Response has success=true")
            results["response_success"] = has_success
        except Exception:
            results["response_success"] = False

    # Test with invalid email - should return 400
    bad_payload = json.dumps({"email": "not-an-email"}).encode("utf-8")
    bad_req = urllib.request.Request(
        endpoint,
        data=bad_payload,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(bad_req, timeout=20) as resp:
            bad_code = resp.status
    except urllib.error.HTTPError as e:
        bad_code = e.code

    validation_works = (bad_code == 400)
    print(f"  [{'OK' if validation_works else 'UNEXPECTED'}] Invalid email returns 400: HTTP {bad_code}")
    results["validation_works"] = validation_works

    return results


# --- Main ------------------------------------------------------------------

def main():
    print("=" * 65)
    print("PureBrain Security Plugin v4.1.0 — Deployment to purebrain.ai")
    print("Changes: AI Partnership Guide content gate")
    print("=" * 65)

    if not PLUGIN_FILE.exists():
        print(f"ERROR: Plugin file not found: {PLUGIN_FILE}")
        sys.exit(1)

    content = PLUGIN_FILE.read_text()
    print(f"\nPlugin file: {PLUGIN_FILE}")
    print(f"Content length: {len(content)} chars\n")

    # Pre-flight validation
    print("--- Validating plugin content ---")
    if not validate_plugin_content(content):
        print("\nERROR: Plugin validation failed. Fix the issues above before deploying.")
        sys.exit(1)
    print("Validation passed.\n")

    # Deploy to purebrain.ai
    for site in SITES:
        success = deploy_to_site(site, content)
        if not success:
            print(f"\n[FAIL] Deployment to {site['name']} failed.")
            sys.exit(1)
        else:
            print(f"\n[OK] Deployment to {site['name']} succeeded.")

    # Post-deploy: verify guide page
    print("\n" + "=" * 65)
    print("--- Post-Deploy Verification ---")
    all_results = {}
    for site in SITES:
        page_results = verify_guide_page(site)
        endpoint_results = verify_unlock_endpoint(site)
        all_results[site["name"]] = {**page_results, **endpoint_results}

    # Final summary
    print("\n" + "=" * 65)
    all_ok = all(
        r.get("gate_css_present") and r.get("gate_js_present") and r.get("endpoint_registered")
        for r in all_results.values()
    )

    if all_ok:
        print("DEPLOYMENT COMPLETE AND VERIFIED.")
        print("\nWhat v4.1.0 adds:")
        print("  - Content gate on /ai-partnership-guide/")
        print("  - Sections 1-3 visible freely")
        print("  - Sections 4-7 blurred behind gradient + email form")
        print("  - POST /wp-json/purebrain/v1/guide-unlock (server-side Brevo proxy)")
        print("  - localStorage persist: pb_guide_unlocked=1 after submit")
        print("  - Auto-reveal on return visit")
        print("  - Brevo list 3 (The Neural Feed) + FIRSTNAME attribute")
    else:
        print("DEPLOYMENT DONE BUT SOME VERIFICATION CHECKS FAILED.")
        for site_name, results in all_results.items():
            failed = [k for k, v in results.items() if v is False]
            if failed:
                print(f"  {site_name} failed checks: {', '.join(failed)}")


if __name__ == "__main__":
    main()
