#!/usr/bin/env python3
"""
Fix pricing numbers in sales-call-wizard/index.html
Source of truth: ai-tool-stack-calculator-v4.html TIERS array

Correct values (Claude Max subscription costs per calculator footnote):
- Awakened ($149/mo): Claude Max = $100/mo, total spend = $249/mo
- Bonded ($499/mo): Claude Max = $200/mo, total spend = $699/mo
- Partnered ($999/mo): Claude Max = $200/mo, total spend = $1,199/mo
- Unified (Custom): volume pricing / contact for quote (unchanged)
"""

import re

with open('/home/jared/projects/AI-CIV/aether/exports/sales-call-wizard/index.html', 'r') as f:
    content = f.read()

original = content

# Fix Awakened tier: $20/mo -> $100/mo, $169/mo -> $249/mo
content = content.replace(
    '          1 AI Brain + Core Tools\n          <span class="cost-line">Claude cost: ~$20/mo per user</span>\n          <span class="cost-line our-cost">Their actual spend: ~$169/mo</span>',
    '          1 AI Brain + Core Tools\n          <span class="cost-line">Claude cost (Claude Max): $100/mo</span>\n          <span class="cost-line our-cost">Their actual spend: $249/mo</span>'
)

# Fix Bonded tier: $60/mo -> $200/mo, $559/mo -> $699/mo
content = content.replace(
    '          3 AI Brains + Advanced Tools\n          <span class="cost-line">Claude cost: ~$60/mo per user</span>\n          <span class="cost-line our-cost">Their actual spend: ~$559/mo</span>',
    '          3 AI Brains + Advanced Tools\n          <span class="cost-line">Claude cost (Claude Max): $200/mo</span>\n          <span class="cost-line our-cost">Their actual spend: $699/mo</span>'
)

# Fix Partnered tier: $100/mo -> $200/mo, $1,099/mo -> $1,199/mo
content = content.replace(
    '          Unlimited Brains + Priority\n          <span class="cost-line">Claude cost: ~$100/mo per user</span>\n          <span class="cost-line our-cost">Their actual spend: ~$1,099/mo</span>',
    '          Unlimited Brains + Priority\n          <span class="cost-line">Claude cost (Claude Max): $200/mo</span>\n          <span class="cost-line our-cost">Their actual spend: $1,199/mo</span>'
)

if content == original:
    print("ERROR: No replacements made — pattern mismatch. Check the HTML carefully.")
    exit(1)

# Count changes
awakened_fixed = '~$20/mo per user' not in content and '$100/mo' in content
bonded_fixed = '~$60/mo per user' not in content
partnered_fixed = '~$100/mo per user' not in content

print(f"Awakened fixed: {awakened_fixed}")
print(f"Bonded fixed: {bonded_fixed}")
print(f"Partnered fixed: {partnered_fixed}")

with open('/home/jared/projects/AI-CIV/aether/exports/sales-call-wizard/index.html', 'w') as f:
    f.write(content)

print("File written successfully.")

# Verify by searching for old values
old_values = ['~$20/mo per user', '~$60/mo per user', '~$100/mo per user', '~$169/mo', '~$559/mo', '~$1,099/mo']
for v in old_values:
    if v in content:
        print(f"WARNING: Old value still present: {v}")
    else:
        print(f"CONFIRMED REMOVED: {v}")

new_values = ['Claude cost (Claude Max): $100/mo', 'Their actual spend: $249/mo',
              'Claude cost (Claude Max): $200/mo', 'Their actual spend: $699/mo',
              'Their actual spend: $1,199/mo']
for v in new_values:
    if v in content:
        print(f"CONFIRMED PRESENT: {v}")
    else:
        print(f"WARNING: New value missing: {v}")
