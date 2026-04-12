#!/usr/bin/env python3
"""Find page IDs for all 4 pricing pages and check for 'How This Levels You Up' links."""

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

def wp_get(endpoint):
    url = f"{WP_URL}{endpoint}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

def search_pages(query):
    endpoint = f"/pages?search={urllib.parse.quote(query)}&per_page=10&_fields=id,slug,title,link"
    return wp_get(endpoint)

def get_page_content(page_id):
    endpoint = f"/pages/{page_id}?_fields=id,slug,title,link,content,meta"
    return wp_get(endpoint)

def check_for_levels_up_link(content_str):
    checks = [
        "How This Levels You Up",
        "levels-you-up",
        "levels you up",
        "levelsyouup",
    ]
    found = []
    for check in checks:
        if check.lower() in content_str.lower():
            found.append(check)
    return found

print("=" * 70)
print("SEARCHING FOR PRICING PAGES")
print("=" * 70)

# Search for each page
searches = ["partnered", "unified", "pay-test-2", "pay-test-sandbox", "sandbox-3", "sandbox3"]
found_pages = {}

for query in searches:
    results = search_pages(query)
    for page in results:
        pid = page['id']
        if pid not in found_pages:
            found_pages[pid] = page
            print(f"  Found: ID={pid} slug='{page['slug']}' title='{page['title']['rendered']}' url={page['link']}")

print(f"\nTotal unique pages found: {len(found_pages)}")
print("\n" + "=" * 70)
print("CHECKING EACH PAGE FOR 'HOW THIS LEVELS YOU UP' LINKS")
print("=" * 70)

results_summary = {}

for pid, page_info in sorted(found_pages.items()):
    slug = page_info['slug']
    title = page_info['title']['rendered']
    link = page_info['link']

    print(f"\n--- Page {pid}: '{slug}' ---")
    print(f"  URL: {link}")

    # Get full content
    try:
        full_page = get_page_content(pid)

        # Check post_content
        content_raw = full_page.get('content', {}).get('rendered', '')

        # Check _elementor_data via meta
        meta = full_page.get('meta', {})
        elementor_data = meta.get('_elementor_data', '')

        # Combined check
        combined = content_raw + (elementor_data if isinstance(elementor_data, str) else '')

        found_in_content = check_for_levels_up_link(content_raw)
        found_in_elementor = check_for_levels_up_link(elementor_data if isinstance(elementor_data, str) else '')

        print(f"  Content size: {len(content_raw)} chars")
        print(f"  Elementor data size: {len(elementor_data) if isinstance(elementor_data, str) else 'N/A (not string)'} chars")

        if found_in_content or found_in_elementor:
            print(f"  ✅ LINK FOUND!")
            if found_in_content:
                print(f"     In content: {found_in_content}")
            if found_in_elementor:
                print(f"     In elementor_data: {found_in_elementor}")
            results_summary[pid] = {'slug': slug, 'link': link, 'has_link': True}
        else:
            print(f"  ❌ LINK MISSING - 'How This Levels You Up' NOT found")
            results_summary[pid] = {'slug': slug, 'link': link, 'has_link': False}

        # Also check for "Reserve" or "Keen" or "Levels" to understand CTA structure
        cta_checks = ['Reserve Keen Now', 'reserve-keen', 'Claim This Spot', 'Activate Your AI Now', 'Get Started', 'How This']
        for cta in cta_checks:
            if cta.lower() in combined.lower():
                count = combined.lower().count(cta.lower())
                print(f"  Found CTA text '{cta}': {count}x")

    except Exception as e:
        print(f"  ERROR fetching page: {e}")
        results_summary[pid] = {'slug': slug, 'link': link, 'has_link': None, 'error': str(e)}

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
for pid, info in sorted(results_summary.items()):
    status = "✅ HAS LINK" if info['has_link'] else "❌ MISSING LINK"
    if info.get('has_link') is None:
        status = "⚠️ ERROR"
    print(f"  {status} | ID={pid} | slug='{info['slug']}' | {info['link']}")
