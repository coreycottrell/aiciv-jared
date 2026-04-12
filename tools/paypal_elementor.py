#!/usr/bin/env python3
"""
Add PayPal buttons to Pure Brain 2.0 via Elementor
"""

from playwright.sync_api import sync_playwright

SCREENSHOT_DIR = "/tmp"
WP_USER = "Purebrain@puremarketing.ai"
WP_PASS = "NW2u!JLQ3!Bt$XD$7CWzz5Z@"

# PayPal HTML for each tier
PAYPAL_HTML = '''
<div style="text-align: center; padding: 20px;">
  <form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_blank" style="display: inline-block;">
    <input type="hidden" name="cmd" value="_xclick">
    <input type="hidden" name="business" value="support@puremarketing.ai">
    <input type="hidden" name="item_name" value="Pure Brain {TIER}">
    <input type="hidden" name="item_number" value="PB-{TIER_UPPER}">
    <input type="hidden" name="amount" value="{PRICE}">
    <input type="hidden" name="currency_code" value="USD">
    <input type="hidden" name="no_shipping" value="1">
    <input type="hidden" name="return" value="https://purebrain.ai/thank-you/">
    <input type="hidden" name="cancel_return" value="https://purebrain.ai/purebrain-2-0/">
    <button type="submit" style="background: linear-gradient(135deg, #f1420b 0%, #ff6b3d 100%); color: white; border: none; padding: 16px 40px; font-size: 18px; font-weight: bold; border-radius: 8px; cursor: pointer; box-shadow: 0 4px 15px rgba(241, 66, 11, 0.4);">{BUTTON_TEXT}</button>
  </form>
</div>
'''

def screenshot(page, name):
    path = f"{SCREENSHOT_DIR}/paypal-elem-{name}.png"
    page.screenshot(path=path, full_page=False)
    print(f"Screenshot: {path}")
    return path

def login(page):
    print("Logging in...")
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

def open_elementor(page):
    """Open page in Elementor editor"""
    print("Opening Elementor editor...")
    # Direct URL to Elementor editor for page 174
    page.goto("https://purebrain.ai/wp-admin/post.php?post=174&action=elementor", wait_until="domcontentloaded")

    # Wait for Elementor to load
    print("Waiting for Elementor to load...")
    page.wait_for_timeout(10000)  # Elementor takes time

    # Check if Elementor loaded
    is_elementor = page.locator("#elementor-panel, .elementor-editor-active").count() > 0
    print(f"Elementor loaded: {is_elementor}")

    screenshot(page, "01-elementor-loaded")
    return is_elementor

def add_paypal_section_via_js(page):
    """Add PayPal section using JavaScript to modify Elementor data"""
    print("\nAttempting to add PayPal section via JavaScript...")

    # Create the PayPal section HTML
    paypal_section = '''
<section id="paypal-purchase-section" style="padding: 60px 20px; background: linear-gradient(180deg, rgba(0,0,0,0.5) 0%, rgba(20,20,20,0.9) 100%);">
  <div style="max-width: 1200px; margin: 0 auto; text-align: center;">
    <h2 style="font-family: 'Oswald', sans-serif; color: #f1420b; font-size: 42px; margin-bottom: 15px; text-transform: uppercase;">Ready to Start?</h2>
    <p style="color: #cccccc; font-size: 18px; margin-bottom: 40px;">Choose your Pure Brain package and begin your AI journey today.</p>

    <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 24px;">

      <!-- Starter -->
      <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(241,66,11,0.3); border-radius: 16px; padding: 32px; width: 260px; text-align: center;">
        <h3 style="font-family: 'Oswald', sans-serif; color: #ffffff; font-size: 24px; margin-bottom: 8px;">STARTER</h3>
        <p style="color: #f1420b; font-size: 42px; font-weight: 700; margin-bottom: 16px;">$79</p>
        <p style="color: #888; font-size: 14px; margin-bottom: 24px;">Perfect for getting started</p>
        <form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_blank">
          <input type="hidden" name="cmd" value="_xclick">
          <input type="hidden" name="business" value="support@puremarketing.ai">
          <input type="hidden" name="item_name" value="Pure Brain Starter">
          <input type="hidden" name="item_number" value="PB-STARTER">
          <input type="hidden" name="amount" value="79.00">
          <input type="hidden" name="currency_code" value="USD">
          <input type="hidden" name="no_shipping" value="1">
          <input type="hidden" name="return" value="https://purebrain.ai/thank-you/">
          <input type="hidden" name="cancel_return" value="https://purebrain.ai/purebrain-2-0/">
          <button type="submit" style="background: linear-gradient(135deg, #f1420b 0%, #ff6b3d 100%); color: white; border: none; padding: 14px 32px; font-size: 16px; font-weight: 600; border-radius: 8px; cursor: pointer; width: 100%;">Get Started</button>
        </form>
      </div>

      <!-- Pro -->
      <div style="background: rgba(255,255,255,0.03); border: 2px solid #f1420b; border-radius: 16px; padding: 32px; width: 260px; text-align: center; position: relative;">
        <div style="position: absolute; top: -12px; left: 50%; transform: translateX(-50%); background: #f1420b; color: white; padding: 4px 16px; border-radius: 20px; font-size: 12px; font-weight: 600;">POPULAR</div>
        <h3 style="font-family: 'Oswald', sans-serif; color: #ffffff; font-size: 24px; margin-bottom: 8px;">PRO</h3>
        <p style="color: #f1420b; font-size: 42px; font-weight: 700; margin-bottom: 16px;">$149</p>
        <p style="color: #888; font-size: 14px; margin-bottom: 24px;">Most popular choice</p>
        <form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_blank">
          <input type="hidden" name="cmd" value="_xclick">
          <input type="hidden" name="business" value="support@puremarketing.ai">
          <input type="hidden" name="item_name" value="Pure Brain Pro">
          <input type="hidden" name="item_number" value="PB-PRO">
          <input type="hidden" name="amount" value="149.00">
          <input type="hidden" name="currency_code" value="USD">
          <input type="hidden" name="no_shipping" value="1">
          <input type="hidden" name="return" value="https://purebrain.ai/thank-you/">
          <input type="hidden" name="cancel_return" value="https://purebrain.ai/purebrain-2-0/">
          <button type="submit" style="background: linear-gradient(135deg, #f1420b 0%, #ff6b3d 100%); color: white; border: none; padding: 14px 32px; font-size: 16px; font-weight: 600; border-radius: 8px; cursor: pointer; width: 100%;">Go Pro</button>
        </form>
      </div>

      <!-- Enterprise -->
      <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(241,66,11,0.3); border-radius: 16px; padding: 32px; width: 260px; text-align: center;">
        <h3 style="font-family: 'Oswald', sans-serif; color: #ffffff; font-size: 24px; margin-bottom: 8px;">ENTERPRISE</h3>
        <p style="color: #f1420b; font-size: 42px; font-weight: 700; margin-bottom: 16px;">$499</p>
        <p style="color: #888; font-size: 14px; margin-bottom: 24px;">For growing teams</p>
        <form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_blank">
          <input type="hidden" name="cmd" value="_xclick">
          <input type="hidden" name="business" value="support@puremarketing.ai">
          <input type="hidden" name="item_name" value="Pure Brain Enterprise">
          <input type="hidden" name="item_number" value="PB-ENTERPRISE">
          <input type="hidden" name="amount" value="499.00">
          <input type="hidden" name="currency_code" value="USD">
          <input type="hidden" name="no_shipping" value="1">
          <input type="hidden" name="return" value="https://purebrain.ai/thank-you/">
          <input type="hidden" name="cancel_return" value="https://purebrain.ai/purebrain-2-0/">
          <button type="submit" style="background: linear-gradient(135deg, #f1420b 0%, #ff6b3d 100%); color: white; border: none; padding: 14px 32px; font-size: 16px; font-weight: 600; border-radius: 8px; cursor: pointer; width: 100%;">Enterprise</button>
        </form>
      </div>

      <!-- Ultimate -->
      <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(241,66,11,0.3); border-radius: 16px; padding: 32px; width: 260px; text-align: center;">
        <h3 style="font-family: 'Oswald', sans-serif; color: #ffffff; font-size: 24px; margin-bottom: 8px;">ULTIMATE</h3>
        <p style="color: #f1420b; font-size: 42px; font-weight: 700; margin-bottom: 16px;">$999</p>
        <p style="color: #888; font-size: 14px; margin-bottom: 24px;">Full-featured solution</p>
        <form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_blank">
          <input type="hidden" name="cmd" value="_xclick">
          <input type="hidden" name="business" value="support@puremarketing.ai">
          <input type="hidden" name="item_name" value="Pure Brain Ultimate">
          <input type="hidden" name="item_number" value="PB-ULTIMATE">
          <input type="hidden" name="amount" value="999.00">
          <input type="hidden" name="currency_code" value="USD">
          <input type="hidden" name="no_shipping" value="1">
          <input type="hidden" name="return" value="https://purebrain.ai/thank-you/">
          <input type="hidden" name="cancel_return" value="https://purebrain.ai/purebrain-2-0/">
          <button type="submit" style="background: linear-gradient(135deg, #f1420b 0%, #ff6b3d 100%); color: white; border: none; padding: 14px 32px; font-size: 16px; font-weight: 600; border-radius: 8px; cursor: pointer; width: 100%;">Ultimate</button>
        </form>
      </div>

    </div>
  </div>
</section>
'''

    # Escape for JavaScript
    paypal_section_escaped = paypal_section.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$').replace('\n', '\\n')

    # This approach won't work directly with Elementor - Elementor requires its own widget system
    # Instead, let's check if we can find where to inject or if there's an existing HTML widget
    result = page.evaluate('''
        async () => {
            // Check if we're in Elementor
            if (typeof elementor === 'undefined') {
                return { error: 'Elementor not loaded' };
            }

            // Get all elements
            const elements = elementor.elements.models;
            let htmlWidgets = [];

            // Recursively find HTML widgets
            function findHtmlWidgets(models, path = '') {
                models.forEach((model, index) => {
                    const type = model.get('widgetType') || model.get('elType');
                    if (type === 'html') {
                        htmlWidgets.push({
                            id: model.get('id'),
                            path: path + '/' + index,
                            content: model.get('settings')?.get('html')?.substring(0, 100) || ''
                        });
                    }
                    // Check children
                    const children = model.get('elements');
                    if (children && children.models) {
                        findHtmlWidgets(children.models, path + '/' + index);
                    }
                });
            }

            findHtmlWidgets(elements);

            return {
                totalElements: elements.length,
                htmlWidgets: htmlWidgets,
                elementorVersion: elementor.config?.version
            };
        }
    ''')

    print(f"Elementor analysis: {result}")
    return result

def try_direct_html_injection(page):
    """Try to inject HTML directly into an existing HTML widget in Elementor"""
    print("\nTrying direct injection approach...")

    # First, search for existing HTML widgets that might contain pricing
    result = page.evaluate('''
        async () => {
            if (typeof elementor === 'undefined') return { error: 'No Elementor' };

            // Find all HTML widgets
            let htmlWidgets = [];
            function searchElements(container) {
                container.models.forEach(model => {
                    if (model.get('widgetType') === 'html') {
                        const settings = model.get('settings');
                        const html = settings?.get('html') || '';
                        // Check if this contains pricing-related content
                        if (html.includes('$79') || html.includes('$149') || html.includes('$499') || html.includes('$999') ||
                            html.toLowerCase().includes('pricing') || html.toLowerCase().includes('starter') ||
                            html.toLowerCase().includes('enterprise')) {
                            htmlWidgets.push({
                                id: model.get('id'),
                                preview: html.substring(0, 200)
                            });
                        }
                    }
                    // Check nested elements
                    const children = model.get('elements');
                    if (children && children.models && children.models.length > 0) {
                        searchElements(children);
                    }
                });
            }

            searchElements(elementor.elements);
            return { found: htmlWidgets };
        }
    ''')

    print(f"Pricing widgets found: {result}")
    return result

def add_widget_at_end(page):
    """Add a new HTML widget at the end of the page"""
    print("\nAdding new HTML widget at end of page...")

    # First let's see the page structure in the preview
    page.goto("https://purebrain.ai/wp-admin/post.php?post=174&action=elementor", wait_until="domcontentloaded")
    page.wait_for_timeout(15000)

    screenshot(page, "02-elementor-ready")

    # Try to use Elementor's API to add a section
    result = page.evaluate('''
        async () => {
            if (typeof elementor === 'undefined') {
                return { error: 'Elementor not loaded' };
            }

            try {
                // Create new section at the end
                const newSectionModel = elementor.elements.add({
                    elType: 'section',
                    settings: {
                        layout: 'full_width',
                        padding: { unit: 'px', top: 60, right: 20, bottom: 60, left: 20 },
                        background_background: 'classic',
                        background_color: 'rgba(0,0,0,0.3)'
                    }
                });

                if (!newSectionModel) {
                    return { error: 'Failed to create section' };
                }

                // Add a column
                const column = newSectionModel.get('elements').add({
                    elType: 'column',
                    settings: {
                        _column_size: 100
                    }
                });

                // Add HTML widget with PayPal buttons
                const paypalHtml = `<section id="paypal-purchase-section" style="padding: 60px 20px;">
  <div style="max-width: 1200px; margin: 0 auto; text-align: center;">
    <h2 style="font-family: 'Oswald', sans-serif; color: #f1420b; font-size: 42px; margin-bottom: 15px; text-transform: uppercase;">Ready to Start?</h2>
    <p style="color: #cccccc; font-size: 18px; margin-bottom: 40px;">Choose your Pure Brain package and begin your AI journey today.</p>

    <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 24px;">

      <!-- Starter -->
      <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(241,66,11,0.3); border-radius: 16px; padding: 32px; width: 260px; text-align: center;">
        <h3 style="font-family: 'Oswald', sans-serif; color: #ffffff; font-size: 24px; margin-bottom: 8px;">STARTER</h3>
        <p style="color: #f1420b; font-size: 42px; font-weight: 700; margin-bottom: 16px;">$79</p>
        <form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_blank">
          <input type="hidden" name="cmd" value="_xclick">
          <input type="hidden" name="business" value="support@puremarketing.ai">
          <input type="hidden" name="item_name" value="Pure Brain Starter">
          <input type="hidden" name="item_number" value="PB-STARTER">
          <input type="hidden" name="amount" value="79.00">
          <input type="hidden" name="currency_code" value="USD">
          <input type="hidden" name="no_shipping" value="1">
          <input type="hidden" name="return" value="https://purebrain.ai/thank-you/">
          <input type="hidden" name="cancel_return" value="https://purebrain.ai/purebrain-2-0/">
          <button type="submit" style="background: linear-gradient(135deg, #f1420b 0%, #ff6b3d 100%); color: white; border: none; padding: 14px 32px; font-size: 16px; font-weight: 600; border-radius: 8px; cursor: pointer; width: 100%;">Get Started - $79</button>
        </form>
      </div>

      <!-- Pro -->
      <div style="background: rgba(255,255,255,0.03); border: 2px solid #f1420b; border-radius: 16px; padding: 32px; width: 260px; text-align: center; position: relative;">
        <div style="position: absolute; top: -12px; left: 50%; transform: translateX(-50%); background: #f1420b; color: white; padding: 4px 16px; border-radius: 20px; font-size: 12px; font-weight: 600;">POPULAR</div>
        <h3 style="font-family: 'Oswald', sans-serif; color: #ffffff; font-size: 24px; margin-bottom: 8px;">PRO</h3>
        <p style="color: #f1420b; font-size: 42px; font-weight: 700; margin-bottom: 16px;">$149</p>
        <form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_blank">
          <input type="hidden" name="cmd" value="_xclick">
          <input type="hidden" name="business" value="support@puremarketing.ai">
          <input type="hidden" name="item_name" value="Pure Brain Pro">
          <input type="hidden" name="item_number" value="PB-PRO">
          <input type="hidden" name="amount" value="149.00">
          <input type="hidden" name="currency_code" value="USD">
          <input type="hidden" name="no_shipping" value="1">
          <input type="hidden" name="return" value="https://purebrain.ai/thank-you/">
          <input type="hidden" name="cancel_return" value="https://purebrain.ai/purebrain-2-0/">
          <button type="submit" style="background: linear-gradient(135deg, #f1420b 0%, #ff6b3d 100%); color: white; border: none; padding: 14px 32px; font-size: 16px; font-weight: 600; border-radius: 8px; cursor: pointer; width: 100%;">Go Pro - $149</button>
        </form>
      </div>

      <!-- Enterprise -->
      <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(241,66,11,0.3); border-radius: 16px; padding: 32px; width: 260px; text-align: center;">
        <h3 style="font-family: 'Oswald', sans-serif; color: #ffffff; font-size: 24px; margin-bottom: 8px;">ENTERPRISE</h3>
        <p style="color: #f1420b; font-size: 42px; font-weight: 700; margin-bottom: 16px;">$499</p>
        <form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_blank">
          <input type="hidden" name="cmd" value="_xclick">
          <input type="hidden" name="business" value="support@puremarketing.ai">
          <input type="hidden" name="item_name" value="Pure Brain Enterprise">
          <input type="hidden" name="item_number" value="PB-ENTERPRISE">
          <input type="hidden" name="amount" value="499.00">
          <input type="hidden" name="currency_code" value="USD">
          <input type="hidden" name="no_shipping" value="1">
          <input type="hidden" name="return" value="https://purebrain.ai/thank-you/">
          <input type="hidden" name="cancel_return" value="https://purebrain.ai/purebrain-2-0/">
          <button type="submit" style="background: linear-gradient(135deg, #f1420b 0%, #ff6b3d 100%); color: white; border: none; padding: 14px 32px; font-size: 16px; font-weight: 600; border-radius: 8px; cursor: pointer; width: 100%;">Enterprise - $499</button>
        </form>
      </div>

      <!-- Ultimate -->
      <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(241,66,11,0.3); border-radius: 16px; padding: 32px; width: 260px; text-align: center;">
        <h3 style="font-family: 'Oswald', sans-serif; color: #ffffff; font-size: 24px; margin-bottom: 8px;">ULTIMATE</h3>
        <p style="color: #f1420b; font-size: 42px; font-weight: 700; margin-bottom: 16px;">$999</p>
        <form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_blank">
          <input type="hidden" name="cmd" value="_xclick">
          <input type="hidden" name="business" value="support@puremarketing.ai">
          <input type="hidden" name="item_name" value="Pure Brain Ultimate">
          <input type="hidden" name="item_number" value="PB-ULTIMATE">
          <input type="hidden" name="amount" value="999.00">
          <input type="hidden" name="currency_code" value="USD">
          <input type="hidden" name="no_shipping" value="1">
          <input type="hidden" name="return" value="https://purebrain.ai/thank-you/">
          <input type="hidden" name="cancel_return" value="https://purebrain.ai/purebrain-2-0/">
          <button type="submit" style="background: linear-gradient(135deg, #f1420b 0%, #ff6b3d 100%); color: white; border: none; padding: 14px 32px; font-size: 16px; font-weight: 600; border-radius: 8px; cursor: pointer; width: 100%;">Ultimate - $999</button>
        </form>
      </div>

    </div>
  </div>
</section>`;

                const htmlWidget = column.get('elements').add({
                    elType: 'widget',
                    widgetType: 'html',
                    settings: {
                        html: paypalHtml
                    }
                });

                return {
                    success: true,
                    sectionId: newSectionModel.get('id'),
                    columnId: column.get('id'),
                    widgetId: htmlWidget.get('id')
                };

            } catch (e) {
                return { error: e.toString() };
            }
        }
    ''')

    print(f"Add widget result: {result}")

    if result.get('success'):
        # Save the page
        print("Saving Elementor changes...")
        page.wait_for_timeout(2000)

        # Click the save/publish button
        save_btn = page.locator("#elementor-panel-saver-button-publish, button:has-text('Publish'), button:has-text('Update')")
        if save_btn.count() > 0:
            save_btn.first.click()
            page.wait_for_timeout(5000)

        screenshot(page, "03-saved")

    return result

def main():
    print("=" * 60)
    print("PayPal Buttons via Elementor")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        try:
            if not login(page):
                print("Login failed")
                return

            # Open Elementor and add widget
            add_widget_at_end(page)

            # Verify
            print("\n=== Verification ===")
            page.goto("https://purebrain.ai/purebrain-2-0/", wait_until="domcontentloaded")
            page.wait_for_timeout(5000)

            # Scroll to bottom
            for _ in range(15):
                page.evaluate("window.scrollBy(0, 500)")
                page.wait_for_timeout(200)

            screenshot(page, "04-verify")

            # Check for PayPal
            paypal_count = page.locator("form[action*='paypal']").count()
            print(f"PayPal forms on page: {paypal_count}")

        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            screenshot(page, "error")
        finally:
            browser.close()

if __name__ == "__main__":
    main()
