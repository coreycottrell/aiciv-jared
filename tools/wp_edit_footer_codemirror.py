#!/usr/bin/env python3
"""
Edit the footer HTML widget using CodeMirror API.

The Elementor HTML editor uses CodeMirror which requires special handling.
"""

import asyncio
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

# Configuration
WP_ADMIN_URL = "https://purebrain.ai/wp-admin"
WP_USERNAME = "Aether"
WP_PASSWORD = "b&JJRfs)6yuSWJCc7WiFY)G8"
HOMEPAGE_ID = "11"

# Social icons HTML to add
SOCIAL_ICONS_HTML = '''
<!-- Social Media Icons -->
<div class="footer-social-icons" style="display: flex; gap: 20px; justify-content: center; margin-top: 20px; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.2);">
    <a href="https://www.linkedin.com/company/purebrain-ai/" target="_blank" title="LinkedIn" style="color: #fff; font-size: 24px;">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 24 24"><path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/></svg>
    </a>
    <a href="https://www.facebook.com/PureBrainAI/" target="_blank" title="Facebook" style="color: #fff; font-size: 24px;">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 24 24"><path d="M9 8h-3v4h3v12h5v-12h3.642l.358-4h-4v-1.667c0-.955.192-1.333 1.115-1.333h2.885v-5h-3.808c-3.596 0-5.192 1.583-5.192 4.615v3.385z"/></svg>
    </a>
    <a href="https://x.com/PureBrainAI" target="_blank" title="X/Twitter" style="color: #fff; font-size: 24px;">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
    </a>
    <a href="https://www.instagram.com/purebrain.ai/" target="_blank" title="Instagram" style="color: #fff; font-size: 24px;">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>
    </a>
</div>
'''

SCREENSHOT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/wp-codemirror-edit")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def ss(name):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return str(SCREENSHOT_DIR / f"{timestamp}_{name}.png")


async def main():
    async with async_playwright() as p:
        print("[INIT] Launching browser...")
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )

        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()

        # Login
        print("[NAV] Logging in...")
        await page.goto(f"{WP_ADMIN_URL}", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(2000)

        username_link = await page.query_selector("a:has-text('Log in with username and password')")
        if username_link:
            await username_link.click()
            await page.wait_for_timeout(2000)

        await page.wait_for_selector("#user_login", state="visible", timeout=10000)
        await page.fill("#user_login", WP_USERNAME)
        await page.fill("#user_pass", WP_PASSWORD)
        await page.click("#wp-submit")
        await page.wait_for_timeout(5000)

        print(f"[INFO] Logged in")

        # Open Elementor editor
        print("[NAV] Opening Elementor editor...")
        elementor_url = f"https://purebrain.ai/?p={HOMEPAGE_ID}&elementor"
        await page.goto(elementor_url, wait_until="domcontentloaded", timeout=120000)
        await page.wait_for_timeout(15000)

        # Close any popups
        for _ in range(3):
            try:
                skip = await page.query_selector("button:has-text('Skip'), .dialog-close-button, [aria-label='Close']")
                if skip:
                    await skip.click(timeout=2000)
                    await page.wait_for_timeout(500)
            except:
                pass

        await page.screenshot(path=ss("01_elementor_loaded"))
        print(f"[SCREENSHOT] Elementor loaded")

        # Scroll to footer
        print("[ACTION] Scrolling to footer...")
        try:
            await page.evaluate("""
                () => {
                    const iframe = document.getElementById('elementor-preview-iframe');
                    if (iframe && iframe.contentWindow) {
                        iframe.contentWindow.scrollTo(0, iframe.contentDocument.body.scrollHeight);
                    }
                }
            """)
            await page.wait_for_timeout(2000)
        except:
            pass

        # Click on footer
        print("[ACTION] Clicking on footer...")
        preview_frame = page.frame_locator("#elementor-preview-iframe")

        try:
            footer = preview_frame.locator("footer, .footer").first
            await footer.click()
            await page.wait_for_timeout(3000)
            print("[SUCCESS] Clicked on footer!")
        except Exception as e:
            print(f"[WARN] Could not click footer: {e}")

        await page.screenshot(path=ss("02_footer_clicked"))
        print(f"[SCREENSHOT] Footer clicked")

        # Get the current HTML using CodeMirror API
        print("[ACTION] Getting current HTML via CodeMirror...")

        current_html = await page.evaluate("""
            () => {
                // Try to find CodeMirror instance
                const cmElements = document.querySelectorAll('.CodeMirror');
                for (const cmEl of cmElements) {
                    if (cmEl.CodeMirror) {
                        return cmEl.CodeMirror.getValue();
                    }
                }
                // Try Elementor's control system
                const htmlControl = document.querySelector('.elementor-control-html');
                if (htmlControl) {
                    const textarea = htmlControl.querySelector('textarea');
                    if (textarea) return textarea.value;
                }
                return null;
            }
        """)

        print(f"\n[CURRENT HTML] ({len(current_html) if current_html else 0} chars)")
        if current_html:
            print(current_html[:2000])

        # Check if social icons already exist
        if current_html and 'footer-social-icons' in current_html:
            print("\n[INFO] Social icons already present in footer HTML!")
            await browser.close()
            return

        # Create new HTML with social icons
        if current_html:
            if '</footer>' in current_html:
                new_html = current_html.replace('</footer>', f'{SOCIAL_ICONS_HTML}\n</footer>')
            elif '</div>' in current_html:
                # Insert before last closing div
                last_div_pos = current_html.rfind('</div>')
                new_html = current_html[:last_div_pos] + SOCIAL_ICONS_HTML + '\n' + current_html[last_div_pos:]
            else:
                new_html = current_html + SOCIAL_ICONS_HTML
        else:
            new_html = SOCIAL_ICONS_HTML

        # Set new HTML using CodeMirror API
        print("\n[ACTION] Setting new HTML via CodeMirror...")

        # Escape the HTML for JavaScript
        escaped_html = new_html.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')

        result = await page.evaluate(f"""
            () => {{
                // Try CodeMirror first
                const cmElements = document.querySelectorAll('.CodeMirror');
                for (const cmEl of cmElements) {{
                    if (cmEl.CodeMirror) {{
                        cmEl.CodeMirror.setValue(`{escaped_html}`);
                        cmEl.CodeMirror.refresh();
                        return 'CodeMirror updated';
                    }}
                }}

                // Try direct textarea
                const htmlControl = document.querySelector('.elementor-control-html');
                if (htmlControl) {{
                    const textarea = htmlControl.querySelector('textarea');
                    if (textarea) {{
                        textarea.value = `{escaped_html}`;
                        textarea.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        textarea.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        return 'Textarea updated';
                    }}
                }}
                return 'No editor found';
            }}
        """)

        print(f"[RESULT] {result}")

        await page.wait_for_timeout(3000)
        await page.screenshot(path=ss("03_html_updated"))
        print(f"[SCREENSHOT] HTML updated")

        # Trigger Elementor to recognize the change
        print("[ACTION] Triggering Elementor update...")

        await page.evaluate("""
            () => {
                // Try to trigger Elementor's change detection
                const event = new Event('input', { bubbles: true });
                document.querySelectorAll('.elementor-control-html textarea, .CodeMirror').forEach(el => {
                    el.dispatchEvent(event);
                });

                // Try Elementor's internal API
                if (window.elementor && window.elementor.channels) {
                    try {
                        window.elementor.channels.editor.trigger('change');
                    } catch(e) {}
                }
            }
        """)

        await page.wait_for_timeout(2000)

        # Click Update/Publish button
        print("\n[ACTION] Publishing changes...")

        publish_btn = await page.query_selector("#elementor-panel-saver-button-publish, button:has-text('Publish'), button:has-text('Update')")
        if publish_btn:
            is_visible = await publish_btn.is_visible()
            is_disabled = await publish_btn.is_disabled()
            print(f"[INFO] Publish button: visible={is_visible}, disabled={is_disabled}")

            if is_visible and not is_disabled:
                await publish_btn.click()
                await page.wait_for_timeout(5000)
                print("[SUCCESS] Clicked Publish!")

                await page.screenshot(path=ss("04_published"))
                print(f"[SCREENSHOT] Published")
            else:
                print("[WARN] Publish button not clickable")
        else:
            print("[WARN] Publish button not found")

        # Verify changes on live site
        print("\n[VERIFY] Checking live site footer...")
        await page.goto("https://purebrain.ai/", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(3000)

        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(2000)

        await page.screenshot(path=ss("05_live_footer"))
        print(f"[SCREENSHOT] Live footer")

        # Check for social icons
        footer_html = await page.evaluate("""
            () => {
                const footer = document.querySelector('footer, .footer');
                return footer ? footer.innerHTML : 'No footer';
            }
        """)

        if 'footer-social-icons' in footer_html:
            print("\n[SUCCESS] Social icons are now visible in the footer!")
        else:
            print("\n[INFO] Social icons not yet visible - may need manual verification")

        # Count social links
        social_count = footer_html.count('linkedin.com') + footer_html.count('facebook.com') + \
                       footer_html.count('x.com') + footer_html.count('instagram.com')
        print(f"[INFO] Social links in footer: {social_count}")

        await browser.close()

        print("\n" + "="*60)
        print("COMPLETE")
        print("="*60)
        print(f"\nScreenshots saved to: {SCREENSHOT_DIR}")


if __name__ == "__main__":
    asyncio.run(main())
