#!/usr/bin/env python3
"""
Fix Blog CTA Button Hover Effect on purebrain.ai
2026-02-20

The existing "FIX 3" CSS in WordPress Additional CSS makes the button background
transparent on hover. We need to REPLACE it with a blue glow/highlight effect.

New behavior: orange button stays orange, but gets a blue (#2a93c1) box-shadow glow
on hover, matching PureBrain brand.

Strategy: Use Playwright to update Additional CSS in WordPress Customizer.
"""

import asyncio
import os
import sys
import time
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

WP_ADMIN_URL = "https://purebrain.ai/wp-admin"
WP_CSS_URL = "https://purebrain.ai/wp-admin/customize.php?autofocus[section]=custom_css"
USERNAME = "Aether"
PASSWORD = os.getenv('PUREBRAIN_WP_PASSWORD', '')
SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots"

# The OLD FIX 3 rule to replace
OLD_FIX3 = """/* FIX 3: Newsletter / subscribe link - no orange background, white border on hover */
body.single-post .blog-cta-block a:hover,
body.single-post .blog-cta-block p a:hover {
    background: transparent !important;
    background-color: transparent !important;
    color: #2a93c1 !important;
    border: 1px solid #ffffff !important;
    border-radius: 3px !important;
    padding: 1px 4px !important;
    text-decoration: underline !important;
}"""

# The NEW replacement
NEW_FIX3 = """/* FIX 3: "Start Your AI Partnership" CTA button - blue glow highlight on hover */
/* Orange background stays; adds brand blue (#2a93c1) box-shadow glow */
body.single-post .blog-cta-block a,
body.single-post .blog-cta-block p a {
    transition: box-shadow 0.25s ease, transform 0.2s ease !important;
}

body.single-post .blog-cta-block a:hover,
body.single-post .blog-cta-block p a:hover {
    box-shadow:
        0 0 0 3px #2a93c1,
        0 0 18px rgba(42, 147, 193, 0.55),
        0 6px 20px rgba(0, 0, 0, 0.35) !important;
    transform: translateY(-2px) !important;
    text-decoration: none !important;
    color: #ffffff !important;
}

body.single-post .blog-cta-block a:focus,
body.single-post .blog-cta-block p a:focus {
    outline: none !important;
    box-shadow:
        0 0 0 3px #2a93c1,
        0 0 18px rgba(42, 147, 193, 0.55) !important;
}"""


async def get_customizer_css(page):
    """Get current CSS from WordPress Customizer via CodeMirror."""
    try:
        css = await page.evaluate("""() => {
            if (window.wp && wp.customize) {
                const css = wp.customize('custom_css_post_id');
                if (css) return css.get();
            }
            // Try CodeMirror
            const cm = document.querySelector('.CodeMirror');
            if (cm && cm.CodeMirror) {
                return cm.CodeMirror.getValue();
            }
            return null;
        }""")
        return css
    except Exception as e:
        print(f"  Error getting CSS: {e}")
        return None


async def set_customizer_css(page, css_content):
    """Set CSS in WordPress Customizer via CodeMirror."""
    escaped_css = css_content.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')
    try:
        result = await page.evaluate(f"""() => {{
            const cm = document.querySelector('.CodeMirror');
            if (cm && cm.CodeMirror) {{
                cm.CodeMirror.setValue(`{escaped_css}`);
                return 'set';
            }}
            return 'no-codemirror';
        }}""")
        return result
    except Exception as e:
        print(f"  Error setting CSS: {e}")
        return None


async def fix_cta_hover():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        print("Step 1: Login to WP Admin...")
        await page.goto(f"{WP_ADMIN_URL}/", wait_until="load", timeout=60000)
        await asyncio.sleep(2)

        # Handle GoDaddy SSO
        try:
            login_link = await page.wait_for_selector(
                'text="Log in with username and password"', timeout=5000
            )
            await login_link.click()
            await asyncio.sleep(2)
            print("  Clicked 'Log in with username and password'")
        except Exception:
            print("  Standard login form visible")

        # Wait for login form
        await page.wait_for_selector('#user_login', state='visible', timeout=30000)
        await page.fill('#user_login', USERNAME)
        await page.fill('#user_pass', PASSWORD)
        await page.click('#wp-submit')
        await page.wait_for_load_state('load', timeout=60000)
        await asyncio.sleep(3)

        if not ('wp-admin' in page.url or await page.query_selector('#wpadminbar')):
            print(f"Login may have failed. URL: {page.url}")
            os.makedirs(SCREENSHOT_DIR, exist_ok=True)
            await page.screenshot(path=f"{SCREENSHOT_DIR}/cta_fix_login.png")
            await browser.close()
            return False
        print("  Login SUCCESS!")

        print("Step 2: Navigate to Customizer CSS...")
        await page.goto(WP_CSS_URL, wait_until="load", timeout=90000)
        await asyncio.sleep(15)  # Customizer needs extra time

        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        await page.screenshot(path=f"{SCREENSHOT_DIR}/cta_fix_customizer.png")
        print(f"  Customizer loaded. URL: {page.url}")

        print("Step 3: Get current CSS...")
        # Wait for CodeMirror
        try:
            await page.wait_for_selector('.CodeMirror', state='visible', timeout=30000)
            print("  CodeMirror found!")
        except Exception:
            print("  Warning: CodeMirror not found within timeout")

        await asyncio.sleep(3)

        css = await get_customizer_css(page)
        if not css:
            print("  ERROR: Could not get CSS via JavaScript")
            # Try alternative
            css_input = await page.query_selector('#customize-control-custom_css textarea')
            if css_input:
                css = await css_input.input_value()
                print(f"  Got CSS via textarea: {len(css)} chars")
            else:
                # Take screenshot to debug
                await page.screenshot(path=f"{SCREENSHOT_DIR}/cta_fix_no_css.png")
                print("  Could not find CSS. Screenshot saved.")
                await browser.close()
                return False

        print(f"  Current CSS length: {len(css)} chars")
        print(f"  OLD FIX 3 present: {OLD_FIX3.strip()[:50] in css}")

        # Check for the old FIX 3
        if 'no orange background, white border on hover' not in css and 'blog-cta-block a:hover' in css:
            print("  FIX 3 text found but different format - searching...")
            # Show what's there
            idx = css.find('blog-cta-block a:hover')
            print(f"  Context: {css[max(0,idx-100):idx+300]}")

        print("Step 4: Replace FIX 3 with new blue glow CSS...")

        # Do the replacement
        old_marker = '/* FIX 3: Newsletter / subscribe link - no orange background, white border on hover */'
        if old_marker in css:
            print("  Found FIX 3 marker. Replacing...")
            new_css = css.replace(OLD_FIX3, NEW_FIX3)
            if new_css == css:
                # Try with normalized whitespace
                print("  Exact match failed, trying normalized replacement...")
                # Find the section
                idx = css.find('/* FIX 3: Newsletter')
                end_marker = '/* ========== END BLOG POST HOVER FIXES ========== */'
                end_idx = css.find(end_marker, idx)
                if idx >= 0 and end_idx > idx:
                    # Get the FIX 3 block
                    fix3_block = css[idx:end_idx]
                    print(f"  FIX 3 block found ({len(fix3_block)} chars)")
                    # Replace the FIX 3 block
                    new_css = css[:idx] + NEW_FIX3 + '\n\n' + css[end_idx:]
                    print(f"  Replaced! New CSS: {len(new_css)} chars")
                else:
                    print(f"  Could not find end marker. idx={idx}, end_idx={end_idx}")
                    new_css = css
        elif 'blog-cta-block a:hover' in css:
            print("  FIX 3 present but with different comment. Finding block...")
            idx = css.find('blog-cta-block a:hover')
            # Show context
            print(f"  Context around blog-cta-block: {css[max(0,idx-200):idx+300]}")
            # Try to find and replace the block
            # Look for the comment before it
            comment_start = css.rfind('/*', 0, idx)
            block_end = css.find('\n}', idx) + 2  # Include closing brace
            if comment_start >= 0 and block_end > idx:
                old_block = css[comment_start:block_end]
                print(f"  Found block ({len(old_block)} chars): {old_block[:100]}...")
                new_css = css[:comment_start] + NEW_FIX3 + css[block_end:]
            else:
                print("  Could not find block boundaries. Will append new CSS.")
                new_css = css + '\n\n' + NEW_FIX3
        else:
            print("  FIX 3 not found. Will append new CSS to end.")
            new_css = css + '\n\n' + NEW_FIX3

        if new_css == css:
            print("  WARNING: No changes made to CSS!")
            if 'translateY(-2px)' in css:
                print("  Blue glow already present! Nothing to do.")
                await browser.close()
                return True
        else:
            print(f"  CSS changed. New length: {len(new_css)} chars")

        print("Step 5: Set new CSS in CodeMirror...")
        result = await set_customizer_css(page, new_css)
        print(f"  Set result: {result}")

        if result == 'no-codemirror':
            print("  CodeMirror not found! Trying textarea approach...")
            textarea = await page.query_selector('#customize-control-custom_css textarea')
            if textarea:
                await page.fill('#customize-control-custom_css textarea', new_css)
                print("  Set via textarea.")
            else:
                print("  ERROR: Cannot find CSS editor!")
                await browser.close()
                return False

        await asyncio.sleep(2)

        print("Step 6: Save/Publish the customizer changes...")
        # Click the Publish/Save button
        save_btn = page.locator('#save')
        if await save_btn.count() > 0:
            await save_btn.click()
            await asyncio.sleep(5)
            print("  Saved!")
        else:
            # Try other save button selectors
            publish_btn = page.locator('.customize-save-and-publish, input.save, #customize-save-button')
            if await publish_btn.count() > 0:
                await publish_btn.first.click()
                await asyncio.sleep(5)
                print("  Published!")
            else:
                print("  WARNING: Could not find save button!")
                await page.screenshot(path=f"{SCREENSHOT_DIR}/cta_fix_no_save_btn.png")

        await page.screenshot(path=f"{SCREENSHOT_DIR}/cta_fix_saved.png")
        print(f"  Screenshot saved.")

        await browser.close()
        return True


if __name__ == '__main__':
    result = asyncio.run(fix_cta_hover())
    print(f"\n{'SUCCESS' if result else 'FAILED'}")
    sys.exit(0 if result else 1)
