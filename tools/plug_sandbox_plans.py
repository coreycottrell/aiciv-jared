#!/usr/bin/env python3
"""Plug Sandbox PayPal Plan IDs + Client ID into pay-test-sandbox (page 468).

Replaces:
1. SANDBOX_CLIENT_ID_PLACEHOLDER with real sandbox Client ID
2. Live Plan IDs with sandbox Plan IDs
"""

import os
import sys
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env')

SITE = 'https://purebrain.ai'
AUTH = ('Aether', os.getenv('PUREBRAIN_WP_APP_PASSWORD', ''))
PAGE_ID = 468

SANDBOX_CLIENT_ID = os.getenv('PAYPAL_SANDBOX_CLIENT_ID', '')

# Load sandbox plan IDs
config_path = Path(__file__).parent.parent / 'config' / 'paypal_sandbox_plans.json'
with open(config_path) as f:
    sandbox_config = json.load(f)
SANDBOX_PLANS = sandbox_config['plan_ids']

# Load live plan IDs (what's currently on the page)
live_config_path = Path(__file__).parent.parent / 'config' / 'paypal_plans.json'
with open(live_config_path) as f:
    live_config = json.load(f)
LIVE_PLANS = live_config['plan_ids']


def main():
    print('='*60)
    print('Plugging Sandbox PayPal into page 468')
    print('='*60)
    print(f'Sandbox Client ID: {SANDBOX_CLIENT_ID[:20]}...')
    print('Sandbox Plan IDs:')
    for name, pid in SANDBOX_PLANS.items():
        print(f'  {name}: {pid}')

    # Fetch page
    r = requests.get(
        f'{SITE}/wp-json/wp/v2/pages/{PAGE_ID}',
        auth=AUTH,
        params={'context': 'edit'}
    )
    r.raise_for_status()
    page_data = r.json()

    elem_data = page_data.get('meta', {}).get('_elementor_data', '')
    if not elem_data:
        print('[ERROR] No _elementor_data')
        return False

    print(f'[OK] Fetched: {len(elem_data)} chars')
    modified = elem_data
    changes = 0

    # 1. Replace Client ID placeholder (or live client ID)
    live_client_id = os.getenv('PAYPAL_CLIENT_ID', '')

    if 'SANDBOX_CLIENT_ID_PLACEHOLDER' in modified:
        modified = modified.replace('SANDBOX_CLIENT_ID_PLACEHOLDER', SANDBOX_CLIENT_ID)
        print('[OK] Replaced SANDBOX_CLIENT_ID_PLACEHOLDER with real sandbox Client ID')
        changes += 1
    elif live_client_id and live_client_id in modified:
        modified = modified.replace(live_client_id, SANDBOX_CLIENT_ID)
        print('[OK] Replaced live Client ID with sandbox Client ID')
        changes += 1
    else:
        print('[WARN] Could not find Client ID to replace')
        # Check what's there
        idx = modified.find('PAYPAL_CLIENT_ID')
        if idx < 0:
            idx = modified.find('client-id=')
        if idx >= 0:
            print(f'  Found at {idx}: {modified[idx:idx+100]}')

    # 2. Replace live Plan IDs with sandbox Plan IDs
    for tier_name in ['Awakened', 'Bonded', 'Partnered', 'Unified']:
        live_id = LIVE_PLANS.get(tier_name, '')
        sandbox_id = SANDBOX_PLANS.get(tier_name, '')
        if live_id and sandbox_id and live_id in modified:
            modified = modified.replace(live_id, sandbox_id)
            print(f'[OK] Replaced {tier_name} Plan ID: {live_id} → {sandbox_id}')
            changes += 1
        elif live_id and live_id not in modified:
            print(f'[WARN] Live Plan ID for {tier_name} not found in page')
        else:
            print(f'[WARN] Missing plan ID for {tier_name}')

    # 3. Replace API endpoint (live → sandbox)
    if 'api-m.paypal.com' in modified:
        # Don't replace - the PayPal SDK handles this based on client-id
        # The SDK auto-detects sandbox vs live based on the client ID format
        print('[INFO] PayPal SDK auto-detects sandbox mode from client ID')

    if changes == 0:
        print('[SKIP] No changes needed')
        return True

    print(f'\n[INFO] Made {changes} replacements')

    # Save
    r2 = requests.post(
        f'{SITE}/wp-json/wp/v2/pages/{PAGE_ID}',
        auth=AUTH,
        json={'meta': {'_elementor_data': modified}}
    )
    if r2.status_code in (200, 201):
        print(f'[OK] Saved page {PAGE_ID}')
    else:
        print(f'[ERROR] Save failed: HTTP {r2.status_code}')
        print(r2.text[:500])
        return False

    # Clear cache
    r3 = requests.delete(f'{SITE}/wp-json/elementor/v1/cache', auth=AUTH)
    print(f'[CACHE] Elementor: HTTP {r3.status_code}')

    return True


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
