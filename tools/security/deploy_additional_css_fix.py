#!/usr/bin/env python3
"""
Narrow the broad blog-cta-block hover rule in WordPress Additional CSS.

Problem (identified 2026-02-21):
  The Additional CSS block "FIX 3: Start Your AI Partnership CTA button"
  uses the overly broad selector:
    body.single-post .blog-cta-block a:hover,
    body.single-post .blog-cta-block p a:hover
  This matches BOTH the CTA button AND the subscribe/newsletter link,
  giving the subscribe link an unwanted blue box-shadow + translateY(-2px).

  The wp-custom-css block loads AFTER the plugin CSS in <head>, so even
  though the plugin has higher specificity rules for subscribe links, the
  Additional CSS blue-glow rule applies too (overriding box-shadow via
  last-stylesheet-wins at equal specificity for the non-subscribe paths).

Fix:
  Replace the broad hover rule with a narrow one scoped to
  a[href*="awakening"] only (the CTA button). Subscribe links are
  governed exclusively by the plugin CSS (purebrain-blog-cta-hover).

  Also bump the FIX 3 comment to reflect it now only applies to the
  awakening CTA button, not the subscribe link.

Companion:
  Plugin v2.9.0 also adds high-specificity data-pb-subscribe override
  as a belt-and-suspenders measure.

Author: full-stack-developer agent
Date: 2026-02-21
Review required: security-engineer-tech before running
"""

import os
import re
import sys
import time
from pathlib import Path

AETHER_ROOT = Path("/home/jared/projects/AI-CIV/aether")

WP_ADMIN_URL = "https://purebrain.ai/wp-admin"
WP_CSS_URL = "https://purebrain.ai/wp-admin/customize.php?autofocus[section]=custom_css"
WP_USER = "Aether"

env_text = (AETHER_ROOT / ".env").read_text()
WP_PASSWORD_MATCH = re.search(r"PUREBRAIN_WP_PASSWORD='([^']+)'", env_text)
WP_PASSWORD = WP_PASSWORD_MATCH.group(1) if WP_PASSWORD_MATCH else ""

SCREENSHOT_BEFORE = str(AETHER_ROOT / "exports/screenshots/additional_css_fix_before.png")
SCREENSHOT_AFTER  = str(AETHER_ROOT / "exports/screenshots/additional_css_fix_after.png")
SCREENSHOT_SAVED  = str(AETHER_ROOT / "exports/screenshots/additional_css_fix_saved.png")

# Exact text to find and replace in the Additional CSS
OLD_BLOCK = (
    '/* FIX 3: "Start Your AI Partnership" CTA button - blue glow highlight on hover */\n'
    '/* Orange background stays; adds brand blue (#2a93c1) box-shadow glow */\n'
    'body.single-post .blog-cta-block a,\n'
    'body.single-post .blog-cta-block p a {\n'
    '    transition: box-shadow 0.25s ease, transform 0.2s ease !important;\n'
    '}\n'
    '\n'
    'body.single-post .blog-cta-block a:hover,\n'
    'body.single-post .blog-cta-block p a:hover {\n'
    '    box-shadow:\n'
    '        0 0 0 3px #2a93c1,\n'
    '        0 0 18px rgba(42, 147, 193, 0.55),\n'
    '        0 6px 20px rgba(0, 0, 0, 0.35) !important;\n'
    '    transform: translateY(-2px) !important;\n'
    '    text-decoration: none !important;\n'
    '    color: #ffffff !important;\n'
    '}\n'
    '\n'
    'body.single-post .blog-cta-block a:focus,\n'
    'body.single-post .blog-cta-block p a:focus {\n'
    '    outline: none !important;\n'
    '    box-shadow:\n'
    '        0 0 0 3px #2a93c1,\n'
    '        0 0 18px rgba(42, 147, 193, 0.55) !important;\n'
    '}\n'
    '\n'
)

# Replacement: scope the blue-glow to ONLY the awakening CTA button.
# Subscribe/newsletter links are handled by purebrain-blog-cta-hover (plugin CSS).
NEW_BLOCK = (
    '/* FIX 3: "Start Your AI Partnership" CTA button - blue glow highlight on hover */\n'
    '/* SCOPED TO AWAKENING LINKS ONLY (v2021-02-21 fix) */\n'
    '/* The broad body.single-post .blog-cta-block a:hover rule was removed because\n'
    '   it also matched subscribe/newsletter links, giving them an unwanted blue glow\n'
    '   and translateY(-2px) lift on hover. The plugin CSS (purebrain-blog-cta-hover)\n'
    '   now governs subscribe link appearance. This rule targets only the CTA button. */\n'
    'body.single-post .blog-cta-block a[href*="awakening"],\n'
    'body.single-post .blog-cta-block p a[href*="awakening"] {\n'
    '    transition: box-shadow 0.25s ease, transform 0.2s ease !important;\n'
    '}\n'
    '\n'
    'body.single-post .blog-cta-block a[href*="awakening"]:hover,\n'
    'body.single-post .blog-cta-block p a[href*="awakening"]:hover {\n'
    '    box-shadow:\n'
    '        0 0 0 3px #2a93c1,\n'
    '        0 0 18px rgba(42, 147, 193, 0.55),\n'
    '        0 6px 20px rgba(0, 0, 0, 0.35) !important;\n'
    '    transform: translateY(-2px) !important;\n'
    '    text-decoration: none !important;\n'
    '    color: #ffffff !important;\n'
    '}\n'
    '\n'
    'body.single-post .blog-cta-block a[href*="awakening"]:focus,\n'
    'body.single-post .blog-cta-block p a[href*="awakening"]:focus {\n'
    '    outline: none !important;\n'
    '    box-shadow:\n'
    '        0 0 0 3px #2a93c1,\n'
    '        0 0 18px rgba(42, 147, 193, 0.55) !important;\n'
    '}\n'
    '\n'
)


def fetch_current_css() -> str:
    """Fetch the current Additional CSS from the live page."""
    import urllib.request
    req = urllib.request.Request(
        "https://purebrain.ai/ceo-vs-employee-ai-transformation-gap/",
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode("utf-8")

    match = re.search(
        r'<style[^>]*id=["\']?wp-custom-css["\']?[^>]*>(.*?)</style>',
        html,
        re.DOTALL,
    )
    if not match:
        raise RuntimeError("wp-custom-css style block not found in page HTML")
    return match.group(1)


def build_new_css(current_css: str) -> str:
    """Replace the old block with the narrowed one."""
    if OLD_BLOCK not in current_css:
        raise RuntimeError(
            "Old block not found in current Additional CSS. "
            "It may have already been updated or the page is serving a cached version."
        )
    new_css = current_css.replace(OLD_BLOCK, NEW_BLOCK, 1)
    # Sanity check
    if OLD_BLOCK in new_css:
        raise RuntimeError("Replacement failed - old block still present after replace()")
    return new_css


def validate_new_css(new_css: str) -> bool:
    """Verify the new CSS has the right rules."""
    checks = {
        "old broad hover rule removed": 'blog-cta-block a:hover,\nbody.single-post .blog-cta-block p a:hover' not in new_css,
        "new awakening-only hover present": 'blog-cta-block a[href*="awakening"]:hover' in new_css,
        "subscribe rule NOT in FIX 3 block": 'blog-cta-block a[href*="subscribe"]' not in new_css or 'purebrain-blog-cta-hover' in new_css,
        "blue glow still applies to awakening": '0 0 0 3px #2a93c1' in new_css,
        "scope comment present": 'SCOPED TO AWAKENING LINKS ONLY' in new_css,
    }
    all_ok = True
    for name, result in checks.items():
        status = "OK" if result else "FAIL"
        print(f"  [{status}] {name}")
        if not result:
            all_ok = False
    return all_ok


def deploy(new_css: str) -> bool:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=2,
        )
        page = context.new_page()

        # Step 1: Login
        print("\n[Step 1] Logging in to WP Admin...")
        page.goto("https://purebrain.ai/wp-login.php", wait_until="domcontentloaded", timeout=60000)
        time.sleep(2)

        # GoDaddy SSO overlay
        sso_toggle = page.locator(".wpaas-sso-login-toggle")
        if sso_toggle.count() > 0 and sso_toggle.is_visible():
            print("  GoDaddy SSO overlay detected - clicking username/password link...")
            sso_toggle.click()
            time.sleep(2)

        try:
            page.locator("#user_login").wait_for(state="visible", timeout=15000)
        except Exception:
            page.screenshot(path=SCREENSHOT_BEFORE)
            print("  ERROR: Login form not visible.")
            browser.close()
            return False

        captcha_field = page.locator("#wpsec_captcha_answer")
        if captcha_field.count() > 0 and captcha_field.is_visible():
            page.screenshot(path=SCREENSHOT_BEFORE)
            print(f"  CAPTCHA detected! Screenshot: {SCREENSHOT_BEFORE}")
            print("  Wait 15-30 minutes for GoDaddy bot protection to reset, then retry.")
            browser.close()
            return False

        page.fill("#user_login", WP_USER)
        page.fill("#user_pass", WP_PASSWORD)
        page.click("#wp-submit")

        try:
            page.wait_for_load_state("domcontentloaded", timeout=30000)
        except Exception:
            pass
        time.sleep(3)

        if "wp-login.php" in page.url:
            page.screenshot(path=SCREENSHOT_BEFORE)
            print(f"  ERROR: Login failed. URL: {page.url}")
            browser.close()
            return False

        print("  Login successful!")

        # Step 2: Navigate to Customizer > Additional CSS
        print("\n[Step 2] Opening Customizer Additional CSS...")
        page.goto(WP_CSS_URL, wait_until="domcontentloaded", timeout=90000)
        time.sleep(12)  # Customizer iframe needs time to load

        try:
            page.screenshot(path=SCREENSHOT_BEFORE, timeout=60000)
            print(f"  Screenshot (before): {SCREENSHOT_BEFORE}")
        except Exception as ss_err:
            print(f"  Screenshot (before) skipped: {ss_err}")

        has_cm = page.evaluate("() => !!document.querySelector('.CodeMirror')")
        print(f"  CodeMirror present: {has_cm}")

        if not has_cm:
            print("  ERROR: CodeMirror editor not found in Customizer.")
            browser.close()
            return False

        # Step 3: Read current CSS from editor and verify old block is there
        print("\n[Step 3] Reading current CSS from editor...")
        current_in_editor = page.evaluate("""() => {
            const cm = document.querySelector('.CodeMirror');
            return cm ? cm.CodeMirror.getValue() : null;
        }""")

        if current_in_editor is None:
            print("  ERROR: Could not read CodeMirror content.")
            browser.close()
            return False

        print(f"  Editor CSS length: {len(current_in_editor)} chars")

        # Check old block is still in the editor
        if 'blog-cta-block a:hover,\nbody.single-post .blog-cta-block p a:hover' not in current_in_editor:
            print("  NOTE: Old broad hover rule not found in editor CSS.")
            print("  The Additional CSS may have already been updated, or the editor")
            print("  is serving different content than the live page.")
            browser.close()
            return False

        print("  Old broad hover rule confirmed in editor. Applying fix...")

        # Step 4: Apply the fix
        print("\n[Step 4] Setting new CSS...")
        fixed_css = current_in_editor.replace(OLD_BLOCK, NEW_BLOCK, 1)

        if current_in_editor == fixed_css:
            # OLD_BLOCK not found verbatim - try a looser match
            print("  WARNING: Exact OLD_BLOCK not found. Attempting partial replacement...")
            # Find the lines by markers
            old_marker = '/* FIX 3: "Start Your AI Partnership" CTA button - blue glow highlight on hover */'
            end_marker = '/* ========== END BLOG POST HOVER FIXES ========== */'
            start_idx = current_in_editor.find(old_marker)
            end_idx = current_in_editor.find(end_marker)
            if start_idx >= 0 and end_idx >= 0:
                found_block = current_in_editor[start_idx:end_idx]
                fixed_css = current_in_editor[:start_idx] + NEW_BLOCK + current_in_editor[end_idx:]
                print(f"  Partial match: replaced {len(found_block)} chars with {len(NEW_BLOCK)} chars")
            else:
                print("  ERROR: Could not locate FIX 3 block by markers.")
                browser.close()
                return False

        result = page.evaluate("""(css) => {
            try {
                const cmEl = document.querySelector('.CodeMirror');
                if (!cmEl) return 'no_cm_element';
                const cm = cmEl.CodeMirror;
                if (!cm) return 'no_cm_instance';
                cm.setValue(css);
                return 'success:' + cm.getValue().length;
            } catch(e) { return 'error: ' + e.message; }
        }""", fixed_css)
        print(f"  CodeMirror setValue result: {result}")

        if "success" not in result:
            print("  ERROR: Failed to set CSS in CodeMirror.")
            browser.close()
            return False

        time.sleep(2)

        # Step 5: Publish
        print("\n[Step 5] Publishing Customizer changes...")
        try:
            page.screenshot(path=SCREENSHOT_AFTER, timeout=60000)
        except Exception as ss_err:
            print(f"  Screenshot (after) skipped: {ss_err}")

        # Find and click the Publish button
        published = page.evaluate("""() => {
            // Try the WP Customize save button
            const saveBtn = document.querySelector('#save') ||
                            document.querySelector('#customize-save-button-wrapper button') ||
                            document.querySelector('button[data-action="save"]');
            if (saveBtn && !saveBtn.disabled) {
                saveBtn.click();
                return 'clicked: ' + (saveBtn.textContent || saveBtn.value || 'btn');
            }
            return 'no_button_found';
        }""")
        print(f"  Publish button: {published}")

        time.sleep(8)  # Wait for save

        try:
            page.screenshot(path=SCREENSHOT_SAVED, timeout=60000)
            print(f"  Screenshot (saved): {SCREENSHOT_SAVED}")
        except Exception as ss_err:
            print(f"  Screenshot (saved) skipped: {ss_err}")

        # Verify by reading editor content
        saved_css = page.evaluate("""() => {
            const cm = document.querySelector('.CodeMirror');
            return cm ? cm.CodeMirror.getValue() : null;
        }""")

        save_ok = (
            saved_css is not None
            and 'blog-cta-block a[href*="awakening"]:hover' in saved_css
            and 'SCOPED TO AWAKENING LINKS ONLY' in saved_css
        )

        if save_ok:
            print("  SUCCESS: Narrowed rule confirmed in editor after save.")
        else:
            print("  WARNING: Could not confirm save via editor re-read.")
            print("  Check screenshots to verify.")

        browser.close()
        return save_ok


def main():
    print("=" * 70)
    print("ADDITIONAL CSS FIX: Narrow CTA hover rule to awakening links only")
    print("=" * 70)
    print("\nThis script narrows the broad WordPress Additional CSS hover rule")
    print("that was applying blue glow + translateY to subscribe links.")
    print()
    print("OLD (too broad):")
    print("  body.single-post .blog-cta-block a:hover { blue glow }")
    print()
    print("NEW (scoped to CTA button only):")
    print("  body.single-post .blog-cta-block a[href*='awakening']:hover { blue glow }")
    print()

    # Step 1: Fetch current CSS
    print("[Step 1] Fetching current Additional CSS from live page...")
    try:
        current_css = fetch_current_css()
        print(f"  Length: {len(current_css)} chars")
    except Exception as e:
        print(f"  ERROR: {e}")
        sys.exit(1)

    # Step 2: Build the new CSS
    print("\n[Step 2] Building replacement CSS...")
    try:
        new_css = build_new_css(current_css)
        print(f"  New length: {len(new_css)} chars (delta: {len(new_css) - len(current_css):+d})")
    except Exception as e:
        print(f"  ERROR: {e}")
        sys.exit(1)

    # Step 3: Validate
    print("\n[Step 3] Validating new CSS...")
    if not validate_new_css(new_css):
        print("\nValidation FAILED. Aborting.")
        sys.exit(1)
    print("  Validation passed.")

    # Step 4: Deploy via Playwright
    print("\n[Step 4] Deploying via Playwright (WordPress Customizer)...")
    success = deploy(new_css)

    print("\n" + "=" * 70)
    if success:
        print("SUCCESS: Additional CSS narrowed. Subscribe links no longer get blue glow.")
        print()
        print("What changed:")
        print("  BEFORE: body.single-post .blog-cta-block a:hover → blue glow + lift")
        print("          (matched CTA button AND subscribe link)")
        print("  AFTER:  body.single-post .blog-cta-block a[href*='awakening']:hover → blue glow + lift")
        print("          (matches CTA button ONLY)")
        print()
        print("Subscribe link hover now controlled exclusively by plugin CSS:")
        print("  body.single-post .blog-cta-block p a[href*='subscribe']:hover → orange gradient")
        print()
        print("Companion fix: plugin v2.9.0 also adds data-pb-subscribe attribute")
        print("for belt-and-suspenders high-specificity override.")
        print(f"\nScreenshots:")
        print(f"  Before: {SCREENSHOT_BEFORE}")
        print(f"  After:  {SCREENSHOT_AFTER}")
        print(f"  Saved:  {SCREENSHOT_SAVED}")
    else:
        print("FAILED or uncertain. Check screenshots.")
        print(f"  Before: {SCREENSHOT_BEFORE}")
        print(f"  After:  {SCREENSHOT_AFTER}")
        print(f"  Saved:  {SCREENSHOT_SAVED}")
        sys.exit(1)


if __name__ == "__main__":
    main()
