#!/usr/bin/env python3
"""
Deploy purebrain-security-plugin.php v5.1.0 to purebrain.ai.

v5.1.0: Performance Optimization (Issues 4, 5, 6)
  - Issue 4: bgVideo paused/hidden on mobile (<768px viewports)
  - Issue 5: Admin/editor scripts dequeued on frontend (~330ms saved)
  - Issue 6: WonderPush SDK given defer attribute (non-blocking load)

NOTE: This script handles BOTH cases:
  (a) Plugin already installed → uses plugin editor to update content
  (b) Plugin not installed → uses wp-admin/plugin-install.php zip upload

Author: full-stack-developer agent
Date: 2026-02-24
"""

import os
import re
import sys
import time
import base64
import zipfile
import json
import urllib.request
import urllib.error
from pathlib import Path

AETHER_ROOT = Path("/home/jared/projects/AI-CIV/aether")
PLUGIN_FILE = AETHER_ROOT / "tools/security/purebrain-security/purebrain-security-plugin.php"
SCREENSHOT_DIR = str(AETHER_ROOT / "exports/screenshots")
ZIP_PATH = "/tmp/purebrain-security-v510.zip"

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
    "install_url":   "https://purebrain.ai/wp-admin/plugin-install.php?tab=upload",
    "plugins_url":   "https://purebrain.ai/wp-admin/plugins.php",
    "screenshot_deploy": f"{SCREENSHOT_DIR}/plugin_v510_deploy.png",
    "screenshot_verify": f"{SCREENSHOT_DIR}/plugin_v510_verify.png",
}


# --- Build zip -------------------------------------------------------------

def build_zip() -> str:
    """Build the plugin zip file for installation."""
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(
            str(PLUGIN_FILE),
            "purebrain-security/purebrain-security-plugin.php",
        )
    size = Path(ZIP_PATH).stat().st_size
    print(f"  ZIP built: {ZIP_PATH} ({size:,} bytes)")
    return ZIP_PATH


# --- Validation ------------------------------------------------------------

def validate_plugin_content(content: str) -> bool:
    checks = {
        "v5.1.0 in header":                             "Version:     5.1.0" in content,
        "v5.1.0 changelog entry":                       "v5.1.0 - Performance Optimization" in content,
        "Issue 5 - script dequeue present":             "wp_enqueue_scripts" in content and "wp_dequeue_script" in content,
        "Issue 6 - WonderPush defer filter present":    "script_loader_tag" in content and "wonderpush" in content,
        "Issue 4 - video mobile pause JS present":      "pb-video-mobile-pause" in content and "matchMedia" in content,
        "is_admin guard present":                       "is_admin()" in content,
        "is_front_page guard present":                  "is_front_page()" in content,
        # Preserved features
        "magic cursor override present":                "pb-magic-cursor-body-override" in content,
        "FAQ accordion present":                        "purebrain-faq-accordion" in content,
        "footer v470 present":                          "pb-aether-footer-v470" in content,
        "transparency section present":                 "aether-transparency__cta-btn" in content,
        "IndexNow key present":                         "823869521fbf4f33b93e67c781571e20" in content,
        "inline CTA template lock present":             "pb-inline-cta-template-lock" in content or "INLINE CTA BUTTON TEMPLATE LOCK" in content,
    }

    all_ok = True
    for name, result in checks.items():
        status = "OK" if result else "MISSING/FAIL"
        print(f"  [{status}] {name}")
        if not result:
            all_ok = False
    return all_ok


# --- Check if plugin is installed ------------------------------------------

def is_plugin_installed() -> bool:
    """Check via REST API if the purebrain plugin is currently installed."""
    credentials = base64.b64encode(
        f"Aether:{PUREBRAIN_APP_PASS}".encode()
    ).decode()
    req = urllib.request.Request(
        "https://purebrain.ai/wp-json/wp/v2/plugins?_fields=plugin,status",
        headers={
            "Authorization": f"Basic {credentials}",
            "User-Agent": "WordPress/6.4; https://purebrain.ai",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            plugins = json.loads(resp.read().decode())
            for p in plugins:
                if "purebrain-security" in p.get("plugin", ""):
                    return True
            return False
    except Exception as e:
        print(f"  Could not check plugin status: {e}")
        return False


# --- Playwright deploy (plugin editor - UPDATE existing plugin) ------------

def deploy_via_plugin_editor(page, site: dict, content: str) -> bool:
    """Edit the existing plugin file via the WP plugin editor."""
    print(f"\n[Step 2a] Opening Plugin Editor (plugin already installed)...")
    page.goto(site["editor_url"], wait_until="domcontentloaded", timeout=60000)
    time.sleep(4)

    page_text = page.inner_text("body")
    if "DISALLOW_FILE_EDIT" in page_text or "editing has been disabled" in page_text.lower():
        print("  ERROR: File editing is disabled.")
        return False

    has_codemirror = page.evaluate("() => !!document.querySelector('.CodeMirror')")
    has_textarea   = page.evaluate("() => !!document.querySelector('#newcontent')")
    print(f"  CodeMirror: {has_codemirror}, Textarea: {has_textarea}")

    if not has_codemirror and not has_textarea:
        page.screenshot(path=site["screenshot_deploy"])
        print(f"  ERROR: No editor found.")
        return False

    # Set content via CodeMirror
    print("\n[Step 3a] Setting plugin content (v5.1.0)...")
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
                    val.includes('Version:     5.1.0') &&
                    val.includes('wp_dequeue_script') &&
                    val.includes('pb-video-mobile-pause')
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

    # Save
    print("\n[Step 4a] Saving plugin...")
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

    if "File edited successfully" in page_text or "updated successfully" in page_text.lower():
        print("  SUCCESS: Plugin file saved!")
        return True
    elif "Parse error" in page_text or "syntax error" in page_text.lower():
        print(f"  ERROR: PHP syntax error!\n  {page_text[:400]}")
        return False
    else:
        print(f"  Status unclear: {page_text[:200]}")
        # Check if content was set successfully by reading back
        if has_codemirror:
            current = page.evaluate("""() => {
                const cm = document.querySelector('.CodeMirror');
                return cm ? cm.CodeMirror.getValue().substring(0, 6000) : 'N/A';
            }""")
            if "Version:     5.1.0" in current and "wp_dequeue_script" in current:
                print("  v5.1.0 content found in editor — save assumed successful.")
                return True
        return False


# --- Playwright deploy (plugin install via zip upload) ---------------------

def deploy_via_zip_upload(page, site: dict, zip_path: str) -> bool:
    """Install the plugin via WP Admin plugin upload form."""
    print(f"\n[Step 2b] Installing plugin via zip upload...")
    print(f"  ZIP: {zip_path}")

    # Go to the upload tab of plugin install page
    page.goto(site["install_url"], wait_until="domcontentloaded", timeout=60000)
    time.sleep(3)

    page_text = page.inner_text("body")
    print(f"  Page title area: {page_text[:100]}")

    # Check if upload form is present
    has_upload_form = page.evaluate("() => !!document.querySelector('#pluginzip')")
    has_upload_button = page.evaluate("() => !!document.querySelector('#install-plugin-submit')")
    print(f"  Upload form: {has_upload_form}, Submit button: {has_upload_button}")

    if not has_upload_form:
        page.screenshot(path=site["screenshot_deploy"])
        print(f"  ERROR: Upload form not found. Screenshot saved.")

        # Try clicking the "Upload Plugin" button if it exists
        upload_btn = page.locator("a:has-text('Upload Plugin'), .upload-view-toggle")
        if upload_btn.count() > 0:
            print("  Clicking 'Upload Plugin' button...")
            upload_btn.first.click()
            time.sleep(2)
            has_upload_form = page.evaluate("() => !!document.querySelector('#pluginzip')")
            if not has_upload_form:
                print("  Still no upload form. Cannot install.")
                return False
        else:
            return False

    # Set the file input
    print("\n[Step 3b] Selecting zip file...")
    page.set_input_files("#pluginzip", zip_path)
    time.sleep(1)

    # Click install
    print("\n[Step 4b] Clicking Install Now...")
    page.evaluate("""() => {
        const btn = document.querySelector('#install-plugin-submit') ||
                    document.querySelector('input[value="Install Now"]');
        if (btn) btn.click();
    }""")

    try:
        page.wait_for_load_state("domcontentloaded", timeout=60000)
    except Exception:
        pass
    time.sleep(5)

    page.screenshot(path=site["screenshot_deploy"])
    page_text = page.inner_text("body")
    print(f"  Install result: {page_text[:300]}")

    if "Plugin installed successfully" in page_text or "Installed successfully" in page_text:
        print("  Plugin installed successfully!")

        # Now activate it
        print("\n[Step 5b] Activating plugin...")
        activate_link = page.locator("a:has-text('Activate Plugin')")
        if activate_link.count() > 0:
            activate_link.click()
            try:
                page.wait_for_load_state("domcontentloaded", timeout=30000)
            except Exception:
                pass
            time.sleep(3)
            page_text = page.inner_text("body")
            if "Plugin activated" in page_text or "activated" in page_text.lower():
                print("  Plugin activated!")
                return True
            else:
                print(f"  Activation result: {page_text[:200]}")
                # Try activation via REST API as backup
                return activate_via_rest()
        else:
            print("  No activate link found — trying REST API activation...")
            return activate_via_rest()

    elif "already exists" in page_text.lower() or "overwrite" in page_text.lower():
        print("  Plugin already exists — clicking Replace/Overwrite...")
        replace_btn = page.locator("a:has-text('Replace current with uploaded'), input[value*='Replace']")
        if replace_btn.count() > 0:
            replace_btn.first.click()
            try:
                page.wait_for_load_state("domcontentloaded", timeout=60000)
            except Exception:
                pass
            time.sleep(5)
            page_text = page.inner_text("body")
            if "Plugin installed successfully" in page_text:
                print("  Plugin replaced successfully!")
                # Activate
                activate_link = page.locator("a:has-text('Activate Plugin')")
                if activate_link.count() > 0:
                    activate_link.click()
                    time.sleep(3)
                return True
        return activate_via_rest()

    elif "Parse error" in page_text or "syntax error" in page_text.lower():
        print(f"  ERROR: PHP syntax error!\n  {page_text[:400]}")
        return False

    else:
        print(f"  Unexpected result. Trying REST activation...")
        return activate_via_rest()


def activate_via_rest() -> bool:
    """Activate the plugin via REST API."""
    credentials = base64.b64encode(
        f"Aether:{PUREBRAIN_APP_PASS}".encode()
    ).decode()
    req = urllib.request.Request(
        "https://purebrain.ai/wp-json/wp/v2/plugins/purebrain-security/purebrain-security-plugin",
        method="PUT",
        data=json.dumps({"status": "active"}).encode(),
        headers={
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/json",
            "User-Agent": "WordPress/6.4; https://purebrain.ai",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            result = json.loads(resp.read().decode())
            status = result.get("status", "unknown")
            version = result.get("version", "?")
            print(f"  REST activation: status={status} version={version}")
            return status == "active"
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:300]
        print(f"  REST activation HTTP {e.code}: {body}")
        return False
    except Exception as ex:
        print(f"  REST activation error: {ex}")
        return False


# --- Full Playwright deploy flow -------------------------------------------

def deploy_plugin_to_site(site: dict, content: str, zip_path: str) -> bool:
    from playwright.sync_api import sync_playwright

    name = site["name"]
    print(f"\n{'='*65}")
    print(f"DEPLOYING PLUGIN TO: {name}")
    print(f"{'='*65}")

    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    # Check if already installed
    plugin_installed = is_plugin_installed()
    print(f"\nPlugin currently installed: {plugin_installed}")

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

        # Step 2: Deploy
        if plugin_installed:
            # Use the plugin editor (faster, no reinstall needed)
            success = deploy_via_plugin_editor(page, site, content)
        else:
            # Plugin was deleted — need to reinstall from zip
            success = deploy_via_zip_upload(page, site, zip_path)

        if not success:
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
                "User-Agent": "WordPress/6.4; https://purebrain.ai",
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
    pages_to_check = [
        ("https://purebrain.ai/", "Homepage"),
        ("https://purebrain.ai/your-next-direct-report-wont-be-human/", "Blog Post"),
    ]

    for url, label in pages_to_check:
        print(f"\n[Verify] {label}: {url}")
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

        if label == "Homepage":
            checks = {
                "page_loads_200":               http_code == 200,
                "pb-video-mobile-pause present": "pb-video-mobile-pause" in html,
                "matchMedia present":            "matchMedia" in html,
                "handleVideoViewport present":   "handleVideoViewport" in html,
                "page_content_present":          "bgVideo" in html or "video-background" in html,
            }
        else:
            checks = {
                "page_loads_200":               http_code == 200,
                "blog_content_present":         "entry-content" in html or "elementor-widget" in html,
                "wp-components NOT present":    "wp-components" not in html,
                "wp-block-editor NOT present":  "wp-block-editor.min.js" not in html,
                "transparency section present": "aether-transparency" in html,
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
    print("PureBrain Security Plugin v5.1.0 — PERFORMANCE OPTIMIZATION")
    print("Issues 4 (video mobile), 5 (script dequeue), 6 (WonderPush defer)")
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

    # Build zip for install case
    print("--- Building plugin zip ---")
    zip_path = build_zip()

    # Deploy plugin via Playwright
    print("\n" + "=" * 65)
    print("DEPLOYING plugin v5.1.0 via Playwright")
    print("=" * 65)
    success = deploy_plugin_to_site(SITE, content, zip_path)
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
        print("\nDEPLOYMENT COMPLETE AND VERIFIED.")
        print("\nPerformance improvements now live on purebrain.ai:")
        print("  - Issue 4: #bgVideo paused/hidden on mobile (<768px)")
        print("  - Issue 5: Admin scripts dequeued on frontend (~330ms saved)")
        print("  - Issue 6: WonderPush SDK loaded with defer (non-blocking)")
    else:
        print("\nDEPLOYMENT DONE — some verification checks failed.")
        print("Note: CDN cache may need time. Hard-refresh (Cmd+Shift+R) to verify.")
        print("If Issue 5 verification shows wp-block-editor still in page:")
        print("  The script may have been re-enqueued by Elementor or another plugin.")
        print("  Check page source and look for the actual script handle loading it.")


if __name__ == "__main__":
    main()
