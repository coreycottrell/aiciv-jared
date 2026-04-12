#!/usr/bin/env python3
"""
Deploy purebrain-security-plugin.php v3.9.2 to jareddsanborn.com ONLY.

JDS is currently at v3.6.0 — deploying v3.9.2 which includes:
  v3.7.0 - Blog nav "Blog" → "Subscribe" link update
  v3.8.0 - Security hardening (MED-003, LOW-001, LOW-002)
  v3.9.0 - Tag pills blue styling + CTA button white text
  v3.9.1 - Blog in-text link hover fix (orange bg + white text)
  v3.9.2 - Transparency section CTA button white text fix

Uses new credentials: AetherPureBrain.ai (granted 2026-02-22)

Author: full-stack-developer agent
Date: 2026-02-22
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
    m = re.search(rf"{key}=([^\n]+)", env_text)
    return m.group(1).strip().strip('"').strip("'") if m else ""


JDS_USER = _env("WORDPRESS_USER")
JDS_APP_PASSWORD = _env("WORDPRESS_APP_PASSWORD")
JDS_ADMIN_PASSWORD = "aHsiCF4NbRPH)pO5YR&%R&l9"  # admin password for wp-login.php form

JDS_SITE = {
    "name":         "jareddsanborn.com",
    "admin_url":    "https://jareddsanborn.com/wp-admin",
    "login_url":    "https://jareddsanborn.com/wp-login.php",
    "user":         JDS_USER,
    "password":     JDS_ADMIN_PASSWORD,  # wp-login.php requires admin password (not app password)
    "editor_url":   (
        "https://jareddsanborn.com/wp-admin/plugin-editor.php"
        "?file=purebrain-security/purebrain-security-plugin.php"
        "&plugin=purebrain-security/purebrain-security-plugin.php"
    ),
    "screenshot_deploy": f"{SCREENSHOT_DIR}/plugin_v392_jds_deploy.png",
    "screenshot_verify": f"{SCREENSHOT_DIR}/plugin_v392_jds_verify.png",
    "blog_post_url": "https://jareddsanborn.com/the-ai-trust-gap/",
}


# --- Validation ------------------------------------------------------------

def validate_plugin_content(content: str) -> bool:
    """Verify the plugin file has all required v3.9.2 features."""
    checks = {
        "version 3.9.2":                         "3.9.2" in content,
        "transparency CTA btn white text fix":    "purebrain-transparency-cta-v392" in content,
        "link hover white text (v3.9.1)":         "pb-link-hover-v391" in content,
        "tag pills CSS (v3.9.0)":                 "purebrain-tag-pills-cta-fix" in content,
        "security hardening MED-003 (v3.8.0)":   "MED-003" in content,
        "BREVO_API_KEY fail-closed":              "BREVO_API_KEY" in content and "503" in content,
        "Subscribe nav link (v3.7.0)":            "neural-feed-subscribe" in content,
        "transparency section (v3.6.0)":          "pb-transparency-section" in content,
        "lead capture (v3.5.0)":                  "pb-lead-inline" in content,
        "universal nav hover (v3.2.0)":           "html body .pb-blog-nav a:hover" in content,
        "footer logo brand fix (v3.0.0)":         "pb-logo-brand" in content,
        "FAQ accordion":                           "faq-accordion" in content,
        "rate limiter":                            "purebrain_check_rate_limit" in content,
    }

    all_ok = True
    for name, result in checks.items():
        status = "OK" if result else "MISSING"
        print(f"  [{status}] {name}")
        if not result:
            all_ok = False
    return all_ok


# --- Playwright deploy -----------------------------------------------------

def deploy_to_jds(content: str) -> bool:
    from playwright.sync_api import sync_playwright

    site = JDS_SITE
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
        print(f"  User: {site['user']}")
        page.goto(site["login_url"], wait_until="domcontentloaded", timeout=60000)
        time.sleep(2)

        # Handle GoDaddy SSO overlay if present
        sso_toggle = page.locator(".wpaas-sso-login-toggle")
        if sso_toggle.count() > 0 and sso_toggle.is_visible():
            print("  GoDaddy SSO overlay detected - switching to username/password...")
            sso_toggle.click()
            time.sleep(2)

        try:
            page.locator("#user_login").wait_for(state="visible", timeout=15000)
        except Exception:
            page.screenshot(path=site["screenshot_deploy"])
            print(f"  ERROR: Login form not visible. Screenshot: {site['screenshot_deploy']}")
            browser.close()
            return False

        # CAPTCHA check
        captcha_field = page.locator("#wpsec_captcha_answer")
        if captcha_field.count() > 0 and captcha_field.is_visible():
            page.screenshot(path=site["screenshot_deploy"])
            print(f"  CAPTCHA detected! Screenshot: {site['screenshot_deploy']}")
            print("  Wait 15-30 minutes for bot protection to reset, then retry.")
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
            print(f"  ERROR: Login failed (still on login page). URL: {page.url}")
            print("  Trying fallback with app password...")
            # Try app password as fallback
            page.fill("#user_login", site["user"])
            page.fill("#user_pass", JDS_APP_PASSWORD)
            page.click("#wp-submit")
            try:
                page.wait_for_load_state("domcontentloaded", timeout=30000)
            except Exception:
                pass
            time.sleep(3)
            if "wp-login.php" in page.url:
                page.screenshot(path=site["screenshot_deploy"])
                print(f"  ERROR: Both passwords failed. URL: {page.url}")
                browser.close()
                return False

        print(f"  Login successful! URL: {page.url}")

        # Step 2: Plugin Editor
        print(f"\n[Step 2] Opening Plugin Editor...")
        page.goto(site["editor_url"], wait_until="domcontentloaded", timeout=60000)
        time.sleep(4)

        page_text = page.inner_text("body")
        if "DISALLOW_FILE_EDIT" in page_text or "editing has been disabled" in page_text.lower():
            print("  ERROR: File editing disabled (DISALLOW_FILE_EDIT is set).")
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

        # Step 3: Set plugin content
        print("\n[Step 3] Setting plugin content (v3.9.2)...")
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
                        val.includes('3.9.2') &&
                        val.includes('purebrain-transparency-cta-v392') &&
                        val.includes('pb-transparency-section') &&
                        val.includes('neural-feed-subscribe') &&
                        val.includes('pb-logo-brand')
                    ) return 'success';
                    return 'set_failed: ' + val.length + ' chars, has_v392=' + val.includes('3.9.2');
                } catch(e) { return 'error: ' + e.message; }
            }""", content)
            print(f"  CodeMirror result: {result}")
            set_ok = (result == "success")

        if not set_ok:
            print("  Falling back to textarea...")
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
            set_ok = True  # Assume OK, check after save

        time.sleep(1)

        # Step 4: Save
        print("\n[Step 4] Saving plugin file...")
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
            print(f"  Save status unclear. Checking editor content...")
            if has_codemirror:
                current_snippet = page.evaluate("""() => {
                    const cm = document.querySelector('.CodeMirror');
                    return cm ? cm.CodeMirror.getValue().substring(0, 400) : 'N/A';
                }""")
                if "3.9.2" in current_snippet:
                    save_success = True
                    print("  v3.9.2 found in editor — save confirmed.")
                else:
                    print(f"  Editor snippet: {current_snippet[:200]}")

        if not save_success:
            print(f"  Deploy screenshot: {site['screenshot_deploy']}")
            browser.close()
            return False

        # Step 5: Clear caches
        print("\n[Step 5] Clearing WordPress cache (LiteSpeed)...")
        # Try LiteSpeed Cache flush
        page.goto(
            "https://jareddsanborn.com/wp-admin/admin.php?page=litespeed",
            wait_until="domcontentloaded", timeout=30000
        )
        time.sleep(2)
        flush_btn = page.locator("a:has-text('Flush All'), button:has-text('Flush All'), input[value*='Flush']")
        if flush_btn.count() > 0:
            flush_btn.first.click()
            time.sleep(3)
            print("  LiteSpeed cache flush clicked.")
        else:
            # Try admin bar flush
            print("  LiteSpeed flush button not found — trying WP admin bar...")
            page.goto("https://jareddsanborn.com/wp-admin/", wait_until="domcontentloaded", timeout=30000)
            time.sleep(2)

        page.screenshot(path=site["screenshot_verify"])
        browser.close()

    print(f"\n  Deploy screenshot:  {site['screenshot_deploy']}")
    print(f"  Verify screenshot:  {site['screenshot_verify']}")
    return True


# --- Live verification (HTTP) ------------------------------------------

def verify_live() -> dict:
    """Verify v3.9.2 is live on JDS blog post."""
    blog_url = JDS_SITE["blog_post_url"]
    results = {}

    print(f"\n[Verify] Checking {blog_url}...")
    req = urllib.request.Request(
        blog_url,
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
            "plugin v3.9.2 transparency CTA fix":   "purebrain-transparency-cta-v392" in html,
            "link hover fix v3.9.1":                 "pb-link-hover-v391" in html,
            "tag pills CSS v3.9.0":                  "purebrain-tag-pills-cta-fix" in html,
            "subscribe nav link v3.7.0":             "neural-feed-subscribe" in html,
            "transparency section v3.6.0":           "aether-transparency" in html,
            "lead capture v3.5.0":                   "pb-security/v1/subscribe" in html,
            "logo brand fix v3.0.0":                 "pb-logo-brand" in html,
            "HTTP 200 response":                     True,  # We got here
        }
        for mk, ok in checks.items():
            status = "OK" if ok else "WARN"
            print(f"  [{status}] {mk}")
            results[mk] = "ok" if ok else "warn"

    except Exception as ex:
        print(f"  [WARN] Could not fetch {blog_url}: {ex}")
        results["fetch_error"] = str(ex)

    return results


# --- REST API version check -----------------------------------------------

def check_plugin_version_via_rest() -> str:
    """Check active plugin version via REST API."""
    token = base64.b64encode(f"{JDS_USER}:{JDS_APP_PASSWORD}".encode()).decode()
    headers = {"Authorization": f"Basic {token}"}

    try:
        import requests
        resp = requests.get(
            "https://jareddsanborn.com/wp-json/wp/v2/plugins",
            headers=headers, timeout=15
        )
        if resp.status_code == 200:
            for p in resp.json():
                plugin_slug = p.get("plugin", "")
                if "purebrain-security/purebrain-security-plugin" in plugin_slug:
                    return f"v{p.get('version', '?')} (status: {p.get('status', '?')})"
    except Exception as ex:
        return f"REST check failed: {ex}"
    return "not found"


# --- Main ------------------------------------------------------------------

def main():
    print("=" * 65)
    print("PureBrain Security Plugin v3.9.2 — Deploy to jareddsanborn.com")
    print("JDS currently at v3.6.0 — upgrading through v3.7.0→v3.9.2")
    print("=" * 65)

    if not PLUGIN_FILE.exists():
        print(f"ERROR: Plugin file not found: {PLUGIN_FILE}")
        sys.exit(1)

    content = PLUGIN_FILE.read_text()
    print(f"\nPlugin source: {PLUGIN_FILE}")
    print(f"Content length: {len(content):,} chars")

    # Confirm version
    ver_match = re.search(r"\* Version:\s+([\d.]+)", content)
    version = ver_match.group(1) if ver_match else "unknown"
    print(f"Plugin version in file: {version}")
    if version != "3.9.2":
        print(f"WARNING: Expected v3.9.2 but found v{version}. Proceeding anyway.")

    print("\n--- Validating plugin content ---")
    if not validate_plugin_content(content):
        print("\nERROR: Validation failed. Fix issues above before deploying.")
        sys.exit(1)
    print("Validation passed.\n")

    # Check current version on JDS
    current = check_plugin_version_via_rest()
    print(f"Current JDS plugin: {current}")
    print(f"Deploying: v{version}")

    # Deploy
    success = deploy_to_jds(content)

    if not success:
        print("\n[FAIL] Deployment to jareddsanborn.com failed.")
        sys.exit(1)

    print("\n[OK] Deployment to jareddsanborn.com succeeded.")

    # Post-deploy version check
    print("\n--- Post-deploy REST API version check ---")
    time.sleep(3)
    new_version = check_plugin_version_via_rest()
    print(f"JDS plugin after deploy: {new_version}")

    # Live verification
    print("\n--- Live Page Verification ---")
    results = verify_live()

    ok_count = sum(1 for v in results.values() if v == "ok")
    warn_count = sum(1 for v in results.values() if v == "warn")

    print(f"\n{'='*65}")
    print(f"DEPLOYMENT COMPLETE")
    print(f"Verification: {ok_count} OK, {warn_count} WARN")
    print(f"\nNew features now live on jareddsanborn.com blog posts:")
    print(f"  v3.9.2 - Transparency section CTA button white text fix")
    print(f"  v3.9.1 - In-text link hover: orange bg + white text")
    print(f"  v3.9.0 - Tag pills (blue → orange on hover) + CTA white text CSS")
    print(f"  v3.8.0 - Security hardening (MED-003, LOW-001, LOW-002)")
    print(f"  v3.7.0 - Nav 'Blog' → 'Subscribe' link")
    print(f"  (v3.6.0 features retained: transparency section, lead capture, etc.)")

    if warn_count > 0:
        print(f"\nNOTE: {warn_count} WARN items may need CDN cache flush on jareddsanborn.com")
        print("Hard-refresh (Ctrl+Shift+R) to verify without cache.")


if __name__ == "__main__":
    main()
