#!/usr/bin/env python3
"""Deploy Sales Call Wizard to WordPress."""

import urllib.request
import urllib.parse
import json
import base64

WP_USER = 'Aether'
WP_APP_PASSWORD = 'ZGuh 1W8k WpWM c9iy kqyd buPr'
WP_BASE = 'https://purebrain.ai/wp-json/wp/v2'

html_path = '/home/jared/projects/AI-CIV/aether/exports/sales-call-wizard/index.html'
with open(html_path, 'r') as f:
    raw_html = f.read()

content = f'<!-- wp:html -->\n{raw_html}\n<!-- /wp:html -->'

credentials = f'{WP_USER}:{WP_APP_PASSWORD}'
token = base64.b64encode(credentials.encode()).decode('utf-8')

page_data = {
    'title': 'Live Sales Call Wizard',
    'slug': 'live-call',
    'content': content,
    'status': 'publish',
    'template': 'elementor_canvas',
    'parent': 1278,
    'password': 'closers2026',
}

payload = json.dumps(page_data).encode('utf-8')

req = urllib.request.Request(
    f'{WP_BASE}/pages',
    data=payload,
    headers={
        'Authorization': f'Basic {token}',
        'Content-Type': 'application/json',
        'User-Agent': 'Aether/1.0'
    },
    method='POST'
)

try:
    with urllib.request.urlopen(req, timeout=60) as resp:
        body = resp.read().decode('utf-8')
        data = json.loads(body)
        print(f"SUCCESS: {resp.status}")
        print(f"Page ID: {data.get('id')}")
        print(f"URL: {data.get('link')}")
        print(f"Template: {data.get('template')}")
        print(f"Status: {data.get('status')}")

        result = {
            'id': data.get('id'),
            'url': data.get('link'),
            'status': 'deployed'
        }
        with open('/home/jared/projects/AI-CIV/aether/exports/sales-call-wizard/deploy-result.json', 'w') as f:
            json.dump(result, f, indent=2)

except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8')
    print(f"HTTP ERROR {e.code}: {e.reason}")
    print(body[:3000])
except Exception as e:
    print(f"ERROR: {e}")
