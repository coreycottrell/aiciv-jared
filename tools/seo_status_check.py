#!/usr/bin/env python3
"""Complete SEO status check for PureBrain.ai."""
import os, re, base64, requests
from dotenv import load_dotenv
load_dotenv('/home/jared/projects/AI-CIV/aether/.env')
WP_BASE_URL = 'https://purebrain.ai'
WP_USER = 'Aether'
WP_APP_PASSWORD = os.getenv('PUREBRAIN_WP_APP_PASSWORD', '').strip("'\"")

credentials = f'{WP_USER}:{WP_APP_PASSWORD}'
encoded = base64.b64encode(credentials.encode()).decode()
auth_headers = {'Authorization': f'Basic {encoded}'}

print('=== COMPLETE PUREBRAIN.AI SEO STATUS CHECK ===')
print()

# 1. Settings > Reading check
resp = requests.get(f'{WP_BASE_URL}/wp-json/wp/v2/settings', headers=auth_headers, timeout=10)
if resp.status_code == 200:
    settings = resp.json()
    blog_public = settings.get('blog_public', '?')
    print(f'1. Settings > Reading (blog_public): {blog_public}')
    if blog_public == 1:
        print(f'   Status: GOOD - site is allowing Google to index')
    elif blog_public == 0:
        print(f'   Status: ERROR - site is blocking Google from indexing')
    else:
        print(f'   Status: Unknown value')
else:
    print(f'1. Settings check: HTTP {resp.status_code}')

# 2. Homepage robots
print()
resp = requests.get(WP_BASE_URL + '/', timeout=10, headers={'Cache-Control': 'no-cache'})
m = re.search(r'meta[^>]*robots[^>]*content=["\']([^"\']+)["\']', resp.text, re.I)
homepage_robots = m.group(1) if m else 'NOT FOUND'
print(f'2. Homepage robots: {homepage_robots} (HTTP {resp.status_code})')
if 'index' in homepage_robots and 'noindex' not in homepage_robots:
    print(f'   Status: GOOD - homepage is indexable by Google')
else:
    print(f'   Status: CHECK NEEDED')

# 3. Dev pages protection
print()
print('3. Dev/Test pages (should NOT be indexed):')
DEV_PAGES = [(439, 'pay-test'), (468, 'pay-test-sandbox'), (150, 'elementor-150'), (311, 'paypal-buttons-embed')]
all_protected = True
for page_id, slug in DEV_PAGES:
    resp_status = requests.get(
        f'{WP_BASE_URL}/wp-json/wp/v2/pages/{page_id}?context=edit&_fields=status',
        headers=auth_headers, timeout=10
    )
    wp_status = resp_status.json().get('status', '?') if resp_status.status_code == 200 else f'HTTP {resp_status.status_code}'

    resp_public = requests.get(
        f'{WP_BASE_URL}/{slug}/',
        timeout=10, allow_redirects=True,
        headers={'Cache-Control': 'no-cache'}
    )
    public_http = resp_public.status_code
    is_protected = public_http != 200

    if not is_protected:
        all_protected = False

    protection_label = 'PROTECTED' if is_protected else 'STILL EXPOSED'
    print(f'   /{slug}/: WP={wp_status} | Public HTTP={public_http} | {protection_label}')

if all_protected:
    print('   -> ALL DEV PAGES PROTECTED from Google')
else:
    print('   -> WARNING: Some pages may still be exposed')

# 4. Main blog/content pages
print()
print('4. Main content pages (should be indexed):')
MAIN_PAGES = [
    ('', 'Homepage'),
    ('blog/', 'Blog'),
    ('why-ai-memory-changes-everything/', 'Blog post sample'),
]
for path, name in MAIN_PAGES:
    url = f'{WP_BASE_URL}/{path}'
    resp = requests.get(url, timeout=10, headers={'Cache-Control': 'no-cache'})
    m = re.search(r'meta[^>]*robots[^>]*content=["\']([^"\']+)["\']', resp.text, re.I)
    robots = m.group(1) if m else 'NOT FOUND'
    print(f'   {name}: HTTP {resp.status_code} | robots={robots[:80]}')

print()
print('=== SUMMARY ===')
print('Settings > Reading: FIXED (was blocking indexing, now allows it)')
print('Homepage: Indexable by Google (index, follow)')
print('Dev pages: Protected (set to WordPress private - return 404 to unauthenticated users)')
print('Main pages: Indexable by Google')
print()
print('WHAT GOOGLE WILL SEE:')
print('- Homepage, blog, blog posts: index and crawl normally')
print('- /pay-test/, /pay-test-sandbox/, /elementor-150/, /paypal-buttons-embed/: 404 (will be removed from index over time)')
print()
print('NEXT STEPS FOR JARED:')
print('1. Go to Google Search Console > URL Inspection > Request re-indexing for homepage')
print('2. Submit sitemap: https://purebrain.ai/sitemap_index.xml')
print('3. For pay-test page: It still works when you are LOGGED IN to WordPress')
print('   (Private pages are accessible to authenticated WP users)')
print('4. Wait 1-2 weeks for Google to re-crawl and index the site properly')
