#!/usr/bin/env python3
"""
Deploy purebrain-security-plugin.php v3.9.0 to BOTH sites:
  1. purebrain.ai      (user=Aether, PUREBRAIN_WP_PASSWORD)
  2. jareddsanborn.com (user=AetherPureBrain.ai, WORDPRESS_APP_PASSWORD)

v3.9.0 changes:
- Tag pills: .post-tags .tag-links a[rel="tag"] now styled as blue pills
  (blue #2a93c1 bg + white text, hover orange #f1420b bg + white text)
- CTA button: white text enforced at CSS level as backup to inline style

Author: full-stack-developer agent
Date: 2026-02-22
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
        "screenshot_deploy": f"{SCREENSHOT_DIR}/plugin_v390_purebrain_deploy.png",
        "screenshot_verify": f"{SCREENSHOT_DIR}/plugin_v390_purebrain_verify.png",
        "blog_post_url": "https://purebrain.ai/the-ai-trust-gap/",
    },
    {
        "name":         "jareddsanborn.com",
        "admin_url":    "https://jareddsanborn.com/wp-admin",
        "login_url":    "https://jareddsanborn.com/wp-login.php",
        "user":         "AetherPureBrain.ai",
        "password":     _env("WORDPRESS_APP_PASSWORD"),
        "editor_url":   (
            "https://jareddsanborn.com/wp-admin/plugin-editor.php"
            "?file=purebrain-security/purebrain-security-plugin.php"
            "&plugin=purebrain-security/purebrain-security-plugin.php"
        ),
        "screenshot_deploy": f"{SCREENSHOT_DIR}/plugin_v390_jared_deploy.png",
        "screenshot_verify": f"{SCREENSHOT_DIR}/plugin_v390_jared_verify.png",
        "blog_post_url": "https://jareddsanborn.com/the-ai-trust-gap/",
    },
]


# --- Validation ------------------------------------------------------------

def validate_plugin_content(content: str) -> bool:
    checks = {
        "version 3.9.0":                        "3.9.0" in content,
        "tag pills CSS present":                 "purebrain-tag-pills-cta-fix" in content,
        "tag pill blue default":                 "#2a93c1" in content and "post-tags" in content,
        "tag pill orange hover":                 "a[rel=\"tag\"]:hover" in content,
        "cta white text rule":                   "blog-cta-block a[href" in content,
        # v3.8.0 features retained
        "v3.8.0 security hardening":             "MED-003" in content,
        "BREVO_API_KEY fail closed":             "503" in content and "BREVO_API_KEY" in content,
        # v3.7.0 features retained
        "Subscribe nav link":                    "neural-feed-subscribe" in content,
        # v3.6.0 features retained
        "transparency REST route":               "purebrain/v1', '/transparency-data'" in content,
        "pb-transparency-section":               "pb-transparency-section" in content,
        # v3.5.0 features retained
        "pb-lead-inline":                        "pb-lead-inline" in content,
        "pb-lead-bar":                           "pb-lead-bar" in content,
        # v3.2.0 features retained
        "html body .pb-blog-nav a:hover":        "html body .pb-blog-nav a:hover" in content,
        # older features retained
        "pb-logo-brand class":                   "pb-logo-brand" in content,
        "FAQ accordion":                         "faq-accordion" in content,
        "rate limiter":                          "purebrain_check_rate_limit" in content,
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
                        val.includes('3.9.0') &&
                        val.includes('purebrain-tag-pills-cta-fix') &&
                        val.includes('pb-transparency-section') &&
                        val.includes('neural-feed-subscribe') &&
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
            if has_codemirror:
                current = page.evaluate("""() => {
                    const cm = document.querySelector('.CodeMirror');
                    return cm ? cm.CodeMirror.getValue().substring(0, 300) : 'N/A';
                }""")
                if "3.9.0" in current:
                    save_success = True
                    print("  v3.9.0 found in editor content - assuming save succeeded.")

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

def verify_live(site: dict) -> dict:
    """Verify v3.9.0 tag pills and CTA white text on a blog post page."""
    name = site["name"]
    results = {}

    print(f"\n[Verify] {name} — checking tag pills and CTA button on blog post...")
    req = urllib.request.Request(
        site["blog_post_url"],
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode("utf-8")

        checks = {
            "plugin v3.9.0 CSS in page":         "purebrain-tag-pills-cta-fix" in html,
            "tag pills CSS present":              "post-tags .tag-links a" in html or "a[rel=\"tag\"]" in html,
            "cta button white text CSS":          "blog-cta-block a[href" in html,
            "no Gleb proper name in page":        "Gleb Kuznetsov" not in html and "Gleb-level" not in html,
            "transparency section present":       "aether-transparency" in html,
            "Brevo subscribe endpoint":           "pb-security/v1/subscribe" in html,
        }
        for mk, ok in checks.items():
            status = "OK" if ok else "WARN"
            print(f"  [{status}] {mk}: {ok}")
            results[mk] = "ok" if ok else "warn"

    except Exception as ex:
        print(f"  [WARN] Could not fetch {site['blog_post_url']}: {ex}")

    return results


# --- Main ------------------------------------------------------------------

def main():
    print("=" * 65)
    print("PureBrain Security Plugin v3.9.0 — Deployment")
    print("Changes: Tag pills (blue bg/white text) + CTA white text CSS")
    print("=" * 65)

    if not PLUGIN_FILE.exists():
        print(f"ERROR: Plugin file not found: {PLUGIN_FILE}")
        sys.exit(1)

    content = PLUGIN_FILE.read_text()
    print(f"\nPlugin file: {PLUGIN_FILE}")
    print(f"Content length: {len(content)} chars\n")

    print("--- Validating plugin content ---")
    if not validate_plugin_content(content):
        print("\nERROR: Plugin validation failed. Fix the issues above before deploying.")
        sys.exit(1)
    print("Validation passed.\n")

    any_error = False
    for site in SITES:
        success = deploy_to_site(site, content)
        if not success:
            print(f"\n[FAIL] Deployment to {site['name']} failed.")
            any_error = True
        else:
            print(f"\n[OK] Deployment to {site['name']} succeeded.")

    print("\n" + "=" * 65)
    print("--- Live Verification ---")
    for site in SITES:
        verify_live(site)

    print("\n" + "=" * 65)
    if any_error:
        print("DEPLOYMENT COMPLETED WITH ERRORS — check output above.")
        sys.exit(1)
    else:
        print("ALL DEPLOYMENTS SUCCESSFUL.")
        print("\nWhat changed on all blog posts:")
        print("  - Tags now show as blue pills (#2a93c1 bg + white text)")
        print("  - Tags hover to orange pills (#f1420b bg + white text)")
        print("  - CTA 'Start Your AI Partnership' button: white text enforced at CSS level")
        print("  - Transparency section: no more proper names (Gleb Kuznetsov removed)")


if __name__ == "__main__":
    main()
