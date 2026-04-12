#!/usr/bin/env python3
"""Quick script to fetch and inspect _elementor_data for page 1283."""
import os, json, requests
from dotenv import load_dotenv

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')
WP_USER = 'Aether'
WP_PASS = os.getenv('PUREBRAIN_WP_APP_PASSWORD')

r = requests.get(
    'https://purebrain.ai/wp-json/wp/v2/pages/1283?context=edit',
    auth=(WP_USER, WP_PASS),
    timeout=30
)
print('HTTP:', r.status_code)
if r.status_code == 200:
    data = r.json()
    meta = data.get('meta', {})
    ed = meta.get('_elementor_data', '')
    print('_elementor_data length:', len(ed))
    if ed:
        try:
            parsed = json.loads(ed)
            print('Top-level element count:', len(parsed))
            print('Structure preview:')
            for i, el in enumerate(parsed[:2]):
                print(f'  [{i}] elType={el.get("elType")} id={el.get("id")}')
                for col in el.get('elements', [])[:1]:
                    for widget in col.get('elements', [])[:2]:
                        wtype = widget.get('widgetType','?')
                        wid = widget.get('id','?')
                        html_snippet = widget.get('settings',{}).get('html','')[:80]
                        print(f'    widget: {wtype} id={wid} html_preview={html_snippet!r}')
        except Exception as e:
            print('Parse error:', e)
            print('Raw (first 300):', ed[:300])
    template = data.get('meta', {}).get('_elementor_template_type', '')
    print('Template type:', template)
    # Also print page template slug
    print('Page template (page_template):', data.get('template', ''))
else:
    print(r.text[:400])
