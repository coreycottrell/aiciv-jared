#!/usr/bin/env python3
"""Get the actual current pricing from the main page and awakening section."""
import requests
import re
from dotenv import load_dotenv
import os

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

wp_pass = os.getenv('PUREBRAIN_WP_APP_PASSWORD')
auth = ('Aether', wp_pass)

# Get main page (usually page ID 2 or the front page)
# First, check what the front page is
r = requests.get('https://purebrain.ai/wp-json/wp/v2/settings', auth=auth)
if r.status_code == 200:
    settings = r.json()
    print(f"Front page ID: {settings.get('page_on_front')}")
    print(f"Posts page ID: {settings.get('page_for_posts')}")
    fp_id = settings.get('page_on_front')
else:
    print(f"Settings error: {r.status_code}")
    fp_id = None

if fp_id:
    r2 = requests.get(f'https://purebrain.ai/wp-json/wp/v2/pages/{fp_id}?context=edit', auth=auth)
    if r2.status_code == 200:
        p = r2.json()
        content = p.get('content', {}).get('raw', '')
        print(f"\nFront page: {p.get('slug')} (ID: {fp_id})")
        print(f"Content length: {len(content)}")

        # Find pricing section - look for Awakened/Bonded/Partnered/Unified with prices
        # Search around tier names
        for tier in ['Awakened', 'Bonded', 'Partnered', 'Unified']:
            matches = list(re.finditer(tier, content))
            for m in matches[:2]:
                start = max(0, m.start() - 50)
                end = min(len(content), m.end() + 300)
                snippet = content[start:end]
                clean = re.sub(r'<[^>]+>', ' ', snippet)
                clean = re.sub(r'\s+', ' ', clean).strip()
                prices_in_snippet = re.findall(r'\$[\d,]+', clean)
                if prices_in_snippet:
                    print(f"\n{tier}: {clean[:250]}")
                    break

# Also fetch the live HTML of the page
print("\n\n=== LIVE PAGE PRICING (main page) ===")
live = requests.get('https://purebrain.ai/', timeout=15)
if live.status_code == 200:
    html = live.text
    # Look for pricing data in JSON/JS blocks
    json_matches = re.findall(r'"price[^"]*":\s*"?\$?[\d,]+', html)
    print(f"JSON price fields: {json_matches[:10]}")

    # Look for tier+price combinations
    for tier in ['Awakened', 'Bonded', 'Partnered', 'Unified']:
        pos = html.find(tier)
        if pos > 0:
            snippet = html[max(0,pos-100):pos+400]
            clean = re.sub(r'<[^>]+>', ' ', snippet)
            clean = re.sub(r'\s+', ' ', clean).strip()
            prices = re.findall(r'\$[\d,]+', clean)
            if prices:
                print(f"\n{tier} (live): prices found = {prices}")
                print(f"  Context: {clean[:200]}")
