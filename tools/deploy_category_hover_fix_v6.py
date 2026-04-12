#!/usr/bin/env python3
"""
Deploy Category + Universal Hover Fix - v6
Fixes:
1. Orange dot in top-left (#magic-cursor / #ball) - HIDE
2. Universal hover rule: orange bg hover -> white text
3. Category page post title hover -> white text
4. Breadcrumb readable + white on hover
5. Category tag links white on hover
6. Newsletter subscribe link white border on hover
7. Share icons reinforced white

Uses Playwright with optional CAPTCHA solving via vision.
If no CAPTCHA present, submits directly.
Appends to existing Additional CSS (does NOT replace).
"""

import sys
import time
import os
import requests
from datetime import datetime
from playwright.sync_api import sync_playwright

from dotenv import load_dotenv
load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

WP_ADMIN_URL = "https://purebrain.ai/wp-admin"
WP_CSS_URL = "https://purebrain.ai/wp-admin/customize.php?autofocus[section]=custom_css"
USERNAME = "Aether"
PASSWORD = os.getenv('PUREBRAIN_WP_PASSWORD', '')

SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/tools/screenshots"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
CAPTCHA_ANSWER_FILE = "/tmp/category_hover_fix_captcha.txt"

# The new CSS to append
NEW_CSS = """

/* ============================================================ */
/* CATEGORY + UNIVERSAL HOVER FIX - Feb 18, 2026               */
/* ============================================================ */

/* 1. HIDE MAGIC CURSOR ORANGE DOT (visible in top-left corner) */
#magic-cursor,
#ball {
    display: none !important;
}

/* 2. UNIVERSAL HOVER RULE - Any orange-background hover = white text */
/* Applied site-wide as requested */
a:hover,
.entry-title a:hover,
h1 a:hover,
h2 a:hover,
h3 a:hover,
h4 a:hover,
h5 a:hover,
h6 a:hover,
.post-title a:hover,
.breadcrumb-trail a:hover,
.trail-items a:hover,
.cat-links a:hover,
[rel="category tag"]:hover,
.tags-links a:hover,
.wp-block-latest-posts__post-title:hover,
.related-reading a:hover,
.related-post-title:hover,
.nav-links a:hover,
.post-navigation a:hover,
.page-numbers:hover,
.pagination a:hover {
    color: #ffffff !important;
}

/* 3. CATEGORY PAGE - Post titles specifically */
body.category .post-item h3 a:hover,
body.archive .post-item h3 a:hover,
body.category .entry-title a:hover,
body.archive .entry-title a:hover,
body.category article h2 a:hover,
body.category article h3 a:hover,
body.archive article h2 a:hover,
body.archive article h3 a:hover {
    color: #ffffff !important;
}

/* 4. BREADCRUMB - Readable + white on hover */
.breadcrumb-trail,
.breadcrumb-trail .trail-items,
.breadcrumb-trail .trail-item {
    color: #cccccc;
}
.breadcrumb-trail a {
    color: #2a93c1;
    text-decoration: none;
}
.breadcrumb-trail a:hover {
    color: #ffffff !important;
    background: transparent;
}
.breadcrumb-trail .trail-end span {
    color: #ffffff;
}

/* 5. CATEGORY TAGS (near date on posts) - Blue, white on hover */
.cat-links a,
[rel="category tag"],
.tags-links a {
    color: #2a93c1;
    text-decoration: none;
    transition: color 0.2s ease;
}
.cat-links a:hover,
[rel="category tag"]:hover,
.tags-links a:hover {
    color: #ffffff !important;
}

/* 6. NEWSLETTER SUBSCRIBE LINK - White border on hover */
a[href*="newsletter"],
a[href*="utm_campaign=newsletter"] {
    border: 1px solid transparent;
    padding: 2px 4px;
    border-radius: 3px;
    transition: border-color 0.2s ease, color 0.2s ease;
}
a[href*="newsletter"]:hover,
a[href*="utm_campaign=newsletter"]:hover {
    border-color: #ffffff !important;
    color: #ffffff !important;
}

/* 7. SHARE ICONS - White icons on blue bg, stay white on hover */
.pt-social-share a {
    background: #2a93c1 !important;
    color: #ffffff !important;
    border-color: #2a93c1 !important;
}
.pt-social-share a:hover {
    background: #1a7aa8 !important;
    color: #ffffff !important;
    border-color: #1a7aa8 !important;
}
.pt-social-share a svg,
.pt-social-share a svg path {
    fill: #ffffff !important;
    color: #ffffff !important;
}

/* ============================================================ */
/* END CATEGORY + UNIVERSAL HOVER FIX                           */
/* ============================================================ */
"""

FIX_MARKER = "CATEGORY + UNIVERSAL HOVER FIX"


def has_captcha(page):
    """Check if the login form has a CAPTCHA image."""
    captcha_imgs = page.locator("form img")
    for i in range(captcha_imgs.count()):
        img = captcha_imgs.nth(i)
        src = img.get_attribute("src") or ""
        if "w-logo" not in src and "wordpress-logo" not in src:
            return True
    return False


def main():
    if not PASSWORD:
        print("ERROR: PUREBRAIN_WP_PASSWORD not found in .env")
        return 1

    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    if os.path.exists(CAPTCHA_ANSWER_FILE):
        os.remove(CAPTCHA_ANSWER_FILE)

    print("=" * 60)
    print(f"PureBrain Category + Hover Fix v6 - {datetime.now()}")
    print("=" * 60)

    with sync_playwright() as p:
        # Use device_scale_factor=2 for sharper CAPTCHA rendering (if present)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=2,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        )
        page = context.new_page()

        # ===== STEP 1: LOGIN PAGE =====
        print("\n[1] Loading login page...")
        page.goto(WP_ADMIN_URL, wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)

        # Click "Log in with username and password" if GoDaddy SSO shows
        try:
            login_link = page.locator("text=Log in with username and password")
            if login_link.is_visible(timeout=5000):
                print("  GoDaddy SSO detected - clicking standard login link...")
                login_link.click()
                time.sleep(2)
        except Exception:
            pass

        page.wait_for_selector('#user_login', state='visible', timeout=30000)
        page.locator("#user_login").fill(USERNAME)
        page.locator("#user_pass").fill(PASSWORD)
        time.sleep(1)

        # Save full page screenshot
        full_path = f"{SCREENSHOT_DIR}/hover_fix_v6_login_{TIMESTAMP}.png"
        page.screenshot(path=full_path)
        print(f"  Login page: {full_path}")

        # ===== STEP 2: HANDLE CAPTCHA (if present) =====
        if has_captcha(page):
            print("  CAPTCHA detected!")

            # Save CAPTCHA element screenshot
            captcha_imgs = page.locator("form img")
            for i in range(captcha_imgs.count()):
                img = captcha_imgs.nth(i)
                src = img.get_attribute("src") or ""
                if "w-logo" not in src and "wordpress-logo" not in src:
                    captcha_path = f"{SCREENSHOT_DIR}/hover_fix_v6_captcha_{TIMESTAMP}.png"
                    img.screenshot(path=captcha_path)
                    print(f"  CAPTCHA element: {captcha_path}")
                    break

            # Try to download raw CAPTCHA image
            captcha_info = page.evaluate("""
                () => {
                    const imgs = document.querySelectorAll('form img, #loginform img');
                    for (const img of imgs) {
                        const src = img.getAttribute('src') || '';
                        if (!src.includes('w-logo') && !src.includes('wordpress-logo')) {
                            return {src: src};
                        }
                    }
                    return null;
                }
            """)
            if captcha_info and captcha_info.get('src'):
                src = captcha_info['src']
                if not src.startswith('http'):
                    src = f"https://purebrain.ai{src}"
                try:
                    r = requests.get(src, timeout=10)
                    if r.status_code == 200:
                        raw_path = f"{SCREENSHOT_DIR}/hover_fix_v6_captcha_raw_{TIMESTAMP}.png"
                        with open(raw_path, 'wb') as f:
                            f.write(r.content)
                        print(f"  CAPTCHA raw: {raw_path} ({len(r.content)} bytes)")
                except Exception as e:
                    print(f"  Raw download failed: {e}")

            print(f"\n  Waiting for CAPTCHA answer in: {CAPTCHA_ANSWER_FILE}")
            print("  Write the answer to that file within 180 seconds.")

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
                print("  TIMEOUT waiting for CAPTCHA answer!")
                browser.close()
                return 1

            # Fill CAPTCHA answer
            print(f"  Filling CAPTCHA: '{captcha_answer}'")
            all_text = page.locator("input[type='text']")
            for i in range(all_text.count()):
                inp = all_text.nth(i)
                name = inp.get_attribute("name") or ""
                id_attr = inp.get_attribute("id") or ""
                if id_attr != "user_login" and name != "log":
                    inp.fill(captcha_answer)
                    print(f"  Filled: name='{name}', id='{id_attr}'")
                    break
        else:
            print("  No CAPTCHA - proceeding directly to submit")

        time.sleep(1)

        # Submit login
        print("  Submitting login...")
        page.locator("#wp-submit").click()
        page.wait_for_load_state("load", timeout=60000)
        time.sleep(5)

        login_result_path = f"{SCREENSHOT_DIR}/hover_fix_v6_login_result_{TIMESTAMP}.png"
        page.screenshot(path=login_result_path)

        url = page.url
        print(f"  URL after login: {url}")

        if "wp-login" in url:
            print("  LOGIN FAILED! Checking for CAPTCHA that appeared after submit...")
            # Maybe CAPTCHA appeared after clicking submit
            page.screenshot(path=f"{SCREENSHOT_DIR}/hover_fix_v6_login_failed_{TIMESTAMP}.png")
            error = page.locator("#login_error")
            if error.count() > 0:
                print(f"  Error: {error.first.inner_text()}")
            browser.close()
            return 1

        print("  LOGIN SUCCESS!")
        print(f"  Login result: {login_result_path}")

        # ===== STEP 3: NAVIGATE TO ADDITIONAL CSS =====
        print("\n[3] Navigating to Additional CSS customizer...")
        page.goto(WP_CSS_URL, wait_until="domcontentloaded", timeout=90000)
        time.sleep(15)

        page.screenshot(path=f"{SCREENSHOT_DIR}/hover_fix_v6_customizer_{TIMESTAMP}.png")
        print(f"  Customizer screenshot saved")

        try:
            page.wait_for_selector('.CodeMirror', state='visible', timeout=30000)
            print("  CodeMirror editor found!")
        except Exception:
            print("  WARNING: CodeMirror not found - will try textarea fallback")
        time.sleep(3)

        # ===== STEP 4: READ CURRENT CSS =====
        print("\n[4] Reading current Additional CSS...")
        current_css = page.evaluate("""
            () => {
                const cm = document.querySelector('.CodeMirror');
                if (cm && cm.CodeMirror) return cm.CodeMirror.getValue();
                const ta = document.querySelector('textarea[id*="css"]');
                if (ta) return ta.value;
                return null;
            }
        """)

        if current_css is None:
            print("  ERROR: Can't read current CSS!")
            browser.close()
            return 1

        print(f"  Current CSS: {len(current_css)} chars")

        # Check if fix already applied
        if FIX_MARKER in current_css:
            print(f"  Fix already present - skipping deployment (already done).")
            browser.close()
            return 0

        # ===== STEP 5: APPEND NEW CSS =====
        full_css = current_css + NEW_CSS
        print(f"\n[5] Appending {len(NEW_CSS)} chars -> {len(full_css)} total")

        result = page.evaluate("""
            (css) => {
                const cm = document.querySelector('.CodeMirror');
                if (cm && cm.CodeMirror) {
                    cm.CodeMirror.setValue(css);
                    cm.CodeMirror.refresh();
                    return 'codemirror_ok_' + cm.CodeMirror.getValue().length;
                }
                const ta = document.querySelector('textarea[id*="css"]');
                if (ta) {
                    ta.value = css;
                    ta.dispatchEvent(new Event('input', {bubbles: true}));
                    ta.dispatchEvent(new Event('change', {bubbles: true}));
                    return 'textarea_ok_' + ta.value.length;
                }
                return 'failed_no_editor';
            }
        """, full_css)
        print(f"  Set result: {result}")

        if not result or "ok" not in result:
            print("  ERROR: Failed to set CSS!")
            browser.close()
            return 1

        time.sleep(2)

        # ===== STEP 6: PUBLISH =====
        print("\n[6] Publishing...")
        time.sleep(3)

        published = False
        btn = page.locator("#save")
        if btn.count() > 0 and btn.first.is_visible():
            btn.first.click()
            published = True
        else:
            pub = page.locator("button:has-text('Publish')")
            if pub.count() > 0:
                pub.first.click()
                published = True

        if not published:
            print("  WARNING: No publish button found - trying Ctrl+S")
            page.keyboard.press("Control+s")

        time.sleep(10)

        pub_path = f"{SCREENSHOT_DIR}/hover_fix_v6_published_{TIMESTAMP}.png"
        page.screenshot(path=pub_path)
        status = page.evaluate("""
            () => {
                const b = document.querySelector('#save');
                return b ? b.textContent.trim() : 'btn not found';
            }
        """)
        print(f"  Publish status button: '{status}'")
        print(f"  Published screenshot: {pub_path}")

        # ===== STEP 7: VERIFY =====
        print("\n[7] Verifying pages...")
        vp = context.new_page()

        pages_to_verify = [
            ("https://purebrain.ai/category/for-teams/", "cat_for_teams", True),
            ("https://purebrain.ai/category/for-individuals/", "cat_for_individuals", True),
            ("https://purebrain.ai/why-ai-memory-changes-everything/", "blog_post", False),
            ("https://purebrain.ai/", "homepage", False),
        ]

        for url, label, full_page in pages_to_verify:
            print(f"\n  [{label}] {url}")
            vp.goto(url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(4)
            vp.evaluate("() => location.reload(true)")
            time.sleep(5)

            vp_path = f"{SCREENSHOT_DIR}/hover_fix_v6_VERIFY_{label}_{TIMESTAMP}.png"
            vp.screenshot(path=vp_path, full_page=full_page)
            print(f"    Screenshot: {vp_path}")

            # Check #ball and #magic-cursor visibility
            ball_check = vp.evaluate("""
                function() {
                    var ball = document.querySelector('#ball');
                    var cursor = document.querySelector('#magic-cursor');
                    return {
                        ball_display: ball ? window.getComputedStyle(ball).display : 'not found',
                        cursor_display: cursor ? window.getComputedStyle(cursor).display : 'not found'
                    };
                }
            """)
            print(f"    Magic cursor hidden: ball={ball_check['ball_display']}, cursor={ball_check['cursor_display']}")

            if label.startswith("cat_"):
                link_check = vp.evaluate("""
                    function() {
                        var links = document.querySelectorAll('.post-item h3 a, article h3 a, article h2 a');
                        var result = [];
                        for (var i = 0; i < Math.min(links.length, 2); i++) {
                            var s = window.getComputedStyle(links[i]);
                            result.push({
                                text: links[i].textContent.trim().substring(0, 35),
                                color: s.color
                            });
                        }
                        return result;
                    }
                """)
                print(f"    Post title colors: {link_check}")

                bc_check = vp.evaluate("""
                    function() {
                        var links = document.querySelectorAll('.breadcrumb-trail a');
                        var result = [];
                        for (var i = 0; i < links.length; i++) {
                            var s = window.getComputedStyle(links[i]);
                            result.push({text: links[i].textContent.trim(), color: s.color});
                        }
                        return result;
                    }
                """)
                print(f"    Breadcrumb links: {bc_check}")

            if label == "blog_post":
                share_check = vp.evaluate("""
                    function() {
                        var links = document.querySelectorAll('.pt-social-share a');
                        var result = [];
                        for (var i = 0; i < links.length; i++) {
                            var s = window.getComputedStyle(links[i]);
                            result.push({color: s.color, bg: s.backgroundColor});
                        }
                        return result;
                    }
                """)
                print(f"    Share icons: {share_check}")

                cat_check = vp.evaluate("""
                    function() {
                        var links = document.querySelectorAll('[rel="category tag"]');
                        var result = [];
                        for (var i = 0; i < links.length; i++) {
                            var s = window.getComputedStyle(links[i]);
                            result.push({text: links[i].textContent.trim(), color: s.color});
                        }
                        return result;
                    }
                """)
                print(f"    Cat links: {cat_check}")

        vp.close()
        browser.close()

        print("\n" + "=" * 60)
        print("DONE - Category + Hover Fix deployed!")
        print("=" * 60)
        print(f"\nVerification screenshots:")
        for f in sorted(os.listdir(SCREENSHOT_DIR)):
            if "VERIFY" in f and TIMESTAMP in f:
                print(f"  {SCREENSHOT_DIR}/{f}")

        return 0


if __name__ == "__main__":
    sys.exit(main())
