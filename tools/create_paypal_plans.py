#!/usr/bin/env python3
"""Create PayPal subscription plans for PureBrain.

Plans to create:
  - Awakened:  $79/month
  - Bonded:    $149/month
  - Partnered: $499/month
  - Unified:   $999/month
  - Enterprise: custom (no PayPal button, but create plan for reference)

Uses PayPal REST API v1 (Billing Plans + Products).
"""

import os
import sys
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env')

CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID', '')
SECRET = os.getenv('PAYPAL_SECRET', '')

# Live API
BASE = 'https://api-m.paypal.com'

PLANS = [
    {'name': 'Awakened',   'price': '79.00',  'description': 'PureBrain Awakened - AI-powered business intelligence'},
    {'name': 'Bonded',     'price': '149.00', 'description': 'PureBrain Bonded - Deep AI partnership for growing businesses'},
    {'name': 'Partnered',  'price': '499.00', 'description': 'PureBrain Partnered - Full AI integration for scaling enterprises'},
    {'name': 'Unified',    'price': '999.00', 'description': 'PureBrain Unified - Complete AI transformation suite'},
]


def get_access_token():
    """Get OAuth2 access token from PayPal."""
    r = requests.post(
        f'{BASE}/v1/oauth2/token',
        auth=(CLIENT_ID, SECRET),
        data={'grant_type': 'client_credentials'},
        headers={'Accept': 'application/json'}
    )
    if r.status_code != 200:
        print(f'[ERROR] Auth failed: HTTP {r.status_code}')
        print(r.text)
        return None
    token = r.json().get('access_token')
    print(f'[OK] Got access token: {token[:20]}...')
    return token


def create_product(token):
    """Create a Product (required before plans)."""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Prefer': 'return=representation',
    }
    payload = {
        'name': 'PureBrain AI Subscriptions',
        'description': 'AI-powered business intelligence and transformation platform',
        'type': 'SERVICE',
        'category': 'SOFTWARE',
        'home_url': 'https://purebrain.ai',
    }
    r = requests.post(f'{BASE}/v1/catalogs/products', headers=headers, json=payload)
    if r.status_code in (200, 201):
        product = r.json()
        print(f'[OK] Created product: {product["id"]}')
        return product['id']
    else:
        print(f'[ERROR] Product creation failed: HTTP {r.status_code}')
        print(r.text)
        return None


def create_plan(token, product_id, name, price, description):
    """Create a Billing Plan."""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Prefer': 'return=representation',
    }
    payload = {
        'product_id': product_id,
        'name': name,
        'description': description,
        'status': 'ACTIVE',
        'billing_cycles': [
            {
                'frequency': {
                    'interval_unit': 'MONTH',
                    'interval_count': 1,
                },
                'tenure_type': 'REGULAR',
                'sequence': 1,
                'total_cycles': 0,  # Infinite
                'pricing_scheme': {
                    'fixed_price': {
                        'value': price,
                        'currency_code': 'USD',
                    }
                }
            }
        ],
        'payment_preferences': {
            'auto_bill_outstanding': True,
            'payment_failure_threshold': 3,
        },
    }
    r = requests.post(f'{BASE}/v1/billing/plans', headers=headers, json=payload)
    if r.status_code in (200, 201):
        plan = r.json()
        print(f'[OK] Created plan "{name}": {plan["id"]} (${price}/mo)')
        return plan['id']
    else:
        print(f'[ERROR] Plan "{name}" creation failed: HTTP {r.status_code}')
        print(r.text[:500])
        return None


def main():
    if not CLIENT_ID or not SECRET:
        print('[ERROR] Missing PAYPAL_CLIENT_ID or PAYPAL_SECRET in .env')
        return False

    print('='*60)
    print('Creating PayPal Subscription Plans for PureBrain')
    print('='*60)

    # Step 1: Get access token
    token = get_access_token()
    if not token:
        return False

    # Step 2: Create product
    product_id = create_product(token)
    if not product_id:
        return False

    # Step 3: Create plans
    plan_ids = {}
    for plan in PLANS:
        pid = create_plan(token, product_id, plan['name'], plan['price'], plan['description'])
        if pid:
            plan_ids[plan['name']] = pid
        else:
            print(f'[WARN] Failed to create {plan["name"]} plan')

    # Step 4: Output results
    print('\n' + '='*60)
    print('RESULTS:')
    print('='*60)
    print(f'Product ID: {product_id}')
    print()
    for name, pid in plan_ids.items():
        price = [p['price'] for p in PLANS if p['name'] == name][0]
        print(f"  {name:12s} ${price}/mo  →  {pid}")

    print('\nPLAN_IDS config for pay-test pages:')
    print('PLAN_IDS = {')
    for name in ['Awakened', 'Bonded', 'Partnered', 'Unified']:
        pid = plan_ids.get(name, '')
        print(f"    {name}: '{pid}',")
    print('}')

    # Save results
    results = {
        'product_id': product_id,
        'plan_ids': plan_ids,
        'environment': 'LIVE',
        'base_url': BASE,
    }
    results_path = Path(__file__).parent.parent / 'config' / 'paypal_plans.json'
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f'\n[OK] Results saved to {results_path}')

    return len(plan_ids) == len(PLANS)


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
