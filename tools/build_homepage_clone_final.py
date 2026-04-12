#!/usr/bin/env python3
"""
Full homepage clone deployment to pay-test-2 (689) and sandbox-3 (1232).
CTO-authored final build script v2.

This script:
1. Fetches live rendered homepage HTML (the REAL design reference)
2. Fetches current content of pages 689 and 1232 (to preserve chatbox + PayPal)
3. Builds merged pages: homepage design + preserved payment/chat scripts
4. Deploys via WP REST API
5. Clears Elementor cache
6. Verifies deployment

Architecture:
- Both 689 and 1232 use _elementor_data[0].elements[0].settings.html
- The HTML widget contains the FULL page HTML (doctype through body close)
- We replace the DESIGN sections while preserving the FUNCTIONAL sections

Memory reference:
- sandbox3 bottom sections: cut at `\n\n\n\n<!-- Calculator CTA Section -->`
- pay-test-2: similar structure but with OAuth/Telegram KEPT
- PayPal LIVE client: AWgWNlBQAy5BMXKB...
- PayPal SANDBOX client: AYTFob05DoSn0Ze...
"""

import requests
import base64
import json
import os
import sys
import re
import subprocess
from datetime import datetime

# ─── Credentials ────────────────────────────────────────────────────────────
def load_env(path='/home/jared/projects/AI-CIV/aether/.env'):
    """Simple .env loader."""
    env = {}
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, _, v = line.partition('=')
                    v = v.strip().strip("'\"")
                    env[k.strip()] = v
    except FileNotFoundError:
        pass
    return env

env = load_env()
WP_USER = env.get('PUREBRAIN_WP_USER', 'purebrain@puremarketing.ai')
WP_APP_PW = env.get('PUREBRAIN_WP_APP_PASSWORD', '')
BASE_URL = 'https://purebrain.ai'

if not WP_APP_PW:
    print("ERROR: PUREBRAIN_WP_APP_PASSWORD not found")
    sys.exit(1)

auth_bytes = base64.b64encode(f'{WP_USER}:{WP_APP_PW}'.encode()).decode()
HEADERS = {
    'Authorization': f'Basic {auth_bytes}',
    'Content-Type': 'application/json',
}

PAYPAL_LIVE = 'AWgWNlBQAy5BMXKB5xbaMwSk01WkatC08b5rTj_JKu4Jm2JugXvjAwMRyNe1FmabNS9v846Rma5ptxhI'
PAYPAL_SANDBOX = 'AYTFob05DoSn0ZeVtLJ05duKwFHOdAckHgkZ2UJhAXvfJlUXEYM_PFib3HbIuVgauxV_6clZ5FdPRYq_'

def log(msg, level='INFO'):
    ts = datetime.now().strftime('%H:%M:%S')
    print(f"[{ts}] [{level}] {msg}")

def send_tg(msg):
    """Send progress update to Telegram."""
    try:
        subprocess.run(
            ['bash', '/home/jared/projects/AI-CIV/aether/tools/tg_send.sh', f'CTO build: {msg}'],
            capture_output=True, timeout=10
        )
    except Exception as e:
        log(f"TG send failed: {e}", 'WARN')

# ─── WP API helpers ──────────────────────────────────────────────────────────

def wp_get_page(page_id):
    """Fetch page with edit context (includes _elementor_data)."""
    url = f"{BASE_URL}/wp-json/wp/v2/pages/{page_id}?context=edit"
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()

def wp_update_page(page_id, payload):
    """Update a page via REST API."""
    url = f"{BASE_URL}/wp-json/wp/v2/pages/{page_id}"
    r = requests.post(url, headers=HEADERS, json=payload, timeout=120)
    r.raise_for_status()
    return r.json()

def wp_clear_elementor_cache():
    """Clear Elementor render cache."""
    r = requests.delete(f"{BASE_URL}/wp-json/elementor/v1/cache", headers=HEADERS, timeout=30)
    if r.status_code in (200, 204):
        log("Elementor cache cleared")
        return True
    log(f"Cache clear: {r.status_code}", 'WARN')
    return False

# ─── Extract elementor HTML widget content ────────────────────────────────────

def get_elementor_html_widget(page_data):
    """
    Extract the main HTML widget content from _elementor_data.
    Both pages 689 and 1232 structure: [0].elements[0].settings.html
    """
    meta = page_data.get('meta', {})
    ed_str = meta.get('_elementor_data', '')
    if not ed_str:
        log("No _elementor_data found", 'WARN')
        return None, None, None

    try:
        ed = json.loads(ed_str)
    except json.JSONDecodeError as e:
        log(f"Failed to parse _elementor_data: {e}", 'ERROR')
        return None, None, None

    # Navigate to the HTML widget
    try:
        html_content = ed[0]['elements'][0]['settings']['html']
        log(f"HTML widget: {len(html_content):,} chars")
        return ed, html_content, ed_str
    except (KeyError, IndexError, TypeError) as e:
        log(f"Could not navigate to HTML widget: {e}", 'ERROR')
        # Dump structure for debugging
        if ed:
            log(f"ED structure: {list(ed[0].keys()) if ed[0] else 'empty'}")
        return None, None, None

def set_elementor_html_widget(ed, new_html):
    """Set new HTML content in the elementor data structure."""
    ed[0]['elements'][0]['settings']['html'] = new_html
    return json.dumps(ed)

# ─── Find the functional section boundaries ──────────────────────────────────

def find_functional_cutpoints(html):
    """
    Find where the FUNCTIONAL content (chatbox, PayPal, scripts) ends and
    the design bottom sections begin. We want to KEEP functional content
    and REPLACE design sections.

    Returns: (functional_end_idx, design_start_idx)
    """
    # The bottom sections always start with one of these patterns:
    bottom_section_markers = [
        '\n\n\n\n<!-- Calculator CTA Section -->',
        '<!-- Calculator CTA Section -->',
        '<!-- CALCULATOR CTA SECTION -->',
        'id="pb-calculator-teaser"',
        'pb-calc-headline',
        '<!-- COMPARE PUREBRAIN SECTION -->',
        '<!-- Compare PureBrain Section -->',
        'id="pb-compare-section"',
        '<!-- WHY PUREBRAIN LINK',
    ]

    for marker in bottom_section_markers:
        idx = html.find(marker)
        if idx > 0:
            log(f"Found cut point at index {idx}: {marker[:50]!r}")
            return idx

    # Fallback: find by known functional end markers
    functional_end_markers = [
        '<!-- END PAY-TEST SCRIPTS -->',
        '<!-- END SCRIPTS -->',
        '// ---------------------------------------------------------------------------\n// Exports',
        'window.initPayTestFlow = initPayTestFlow',
    ]

    for marker in functional_end_markers:
        idx = html.find(marker)
        if idx > 0:
            # Find the end of this marker
            end_idx = idx + len(marker)
            # Find the next newline after this
            nl_idx = html.find('\n', end_idx)
            if nl_idx > 0:
                log(f"Found functional end at index {nl_idx}: {marker[:50]!r}")
                return nl_idx

    log("WARNING: Could not find cut point — will append to end", 'WARN')
    # Last resort: find </body> and cut before it
    body_close = html.rfind('</body>')
    if body_close > 0:
        return body_close
    return len(html)

# ─── Fetch and extract homepage design sections ──────────────────────────────

def fetch_homepage_design():
    """
    Fetch the rendered homepage HTML and extract the design sections
    that should be cloned to pay-test-2 and sandbox-3.

    Returns the bottom sections HTML string.
    """
    log("Fetching homepage rendered HTML...")
    try:
        r = requests.get('https://purebrain.ai/', timeout=30,
                        headers={'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15'})
        homepage_html = r.text
        log(f"Homepage HTML: {len(homepage_html):,} chars")
    except Exception as e:
        log(f"Failed to fetch homepage: {e}", 'ERROR')
        return None

    # Save for inspection
    save_path = '/home/jared/projects/AI-CIV/aether/exports/homepage-rendered-live.html'
    with open(save_path, 'w') as f:
        f.write(homepage_html)
    log(f"Homepage saved to {save_path}")

    return homepage_html

def extract_design_sections_from_homepage(homepage_html):
    """
    Extract the bottom design sections from the homepage HTML.
    These are: calculator CTA, compare pills, awaken CTA, see why different, footer, legal footer, aether bar.

    Returns the HTML string of just these sections.
    """
    if not homepage_html:
        return None

    # Find the calculator CTA section start
    design_start_markers = [
        '<!-- Calculator CTA Section -->',
        'id="pb-calculator-teaser"',
        'pb-calc-headline',
        'How Much Are You Wasting on AI Tool Sprawl',
        'FREE TOOL',
        '<!-- Compare PureBrain Section -->',
        'id="pb-compare-section"',
    ]

    design_start_idx = -1
    for marker in design_start_markers:
        idx = homepage_html.find(marker)
        if idx > 0:
            # Go back to find the containing section/div
            search_back = homepage_html.rfind('<section', 0, idx)
            search_back2 = homepage_html.rfind('<div class="pb-', 0, idx)
            section_start = max(search_back, search_back2)
            if section_start > 0 and (idx - section_start) < 500:
                design_start_idx = section_start
            else:
                design_start_idx = idx
            log(f"Design sections start at index {design_start_idx}: {marker[:60]!r}")
            break

    if design_start_idx < 0:
        log("Could not find design sections start in homepage", 'ERROR')
        return None

    # Find the end - look for </html> or end of page
    design_end_markers = [
        '</html>',
        '<!-- END PUREBRAIN PAGE -->',
    ]

    design_end_idx = len(homepage_html)
    for marker in design_end_markers:
        idx = homepage_html.rfind(marker)
        if idx > design_start_idx:
            design_end_idx = idx + len(marker)
            log(f"Design sections end at index {design_end_idx}")
            break

    design_html = homepage_html[design_start_idx:design_end_idx]
    log(f"Extracted design sections: {len(design_html):,} chars")

    return design_html

# ─── Also check for the pre-extracted sections file ──────────────────────────

def load_pre_extracted_sections():
    """
    Load the pre-extracted bottom sections file from the earlier session today.
    This was created at /tmp/homepage_bottom_sections.html by the earlier session.
    """
    paths_to_try = [
        '/tmp/homepage_bottom_sections.html',
        '/home/jared/projects/AI-CIV/aether/exports/homepage_bottom_sections.html',
        '/home/jared/projects/AI-CIV/aether/exports/homepage-bottom-sections.html',
    ]

    for path in paths_to_try:
        if os.path.exists(path):
            with open(path) as f:
                content = f.read()
            log(f"Loaded pre-extracted sections from {path}: {len(content):,} chars")
            return content

    log("No pre-extracted sections file found — will extract from live homepage", 'INFO')
    return None

# ─── Build the new page HTML ──────────────────────────────────────────────────

def build_new_page_html(existing_html, new_bottom_sections, paypal_client_id, page_name):
    """
    Build the new page HTML by:
    1. Taking existing page HTML up to the cut point (preserving chatbox + PayPal + scripts)
    2. Appending the new design sections from homepage

    Returns the new merged HTML.
    """
    log(f"Building new page HTML for {page_name}...")

    # Find the cut point in existing content
    cut_idx = find_functional_cutpoints(existing_html)
    log(f"Cut point at index {cut_idx} of {len(existing_html)}")

    # Take everything up to the cut point (functional content)
    functional_top = existing_html[:cut_idx]

    # Verify PayPal client ID is in the top section (safety check)
    if paypal_client_id not in functional_top:
        log(f"WARNING: PayPal client ID NOT found in functional top section!", 'WARN')
        # Try to find where PayPal is in the full content
        pp_idx = existing_html.find(paypal_client_id)
        if pp_idx > 0:
            log(f"PayPal is at index {pp_idx} — cut point {cut_idx} might be too early", 'WARN')
            if pp_idx < cut_idx:
                log("PayPal IS in functional top — the ID may have special chars, checking...", 'INFO')
        else:
            log("PayPal client ID not found anywhere in page — deployment may break PayPal!", 'ERROR')
    else:
        log(f"PayPal client ID confirmed in functional top section ✓")

    # Verify chatbox is in the top section
    chatbox_markers = ['initPayTestFlow', 'chatbox', 'chat-container', 'pay-test-chat']
    chatbox_found = any(m in functional_top for m in chatbox_markers)
    if chatbox_found:
        log(f"Chatbox confirmed in functional top section ✓")
    else:
        log(f"WARNING: Chatbox not found in functional top section!", 'WARN')

    # Build the new HTML
    new_html = functional_top.rstrip()
    new_html += '\n\n\n\n'
    new_html += new_bottom_sections.strip()
    new_html += '\n\n</body>\n</html>'

    log(f"New page HTML: {len(new_html):,} chars (was {len(existing_html):,})")

    return new_html

# ─── Main deployment function ─────────────────────────────────────────────────

def deploy_page(page_id, page_name, paypal_client_id, new_bottom_sections):
    """Deploy new page content to WordPress."""
    log(f"\n{'='*60}")
    log(f"Deploying {page_name} (page {page_id})")
    log(f"{'='*60}")

    # Step 1: Fetch current page
    log(f"Fetching current page {page_id}...")
    page_data = wp_get_page(page_id)

    # Step 2: Get HTML widget content
    ed, html_content, ed_str = get_elementor_html_widget(page_data)
    if html_content is None:
        log(f"FAILED to get HTML content for page {page_id}", 'ERROR')
        return False

    # Step 3: Backup current content
    backup_path = f'/home/jared/projects/AI-CIV/aether/exports/backup-page-{page_id}-{datetime.now().strftime("%Y%m%d-%H%M%S")}.html'
    with open(backup_path, 'w') as f:
        f.write(html_content)
    log(f"Backup saved: {backup_path}")

    # Step 4: Build new HTML
    new_html = build_new_page_html(html_content, new_bottom_sections, paypal_client_id, page_name)

    if not new_html:
        log(f"FAILED to build new HTML for page {page_id}", 'ERROR')
        return False

    # Step 5: Update elementor data
    new_ed_str = set_elementor_html_widget(ed, new_html)
    log(f"New _elementor_data size: {len(new_ed_str):,} chars")

    # Step 6: Deploy
    log(f"Deploying to WP page {page_id}...")
    try:
        result = wp_update_page(page_id, {
            'meta': {'_elementor_data': new_ed_str}
        })
        log(f"Deploy successful. Modified: {result.get('modified', 'unknown')}")
    except requests.HTTPError as e:
        log(f"Deploy FAILED: {e}", 'ERROR')
        if e.response:
            log(f"Response: {e.response.text[:500]}", 'ERROR')
        return False

    # Step 7: Verify
    log(f"Verifying deployment...")
    verify_data = wp_get_page(page_id)
    verify_ed, verify_html, _ = get_elementor_html_widget(verify_data)

    if verify_html and 'Compare PureBrain' in verify_html:
        log(f"✓ Compare PureBrain section found in deployed content")
    else:
        log(f"⚠ Compare PureBrain not found in deployed content", 'WARN')

    if verify_html and 'Awaken Your' in verify_html:
        log(f"✓ Awaken CTA section found in deployed content")

    if verify_html and paypal_client_id in verify_html:
        log(f"✓ PayPal client ID preserved in deployed content")
    else:
        log(f"⚠ PayPal client ID NOT in deployed content!", 'WARN')

    if verify_html and 'initPayTestFlow' in verify_html:
        log(f"✓ initPayTestFlow preserved in deployed content")

    return True

# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    send_tg("Build script starting — fetching homepage design")
    log("Starting homepage clone deployment")

    # Step 1: Get design sections
    # First try the pre-extracted file from earlier today
    new_bottom_sections = load_pre_extracted_sections()

    if not new_bottom_sections:
        # Extract from live homepage
        homepage_html = fetch_homepage_design()
        if not homepage_html:
            log("CRITICAL: Could not get homepage design", 'ERROR')
            send_tg("FAILED: Could not fetch homepage design")
            sys.exit(1)

        new_bottom_sections = extract_design_sections_from_homepage(homepage_html)
        if not new_bottom_sections:
            log("CRITICAL: Could not extract design sections from homepage", 'ERROR')
            send_tg("FAILED: Could not extract design sections from homepage")
            sys.exit(1)

        # Save for reference
        save_path = '/home/jared/projects/AI-CIV/aether/exports/homepage_bottom_sections_new.html'
        with open(save_path, 'w') as f:
            f.write(new_bottom_sections)
        log(f"Design sections saved to {save_path}")
    else:
        # We have pre-extracted sections — great, use them
        pass

    log(f"\nDesign sections to inject: {len(new_bottom_sections):,} chars")
    log(f"Preview (first 200 chars): {new_bottom_sections[:200]!r}")

    send_tg("Homepage design sections ready — deploying to pay-test-2")

    # Step 2: Deploy to pay-test-2 (page 689, LIVE PayPal)
    success_689 = deploy_page(
        page_id=689,
        page_name="pay-test-2",
        paypal_client_id=PAYPAL_LIVE,
        new_bottom_sections=new_bottom_sections,
    )

    if success_689:
        send_tg("pay-test-2 (689) deployed successfully")
        log("pay-test-2 deployed ✓")
    else:
        send_tg("FAILED: pay-test-2 (689) deployment failed")
        log("pay-test-2 deployment FAILED", 'ERROR')

    send_tg("Deploying to sandbox-3")

    # Step 3: Deploy to sandbox-3 (page 1232, SANDBOX PayPal)
    success_1232 = deploy_page(
        page_id=1232,
        page_name="sandbox-3",
        paypal_client_id=PAYPAL_SANDBOX,
        new_bottom_sections=new_bottom_sections,
    )

    if success_1232:
        send_tg("sandbox-3 (1232) deployed successfully")
        log("sandbox-3 deployed ✓")
    else:
        send_tg("FAILED: sandbox-3 (1232) deployment failed")
        log("sandbox-3 deployment FAILED", 'ERROR')

    # Step 4: Clear Elementor cache
    log("\nClearing Elementor cache...")
    wp_clear_elementor_cache()

    # Summary
    log("\n" + "="*60)
    log("DEPLOYMENT SUMMARY")
    log("="*60)
    log(f"pay-test-2 (689):  {'✓ SUCCESS' if success_689 else '✗ FAILED'}")
    log(f"sandbox-3 (1232):  {'✓ SUCCESS' if success_1232 else '✗ FAILED'}")

    if success_689 and success_1232:
        send_tg("Phase 1 COMPLETE: Both pages deployed. QA running next.")
    else:
        send_tg(f"Phase 1 PARTIAL: 689={'OK' if success_689 else 'FAIL'}, 1232={'OK' if success_1232 else 'FAIL'}")

    return success_689 and success_1232


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
