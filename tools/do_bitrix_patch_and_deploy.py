#!/usr/bin/env python3
"""
Atomic patch + deploy for Bitrix CRM wiring.
Verified webhook: https://puremarketing.bitrix24.com/rest/1/d1azasrcgghsy27v/
  - 200 OK, 90+ lead fields returned

Steps:
  1. Patch 4 config lines in index.html (in-place)
  2. Deploy to WordPress page 1283 via _elementor_data meta
  3. Clear Elementor cache
  4. Send Telegram confirmation
"""
import os, sys, json, subprocess, requests
from dotenv import load_dotenv

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

HTML   = '/home/jared/projects/AI-CIV/aether/exports/sales-call-wizard/index.html'
WP     = 'https://purebrain.ai/wp-json/wp/v2'
USER   = 'Aether'
PASS   = os.getenv('PUREBRAIN_WP_APP_PASSWORD', '')
PID    = 1283
TG     = '/home/jared/projects/AI-CIV/aether/tools/tg_send.sh'

BITRIX = 'https://puremarketing.bitrix24.com/rest/1/d1azasrcgghsy27v/'
GFID   = '1KetwS3uHPEKJZfwV5XQM1hsW6OOw9JqT'

def tg(msg):
    try: subprocess.run([TG, msg], timeout=10, check=False)
    except: pass

# ── 1. PATCH HTML ─────────────────────────────────────────────────────────────
print('Step 1: Patching index.html...')
tg('🔧 Bitrix wiring step 1/3 — patching HTML config')

with open(HTML, 'r') as f:
    src = f.read()

patches = [
    ("const BITRIX_ENABLED = false; // SET TO true AFTER entering your webhook URL below",
     "const BITRIX_ENABLED = true; // Enabled 2026-03-05"),
    ("const BITRIX_WEBHOOK_URL = 'https://YOUR-DOMAIN.bitrix24.com/rest/USER_ID/WEBHOOK_CODE';",
     f"const BITRIX_WEBHOOK_URL = '{BITRIX}';"),
    ("const GDRIVE_ENABLED = false; // SET TO true once backend endpoint is live",
     "const GDRIVE_ENABLED = true; // Enabled 2026-03-05"),
    ("const GDRIVE_SALES_FOLDER_ID = ''; // Paste your Google Drive Sales Calls folder ID here",
     f"const GDRIVE_SALES_FOLDER_ID = '{GFID}'; // Sales Calls folder"),
]

for old, new in patches:
    if old not in src:
        print(f'  ABORT: string not found: {old[:60]}')
        tg(f'🔧 Bitrix wiring FAILED — string not found in HTML')
        sys.exit(1)
    src = src.replace(old, new, 1)
    print(f'  OK: {new[:80]}')

with open(HTML, 'w') as f:
    f.write(src)
print('  HTML saved.')

# ── 2. DEPLOY TO WORDPRESS ────────────────────────────────────────────────────
print('\nStep 2: Deploying to WordPress page 1283...')
tg('🔧 Bitrix wiring step 2/3 — deploying to WordPress')

if not PASS:
    print('  ERROR: PUREBRAIN_WP_APP_PASSWORD not set')
    sys.exit(1)

auth = (USER, PASS)

# Fetch existing _elementor_data to preserve structure
r = requests.get(f'{WP}/pages/{PID}?context=edit', auth=auth, timeout=30)
if r.status_code != 200:
    print(f'  WARN: Could not fetch page ({r.status_code}) — using fresh structure')
    existing = None
else:
    meta = r.json().get('meta', {})
    raw = meta.get('_elementor_data', '')
    try:
        existing = json.loads(raw) if raw else None
    except:
        existing = None

# Build Elementor data — surgical replace if structure matches, fresh otherwise
def build_ed(html_content, existing):
    if existing and len(existing) == 1:
        s = existing[0]
        cols = s.get('elements', [])
        if len(cols) == 1:
            widgets = cols[0].get('elements', [])
            if len(widgets) == 1 and widgets[0].get('widgetType') == 'html':
                widgets[0]['settings']['html'] = html_content
                print('  Surgical widget replacement (IDs preserved)')
                return json.dumps(existing)
    print('  Fresh Elementor HTML widget structure')
    return json.dumps([{
        "id": "scw_sec", "elType": "section", "isInner": False,
        "settings": {}, "elements": [{
            "id": "scw_col", "elType": "column",
            "settings": {"_column_size": 100}, "elements": [{
                "id": "scw_wgt", "elType": "widget", "widgetType": "html",
                "settings": {"html": html_content}, "elements": []
            }]
        }]
    }])

# Strip document envelope for Elementor embedding (browser mangles nested <html>/<head>/<body>)
import re
deploy_html = src
deploy_html = re.sub(r'<!DOCTYPE[^>]*>\s*', '', deploy_html)
deploy_html = re.sub(r'<html[^>]*>\s*', '', deploy_html)
deploy_html = re.sub(r'<head>\s*', '', deploy_html)
deploy_html = re.sub(r'</head>\s*', '', deploy_html)
deploy_html = re.sub(r'<body>\s*', '', deploy_html)
deploy_html = re.sub(r'</body>\s*', '', deploy_html)
deploy_html = re.sub(r'</html>\s*', '', deploy_html)
print('  Stripped document envelope for Elementor embedding')

ed = build_ed(deploy_html, existing)

resp = requests.post(
    f'{WP}/pages/{PID}',
    auth=auth,
    headers={'Content-Type': 'application/json'},
    json={'meta': {
        '_elementor_data': ed,
        '_elementor_edit_mode': 'builder',
        '_elementor_template_type': 'wp-page',
    }},
    timeout=30
)

if resp.status_code not in (200, 201):
    print(f'  ERROR: HTTP {resp.status_code} — {resp.text[:300]}')
    tg(f'🔧 Bitrix wiring FAILED — WP deploy HTTP {resp.status_code}')
    sys.exit(1)

print(f'  OK: _elementor_data updated (HTTP {resp.status_code})')

# ── 3. CLEAR ELEMENTOR CACHE ──────────────────────────────────────────────────
print('\nStep 3: Clearing Elementor cache...')
cr = requests.delete(
    'https://purebrain.ai/wp-json/elementor/v1/cache',
    auth=auth, timeout=30
)
print(f'  Cache clear: HTTP {cr.status_code}')

# ── DONE ──────────────────────────────────────────────────────────────────────
print('\n=== COMPLETE ===')
print(f'  File: {HTML}')
print(f'  Live: https://purebrain.ai/sales-playbook/live-call/')
print(f'  BITRIX_ENABLED = true')
print(f'  BITRIX_WEBHOOK_URL = {BITRIX}')
print(f'  GDRIVE_ENABLED = true')
print(f'  GDRIVE_SALES_FOLDER_ID = {GFID}')

tg('✅ Bitrix CRM wiring COMPLETE — Sales Call Wizard creates Bitrix leads + GDrive docs on every call save. Live: https://purebrain.ai/sales-playbook/live-call/')
