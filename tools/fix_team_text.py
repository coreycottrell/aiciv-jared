#!/usr/bin/env python3
"""Fix Team link text to say Our Team"""

import os
import re
from pathlib import Path

def should_skip(filepath):
    """Check if file should be skipped"""
    path_str = str(filepath)
    if '_archived' in path_str or '.bak' in path_str:
        return True
    if filepath.name == 'index.html' and filepath.parent.name == 'cf-pages-deploy':
        return True
    return False

def fix_html_file(filepath):
    """Fix the Team text to Our Team"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Pattern: <a href="https://purebrain.ai/our-team/" ... >Team</a>
        # Replace with: Our Team
        pattern = r'(<a href="https://purebrain\.ai/our-team/"[^>]*>)Team(</a>)'
        replacement = r'\1Our Team\2'

        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True

        return False

    except Exception as e:
        print(f"ERROR processing {filepath}: {e}")
        return False

def main():
    base_dir = Path('/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy')
    html_files = list(base_dir.rglob('*.html'))

    print(f"Found {len(html_files)} HTML files")
    print(f"Fixing link text...\n")

    modified_count = 0
    skipped_count = 0

    for filepath in sorted(html_files):
        if should_skip(filepath):
            skipped_count += 1
            continue

        if fix_html_file(filepath):
            modified_count += 1
            rel_path = filepath.relative_to(base_dir)
            print(f"✓ {rel_path}")

    print(f"\n{'='*60}")
    print(f"SUMMARY:")
    print(f"  Files modified: {modified_count}")
    print(f"  Files skipped: {skipped_count}")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
