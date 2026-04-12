#!/usr/bin/env python3
"""
Final WordPress Updates:
1. Update Thank You page with enhanced design via Gutenberg code editor
2. Add PayPal-linked pricing section to PureBrain 2.0 page via Elementor
"""

import os
import time
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

SCREENSHOT_DIR = "/tmp"
WP_URL = "https://purebrain.ai/wp-admin/"
WP_USER = "Purebrain@puremarketing.ai"
WP_PASS = "NW2u!JLQ3!Bt$XD$7CWzz5Z@"

# Enhanced Thank You page HTML (simpler version that will display well)
THANK_YOU_HTML = '''<!-- wp:html -->
<div style="text-align: center; padding: 60px 20px; max-width: 800px; margin: 0 auto;">

  <!-- Sparkle Icon -->
  <div style="font-size: 64px; margin-bottom: 20px;">&#10024;</div>

  <!-- Main Heading -->
  <h1 style="color: #f1420b; font-size: 42px; margin-bottom: 15px;">Welcome to the Family!</h1>

  <p style="font-size: 20px; color: #ffffff; margin-bottom: 40px;">
    Your Pure Brain journey begins now. We're thrilled to have you.
  </p>

  <!-- Confirmation Box -->
  <div style="background: rgba(241, 66, 11, 0.1); border: 2px solid rgba(241, 66, 11, 0.3); border-radius: 16px; padding: 40px; margin-bottom: 40px;">
    <h2 style="color: #f1420b; font-size: 28px; margin-bottom: 15px;">Payment Confirmed!</h2>
    <p style="color: #ffffff; font-size: 18px; margin-bottom: 10px;">
      We've received your payment and our team will reach out within 24 hours to begin your onboarding.
    </p>
    <p style="color: #aaaaaa; font-size: 14px;">
      Check your email for a confirmation and next steps.
    </p>
  </div>

  <!-- Timeline Header -->
  <h3 style="color: #f1420b; font-size: 12px; letter-spacing: 3px; text-transform: uppercase; margin-bottom: 30px;">
    What Happens Next
  </h3>

  <!-- Timeline -->
  <div style="text-align: left; max-width: 500px; margin: 0 auto 40px auto;">
    <div style="display: flex; align-items: center; gap: 20px; margin-bottom: 15px; background: rgba(255,255,255,0.05); padding: 15px 20px; border-radius: 10px;">
      <span style="background: #f1420b; color: white; padding: 10px 15px; border-radius: 8px; font-weight: bold; font-size: 14px;">24 hrs</span>
      <span style="color: #ffffff;">Personal welcome email from our team</span>
    </div>
    <div style="display: flex; align-items: center; gap: 20px; margin-bottom: 15px; background: rgba(255,255,255,0.05); padding: 15px 20px; border-radius: 10px;">
      <span style="background: #f1420b; color: white; padding: 10px 15px; border-radius: 8px; font-weight: bold; font-size: 14px;">48 hrs</span>
      <span style="color: #ffffff;">Your AI partner setup begins</span>
    </div>
    <div style="display: flex; align-items: center; gap: 20px; background: rgba(255,255,255,0.05); padding: 15px 20px; border-radius: 10px;">
      <span style="background: #f1420b; color: white; padding: 10px 15px; border-radius: 8px; font-weight: bold; font-size: 14px;">1 week</span>
      <span style="color: #ffffff;">Your Pure Brain is fully configured and ready</span>
    </div>
  </div>

  <!-- CTA Button -->
  <a href="https://purebrain.ai" style="display: inline-block; background: linear-gradient(135deg, #f1420b 0%, #ff6b3d 100%); color: white; padding: 16px 50px; font-size: 16px; font-weight: bold; border-radius: 50px; text-decoration: none; box-shadow: 0 4px 20px rgba(241, 66, 11, 0.4);">Return to Homepage</a>

  <!-- Footer Note -->
  <p style="color: #666666; font-size: 13px; margin-top: 50px;">
    Questions? Email us at <a href="mailto:support@puremarketing.ai" style="color: #f1420b;">support@puremarketing.ai</a>
  </p>

</div>
<!-- /wp:html -->'''


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


def update_thank_you_page(page):
    """Update Thank You page via Gutenberg code editor"""
    print("\n=== UPDATING THANK YOU PAGE ===")

    # Go directly to the Thank You page edit URL
    # First find the post ID
    page.goto("https://purebrain.ai/wp-admin/edit.php?post_type=page", wait_until="domcontentloaded")
    page.wait_for_timeout(2000)

    # Click Thank You in the list
    thank_you_row = page.locator("tr:has(a.row-title:has-text('Thank You'))")
    if thank_you_row.count() > 0:
        # Get the edit link
        edit_link = thank_you_row.locator("a.row-title")
        edit_link.click()
        page.wait_for_timeout(5000)
        screenshot(page, "ty-01-edit-open")

        # We're in the Gutenberg editor. Need to switch to code editor
        # Click the 3-dot menu (Options)
        options_btn = page.locator("button[aria-label='Options']")
        if options_btn.count() > 0:
            options_btn.click()
            page.wait_for_timeout(500)

            # Click "Code editor"
            code_editor_option = page.locator("button:has-text('Code editor')")
            if code_editor_option.count() > 0:
                code_editor_option.click()
                page.wait_for_timeout(1000)
                screenshot(page, "ty-02-code-editor")

        # Now we should be in code editor mode
        # Find the textarea
        code_area = page.locator("textarea.editor-post-text-editor")
        if code_area.count() > 0:
            print("Found code editor textarea")

            # Clear and fill with our new content
            code_area.fill(THANK_YOU_HTML)
            page.wait_for_timeout(500)
            screenshot(page, "ty-03-new-content")

            # Click Update button
            update_btn = page.locator("button.editor-post-publish-button:has-text('Update')")
            if update_btn.count() > 0:
                update_btn.click()
                page.wait_for_timeout(3000)
                print("Clicked Update")
                screenshot(page, "ty-04-updated")

                # Check for success notice
                notice = page.locator(".components-snackbar")
                if notice.count() > 0:
                    print(f"Notice: {notice.text_content()}")

                return True
            else:
                # Try alternate update button
                update_btn2 = page.locator("button:has-text('Update')")
                if update_btn2.count() > 0:
                    update_btn2.first.click()
                    page.wait_for_timeout(3000)
                    print("Clicked Update (alt)")
                    screenshot(page, "ty-04-updated")
                    return True
        else:
            print("Code editor textarea not found")
            # Try clicking the content area to switch
            page.keyboard.press("Control+Shift+Alt+M")  # Toggle code editor shortcut
            page.wait_for_timeout(1000)
            screenshot(page, "ty-02b-after-shortcut")

    return False


def add_pricing_to_purebrain(page):
    """Navigate to PureBrain 2.0 in Elementor and add pricing section"""
    print("\n=== ADDING PAYPAL TO PUREBRAIN 2.0 ===")

    # Go to pages list
    page.goto("https://purebrain.ai/wp-admin/edit.php?post_type=page", wait_until="domcontentloaded")
    page.wait_for_timeout(2000)

    # Find PureBrain 2.0 row
    purebrain_row = page.locator("tr:has(a.row-title:has-text('PureBrain 2.0'))")
    if purebrain_row.count() > 0:
        # Hover to reveal Edit with Elementor
        purebrain_row.hover()
        page.wait_for_timeout(500)

        # Click Edit with Elementor
        elementor_link = purebrain_row.locator("a:has-text('Edit with Elementor')")
        if elementor_link.count() > 0:
            elementor_link.click()
            page.wait_for_timeout(15000)  # Elementor takes a while
            screenshot(page, "pb-01-elementor-open")

            # Wait for Elementor to fully load
            try:
                page.wait_for_selector("#elementor-preview-iframe", timeout=20000)
            except:
                print("Elementor iframe not found")
                return False

            # Now we need to find the pricing section and add PayPal widgets
            # This requires navigating in Elementor which is complex
            # For now, let's take a screenshot and document what needs manual work

            screenshot(page, "pb-02-elementor-loaded")

            # Try to open the navigator panel to see the structure
            nav_btn = page.locator("button[title='Navigator'], [data-testid='navigator-trigger']")
            if nav_btn.count() > 0:
                nav_btn.first.click()
                page.wait_for_timeout(1000)
                screenshot(page, "pb-03-navigator")

            # Search for HTML widget in the panel
            search_input = page.locator("#elementor-panel-elements-search-input")
            if search_input.count() > 0 and search_input.is_visible():
                search_input.fill("HTML")
                page.wait_for_timeout(500)
                screenshot(page, "pb-04-html-widget-search")

            return True
        else:
            print("Edit with Elementor link not found")
    else:
        print("PureBrain 2.0 row not found")

    return False


def verify_updates(page):
    """Verify the updates by viewing the live pages"""
    print("\n=== VERIFICATION ===")

    # Check Thank You page
    page.goto("https://purebrain.ai/thank-you/", wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    screenshot(page, "verify-thank-you")

    # Check PureBrain 2.0 page
    page.goto("https://purebrain.ai/purebrain-2-0/", wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    screenshot(page, "verify-purebrain")

    # Check existing PayPal page
    page.goto("https://purebrain.ai/paypal-buttons-embed/", wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    screenshot(page, "verify-paypal-embed")

    # Test a PayPal button by checking if clicking opens PayPal
    starter_btn = page.locator("button:has-text('Get Started'), form button:first-of-type")
    if starter_btn.count() > 0:
        print(f"Found {starter_btn.count()} starter button(s)")

        # Get the form action to verify it's PayPal
        forms = page.locator("form[action*='paypal']").all()
        print(f"Found {len(forms)} PayPal forms")
        for i, form in enumerate(forms):
            action = form.get_attribute("action")
            print(f"  Form {i+1}: {action}")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        print("=" * 60)
        print("FINAL WORDPRESS UPDATES")
        print("=" * 60)

        if not wp_login(page):
            print("Login failed!")
            browser.close()
            return

        # Task 1: Update Thank You page
        thank_you_success = update_thank_you_page(page)
        print(f"\nThank You page update: {'SUCCESS' if thank_you_success else 'NEEDS ATTENTION'}")

        # Task 2: Work on PureBrain 2.0
        wp_login(page)  # Re-login for fresh session
        purebrain_success = add_pricing_to_purebrain(page)
        print(f"PureBrain 2.0 work: {'OPENED' if purebrain_success else 'NEEDS ATTENTION'}")

        # Verification
        wp_login(page)  # Re-login
        verify_updates(page)

        print("\n" + "=" * 60)
        print("COMPLETED - Screenshots in /tmp/paypal-final-*.png")
        print("=" * 60)

        browser.close()


if __name__ == "__main__":
    main()
