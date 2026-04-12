#!/usr/bin/env python3
"""
Post-GoDaddy Restore: WP REST API Content Audit
Since browser WAF blocks our IP, use REST API to inspect page content
Pages: 689 (pay-test-2) and 688 (pay-test-sandbox-2)
"""

import os
import re
import base64
import requests
import json

# Load env
def get_env():
    env = {}
    try:
        with open('/home/jared/projects/AI-CIV/aether/.env', 'r') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    try:
                        key, val = line.split('=', 1)
                        env[key.strip()] = val.strip().strip('"').strip("'")
                    except:
                        pass
    except Exception as e:
        print(f"Error loading .env: {e}")
    return env

env = get_env()
APP_PASS = env.get('PUREBRAIN_WP_APP_PASSWORD', '')
auth_b64 = base64.b64encode(f"Aether:{APP_PASS}".encode()).decode()
PAGE_PASSWORD = "PureBrain.ai253443$$$"
PAGE_PASSWORD_ENCODED = "PureBrain.ai253443%24%24%24"

PAGES = [
    {"id": 689, "name": "pay-test-2", "label": "PRODUCTION PayPal"},
    {"id": 688, "name": "pay-test-sandbox-2", "label": "SANDBOX PayPal"},
]


def fetch_page_content(page_id):
    """Fetch page content via WP REST API."""
    url = f"https://purebrain.ai/wp-json/wp/v2/pages?include={page_id}&password={PAGE_PASSWORD_ENCODED}&context=edit"
    headers = {"Authorization": f"Basic {auth_b64}"}
    resp = requests.get(url, headers=headers, timeout=30)
    if resp.status_code != 200:
        return None, f"HTTP {resp.status_code}: {resp.text[:200]}"
    data = resp.json()
    if not data:
        return None, "Empty response"
    return data[0], None


def analyze_content(page_data, page_name, label):
    """Deep analysis of page content for plugin state."""
    content = page_data.get('content', {}).get('raw', '')
    modified = page_data.get('modified', 'unknown')
    content_len = len(content)

    print(f"\n{'='*60}")
    print(f"PAGE: {page_name} ({label}) - ID: {page_data.get('id')}")
    print(f"Last modified: {modified}")
    print(f"Content length: {content_len:,} chars")
    print(f"{'='*60}")

    results = {
        'page_id': page_data.get('id'),
        'modified': modified,
        'content_length': content_len,
        'plugin_version': None,
        'paypal_sdk': {},
        'functions': {},
        'modals': {},
        'chatbox': {},
        'pricing': {},
        'flags': []
    }

    # --- PLUGIN VERSION CHECK ---
    version_matches = re.findall(r'ptc-v(\d+\.\d+\.\d+)', content)
    pb_version_matches = re.findall(r'PureBrain Plugin v(\d+\.\d+\.\d+)', content)
    results['plugin_version'] = version_matches[:3] + pb_version_matches[:3]
    print(f"\n[PLUGIN VERSION] References found: {results['plugin_version']}")

    # --- PAYPAL SDK CHECK ---
    # Check for PayPal SDK script tags
    paypal_scripts = re.findall(r'<script[^>]*src=["\']([^"\']*paypal[^"\']*)["\'][^>]*>', content, re.IGNORECASE)
    sandbox_mode = 'sandbox' in content.lower() and ('sandbox=true' in content.lower() or 'SANDBOX' in content)
    results['paypal_sdk']['scripts'] = paypal_scripts
    results['paypal_sdk']['sandbox_mode'] = sandbox_mode
    print(f"\n[PAYPAL SDK]")
    print(f"  Script tags: {paypal_scripts}")
    print(f"  Sandbox mode indicators: {'YES' if sandbox_mode else 'NO'}")

    # Check client IDs
    prod_client = re.findall(r'client-id=([A-Za-z0-9_-]{20,})', content)
    sandbox_client = re.findall(r'AWgW|sandbox.*client|client.*sandbox', content[:5000], re.IGNORECASE)
    results['paypal_sdk']['client_ids'] = prod_client[:3]
    print(f"  Client IDs found: {prod_client[:3]}")

    # --- FUNCTION DEFINITIONS ---
    print(f"\n[FUNCTION DEFINITIONS]")
    for fn_name in ['openWaitlistModal', 'openPayPalCheckout', 'openPayPalModal']:
        fn_count = content.count(f'function {fn_name}') + content.count(f'{fn_name} =') + content.count(f'{fn_name}=')
        # Get snippet of first definition
        idx = content.find(f'function {fn_name}')
        if idx == -1:
            idx = content.find(f'{fn_name} = function')
        snippet = content[idx:idx+200] if idx != -1 else 'NOT FOUND'
        results['functions'][fn_name] = {'count': fn_count, 'snippet': snippet[:150]}
        print(f"  {fn_name}: {fn_count} definitions, snippet: {snippet[:100]}")

    # --- MODAL CHECK ---
    print(f"\n[MODALS]")
    # Waitlist modal
    waitlist_modal = '#waitlistModal' in content or 'id="waitlistModal"' in content or "id='waitlistModal'" in content
    paypal_modal = '#pb-paypal-modal' in content or 'id="pb-paypal-modal"' in content
    results['modals']['waitlist_modal_present'] = waitlist_modal
    results['modals']['paypal_modal_present'] = paypal_modal
    print(f"  #waitlistModal present: {waitlist_modal}")
    print(f"  #pb-paypal-modal present: {paypal_modal}")

    # --- PRICING BUTTONS ---
    print(f"\n[PRICING BUTTONS]")
    # Find all onclick attributes on buttons
    button_onclicks = re.findall(r'onclick=["\']([^"\']*)["\']', content)
    tier_buttons = [o for o in button_onclicks if any(t in o for t in ['Awakened', 'Bonded', 'Partnered', 'Unified', 'PayPal', 'Waitlist'])]
    results['pricing']['button_onclicks'] = tier_buttons
    print(f"  Tier button onclicks: {tier_buttons}")

    # Check which function tier buttons call
    calls_paypal = any('PayPal' in o or 'paypal' in o for o in tier_buttons)
    calls_waitlist = any('Waitlist' in o or 'waitlist' in o for o in tier_buttons)
    results['pricing']['calls_paypal'] = calls_paypal
    results['pricing']['calls_waitlist'] = calls_waitlist
    print(f"  Buttons call PayPal function: {calls_paypal}")
    print(f"  Buttons call Waitlist function: {calls_waitlist}")

    # --- CHATBOX CHECK ---
    print(f"\n[CHATBOX]")
    chat_elements = {
        'chatMessages': 'id="chatMessages"' in content or "id='chatMessages'" in content,
        'userInput': 'id="userInput"' in content or "id='userInput'" in content,
        'awakeningSection': 'id="awakening"' in content or "id='awakening'" in content,
        'beginButton': 'chat-initial__btn' in content or 'Begin Your Awakening' in content,
        'oauthButton': 'oauth' in content.lower() and 'claude' in content.lower(),
        'birthCall': '/birth' in content or 'birth/start' in content,
    }
    results['chatbox'] = chat_elements
    for k, v in chat_elements.items():
        print(f"  {k}: {v}")

    # --- PLUGIN FLAGS ---
    print(f"\n[PLUGIN FLAGS]")
    flags_to_check = [
        ('[ptc-v4]', 'ptc-v4 plugin present'),
        ('[PB-FIX]', 'PB-FIX script present'),
        ('[PB-SANDBOX]', 'PB-SANDBOX script present'),
        ('[PB PayPal]', 'PB PayPal script present'),
        ('pool_exhausted', 'pool_exhausted reference'),
        ('waitlist_mode', 'waitlist_mode flag'),
        ('ptc-waitlist-mode', 'ptc-waitlist-mode'),
        ('force_waitlist', 'force_waitlist'),
    ]
    for pattern, desc in flags_to_check:
        found = pattern in content
        if found:
            results['flags'].append(desc)
            print(f"  FOUND: {desc}")

    if not results['flags']:
        print(f"  (No special flags found)")

    # --- DETERMINE VERDICT ---
    print(f"\n[VERDICT]")
    if not paypal_scripts:
        print(f"  STATUS: PLUGIN NOT LOADING - No PayPal SDK script tags found")
        results['verdict'] = 'PLUGIN_NOT_LOADING'
    elif calls_waitlist and not calls_paypal:
        print(f"  STATUS: WAITLIST MODE - Buttons call waitlist, not PayPal")
        results['verdict'] = 'WAITLIST_MODE'
    elif calls_paypal:
        print(f"  STATUS: PAYPAL MODE - Buttons call PayPal function")
        results['verdict'] = 'PAYPAL_MODE'
    else:
        print(f"  STATUS: UNKNOWN - Cannot determine mode")
        results['verdict'] = 'UNKNOWN'

    return results


def main():
    print("POST-RESTORE WP REST API AUDIT")
    print(f"Auth: Aether / {APP_PASS[:8]}...")
    print(f"Page password: {PAGE_PASSWORD[:10]}...")

    all_results = {}

    for page_config in PAGES:
        page_id = page_config['id']
        page_name = page_config['name']
        label = page_config['label']

        print(f"\nFetching page {page_id} ({page_name})...")
        data, error = fetch_page_content(page_id)

        if error:
            print(f"  ERROR fetching: {error}")
            all_results[page_name] = {'error': error}
            continue

        results = analyze_content(data, page_name, label)
        all_results[page_name] = results

    # Save results
    report_path = '/home/jared/projects/AI-CIV/aether/exports/screenshots/post-restore-audit/api-audit-results.json'
    with open(report_path, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\n\nFull results saved to: {report_path}")

    # Comparison summary
    print("\n\n" + "="*60)
    print("COMPARISON: pay-test-2 vs pay-test-sandbox-2")
    print("="*60)

    for name, r in all_results.items():
        if 'error' in r:
            print(f"\n{name}: ERROR - {r['error']}")
        else:
            print(f"\n{name}:")
            print(f"  Plugin version refs: {r.get('plugin_version', [])}")
            print(f"  PayPal scripts: {r.get('paypal_sdk', {}).get('scripts', [])}")
            print(f"  Verdict: {r.get('verdict', 'N/A')}")
            print(f"  Button onclicks: {r.get('pricing', {}).get('button_onclicks', [])}")

    return all_results


if __name__ == "__main__":
    main()
