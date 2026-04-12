#!/usr/bin/env python3
"""
Update Elementor data to add PayPal buttons
"""

import json
from playwright.sync_api import sync_playwright

WP_USER = "Purebrain@puremarketing.ai"
WP_PASS = "NW2u!JLQ3!Bt$XD$7CWzz5Z@"

PAYPAL_SECTION = '''
<!-- PayPal Purchase Section - Added by Aether -->
<section id="paypal-purchase-buttons" style="padding: 80px 20px; background: linear-gradient(180deg, rgba(10,10,10,0.95) 0%, rgba(20,20,20,0.98) 100%);">
  <div style="max-width: 1200px; margin: 0 auto; text-align: center;">
    <h2 style="font-family: 'Oswald', sans-serif; color: #f1420b; font-size: 48px; margin-bottom: 20px; text-transform: uppercase; letter-spacing: 2px;">Start Your Journey</h2>
    <p style="color: #888; font-size: 18px; margin-bottom: 50px; max-width: 600px; margin-left: auto; margin-right: auto;">Choose your Pure Brain package and awaken your personal AI partner today.</p>
    <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 30px;">
      <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(241,66,11,0.2); border-radius: 20px; padding: 40px 30px; width: 280px; transition: all 0.3s ease;">
        <h3 style="font-family: 'Oswald', sans-serif; color: #fff; font-size: 26px; margin-bottom: 10px; letter-spacing: 1px;">STARTER</h3>
        <p style="color: #f1420b; font-size: 48px; font-weight: 700; margin-bottom: 20px;">$79</p>
        <p style="color: #666; font-size: 14px; margin-bottom: 30px; line-height: 1.6;">Perfect for individuals ready to explore AI partnership</p>
        <form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_blank"><input type="hidden" name="cmd" value="_xclick"><input type="hidden" name="business" value="support@puremarketing.ai"><input type="hidden" name="item_name" value="Pure Brain Starter"><input type="hidden" name="item_number" value="PB-STARTER"><input type="hidden" name="amount" value="79.00"><input type="hidden" name="currency_code" value="USD"><input type="hidden" name="no_shipping" value="1"><input type="hidden" name="return" value="https://purebrain.ai/thank-you/"><input type="hidden" name="cancel_return" value="https://purebrain.ai/purebrain-2-0/"><button type="submit" style="background: linear-gradient(135deg, #f1420b 0%, #ff6b3d 100%); color: #fff; border: none; padding: 16px 40px; font-size: 16px; font-weight: 600; border-radius: 10px; cursor: pointer; width: 100%; transition: transform 0.2s, box-shadow 0.2s; box-shadow: 0 4px 20px rgba(241,66,11,0.3);">Get Started</button></form>
      </div>
      <div style="background: rgba(241,66,11,0.05); border: 2px solid #f1420b; border-radius: 20px; padding: 40px 30px; width: 280px; position: relative; transform: scale(1.02);">
        <div style="position: absolute; top: -14px; left: 50%; transform: translateX(-50%); background: linear-gradient(135deg, #f1420b, #ff6b3d); color: #fff; padding: 6px 20px; border-radius: 20px; font-size: 12px; font-weight: 700; letter-spacing: 1px;">MOST POPULAR</div>
        <h3 style="font-family: 'Oswald', sans-serif; color: #fff; font-size: 26px; margin-bottom: 10px; letter-spacing: 1px;">PRO</h3>
        <p style="color: #f1420b; font-size: 48px; font-weight: 700; margin-bottom: 20px;">$149</p>
        <p style="color: #666; font-size: 14px; margin-bottom: 30px; line-height: 1.6;">Our most popular choice for serious AI adopters</p>
        <form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_blank"><input type="hidden" name="cmd" value="_xclick"><input type="hidden" name="business" value="support@puremarketing.ai"><input type="hidden" name="item_name" value="Pure Brain Pro"><input type="hidden" name="item_number" value="PB-PRO"><input type="hidden" name="amount" value="149.00"><input type="hidden" name="currency_code" value="USD"><input type="hidden" name="no_shipping" value="1"><input type="hidden" name="return" value="https://purebrain.ai/thank-you/"><input type="hidden" name="cancel_return" value="https://purebrain.ai/purebrain-2-0/"><button type="submit" style="background: linear-gradient(135deg, #f1420b 0%, #ff6b3d 100%); color: #fff; border: none; padding: 16px 40px; font-size: 16px; font-weight: 600; border-radius: 10px; cursor: pointer; width: 100%; transition: transform 0.2s, box-shadow 0.2s; box-shadow: 0 6px 25px rgba(241,66,11,0.4);">Go Pro</button></form>
      </div>
      <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(241,66,11,0.2); border-radius: 20px; padding: 40px 30px; width: 280px; transition: all 0.3s ease;">
        <h3 style="font-family: 'Oswald', sans-serif; color: #fff; font-size: 26px; margin-bottom: 10px; letter-spacing: 1px;">ENTERPRISE</h3>
        <p style="color: #f1420b; font-size: 48px; font-weight: 700; margin-bottom: 20px;">$499</p>
        <p style="color: #666; font-size: 14px; margin-bottom: 30px; line-height: 1.6;">Full power for teams and growing businesses</p>
        <form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_blank"><input type="hidden" name="cmd" value="_xclick"><input type="hidden" name="business" value="support@puremarketing.ai"><input type="hidden" name="item_name" value="Pure Brain Enterprise"><input type="hidden" name="item_number" value="PB-ENTERPRISE"><input type="hidden" name="amount" value="499.00"><input type="hidden" name="currency_code" value="USD"><input type="hidden" name="no_shipping" value="1"><input type="hidden" name="return" value="https://purebrain.ai/thank-you/"><input type="hidden" name="cancel_return" value="https://purebrain.ai/purebrain-2-0/"><button type="submit" style="background: linear-gradient(135deg, #f1420b 0%, #ff6b3d 100%); color: #fff; border: none; padding: 16px 40px; font-size: 16px; font-weight: 600; border-radius: 10px; cursor: pointer; width: 100%; transition: transform 0.2s, box-shadow 0.2s; box-shadow: 0 4px 20px rgba(241,66,11,0.3);">Enterprise</button></form>
      </div>
      <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(241,66,11,0.2); border-radius: 20px; padding: 40px 30px; width: 280px; transition: all 0.3s ease;">
        <h3 style="font-family: 'Oswald', sans-serif; color: #fff; font-size: 26px; margin-bottom: 10px; letter-spacing: 1px;">ULTIMATE</h3>
        <p style="color: #f1420b; font-size: 48px; font-weight: 700; margin-bottom: 20px;">$999</p>
        <p style="color: #666; font-size: 14px; margin-bottom: 30px; line-height: 1.6;">The complete solution with priority everything</p>
        <form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_blank"><input type="hidden" name="cmd" value="_xclick"><input type="hidden" name="business" value="support@puremarketing.ai"><input type="hidden" name="item_name" value="Pure Brain Ultimate"><input type="hidden" name="item_number" value="PB-ULTIMATE"><input type="hidden" name="amount" value="999.00"><input type="hidden" name="currency_code" value="USD"><input type="hidden" name="no_shipping" value="1"><input type="hidden" name="return" value="https://purebrain.ai/thank-you/"><input type="hidden" name="cancel_return" value="https://purebrain.ai/purebrain-2-0/"><button type="submit" style="background: linear-gradient(135deg, #f1420b 0%, #ff6b3d 100%); color: #fff; border: none; padding: 16px 40px; font-size: 16px; font-weight: 600; border-radius: 10px; cursor: pointer; width: 100%; transition: transform 0.2s, box-shadow 0.2s; box-shadow: 0 4px 20px rgba(241,66,11,0.3);">Ultimate</button></form>
      </div>
    </div>
  </div>
</section>
'''

def login(page):
    page.goto("https://purebrain.ai/wp-admin/", wait_until="domcontentloaded")
    page.wait_for_timeout(2000)

    pw_link = page.get_by_text("Log in with username and password")
    if pw_link.count() > 0:
        pw_link.click()
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

    return "wp-admin" in page.url

def update_elementor_data(page):
    """Update Elementor data via REST API"""

    # Escape PayPal section for JavaScript string
    paypal_escaped = PAYPAL_SECTION.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')

    result = page.evaluate(f'''
        async () => {{
            const nonce = window.wpApiSettings?.nonce;
            if (!nonce) return {{ error: 'No nonce' }};

            // Get current Elementor data
            const getResp = await fetch('/wp-json/wp/v2/pages/174?context=edit', {{
                headers: {{ 'X-WP-Nonce': nonce }}
            }});

            if (!getResp.ok) return {{ error: 'Failed to fetch: ' + getResp.status }};

            const pageData = await getResp.json();
            let elementorData = pageData.meta?._elementor_data;

            if (!elementorData) return {{ error: 'No Elementor data found' }};

            // Parse the Elementor data (it's a JSON string)
            let parsed;
            try {{
                parsed = JSON.parse(elementorData);
            }} catch (e) {{
                return {{ error: 'Failed to parse Elementor data: ' + e }};
            }}

            // The structure has one container with one HTML widget
            // We need to find the HTML widget and modify its content
            if (!parsed[0] || !parsed[0].elements || !parsed[0].elements[0]) {{
                return {{ error: 'Unexpected Elementor structure' }};
            }}

            const htmlWidget = parsed[0].elements[0];
            if (htmlWidget.elType !== 'widget' || !htmlWidget.settings?.html) {{
                return {{ error: 'First element is not an HTML widget' }};
            }}

            let htmlContent = htmlWidget.settings.html;

            // Check if PayPal already exists
            if (htmlContent.includes('paypal.com/cgi-bin/webscr')) {{
                return {{ success: true, message: 'PayPal buttons already exist' }};
            }}

            // Find insertion point - before </body>
            const paypalSection = `{paypal_escaped}`;

            if (htmlContent.includes('</body>')) {{
                htmlContent = htmlContent.replace('</body>', paypalSection + '\\n</body>');
            }} else {{
                // Append
                htmlContent += paypalSection;
            }}

            // Update the widget content
            htmlWidget.settings.html = htmlContent;

            // Convert back to JSON string
            const newElementorData = JSON.stringify(parsed);

            // Update via REST API
            const updateResp = await fetch('/wp-json/wp/v2/pages/174', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                    'X-WP-Nonce': nonce
                }},
                body: JSON.stringify({{
                    meta: {{
                        _elementor_data: newElementorData
                    }}
                }})
            }});

            if (!updateResp.ok) {{
                const err = await updateResp.text();
                return {{ error: 'Update failed: ' + updateResp.status + ' - ' + err.substring(0, 200) }};
            }}

            return {{ success: true, message: 'Elementor data updated' }};
        }}
    ''')

    return result

def verify(page):
    """Check if PayPal buttons appear on the page"""
    page.goto("https://purebrain.ai/purebrain-2-0/", wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    # Scroll to bottom
    for _ in range(20):
        page.evaluate("window.scrollBy(0, 400)")
        page.wait_for_timeout(150)

    # Take screenshot
    page.screenshot(path="/tmp/paypal-verify-final.png", full_page=True)

    # Check for PayPal
    paypal_forms = page.locator("form[action*='paypal']").count()
    html = page.content()
    has_paypal = 'paypal.com/cgi-bin/webscr' in html

    return paypal_forms > 0 or has_paypal, paypal_forms

def main():
    print("PayPal Button Integration via Elementor Data Update")
    print("=" * 55)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        try:
            print("1. Logging in...")
            if not login(page):
                print("   FAILED")
                return
            print("   OK")

            print("2. Updating Elementor data...")
            result = update_elementor_data(page)
            print(f"   Result: {result}")

            print("3. Verifying...")
            page.wait_for_timeout(2000)
            success, count = verify(page)
            print(f"   PayPal forms found: {count}")
            print(f"   Success: {success}")

            if success:
                print("\n*** SUCCESS: PayPal buttons are now on the page! ***")
            else:
                print("\n*** PayPal buttons NOT found on front-end ***")
                print("   This may require Elementor cache clear or manual save")

            # Also verify Thank You page
            print("\n4. Verifying Thank You page...")
            page.goto("https://purebrain.ai/thank-you/", wait_until="domcontentloaded")
            page.wait_for_timeout(3000)
            page.screenshot(path="/tmp/paypal-thankyou-final.png")

            title = page.title()
            is_404 = "not found" in page.content().lower() or "404" in title
            print(f"   Title: {title}")
            print(f"   Is 404: {is_404}")
            print(f"   Status: {'FAIL' if is_404 else 'OK'}")

        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            browser.close()

    print("\nScreenshots saved to /tmp/paypal-*.png")

if __name__ == "__main__":
    main()
