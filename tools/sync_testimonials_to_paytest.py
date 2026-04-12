#!/usr/bin/env python3
"""Sync testimonial headshot + LinkedIn links from homepage to pay-test pages.

Homepage (11) has:
- Headshot photo with circle CSS + white border
- LinkedIn link on photo + name
- BEM structure (.testimonial-card__author-wrap, __photo, __linkedin-link, __author-info)

Pay-test (439, 468) have:
- Old plain text: <p class="testimonial-card__author">— Jared Sanborn...</p>
- No headshot, no LinkedIn links
- Missing CSS for photo/LinkedIn classes

This script syncs both the HTML and CSS.
"""

import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env')

SITE = 'https://purebrain.ai'
AUTH = ('Aether', os.getenv('PUREBRAIN_WP_APP_PASSWORD', ''))
PAGES = [439, 468]

# OLD: plain text author line on pay-test pages
OLD_AUTHOR = (
    '<p class=\\"testimonial-card__author\\">\\u2014 Jared Sanborn, '
    'CEO of PureBrain.ai, PureMarketing.ai &amp; PureTechnology.ai</p>'
)

# Also try with non-encoded ampersand
OLD_AUTHOR_ALT = (
    '<p class=\\"testimonial-card__author\\">\\u2014 Jared Sanborn, '
    'CEO of PureBrain.ai, PureMarketing.ai & PureTechnology.ai</p>'
)

# NEW: headshot + LinkedIn structure (from homepage)
NEW_AUTHOR = (
    '<div class=\\"testimonial-card__author-wrap\\">'
    '<a href=\\"https://www.linkedin.com/in/jaredsanborn/\\" target=\\"_blank\\" '
    'rel=\\"noopener noreferrer\\" class=\\"testimonial-card__linkedin-link\\">'
    '<img class=\\"testimonial-card__photo\\" '
    'src=\\"https://purebrain.ai/wp-content/uploads/2026/02/jared-sanborn-headshot-official.png\\" '
    'alt=\\"Jared Sanborn\\"></a>'
    '<div class=\\"testimonial-card__author-info\\">'
    '<a href=\\"https://www.linkedin.com/in/jaredsanborn/\\" target=\\"_blank\\" '
    'rel=\\"noopener noreferrer\\" class=\\"testimonial-card__linkedin-link\\">'
    '<span class=\\"testimonial-card__author-name\\">Jared Sanborn</span></a>'
    '<span class=\\"testimonial-card__author-role\\">'
    'CEO of PureBrain.ai, PureMarketing.ai &amp; PureTechnology.ai'
    '</span></div></div>'
)

# CSS for testimonial photos and LinkedIn links (to inject into existing <style> block)
TESTIMONIAL_CSS = """

        /* Testimonial headshot photo */
        .testimonial-card__photo,
        .testimonial-author__photo {
            width: 56px !important;
            min-width: 56px !important;
            max-width: 56px !important;
            height: 56px !important;
            border-radius: 50% !important;
            object-fit: cover !important;
            border: 2px solid rgba(255, 255, 255, 0.6) !important;
            flex-shrink: 0;
        }

        .testimonial-card__author-wrap {
            display: inline-flex;
            align-items: center;
            gap: 12px;
            margin-top: 16px;
        }

        .testimonial-card__author-info {
            display: flex;
            flex-direction: column;
            gap: 2px;
        }

        .testimonial-card__author-name {
            font-weight: 600;
            color: #ffffff;
            font-size: 0.95rem;
        }

        .testimonial-card__author-role {
            color: rgba(255, 255, 255, 0.5);
            font-size: 0.8rem;
        }

        .testimonial-card__linkedin-link {
            text-decoration: none;
            color: inherit;
            cursor: pointer;
            transition: opacity 0.2s ease;
        }

        .testimonial-card__linkedin-link:hover {
            opacity: 0.85;
        }

        .testimonial-card__linkedin-link:hover .testimonial-card__photo {
            border-color: rgba(255, 255, 255, 0.9) !important;
            transform: scale(1.05);
        }

        .testimonial-card__linkedin-link:hover .testimonial-card__author-name {
            color: #2a93c1;
        }"""


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
        print(f'[ERROR] No _elementor_data')
        return False

    print(f'[OK] Fetched: {len(elem_data)} chars')
    modified = elem_data
    changes = 0

    # 1. Replace author HTML
    if 'testimonial-card__author-wrap' in modified:
        print('[SKIP] Author wrap already exists (testimonial already synced)')
    elif OLD_AUTHOR in modified:
        modified = modified.replace(OLD_AUTHOR, NEW_AUTHOR, 1)
        print('[OK] Replaced author HTML (with headshot + LinkedIn)')
        changes += 1
    elif OLD_AUTHOR_ALT in modified:
        modified = modified.replace(OLD_AUTHOR_ALT, NEW_AUTHOR, 1)
        print('[OK] Replaced author HTML alt (with headshot + LinkedIn)')
        changes += 1
    else:
        # Try to find what's actually there
        idx = modified.find('Jared Sanborn')
        if idx > 0:
            ctx = modified[max(0,idx-200):idx+200]
            print(f'[WARN] Could not match author pattern. Found "Jared Sanborn" at {idx}:')
            print(f'  {repr(ctx[:300])}')
        else:
            print('[WARN] No "Jared Sanborn" found on page')

    # 2. Add CSS if missing
    if 'testimonial-card__photo' not in modified:
        # Find the last </style> or a good CSS injection point
        # Look for the closing of the main style block
        css_escaped = TESTIMONIAL_CSS.replace('\n', '\\n').replace('"', '\\"')

        # Find the CSS section - look for existing testimonial-card CSS
        inject_point = modified.find('.testimonial-card {')
        if inject_point < 0:
            inject_point = modified.find('testimonial-card')

        if inject_point > 0:
            # Find the end of the style block that contains testimonial-card
            # Insert before the </style> that follows
            style_end = modified.find('</style>', inject_point)
            if style_end > 0:
                modified = modified[:style_end] + css_escaped + modified[style_end:]
                print('[OK] Injected testimonial photo + LinkedIn CSS')
                changes += 1
            else:
                print('[WARN] Could not find </style> after testimonial CSS')
        else:
            print('[WARN] Could not find testimonial-card CSS section')
    else:
        print('[SKIP] Testimonial photo CSS already present')

    if changes == 0:
        print('[SKIP] No changes needed')
        return True

    print(f'[INFO] Made {changes} changes')

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
