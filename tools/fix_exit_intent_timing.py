#!/usr/bin/env python3
"""Fix exit-intent popup timing: trigger after naming, BEFORE celebration.

Currently `state.exitIntentEnabled = true` is set inside revealPricing() (celebration).
Jared wants it to trigger as soon as the AI name is chosen (naming complete).

Fix:
1. Add `state.exitIntentEnabled = true;` right after `state.aiName = detectedName;`
2. Keep the one in revealPricing() (harmless duplicate - setting true twice is fine)

Apply to all 5 chatbox pages: 11, 174, 338, 439, 468
"""

import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env')

SITE = 'https://purebrain.ai'
AUTH = ('Aether', os.getenv('PUREBRAIN_WP_APP_PASSWORD', ''))
PAGES = [11, 174, 338, 439, 468]

# The pattern where AI name gets set (naming moment)
# We want to add exitIntentEnabled = true right after this line
OLD_PATTERN = 'state.aiName = detectedName;'
NEW_PATTERN = 'state.aiName = detectedName;\\n                state.exitIntentEnabled = true;'


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

    # Check if the pattern exists
    if OLD_PATTERN not in elem_data:
        print(f'[WARN] Pattern "state.aiName = detectedName;" not found')
        # Try to find what's there
        idx = elem_data.find('state.aiName')
        if idx > 0:
            snippet = elem_data[idx:idx+200]
            print(f'[DEBUG] Found "state.aiName" at {idx}: {repr(snippet[:150])}')
        else:
            print(f'[SKIP] No state.aiName on this page (may not have chatbox)')
        return True  # Not an error - page may not have chatbox

    # Check if already fixed
    if 'state.exitIntentEnabled = true;' in elem_data:
        # Check if it's ONLY in revealPricing or also at naming point
        # Find the naming point
        naming_idx = elem_data.find(OLD_PATTERN)
        # Check if exitIntentEnabled is within 100 chars after naming point
        after_naming = elem_data[naming_idx:naming_idx + 200]
        if 'exitIntentEnabled' in after_naming:
            print(f'[SKIP] exitIntentEnabled already set at naming point')
            return True
        else:
            print(f'[INFO] exitIntentEnabled exists but only in revealPricing, adding at naming point')

    # Make the replacement (only first occurrence - the naming moment)
    modified = elem_data.replace(OLD_PATTERN, NEW_PATTERN, 1)

    if modified == elem_data:
        print('[SKIP] No changes made')
        return True

    size_diff = len(modified) - len(elem_data)
    print(f'[INFO] Size change: {size_diff:+d} chars')

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
    results = {}
    for pid in PAGES:
        results[pid] = update_page(pid)

    # Clear cache
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
