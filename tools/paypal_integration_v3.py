#!/usr/bin/env python3
"""
PayPal Integration v3 for purebrain.ai
- Uses WordPress REST API for all operations
- Thank You page already created (ID: 309)
- Updates Pure Brain 2.0 page via API
"""

import os
import sys
from datetime import datetime
from playwright.sync_api import sync_playwright

# Create screenshots directory
SCREENSHOT_DIR = "/tmp"

# Credentials
WP_URL = "https://purebrain.ai/wp-admin/"
WP_USER = "Purebrain@puremarketing.ai"
WP_PASS = "NW2u!JLQ3!Bt$XD$7CWzz5Z@"

PAYPAL_SECTION = '''
<!-- PayPal Purchase Buttons Section -->
<section id="paypal-buttons" style="padding: 60px 20px; background: rgba(0,0,0,0.3);">
  <div style="max-width: 1200px; margin: 0 auto; text-align: center;">
    <h2 style="color: #f1420b; font-size: 36px; margin-bottom: 40px;">Ready to Get Started?</h2>
    <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 30px;">

      <!-- Starter $79 -->
      <div style="background: rgba(255,255,255,0.05); border-radius: 12px; padding: 30px; min-width: 250px;">
        <h3 style="color: #ffffff; margin-bottom: 10px;">Starter</h3>
        <p style="color: #f1420b; font-size: 32px; font-weight: bold;">$79</p>
        <form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_blank" style="display: inline-block; margin-top: 20px;">
          <input type="hidden" name="cmd" value="_xclick">
          <input type="hidden" name="business" value="support@puremarketing.ai">
          <input type="hidden" name="item_name" value="Pure Brain Starter">
          <input type="hidden" name="item_number" value="PB-STARTER">
          <input type="hidden" name="amount" value="79.00">
          <input type="hidden" name="currency_code" value="USD">
          <input type="hidden" name="no_shipping" value="1">
          <input type="hidden" name="return" value="https://purebrain.ai/thank-you/">
          <input type="hidden" name="cancel_return" value="https://purebrain.ai/purebrain-2-0/">
          <button type="submit" style="background: linear-gradient(135deg, #f1420b 0%, #ff6b3d 100%); color: white; border: none; padding: 16px 40px; font-size: 18px; font-weight: bold; border-radius: 8px; cursor: pointer; box-shadow: 0 4px 15px rgba(241, 66, 11, 0.4);">Get Started - $79</button>
        </form>
      </div>

      <!-- Pro $149 -->
      <div style="background: rgba(255,255,255,0.05); border-radius: 12px; padding: 30px; min-width: 250px;">
        <h3 style="color: #ffffff; margin-bottom: 10px;">Pro</h3>
        <p style="color: #f1420b; font-size: 32px; font-weight: bold;">$149</p>
        <form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_blank" style="display: inline-block; margin-top: 20px;">
          <input type="hidden" name="cmd" value="_xclick">
          <input type="hidden" name="business" value="support@puremarketing.ai">
          <input type="hidden" name="item_name" value="Pure Brain Pro">
          <input type="hidden" name="item_number" value="PB-PRO">
          <input type="hidden" name="amount" value="149.00">
          <input type="hidden" name="currency_code" value="USD">
          <input type="hidden" name="no_shipping" value="1">
          <input type="hidden" name="return" value="https://purebrain.ai/thank-you/">
          <input type="hidden" name="cancel_return" value="https://purebrain.ai/purebrain-2-0/">
          <button type="submit" style="background: linear-gradient(135deg, #f1420b 0%, #ff6b3d 100%); color: white; border: none; padding: 16px 40px; font-size: 18px; font-weight: bold; border-radius: 8px; cursor: pointer; box-shadow: 0 4px 15px rgba(241, 66, 11, 0.4);">Go Pro - $149</button>
        </form>
      </div>

      <!-- Enterprise $499 -->
      <div style="background: rgba(255,255,255,0.05); border-radius: 12px; padding: 30px; min-width: 250px;">
        <h3 style="color: #ffffff; margin-bottom: 10px;">Enterprise</h3>
        <p style="color: #f1420b; font-size: 32px; font-weight: bold;">$499</p>
        <form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_blank" style="display: inline-block; margin-top: 20px;">
          <input type="hidden" name="cmd" value="_xclick">
          <input type="hidden" name="business" value="support@puremarketing.ai">
          <input type="hidden" name="item_name" value="Pure Brain Enterprise">
          <input type="hidden" name="item_number" value="PB-ENTERPRISE">
          <input type="hidden" name="amount" value="499.00">
          <input type="hidden" name="currency_code" value="USD">
          <input type="hidden" name="no_shipping" value="1">
          <input type="hidden" name="return" value="https://purebrain.ai/thank-you/">
          <input type="hidden" name="cancel_return" value="https://purebrain.ai/purebrain-2-0/">
          <button type="submit" style="background: linear-gradient(135deg, #f1420b 0%, #ff6b3d 100%); color: white; border: none; padding: 16px 40px; font-size: 18px; font-weight: bold; border-radius: 8px; cursor: pointer; box-shadow: 0 4px 15px rgba(241, 66, 11, 0.4);">Enterprise - $499</button>
        </form>
      </div>

      <!-- Ultimate $999 -->
      <div style="background: rgba(255,255,255,0.05); border-radius: 12px; padding: 30px; min-width: 250px;">
        <h3 style="color: #ffffff; margin-bottom: 10px;">Ultimate</h3>
        <p style="color: #f1420b; font-size: 32px; font-weight: bold;">$999</p>
        <form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_blank" style="display: inline-block; margin-top: 20px;">
          <input type="hidden" name="cmd" value="_xclick">
          <input type="hidden" name="business" value="support@puremarketing.ai">
          <input type="hidden" name="item_name" value="Pure Brain Ultimate">
          <input type="hidden" name="item_number" value="PB-ULTIMATE">
          <input type="hidden" name="amount" value="999.00">
          <input type="hidden" name="currency_code" value="USD">
          <input type="hidden" name="no_shipping" value="1">
          <input type="hidden" name="return" value="https://purebrain.ai/thank-you/">
          <input type="hidden" name="cancel_return" value="https://purebrain.ai/purebrain-2-0/">
          <button type="submit" style="background: linear-gradient(135deg, #f1420b 0%, #ff6b3d 100%); color: white; border: none; padding: 16px 40px; font-size: 18px; font-weight: bold; border-radius: 8px; cursor: pointer; box-shadow: 0 4px 15px rgba(241, 66, 11, 0.4);">Ultimate - $999</button>
        </form>
      </div>

    </div>
  </div>
</section>
'''

def screenshot(page, name):
    path = f"{SCREENSHOT_DIR}/paypal-integration-{name}.png"
    page.screenshot(path=path, full_page=True)
    print(f"Screenshot saved: {path}")
    return path

def login(page):
    """Login to WordPress admin"""
    print(f"Navigating to {WP_URL}...")
    page.goto(WP_URL, wait_until="domcontentloaded")
    page.wait_for_timeout(2000)

    password_login_link = page.get_by_text("Log in with username and password")
    if password_login_link.count() > 0:
        print("Found GoDaddy SSO page, clicking username/password option...")
        password_login_link.click()
        page.wait_for_timeout(2000)

    if page.locator("#user_login").is_visible():
        print("On login page, entering credentials...")
        page.fill("#user_login", WP_USER)
        page.fill("#user_pass", WP_PASS)
        print("Clicking Log In button...")
        page.click("#wp-submit")

        try:
            page.wait_for_url("**/wp-admin/**", timeout=15000)
        except:
            pass

        page.wait_for_timeout(3000)

    print(f"Current URL after login: {page.url}")
    return "wp-admin" in page.url

def update_purebrain_page_via_api(page):
    """Update Pure Brain 2.0 page (ID 174) via REST API"""
    print("\n=== Updating Pure Brain 2.0 via REST API ===")

    # Go to admin to get nonce
    page.goto("https://purebrain.ai/wp-admin/", wait_until="domcontentloaded")
    page.wait_for_timeout(2000)

    # Escape PAYPAL_SECTION for JavaScript
    paypal_escaped = PAYPAL_SECTION.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')

    # Use JavaScript to:
    # 1. Fetch current content
    # 2. Add PayPal section before </body>
    # 3. Update via REST API
    result = page.evaluate(f'''
        async () => {{
            try {{
                const nonce = window.wpApiSettings?.nonce;
                if (!nonce) {{
                    return {{ success: false, error: 'No nonce found' }};
                }}

                // Get current page content
                const getResp = await fetch('/wp-json/wp/v2/pages/174', {{
                    headers: {{ 'X-WP-Nonce': nonce }}
                }});

                if (!getResp.ok) {{
                    return {{ success: false, error: 'Failed to get page: ' + getResp.status }};
                }}

                const pageData = await getResp.json();
                let content = pageData.content.raw || pageData.content.rendered || '';

                // Check if PayPal buttons already exist
                if (content.includes('paypal.com/cgi-bin/webscr')) {{
                    return {{ success: true, message: 'PayPal buttons already exist', alreadyDone: true }};
                }}

                // Add PayPal section before </body>
                const paypalSection = `{paypal_escaped}`;

                if (content.includes('</body>')) {{
                    content = content.replace('</body>', paypalSection + '\\n</body>');
                }} else {{
                    // Just append
                    content = content + '\\n' + paypalSection;
                }}

                // Update the page
                const updateResp = await fetch('/wp-json/wp/v2/pages/174', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                        'X-WP-Nonce': nonce
                    }},
                    body: JSON.stringify({{
                        content: content
                    }})
                }});

                if (updateResp.ok) {{
                    const updated = await updateResp.json();
                    return {{ success: true, message: 'Page updated', id: updated.id }};
                }} else {{
                    const error = await updateResp.text();
                    return {{ success: false, error: error, status: updateResp.status }};
                }}

            }} catch (e) {{
                return {{ success: false, error: e.toString() }};
            }}
        }}
    ''')

    print(f"API result: {result}")
    return result.get('success', False)

def verify_pages(page):
    """Verify both pages are working"""
    print("\n=== Verification ===")

    # Check Thank You page
    print("\n1. Checking Thank You page...")
    page.goto("https://purebrain.ai/thank-you/", wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    screenshot(page, "v3-verify-thankyou")

    title = page.title()
    print(f"   Title: {title}")

    is_404 = page.locator("text=Page not found, text=404, text=Not Found").count() > 0
    if is_404:
        print("   STATUS: 404 - Page not found")
    else:
        body = page.locator("body").text_content()
        if "Thank You" in body or "Pure Brain" in body or "payment" in body.lower():
            print("   STATUS: OK - Content found")
        else:
            print("   STATUS: Page exists but content unclear")

    # Check Pure Brain 2.0 page
    print("\n2. Checking Pure Brain 2.0 page...")
    page.goto("https://purebrain.ai/purebrain-2-0/", wait_until="domcontentloaded")
    page.wait_for_timeout(5000)
    screenshot(page, "v3-verify-purebrain20-top")

    # Scroll through the page to find PayPal buttons
    for i in range(10):
        page.evaluate(f"window.scrollBy(0, 500)")
        page.wait_for_timeout(300)

    screenshot(page, "v3-verify-purebrain20-bottom")

    # Check for PayPal buttons
    paypal_forms = page.locator("form[action*='paypal']").count()
    print(f"   PayPal forms found: {paypal_forms}")

    # Check if buttons are visible
    paypal_buttons = page.locator("button:has-text('$79'), button:has-text('$149'), button:has-text('$499'), button:has-text('$999')")
    button_count = paypal_buttons.count()
    print(f"   PayPal buy buttons found: {button_count}")

    if paypal_forms > 0 or button_count > 0:
        print("   STATUS: OK - PayPal buttons present")
    else:
        print("   STATUS: PayPal buttons NOT found")

    return paypal_forms > 0 or button_count > 0

def main():
    print("=" * 60)
    print("PayPal Integration v3 for purebrain.ai")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        try:
            # Login
            if not login(page):
                print("Login may have failed")
                screenshot(page, "v3-login-state")

            # Update Pure Brain 2.0 page
            update_purebrain_page_via_api(page)

            # Verify
            verify_pages(page)

        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            screenshot(page, "v3-error")
        finally:
            browser.close()

    print("\n" + "=" * 60)
    print("Done! Screenshots saved to /tmp/paypal-integration-*.png")
    print("=" * 60)

if __name__ == "__main__":
    main()
