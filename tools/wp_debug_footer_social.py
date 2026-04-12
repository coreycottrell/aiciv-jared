#!/usr/bin/env python3
"""
Debug script to understand the Footer Options customizer fields structure.
"""

import asyncio
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

# Configuration
WP_ADMIN_URL = "https://purebrain.ai/wp-admin"
WP_USERNAME = "Aether"
WP_PASSWORD = "b&JJRfs)6yuSWJCc7WiFY)G8"

SCREENSHOT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/wp-debug-footer")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

def screenshot_path(name: str) -> str:
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
        print("[NAV] Going to WordPress login...")
        await page.goto(f"{WP_ADMIN_URL}", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(2000)

        # Handle GoDaddy SSO
        username_link = await page.query_selector("a:has-text('Log in with username and password')")
        if username_link:
            print("[LOGIN] GoDaddy SSO detected - clicking username/password link...")
            await username_link.click()
            await page.wait_for_timeout(2000)

        # Fill login form
        print("[LOGIN] Entering credentials...")
        await page.wait_for_selector("#user_login", state="visible", timeout=10000)
        await page.fill("#user_login", WP_USERNAME)
        await page.fill("#user_pass", WP_PASSWORD)
        await page.click("#wp-submit")
        await page.wait_for_timeout(5000)

        # Go to Customizer Footer Options
        print("[NAV] Opening Customizer Footer Options...")
        customizer_url = f"{WP_ADMIN_URL}/customize.php?autofocus[section]=footer_options"
        await page.goto(customizer_url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(8000)  # Wait longer for customizer to fully load

        # Click on Footer Options section to make sure it's open
        footer_section = await page.query_selector("#accordion-section-footer_options")
        if footer_section:
            await footer_section.click()
            await page.wait_for_timeout(2000)

        path = screenshot_path("01_footer_options")
        await page.screenshot(path=path)
        print(f"[SCREENSHOT] {path}")

        # Get the HTML of the footer_options section
        print("\n[DEBUG] Getting Footer Options section HTML...")
        footer_html = await page.evaluate("""
            () => {
                const section = document.querySelector('#sub-accordion-section-footer_options, #accordion-section-footer_options');
                return section ? section.innerHTML : 'Section not found';
            }
        """)
        print(f"\n[FOOTER SECTION HTML]\n{footer_html[:5000]}")

        # Find ALL inputs and textareas in the customizer
        print("\n[DEBUG] Finding ALL inputs in customizer panel...")
        all_inputs_info = await page.evaluate("""
            () => {
                const inputs = document.querySelectorAll('#customize-controls input, #customize-controls textarea');
                return Array.from(inputs).map(inp => ({
                    tagName: inp.tagName,
                    type: inp.type,
                    id: inp.id,
                    name: inp.name,
                    className: inp.className,
                    value: inp.value?.substring(0, 100) || '',
                    dataSettingLink: inp.getAttribute('data-customize-setting-link'),
                    placeholder: inp.placeholder,
                    parentClasses: inp.closest('.customize-control')?.className || '',
                    parentId: inp.closest('.customize-control')?.id || '',
                    isVisible: inp.offsetParent !== null
                }));
            }
        """)

        print(f"\n[DEBUG] Found {len(all_inputs_info)} total inputs")
        for inp in all_inputs_info:
            if inp['isVisible'] and inp['type'] not in ['hidden', 'checkbox', 'radio', 'file']:
                print(f"\n  Input: {inp['tagName']} type={inp['type']}")
                print(f"    ID: {inp['id']}")
                print(f"    Name: {inp['name']}")
                print(f"    Setting: {inp['dataSettingLink']}")
                print(f"    Value: {inp['value'][:50]}...")
                print(f"    Parent: {inp['parentId']} ({inp['parentClasses'][:50]})")

        # Look specifically for URL-containing inputs
        print("\n[DEBUG] Looking for URL fields...")
        url_inputs = await page.evaluate("""
            () => {
                const inputs = document.querySelectorAll('input[value*="linkedin"], input[value*="facebook"], input[value*="twitter"], input[value*="instagram"], input[value*="x.com"]');
                return Array.from(inputs).map(inp => ({
                    id: inp.id,
                    value: inp.value,
                    settingLink: inp.getAttribute('data-customize-setting-link'),
                    parentId: inp.closest('.customize-control')?.id || 'no-parent'
                }));
            }
        """)
        print(f"\n[DEBUG] Found {len(url_inputs)} URL-containing inputs")
        for inp in url_inputs:
            print(f"  - ID: {inp['id']}, Value: {inp['value']}, Setting: {inp['settingLink']}")

        # Also look for inputs with social in their attributes
        print("\n[DEBUG] Looking for inputs with 'social' in attributes...")
        social_inputs = await page.evaluate("""
            () => {
                const allInputs = document.querySelectorAll('#customize-controls input[type="text"], #customize-controls input[type="url"]');
                return Array.from(allInputs).filter(inp => {
                    const settingLink = inp.getAttribute('data-customize-setting-link') || '';
                    const parentId = inp.closest('.customize-control')?.id || '';
                    return settingLink.toLowerCase().includes('social') ||
                           settingLink.toLowerCase().includes('footer') ||
                           parentId.toLowerCase().includes('social') ||
                           parentId.toLowerCase().includes('footer');
                }).map(inp => ({
                    id: inp.id,
                    value: inp.value,
                    settingLink: inp.getAttribute('data-customize-setting-link'),
                    parentId: inp.closest('.customize-control')?.id || 'no-parent'
                }));
            }
        """)
        print(f"\n[DEBUG] Found {len(social_inputs)} social/footer related inputs")
        for inp in social_inputs:
            print(f"  - ID: {inp['id']}, Setting: {inp['settingLink']}, Value: {inp['value'][:50]}...")

        await browser.close()

        print("\n" + "="*60)
        print("Debug complete. Review output above.")
        print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
