#!/usr/bin/env python3
from dotenv import load_dotenv
load_dotenv('/home/jared/projects/AI-CIV/aether/.env')
import os, requests
from requests.auth import HTTPBasicAuth

BASE = 'https://purebrain.ai/wp-json/wp/v2'
AUTH = HTTPBasicAuth('Aether', os.getenv('PUREBRAIN_WP_APP_PASSWORD'))

ALL_PAGE_IDS = [11,319,777,752,753,754,755,756,757,758,759,760,284,577,731,794,923,929,405,620,700,800,816,860,970,987]
NEEDS_OG_IMAGE = {319,777,752,753,754,755,756,757,758,759,760,284,405,987,620,800,816,970}

print('Full verification -- all 26 pages')
print('=' * 80)
all_pass = True
for pid in ALL_PAGE_IDS:
    r = requests.get(f'{BASE}/pages/{pid}?context=edit', auth=AUTH, timeout=15)
    if r.status_code != 200:
        print(f'  [{pid}] FETCH ERROR {r.status_code}')
        all_pass = False
        continue
    d = r.json()
    meta = d.get('meta', {})
    exc_raw = d.get('excerpt', {}).get('raw', '')
    og_title = meta.get('_yoast_wpseo_opengraph-title', '')
    og_image = meta.get('_yoast_wpseo_opengraph-image', '')
    og_image_id = meta.get('_yoast_wpseo_opengraph-image-id', '')
    fm = d.get('featured_media', 0)

    checks = []
    if not exc_raw:
        checks.append('MISSING_EXCERPT')
    if not og_title:
        checks.append('MISSING_OG_TITLE')
    if pid in NEEDS_OG_IMAGE and not og_image:
        checks.append('MISSING_OG_IMAGE')

    status = 'PASS' if not checks else 'FAIL: ' + ', '.join(checks)
    if checks:
        all_pass = False
    print(f'  [{pid:>4}] {status}  | fm={fm} | og_image_id={og_image_id or "--"} | exc={"YES" if exc_raw else "NO"}')

print('=' * 80)
print('Overall:', 'ALL PASS' if all_pass else 'SOME FAILURES (see above)')
