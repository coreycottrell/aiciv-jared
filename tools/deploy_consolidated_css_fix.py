"""
Consolidated CSS deployment for purebrain.ai blog/category fixes.
Combines ALL three CSS blocks that agents tried to deploy separately.
Prevents race condition by doing ONE atomic deployment.

Date: 2026-02-18
"""
import time
import os
from playwright.sync_api import sync_playwright

SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/tools/screenshots/consolidated-css-2026-02-18"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

WP_ADMIN_URL = "https://purebrain.ai/wp-admin"
WP_CSS_URL = "https://purebrain.ai/wp-admin/customize.php?autofocus[section]=custom_css"
USERNAME = "Purebrain@puremarketing.ai"
PASSWORD = "NW2u!JLQ3!Bt$XD$7CWzz5Z@"

# ============================================================
# ALL THREE CSS BLOCKS COMBINED
# ============================================================

BLOCK_1_HOVER_FIXES = """

/* ========== BLOG POST HOVER FIXES - Feb 18, 2026 ========== */
/* Fix 1: pt-social-share icons - WHITE on hover (not orange) */
/* Fix 2: Category tag - WHITE text on hover (no orange background) */
/* Fix 3: Newsletter subscribe link - WHITE border on hover */

/* FIX 1: pt-social-share social icons hover - white background with blue icon */
body.single-post .pt-social-share a:hover,
.pt-social-share a:hover {
    background: #ffffff !important;
    color: #2a93c1 !important;
    border-color: #ffffff !important;
    box-shadow: 0 4px 12px rgba(255, 255, 255, 0.3) !important;
    transform: scale(1.1) !important;
}

body.single-post .pt-social-share a:hover svg,
body.single-post .pt-social-share a:hover i,
.pt-social-share a:hover svg,
.pt-social-share a:hover i {
    color: #2a93c1 !important;
    fill: #2a93c1 !important;
}

/* FIX 2: Category tag links hover - white text, no orange background */
body.single-post a[rel="category tag"]:hover,
.post-single-meta a[rel="category tag"]:hover {
    color: #ffffff !important;
    background: transparent !important;
    background-color: transparent !important;
}

/* FIX 3: Newsletter / subscribe link - no orange background, white border on hover */
body.single-post .blog-cta-block a:hover,
body.single-post .blog-cta-block p a:hover {
    background: transparent !important;
    background-color: transparent !important;
    color: #2a93c1 !important;
    border: 1px solid #ffffff !important;
    border-radius: 3px !important;
    padding: 1px 4px !important;
    text-decoration: underline !important;
}

/* ========== END BLOG POST HOVER FIXES ========== */"""

BLOCK_2_NAV_LINKS = """

/* === BLOG NAV REAL LINKS FIX (Feb 18 2026) === */
body.single-post nav.navbar .container::after,
body.archive nav.navbar .container::after,
body.category nav.navbar .container::after,
body.search nav.navbar .container::after,
body.tag nav.navbar .container::after {
    content: none !important;
    display: none !important;
}
.blog-nav-links {
    display: flex !important;
    align-items: center !important;
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
    .blog-nav-links { font-size: 11px !important; }
    .blog-nav-links a { padding: 3px 6px !important; }
}
/* === END BLOG NAV REAL LINKS FIX === */"""

BLOCK_3_CATEGORY_UNIVERSAL = """

/* ============================================================ */
/* CATEGORY + HOVER FIX - Feb 18, 2026                         */
/* ============================================================ */

/* 1. HIDE MAGIC CURSOR ORANGE DOT */
#magic-cursor,
#ball {
    display: none !important;
}

/* 2. UNIVERSAL HOVER RULE - Any link with orange bg on hover = white text */
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

/* 3. BREADCRUMB TEXT - Readable and white on hover */
.breadcrumb-trail a:hover {
    color: #ffffff !important;
    background: transparent !important;
}
.breadcrumb-trail .trail-end span {
    color: #ffffff;
}

/* 4. CATEGORY TAGS - White on hover */
.cat-links a:hover,
[rel="category tag"]:hover,
.tags-links a:hover {
    color: #ffffff !important;
}

/* 5. Related reading links - white on hover */
.related-reading a:hover,
.related-post-title:hover,
.post-navigation a:hover {
    color: #ffffff !important;
}

/* 6. SHARE ICONS - Ensure white icons remain white */
.pt-social-share a svg,
.pt-social-share a svg path {
    fill: #ffffff !important;
    color: #ffffff !important;
}

/* ============================================================ */
/* END CATEGORY + HOVER FIX                                     */
/* ============================================================ */"""

ALL_CSS_BLOCKS = BLOCK_1_HOVER_FIXES + BLOCK_2_NAV_LINKS + BLOCK_3_CATEGORY_UNIVERSAL

def safe_screenshot(page, path, timeout=15000):
    try:
        page.screenshot(path=path, timeout=timeout)
        print(f"  Screenshot: {path}")
    except:
        print(f"  Screenshot skipped (timeout)")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=1,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = ctx.new_page()

        # LOGIN - go directly to wp-login.php to avoid SSO redirect issues
        print("[1] Logging in...")
        page.goto("https://purebrain.ai/wp-login.php", wait_until="domcontentloaded", timeout=60000)
        time.sleep(5)

        # Handle GoDaddy SSO bypass if present
        for attempt in range(3):
            login_visible = page.locator("#user_login").is_visible()
            if login_visible:
                print(f"  Login form visible on attempt {attempt+1}")
                break
            # Try clicking SSO bypass link
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

        print(f"  URL: {page.url}")
        if "wp-login" in page.url:
            print("  LOGIN FAILED!")
            browser.close()
            return 1
        print("  LOGIN SUCCESS!")

        # CUSTOMIZER
        print("\n[2] Opening Customizer Additional CSS...")
        page.goto(WP_CSS_URL, wait_until="domcontentloaded", timeout=120000)
        time.sleep(25)

        # Wait for CodeMirror
        for attempt in range(8):
            found = page.evaluate("() => !!document.querySelector('.CodeMirror')")
            if found:
                print(f"  CodeMirror found on attempt {attempt+1}")
                break
            print(f"  Attempt {attempt+1}: waiting...")
            time.sleep(5)
        else:
            print("  ERROR: CodeMirror never appeared!")
            browser.close()
            return 1

        time.sleep(3)

        # READ CURRENT CSS
        current_css = page.evaluate("""
            () => {
                const cm = document.querySelector('.CodeMirror');
                if (cm && cm.CodeMirror) return cm.CodeMirror.getValue();
                return null;
            }
        """)

        if current_css is None:
            print("  ERROR: Cannot read CSS!")
            browser.close()
            return 1

        print(f"  Current CSS: {len(current_css)} chars")

        # CHECK WHAT'S ALREADY PRESENT
        has_hover = "BLOG POST HOVER FIXES" in current_css
        has_nav = "BLOG NAV REAL LINKS FIX" in current_css
        has_category = "CATEGORY + HOVER FIX" in current_css
        print(f"  Has HOVER FIXES:    {has_hover}")
        print(f"  Has NAV LINKS:      {has_nav}")
        print(f"  Has CATEGORY+HOVER: {has_category}")

        if has_hover and has_nav and has_category:
            print("  ALL blocks already present! Nothing to do.")
            browser.close()
            return 0

        # STRIP EXISTING PARTIAL BLOCKS (to avoid duplicates)
        import re
        # Remove block 1 if present
        current_css = re.sub(
            r'/\* =+ BLOG POST HOVER FIXES.*?/\* =+ END BLOG POST HOVER FIXES =+ \*/',
            '', current_css, flags=re.DOTALL)
        # Remove block 2 if present
        current_css = re.sub(
            r'/\* === BLOG NAV REAL LINKS FIX.*?/\* === END BLOG NAV REAL LINKS FIX === \*/',
            '', current_css, flags=re.DOTALL)
        # Remove block 3 if present
        current_css = re.sub(
            r'/\* =+ CATEGORY \+ HOVER FIX.*?/\* =+ END CATEGORY \+ HOVER FIX =+ \*/',
            '', current_css, flags=re.DOTALL)

        # Clean up trailing whitespace
        current_css = current_css.rstrip()

        print(f"  Base CSS after stripping: {len(current_css)} chars")

        # APPEND ALL BLOCKS
        new_css = current_css + ALL_CSS_BLOCKS
        print(f"  New CSS total: {len(new_css)} chars")

        # SET CSS
        set_result = page.evaluate("""
            (css) => {
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
            }
        """, new_css)
        print(f"  Set result: {set_result}")

        if not set_result.startswith("ok"):
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

        btn_text = page.evaluate("""
            () => {
                const b = document.querySelector('#save');
                return b ? b.textContent.trim() : 'no-btn';
            }
        """)
        print(f"  Button text: '{btn_text}'")

        safe_screenshot(page, f"{SCREENSHOT_DIR}/published.png")
        browser.close()

        # VERIFY
        print("\n[4] Verifying live pages...")
        import requests as req

        # Blog post
        r = req.get("https://purebrain.ai/why-ai-memory-changes-everything/", timeout=30)
        html = r.text
        v_hover = "BLOG POST HOVER FIXES" in html
        v_nav = "BLOG NAV REAL LINKS FIX" in html
        v_cat = "CATEGORY + HOVER FIX" in html
        v_inject = "blog-nav-inject" in html

        print(f"  Blog post:")
        print(f"    HOVER FIXES: {'PASS' if v_hover else 'FAIL'}")
        print(f"    NAV LINKS:   {'PASS' if v_nav else 'FAIL'}")
        print(f"    CATEGORY:    {'PASS' if v_cat else 'FAIL'}")
        print(f"    JS inject:   {'PASS' if v_inject else 'FAIL'}")

        # Category page
        r2 = req.get("https://purebrain.ai/category/for-teams/", timeout=30)
        html2 = r2.text
        v2_hover = "BLOG POST HOVER FIXES" in html2
        v2_nav = "BLOG NAV REAL LINKS FIX" in html2
        v2_cat = "CATEGORY + HOVER FIX" in html2

        print(f"  Category page:")
        print(f"    HOVER FIXES: {'PASS' if v2_hover else 'FAIL'}")
        print(f"    NAV LINKS:   {'PASS' if v2_nav else 'FAIL'}")
        print(f"    CATEGORY:    {'PASS' if v2_cat else 'FAIL'}")

        all_pass = all([v_hover, v_nav, v_cat, v_inject, v2_hover, v2_nav, v2_cat])
        print(f"\n=== {'ALL PASS' if all_pass else 'SOME FAILURES'} ===")

        return 0 if all_pass else 1


if __name__ == "__main__":
    exit(main())
