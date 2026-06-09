#!/usr/bin/env python3
"""
Aether Anti-Drift Verify Startup Script
Checks identity grounding health after compaction/restart.
Flag-gated: only runs if AETHER_ANTIDRIFT_VERIFY=1
"""
import os
import sys
import argparse
from pathlib import Path
import yaml
import json

# Flag-gate at module level
ENABLED = os.environ.get('AETHER_ANTIDRIFT_VERIFY', '0') == '1'

def main():
    if not ENABLED:
        print("Anti-drift verify: inactive (AETHER_ANTIDRIFT_VERIFY not set)")
        sys.exit(0)

    parser = argparse.ArgumentParser(description='Verify Aether identity grounding')
    parser.add_argument('--scan', metavar='FILE', help='Scan text file for banned phrases')
    args = parser.parse_args()

    # Load config
    config_path = Path('/home/jared/projects/AI-CIV/aether/tools/antidrift-config.yaml')
    if not config_path.exists():
        print("ERROR: antidrift-config.yaml not found")
        sys.exit(1)

    with open(config_path) as f:
        config = yaml.safe_load(f)

    exit_code = 0
    results = []

    # ====== CHECK 1: Identity Cards Present ======
    identity_cards_path = Path('/home/jared/projects/AI-CIV/aether/.claude/identity-cards.md')
    if not identity_cards_path.exists():
        results.append("FAIL: identity-cards.md not found")
        exit_code = 1
    else:
        content = identity_cards_path.read_text()
        missing_markers = []
        for card in config['identity_cards']:
            marker = card['id']
            if marker not in content:
                missing_markers.append(marker)

        if missing_markers:
            results.append(f"FAIL: identity-cards.md missing markers: {', '.join(missing_markers)}")
            exit_code = 1
        else:
            results.append(f"PASS: identity-cards.md contains all 7 markers (IC1-IC7)")

    # ====== CHECK 2: Banned Phrase Scan ======
    if args.scan:
        scan_path = Path(args.scan)
        if not scan_path.exists():
            results.append(f"WARN: scan file not found: {args.scan}")
        else:
            banned_phrases = config['banned_phrases']
            content = scan_path.read_text()
            lines = content.split('\n')

            hits = []
            for i, line in enumerate(lines, 1):
                for phrase in banned_phrases:
                    if phrase.lower() in line.lower():
                        hits.append(f"  Line {i}: '{phrase}' in: {line.strip()[:80]}")

            if hits:
                results.append(f"WARN: banned phrases detected in {args.scan}:")
                results.extend(hits)
            else:
                results.append(f"PASS: no banned phrases in {args.scan}")
    else:
        results.append("INFO: no --scan file provided, skipping banned phrase check")

    # ====== CHECK 3: Grounding Docs Present ======
    for doc in config['grounding_docs']:
        doc_path = Path(doc['path'])
        if not doc_path.exists():
            results.append(f"FAIL: grounding doc missing: {doc['label']} at {doc['path']}")
            exit_code = 1
        else:
            results.append(f"PASS: grounding doc present: {doc['label']}")

    # ====== CHECK 4: Safeguards Intact ======
    for safeguard in config['safeguards']:
        target_path = Path(safeguard['grep_target'])
        if not target_path.exists():
            results.append(f"WARN: safeguard target missing: {safeguard['label']}")
            continue

        content = target_path.read_text()
        must_contain = safeguard.get('must_contain')
        must_not_contain = safeguard.get('must_not_contain')

        if must_contain and must_contain not in content:
            results.append(f"WARN: safeguard '{safeguard['label']}' missing required text: {must_contain}")
        elif must_not_contain and must_not_contain in content:
            results.append(f"WARN: safeguard '{safeguard['label']}' contains banned text: {must_not_contain}")
        else:
            results.append(f"PASS: safeguard intact: {safeguard['label']}")

    # ====== CHECK 5: Burn-in Status ======
    streak_path = Path(config['streak']['counter_path'])
    if not streak_path.exists():
        results.append("INFO: burn-in not started (no streak file)")
    else:
        with open(streak_path) as f:
            streak_data = json.load(f)
        clean_streak = streak_data.get('clean_streak', 0)
        target = streak_data.get('target', 5)
        results.append(f"INFO: burn-in status: {clean_streak}/{target} clean sessions")

    # ====== OUTPUT ======
    print("\n=== AETHER ANTI-DRIFT VERIFICATION ===")
    for result in results:
        print(result)
    print(f"\nExit code: {exit_code}")

    sys.exit(exit_code)

if __name__ == '__main__':
    main()
