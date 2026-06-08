#!/usr/bin/env python3
"""
Aether Anti-Drift Config Validator and Infrastructure Setup

Reads tools/antidrift-config.yaml, validates its shape, creates .antidrift/ directory.
NO runtime wiring into boop_executor yet (that's phased).

Usage:
    python3 tools/antidrift_parameterize.py

Returns:
    Exit 0 on PASS, Exit 1 on FAIL
"""

import sys
import yaml
import json
from pathlib import Path
from datetime import datetime, timezone

# Repo root
REPO_ROOT = Path(__file__).parent.parent
CONFIG_PATH = REPO_ROOT / "tools" / "antidrift-config.yaml"
ANTIDRIFT_DIR = REPO_ROOT / ".antidrift"
MARKERS_DIR = ANTIDRIFT_DIR / "markers"
STREAK_FILE = ANTIDRIFT_DIR / "clean-session-streak.json"


def validate_config(config):
    """Validate config shape. Returns (bool, list_of_errors)."""
    errors = []

    # Check required top-level keys
    required_keys = ["schema", "generated_at", "identity_cards", "grounding_docs",
                     "inboxes", "safeguards", "banned_phrases", "streak", "timing"]
    for key in required_keys:
        if key not in config:
            errors.append(f"Missing required key: {key}")

    # Check identity_cards count
    if "identity_cards" in config:
        cards = config["identity_cards"]
        if not isinstance(cards, list):
            errors.append("identity_cards must be a list")
        elif len(cards) != 7:
            errors.append(f"Expected 7 identity cards, got {len(cards)}")
        else:
            # Validate each card has required fields
            for i, card in enumerate(cards):
                required_card_keys = ["id", "label", "anchor_phrase", "drift_opposite"]
                for key in required_card_keys:
                    if key not in card:
                        errors.append(f"Identity card {i} missing key: {key}")

    # Check banned_phrases count
    if "banned_phrases" in config:
        phrases = config["banned_phrases"]
        if not isinstance(phrases, list):
            errors.append("banned_phrases must be a list")
        elif len(phrases) != 18:
            errors.append(f"Expected 18 banned phrases, got {len(phrases)}")

    # Check grounding_docs count
    if "grounding_docs" in config:
        docs = config["grounding_docs"]
        if not isinstance(docs, list):
            errors.append("grounding_docs must be a list")
        elif len(docs) != 2:
            errors.append(f"Expected 2 grounding docs, got {len(docs)}")

    # Check inboxes count
    if "inboxes" in config:
        inboxes = config["inboxes"]
        if not isinstance(inboxes, list):
            errors.append("inboxes must be a list")
        elif len(inboxes) != 2:
            errors.append(f"Expected 2 inboxes, got {len(inboxes)}")

    # Check safeguards count
    if "safeguards" in config:
        safeguards = config["safeguards"]
        if not isinstance(safeguards, list):
            errors.append("safeguards must be a list")
        elif len(safeguards) != 2:
            errors.append(f"Expected 2 safeguards, got {len(safeguards)}")

    return (len(errors) == 0, errors)


def create_infrastructure():
    """Create .antidrift/ directory structure if missing."""
    ANTIDRIFT_DIR.mkdir(exist_ok=True)
    MARKERS_DIR.mkdir(exist_ok=True)

    # Initialize streak counter if missing
    if not STREAK_FILE.exists():
        initial_streak = {
            "streak": 0,
            "last_clean": None,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        with open(STREAK_FILE, 'w') as f:
            json.dump(initial_streak, f, indent=2)
        print(f"✓ Created initial streak counter: {STREAK_FILE}")
    else:
        print(f"✓ Streak counter already exists: {STREAK_FILE}")


def main():
    print("=" * 60)
    print("Aether Anti-Drift Config Validator")
    print("=" * 60)

    # Check config file exists
    if not CONFIG_PATH.exists():
        print(f"✗ FAIL: Config file not found: {CONFIG_PATH}")
        return 1

    print(f"✓ Config file found: {CONFIG_PATH}")

    # Load YAML
    try:
        with open(CONFIG_PATH) as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"✗ FAIL: Could not parse YAML: {e}")
        return 1

    print(f"✓ YAML parsed successfully")

    # Validate config shape
    is_valid, errors = validate_config(config)

    if not is_valid:
        print("\n✗ FAIL: Config validation errors:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("✓ Config validation PASS")
    print(f"  - 7 identity cards present")
    print(f"  - 18 banned phrases present")
    print(f"  - 2 grounding docs configured")
    print(f"  - 2 inboxes configured")
    print(f"  - 2 safeguards configured")

    # Create infrastructure
    print("\nCreating .antidrift/ infrastructure...")
    try:
        create_infrastructure()
    except Exception as e:
        print(f"✗ FAIL: Could not create infrastructure: {e}")
        return 1

    print(f"\n✓ Infrastructure created:")
    print(f"  - {ANTIDRIFT_DIR}")
    print(f"  - {MARKERS_DIR}")
    print(f"  - {STREAK_FILE}")

    print("\n" + "=" * 60)
    print("VALIDATION PASS ✓")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Review .antidrift/clean-session-streak.json")
    print("  2. Enable stamp in postcompact-identity-reground.sh (AETHER_ANTIDRIFT_STAMP=1)")
    print("  3. Implement antidrift_stamp_marker.py (Phase 1)")
    print("  4. Implement antidrift_verify_startup.py (Phase 2)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
