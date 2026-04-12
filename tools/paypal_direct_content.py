#!/usr/bin/env python3
"""
Update the page content directly to add PayPal buttons
This updates the actual post_content which should be rendered
"""

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

def update_page_content(page):
    """Update page content directly via REST API"""
    paypal_escaped = PAYPAL_SECTION.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')

    result = page.evaluate(f'''
        async () => {{
            const nonce = window.wpApiSettings?.nonce;
            if (!nonce) return {{ error: 'No nonce' }};

            // Get current page content
            const getResp = await fetch('/wp-json/wp/v2/pages/174?context=edit', {{
                headers: {{ 'X-WP-Nonce': nonce }}
            }});

            if (!getResp.ok) return {{ error: 'Fetch failed: ' + getResp.status }};

            const data = await getResp.json();
            let content = data.content?.raw || data.content?.rendered || '';

            // Check if PayPal already in content
            if (content.includes('paypal.com/cgi-bin/webscr')) {{
                return {{ success: true, message: 'PayPal already in content' }};
            }}

            // Append PayPal section
            const paypalSection = `{paypal_escaped}`;
            content = content + '\\n' + paypalSection;

            // Update via REST API
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

            if (!updateResp.ok) {{
                const err = await updateResp.text();
                return {{ error: 'Update failed: ' + updateResp.status + ' ' + err.substring(0, 200) }};
            }}

            return {{ success: true, message: 'Content updated' }};
        }}
    ''')

    return result

def try_add_shortcode(page):
    """Try adding shortcode approach - create a reusable PayPal block"""
    print("Creating standalone PayPal shortcode block...")

    paypal_escaped = PAYPAL_SECTION.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')

    # Create a new page that just has the PayPal section
    result = page.evaluate(f'''
        async () => {{
            const nonce = window.wpApiSettings?.nonce;
            if (!nonce) return {{ error: 'No nonce' }};

            // Create a standalone PayPal page we can embed
            const createResp = await fetch('/wp-json/wp/v2/pages', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                    'X-WP-Nonce': nonce
                }},
                body: JSON.stringify({{
                    title: 'PayPal Buttons (Embed)',
                    content: `{paypal_escaped}`,
                    status: 'publish',
                    slug: 'paypal-buttons-embed'
                }})
            }});

            if (createResp.ok) {{
                const data = await createResp.json();
                return {{ success: true, page_id: data.id, url: data.link }};
            }}

            const err = await createResp.text();
            return {{ error: 'Create failed: ' + err.substring(0, 200) }};
        }}
    ''')

    return result

def verify(page):
    """Check front-end"""
    page.goto("https://purebrain.ai/purebrain-2-0/", wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    for _ in range(25):
        page.evaluate("window.scrollBy(0, 300)")
        page.wait_for_timeout(100)

    page.screenshot(path="/tmp/paypal-direct-verify.png", full_page=True)

    forms = page.locator("form[action*='paypal']").count()
    html = page.content()

    return forms > 0 or 'paypal.com/cgi-bin/webscr' in html, forms

def main():
    print("Direct Content Update for PayPal Buttons")
    print("=" * 45)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_context(viewport={'width': 1920, 'height': 1080}).new_page()

        try:
            print("1. Login...")
            if not login(page):
                print("   FAILED")
                return
            print("   OK")

            print("2. Update page content...")
            result = update_page_content(page)
            print(f"   Result: {result}")

            print("3. Create standalone PayPal page...")
            result2 = try_add_shortcode(page)
            print(f"   Result: {result2}")

            print("4. Verify...")
            success, count = verify(page)
            print(f"   Forms found: {count}")

            # Check if standalone page works
            if result2.get('success'):
                print(f"\n5. Check standalone PayPal page...")
                page.goto(result2['url'], wait_until="domcontentloaded")
                page.wait_for_timeout(3000)
                page.screenshot(path="/tmp/paypal-standalone.png")
                standalone_forms = page.locator("form[action*='paypal']").count()
                print(f"   Standalone PayPal forms: {standalone_forms}")

                if standalone_forms > 0:
                    print(f"\n*** PayPal buttons are available at: {result2['url']} ***")
                    print("   This page can be linked from the main pricing page or embedded via iframe.")

            # Verify thank you page
            print("\n6. Verify Thank You page...")
            page.goto("https://purebrain.ai/thank-you/", wait_until="domcontentloaded")
            page.wait_for_timeout(3000)
            page.screenshot(path="/tmp/paypal-thankyou-verify.png")
            title = page.title()
            print(f"   Title: {title}")
            print(f"   Status: {'OK' if 'Thank You' in title else 'Check'}")

        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            browser.close()

if __name__ == "__main__":
    main()
