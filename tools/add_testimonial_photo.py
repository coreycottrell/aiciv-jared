#!/usr/bin/env python3
"""Add Jared's headshot photo to testimonial sections.

Targets: Homepage (11), PB2 (174), PB3 (338), PB4 (383)
NOT touching: pay-test (439), pay-test-sandbox (468)

Two testimonial structures exist:
  - Pages 11/174/338: testimonial-card__author (BEM-style)
  - Page 383: testimonial-author with testimonial-name/role spans

Usage:
    python3 tools/add_testimonial_photo.py              # Apply to all 4 pages
    python3 tools/add_testimonial_photo.py --dry-run     # Preview
    python3 tools/add_testimonial_photo.py --page 11     # Single page
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env')

SITE = 'https://purebrain.ai'
AUTH = ('Aether', os.getenv('PUREBRAIN_WP_APP_PASSWORD', ''))
HEADSHOT_URL = 'https://purebrain.ai/wp-content/uploads/2026/02/jared-sanborn-headshot.jpg'

# Pages to update (NOT pay-test pages)
PAGES = [11, 174, 338, 383]

# CSS for testimonial photos - injected once per page
TESTIMONIAL_PHOTO_CSS = """
/* ── Testimonial Author Photos ──────────────────────────── */
.testimonial-card__author-wrap {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-top: 16px;
}

.testimonial-card__photo,
.testimonial-author__photo {
    width: 56px;
    height: 56px;
    border-radius: 50%;
    object-fit: cover;
    border: 2px solid rgba(42, 147, 193, 0.4);
    flex-shrink: 0;
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
    color: #888888;
    font-size: 0.8rem;
}

/* PB4 style - testimonial-author with photo */
.testimonial-author--with-photo {
    display: flex !important;
    align-items: center;
    gap: 14px;
}

.testimonial-author--with-photo .testimonial-name {
    display: block;
}

.testimonial-author--with-photo .testimonial-role {
    display: block;
}
"""


def apply_to_page(page_id, dry_run=False):
    """Add Jared's photo to testimonial on a specific page."""
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

    # Check if already done
    if 'jared-sanborn-headshot' in elem_data:
        print(f'[SKIP] Headshot already present on page {page_id}')
        return True

    modified = elem_data
    changes = 0

    # Strategy 1: Pages 11, 174, 338 - BEM-style testimonial-card__author
    # Old: <p class="testimonial-card__author">— Jared Sanborn, CEO of PureBrain.ai, PureMarketing.ai & PureTechnology.ai</p>
    # New: Author wrap with photo + name + role

    # The exact format from debug output:
    # <p class=\"testimonial-card__author\">— Jared Sanborn, CEO of PureBrain.ai, PureMarketing.ai & PureTechnology.ai</p>
    old_bem = (
        '<p class=\\"testimonial-card__author\\">\\u2014 Jared Sanborn, '
        'CEO of PureBrain.ai, PureMarketing.ai & PureTechnology.ai</p>'
    )
    new_bem = (
        '<div class=\\"testimonial-card__author-wrap\\">'
        f'<img class=\\"testimonial-card__photo\\" src=\\"{HEADSHOT_URL}\\" alt=\\"Jared Sanborn\\">'
        '<div class=\\"testimonial-card__author-info\\">'
        '<span class=\\"testimonial-card__author-name\\">Jared Sanborn</span>'
        '<span class=\\"testimonial-card__author-role\\">CEO of PureBrain.ai, PureMarketing.ai & PureTechnology.ai</span>'
        '</div></div>'
    )

    if old_bem in modified:
        modified = modified.replace(old_bem, new_bem, 1)
        changes += 1
        print(f'[OK] Replaced BEM-style testimonial author (with photo)')
    else:
        # Try with literal em-dash
        alt_old = old_bem.replace('\\u2014', '\u2014')
        alt_new = new_bem
        if alt_old in modified:
            modified = modified.replace(alt_old, alt_new, 1)
            changes += 1
            print(f'[OK] Replaced BEM-style author (literal em-dash)')
        else:
            # Try &amp; variant
            alt2 = old_bem.replace('& PureTechnology', '&amp; PureTechnology')
            if alt2 in modified:
                modified = modified.replace(alt2, new_bem.replace('& PureTechnology', '&amp; PureTechnology'), 1)
                changes += 1
                print(f'[OK] Replaced BEM-style author (&amp; variant)')
            else:
                # Last resort: search for the actual bytes
                jared_idx = modified.find('Jared Sanborn')
                if jared_idx >= 0:
                    ctx = modified[max(0,jared_idx-200):jared_idx+200]
                    print(f'[DEBUG] Found "Jared Sanborn" at {jared_idx}')
                    print(f'  Context: {repr(ctx[:300])}')

    # Strategy 2: Page 383 (PB4) - different structure
    # Old: <div class="testimonial-author">
    #        <span class="testimonial-name">Jared Sanborn</span>
    #        <span class="testimonial-role">CEO of PureBrain.ai...</span>
    #      </div>
    old_pb4 = (
        '<div class=\\"testimonial-author\\">\\n'
        '          <span class=\\"testimonial-name\\">Jared Sanborn</span>\\n'
        '          <span class=\\"testimonial-role\\">CEO of PureBrain.ai, PureMarketing.ai &amp; PureTechnology.ai</span>\\n'
        '        </div>'
    )
    new_pb4 = (
        '<div class=\\"testimonial-author testimonial-author--with-photo\\">'
        f'<img class=\\"testimonial-author__photo\\" src=\\"{HEADSHOT_URL}\\" alt=\\"Jared Sanborn\\">'
        '<div>'
        '<span class=\\"testimonial-name\\">Jared Sanborn</span>'
        '<span class=\\"testimonial-role\\">CEO of PureBrain.ai, PureMarketing.ai &amp; PureTechnology.ai</span>'
        '</div></div>'
    )

    if old_pb4 in modified:
        modified = modified.replace(old_pb4, new_pb4, 1)
        changes += 1
        print(f'[OK] Replaced PB4-style testimonial author (with photo)')

    # Inject CSS for testimonial photos
    if changes > 0:
        css_escaped = TESTIMONIAL_PHOTO_CSS.replace('\n', '\\n').replace('"', '\\"')

        # Strategy: inject right after the existing .testimonial-card__author CSS rule
        # The pattern in the data:
        # .testimonial-card__author {\n            font-size: 0.9rem;\n            color: var(--text-muted);\n        }
        css_anchor = '.testimonial-card__author {\\n            font-size: 0.9rem;\\n            color: var(--text-muted);\\n        }'
        css_anchor_idx = modified.find(css_anchor)
        if css_anchor_idx >= 0:
            inject_at = css_anchor_idx + len(css_anchor)
            modified = modified[:inject_at] + '\\n' + css_escaped + modified[inject_at:]
            changes += 1
            print(f'[OK] Injected photo CSS after .testimonial-card__author')
        else:
            # PB4 uses different class names - try testimonial-author
            css_anchor_pb4 = '.testimonial-author'
            css_anchor_pb4_idx = modified.find(css_anchor_pb4)
            if css_anchor_pb4_idx >= 0:
                # Find the closing brace of this rule
                brace_idx = modified.find('}', css_anchor_pb4_idx)
                if brace_idx >= 0:
                    inject_at = brace_idx + 1
                    modified = modified[:inject_at] + '\\n' + css_escaped + modified[inject_at:]
                    changes += 1
                    print(f'[OK] Injected photo CSS after .testimonial-author')
            else:
                # Fallback: inject before the testimonial HTML section
                fallback_marker = 'testimonials-grid'
                fallback_idx = modified.find(fallback_marker)
                if fallback_idx >= 0:
                    search_back = modified[max(0, fallback_idx-500):fallback_idx]
                    div_idx = search_back.rfind('<div')
                    if div_idx >= 0:
                        inject_at = fallback_idx - 500 + div_idx
                        style_inject = f'<style>{css_escaped}</style>'
                        modified = modified[:inject_at] + style_inject + modified[inject_at:]
                        changes += 1
                        print(f'[OK] Injected CSS (fallback inline style)')
                    else:
                        print('[WARN] Could not find CSS injection point')
                else:
                    print('[WARN] No testimonial CSS anchor found')

    if changes == 0:
        print(f'[WARN] No changes made to page {page_id} - need manual investigation')
        # Let's do a more flexible search
        for pattern in ['Jared Sanborn', 'testimonial-card__author', 'testimonial-author']:
            idx = modified.find(pattern)
            if idx >= 0:
                ctx = modified[max(0,idx-100):idx+200]
                print(f'  Found "{pattern}" at {idx}: {repr(ctx[:200])}')
        return False

    # Save
    if dry_run:
        print(f'[DRY RUN] Would save {len(modified)} chars')
        return True

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
    parser = argparse.ArgumentParser(description='Add testimonial photos')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--page', type=int)
    args = parser.parse_args()

    pages = [args.page] if args.page else PAGES
    results = {}

    for pid in pages:
        results[pid] = apply_to_page(pid, dry_run=args.dry_run)

    # Clear caches
    if not args.dry_run and any(results.values()):
        print('\n--- Clearing caches ---')
        r = requests.delete(f'{SITE}/wp-json/elementor/v1/cache', auth=AUTH)
        print(f'[CACHE] Elementor: HTTP {r.status_code}')

    print('\n' + '='*60)
    for pid, ok in results.items():
        print(f'  Page {pid}: {"OK" if ok else "FAILED"}')
    print('='*60)

    return all(results.values())


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
