#!/usr/bin/env python3
"""
Add PayPal purchase buttons to purebrain.ai/purebrain-3/ (Page ID 338)

Strategy:
- The page is a single HTML widget inside one Elementor container
- We fetch the _elementor_data via WordPress REST API (context=edit)
- Replace the 3 pricing CTA buttons (Awakened, Bonded, Partnered) with PayPal forms
- The PayPal forms reuse the existing pricing-card__cta CSS classes for visual consistency
- Update the page via REST API POST to pages/338

Credentials: Aether / FlFr2VOtlHiHaJWjzW96OHUJ
Page ID: 338 (/purebrain-3/)
"""

import json
import re
import requests
import sys

# WordPress credentials
WP_BASE = "https://purebrain.ai"
WP_USER = "Aether"
WP_PASS = "FlFr2VOtlHiHaJWjzW96OHUJ"
PAGE_ID = 338

# PayPal form templates - uses existing pricing-card__cta CSS classes
# so buttons visually match existing style. cancel_return points back to /purebrain-3/

PAYPAL_AWAKENED = '''<form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_blank" style="display:block;width:100%;">
  <input type="hidden" name="cmd" value="_xclick">
  <input type="hidden" name="business" value="support@puremarketing.ai">
  <input type="hidden" name="item_name" value="Pure Brain Awakened">
  <input type="hidden" name="item_number" value="PB-AWAKENED">
  <input type="hidden" name="amount" value="79.00">
  <input type="hidden" name="currency_code" value="USD">
  <input type="hidden" name="no_shipping" value="1">
  <input type="hidden" name="return" value="https://purebrain.ai/thank-you/">
  <input type="hidden" name="cancel_return" value="https://purebrain.ai/purebrain-3/">
  <button type="submit" class="pricing-card__cta pricing-card__cta--secondary" style="width:100%;cursor:pointer;">
    Get Started
  </button>
</form>'''

PAYPAL_BONDED = '''<form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_blank" style="display:block;width:100%;">
  <input type="hidden" name="cmd" value="_xclick">
  <input type="hidden" name="business" value="support@puremarketing.ai">
  <input type="hidden" name="item_name" value="Pure Brain Bonded">
  <input type="hidden" name="item_number" value="PB-BONDED">
  <input type="hidden" name="amount" value="149.00">
  <input type="hidden" name="currency_code" value="USD">
  <input type="hidden" name="no_shipping" value="1">
  <input type="hidden" name="return" value="https://purebrain.ai/thank-you/">
  <input type="hidden" name="cancel_return" value="https://purebrain.ai/purebrain-3/">
  <button type="submit" class="pricing-card__cta pricing-card__cta--primary" id="proCta" style="width:100%;cursor:pointer;">
    Activate Now
  </button>
</form>'''

PAYPAL_PARTNERED = '''<form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_blank" style="display:block;width:100%;">
  <input type="hidden" name="cmd" value="_xclick">
  <input type="hidden" name="business" value="support@puremarketing.ai">
  <input type="hidden" name="item_name" value="Pure Brain Partnered">
  <input type="hidden" name="item_number" value="PB-PARTNERED">
  <input type="hidden" name="amount" value="499.00">
  <input type="hidden" name="currency_code" value="USD">
  <input type="hidden" name="no_shipping" value="1">
  <input type="hidden" name="return" value="https://purebrain.ai/thank-you/">
  <input type="hidden" name="cancel_return" value="https://purebrain.ai/purebrain-3/">
  <button type="submit" class="pricing-card__cta pricing-card__cta--secondary" style="width:100%;cursor:pointer;">
    Get Started
  </button>
</form>'''

# Exact button strings to replace (from the live page HTML)
AWAKENED_BUTTON = """<button class="pricing-card__cta pricing-card__cta--secondary" onclick="openWaitlistModal('Awakened')">
                        Get Started
                    </button>"""

BONDED_BUTTON = """<button class="pricing-card__cta pricing-card__cta--primary" id="proCta" onclick="openWaitlistModal('Bonded')">
                        Activate Now
                    </button>"""

PARTNERED_BUTTON = """<button class="pricing-card__cta pricing-card__cta--secondary" onclick="openWaitlistModal('Partnered')">
                        Get Started
                    </button>"""


def fetch_page_elementor_data():
    """Fetch the Elementor JSON data for page 338."""
    print(f"Fetching page {PAGE_ID} from {WP_BASE}...")
    url = f"{WP_BASE}/wp-json/wp/v2/pages/{PAGE_ID}?context=edit"
    resp = requests.get(url, auth=(WP_USER, WP_PASS), timeout=30)
    resp.raise_for_status()
    data = resp.json()

    meta = data.get("meta", {})
    elementor_data_raw = meta.get("_elementor_data", "")
    if not elementor_data_raw:
        raise ValueError("No _elementor_data found in page meta")

    elementor_data = json.loads(elementor_data_raw)
    print(f"Fetched Elementor data: {len(elementor_data_raw)} chars, {len(elementor_data)} top-level containers")
    return elementor_data, elementor_data_raw


def replace_buttons_in_html(html_content):
    """Replace the three pricing CTA buttons with PayPal forms."""
    changes = []

    # Check if PayPal already exists
    if "paypal.com/cgi-bin/webscr" in html_content:
        print("WARNING: PayPal buttons already exist in this page. Aborting to avoid duplicates.")
        return html_content, changes

    # Replace Awakened button
    if AWAKENED_BUTTON in html_content:
        html_content = html_content.replace(AWAKENED_BUTTON, PAYPAL_AWAKENED)
        changes.append("Awakened ($79) - replaced with PayPal form")
        print("  [OK] Replaced Awakened button")
    else:
        print("  [WARN] Awakened button not found - trying regex fallback")
        pattern = r'<button[^>]*pricing-card__cta[^>]*onclick=["\']openWaitlistModal\(["\']Awakened["\'][^>]*>.*?</button>'
        if re.search(pattern, html_content, re.DOTALL | re.IGNORECASE):
            html_content = re.sub(pattern, PAYPAL_AWAKENED, html_content, count=1, flags=re.DOTALL | re.IGNORECASE)
            changes.append("Awakened ($79) - replaced with PayPal form (regex)")
            print("  [OK] Replaced Awakened button (regex)")
        else:
            print("  [FAIL] Could not find Awakened button")

    # Replace Bonded button
    if BONDED_BUTTON in html_content:
        html_content = html_content.replace(BONDED_BUTTON, PAYPAL_BONDED)
        changes.append("Bonded ($149) - replaced with PayPal form")
        print("  [OK] Replaced Bonded button")
    else:
        print("  [WARN] Bonded button not found - trying regex fallback")
        pattern = r'<button[^>]*pricing-card__cta[^>]*onclick=["\']openWaitlistModal\(["\']Bonded["\'][^>]*>.*?</button>'
        if re.search(pattern, html_content, re.DOTALL | re.IGNORECASE):
            html_content = re.sub(pattern, PAYPAL_BONDED, html_content, count=1, flags=re.DOTALL | re.IGNORECASE)
            changes.append("Bonded ($149) - replaced with PayPal form (regex)")
            print("  [OK] Replaced Bonded button (regex)")
        else:
            print("  [FAIL] Could not find Bonded button")

    # Replace Partnered button
    if PARTNERED_BUTTON in html_content:
        html_content = html_content.replace(PARTNERED_BUTTON, PAYPAL_PARTNERED)
        changes.append("Partnered ($499) - replaced with PayPal form")
        print("  [OK] Replaced Partnered button")
    else:
        print("  [WARN] Partnered button not found - trying regex fallback")
        pattern = r'<button[^>]*pricing-card__cta[^>]*onclick=["\']openWaitlistModal\(["\']Partnered["\'][^>]*>.*?</button>'
        if re.search(pattern, html_content, re.DOTALL | re.IGNORECASE):
            html_content = re.sub(pattern, PAYPAL_PARTNERED, html_content, count=1, flags=re.DOTALL | re.IGNORECASE)
            changes.append("Partnered ($499) - replaced with PayPal form (regex)")
            print("  [OK] Replaced Partnered button (regex)")
        else:
            print("  [FAIL] Could not find Partnered button")

    return html_content, changes


def update_page_elementor_data(elementor_data):
    """Push updated Elementor JSON back to WordPress via REST API."""
    print(f"\nUpdating page {PAGE_ID} via REST API...")
    url = f"{WP_BASE}/wp-json/wp/v2/pages/{PAGE_ID}"
    new_elementor_json = json.dumps(elementor_data)
    payload = {
        "meta": {
            "_elementor_data": new_elementor_json
        }
    }
    resp = requests.post(url, auth=(WP_USER, WP_PASS), json=payload, timeout=60)
    resp.raise_for_status()
    result = resp.json()
    print(f"Update response status: {resp.status_code}")
    print(f"Page modified: {result.get('modified', 'unknown')}")
    return result


def verify_live_page():
    """Verify that PayPal buttons appear on the live page."""
    print("\nVerifying live page...")
    resp = requests.get("https://purebrain.ai/purebrain-3/", timeout=30)
    content = resp.text
    paypal_count = content.count("paypal.com/cgi-bin/webscr")
    awakened_paypal = "PB-AWAKENED" in content
    bonded_paypal = "PB-BONDED" in content
    partnered_paypal = "PB-PARTNERED" in content

    print(f"  PayPal form references found: {paypal_count}")
    print(f"  PB-AWAKENED present: {awakened_paypal}")
    print(f"  PB-BONDED present: {bonded_paypal}")
    print(f"  PB-PARTNERED present: {partnered_paypal}")

    # Check old buttons are gone
    waitlist_awakened = "openWaitlistModal('Awakened')" in content
    waitlist_bonded = "openWaitlistModal('Bonded')" in content
    waitlist_partnered = "openWaitlistModal('Partnered')" in content
    print(f"  Old Awakened waitlist button still present: {waitlist_awakened}")
    print(f"  Old Bonded waitlist button still present: {waitlist_bonded}")
    print(f"  Old Partnered waitlist button still present: {waitlist_partnered}")

    success = awakened_paypal and bonded_paypal and partnered_paypal
    return success


def main():
    print("=" * 60)
    print("PureBrain 3.0 PayPal Button Integration")
    print("Page: https://purebrain.ai/purebrain-3/ (ID 338)")
    print("=" * 60)

    # Step 1: Fetch Elementor data
    try:
        elementor_data, original_raw = fetch_page_elementor_data()
    except Exception as e:
        print(f"FAILED to fetch page data: {e}")
        sys.exit(1)

    # Step 2: Find the HTML widget and replace buttons
    print("\nLocating HTML widget and replacing pricing buttons...")
    container = elementor_data[0]
    html_widget = container["elements"][0]

    if html_widget.get("widgetType") != "html":
        print(f"ERROR: Expected html widget, got: {html_widget.get('widgetType')}")
        sys.exit(1)

    original_html = html_widget["settings"]["html"]
    print(f"HTML content length: {len(original_html)} chars")

    updated_html, changes = replace_buttons_in_html(original_html)

    if not changes:
        print("\nNo changes made. Exiting.")
        sys.exit(0)

    print(f"\nChanges to apply:")
    for c in changes:
        print(f"  - {c}")

    # Step 3: Update the Elementor data structure
    html_widget["settings"]["html"] = updated_html
    elementor_data[0]["elements"][0] = html_widget

    # Step 4: Push update to WordPress
    try:
        update_page_elementor_data(elementor_data)
        print("Page updated successfully.")
    except Exception as e:
        print(f"FAILED to update page: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Step 5: Verify live page
    import time
    print("\nWaiting 3 seconds for cache to clear...")
    time.sleep(3)
    success = verify_live_page()

    print("\n" + "=" * 60)
    if success:
        print("SUCCESS: PayPal buttons are live on purebrain.ai/purebrain-3/")
        print("  - Awakened ($79/month) -> PayPal form with PB-AWAKENED")
        print("  - Bonded ($149/month)  -> PayPal form with PB-BONDED")
        print("  - Partnered ($499/month) -> PayPal form with PB-PARTNERED")
        print("  - Return URL: https://purebrain.ai/thank-you/")
        print("  - Cancel URL: https://purebrain.ai/purebrain-3/")
    else:
        print("PARTIAL/FAILED: Check live page manually.")
        print("Note: Elementor may cache pages - try clearing Elementor cache")
        print("if buttons are not visible on the live site.")
    print("=" * 60)
    return success


if __name__ == "__main__":
    main()
