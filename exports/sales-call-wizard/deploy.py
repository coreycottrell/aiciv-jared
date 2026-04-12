#!/usr/bin/env python3
"""Deploy Sales Call Wizard to WordPress as a password-protected page."""

import requests
import json
import base64
import os
import sys

# Credentials
WP_USER = 'Aether'
WP_APP_PASSWORD = 'ZGuh 1W8k WpWM c9iy kqyd buPr'
WP_BASE = 'https://purebrain.ai/wp-json/wp/v2'

# Page config
PAGE_TITLE = 'Live Sales Call Wizard'
PAGE_SLUG = 'live-call'
PAGE_PARENT = 1278  # sales-playbook parent
PAGE_PASSWORD = 'closers2026'
PAGE_TEMPLATE = 'elementor_canvas'

# Read the HTML file
html_path = '/home/jared/projects/AI-CIV/aether/exports/sales-call-wizard/index.html'
with open(html_path, 'r') as f:
    raw_html = f.read()

# Wrap in WordPress html block
content = f'<!-- wp:html -->\n{raw_html}\n<!-- /wp:html -->'

# Build auth header
credentials = f'{WP_USER}:{WP_APP_PASSWORD}'
token = base64.b64encode(credentials.encode()).decode('utf-8')
headers = {
    'Authorization': f'Basic {token}',
    'Content-Type': 'application/json'
}

# First check if page already exists
print("Checking for existing page...")
check_url = f'{WP_BASE}/pages?slug={PAGE_SLUG}&parent={PAGE_PARENT}'
check_resp = requests.get(check_url, headers=headers)
existing = check_resp.json()
print(f"Existing pages found: {len(existing)}")

# Page data
page_data = {
    'title': PAGE_TITLE,
    'slug': PAGE_SLUG,
    'content': content,
    'status': 'publish',
    'template': PAGE_TEMPLATE,
    'parent': PAGE_PARENT,
    'password': PAGE_PASSWORD,
    'meta': {
        '_elementor_edit_mode': 'builder',
        '_elementor_template_type': 'wp-page',
        '_elementor_version': '3.18.0',
        '_elementor_data': '[]'
    }
}

if existing and len(existing) > 0:
    # Update existing page
    page_id = existing[0]['id']
    print(f"Updating existing page ID: {page_id}")
    url = f'{WP_BASE}/pages/{page_id}'
    resp = requests.post(url, headers=headers, json=page_data)
else:
    # Create new page
    print("Creating new page...")
    url = f'{WP_BASE}/pages'
    resp = requests.post(url, headers=headers, json=page_data)

print(f"Status code: {resp.status_code}")

if resp.status_code in [200, 201]:
    data = resp.json()
    page_id = data.get('id')
    page_link = data.get('link', '')
    print(f"SUCCESS!")
    print(f"Page ID: {page_id}")
    print(f"Page URL: {page_link}")
    print(f"Status: {data.get('status')}")
    print(f"Template: {data.get('template')}")
    # Save result
    with open('/home/jared/projects/AI-CIV/aether/exports/sales-call-wizard/deploy-result.json', 'w') as f:
        json.dump({'id': page_id, 'url': page_link, 'status': 'success'}, f, indent=2)
else:
    print(f"FAILED!")
    print(f"Response: {resp.text[:2000]}")
    sys.exit(1)
