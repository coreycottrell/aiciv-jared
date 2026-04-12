#!/usr/bin/env python3
"""Final verification of all page protection and site health."""
import os, re, base64, requests
from dotenv import load_dotenv
load_dotenv('/home/jared/projects/AI-CIV/aether/.env')
WP_BASE_URL = 'https://purebrain.ai'
WP_USER = 'Aether'
WP_APP_PASSWORD = os.getenv('PUREBRAIN_WP_APP_PASSWORD', '').strip("'\"")

credentials = f'{WP_USER}:{WP_APP_PASSWORD}'
encoded = base64.b64encode(credentials.encode()).decode()
headers = {'Authorization': f'Basic {encoded}'}

DEV_PAGES = [
    (439, 'pay-test'),
    (468, 'pay-test-sandbox'),
    (150, 'elementor-150'),
    (311, 'paypal-buttons-embed'),
]

print('=== Dev Pages - Should NOT be indexed by Google ===')
print()

all_protected = True
for page_id, slug in DEV_PAGES:
    print(f'--- /{slug}/ (ID={page_id}) ---')

    # 1. Check page status via REST API
    resp = requests.get(
        f'{WP_BASE_URL}/wp-json/wp/v2/pages/{page_id}?context=edit&_fields=id,status',
        headers=headers, timeout=10
    )
    if resp.status_code == 200:
        status = resp.json().get('status', 'unknown')
        print(f'  WP Status: {status}')
    else:
        print(f'  WP Status: HTTP {resp.status_code}')
        status = 'error'

    # 2. Check live page (simulates Googlebot - no cookies, no auth)
    session = requests.Session()
    resp2 = session.get(
        f'{WP_BASE_URL}/{slug}/',
        timeout=10,
        allow_redirects=True,
        headers={'Cache-Control': 'no-cache', 'User-Agent': 'Mozilla/5.0 Googlebot/2.1'}
    )
    print(f'  HTTP Response: {resp2.status_code} | Final URL: {resp2.url}')

    if resp2.status_code == 200:
        # Check what robots tag is present
        robots_matches = re.findall(r'meta[^>]*robots[^>]*', resp2.text, re.I)
        for m in robots_matches[:3]:
            print(f'  robots tag: {m[:150]}')

        # Check if it has noindex
        has_noindex = 'noindex' in resp2.text.lower() and 'robots' in resp2.text.lower()
        print(f'  Has noindex: {has_noindex}')

        if not has_noindex:
            all_protected = False
            print(f'  ISSUE: Page still publicly accessible with index robots')
    else:
        print(f'  PROTECTED: Not publicly accessible (HTTP {resp2.status_code})')

    # 3. Check Yoast API
    resp3 = requests.get(
        f'{WP_BASE_URL}/wp-json/yoast/v1/get_head?url={WP_BASE_URL}/?p={page_id}',
        headers=headers, timeout=10
    )
    if resp3.status_code == 200:
        head = resp3.json().get('html', '')
        m = re.search(r'meta name="robots" content="([^"]+)"', head)
        yoast_robots = m.group(1) if m else 'NOT FOUND'
        print(f'  Yoast API robots: {yoast_robots}')
    print()

print()
print('=== Main Site Pages - Should be indexed by Google ===')
MAIN_PAGES = [
    ('', 'Homepage'),
    ('blog/', 'Blog'),
    ('enterprise-ai-readiness-assessment/', 'Assessment'),
]
for path, name in MAIN_PAGES:
    url = f'{WP_BASE_URL}/{path}'
    resp = requests.get(url, timeout=10, headers={'Cache-Control': 'no-cache'})
    m = re.search(r'meta[^>]*name=["\']robots["\'][^>]*content=["\']([^"\']+)["\']', resp.text, re.I)
    robots = m.group(1) if m else 'NOT FOUND'
    canonical_m = re.search(r'link rel="canonical" href="([^"]+)"', resp.text)
    canonical = canonical_m.group(1) if canonical_m else 'NOT FOUND'
    print(f'  {name}: HTTP {resp.status_code} | robots={robots}')
    print(f'    canonical: {canonical}')
print()

if all_protected:
    print('RESULT: All dev pages are protected from Google indexing.')
else:
    print('RESULT: Some pages may still be accessible. Check above for details.')
    print('Note: GoDaddy cache may take up to 5 minutes to expire.')
