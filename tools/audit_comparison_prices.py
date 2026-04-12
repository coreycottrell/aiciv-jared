#!/usr/bin/env python3
"""Audit all comparison pages for PureBrain pricing accuracy."""
import requests
import os
import re
import sys
from dotenv import load_dotenv

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

wp_pass = os.getenv('PUREBRAIN_WP_APP_PASSWORD')
auth = ('Aether', wp_pass)

# All comparison page IDs found
all_ids = [1190, 1044, 970, 794, 760, 759, 758, 757, 756, 755, 754, 753, 752]

results = {}

for pid in all_ids:
    r = requests.get(f'https://purebrain.ai/wp-json/wp/v2/pages/{pid}?context=edit', auth=auth)
    if r.status_code != 200:
        print(f'ERROR fetching page {pid}: {r.status_code}')
        continue
    p = r.json()
    content = p.get('content', {}).get('raw', '')
    slug = p.get('slug', '')

    # Find all dollar amounts in the content
    prices = re.findall(r'\$[\d,]+(?:/mo(?:nth)?)?', content)
    unique_prices = sorted(set(prices))

    # Find dollar amounts near PureBrain tier names
    pb_context = []
    # Search for tier names with nearby prices
    for pattern in [
        r'(?:Awakened|Bonded|Partnered|Unified).{0,300}?\$[\d,]+',
        r'\$[\d,]+.{0,200}?(?:Awakened|Bonded|Partnered|Unified)',
        r'(?:PureBrain)[^<]{0,300}?\$[\d,]+',
    ]:
        for match in re.finditer(pattern, content, re.DOTALL):
            snippet = match.group()
            # Strip HTML tags
            clean = re.sub(r'<[^>]+>', ' ', snippet)
            clean = re.sub(r'\s+', ' ', clean).strip()
            if len(clean) > 10:
                pb_context.append(clean[:200])

    results[pid] = {
        'slug': slug,
        'all_prices': unique_prices,
        'pb_context': pb_context[:8],
        'content_length': len(content),
        'content': content,
    }

    print(f"\nPage {pid} ({slug}):")
    print(f"  All prices: {unique_prices}")
    if pb_context:
        print(f"  PureBrain pricing contexts:")
        for ctx in pb_context[:5]:
            print(f"    > {ctx[:150]}")

# Now get the MAIN PAGE pricing to use as source of truth
print("\n\n=== MAIN PAGE PRICING (source of truth) ===")
main_r = requests.get('https://purebrain.ai/wp-json/wp/v2/pages?slug=page&context=edit', auth=auth)
# Try the home page via the REST API - get all pages and find home
home_r = requests.get('https://purebrain.ai/', timeout=10)
if home_r.status_code == 200:
    home_prices = re.findall(r'\$[\d,]+(?:/mo(?:nth)?)?', home_r.text)
    unique_home = sorted(set(home_prices))
    print(f"Main page prices: {unique_home}")

# Also check the /#awakening section specifically
print("\n=== Raw pricing from main page HTML ===")
# Search for tier+price combinations on main page
tier_patterns = re.findall(
    r'(?:Awakened|Bonded|Partnered|Unified)[^<]{0,200}?\$[\d,]+',
    home_r.text, re.DOTALL
)
for t in tier_patterns[:10]:
    clean = re.sub(r'<[^>]+>', ' ', t)
    clean = re.sub(r'\s+', ' ', clean).strip()
    print(f"  {clean[:200]}")
