#!/usr/bin/env python3
"""
Set social media URLs in WordPress Theme Customizer.
Navigate to Appearance > Customize > Footer Options > Social URLs

The theme uses a sortable_repeater control where each URL is a .repeater-input.
Current values: Instagram, Facebook, YouTube
Target values: Facebook, LinkedIn, Twitter/X, Instagram, YouTube
"""

import asyncio
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

WP_URL = "https://purebrain.ai/wp-admin"
WP_USERNAME = "Aether"
WP_PASSWORD = "b&JJRfs)6yuSWJCc7WiFY)G8"
SCREENSHOT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/wp-social-links")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

# Social URLs to set (in order)
SOCIAL_URLS = [
    "https://www.facebook.com/PureBrainAI/",
    "https://www.linkedin.com/company/purebrain-ai/",
    "https://x.com/PureBrainAI",
    "https://www.instagram.com/purebrain.ai/",
    "https://www.youtube.com/",  # Keep existing
]

def screenshot_path(name: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return str(SCREENSHOT_DIR / f"{timestamp}_{name}.png")

async def save_screenshot(page, name: str, full_page: bool = False):
    path = screenshot_path(name)
    await page.screenshot(path=path, full_page=full_page)
    print(f"[SCREENSHOT] {path}")
    return path

async def login(page):
    print("[NAV] Logging in...")
    await page.goto(WP_URL, wait_until="domcontentloaded", timeout=60000)
    await page.wait_for_timeout(3000)

    try:
        link = await page.query_selector("text='Log in with username and password'")
        if link:
            await link.click()
            await page.wait_for_timeout(2000)
    except:
        pass

    await page.wait_for_selector("#user_login", state="visible", timeout=10000)
    await page.fill("#user_login", WP_USERNAME)
    await page.fill("#user_pass", WP_PASSWORD)
    await page.click("#wp-submit")
    await page.wait_for_timeout(5000)
    print("[SUCCESS] Logged in")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )

        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()

        await login(page)

        # Go to Customizer Footer Options directly
        print("[NAV] Going to Theme Customizer > Footer Options...")
        await page.goto(f"{WP_URL}/customize.php?autofocus[section]=footer_options", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(10000)
        await save_screenshot(page, "01_footer_options_initial")

        # Find all existing repeater inputs (visible social URL fields)
        repeater_inputs = page.locator(".repeater-input")
        existing_count = await repeater_inputs.count()
        print(f"[INFO] Found {existing_count} existing social URL fields")

        # We need 5 fields total (Facebook, LinkedIn, Twitter, Instagram, YouTube)
        # Add more rows if needed
        add_button = page.locator("button.customize-control-sortable-repeater-add")

        while existing_count < len(SOCIAL_URLS):
            print(f"[ACTION] Adding new row (current: {existing_count}, need: {len(SOCIAL_URLS)})")
            await add_button.click()
            await page.wait_for_timeout(500)
            existing_count = await repeater_inputs.count()

        print(f"[INFO] Now have {existing_count} fields")
        await save_screenshot(page, "02_after_adding_rows")

        # Clear and fill each field with our URLs
        for i, url in enumerate(SOCIAL_URLS):
            if i < existing_count:
                field = repeater_inputs.nth(i)
                await field.clear()
                await field.fill(url)
                print(f"[SET] Field {i+1}: {url}")
            else:
                print(f"[WARN] Not enough fields for URL {i+1}: {url}")

        await page.wait_for_timeout(1000)
        await save_screenshot(page, "03_after_filling_urls")

        # Trigger change event on the hidden input to sync with customizer
        hidden_input = page.locator("#social_urls")
        if await hidden_input.count() > 0:
            # Get all repeater values and join them
            all_values = []
            for i in range(await repeater_inputs.count()):
                val = await repeater_inputs.nth(i).input_value()
                if val.strip():
                    all_values.append(val.strip())

            new_value = ",".join(all_values)
            print(f"[INFO] Setting hidden input value: {new_value}")

            # Set value via JavaScript to trigger proper events
            await page.evaluate(f"""
                const input = document.querySelector('#social_urls');
                if (input) {{
                    input.value = "{new_value}";
                    input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                }}
            """)
            await page.wait_for_timeout(1000)

        await save_screenshot(page, "04_before_publish")

        # Click Publish to save
        print("[NAV] Looking for Publish button...")
        publish_btn = page.locator("#save")
        if await publish_btn.count() > 0:
            # Check if button is enabled
            is_disabled = await publish_btn.is_disabled()
            if not is_disabled:
                await publish_btn.click()
                await page.wait_for_timeout(5000)
                await save_screenshot(page, "05_after_publish")
                print("[SUCCESS] Clicked Publish")
            else:
                print("[INFO] Publish button is disabled (no changes detected?)")
                # Try triggering a change on one of the fields
                first_input = repeater_inputs.first
                await first_input.press("End")
                await first_input.press("Space")
                await first_input.press("Backspace")
                await page.wait_for_timeout(1000)

                if not await publish_btn.is_disabled():
                    await publish_btn.click()
                    await page.wait_for_timeout(5000)
                    await save_screenshot(page, "05_after_publish_retry")
                    print("[SUCCESS] Clicked Publish (after triggering change)")
        else:
            print("[WARN] Publish button not found")

        # Verify the saved values
        await page.reload()
        await page.wait_for_timeout(5000)
        await save_screenshot(page, "06_after_reload")

        # Go to the frontend and take screenshot of footer
        print("[NAV] Going to frontend to verify footer...")
        await page.goto("https://purebrain.ai", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(5000)

        # Scroll to footer
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(2000)
        await save_screenshot(page, "07_footer_verification")

        # Get footer HTML to see social icons
        footer = await page.query_selector("footer, .footer, #footer")
        if footer:
            footer_html = await footer.inner_html()
            print(f"[DEBUG] Footer HTML snippet: {footer_html[:500]}...")

        await browser.close()
        print("[DONE]")

if __name__ == "__main__":
    asyncio.run(main())
