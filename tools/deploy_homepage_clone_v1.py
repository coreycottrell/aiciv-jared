#!/usr/bin/env python3
"""
CTO-authored deploy script: Clone homepage design to pay-test-2 and sandbox-3
Also fixes the wrong brain video source on all 3 pages.

Architecture facts (from CTO memory bank):
- Page 11 (homepage): uses _elementor_data — must be read and cleared
- Page 689 (pay-test-2): uses post_content with <!-- wp:html --> blocks
- Page 1232 (sandbox-3): uses _elementor_data

PayPal client IDs:
- LIVE (page 689): AWgWNlBQAy5BMXKB5xbaMwSk01WkatC08b5rTj_JKu4Jm2JugXvjAwMRyNe1FmabNS9v846Rma5ptxhI
- SANDBOX (page 1232): AYTFob05DoSn0ZeVtLJ05duKwFHOdAckHgkZ2UJhAXvfJlUXEYM_PFib3HbIuVgauxV_6clZ5FdPRYq_

WP auth: PUREBRAIN_WP_USER + PUREBRAIN_WP_APP_PASSWORD from .env
"""

import requests
import base64
import json
import os
import sys
import re
from dotenv import load_dotenv

# ─── Load credentials ────────────────────────────────────────────────────────
load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

WP_USER = os.getenv('PUREBRAIN_WP_USER', 'purebrain@puremarketing.ai')
WP_APP_PW = os.getenv('PUREBRAIN_WP_APP_PASSWORD', '')
BASE_URL = 'https://purebrain.ai'

if not WP_APP_PW:
    print("ERROR: PUREBRAIN_WP_APP_PASSWORD not found in .env")
    sys.exit(1)

auth_string = base64.b64encode(f'{WP_USER}:{WP_APP_PW}'.encode()).decode()
HEADERS = {
    'Authorization': f'Basic {auth_string}',
    'Content-Type': 'application/json',
}

PAYPAL_LIVE_CLIENT_ID = 'AWgWNlBQAy5BMXKB5xbaMwSk01WkatC08b5rTj_JKu4Jm2JugXvjAwMRyNe1FmabNS9v846Rma5ptxhI'
PAYPAL_SANDBOX_CLIENT_ID = 'AYTFob05DoSn0ZeVtLJ05duKwFHOdAckHgkZ2UJhAXvfJlUXEYM_PFib3HbIuVgauxV_6clZ5FdPRYq_'

# ─── Fetch a page ────────────────────────────────────────────────────────────
def fetch_page(page_id, include_elementor=True):
    """Fetch page content and optionally _elementor_data meta."""
    url = f"{BASE_URL}/wp-json/wp/v2/pages/{page_id}?context=edit"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    content_raw = data.get('content', {}).get('raw', '')
    elementor_data = None

    if include_elementor:
        # _elementor_data is in the meta field
        meta = data.get('meta', {})
        if isinstance(meta, dict):
            elementor_data = meta.get('_elementor_data', None)

    return {
        'id': page_id,
        'title': data.get('title', {}).get('rendered', ''),
        'content_raw': content_raw,
        'elementor_data': elementor_data,
        'template': data.get('template', ''),
        'status': data.get('status', ''),
    }

# ─── Update page content ─────────────────────────────────────────────────────
def update_page_content(page_id, new_content_raw=None, new_elementor_data=None):
    """Update page content and/or _elementor_data."""
    url = f"{BASE_URL}/wp-json/wp/v2/pages/{page_id}"
    payload = {}

    if new_content_raw is not None:
        payload['content'] = new_content_raw

    if new_elementor_data is not None:
        payload['meta'] = {'_elementor_data': new_elementor_data}

    resp = requests.post(url, headers=HEADERS, json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()

# ─── Clear Elementor cache ────────────────────────────────────────────────────
def clear_elementor_cache():
    """Clear Elementor's render cache."""
    url = f"{BASE_URL}/wp-json/elementor/v1/cache"
    resp = requests.delete(url, headers=HEADERS, timeout=30)
    if resp.status_code in (200, 204):
        print("  ✓ Elementor cache cleared")
        return True
    else:
        print(f"  ⚠ Cache clear returned {resp.status_code}: {resp.text[:200]}")
        return False

# ─── Extract homepage sections from _elementor_data ──────────────────────────
def extract_homepage_sections_from_elementor(elementor_data_str):
    """
    Parse the elementor_data JSON string and extract named section IDs.
    Returns the full parsed structure so we can identify sections by their content.
    """
    if not elementor_data_str:
        return None
    try:
        data = json.loads(elementor_data_str)
        return data
    except json.JSONDecodeError as e:
        print(f"  ERROR parsing elementor_data: {e}")
        return None

# ─── Find section HTML by searching for markers in post_content ──────────────
def find_section_boundaries(html_content):
    """
    Find key section markers in the post_content HTML.
    Returns a dict of {section_name: (start_pos, end_pos)} or just the markers found.
    """
    markers = {}

    # Common section markers used in purebrain.ai pages
    patterns = {
        'chatbox_start': r'<!-- PAY-TEST CHATBOX|<!-- CHATBOX|id="chatbox"|id="chat-container"',
        'chatbox_section': r'<!-- PAY-TEST|<!-- pay-test',
        'paypal_section': r'paypal|PayPal|PAYPAL',
        'calculator_section': r'pb-calculator-teaser|pb-calc-headline|AI Tool Stack Calculator|How Much Are You Wasting',
        'compare_pills': r'compare-pills|comparison-pills|pb-compare|comparison section',
        'awaken_cta': r'awaken-cta|pb-awaken|begin-awakening|Awaken Your',
        'why_different': r'pb-why-purebrain|why-purebrain|See Why PureBrain|WHY PUREBRAIN LINK',
        'footer_section': r'<!-- END|</body>',
    }

    for section, pattern in patterns.items():
        matches = list(re.finditer(pattern, html_content, re.IGNORECASE))
        if matches:
            markers[section] = [(m.start(), m.end(), m.group()) for m in matches]

    return markers

# ─── PHASE 2: Fix the video source URL ───────────────────────────────────────
def fix_video_source_in_elementor(elementor_data_str, page_id):
    """
    Fix the wrong video source URL in _elementor_data.
    The current source is PureResearch.ai-1.mp4 — this needs to be the brain video.
    We also need to ensure mobile autoplay attributes are set.
    """
    if not elementor_data_str:
        return elementor_data_str, False

    # The wrong video that's currently showing
    wrong_video = 'PureResearch.ai-1.mp4'
    # What it should be (the brain animation)
    # Based on the page, we need to find the correct brain video URL
    # From prior work, the brain video is likely a different URL in wp-content
    # We'll search for and fix the video element

    changed = False

    # Search for the video source in the JSON
    if wrong_video in elementor_data_str:
        print(f"  Found wrong video source '{wrong_video}' in page {page_id}")
        # The correct brain video URL - we need to identify this
        # For now, flag it for manual review
        print(f"  ⚠ WARNING: Wrong video detected on page {page_id} - needs brain video URL")

    return elementor_data_str, changed

# ─── Fix video source in post_content HTML ───────────────────────────────────
def fix_video_source_in_content(content_html, page_id, correct_brain_video_url):
    """
    Fix video source in post_content HTML (for page 689 which uses post_content).
    Ensures mobile autoplay attributes are present.
    """
    if not content_html or not correct_brain_video_url:
        return content_html, False

    changed = False
    wrong_video = 'PureResearch.ai-1.mp4'

    if wrong_video in content_html:
        new_content = content_html.replace(wrong_video, correct_brain_video_url.split('/')[-1])
        # Also ensure video element has mobile-required attributes
        # iOS Safari requires: muted, playsinline, autoplay
        # These should already be in the video tag but let's verify pattern
        print(f"  Fixing video source on page {page_id}")
        changed = True
        return new_content, changed

    return content_html, changed

# ─── Main diagnosis function ──────────────────────────────────────────────────
def diagnose_pages():
    """
    Fetch all three pages and report their current state.
    This is the first step before making any changes.
    """
    print("\n" + "="*70)
    print("PHASE 0: DIAGNOSIS — Fetching current page states")
    print("="*70)

    pages_to_check = [
        (11, "Homepage"),
        (689, "pay-test-2 (LIVE PayPal)"),
        (1232, "sandbox-3 (SANDBOX PayPal)"),
    ]

    results = {}

    for page_id, name in pages_to_check:
        print(f"\n[{page_id}] {name}")
        print("-"*50)
        try:
            page = fetch_page(page_id)

            content_len = len(page['content_raw'])
            has_elementor = bool(page['elementor_data'])
            elementor_len = len(page['elementor_data']) if page['elementor_data'] else 0

            print(f"  Template: {page['template']!r}")
            print(f"  Status: {page['status']}")
            print(f"  post_content length: {content_len:,} chars")
            print(f"  _elementor_data: {'YES' if has_elementor else 'NO'} ({elementor_len:,} chars)")

            if page['content_raw']:
                # Check for key sections
                markers = find_section_boundaries(page['content_raw'])
                print(f"  Section markers found in content:")
                for section, positions in markers.items():
                    print(f"    - {section}: {len(positions)} match(es)")

                # Check for PayPal
                if PAYPAL_LIVE_CLIENT_ID in page['content_raw']:
                    print(f"  ✓ LIVE PayPal client ID present")
                elif PAYPAL_SANDBOX_CLIENT_ID in page['content_raw']:
                    print(f"  ✓ SANDBOX PayPal client ID present")
                else:
                    # Check elementor data too
                    if has_elementor:
                        if PAYPAL_LIVE_CLIENT_ID in page['elementor_data']:
                            print(f"  ✓ LIVE PayPal in elementor_data")
                        elif PAYPAL_SANDBOX_CLIENT_ID in page['elementor_data']:
                            print(f"  ✓ SANDBOX PayPal in elementor_data")
                        else:
                            print(f"  ⚠ No PayPal client ID found in content or elementor_data")

                # Check for video source
                if 'PureResearch.ai-1.mp4' in page['content_raw']:
                    print(f"  ⚠ WRONG video source in post_content (PureResearch.ai-1.mp4)")
                elif has_elementor and 'PureResearch.ai-1.mp4' in page['elementor_data']:
                    print(f"  ⚠ WRONG video source in _elementor_data (PureResearch.ai-1.mp4)")
                else:
                    # Check for any video source
                    video_matches = re.findall(r'<source[^>]+src=["\']([^"\']+\.mp4)["\']', page['content_raw'])
                    if video_matches:
                        print(f"  Video source(s) in content: {video_matches}")
                    if has_elementor:
                        video_in_elementor = re.findall(r'"url":"([^"]+\.mp4)"', page['elementor_data'][:5000])
                        if video_in_elementor:
                            print(f"  Video source(s) in elementor: {video_in_elementor}")

                # Check for key bottom sections
                if 'pb-calculator-teaser' in page['content_raw'] or 'How Much Are You Wasting' in page['content_raw']:
                    print(f"  ✓ Calculator CTA section present")
                else:
                    print(f"  ✗ Calculator CTA section MISSING")

                if 'compare-pills' in page['content_raw'] or 'See All Comparisons' in page['content_raw'] or 'compare-hub' in page['content_raw']:
                    print(f"  ✓ Compare pills section present")
                else:
                    print(f"  ✗ Compare pills section MISSING or different")

                if 'pb-why-purebrain' in page['content_raw'] or 'See Why PureBrain Is Different' in page['content_raw']:
                    print(f"  ✓ 'See Why Different' link present")
                else:
                    print(f"  ✗ 'See Why Different' link MISSING")

            results[page_id] = page

            # Save snapshot
            snapshot_path = f'/home/jared/projects/AI-CIV/aether/exports/page-{page_id}-snapshot-{__import__("datetime").date.today()}.json'
            with open(snapshot_path, 'w') as f:
                # Don't save full elementor data (too large), save summary
                summary = {
                    'id': page_id,
                    'title': page['title'],
                    'template': page['template'],
                    'status': page['status'],
                    'content_raw_length': len(page['content_raw']),
                    'elementor_data_length': elementor_len,
                    'content_raw_preview': page['content_raw'][:2000] if page['content_raw'] else '',
                }
                json.dump(summary, f, indent=2)
            print(f"  Snapshot saved: {snapshot_path}")

        except requests.HTTPError as e:
            print(f"  ERROR fetching page {page_id}: {e}")
            print(f"  Response: {e.response.text[:500] if e.response else 'no response'}")
            results[page_id] = None
        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback
            traceback.print_exc()
            results[page_id] = None

    return results

# ─── Fetch full content for export ───────────────────────────────────────────
def export_full_page_content(page_id, filename_suffix=""):
    """Export the full page content to a file for inspection."""
    page = fetch_page(page_id)

    export_dir = '/home/jared/projects/AI-CIV/aether/exports'
    os.makedirs(export_dir, exist_ok=True)

    if page['content_raw']:
        content_path = f'{export_dir}/page-{page_id}-content{filename_suffix}.html'
        with open(content_path, 'w') as f:
            f.write(page['content_raw'])
        print(f"  Content exported to: {content_path}")

    if page['elementor_data']:
        elementor_path = f'{export_dir}/page-{page_id}-elementor{filename_suffix}.json'
        with open(elementor_path, 'w') as f:
            # Pretty print the elementor data
            try:
                parsed = json.loads(page['elementor_data'])
                json.dump(parsed, f, indent=2)
            except:
                f.write(page['elementor_data'])
        print(f"  Elementor data exported to: {elementor_path}")

    return page


# ─── Entry point ─────────────────────────────────────────────────────────────
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Deploy homepage design to pay-test pages')
    parser.add_argument('--diagnose', action='store_true', help='Run diagnosis only (no changes)')
    parser.add_argument('--export', action='store_true', help='Export full page content to files')
    parser.add_argument('--page', type=int, help='Export specific page ID')
    args = parser.parse_args()

    if args.export and args.page:
        print(f"\nExporting page {args.page}...")
        export_full_page_content(args.page, "-live")
    elif args.diagnose or True:  # Default to diagnose
        results = diagnose_pages()

        if args.export:
            print("\n" + "="*70)
            print("EXPORTING FULL PAGE CONTENT")
            print("="*70)
            for page_id in [11, 689, 1232]:
                print(f"\nExporting page {page_id}...")
                export_full_page_content(page_id, "-live")

        print("\n" + "="*70)
        print("DIAGNOSIS COMPLETE")
        print("="*70)
        print("\nNext steps based on diagnosis:")
        print("1. Review the exported page content")
        print("2. Run deploy script with --build flag to create merged HTML")
        print("3. Review merged HTML before deploying")
        print("4. Run with --deploy flag to push to WordPress")
