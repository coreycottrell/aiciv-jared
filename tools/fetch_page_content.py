#!/usr/bin/env python3
"""Fetch and display raw content of a specific page."""
import requests
import re
import sys
import os
from dotenv import load_dotenv

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

wp_pass = os.getenv('PUREBRAIN_WP_APP_PASSWORD')
auth = ('Aether', wp_pass)

page_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1044

r = requests.get(f'https://purebrain.ai/wp-json/wp/v2/pages/{page_id}?context=edit', auth=auth)
if r.status_code != 200:
    print(f"ERROR: {r.status_code}")
    sys.exit(1)

p = r.json()
content = p.get('content', {}).get('raw', '')
print(f"Page: {p['slug']} (ID: {page_id})")
print(f"Content length: {len(content)}")
print(f"\n=== PRICING SECTION ===")

# Find all price occurrences with context
for m in re.finditer(r'\$[\d,]+(?:/mo(?:nth)?)?', content):
    start = max(0, m.start() - 200)
    end = min(len(content), m.end() + 200)
    snippet = content[start:end]
    clean = re.sub(r'<[^>]+>', ' ', snippet)
    clean = re.sub(r'\s+', ' ', clean).strip()
    print(f"\nPrice {m.group()} at pos {m.start()}:")
    print(f"  {clean[:300]}")
