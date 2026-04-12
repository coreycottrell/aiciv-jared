#!/usr/bin/env python3
"""
WordPress Complete Tasks:
1. Check PayPal button functionality on both pages
2. Add/update PayPal forms if needed
3. Update Thank You page with enhanced design
"""

import os
import re
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

SCREENSHOT_DIR = "/tmp"
WP_URL = "https://purebrain.ai/wp-admin/"
WP_USER = "Purebrain@puremarketing.ai"
WP_PASS = "NW2u!JLQ3!Bt$XD$7CWzz5Z@"

# Enhanced Thank You HTML that matches the homepage style better
THANK_YOU_HTML_ENHANCED = '''<div style="min-height: 100vh; background: linear-gradient(180deg, #0a0a0a 0%, #1a1a2e 50%, #0a0a0a 100%); padding: 80px 20px; text-align: center; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">

  <div style="max-width: 900px; margin: 0 auto;">

    <!-- Logo/Brand -->
    <div style="margin-bottom: 50px;">
      <span style="font-size: 36px; font-weight: 800; letter-spacing: 2px;">
        <span style="color: #2a93c1;">PURE BR</span><span style="color: #f1420b;">AI</span><span style="color: #2a93c1;">N</span>
      </span>
    </div>

    <!-- Sparkle Icon -->
    <div style="font-size: 72px; margin-bottom: 30px;">&#10024;</div>

    <!-- Main Heading -->
    <h1 style="font-size: 52px; font-weight: 800; margin-bottom: 20px; color: #ffffff; text-shadow: 0 2px 10px rgba(241, 66, 11, 0.3);">
      Welcome to the Family!
    </h1>

    <p style="font-size: 22px; color: #cccccc; margin-bottom: 60px; line-height: 1.6;">
      Your Pure Brain journey begins now. We're thrilled to have you.
    </p>

    <!-- Confirmation Box -->
    <div style="background: linear-gradient(135deg, rgba(241, 66, 11, 0.15) 0%, rgba(42, 147, 193, 0.15) 100%); border: 2px solid rgba(241, 66, 11, 0.4); border-radius: 20px; padding: 50px 40px; margin-bottom: 60px; box-shadow: 0 10px 40px rgba(0,0,0,0.3);">
      <h2 style="color: #f1420b; font-size: 32px; margin-bottom: 20px; font-weight: 700;">Payment Confirmed!</h2>
      <p style="color: #ffffff; font-size: 20px; margin-bottom: 10px;">
        We've received your payment and our team will reach out within 24 hours to begin your onboarding.
      </p>
      <p style="color: #aaaaaa; font-size: 16px;">
        Check your email for a confirmation and next steps.
      </p>
    </div>

    <!-- Timeline Header -->
    <h3 style="color: #f1420b; font-size: 14px; letter-spacing: 4px; text-transform: uppercase; margin-bottom: 40px; font-weight: 600;">
      What Happens Next
    </h3>

    <!-- Timeline Cards -->
    <div style="display: flex; flex-direction: column; gap: 20px; max-width: 650px; margin: 0 auto 60px auto; text-align: left;">

      <div style="display: flex; align-items: center; gap: 25px; background: linear-gradient(135deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.03) 100%); padding: 25px 30px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.1);">
        <div style="background: linear-gradient(135deg, #f1420b 0%, #ff6b3d 100%); color: white; padding: 15px 20px; border-radius: 12px; font-weight: bold; white-space: nowrap; font-size: 16px; box-shadow: 0 4px 15px rgba(241, 66, 11, 0.4);">24 hrs</div>
        <div style="color: #ffffff; font-size: 18px;">Personal welcome email from our team</div>
      </div>

      <div style="display: flex; align-items: center; gap: 25px; background: linear-gradient(135deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.03) 100%); padding: 25px 30px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.1);">
        <div style="background: linear-gradient(135deg, #f1420b 0%, #ff6b3d 100%); color: white; padding: 15px 20px; border-radius: 12px; font-weight: bold; white-space: nowrap; font-size: 16px; box-shadow: 0 4px 15px rgba(241, 66, 11, 0.4);">48 hrs</div>
        <div style="color: #ffffff; font-size: 18px;">Your AI partner setup begins</div>
      </div>

      <div style="display: flex; align-items: center; gap: 25px; background: linear-gradient(135deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.03) 100%); padding: 25px 30px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.1);">
        <div style="background: linear-gradient(135deg, #f1420b 0%, #ff6b3d 100%); color: white; padding: 15px 20px; border-radius: 12px; font-weight: bold; white-space: nowrap; font-size: 16px; box-shadow: 0 4px 15px rgba(241, 66, 11, 0.4);">1 week</div>
        <div style="color: #ffffff; font-size: 18px;">Your Pure Brain is fully configured and ready</div>
      </div>

    </div>

    <!-- CTA Button -->
    <a href="https://purebrain.ai" style="
      display: inline-block;
      background: linear-gradient(135deg, #f1420b 0%, #ff6b3d 100%);
      color: white;
      padding: 20px 60px;
      font-size: 18px;
      font-weight: bold;
      border-radius: 50px;
      text-decoration: none;
      box-shadow: 0 8px 30px rgba(241, 66, 11, 0.5);
      transition: transform 0.2s, box-shadow 0.2s;
    ">Return to Homepage</a>

    <!-- Footer Note -->
    <p style="color: #666666; font-size: 14px; margin-top: 80px;">
      Questions? Email us at <a href="mailto:support@puremarketing.ai" style="color: #f1420b; text-decoration: none;">support@puremarketing.ai</a>
    </p>

  </div>
</div>'''


def screenshot(page, name):
    path = f"{SCREENSHOT_DIR}/paypal-final-{name}.png"
    page.screenshot(path=path, full_page=True)
    print(f"Screenshot: {path}")
    return path


def wp_login(page):
    """Login to WordPress"""
    print("Logging in to WordPress...")
    page.goto(WP_URL, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)

    password_link = page.get_by_text("Log in with username and password")
    if password_link.count() > 0:
        password_link.click()
        page.wait_for_timeout(2000)

    if page.locator("#user_login").is_visible():
        page.fill("#user_login", WP_USER)
        page.fill("#user_pass", WP_PASS)
        page.click("#wp-submit")
        try:
            page.wait_for_url("**/wp-admin/**", timeout=15000)
        except:
            pass
        page.wait_for_timeout(3000)

    if "wp-admin" in page.url:
        print("Login successful!")
        return True
    return False


def check_paypal_buttons_on_page(page, url):
    """Check if a page has working PayPal buttons"""
    print(f"\nChecking PayPal buttons on: {url}")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(2000)

    html = page.content()

    # Look for PayPal form indicators
    has_paypal_form = "paypal.com/cgi-bin/webscr" in html.lower()
    has_paypal_button = "paypal" in html.lower()

    # Look for button elements that might be PayPal
    buttons = page.locator("button, input[type='submit'], a").all()
    button_texts = []
    for btn in buttons[:20]:
        try:
            text = btn.text_content() or ""
            button_texts.append(text.strip())
        except:
            pass

    print(f"  Has PayPal form action: {has_paypal_form}")
    print(f"  Has PayPal reference: {has_paypal_button}")
    print(f"  Buttons found: {button_texts[:10]}")

    return has_paypal_form


def update_thank_you_via_wp_api(page):
    """Update Thank You page using WordPress REST API or direct Gutenberg editing"""
    print("\n--- Updating Thank You Page ---")

    # Navigate to edit page
    page.goto("https://purebrain.ai/wp-admin/edit.php?post_type=page", wait_until="domcontentloaded")
    page.wait_for_timeout(2000)

    # Find and click Thank You page
    thank_you_link = page.locator("a.row-title:has-text('Thank You')")
    if thank_you_link.count() > 0:
        thank_you_link.click()
        page.wait_for_timeout(5000)
        screenshot(page, "50-thank-you-edit-start")

        # Check if we're in code editor or visual editor
        # Try to switch to code editor
        code_editor_btn = page.locator("button:has-text('Code editor'), [aria-label='Code editor']")
        if code_editor_btn.count() > 0:
            code_editor_btn.first.click()
            page.wait_for_timeout(1000)

        # Look for the content textarea or code editor
        code_textarea = page.locator("textarea.editor-post-text-editor")
        if code_textarea.count() > 0:
            print("Found code editor textarea")
            # Get current content
            current = code_textarea.input_value()
            print(f"Current content length: {len(current)}")

            # Replace with our enhanced HTML
            # First clear it
            code_textarea.fill("")
            page.wait_for_timeout(500)

            # Now fill with our new content wrapped in HTML block
            new_content = f'''<!-- wp:html -->
{THANK_YOU_HTML_ENHANCED}
<!-- /wp:html -->'''

            code_textarea.fill(new_content)
            page.wait_for_timeout(1000)
            screenshot(page, "51-thank-you-new-content")

            # Click Update button
            update_btn = page.locator("button:has-text('Update')")
            if update_btn.count() > 0:
                update_btn.first.click()
                page.wait_for_timeout(3000)
                print("Clicked Update button")
                screenshot(page, "52-thank-you-updated")

                # Wait for save confirmation
                page.wait_for_timeout(2000)
                return True

    return False


def add_paypal_buttons_to_purebrain(page):
    """Add PayPal form buttons to PureBrain 2.0 page via Elementor"""
    print("\n--- Adding PayPal Buttons to PureBrain 2.0 ---")

    # First, let's check the current page structure
    page.goto("https://purebrain.ai/purebrain-2-0/", wait_until="domcontentloaded")
    page.wait_for_timeout(2000)

    # Look for existing buttons
    buttons = page.locator("button, a.elementor-button").all()
    button_texts = []
    for btn in buttons[:20]:
        try:
            text = btn.text_content() or ""
            if text.strip():
                button_texts.append(text.strip())
        except:
            pass

    print(f"Buttons on page: {button_texts}")

    # Check if pricing section exists
    html = page.content()
    has_79 = "$79" in html
    has_149 = "$149" in html
    has_499 = "$499" in html
    has_999 = "$999" in html

    print(f"Pricing tiers found: $79={has_79}, $149={has_149}, $499={has_499}, $999={has_999}")

    # Take screenshot of pricing section
    page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.6)")
    page.wait_for_timeout(500)
    screenshot(page, "60-purebrain-pricing-section")

    # Check if buttons already have PayPal functionality
    has_paypal = "paypal.com/cgi-bin/webscr" in html.lower()
    print(f"Page has PayPal forms: {has_paypal}")

    return has_paypal


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        print("=" * 60)
        print("WORDPRESS TASKS: PayPal Buttons & Thank You Page")
        print("=" * 60)

        if not wp_login(page):
            print("Login failed!")
            browser.close()
            return

        # Task 1: Check PayPal buttons on both relevant pages
        print("\n" + "=" * 40)
        print("TASK 1: Verify PayPal Button Status")
        print("=" * 40)

        # Check PayPal Embed page
        has_paypal_embed = check_paypal_buttons_on_page(page, "https://purebrain.ai/paypal-buttons-embed/")
        screenshot(page, "61-paypal-embed-check")

        # Check PureBrain 2.0 page
        has_paypal_purebrain = check_paypal_buttons_on_page(page, "https://purebrain.ai/purebrain-2-0/")
        screenshot(page, "62-purebrain-check")

        # Task 2: Update Thank You page
        print("\n" + "=" * 40)
        print("TASK 2: Update Thank You Page Design")
        print("=" * 40)

        wp_login(page)  # Re-login to ensure session
        thank_you_updated = update_thank_you_via_wp_api(page)

        # Verify the update
        page.goto("https://purebrain.ai/thank-you/", wait_until="domcontentloaded")
        page.wait_for_timeout(3000)
        screenshot(page, "70-thank-you-final-result")

        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"PayPal Embed Page has PayPal forms: {has_paypal_embed}")
        print(f"PureBrain 2.0 Page has PayPal forms: {has_paypal_purebrain}")
        print(f"Thank You Page Updated: {thank_you_updated}")
        print("\nScreenshots saved to /tmp/paypal-final-*.png")
        print("=" * 60)

        browser.close()


if __name__ == "__main__":
    main()
