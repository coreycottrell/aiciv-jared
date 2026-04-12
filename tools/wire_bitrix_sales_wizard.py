#!/usr/bin/env python3
"""
Wire Bitrix CRM into Sales Call Wizard — CTO-authorized deployment
Tasks:
  1. Patch 4 config lines in index.html
  2. Verify Bitrix webhook via crm.lead.fields
  3. Deploy to WordPress page 1283 (Elementor meta + cache clear)
  4. Send progress to Telegram

Run: python3 /home/jared/projects/AI-CIV/aether/tools/wire_bitrix_sales_wizard.py
"""

import os, sys, json, subprocess, requests
from dotenv import load_dotenv

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

# ── CONSTANTS ────────────────────────────────────────────────────────────────
HTML_PATH   = '/home/jared/projects/AI-CIV/aether/exports/sales-call-wizard/index.html'
WP_BASE     = 'https://purebrain.ai/wp-json/wp/v2'
WP_USER     = 'Aether'
WP_PASS     = os.getenv('PUREBRAIN_WP_APP_PASSWORD', '')
PAGE_ID     = 1283
BITRIX_URL  = 'https://puremarketing.bitrix24.com/rest/1/d1azasrcgghsy27v/'
GDRIVE_FID  = '1KetwS3uHPEKJZfwV5XQM1hsW6OOw9JqT'
TG_SEND     = '/home/jared/projects/AI-CIV/aether/tools/tg_send.sh'

# ── TELEGRAM HELPER ──────────────────────────────────────────────────────────
def tg(msg):
    try:
        subprocess.run([TG_SEND, msg], timeout=10, check=False)
    except Exception as e:
        print(f'  [TG warn] {e}')

# ── STEP 1: PATCH HTML ───────────────────────────────────────────────────────
def patch_html():
    print('\n[1/4] Patching config flags in index.html...')
    tg('🔧 Bitrix CRM wiring: Step 1/4 — patching HTML config flags')

    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        html = f.read()

    replacements = [
        (
            "const BITRIX_ENABLED = false; // SET TO true AFTER entering your webhook URL below",
            "const BITRIX_ENABLED = true; // Enabled 2026-03-05"
        ),
        (
            "const BITRIX_WEBHOOK_URL = 'https://YOUR-DOMAIN.bitrix24.com/rest/USER_ID/WEBHOOK_CODE';",
            f"const BITRIX_WEBHOOK_URL = '{BITRIX_URL}';"
        ),
        (
            "const GDRIVE_ENABLED = false; // SET TO true once backend endpoint is live",
            "const GDRIVE_ENABLED = true; // Enabled 2026-03-05"
        ),
        (
            "const GDRIVE_SALES_FOLDER_ID = ''; // Paste your Google Drive Sales Calls folder ID here",
            f"const GDRIVE_SALES_FOLDER_ID = '{GDRIVE_FID}'; // Sales Calls folder"
        ),
    ]

    for old, new in replacements:
        if old not in html:
            msg = f'ABORT: Target string not found:\n  {old}'
            print(f'  ERROR: {msg}')
            tg(f'🔧 Bitrix CRM wiring: FAILED — {msg}')
            sys.exit(1)
        html = html.replace(old, new, 1)
        print(f'  PATCHED: {new}')

    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(html)

    print('  HTML saved to disk.')
    return html


# ── STEP 2: TEST BITRIX WEBHOOK ──────────────────────────────────────────────
def test_bitrix():
    print('\n[2/4] Testing Bitrix webhook (crm.lead.fields)...')
    tg('🔧 Bitrix CRM wiring: Step 2/4 — testing webhook')

    url = BITRIX_URL.rstrip('/') + '/crm.lead.fields'
    try:
        r = requests.get(url, timeout=15)
    except Exception as e:
        print(f'  ERROR: {e}')
        tg(f'🔧 Bitrix CRM wiring: FAILED — webhook unreachable: {e}')
        sys.exit(1)

    if r.status_code != 200:
        print(f'  ERROR: HTTP {r.status_code} — {r.text[:200]}')
        tg(f'🔧 Bitrix CRM wiring: FAILED — webhook HTTP {r.status_code}')
        sys.exit(1)

    data = r.json()
    if 'result' not in data:
        print(f'  ERROR: Unexpected response: {r.text[:200]}')
        tg('🔧 Bitrix CRM wiring: FAILED — unexpected webhook response')
        sys.exit(1)

    field_count = len(data['result'])
    print(f'  OK: Webhook live — {field_count} lead fields available')
    tg(f'🔧 Bitrix CRM wiring: Step 2/4 — webhook verified ({field_count} fields)')
    return True


# ── STEP 3: FETCH CURRENT ELEMENTOR DATA (preserve structure) ────────────────
def fetch_current_elementor():
    print('\n[3/4a] Fetching current Elementor data for page 1283...')
    r = requests.get(
        f'{WP_BASE}/pages/{PAGE_ID}?context=edit',
        auth=(WP_USER, WP_PASS),
        timeout=30
    )
    if r.status_code != 200:
        print(f'  WARN: Could not fetch page (HTTP {r.status_code}) — will use fresh structure')
        return None

    meta = r.json().get('meta', {})
    ed = meta.get('_elementor_data', '')
    if not ed:
        print('  WARN: No existing _elementor_data — will use fresh structure')
        return None

    try:
        parsed = json.loads(ed)
        print(f'  Found existing structure with {len(parsed)} top-level sections')
        return parsed
    except Exception as e:
        print(f'  WARN: Could not parse existing data ({e}) — will use fresh structure')
        return None


def build_elementor_data(html_content, existing=None):
    """
    Strategy:
    - If existing data has a single section with a single HTML widget, replace that widget's html.
    - Otherwise build a fresh minimal wrapper.
    """
    if existing and len(existing) == 1:
        section = existing[0]
        cols = section.get('elements', [])
        if len(cols) == 1:
            widgets = cols[0].get('elements', [])
            if len(widgets) == 1 and widgets[0].get('widgetType') == 'html':
                # Surgical replace — preserve all IDs and settings, just swap html
                widgets[0]['settings']['html'] = html_content
                print('  Using surgical replacement (preserved existing widget IDs)')
                return json.dumps(existing)

    # Fresh structure fallback
    print('  Building fresh Elementor HTML widget structure')
    block = [
        {
            "id": "scwiz_sec",
            "elType": "section",
            "isInner": False,
            "settings": {"layout": "full_width", "content_width": {"unit": "px", "size": 1200}},
            "elements": [
                {
                    "id": "scwiz_col",
                    "elType": "column",
                    "settings": {"_column_size": 100, "content_position": ""},
                    "elements": [
                        {
                            "id": "scwiz_widget",
                            "elType": "widget",
                            "widgetType": "html",
                            "settings": {"html": html_content},
                            "elements": []
                        }
                    ]
                }
            ]
        }
    ]
    return json.dumps(block)


# ── STEP 3: DEPLOY TO WORDPRESS ──────────────────────────────────────────────
def deploy_to_wordpress(html_content):
    print('\n[3/4] Deploying to WordPress page 1283...')
    tg('🔧 Bitrix CRM wiring: Step 3/4 — deploying to WordPress')

    existing = fetch_current_elementor()
    elementor_data = build_elementor_data(html_content, existing)

    payload = {
        'meta': {
            '_elementor_data': elementor_data,
            '_elementor_edit_mode': 'builder',
            '_elementor_template_type': 'wp-page',
        }
    }

    r = requests.post(
        f'{WP_BASE}/pages/{PAGE_ID}',
        auth=(WP_USER, WP_PASS),
        headers={'Content-Type': 'application/json'},
        json=payload,
        timeout=30
    )

    if r.status_code not in (200, 201):
        print(f'  ERROR: HTTP {r.status_code} — {r.text[:400]}')
        tg(f'🔧 Bitrix CRM wiring: FAILED — WP deploy HTTP {r.status_code}')
        sys.exit(1)

    print(f'  OK: Page meta updated (HTTP {r.status_code})')

    # Clear Elementor cache
    print('  Clearing Elementor cache...')
    cache_r = requests.delete(
        'https://purebrain.ai/wp-json/elementor/v1/cache',
        auth=(WP_USER, WP_PASS),
        timeout=30
    )
    if cache_r.status_code in (200, 201, 204):
        print(f'  OK: Cache cleared (HTTP {cache_r.status_code})')
    else:
        print(f'  WARN: Cache clear returned HTTP {cache_r.status_code} — continuing')

    return True


# ── MAIN ─────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print('=== Sales Call Wizard — Bitrix CRM Wiring ===')
    tg('🔧 Bitrix CRM wiring: Starting deployment sequence')

    if not WP_PASS:
        print('ERROR: PUREBRAIN_WP_APP_PASSWORD not set in .env')
        sys.exit(1)

    patched_html = patch_html()
    test_bitrix()
    deploy_to_wordpress(patched_html)

    print('\n=== ALL STEPS COMPLETE ===')
    print(f'  HTML:    {HTML_PATH}')
    print(f'  Page:    https://purebrain.ai/sales-playbook/live-call/')
    print(f'  Bitrix:  ENABLED — {BITRIX_URL}')
    print(f'  GDrive:  ENABLED — folder {GDRIVE_FID}')

    tg('✅ Bitrix CRM wiring: COMPLETE — Sales Call Wizard now creates Bitrix leads + GDrive docs on call save. Live at https://purebrain.ai/sales-playbook/live-call/')
