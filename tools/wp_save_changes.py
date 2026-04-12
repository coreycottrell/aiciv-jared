#!/usr/bin/env python3
"""
Save the Thank You page changes properly
"""

import os
import time
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

SCREENSHOT_DIR = "/tmp"
WP_URL = "https://purebrain.ai/wp-admin/"
WP_USER = "Purebrain@puremarketing.ai"
WP_PASS = "NW2u!JLQ3!Bt$XD$7CWzz5Z@"

# Enhanced Thank You page HTML
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
    """Update Thank You page with enhanced design"""
    print("\n=== UPDATING THANK YOU PAGE ===")

    # Navigate to Thank You page edit directly using post ID
    # First get the post ID from pages list
    page.goto("https://purebrain.ai/wp-admin/edit.php?post_type=page", wait_until="domcontentloaded")
    page.wait_for_timeout(2000)

    # Find Thank You row and get post ID from edit link
    thank_you_row = page.locator("tr:has(a.row-title:has-text('Thank You'))")
    if thank_you_row.count() == 0:
        print("Thank You page not found!")
        return False

    # Get the edit link
    edit_link = thank_you_row.locator("a.row-title").get_attribute("href")
    print(f"Edit link: {edit_link}")

    # Navigate to the edit page
    page.goto(edit_link, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    # Wait for Gutenberg to load
    screenshot(page, "save-01-editor-open")

    # Check if we're in visual editor and switch to code editor
    # Press Ctrl+Shift+Alt+M to toggle code editor
    page.keyboard.press("Control+Shift+Alt+M")
    page.wait_for_timeout(2000)
    screenshot(page, "save-02-code-editor")

    # Find the code editor textarea
    code_area = page.locator("textarea.editor-post-text-editor")
    if code_area.count() == 0:
        # Try alternate selector
        code_area = page.locator("textarea[aria-label*='code'], textarea.wp-block-code__textarea")

    if code_area.count() > 0 and code_area.is_visible():
        print("Found code editor textarea")

        # Select all and replace
        code_area.click()
        code_area.press("Control+a")
        page.wait_for_timeout(200)

        # Type our new content
        code_area.fill(THANK_YOU_HTML)
        page.wait_for_timeout(500)

        screenshot(page, "save-03-content-filled")

        # Now find and click the Update/Save button
        # In Gutenberg, it's usually at the top right
        # First check if there's an unsaved changes indicator

        # Wait a moment for the editor to register changes
        page.wait_for_timeout(1000)

        # Look for Update button (may say "Save" or "Update")
        # It's usually in the top bar with a specific class
        save_btn = page.locator("button.editor-post-publish-button")
        if save_btn.count() == 0:
            save_btn = page.locator("button:has-text('Update')")
        if save_btn.count() == 0:
            save_btn = page.locator("button:has-text('Save')")

        # Take screenshot to see what buttons are available
        screenshot(page, "save-04-looking-for-button")

        # Try to find any button with save/update text
        all_buttons = page.locator("button").all()
        save_found = False
        for btn in all_buttons:
            try:
                text = btn.text_content() or ""
                aria = btn.get_attribute("aria-label") or ""
                if "update" in text.lower() or "save" in text.lower() or "publish" in aria.lower():
                    print(f"Found button: '{text}' aria: '{aria}'")
                    if btn.is_visible() and btn.is_enabled():
                        btn.click()
                        save_found = True
                        print("Clicked save button!")
                        page.wait_for_timeout(3000)
                        break
            except:
                continue

        if not save_found:
            # Try keyboard shortcut Ctrl+S
            print("Trying Ctrl+S...")
            page.keyboard.press("Control+s")
            page.wait_for_timeout(3000)

        screenshot(page, "save-05-after-save")

        # Check for success snackbar/notice
        notice = page.locator(".components-snackbar, .notice-success")
        if notice.count() > 0:
            notice_text = notice.text_content()
            print(f"Notice: {notice_text}")

        return True
    else:
        print("Code editor textarea not visible")
        # List what textareas exist
        textareas = page.locator("textarea").all()
        print(f"Found {len(textareas)} textareas")
        for i, ta in enumerate(textareas[:5]):
            try:
                classes = ta.get_attribute("class")
                print(f"  Textarea {i}: {classes}")
            except:
                pass

    return False


def verify_thank_you(page):
    """Verify the Thank You page update"""
    print("\n=== VERIFYING THANK YOU PAGE ===")

    page.goto("https://purebrain.ai/thank-you/", wait_until="domcontentloaded")
    page.wait_for_timeout(3000)

    screenshot(page, "save-verify-thank-you")

    # Check if our new content is there
    html = page.content()
    has_sparkle = "&#10024;" in html or "10024" in html or "sparkle" in html.lower()
    has_welcome = "Welcome to the Family" in html
    has_payment_confirmed = "Payment Confirmed" in html

    print(f"Has sparkle icon: {has_sparkle}")
    print(f"Has 'Welcome to the Family': {has_welcome}")
    print(f"Has 'Payment Confirmed': {has_payment_confirmed}")

    return has_welcome and has_payment_confirmed


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        print("=" * 60)
        print("SAVING THANK YOU PAGE CHANGES")
        print("=" * 60)

        if not wp_login(page):
            print("Login failed!")
            browser.close()
            return

        success = update_thank_you_page(page)

        if success:
            # Re-login and verify
            wp_login(page)
            verified = verify_thank_you(page)
            print(f"\nVerification: {'SUCCESS' if verified else 'NEEDS CHECK'}")

        print("\n" + "=" * 60)
        print("COMPLETED - Screenshots in /tmp/paypal-final-save-*.png")
        print("=" * 60)

        browser.close()


if __name__ == "__main__":
    main()
