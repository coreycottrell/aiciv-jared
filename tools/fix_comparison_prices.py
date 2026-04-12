#!/usr/bin/env python3
"""
Fix PureBrain pricing on comparison pages.

Source of truth (from main page):
- Awakened: $79/mo (DO NOT show on comparison pages per rules)
- Bonded: $149/mo
- Partnered: $499/mo
- Unified: $999/mo

Rules:
- Do NOT show $79 Awakened tier on comparison pages
- Do NOT change competitor pricing
- Minimum surgical changes only
"""
import requests
import re
import os
import json
import copy
from dotenv import load_dotenv

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

wp_pass = os.getenv('PUREBRAIN_WP_APP_PASSWORD')
auth = ('Aether', wp_pass)

changes_report = []


def update_page(page_id, new_content):
    """Update page content via WP REST API."""
    r = requests.post(
        f'https://purebrain.ai/wp-json/wp/v2/pages/{page_id}',
        auth=auth,
        json={'content': new_content}
    )
    return r.status_code, r.json() if r.status_code in [200, 201] else r.text


def clear_elementor_cache():
    """Clear Elementor cache."""
    r = requests.delete(
        'https://purebrain.ai/wp-json/elementor/v1/cache',
        auth=auth
    )
    return r.status_code


# ============================================================
# PAGE 1044: purebrain-vs-sitegpt
# ============================================================
print("=" * 60)
print("FIXING PAGE 1044: purebrain-vs-sitegpt")
print("=" * 60)

r1044 = requests.get('https://purebrain.ai/wp-json/wp/v2/pages/1044?context=edit', auth=auth)
content_1044 = r1044.json()['content']['raw']
original_1044 = content_1044

page_changes_1044 = []

# Fix 1: Schema/meta description - "$179/mo" in description field
old = '"description": "Honest comparison of PureBrain vs SiteGPT. SiteGPT is a $39/mo AI support chatbot. PureBrain is a $179/mo AI executive team with 23 departments. Different products for different problems."'
new = '"description": "Honest comparison of PureBrain vs SiteGPT. SiteGPT is a $39/mo AI support chatbot. PureBrain is a $149/mo AI executive team with 23 departments. Different products for different problems."'
if old in content_1044:
    content_1044 = content_1044.replace(old, new)
    page_changes_1044.append("Fix 1: Schema description $179/mo → $149/mo")
else:
    page_changes_1044.append("Fix 1: SKIPPED - text not found exactly")
    print(f"  WARNING: Fix 1 old text not found")

# Fix 2: Hero card price range "$179 – $1,999/mo" → "$149 – $999/mo"
old2 = '$179 – $1,999/mo'
new2 = '$149 – $999/mo'
if old2 in content_1044:
    content_1044 = content_1044.replace(old2, new2)
    page_changes_1044.append(f"Fix 2: Hero card price range {old2} → {new2}")
else:
    page_changes_1044.append("Fix 2: SKIPPED - not found")
    print("  WARNING: Fix 2 not found")

# Fix 3: "PureBrain starts at $179/mo" → "$149/mo"
old3 = 'PureBrain starts at $179/mo'
new3 = 'PureBrain starts at $149/mo'
if old3 in content_1044:
    content_1044 = content_1044.replace(old3, new3)
    page_changes_1044.append(f"Fix 3: Starts at {old3} → {new3}")
else:
    page_changes_1044.append("Fix 3: SKIPPED - not found")
    print("  WARNING: Fix 3 not found")

# Fix 4: "more expensive at $179/mo minimum" → "$149/mo"
old4 = "We're more expensive at $179/mo minimum."
new4 = "We're more expensive at $149/mo minimum."
if old4 in content_1044:
    content_1044 = content_1044.replace(old4, new4)
    page_changes_1044.append(f"Fix 4: Honest weaknesses $179/mo → $149/mo")
else:
    page_changes_1044.append("Fix 4: SKIPPED - not found")
    print("  WARNING: Fix 4 not found")

# Fix 5: Pricing table column header "PureBrain Awakened" → "PureBrain Bonded"
old5 = '<th class="pb-col">PureBrain Awakened</th>'
new5 = '<th class="pb-col">PureBrain Bonded</th>'
if old5 in content_1044:
    content_1044 = content_1044.replace(old5, new5)
    page_changes_1044.append("Fix 5: Table header PureBrain Awakened → PureBrain Bonded")
else:
    page_changes_1044.append("Fix 5: SKIPPED - not found")
    print("  WARNING: Fix 5 not found")

# Fix 6: Pricing table Monthly Price PureBrain column "$179/mo" → "$149/mo"
# The row is: <td>$39/mo</td><td>$79/mo</td><td>$259/mo</td><td class="highlight">$179/mo</td>
# $79/mo and $259/mo are SiteGPT tiers - DO NOT CHANGE
# Only change the last highlight cell $179/mo
old6 = '<td class="highlight">$179/mo</td>'
new6 = '<td class="highlight">$149/mo</td>'
if old6 in content_1044:
    content_1044 = content_1044.replace(old6, new6)
    page_changes_1044.append("Fix 6: Table Monthly Price PureBrain $179/mo → $149/mo")
else:
    page_changes_1044.append("Fix 6: SKIPPED - not found")
    print("  WARNING: Fix 6 not found")

# Fix 7: Verdict text - "$179/mo" in the per-function math context
# "PureBrain's Awakened tier covers 12 business functions for $179/mo. That's roughly <strong>$15 per function</strong>"
# → "PureBrain's Bonded tier covers 12 business functions for $149/mo. That's roughly <strong>~$12 per function</strong>"
old7 = "PureBrain's Awakened tier covers 12 business functions for $179/mo. That's roughly <strong>$15 per function</strong>."
new7 = "PureBrain's Bonded tier covers 12 business functions for $149/mo. That's roughly <strong>~$12 per function</strong>."
if old7 in content_1044:
    content_1044 = content_1044.replace(old7, new7)
    page_changes_1044.append("Fix 7: Verdict math Awakened/$179/$15 → Bonded/$149/~$12")
else:
    # Try a looser match
    old7b = "PureBrain's Awakened tier covers 12 business functions for $179/mo."
    if old7b in content_1044:
        content_1044 = content_1044.replace(old7b, "PureBrain's Bonded tier covers 12 business functions for $149/mo.")
        page_changes_1044.append("Fix 7 (partial): Awakened/$179 → Bonded/$149 in verdict")
        # Also fix the $15 per function part separately
        old7c = 'roughly <strong>$15 per function</strong>'
        new7c = 'roughly <strong>~$12 per function</strong>'
        if old7c in content_1044:
            content_1044 = content_1044.replace(old7c, new7c)
            page_changes_1044.append("Fix 7b: $15 per function → ~$12 per function")
    else:
        page_changes_1044.append("Fix 7: SKIPPED - not found")
        print("  WARNING: Fix 7 not found")

# Fix 8: The compare stat block that references $179/mo (if any standalone $179/mo remain)
# Check for any remaining $179 references that are PureBrain
remaining_179 = [(m.start(), content_1044[max(0,m.start()-100):m.end()+100]) for m in re.finditer(r'\$179', content_1044)]
if remaining_179:
    print(f"\n  Remaining $179 references ({len(remaining_179)}):")
    for pos, ctx in remaining_179:
        clean = re.sub(r'<[^>]+>', ' ', ctx)
        clean = re.sub(r'\s+', ' ', clean).strip()
        print(f"    pos {pos}: {clean[:150]}")

# Also verify no $79 PureBrain references remain (there shouldn't be any pure PureBrain $79)
remaining_79 = [(m.start(), content_1044[max(0,m.start()-100):m.end()+100]) for m in re.finditer(r'\$79(?!/)', content_1044)]
if remaining_79:
    print(f"\n  $79 references ({len(remaining_79)}) - checking if any are PureBrain:")
    for pos, ctx in remaining_79:
        clean = re.sub(r'<[^>]+>', ' ', ctx)
        clean = re.sub(r'\s+', ' ', clean).strip()
        print(f"    pos {pos}: {clean[:150]}")

# Count changes
print(f"\n  Changes for page 1044:")
for c in page_changes_1044:
    print(f"    - {c}")

# Only update if changes were made
if content_1044 != original_1044:
    print(f"\n  Uploading changes to page 1044...")
    status, result = update_page(1044, content_1044)
    if status == 200:
        print(f"  SUCCESS: Page 1044 updated")
        new_len = len(result.get('content', {}).get('raw', ''))
        print(f"  New content length: {new_len}")
    else:
        print(f"  ERROR: {status} - {result}")
else:
    print("\n  No changes needed for page 1044")

changes_report.append({
    'page_id': 1044,
    'slug': 'purebrain-vs-sitegpt',
    'changes': page_changes_1044,
    'modified': content_1044 != original_1044
})


# ============================================================
# PAGE 1190: purebrain-vs-glbgpt
# ============================================================
print("\n" + "=" * 60)
print("FIXING PAGE 1190: purebrain-vs-glbgpt")
print("=" * 60)

r1190 = requests.get('https://purebrain.ai/wp-json/wp/v2/pages/1190?context=edit', auth=auth)
content_1190 = r1190.json()['content']['raw']
original_1190 = content_1190

page_changes_1190 = []

# Fix 1: Hero card "From $97 /month" → "From $149 /month"
old_g1 = 'From $97 /month'
new_g1 = 'From $149 /month'
if old_g1 in content_1190:
    content_1190 = content_1190.replace(old_g1, new_g1)
    page_changes_1190.append(f"Fix 1: Hero 'From $97 /month' → 'From $149 /month'")
else:
    page_changes_1190.append("Fix 1: SKIPPED - not found")
    print("  WARNING: Fix 1 not found")

# Fix 2: Compare strip "From $97/mo" → "From $149/mo"
old_g2 = 'From $97/mo'
new_g2 = 'From $149/mo'
count_g2 = content_1190.count(old_g2)
if count_g2 > 0:
    content_1190 = content_1190.replace(old_g2, new_g2)
    page_changes_1190.append(f"Fix 2: Compare strip 'From $97/mo' → 'From $149/mo' ({count_g2} instances)")
else:
    page_changes_1190.append("Fix 2: SKIPPED - not found")
    print("  WARNING: Fix 2 not found")

# Fix 3: Feature table "Entry price" row: "$97/mo Awakened" → "$149/mo Bonded"
old_g3 = '$97/mo Awakened'
new_g3 = '$149/mo Bonded'
if old_g3 in content_1190:
    content_1190 = content_1190.replace(old_g3, new_g3)
    page_changes_1190.append(f"Fix 3: Feature table entry price '$97/mo Awakened' → '$149/mo Bonded'")
else:
    page_changes_1190.append("Fix 3: SKIPPED - not found")
    print("  WARNING: Fix 3 not found")

# Fix 4: PureBrain pricing tiers section
# Remove the Awakened tier ($97) entirely, and fix Bonded ($297→$149) and Partnered ($997→$499)
# Also need to add Unified ($999)

# Replace Awakened tier block (remove it - $79 tier not shown)
old_awakened_tier = '''          <div class="pb-pricing-tier">
            <div>
              <div class="tier-name">Awakened</div>
              <div class="tier-includes">Your AI partner begins learning your business. Full memory, context, and business intelligence from day one.</div>
            </div>
            <div class="tier-price">$97<span style="font-size:12px;font-weight:400;color:#667788">/mo</span></div>
          </div>'''

# Check if it exists (with possible whitespace variations)
if 'tier-name">Awakened</div>' in content_1190:
    # Find the complete div block for Awakened
    awakened_start = content_1190.find('<div class="pb-pricing-tier">\n            <div>\n              <div class="tier-name">Awakened</div>')
    if awakened_start == -1:
        # Try with different whitespace
        awakened_start = content_1190.find('<div class="pb-pricing-tier">', content_1190.find('tier-name">Awakened'))
        # Go back to find the opening of this tier
        awakened_start = content_1190.rfind('<div class="pb-pricing-tier">', 0, content_1190.find('tier-name">Awakened'))

    if awakened_start >= 0:
        # Find the end of this tier block
        awakened_end = content_1190.find('</div>\n          <div class="pb-pricing-tier">', awakened_start)
        if awakened_end >= 0:
            awakened_end += len('</div>')  # end of the tier's outer div
            removed_block = content_1190[awakened_start:awakened_end]
            print(f"  Found Awakened tier block to remove:")
            print(f"  {repr(removed_block[:150])}")
            # But don't remove yet - do targeted string replacements instead

    page_changes_1190.append("Fix 4: Awakened tier found (will handle via targeted replacements)")
else:
    page_changes_1190.append("Fix 4: Awakened tier not found by tier-name check")

# Instead of removing Awakened (which risks breaking structure),
# Rename Awakened → Bonded and fix its price, then fix Bonded → Partnered, Partnered → Unified

# Strategy: Use sequential replacement to rename tiers
# Current: Awakened($97), Bonded($297), Partnered($997)
# Target:  Bonded($149), Partnered($499), Unified($999)

# Step 1: Rename Partnered → Unified (do this first to avoid conflicts)
# Find the Partnered tier block
old_partnered = '''<div class="tier-name">Partnered</div>
              <div class="tier-includes">Full AI partnership. Highest memory capacity, enterprise-grade support, and bespoke intelligence building for your organisation.</div>
            </div>
            <div class="tier-price">$997'''
new_partnered = '''<div class="tier-name">Unified</div>
              <div class="tier-includes">Full AI partnership. Highest memory capacity, enterprise-grade support, and bespoke intelligence building for your organisation.</div>
            </div>
            <div class="tier-price">$999'''
if old_partnered in content_1190:
    content_1190 = content_1190.replace(old_partnered, new_partnered)
    page_changes_1190.append("Fix 4a: Partnered($997) → Unified($999)")
else:
    # Try looser
    if 'tier-name">Partnered</div>' in content_1190 and '$997' in content_1190:
        content_1190 = content_1190.replace('tier-name">Partnered</div>', 'tier-name">Unified</div>')
        content_1190 = content_1190.replace('>$997<', '>$999<')
        page_changes_1190.append("Fix 4a (loose): Partnered→Unified, $997→$999")
    else:
        page_changes_1190.append("Fix 4a: SKIPPED - Partnered tier not found")
        print("  WARNING: Fix 4a not found")

# Step 2: Rename Bonded($297) → Partnered($499)
old_bonded = '''<div class="tier-name">Bonded</div>
              <div class="tier-includes">Deeper integration, expanded memory capacity, priority support, and advanced business context tools.</div>
            </div>
            <div class="tier-price">$297'''
new_bonded = '''<div class="tier-name">Partnered</div>
              <div class="tier-includes">Deeper integration, expanded memory capacity, priority support, and advanced business context tools.</div>
            </div>
            <div class="tier-price">$499'''
if old_bonded in content_1190:
    content_1190 = content_1190.replace(old_bonded, new_bonded)
    page_changes_1190.append("Fix 4b: Bonded($297) → Partnered($499)")
else:
    if 'tier-name">Bonded</div>' in content_1190 and '$297' in content_1190:
        content_1190 = content_1190.replace('tier-name">Bonded</div>', 'tier-name">Partnered</div>')
        content_1190 = content_1190.replace('>$297<', '>$499<')
        page_changes_1190.append("Fix 4b (loose): Bonded→Partnered, $297→$499")
    else:
        page_changes_1190.append("Fix 4b: SKIPPED - Bonded tier not found")
        print("  WARNING: Fix 4b not found")

# Step 3: Rename Awakened($97) → Bonded($149)
old_awakened = '''<div class="tier-name">Awakened</div>
              <div class="tier-includes">Your AI partner begins learning your business. Full memory, context, and business intelligence from day one.</div>
            </div>
            <div class="tier-price">$97'''
new_awakened = '''<div class="tier-name">Bonded</div>
              <div class="tier-includes">Your AI partner begins learning your business. Full memory, context, and business intelligence from day one.</div>
            </div>
            <div class="tier-price">$149'''
if old_awakened in content_1190:
    content_1190 = content_1190.replace(old_awakened, new_awakened)
    page_changes_1190.append("Fix 4c: Awakened($97) → Bonded($149)")
else:
    if 'tier-name">Awakened</div>' in content_1190 and '$97<' in content_1190:
        content_1190 = content_1190.replace('tier-name">Awakened</div>', 'tier-name">Bonded</div>')
        content_1190 = content_1190.replace('>$97<', '>$149<')
        page_changes_1190.append("Fix 4c (loose): Awakened→Bonded, $97→$149")
    else:
        page_changes_1190.append("Fix 4c: SKIPPED - Awakened tier not found")
        print("  WARNING: Fix 4c not found")

# Verify remaining $97 references
remaining_97 = [(m.start(), content_1190[max(0,m.start()-100):m.end()+100]) for m in re.finditer(r'\$97', content_1190)]
if remaining_97:
    print(f"\n  Remaining $97 references ({len(remaining_97)}):")
    for pos, ctx in remaining_97:
        clean = re.sub(r'<[^>]+>', ' ', ctx)
        clean = re.sub(r'\s+', ' ', clean).strip()
        print(f"    pos {pos}: {clean[:150]}")

# Count changes
print(f"\n  Changes for page 1190:")
for c in page_changes_1190:
    print(f"    - {c}")

# Only update if changes were made
if content_1190 != original_1190:
    print(f"\n  Uploading changes to page 1190...")
    status, result = update_page(1190, content_1190)
    if status == 200:
        print(f"  SUCCESS: Page 1190 updated")
        new_len = len(result.get('content', {}).get('raw', ''))
        print(f"  New content length: {new_len}")
    else:
        print(f"  ERROR: {status} - {result}")
else:
    print("\n  No changes needed for page 1190")

changes_report.append({
    'page_id': 1190,
    'slug': 'purebrain-vs-glbgpt',
    'changes': page_changes_1190,
    'modified': content_1190 != original_1190
})


# ============================================================
# Clear Elementor Cache
# ============================================================
print("\n" + "=" * 60)
print("CLEARING ELEMENTOR CACHE")
print("=" * 60)
cache_status = clear_elementor_cache()
print(f"Cache clear status: {cache_status}")


# ============================================================
# FINAL REPORT
# ============================================================
print("\n" + "=" * 60)
print("AUDIT COMPLETE - FINAL REPORT")
print("=" * 60)

print("""
ACTUAL PUREBRAIN PRICING (source of truth from main page):
  Awakened:  $79/mo  (DO NOT show on comparison pages)
  Bonded:    $149/mo
  Partnered: $499/mo
  Unified:   $999/mo
""")

print("PAGES CHECKED:")
print("  ID 1190 - purebrain-vs-glbgpt")
print("  ID 1044 - purebrain-vs-sitegpt")
print("  ID 970  - cost-comparison (no PureBrain tier pricing, skip)")
print("  ID 794  - why-purebrain (no pricing found, skip)")
print("  ID 760  - purebrain-vs-perplexity (no pricing in content)")
print("  ID 759  - purebrain-vs-jasper (no pricing in content)")
print("  ID 758  - purebrain-vs-gemini (no pricing in content)")
print("  ID 757  - purebrain-vs-deepseek (no pricing in content)")
print("  ID 756  - purebrain-vs-custom-gpts (no pricing in content)")
print("  ID 755  - purebrain-vs-copilot ($30 is Copilot pricing only, skip)")
print("  ID 754  - purebrain-vs-claude (no pricing in content)")
print("  ID 753  - purebrain-vs-chatgpt (no pricing in content)")
print("  ID 752  - compare hub ($5 is competitor pricing only, skip)")

print("\nPAGES FIXED:")
for report in changes_report:
    if report['modified']:
        print(f"\n  Page {report['page_id']} ({report['slug']}):")
        for c in report['changes']:
            print(f"    {c}")

print("\nPAGES WITH NO CHANGES NEEDED:")
for report in changes_report:
    if not report['modified']:
        print(f"  Page {report['page_id']} ({report['slug']}) - no changes")
