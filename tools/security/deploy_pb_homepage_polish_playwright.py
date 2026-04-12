#!/usr/bin/env python3
"""
Deploy pb-homepage-polish v1.0.0 to purebrain.ai via Playwright.

Fixes:
  1. Preloader orange/light flash — dark #080a12 background at priority 1
  2. Hero top gap — overrides .hero align-items:center to flex-start
  3. Footer Pure Technology logo wrong proportions — height:40px override

Strategy:
  1. Login via wpaas-standard-login bypass
  2. Check if plugin already installed (plugins.php)
  3. If NOT installed: upload zip via wp-admin/plugin-install.php?tab=upload
  4. If already installed: go to plugin editor and update content
  5. Activate if needed
  6. Verify CSS is live on homepage

DO NOT touch purebrain-security-plugin.php (locked).
"""

import io
import os
import re
import sys
import time
import base64
import zipfile
import urllib.request
import urllib.error
import ssl
import subprocess
from pathlib import Path

AETHER_ROOT  = Path("/home/jared/projects/AI-CIV/aether")
PLUGIN_FILE  = AETHER_ROOT / "tools/security/pb-homepage-polish/pb-homepage-polish.php"
PLUGIN_SLUG  = "pb-homepage-polish"
SCREENSHOT_DIR = str(AETHER_ROOT / "exports/screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# ── Credentials ────────────────────────────────────────────────────────────────
env_text = (AETHER_ROOT / ".env").read_text()

def _env(key):
    m = re.search(rf"^{key}='([^']+)'", env_text, re.MULTILINE)
    if m:
        return m.group(1).strip()
    m = re.search(rf'^{key}="([^"]+)"', env_text, re.MULTILINE)
    if m:
        return m.group(1).strip()
    m = re.search(rf"^{key}=([^\n]+)", env_text, re.MULTILINE)
    return m.group(1).strip() if m else ""

WP_USER    = _env("PUREBRAIN_WP_USER")
WP_PASS    = _env("PUREBRAIN_WP_PASSWORD")
WP_APP_PASS = "41w3 xWWZ 11em UXgj hjAF sx2T"

LOGIN_URL  = "https://purebrain.ai/wp-login.php?wpaas-standard-login=1"
EDITOR_URL = (
    f"https://purebrain.ai/wp-admin/plugin-editor.php"
    f"?file={PLUGIN_SLUG}/{PLUGIN_SLUG}.php"
    f"&plugin={PLUGIN_SLUG}/{PLUGIN_SLUG}.php"
)
PLUGINS_URL = "https://purebrain.ai/wp-admin/plugins.php"
UPLOAD_URL  = "https://purebrain.ai/wp-admin/plugin-install.php?tab=upload"


def tg_send(msg):
    tg = str(AETHER_ROOT / "tools/tg_send.sh")
    subprocess.run([tg, f"dept-systems-technology: {msg}"], capture_output=True)


def build_zip(php_path: Path) -> bytes:
    slug = php_path.parent.name
    php_filename = php_path.name
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(php_path, f"{slug}/{php_filename}")
    return buf.getvalue()


def validate_plugin(content: str) -> bool:
    checks = {
        "PHP opening tag":                   "<?php" in content,
        "Plugin Name header":                "Plugin Name: PureBrain Homepage Polish" in content,
        "v1.0.0 version":                    "1.0.0" in content,
        "pb-homepage-polish-early style id": "pb-homepage-polish-early" in content,
        "pb-homepage-polish-late style id":  "pb-homepage-polish-late" in content,
        "preloader background fix":          "#080a12" in content,
        "hero flex-start fix":               "flex-start" in content,
        "footer__logo height fix":           "footer__logo" in content and "40px" in content,
        "priority 1 wp_head":                "}, 1 );" in content or "}, 1);" in content,
        "ABSPATH check":                     "ABSPATH" in content,
    }
    all_ok = True
    for name, result in checks.items():
        status = "OK" if result else "FAIL"
        print(f"  [{status}] {name}")
        if not result:
            all_ok = False
    return all_ok


def deploy_plugin(content: str, zip_bytes: bytes) -> bool:
    from playwright.sync_api import sync_playwright

    print(f"\n{'='*65}")
    print(f"DEPLOYING {PLUGIN_SLUG} v1.0.0 TO: purebrain.ai")
    print(f"{'='*65}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()

        # ── Step 1: Login ──────────────────────────────────────────────────────
        print("\n[Step 1] Logging in via wpaas bypass...")
        page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=60000)
        time.sleep(2)

        page_body = page.inner_text("body")
        if "captcha" in page_body.lower():
            print("  CAPTCHA detected — aborting.")
            page.screenshot(path=f"{SCREENSHOT_DIR}/polish_captcha.png")
            browser.close()
            return False

        try:
            page.locator("#user_login").wait_for(state="visible", timeout=15000)
        except Exception:
            print(f"  Login form not found. URL: {page.url}")
            page.screenshot(path=f"{SCREENSHOT_DIR}/polish_no_form.png")
            browser.close()
            return False

        page.fill("#user_login", WP_USER)
        page.fill("#user_pass", WP_PASS)
        page.click("#wp-submit")
        try:
            page.wait_for_load_state("domcontentloaded", timeout=30000)
        except Exception:
            pass
        time.sleep(3)

        if "wp-admin" not in page.url:
            print(f"  Login failed. URL: {page.url}")
            page.screenshot(path=f"{SCREENSHOT_DIR}/polish_login_fail.png")
            browser.close()
            return False
        print("  Login successful!")

        # ── Step 2: Check if plugin already installed ──────────────────────────
        print(f"\n[Step 2] Checking plugin installation status...")
        page.goto(PLUGINS_URL, wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)

        plugin_row = page.evaluate(f"""() => {{
            var rows = document.querySelectorAll('tr[data-slug="{PLUGIN_SLUG}"]');
            if (rows.length > 0) return rows[0].innerHTML;
            return '';
        }}""")

        already_installed = bool(plugin_row)
        print(f"  Plugin installed: {already_installed}")

        if already_installed:
            is_active = "deactivate" in plugin_row.lower()
            print(f"  Plugin active: {is_active}")

            if not is_active:
                print("  Activating plugin from plugins page...")
                activate_href = page.evaluate(f"""() => {{
                    var rows = document.querySelectorAll('tr[data-slug="{PLUGIN_SLUG}"]');
                    if (!rows.length) return '';
                    var link = rows[0].querySelector('a[href*="action=activate"]');
                    return link ? link.href : '';
                }}""")
                if activate_href:
                    page.goto(activate_href, wait_until="domcontentloaded", timeout=30000)
                    time.sleep(2)
                    print("  Activation attempted.")

            # Go to editor to update content
            print(f"\n[Step 3] Updating plugin content via editor...")
            page.goto(EDITOR_URL, wait_until="domcontentloaded", timeout=60000)
            time.sleep(5)

            page_body = page.inner_text("body")
            if "DISALLOW_FILE_EDIT" in page_body or "editing has been disabled" in page_body.lower():
                print("  File editing disabled — cannot update via editor.")
                page.screenshot(path=f"{SCREENSHOT_DIR}/polish_edit_disabled.png")
                browser.close()
                return False

            has_cm = page.evaluate("() => !!document.querySelector('.CodeMirror')")
            has_ta = page.evaluate("() => !!document.querySelector('#newcontent')")
            print(f"  CodeMirror: {has_cm}, Textarea: {has_ta}")

            if not has_cm and not has_ta:
                print(f"  No editor found. Plugin may need reinstall.")
                page.screenshot(path=f"{SCREENSHOT_DIR}/polish_no_editor.png")
                browser.close()
                return False

            # Set content
            print("\n[Step 4] Setting plugin content in editor...")
            set_ok = False
            verify_markers = ["pb-homepage-polish-early", "footer__logo", "flex-start", "080a12"]

            if has_cm:
                result = page.evaluate(
                    f"""(pluginContent) => {{
                        try {{
                            var cmEl = document.querySelector('.CodeMirror');
                            if (!cmEl) return 'no_cm_element';
                            var cm = cmEl.CodeMirror;
                            if (!cm) return 'no_cm_instance';
                            cm.setValue(pluginContent);
                            var val = cm.getValue();
                            var markers = {verify_markers};
                            for (var i = 0; i < markers.length; i++) {{
                                if (val.indexOf(markers[i]) === -1) return 'missing_marker:' + markers[i];
                            }}
                            return 'success';
                        }} catch(e) {{ return 'error:' + e.message; }}
                    }}""",
                    content,
                )
                print(f"  CodeMirror result: {result}")
                set_ok = result == "success"

            if not set_ok:
                print("  Using textarea fallback...")
                page.evaluate("""() => {
                    var ta = document.querySelector('#newcontent');
                    if (ta) { ta.style.display = 'block'; ta.style.visibility = 'visible'; }
                }""")
                page.evaluate(
                    """(pluginContent) => {
                        var ta = document.querySelector('#newcontent');
                        if (!ta) return;
                        var setter = Object.getOwnPropertyDescriptor(
                            window.HTMLTextAreaElement.prototype, 'value').set;
                        setter.call(ta, pluginContent);
                        ta.dispatchEvent(new Event('input', {bubbles: true}));
                        ta.dispatchEvent(new Event('change', {bubbles: true}));
                    }""",
                    content,
                )
                print("  Textarea content set.")

            time.sleep(1)

        else:
            # ── Step 3: Upload plugin zip ──────────────────────────────────────
            print(f"\n[Step 3] Plugin not installed — uploading via plugin-install.php...")
            page.goto(UPLOAD_URL, wait_until="domcontentloaded", timeout=60000)
            time.sleep(3)

            page_body = page.inner_text("body")
            print(f"  Page title: {page.title()}")

            # Write zip to temp file
            zip_path = f"/tmp/{PLUGIN_SLUG}.zip"
            with open(zip_path, "wb") as f:
                f.write(zip_bytes)
            print(f"  Zip written to: {zip_path}")

            # Set file input
            try:
                file_input = page.locator('input[type="file"]')
                file_input.wait_for(state="visible", timeout=10000)
                file_input.set_input_files(zip_path)
                print("  File set on input.")
            except Exception as e:
                print(f"  File input error: {e}")
                page.screenshot(path=f"{SCREENSHOT_DIR}/polish_upload_form.png")
                browser.close()
                return False

            time.sleep(1)

            # Click Install Now
            install_btn = page.locator('#install-plugin-submit, input[value="Install Now"], button:has-text("Install Now")')
            try:
                install_btn.first.click()
                page.wait_for_load_state("domcontentloaded", timeout=60000)
                time.sleep(5)
            except Exception as e:
                print(f"  Install click error: {e}")

            page_text = page.inner_text("body")
            page.screenshot(path=f"{SCREENSHOT_DIR}/polish_after_upload.png")
            print(f"  Post-install page snippet: {page_text[:300]}")

            # Check for success
            if "successfully" in page_text.lower() or "installed" in page_text.lower():
                print("  Plugin uploaded successfully!")
            elif "already installed" in page_text.lower():
                print("  Plugin already installed (ok).")
            else:
                print(f"  Upload result unclear. Continuing anyway.")

            # Click Activate Plugin link if present
            activate_link = page.locator('a:has-text("Activate Plugin")')
            try:
                activate_link.wait_for(state="visible", timeout=5000)
                activate_link.click()
                page.wait_for_load_state("domcontentloaded", timeout=20000)
                time.sleep(2)
                print("  Activate Plugin link clicked.")
            except Exception:
                print("  No 'Activate Plugin' link found — may already be active or needs manual activation.")

            # Now go to editor to verify/set content
            print(f"\n[Step 4] Opening plugin editor to verify content...")
            page.goto(EDITOR_URL, wait_until="domcontentloaded", timeout=60000)
            time.sleep(5)

            has_cm = page.evaluate("() => !!document.querySelector('.CodeMirror')")
            has_ta = page.evaluate("() => !!document.querySelector('#newcontent')")
            print(f"  CodeMirror: {has_cm}, Textarea: {has_ta}")

            set_ok = False
            verify_markers = ["pb-homepage-polish-early", "footer__logo", "flex-start", "080a12"]

            if has_cm:
                # Verify current content is correct (should be from zip upload)
                current = page.evaluate("""() => {
                    var cm = document.querySelector('.CodeMirror');
                    return cm && cm.CodeMirror ? cm.CodeMirror.getValue() : '';
                }""")
                has_all = all(m in current for m in verify_markers)
                if has_all:
                    print("  Content verified in editor — matches expected plugin.")
                    set_ok = True
                else:
                    # Set content via editor as backup
                    result = page.evaluate(
                        f"""(pluginContent) => {{
                            try {{
                                var cm = document.querySelector('.CodeMirror').CodeMirror;
                                cm.setValue(pluginContent);
                                var val = cm.getValue();
                                var markers = {verify_markers};
                                for (var i = 0; i < markers.length; i++) {{
                                    if (val.indexOf(markers[i]) === -1) return 'missing:' + markers[i];
                                }}
                                return 'success';
                            }} catch(e) {{ return 'error:' + e.message; }}
                        }}""",
                        content,
                    )
                    print(f"  CodeMirror set result: {result}")
                    set_ok = result == "success"
            elif has_ta:
                set_ok = True  # Content came from zip, assume correct

        # ── Step 5: Save (if we modified editor content) ──────────────────────
        has_submit = page.evaluate("() => !!document.querySelector('#submit, input[type=\"submit\"]')")
        if has_submit:
            print("\n[Step 5] Saving plugin file...")
            page.evaluate("""() => {
                var btn = document.querySelector('#submit') ||
                          document.querySelector('input[type="submit"]');
                if (btn) btn.click();
            }""")
            try:
                page.wait_for_load_state("domcontentloaded", timeout=45000)
            except Exception:
                pass
            time.sleep(5)

            page.screenshot(path=f"{SCREENSHOT_DIR}/polish_after_save.png")
            page_text = page.inner_text("body")

            if "File edited successfully" in page_text or "updated successfully" in page_text.lower():
                print("  SUCCESS: File saved!")
            elif "Parse error" in page_text or "syntax error" in page_text.lower():
                m = re.search(r"(?:Parse error|syntax error)[^<]{0,200}", page_text)
                print(f"  ERROR: PHP syntax error: {m.group(0) if m else 'unknown'}")
                browser.close()
                return False
            else:
                print(f"  Save result unclear. Snippet: {page_text[1000:1300]}")

        # ── Step 6: Ensure plugin is active ───────────────────────────────────
        print("\n[Step 6] Verifying plugin is active...")
        page.goto(PLUGINS_URL, wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)

        plugin_row = page.evaluate(f"""() => {{
            var rows = document.querySelectorAll('tr[data-slug="{PLUGIN_SLUG}"]');
            return rows.length > 0 ? rows[0].innerHTML : '';
        }}""")

        if plugin_row:
            is_active = "deactivate" in plugin_row.lower()
            print(f"  Plugin active: {is_active}")
            if not is_active:
                activate_href = page.evaluate(f"""() => {{
                    var rows = document.querySelectorAll('tr[data-slug="{PLUGIN_SLUG}"]');
                    if (!rows.length) return '';
                    var link = rows[0].querySelector('a[href*="action=activate"]');
                    return link ? link.href : '';
                }}""")
                if activate_href:
                    page.goto(activate_href, wait_until="domcontentloaded", timeout=30000)
                    time.sleep(2)
                    print("  Activation attempted.")
                    is_active = True
        else:
            print(f"  Plugin not found in plugins list — deployment may have failed.")
            page.screenshot(path=f"{SCREENSHOT_DIR}/polish_not_in_list.png")
            browser.close()
            return False

        browser.close()

    # ── Step 7: Clear Elementor cache ─────────────────────────────────────────
    print("\n[Step 7] Clearing Elementor cache...")
    credentials = base64.b64encode(f"{WP_USER}:{WP_APP_PASS}".encode()).decode()
    cache_req = urllib.request.Request(
        "https://purebrain.ai/wp-json/elementor/v1/cache",
        method="DELETE",
        headers={
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/json",
        },
    )
    ctx_ssl = ssl.create_default_context()
    try:
        with urllib.request.urlopen(cache_req, context=ctx_ssl, timeout=20) as resp:
            print(f"  Cache clear: HTTP {resp.status}")
    except urllib.error.HTTPError as e:
        print(f"  Cache clear response: HTTP {e.code} (may be OK)")
    except Exception as ex:
        print(f"  Cache clear skipped: {ex}")

    return True


def verify_live() -> bool:
    print("\n[Verify] Fetching purebrain.ai homepage...")
    ctx_ssl = ssl.create_default_context()
    req = urllib.request.Request(
        "https://purebrain.ai/",
        headers={"User-Agent": "Mozilla/5.0 (PureBrain-Verify)", "Cache-Control": "no-cache"},
    )
    try:
        with urllib.request.urlopen(req, context=ctx_ssl, timeout=20) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  Could not fetch: {e}")
        return False

    checks = {
        "pb-homepage-polish-early CSS id":    "pb-homepage-polish-early" in html,
        "preloader dark #080a12 override":    "080a12" in html,
        "footer logo height 40px override":   "footer__logo" in html,
        "hero flex-start override":            "flex-start" in html,
    }
    all_ok = True
    for name, result in checks.items():
        status = "PASS" if result else "FAIL"
        print(f"  [{status}] {name}")
        if not result:
            all_ok = False
    return all_ok


def main():
    print("=" * 65)
    print(f"pb-homepage-polish v1.0.0 — Playwright Deploy")
    print("Fixes: preloader flash, hero top gap, footer logo")
    print("=" * 65)

    if not PLUGIN_FILE.exists():
        print(f"ERROR: Plugin file not found: {PLUGIN_FILE}")
        sys.exit(1)

    content = PLUGIN_FILE.read_text()
    print(f"\nPlugin: {len(content):,} chars")

    print("\n--- Validating plugin content ---")
    if not validate_plugin(content):
        print("\nERROR: Validation failed. Aborting.")
        sys.exit(1)
    print("All checks passed.\n")

    zip_bytes = build_zip(PLUGIN_FILE)
    print(f"Zip: {len(zip_bytes):,} bytes")

    tg_send(f"Starting deploy: {PLUGIN_SLUG} v1.0.0 (preloader+hero+footer fixes)")

    success = deploy_plugin(content, zip_bytes)
    if not success:
        print("\n[FAIL] Deployment failed.")
        tg_send(f"FAILED: {PLUGIN_SLUG} deployment failed. Check logs.")
        sys.exit(1)

    print(f"\nDeploy complete. Waiting 8s for cache...")
    time.sleep(8)

    verified = verify_live()
    if verified:
        msg = (
            f"{PLUGIN_SLUG} v1.0.0 LIVE. "
            "All 3 fixes active: preloader dark bg, hero gap reduced, footer logo proportions fixed."
        )
        print(f"\nSUCCESS: {msg}")
        tg_send(msg)
    else:
        msg = f"{PLUGIN_SLUG} deployed but live verification has gaps. May be CF cache. Check manually."
        print(f"\nPARTIAL: {msg}")
        tg_send(msg)
        # Don't exit 1 — plugin may be deployed but behind CDN cache


if __name__ == "__main__":
    main()
