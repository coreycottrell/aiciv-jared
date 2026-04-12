#!/usr/bin/env python3
"""Get full raw content of a page and save to file."""
import requests
import sys
import os
from dotenv import load_dotenv

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

wp_pass = os.getenv('PUREBRAIN_WP_APP_PASSWORD')
auth = ('Aether', wp_pass)

page_id = int(sys.argv[1])
out_file = sys.argv[2] if len(sys.argv) > 2 else f'/tmp/page_{page_id}.html'

r = requests.get(f'https://purebrain.ai/wp-json/wp/v2/pages/{page_id}?context=edit', auth=auth)
if r.status_code != 200:
    print(f"ERROR: {r.status_code}")
    sys.exit(1)

p = r.json()
content = p.get('content', {}).get('raw', '')
with open(out_file, 'w') as f:
    f.write(content)
print(f"Saved {len(content)} chars to {out_file}")
