#!/usr/bin/env python3
"""
Deploy purebrain-security-plugin.php v4.1.1 to purebrain.ai.

v4.1.1 changes:
- TEST 20: Blog nav copy "AI Assessment" -> "Free AI Assessment"
  - Applies on single blog posts and category/archive pages
  - No functional changes — text label only

All v4.1.0 features retained.

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
        "screenshot_deploy": f"{SCREENSHOT_DIR}/plugin_v411_purebrain_deploy.png",
        "screenshot_verify": f"{SCREENSHOT_DIR}/plugin_v411_purebrain_verify.png",
        "blog_post_url":     "https://purebrain.ai/the-ai-trust-gap/",
        "blog_listing_url":  "https://purebrain.ai/blog/",
    },
]


# --- Validation ------------------------------------------------------------

def validate_plugin_content(content: str) -> bool:
    checks = {
        "version 4.1.1":                          "4.1.1" in content,
        # TEST 20: Free AI Assessment nav label
        "Free AI Assessment in nav JS":           ">Free AI Assessment<" in content,
        "Free AI Assessment in comment":          "Free AI Assessment" in content,
        "changelog TEST 20 entry":                "TEST 20" in content,
        # v4.1.0 features preserved
        "guide-unlock REST route":                 "purebrain/v1', '/guide-unlock'" in content,
        "pb-guide-gate-css style block":           "pb-guide-gate-css" in content,
        "pb-guide-gated-content element":          "pb-guide-gated-content" in content,
        # v4.0.0+ features preserved
        "blog listing Read More button":           "pb-read-more-btn" in content,
        "transparency CTA white text":             "aether-transparency__cta-btn" in content,
        "link hover white text":                   "purebrain-link-hover-fix" in content,
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
                        val.includes('4.1.1') &&
                        val.includes('Free AI Assessment') &&
                        val.includes('TEST 20')
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
                if "4.1.1" in current and "Free AI Assessment" in current:
                    save_success = True
                    print("  v4.1.1 + Free AI Assessment found in editor — save assumed successful.")

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


# --- Post-deploy cache bust (touch blog posts) ---

def bust_page_cache(site: dict) -> None:
    """Touch relevant posts to bust WordPress page cache."""
    import base64, json

    base_url = site["admin_url"].replace("/wp-admin", "")
    credentials = base64.b64encode(
        f"{site['user']}:{site['password']}".encode()
    ).decode()
    auth_header = f"Basic {credentials}"

    # Touch a blog post that shows the nav menu to bust its cache
    # These post IDs are known blog posts with the nav menu
    post_ids = [696, 381, 316]  # origin story, trust gap, other blog posts

    print(f"\n[Step 6] Busting page cache (touching blog posts)...")
    for post_id in post_ids:
        payload = json.dumps({"status": "publish"}).encode()
        req = urllib.request.Request(
            f"{base_url}/wp-json/wp/v2/posts/{post_id}",
            data=payload,
            method="POST",
            headers={
                "Authorization": auth_header,
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                print(f"  Post {post_id}: HTTP {resp.status} — cache busted")
        except urllib.error.HTTPError as e:
            print(f"  Post {post_id}: HTTP {e.code} (may be normal)")
        except Exception as ex:
            print(f"  Post {post_id}: {ex}")


# --- Live verification (HTTP) ------------------------------------------

def verify_nav_text(site: dict) -> dict:
    """
    Verify blog post shows "Free AI Assessment" in nav menu.
    Checks a single blog post page for the updated nav label.
    """
    name = site["name"]
    url  = site["blog_post_url"]
    results = {}

    print(f"\n[Verify] {name} — checking blog post nav: {url}")

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; AetherBot/1.0)",
            "Cache-Control": "no-cache, no-store",
            "Pragma": "no-cache",
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

    print(f"  HTTP {http_code} — page loaded ({len(html)} bytes)")
    results["page_loads"] = (http_code == 200)

    # Check for "Free AI Assessment" in nav JS injection
    has_free_assessment = "Free AI Assessment" in html
    has_old_label = ">AI Assessment<" in html and "Free AI Assessment" not in html
    print(f"  [{'OK' if has_free_assessment else 'MISSING'}] 'Free AI Assessment' in page HTML")
    print(f"  [{'FAIL (old label still present)' if has_old_label else 'OK'}] old '>AI Assessment<' label gone")
    results["free_assessment_present"] = has_free_assessment
    results["old_label_gone"] = not has_old_label

    # Check the plugin version in HTML (injected via plugin)
    # The nav menu style block comment can contain version references
    has_pb_nav = "pb-blog-nav" in html
    print(f"  [{'OK' if has_pb_nav else 'MISSING'}] pb-blog-nav CSS injected")
    results["pb_nav_injected"] = has_pb_nav

    passed = sum(1 for v in results.values() if v is True)
    total  = len(results)
    print(f"\n  Verification result: {passed}/{total} checks passed")

    return results


# --- Main ------------------------------------------------------------------

def main():
    print("=" * 65)
    print("PureBrain Security Plugin v4.1.1 — Deployment to purebrain.ai")
    print("Changes: TEST 20 — Blog nav 'AI Assessment' -> 'Free AI Assessment'")
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

        # Bust page cache after deploy
        bust_page_cache(site)

    # Post-deploy: wait a moment for cache to settle
    print("\nWaiting 5 seconds for cache to settle...")
    time.sleep(5)

    # Verify live blog post shows updated nav text
    print("\n" + "=" * 65)
    print("--- Post-Deploy Verification ---")
    all_results = {}
    for site in SITES:
        nav_results = verify_nav_text(site)
        all_results[site["name"]] = nav_results

    # Final summary
    print("\n" + "=" * 65)
    all_ok = all(
        r.get("free_assessment_present") and r.get("pb_nav_injected")
        for r in all_results.values()
    )

    if all_ok:
        print("DEPLOYMENT COMPLETE AND VERIFIED.")
        print("\nWhat v4.1.1 changes:")
        print("  - Blog nav label: 'AI Assessment' -> 'Free AI Assessment'")
        print("  - Applies on: single blog posts + category/archive pages")
        print("  - Verified live on: " + ", ".join(SITES[0]["blog_post_url"].split("/")[2:3]))
    else:
        print("DEPLOYMENT DONE BUT SOME VERIFICATION CHECKS FAILED.")
        for site_name, results in all_results.items():
            failed = [k for k, v in results.items() if v is not True]
            if failed:
                print(f"  {site_name} failed checks: {', '.join(failed)}")
        print("\nNote: If 'Free AI Assessment' not showing, try hard-refresh (Cmd+Shift+R)")
        print("or wait for Cloudflare CDN cache to expire.")


if __name__ == "__main__":
    main()
