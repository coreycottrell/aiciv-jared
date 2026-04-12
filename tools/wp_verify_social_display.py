#!/usr/bin/env python3
"""
Verify that social icons are actually displayed in the footer.
Check what the theme's social_urls setting produces on the live site.
"""

import asyncio
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

# Configuration
WP_ADMIN_URL = "https://purebrain.ai/wp-admin"
WP_USERNAME = "Aether"
WP_PASSWORD = "b&JJRfs)6yuSWJCc7WiFY)G8"

SCREENSHOT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/wp-verify-social")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


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

        # First check the live site WITHOUT logging in (public view)
        print("[NAV] Checking live site footer (public view)...")
        await page.goto("https://purebrain.ai/", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(5000)

        # Scroll to footer
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(2000)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = str(SCREENSHOT_DIR / f"{timestamp}_01_live_footer_public.png")
        await page.screenshot(path=path, full_page=False)
        print(f"[SCREENSHOT] {path}")

        # Get the full footer HTML
        print("\n[DEBUG] Extracting footer HTML...")
        footer_html = await page.evaluate("""
            () => {
                const footer = document.querySelector('footer, #footer, .footer, #et-footer, .site-footer');
                return footer ? footer.outerHTML : 'No footer found';
            }
        """)
        print(f"\n[FOOTER HTML]\n{footer_html}")

        # Check for any social icon elements
        print("\n[DEBUG] Checking for social icon elements...")
        social_elements = await page.evaluate("""
            () => {
                // Look for social icons by various patterns
                const selectors = [
                    '.social-icon', '.social-icons', '.social-links',
                    'a[href*="facebook.com"]', 'a[href*="linkedin.com"]',
                    'a[href*="twitter.com"]', 'a[href*="x.com"]',
                    'a[href*="instagram.com"]', 'a[href*="youtube.com"]',
                    '[class*="social"]', '[class*="fa-facebook"]', '[class*="fa-linkedin"]',
                    '[class*="fa-twitter"]', '[class*="fa-instagram"]'
                ];
                let found = [];
                selectors.forEach(sel => {
                    const els = document.querySelectorAll(sel);
                    els.forEach(el => {
                        // Check if it's in the footer area (bottom of page)
                        const rect = el.getBoundingClientRect();
                        const isInFooter = rect.top > window.innerHeight * 0.7;
                        found.push({
                            selector: sel,
                            tag: el.tagName,
                            href: el.href || el.getAttribute('href') || '',
                            class: el.className,
                            text: el.textContent?.trim().substring(0, 30) || '',
                            inFooter: isInFooter
                        });
                    });
                });
                return found;
            }
        """)

        print(f"\n[FOUND] {len(social_elements)} potential social elements:")
        footer_social = [e for e in social_elements if e.get('inFooter')]
        for elem in social_elements[:20]:  # Limit output
            location = "[FOOTER]" if elem.get('inFooter') else "[PAGE]"
            print(f"  {location} {elem['tag']}: href={elem['href'][:50] if elem['href'] else 'none'}... class={elem['class'][:30] if elem['class'] else 'none'}")

        # Now check the Theme Customizer to see the stored social URLs
        print("\n[NAV] Logging in to check Customizer settings...")
        await page.goto(f"{WP_ADMIN_URL}", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(2000)

        # Handle GoDaddy SSO
        username_link = await page.query_selector("a:has-text('Log in with username and password')")
        if username_link:
            await username_link.click()
            await page.wait_for_timeout(2000)

        # Fill login form
        await page.wait_for_selector("#user_login", state="visible", timeout=10000)
        await page.fill("#user_login", WP_USERNAME)
        await page.fill("#user_pass", WP_PASSWORD)
        await page.click("#wp-submit")
        await page.wait_for_timeout(5000)

        # Go to Customizer
        print("[NAV] Opening Customizer Footer Options...")
        customizer_url = f"{WP_ADMIN_URL}/customize.php?autofocus[section]=footer_options"
        await page.goto(customizer_url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(8000)

        path = str(SCREENSHOT_DIR / f"{timestamp}_02_customizer.png")
        await page.screenshot(path=path)
        print(f"[SCREENSHOT] {path}")

        # Get the full social_urls value
        social_urls_value = await page.evaluate("""
            () => {
                const input = document.querySelector('input[data-customize-setting-link="social_urls"], #social_urls');
                return input ? input.value : 'Not found';
            }
        """)
        print(f"\n[SOCIAL URLS SETTING] {social_urls_value}")

        # Get all visible social URL text inputs
        print("\n[DEBUG] Visible social URL input fields:")
        social_inputs = await page.evaluate("""
            () => {
                const section = document.querySelector('#sub-accordion-section-footer_options');
                if (!section) return ['Section not found'];

                // Get all text inputs in the section
                const inputs = section.querySelectorAll('input[type="text"], input[type="url"]');
                return Array.from(inputs).map(inp => ({
                    id: inp.id,
                    name: inp.name,
                    value: inp.value,
                    placeholder: inp.placeholder,
                    className: inp.className,
                    dataIndex: inp.getAttribute('data-index')
                }));
            }
        """)

        for inp in social_inputs:
            if isinstance(inp, dict):
                print(f"  - {inp['id'] or inp['name'] or 'no-id'}: '{inp['value']}' (placeholder: {inp['placeholder']})")

        # Check the theme file editor for footer.php
        print("\n[NAV] Checking theme's footer.php for social icon implementation...")
        await page.goto(f"{WP_ADMIN_URL}/theme-editor.php?file=footer.php", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(3000)

        path = str(SCREENSHOT_DIR / f"{timestamp}_03_footer_php.png")
        await page.screenshot(path=path, full_page=True)
        print(f"[SCREENSHOT] {path}")

        # Get footer.php content
        footer_php = await page.evaluate("""
            () => {
                const textarea = document.querySelector('#newcontent, textarea[name="newcontent"]');
                return textarea ? textarea.value : 'Not found';
            }
        """)

        if footer_php and footer_php != 'Not found':
            # Look for social-related code in footer.php
            if 'social' in footer_php.lower():
                print("\n[FOUND] Social-related code in footer.php:")
                # Extract relevant lines
                lines = footer_php.split('\n')
                for i, line in enumerate(lines):
                    if 'social' in line.lower():
                        print(f"  Line {i+1}: {line.strip()[:100]}")
            else:
                print("\n[INFO] No 'social' keyword found in footer.php")
                print(f"\n[FOOTER.PHP PREVIEW]\n{footer_php[:2000]}")

        await browser.close()

        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"\nScreenshots saved to: {SCREENSHOT_DIR}")
        print(f"\nCurrent social_urls setting: {social_urls_value}")
        print(f"\nSocial elements found in footer: {len(footer_social)}")


if __name__ == "__main__":
    asyncio.run(main())
