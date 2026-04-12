#!/usr/bin/env python3
"""Swap testimonial headshot image and update border to white on all 4 pages.

Old image: jared-sanborn-headshot.jpg
New image: jared-sanborn-headshot-official.png
Old border: rgba(42, 147, 193, 0.4) (blue)
New border: rgba(255, 255, 255, 0.6) (white)
"""

import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env')

SITE = 'https://purebrain.ai'
AUTH = ('Aether', os.getenv('PUREBRAIN_WP_APP_PASSWORD', ''))

OLD_IMG = 'jared-sanborn-headshot.jpg'
NEW_IMG = 'jared-sanborn-headshot-official.png'

# Blue border → white thin border
OLD_BORDER = 'rgba(42, 147, 193, 0.4)'
NEW_BORDER = 'rgba(255, 255, 255, 0.6)'

PAGES = [11, 174, 338, 383]


def swap_on_page(page_id):
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

    modified = elem_data
    changes = 0

    # 1. Swap image filename
    if OLD_IMG in modified:
        count = modified.count(OLD_IMG)
        modified = modified.replace(OLD_IMG, NEW_IMG)
        changes += count
        print(f'[OK] Swapped image filename ({count} occurrences)')
    else:
        print(f'[SKIP] Old image not found on page {page_id}')
        # Check if new image is already there
        if NEW_IMG in modified:
            print(f'[INFO] New image already present')
        else:
            print(f'[WARN] Neither old nor new image found!')

    # 2. Swap border color (blue → white)
    if OLD_BORDER in modified:
        count = modified.count(OLD_BORDER)
        modified = modified.replace(OLD_BORDER, NEW_BORDER)
        changes += count
        print(f'[OK] Swapped border color to white ({count} occurrences)')
    else:
        print(f'[INFO] Old blue border not found - checking for other border patterns')
        # Try the CSS escaped version
        old_esc = OLD_BORDER.replace(' ', '')  # rgba(42,147,193,0.4)
        new_esc = NEW_BORDER.replace(' ', '')
        if old_esc in modified:
            count = modified.count(old_esc)
            modified = modified.replace(old_esc, new_esc)
            changes += count
            print(f'[OK] Swapped border color (no-space variant, {count} occurrences)')

    if modified == elem_data:
        print(f'[SKIP] No changes needed on page {page_id}')
        return True

    # Save
    r2 = requests.post(
        f'{SITE}/wp-json/wp/v2/pages/{page_id}',
        auth=AUTH,
        json={'meta': {'_elementor_data': modified}}
    )
    if r2.status_code in (200, 201):
        print(f'[OK] Saved page {page_id} ({changes} changes)')
        return True
    else:
        print(f'[ERROR] Save failed: HTTP {r2.status_code}')
        print(r2.text[:500])
        return False


def main():
    results = {}
    for pid in PAGES:
        results[pid] = swap_on_page(pid)

    # Clear Elementor cache
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
