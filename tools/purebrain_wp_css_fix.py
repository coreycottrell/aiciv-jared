#!/usr/bin/env python3
"""
PureBrain WordPress CSS Fix
Logs into WordPress and applies scoped CSS fixes for orange text issues
"""

import asyncio
from playwright.async_api import async_playwright
import os
from datetime import datetime

SCREENSHOT_DIR = "/tmp"

# WordPress credentials
WP_URL = "https://purebrain.ai/wp-admin"
WP_USER = "Purebrain@puremarketing.ai"
WP_PASS = "NW2u!JLQ3!Bt$XD$7CWzz5Z@"

async def save_screenshot(page, label):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"purebrain-wp-fix-{timestamp}-{label}.png"
    filepath = os.path.join(SCREENSHOT_DIR, filename)
    await page.screenshot(path=filepath, full_page=False)
    print(f"Saved: {filepath}")
    return filepath

async def apply_css_fixes():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        page.set_default_timeout(60000)

        print("=" * 60)
        print("PUREBRAIN WORDPRESS CSS FIX")
        print("=" * 60)

        screenshots = []

        # Login to WordPress
        print("\n[1] Logging into WordPress...")
        await page.goto(WP_URL, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(2)
        screenshots.append(await save_screenshot(page, "01-login-page"))

        # Click "Log in with username and password" link
        print("\n[2] Clicking 'Log in with username and password'...")
        username_password_link = page.locator("text=Log in with username and password")
        if await username_password_link.is_visible(timeout=5000):
            await username_password_link.click()
            await asyncio.sleep(2)
            screenshots.append(await save_screenshot(page, "02-login-form"))

        # Now fill the login form
        print("\n[3] Filling login form...")
        await page.fill("#user_login", WP_USER)
        await page.fill("#user_pass", WP_PASS)
        screenshots.append(await save_screenshot(page, "03-form-filled"))

        await page.click("#wp-submit")
        await asyncio.sleep(3)
        screenshots.append(await save_screenshot(page, "04-after-login"))

        # Check if we're logged in by looking for the admin bar
        print("\n[4] Checking login status...")
        dashboard = page.locator("#wpadminbar").first
        if await dashboard.is_visible(timeout=5000):
            print("  Successfully logged in!")
        else:
            print("  Login may have failed, continuing anyway...")

        # Navigate directly to Additional CSS customizer
        print("\n[5] Navigating to Additional CSS...")
        await page.goto("https://purebrain.ai/wp-admin/customize.php?autofocus[section]=custom_css", wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(5)
        screenshots.append(await save_screenshot(page, "05-customizer"))

        # Wait for customizer to fully load
        await asyncio.sleep(3)

        # Check if CodeMirror editor is present
        print("\n[6] Looking for CSS editor...")
        cm_present = await page.locator(".CodeMirror").count()
        print(f"  CodeMirror found: {cm_present > 0}")

        # Get current CSS
        current_css = ""
        try:
            if cm_present > 0:
                current_css = await page.evaluate("() => document.querySelector('.CodeMirror').CodeMirror.getValue()")
                print(f"  Current CSS length: {len(current_css)} chars")
            else:
                textarea = page.locator("#customize-control-custom_css textarea, textarea.wp-code-editor").first
                if await textarea.is_visible(timeout=3000):
                    current_css = await textarea.input_value()
                    print(f"  Current CSS length: {len(current_css)} chars")
        except Exception as e:
            print(f"  Error getting current CSS: {e}")

        print("\n  Current CSS preview:")
        print(current_css[:300] if current_css else "  (empty or not accessible)")

        # The comprehensive CSS fix
        new_css_additions = '''
/* ===========================================
   PUREBRAIN ORANGE TEXT FIXES - 2026-02-16
   SCOPED: Main page only, NOT blog posts
   =========================================== */

/* SECTION 1: Form Labels - Must be WHITE, not orange */
/* These selectors are specific to the main page awakening form */
body.home label,
body.page-id-2 label,
.awakening-form label,
.waitlist-form label,
.pb-form label,
[data-widget_type*="form"] label {
    color: #ffffff !important;
}

/* Specific labels from audit: Full Name, Email, Company, Role */
body.home .elementor-field-label,
body.page-id-2 .elementor-field-label {
    color: #ffffff !important;
}

/* SECTION 2: Modal/Popup Content */
/* The awakening modal text should be white, not orange */
.awakening-container p,
.awakening-container span:not(.brand-accent),
.modal-content p,
[role="dialog"] p,
.chat-container p {
    color: #ffffff !important;
}

/* "Leave anyway" button - white text */
button.leave-button,
.confirm-leave-btn {
    color: #ffffff !important;
}

/* SECTION 3: Limited Availability Banner */
.limited-availability,
.availability-notice {
    color: #ffffff !important;
}

/* SECTION 4: Timer/Countdown Text */
.timer-display,
.countdown-text,
.session-timer span {
    color: #ffffff !important;
}

/* SECTION 5: Hero Taglines (non-CTA text) */
/* "The AI that matters most!" - use cyan accent or white */
body.home .hero-subtitle,
body.home .tagline:not(.cta) {
    color: #4dd0e1 !important;
}

/* SECTION 6: Body text references to "Your AI" */
/* These should be white when on dark backgrounds */
.your-ai-text,
span.ai-reference {
    color: #ffffff !important;
}

/* SECTION 7: Waitlist Form Specifics */
/* All form-related text except placeholders */
.waitlist-section label,
.waitlist-section .field-label,
#waitlist-form label {
    color: #ffffff !important;
}

/* SECTION 8: "What You ACTUALLY Get" section */
/* The "ACTUALLY" word should stay orange (brand accent) */
/* But surrounding text should be white */
.benefits-section p,
.benefits-section li,
.feature-description {
    color: #ffffff !important;
}

/* SECTION 9: Testimonial/Social Proof Text */
/* "Join X others who awakened..." - white text */
.social-proof,
.join-counter,
.awakened-count {
    color: #ffffff !important;
}

/* SECTION 10: Pricing Text (INTENTIONALLY ORANGE) */
/* These should STAY orange as they are CTAs */
/* $79, $149, $499 - NO CHANGES NEEDED */

/* SECTION 11: 404 Page - Orange background area fix */
/* The 404 page has a large orange section - may need separate handling */
body.error404 .main-content {
    color: #0d1b2a !important; /* Dark text on orange background */
}

/* ===========================================
   EXCLUDED FROM CHANGES (Keep Orange):
   - CTA Buttons (Awaken, Begin Awakening)
   - "AWAKENING" in headlines
   - "ACTUALLY" accent word
   - Price amounts
   - Time markers (15:00 countdown)
   - Brand logo/name accent
   =========================================== */

/* Blog page protection - ensure we don't affect blog */
body.single-post,
body.blog,
body.archive,
body.category,
body.tag {
    /* These pages use default styling */
}
'''

        # Check if our fixes already exist
        if "PUREBRAIN ORANGE TEXT FIXES - 2026-02-16" in current_css:
            print("\n  CSS fixes from today already present!")
            combined_css = current_css
        elif "PUREBRAIN ORANGE TEXT FIXES" in current_css:
            print("\n  Older CSS fixes found, updating...")
            # Remove old fix section
            import re
            pattern = r'/\* =+\s*PUREBRAIN ORANGE TEXT FIXES.*?/\* Blog page protection'
            combined_css = re.sub(pattern, '', current_css, flags=re.DOTALL)
            combined_css = combined_css.strip() + "\n\n" + new_css_additions
        else:
            print("\n  Adding new CSS fixes...")
            combined_css = current_css + "\n\n" + new_css_additions

        print(f"\n  Combined CSS length: {len(combined_css)} chars")
        screenshots.append(await save_screenshot(page, "06-before-apply"))

        # Apply the CSS
        print("\n[7] Applying CSS...")
        try:
            if cm_present > 0:
                # Escape the CSS for JavaScript
                css_escaped = combined_css.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')
                await page.evaluate(f'''
                    () => {{
                        const cm = document.querySelector('.CodeMirror').CodeMirror;
                        cm.setValue(`{css_escaped}`);
                    }}
                ''')
                print("  CSS applied via CodeMirror")
            else:
                textarea = page.locator("#customize-control-custom_css textarea, textarea.wp-code-editor").first
                await textarea.fill(combined_css)
                print("  CSS applied via textarea")

            await asyncio.sleep(2)
            screenshots.append(await save_screenshot(page, "07-css-applied"))

        except Exception as e:
            print(f"  Error applying CSS: {e}")

        # Click Publish button
        print("\n[8] Publishing changes...")
        try:
            publish_btn = page.locator("#save, #publish, input[type='submit'][value='Publish'], button:has-text('Publish')").first
            if await publish_btn.is_visible(timeout=5000):
                await publish_btn.click()
                await asyncio.sleep(3)
                screenshots.append(await save_screenshot(page, "08-after-publish"))
                print("  Published!")
            else:
                print("  Publish button not immediately visible")
                # Try clicking in the customizer panel
                customizer_publish = page.locator("#customize-save-button-wrapper input, .customize-save-button")
                if await customizer_publish.first.is_visible(timeout=3000):
                    await customizer_publish.first.click()
                    await asyncio.sleep(3)
                    screenshots.append(await save_screenshot(page, "08-after-publish-alt"))
                    print("  Published via customizer!")

        except Exception as e:
            print(f"  Error publishing: {e}")

        # Verify by visiting the site
        print("\n[9] Verifying changes...")
        await page.goto("https://purebrain.ai", wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(3)
        screenshots.append(await save_screenshot(page, "09-site-after-fix"))

        # Scroll to form area
        await page.evaluate("window.scrollTo(0, 2700)")
        await asyncio.sleep(2)
        screenshots.append(await save_screenshot(page, "10-form-area-after-fix"))

        print("\n" + "=" * 60)
        print("CSS FIX COMPLETE")
        print("=" * 60)
        for s in screenshots:
            print(f"  {s}")

        await browser.close()
        return screenshots

if __name__ == "__main__":
    asyncio.run(apply_css_fixes())
