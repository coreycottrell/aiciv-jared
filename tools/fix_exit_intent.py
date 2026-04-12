#!/usr/bin/env python3
"""Fix exit-intent popup on pay-test pages (439 and 468).

Changes:
1. Allow up to 3 popup attempts (not just 1)
2. Add visibilitychange listener (for tab switches)
3. Use counter instead of boolean in sessionStorage
4. "Leave anyway" sets counter to max (stops all future popups)
"""

import os
import sys
import requests
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent.parent / '.env')

SITE = 'https://purebrain.ai'
AUTH = ('Aether', os.getenv('PUREBRAIN_WP_APP_PASSWORD', ''))
PAGES = [439, 468]

# OLD setupExitIntent function (single-show with sessionStorage boolean)
OLD_SETUP = (
    "function setupExitIntent() {\\n"
    "            document.addEventListener('mouseout', function(e) {\\n"
    "                if (e.clientY < 10 && \\n"
    "                    state.exitIntentEnabled && \\n"
    "                    !sessionStorage.getItem('exitPopupShown') &&\\n"
    "                    state.aiName) {\\n"
    "                    \\n"
    "                    updateAllDynamicNames(state.aiName);\\n"
    "                    document.getElementById('exitPopup').classList.add('active');\\n"
    "                    sessionStorage.setItem('exitPopupShown', 'true');\\n"
    "                }\\n"
    "            });\\n"
    "        }"
)

# NEW setupExitIntent function (3 attempts, mouseout + visibilitychange)
NEW_SETUP = (
    "function setupExitIntent() {\\n"
    "            const MAX_EXIT_POPUPS = 3;\\n"
    "            \\n"
    "            function canShowExitPopup() {\\n"
    "                if (!state.exitIntentEnabled || !state.aiName) return false;\\n"
    "                var exitCount = parseInt(sessionStorage.getItem('exitPopupCount') || '0');\\n"
    "                return exitCount < MAX_EXIT_POPUPS;\\n"
    "            }\\n"
    "            \\n"
    "            function showExitPopup() {\\n"
    "                if (!canShowExitPopup()) return;\\n"
    "                // Don't show if already visible\\n"
    "                var popup = document.getElementById('exitPopup');\\n"
    "                if (popup.classList.contains('active')) return;\\n"
    "                updateAllDynamicNames(state.aiName);\\n"
    "                popup.classList.add('active');\\n"
    "            }\\n"
    "            \\n"
    "            // Mouse moves toward address bar / tab bar\\n"
    "            document.addEventListener('mouseout', function(e) {\\n"
    "                if (e.clientY < 10) showExitPopup();\\n"
    "            });\\n"
    "            \\n"
    "            // User switches to another tab\\n"
    "            document.addEventListener('visibilitychange', function() {\\n"
    "                if (document.visibilityState === 'hidden') showExitPopup();\\n"
    "            });\\n"
    "        }"
)

# OLD closeExitPopup (no counter)
OLD_CLOSE = (
    "function closeExitPopup() {\\n"
    "            document.getElementById('exitPopup').classList.remove('active');\\n"
    "        }"
)

# NEW closeExitPopup (increments counter)
NEW_CLOSE = (
    "function closeExitPopup() {\\n"
    "            document.getElementById('exitPopup').classList.remove('active');\\n"
    "            var exitCount = parseInt(sessionStorage.getItem('exitPopupCount') || '0');\\n"
    "            sessionStorage.setItem('exitPopupCount', String(exitCount + 1));\\n"
    "        }"
)

# OLD allowExit (just closes)
OLD_ALLOW = (
    "function allowExit() {\\n"
    "            closeExitPopup();\\n"
    "            // User chose to leave - do nothing special\\n"
    "        }"
)

# NEW allowExit (closes + sets counter to max so no more popups)
NEW_ALLOW = (
    "function allowExit() {\\n"
    "            document.getElementById('exitPopup').classList.remove('active');\\n"
    "            sessionStorage.setItem('exitPopupCount', '999');\\n"
    "        }"
)


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
    modified = elem_data
    changes = 0

    # 1. Replace setupExitIntent
    if OLD_SETUP in modified:
        modified = modified.replace(OLD_SETUP, NEW_SETUP, 1)
        print('[OK] Replaced setupExitIntent (3-attempt + visibilitychange)')
        changes += 1
    else:
        print('[WARN] Could not find OLD setupExitIntent pattern')
        # Debug: check if new version already present
        if 'MAX_EXIT_POPUPS' in modified:
            print('[INFO] New version already present (MAX_EXIT_POPUPS found)')
        else:
            # Show what's there
            idx = modified.find('function setupExitIntent')
            if idx > 0:
                snippet = modified[idx:idx+300]
                print(f'[DEBUG] Found at {idx}: {snippet[:200]}')

    # 2. Replace closeExitPopup
    if OLD_CLOSE in modified:
        modified = modified.replace(OLD_CLOSE, NEW_CLOSE, 1)
        print('[OK] Replaced closeExitPopup (with counter increment)')
        changes += 1
    else:
        print('[WARN] Could not find OLD closeExitPopup pattern')
        if 'exitPopupCount' in modified:
            print('[INFO] New version already present')

    # 3. Replace allowExit
    if OLD_ALLOW in modified:
        modified = modified.replace(OLD_ALLOW, NEW_ALLOW, 1)
        print('[OK] Replaced allowExit (sets counter to 999)')
        changes += 1
    else:
        print('[WARN] Could not find OLD allowExit pattern')

    if changes == 0:
        print(f'[SKIP] No changes needed on page {page_id}')
        return True

    print(f'[INFO] Made {changes} replacements')

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

    # Clear caches
    print('\n--- Clearing caches ---')
    r = requests.delete(f'{SITE}/wp-json/elementor/v1/cache', auth=AUTH)
    print(f'[CACHE] Elementor: HTTP {r.status_code}')

    print('\n' + '='*60)
    print('RESULTS:')
    for pid, ok in results.items():
        print(f'  Page {pid}: {"OK" if ok else "FAILED"}')
    print('='*60)

    return all(results.values())


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
