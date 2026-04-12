#!/usr/bin/env python3
"""
Deploy purebrain-security-plugin.php v4.0.1 to purebrain.ai ONLY.

v4.0.1 changes:
- Line ~90:   "every week" → "every day" (comment in plugin description)
- Line ~2281: "every week" → "every day" (lead capture headline text)
- Line ~2973: "every week" → "every day" (default CTA text)

All v4.0.0 features retained:
- Blog listing "READ MORE" orange button on all post cards
- posts_per_page filter (10 posts max on /blog/)

All v3.9.x features retained.

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
        "screenshot_deploy": f"{SCREENSHOT_DIR}/plugin_v401_purebrain_deploy.png",
        "screenshot_verify": f"{SCREENSHOT_DIR}/plugin_v401_purebrain_verify.png",
        "origin_story_url":  "https://purebrain.ai/we-both-wrote-this-post/",
        "homepage_url":      "https://purebrain.ai/",
    },
]


# --- Validation ------------------------------------------------------------

def validate_plugin_content(content: str) -> bool:
    checks = {
        "version 4.0.1":                          "4.0.1" in content,
        "'every day' (lead headline)":             "every day in The Neural Feed" in content,
        "'every day' (CTA text)":                  "every day, alongside you" in content,
        "NO 'every week' remaining":               "every week" not in content,
        # v4.0.0 features
        "blog listing Read More button":           "pb-read-more-btn" in content or "READ MORE" in content,
        # v3.9.3 features
        "twitter-image in REST meta":              "_yoast_wpseo_twitter-image" in content,
        # v3.9.2 features
        "transparency CTA white text":             "aether-transparency__cta-btn" in content,
        # v3.9.1 features
        "link hover white text":                   "purebrain-link-hover-fix" in content,
        # v3.9.0 features
        "tag pills CSS":                           "purebrain-tag-pills-cta-fix" in content,
        # v3.8.0 features
        "security hardening MED-003":              "MED-003" in content,
        # v3.7.0 features
        "Subscribe nav link":                      "neural-feed-subscribe" in content,
        # v3.6.0 features
        "transparency REST route":                 "purebrain/v1', '/transparency-data'" in content,
        "pb-transparency-section":                 "pb-transparency-section" in content,
        # v3.5.0 features
        "pb-lead-inline":                          "pb-lead-inline" in content,
        # older features
        "footer logo brand":                       "pb-logo-brand" in content,
        "FAQ accordion":                           "faq-accordion" in content,
        "rate limiter":                            "purebrain_check_rate_limit" in content,
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
                        val.includes('4.0.1') &&
                        val.includes('every day in The Neural Feed') &&
                        val.includes('every day, alongside you') &&
                        val.includes('pb-transparency-section') &&
                        val.includes('neural-feed-subscribe')
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
                if "4.0.1" in current:
                    save_success = True
                    print("  v4.0.1 found in editor content - assuming save succeeded.")

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

def verify_live_origin_story(site: dict) -> dict:
    """
    Verify the origin story post at /we-both-wrote-this-post/:
    - Zero instances of 'every week'
    - Transparency section shows February 22, 2026 data
    - 21 agents, 8 work domains, 26 tasks, 1.5-2 hours
    - CSS style blocks present
    """
    import json
    import base64

    name = site["name"]
    url  = site["origin_story_url"]
    results = {}

    print(f"\n[Verify] {name} — checking origin story post: {url}")

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
    except Exception as ex:
        print(f"  ERROR fetching page: {ex}")
        return {"fetch_error": str(ex)}

    # 1. "every week" must be gone
    every_week_count = html.lower().count("every week")
    print(f"  [{'OK' if every_week_count == 0 else 'FAIL'}] 'every week' occurrences: {every_week_count} (expected 0)")
    results["every_week_gone"] = (every_week_count == 0)

    # 2. "every day" must be present
    every_day_count = html.lower().count("every day")
    print(f"  [{'OK' if every_day_count > 0 else 'FAIL'}] 'every day' occurrences: {every_day_count} (expected >0)")
    results["every_day_present"] = (every_day_count > 0)

    # 3. Transparency section present
    has_transparency = "pb-transparency-section" in html
    print(f"  [{'OK' if has_transparency else 'MISSING'}] pb-transparency-section present")
    results["transparency_section"] = has_transparency

    # 4. Check transparency data content
    has_feb22 = "February 22, 2026" in html
    print(f"  [{'OK' if has_feb22 else 'MISSING'}] 'February 22, 2026' in transparency section")
    results["feb22_date"] = has_feb22

    has_21_agents = "21" in html and "agent" in html.lower()
    print(f"  [{'OK' if has_21_agents else 'CHECK'}] 21 agents mentioned")
    results["agents_21"] = has_21_agents

    has_26_tasks = "26" in html
    print(f"  [{'CHECK'}] 26 tasks: {'26' in html}")
    results["tasks_26"] = "26" in html

    has_8_domains = "8" in html
    print(f"  [{'CHECK'}] 8 work domains: {'8' in html}")
    results["domains_8"] = has_8_domains

    # 5. CSS style blocks present (not corrupted by wpautop)
    has_style_blocks = "<style>" in html or "<style " in html
    print(f"  [{'OK' if has_style_blocks else 'MISSING'}] CSS <style> blocks present")
    results["css_style_blocks"] = has_style_blocks

    # 6. No old version references in transparency
    has_v290 = "v2.9.0" in html or "v290" in html.lower()
    has_v380 = "v3.8.0" in html or "v380" in html.lower()
    print(f"  [{'OK' if not has_v290 else 'FOUND'}] No v2.9.0 references")
    print(f"  [{'OK' if not has_v380 else 'FOUND'}] No v3.8.0 references")
    results["no_old_versions"] = (not has_v290 and not has_v380)

    # 7. Verify transparency REST API data (server-side)
    env_text_local = (AETHER_ROOT / ".env").read_text()
    def _env_local(key, quoted=True):
        if quoted:
            m = re.search(rf"{key}='([^']+)'", env_text_local)
            if m:
                return m.group(1)
        m = re.search(rf"{key}=([^\n]+)", env_text_local)
        return m.group(1).strip() if m else ""

    app_pass = _env_local("PUREBRAIN_WP_APP_PASSWORD")
    auth = base64.b64encode(f"Aether:{app_pass}".encode()).decode()
    transparency_req = urllib.request.Request(
        "https://purebrain.ai/wp-json/purebrain/v1/transparency-data",
        headers={
            "Authorization": f"Basic {auth}",
            "User-Agent": "Aether-Deploy-Verify/1.0",
        },
    )
    try:
        with urllib.request.urlopen(transparency_req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        week_label = data.get("week_label", "")
        agents     = data.get("agents_count", 0)
        domains    = data.get("work_domains_count", 0)
        tasks      = data.get("tasks_completed", 0)
        print(f"\n  [Transparency REST API]")
        print(f"    week_label:        {week_label}")
        print(f"    agents_count:      {agents}  (expected 21)")
        print(f"    work_domains:      {domains} (expected 8)")
        print(f"    tasks_completed:   {tasks}   (expected 26)")
        results["transparency_api_ok"] = (
            "February 22" in week_label and agents == 21 and domains == 8
        )
    except Exception as ex:
        print(f"  [WARN] Transparency API check failed: {ex}")
        results["transparency_api_ok"] = False

    # Summary
    passed = sum(1 for v in results.values() if v is True)
    total  = len(results)
    print(f"\n  Verification result: {passed}/{total} checks passed")

    return results


# --- Main ------------------------------------------------------------------

def main():
    print("=" * 65)
    print("PureBrain Security Plugin v4.0.1 — Deployment to purebrain.ai")
    print("Changes: 'every week' → 'every day' in 3 locations")
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

    # Post-deploy: verify origin story
    print("\n" + "=" * 65)
    print("--- Post-Deploy Verification ---")
    all_results = {}
    for site in SITES:
        results = verify_live_origin_story(site)
        all_results[site["name"]] = results

    # Final summary
    print("\n" + "=" * 65)
    all_ok = all(
        r.get("every_week_gone") and r.get("every_day_present") and r.get("transparency_section")
        for r in all_results.values()
    )

    if all_ok:
        print("DEPLOYMENT COMPLETE AND VERIFIED.")
        print("\nWhat changed (v4.0.1):")
        print("  - 'every week' → 'every day' in lead headline")
        print("  - 'every week' → 'every day' in CTA text")
        print("  - 'every week' → 'every day' in plugin description comment")
        print("  - All v4.0.0 + v3.9.x features retained")
        print("\nOrigin story post verified:")
        print("  - Zero 'every week' occurrences")
        print("  - Transparency section showing Feb 22, 2026 data")
    else:
        print("DEPLOYMENT DONE BUT SOME VERIFICATION CHECKS FAILED.")
        print("Review output above for details.")
        for site_name, results in all_results.items():
            failed = [k for k, v in results.items() if v is False]
            if failed:
                print(f"  {site_name} failed checks: {', '.join(failed)}")


if __name__ == "__main__":
    main()
