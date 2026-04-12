#!/usr/bin/env python3
"""
WordPress Footer Social Icons Configuration
Sets social media URLs in the Theme Customizer Footer Options
"""

import sys
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Configuration
WP_URL = "https://purebrain.ai/wp-admin"
WP_USER = "Aether"
WP_PASS = "b&JJRfs)6yuSWJCc7WiFY)G8"

# Social media URLs to set
SOCIAL_URLS = {
    "linkedin": "https://www.linkedin.com/company/purebrain-ai/",
    "facebook": "https://www.facebook.com/PureBrainAI/",
    "twitter": "https://x.com/PureBrainAI",  # Twitter/X
    "instagram": "https://www.instagram.com/purebrain.ai/",
}


def take_screenshot(page, name):
    """Take screenshot and save to temp directory"""
    path = f"/tmp/wp_footer_socials_{name}.png"
    page.screenshot(path=path)
    print(f"Screenshot saved: {path}")
    return path


def login(page):
    """Handle WordPress login"""
    page.goto(WP_URL, wait_until="networkidle", timeout=30000)

    if page.url.endswith("/wp-login.php") or "wp-login" in page.url:
        username_password_link = page.locator('text="Log in with username and password"')
        if username_password_link.count() > 0:
            print("Clicking 'Log in with username and password'")
            username_password_link.click()
            page.wait_for_timeout(1000)

        page.fill("#user_login", WP_USER)
        page.fill("#user_pass", WP_PASS)
        page.click("#wp-submit")
        page.wait_for_load_state("networkidle")
        print("Logged in successfully")


def main():
    print("Setting Footer Social Media URLs")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        try:
            # Login
            print("\n[Step 1] Logging in...")
            login(page)
            take_screenshot(page, "01_dashboard")

            # Go to Theme Customizer
            print("\n[Step 2] Opening Theme Customizer...")
            page.goto("https://purebrain.ai/wp-admin/customize.php",
                      wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(3000)  # Wait for customizer to load
            take_screenshot(page, "02_customizer")

            # Click on Footer Options
            print("\n[Step 3] Opening Footer Options...")
            footer_options = page.locator('#accordion-section-footer_options, li:has-text("Footer Options")')
            if footer_options.count() > 0:
                footer_options.first.click()
                page.wait_for_timeout(2000)
                take_screenshot(page, "03_footer_options")
            else:
                print("Footer Options section not found!")
                return 1

            # Debug: List all visible input fields
            print("\n[Step 4] Analyzing form structure...")

            # Get the footer options panel content
            panel = page.locator('#sub-accordion-section-footer_options, .customize-pane-child:visible')
            if panel.count() > 0:
                # Scroll to see all content
                panel.first.evaluate('el => el.scrollTop = 0')
                page.wait_for_timeout(500)
                take_screenshot(page, "04a_panel_top")

                # Find all text inputs in the panel
                text_inputs = page.locator('#sub-accordion-section-footer_options input[type="text"], #sub-accordion-section-footer_options input[type="url"]').all()
                print(f"Found {len(text_inputs)} text/url inputs")

                for i, inp in enumerate(text_inputs):
                    inp_id = inp.get_attribute("id") or "no-id"
                    inp_value = inp.input_value() or ""
                    inp_placeholder = inp.get_attribute("placeholder") or ""
                    print(f"  Input {i}: id={inp_id}, placeholder={inp_placeholder}, value={inp_value[:60]}...")

                # Scroll down in the panel
                panel.first.evaluate('el => el.scrollTop = el.scrollHeight / 2')
                page.wait_for_timeout(500)
                take_screenshot(page, "04b_panel_mid")

            # Now let's try to set the social URLs
            # The inputs seem to be in a "Social URLs" section
            print("\n[Step 5] Setting social media URLs...")

            # Look for specific input IDs or patterns
            # Common naming: _customize-input-SETTING_NAME

            # Try different selectors for each social network
            social_selectors = {
                "linkedin": [
                    'input[id*="linkedin"][type="text"]',
                    'input[id*="linkedin"][type="url"]',
                    'input[placeholder*="linkedin" i]',
                    '#_customize-input-artistics_linkedin_url',
                    'input[data-customize-setting-link*="linkedin"]',
                ],
                "facebook": [
                    'input[id*="facebook"][type="text"]',
                    'input[id*="facebook"][type="url"]',
                    'input[placeholder*="facebook" i]',
                    '#_customize-input-artistics_facebook_url',
                    'input[data-customize-setting-link*="facebook"]',
                ],
                "twitter": [
                    'input[id*="twitter"][type="text"]',
                    'input[id*="twitter"][type="url"]',
                    'input[placeholder*="twitter" i]',
                    'input[placeholder*="x.com" i]',
                    '#_customize-input-artistics_twitter_url',
                    'input[data-customize-setting-link*="twitter"]',
                ],
                "instagram": [
                    'input[id*="instagram"][type="text"]',
                    'input[id*="instagram"][type="url"]',
                    'input[placeholder*="instagram" i]',
                    '#_customize-input-artistics_instagram_url',
                    'input[data-customize-setting-link*="instagram"]',
                ],
            }

            for social, url in SOCIAL_URLS.items():
                found = False
                for selector in social_selectors[social]:
                    inp = page.locator(selector).first
                    if inp.count() > 0:
                        try:
                            # Clear and fill the input
                            inp.click()
                            inp.fill("")
                            inp.fill(url)
                            print(f"  Set {social}: {url}")
                            found = True
                            break
                        except Exception as e:
                            print(f"  Failed to set {social} with selector {selector}: {e}")
                            continue

                if not found:
                    print(f"  Could not find input for {social}")

            page.wait_for_timeout(1000)
            take_screenshot(page, "05_urls_set")

            # Publish changes
            print("\n[Step 6] Publishing changes...")
            publish_button = page.locator('#save, #publish-settings, button:has-text("Publish")').first
            if publish_button.count() > 0:
                # Check if the button is enabled (there are changes)
                is_disabled = publish_button.get_attribute("disabled")
                if not is_disabled:
                    publish_button.click()
                    page.wait_for_timeout(3000)
                    take_screenshot(page, "06_published")
                    print("Changes published!")
                else:
                    print("Publish button is disabled - no changes detected")
                    take_screenshot(page, "06_no_changes")
            else:
                print("Could not find Publish button")
                take_screenshot(page, "06_no_publish")

            # Verify on frontend
            print("\n[Step 7] Verifying on frontend...")
            page.goto("https://purebrain.ai", wait_until="networkidle", timeout=30000)
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1500)
            take_screenshot(page, "07_frontend_footer")

            # Check for social icons in footer
            for social in ["linkedin", "facebook", "twitter", "instagram"]:
                links = page.locator(f'footer a[href*="{social}"], #footer a[href*="{social}"]')
                if links.count() > 0:
                    href = links.first.get_attribute("href")
                    print(f"  Found {social} link: {href}")
                else:
                    print(f"  {social} link not found in footer")

            print("\n" + "=" * 60)
            print("Configuration complete!")
            print("Screenshots saved to /tmp/wp_footer_socials_*.png")

        except PlaywrightTimeout as e:
            print(f"Timeout error: {e}")
            take_screenshot(page, "error_timeout")
            return 1
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            take_screenshot(page, "error_general")
            return 1
        finally:
            browser.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
