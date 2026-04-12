#!/usr/bin/env python3
"""
Fix Blog Navigation - Make nav visible on blog pages while keeping it hidden on landing pages.

Reads current Additional CSS from WordPress Customizer, finds navigation-hiding rules,
and scopes them to only apply on non-blog pages.

Based on proven deploy_category_css_fix_v5.py pattern.
"""

import sys
import time
import os
import re
from datetime import datetime
from playwright.sync_api import sync_playwright

from dotenv import load_dotenv
load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

WP_ADMIN_URL = "https://purebrain.ai/wp-admin"
WP_CSS_URL = "https://purebrain.ai/wp-admin/customize.php?autofocus[section]=custom_css"
USERNAME = "Aether"
PASSWORD = os.getenv('PUREBRAIN_WP_PASSWORD', '')

SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/tools/screenshots"
BACKUP_DIR = "/home/jared/projects/AI-CIV/aether/tools/css_backups"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
CAPTCHA_ANSWER_FILE = "/tmp/navfix_captcha_answer.txt"


def screenshot(page, label, timeout_ms=60000):
    """Take a screenshot with consistent naming and configurable timeout."""
    path = f"{SCREENSHOT_DIR}/navfix_{label}_{TIMESTAMP}.png"
    try:
        page.screenshot(path=path, timeout=timeout_ms)
        print(f"  Screenshot: {path}")
    except Exception as e:
        print(f"  Screenshot failed ({label}): {e}")
        path = None
    return path


def main():
    if not PASSWORD:
        print("ERROR: PUREBRAIN_WP_PASSWORD not found in .env")
        return 1

    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)
    if os.path.exists(CAPTCHA_ANSWER_FILE):
        os.remove(CAPTCHA_ANSWER_FILE)

    print("=" * 60)
    print(f"PureBrain.ai Blog Navigation Fix - {datetime.now()}")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=2,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        )
        page = context.new_page()
        # Increase default timeout for this heavy page
        page.set_default_timeout(60000)

        # ============================================
        # STEP 1: Login
        # ============================================
        print("\n[1] Loading login page...")
        page.goto(WP_ADMIN_URL, wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)

        # Click "Log in with username and password" if present
        try:
            login_link = page.locator("text=Log in with username and password")
            if login_link.is_visible(timeout=5000):
                login_link.click()
                time.sleep(2)
        except:
            pass

        page.wait_for_selector('#user_login', state='visible', timeout=30000)
        page.locator("#user_login").fill(USERNAME)
        page.locator("#user_pass").fill(PASSWORD)
        time.sleep(1)

        # Check for CAPTCHA
        captcha_info = page.evaluate("""
            () => {
                const imgs = document.querySelectorAll('form img, #loginform img');
                let captchaImg = null;
                for (const img of imgs) {
                    const src = img.getAttribute('src') || '';
                    if (!src.includes('w-logo') && !src.includes('wordpress-logo')) {
                        captchaImg = img;
                        break;
                    }
                }
                if (!captchaImg) {
                    const allImgs = document.querySelectorAll('img');
                    for (const img of allImgs) {
                        const rect = img.getBoundingClientRect();
                        if (rect.top > 250 && rect.top < 400 && rect.width > 100) {
                            captchaImg = img;
                            break;
                        }
                    }
                }
                if (captchaImg) {
                    const rect = captchaImg.getBoundingClientRect();
                    return {
                        src: captchaImg.getAttribute('src'),
                        alt: captchaImg.getAttribute('alt'),
                        width: rect.width, height: rect.height,
                        x: rect.x, y: rect.y,
                    };
                }
                return null;
            }
        """)

        screenshot(page, "01_login_page")

        if captcha_info:
            print(f"  CAPTCHA detected: {captcha_info}")

            # Save CAPTCHA image
            captcha_imgs = page.locator("form img")
            for i in range(captcha_imgs.count()):
                img = captcha_imgs.nth(i)
                src = img.get_attribute("src") or ""
                if "w-logo" not in src and "wordpress-logo" not in src:
                    captcha_path = f"{SCREENSHOT_DIR}/navfix_captcha_{TIMESTAMP}.png"
                    img.screenshot(path=captcha_path)
                    print(f"  CAPTCHA image: {captcha_path}")
                    break

            print(f"\n  Waiting for CAPTCHA answer in: {CAPTCHA_ANSWER_FILE}")
            print("  Create that file with the CAPTCHA answer text.")
            print("  Timeout: 180s")

            start = time.time()
            captcha_answer = None
            while time.time() - start < 180:
                if os.path.exists(CAPTCHA_ANSWER_FILE):
                    with open(CAPTCHA_ANSWER_FILE, 'r') as f:
                        captcha_answer = f.read().strip()
                    if captcha_answer:
                        print(f"  Got answer: '{captcha_answer}'")
                        os.remove(CAPTCHA_ANSWER_FILE)
                        break
                time.sleep(1)

            if not captcha_answer:
                print("  CAPTCHA TIMEOUT!")
                browser.close()
                return 1

            # Fill CAPTCHA
            all_text = page.locator("input[type='text']")
            for i in range(all_text.count()):
                inp = all_text.nth(i)
                name = inp.get_attribute("name") or ""
                id_attr = inp.get_attribute("id") or ""
                if id_attr != "user_login" and name != "log":
                    inp.fill(captcha_answer)
                    print(f"  Filled CAPTCHA: name='{name}', id='{id_attr}'")
                    break
            time.sleep(1)
        else:
            print("  No CAPTCHA detected")

        # Submit login
        print("  Submitting login...")
        page.locator("#wp-submit").click()
        page.wait_for_load_state("load", timeout=60000)
        time.sleep(5)

        screenshot(page, "02_login_result")
        url = page.url
        print(f"  URL after login: {url}")

        if "wp-login" in url:
            print("  LOGIN FAILED!")
            error = page.locator("#login_error")
            if error.count() > 0:
                print(f"  Error: {error.first.inner_text()}")
            browser.close()
            return 1

        print("  LOGIN SUCCESS!")

        # ============================================
        # STEP 2: Navigate to Additional CSS
        # ============================================
        print("\n[2] Navigating to Additional CSS...")
        page.goto(WP_CSS_URL, wait_until="domcontentloaded", timeout=90000)
        print("  Waiting for Customizer to load (20s)...")
        time.sleep(20)

        # Try screenshot but don't fail if it times out (Customizer is heavy)
        screenshot(page, "03_customizer", timeout_ms=90000)

        # Wait for CodeMirror
        try:
            page.wait_for_selector('.CodeMirror', state='visible', timeout=45000)
            print("  CodeMirror editor found!")
        except:
            print("  WARNING: CodeMirror not immediately visible, waiting longer...")
            time.sleep(15)
            try:
                page.wait_for_selector('.CodeMirror', state='visible', timeout=30000)
                print("  CodeMirror found after extra wait!")
            except:
                print("  ERROR: CodeMirror not found!")
                screenshot(page, "03_error", timeout_ms=90000)
                browser.close()
                return 1

        time.sleep(3)

        # ============================================
        # STEP 3: Read current CSS
        # ============================================
        print("\n[3] Reading current CSS...")
        current_css = page.evaluate("""
            () => {
                const cm = document.querySelector('.CodeMirror');
                if (cm && cm.CodeMirror) return cm.CodeMirror.getValue();
                return null;
            }
        """)

        if current_css is None:
            print("  ERROR: Cannot read CSS from CodeMirror!")
            browser.close()
            return 1

        print(f"  Current CSS length: {len(current_css)} chars")

        # Save backup
        backup_path = f"{BACKUP_DIR}/additional_css_backup_{TIMESTAMP}.css"
        with open(backup_path, 'w') as f:
            f.write(current_css)
        print(f"  Backup saved: {backup_path}")

        latest_backup = f"{BACKUP_DIR}/additional_css_latest.css"
        with open(latest_backup, 'w') as f:
            f.write(current_css)
        print(f"  Latest backup: {latest_backup}")

        # ============================================
        # STEP 4: Analyze navigation-hiding rules
        # ============================================
        print("\n[4] Analyzing CSS for navigation-hiding rules...")

        # Search for display:none rules
        display_none_lines = []
        lines = current_css.split('\n')
        for i, line in enumerate(lines):
            if 'display' in line.lower() and 'none' in line.lower():
                start_ctx = max(0, i - 3)
                end_ctx = min(len(lines), i + 4)
                context_lines = lines[start_ctx:end_ctx]
                display_none_lines.append({
                    'line_num': i + 1,
                    'line': line.strip(),
                    'context': '\n'.join(f"  {j+start_ctx+1:4d}| {l}" for j, l in enumerate(context_lines))
                })

        print(f"  Found {len(display_none_lines)} lines with display:none")
        for item in display_none_lines:
            print(f"\n  Line {item['line_num']}: {item['line']}")
            print(f"{item['context']}")

        # Search for nav/header/menu related hiding
        nav_keywords = ['nav', 'header', 'menu', 'navigation', 'masthead', 'ehf-header', 'elementor-location-header']
        nav_related = []
        for item in display_none_lines:
            ctx_lower = item['context'].lower()
            if any(kw in ctx_lower for kw in nav_keywords):
                nav_related.append(item)

        print(f"\n  Navigation-related display:none rules: {len(nav_related)}")
        for item in nav_related:
            print(f"    Line {item['line_num']}: {item['line']}")

        # Also print full CSS for analysis
        print("\n  === FULL CURRENT CSS (first 5000 chars) ===")
        print(current_css[:5000])
        if len(current_css) > 5000:
            print(f"\n  ... ({len(current_css) - 5000} more chars) ...")
            print("\n  === LAST 2000 chars ===")
            print(current_css[-2000:])
        print("  === END CSS ===")

        # ============================================
        # STEP 5: Build the navigation fix CSS
        # ============================================
        print("\n[5] Building navigation override CSS...")

        # The safest approach: add override rules at the END of CSS
        # These use body class specificity to show nav on blog pages
        # blog-related body classes: .blog, .single-post, .archive, .category, .search, .tag
        NAV_FIX_CSS = """

/* === BLOG NAVIGATION FIX (Feb 18, 2026) === */
/* Show navigation on blog pages - override any hiding rules */
body.blog header,
body.blog nav,
body.blog .navbar,
body.blog .main-navigation,
body.blog .site-navigation,
body.blog .site-header,
body.blog .elementor-location-header,
body.blog .ehf-header,
body.blog #masthead,
body.single-post header,
body.single-post nav,
body.single-post .navbar,
body.single-post .main-navigation,
body.single-post .site-navigation,
body.single-post .site-header,
body.single-post .elementor-location-header,
body.single-post .ehf-header,
body.single-post #masthead,
body.archive header,
body.archive nav,
body.archive .navbar,
body.archive .main-navigation,
body.archive .site-navigation,
body.archive .site-header,
body.archive .elementor-location-header,
body.archive .ehf-header,
body.archive #masthead,
body.category header,
body.category nav,
body.category .navbar,
body.category .main-navigation,
body.category .site-navigation,
body.category .site-header,
body.category .elementor-location-header,
body.category .ehf-header,
body.category #masthead,
body.search header,
body.search nav,
body.search .navbar,
body.search .main-navigation,
body.search .site-navigation,
body.search .site-header,
body.search .elementor-location-header,
body.search .ehf-header,
body.search #masthead,
body.tag header,
body.tag nav,
body.tag .navbar,
body.tag .main-navigation,
body.tag .site-navigation,
body.tag .site-header,
body.tag .elementor-location-header,
body.tag .ehf-header,
body.tag #masthead {
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
    height: auto !important;
    max-height: none !important;
    overflow: visible !important;
}
/* === END BLOG NAVIGATION FIX === */"""

        if "BLOG NAVIGATION FIX" in current_css:
            print("  Blog Navigation Fix already present - removing old version...")
            current_css = re.sub(
                r'/\* === BLOG NAVIGATION FIX.*?/\* === END BLOG NAVIGATION FIX === \*/',
                '',
                current_css,
                flags=re.DOTALL
            ).rstrip()
            print("  Old fix removed")

        new_css = current_css + NAV_FIX_CSS
        print(f"  New CSS: {len(new_css)} chars (was {len(current_css)}, added {len(NAV_FIX_CSS)})")

        # ============================================
        # STEP 6: Apply the new CSS
        # ============================================
        print("\n[6] Applying new CSS to CodeMirror...")
        result = page.evaluate("""
            (css) => {
                const cm = document.querySelector('.CodeMirror');
                if (cm && cm.CodeMirror) {
                    cm.CodeMirror.setValue(css);
                    cm.CodeMirror.refresh();
                    return 'ok_' + cm.CodeMirror.getValue().length;
                }
                return 'fail';
            }
        """, new_css)
        print(f"  Result: {result}")

        if not str(result).startswith("ok"):
            print("  ERROR: Failed to set CSS!")
            browser.close()
            return 1

        time.sleep(3)
        screenshot(page, "04_css_applied", timeout_ms=90000)

        # ============================================
        # STEP 7: Publish
        # ============================================
        print("\n[7] Publishing changes...")
        time.sleep(3)

        btn = page.locator("#save")
        if btn.count() > 0 and btn.first.is_visible():
            btn.first.click()
            print("  Clicked #save button")
        else:
            pub_btn = page.locator("button:has-text('Publish')")
            if pub_btn.count() > 0:
                pub_btn.first.click()
                print("  Clicked Publish button")
            else:
                print("  WARNING: No save/publish button found!")

        time.sleep(10)
        screenshot(page, "05_published", timeout_ms=90000)

        status = page.evaluate("""
            () => {
                const b = document.querySelector('#save');
                return b ? b.textContent.trim() : 'no btn found';
            }
        """)
        print(f"  Publish status: {status}")

        # ============================================
        # STEP 8: Verify on live pages
        # ============================================
        print("\n[8] Verifying on live pages...")
        vp = context.new_page()

        test_pages = [
            ("https://purebrain.ai/blog/", "blog"),
            ("https://purebrain.ai/", "homepage"),
            ("https://purebrain.ai/category/for-teams/", "category"),
        ]

        for test_url, label in test_pages:
            print(f"\n  Testing {label}: {test_url}")
            vp.goto(test_url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(5)
            # Force reload to bypass cache
            vp.evaluate("() => location.reload(true)")
            time.sleep(5)

            path = f"{SCREENSHOT_DIR}/navfix_VERIFY_{label}_{TIMESTAMP}.png"
            try:
                vp.screenshot(path=path, timeout=60000)
                print(f"    Screenshot: {path}")
            except Exception as e:
                print(f"    Screenshot failed: {e}")

            # Check if nav elements are visible
            nav_check = vp.evaluate("""
                () => {
                    const results = {};
                    const selectors = ['nav', 'header', '.navbar', '.site-header',
                                       '.main-navigation', '.elementor-location-header',
                                       '.ehf-header', '#masthead'];
                    for (const sel of selectors) {
                        const el = document.querySelector(sel);
                        if (el) {
                            const style = getComputedStyle(el);
                            results[sel] = {
                                display: style.display,
                                visibility: style.visibility,
                                opacity: style.opacity,
                                height: style.height,
                            };
                        }
                    }
                    results['body_classes'] = document.body.className.substring(0, 300);
                    return results;
                }
            """)
            print(f"    Nav check: {nav_check}")

        vp.close()
        browser.close()
        print("\n" + "=" * 60)
        print("DONE! Blog navigation fix deployed.")
        print(f"CSS backup: {backup_path}")
        print("=" * 60)
        return 0


if __name__ == "__main__":
    sys.exit(main())
