#!/usr/bin/env python3
"""
PureBrain.ai Footer Social Icons via Theme Footer Options
The Artistics theme has built-in social URL fields.

Usage:
    python3 tools/elementor_footer_social.py
"""

import asyncio
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

# Configuration
WP_URL = "https://purebrain.ai/wp-admin"
WP_USERNAME = "Aether"
WP_PASSWORD = "b&JJRfs)6yuSWJCc7WiFY)G8"
SCREENSHOT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/elementor-footer-edit")

# Social URLs to set
SOCIAL_URLS = {
    "linkedin": "https://www.linkedin.com/company/purebrain-ai/",
    "facebook": "https://www.facebook.com/PureBrainAI/",
    "twitter": "https://x.com/PureBrainAI",
    "instagram": "https://www.instagram.com/purebrain.ai/"
}

# Ensure screenshot directory exists
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

def screenshot_path(name: str) -> str:
    """Generate timestamped screenshot path."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return str(SCREENSHOT_DIR / f"v4_{timestamp}_{name}.png")

async def save_screenshot(page, name: str, full_page: bool = False):
    """Save a screenshot with logging."""
    path = screenshot_path(name)
    await page.screenshot(path=path, full_page=full_page)
    print(f"[SCREENSHOT] Saved: {path}")
    return path

async def safe_goto(page, url, wait_time=5000):
    """Navigate to URL with domcontentloaded and then wait."""
    print(f"[NAV] Going to: {url}")
    await page.goto(url, wait_until="domcontentloaded", timeout=60000)
    await page.wait_for_timeout(wait_time)

async def login_to_wordpress(page):
    """Login to WordPress admin."""
    print("\n=== PHASE 1: Login to WordPress ===")

    await safe_goto(page, WP_URL)

    # Check if already logged in
    if "wp-login.php" not in page.url:
        content = await page.content()
        if "wpbody" in content or "adminmenu" in content:
            print("[INFO] Already logged in")
            await save_screenshot(page, "01_already_logged_in")
            return True

    await save_screenshot(page, "01_login_page")

    # GoDaddy-hosted WordPress has a different login flow
    try:
        username_link = await page.query_selector("a:has-text('Log in with username and password')")
        if username_link:
            print("[INFO] Clicking 'Log in with username and password'")
            await username_link.click()
            await page.wait_for_timeout(2000)
            await save_screenshot(page, "01b_login_form_revealed")
    except Exception as e:
        print(f"[DEBUG] No GoDaddy login toggle found: {e}")

    try:
        await page.wait_for_selector("#user_login", state="visible", timeout=10000)
        await page.fill("#user_login", WP_USERNAME, timeout=10000)
        await page.fill("#user_pass", WP_PASSWORD, timeout=10000)
        await page.wait_for_timeout(500)
        await save_screenshot(page, "02_credentials_entered")

        await page.click("#wp-submit")
        await page.wait_for_timeout(5000)

        await save_screenshot(page, "03_dashboard_after_login")
        print("[SUCCESS] Logged into WordPress dashboard")
        return True
    except Exception as e:
        print(f"[ERROR] Login failed: {e}")
        await save_screenshot(page, "03_login_failed")
        return False

async def fill_footer_social_urls(page):
    """Fill social URLs in the theme's Footer Options."""
    print("\n=== PHASE 2: Fill Footer Social URLs ===")

    await safe_goto(page, f"{WP_URL}/customize.php")
    await page.wait_for_timeout(8000)
    await save_screenshot(page, "04_customizer_loaded")

    # Click on Footer Options
    try:
        await page.click("text=Footer Options")
        await page.wait_for_timeout(3000)
        await save_screenshot(page, "05_footer_options_opened")
        print("[SUCCESS] Opened Footer Options")
    except Exception as e:
        print(f"[ERROR] Could not open Footer Options: {e}")
        return False

    # Now find and fill the social URL fields
    # The theme has these fields visible in the panel
    try:
        # Scroll down in the panel to see all fields
        panel = await page.query_selector("#customize-controls, .customize-pane-child")
        if panel:
            await panel.evaluate("el => el.scrollTop = 200")
            await page.wait_for_timeout(1000)

        # Take a screenshot to see what we're working with
        await save_screenshot(page, "06_footer_panel_scrolled")

        # Find all text inputs in the footer options section
        inputs = await page.query_selector_all("#sub-accordion-section-artistics_footer_settings input[type='text'], .customize-control input[type='text'], input[type='url']")
        print(f"[DEBUG] Found {len(inputs)} input fields")

        # List all inputs with their current values
        for i, inp in enumerate(inputs):
            try:
                value = await inp.input_value()
                placeholder = await inp.get_attribute("placeholder")
                input_id = await inp.get_attribute("id")
                print(f"[DEBUG] Input #{i}: id={input_id}, value='{value[:50] if value else 'empty'}', placeholder='{placeholder}'")
            except:
                pass

        await save_screenshot(page, "07_inputs_found")

        # Try to find inputs by their labels or surrounding context
        # Look for inputs that contain "linkedin", "facebook", "twitter", "instagram"
        content = await page.content()

        # Check what social fields are available
        social_keywords = ["linkedin", "facebook", "twitter", "instagram", "youtube", "social"]
        for keyword in social_keywords:
            if keyword.lower() in content.lower():
                print(f"[INFO] Found '{keyword}' in page content")

        # Fill the URL fields based on their position or label
        # First, let's try filling by finding inputs near the social text labels

        filled_count = 0

        # LinkedIn
        linkedin_input = await page.query_selector("input[id*='linkedin'], input[placeholder*='linkedin' i], .customize-control:has-text('LinkedIn') input")
        if linkedin_input:
            await linkedin_input.fill(SOCIAL_URLS["linkedin"])
            print(f"[SUCCESS] Filled LinkedIn URL")
            filled_count += 1

        # Facebook
        facebook_input = await page.query_selector("input[id*='facebook'], input[placeholder*='facebook' i], .customize-control:has-text('Facebook') input")
        if facebook_input:
            await facebook_input.fill(SOCIAL_URLS["facebook"])
            print(f"[SUCCESS] Filled Facebook URL")
            filled_count += 1

        # Twitter/X
        twitter_input = await page.query_selector("input[id*='twitter'], input[id*='x_url'], input[placeholder*='twitter' i], input[placeholder*='x.com' i], .customize-control:has-text('Twitter') input")
        if twitter_input:
            await twitter_input.fill(SOCIAL_URLS["twitter"])
            print(f"[SUCCESS] Filled Twitter/X URL")
            filled_count += 1

        # Instagram
        instagram_input = await page.query_selector("input[id*='instagram'], input[placeholder*='instagram' i], .customize-control:has-text('Instagram') input")
        if instagram_input:
            await instagram_input.fill(SOCIAL_URLS["instagram"])
            print(f"[SUCCESS] Filled Instagram URL")
            filled_count += 1

        await save_screenshot(page, "08_urls_filled")

        if filled_count > 0:
            print(f"[SUCCESS] Filled {filled_count} social URL fields")
            return True
        else:
            print("[WARNING] No social URL fields were filled")
            return False

    except Exception as e:
        print(f"[ERROR] Could not fill social URLs: {e}")
        import traceback
        traceback.print_exc()
        await save_screenshot(page, "08_fill_error")
        return False

async def publish_customizer_changes(page):
    """Publish changes in the customizer."""
    print("\n=== PHASE 3: Publish Changes ===")

    try:
        # Look for Publish button - it should be in the top bar
        publish_btn = await page.query_selector("#save, .customize-save-button-wrapper button, input[value='Publish']")

        if publish_btn:
            # Check if button is enabled
            is_disabled = await publish_btn.is_disabled()
            if is_disabled:
                print("[INFO] Publish button is disabled (no changes to publish)")
                await save_screenshot(page, "09_publish_disabled")
                return True  # No changes needed

            await publish_btn.click()
            await page.wait_for_timeout(5000)
            await save_screenshot(page, "09_published")
            print("[SUCCESS] Published customizer changes")
            return True
        else:
            # Try clicking by text
            await page.click("text=Publish")
            await page.wait_for_timeout(5000)
            await save_screenshot(page, "09_published_text")
            print("[SUCCESS] Published via text click")
            return True

    except Exception as e:
        print(f"[WARNING] Publish issue: {e}")
        await save_screenshot(page, "09_publish_warning")

    return False

async def verify_changes(page):
    """Verify the changes on the live site."""
    print("\n=== VERIFICATION ===")

    await page.goto("https://purebrain.ai", wait_until="domcontentloaded")
    await page.wait_for_timeout(5000)

    # Scroll to bottom
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    await page.wait_for_timeout(2000)

    await save_screenshot(page, "10_live_footer", full_page=False)
    await save_screenshot(page, "10b_live_fullpage", full_page=True)

    content = await page.content()

    # Check for any social links
    social_indicators = [
        "linkedin.com/company/purebrain",
        "facebook.com/PureBrainAI",
        "x.com/PureBrainAI",
        "instagram.com/purebrain",
        "fa-linkedin",
        "fa-facebook",
        "fa-twitter",
        "fa-instagram",
        "social-icon"
    ]

    found_any = False
    for indicator in social_indicators:
        if indicator.lower() in content.lower():
            print(f"[SUCCESS] Found '{indicator}' on live site!")
            found_any = True

    if found_any:
        return True
    else:
        print("[INFO] Social icons may not be visible yet (theme may not render them)")
        return False

async def explore_footer_theme_settings(page):
    """Explore footer theme settings more deeply."""
    print("\n=== PHASE 2b: Deep Explore Footer Settings ===")

    # Let's look at the raw HTML of the footer options section
    try:
        # Get all controls in the footer options section
        controls = await page.query_selector_all(".customize-control")

        for i, ctrl in enumerate(controls):
            try:
                # Get the control's HTML
                html = await ctrl.inner_html()
                if any(keyword in html.lower() for keyword in ['social', 'facebook', 'twitter', 'linkedin', 'instagram', 'url']):
                    print(f"[DEBUG] Control #{i} contains social content:")
                    print(f"  HTML: {html[:200]}...")

                    # Try to find and fill any inputs in this control
                    inp = await ctrl.query_selector("input")
                    if inp:
                        input_id = await inp.get_attribute("id")
                        current_val = await inp.input_value()
                        print(f"  Input ID: {input_id}, Current value: {current_val}")

            except Exception as e:
                pass

        await save_screenshot(page, "11_deep_explore")

    except Exception as e:
        print(f"[DEBUG] Deep explore error: {e}")

async def main():
    """Main automation flow."""
    print("=" * 60)
    print("PureBrain.ai Footer Social Icons - Theme Built-in Fields")
    print("=" * 60)
    print(f"Target: {WP_URL}")
    print(f"Screenshots: {SCREENSHOT_DIR}")
    print("=" * 60)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )

        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

        page = await context.new_page()
        page.set_default_timeout(30000)  # Shorter timeout for faster failure

        results = {
            "login": False,
            "social_urls_filled": False,
            "published": False,
            "verified": False
        }

        try:
            # Login
            results["login"] = await login_to_wordpress(page)
            if not results["login"]:
                print("[FATAL] Login failed")
                return results

            # Fill social URLs
            results["social_urls_filled"] = await fill_footer_social_urls(page)

            # Explore more deeply if initial fill didn't work
            if not results["social_urls_filled"]:
                await explore_footer_theme_settings(page)

            # Publish changes
            results["published"] = await publish_customizer_changes(page)

            # Verify
            results["verified"] = await verify_changes(page)

        except Exception as e:
            print(f"[ERROR] Exception: {e}")
            import traceback
            traceback.print_exc()
            await save_screenshot(page, "error_state")

        finally:
            await browser.close()

        # Summary
        print("\n" + "=" * 60)
        print("RESULTS SUMMARY")
        print("=" * 60)
        for step, success in results.items():
            status = "[PASS]" if success else "[FAIL/SKIP]"
            print(f"{status} {step}")
        print("=" * 60)

        # List screenshots
        print("\nScreenshots:")
        for f in sorted(SCREENSHOT_DIR.glob("v4_*.png")):
            print(f"  - {f.name}")

        return results

if __name__ == "__main__":
    asyncio.run(main())
