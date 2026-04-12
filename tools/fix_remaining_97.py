#!/usr/bin/env python3
"""Fix remaining $97 reference on page 1190."""
import requests
import re
from dotenv import load_dotenv

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

wp_pass = os.getenv('PUREBRAIN_WP_APP_PASSWORD') if 'os' in dir() else __import__('os').environ.get('PUREBRAIN_WP_APP_PASSWORD', '')

import os
from dotenv import load_dotenv
load_dotenv('/home/jared/projects/AI-CIV/aether/.env')
wp_pass = os.getenv('PUREBRAIN_WP_APP_PASSWORD')
auth = ('Aether', wp_pass)

r = requests.get('https://purebrain.ai/wp-json/wp/v2/pages/1190?context=edit', auth=auth)
content = r.json()['content']['raw']

# Find the exact $97 context
for m in re.finditer(r'\$97', content):
    start = max(0, m.start()-200)
    end = min(len(content), m.end()+200)
    snippet = content[start:end]
    print(f"$97 at pos {m.start()}:")
    print(repr(snippet))
    print()
