#!/usr/bin/env python3
"""
PureBrain Body Color Fix
Fixes the root cause - body color inheritance
"""

import asyncio
from playwright.async_api import async_playwright
import os
from datetime import datetime

SCREENSHOT_DIR = "/tmp"
WP_URL = "https://purebrain.ai/wp-admin"
WP_USER = "Purebrain@puremarketing.ai"
WP_PASS = "NW2u!JLQ3!Bt$XD$7CWzz5Z@"

async def save_screenshot(page, label):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"purebrain-body-fix-{timestamp}-{label}.png"
    filepath = os.path.join(SCREENSHOT_DIR, filename)
    await page.screenshot(path=filepath, full_page=False)
    print(f"Saved: {filepath}")
    return filepath

async def fix_body_color():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        page.set_default_timeout(60000)

        print("=" * 60)
        print("PUREBRAIN BODY COLOR FIX")
        print("=" * 60)

        screenshots = []

        # Login
        print("\n[1] Logging into WordPress...")
        await page.goto(WP_URL, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(2)

        # Click username/password link
        link = page.locator("text=Log in with username and password")
        if await link.is_visible(timeout=5000):
            await link.click()
            await asyncio.sleep(2)

        await page.fill("#user_login", WP_USER)
        await page.fill("#user_pass", WP_PASS)
        await page.click("#wp-submit")
        await asyncio.sleep(3)

        # Navigate to Additional CSS
        print("\n[2] Navigating to Additional CSS...")
        await page.goto("https://purebrain.ai/wp-admin/customize.php?autofocus[section]=custom_css", wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(8)  # Wait longer for customizer

        screenshots.append(await save_screenshot(page, "01-customizer"))

        # Get current CSS
        print("\n[3] Getting current CSS...")
        current_css = ""
        cm_present = await page.locator(".CodeMirror").count()

        if cm_present > 0:
            current_css = await page.evaluate("() => document.querySelector('.CodeMirror').CodeMirror.getValue()")
            print(f"  Current CSS: {len(current_css)} chars")

        # The REAL fix - target the actual elements and body
        body_color_fix = '''
/* ===========================================
   PUREBRAIN BODY COLOR FIX - 2026-02-16
   ROOT CAUSE: Body inherits orange text color
   =========================================== */

/* CRITICAL FIX: Set default body text to white on dark sections */
body.home,
body.page-id-11 {
    color: #ffffff !important;
}

/* Hero section text */
body.home .hero__description,
body.home p.hero__description {
    color: #ffffff !important;
}

/* Section badges - should be white or cyan */
body.home .section__badge {
    color: #4dd0e1 !important;
}

/* Feature cards text */
body.home .feature-card,
body.home .feature-card p,
body.home .feature-card h3 {
    color: #ffffff !important;
}

/* Capability items */
body.home .capability-item,
body.home .capability-item p,
body.home .capability-item h3 {
    color: #ffffff !important;
}

/* Chat container */
body.home .chat-container,
body.home .chat-container p,
body.home .chat-header,
body.home .chat-messages {
    color: #ffffff !important;
}

/* Exit popup text */
body.home .exit-popup__text,
body.home .exit-popup__buttons {
    color: #ffffff !important;
}

/* The "Leave anyway" ghost button */
body.home .exit-popup__btn--ghost {
    color: #ffffff !important;
    border-color: rgba(255, 255, 255, 0.3) !important;
}

/* Celebration moment text */
body.home .celebration-moment__text {
    color: #ffffff !important;
}

/* Waitlist modal text */
body.home .waitlist-modal__badge {
    color: #ffffff !important;
    background: rgba(241, 66, 11, 0.2) !important;
}

body.home .waitlist-modal__text,
body.home .waitlist-success__text {
    color: #ffffff !important;
}

/* Marquee text */
body.home .marquee {
    color: rgba(255, 255, 255, 0.7) !important;
}

/* Pyramid layers text */
body.home #value-pyramid p,
body.home #value-pyramid div {
    color: #ffffff !important;
}

/* Section titles - white except accent words */
body.home .section__title {
    color: #ffffff !important;
}

/* Section descriptions */
body.home .section__description {
    color: rgba(255, 255, 255, 0.8) !important;
}

/* Rating buttons in form */
body.home .waitlist-form__rating-btn {
    color: #ffffff !important;
}

/* KEEP ORANGE (intentional brand accents) */
body.home .text-orange,
body.home span.text-orange {
    color: #f1420b !important;
}

/* CTA buttons - keep orange background */
body.home .hero__cta a,
body.home .btn-primary {
    background-color: #f1420b !important;
    color: #ffffff !important;
}

/* Blog pages - leave untouched */
body.single-post,
body.blog,
body.archive,
body.category,
body.tag {
    /* Default styling for blog */
}
'''

        # Check if this fix already exists
        if "PUREBRAIN BODY COLOR FIX - 2026-02-16" in current_css:
            print("\n  Fix already applied today!")
            combined_css = current_css
        else:
            print("\n  Adding body color fix...")
            combined_css = current_css + "\n\n" + body_color_fix

        # Apply the CSS
        print("\n[4] Applying CSS fix...")
        try:
            css_escaped = combined_css.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')
            await page.evaluate(f'''
                () => {{
                    const cm = document.querySelector('.CodeMirror').CodeMirror;
                    cm.setValue(`{css_escaped}`);
                }}
            ''')
            print("  CSS applied!")
            await asyncio.sleep(2)
            screenshots.append(await save_screenshot(page, "02-css-applied"))

        except Exception as e:
            print(f"  Error: {e}")

        # Publish
        print("\n[5] Publishing...")
        try:
            publish_btn = page.locator("input[type='submit'][value='Publish'], button:has-text('Publish')").first
            if await publish_btn.is_visible(timeout=5000):
                await publish_btn.click()
                await asyncio.sleep(3)
                print("  Published!")
                screenshots.append(await save_screenshot(page, "03-published"))
        except Exception as e:
            print(f"  Error publishing: {e}")

        # Verify
        print("\n[6] Verifying on site...")
        await page.goto("https://purebrain.ai", wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(3)
        screenshots.append(await save_screenshot(page, "04-hero-after"))

        # Scroll through page
        await page.evaluate("window.scrollTo(0, 800)")
        await asyncio.sleep(1)
        screenshots.append(await save_screenshot(page, "05-features-after"))

        await page.evaluate("window.scrollTo(0, 1600)")
        await asyncio.sleep(1)
        screenshots.append(await save_screenshot(page, "06-pyramid-after"))

        await page.evaluate("window.scrollTo(0, 2700)")
        await asyncio.sleep(1)
        screenshots.append(await save_screenshot(page, "07-awakening-after"))

        print("\n" + "=" * 60)
        print("BODY COLOR FIX COMPLETE")
        print("=" * 60)
        for s in screenshots:
            print(f"  {s}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(fix_body_color())
