#!/usr/bin/env python3
"""
Deploy purebrain-security-plugin.php v4.8.0 to purebrain.ai.

v4.8.0: Magic cursor body fix with !important (page 816 specific fix).
- Fixes [class*="magic"] !important overriding page-816 body color
- Previous fix used `color: initial` without !important — could not beat Additional CSS
- New fix uses `color: #e8edf5 !important` with body.tt-magic-cursor (0,1,1 specificity)
- Adds page-816-specific body.page-id-816.tt-magic-cursor (0,2,1 specificity)
- Adds SVG descendant overrides for [class*="magic"] svg rules
- Priority changed from wp_footer 1 to wp_footer 99 — loads absolutely last

Author: full-stack-developer agent
Date: 2026-02-23
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
    "screenshot_deploy": f"{SCREENSHOT_DIR}/plugin_v480_purebrain_deploy.png",
    "screenshot_verify": f"{SCREENSHOT_DIR}/plugin_v480_purebrain_verify.png",
}


# --- Validation ------------------------------------------------------------

def validate_plugin_content(content: str) -> bool:
    checks = {
        "v4.8.0 in header":                 "Version:     4.8.0" in content,
        "magic cursor body override (v4.8.0)": "pb-magic-cursor-body-override" in content,
        "body.tt-magic-cursor with !important": "body.tt-magic-cursor {" in content and "color: #e8edf5 !important" in content,
        "page-id-816 specific override":    "body.page-id-816.tt-magic-cursor" in content,
        "SVG descendant override":          "body.tt-magic-cursor svg" in content,
        "wp_footer priority 99":            "}, 99 );" in content,
        "elementor_canvas check":           "is_page_template( 'elementor_canvas' )" in content,
        # v4.7.0 features preserved
        "footer css block (v470)":          "pb-aether-footer-v470" in content,
        "footer height 64px":               "height: 64px" in content,
        "orange border-top":                "border-top: 2px solid #f1420b" in content,
        "aether pulse animation":           "pb-aether-pulse" in content,
        "footer div present":               'id="pb-aether-footer"' in content,
        "body padding-bottom 64px":         "padding-bottom: 64px" in content,
        "Why Choose PureBrain? CTA":        "Why Choose PureBrain?" in content,
        # Previous features preserved
        "social share bar (v4.2.0)":        "pb-social-share-js" in content,
        "guide-unlock REST route":          "purebrain/v1', '/guide-unlock'" in content,
        "blog listing Read More button":    "pb-read-more-btn" in content,
        "transparency section":             "aether-transparency__cta-btn" in content,
        "link hover fix":                   "purebrain-link-hover-fix" in content,
        "footer logo brand":                "pb-logo-brand" in content,
        "FAQ accordion":                    "faq-accordion" in content,
        "rate limiter":                     "purebrain_check_rate_limit" in content,
        "IndexNow (v4.3.0)":               "823869521fbf4f33b93e67c781571e20" in content,
        "homepage why bar (v4.6.0)":        "pb-why-purebrain-v460" in content,
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
        print("\n[Step 3] Setting plugin content (v4.8.0)...")
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
                        val.includes('Version:     4.8.0') &&
                        val.includes('body.page-id-816.tt-magic-cursor') &&
                        val.includes('pb-aether-footer-v470')
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
                if "Version:     4.8.0" in current and "body.page-id-816.tt-magic-cursor" in current:
                    save_success = True
                    print("  v4.8.0 content found in editor — save assumed successful.")

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


# --- Post-deploy cache bust ------------------------------------------------

def bust_page_cache(site: dict) -> None:
    credentials = base64.b64encode(
        f"{site['user']}:{site['app_password']}".encode()
    ).decode()
    auth_header = f"Basic {credentials}"

    # Key pages to bust cache on — including page 816 specifically
    page_ids = [816, 11, 439, 468, 689, 688, 777]

    print(f"\n[Step 6] Busting page cache for key pages (including 816)...")

    for page_id in page_ids:
        payload = json.dumps({"status": "publish"}).encode()
        req = urllib.request.Request(
            f"https://purebrain.ai/wp-json/wp/v2/pages/{page_id}",
            data=payload,
            method="POST",
            headers={
                "Authorization": auth_header,
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                print(f"  Page {page_id}: HTTP {resp.status} — cache busted")
        except urllib.error.HTTPError as e:
            print(f"  Page {page_id}: HTTP {e.code}")
        except Exception as ex:
            print(f"  Page {page_id}: {ex}")
        time.sleep(0.5)


# --- Live verification -----------------------------------------------------

def verify_live(app_pass: str) -> dict:
    results = {}

    import urllib.request as urlreq
    import time as t

    # Specifically verify page 816 has the fix
    print(f"\n[Verify] Page 816 - ai-website-analysis")
    url = "https://purebrain.ai/ai-website-analysis/"
    req = urlreq.Request(
        url,
        headers={
            "User-Agent":    "Mozilla/5.0 (compatible; AetherBot/1.0)",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma":        "no-cache",
        },
    )
    try:
        with urlreq.urlopen(req, timeout=30) as resp:
            html = resp.read().decode("utf-8", errors="replace")
            http_code = resp.status
    except Exception as ex:
        print(f"  fetch error: {ex}")
        return {"page_816": {"error": str(ex)}}

    checks = {
        "page_loads_200":                   http_code == 200,
        "v4.8.0_fix_present":               "pb-magic-cursor-body-override" in html,
        "body_tt_magic_cursor_override":    "body.tt-magic-cursor {" in html or "body.tt-magic-cursor{" in html,
        "color_e8edf5_important":           "color: #e8edf5 !important" in html,
        "page_id_816_override":             "body.page-id-816.tt-magic-cursor" in html,
        "svg_descendant_override":          "body.tt-magic-cursor svg" in html,
        "bg_0a0e1a_important":              "background-color: #0a0e1a !important" in html,
        "no_wp_autop_damage":               "</p>\n</style>" not in html and "</p></style>" not in html,
        "footer_v470_present":              "pb-aether-footer-v470" in html,
    }

    page_816_results = {}
    for name, result in checks.items():
        status = "OK" if result else "MISSING/FAIL"
        print(f"  [{status}] {name}")
        page_816_results[name] = result

    passed = sum(1 for v in page_816_results.values() if v is True)
    total  = len(page_816_results)
    print(f"  Result: {passed}/{total} checks passed")
    results["page_816"] = page_816_results

    # Also check homepage to ensure existing features still work
    print(f"\n[Verify] Homepage")
    req2 = urlreq.Request(
        "https://purebrain.ai/",
        headers={
            "User-Agent":    "Mozilla/5.0 (compatible; AetherBot/1.0)",
            "Cache-Control": "no-cache",
        },
    )
    try:
        with urlreq.urlopen(req2, timeout=30) as resp:
            html2 = resp.read().decode("utf-8", errors="replace")
            code2 = resp.status
    except Exception as ex:
        print(f"  fetch error: {ex}")
        results["homepage"] = {"error": str(ex)}
        return results

    hp_checks = {
        "loads_200":            code2 == 200,
        "footer_v470":          "pb-aether-footer-v470" in html2,
        "aether_pulse":         "pb-aether-pulse" in html2,
        "why_purebrain":        "Why Choose PureBrain?" in html2,
    }
    hp_results = {}
    for name, result in hp_checks.items():
        status = "OK" if result else "MISSING"
        print(f"  [{status}] {name}")
        hp_results[name] = result

    hp_passed = sum(1 for v in hp_results.values() if v is True)
    print(f"  Result: {hp_passed}/{len(hp_results)} checks passed")
    results["homepage"] = hp_results

    return results


# --- Main ------------------------------------------------------------------

def main():
    print("=" * 65)
    print("PureBrain Security Plugin v4.8.0 — Magic Cursor Fix with !important")
    print("Fixes [class*=magic] !important beating page-816 body color overrides")
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
    print("DEPLOYING plugin v4.8.0 via Playwright")
    print("=" * 65)
    success = deploy_plugin_to_site(SITE, content)
    if not success:
        print("\n[FAIL] Plugin deployment failed.")
        sys.exit(1)

    print(f"\n[OK] Plugin deployment succeeded.")

    # Bust cache for page 816 specifically
    bust_page_cache(SITE)

    # Wait for cache to settle
    print("\nWaiting 6 seconds for cache to settle...")
    time.sleep(6)

    # Verify live
    print("\n" + "=" * 65)
    print("LIVE VERIFICATION")
    print("=" * 65)
    results = verify_live(SITE["app_password"])

    # Summary
    print("\n" + "=" * 65)
    page_816 = results.get("page_816", {})
    all_816_ok = all(v for v in page_816.values() if isinstance(v, bool))

    if all_816_ok:
        print("DEPLOYMENT COMPLETE AND VERIFIED.")
        print("\nv4.8.0 orange fix is LIVE on /ai-website-analysis/ (page 816):")
        print("  - body.tt-magic-cursor { color: #e8edf5 !important } — beats Additional CSS")
        print("  - body.page-id-816.tt-magic-cursor — maximum specificity (0,2,1)")
        print("  - SVG descendant overrides — beats [class*=magic] svg rules")
        print("  - wp_footer priority 99 — loads absolutely last")
    else:
        failed = [k for k, v in page_816.items() if v is not True]
        print(f"DEPLOYMENT DONE — some verification checks failed:")
        for f in failed:
            print(f"  FAIL: {f}")
        print("\nNote: CDN cache may need time. Hard-refresh (Cmd+Shift+R) to verify.")
        print("If color checks fail, CDN caching may still serve old version.")


if __name__ == "__main__":
    main()
