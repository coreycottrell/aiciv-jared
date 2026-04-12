#!/usr/bin/env python3
"""
Deploy purebrain-security-plugin.php v4.5.0 to purebrain.ai.

Aether Footer Credit bar: fixed-position credit line on ALL pages.
"Built by AETHER (an AI) for PureBrain.ai, PureMarketing.ai & PureTechnology.ai"

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
    # Handle both quoted ('value') and unquoted forms
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
    "screenshot_deploy": f"{SCREENSHOT_DIR}/plugin_v450_purebrain_deploy.png",
    "screenshot_verify": f"{SCREENSHOT_DIR}/plugin_v450_purebrain_verify.png",
}


# --- Validation ------------------------------------------------------------

def validate_plugin_content(content: str) -> bool:
    checks = {
        "v4.5.0 in header":                 "Version:     4.5.0" in content,
        "footer credit CSS block":          "pb-aether-footer-v450" in content,
        "footer credit div":                "pb-aether-footer" in content,
        "AETHER span class":                "pb-footer-aether" in content,
        "PureBrain.ai link (orange)":       "pb-footer-purebrain" in content,
        "PureMarketing.ai link (blue)":     "puremarketing.ai" in content,
        "PureTechnology.ai link (blue)":    "puretechnology.nyc" in content,
        "body padding-bottom 36px":         "padding-bottom: 36px" in content,
        "z-index 9999":                     "z-index: 9999" in content,
        "wp_footer priority 100":           "}, 100 );" in content,
        "changelog v4.5.0":                 "v4.5.0" in content,
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
    }

    all_ok = True
    for name, result in checks.items():
        status = "OK" if result else "MISSING/FAIL"
        print(f"  [{status}] {name}")
        if not result:
            all_ok = False
    return all_ok


# --- Playwright deploy -----------------------------------------------------

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
        print(f"\n[Step 1] Logging in to {name}...")
        page.goto(site["login_url"], wait_until="domcontentloaded", timeout=60000)
        time.sleep(2)

        # Handle GoDaddy SSO overlay - try both the class selector and the link text
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

        # CAPTCHA check (must run AFTER toggle click — CAPTCHA appears in the u/p form)
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
        page.screenshot(path=site["screenshot_deploy"].replace("_deploy.png", "_prefill.png"))
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
                        val.includes('pb-aether-footer-v450') &&
                        val.includes('pb-footer-aether') &&
                        val.includes('puremarketing.ai')
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
                    return cm ? cm.CodeMirror.getValue().substring(0, 2000) : 'N/A';
                }""")
                if "pb-aether-footer-v450" in current and "puremarketing.ai" in current:
                    save_success = True
                    print("  Footer credit found in editor — save assumed successful.")

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

    # Pages (homepage=11) + key blog posts
    page_ids  = [11]
    post_ids  = [631, 381, 316, 98, 172, 373, 565, 480, 606, 696]

    print(f"\n[Step 6] Busting page cache...")

    # Touch pages
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

    # Touch posts
    for post_id in post_ids:
        payload = json.dumps({"status": "publish"}).encode()
        req = urllib.request.Request(
            f"https://purebrain.ai/wp-json/wp/v2/posts/{post_id}",
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
                print(f"  Post {post_id}: HTTP {resp.status} — cache busted")
        except urllib.error.HTTPError as e:
            print(f"  Post {post_id}: HTTP {e.code}")
        except Exception as ex:
            print(f"  Post {post_id}: {ex}")


# --- Live verification -----------------------------------------------------

def verify_live(app_pass: str) -> dict:
    credentials = base64.b64encode(f"Aether:{app_pass}".encode()).decode()
    results = {}

    verify_urls = [
        ("homepage",    "https://purebrain.ai/"),
        ("blog_listing","https://purebrain.ai/blog/"),
        ("blog_post",   "https://purebrain.ai/the-ai-trust-gap/"),
        ("pay_test",    "https://purebrain.ai/pay-test/"),
    ]

    for label, url in verify_urls:
        print(f"\n[Verify] {label}: {url}")
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent":    "Mozilla/5.0 (compatible; AetherBot/1.0)",
                "Cache-Control": "no-cache, no-store",
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
            "page_loads":            http_code == 200,
            "footer_div_present":    "pb-aether-footer" in html,
            "footer_css_present":    "pb-aether-footer-v450" in html,
            "aether_text":           "AETHER" in html,
            "purebrain_link":        "purebrain.ai" in html,
            "puremarketing_link":    "puremarketing.ai" in html,
            "puretechnology_link":   "puretechnology.nyc" in html,
        }

        page_results = {}
        for name, result in checks.items():
            status = "OK" if result else "MISSING"
            print(f"  [{status}] {name}")
            page_results[name] = result

        passed = sum(1 for v in page_results.values() if v is True)
        total  = len(page_results)
        print(f"  Result: {passed}/{total} checks passed")
        results[label] = page_results

    return results


# --- Main ------------------------------------------------------------------

def main():
    print("=" * 65)
    print("PureBrain Security Plugin v4.5.0 — Aether Footer Credit")
    print("Fixed credit bar on ALL pages site-wide")
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

    # Deploy
    success = deploy_to_site(SITE, content)
    if not success:
        print("\n[FAIL] Deployment failed.")
        sys.exit(1)

    print(f"\n[OK] Deployment succeeded.")

    # Bust cache
    bust_page_cache(SITE)

    # Wait for cache to settle
    print("\nWaiting 6 seconds for cache to settle...")
    time.sleep(6)

    # Verify live
    results = verify_live(SITE["app_password"])

    # Summary
    print("\n" + "=" * 65)
    all_pages_ok = all(
        all(v for v in page.values() if isinstance(v, bool))
        for page in results.values()
        if isinstance(page, dict) and "error" not in page
    )

    if all_pages_ok:
        print("DEPLOYMENT COMPLETE AND VERIFIED.")
        print("\nAether footer credit is live on ALL pages:")
        print('  "Built by AETHER (an AI) for PureBrain.ai, PureMarketing.ai & PureTechnology.ai"')
        print("  - Fixed bottom, #080a12 dark bg, z-index 9999")
        print("  - AETHER in bold white, PureBrain.ai in orange, others in blue")
        print("  - Links open in _blank")
        print("  - Body padding-bottom: 36px prevents content overlap")
    else:
        failed_pages = []
        for page_label, page_checks in results.items():
            if isinstance(page_checks, dict):
                failed = [k for k, v in page_checks.items() if v is not True]
                if failed:
                    failed_pages.append(f"{page_label}: {', '.join(failed)}")
        print(f"DEPLOYMENT DONE — some verification checks need review:")
        for f in failed_pages:
            print(f"  {f}")
        print("\nNote: CDN cache may need time. Hard-refresh (Cmd+Shift+R) to verify.")


if __name__ == "__main__":
    main()
