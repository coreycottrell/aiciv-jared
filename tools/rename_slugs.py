#!/usr/bin/env python3
"""
Safe slug rename script.
Replaces exact old slugs with new slugs in HTML files.
Uses word-boundary matching to avoid partial matches.

Mappings:
  pay-test-2        -> live
  pay-test-awakened -> awakened
  pay-test-partnered -> partnered
  pay-test-unified  -> unified
"""

import re
import os
import sys
from pathlib import Path

# Order matters: longer/more-specific strings first to avoid partial matches
REPLACEMENTS = [
    # pay-test-2 -> live
    # Must NOT match pay-test-2x, pay-test-25, etc.
    # Match only when followed by non-alphanumeric or end of string
    (r'pay-test-2(?![\w-])', 'live'),

    # pay-test-awakened -> awakened
    (r'pay-test-awakened', 'awakened'),

    # pay-test-partnered -> partnered
    (r'pay-test-partnered', 'partnered'),

    # pay-test-unified -> unified
    (r'pay-test-unified', 'unified'),
]


def replace_in_file(filepath: Path, dry_run: bool = False) -> tuple[int, list[str]]:
    """Replace old slugs in a file. Returns (change_count, list_of_changes)."""
    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception as e:
        print(f"  ERROR reading {filepath}: {e}")
        return 0, []

    original = content
    changes = []

    for pattern, replacement in REPLACEMENTS:
        matches = re.findall(pattern, content)
        if matches:
            new_content = re.sub(pattern, replacement, content)
            count = len(matches)
            changes.append(f"    {matches[0]} -> {replacement} ({count} occurrences)")
            content = new_content

    if content != original:
        if not dry_run:
            filepath.write_text(content, encoding='utf-8')
        return len(changes), changes

    return 0, []


def process_directory(directory: Path, dry_run: bool = False) -> dict:
    """Process all HTML files in a directory recursively."""
    results = {
        'files_changed': 0,
        'files_scanned': 0,
        'total_changes': 0,
        'details': []
    }

    html_files = list(directory.rglob('*.html'))
    results['files_scanned'] = len(html_files)

    for filepath in sorted(html_files):
        count, changes = replace_in_file(filepath, dry_run=dry_run)
        if count > 0:
            results['files_changed'] += 1
            results['total_changes'] += count
            rel_path = filepath.relative_to(directory.parent.parent.parent) if directory.parent.parent.parent.exists() else filepath
            results['details'].append({
                'file': str(filepath),
                'changes': changes
            })

    return results


def main():
    dry_run = '--dry-run' in sys.argv

    base_cf = Path('/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy')
    base_pb = Path('/home/jared/projects/AI-CIV/aether/purebrain-site/public')

    if dry_run:
        print("DRY RUN MODE - no files will be modified\n")

    print("=" * 60)
    print(f"Processing: {base_cf}")
    print("=" * 60)
    results_cf = process_directory(base_cf, dry_run=dry_run)

    print(f"Scanned: {results_cf['files_scanned']} HTML files")
    print(f"Changed: {results_cf['files_changed']} files")
    print(f"Total replacements: {results_cf['total_changes']}")
    print()
    for detail in results_cf['details']:
        print(f"  {detail['file']}")
        for change in detail['changes']:
            print(change)
    print()

    print("=" * 60)
    print(f"Processing: {base_pb}")
    print("=" * 60)
    results_pb = process_directory(base_pb, dry_run=dry_run)

    print(f"Scanned: {results_pb['files_scanned']} HTML files")
    print(f"Changed: {results_pb['files_changed']} files")
    print(f"Total replacements: {results_pb['total_changes']}")
    print()
    for detail in results_pb['details']:
        print(f"  {detail['file']}")
        for change in detail['changes']:
            print(change)

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    total_files = results_cf['files_changed'] + results_pb['files_changed']
    total_changes = results_cf['total_changes'] + results_pb['total_changes']
    print(f"Total files changed: {total_files}")
    print(f"Total slug replacements: {total_changes}")
    if dry_run:
        print("\nDRY RUN - run without --dry-run to apply changes")


if __name__ == '__main__':
    main()
