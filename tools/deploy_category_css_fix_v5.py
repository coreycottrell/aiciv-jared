#!/usr/bin/env python3
"""
Deploy Category Page CSS Fix - v5
Enhanced CAPTCHA extraction at higher resolution.
Saves CAPTCHA image cropped and at 2x scale.
"""

import sys
import time
import os
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
CAPTCHA_ANSWER_FILE = "/tmp/catfix_captcha_answer.txt"

CATEGORY_CSS_FIX = """

/* === CATEGORY PAGE FIX (Feb 18) === */
body.category,
body.archive {
  color: #ffffff !important;
  background: #0a0a0a !important;
}
body.category a,
body.archive a {
  color: #2a93c1 !important;
}
body.category a:hover,
body.archive a:hover {
  color: #f1420b !important;
}
body.category h1,
body.category h2,
body.category .page-title,
body.archive h1,
body.archive h2,
body.archive .page-title {
  color: #ffffff !important;
}
body.category .nav-links a,
body.archive .nav-links a {
  color: #2a93c1 !important;
}
/* === END CATEGORY PAGE FIX === */"""


def main():
    if not PASSWORD:
        print("ERROR: PUREBRAIN_WP_PASSWORD not found in .env")
        return 1

    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    if os.path.exists(CAPTCHA_ANSWER_FILE):
        os.remove(CAPTCHA_ANSWER_FILE)

    print("=" * 60)
    print(f"PureBrain.ai Category CSS Fix v5 - {datetime.now()}")
    print("=" * 60)

    with sync_playwright() as p:
        # Use device_scale_factor=2 for sharper CAPTCHA rendering
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=2,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        )
        page = context.new_page()

        # Load login page
        print("\n[1] Loading login page...")
        page.goto(WP_ADMIN_URL, wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)

        # Click "Log in with username and password"
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

        # Get CAPTCHA image info via JavaScript
        captcha_info = page.evaluate("""
            () => {
                // Find the CAPTCHA image
                const imgs = document.querySelectorAll('form img, #loginform img');
                let captchaImg = null;
                for (const img of imgs) {
                    const src = img.getAttribute('src') || '';
                    // It's usually the only non-WordPress logo image
                    if (!src.includes('w-logo') && !src.includes('wordpress-logo')) {
                        captchaImg = img;
                        break;
                    }
                }

                // Also try to find by position (image between password and text field)
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
                        width: rect.width,
                        height: rect.height,
                        x: rect.x,
                        y: rect.y,
                        naturalWidth: captchaImg.naturalWidth,
                        naturalHeight: captchaImg.naturalHeight
                    };
                }
                return null;
            }
        """)
        print(f"  CAPTCHA image info: {captcha_info}")

        # Save full page screenshot
        full_path = f"{SCREENSHOT_DIR}/catfix5_full_{TIMESTAMP}.png"
        page.screenshot(path=full_path)
        print(f"  Full page: {full_path}")

        # Try to save just the CAPTCHA image element
        captcha_imgs = page.locator("form img")
        for i in range(captcha_imgs.count()):
            img = captcha_imgs.nth(i)
            src = img.get_attribute("src") or ""
            if "w-logo" not in src and "wordpress-logo" not in src:
                captcha_path = f"{SCREENSHOT_DIR}/catfix5_captcha_only_{TIMESTAMP}.png"
                img.screenshot(path=captcha_path)
                print(f"  CAPTCHA only: {captcha_path}")
                break

        # Also try to get CAPTCHA source URL and download at full res
        if captcha_info and captcha_info.get('src'):
            src = captcha_info['src']
            if not src.startswith('http'):
                src = f"https://purebrain.ai{src}"
            print(f"  CAPTCHA source URL: {src}")

            # Try to download the image directly
            import requests
            try:
                r = requests.get(src, timeout=10)
                if r.status_code == 200:
                    raw_path = f"{SCREENSHOT_DIR}/catfix5_captcha_raw_{TIMESTAMP}.png"
                    with open(raw_path, 'wb') as f:
                        f.write(r.content)
                    print(f"  CAPTCHA raw download: {raw_path} ({len(r.content)} bytes)")
            except Exception as e:
                print(f"  Could not download raw: {e}")

        print(f"\n  Waiting for CAPTCHA answer in: {CAPTCHA_ANSWER_FILE}")
        print("  Timeout: 180s")

        # Wait for answer
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
            print("  TIMEOUT!")
            browser.close()
            return 1

        # Fill CAPTCHA
        print(f"\n[2] Filling CAPTCHA: '{captcha_answer}'")
        all_text = page.locator("input[type='text']")
        for i in range(all_text.count()):
            inp = all_text.nth(i)
            name = inp.get_attribute("name") or ""
            id_attr = inp.get_attribute("id") or ""
            if id_attr != "user_login" and name != "log":
                inp.fill(captcha_answer)
                print(f"  Filled: name='{name}', id='{id_attr}'")
                break

        time.sleep(1)

        # Submit
        print("  Submitting login...")
        page.locator("#wp-submit").click()
        page.wait_for_load_state("load", timeout=60000)
        time.sleep(5)

        result_path = f"{SCREENSHOT_DIR}/catfix5_login_result_{TIMESTAMP}.png"
        page.screenshot(path=result_path)
        print(f"  Result: {result_path}")

        url = page.url
        print(f"  URL: {url}")

        if "wp-login" in url:
            print("  LOGIN FAILED!")
            error = page.locator("#login_error")
            if error.count() > 0:
                print(f"  Error: {error.first.inner_text()}")
            browser.close()
            return 1

        print("  LOGIN SUCCESS!")

        # Navigate to Additional CSS
        print("\n[3] Navigating to Additional CSS...")
        page.goto(WP_CSS_URL, wait_until="domcontentloaded", timeout=90000)
        time.sleep(15)

        page.screenshot(path=f"{SCREENSHOT_DIR}/catfix5_customizer_{TIMESTAMP}.png")

        try:
            page.wait_for_selector('.CodeMirror', state='visible', timeout=30000)
            print("  CodeMirror found!")
        except:
            print("  CodeMirror not found")
        time.sleep(3)

        # Get current CSS
        current_css = page.evaluate("""
            () => {
                const cm = document.querySelector('.CodeMirror');
                if (cm && cm.CodeMirror) return cm.CodeMirror.getValue();
                return null;
            }
        """)

        if current_css is None:
            print("  ERROR: Can't read CSS!")
            browser.close()
            return 1

        print(f"  Current CSS: {len(current_css)} chars")

        if "CATEGORY PAGE FIX" in current_css:
            print("  Already present! Skipping.")
        else:
            full_css = current_css + CATEGORY_CSS_FIX
            print(f"  Appending {len(CATEGORY_CSS_FIX)} chars -> {len(full_css)} total")

            result = page.evaluate("(css) => { const cm = document.querySelector('.CodeMirror'); if (cm && cm.CodeMirror) { cm.CodeMirror.setValue(css); cm.CodeMirror.refresh(); return 'ok_' + cm.CodeMirror.getValue().length; } return 'fail'; }", full_css)
            print(f"  Set: {result}")

            if not result.startswith("ok"):
                browser.close()
                return 1

            time.sleep(2)

            # Publish
            print("\n[4] Publishing...")
            time.sleep(3)
            btn = page.locator("#save")
            if btn.count() > 0 and btn.first.is_visible():
                btn.first.click()
            else:
                page.locator("button:has-text('Publish')").first.click()
            time.sleep(8)

            page.screenshot(path=f"{SCREENSHOT_DIR}/catfix5_published_{TIMESTAMP}.png")
            status = page.evaluate("() => { const b = document.querySelector('#save'); return b ? b.textContent.trim() : 'no btn'; }")
            print(f"  Status: {status}")

        # Verify
        print("\n[5] Verification...")
        vp = context.new_page()

        for url, label in [
            ("https://purebrain.ai/category/for-teams/", "category"),
            ("https://purebrain.ai/", "homepage"),
            ("https://purebrain.ai/blog/", "blog"),
        ]:
            print(f"  {label}: {url}")
            vp.goto(url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(5)
            vp.evaluate("() => location.reload(true)")
            time.sleep(5)
            path = f"{SCREENSHOT_DIR}/catfix5_FINAL_{label}_{TIMESTAMP}.png"
            vp.screenshot(path=path, full_page=(label == "category"))
            print(f"    Screenshot: {path}")

            if label == "category":
                s = vp.evaluate("""
                    () => {
                        const b = document.body;
                        return {
                            color: getComputedStyle(b).color,
                            bg: getComputedStyle(b).backgroundColor,
                            classes: b.className.substring(0, 100)
                        };
                    }
                """)
                print(f"    Styles: {s}")

        vp.close()
        browser.close()
        print("\nDONE!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
