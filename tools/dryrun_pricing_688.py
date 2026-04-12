#!/usr/bin/env python3
"""
Dry-run: verify replacement logic works without touching WordPress.
Outputs the new HTML section to a file for review.
"""
import json
import re
import sys

def fi(text, color="blue", bold=False):
    CHECK_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>'
    inner = f"<strong>{text}</strong>" if bold else text
    return (
        f'\n                        <li class="pricing-card__feature pricing-card__feature--{color}">'
        f'{CHECK_SVG}{inner}</li>'
    )

def build_new_pricing_html():
    awakened = f"""
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
                    <button class="pricing-card__cta pricing-card__cta--primary" onclick="openWaitlistModal('Awakened')">CLAIM THIS SPOT</button>
                </div>"""

    partnered = f"""
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
                    <button class="pricing-card__cta pricing-card__cta--secondary" onclick="openWaitlistModal('Partnered')">GET STARTED</button>
                </div>"""

    unified = f"""
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
                    <button class="pricing-card__cta pricing-card__cta--secondary" onclick="openPayPalModal('Unified')">GET STARTED</button>
                </div>"""

    enterprise = f"""
                <div class="pricing-card pricing-card--enterprise">
                    <h3 class="pricing-card__tier">Enterprise</h3>
                    <p class="pricing-card__tagline">Teams &amp; organizations</p>
                    <div class="pricing-card__price">
                        <span class="pricing-card__custom">Custom</span>
                    </div>
                    <ul class="pricing-card__features">{fi('Everything in Unified, plus:')}{fi('Unlimited consulting hours')}{fi('Dedicated infrastructure')}{fi('99.9% uptime SLA')}{fi('White-label options')}{fi('Custom integrations')}{fi('Multi-team deployment')}{fi('Custom SLA terms')}{fi('Executive strategy sessions')}{fi('Dedicated account manager')}{fi('On-site training available')}{fi('Enterprise API access')}
                    </ul>
                    <button class="pricing-card__cta pricing-card__cta--secondary" onclick="openWaitlistModal('Enterprise')">LET'S TALK</button>
                </div>"""

    footnote = """
            <p style="text-align:center; color:rgba(255,255,255,0.5); font-size:0.8rem; margin-top:40px; max-width:600px; margin-left:auto; margin-right:auto;">
                *Pricing post our full launch. Lock in the savings today for 1 full year!
            </p>"""

    return f"""<div class="pricing-grid">
{awakened}
{partnered}
{unified}
{enterprise}
            </div>
{footnote}
            """


def find_html_widget(element):
    results = []
    if isinstance(element, list):
        for item in element:
            results.extend(find_html_widget(item))
    elif isinstance(element, dict):
        if element.get('widgetType') == 'html':
            settings = element.get('settings', {})
            html_val = settings.get('html', '')
            if html_val and 'pricing-grid' in html_val:
                results.append(element)
        for child in element.get('elements', []):
            results.extend(find_html_widget(child))
    return results


print("Loading local Elementor JSON...")
with open('/home/jared/projects/AI-CIV/aether/exports/package-sandbox-2/page688_elementor_data.json') as f:
    elementor_data = json.load(f)

print(f"Top-level elements: {len(elementor_data)}")

print("Finding HTML widget with pricing-grid...")
widgets = find_html_widget(elementor_data)
print(f"Found {len(widgets)} matching widget(s)")

if not widgets:
    print("ERROR: No widget found")
    sys.exit(1)

w = widgets[0]
html = w['settings']['html']
print(f"Widget ID: {w['id']}, HTML length: {len(html)}")

# Find pricing section in the HTML
start_match = re.search(r'<div class="pricing-grid[^"]*">', html)
end_idx = html.find('<div class="pricing-requirements">')

if not start_match:
    print("ERROR: pricing-grid not found in widget HTML")
    sys.exit(1)
if end_idx == -1:
    print("ERROR: pricing-requirements not found in widget HTML")
    sys.exit(1)

start_idx = start_match.start()
old_section = html[start_idx:end_idx]
print(f"\nOld pricing section: {len(old_section)} chars")
print(f"Starts with: {old_section[:80]}")
print(f"Contains Bonded: {'Bonded' in old_section}")
print(f"Contains Awakened: {'Awakened' in old_section}")
print(f"Contains Partnered: {'Partnered' in old_section}")
print(f"Contains Unified: {'Unified' in old_section}")
print(f"Contains Enterprise: {'Enterprise' in old_section}")

new_grid = build_new_pricing_html()
new_html = html[:start_idx] + new_grid + html[end_idx:]

print(f"\nNew pricing section: {len(new_grid)} chars")
print(f"\nNew HTML total length: {len(new_html)} (was {len(html)})")

# Verify
new_section = new_html[start_idx:start_idx+len(new_grid)+200]
print(f"\nVerification:")
print(f"  $149 present: {'$149' in new_section}")
print(f"  $197/month* present: {'$197/month*' in new_section}")
print(f"  $499 present: {'$499' in new_section}")
print(f"  $579/month* present: {'$579/month*' in new_section}")
print(f"  $999 present: {'$999' in new_section}")
print(f"  $1,089/month* present: {'$1,089/month*' in new_section}")
print(f"  MOST POPULAR present: {'MOST POPULAR' in new_section}")
print(f"  CLAIM THIS SPOT present: {'CLAIM THIS SPOT' in new_section}")
print(f"  Footnote present: {'Lock in the savings today' in new_section}")
print(f"  Bonded removed: {'Bonded' not in new_section}")
print(f"  openPayPalModal preserved: {'openPayPalModal' in new_html}")
print(f"  openWaitlistModal preserved: {'openWaitlistModal' in new_html}")

# Save new HTML for inspection
out_path = '/home/jared/projects/AI-CIV/aether/exports/package-sandbox-2/page688_new_pricing_section.html'
with open(out_path, 'w') as f:
    f.write(new_grid)
print(f"\nNew pricing section saved to: {out_path}")

print("\nDRY-RUN COMPLETE — ready for live deployment")
