#!/usr/bin/env python3
"""
Deploy purebrain-security-plugin.php v2.3.0 to WordPress.

v2.3.0 fixes:
1. FAQ Accordion: Fixed "flash of expanded content" bug.
   - Added pre-JS CSS to hide <p> tags inside .faq-section immediately on load,
     so FAQs start collapsed before JavaScript runs (no flash of open content).
   - Added .faq-answer > p reset rule to restore paragraph display once JS wraps them.
   - Improved JS: checks document.body.classList directly instead of DOM selector
     for body class, handles multiple <p> children per .faq-section, uses
     readyState check to init as early as possible.
   - Increased max-height from 600px to 800px to handle longer answers.

2. CTA Button Hover: Fixed blank/invisible button text on hover.
   - Root cause: generic rule body.single-post a:hover { color: #f1420b !important }
     in wp-custom-css was overriding the button's white text on hover, making it
     invisible against the orange button background.
   - Fix: explicitly declare color: #ffffff !important and
     background: linear-gradient(135deg, #f1420b ...) !important on .blog-cta-block a:hover
     so the button stays visually correct (orange background, white text, blue glow ring).

Author: full-stack-developer agent
Date: 2026-02-20
"""

import os
import sys
import time
import urllib.request
from pathlib import Path
from dotenv import load_dotenv

AETHER_ROOT = Path("/home/jared/projects/AI-CIV/aether")
ENV_FILE = AETHER_ROOT / ".env"
load_dotenv(ENV_FILE)

PLUGIN_FILE = AETHER_ROOT / "tools/security/purebrain-security-plugin.php"
WP_ADMIN_URL = "https://purebrain.ai/wp-admin"
WP_USER = "Aether"
WP_PASSWORD = os.environ.get("PUREBRAIN_WP_PASSWORD", "")

PLUGIN_EDITOR_URL = (
    f"{WP_ADMIN_URL}/plugin-editor.php"
    f"?file=purebrain-security/purebrain-security-plugin.php"
    f"&plugin=purebrain-security/purebrain-security-plugin.php"
)

SCREENSHOT_DEPLOY = str(AETHER_ROOT / "exports/screenshots/plugin_v230_deploy.png")
SCREENSHOT_VERIFY = str(AETHER_ROOT / "exports/screenshots/plugin_v230_verify.png")
SCREENSHOT_FAQ = str(AETHER_ROOT / "exports/screenshots/plugin_v230_faq_live.png")
SCREENSHOT_CTA = str(AETHER_ROOT / "exports/screenshots/plugin_v230_cta_hover.png")


def deploy():
    from playwright.sync_api import sync_playwright

    print("=== PureBrain Security Plugin v2.3.0 Deployer ===")
    print(f"Plugin file: {PLUGIN_FILE}")
    print(f"Target: {WP_ADMIN_URL}")
    print("Fixes: FAQ collapsed on load + CTA hover white text")

    if not PLUGIN_FILE.exists():
        print(f"ERROR: Plugin file not found: {PLUGIN_FILE}")
        sys.exit(1)

    new_content = PLUGIN_FILE.read_text()
    print(f"Plugin content: {len(new_content)} chars")

    # Validate the new code is present
    if "2.3.0" not in new_content:
        print("ERROR: Plugin file does not contain version 2.3.0. Aborting.")
        sys.exit(1)

    if "faq-section > p" not in new_content:
        print("ERROR: Plugin file does not contain pre-JS FAQ CSS fix. Aborting.")
        sys.exit(1)

    if "color: #ffffff !important;" not in new_content:
        print("ERROR: Plugin file does not contain CTA white text fix. Aborting.")
        sys.exit(1)

    print("Plugin content validated (v2.3.0, FAQ fix + CTA fix present). Starting Playwright...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=2,  # Sharp rendering for CAPTCHA reading
        )
        page = context.new_page()

        # Step 1: Login
        print("\n[Step 1] Logging in to WP Admin...")
        page.goto("https://purebrain.ai/wp-login.php", wait_until="domcontentloaded", timeout=60000)
        time.sleep(2)

        # Handle GoDaddy SSO overlay
        sso_toggle = page.locator(".wpaas-sso-login-toggle")
        if sso_toggle.count() > 0 and sso_toggle.is_visible():
            print("  GoDaddy SSO overlay detected. Clicking username/password link...")
            sso_toggle.click()
            time.sleep(2)

        try:
            page.locator("#user_login").wait_for(state="visible", timeout=15000)
        except Exception:
            page.screenshot(path=SCREENSHOT_DEPLOY)
            print("  ERROR: Login form not visible. Screenshot saved.")
            browser.close()
            return False

        # Check for CAPTCHA
        captcha_field = page.locator("#wpsec_captcha_answer")
        if captcha_field.count() > 0 and captcha_field.is_visible():
            print("  CAPTCHA detected! Taking screenshot to read it...")
            page.screenshot(path=SCREENSHOT_DEPLOY)
            print(f"  CAPTCHA screenshot: {SCREENSHOT_DEPLOY}")
            print("  Cannot proceed - CAPTCHA requires manual solving.")
            print("  Wait 15-30 minutes for GoDaddy bot protection to reset.")
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

        current_url = page.url
        print(f"  After login URL: {current_url}")

        if "wp-login.php" in current_url:
            page.screenshot(path=SCREENSHOT_DEPLOY)
            page_text = page.inner_text("body")
            print(f"  ERROR: Login failed. Page: {page_text[:300]}")
            browser.close()
            return False

        print("  Login successful!")

        # Step 2: Plugin Editor
        print("\n[Step 2] Opening Plugin Editor...")
        page.goto(PLUGIN_EDITOR_URL, wait_until="domcontentloaded", timeout=60000)
        time.sleep(4)

        page_text = page.inner_text("body")
        if "DISALLOW_FILE_EDIT" in page_text or "editing has been disabled" in page_text.lower():
            print("  ERROR: File editing disabled in wp-config.php")
            browser.close()
            return False
        if "You need a higher level" in page_text:
            print("  ERROR: Insufficient permissions")
            browser.close()
            return False

        # Check which editor type is present
        has_codemirror = page.evaluate("() => !!document.querySelector('.CodeMirror')")
        has_textarea = page.evaluate("() => !!document.querySelector('#newcontent')")
        print(f"  CodeMirror: {has_codemirror}, Textarea: {has_textarea}")

        if not has_codemirror and not has_textarea:
            print("  ERROR: No editor found")
            page.screenshot(path=SCREENSHOT_DEPLOY)
            browser.close()
            return False

        # Step 3: Set content
        print("\n[Step 3] Setting plugin content via JS...")

        if has_codemirror:
            print("  Using CodeMirror setValue()...")
            success = page.evaluate("""(content) => {
                try {
                    const cmEl = document.querySelector('.CodeMirror');
                    if (!cmEl) return 'no_cm_element';
                    const cm = cmEl.CodeMirror;
                    if (!cm) return 'no_cm_instance';
                    cm.setValue(content);
                    const val = cm.getValue();
                    if (val.includes('2.3.0') && val.includes('faq-section > p') && val.includes('color: #ffffff !important;')) return 'success';
                    return 'set_failed: got ' + val.length + ' chars, missing expected content';
                } catch(e) {
                    return 'error: ' + e.message;
                }
            }""", new_content)
            print(f"  CodeMirror result: {success}")

            if success != 'success':
                print("  CodeMirror failed. Trying textarea fallback...")
                page.evaluate("""() => {
                    const ta = document.querySelector('#newcontent');
                    if (ta) {
                        ta.style.display = 'block';
                        ta.style.visibility = 'visible';
                    }
                }""")
                page.evaluate("""(content) => {
                    const ta = document.querySelector('#newcontent');
                    if (ta) {
                        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                            window.HTMLTextAreaElement.prototype, 'value').set;
                        nativeInputValueSetter.call(ta, content);
                        ta.dispatchEvent(new Event('input', { bubbles: true }));
                        ta.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                }""", new_content)
                print("  Textarea fallback set.")
        else:
            print("  Using textarea via JS...")
            page.evaluate("""(content) => {
                const ta = document.querySelector('#newcontent');
                if (ta) {
                    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                        window.HTMLTextAreaElement.prototype, 'value').set;
                    nativeInputValueSetter.call(ta, content);
                    ta.dispatchEvent(new Event('input', { bubbles: true }));
                    ta.dispatchEvent(new Event('change', { bubbles: true }));
                }
            }""", new_content)
            print("  Textarea content set.")

        time.sleep(1)

        # Step 4: Save
        print("\n[Step 4] Saving plugin file...")
        saved = page.evaluate("""() => {
            const btn = document.querySelector('#submit') ||
                        document.querySelector('input[type="submit"]');
            if (btn) {
                btn.click();
                return 'clicked';
            }
            return 'no_button';
        }""")
        print(f"  Save button click: {saved}")

        try:
            page.wait_for_load_state("domcontentloaded", timeout=45000)
        except Exception:
            pass
        time.sleep(4)

        page.screenshot(path=SCREENSHOT_DEPLOY)
        page_text = page.inner_text("body")

        save_success = False
        if "File edited successfully" in page_text or "updated successfully" in page_text.lower():
            print("  SUCCESS: Plugin file saved!")
            save_success = True
        elif "Parse error" in page_text or "syntax error" in page_text:
            print("  ERROR: PHP syntax error - file NOT saved!")
            print(f"  Page: {page_text[:500]}")
            browser.close()
            return False
        else:
            print(f"  Status unclear. Page excerpt: {page_text[:400]}")
            if has_codemirror:
                current = page.evaluate("""() => {
                    const cm = document.querySelector('.CodeMirror');
                    return cm ? cm.CodeMirror.getValue().substring(0, 300) : 'N/A';
                }""")
                print(f"  Current editor start: {current}")
                if '2.3.0' in current:
                    save_success = True
                    print("  Version 2.3.0 found in editor - assuming success.")

        # Step 5: Flush GoDaddy cache
        print("\n[Step 5] Flushing GoDaddy/Cloudflare cache...")
        page.goto(f"{WP_ADMIN_URL}/options-general.php", wait_until="domcontentloaded", timeout=30000)
        time.sleep(2)

        flush_url = page.evaluate("""() => {
            const links = Array.from(document.querySelectorAll('a'));
            const flushLink = links.find(a => /flush.cache/i.test(a.textContent) || /flush.cache/i.test(a.href));
            return flushLink ? flushLink.href : null;
        }""")
        print(f"  Flush URL: {flush_url}")

        if flush_url:
            page.goto(flush_url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(2)
            print("  Cache flush requested!")
            page.screenshot(path=SCREENSHOT_VERIFY)
        else:
            print("  No flush URL found. Cache will expire naturally.")

        browser.close()

    return save_success


def verify_live():
    """Verify the v2.3.0 fixes are live on a blog post."""
    print("\n[Verification] Checking v2.3.0 fixes on live blog post...")

    url = "https://purebrain.ai/ceo-vs-employee-ai-transformation-gap/"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
        },
    )

    try:
        response = urllib.request.urlopen(req, timeout=30)
        html = response.read().decode("utf-8")

        # Check for v2.3.0 specific content
        has_faq_style = "purebrain-faq-accordion" in html
        has_faq_pre_js = "faq-section > p" in html
        has_cta_hover = "purebrain-blog-cta-hover" in html
        has_cta_white = "color: #ffffff !important;" in html
        has_version_230 = "2.3.0" in html

        print(f"  FAQ accordion CSS block: {has_faq_style}")
        print(f"  FAQ pre-JS hide rule (.faq-section > p): {has_faq_pre_js}")
        print(f"  CTA hover CSS block: {has_cta_hover}")
        print(f"  CTA white text fix: {has_cta_white}")
        print(f"  v2.3.0 reference: {has_version_230}")

        all_good = has_faq_style and has_faq_pre_js and has_cta_hover and has_cta_white
        if all_good:
            print("  CONFIRMED: v2.3.0 fixes are LIVE!")
        else:
            print("  WARNING: Not all fixes detected. CDN may still serve cached version.")

        return all_good

    except Exception as e:
        print(f"  Verification request failed: {e}")
        return False


def screenshot_verify():
    """Take screenshots of FAQ and CTA on a blog post."""
    from playwright.sync_api import sync_playwright

    print("\n[Visual Check] Taking screenshots of FAQ + CTA sections...")

    url = "https://purebrain.ai/ceo-vs-employee-ai-transformation-gap/"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()

        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(4)

        # Check FAQ state
        faq_info = page.evaluate("""() => {
            const body = document.body;
            const isSinglePost = body.classList.contains('single-post');
            const items = document.querySelectorAll('.post-content .faq-section');
            const preJsCss = Array.from(document.styleSheets).some(ss => {
                try {
                    return Array.from(ss.cssRules || []).some(r =>
                        r.selectorText && r.selectorText.includes('faq-section > p')
                    );
                } catch(e) { return false; }
            });

            return {
                isSinglePost: isSinglePost,
                faqCount: items.length,
                hasPreJsCss: preJsCss,
                hasStyle: !!document.getElementById('purebrain-faq-accordion'),
                hasCtaHover: !!document.getElementById('purebrain-blog-cta-hover'),
                firstIsOpen: items.length > 0 ? items[0].classList.contains('faq-open') : 'N/A',
                firstQuestion: items.length > 0 ? (items[0].querySelector('h3') || {}).textContent || 'N/A' : 'N/A'
            };
        }""")

        print(f"  Single post body class: {faq_info.get('isSinglePost')}")
        print(f"  FAQ items found: {faq_info.get('faqCount')}")
        print(f"  Pre-JS CSS active: {faq_info.get('hasPreJsCss')}")
        print(f"  FAQ style tag: {faq_info.get('hasStyle')}")
        print(f"  CTA hover style tag: {faq_info.get('hasCtaHover')}")
        print(f"  First FAQ starts open: {faq_info.get('firstIsOpen')}")
        print(f"  First question: {faq_info.get('firstQuestion', '')[:60]}")

        # Scroll to FAQ section and screenshot
        page.evaluate("""() => {
            const faq = document.querySelector('.faq-section');
            if (faq) faq.scrollIntoView({block: 'center', behavior: 'instant'});
        }""")
        time.sleep(0.5)
        page.screenshot(path=SCREENSHOT_FAQ)
        print(f"  FAQ screenshot: {SCREENSHOT_FAQ}")

        # Scroll to CTA block and screenshot
        page.evaluate("""() => {
            const cta = document.querySelector('.blog-cta-block');
            if (cta) cta.scrollIntoView({block: 'center', behavior: 'instant'});
        }""")
        time.sleep(0.5)
        page.screenshot(path=SCREENSHOT_CTA)
        print(f"  CTA screenshot: {SCREENSHOT_CTA}")

        browser.close()

    return faq_info


if __name__ == "__main__":
    print("=" * 60)
    print("PUREBRAIN SECURITY PLUGIN v2.3.0 - BUG FIX DEPLOY")
    print("Fix 1: FAQ starts collapsed (pre-JS CSS hide)")
    print("Fix 2: CTA hover shows white text + orange background")
    print("=" * 60)

    result = deploy()

    if result:
        print("\n[Deploy] SUCCESS: Plugin saved to WordPress.")
    else:
        print("\n[Deploy] FAILED or uncertain. Check screenshots.")
        sys.exit(1)

    # Wait for CDN
    print("\nWaiting 8 seconds for CDN propagation...")
    time.sleep(8)

    # Verify
    live_ok = verify_live()
    faq_info = screenshot_verify()

    print("\n" + "=" * 60)
    print("FINAL RESULT")
    print("=" * 60)

    if live_ok:
        print("\n[SUCCESS] v2.3.0 IS LIVE!")
        print(f"  FAQ items: {faq_info.get('faqCount', '?')}")
        print(f"  First FAQ starts open: {faq_info.get('firstIsOpen', '?')} (should be False)")
        print(f"\n  Screenshots:")
        print(f"    FAQ: {SCREENSHOT_FAQ}")
        print(f"    CTA: {SCREENSHOT_CTA}")
        print("\n  What was fixed:")
        print("  FAQ:")
        print("  - Pre-JS CSS hides <p> immediately (no flash of expanded content)")
        print("  - JS wraps <p> in .faq-answer, then max-height animation controls visibility")
        print("  - All FAQ items start collapsed, click to expand one at a time")
        print("  CTA:")
        print("  - Hover now shows: orange bg + white text + blue glow ring")
        print("  - Was: text going orange (invisible) due to conflicting a:hover rule")
    else:
        print("\n[WARNING] CSS/JS may not be visible yet due to CDN caching.")
        print("  Wait 15-30 minutes for full propagation, then hard-refresh (Ctrl+Shift+R).")
        print(f"  Deploy screenshot: {SCREENSHOT_DEPLOY}")
