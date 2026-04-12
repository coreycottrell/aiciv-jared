#!/usr/bin/env python3
"""
Fix pricing numbers in sales-call-wizard/index.html and deploy to WordPress.

Source of truth: ai-tool-stack-calculator-v4.html TIERS array
Claude Max subscription costs (per calculator footnote):
  "$100/mo for Awakened & Bonded, $200/mo for Partnered & Unified"

Correct values:
- Awakened ($149/mo): Claude Max = $100/mo, total spend = $249/mo
- Bonded ($499/mo): Claude Max = $200/mo, total spend = $699/mo
- Partnered ($999/mo): Claude Max = $200/mo, total spend = $1,199/mo
- Unified (Custom): volume pricing / contact for quote (unchanged)

WP Page: live-call (ID 1283) at https://purebrain.ai/sales-playbook/live-call/
"""

import urllib.request
import urllib.error
import json
import base64

HTML_PATH = '/home/jared/projects/AI-CIV/aether/exports/sales-call-wizard/index.html'
WP_USER = 'Aether'
WP_APP_PASSWORD = 'ZGuh 1W8k WpWM c9iy kqyd buPr'
WP_BASE = 'https://purebrain.ai/wp-json/wp/v2'
PAGE_ID = 1283

# ── STEP 1: Read the file ──────────────────────────────────────────────────
print("Reading index.html...")
with open(HTML_PATH, 'r') as f:
    content = f.read()

original = content

# ── STEP 2: Apply targeted replacements ───────────────────────────────────
print("Applying pricing fixes...")

# Awakened: $20/mo → $100/mo (Claude Max), $169/mo → $249/mo
content = content.replace(
    'Claude cost: ~$20/mo per user',
    'Claude cost (Claude Max): $100/mo'
)
content = content.replace(
    'Their actual spend: ~$169/mo',
    'Their actual spend: $249/mo'
)

# Bonded: $60/mo → $200/mo (Claude Max), $559/mo → $699/mo
content = content.replace(
    'Claude cost: ~$60/mo per user',
    'Claude cost (Claude Max): $200/mo'
)
content = content.replace(
    'Their actual spend: ~$559/mo',
    'Their actual spend: $699/mo'
)

# Partnered: $100/mo → $200/mo (Claude Max), $1,099/mo → $1,199/mo
content = content.replace(
    'Claude cost: ~$100/mo per user',
    'Claude cost (Claude Max): $200/mo'
)
content = content.replace(
    'Their actual spend: ~$1,099/mo',
    'Their actual spend: $1,199/mo'
)

if content == original:
    print("ERROR: No replacements made — patterns did not match. Check file content.")
    exit(1)

# ── STEP 3: Verify old values gone, new values present ───────────────────
print("Verifying replacements...")
issues = []

old_checks = [
    '~$20/mo per user', '~$60/mo per user', '~$100/mo per user',
    '~$169/mo', '~$559/mo', '~$1,099/mo'
]
for v in old_checks:
    if v in content:
        issues.append(f"OLD VALUE STILL PRESENT: {v}")
    else:
        print(f"  REMOVED: {v}")

new_checks = [
    ('Claude cost (Claude Max): $100/mo', 'Awakened Claude Max cost'),
    ('Their actual spend: $249/mo', 'Awakened total spend'),
    ('Claude cost (Claude Max): $200/mo', 'Bonded+Partnered Claude Max cost'),
    ('Their actual spend: $699/mo', 'Bonded total spend'),
    ('Their actual spend: $1,199/mo', 'Partnered total spend'),
]
for v, label in new_checks:
    if v not in content:
        issues.append(f"NEW VALUE MISSING: {v} ({label})")
    else:
        print(f"  CONFIRMED: {label} = {v}")

if issues:
    print("\nVERIFICATION FAILED:")
    for i in issues:
        print(f"  - {i}")
    exit(1)

print("\nAll verifications PASSED.")

# ── STEP 4: Write the fixed file ──────────────────────────────────────────
with open(HTML_PATH, 'w') as f:
    f.write(content)
print(f"Local file updated: {HTML_PATH}")

# ── STEP 5: Deploy to WordPress (UPDATE existing page 1283) ──────────────
print(f"\nDeploying to WordPress page ID {PAGE_ID}...")

wrapped = f'<!-- wp:html -->\n{content}\n<!-- /wp:html -->'

credentials = f'{WP_USER}:{WP_APP_PASSWORD}'
token = base64.b64encode(credentials.encode()).decode('utf-8')

page_data = {
    'content': wrapped,
    'status': 'publish',
}

payload = json.dumps(page_data).encode('utf-8')

req = urllib.request.Request(
    f'{WP_BASE}/pages/{PAGE_ID}',
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
        print(f"\nDeploy SUCCESS (HTTP {resp.status})")
        print(f"  Page ID:  {data.get('id')}")
        print(f"  Slug:     {data.get('slug')}")
        print(f"  Status:   {data.get('status')}")
        print(f"  URL:      {data.get('link')}")
        print(f"  Modified: {data.get('modified')}")
        print("\nPricing fix is LIVE at https://purebrain.ai/sales-playbook/live-call/")

except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8')
    print(f"HTTP ERROR {e.code}: {e.reason}")
    print(body[:2000])
    exit(1)
except Exception as e:
    print(f"ERROR: {e}")
    exit(1)
