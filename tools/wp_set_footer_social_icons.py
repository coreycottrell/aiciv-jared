#!/usr/bin/env python3
"""
Set social media icons in the Artistics theme Footer Options via WordPress Customizer.

Social links to set:
- LinkedIn: https://www.linkedin.com/company/purebrain-ai/
- Facebook: https://www.facebook.com/PureBrainAI/
- X/Twitter: https://x.com/PureBrainAI
- Instagram: https://www.instagram.com/purebrain.ai/
"""

import asyncio
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

# Configuration
WP_ADMIN_URL = "https://purebrain.ai/wp-admin"
WP_USERNAME = "Aether"
WP_PASSWORD = "b&JJRfs)6yuSWJCc7WiFY)G8"

SOCIAL_LINKS = {
    "linkedin": "https://www.linkedin.com/company/purebrain-ai/",
    "facebook": "https://www.facebook.com/PureBrainAI/",
    "twitter": "https://x.com/PureBrainAI",  # X/Twitter
    "instagram": "https://www.instagram.com/purebrain.ai/",
}

SCREENSHOT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/wp-set-footer-social")
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

        print(f"[INFO] Logged in, current URL: {page.url}")

        # Go to Customizer with Footer Options focused
        print("[NAV] Opening Customizer Footer Options...")
        customizer_url = f"{WP_ADMIN_URL}/customize.php?autofocus[section]=footer_options"
        await page.goto(customizer_url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(5000)

        path = screenshot_path("01_customizer_footer_options")
        await page.screenshot(path=path)
        print(f"[SCREENSHOT] {path}")

        # Check if Footer Options section is open
        footer_section = await page.query_selector("#accordion-section-footer_options.open, #sub-accordion-section-footer_options.open")
        if not footer_section:
            print("[INFO] Footer Options not open, clicking to expand...")
            section_btn = await page.query_selector("#accordion-section-footer_options")
            if section_btn:
                await section_btn.click()
                await page.wait_for_timeout(2000)

        path = screenshot_path("02_footer_section_expanded")
        await page.screenshot(path=path)
        print(f"[SCREENSHOT] {path}")

        # Find and fill social URL fields
        # Look for input fields with social media related names/ids
        print("\n[FILL] Looking for social URL input fields...")

        # Get all visible input fields in the customizer
        inputs = await page.query_selector_all("#customize-controls input[type='text'], #customize-controls input[type='url']")
        print(f"[INFO] Found {len(inputs)} text/url inputs in customizer")

        # List all inputs to understand the structure
        for inp in inputs:
            inp_id = await inp.get_attribute("id")
            inp_name = await inp.get_attribute("data-customize-setting-link")
            inp_value = await inp.input_value()
            placeholder = await inp.get_attribute("placeholder")
            if inp_id or inp_name:
                print(f"  - ID: {inp_id}, Setting: {inp_name}, Value: '{inp_value[:50] if inp_value else ''}...', Placeholder: {placeholder}")

        # Try to find specific social input fields
        social_inputs = {
            "linkedin": None,
            "facebook": None,
            "twitter": None,
            "instagram": None,
        }

        # Look for inputs by various selectors
        for platform in social_inputs.keys():
            selectors = [
                f"input[id*='{platform}']",
                f"input[data-customize-setting-link*='{platform}']",
                f"input[placeholder*='{platform}' i]",
                f"input[aria-label*='{platform}' i]",
            ]
            for selector in selectors:
                inp = await page.query_selector(selector)
                if inp:
                    is_visible = await inp.is_visible()
                    if is_visible:
                        social_inputs[platform] = inp
                        print(f"[FOUND] {platform} input: {selector}")
                        break

        # Fill in the social URLs
        print("\n[FILL] Setting social URLs...")
        for platform, url in SOCIAL_LINKS.items():
            inp = social_inputs.get(platform)
            if inp:
                current_value = await inp.input_value()
                print(f"  {platform}: current='{current_value}', new='{url}'")

                # Clear and fill
                await inp.fill("")
                await inp.fill(url)
                await page.wait_for_timeout(500)
            else:
                print(f"  {platform}: INPUT NOT FOUND - trying alternative approaches...")

        path = screenshot_path("03_after_filling_social")
        await page.screenshot(path=path)
        print(f"[SCREENSHOT] {path}")

        # If some inputs weren't found, try scrolling within the section
        print("\n[SCROLL] Scrolling to reveal all fields...")
        section_content = await page.query_selector("#sub-accordion-section-footer_options .accordion-section-content, #accordion-section-footer_options .customize-control")
        if section_content:
            await page.evaluate("document.querySelector('#sub-accordion-section-footer_options .accordion-section-content, #accordion-section-footer_options .customize-control')?.scrollIntoView()")

        await page.wait_for_timeout(1000)
        path = screenshot_path("04_after_scroll")
        await page.screenshot(path=path)
        print(f"[SCREENSHOT] {path}")

        # Try filling by label text
        print("\n[FILL] Trying to fill by label text...")
        labels = await page.query_selector_all("#customize-controls label, #customize-controls .customize-control-title")
        for label in labels:
            label_text = await label.inner_text()
            label_text_lower = label_text.lower()

            # Check if this label is for a social field
            for platform, url in SOCIAL_LINKS.items():
                if platform in label_text_lower:
                    # Find the associated input
                    parent = await label.evaluate_handle("el => el.closest('.customize-control')")
                    if parent:
                        inp = await parent.query_selector("input")
                        if inp:
                            current_value = await inp.input_value()
                            print(f"  Found {platform} via label: current='{current_value}'")
                            if not current_value or current_value != url:
                                await inp.fill("")
                                await inp.fill(url)
                                print(f"  Set {platform} = {url}")

        await page.wait_for_timeout(1000)
        path = screenshot_path("05_final_state")
        await page.screenshot(path=path)
        print(f"[SCREENSHOT] {path}")

        # Click Publish/Save button
        print("\n[SAVE] Looking for Publish button...")
        publish_btn = await page.query_selector("#save, input[value='Publish'], button:has-text('Publish')")
        if publish_btn:
            is_disabled = await publish_btn.is_disabled()
            if not is_disabled:
                print("[SAVE] Clicking Publish...")
                await publish_btn.click()
                await page.wait_for_timeout(5000)

                path = screenshot_path("06_after_publish")
                await page.screenshot(path=path)
                print(f"[SCREENSHOT] {path}")
                print("[SUCCESS] Changes published!")
            else:
                print("[INFO] Publish button is disabled - no changes to save or need to make changes first")
        else:
            print("[WARN] Publish button not found")

        # Verify on the live site
        print("\n[VERIFY] Checking live site footer...")
        await page.goto("https://purebrain.ai/", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(3000)

        # Scroll to footer
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(1000)

        path = screenshot_path("07_live_footer")
        await page.screenshot(path=path)
        print(f"[SCREENSHOT] {path}")

        # Check for social icons
        social_elements = await page.query_selector_all("a[href*='linkedin.com'], a[href*='facebook.com'], a[href*='x.com'], a[href*='twitter.com'], a[href*='instagram.com']")
        print(f"\n[VERIFY] Found {len(social_elements)} social links on live site")
        for elem in social_elements:
            href = await elem.get_attribute("href")
            print(f"  - {href}")

        await browser.close()

        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"Screenshots saved to: {SCREENSHOT_DIR}")
        print("\nSocial links to set:")
        for platform, url in SOCIAL_LINKS.items():
            print(f"  {platform}: {url}")


if __name__ == "__main__":
    asyncio.run(main())
