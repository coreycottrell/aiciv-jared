#!/usr/bin/env python3
"""
Fix Blog Navigation v2 - Proper approach.

The problem: Single blog posts and category/archive pages use the WordPress
theme template (Artistics) which has a header containing only a 512x512 logo.
The CSS hides this completely. We need to:

1. Remove the bad v1 override (which showed the giant logo)
2. On blog-related pages (single-post, archive, category), show the header
   but constrain the logo to a reasonable navbar size
3. Keep the header hidden on landing pages (homepage, Elementor Canvas pages)

The blog INDEX page (/blog/) uses Elementor Canvas template with its own
built-in nav bar, so it doesn't need this fix.
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
CAPTCHA_ANSWER_FILE = "/tmp/navfix2_captcha_answer.txt"


def screenshot(page, label, timeout_ms=90000):
    """Take a screenshot with consistent naming."""
    path = f"{SCREENSHOT_DIR}/navfix2_{label}_{TIMESTAMP}.png"
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
    print(f"PureBrain.ai Blog Navigation Fix v2 - {datetime.now()}")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=2,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        )
        page = context.new_page()
        page.set_default_timeout(60000)

        # ============================================
        # STEP 1: Login
        # ============================================
        print("\n[1] Loading login page...")
        page.goto(WP_ADMIN_URL, wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)

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
                    return {src: captchaImg.getAttribute('src'), alt: captchaImg.getAttribute('alt'),
                            width: rect.width, height: rect.height, x: rect.x, y: rect.y};
                }
                return null;
            }
        """)

        screenshot(page, "01_login_page")

        if captcha_info:
            print(f"  CAPTCHA detected: {captcha_info}")
            captcha_imgs = page.locator("form img")
            for i in range(captcha_imgs.count()):
                img = captcha_imgs.nth(i)
                src = img.get_attribute("src") or ""
                if "w-logo" not in src and "wordpress-logo" not in src:
                    captcha_path = f"{SCREENSHOT_DIR}/navfix2_captcha_{TIMESTAMP}.png"
                    img.screenshot(path=captcha_path)
                    print(f"  CAPTCHA image: {captcha_path}")
                    break

            print(f"\n  Waiting for CAPTCHA answer in: {CAPTCHA_ANSWER_FILE}")
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

        screenshot(page, "03_customizer")

        try:
            page.wait_for_selector('.CodeMirror', state='visible', timeout=45000)
            print("  CodeMirror editor found!")
        except:
            print("  WARNING: CodeMirror not found, waiting longer...")
            time.sleep(15)
            try:
                page.wait_for_selector('.CodeMirror', state='visible', timeout=30000)
                print("  CodeMirror found after extra wait!")
            except:
                print("  ERROR: CodeMirror not found!")
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
        backup_path = f"{BACKUP_DIR}/additional_css_backup_v2_{TIMESTAMP}.css"
        with open(backup_path, 'w') as f:
            f.write(current_css)
        print(f"  Backup saved: {backup_path}")

        # ============================================
        # STEP 4: Remove old bad override (v1)
        # ============================================
        print("\n[4] Removing old Blog Navigation Fix v1 (if present)...")
        if "BLOG NAVIGATION FIX" in current_css:
            current_css = re.sub(
                r'/\* === BLOG NAVIGATION FIX.*?/\* === END BLOG NAVIGATION FIX === \*/',
                '',
                current_css,
                flags=re.DOTALL
            ).rstrip()
            print("  Removed old v1 fix")
        else:
            print("  No old v1 fix found")

        # ============================================
        # STEP 5: Build the proper navigation fix
        # ============================================
        print("\n[5] Building proper navigation fix v2...")

        # Strategy:
        # On single-post, archive, category pages (which use the theme template):
        # 1. Show the header but make it a proper slim navbar
        # 2. Constrain the logo to 40px height
        # 3. Add a "Back to Blog" link via the breadcrumb styling
        # 4. Style the navbar bar properly with PureBrain brand colors

        NAV_FIX_V2 = """

/* === BLOG NAVIGATION FIX v2 (Feb 18, 2026) === */
/* Show and style theme header as slim navbar on blog-related pages */
/* These pages use WordPress theme template (not Elementor Canvas) */

/* 1. Show the header on blog-related pages */
body.single-post header#masthead,
body.single-post .header-sticky,
body.single-post nav.navbar,
body.single-post .navbar-brand,
body.archive header#masthead,
body.archive .header-sticky,
body.archive nav.navbar,
body.archive .navbar-brand,
body.category header#masthead,
body.category .header-sticky,
body.category nav.navbar,
body.category .navbar-brand,
body.search header#masthead,
body.search .header-sticky,
body.search nav.navbar,
body.search .navbar-brand,
body.tag header#masthead,
body.tag .header-sticky,
body.tag nav.navbar,
body.tag .navbar-brand {
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
}

/* 2. Style the header as a slim navbar */
body.single-post header#masthead,
body.archive header#masthead,
body.category header#masthead,
body.search header#masthead,
body.tag header#masthead {
    height: auto !important;
    max-height: 70px !important;
    overflow: hidden !important;
    background: #0a0a0a !important;
    border-bottom: 2px solid #f1420b !important;
    position: sticky !important;
    top: 0 !important;
    z-index: 9999 !important;
    padding: 0 !important;
}

/* Admin bar offset when logged in */
body.single-post.admin-bar header#masthead,
body.archive.admin-bar header#masthead,
body.category.admin-bar header#masthead,
body.search.admin-bar header#masthead,
body.tag.admin-bar header#masthead {
    top: 32px !important;
}

/* 3. Style the sticky wrapper */
body.single-post .header-sticky,
body.archive .header-sticky,
body.category .header-sticky,
body.search .header-sticky,
body.tag .header-sticky {
    height: auto !important;
    max-height: 70px !important;
    padding: 10px 20px !important;
}

/* 4. Style the navbar container */
body.single-post nav.navbar,
body.archive nav.navbar,
body.category nav.navbar,
body.search nav.navbar,
body.tag nav.navbar {
    height: auto !important;
    max-height: 50px !important;
    padding: 0 !important;
}

body.single-post nav.navbar .container,
body.archive nav.navbar .container,
body.category nav.navbar .container,
body.search nav.navbar .container,
body.tag nav.navbar .container {
    display: flex !important;
    align-items: center !important;
    height: 50px !important;
    max-width: 1300px !important;
    padding: 0 20px !important;
}

/* 5. Constrain the logo to a proper navbar size */
body.single-post .navbar-brand,
body.archive .navbar-brand,
body.category .navbar-brand,
body.search .navbar-brand,
body.tag .navbar-brand {
    height: 40px !important;
    width: auto !important;
    padding: 0 !important;
    margin: 0 !important;
}

body.single-post .navbar-brand img.logo,
body.archive .navbar-brand img.logo,
body.category .navbar-brand img.logo,
body.search .navbar-brand img.logo,
body.tag .navbar-brand img.logo {
    height: 40px !important;
    width: 40px !important;
    object-fit: contain !important;
}

/* 6. Style breadcrumb as a secondary nav below header */
body.single-post .breadcrumb-trail,
body.archive .breadcrumb-trail,
body.category .breadcrumb-trail,
body.search .breadcrumb-trail,
body.tag .breadcrumb-trail {
    background: #111 !important;
    padding: 8px 20px !important;
    border-bottom: 1px solid rgba(42,147,193,0.3) !important;
}

body.single-post .breadcrumb-trail a,
body.archive .breadcrumb-trail a,
body.category .breadcrumb-trail a,
body.search .breadcrumb-trail a,
body.tag .breadcrumb-trail a {
    color: #2a93c1 !important;
    text-decoration: none !important;
}

body.single-post .breadcrumb-trail a:hover,
body.archive .breadcrumb-trail a:hover,
body.category .breadcrumb-trail a:hover,
body.search .breadcrumb-trail a:hover,
body.tag .breadcrumb-trail a:hover {
    color: #f1420b !important;
}

/* 7. Add "Back to Blog" link using CSS - via ::after on navbar container */
body.single-post nav.navbar .container::after,
body.archive nav.navbar .container::after,
body.category nav.navbar .container::after,
body.search nav.navbar .container::after,
body.tag nav.navbar .container::after {
    content: "Home  |  Blog  |  AI Assessment" !important;
    display: flex !important;
    align-items: center !important;
    color: rgba(255,255,255,0.6) !important;
    font-size: 14px !important;
    font-weight: 400 !important;
    letter-spacing: 1px !important;
    margin-left: auto !important;
}

/* === END BLOG NAVIGATION FIX v2 === */"""

        # Remove old v2 if present (for re-runs)
        if "BLOG NAVIGATION FIX v2" in current_css:
            current_css = re.sub(
                r'/\* === BLOG NAVIGATION FIX v2.*?/\* === END BLOG NAVIGATION FIX v2 === \*/',
                '',
                current_css,
                flags=re.DOTALL
            ).rstrip()
            print("  Removed previous v2 fix")

        new_css = current_css + NAV_FIX_V2
        print(f"  New CSS: {len(new_css)} chars (was {len(current_css)}, added {len(NAV_FIX_V2)})")

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
        screenshot(page, "04_css_applied")

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
        screenshot(page, "05_published")

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
            ("https://purebrain.ai/ceo-vs-employee-ai-transformation-gap/", "single_post"),
            ("https://purebrain.ai/blog/", "blog_index"),
            ("https://purebrain.ai/", "homepage"),
            ("https://purebrain.ai/category/for-teams/", "category"),
            ("https://purebrain.ai/why-ai-memory-changes-everything/", "single_post_2"),
        ]

        for test_url, label in test_pages:
            print(f"\n  Testing {label}: {test_url}")
            vp.goto(test_url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(5)
            vp.evaluate("() => location.reload(true)")
            time.sleep(5)

            path = f"{SCREENSHOT_DIR}/navfix2_VERIFY_{label}_{TIMESTAMP}.png"
            try:
                vp.screenshot(path=path, timeout=60000)
                print(f"    Screenshot: {path}")
            except Exception as e:
                print(f"    Screenshot failed: {e}")

            # Nav element check
            nav_check = vp.evaluate("""
                () => {
                    const results = {};
                    const header = document.querySelector('header#masthead');
                    if (header) {
                        const style = getComputedStyle(header);
                        const rect = header.getBoundingClientRect();
                        results['header#masthead'] = {
                            display: style.display,
                            height: Math.round(rect.height),
                            maxHeight: style.maxHeight,
                            visible: rect.height > 0 && style.display !== 'none'
                        };
                    }
                    const logo = document.querySelector('.navbar-brand img.logo');
                    if (logo) {
                        const rect = logo.getBoundingClientRect();
                        results['logo'] = {
                            height: Math.round(rect.height),
                            width: Math.round(rect.width)
                        };
                    }
                    results['body_classes'] = document.body.className.substring(0, 200);
                    return results;
                }
            """)
            print(f"    Nav: {nav_check}")

        vp.close()
        browser.close()
        print("\n" + "=" * 60)
        print("DONE! Blog navigation fix v2 deployed.")
        print(f"CSS backup: {backup_path}")
        print("=" * 60)
        return 0


if __name__ == "__main__":
    sys.exit(main())
