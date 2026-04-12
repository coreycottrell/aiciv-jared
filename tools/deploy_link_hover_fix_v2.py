"""
Deploy broader link hover fix for category/archive pages.
Post titles were still turning orange despite earlier CSS.
This adds broader selectors + magic cursor class hide.

Date: 2026-02-18
"""
import time
import os
import re
from playwright.sync_api import sync_playwright

WP_CSS_URL = "https://purebrain.ai/wp-admin/customize.php?autofocus[section]=custom_css"
USERNAME = "Purebrain@puremarketing.ai"
PASSWORD = "NW2u!JLQ3!Bt$XD$7CWzz5Z@"

ADDITIONAL_CSS = """

/* === LINK HOVER FIX v2 - Feb 18, 2026 === */
/* Post title links WHITE on hover (broader selectors) */
body.category h2 a:hover, body.archive h2 a:hover,
body.category h3 a:hover, body.archive h3 a:hover,
body.category .post-title a:hover, body.archive .post-title a:hover,
body.category .entry-title a:hover, body.archive .entry-title a:hover,
body.category .post-item a:hover, body.archive .post-item a:hover,
body.search h2 a:hover, body.search h3 a:hover,
body.tag h2 a:hover, body.tag h3 a:hover {
    color: #ffffff !important;
}

/* Magic cursor hidden (class + ID + wildcard) */
.magic-cursor, #magic-cursor, [class*="magic-cursor"] {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
}
/* === END LINK HOVER FIX v2 === */"""


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=1,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = ctx.new_page()

        # LOGIN
        print("[1] Logging in...")
        page.goto("https://purebrain.ai/wp-login.php", wait_until="domcontentloaded", timeout=60000)
        time.sleep(5)

        for attempt in range(3):
            if page.locator("#user_login").is_visible():
                print(f"  Login form visible on attempt {attempt+1}")
                break
            try:
                sso = page.locator("text=Log in with username and password")
                if sso.is_visible(timeout=3000):
                    sso.click()
                    print("  Clicked SSO bypass")
                    time.sleep(4)
            except:
                pass
            time.sleep(3)

        page.wait_for_selector("#user_login", state="visible", timeout=45000)
        page.fill("#user_login", USERNAME)
        page.fill("#user_pass", PASSWORD)
        time.sleep(1)
        page.locator("#wp-submit").click()
        page.wait_for_load_state("load", timeout=60000)
        time.sleep(5)

        if "wp-login" in page.url:
            print("  LOGIN FAILED!")
            browser.close()
            return 1
        print("  LOGIN SUCCESS!")

        # CUSTOMIZER
        print("\n[2] Opening Customizer...")
        page.goto(WP_CSS_URL, wait_until="domcontentloaded", timeout=120000)
        time.sleep(25)

        for attempt in range(8):
            found = page.evaluate("() => !!document.querySelector('.CodeMirror')")
            if found:
                print(f"  CodeMirror found on attempt {attempt+1}")
                break
            time.sleep(5)
        else:
            print("  ERROR: CodeMirror not found!")
            browser.close()
            return 1

        time.sleep(3)
        current_css = page.evaluate("""() => {
            const cm = document.querySelector('.CodeMirror');
            return cm && cm.CodeMirror ? cm.CodeMirror.getValue() : null;
        }""")

        if current_css is None:
            print("  ERROR: Cannot read CSS!")
            browser.close()
            return 1

        print(f"  Current CSS: {len(current_css)} chars")

        if "LINK HOVER FIX v2" in current_css:
            print("  Already deployed! Nothing to do.")
            browser.close()
            return 0

        # Strip old v2 if partial
        current_css = re.sub(
            r'/\* === LINK HOVER FIX v2.*?/\* === END LINK HOVER FIX v2 === \*/',
            '', current_css, flags=re.DOTALL
        ).rstrip()

        new_css = current_css + ADDITIONAL_CSS
        print(f"  New CSS: {len(new_css)} chars")

        result = page.evaluate("""(css) => {
            try {
                const cm = document.querySelector('.CodeMirror');
                if (cm && cm.CodeMirror) {
                    cm.CodeMirror.setValue(css);
                    cm.CodeMirror.refresh();
                    return 'ok_' + cm.CodeMirror.getValue().length;
                }
                return 'no_cm';
            } catch(e) {
                return 'err_' + e.message;
            }
        }""", new_css)
        print(f"  Set result: {result}")

        if not result.startswith("ok"):
            print("  FAILED to set CSS!")
            browser.close()
            return 1

        time.sleep(3)

        # PUBLISH
        print("\n[3] Publishing...")
        btn = page.locator("#save")
        if btn.count() > 0:
            try:
                btn.first.wait_for(state="visible", timeout=10000)
                btn.first.click()
                print("  Clicked #save")
            except:
                page.locator("button:has-text('Publish')").first.click()
                print("  Clicked Publish")
        else:
            page.locator("button:has-text('Publish')").first.click()
            print("  Clicked Publish")

        time.sleep(12)
        browser.close()

        # VERIFY
        print("\n[4] Verifying...")
        import requests
        r = requests.get("https://purebrain.ai/category/for-teams/", timeout=30)
        has_fix = "LINK HOVER FIX v2" in r.text
        print(f"  LINK HOVER FIX v2: {'PASS' if has_fix else 'FAIL'}")

        r2 = requests.get("https://purebrain.ai/category/for-individuals/", timeout=30)
        has_fix2 = "LINK HOVER FIX v2" in r2.text
        print(f"  For Individuals: {'PASS' if has_fix2 else 'FAIL'}")

        all_pass = has_fix and has_fix2
        print(f"\n=== {'ALL PASS' if all_pass else 'SOME FAILURES'} ===")
        return 0 if all_pass else 1


if __name__ == "__main__":
    exit(main())
