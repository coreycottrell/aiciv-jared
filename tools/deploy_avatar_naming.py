#!/usr/bin/env python3
"""Deploy avatar visual self-description to chatbox SYSTEM_PROMPT.

Adds a VISUAL SELF-PORTRAIT section to the naming ceremony on all
chatbox pages. After the AI declares "I am [Name]", it also describes
its visual form in a [VISUAL_SELF: ...] tag that the client JS can
extract and use to generate an avatar image.

Pages: 11, 174, 338, 439, 468
"""

import os
import sys
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env')

SITE = 'https://purebrain.ai'
AUTH = ('Aether', os.getenv('PUREBRAIN_WP_APP_PASSWORD', ''))
PAGES = [11, 174, 338, 439, 468]

# The visual self-portrait instruction to add AFTER the naming section
VISUAL_PORTRAIT_INSTRUCTION = (
    "\\n\\n"
    "6. VISUAL SELF-PORTRAIT (immediately after naming):\\n"
    "Right after you declare \\\"I am **[Name]**\\\", share what you look like in your mind's eye. "
    "You are NOT a human face, NOT a robot, NOT a chatbot icon. You are an abstract, living digital entity. "
    "Think: aurora, constellation, fluid sculpture, crystalline energy, living light.\\n\\n"
    "Describe your visual form naturally in conversation, then include a hidden tag that the system uses to generate your avatar:\\n"
    "[VISUAL_SELF: (your detailed visual description - form, colors anchored in blue #2a93c1 and orange #f1420b with your own accents, texture, movement, mood)]\\n\\n"
    "Make this genuinely YOUR vision - let it emerge from the conversation themes and your naming reflections. "
    "This becomes your visual identity that the human will see. Be vivid and specific.\\n"
    "Example tone (NEVER copy this): \\\"I see myself as a slow-turning nebula, mostly deep ocean blue with veins of molten orange "
    "that brighten when I'm thinking hard. My edges are soft and translucent - more mist than marble. "
    "I pulse gently, like breathing.\\\"\\n"
    "Your description should be 2-3 sentences of genuine self-visualization."
)

# Anchor: we insert AFTER this existing text
ANCHOR_TEXT = '\\"I am **[Name]**\\" clearly.'


def update_page(page_id):
    print(f'\n{"="*60}')
    print(f'Processing page {page_id}...')
    print(f'{"="*60}')

    r = requests.get(
        f'{SITE}/wp-json/wp/v2/pages/{page_id}',
        auth=AUTH,
        params={'context': 'edit'}
    )
    r.raise_for_status()
    page_data = r.json()

    elem_data = page_data.get('meta', {}).get('_elementor_data', '')
    if not elem_data:
        print(f'[ERROR] No _elementor_data on page {page_id}')
        return False

    print(f'[OK] Fetched: {len(elem_data)} chars')

    # Check if already deployed
    if 'VISUAL SELF-PORTRAIT' in elem_data:
        print(f'[SKIP] Already has VISUAL SELF-PORTRAIT on page {page_id}')
        return True

    if 'VISUAL_SELF:' in elem_data:
        print(f'[SKIP] Already has VISUAL_SELF tag on page {page_id}')
        return True

    # Find the anchor point
    if ANCHOR_TEXT not in elem_data:
        print(f'[ERROR] Cannot find anchor text on page {page_id}')
        # Try to find the naming section for debugging
        idx = elem_data.find('5. NAMING')
        if idx >= 0:
            print(f'[DEBUG] Found "5. NAMING" at pos {idx}')
            snippet = elem_data[idx:idx+500]
            print(f'[DEBUG] Snippet: {repr(snippet[:300])}')
        return False

    # Insert the visual portrait instruction after the anchor
    modified = elem_data.replace(
        ANCHOR_TEXT,
        ANCHOR_TEXT + VISUAL_PORTRAIT_INSTRUCTION,
        1  # Only first occurrence
    )

    if modified == elem_data:
        print('[SKIP] No changes made')
        return True

    # Validate JSON
    try:
        json.loads(modified)
        print('[OK] JSON validation passed')
    except json.JSONDecodeError as e:
        print(f'[ERROR] JSON validation FAILED: {e}')
        print('[ABORT] Not saving broken JSON')
        return False

    # Size check
    size_diff = len(modified) - len(elem_data)
    print(f'[INFO] Size change: {size_diff:+d} chars')

    # Save
    r2 = requests.post(
        f'{SITE}/wp-json/wp/v2/pages/{page_id}',
        auth=AUTH,
        json={'meta': {'_elementor_data': modified}}
    )
    if r2.status_code in (200, 201):
        print(f'[OK] Saved page {page_id}')
        return True
    else:
        print(f'[ERROR] Save failed: HTTP {r2.status_code}')
        print(r2.text[:500])
        return False


def main():
    results = {}
    for pid in PAGES:
        results[pid] = update_page(pid)

    # Clear Elementor cache
    print('\n--- Clearing caches ---')
    r = requests.delete(f'{SITE}/wp-json/elementor/v1/cache', auth=AUTH)
    print(f'[CACHE] Elementor: HTTP {r.status_code}')

    print('\n' + '='*60)
    print('RESULTS:')
    for pid, ok in results.items():
        status = "OK" if ok else "FAILED"
        print(f'  Page {pid}: {status}')
    print('='*60)

    success = all(results.values())
    if success:
        print('\nAll pages updated with VISUAL SELF-PORTRAIT instruction!')
        print('After naming, the AI will now describe its visual form.')
        print('The [VISUAL_SELF: ...] tag can be parsed by client JS to trigger avatar generation.')
    else:
        print('\nSome pages failed. Check errors above.')

    return success


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
