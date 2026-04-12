#!/usr/bin/env python3
"""
PureBrain Migration Portal — Brevo Attribute Setup Script

Creates the Brevo contact attributes and competitor drip lists needed by the
AI Migration Portal (migration-brevo-integration.js).

Creates attributes:
  - COMPETITOR           (text)
  - PRIMARY_USE_CASES    (text)
  - USAGE_FREQUENCY      (text)
  - HAD_CUSTOM_CONFIG    (boolean)
  - MAIN_FRUSTRATION     (text)
  - MIGRATION_STATUS     (text: not_started | in_progress | complete)
  - MIGRATION_PROFILE    (text — JSON string of full profile)
  - CONVERSATION_COUNT   (number)
  - TOP_TOPICS           (text)
  - TAGS                 (text — comma-separated tag list)

Creates competitor drip lists:
  - PureBrain Migration — ChatGPT
  - PureBrain Migration — Claude
  - PureBrain Migration — Gemini
  - PureBrain Migration — Perplexity
  - PureBrain Migration — Midjourney
  - PureBrain Migration — Copilot
  - PureBrain Migration — Other

Creates a migration leads list:
  - PureBrain Migration Leads (general — all migration intent contacts)

Saves list IDs to: config/migration_brevo_config.json

Usage:
    source .env && python3 tools/setup_brevo_migration_attributes.py
    python3 tools/setup_brevo_migration_attributes.py --dry-run

Author: full-stack-developer
Date: 2026-02-23
Spec: docs/from-telegram/ai-migration-portal-spec.md (Sections 2, 5)
"""

import argparse
import json
import os
import sys
import time

import requests
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(_PROJECT_ROOT, '.env'))

BREVO_API_KEY = os.getenv('BREVO_API_KEY', '')
BREVO_BASE_URL = 'https://api.brevo.com/v3'
RESULTS_FILE = os.path.join(_PROJECT_ROOT, 'config', 'migration_brevo_config.json')

# ---------------------------------------------------------------------------
# Attributes to create
# ---------------------------------------------------------------------------

MIGRATION_ATTRIBUTES = [
    # (attribute_name, brevo_type, description)
    ('COMPETITOR',         'text',    'Competitor the user is migrating FROM (e.g. chatgpt, claude, gemini)'),
    ('PRIMARY_USE_CASES',  'text',    'Comma-separated use cases from Exodus quiz (e.g. writing,research,coding)'),
    ('USAGE_FREQUENCY',    'text',    'How often they used the competitor tool (multiple_times_daily, once_a_day, etc.)'),
    ('HAD_CUSTOM_CONFIG',  'boolean', 'True if they had custom instructions/templates configured'),
    ('MAIN_FRUSTRATION',   'text',    'Single frustration that drove the switch (e.g. no_memory, too_generic)'),
    ('MIGRATION_STATUS',   'text',    'Current migration state: not_started | in_progress | complete'),
    ('MIGRATION_PROFILE',  'text',    'Full JSON profile from portal analysis (topics, style, count, date range)'),
    ('CONVERSATION_COUNT', 'number',  'Total conversations imported from previous AI tool'),
    ('TOP_TOPICS',         'text',    'Comma-separated top 5 topics extracted from conversation history'),
    ('TAGS',               'text',    'Comma-separated tag list (e.g. migration-intent,from-chatgpt)'),
]

# ---------------------------------------------------------------------------
# Competitor drip lists to create
# ---------------------------------------------------------------------------

MIGRATION_LISTS = [
    # (list_name, description, env_var_key)
    (
        'PureBrain Migration Leads',
        'All migration intent contacts — general pool regardless of competitor',
        'MIGRATION_LEADS',
    ),
    (
        'PureBrain Migration — ChatGPT',
        'Migration drip for users switching from ChatGPT/OpenAI. Trigger: Contact added to this list.',
        'CHATGPT',
    ),
    (
        'PureBrain Migration — Claude',
        'Migration drip for users switching from Claude/Anthropic. Trigger: Contact added to this list.',
        'CLAUDE',
    ),
    (
        'PureBrain Migration — Gemini',
        'Migration drip for users switching from Gemini/Google. Trigger: Contact added to this list.',
        'GEMINI',
    ),
    (
        'PureBrain Migration — Perplexity',
        'Migration drip for users switching from Perplexity. Trigger: Contact added to this list.',
        'PERPLEXITY',
    ),
    (
        'PureBrain Migration — Midjourney',
        'Migration drip for users switching from Midjourney. Trigger: Contact added to this list.',
        'MIDJOURNEY',
    ),
    (
        'PureBrain Migration — Copilot',
        'Migration drip for users switching from Microsoft Copilot. Trigger: Contact added to this list.',
        'COPILOT',
    ),
    (
        'PureBrain Migration — Other',
        'Migration drip for users switching from other/unknown tools. Trigger: Contact added to this list.',
        'UNKNOWN',
    ),
]

# ---------------------------------------------------------------------------
# Brevo helpers
# ---------------------------------------------------------------------------

def brevo_headers() -> dict:
    return {
        'api-key': BREVO_API_KEY,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }


def get_existing_attributes() -> list:
    """Fetch all existing Brevo contact attributes."""
    resp = requests.get(
        f'{BREVO_BASE_URL}/contacts/attributes',
        headers=brevo_headers(),
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json().get('attributes', [])


def get_existing_lists() -> list:
    """Fetch all existing Brevo contact lists."""
    resp = requests.get(
        f'{BREVO_BASE_URL}/contacts/lists',
        headers=brevo_headers(),
        params={'limit': 50, 'offset': 0},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json().get('lists', [])


# ---------------------------------------------------------------------------
# Attribute creation
# ---------------------------------------------------------------------------

def create_attribute(attr_name: str, attr_type: str, existing_attrs: list, dry_run: bool) -> dict:
    """
    Create a Brevo contact attribute if it does not already exist.

    Brevo attribute types:
      text     → 'text'
      number   → 'float'
      boolean  → 'boolean'
      date     → 'date'
    """
    # Normalise type for Brevo API
    brevo_type_map = {
        'text': 'text',
        'number': 'float',
        'boolean': 'boolean',
        'date': 'date',
    }
    api_type = brevo_type_map.get(attr_type, 'text')

    existing_names = [a.get('name', '').upper() for a in existing_attrs]
    if attr_name.upper() in existing_names:
        print(f'  [SKIP]    Attribute {attr_name:25s} — already exists')
        return {'name': attr_name, 'type': attr_type, 'status': 'already_exists'}

    if dry_run:
        print(f'  [DRY-RUN] Would create attribute: {attr_name} ({attr_type})')
        return {'name': attr_name, 'type': attr_type, 'status': 'dry_run'}

    resp = requests.post(
        f'{BREVO_BASE_URL}/contacts/attributes/normal/{attr_name}',
        headers=brevo_headers(),
        json={'type': api_type},
        timeout=15,
    )

    if resp.status_code in (200, 201, 204):
        print(f'  [CREATED] Attribute {attr_name:25s} ({attr_type})')
        return {'name': attr_name, 'type': attr_type, 'status': 'created'}
    else:
        print(f'  [ERROR]   Attribute {attr_name:25s} → {resp.status_code}: {resp.text}')
        return {'name': attr_name, 'type': attr_type, 'status': 'error', 'error': resp.text}


def setup_attributes(dry_run: bool) -> list:
    """Create all migration attributes. Returns list of result dicts."""
    print('\n--- Contact Attributes ---')
    existing = get_existing_attributes()
    results = []
    for attr_name, attr_type, description in MIGRATION_ATTRIBUTES:
        result = create_attribute(attr_name, attr_type, existing, dry_run)
        result['description'] = description
        results.append(result)
        # Small delay to avoid rate limits
        if not dry_run:
            time.sleep(0.3)
    return results


# ---------------------------------------------------------------------------
# List creation
# ---------------------------------------------------------------------------

def create_migration_list(list_name: str, existing_lists: list, dry_run: bool) -> dict:
    """Create a Brevo contact list if it doesn't already exist."""
    existing_match = next((l for l in existing_lists if l.get('name') == list_name), None)
    if existing_match:
        list_id = existing_match['id']
        print(f'  [SKIP]    List "{list_name}" — already exists (ID={list_id})')
        return {'name': list_name, 'id': list_id, 'status': 'already_exists'}

    if dry_run:
        print(f'  [DRY-RUN] Would create list: "{list_name}"')
        return {'name': list_name, 'id': None, 'status': 'dry_run'}

    resp = requests.post(
        f'{BREVO_BASE_URL}/contacts/lists',
        headers=brevo_headers(),
        json={'name': list_name, 'folderId': 1},
        timeout=15,
    )
    if resp.status_code in (200, 201):
        list_id = resp.json().get('id')
        print(f'  [CREATED] List "{list_name}" → ID={list_id}')
        return {'name': list_name, 'id': list_id, 'status': 'created'}
    else:
        print(f'  [ERROR]   List "{list_name}" → {resp.status_code}: {resp.text}')
        return {'name': list_name, 'id': None, 'status': 'error', 'error': resp.text}


def setup_lists(dry_run: bool) -> dict:
    """Create all competitor drip lists. Returns dict of env_var_key → result."""
    print('\n--- Migration Drip Lists ---')
    existing = get_existing_lists()
    results = {}
    for list_name, description, env_key in MIGRATION_LISTS:
        result = create_migration_list(list_name, existing, dry_run)
        result['description'] = description
        results[env_key] = result
        if not dry_run:
            time.sleep(0.3)
    return results


# ---------------------------------------------------------------------------
# Config saving
# ---------------------------------------------------------------------------

def save_config(attr_results: list, list_results: dict) -> None:
    """Save created IDs to config file for use by the portal backend."""
    os.makedirs(os.path.dirname(RESULTS_FILE), exist_ok=True)
    config = {
        'created_at': __import__('datetime').datetime.utcnow().isoformat() + 'Z',
        'attributes': attr_results,
        'lists': list_results,
        # Convenience: flat dict of list name → ID for quick lookup
        'list_ids': {
            key: result.get('id')
            for key, result in list_results.items()
        },
    }
    with open(RESULTS_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    print(f'\n  Config saved to: {RESULTS_FILE}')


def print_env_snippet(list_results: dict) -> None:
    """Print the .env snippet the developer should add after running this script."""
    print('\n--- Add to .env (after running this script) ---')
    print('# Brevo competitor drip list IDs for migration-brevo-integration.js')
    for key, result in list_results.items():
        list_id = result.get('id', 'REPLACE_WITH_ID')
        if key == 'MIGRATION_LEADS':
            # This is the general migration leads list (BREVO_LIST_ID = 9 or similar)
            print(f'BREVO_MIGRATION_LEADS_LIST_ID={list_id}')
        else:
            print(f'BREVO_DRIP_LIST_{key}={list_id}')
    print('# Also update BREVO_LISTS.MIGRATION_LEADS in migration-brevo-integration.js')
    print('# with the ID for "PureBrain Migration Leads"')


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description='Set up Brevo attributes and lists for PureBrain Migration Portal'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview what would be created without making API calls',
    )
    args = parser.parse_args()

    if not BREVO_API_KEY:
        print('[ERROR] BREVO_API_KEY not found. Run: source .env')
        sys.exit(1)

    dry_run = args.dry_run
    mode = 'DRY-RUN' if dry_run else 'LIVE'
    print(f'\n=== PureBrain Migration Portal — Brevo Setup ({mode}) ===')
    print(f'API Key: {BREVO_API_KEY[:20]}...[redacted]')

    # Step 1: Create contact attributes
    attr_results = setup_attributes(dry_run)

    # Step 2: Create competitor drip lists
    list_results = setup_lists(dry_run)

    # Step 3: Save config and print summary
    print('\n--- Summary ---')
    created_attrs = [r for r in attr_results if r['status'] == 'created']
    skipped_attrs = [r for r in attr_results if r['status'] == 'already_exists']
    error_attrs   = [r for r in attr_results if r['status'] == 'error']
    print(f'  Attributes created : {len(created_attrs)}')
    print(f'  Attributes skipped : {len(skipped_attrs)}')
    print(f'  Attributes errored : {len(error_attrs)}')

    created_lists = [r for r in list_results.values() if r['status'] == 'created']
    skipped_lists = [r for r in list_results.values() if r['status'] == 'already_exists']
    error_lists   = [r for r in list_results.values() if r['status'] == 'error']
    print(f'  Lists created      : {len(created_lists)}')
    print(f'  Lists skipped      : {len(skipped_lists)}')
    print(f'  Lists errored      : {len(error_lists)}')

    if error_attrs or error_lists:
        print('\n[WARNING] Some items failed to create. Check errors above.')

    if not dry_run:
        save_config(attr_results, list_results)
        print_env_snippet(list_results)
        print('\n[DONE] Migration Brevo setup complete.')
        print('\nNext steps:')
        print('  1. Add the env vars above to .env')
        print('  2. In Brevo UI: create automation workflows for each drip list')
        print('     Trigger: "Contact added to list" → [competitor drip list]')
        print('  3. Update BREVO_LISTS.MIGRATION_LEADS in migration-brevo-integration.js')
        print(f'     with ID from config: {RESULTS_FILE}')
    else:
        print('\n[DRY-RUN COMPLETE] No changes made. Run without --dry-run to apply.')


if __name__ == '__main__':
    main()
