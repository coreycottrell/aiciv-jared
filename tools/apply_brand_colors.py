#!/usr/bin/env python3
"""
Apply PureBrain brand colors across all 7 CF Pages.

Brand rule:
  PureBr = #2a93c1 (PT Blue)
  ai     = #f1420b (PT Orange)
  n      = #2a93c1 (PT Blue)

Applies to: Watch heading, footer, and visible PureBrain text in headings/descriptions/CTAs.
"""

import re

FILES = [
    "/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/index.html",
    "/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/pay-test-sandbox-3/index.html",
    "/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/pay-test-2/index.html",
    "/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/pay-test-awakened/index.html",
    "/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/pay-test-partnered/index.html",
    "/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/pay-test-unified/index.html",
    "/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/insiders/index.html",
]

# The branded span markup (lowercase mixed case per task spec)
BRANDED_PUREBRAIN = '<span style="color:#2a93c1">PureBr</span><span style="color:#f1420b">ai</span><span style="color:#2a93c1">n</span>'

# The old uppercase branded markup (already in the files)
OLD_BRANDED_UPPER = '<span style="color:#2a93c1">PUREBR</span><span style="color:#f1420b">AI</span><span style="color:#2a93c1">N</span>'

# Footer PureBrain.ai link text - old and new
OLD_FOOTER_LINK = '>PureBrain.ai</a>'
NEW_FOOTER_LINK = f'>{BRANDED_PUREBRAIN}.ai</a>'

def apply_brands(content):
    changes = []

    # 1. Fix the "Watch PUREBR/AI/N Come Alive" heading (uppercase -> mixed case)
    old_heading = f'Watch {OLD_BRANDED_UPPER} Come Alive'
    new_heading = f'Watch {BRANDED_PUREBRAIN} Come Alive'
    if old_heading in content:
        count = content.count(old_heading)
        content = content.replace(old_heading, new_heading)
        changes.append(f"  [HEADING] Watch...Come Alive: {count} instance(s) updated (uppercase -> mixed case)")
    elif new_heading in content:
        changes.append(f"  [HEADING] Watch...Come Alive: already correct mixed case")
    else:
        # Try plain text fallback
        if 'Watch PureBrain Come Alive' in content:
            content = content.replace('Watch PureBrain Come Alive', new_heading)
            changes.append(f"  [HEADING] Watch...Come Alive: plain text -> branded")

    # 2. Fix footer "PureBrain.ai" link text
    # Only replace within the anchor tag text, not in href= attributes
    # Pattern: class="pb-footer-purebrain">PureBrain.ai</a>
    old_footer = 'class="pb-footer-purebrain">PureBrain.ai</a>'
    new_footer = f'class="pb-footer-purebrain">{BRANDED_PUREBRAIN}.ai</a>'
    if old_footer in content:
        count = content.count(old_footer)
        content = content.replace(old_footer, new_footer)
        changes.append(f"  [FOOTER] PureBrain.ai link: {count} instance(s) updated")
    elif new_footer in content:
        changes.append(f"  [FOOTER] PureBrain.ai link: already branded")

    # 3. Fix "Compare PureBrain" text (the visible pill label, not the comment)
    # Only the actual visible text in HTML elements, not CSS comments
    old_compare = '>Compare PureBrain<'
    new_compare = f'>Compare {BRANDED_PUREBRAIN}<'
    if old_compare in content:
        count = content.count(old_compare)
        content = content.replace(old_compare, new_compare)
        changes.append(f"  [COMPARE] Compare PureBrain label: {count} instance(s) updated")
    else:
        changes.append(f"  [COMPARE] Compare PureBrain: no bare visible text found (likely in comment/CSS only)")

    # 4. Fix "See Why PureBrain Is Different" CTA text
    old_cta = '>See Why PureBrain Is Different'
    new_cta = f'>See Why {BRANDED_PUREBRAIN} Is Different'
    if old_cta in content:
        count = content.count(old_cta)
        content = content.replace(old_cta, new_cta)
        changes.append(f"  [CTA] See Why PureBrain Is Different: {count} instance(s) updated")
    else:
        changes.append(f"  [CTA] See Why PureBrain Is Different: already branded or not found")

    # 5. Fix "Understand what sets PureBrain apart" description text
    old_desc = 'Understand what sets PureBrain apart'
    new_desc = f'Understand what sets {BRANDED_PUREBRAIN} apart'
    if old_desc in content:
        count = content.count(old_desc)
        content = content.replace(old_desc, new_desc)
        changes.append(f"  [DESC] Understand what sets PureBrain apart: {count} instance(s) updated")
    else:
        changes.append(f"  [DESC] sets PureBrain apart: not found or already branded")

    # 6. Fix "PureBrain saves you every month" description
    old_saves = 'PureBrain saves you every month'
    new_saves = f'{BRANDED_PUREBRAIN} saves you every month'
    if old_saves in content:
        count = content.count(old_saves)
        content = content.replace(old_saves, new_saves)
        changes.append(f"  [DESC] PureBrain saves you every month: {count} instance(s) updated")
    else:
        changes.append(f"  [DESC] PureBrain saves you: not found or already branded")

    return content, changes


def main():
    for filepath in FILES:
        print(f"\nProcessing: {filepath}")
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original_len = len(content)
        new_content, changes = apply_brands(content)

        for change in changes:
            print(change)

        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"  SAVED ({original_len} -> {len(new_content)} bytes)")
        else:
            print(f"  No changes needed")

    print("\nDone. All 7 files processed.")


if __name__ == "__main__":
    main()
