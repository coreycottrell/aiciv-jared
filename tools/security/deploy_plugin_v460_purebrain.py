#!/usr/bin/env python3
"""
Deploy purebrain-security-plugin.php v4.6.0 to purebrain.ai.

Why PureBrain link injection:
- Footer credit bar updated: "Why Choose PureBrain?" link appended to footer bar on ALL pages
- Homepage banner: "See Why PureBrain Is Different →" bar above footer bar on homepage only
- Pay-test pages (439, 689, 468, 688): link injected before <!-- END PAY-TEST SCRIPTS -->

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
    "screenshot_deploy": f"{SCREENSHOT_DIR}/plugin_v460_purebrain_deploy.png",
    "screenshot_verify": f"{SCREENSHOT_DIR}/plugin_v460_purebrain_verify.png",
}

# Pay-test page IDs to update
PAY_TEST_PAGES = [439, 689, 468, 688]

# The Why PureBrain link HTML to inject into pay-test pages
WHY_PUREBRAIN_LINK_HTML = '''
<!-- WHY PUREBRAIN LINK (v4.6.0) -->
<style id="pb-why-purebrain-paytest-v460">
#pb-why-purebrain-paytest-link {
    text-align: center;
    padding: 16px 0 8px 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    font-size: 13px;
}
#pb-why-purebrain-paytest-link a {
    color: #2a93c1;
    text-decoration: none;
    font-weight: 600;
    letter-spacing: 0.02em;
    transition: color 0.15s ease;
}
#pb-why-purebrain-paytest-link a:hover {
    color: #f1420b;
}
</style>
<div id="pb-why-purebrain-paytest-link">
    <a href="https://purebrain.ai/why-purebrain/" rel="noopener">See Why PureBrain Is Different &rarr;</a>
</div>
'''

INJECT_BEFORE = "<!-- END PAY-TEST SCRIPTS -->"


# --- Validation ------------------------------------------------------------

def validate_plugin_content(content: str) -> bool:
    checks = {
        "v4.6.0 in header":                 "Version:     4.6.0" in content,
        "why-purebrain link in footer bar": "why-purebrain" in content,
        "footer css block (v460)":          "pb-aether-footer-v460" in content,
        "footer why link class":            "pb-footer-why" in content,
        "homepage why bar (v460)":          "pb-why-purebrain-v460" in content,
        "homepage why bar div":             "pb-why-purebrain-bar" in content,
        "footer credit div":                "pb-aether-footer" in content,
        "AETHER span class":                "pb-footer-aether" in content,
        "PureBrain.ai link (orange)":       "pb-footer-purebrain" in content,
        "PureMarketing.ai link (blue)":     "puremarketing.ai" in content,
        "PureTechnology.ai link (blue)":    "puretechnology.nyc" in content,
        "body padding-bottom 36px":         "padding-bottom: 36px" in content,
        "z-index 9999":                     "z-index: 9999" in content,
        "wp_footer priority 100":           "}, 100 );" in content,
        "wp_footer priority 99":            "}, 99 );" in content,
        "changelog v4.6.0":                 "v4.6.0" in content,
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


# --- Update pay-test pages via REST API ------------------------------------

def update_pay_test_pages(app_pass: str) -> dict:
    credentials = base64.b64encode(f"Aether:{app_pass}".encode()).decode()
    auth_header = f"Basic {credentials}"
    results = {}

    for page_id in PAY_TEST_PAGES:
        print(f"\n[Pay-Test] Updating page ID {page_id}...")

        # Fetch current content
        req = urllib.request.Request(
            f"https://purebrain.ai/wp-json/wp/v2/pages/{page_id}?context=edit",
            headers={
                "Authorization": auth_header,
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception as ex:
            print(f"  ERROR fetching page {page_id}: {ex}")
            results[page_id] = {"error": str(ex)}
            continue

        content = data.get("content", {}).get("raw", "")
        slug = data.get("slug", "unknown")
        print(f"  Slug: {slug}, Content length: {len(content)}")

        # Check if link already exists
        if "why-purebrain" in content:
            print(f"  Link already present in page {page_id}. Skipping.")
            results[page_id] = {"status": "already_present", "slug": slug}
            continue

        # Check if injection point exists
        if INJECT_BEFORE not in content:
            print(f"  WARNING: Injection marker not found in page {page_id}!")
            results[page_id] = {"error": "injection_marker_not_found", "slug": slug}
            continue

        # Inject the link before the END PAY-TEST SCRIPTS comment
        new_content = content.replace(
            INJECT_BEFORE,
            WHY_PUREBRAIN_LINK_HTML + "\n" + INJECT_BEFORE,
            1  # replace first occurrence only
        )

        print(f"  Content after injection: {len(new_content)} chars (was {len(content)})")

        # POST update
        payload = json.dumps({"content": new_content}).encode("utf-8")
        update_req = urllib.request.Request(
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
            with urllib.request.urlopen(update_req, timeout=60) as resp:
                result_data = json.loads(resp.read().decode("utf-8"))
                new_len = len(result_data.get("content", {}).get("raw", ""))
                print(f"  Page {page_id} updated: HTTP {resp.status}, new length: {new_len}")
                results[page_id] = {"status": "updated", "slug": slug, "new_length": new_len}
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")[:300]
            print(f"  ERROR updating page {page_id}: HTTP {e.code}: {err_body}")
            results[page_id] = {"error": f"HTTP {e.code}", "slug": slug}
        except Exception as ex:
            print(f"  ERROR updating page {page_id}: {ex}")
            results[page_id] = {"error": str(ex), "slug": slug}

        time.sleep(1)

    return results


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
                        val.includes('pb-aether-footer-v460') &&
                        val.includes('pb-footer-why') &&
                        val.includes('why-purebrain')
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
                    return cm ? cm.CodeMirror.getValue().substring(0, 3000) : 'N/A';
                }""")
                if "pb-aether-footer-v460" in current and "why-purebrain" in current:
                    save_success = True
                    print("  v4.6.0 content found in editor — save assumed successful.")

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

    page_ids  = [11] + PAY_TEST_PAGES
    post_ids  = []

    print(f"\n[Step 7] Busting page cache...")

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


# --- Live verification -----------------------------------------------------

def verify_live(app_pass: str) -> dict:
    results = {}

    verify_urls = [
        ("homepage",         "https://purebrain.ai/"),
        ("blog_listing",     "https://purebrain.ai/blog/"),
        ("blog_post",        "https://purebrain.ai/the-ai-trust-gap/"),
        ("pay_test_439",     "https://purebrain.ai/pay-test/"),
        ("pay_test_sandbox", "https://purebrain.ai/pay-test-sandbox/"),
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

        is_pay_test = "pay_test" in label
        is_homepage = label == "homepage"

        checks = {
            "page_loads":                http_code == 200,
            "footer_div_present":        "pb-aether-footer" in html,
            "footer_v460_css":           "pb-aether-footer-v460" in html,
            "why_purebrain_in_footer":   "pb-footer-why" in html,
            "why_purebrain_link":        "why-purebrain" in html,
        }

        if is_homepage:
            checks["homepage_why_bar"] = "pb-why-purebrain-bar" in html

        if is_pay_test:
            checks["paytest_why_link"] = "pb-why-purebrain-paytest-link" in html

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
    print("PureBrain Security Plugin v4.6.0 — Why PureBrain Link Injection")
    print("Footer bar link (all pages) + Homepage bar + Pay-test pages")
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

    # Step 1: Update pay-test pages via REST API (no Playwright needed)
    print("\n" + "=" * 65)
    print("STEP 1: Update pay-test pages via REST API")
    print("=" * 65)
    pay_test_results = update_pay_test_pages(SITE["app_password"])
    print("\nPay-test update results:")
    for page_id, result in pay_test_results.items():
        print(f"  Page {page_id}: {result}")

    # Step 2: Deploy plugin via Playwright
    print("\n" + "=" * 65)
    print("STEP 2: Deploy plugin v4.6.0 via Playwright")
    print("=" * 65)
    success = deploy_plugin_to_site(SITE, content)
    if not success:
        print("\n[FAIL] Plugin deployment failed.")
        sys.exit(1)

    print(f"\n[OK] Plugin deployment succeeded.")

    # Step 3: Bust cache
    bust_page_cache(SITE)

    # Wait for cache to settle
    print("\nWaiting 6 seconds for cache to settle...")
    time.sleep(6)

    # Step 4: Verify live
    print("\n" + "=" * 65)
    print("STEP 3: Live verification")
    print("=" * 65)
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
        print("\nWhy PureBrain links are LIVE:")
        print("  - Footer bar: 'Why Choose PureBrain?' on ALL pages site-wide")
        print("  - Homepage bar: 'See Why PureBrain Is Different' above footer")
        print("  - Pay-test pages (439, 689, 468, 688): link above END PAY-TEST SCRIPTS")
        print("  - Link: https://purebrain.ai/why-purebrain/")
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

    # Print pay-test summary
    print("\nPay-test page results:")
    for page_id, result in pay_test_results.items():
        status = result.get("status", result.get("error", "unknown"))
        slug = result.get("slug", "")
        print(f"  Page {page_id} ({slug}): {status}")


if __name__ == "__main__":
    main()
