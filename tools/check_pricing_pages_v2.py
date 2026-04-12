#!/usr/bin/env python3
"""Check all 4 pricing pages for 'How This Levels You Up' links."""

import urllib.request
import urllib.parse
import json
import base64
import sys

WP_URL = "https://purebrain.ai/wp-json/wp/v2"
WP_USER = "Aether"
WP_PASS = "ZGuh 1W8k WpWM c9iy kqyd buPr"

credentials = base64.b64encode(f"{WP_USER}:{WP_PASS}".encode()).decode()
headers = {
    "Authorization": f"Basic {credentials}",
    "Content-Type": "application/json"
}

def wp_get(endpoint, timeout=30):
    url = f"{WP_URL}{endpoint}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())

def search_pages(query):
    endpoint = f"/pages?search={urllib.parse.quote(query)}&per_page=20&_fields=id,slug,title,link,status"
    return wp_get(endpoint)

print("SEARCHING FOR ALL RELEVANT PAGES")
print("=" * 70)

# Build comprehensive list
all_pages = {}

for query in ["partnered", "unified", "pay-test", "sandbox"]:
    try:
        results = search_pages(query)
        for page in results:
            pid = page['id']
            if pid not in all_pages:
                all_pages[pid] = page
                print(f"  ID={pid} slug='{page['slug']}' status='{page.get('status','?')}' url={page['link']}")
    except Exception as e:
        print(f"  Error searching '{query}': {e}")

print(f"\nTotal pages: {len(all_pages)}")

# Key pages to check (known from context)
key_page_ids = []
for pid, p in all_pages.items():
    slug = p['slug']
    # Partnered pricing page
    if slug in ['partnered', 'pay-test-sandbox-3', 'pay-test-2', 'pay-test-sandbox-2']:
        key_page_ids.append(pid)
    # Any pay-test page
    elif 'pay-test' in slug or 'sandbox' in slug:
        key_page_ids.append(pid)
    # Main partnered/unified pages
    elif slug in ['partnered', 'unified']:
        key_page_ids.append(pid)

# Also explicitly try to find partnered and unified by slug
print("\nTrying direct slug lookups...")
for slug in ['partnered', 'unified']:
    try:
        results = wp_get(f"/pages?slug={slug}&_fields=id,slug,title,link,status")
        for page in results:
            pid = page['id']
            print(f"  Direct slug '{slug}': ID={pid} url={page['link']}")
            if pid not in all_pages:
                all_pages[pid] = page
            if pid not in key_page_ids:
                key_page_ids.append(pid)
    except Exception as e:
        print(f"  Error: {e}")

print(f"\nKey page IDs to inspect: {key_page_ids}")

print("\n" + "=" * 70)
print("CHECKING PAGES FOR 'HOW THIS LEVELS YOU UP' LINK")
print("=" * 70)

for pid in sorted(set(key_page_ids)):
    page_info = all_pages.get(pid, {})
    slug = page_info.get('slug', '?')
    link = page_info.get('link', '?')

    print(f"\n--- Page {pid}: '{slug}' ---")
    print(f"  URL: {link}")

    try:
        # Get content + meta (need meta for elementor_data)
        full = wp_get(f"/pages/{pid}?context=edit&_fields=id,slug,content,meta")

        content_raw = full.get('content', {}).get('raw', '') or full.get('content', {}).get('rendered', '')
        meta = full.get('meta', {})
        elementor_data = meta.get('_elementor_data', '') or ''

        if not isinstance(elementor_data, str):
            elementor_data = json.dumps(elementor_data)

        combined = content_raw + elementor_data

        print(f"  Content size: {len(content_raw):,} chars")
        print(f"  Elementor data size: {len(elementor_data):,} chars")
        print(f"  Combined size: {len(combined):,} chars")

        # Check for levels-you-up link
        checks = [
            "How This Levels You Up",
            "levels-you-up",
            "how-this-levels",
            "levelsyouup",
        ]

        found = []
        for check in checks:
            if check.lower() in combined.lower():
                found.append(check)

        if found:
            print(f"  ✅ LINK FOUND: {found}")
        else:
            print(f"  ❌ LINK MISSING")

        # Check CTA buttons present
        cta_texts = ['Reserve Keen Now', 'Activate Your AI Now', 'Claim This Spot', 'Get Started', 'Reserve Your AI']
        for cta in cta_texts:
            if cta.lower() in combined.lower():
                count = combined.lower().count(cta.lower())
                print(f"  CTA '{cta}': {count}x")

        # Check tier names
        for tier in ['Awakened', 'Partnered', 'Unified', 'Enterprise', 'Bonded']:
            if tier.lower() in combined.lower():
                count = combined.lower().count(tier.lower())
                print(f"  Tier '{tier}': mentioned {count}x")

    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
