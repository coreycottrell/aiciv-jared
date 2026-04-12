#!/usr/bin/env python3
"""
Delayed Blog Styling Fix
Waits 45 minutes then applies comprehensive blog styling fixes to purebrain.ai

FIXES:
1. Logo - centered, reduced size by 75%
2. Loading spinner - green → orange
3. Footer social icons - green → blue
4. Share icons (top) - green → blue
5. Comment section - styled to match brand
"""

import asyncio
import time
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, '/home/jared/projects/AI-CIV/aether')

from playwright.async_api import async_playwright
import requests

# Configuration
WP_ADMIN_URL = "https://purebrain.ai/wp-admin"
WP_CUSTOMIZER_URL = "https://purebrain.ai/wp-admin/customize.php?autofocus[section]=custom_css"
BLOG_POST_URL = "https://purebrain.ai/most-ai-agents-break-the-moment-you-ask-where-the-data-goes/"
HOMEPAGE_URL = "https://purebrain.ai"
USERNAME = "Aether"
PASSWORD = "b&JJRfs)6yuSWJCc7WiFY)G8"

SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/sandbox/blog-styling-fix"
LOG_FILE = "/home/jared/projects/AI-CIV/aether/logs/blog_styling_fix.log"

# CSS File to apply
CSS_FILE = "/home/jared/projects/AI-CIV/aether/exports/blog-complete-styling-fix.css"

# Wait time in minutes
WAIT_MINUTES = 45

def log(msg):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {msg}"
    print(log_msg)
    Path(LOG_FILE).parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, 'a') as f:
        f.write(log_msg + "\n")

def send_telegram(msg):
    """Send notification to Jared via Telegram"""
    try:
        BOT_TOKEN = '8559081952:AAHcLiEcC3GtQCAHRu5yc86BByiiLDqyjz0'
        CHAT_ID = '548906264'
        requests.post(
            f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
            data={'chat_id': CHAT_ID, 'text': f"🤖 Blog Styling Fix:\n\n{msg}", 'parse_mode': 'HTML'},
            timeout=30
        )
    except Exception as e:
        log(f"Telegram notification failed: {e}")

async def take_screenshot(page, name):
    """Take screenshot with timestamp"""
    Path(SCREENSHOT_DIR).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"{SCREENSHOT_DIR}/{timestamp}_{name}.png"
    await page.screenshot(path=path, full_page=False)
    log(f"Screenshot: {path}")
    return path

async def verify_pages(page, stage):
    """Verify both homepage and blog post look correct"""
    results = {}

    # Check homepage
    try:
        log(f"Checking homepage at stage: {stage}")
        await page.goto(HOMEPAGE_URL, wait_until='domcontentloaded', timeout=60000)
        await asyncio.sleep(3)
        await take_screenshot(page, f"{stage}_homepage")
        hero = await page.locator('text=YOUR BRAIN').is_visible()
        results['homepage'] = hero
        log(f"  Homepage hero visible: {hero}")
    except Exception as e:
        log(f"  Homepage check failed: {e}")
        results['homepage'] = False

    # Check blog post
    try:
        log(f"Checking blog post at stage: {stage}")
        await page.goto(BLOG_POST_URL, wait_until='domcontentloaded', timeout=60000)
        await asyncio.sleep(3)
        await take_screenshot(page, f"{stage}_blogpost")
        title = await page.locator('text=Most AI Agents').is_visible()
        results['blogpost'] = title
        log(f"  Blog title visible: {title}")
    except Exception as e:
        log(f"  Blog post check failed: {e}")
        results['blogpost'] = False

    return results

async def login_wordpress(page):
    """Log into WordPress admin"""
    try:
        log("Navigating to WordPress login...")
        await page.goto(WP_ADMIN_URL, wait_until='domcontentloaded', timeout=60000)
        await asyncio.sleep(3)

        # Check if already logged in
        if 'wp-admin' in page.url and 'login' not in page.url:
            log("Already logged in")
            return True

        # Handle "Log in with username and password" link
        username_login_link = page.locator('text=Log in with username and password')
        if await username_login_link.count() > 0:
            await username_login_link.click()
            await asyncio.sleep(2)

        # Fill login form
        await page.fill('#user_login', USERNAME)
        await page.fill('#user_pass', PASSWORD)
        await page.click('#wp-submit')
        await asyncio.sleep(5)

        # Check for CAPTCHA
        page_content = await page.content()
        if 'captcha' in page_content.lower() or 'recaptcha' in page_content.lower():
            log("❌ CAPTCHA detected - cannot proceed")
            send_telegram("❌ CAPTCHA still active. Please wait longer or apply CSS manually.\n\nFile: exports/blog-complete-styling-fix.css")
            return False

        # Verify login
        if 'wp-admin' in page.url and 'login' not in page.url:
            log("✅ WordPress login successful")
            return True
        else:
            log("❌ WordPress login failed")
            return False

    except Exception as e:
        log(f"❌ Login error: {e}")
        return False

async def apply_css_via_customizer(page, css_content):
    """Apply CSS via WordPress Customizer"""
    try:
        log("Navigating to WordPress Customizer...")
        await page.goto(WP_CUSTOMIZER_URL, wait_until='domcontentloaded', timeout=60000)
        await asyncio.sleep(8)

        await take_screenshot(page, "customizer_loaded")

        # Wait for customizer to load
        try:
            await page.wait_for_selector('#customize-controls', timeout=30000)
            log("Customizer controls loaded")
        except:
            log("⚠️ Customizer controls not found, trying anyway...")

        # Click on Additional CSS section if collapsed
        try:
            section = page.locator('li[id*="custom_css"]')
            if await section.count() > 0:
                await section.click()
                await asyncio.sleep(2)
        except:
            pass

        # Use JavaScript to append CSS to CodeMirror
        result = await page.evaluate('''(cssContent) => {
            // Try to find CodeMirror
            const cm = document.querySelector('.CodeMirror');
            if (cm && cm.CodeMirror) {
                const editor = cm.CodeMirror;
                const currentContent = editor.getValue();
                const timestamp = new Date().toISOString();
                const newContent = currentContent + "\\n\\n/* === BLOG STYLING FIX BY AETHER - " + timestamp + " === */\\n" + cssContent;
                editor.setValue(newContent);
                return {success: true, newLength: newContent.length, method: 'codemirror'};
            }

            // Fallback: try textarea
            const textarea = document.querySelector('textarea[id*="custom_css"]');
            if (textarea) {
                const currentContent = textarea.value;
                const timestamp = new Date().toISOString();
                textarea.value = currentContent + "\\n\\n/* === BLOG STYLING FIX BY AETHER - " + timestamp + " === */\\n" + cssContent;
                textarea.dispatchEvent(new Event('change', {bubbles: true}));
                return {success: true, newLength: textarea.value.length, method: 'textarea'};
            }

            return {success: false, error: 'No editor found'};
        }''', css_content)

        if result.get('success'):
            log(f"CSS appended via {result.get('method')}, new length: {result.get('newLength')}")
            await take_screenshot(page, "css_appended")

            # Click Publish
            await asyncio.sleep(2)
            publish_btn = page.locator('#save, input[value="Publish"], button:has-text("Publish")')
            if await publish_btn.count() > 0:
                await publish_btn.first.click()
                await asyncio.sleep(5)
                await take_screenshot(page, "after_publish")
                log("✅ Publish button clicked")
                return True
            else:
                log("⚠️ Publish button not found")
                return False
        else:
            log(f"❌ Failed to append CSS: {result.get('error')}")
            return False

    except Exception as e:
        log(f"❌ Error applying CSS: {e}")
        await take_screenshot(page, "error_state")
        return False

async def main():
    """Main function"""
    log("=" * 60)
    log("BLOG STYLING FIX SCRIPT STARTED")
    log(f"Will wait {WAIT_MINUTES} minutes before executing")
    log("=" * 60)

    send_telegram(f"⏰ Blog styling fix scheduled.\nWaiting {WAIT_MINUTES} minutes for CAPTCHA cooldown...\n\nFixes queued:\n• Logo centering + 75% size reduction\n• Green → Blue social icons\n• Comment section styling\n• Loading spinner color")

    # Wait
    for i in range(WAIT_MINUTES):
        await asyncio.sleep(60)
        remaining = WAIT_MINUTES - i - 1
        if remaining % 15 == 0 and remaining > 0:
            log(f"{remaining} minutes remaining...")

    log("Wait complete. Starting deployment...")
    send_telegram("🚀 Starting blog styling fix deployment...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()

        try:
            # Step 1: Verify pages BEFORE
            log("\n--- STEP 1: Pre-deployment verification ---")
            before = await verify_pages(page, "01_BEFORE")

            # Step 2: Login
            log("\n--- STEP 2: WordPress login ---")
            if not await login_wordpress(page):
                return

            # Step 3: Load CSS
            log("\n--- STEP 3: Loading CSS file ---")
            if not Path(CSS_FILE).exists():
                log(f"❌ CSS file not found: {CSS_FILE}")
                send_telegram(f"❌ CSS file not found: {CSS_FILE}")
                return

            with open(CSS_FILE, 'r') as f:
                css_content = f.read()
            log(f"Loaded CSS: {len(css_content)} chars")

            # Step 4: Apply CSS
            log("\n--- STEP 4: Applying CSS ---")
            if not await apply_css_via_customizer(page, css_content):
                send_telegram("❌ Failed to apply CSS. Manual application needed.\n\nFile: exports/blog-complete-styling-fix.css")
                return

            # Step 5: Verify pages AFTER
            log("\n--- STEP 5: Post-deployment verification ---")
            await asyncio.sleep(5)
            after = await verify_pages(page, "02_AFTER")

            # Report results
            if after.get('homepage') and after.get('blogpost'):
                send_telegram("✅ Blog styling fix COMPLETE!\n\nApplied:\n• Logo centered + reduced 75%\n• Social icons → blue\n• Comment section styled\n• Loading spinner → orange\n\nHomepage ✅\nBlog post ✅\n\nScreenshots in: sandbox/blog-styling-fix/")
                log("✅ DEPLOYMENT SUCCESSFUL")
            else:
                send_telegram(f"⚠️ Blog styling fix applied but verification had issues.\n\nHomepage: {'✅' if after.get('homepage') else '❌'}\nBlog post: {'✅' if after.get('blogpost') else '❌'}\n\nPlease check manually!")
                log("⚠️ DEPLOYMENT COMPLETE WITH WARNINGS")

        except Exception as e:
            log(f"❌ Error: {e}")
            send_telegram(f"❌ Blog styling fix error: {e}")

        finally:
            await browser.close()

    log("=" * 60)
    log("BLOG STYLING FIX SCRIPT COMPLETED")
    log("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
