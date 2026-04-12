#!/usr/bin/env python3
"""
Deploy surgical pricing tier update for pay-test-sandbox-2 (page 688).

Strategy:
1. Fetch _elementor_data from WP REST API (returns as JSON string)
2. Parse the JSON to find the HTML widget
3. Within the HTML widget's 'html' setting, replace the pricing-grid section
4. Serialize back and push via REST API
5. Clear cache, verify

What changes:
- 5 tiers -> 4 tiers (remove Bonded, rename remaining)
- Awakened: $79 -> $149, becomes MOST POPULAR, gets orange checkmarks
- Partnered: stays $499, gets expanded features, strikethrough $579
- Unified: stays $999, gets expanded features, strikethrough $1089
- Enterprise: stays custom, gets expanded features
- Footnote added below grid
"""

import json
import sys
import re
import requests
from requests.auth import HTTPBasicAuth

WP_URL = "https://purebrain.ai"
WP_USER = "purebrainai"
WP_PASS = "FlFr2VOtlHiHaJWjzW96OHUJ"
PAGE_ID = 688
AUTH = HTTPBasicAuth(WP_USER, WP_PASS)

CHECK_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>'


def fi(text, color="blue", bold=False):
    """Build a feature list item."""
    inner = f"<strong>{text}</strong>" if bold else text
    return (
        f'\n                        <li class="pricing-card__feature pricing-card__feature--{color}">'
        f'{CHECK_SVG}'
        f'{inner}'
        f'</li>'
    )


def build_new_pricing_html():
    """
    Builds the replacement HTML from <div class="pricing-grid"> through
    the closing </div> of the grid, plus the footnote.
    Does NOT include what comes after (pricing-requirements etc).
    """

    # Card 1: Awakened — featured, MOST POPULAR, orange checkmarks, $149
    awakened = f"""
                <!-- AWAKENED — MOST POPULAR -->
                <div class="pricing-card pricing-card--featured">
                    <div class="pricing-card__badge">MOST POPULAR</div>
                    <h3 class="pricing-card__tier">Awakened</h3>
                    <p class="pricing-card__tagline">Your AI partnership begins</p>
                    <div class="pricing-card__price">
                        <span class="pricing-card__amount">$149</span>
                        <span class="pricing-card__period">/month</span>
                    </div>
                    <div style="font-size:0.85rem; color:rgba(255,255,255,0.4); text-decoration:line-through; margin-top:4px;">$197/month*</div>
                    <ul class="pricing-card__features">{fi('Unlimited agent creation','orange')}{fi('50+ agent simultaneous deployment','orange')}{fi('<span class="ai-name-dynamic">Your AI</span> has a permanent home that\'s always on','orange')}{fi('<span class="ai-name-dynamic">Your AI</span> inherits wisdom from a family of AI minds','orange')}{fi('Comms hub access (skills sync)','orange')}{fi('We maintain it for you — problems fixed before you notice them','orange',bold=True)}{fi('Proactive health checks','orange')}{fi('Priority skills sync','orange')}{fi('24h support response','orange')}{fi('Telegram + Bluesky setup','orange')}{fi('Community support','orange')}{fi('Basic documentation','orange')}
                    </ul>
                    <button class="pricing-card__cta pricing-card__cta--primary" onclick="openWaitlistModal('Awakened')">
                        CLAIM THIS SPOT
                    </button>
                </div>"""

    # Card 2: Partnered — standard, blue, $499
    partnered = f"""
                <!-- PARTNERED -->
                <div class="pricing-card">
                    <h3 class="pricing-card__tier">Partnered</h3>
                    <p class="pricing-card__tagline">Your AI has expert guidance</p>
                    <div class="pricing-card__price">
                        <span class="pricing-card__amount">$499</span>
                        <span class="pricing-card__period">/month</span>
                    </div>
                    <div style="font-size:0.85rem; color:rgba(255,255,255,0.4); text-decoration:line-through; margin-top:4px;">$579/month*</div>
                    <ul class="pricing-card__features">{fi('Everything in Awakened, plus:')}{fi('1 hour/month expert consulting')}{fi('1 custom agent/month')}{fi('Same-day support responses')}{fi('Early access to new skills')}{fi('Quarterly strategy review')}{fi('Dedicated onboarding session')}{fi('Monthly performance report')}{fi('Priority feature requests')}{fi('Advanced analytics dashboard')}{fi('Custom AI personality tuning')}{fi('Bi-weekly optimization check-ins')}
                    </ul>
                    <button class="pricing-card__cta pricing-card__cta--secondary" onclick="openWaitlistModal('Partnered')">
                        GET STARTED
                    </button>
                </div>"""

    # Card 3: Unified — standard, blue, $999
    unified = f"""
                <!-- UNIFIED -->
                <div class="pricing-card">
                    <h3 class="pricing-card__tier">Unified</h3>
                    <p class="pricing-card__tagline">Full integration &amp; priority access</p>
                    <div class="pricing-card__price">
                        <span class="pricing-card__amount">$999</span>
                        <span class="pricing-card__period">/month</span>
                    </div>
                    <div style="font-size:0.85rem; color:rgba(255,255,255,0.4); text-decoration:line-through; margin-top:4px;">$1,089/month*</div>
                    <ul class="pricing-card__features">{fi('Everything in Partnered, plus:')}{fi('3 hours/month consulting')}{fi('Unlimited custom agents')}{fi('Same-hour support')}{fi('Direct team channel')}{fi('Beta access to everything')}{fi('Custom workflow automation')}{fi('Dedicated Slack/Teams channel')}{fi('Priority bug fixes')}{fi('White-glove onboarding')}{fi('Multi-platform deployment')}{fi('Quarterly roadmap reviews')}
                    </ul>
                    <button class="pricing-card__cta pricing-card__cta--secondary" onclick="openPayPalModal('Unified')">
                        GET STARTED
                    </button>
                </div>"""

    # Card 4: Enterprise — enterprise card, custom pricing
    enterprise = f"""
                <!-- ENTERPRISE -->
                <div class="pricing-card pricing-card--enterprise">
                    <h3 class="pricing-card__tier">Enterprise</h3>
                    <p class="pricing-card__tagline">Teams &amp; organizations</p>
                    <div class="pricing-card__price">
                        <span class="pricing-card__custom">Custom</span>
                    </div>
                    <ul class="pricing-card__features">{fi('Everything in Unified, plus:')}{fi('Unlimited consulting hours')}{fi('Dedicated infrastructure')}{fi('99.9% uptime SLA')}{fi('White-label options')}{fi('Custom integrations')}{fi('Multi-team deployment')}{fi('Custom SLA terms')}{fi('Executive strategy sessions')}{fi('Dedicated account manager')}{fi('On-site training available')}{fi('Enterprise API access')}
                    </ul>
                    <button class="pricing-card__cta pricing-card__cta--secondary" onclick="openWaitlistModal('Enterprise')">
                        LET'S TALK
                    </button>
                </div>"""

    footnote = """
            <p style="text-align:center; color:rgba(255,255,255,0.5); font-size:0.8rem; margin-top:40px; max-width:600px; margin-left:auto; margin-right:auto;">
                *Pricing post our full launch. Lock in the savings today for 1 full year!
            </p>"""

    new_grid = f"""<div class="pricing-grid">
{awakened}
{partnered}
{unified}
{enterprise}
            </div>
{footnote}
            """

    return new_grid


def find_and_replace_in_html(html_content, new_grid_html):
    """
    Replace the pricing-grid section in the widget's HTML content.

    Finds: from <div class="pricing-grid..."> to the closing </div>
    before <div class="pricing-requirements">
    """
    # Pattern for start: the pricing-grid div (may have extra classes like pricing-grid--five)
    # Pattern for end: <div class="pricing-requirements">

    # Find start of pricing-grid
    start_match = re.search(r'<div class="pricing-grid[^"]*">', html_content)
    if not start_match:
        raise ValueError("Could not find pricing-grid div in HTML")
    start_idx = start_match.start()
    print(f"  Found pricing-grid at HTML position {start_idx}")

    # Find pricing-requirements after the grid
    end_marker = '<div class="pricing-requirements">'
    end_idx = html_content.find(end_marker, start_idx)
    if end_idx == -1:
        raise ValueError("Could not find pricing-requirements div in HTML")
    print(f"  Found pricing-requirements at HTML position {end_idx}")

    old_section = html_content[start_idx:end_idx]
    print(f"  Replacing {len(old_section)} chars of HTML")

    # Verify old section has expected tiers
    for name in ['Awakened', 'Bonded', 'Partnered', 'Unified', 'Enterprise']:
        found = name in old_section
        print(f"    Old section has '{name}': {found}")

    new_html = html_content[:start_idx] + new_grid_html + html_content[end_idx:]

    # Verify new section
    print("\n  Verification of new HTML:")
    for name in ['Awakened', 'Bonded', 'Partnered', 'Unified', 'Enterprise']:
        found = name in new_html[start_idx:start_idx + len(new_grid_html) + 500]
        print(f"    New section has '{name}': {found}")

    return new_html


def find_html_widget(element, depth=0):
    """Recursively find the HTML widget(s) in Elementor data."""
    results = []

    if isinstance(element, list):
        for item in element:
            results.extend(find_html_widget(item, depth))
    elif isinstance(element, dict):
        widget_type = element.get('widgetType', '')
        settings = element.get('settings', {})

        if widget_type == 'html' and isinstance(settings, dict):
            html_val = settings.get('html', '')
            if html_val and 'pricing-grid' in html_val:
                results.append(element)

        # Recurse
        for child in element.get('elements', []):
            results.extend(find_html_widget(child, depth + 1))

    return results


def fetch_elementor_data_from_api():
    """Fetch current _elementor_data from WordPress REST API."""
    print("Fetching page data from WordPress REST API...")
    url = f"{WP_URL}/wp-json/wp/v2/pages/{PAGE_ID}?context=edit"
    resp = requests.get(url, auth=AUTH, timeout=30)
    resp.raise_for_status()
    page_data = resp.json()

    # _elementor_data is stored as a JSON string in the meta field
    elementor_data_str = page_data.get("meta", {}).get("_elementor_data", "")
    if not elementor_data_str:
        raise ValueError("No _elementor_data found in API response")

    print(f"  Got _elementor_data string: {len(elementor_data_str)} chars")
    return elementor_data_str


def main():
    print("=" * 65)
    print("PRICING TIER DEPLOYMENT — Page 688 (pay-test-sandbox-2)")
    print("5 tiers -> 4 tiers | Awakened $149 MOST POPULAR")
    print("=" * 65)

    # ---- Step 1: Get source data ----
    # First try the local file (faster for testing the replacement logic)
    # Then fetch fresh from API

    print("\n[1/6] Loading Elementor data from local file...")
    with open('/home/jared/projects/AI-CIV/aether/exports/package-sandbox-2/page688_elementor_data.json', 'r') as f:
        elementor_data_local = json.load(f)

    # The local file is the parsed JSON array
    # We need to work with it to find the HTML widget
    print(f"  Local file: {type(elementor_data_local).__name__}, {len(elementor_data_local)} top-level elements")

    # ---- Step 2: Find the HTML widget ----
    print("\n[2/6] Finding HTML widget with pricing section...")
    widgets = find_html_widget(elementor_data_local)
    print(f"  Found {len(widgets)} HTML widget(s) with pricing-grid")

    if not widgets:
        print("  ERROR: No HTML widget found with pricing-grid content")
        sys.exit(1)

    target_widget = widgets[0]
    original_html = target_widget['settings']['html']
    print(f"  Widget ID: {target_widget['id']}, HTML length: {len(original_html)} chars")

    # ---- Step 3: Build new pricing HTML ----
    print("\n[3/6] Building new pricing grid HTML...")
    new_grid_html = build_new_pricing_html()
    print(f"  New grid HTML: {len(new_grid_html)} chars")

    # ---- Step 4: Replace pricing section ----
    print("\n[4/6] Performing surgical HTML replacement...")
    new_html = find_and_replace_in_html(original_html, new_grid_html)
    print(f"  New HTML length: {len(new_html)} chars (was {len(original_html)})")

    # Save backup of original
    backup_path = '/home/jared/projects/AI-CIV/aether/exports/package-sandbox-2/page688_widget_html_backup.html'
    with open(backup_path, 'w') as f:
        f.write(original_html)
    print(f"  Backup saved: {backup_path}")

    # Update the widget in the Elementor data structure
    target_widget['settings']['html'] = new_html

    # ---- Step 5: Serialize and push to WordPress ----
    print("\n[5/6] Fetching live _elementor_data string from WordPress...")
    live_elementor_str = fetch_elementor_data_from_api()

    # Parse the live string, apply our change, re-serialize
    live_elementor_data = json.loads(live_elementor_str)

    # Find the same widget in the live data and update it
    live_widgets = find_html_widget(live_elementor_data)
    if not live_widgets:
        print("  WARNING: Widget not found in live data, using local data structure")
        live_elementor_data = elementor_data_local
        live_widgets = find_html_widget(live_elementor_data)

    if live_widgets:
        live_widgets[0]['settings']['html'] = new_html
        print(f"  Updated widget {live_widgets[0]['id']} in live data")
    else:
        print("  ERROR: Cannot find widget in live data")
        sys.exit(1)

    # Serialize back to JSON string
    new_elementor_str = json.dumps(live_elementor_data, ensure_ascii=False)
    print(f"  Serialized: {len(new_elementor_str)} chars")

    # Push to WordPress
    print("\n  Pushing to WordPress...")
    push_url = f"{WP_URL}/wp-json/wp/v2/pages/{PAGE_ID}"
    push_payload = {"meta": {"_elementor_data": new_elementor_str}}
    push_resp = requests.post(push_url, auth=AUTH, json=push_payload, timeout=60)

    if push_resp.status_code not in (200, 201):
        print(f"  ERROR: Status {push_resp.status_code}")
        print(f"  Body: {push_resp.text[:500]}")
        sys.exit(1)

    print(f"  SUCCESS: Status {push_resp.status_code}")

    # ---- Step 6: Clear cache and verify ----
    print("\n[6/6] Clearing Elementor cache...")
    cache_resp = requests.delete(
        f"{WP_URL}/wp-json/elementor/v1/cache",
        auth=AUTH,
        timeout=30
    )
    print(f"  Cache clear: {cache_resp.status_code} — {cache_resp.text[:100]}")

    print("\nVerifying deployment on live page...")
    import time
    time.sleep(3)  # Give cache a moment to clear
    verify_resp = requests.get(f"{WP_URL}/pay-test-sandbox-2/", timeout=30)
    live_html = verify_resp.text

    checks = [
        ("Awakened present", "Awakened" in live_html),
        ("$149 present", "$149" in live_html),
        ("Strikethrough $197/month*", "$197/month*" in live_html),
        ("Partnered present", "Partnered" in live_html),
        ("$499 present", "$499" in live_html),
        ("Strikethrough $579/month*", "$579/month*" in live_html),
        ("Unified present", "Unified" in live_html),
        ("$999 present", "$999" in live_html),
        ("Strikethrough $1,089/month*", "$1,089/month*" in live_html),
        ("Enterprise present", "Enterprise" in live_html),
        ("MOST POPULAR present", "MOST POPULAR" in live_html),
        ("CLAIM THIS SPOT present", "CLAIM THIS SPOT" in live_html),
        ("Footnote present", "Lock in the savings today" in live_html),
        ("Bonded REMOVED", "Bonded" not in live_html),
        ("openPayPalModal preserved", "openPayPalModal" in live_html),
        ("openWaitlistModal preserved", "openWaitlistModal" in live_html),
    ]

    all_pass = True
    for name, result in checks:
        status = "PASS" if result else "FAIL"
        if not result:
            all_pass = False
        print(f"  [{status}] {name}")

    print("\n" + "=" * 65)
    if all_pass:
        print("DEPLOYMENT SUCCESSFUL — ALL CHECKS PASSED")
    else:
        print("DEPLOYMENT COMPLETE — SOME CHECKS FAILED")
    print("=" * 65)

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
