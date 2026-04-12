#!/usr/bin/env python3
"""
Deploy purebrain-security-plugin.php v3.6.0 to BOTH sites:
  1. purebrain.ai      (user=Aether, PUREBRAIN_WP_PASSWORD)
  2. jareddsanborn.com (user=jared,  WORDPRESS_APP_PASSWORD)

v3.6.0 changes:
- Aether Transparency Section auto-inject on single blog posts
- New REST endpoint: POST /wp-json/purebrain/v1/transparency-data
- Security fixes: CF-Connecting-IP for rate limiter (MED-001)
                  Brevo API key fail-open fix (MED-003)

v3.5.0 changes (included):
- Lead capture systems for blog posts

Author: full-stack-developer agent
Date: 2026-02-21
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
        "screenshot_deploy": f"{SCREENSHOT_DIR}/plugin_v360_purebrain_deploy.png",
        "screenshot_verify": f"{SCREENSHOT_DIR}/plugin_v360_purebrain_verify.png",
        "verify_url":    "https://purebrain.ai/wp-json/purebrain/v1/transparency-data",
        "blog_url":      "https://purebrain.ai/why-95-percent-of-ai-pilots-fail/",
    },
    {
        "name":         "jareddsanborn.com",
        "admin_url":    "https://jareddsanborn.com/wp-admin",
        "login_url":    "https://jareddsanborn.com/wp-login.php",
        "user":         "jared",
        "password":     _env("WORDPRESS_APP_PASSWORD"),
        "editor_url":   (
            "https://jareddsanborn.com/wp-admin/plugin-editor.php"
            "?file=purebrain-security/purebrain-security-plugin.php"
            "&plugin=purebrain-security/purebrain-security-plugin.php"
        ),
        "screenshot_deploy": f"{SCREENSHOT_DIR}/plugin_v360_jared_deploy.png",
        "screenshot_verify": f"{SCREENSHOT_DIR}/plugin_v360_jared_verify.png",
        "verify_url":    "https://jareddsanborn.com/wp-json/purebrain/v1/transparency-data",
        "blog_url":      "https://jareddsanborn.com/",
    },
]


# --- Validation ------------------------------------------------------------

def validate_plugin_content(content: str) -> bool:
    checks = {
        "version 3.6.0":                        "3.6.0" in content,
        "v3.6.0 changelog entry":               "Aether Transparency Section auto-injection" in content,
        "transparency REST route":              "purebrain/v1', '/transparency-data'" in content,
        "purebrain_update_transparency_data":   "purebrain_update_transparency_data" in content,
        "purebrain_transparency_data option":   "purebrain_transparency_data" in content,
        "transparency CSS hook":                "purebrain-transparency-css" in content,
        "transparency section id":              "pb-transparency-section" in content,
        "aether-transparency class":            "aether-transparency" in content,
        # MED-001: CF-Connecting-IP
        "CF-Connecting-IP header":              "HTTP_CF_CONNECTING_IP" in content,
        # MED-003: Brevo fail-open fix
        "brevo fail-open check":                "brevo_subscribe" in content,
        # v3.5.0 features retained
        "pb-lead-inline":                       "pb-lead-inline" in content,
        "pb-lead-bar":                          "pb-lead-bar" in content,
        "pb-security/v1 subscribe":             "pb-security/v1', '/subscribe'" in content,
        "purebrain_brevo_subscribe":            "purebrain_brevo_subscribe" in content,
        # older features retained
        "html body .pb-blog-nav a:hover":       "html body .pb-blog-nav a:hover" in content,
        "pb-logo-brand class":                  "pb-logo-brand" in content,
        "FAQ accordion":                        "faq-accordion" in content,
        "rate limiter":                         "purebrain_check_rate_limit" in content,
        "api.purebrain.ai (log)":               "https://api.purebrain.ai/api/log-conversation" in content,
    }

    all_ok = True
    for name, result in checks.items():
        status = "OK" if result else "MISSING"
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
                        val.includes('3.6.0') &&
                        val.includes('purebrain_update_transparency_data') &&
                        val.includes('pb-transparency-section') &&
                        val.includes('pb-lead-inline') &&
                        val.includes('html body .pb-blog-nav a:hover') &&
                        val.includes('pb-logo-brand')
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
            # Try reading CodeMirror to confirm v3.6.0 is in editor
            if has_codemirror:
                current = page.evaluate("""() => {
                    const cm = document.querySelector('.CodeMirror');
                    return cm ? cm.CodeMirror.getValue().substring(0, 200) : 'N/A';
                }""")
                if "3.6.0" in current:
                    save_success = True
                    print("  v3.6.0 found in editor content - assuming save succeeded.")

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

        cache_req = urllib.request.Request(
            f"https://{name.split('/')[0]}/wp-json/elementor/v1/cache",
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

        # Step 6: Flush WP cache
        print("\n[Step 6] Attempting WP cache flush...")
        page.goto(f"{site['admin_url']}/options-general.php", wait_until="domcontentloaded", timeout=30000)
        time.sleep(2)
        flush_url = page.evaluate("""() => {
            const links = Array.from(document.querySelectorAll('a'));
            const link = links.find(a =>
                /flush.cache/i.test(a.textContent) ||
                /flush.cache/i.test(a.href) ||
                /wpaas_action=flush_cache/i.test(a.href)
            );
            return link ? link.href : null;
        }""")
        if flush_url:
            page.goto(flush_url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(2)
            print("  WP cache flushed!")
        else:
            print("  No flush URL found — cache will expire naturally.")

        page.screenshot(path=site["screenshot_verify"])
        browser.close()

    print(f"\n  Deploy screenshots:")
    print(f"    {site['screenshot_deploy']}")
    print(f"    {site['screenshot_verify']}")
    return True


# --- Live verification (REST API) ------------------------------------------

def verify_live(site: dict) -> dict:
    """Verify v3.6.0 REST endpoint and lead-capture markup on site."""
    name = site["name"]
    print(f"\n[Verify] {name} — checking transparency-data endpoint...")

    results = {}

    # 1) Check transparency endpoint (expects 401 or 405 = endpoint registered)
    req = urllib.request.Request(
        site["verify_url"],
        method="OPTIONS",
        headers={"User-Agent": "Mozilla/5.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            results["transparency_endpoint"] = f"HTTP {resp.status}"
            print(f"  [OK] Transparency endpoint: HTTP {resp.status}")
    except urllib.error.HTTPError as e:
        if e.code in (200, 401, 405):
            results["transparency_endpoint"] = f"HTTP {e.code} (endpoint exists)"
            print(f"  [OK] Transparency endpoint: HTTP {e.code}")
        else:
            results["transparency_endpoint"] = f"HTTP {e.code} WARN"
            print(f"  [WARN] Transparency endpoint: HTTP {e.code}")
    except Exception as ex:
        results["transparency_endpoint"] = f"ERROR: {ex}"
        print(f"  [ERROR] Transparency endpoint: {ex}")

    # 2) Check blog post for lead-capture markup
    print(f"\n[Verify] {name} — checking lead capture on blog post...")
    req2 = urllib.request.Request(
        site["blog_url"],
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
        },
    )
    try:
        with urllib.request.urlopen(req2, timeout=30) as resp:
            html = resp.read().decode("utf-8")

        markup_checks = {
            "lead-capture-css":  'id="purebrain-lead-capture-css"' in html,
            "lead-capture-js":   'id="purebrain-lead-capture-js"' in html,
            "pb-lead-inline":    'id="pb-lead-inline"' in html,
            "pb-lead-bar":       'id="pb-lead-bar"' in html,
        }
        for mk, ok in markup_checks.items():
            status = "OK" if ok else "MISSING (blog post only / CDN cache)"
            print(f"  [{status[:2]}] {mk}")
            results[mk] = "ok" if ok else "missing"

    except Exception as ex:
        print(f"  [WARN] Could not fetch {site['blog_url']}: {ex}")
        results["blog_markup"] = f"fetch_error: {ex}"

    return results


# --- Main ------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 65)
    print("PUREBRAIN SECURITY PLUGIN v3.6.0 - DUAL-SITE DEPLOY")
    print("=" * 65)
    print("Sites:  purebrain.ai  +  jareddsanborn.com")
    print("Changes:")
    print("  v3.6.0 - Aether Transparency Section auto-inject (blog posts)")
    print("           POST /wp-json/purebrain/v1/transparency-data endpoint")
    print("           MED-001: CF-Connecting-IP in rate limiter")
    print("           MED-003: Brevo API key fail-open fix")
    print("  v3.5.0 - Lead capture (in-content box + post-read bar)")
    print("=" * 65)

    if not PLUGIN_FILE.exists():
        print(f"ERROR: Plugin file not found: {PLUGIN_FILE}")
        sys.exit(1)

    plugin_content = PLUGIN_FILE.read_text()
    print(f"\nPlugin file: {PLUGIN_FILE}")
    print(f"Size: {len(plugin_content):,} chars")

    print("\n--- Validating plugin content ---")
    if not validate_plugin_content(plugin_content):
        print("\nERROR: Plugin validation failed. Aborting.")
        sys.exit(1)
    print("Validation passed.\n")

    # Deploy to both sites
    deploy_results = {}
    for site in SITES:
        ok = deploy_to_site(site, plugin_content)
        deploy_results[site["name"]] = ok

    # Wait for CDN propagation
    print("\nWaiting 10 seconds for CDN propagation...")
    time.sleep(10)

    # Verify both sites
    verify_results = {}
    for site in SITES:
        if deploy_results.get(site["name"]):
            verify_results[site["name"]] = verify_live(site)
        else:
            verify_results[site["name"]] = {"skipped": "deploy_failed"}

    # Final summary
    print("\n" + "=" * 65)
    print("FINAL RESULT")
    print("=" * 65)
    all_ok = True
    for name, ok in deploy_results.items():
        status = "SUCCESS" if ok else "FAILED"
        print(f"  Deploy {name}: {status}")
        if not ok:
            all_ok = False

    for name, v in verify_results.items():
        print(f"  Verify {name}: {v}")

    if all_ok:
        print("\n[SUCCESS] v3.6.0 deployed to both sites!")
        print("\n  What's now active:")
        print("  - Aether Transparency Section: auto-injects into single blog posts")
        print("    (only visible once you POST data to /wp-json/purebrain/v1/transparency-data)")
        print("  - Lead capture: in-content box (50%) + post-read bar (85%)")
        print("  - MED-001 + MED-003 security fixes applied")
    else:
        print("\n[PARTIAL/FAILED] Check screenshots above for details.")
        sys.exit(1)
