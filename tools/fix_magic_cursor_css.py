"""
URGENT FIX: The CSS rule [class*="magic-cursor"] matches the BODY element
and hides the ENTIRE PAGE with display:none, visibility:hidden, opacity:0.

This replaces the wildcard selector with targeted div/span selectors.

Date: 2026-02-18
"""
import time
import re
from playwright.sync_api import sync_playwright

WP_LOGIN = "https://purebrain.ai/wp-login.php"
WP_CSS_URL = "https://purebrain.ai/wp-admin/customize.php?autofocus[section]=custom_css"
USERNAME = "Purebrain@puremarketing.ai"
PASSWORD = 'NW2u!JLQ3!Bt$XD$7CWzz5Z@'


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=2,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = ctx.new_page()

        # LOGIN
        print("[1] Logging in...")
        page.goto(WP_LOGIN, wait_until="domcontentloaded", timeout=60000)
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

        # FIX: Replace the overly-broad magic-cursor selector
        # Old (BROKEN - [class*="magic-cursor"] matches body element):
        # New (SAFE - only matches specific div/span elements):

        # Try exact string match first
        old_pattern = '.magic-cursor, #magic-cursor, [class*="magic-cursor"]'
        new_pattern = 'div.magic-cursor, div#magic-cursor, span.magic-cursor'

        if old_pattern in current_css:
            new_css = current_css.replace(old_pattern, new_pattern)
            print(f"  Found and replaced magic-cursor selector (exact match)")
        else:
            # Try regex
            regex = r'\.magic-cursor,\s*#magic-cursor,\s*\[class\*=["\']magic-cursor["\']\]'
            match = re.search(regex, current_css)
            if match:
                new_css = current_css[:match.start()] + new_pattern + current_css[match.end():]
                print(f"  Found and replaced magic-cursor selector (regex match)")
            else:
                # Show what's around "magic-cursor" in the CSS
                idx = current_css.find("magic-cursor")
                if idx >= 0:
                    print(f"  Found 'magic-cursor' at pos {idx}")
                    print(f"  Context: ...{current_css[max(0,idx-80):idx+120]}...")
                else:
                    print("  ERROR: 'magic-cursor' not found in CSS at all!")
                browser.close()
                return 1

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

        # Check pay-test
        r = requests.get("https://purebrain.ai/pay-test/?v=" + str(int(time.time())), timeout=30)
        has_old = '[class*="magic-cursor"]' in r.text
        has_new = 'div.magic-cursor' in r.text
        print(f"  Old wildcard selector gone: {not has_old}")
        print(f"  New safe selector present: {has_new}")

        # Check homepage too
        r2 = requests.get("https://purebrain.ai/?v=" + str(int(time.time())), timeout=30)
        has_old2 = '[class*="magic-cursor"]' in r2.text
        print(f"  Homepage old selector gone: {not has_old2}")

        if has_old:
            print("  WARNING: Old selector still present (may be cached)")

        all_pass = not has_old and has_new
        print(f"\n=== {'ALL PASS' if all_pass else 'CHECK CACHE'} ===")
        return 0 if all_pass else 1


if __name__ == "__main__":
    exit(main())
