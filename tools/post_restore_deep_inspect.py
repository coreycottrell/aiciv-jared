#!/usr/bin/env python3
"""
Deep inspection of page 689 content to understand exact PayPal vs Waitlist state.
"""

import re
import base64
import requests

def get_env():
    env = {}
    with open('/home/jared/projects/AI-CIV/aether/.env', 'r') as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                try:
                    key, val = line.split('=', 1)
                    env[key.strip()] = val.strip().strip('"').strip("'")
                except:
                    pass
    return env

env = get_env()
APP_PASS = env.get('PUREBRAIN_WP_APP_PASSWORD', '')
auth_b64 = base64.b64encode(f"Aether:{APP_PASS}".encode()).decode()
PAGE_PASSWORD_ENCODED = "PureBrain.ai253443%24%24%24"


def fetch(page_id):
    url = f"https://purebrain.ai/wp-json/wp/v2/pages?include={page_id}&password={PAGE_PASSWORD_ENCODED}&context=edit"
    resp = requests.get(url, headers={"Authorization": f"Basic {auth_b64}"}, timeout=30)
    return resp.json()[0]['content']['raw']


def analyze(page_id, page_name):
    print(f"\n{'='*70}")
    print(f"DEEP INSPECT: {page_name} (ID: {page_id})")
    print(f"{'='*70}")
    content = fetch(page_id)

    # --- FIND ALL INLINE SCRIPTS ---
    scripts = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL | re.IGNORECASE)
    paypal_scripts = [s for s in scripts if 'paypal' in s.lower() or 'PayPal' in s]
    waitlist_scripts = [s for s in scripts if 'waitlist' in s.lower() or 'openWaitlistModal' in s]

    print(f"\n[INLINE SCRIPTS] Total: {len(scripts)}, PayPal-related: {len(paypal_scripts)}, Waitlist-related: {len(waitlist_scripts)}")

    for i, s in enumerate(paypal_scripts):
        print(f"\n  [PayPal Script {i+1}] ({len(s)} chars)")
        print(f"    First 500 chars: {s[:500]}")

    # --- ALL openWaitlistModal DEFINITIONS ---
    print(f"\n[openWaitlistModal DEFINITIONS]")
    idx = 0
    found = 0
    while True:
        pos = content.find('function openWaitlistModal', idx)
        if pos == -1:
            break
        found += 1
        snippet = content[pos:pos+300]
        # Determine which type this is
        is_waitlist_form = 'waitlistForm' in snippet or 'Full Name' in snippet or 'waitlist-form' in snippet.lower()
        is_paypal = 'paypal' in snippet.lower() or 'PayPal' in snippet
        print(f"  Definition #{found} at char {pos}:")
        print(f"    Type: {'WAITLIST FORM' if is_waitlist_form else 'PAYPAL' if is_paypal else 'UNKNOWN'}")
        print(f"    Snippet: {snippet[:200]}")
        idx = pos + 1

    # --- PRICING CARD BUTTONS ---
    print(f"\n[PRICING CARD BUTTONS - Full onclick]")
    # Find all button elements near pricing section
    pricing_section = re.search(r'id=["\']pricing["\'].*?(?=id=["\']awakening["\'])', content, re.DOTALL)
    if pricing_section:
        pricing_html = pricing_section.group(0)
        btn_onclicks = re.findall(r'onclick=["\']([^"\']+)["\']', pricing_html)
        print(f"  All onclicks in pricing section:")
        for o in btn_onclicks:
            print(f"    {o}")
    else:
        print(f"  Could not isolate pricing section, searching globally...")
        all_onclicks = re.findall(r'onclick=["\']([^"\']+)["\']', content)
        tier_related = [o for o in all_onclicks if any(t in o for t in ['Awakened', 'Bonded', 'Partnered', 'Unified', 'PayPal', 'Waitlist'])]
        for o in tier_related:
            print(f"    {o}")

    # --- PB-FIX SCRIPT ---
    print(f"\n[PB-FIX SCRIPTS]")
    pb_fix_scripts = [s for s in scripts if '[PB-FIX]' in s or 'PB-FIX' in s]
    for i, s in enumerate(pb_fix_scripts):
        print(f"  [PB-FIX Script {i+1}] ({len(s)} chars):")
        print(f"    {s[:400]}")

    # --- PB PAYPAL SCRIPTS ---
    print(f"\n[PB PayPal SCRIPTS]")
    pb_pp_scripts = [s for s in scripts if '[PB PayPal]' in s or 'PB PayPal' in s]
    for i, s in enumerate(pb_pp_scripts):
        print(f"  [PB PayPal Script {i+1}] ({len(s)} chars):")
        print(f"    {s[:600]}")

    # --- PAYPAL SDK LOADING MECHANISM ---
    print(f"\n[HOW PAYPAL SDK LOADS]")
    # Check for dynamic script injection
    dynamic_load = [s for s in scripts if 'document.createElement' in s and 'paypal' in s.lower()]
    print(f"  Dynamic injection scripts: {len(dynamic_load)}")
    for s in dynamic_load:
        print(f"    {s[:300]}")

    # Check plugin_footer / wp_footer hooks
    wp_footer_mentions = content.count('wp_footer')
    print(f"  wp_footer mentions in content: {wp_footer_mentions}")

    # --- LAST MODIFIED + CONTENT HASH ---
    print(f"\n[CONTENT SUMMARY]")
    print(f"  Content length: {len(content):,}")
    # Check for specific PayPal client ID
    client_ids = re.findall(r'AWgW[A-Za-z0-9_-]{10,}', content)
    sandbox_ids = re.findall(r'AZD[A-Za-z0-9_-]{10,}', content)
    print(f"  Production client IDs: {list(set(client_ids))[:3]}")
    print(f"  Sandbox client IDs: {list(set(sandbox_ids))[:3]}")

    # Check plugin slug references
    plugin_refs = re.findall(r'ptc-[a-z-]+(?:/[a-z-]+)?\.(?:js|css)', content)
    print(f"  Plugin file references: {list(set(plugin_refs))[:10]}")

    return content


# Run on page 689 (pay-test-2)
content_689 = analyze(689, "pay-test-2 (PRODUCTION)")

# Quick check on 688 to see if it differs
print(f"\n\n{'='*70}")
print("QUICK DIFF: Are the two pages structurally the same?")
print(f"{'='*70}")
content_688 = fetch(688)
print(f"Page 689 length: {len(content_689):,}")
print(f"Page 688 length: {len(content_688):,}")

# Compare key indicators
for indicator in ['openWaitlistModal', 'openPayPalModal', 'openPayPalCheckout', 'sandbox', 'waitlistModal']:
    count_689 = content_689.count(indicator)
    count_688 = content_688.count(indicator)
    same = "SAME" if count_689 == count_688 else "DIFFERENT"
    print(f"  '{indicator}': page689={count_689}, page688={count_688} [{same}]")

# Check if sandbox page has different PayPal client ID
prod_ids = set(re.findall(r'AWgW[A-Za-z0-9_-]{10,}', content_689))
sandbox_ids_688 = set(re.findall(r'AWgW[A-Za-z0-9_-]{10,}', content_688))
print(f"\nProduction client IDs in 689: {prod_ids}")
print(f"PayPal client IDs in 688: {sandbox_ids_688}")

# Check for sandbox-specific indicator
sandbox_mode_688 = 'sandbox' in content_688.lower()
print(f"Sandbox mode in 688: {sandbox_mode_688}")
sandbox_snippets = re.findall(r'.{0,50}sandbox.{0,50}', content_688, re.IGNORECASE)[:5]
for s in sandbox_snippets:
    print(f"  sandbox context: '{s}'")
