#!/usr/bin/env python3
"""
Dump the customizer structure to understand footer social inputs.
"""

import asyncio
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

# Configuration
WP_ADMIN_URL = "https://purebrain.ai/wp-admin"
WP_USERNAME = "Aether"
WP_PASSWORD = "b&JJRfs)6yuSWJCc7WiFY)G8"

SCREENSHOT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/wp-dump")
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

        # Login
        print("[NAV] Going to WordPress login...")
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

        print(f"[INFO] Logged in")

        # Go to Customizer Footer Options
        print("[NAV] Opening Customizer Footer Options...")
        customizer_url = f"{WP_ADMIN_URL}/customize.php?autofocus[section]=footer_options"
        await page.goto(customizer_url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(10000)  # Wait longer for customizer

        # Take screenshot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = str(SCREENSHOT_DIR / f"{timestamp}_customizer.png")
        await page.screenshot(path=path)
        print(f"[SCREENSHOT] {path}")

        # Dump all setting-link inputs (the key customizer identifiers)
        print("\n[DEBUG] All customize-setting-link inputs:")
        inputs_info = await page.evaluate("""
            () => {
                return Array.from(document.querySelectorAll('[data-customize-setting-link]')).map(el => ({
                    tag: el.tagName,
                    type: el.type || el.tagName,
                    settingLink: el.getAttribute('data-customize-setting-link'),
                    value: el.value?.substring(0, 100) || el.textContent?.substring(0, 100) || '',
                    id: el.id
                }));
            }
        """)

        for inp in inputs_info:
            print(f"  - {inp['settingLink']}: {inp['value'][:60]}... (tag={inp['tag']}, type={inp['type']})")

        # Look for anything containing these social keywords in the whole page
        print("\n[DEBUG] Searching page for social URLs...")
        social_content = await page.evaluate("""
            () => {
                const html = document.body.innerHTML;
                const patterns = [
                    /linkedin[^"'\\s]*/gi,
                    /facebook[^"'\\s]*/gi,
                    /instagram[^"'\\s]*/gi,
                    /x\\.com[^"'\\s]*/gi,
                    /twitter[^"'\\s]*/gi
                ];
                let found = [];
                patterns.forEach(pattern => {
                    const matches = html.match(pattern);
                    if (matches) found = found.concat(matches.slice(0, 3));
                });
                return [...new Set(found)];
            }
        """)
        print(f"  Found patterns: {social_content}")

        # Get the footer_options section controls
        print("\n[DEBUG] Footer options section controls:")
        footer_controls = await page.evaluate("""
            () => {
                const section = document.querySelector('#sub-accordion-section-footer_options');
                if (!section) return ['Section not found'];
                const controls = section.querySelectorAll('.customize-control');
                return Array.from(controls).map(ctrl => {
                    const label = ctrl.querySelector('.customize-control-title, label');
                    const input = ctrl.querySelector('input, textarea, select');
                    return {
                        id: ctrl.id,
                        label: label?.textContent?.trim() || 'no label',
                        inputType: input?.type || input?.tagName || 'no input',
                        inputId: input?.id || 'no id',
                        settingLink: input?.getAttribute('data-customize-setting-link') || 'no setting',
                        value: input?.value?.substring(0, 80) || ''
                    };
                });
            }
        """)

        for ctrl in footer_controls:
            if isinstance(ctrl, str):
                print(f"  {ctrl}")
            else:
                print(f"\n  Control: {ctrl['id']}")
                print(f"    Label: {ctrl['label']}")
                print(f"    Input: {ctrl['inputType']} (id={ctrl['inputId']})")
                print(f"    Setting: {ctrl['settingLink']}")
                print(f"    Value: {ctrl['value']}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
