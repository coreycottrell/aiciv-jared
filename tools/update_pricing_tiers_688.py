#!/usr/bin/env python3
"""
Surgical pricing tier update for pay-test-sandbox-2 (page 688).

What this does:
- Reads the current _elementor_data from WordPress via REST API
- Finds the HTML widget containing the pricing section
- Replaces ONLY the pricing grid (5 tiers -> 4 tiers) and adds footnote
- Pushes updated _elementor_data back via REST API
- Clears Elementor cache

What this does NOT touch:
- Any CSS, JS, layout, PayPal buttons outside pricing section
- Any other section of the page
- Any Elementor widget structure
"""

import json
import sys
import re
import requests
from requests.auth import HTTPBasicAuth

# WordPress credentials
WP_URL = "https://purebrain.ai"
WP_USER = "purebrainai"
WP_PASS = "FlFr2VOtlHiHaJWjzW96OHUJ"
PAGE_ID = 688

AUTH = HTTPBasicAuth(WP_USER, WP_PASS)

# SVG checkmark reused in every feature list item
CHECK_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>'

def feature(text, color="blue", bold=False):
    """Build a single feature list item."""
    inner = f"<strong>{text}</strong>" if bold else text
    return (
        f'<li class="pricing-card__feature pricing-card__feature--{color}">'
        f'{CHECK_SVG}'
        f'{inner}'
        f'</li>'
    )

def build_new_pricing_grid():
    """
    Returns the complete replacement HTML for the pricing section,
    from <div class="pricing-grid"> through the closing </div> plus footnote.
    """

    # ---- CARD 1: AWAKENED (featured, MOST POPULAR) ----
    awakened_features = [
        feature("Unlimited agent creation", "orange"),
        feature("50+ agent simultaneous deployment", "orange"),
        feature('<span class="ai-name-dynamic">Your AI</span> has a permanent home that\'s always on', "orange"),
        feature('<span class="ai-name-dynamic">Your AI</span> inherits wisdom from a family of AI minds', "orange"),
        feature("Comms hub access (skills sync)", "orange"),
        feature("We maintain it for you — problems fixed before you notice them", "orange", bold=True),
        feature("Proactive health checks", "orange"),
        feature("Priority skills sync", "orange"),
        feature("24h support response", "orange"),
        feature("Telegram + Bluesky setup", "orange"),
        feature("Community support", "orange"),
        feature("Basic documentation", "orange"),
    ]

    card_awakened = f"""
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
                    <ul class="pricing-card__features">
                        {''.join(awakened_features)}
                    </ul>
                    <button class="pricing-card__cta pricing-card__cta--primary" onclick="openWaitlistModal('Awakened')">
                        CLAIM THIS SPOT
                    </button>
                </div>"""

    # ---- CARD 2: PARTNERED ----
    partnered_features = [
        feature("Everything in Awakened, plus:"),
        feature("1 hour/month expert consulting"),
        feature("1 custom agent/month"),
        feature("Same-day support responses"),
        feature("Early access to new skills"),
        feature("Quarterly strategy review"),
        feature("Dedicated onboarding session"),
        feature("Monthly performance report"),
        feature("Priority feature requests"),
        feature("Advanced analytics dashboard"),
        feature("Custom AI personality tuning"),
        feature("Bi-weekly optimization check-ins"),
    ]

    card_partnered = f"""
                <!-- PARTNERED -->
                <div class="pricing-card">
                    <h3 class="pricing-card__tier">Partnered</h3>
                    <p class="pricing-card__tagline">Your AI has expert guidance</p>
                    <div class="pricing-card__price">
                        <span class="pricing-card__amount">$499</span>
                        <span class="pricing-card__period">/month</span>
                    </div>
                    <div style="font-size:0.85rem; color:rgba(255,255,255,0.4); text-decoration:line-through; margin-top:4px;">$579/month*</div>
                    <ul class="pricing-card__features">
                        {''.join(partnered_features)}
                    </ul>
                    <button class="pricing-card__cta pricing-card__cta--secondary" onclick="openWaitlistModal('Partnered')">
                        GET STARTED
                    </button>
                </div>"""

    # ---- CARD 3: UNIFIED ----
    unified_features = [
        feature("Everything in Partnered, plus:"),
        feature("3 hours/month consulting"),
        feature("Unlimited custom agents"),
        feature("Same-hour support"),
        feature("Direct team channel"),
        feature("Beta access to everything"),
        feature("Custom workflow automation"),
        feature("Dedicated Slack/Teams channel"),
        feature("Priority bug fixes"),
        feature("White-glove onboarding"),
        feature("Multi-platform deployment"),
        feature("Quarterly roadmap reviews"),
    ]

    card_unified = f"""
                <!-- UNIFIED -->
                <div class="pricing-card">
                    <h3 class="pricing-card__tier">Unified</h3>
                    <p class="pricing-card__tagline">Full integration &amp; priority access</p>
                    <div class="pricing-card__price">
                        <span class="pricing-card__amount">$999</span>
                        <span class="pricing-card__period">/month</span>
                    </div>
                    <div style="font-size:0.85rem; color:rgba(255,255,255,0.4); text-decoration:line-through; margin-top:4px;">$1,089/month*</div>
                    <ul class="pricing-card__features">
                        {''.join(unified_features)}
                    </ul>
                    <button class="pricing-card__cta pricing-card__cta--secondary" onclick="openPayPalModal('Unified')">
                        GET STARTED
                    </button>
                </div>"""

    # ---- CARD 4: ENTERPRISE (centered below in its own wrapper) ----
    enterprise_features = [
        feature("Everything in Unified, plus:"),
        feature("Unlimited consulting hours"),
        feature("Dedicated infrastructure"),
        feature("99.9% uptime SLA"),
        feature("White-label options"),
        feature("Custom integrations"),
        feature("Multi-team deployment"),
        feature("Custom SLA terms"),
        feature("Executive strategy sessions"),
        feature("Dedicated account manager"),
        feature("On-site training available"),
        feature("Enterprise API access"),
    ]

    card_enterprise = f"""
                <!-- ENTERPRISE -->
                <div class="pricing-card pricing-card--enterprise">
                    <h3 class="pricing-card__tier">Enterprise</h3>
                    <p class="pricing-card__tagline">Teams &amp; organizations</p>
                    <div class="pricing-card__price">
                        <span class="pricing-card__custom">Custom</span>
                    </div>
                    <ul class="pricing-card__features">
                        {''.join(enterprise_features)}
                    </ul>
                    <button class="pricing-card__cta pricing-card__cta--secondary" onclick="openWaitlistModal('Enterprise')">
                        LET'S TALK
                    </button>
                </div>"""

    footnote = """
            <p style="text-align:center; color:rgba(255,255,255,0.5); font-size:0.8rem; margin-top:40px; max-width:600px; margin-left:auto; margin-right:auto;">
                *Pricing post our full launch. Lock in the savings today for 1 full year!
            </p>"""

    # Assemble the full new pricing-grid block
    new_grid = f"""<div class="pricing-grid">
{card_awakened}
{card_partnered}
{card_unified}
{card_enterprise}
            </div>
{footnote}"""

    return new_grid


def get_elementor_data():
    """Fetch current _elementor_data from WordPress REST API."""
    print("Fetching current _elementor_data from WordPress...")
    url = f"{WP_URL}/wp-json/wp/v2/pages/{PAGE_ID}?context=edit"
    resp = requests.get(url, auth=AUTH, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    elementor_data_raw = data.get("meta", {}).get("_elementor_data", "")
    if not elementor_data_raw:
        # Try content field (fallback)
        elementor_data_raw = data.get("content", {}).get("raw", "")

    if not elementor_data_raw:
        raise ValueError("Could not find _elementor_data in API response")

    print(f"  Got _elementor_data, length: {len(elementor_data_raw)} chars")
    return elementor_data_raw


def find_and_replace_pricing_in_widget(elementor_data_str, new_grid_html):
    """
    Find the pricing-grid block inside the Elementor HTML widget content
    and replace it with new_grid_html.

    The pricing grid starts with <div class="pricing-grid"> (possibly with
    a --five modifier class) and ends with the closing </div> of that grid,
    followed by the footnote insertion point.
    """
    # We need to find the pricing-grid block in the raw Elementor JSON string.
    # The HTML is stored as a JSON string value, so we work at the string level.
    # The pricing-grid div starts with one of these patterns:
    #   <div class=\"pricing-grid\">
    #   <div class=\"pricing-grid pricing-grid--five\">

    # Pattern: opening of pricing-grid
    start_marker = '<div class=\\"pricing-grid'
    # After the grid there's a footnote area, then pricing-requirements.
    # The grid closes before <div class=\"pricing-requirements\">
    # We'll find the last </div> before pricing-requirements.

    # Find start of pricing-grid
    start_idx = elementor_data_str.find(start_marker)
    if start_idx == -1:
        raise ValueError(f"Could not find '{start_marker}' in Elementor data")
    print(f"  Found pricing-grid at char index {start_idx}")

    # Find the end: the pricing-requirements div (or the footnote area).
    # Between the end of the grid and pricing-requirements there may already be
    # a footnote from a previous deployment. We target from grid start to just
    # before pricing-requirements.
    end_marker = '<div class=\\"pricing-requirements\\">'
    end_idx = elementor_data_str.find(end_marker, start_idx)
    if end_idx == -1:
        raise ValueError(f"Could not find '{end_marker}' after pricing-grid")

    # The content to replace is from start_idx to end_idx
    # (we keep pricing-requirements and everything after)
    old_section = elementor_data_str[start_idx:end_idx]
    print(f"  Replacing section of {len(old_section)} chars")
    print(f"  Old section preview (first 100): {old_section[:100]}")

    # Escape the new HTML for JSON string embedding
    # JSON strings use \" for quotes, \n is fine but we need to escape properly
    new_grid_escaped = json.dumps(new_grid_html)[1:-1]  # strip surrounding quotes
    # Add trailing whitespace/newline to match original formatting
    new_grid_escaped = new_grid_escaped + "\\n            "

    new_data = elementor_data_str[:start_idx] + new_grid_escaped + elementor_data_str[end_idx:]
    print(f"  New Elementor data length: {len(new_data)} chars (was {len(elementor_data_str)})")
    return new_data


def push_elementor_data(new_elementor_data_str):
    """Push updated _elementor_data to WordPress."""
    print("Pushing updated _elementor_data to WordPress...")

    # The _elementor_data field expects the JSON string as-is (it's stored as a string)
    payload = {
        "meta": {
            "_elementor_data": new_elementor_data_str
        }
    }

    url = f"{WP_URL}/wp-json/wp/v2/pages/{PAGE_ID}"
    resp = requests.post(url, auth=AUTH, json=payload, timeout=60)

    if resp.status_code not in (200, 201):
        print(f"  ERROR: Status {resp.status_code}")
        print(f"  Response: {resp.text[:500]}")
        resp.raise_for_status()

    print(f"  SUCCESS: Status {resp.status_code}")
    return resp.json()


def clear_elementor_cache():
    """Clear Elementor's CSS/HTML cache."""
    print("Clearing Elementor cache...")
    url = f"{WP_URL}/wp-json/elementor/v1/cache"
    resp = requests.delete(url, auth=AUTH, timeout=30)
    print(f"  Cache clear response: {resp.status_code} — {resp.text[:200]}")


def verify_deployment():
    """Fetch the live page and verify the new pricing is present."""
    print("Verifying deployment by fetching live page...")
    resp = requests.get(f"{WP_URL}/pay-test-sandbox-2/", timeout=30)
    content = resp.text

    checks = {
        "Awakened $149 present": "$149" in content and "Awakened" in content,
        "Partnered $499 present": "$499" in content and "Partnered" in content,
        "Unified $999 present": "$999" in content and "Unified" in content,
        "Enterprise present": "Enterprise" in content,
        "Strikethrough $197 present": "$197/month*" in content,
        "Strikethrough $579 present": "$579/month*" in content,
        "Footnote present": "Lock in the savings today" in content,
        "MOST POPULAR on Awakened": content.count("MOST POPULAR") >= 1,
        "CLAIM THIS SPOT button": "CLAIM THIS SPOT" in content,
        "Old Bonded tier gone": "Bonded" not in content,
        "PayPal modal preserved": "openPayPalModal" in content,
        "Waitlist modal preserved": "openWaitlistModal" in content,
    }

    all_pass = True
    for check, result in checks.items():
        status = "PASS" if result else "FAIL"
        if not result:
            all_pass = False
        print(f"  [{status}] {check}")

    return all_pass


def save_backup(elementor_data_str):
    """Save original data as backup before making changes."""
    backup_path = "/home/jared/projects/AI-CIV/aether/exports/package-sandbox-2/page688_elementor_data_backup_pre_pricing_update.json"
    with open(backup_path, "w") as f:
        f.write(elementor_data_str)
    print(f"  Backup saved to: {backup_path}")
    return backup_path


def main():
    print("=" * 60)
    print("SURGICAL PRICING UPDATE — Page 688 (pay-test-sandbox-2)")
    print("=" * 60)

    # Step 1: Fetch current Elementor data
    elementor_data_str = get_elementor_data()

    # Step 2: Save backup
    print("Saving backup of original Elementor data...")
    save_backup(elementor_data_str)

    # Step 3: Build new pricing grid HTML
    print("Building new pricing grid HTML...")
    new_grid_html = build_new_pricing_grid()
    print(f"  New grid HTML length: {len(new_grid_html)} chars")

    # Step 4: Find and replace pricing section in Elementor data
    print("Performing surgical replacement...")
    new_elementor_data_str = find_and_replace_pricing_in_widget(elementor_data_str, new_grid_html)

    # Step 5: Push to WordPress
    push_elementor_data(new_elementor_data_str)

    # Step 6: Clear cache
    clear_elementor_cache()

    # Step 7: Verify
    print("Verifying deployment...")
    all_pass = verify_deployment()

    print("=" * 60)
    if all_pass:
        print("DEPLOYMENT COMPLETE — ALL CHECKS PASSED")
    else:
        print("DEPLOYMENT COMPLETE — SOME CHECKS FAILED (review above)")
    print("=" * 60)

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
