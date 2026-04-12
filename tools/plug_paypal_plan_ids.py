#!/usr/bin/env python3
"""Plug PayPal Plan IDs into pay-test pages (439 and 468).

Replaces the empty PLAN_IDS config with real Plan IDs.
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

# Load plan IDs from config
config_path = Path(__file__).parent.parent / 'config' / 'paypal_plans.json'
with open(config_path) as f:
    config = json.load(f)

PLAN_IDS = config['plan_ids']
PAGES = [439, 468]

# Old PLAN_IDS config (empty placeholders)
OLD_PLAN_IDS = (
    "PLAN_IDS = {\\n"
    "    Awakened:  '', // e.g. 'P-XXXXXXXXXXXXXXXXXXXXXX'\\n"
    "    Bonded:    '', // e.g. 'P-YYYYYYYYYYYYYYYYYYYYYY'\\n"
    "    Partnered: '', // e.g. 'P-ZZZZZZZZZZZZZZZZZZZZZZ'\\n"
    "    Unified:   '', // e.g. 'P-WWWWWWWWWWWWWWWWWWWWWW'\\n"
    "  }"
)

NEW_PLAN_IDS = (
    "PLAN_IDS = {\\n"
    f"    Awakened:  '{PLAN_IDS['Awakened']}',\\n"
    f"    Bonded:    '{PLAN_IDS['Bonded']}',\\n"
    f"    Partnered: '{PLAN_IDS['Partnered']}',\\n"
    f"    Unified:   '{PLAN_IDS['Unified']}',\\n"
    "  }"
)


def update_page(page_id):
    print(f'\n{"="*60}')
    print(f'Processing page {page_id}...')
    print(f'{"="*60}')

    r = requests.get(
        f'{SITE}/wp-json/wp/v2/pages/{page_id}',
        auth=AUTH,
        params={'context': 'edit'}
    )
    r.raise_for_status()
    page_data = r.json()

    elem_data = page_data.get('meta', {}).get('_elementor_data', '')
    if not elem_data:
        print(f'[ERROR] No _elementor_data on page {page_id}')
        return False

    print(f'[OK] Fetched: {len(elem_data)} chars')

    # Check if plan IDs already present
    if PLAN_IDS['Awakened'] in elem_data:
        print(f'[SKIP] Plan IDs already present on page {page_id}')
        return True

    modified = elem_data

    # Replace PLAN_IDS
    if OLD_PLAN_IDS in modified:
        modified = modified.replace(OLD_PLAN_IDS, NEW_PLAN_IDS, 1)
        print(f'[OK] Replaced PLAN_IDS config')
    else:
        # Try to find it with flexible matching
        import re
        pattern = r"PLAN_IDS\s*=\s*\{[^}]*\}"
        match = re.search(pattern, modified)
        if match:
            old_text = match.group(0)
            print(f'[DEBUG] Found PLAN_IDS: {old_text[:100]}...')
            # Build replacement
            new_text = (
                "PLAN_IDS = {\\n"
                f"    Awakened:  '{PLAN_IDS['Awakened']}',\\n"
                f"    Bonded:    '{PLAN_IDS['Bonded']}',\\n"
                f"    Partnered: '{PLAN_IDS['Partnered']}',\\n"
                f"    Unified:   '{PLAN_IDS['Unified']}',\\n"
                "  }"
            )
            modified = modified.replace(old_text, new_text, 1)
            print(f'[OK] Replaced PLAN_IDS (flexible match)')
        else:
            print(f'[ERROR] Could not find PLAN_IDS config on page {page_id}')
            # Debug: search for PLAN_IDS
            idx = modified.find('PLAN_IDS')
            if idx >= 0:
                ctx = modified[idx:idx+300]
                print(f'  Found at {idx}: {repr(ctx[:200])}')
            return False

    if modified == elem_data:
        print(f'[SKIP] No changes needed')
        return True

    # Save
    r2 = requests.post(
        f'{SITE}/wp-json/wp/v2/pages/{page_id}',
        auth=AUTH,
        json={'meta': {'_elementor_data': modified}}
    )
    if r2.status_code in (200, 201):
        print(f'[OK] Saved page {page_id}')
        return True
    else:
        print(f'[ERROR] Save failed: HTTP {r2.status_code}')
        print(r2.text[:500])
        return False


def main():
    print('Plan IDs to plug in:')
    for name, pid in PLAN_IDS.items():
        print(f'  {name}: {pid}')

    results = {}
    for pid in PAGES:
        results[pid] = update_page(pid)

    # Clear caches
    print('\n--- Clearing caches ---')
    r = requests.delete(f'{SITE}/wp-json/elementor/v1/cache', auth=AUTH)
    print(f'[CACHE] Elementor: HTTP {r.status_code}')

    print('\n' + '='*60)
    print('RESULTS:')
    for pid, ok in results.items():
        print(f'  Page {pid}: {"OK" if ok else "FAILED"}')
    print('='*60)

    return all(results.values())


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
