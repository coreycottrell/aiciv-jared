#!/usr/bin/env python3
"""
Deploy blog post featured image padding fix to jareddsanborn.com.

jareddsanborn.com uses Divi theme. The featured image structure is:
  article.et_pb_post > .et_post_meta_wrapper > img (bare img, no wrapper div)

CSS is deployed via WordPress Customizer Additional CSS.

Author: full-stack-developer agent
Date: 2026-02-20
"""

import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

AETHER_ROOT = Path("/home/jared/projects/AI-CIV/aether")
ENV_FILE = AETHER_ROOT / ".env"
load_dotenv(ENV_FILE)

WP_USER = "jared"
WP_PASSWORD = os.environ.get("WORDPRESS_APP_PASSWORD", "").strip()

# jareddsanborn.com uses Divi theme - different HTML structure than purebrain.ai
# Structure: article.et_pb_post > .et_post_meta_wrapper > img.wp-post-image (NO wrapper div)
# Container: #main-content > .container (Divi's standard container)
BLOG_PADDING_CSS = """
/* ================================================
   JAREDDSANBORN.COM - BLOG POST FEATURED IMAGE PADDING
   Adds breathing room to featured image on desktop.
   Divi theme structure: .et_post_meta_wrapper > img
   v1.0 - 2026-02-20
   ================================================ */

@media (min-width: 1025px) {
    /* Constrain the main content container width */
    body.single-post #main-content > .container {
        max-width: 1100px !important;
        padding-left: 60px !important;
        padding-right: 60px !important;
        box-sizing: border-box !important;
    }

    /* Constrain left content area */
    body.single-post #left-area {
        padding-left: 0 !important;
    }

    /* Featured image: constrain and center with breathing room */
    body.single-post article.et_pb_post .et_post_meta_wrapper img.wp-post-image,
    body.single-post article.et_pb_post .et_post_meta_wrapper > img,
    body.single-post .et_post_meta_wrapper img:not(.avatar) {
        max-width: 760px !important;
        width: 100% !important;
        height: auto !important;
        display: block !important;
        margin-left: auto !important;
        margin-right: auto !important;
        margin-bottom: 40px !important;
        border-radius: 16px !important;
        box-shadow: 0 8px 40px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(0, 0, 0, 0.08) !important;
    }

    /* Page header title area: cap width to match */
    body.single-post #page-container > header,
    body.single-post .page_meta_wrapper,
    body.single-post .et_post_meta_wrapper {
        max-width: 1100px !important;
        margin-left: auto !important;
        margin-right: auto !important;
        padding-left: 60px !important;
        padding-right: 60px !important;
        box-sizing: border-box !important;
    }
}

@media (min-width: 1400px) {
    body.single-post #main-content > .container {
        padding-left: 80px !important;
        padding-right: 80px !important;
    }
    body.single-post .et_post_meta_wrapper {
        padding-left: 80px !important;
        padding-right: 80px !important;
    }
}
"""

SCREENSHOT_PATH = str(AETHER_ROOT / "exports/screenshots/jared_blog_padding_deploy.png")
SCREENSHOT_VERIFY = str(AETHER_ROOT / "exports/screenshots/jared_blog_padding_live.png")


def deploy():
    from playwright.sync_api import sync_playwright

    print("=== jareddsanborn.com Blog Padding Fix Deployer ===")
    print(f"Target: https://jareddsanborn.com/wp-admin/customize.php")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=2,  # High-res for CAPTCHA if needed
        )
        page = context.new_page()

        # Step 1: Login
        print("\n[Step 1] Logging in to WP Admin...")
        page.goto("https://jareddsanborn.com/wp-login.php", wait_until="domcontentloaded", timeout=60000)
        time.sleep(2)

        page_text = page.inner_text("body")
        print(f"  Login page loaded. Has user_login: {'user_login' in page.content()}")

        # Check for CAPTCHA
        if 'captcha' in page_text.lower():
            page.screenshot(path=SCREENSHOT_PATH)
            print("  WARNING: CAPTCHA detected on login page. Cannot proceed automatically.")
            browser.close()
            return False

        try:
            page.locator("#user_login").wait_for(state="visible", timeout=15000)
        except Exception:
            page.screenshot(path=SCREENSHOT_PATH)
            print("  ERROR: Login form not visible.")
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
            page.screenshot(path=SCREENSHOT_PATH)
            page_text = page.inner_text("body")
            print(f"  ERROR: Login failed. Page: {page_text[:300]}")
            browser.close()
            return False

        print("  Login successful!")

        # Step 2: Go to Customizer > Additional CSS
        print("\n[Step 2] Opening Customizer Additional CSS...")
        customize_url = "https://jareddsanborn.com/wp-admin/customize.php?autofocus[section]=custom_css"
        page.goto(customize_url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(5)

        page.screenshot(path=SCREENSHOT_PATH)
        page_text = page.inner_text("body")
        print(f"  Customizer loaded. URL: {page.url}")

        # Step 3: Read existing CSS and append our fix
        print("\n[Step 3] Reading existing Additional CSS...")

        has_codemirror = page.evaluate("() => !!document.querySelector('.CodeMirror')")
        has_textarea = page.evaluate("() => !!document.querySelector('#customize-control-custom_css textarea')")
        print(f"  CodeMirror: {has_codemirror}, Textarea: {has_textarea}")

        if has_codemirror:
            existing_css = page.evaluate("""() => {
                const cm = document.querySelector('.CodeMirror');
                return cm ? cm.CodeMirror.getValue() : '';
            }""")
        elif has_textarea:
            existing_css = page.evaluate("""() => {
                const ta = document.querySelector('#customize-control-custom_css textarea');
                return ta ? ta.value : '';
            }""")
        else:
            page.screenshot(path=SCREENSHOT_PATH)
            print("  ERROR: No CSS editor found.")
            browser.close()
            return False

        print(f"  Existing CSS length: {len(existing_css)} chars")

        # Check if our CSS is already there
        if 'JAREDDSANBORN.COM - BLOG POST FEATURED IMAGE PADDING' in existing_css:
            print("  NOTE: Blog padding CSS already present. Replacing it...")
            # Remove old version
            import re
            existing_css = re.sub(
                r'/\* ={3,}\s*JAREDDSANBORN\.COM - BLOG POST FEATURED IMAGE PADDING.*?@media.*?\}[\s\n]*\}',
                '',
                existing_css,
                flags=re.DOTALL
            )
            print(f"  After removing old: {len(existing_css)} chars")

        new_css = existing_css.rstrip() + "\n\n" + BLOG_PADDING_CSS.strip()
        print(f"  New CSS length: {len(new_css)} chars")

        # Step 4: Set the new CSS
        print("\n[Step 4] Setting new CSS...")

        if has_codemirror:
            result = page.evaluate("""(css) => {
                try {
                    const cm = document.querySelector('.CodeMirror');
                    if (!cm) return 'no_cm';
                    cm.CodeMirror.setValue(css);
                    return 'set:' + cm.CodeMirror.getValue().length;
                } catch(e) {
                    return 'error: ' + e.message;
                }
            }""", new_css)
            print(f"  CodeMirror set result: {result}")
        else:
            result = page.evaluate("""(css) => {
                const ta = document.querySelector('#customize-control-custom_css textarea');
                if (!ta) return 'no_ta';
                const setter = Object.getOwnPropertyDescriptor(
                    window.HTMLTextAreaElement.prototype, 'value').set;
                setter.call(ta, css);
                ta.dispatchEvent(new Event('input', {bubbles: true}));
                ta.dispatchEvent(new Event('change', {bubbles: true}));
                return 'set:' + ta.value.length;
            }""", new_css)
            print(f"  Textarea set result: {result}")

        time.sleep(2)

        # Step 5: Publish
        print("\n[Step 5] Publishing Customizer changes...")
        publish_result = page.evaluate("""() => {
            // Try the standard Publish button
            const saveBtn = document.querySelector('#save') ||
                           document.querySelector('.save-publish-button') ||
                           document.querySelector('[data-action="save"]');
            if (saveBtn) {
                saveBtn.click();
                return 'clicked: ' + (saveBtn.textContent || saveBtn.value || 'btn').trim();
            }
            return 'no_button_found';
        }""")
        print(f"  Publish click: {publish_result}")

        try:
            page.wait_for_load_state("domcontentloaded", timeout=30000)
        except Exception:
            pass
        time.sleep(5)

        page.screenshot(path=SCREENSHOT_VERIFY)
        print(f"  Screenshot after publish: {SCREENSHOT_VERIFY}")

        # Check if saved
        page_text = page.inner_text("body")
        if "saved" in page_text.lower() or "published" in page_text.lower():
            print("  SUCCESS: Customizer saved!")
        else:
            print(f"  Status unclear. Checking...")
            # Verify by checking if CSS is in the page source
            current_css = page.evaluate("""() => {
                const cm = document.querySelector('.CodeMirror');
                return cm ? cm.CodeMirror.getValue().substring(0, 200) : 'N/A';
            }""")
            print(f"  Current CSS start: {current_css[:200]}")

        browser.close()
        return True


def verify():
    """Verify the CSS is live on jareddsanborn.com."""
    from playwright.sync_api import sync_playwright
    import json

    print("\n[Verification] Loading jareddsanborn.com blog post at 1440px...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        post_url = "https://jareddsanborn.com/the-difference-between-using-ai-and-having-an-ai-partner/"
        page.goto(post_url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(4)

        # Scroll to featured image
        page.evaluate("""() => {
            const img = document.querySelector('.et_post_meta_wrapper img, .wp-post-image');
            if (img) img.scrollIntoView({block: 'center'});
        }""")
        time.sleep(1)

        verify_path = str(AETHER_ROOT / "exports/screenshots/jared_blog_padding_verified.png")
        page.screenshot(path=verify_path, full_page=False)
        print(f"  Screenshot: {verify_path}")

        computed = page.evaluate("""() => {
            const img = document.querySelector('.et_post_meta_wrapper img');
            if (!img) return {error: 'no image found'};
            const cs = window.getComputedStyle(img);
            return {
                viewportWidth: window.innerWidth,
                imgWidth: img.offsetWidth,
                imgMaxWidth: cs.maxWidth,
                imgMarginLeft: cs.marginLeft,
                imgBoundsLeft: img.getBoundingClientRect().left,
                imgBoundsRight: img.getBoundingClientRect().right,
                imgBorderRadius: cs.borderRadius,
                imgBoxShadow: cs.boxShadow !== 'none' ? 'present' : 'none',
                hasOurCSS: !!document.querySelector('style') &&
                    Array.from(document.querySelectorAll('style')).some(
                        s => s.textContent.includes('JAREDDSANBORN.COM - BLOG POST')
                    )
            };
        }""")

        print("\n  === jareddsanborn.com Computed Styles ===")
        for k, v in computed.items():
            print(f"  {k}: {v}")

        browser.close()
        return computed


if __name__ == "__main__":
    print("=" * 60)
    print("JAREDDSANBORN.COM BLOG POST PADDING FIX")
    print("=" * 60)

    if not WP_PASSWORD:
        print("ERROR: WORDPRESS_APP_PASSWORD not found in .env")
        sys.exit(1)

    print(f"WP User: {WP_USER}")
    print(f"WP Password: {'*' * len(WP_PASSWORD)}")

    result = deploy()

    if result:
        print("\n[Deploy reported success. Running verification...]")
        time.sleep(5)
        computed = verify()
        if computed.get('imgBoundsLeft', 0) > 50:
            print(f"\n[SUCCESS] Blog padding is live on jareddsanborn.com!")
            print(f"  Image left from viewport: {computed.get('imgBoundsLeft')}px")
        else:
            print(f"\n[WARNING] Verification shows image at left edge. May need manual review.")
    else:
        print("\n[FAILED] Deploy did not complete. Manual intervention needed.")
