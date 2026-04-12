#!/usr/bin/env python3
"""
Deploy 9 competitor exodus pages to purebrain.ai WordPress.
Then fix cross-links and add comparison footer to 5 existing pages.
"""

import os
import re
import json
import time
import requests
from dotenv import load_dotenv

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

BASE_URL = 'https://purebrain.ai'
WP_API = f'{BASE_URL}/wp-json/wp/v2'
AUTH = ('Aether', os.environ['PUREBRAIN_WP_APP_PASSWORD'])
EXPORTS = '/home/jared/projects/AI-CIV/aether/exports'

# ─── PAGE DEFINITIONS ───
PAGES = [
    {
        'file': 'competitor-exodus-hub.html',
        'slug': 'compare',
        'title': 'Compare AI Tools to PureBrain',
    },
    {
        'file': 'competitor-exodus-chatgpt.html',
        'slug': 'purebrain-vs-chatgpt',
        'title': 'PureBrain vs ChatGPT',
    },
    {
        'file': 'competitor-exodus-claude.html',
        'slug': 'purebrain-vs-claude',
        'title': 'PureBrain vs Claude',
    },
    {
        'file': 'competitor-exodus-copilot.html',
        'slug': 'purebrain-vs-copilot',
        'title': 'PureBrain vs Microsoft Copilot',
    },
    {
        'file': 'competitor-exodus-custom-gpts.html',
        'slug': 'purebrain-vs-custom-gpts',
        'title': 'PureBrain vs Custom GPTs',
    },
    {
        'file': 'competitor-exodus-deepseek.html',
        'slug': 'purebrain-vs-deepseek',
        'title': 'PureBrain vs DeepSeek',
    },
    {
        'file': 'competitor-exodus-gemini.html',
        'slug': 'purebrain-vs-gemini',
        'title': 'PureBrain vs Gemini',
    },
    {
        'file': 'competitor-exodus-jasper.html',
        'slug': 'purebrain-vs-jasper',
        'title': 'PureBrain vs Jasper',
    },
    {
        'file': 'competitor-exodus-perplexity.html',
        'slug': 'purebrain-vs-perplexity',
        'title': 'PureBrain vs Perplexity',
    },
]

# Old hub URL patterns → new WP slugs
HUB_LINK_MAP = {
    '/switching-from-chatgpt':    '/purebrain-vs-chatgpt/',
    '/switching-from-copilot':    '/purebrain-vs-copilot/',
    '/switching-from-gemini':     '/purebrain-vs-gemini/',
    '/switching-from-claude':     '/purebrain-vs-claude/',
    '/switching-from-deepseek':   '/purebrain-vs-deepseek/',
    '/switching-from-perplexity': '/purebrain-vs-perplexity/',
    '/switching-from-jasper':     '/purebrain-vs-jasper/',
    '/switching-from-custom-gpts':'/purebrain-vs-custom-gpts/',
}

# Comparison footer HTML
COMPARE_FOOTER = '''<!-- Compare PureBrain Section -->
<div style="background: #0a0e1a; border-top: 1px solid #1a2235; padding: 40px 20px; text-align: center; margin-top: 40px;">
  <p style="color: #5a6a7a; font-size: 11px; letter-spacing: 3px; text-transform: uppercase; margin-bottom: 16px;">Compare PureBrain</p>
  <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 12px; max-width: 800px; margin: 0 auto;">
    <a href="/purebrain-vs-chatgpt/" style="background: #111827; color: #b8c5d6; padding: 8px 16px; border-radius: 20px; text-decoration: none; font-size: 13px; border: 1px solid #1a2235; transition: all 0.3s;">vs ChatGPT</a>
    <a href="/purebrain-vs-claude/" style="background: #111827; color: #b8c5d6; padding: 8px 16px; border-radius: 20px; text-decoration: none; font-size: 13px; border: 1px solid #1a2235;">vs Claude</a>
    <a href="/purebrain-vs-copilot/" style="background: #111827; color: #b8c5d6; padding: 8px 16px; border-radius: 20px; text-decoration: none; font-size: 13px; border: 1px solid #1a2235;">vs Copilot</a>
    <a href="/purebrain-vs-custom-gpts/" style="background: #111827; color: #b8c5d6; padding: 8px 16px; border-radius: 20px; text-decoration: none; font-size: 13px; border: 1px solid #1a2235;">vs Custom GPTs</a>
    <a href="/purebrain-vs-deepseek/" style="background: #111827; color: #b8c5d6; padding: 8px 16px; border-radius: 20px; text-decoration: none; font-size: 13px; border: 1px solid #1a2235;">vs DeepSeek</a>
    <a href="/purebrain-vs-gemini/" style="background: #111827; color: #b8c5d6; padding: 8px 16px; border-radius: 20px; text-decoration: none; font-size: 13px; border: 1px solid #1a2235;">vs Gemini</a>
    <a href="/purebrain-vs-jasper/" style="background: #111827; color: #b8c5d6; padding: 8px 16px; border-radius: 20px; text-decoration: none; font-size: 13px; border: 1px solid #1a2235;">vs Jasper</a>
    <a href="/purebrain-vs-perplexity/" style="background: #111827; color: #b8c5d6; padding: 8px 16px; border-radius: 20px; text-decoration: none; font-size: 13px; border: 1px solid #1a2235;">vs Perplexity</a>
    <a href="/compare/" style="background: #2a93c1; color: #ffffff; padding: 8px 16px; border-radius: 20px; text-decoration: none; font-size: 13px; font-weight: 600;">See All Comparisons &#x2192;</a>
  </div>
</div>'''

# "See All Comparisons" back-link for competitor pages
SEE_ALL_LINK = '''<!-- Back to Hub -->
<div style="background: #080a12; border-top: 1px solid rgba(42,147,193,0.18); padding: 20px; text-align: center;">
  <a href="/compare/" style="color: #2a93c1; text-decoration: none; font-size: 14px;">&#x2190; See All Comparisons</a>
</div>'''

deployed = {}


def read_html(filename):
    path = os.path.join(EXPORTS, filename)
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def wrap_as_wp_block(html_content):
    """Wrap full HTML in a wp:html block so WordPress doesn't mangle it."""
    return f'<!-- wp:html -->\n{html_content}\n<!-- /wp:html -->'


def check_existing_page(slug):
    """Check if a page with this slug already exists. Returns page ID or None."""
    r = requests.get(
        f'{WP_API}/pages',
        auth=AUTH,
        params={'slug': slug, 'context': 'edit', 'per_page': 5}
    )
    if r.status_code == 200:
        pages = r.json()
        if pages:
            return pages[0]['id']
    return None


def create_page(page_def, html_content):
    """Create a WordPress page from HTML content."""
    slug = page_def['slug']
    title = page_def['title']

    # Check if already exists
    existing_id = check_existing_page(slug)
    if existing_id:
        print(f"  [SKIP] Page '{slug}' already exists (ID: {existing_id}). Updating instead.")
        r = requests.post(
            f'{WP_API}/pages/{existing_id}',
            auth=AUTH,
            json={
                'title': title,
                'content': wrap_as_wp_block(html_content),
                'template': 'elementor_canvas',
                'status': 'publish',
                'password': 'purebrain',
            }
        )
    else:
        r = requests.post(
            f'{WP_API}/pages',
            auth=AUTH,
            json={
                'title': title,
                'slug': slug,
                'content': wrap_as_wp_block(html_content),
                'template': 'elementor_canvas',
                'status': 'publish',
                'password': 'purebrain',
            }
        )

    if r.status_code in (200, 201):
        page = r.json()
        page_id = page['id']
        page_link = page.get('link', f'{BASE_URL}/{slug}/')
        print(f"  [OK] '{title}' => ID: {page_id}, URL: {page_link}")
        return page_id, page_link
    else:
        print(f"  [ERROR] Failed to create '{title}': {r.status_code} {r.text[:300]}")
        return None, None


def fix_hub_links(hub_html):
    """Replace old /switching-from-* URLs with actual WordPress URLs."""
    updated = hub_html
    for old_url, new_url in HUB_LINK_MAP.items():
        # Replace in deepDive JS property
        updated = updated.replace(f"'{old_url}'", f"'{new_url}'")
        updated = updated.replace(f'"{old_url}"', f'"{new_url}"')
        # Replace in href attributes
        updated = updated.replace(f'href="{old_url}"', f'href="{new_url}"')
        updated = updated.replace(f"href='{old_url}'", f"href='{new_url}'")
    return updated


def add_see_all_link_to_competitor(html_content):
    """Inject a See All Comparisons link before </body>."""
    if '</body>' in html_content:
        return html_content.replace('</body>', f'{SEE_ALL_LINK}\n</body>')
    # fallback: append
    return html_content + '\n' + SEE_ALL_LINK


def update_page_content(page_id, new_content):
    """Update a page's content via REST API."""
    r = requests.post(
        f'{WP_API}/pages/{page_id}',
        auth=AUTH,
        json={'content': wrap_as_wp_block(new_content)}
    )
    if r.status_code in (200, 201):
        print(f"  [OK] Updated page ID {page_id}")
        return True
    else:
        print(f"  [ERROR] Failed to update page ID {page_id}: {r.status_code} {r.text[:200]}")
        return False


def get_page_raw_content(page_id):
    """Fetch raw page content via REST API."""
    r = requests.get(
        f'{WP_API}/pages/{page_id}',
        auth=AUTH,
        params={'context': 'edit'}
    )
    if r.status_code == 200:
        data = r.json()
        return data.get('content', {}).get('raw', '')
    return None


def inject_footer_into_wp_page(page_id, page_name):
    """
    For non-Elementor pages (raw HTML in wp:html blocks),
    inject comparison footer before </body> in the wp:html block content.
    """
    raw_content = get_page_raw_content(page_id)
    if raw_content is None:
        print(f"  [ERROR] Could not fetch content for page ID {page_id}")
        return False

    # Pages created with wp:html blocks - inject before </body>
    if '</body>' in raw_content:
        new_content = raw_content.replace('</body>', f'{COMPARE_FOOTER}\n</body>')
    elif '<!-- /wp:html -->' in raw_content:
        # Inject before closing wp:html tag
        new_content = raw_content.replace('<!-- /wp:html -->', f'{COMPARE_FOOTER}\n<!-- /wp:html -->')
    else:
        # Just append
        new_content = raw_content + '\n<!-- wp:html -->\n' + COMPARE_FOOTER + '\n<!-- /wp:html -->'

    r = requests.post(
        f'{WP_API}/pages/{page_id}',
        auth=AUTH,
        json={'content': new_content}
    )
    if r.status_code in (200, 201):
        print(f"  [OK] Footer injected into {page_name} (ID: {page_id})")
        return True
    else:
        print(f"  [ERROR] Footer injection failed for {page_name} (ID: {page_id}): {r.status_code} {r.text[:200]}")
        return False


def inject_footer_into_elementor_page(page_id, page_name):
    """
    For Elementor pages (homepage + pay-test pages), inject comparison footer
    as a new Elementor HTML widget section at the end of _elementor_data.
    """
    r = requests.get(
        f'{WP_API}/pages/{page_id}',
        auth=AUTH,
        params={'context': 'edit'}
    )
    if r.status_code != 200:
        print(f"  [ERROR] Could not fetch Elementor page {page_id}: {r.status_code}")
        return False

    page_data = r.json()
    meta = page_data.get('meta', {})
    elementor_data_str = meta.get('_elementor_data', '')

    if not elementor_data_str:
        print(f"  [WARN] No _elementor_data found for page {page_id}. Falling back to content injection.")
        return inject_footer_into_wp_page(page_id, page_name)

    # Parse existing Elementor data
    try:
        elementor_data = json.loads(elementor_data_str)
    except json.JSONDecodeError as e:
        print(f"  [ERROR] Could not parse _elementor_data for page {page_id}: {e}")
        return False

    # Build a new Elementor section with HTML widget containing the footer
    import uuid
    new_section = {
        "id": uuid.uuid4().hex[:8],
        "elType": "section",
        "settings": {
            "background_background": "classic",
            "background_color": "#0a0e1a",
            "padding": {"unit": "px", "top": "0", "right": "0", "bottom": "0", "left": "0", "isLinked": False}
        },
        "elements": [
            {
                "id": uuid.uuid4().hex[:8],
                "elType": "column",
                "settings": {"_column_size": 100},
                "elements": [
                    {
                        "id": uuid.uuid4().hex[:8],
                        "elType": "widget",
                        "widgetType": "html",
                        "settings": {
                            "html": COMPARE_FOOTER
                        },
                        "elements": []
                    }
                ]
            }
        ]
    }

    # Append new section to the end
    elementor_data.append(new_section)
    new_elementor_str = json.dumps(elementor_data, ensure_ascii=False)

    update_r = requests.post(
        f'{WP_API}/pages/{page_id}',
        auth=AUTH,
        json={
            'meta': {
                '_elementor_data': new_elementor_str,
                '_elementor_edit_mode': 'builder',
            }
        }
    )

    if update_r.status_code in (200, 201):
        print(f"  [OK] Elementor footer section added to {page_name} (ID: {page_id})")
        return True
    else:
        print(f"  [ERROR] Failed to update Elementor data for {page_name} (ID: {page_id}): {update_r.status_code} {update_r.text[:200]}")
        return False


def clear_elementor_cache():
    """Clear Elementor's server-side cache."""
    r = requests.delete(
        f'{BASE_URL}/wp-json/elementor/v1/cache',
        auth=AUTH
    )
    print(f"  [CACHE] Elementor cache cleared: {r.status_code}")


def verify_page(page_id, slug, title):
    """Quick verification that the page is accessible."""
    r = requests.get(
        f'{WP_API}/pages/{page_id}',
        auth=AUTH,
        params={'context': 'view'}
    )
    if r.status_code == 200:
        data = r.json()
        status = data.get('status')
        link = data.get('link', 'unknown')
        print(f"  [VERIFY] '{title}': status={status}, link={link}")
        return True
    else:
        print(f"  [VERIFY] FAILED for '{title}' (ID: {page_id}): {r.status_code}")
        return False


# ══════════════════════════════════════════════
#  STEP 1: CREATE / UPDATE 9 COMPETITOR PAGES
# ══════════════════════════════════════════════
print("\n" + "="*60)
print("STEP 1: DEPLOYING 9 COMPETITOR EXODUS PAGES")
print("="*60)

for page_def in PAGES:
    print(f"\nProcessing: {page_def['file']} → /{page_def['slug']}/")
    html = read_html(page_def['file'])

    # For the hub page: fix the old /switching-from-* links
    if page_def['slug'] == 'compare':
        html = fix_hub_links(html)
        print("  [FIX] Replaced old switching-from-* URLs with WordPress slugs")
    else:
        # For competitor pages: add See All Comparisons back-link
        html = add_see_all_link_to_competitor(html)
        print("  [FIX] Added 'See All Comparisons' link")

    page_id, page_url = create_page(page_def, html)
    if page_id:
        deployed[page_def['slug']] = {
            'id': page_id,
            'url': page_url,
            'title': page_def['title']
        }
    time.sleep(0.5)  # gentle on the API

print(f"\n✓ Deployed {len(deployed)}/9 pages")

# Clear cache after all pages created
print("\nClearing Elementor cache...")
clear_elementor_cache()

# ══════════════════════════════════════════════
#  STEP 2: VERIFY NEW PAGES
# ══════════════════════════════════════════════
print("\n" + "="*60)
print("STEP 2: VERIFYING NEW PAGES")
print("="*60)

for slug, info in deployed.items():
    verify_page(info['id'], slug, info['title'])
    time.sleep(0.3)

# ══════════════════════════════════════════════
#  STEP 3: ADD COMPARISON FOOTER TO 5 EXISTING PAGES
# ══════════════════════════════════════════════
print("\n" + "="*60)
print("STEP 3: ADDING COMPARISON FOOTER TO 5 EXISTING PAGES")
print("="*60)

# Homepage (ID: 11) - Elementor page
print("\n[3a] Homepage (ID: 11) - Elementor page")
inject_footer_into_elementor_page(11, 'Homepage')

# pay-test (ID: 439) - Elementor page
print("\n[3b] pay-test (ID: 439) - Elementor page")
inject_footer_into_elementor_page(439, 'pay-test')

# pay-test-sandbox (ID: 468) - Elementor page
print("\n[3c] pay-test-sandbox (ID: 468) - Elementor page")
inject_footer_into_elementor_page(468, 'pay-test-sandbox')

# pay-test-2 (ID: 689) - Elementor page
print("\n[3d] pay-test-2 (ID: 689) - Elementor page")
inject_footer_into_elementor_page(689, 'pay-test-2')

# pay-test-sandbox-2 (ID: 688) - Elementor page
print("\n[3e] pay-test-sandbox-2 (ID: 688) - Elementor page")
inject_footer_into_elementor_page(688, 'pay-test-sandbox-2')

# Clear Elementor cache after all footer updates
print("\nClearing Elementor cache after footer updates...")
clear_elementor_cache()

# ══════════════════════════════════════════════
#  STEP 4: FINAL REPORT
# ══════════════════════════════════════════════
print("\n" + "="*60)
print("STEP 4: DEPLOYMENT SUMMARY")
print("="*60)

print("\n9 NEW COMPETITOR PAGES:")
for slug, info in deployed.items():
    print(f"  ID: {info['id']:6d}  {info['url']}")
    print(f"            Title: {info['title']}")

print("\n5 EXISTING PAGES UPDATED WITH COMPARISON FOOTER:")
print("  ID: 11    https://purebrain.ai/  (Homepage)")
print("  ID: 439   https://purebrain.ai/pay-test/")
print("  ID: 468   https://purebrain.ai/pay-test-sandbox/")
print("  ID: 689   https://purebrain.ai/pay-test-2/")
print("  ID: 688   https://purebrain.ai/pay-test-sandbox-2/")

print("\nAll pages password-protected with: purebrain")
print("Elementor cache cleared after deployments.")
print("\nDEPLOYMENT COMPLETE.")
