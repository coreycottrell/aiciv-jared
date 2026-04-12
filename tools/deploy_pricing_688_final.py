#!/usr/bin/env python3
"""
FINAL DEPLOYMENT: Surgical pricing update on page 688 (pay-test-sandbox-2).

Based on battle-tested patterns from agent memory:
- Updates BOTH _elementor_data AND content.raw (both must be updated)
- Uses Python urllib for large payloads (curl has ~100KB arg limit)
- str.replace() on the raw JSON string (not re-parse)
- Clear Elementor cache after update

Changes: 5 tiers -> 4 tiers
- Remove: Bonded ($149, MOST POPULAR)
- Awakened: $79 -> $149, becomes MOST POPULAR, orange features, "CLAIM THIS SPOT"
- Partnered: stays $499, updated features list, strikethrough $579
- Unified: stays $999, updated features list, strikethrough $1,197
- Enterprise: stays Custom, updated features list, no strikethrough
- Footnote added below grid
- Grid class: remove pricing-grid--five (if present)
"""

import json
import re
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
import base64

WP_URL = "https://purebrain.ai"
WP_USER = "Aether"
WP_PASS = "ZGuh 1W8k WpWM c9iy kqyd buPr"
PAGE_ID = 688
BASE_URL = f"{WP_URL}/wp-json/wp/v2/pages/{PAGE_ID}"

# Basic auth header
AUTH_HEADER = "Basic " + base64.b64encode(f"{WP_USER}:{WP_PASS}".encode()).decode()


def wp_request(method, path, data=None, content_type="application/json"):
    """Make authenticated WordPress REST API request using urllib."""
    url = f"{WP_URL}/wp-json/{path}"
    headers = {
        "Authorization": AUTH_HEADER,
        "Content-Type": content_type,
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    }
    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        headers["Content-Length"] = str(len(body))

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            resp_body = resp.read().decode("utf-8")
            try:
                return resp.status, json.loads(resp_body) if resp_body.strip() else {}
            except json.JSONDecodeError:
                return resp.status, resp_body
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"  HTTP Error {e.code}: {body[:300]}")
        return e.code, body
    except Exception as ex:
        print(f"  Request error: {ex}")
        return 0, str(ex)


SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>'


def li(text, color="blue", bold=False):
    """Single feature list item — for use inside HTML strings."""
    inner = f"<strong>{text}</strong>" if bold else text
    return f'<li class="pricing-card__feature pricing-card__feature--{color}">{SVG}{inner}</li>'


def build_new_pricing_section():
    """
    Build the complete replacement HTML for the pricing-grid block.
    Returns plain HTML (not JSON-escaped). We'll apply escaping when needed.
    """
    # Awakened features (orange)
    aw = [
        li("Unlimited agent creation", "orange"),
        li("50+ agent simultaneous deployment", "orange"),
        li('<span class="ai-name-dynamic">Your AI</span> has a permanent home that\'s always on', "orange"),
        li('<span class="ai-name-dynamic">Your AI</span> inherits wisdom from a family of AI minds', "orange"),
        li("Comms hub access (skills sync)", "orange"),
        li("We maintain it for you — problems fixed before you notice them", "orange", bold=True),
        li("Proactive health checks", "orange"),
        li("Priority skills sync", "orange"),
        li("24h support response", "orange"),
        li("Telegram + Bluesky setup", "orange"),
        li("Community support", "orange"),
        li("Basic documentation", "orange"),
    ]

    # Partnered features (blue)
    pa = [
        li("Everything in Awakened, plus:"),
        li("1 hour/month expert consulting"),
        li("1 custom agent/month"),
        li("Same-day support responses"),
        li("Early access to new skills"),
        li("Quarterly strategy review"),
        li("Dedicated onboarding session"),
        li("Monthly performance report"),
        li("Priority feature requests"),
        li("Advanced analytics dashboard"),
        li("Custom AI personality tuning"),
        li("Bi-weekly optimization check-ins"),
    ]

    # Unified features (blue)
    un = [
        li("Everything in Partnered, plus:"),
        li("3 hours/month consulting"),
        li("Unlimited custom agents"),
        li("Same-hour support"),
        li("Direct team channel"),
        li("Beta access to everything"),
        li("Custom workflow automation"),
        li("Dedicated Slack/Teams channel"),
        li("Priority bug fixes"),
        li("White-glove onboarding"),
        li("Multi-platform deployment"),
        li("Quarterly roadmap reviews"),
    ]

    # Enterprise features (blue)
    en = [
        li("Everything in Unified, plus:"),
        li("Unlimited consulting hours"),
        li("Dedicated infrastructure"),
        li("99.9% uptime SLA"),
        li("White-label options"),
        li("Custom integrations"),
        li("Multi-team deployment"),
        li("Custom SLA terms"),
        li("Executive strategy sessions"),
        li("Dedicated account manager"),
        li("On-site training available"),
        li("Enterprise API access"),
    ]

    card_aw = (
        '<div class="pricing-card pricing-card--featured">'
        '<div class="pricing-card__badge">MOST POPULAR</div>'
        '<h3 class="pricing-card__tier">Awakened</h3>'
        '<p class="pricing-card__tagline">Your AI partnership begins</p>'
        '<div class="pricing-card__price">'
        '<span class="pricing-card__amount">$149</span>'
        '<span class="pricing-card__period">/month</span>'
        '</div>'
        '<div style="font-size:0.85rem; color:rgba(255,255,255,0.4); text-decoration:line-through; margin-top:4px;">$197/month*</div>'
        f'<ul class="pricing-card__features">{"".join(aw)}</ul>'
        "<button class=\"pricing-card__cta pricing-card__cta--primary\" onclick=\"openWaitlistModal('Awakened')\">CLAIM THIS SPOT</button>"
        '</div>'
    )

    card_pa = (
        '<div class="pricing-card">'
        '<h3 class="pricing-card__tier">Partnered</h3>'
        '<p class="pricing-card__tagline">Your AI has expert guidance</p>'
        '<div class="pricing-card__price">'
        '<span class="pricing-card__amount">$499</span>'
        '<span class="pricing-card__period">/month</span>'
        '</div>'
        '<div style="font-size:0.85rem; color:rgba(255,255,255,0.4); text-decoration:line-through; margin-top:4px;">$579/month*</div>'
        f'<ul class="pricing-card__features">{"".join(pa)}</ul>'
        "<button class=\"pricing-card__cta pricing-card__cta--secondary\" onclick=\"openWaitlistModal('Partnered')\">GET STARTED</button>"
        '</div>'
    )

    card_un = (
        '<div class="pricing-card">'
        '<h3 class="pricing-card__tier">Unified</h3>'
        '<p class="pricing-card__tagline">Full integration &amp; priority access</p>'
        '<div class="pricing-card__price">'
        '<span class="pricing-card__amount">$999</span>'
        '<span class="pricing-card__period">/month</span>'
        '</div>'
        '<div style="font-size:0.85rem; color:rgba(255,255,255,0.4); text-decoration:line-through; margin-top:4px;">$1,197/month*</div>'
        f'<ul class="pricing-card__features">{"".join(un)}</ul>'
        "<button class=\"pricing-card__cta pricing-card__cta--secondary\" onclick=\"openPayPalModal('Unified')\">GET STARTED</button>"
        '</div>'
    )

    card_en = (
        '<div class="pricing-card pricing-card--enterprise">'
        '<h3 class="pricing-card__tier">Enterprise</h3>'
        '<p class="pricing-card__tagline">Teams &amp; organizations</p>'
        '<div class="pricing-card__price">'
        '<span class="pricing-card__custom">Custom</span>'
        '</div>'
        f'<ul class="pricing-card__features">{"".join(en)}</ul>'
        "<button class=\"pricing-card__cta pricing-card__cta--secondary\" onclick=\"openWaitlistModal('Enterprise')\">LET'S TALK</button>"
        '</div>'
    )

    footnote = (
        '<p style="text-align:center; color:rgba(255,255,255,0.5); font-size:0.8rem; '
        'margin-top:40px; max-width:600px; margin-left:auto; margin-right:auto;">'
        '*Pricing post our full launch. Lock in the savings today for 1 full year!'
        '</p>'
    )

    return (
        f'<div class="pricing-grid">'
        f'{card_aw}{card_pa}{card_un}{card_en}'
        f'</div>'
        f'{footnote}'
    )


def replace_pricing_in_html(html_str):
    """
    Replace pricing-grid section in an HTML string.
    Works on either plain HTML or JSON-escaped HTML.
    Returns (new_html, success_bool)
    """
    # Detect if this is JSON-escaped (contains \\")
    # For JSON-escaped strings, the markers will have \\\" instead of "
    is_json = '\\"' in html_str

    if is_json:
        start_marker_pattern = r'<div class=\\"pricing-grid[^\\"]*\\">'
        end_marker = '<div class=\\"pricing-requirements\\">'
    else:
        start_marker_pattern = r'<div class="pricing-grid[^"]*">'
        end_marker = '<div class="pricing-requirements">'

    start_m = re.search(start_marker_pattern, html_str)
    if not start_m:
        return html_str, False

    start_i = start_m.start()
    end_i = html_str.find(end_marker, start_i)
    if end_i == -1:
        return html_str, False

    old_section = html_str[start_i:end_i]
    new_grid_plain = build_new_pricing_section()

    if is_json:
        # JSON-escape the new grid for embedding in Elementor data string
        # json.dumps escapes properly, we just remove the surrounding quotes
        new_grid_escaped = json.dumps(new_grid_plain)[1:-1]
        new_section = new_grid_escaped
    else:
        new_section = new_grid_plain

    new_html = html_str[:start_i] + new_section + html_str[end_i:]
    return new_html, True


def main():
    print("=" * 65)
    print("PRICING DEPLOYMENT: Page 688 (pay-test-sandbox-2)")
    print("5 tiers -> 4 tiers | Awakened $149 MOST POPULAR")
    print("=" * 65)

    # ---- Step 1: Fetch page from API ----
    print("\n[1/7] Fetching page 688 from WordPress API...")
    status, page = wp_request("GET", f"wp/v2/pages/{PAGE_ID}?context=edit")
    if status != 200:
        print(f"  ERROR: Status {status}")
        sys.exit(1)

    elementor_str = page.get("meta", {}).get("_elementor_data", "")
    raw_content = page.get("content", {}).get("raw", "")

    if not elementor_str:
        print("  ERROR: No _elementor_data in response")
        print("  Meta keys:", list(page.get("meta", {}).keys()))
        sys.exit(1)

    print(f"  _elementor_data: {len(elementor_str)} chars")
    print(f"  content.raw: {len(raw_content)} chars")

    # ---- Step 2: Save backups ----
    print("\n[2/7] Saving backups...")
    backup_e = "/home/jared/projects/AI-CIV/aether/exports/package-sandbox-2/page688_elementor_backup_pricing.txt"
    backup_c = "/home/jared/projects/AI-CIV/aether/exports/package-sandbox-2/page688_content_backup_pricing.html"
    with open(backup_e, "w") as f:
        f.write(elementor_str)
    with open(backup_c, "w") as f:
        f.write(raw_content)
    print(f"  Elementor backup: {backup_e}")
    print(f"  Content backup: {backup_c}")

    # ---- Step 3: Replace in _elementor_data ----
    print("\n[3/7] Replacing pricing in _elementor_data (JSON-escaped)...")
    new_elementor_str, ok_e = replace_pricing_in_html(elementor_str)
    if not ok_e:
        print("  ERROR: Could not find pricing section in _elementor_data")
        # Debug
        idx = elementor_str.find('pricing-grid')
        print(f"  'pricing-grid' in elementor_str: {idx != -1} at pos {idx}")
        sys.exit(1)
    print(f"  Replacement OK. New length: {len(new_elementor_str)}")
    # Quick spot checks
    for check, val in [("Bonded removed", "Bonded" not in new_elementor_str),
                       ("Awakened $149", "$149" in new_elementor_str),
                       ("MOST POPULAR", "MOST POPULAR" in new_elementor_str),
                       ("openPayPalModal", "openPayPalModal" in new_elementor_str)]:
        print(f"    {check}: {val}")

    # Validate the new _elementor_data parses as JSON (sanity check)
    print("  Validating JSON integrity...")
    try:
        json.loads(new_elementor_str)
        print("  JSON valid OK")
    except json.JSONDecodeError as e:
        print(f"  WARNING: JSON validation failed: {e}")
        # Not necessarily fatal — the data may be stored as a JSON string within JSON

    # ---- Step 4: Replace in content.raw ----
    print("\n[4/7] Replacing pricing in content.raw (plain HTML)...")
    new_raw_content, ok_c = replace_pricing_in_html(raw_content)
    if not ok_c:
        print("  WARNING: Could not find pricing section in content.raw")
        print("  Proceeding with _elementor_data update only")
    else:
        print(f"  Replacement OK. New length: {len(new_raw_content)}")

    # ---- Step 5: Push _elementor_data ----
    print("\n[5/7] Pushing _elementor_data to WordPress...")
    status_e, resp_e = wp_request(
        "POST",
        f"wp/v2/pages/{PAGE_ID}",
        {"meta": {"_elementor_data": new_elementor_str}}
    )
    if status_e not in (200, 201):
        print(f"  ERROR: Status {status_e}")
        sys.exit(1)
    print(f"  Elementor data pushed: {status_e}")

    # ---- Step 6: Push content.raw (if we have it) ----
    if ok_c and new_raw_content:
        print("\n[6/7] Pushing content.raw to WordPress...")
        status_c, resp_c = wp_request(
            "POST",
            f"wp/v2/pages/{PAGE_ID}",
            {"content": new_raw_content}
        )
        if status_c not in (200, 201):
            print(f"  WARNING: content.raw push returned {status_c}")
        else:
            print(f"  content.raw pushed: {status_c}")
    else:
        print("\n[6/7] Skipping content.raw push (no replacement found)")

    # ---- Step 7: Clear cache and verify ----
    print("\n[7/7] Clearing Elementor cache...")
    status_cache, _ = wp_request("DELETE", "elementor/v1/cache")
    print(f"  Cache clear: {status_cache}")

    print("\n  Waiting 5s for cache to propagate...")
    time.sleep(5)

    print("  Fetching live page for verification...")
    try:
        req = urllib.request.Request(f"{WP_URL}/pay-test-sandbox-2/", headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            live_html = resp.read().decode("utf-8")
        print(f"  Live page: {len(live_html)} chars")
    except Exception as ex:
        print(f"  WARNING: Could not fetch live page: {ex}")
        live_html = ""

    checks = [
        ("Awakened present", "Awakened" in live_html),
        ("$149 present", "$149" in live_html),
        ("$197/month* (strikethrough)", "$197/month*" in live_html),
        ("MOST POPULAR present", "MOST POPULAR" in live_html),
        ("CLAIM THIS SPOT present", "CLAIM THIS SPOT" in live_html),
        ("Partnered present", "Partnered" in live_html),
        ("$499 present", "$499" in live_html),
        ("$579/month* (strikethrough)", "$579/month*" in live_html),
        ("Unified present", "Unified" in live_html),
        ("$999 present", "$999" in live_html),
        ("$1,197/month* (strikethrough)", "$1,197/month*" in live_html),
        ("Enterprise present", "Enterprise" in live_html),
        ("Footnote present", "Lock in the savings today" in live_html),
        ("Bonded REMOVED", "Bonded" not in live_html),
        ("openPayPalModal preserved", "openPayPalModal" in live_html),
        ("openWaitlistModal preserved", "openWaitlistModal" in live_html),
    ]

    all_pass = True
    for name, result in checks:
        s = "PASS" if result else "FAIL"
        if not result:
            all_pass = False
        print(f"  [{s}] {name}")

    print("\n" + "=" * 65)
    if all_pass:
        print("DEPLOYMENT COMPLETE — ALL CHECKS PASSED")
        print("Review: https://purebrain.ai/pay-test-sandbox-2/")
    else:
        print("DEPLOYMENT COMPLETE — SOME CHECKS FAILED — review above")
    print("=" * 65)

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
