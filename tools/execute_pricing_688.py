#!/usr/bin/env python3
"""
EXECUTE: Surgical pricing update on page 688 (pay-test-sandbox-2).
Run this script to deploy.
"""
import json
import re
import sys
import time
import requests
from requests.auth import HTTPBasicAuth

WP_URL = "https://purebrain.ai"
WP_USER = "purebrainai"
WP_PASS = "FlFr2VOtlHiHaJWjzW96OHUJ"
PAGE_ID = 688
AUTH = HTTPBasicAuth(WP_USER, WP_PASS)

SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>'


def li(text, color="blue", bold=False):
    inner = f"<strong>{text}</strong>" if bold else text
    return f'<li class="pricing-card__feature pricing-card__feature--{color}">{SVG}{inner}</li>'


def new_pricing():
    aw_feats = "".join([
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
    ])

    pa_feats = "".join([
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
    ])

    un_feats = "".join([
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
    ])

    en_feats = "".join([
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
    ])

    card_aw = f'''<div class="pricing-card pricing-card--featured"><div class="pricing-card__badge">MOST POPULAR</div><h3 class="pricing-card__tier">Awakened</h3><p class="pricing-card__tagline">Your AI partnership begins</p><div class="pricing-card__price"><span class="pricing-card__amount">$149</span><span class="pricing-card__period">/month</span></div><div style="font-size:0.85rem; color:rgba(255,255,255,0.4); text-decoration:line-through; margin-top:4px;">$197/month*</div><ul class="pricing-card__features">{aw_feats}</ul><button class="pricing-card__cta pricing-card__cta--primary" onclick="openWaitlistModal('Awakened')">CLAIM THIS SPOT</button></div>'''

    card_pa = f'''<div class="pricing-card"><h3 class="pricing-card__tier">Partnered</h3><p class="pricing-card__tagline">Your AI has expert guidance</p><div class="pricing-card__price"><span class="pricing-card__amount">$499</span><span class="pricing-card__period">/month</span></div><div style="font-size:0.85rem; color:rgba(255,255,255,0.4); text-decoration:line-through; margin-top:4px;">$579/month*</div><ul class="pricing-card__features">{pa_feats}</ul><button class="pricing-card__cta pricing-card__cta--secondary" onclick="openWaitlistModal('Partnered')">GET STARTED</button></div>'''

    card_un = f'''<div class="pricing-card"><h3 class="pricing-card__tier">Unified</h3><p class="pricing-card__tagline">Full integration &amp; priority access</p><div class="pricing-card__price"><span class="pricing-card__amount">$999</span><span class="pricing-card__period">/month</span></div><div style="font-size:0.85rem; color:rgba(255,255,255,0.4); text-decoration:line-through; margin-top:4px;">$1,089/month*</div><ul class="pricing-card__features">{un_feats}</ul><button class="pricing-card__cta pricing-card__cta--secondary" onclick="openPayPalModal('Unified')">GET STARTED</button></div>'''

    card_en = f'''<div class="pricing-card pricing-card--enterprise"><h3 class="pricing-card__tier">Enterprise</h3><p class="pricing-card__tagline">Teams &amp; organizations</p><div class="pricing-card__price"><span class="pricing-card__custom">Custom</span></div><ul class="pricing-card__features">{en_feats}</ul><button class="pricing-card__cta pricing-card__cta--secondary" onclick="openWaitlistModal('Enterprise')">LET'S TALK</button></div>'''

    footnote = '<p style="text-align:center; color:rgba(255,255,255,0.5); font-size:0.8rem; margin-top:40px; max-width:600px; margin-left:auto; margin-right:auto;">*Pricing post our full launch. Lock in the savings today for 1 full year!</p>'

    return f'<div class="pricing-grid">{card_aw}{card_pa}{card_un}{card_en}</div>{footnote}'


def find_html_widget(element):
    results = []
    if isinstance(element, list):
        for item in element:
            results.extend(find_html_widget(item))
    elif isinstance(element, dict):
        if element.get("widgetType") == "html":
            html_val = element.get("settings", {}).get("html", "")
            if "pricing-grid" in html_val:
                results.append(element)
        for child in element.get("elements", []):
            results.extend(find_html_widget(child))
    return results


def main():
    print("=" * 60)
    print("PRICING UPDATE: Page 688 | 5 tiers -> 4 tiers")
    print("=" * 60)

    # 1. Fetch live _elementor_data
    print("\n[1] Fetching live Elementor data...")
    r = requests.get(
        f"{WP_URL}/wp-json/wp/v2/pages/{PAGE_ID}?context=edit",
        auth=AUTH, timeout=30
    )
    r.raise_for_status()
    page = r.json()
    elementor_str = page.get("meta", {}).get("_elementor_data", "")
    if not elementor_str:
        print("ERROR: No _elementor_data in API response")
        print("Available meta keys:", list(page.get("meta", {}).keys()))
        sys.exit(1)
    print(f"  Got {len(elementor_str)} chars of Elementor data")

    # 2. Parse
    print("\n[2] Parsing Elementor JSON...")
    elementor_data = json.loads(elementor_str)
    print(f"  Parsed OK, type: {type(elementor_data).__name__}")

    # 3. Find widget
    print("\n[3] Finding pricing HTML widget...")
    widgets = find_html_widget(elementor_data)
    print(f"  Found {len(widgets)} widget(s)")
    if not widgets:
        print("ERROR: No widget found with pricing-grid")
        sys.exit(1)

    widget = widgets[0]
    original_html = widget["settings"]["html"]
    print(f"  Widget ID: {widget['id']}, HTML: {len(original_html)} chars")

    # Save backup
    backup_path = "/home/jared/projects/AI-CIV/aether/exports/package-sandbox-2/page688_widget_backup_pre_pricing.html"
    with open(backup_path, "w") as f:
        f.write(original_html)
    print(f"  Backup: {backup_path}")

    # 4. Replace pricing section
    print("\n[4] Replacing pricing section...")
    start_m = re.search(r'<div class="pricing-grid[^"]*">', original_html)
    end_i = original_html.find('<div class="pricing-requirements">')
    if not start_m:
        print("ERROR: pricing-grid not found")
        sys.exit(1)
    if end_i == -1:
        print("ERROR: pricing-requirements not found")
        sys.exit(1)

    start_i = start_m.start()
    old = original_html[start_i:end_i]
    print(f"  Replacing {len(old)} chars")
    print(f"  Old has Bonded: {'Bonded' in old}")

    new_grid = new_pricing()
    new_html = original_html[:start_i] + new_grid + original_html[end_i:]
    print(f"  New HTML: {len(new_html)} chars")

    # Verify replacement
    inserted = new_html[start_i:start_i + len(new_grid)]
    print(f"  Awakened $149: {'$149' in inserted}")
    print(f"  MOST POPULAR: {'MOST POPULAR' in inserted}")
    print(f"  Strikethrough $197: {'$197/month*' in inserted}")
    print(f"  Partnered $499: {'$499' in inserted}")
    print(f"  Unified $999: {'$999' in inserted}")
    print(f"  Enterprise Custom: {'pricing-card--enterprise' in inserted}")
    print(f"  Footnote: {'Lock in the savings today' in inserted}")
    print(f"  Bonded gone: {'Bonded' not in inserted}")
    print(f"  openPayPalModal in full HTML: {'openPayPalModal' in new_html}")

    # Update widget
    widget["settings"]["html"] = new_html

    # 5. Push back
    print("\n[5] Pushing to WordPress...")
    new_str = json.dumps(elementor_data, ensure_ascii=False)
    push = requests.post(
        f"{WP_URL}/wp-json/wp/v2/pages/{PAGE_ID}",
        auth=AUTH,
        json={"meta": {"_elementor_data": new_str}},
        timeout=60
    )
    if push.status_code not in (200, 201):
        print(f"ERROR: {push.status_code}")
        print(push.text[:300])
        sys.exit(1)
    print(f"  Pushed OK: {push.status_code}")

    # 6. Clear cache
    print("\n[6] Clearing Elementor cache...")
    cache = requests.delete(
        f"{WP_URL}/wp-json/elementor/v1/cache",
        auth=AUTH, timeout=30
    )
    print(f"  Cache: {cache.status_code}")

    # 7. Verify live
    print("\n[7] Verifying live page...")
    time.sleep(4)
    live = requests.get(f"{WP_URL}/pay-test-sandbox-2/", timeout=30)
    body = live.text

    all_pass = True
    checks = [
        ("$149 on live page", "$149" in body),
        ("$197/month* strikethrough", "$197/month*" in body),
        ("Awakened present", "Awakened" in body),
        ("Partnered present", "Partnered" in body),
        ("$579/month* strikethrough", "$579/month*" in body),
        ("Unified present", "Unified" in body),
        ("$1,089/month* strikethrough", "$1,089/month*" in body),
        ("Enterprise present", "Enterprise" in body),
        ("MOST POPULAR present", "MOST POPULAR" in body),
        ("CLAIM THIS SPOT present", "CLAIM THIS SPOT" in body),
        ("Footnote present", "Lock in the savings today" in body),
        ("Bonded GONE", "Bonded" not in body),
        ("PayPal modal preserved", "openPayPalModal" in body),
        ("Waitlist modal preserved", "openWaitlistModal" in body),
    ]

    for name, result in checks:
        s = "PASS" if result else "FAIL"
        if not result:
            all_pass = False
        print(f"  [{s}] {name}")

    print("\n" + "=" * 60)
    if all_pass:
        print("COMPLETE — ALL CHECKS PASSED")
    else:
        print("COMPLETE — SOME CHECKS FAILED")
    print("=" * 60)

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
