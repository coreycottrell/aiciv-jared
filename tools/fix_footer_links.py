#!/usr/bin/env python3
"""
Fix footer links across CF Pages HTML files:
1. Change Team link in real footer to Our Team with correct URL
2. Remove incorrect Our Team link from Aether bottom bar
"""

import os
import re
from pathlib import Path

def should_skip(filepath):
    """Check if file should be skipped"""
    path_str = str(filepath)

    # Skip archived and backup files
    if '_archived' in path_str or '.bak' in path_str:
        return True

    # Skip root index.html (already fixed)
    if filepath.name == 'index.html' and filepath.parent.name == 'cf-pages-deploy':
        return True

    return False

def fix_html_file(filepath):
    """Apply both fixes to a single HTML file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        changes_made = []

        # FIX 1: Change Team link in real footer to Our Team
        # Pattern: href="https://puretechnology.ai/#team"
        fix1_pattern = r'href="https://puretechnology\.ai/#team"'
        fix1_replacement = 'href="https://purebrain.ai/our-team/"'

        if re.search(fix1_pattern, content):
            content = re.sub(fix1_pattern, fix1_replacement, content)

            # Also change link text from "Team" to "Our Team"
            # Pattern: <a href="https://purebrain.ai/our-team/" ... >Team</a>
            content = re.sub(
                r'(<a href="https://purebrain\.ai/our-team/"[^>]*>)Team(</a>)',
                r'\1Our Team\2',
                content
            )
            changes_made.append("Fix 1: Updated Team link to Our Team")

        # FIX 2: Remove incorrect Our Team link from Aether bottom bar
        # This appears as: <span class="pb-footer-sep">|</span><a href="https://purebrain.ai/our-team/" rel="noopener" class="pb-footer-blue">Our Team</a>
        fix2_pattern = r'<span class="pb-footer-sep">\|</span><a href="https://purebrain\.ai/our-team/" rel="noopener" class="pb-footer-blue">Our Team</a>'

        if re.search(fix2_pattern, content):
            content = re.sub(fix2_pattern, '', content)
            changes_made.append("Fix 2: Removed incorrect Aether bar link")

        # Write back if changes were made
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, changes_made

        return False, []

    except Exception as e:
        print(f"ERROR processing {filepath}: {e}")
        return False, []

def main():
    """Process all HTML files in cf-pages-deploy directory"""
    base_dir = Path('/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy')

    if not base_dir.exists():
        print(f"ERROR: Directory not found: {base_dir}")
        return

    # Find all HTML files recursively
    html_files = list(base_dir.rglob('*.html'))

    print(f"Found {len(html_files)} HTML files")
    print(f"Scanning and applying fixes...\n")

    modified_count = 0
    skipped_count = 0

    for filepath in sorted(html_files):
        if should_skip(filepath):
            skipped_count += 1
            continue

        was_modified, changes = fix_html_file(filepath)

        if was_modified:
            modified_count += 1
            rel_path = filepath.relative_to(base_dir)
            print(f"✓ {rel_path}")
            for change in changes:
                print(f"  - {change}")

    print(f"\n{'='*60}")
    print(f"SUMMARY:")
    print(f"  Total HTML files found: {len(html_files)}")
    print(f"  Files modified: {modified_count}")
    print(f"  Files skipped: {skipped_count}")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
