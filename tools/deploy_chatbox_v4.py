#!/usr/bin/env python3
"""
Deploy pay-test-script-chat-flow-v4.js to WordPress pages 688 and 689.

Pattern (from v3 deployment memory):
  1. GET page via REST API
  2. json.loads(_elementor_data) → Python tree
  3. Navigate to elem_data[0]['elements'][0]['settings']['html']
  4. Find <script>\n/* === Post-Payment Chat Flow ... === */
  5. Replace the entire <script>...</script> block with v4 content
  6. json.dumps back, PUT via REST API
  7. DELETE Elementor cache

Pages:
  688 = pay-test-sandbox-2 (test/QA)
  689 = pay-test-2 (live)
"""

import json
import re
import sys
import os
import requests
from dotenv import load_dotenv

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

WP_BASE    = 'https://purebrain.ai/wp-json/wp/v2'
WP_USER    = 'Aether'
WP_PASS    = os.environ['PUREBRAIN_WP_APP_PASSWORD']
V4_JS_PATH = '/home/jared/projects/AI-CIV/aether/exports/pay-test-script-chat-flow-v4.js'

AUTH = (WP_USER, WP_PASS)
HEADERS = {'Content-Type': 'application/json'}

# Load the v4 JS source
with open(V4_JS_PATH, 'r') as f:
    V4_JS = f.read()

# The new <script> block to inject
NEW_SCRIPT_BLOCK = f'<script>\n{V4_JS}\n</script>'


def get_page(page_id):
    url = f'{WP_BASE}/pages/{page_id}?context=edit'
    r = requests.get(url, auth=AUTH)
    r.raise_for_status()
    return r.json()


def find_and_replace_script(html_content, page_id):
    """
    Find the <script>/* === Post-Payment Chat Flow ... */</script> block
    and replace it with the new v4 script block.
    """
    # Match any version of the script block header
    pattern = r'<script>\s*/\* === Post-Payment Chat Flow'
    match = re.search(pattern, html_content)
    if not match:
        print(f'  [Page {page_id}] ERROR: Could not find script block marker in HTML content')
        print(f'  [Page {page_id}] First 200 chars of HTML: {html_content[:200]}')
        return None

    start_pos = match.start()

    # Find the closing </script> after the match position
    end_marker = '</script>'
    end_pos = html_content.find(end_marker, start_pos)
    if end_pos == -1:
        print(f'  [Page {page_id}] ERROR: Could not find closing </script> tag')
        return None

    end_pos += len(end_marker)

    old_block = html_content[start_pos:end_pos]
    print(f'  [Page {page_id}] Found script block: {old_block[:80].strip()}...')
    print(f'  [Page {page_id}] Block length: {len(old_block)} chars → replacing with {len(NEW_SCRIPT_BLOCK)} chars')

    new_html = html_content[:start_pos] + NEW_SCRIPT_BLOCK + html_content[end_pos:]
    return new_html


def deploy_page(page_id):
    print(f'\n--- Deploying to Page {page_id} ---')

    # Step 1: GET page
    print(f'  Fetching page {page_id}...')
    page = get_page(page_id)
    elem_data_str = page.get('meta', {}).get('_elementor_data', '')

    if not elem_data_str:
        print(f'  [Page {page_id}] ERROR: _elementor_data is empty or missing')
        return False

    print(f'  _elementor_data length: {len(elem_data_str)} chars')

    # Step 2: Parse the Elementor data
    try:
        elem_data = json.loads(elem_data_str)
    except json.JSONDecodeError as e:
        print(f'  [Page {page_id}] ERROR: Failed to parse _elementor_data: {e}')
        return False

    # Step 3: Navigate to the HTML widget
    # Structure: elem_data[0]['elements'][0] → the HTML widget
    try:
        widget = elem_data[0]['elements'][0]
        widget_type = widget.get('widgetType', '')
        print(f'  Widget type: {widget_type}')

        if widget_type != 'html':
            print(f'  [Page {page_id}] WARNING: Expected "html" widget, got "{widget_type}"')
            print(f'  [Page {page_id}] Attempting to find html widget by scanning...')
            # Try to find it by scanning
            found = False
            for section in elem_data:
                for col in section.get('elements', []):
                    for w in col.get('elements', []):
                        if w.get('widgetType') == 'html':
                            widget = w
                            found = True
                            break
                    if found:
                        break
                if found:
                    break
            if not found:
                print(f'  [Page {page_id}] ERROR: Could not find html widget')
                return False

        html_content = widget['settings']['html']

    except (IndexError, KeyError) as e:
        print(f'  [Page {page_id}] ERROR: Failed to navigate to HTML widget: {e}')
        return False

    print(f'  HTML widget content length: {len(html_content)} chars')

    # Step 4: Replace the script block
    new_html = find_and_replace_script(html_content, page_id)
    if new_html is None:
        return False

    # Step 5: Write back into the Elementor tree
    widget['settings']['html'] = new_html

    # Step 6: Re-serialize
    new_elem_data_str = json.dumps(elem_data, separators=(',', ':'), ensure_ascii=False)
    print(f'  New _elementor_data length: {len(new_elem_data_str)} chars')

    # Quick validation: round-trip parse
    try:
        json.loads(new_elem_data_str)
        print(f'  JSON round-trip validation: OK')
    except json.JSONDecodeError as e:
        print(f'  [Page {page_id}] ERROR: New JSON failed validation: {e}')
        return False

    # Step 7a: PUT _elementor_data to WordPress
    print(f'  Pushing _elementor_data to WordPress...')
    put_url = f'{WP_BASE}/pages/{page_id}'
    payload = {'meta': {'_elementor_data': new_elem_data_str}}
    r = requests.put(put_url, auth=AUTH, headers=HEADERS, json=payload)

    if not r.ok:
        print(f'  [Page {page_id}] ERROR: PUT _elementor_data failed: HTTP {r.status_code}')
        print(f'  Response: {r.text[:300]}')
        return False

    print(f'  PUT _elementor_data: HTTP {r.status_code} OK')

    # Step 7b: Also update content.raw (WordPress post_content) — v4.2 lesson
    # Elementor stores content in BOTH _elementor_data AND post_content.
    # Both must be updated or old script version persists in content.raw.
    # Replace the script block in the raw HTML content too.
    content_raw = page.get('content', {}).get('raw', '')
    if content_raw and '<script>' in content_raw:
        new_content_raw = find_and_replace_script(content_raw, page_id)
        if new_content_raw is not None:
            print(f'  Pushing content.raw to WordPress...')
            payload_content = {'content': new_content_raw}
            r2 = requests.put(put_url, auth=AUTH, headers=HEADERS, json=payload_content)
            if r2.ok:
                print(f'  PUT content.raw: HTTP {r2.status_code} OK')
            else:
                print(f'  [Page {page_id}] WARNING: PUT content.raw failed: HTTP {r2.status_code}')
                print(f'  Response: {r2.text[:200]}')
        else:
            print(f'  [Page {page_id}] WARNING: Could not update content.raw (script block not found)')
    else:
        print(f'  [Page {page_id}] NOTE: content.raw empty or no script block — skipping content.raw update')

    # Step 8: Verify BOTH storage locations contain v4.3.3 markers
    saved_page = get_page(page_id)
    saved_elem_str = saved_page.get('meta', {}).get('_elementor_data', '')
    saved_content_raw = saved_page.get('content', {}).get('raw', '')

    # _elementor_data checks
    marker_check = 'Chat Flow v4.7' in saved_elem_str
    birth_init_check = 'runBirthInit' in saved_elem_str
    portal_watcher_check = 'runPortalButtonWatcher' in saved_elem_str
    https_host_check = 'https://api.purebrain.ai' in saved_elem_str
    sanitize_check = 'sanitizeText' in saved_elem_str
    no_api_key_check = 'sk-ant-' not in saved_elem_str
    birth_in_phase1_check = 'Step 5b: Witness Birth Init' in saved_elem_str
    # v4.5 specific checks
    new_msg_check = 'The next step in' in saved_elem_str
    no_fallback_check = 'No action needed from you right now' not in saved_elem_str
    brain_connected_check = "brain is connected" in saved_elem_str

    # content.raw checks
    content_marker_check = 'Chat Flow v4.7' in saved_content_raw if saved_content_raw else None
    content_no_api_key = 'sk-ant-' not in saved_content_raw if saved_content_raw else None

    print(f'  Verification (_elementor_data):')
    print(f'    Chat Flow v4.7 marker: {"YES" if marker_check else "NO ← FAIL"}')
    print(f'    runBirthInit present: {"YES" if birth_init_check else "NO ← FAIL"}')
    print(f'    runPortalButtonWatcher present: {"YES" if portal_watcher_check else "NO ← FAIL"}')
    print(f'    HTTPS log host present: {"YES" if https_host_check else "NO ← FAIL"}')
    print(f'    sanitizeText helper present: {"YES" if sanitize_check else "NO ← FAIL (CRIT-004 regression!)"}')
    print(f'    sk-ant- API key flow removed: {"YES" if no_api_key_check else "NO ← FAIL (old key flow still present!)"}')
    print(f'    Birth init in Phase 1: {"YES" if birth_in_phase1_check else "NO ← FAIL (move not applied!)"}')
    print(f'    New birth msg text ("The next step in"): {"YES" if new_msg_check else "NO ← FAIL (Change 1 not applied!)"}')
    print(f'    Fallback msg removed: {"YES" if no_fallback_check else "NO ← FAIL (Change 3 not applied!)"}')
    print(f'    Brain connected msg present: {"YES" if brain_connected_check else "NO ← FAIL (Change 3 post-auth msg missing!)"}')

    if content_marker_check is not None:
        print(f'  Verification (content.raw):')
        print(f'    Chat Flow v4.7 marker: {"YES" if content_marker_check else "NO ← FAIL"}')
        print(f'    sk-ant- API key flow removed: {"YES" if content_no_api_key else "NO ← FAIL"}')

    all_pass = all([marker_check, birth_init_check, portal_watcher_check,
                    https_host_check, sanitize_check,
                    no_api_key_check, birth_in_phase1_check,
                    new_msg_check, no_fallback_check, brain_connected_check])
    if content_marker_check is not None:
        all_pass = all_pass and content_marker_check

    if all_pass:
        print(f'  Page {page_id}: ALL CHECKS PASSED')
    else:
        print(f'  Page {page_id}: SOME CHECKS FAILED')

    return all_pass


def clear_elementor_cache():
    print('\n--- Clearing Elementor cache ---')
    url = 'https://purebrain.ai/wp-json/elementor/v1/cache'
    r = requests.delete(url, auth=AUTH)
    print(f'  Cache clear: HTTP {r.status_code}')
    return r.ok


def main():
    print('=== Deploy Chatbox v4.5 (Corey Production: auto-fire birth, no hardcode, HTTPS proxy) ===')
    print(f'Source: {V4_JS_PATH}')
    print(f'JS size: {len(V4_JS)} chars')

    # Verify key v4.5 markers exist in JS
    assert 'Chat Flow v4.7' in V4_JS, 'v4.5 header marker missing from JS file'
    assert 'runBirthInit' in V4_JS, 'runBirthInit missing from JS file'
    assert 'https://api.purebrain.ai' in V4_JS, 'HTTPS log host missing from JS file'
    assert 'sanitizeText' in V4_JS, 'sanitizeText helper missing — CRIT-004 regression!'
    assert 'portal-status' in V4_JS, 'portal-status endpoint missing from JS file'
    assert 'sk-ant-' not in V4_JS, 'sk-ant- still present — old API key flow not fully removed!'
    assert 'Step 5b: Witness Birth Init' in V4_JS, 'Birth init Phase 1 marker missing — move not applied!'
    # v4.5 specific: auto-fire birth, no hardcode, HTTPS proxy
    assert 'The next step in' in V4_JS, 'Change 1 not applied: new birth setup message text missing!'
    # Change 3: Verify the original graceful-degradation fallback texts are absent from code
    # These appeared in v4.x as user-visible messages (not comments) in the birth/start catch block
    assert 'No action needed from you right now' not in V4_JS, 'Change 3 not applied: old fallback msg still present!'
    assert 'brain is connected' in V4_JS, 'Change 3 not applied: post-auth success message missing!'
    print('Pre-flight checks: PASSED')

    pages = [688, 689]
    results = {}

    for page_id in pages:
        success = deploy_page(page_id)
        results[page_id] = success

    clear_elementor_cache()

    print('\n=== DEPLOYMENT SUMMARY ===')
    all_ok = True
    for page_id, success in results.items():
        status = 'OK' if success else 'FAILED'
        url = 'https://purebrain.ai/pay-test-sandbox-2/' if page_id == 688 else 'https://purebrain.ai/pay-test/'
        print(f'  Page {page_id} ({url}): {status}')
        if not success:
            all_ok = False

    if all_ok:
        print('\nDeployment complete. Verify at:')
        print('  https://purebrain.ai/pay-test-sandbox-2/')
        print('  https://purebrain.ai/pay-test/')
    else:
        print('\nDEPLOYMENT HAD FAILURES. Review output above.')
        sys.exit(1)


if __name__ == '__main__':
    main()
