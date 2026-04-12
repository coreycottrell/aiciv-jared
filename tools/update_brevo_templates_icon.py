#!/usr/bin/env python3
"""
Update all 7 Neural Feed Brevo templates to add PureBrain hexagon icon
and verify brand colors in header.

Changes:
- Add PureBrain hexagon icon above the PUREBRAIN.ai text in header
- Icon: https://purebrain.ai/wp-content/uploads/2026/02/purebrain-icon-email.png
- PUREBR + N = #2a93c1 (blue), AI = #f1420b (orange), .ai = white
- THE NEURAL FEED subtitle remains
"""

from dotenv import load_dotenv
import os
import requests
import re

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

BREVO_API_KEY = os.getenv('BREVO_API_KEY')
ICON_URL = 'https://purebrain.ai/wp-content/uploads/2026/02/purebrain-icon-email.png'
HEADERS = {'api-key': BREVO_API_KEY, 'Content-Type': 'application/json'}

# The new header HTML - replaces the old header div content
# Using a table layout for email client compatibility (no flexbox in email)
NEW_HEADER_INNER = '''<a href="https://purebrain.ai" style="text-decoration: none;">
        <!-- Icon -->
        <div style="margin-bottom: 10px;">
          <img src="{icon_url}" alt="PureBrain" width="52" height="52" style="width: 52px; height: 52px; display: block; margin: 0 auto;" />
        </div>
        <!-- Logo text -->
        <div class="header-logo">PUREBR<span class="ai">AI</span>N<span class="header-ai-suffix">.ai</span></div>
      </a>
      <div class="header-sub">The Neural Feed</div>'''.format(icon_url=ICON_URL)

# Old header inner pattern to find and replace
OLD_HEADER_INNER_PATTERN = r'<a href="https://purebrain\.ai">\s*<div class="header-logo">PUREBR<span class="ai">AI</span>N\.ai</div>\s*</a>\s*<div class="header-sub">The Neural Feed</div>'

# Also need to add .header-ai-suffix style for white .ai text
OLD_HEADER_LOGO_STYLE = '.header-logo { font-size: 18px; font-weight: 700; letter-spacing: 1px; }'
NEW_HEADER_LOGO_STYLE = '''.header-logo { font-size: 18px; font-weight: 700; letter-spacing: 1px; }
  .header-ai-suffix { color: #ffffff; }'''

def fetch_template(template_id):
    resp = requests.get(
        f'https://api.brevo.com/v3/smtp/templates/{template_id}',
        headers=HEADERS,
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()

def update_template(template_id, html_content, subject):
    resp = requests.put(
        f'https://api.brevo.com/v3/smtp/templates/{template_id}',
        headers=HEADERS,
        json={'htmlContent': html_content, 'subject': subject},
        timeout=15,
    )
    return resp.status_code, resp.text

def patch_template_html(html):
    """Apply branding fixes to template HTML."""
    original = html
    changed = False

    # 1. Add .header-ai-suffix CSS rule if not present
    if '.header-ai-suffix' not in html:
        html = html.replace(
            OLD_HEADER_LOGO_STYLE,
            NEW_HEADER_LOGO_STYLE,
        )
        if '.header-ai-suffix' in html:
            changed = True

    # 2. Replace header inner content (add icon + fix .ai color)
    # Use regex to find the old pattern
    match = re.search(OLD_HEADER_INNER_PATTERN, html, re.DOTALL)
    if match:
        html = html[:match.start()] + NEW_HEADER_INNER + html[match.end():]
        changed = True
    else:
        # Check if icon is already there (already updated)
        if ICON_URL in html:
            print('  [SKIP] Icon already present in this template')
            return html, False
        else:
            print('  [WARN] Could not find expected header pattern - manual inspection needed')
            print('  Header section:')
            idx = html.find('<div class="header">')
            if idx >= 0:
                print(' ', repr(html[idx:idx+300]))

    return html, changed

def main():
    print('=== PureBrain Brevo Template Icon Update ===')
    print(f'Icon URL: {ICON_URL}')
    print()

    results = []

    for template_id in range(1, 8):
        print(f'Processing Template {template_id}...')
        try:
            # Fetch current template
            tpl = fetch_template(template_id)
            name = tpl.get('name', '')
            subject = tpl.get('subject', '')
            html = tpl.get('htmlContent', '')
            print(f'  Name: {name}')
            print(f'  Subject: {subject}')
            print(f'  HTML length: {len(html)}')

            # Apply patches
            new_html, changed = patch_template_html(html)

            if changed:
                # Update template via API
                status, response_text = update_template(template_id, new_html, subject)
                if status in (200, 204):
                    print(f'  [OK] Updated successfully (HTTP {status})')
                    results.append({'id': template_id, 'status': 'updated', 'name': name})
                else:
                    print(f'  [ERROR] Update failed (HTTP {status}): {response_text[:200]}')
                    results.append({'id': template_id, 'status': 'error', 'name': name, 'error': response_text[:200]})
            else:
                print(f'  [SKIP] No changes needed')
                results.append({'id': template_id, 'status': 'skipped', 'name': name})

        except Exception as e:
            print(f'  [ERROR] Exception: {e}')
            results.append({'id': template_id, 'status': 'exception', 'error': str(e)})

        print()

    print('=== Summary ===')
    for r in results:
        print(f'  Template {r["id"]}: {r.get("name", "?")} -> {r["status"]}')

    return results

if __name__ == '__main__':
    main()
