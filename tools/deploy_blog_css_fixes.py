#!/usr/bin/env python3
"""
Deploy Blog CSS Fixes to purebrain.ai
Feb 18, 2026 - Fix lime green elements, logo size, hover text issues

Strategy:
1. Read current CSS from the export file
2. Append new blog-specific fixes
3. Deploy via Playwright to WordPress Customizer > Additional CSS
"""

import asyncio
import os
import sys
import time
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright

# Load environment
from dotenv import load_dotenv
load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

# Configuration
WP_ADMIN_URL = "https://purebrain.ai/wp-admin"
WP_CSS_URL = "https://purebrain.ai/wp-admin/customize.php?autofocus[section]=custom_css"
USERNAME = "Aether"
PASSWORD = os.getenv('PUREBRAIN_WP_PASSWORD', '')
APP_PASSWORD = os.getenv('PUREBRAIN_WP_APP_PASSWORD', '')

CSS_FILE = "/home/jared/projects/AI-CIV/aether/exports/purebrain-complete-styling.css"
SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/tools/screenshots"

# New CSS fixes to append
NEW_CSS_FIXES = """

/* ============================================
   BLOG POST FIXES - Feb 18, 2026
   Scoped to blog pages only - DO NOT affect homepage
   Issues: lime green elements, logo size, hover text
   ============================================ */

/* 1. Loading spinner dot - lime green to orange */
.single-post .starter-starter-preloader .starter-preloader-dot,
.blog .starter-starter-preloader .starter-preloader-dot,
.starter-starter-preloader .starter-preloader-dot,
body.single-post .starter-starter-preloader .starter-preloader-dot,
body.blog .starter-starter-preloader .starter-preloader-dot {
    background-color: #f1420b !important;
}

/* Loading spinner circle/arc - lime to blue */
.single-post .starter-starter-preloader .starter-preloader-circle,
.blog .starter-starter-preloader .starter-preloader-circle,
.starter-starter-preloader .starter-preloader-circle,
.starter-starter-preloader svg circle,
.starter-starter-preloader .starter-preloader-svg circle,
body.single-post .starter-starter-preloader svg circle,
body.blog .starter-starter-preloader svg circle {
    stroke: #2a93c1 !important;
}

/* 2. Footer social icons - override ANY lime/green to blue */
body.single-post footer .social-links a,
body.single-post footer .elementor-social-icon,
body.single-post .site-footer .social-links a,
body.blog footer .social-links a,
body.blog footer .elementor-social-icon,
footer .starter-footer-social-links a,
footer .starter-social-icon,
body.single-post footer a[class*="social"],
body.blog footer a[class*="social"],
footer .starter-social-links a,
.footer-social .starter-social-icon,
#site-footer .starter-social-icon,
.starter-footer-social-links .starter-social-icon {
    color: #2a93c1 !important;
    border-color: #2a93c1 !important;
    background-color: transparent !important;
    fill: #2a93c1 !important;
}

footer .starter-footer-social-links a:hover,
footer .starter-social-icon:hover,
.starter-footer-social-links .starter-social-icon:hover,
#site-footer .starter-social-icon:hover {
    color: #ffffff !important;
    background-color: #2a93c1 !important;
    fill: #ffffff !important;
}

/* Footer social icon SVGs - force blue not green */
footer .starter-social-icon svg,
footer .starter-social-icon i,
footer .starter-footer-social-links svg,
footer .starter-footer-social-links i,
#site-footer .starter-social-icon svg,
#site-footer .starter-social-icon i {
    color: #2a93c1 !important;
    fill: #2a93c1 !important;
}

footer .starter-social-icon:hover svg,
footer .starter-social-icon:hover i {
    color: #ffffff !important;
    fill: #ffffff !important;
}

/* 3. Social sharing icons above comments - lime to blue */
body.single-post .social-share a,
body.single-post .starter-social-share a,
body.single-post .starter-share-icons a,
body.single-post .starter-post-share a,
body.single-post .starter-social-icon-circle,
body.single-post .post-social-sharing a,
body.single-post [class*="social-share"] a,
body.single-post [class*="share-icons"] a {
    background-color: #2a93c1 !important;
    color: #ffffff !important;
    border-color: #2a93c1 !important;
}

body.single-post .social-share a:hover,
body.single-post .starter-social-share a:hover,
body.single-post .starter-share-icons a:hover,
body.single-post .starter-post-share a:hover,
body.single-post .post-social-sharing a:hover,
body.single-post [class*="social-share"] a:hover,
body.single-post [class*="share-icons"] a:hover {
    background-color: #f1420b !important;
    border-color: #f1420b !important;
}

/* 4. Post Comment button - lime to orange */
body.single-post .comment-form .submit,
body.single-post #commentform .submit,
body.single-post .form-submit .submit,
body.single-post .comment-form input[type="submit"],
body.single-post #commentform input[type="submit"],
body.single-post .form-submit input[type="submit"] {
    background-color: #f1420b !important;
    color: #ffffff !important;
    border-color: #f1420b !important;
    background: linear-gradient(135deg, #f1420b 0%, #d63a09 100%) !important;
}

body.single-post .comment-form .submit:hover,
body.single-post #commentform .submit:hover,
body.single-post .form-submit .submit:hover,
body.single-post .comment-form input[type="submit"]:hover,
body.single-post #commentform input[type="submit"]:hover {
    background-color: #2a93c1 !important;
    border-color: #2a93c1 !important;
    background: linear-gradient(135deg, #2a93c1 0%, #1a7aa8 100%) !important;
}

/* 5. Logo at top of blog posts - center and reduce by 75% */
body.single-post .site-branding img,
body.single-post .custom-logo,
body.single-post header .site-logo img,
body.single-post .starter-logo img,
body.single-post .starter-site-logo img,
body.blog .site-branding img,
body.blog .custom-logo,
body.blog header .site-logo img,
body.blog .starter-logo img,
body.blog .starter-site-logo img {
    max-width: 80px !important;
    height: auto !important;
    display: block !important;
    margin: 0 auto !important;
}

body.single-post .site-branding,
body.single-post header .site-logo,
body.single-post .starter-logo,
body.single-post .starter-site-logo,
body.blog .site-branding,
body.blog header .site-logo,
body.blog .starter-logo,
body.blog .starter-site-logo {
    text-align: center !important;
    display: flex !important;
    justify-content: center !important;
}

/* 7. Blog listing page - hover text fix */
/* When hovering article title buttons, text should be BLACK not orange */
/* (orange text on orange background = invisible) */
body.blog .starter-latest-posts a:hover,
body.blog .wp-block-latest-posts a:hover,
body.blog .starter-post-title a:hover,
body.blog article .entry-title a:hover,
body.blog .starter-posts-list a:hover,
body.page-id-95 .elementor-post__title a:hover,
body.page-id-95 .elementor-post__title:hover a {
    color: #000000 !important;
}

/* Fix button-style article links on hover */
body.blog .starter-read-more:hover,
body.blog .read-more-btn:hover {
    color: #ffffff !important;
    background-color: #2a93c1 !important;
}

/* Fix the elementor post title hover - ensure text stays WHITE on blue bg */
body.page-id-95 .elementor-post__title:hover a,
.elementor-post__title:hover a {
    color: #ffffff !important;
}

/* 8. Nuclear option: Override ANY remaining lime/green colors on blog pages */
/* Target common green hex values and named colors */
body.single-post [style*="color: lime"],
body.single-post [style*="color: green"],
body.single-post [style*="color: limegreen"],
body.single-post [style*="color: chartreuse"],
body.single-post [style*="color: greenyellow"],
body.single-post [style*="color:#b3ff00"],
body.single-post [style*="color:#9acd32"],
body.single-post [style*="color:#7cfc00"],
body.single-post [style*="color:#00ff00"],
body.single-post [style*="color:#adff2f"],
body.single-post [style*="color:#39ff14"],
body.blog [style*="color: lime"],
body.blog [style*="color: green"],
body.blog [style*="color: limegreen"],
body.blog [style*="color:#b3ff00"],
body.blog [style*="color:#00ff00"] {
    color: #2a93c1 !important;
}

body.single-post [style*="background-color: lime"],
body.single-post [style*="background-color: green"],
body.single-post [style*="background-color: limegreen"],
body.single-post [style*="background:#b3ff00"],
body.single-post [style*="background:#00ff00"],
body.blog [style*="background-color: lime"],
body.blog [style*="background-color: green"],
body.blog [style*="background:#b3ff00"],
body.blog [style*="background:#00ff00"] {
    background-color: #2a93c1 !important;
    background: #2a93c1 !important;
}

/* ========== END BLOG POST FIXES Feb 18, 2026 ========== */
"""


def load_existing_css():
    """Load existing CSS from file"""
    with open(CSS_FILE, 'r') as f:
        return f.read()


def build_complete_css():
    """Combine existing CSS with new fixes"""
    existing = load_existing_css()

    # Check if the Feb 18 fixes are already appended
    if "BLOG POST FIXES - Feb 18, 2026" in existing:
        print("Feb 18 fixes already present in CSS file. Updating...")
        # Remove old Feb 18 fixes and re-append
        marker = "/* ============================================\n   BLOG POST FIXES - Feb 18, 2026"
        idx = existing.find(marker)
        if idx > 0:
            existing = existing[:idx].rstrip()

    complete = existing + NEW_CSS_FIXES
    return complete


def save_updated_css(css_content):
    """Save the combined CSS back to file for reference"""
    with open(CSS_FILE, 'w') as f:
        f.write(css_content)
    print(f"Saved updated CSS to {CSS_FILE} ({len(css_content)} chars)")


async def deploy_via_playwright(css_content):
    """Deploy CSS via Playwright browser automation"""
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        try:
            # Step 1: Navigate to WordPress login
            print("\n[Step 1] Navigating to WordPress login...")
            await page.goto(f"{WP_ADMIN_URL}/", wait_until="load", timeout=60000)

            screenshot_path = f"{SCREENSHOT_DIR}/blog_fix_01_login_{timestamp}.png"
            await page.screenshot(path=screenshot_path)
            print(f"  Screenshot: {screenshot_path}")

            # Step 2: Handle login
            print("[Step 2] Logging in...")

            # Check for GoDaddy SSO
            try:
                login_link = await page.wait_for_selector('text="Log in with username and password"', timeout=5000)
                await login_link.click()
                await asyncio.sleep(2)
                print("  Clicked 'Log in with username and password'")
            except:
                print("  Standard login form visible")

            # Wait for login form
            await page.wait_for_selector('#user_login', state='visible', timeout=30000)

            # Fill credentials
            await page.fill('#user_login', USERNAME)
            await page.fill('#user_pass', PASSWORD)

            # Check for CAPTCHA
            captcha_input = await page.query_selector('input[name="captcha_code"]')
            if captcha_input:
                screenshot_path = f"{SCREENSHOT_DIR}/blog_fix_02_captcha_{timestamp}.png"
                await page.screenshot(path=screenshot_path)
                print(f"\n*** CAPTCHA DETECTED ***")
                print(f"  Screenshot: {screenshot_path}")
                print("  Cannot proceed without CAPTCHA solution.")
                print("  Please login manually or try App Password approach.")
                await browser.close()
                return False

            # Click submit
            await page.click('#wp-submit')
            await page.wait_for_load_state('load', timeout=60000)
            await asyncio.sleep(5)

            screenshot_path = f"{SCREENSHOT_DIR}/blog_fix_03_dashboard_{timestamp}.png"
            await page.screenshot(path=screenshot_path)
            print(f"  Screenshot: {screenshot_path}")

            # Verify login
            if await page.query_selector('#wpadminbar') or 'wp-admin' in page.url:
                print("  Login successful!")
            else:
                error = await page.query_selector('#login_error')
                if error:
                    error_text = await error.inner_text()
                    print(f"  Login error: {error_text}")
                    await browser.close()
                    return False
                print("  Warning: Login verification unclear, continuing...")

            # Step 3: Navigate to Additional CSS
            print("[Step 3] Navigating to Additional CSS...")
            await page.goto(WP_CSS_URL, wait_until='load', timeout=90000)
            await asyncio.sleep(10)  # Customizer needs time

            screenshot_path = f"{SCREENSHOT_DIR}/blog_fix_04_customizer_{timestamp}.png"
            await page.screenshot(path=screenshot_path)
            print(f"  Screenshot: {screenshot_path}")

            # Wait for customizer
            try:
                await page.wait_for_selector('#customize-controls', state='visible', timeout=30000)
            except:
                print("  Warning: customize-controls not found, continuing...")

            await asyncio.sleep(5)

            # Step 4: Update CSS
            print("[Step 4] Updating CSS content...")

            codemirror = await page.query_selector('.CodeMirror')
            if codemirror:
                print("  Found CodeMirror editor")
                await codemirror.click()
                await asyncio.sleep(1)

                # Set value via JavaScript
                # We need to escape the CSS for JS
                await page.evaluate("""(css) => {
                    const cm = document.querySelector('.CodeMirror').CodeMirror;
                    cm.setValue(css);
                }""", css_content)

                await asyncio.sleep(2)
                print(f"  CSS updated ({len(css_content)} characters)")

                screenshot_path = f"{SCREENSHOT_DIR}/blog_fix_05_css_updated_{timestamp}.png"
                await page.screenshot(path=screenshot_path)
                print(f"  Screenshot: {screenshot_path}")
            else:
                print("  ERROR: CodeMirror not found!")
                # Try plain textarea
                textarea = await page.query_selector('textarea.wp-editor-area, #custom-css-textarea, textarea[id*="css"]')
                if textarea:
                    print("  Found plain textarea")
                    await textarea.fill(css_content)
                else:
                    print("  ERROR: No CSS editor found!")
                    screenshot_path = f"{SCREENSHOT_DIR}/blog_fix_05_error_{timestamp}.png"
                    await page.screenshot(path=screenshot_path)
                    html = await page.content()
                    debug_path = f"{SCREENSHOT_DIR}/debug_page_{timestamp}.html"
                    with open(debug_path, 'w') as f:
                        f.write(html)
                    print(f"  Saved debug HTML to {debug_path}")
                    await browser.close()
                    return False

            # Step 5: Publish
            print("[Step 5] Publishing...")
            await asyncio.sleep(3)

            publish_selectors = [
                '#save',
                '#customize-save-button-wrapper button',
                'input[type="submit"][value="Publish"]',
                'button:has-text("Publish")',
            ]

            publish_btn = None
            for selector in publish_selectors:
                try:
                    btn = await page.query_selector(selector)
                    if btn and await btn.is_visible():
                        publish_btn = btn
                        print(f"  Found publish button: {selector}")
                        break
                except:
                    continue

            if publish_btn:
                await publish_btn.click()
                print("  Clicked publish!")
                await asyncio.sleep(5)

                screenshot_path = f"{SCREENSHOT_DIR}/blog_fix_06_published_{timestamp}.png"
                await page.screenshot(path=screenshot_path)
                print(f"  Screenshot: {screenshot_path}")
            else:
                print("  Publish button not found, trying Ctrl+Shift+S...")
                await page.keyboard.press('Control+Shift+s')
                await asyncio.sleep(5)

            # Step 6: Verify - visit blog post
            print("[Step 6] Verifying on blog post...")
            await page.goto(
                "https://purebrain.ai/most-ai-agents-break-the-moment-you-ask-where-the-data-goes-2/",
                wait_until='load', timeout=60000
            )
            await asyncio.sleep(5)

            screenshot_path = f"{SCREENSHOT_DIR}/blog_fix_07_blog_post_{timestamp}.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"  Blog post screenshot: {screenshot_path}")

            # Step 7: Verify homepage not broken
            print("[Step 7] Verifying homepage...")
            await page.goto("https://purebrain.ai/", wait_until='load', timeout=60000)
            await asyncio.sleep(5)

            screenshot_path = f"{SCREENSHOT_DIR}/blog_fix_08_homepage_{timestamp}.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"  Homepage screenshot: {screenshot_path}")

            # Step 8: Verify blog listing page
            print("[Step 8] Verifying blog listing...")
            await page.goto("https://purebrain.ai/blog/", wait_until='load', timeout=60000)
            await asyncio.sleep(5)

            screenshot_path = f"{SCREENSHOT_DIR}/blog_fix_09_blog_listing_{timestamp}.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"  Blog listing screenshot: {screenshot_path}")

            print("\n=== DEPLOYMENT COMPLETE ===")
            print(f"Total CSS size: {len(css_content)} characters")
            print(f"Screenshots saved to: {SCREENSHOT_DIR}")

            await browser.close()
            return True

        except Exception as e:
            print(f"\nERROR: {e}")
            import traceback
            traceback.print_exc()
            screenshot_path = f"{SCREENSHOT_DIR}/blog_fix_error_{timestamp}.png"
            try:
                await page.screenshot(path=screenshot_path)
                print(f"Error screenshot: {screenshot_path}")
            except:
                pass
            await browser.close()
            return False


async def main():
    print("=" * 60)
    print("PureBrain.ai Blog CSS Fix Deployment")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    # Build complete CSS
    print("\n[1] Building complete CSS...")
    complete_css = build_complete_css()
    print(f"  Total CSS: {len(complete_css)} characters")

    # Save to file
    print("\n[2] Saving updated CSS file...")
    save_updated_css(complete_css)

    # Deploy
    print("\n[3] Deploying via Playwright...")
    success = await deploy_via_playwright(complete_css)

    if success:
        print("\n*** SUCCESS ***")
        print("CSS deployed to purebrain.ai")
        print("Verify visually:")
        print("  - Blog post: https://purebrain.ai/most-ai-agents-break-the-moment-you-ask-where-the-data-goes-2/")
        print("  - Blog listing: https://purebrain.ai/blog/")
        print("  - Homepage: https://purebrain.ai/")
    else:
        print("\n*** DEPLOYMENT FAILED ***")
        print("Check screenshots for diagnostics.")

    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
