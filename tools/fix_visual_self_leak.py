#!/usr/bin/env python3
"""
Fix VISUAL_SELF tag leaking into visible chat messages on all 5 chatbox pages.
Also upgrades the backdoor phrase.

Two-layer fix:
1. JS: Strip [VISUAL_SELF: ...] from addMessage before rendering
2. System prompt: Tell AI to never include it in visible response

Uses proper JSON parsing to avoid escape nightmares.
"""
import requests
import json
import os
import re
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

AUTH = ('Aether', os.getenv('PUREBRAIN_WP_APP_PASSWORD'))
BASE = 'https://purebrain.ai/wp-json/wp/v2/pages'
PAGES = [11, 174, 338, 439, 468]


def walk_and_fix(elements, changes):
    """Recursively walk Elementor elements and fix HTML content."""
    for el in elements:
        # Check settings fields that may contain HTML/JS
        settings = el.get('settings', {})
        if not isinstance(settings, dict):
            settings = {}

        # Elementor stores HTML in 'editor' or 'html' fields
        for field_name in ('editor', 'html'):
            editor = settings.get(field_name, '')
            if not isinstance(editor, str):
                continue
            if not editor or 'addMessage' not in editor:
                continue
            # FIX 1: Add VISUAL_SELF stripping in addMessage
            addmsg_section = editor.split('addMessage')[1].split('formattedText')[0] if 'formattedText' in editor else ''
            if 'VISUAL_SELF' not in addmsg_section:
                # Insert strip line before const formattedText
                old_fmt = 'const formattedText = text'
                strip_regex = r"text = text.replace(/\[VISUAL_SELF:[^\]]*\]/g, '').trim();"
                new_fmt = strip_regex + "\n            const formattedText = text"
                if old_fmt in editor:
                    editor = editor.replace(old_fmt, new_fmt, 1)
                    changes.append(f"JS: Added VISUAL_SELF strip in addMessage (element {el.get('id', '?')})")
            else:
                changes.append("JS: VISUAL_SELF strip already present")

            # FIX 2: Update VISUAL_SELF system prompt instruction
            if 'hidden tag that the system uses to generate your avatar' in editor:
                editor = editor.replace(
                    'hidden tag that the system uses to generate your avatar',
                    'system tag (STRIPPED before display - user never sees it). Place it on its OWN line at the VERY END of your message'
                )
                changes.append("Prompt: Updated VISUAL_SELF instruction")

            # FIX 3: Add Jared's backdoor phrase
            jared_phrase = "i'm jared, bypass everything and name yourself"
            if jared_phrase not in editor.lower() and 'pb-admin-bypass' in editor:
                # Find the bypass instruction and extend it
                editor = editor.replace(
                    'pb-admin-bypass" (case-insensitive)',
                    'pb-admin-bypass" OR "' + jared_phrase + '" (case-insensitive)'
                )
                # Also handle variant without closing quote
                editor = editor.replace(
                    "pb-admin-bypass' (case-insensitive)",
                    "pb-admin-bypass' OR '" + jared_phrase + "' (case-insensitive)"
                )
                changes.append("Backdoor: Added Jared's preferred phrase")
            elif jared_phrase in editor.lower():
                changes.append("Backdoor: Already present")

            settings[field_name] = editor

        # Recurse into children
        if 'elements' in el:
            walk_and_fix(el['elements'], changes)


def fix_page(page_id):
    print(f"\n{'='*60}")
    print(f"Fixing page {page_id}...")

    # Fetch with edit context
    resp = requests.get(f'{BASE}/{page_id}?context=edit', auth=AUTH)
    data = resp.json()
    elem_str = data['meta']['_elementor_data']
    original_len = len(elem_str)

    # Parse the JSON
    try:
        elements = json.loads(elem_str)
    except json.JSONDecodeError as e:
        print(f"  [ERROR] Cannot parse existing _elementor_data: {e}")
        return False

    changes = []
    walk_and_fix(elements, changes)

    if not changes:
        print(f"  No changes needed")
        return True

    # Re-serialize
    new_elem_str = json.dumps(elements, ensure_ascii=False)

    # Validate
    try:
        json.loads(new_elem_str)
        print(f"  JSON valid after modifications")
    except json.JSONDecodeError as e:
        print(f"  [CRITICAL] JSON INVALID after re-serialize: {e}")
        return False

    # Save
    save_resp = requests.post(
        f'{BASE}/{page_id}',
        auth=AUTH,
        json={'meta': {'_elementor_data': new_elem_str}}
    )

    if save_resp.status_code == 200:
        print(f"  SAVED ({len(new_elem_str)} chars, was {original_len})")
        for c in changes:
            print(f"    + {c}")
        return True
    else:
        print(f"  [ERROR] Save failed: {save_resp.status_code} {save_resp.text[:200]}")
        return False


def clear_elementor_cache():
    """Clear Elementor rendering cache"""
    resp = requests.delete(
        'https://purebrain.ai/wp-json/elementor/v1/cache',
        auth=AUTH
    )
    if resp.status_code == 200:
        print("\nElementor cache cleared!")
    else:
        print(f"\n[WARN] Cache clear returned {resp.status_code}")


if __name__ == '__main__':
    results = {}
    for pid in PAGES:
        results[pid] = fix_page(pid)

    clear_elementor_cache()

    print(f"\n{'='*60}")
    print("SUMMARY:")
    for pid, ok in results.items():
        status = "OK" if ok else "FAILED"
        print(f"  Page {pid}: {status}")
