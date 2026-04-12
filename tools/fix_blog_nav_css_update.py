#!/usr/bin/env python3
"""
Update Additional CSS to:
1. Remove old ::after pseudo-element (replace with content: none)
2. Add styles for the new real .blog-nav-links div

Uses Playwright with CAPTCHA support.
"""

import sys
import os
import time
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
CAPTCHA_ANSWER_FILE = "/tmp/blognav_captcha_answer.txt"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

NAV_CSS_UPDATE = """

/* === BLOG NAV REAL LINKS FIX (Feb 18 2026) === */
/* Override old CSS pseudo-element - now we use real <a> links injected by JS */
body.single-post nav.navbar .container::after,
body.archive nav.navbar .container::after,
body.category nav.navbar .container::after,
body.search nav.navbar .container::after,
body.tag nav.navbar .container::after {
    content: none !important;
    display: none !important;
}

/* Style the real injected nav links (.blog-nav-links div injected via JS) */
.blog-nav-links {
    display: flex !important;
    align-items: center !important;
    gap: 0 !important;
    margin-left: auto !important;
    font-size: 14px !important;
    font-weight: 400 !important;
    letter-spacing: 0.5px !important;
}

.blog-nav-links a {
    color: rgba(255,255,255,0.7) !important;
    text-decoration: none !important;
    padding: 4px 10px !important;
    transition: color 0.2s ease !important;
    cursor: pointer !important;
}

.blog-nav-links a:hover {
    color: #f1420b !important;
    text-decoration: none !important;
}

.blog-nav-sep {
    color: rgba(255,255,255,0.3) !important;
    font-size: 12px !important;
    user-select: none !important;
}

@media (max-width: 600px) {
    .blog-nav-links {
        font-size: 11px !important;
    }
    .blog-nav-links a {
        padding: 3px 6px !important;
    }
}
/* === END BLOG NAV REAL LINKS FIX === */"""


def main():
    if not PASSWORD:
        print("ERROR: PUREBRAIN_WP_PASSWORD not set")
        return 1

    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    if os.path.exists(CAPTCHA_ANSWER_FILE):
        os.remove(CAPTCHA_ANSWER_FILE)

    print("=" * 60)
    print(f"Blog Nav CSS Update - {TIMESTAMP}")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=2,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        )
        page = context.new_page()

        print("\n[1] Loading login page...")
        page.goto(WP_ADMIN_URL, wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)

        try:
            login_link = page.locator("text=Log in with username and password")
            if login_link.is_visible(timeout=5000):
                login_link.click()
                time.sleep(2)
        except Exception:
            pass

        page.wait_for_selector('#user_login', state='visible', timeout=30000)
        page.locator("#user_login").fill(USERNAME)
        page.locator("#user_pass").fill(PASSWORD)
        time.sleep(1)

        # Screenshot for CAPTCHA
        full_path = f"{SCREENSHOT_DIR}/blognav_css_login_{TIMESTAMP}.png"
        page.screenshot(path=full_path)
        print(f"  Login screenshot: {full_path}")

        # Get CAPTCHA info
        captcha_info = page.evaluate("""
            () => {
                const imgs = document.querySelectorAll('form img, #loginform img');
                for (const img of imgs) {
                    const src = img.getAttribute('src') || '';
                    if (!src.includes('w-logo') && !src.includes('wordpress-logo')) {
                        const rect = img.getBoundingClientRect();
                        return { src, x: rect.x, y: rect.y, w: rect.width, h: rect.height };
                    }
                }
                return null;
            }
        """)
        print(f"  CAPTCHA info: {captcha_info}")

        # Save CAPTCHA element screenshot
        captcha_imgs = page.locator("form img")
        for i in range(captcha_imgs.count()):
            img = captcha_imgs.nth(i)
            src = img.get_attribute("src") or ""
            if "w-logo" not in src and "wordpress-logo" not in src:
                cap_path = f"{SCREENSHOT_DIR}/blognav_css_captcha_{TIMESTAMP}.png"
                img.screenshot(path=cap_path)
                print(f"  CAPTCHA element: {cap_path}")
                break

        # Download raw CAPTCHA
        if captcha_info and captcha_info.get('src'):
            src = captcha_info['src']
            if not src.startswith('http'):
                src = f"https://purebrain.ai{src}"
            try:
                r = requests.get(src, timeout=10)
                if r.status_code == 200:
                    raw_path = f"{SCREENSHOT_DIR}/blognav_css_captcha_raw_{TIMESTAMP}.png"
                    with open(raw_path, 'wb') as f:
                        f.write(r.content)
                    print(f"  CAPTCHA raw: {raw_path}")
            except Exception as e:
                print(f"  CAPTCHA download error: {e}")

        print(f"\n  Waiting for CAPTCHA answer in: {CAPTCHA_ANSWER_FILE}")
        print("  Timeout: 180s")

        start = time.time()
        captcha_answer = None
        while time.time() - start < 180:
            if os.path.exists(CAPTCHA_ANSWER_FILE):
                with open(CAPTCHA_ANSWER_FILE, 'r') as f:
                    captcha_answer = f.read().strip()
                if captcha_answer:
                    os.remove(CAPTCHA_ANSWER_FILE)
                    break
            time.sleep(1)

        if not captcha_answer:
            print("  CAPTCHA TIMEOUT")
            browser.close()
            return 1

        print(f"  Got CAPTCHA: '{captcha_answer}'")

        # Fill CAPTCHA
        all_text = page.locator("input[type='text']")
        for i in range(all_text.count()):
            inp = all_text.nth(i)
            id_attr = inp.get_attribute("id") or ""
            name_attr = inp.get_attribute("name") or ""
            if id_attr != "user_login" and name_attr != "log":
                inp.fill(captcha_answer)
                print(f"  Filled CAPTCHA: id={id_attr}")
                break

        time.sleep(1)
        page.locator("#wp-submit").click()
        page.wait_for_load_state("load", timeout=60000)
        time.sleep(5)

        result_path = f"{SCREENSHOT_DIR}/blognav_css_login_result_{TIMESTAMP}.png"
        page.screenshot(path=result_path)

        if "wp-login" in page.url:
            print("  LOGIN FAILED")
            browser.close()
            return 1

        print("  LOGIN SUCCESS")

        print("\n[2] Loading Customizer Additional CSS...")
        page.goto(WP_CSS_URL, wait_until="domcontentloaded", timeout=90000)
        time.sleep(15)

        page.screenshot(path=f"{SCREENSHOT_DIR}/blognav_css_customizer_{TIMESTAMP}.png")

        try:
            page.wait_for_selector('.CodeMirror', state='visible', timeout=30000)
            print("  CodeMirror found")
        except Exception:
            print("  WARNING: CodeMirror not found")

        time.sleep(3)

        current_css = page.evaluate("""
            () => {
                const cm = document.querySelector('.CodeMirror');
                if (cm && cm.CodeMirror) return cm.CodeMirror.getValue();
                return null;
            }
        """)

        if current_css is None:
            print("  ERROR: Cannot read CodeMirror CSS")
            browser.close()
            return 1

        print(f"  Current CSS: {len(current_css)} chars")

        if 'BLOG NAV REAL LINKS FIX' in current_css:
            print("  Already updated - no changes needed")
            browser.close()
            return 0

        new_css = current_css + NAV_CSS_UPDATE
        print(f"  New CSS: {len(new_css)} chars (added {len(NAV_CSS_UPDATE)})")

        result = page.evaluate(
            "(css) => { const cm = document.querySelector('.CodeMirror'); if (cm && cm.CodeMirror) { cm.CodeMirror.setValue(css); cm.CodeMirror.refresh(); return 'ok_' + cm.CodeMirror.getValue().length; } return 'fail'; }",
            new_css
        )
        print(f"  Set result: {result}")

        if not result.startswith("ok"):
            print("  ERROR: Failed to set CSS")
            browser.close()
            return 1

        time.sleep(2)

        print("\n[3] Publishing...")
        time.sleep(3)
        btn = page.locator("#save")
        if btn.count() > 0 and btn.first.is_visible():
            btn.first.click()
        else:
            page.locator("button:has-text('Publish')").first.click()

        time.sleep(10)
        page.screenshot(path=f"{SCREENSHOT_DIR}/blognav_css_published_{TIMESTAMP}.png")
        status = page.evaluate("() => { const b = document.querySelector('#save'); return b ? b.textContent.trim() : 'no btn'; }")
        print(f"  Publish status: {status}")

        browser.close()
        print("\nCSS UPDATE COMPLETE")
        return 0


if __name__ == "__main__":
    sys.exit(main())
