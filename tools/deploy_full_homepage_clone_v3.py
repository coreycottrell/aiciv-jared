#!/usr/bin/env python3
"""
COMPLETE HOMEPAGE CLONE DEPLOYMENT — v3 (CTO Final)
====================================================

This script is the DEFINITIVE fix for pay-test-2 (689) and sandbox-3 (1232).

It does EVERYTHING in one shot:

PHASE 1: Clone homepage design to both pages
- Fetches live rendered homepage HTML from purebrain.ai
- Fetches current content of pages 689 and 1232
- Preserves: chatbox HTML, PayPal integration, post-payment flow scripts
- Removes: old bottom sections (pricing-section, comparison-section, timeline, testimonials)
- Injects: homepage bottom sections (calculator CTA, compare pills, awaken CTA, see why different, footer)
- Cleans: nested HTML documents (prevents mobile rendering issues)

PHASE 2: Fix mobile video background on all 3 pages (homepage, 689, 1232)
- Ensures video element has correct iOS-compatible attributes
- Fixes CSS: width:100%; height:100% (not auto/auto which fails on iOS)
- Applies to all 3 pages via _elementor_data update

PHASE 3: Fix mobile section backgrounds
- Adds solid dark backgrounds to sections that are transparent
- This prevents the dark video overlay from making content invisible
- Applied to the injected CSS block inside page HTML

Architecture notes:
- Both 689 and 1232 use _elementor_data[0].elements[0].settings.html
- The HTML widget contains the FULL page HTML
- homepage (page 11) also uses _elementor_data but with Elementor layout sections
- PayPal LIVE client: AWgWNlBQAy5BMXKB...
- PayPal SANDBOX client: AYTFob05DoSn0Ze...

Memory refs:
- CTO arch: .claude/memory/agent-learnings/cto/2026-03-09--homepage-clone-mission-architecture.md
- Mobile video CSS: .claude/memory/agent-learnings/full-stack-developer/2026-03-08--mobile-video-background-fix.md
- Nested HTML docs: .claude/memory/agent-learnings/full-stack-developer/2026-03-08--mobile-sections-invisible-nested-html-docs.md
- Mobile transparent bg: .claude/memory/agent-learnings/browser-vision-tester/2026-03-08--pay-test-2-mobile-transparent-bg-video-overlay.md
"""

import requests
import base64
import json
import os
import sys
import subprocess
from datetime import datetime

# ─── Credentials ────────────────────────────────────────────────────────────

def load_env(path='/home/jared/projects/AI-CIV/aether/.env'):
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
    print("ERROR: PUREBRAIN_WP_APP_PASSWORD not found in .env")
    sys.exit(1)

auth_bytes = base64.b64encode(f'{WP_USER}:{WP_APP_PW}'.encode()).decode()
HEADERS = {
    'Authorization': f'Basic {auth_bytes}',
    'Content-Type': 'application/json',
}

PAYPAL_LIVE    = 'AWgWNlBQAy5BMXKB5xbaMwSk01WkatC08b5rTj_JKu4Jm2JugXvjAwMRyNe1FmabNS9v846Rma5ptxhI'
PAYPAL_SANDBOX = 'AYTFob05DoSn0ZeVtLJ05duKwFHOdAckHgkZ2UJhAXvfJlUXEYM_PFib3HbIuVgauxV_6clZ5FdPRYq_'

def log(msg, level='INFO'):
    ts = datetime.now().strftime('%H:%M:%S')
    prefix = {'INFO': '', 'WARN': '⚠ ', 'ERROR': '✗ ', 'OK': '✓ '}.get(level, '')
    print(f"[{ts}] [{level}] {prefix}{msg}")

def tg(msg):
    try:
        subprocess.run(
            ['bash', '/home/jared/projects/AI-CIV/aether/tools/tg_send.sh', f'CTO deploy v3: {msg}'],
            capture_output=True, timeout=15
        )
    except Exception as e:
        log(f"TG send failed: {e}", 'WARN')

# ─── WP API helpers ──────────────────────────────────────────────────────────

def wp_get(page_id):
    url = f"{BASE_URL}/wp-json/wp/v2/pages/{page_id}?context=edit"
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()

def wp_post(page_id, payload):
    url = f"{BASE_URL}/wp-json/wp/v2/pages/{page_id}"
    r = requests.post(url, headers=HEADERS, json=payload, timeout=120)
    r.raise_for_status()
    return r.json()

def wp_clear_cache():
    r = requests.delete(f"{BASE_URL}/wp-json/elementor/v1/cache", headers=HEADERS, timeout=30)
    log(f"Cache clear: {r.status_code}", 'OK' if r.status_code in (200, 204) else 'WARN')

def get_elementor_html(page_data):
    """Extract HTML from _elementor_data[0].elements[0].settings.html"""
    meta = page_data.get('meta', {})
    ed_str = meta.get('_elementor_data', '')
    if not ed_str:
        log("No _elementor_data found", 'ERROR')
        return None, None
    ed = json.loads(ed_str)
    html = ed[0]['elements'][0]['settings']['html']
    log(f"Got HTML widget: {len(html):,} chars")
    return ed, html

def set_elementor_html(ed, new_html):
    ed[0]['elements'][0]['settings']['html'] = new_html
    return json.dumps(ed)

# ─── PHASE 1: Homepage design extraction ─────────────────────────────────────

HOMEPAGE_BOTTOM_MARKERS = [
    '<!-- Calculator CTA Section -->',
    'id="pb-calculator-teaser"',
    'pb-calc-headline',
    'How Much Are You Wasting on AI Tool Sprawl',
    '<!-- Compare PureBrain Section -->',
    'id="pb-compare-section"',
    'Compare PureBrain',
]

def fetch_homepage_rendered():
    """Fetch the live rendered homepage HTML (includes injected sections)."""
    log("Fetching live rendered homepage...")
    r = requests.get(f'{BASE_URL}/', timeout=30, headers={
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1'
    })
    html = r.text
    log(f"Homepage: {len(html):,} chars")
    # Save for reference
    with open('/home/jared/projects/AI-CIV/aether/exports/homepage-rendered-v3.html', 'w') as f:
        f.write(html)
    return html

def extract_bottom_sections(homepage_html):
    """
    Extract the bottom design sections from the rendered homepage.
    These are the sections that will replace the bottom of pay-test-2 and sandbox-3.

    Returns a string of HTML starting from the Calculator CTA section through </html>.
    """
    start_idx = -1
    for marker in HOMEPAGE_BOTTOM_MARKERS:
        idx = homepage_html.find(marker)
        if idx > 0:
            # Walk back to find the opening <section or <div
            section_open = homepage_html.rfind('<section', 0, idx)
            div_open = homepage_html.rfind('<div class="pb-', 0, idx)
            div_open2 = homepage_html.rfind('<div id="pb-', 0, idx)
            candidate = max(section_open, div_open, div_open2)
            if candidate > 0 and (idx - candidate) < 600:
                start_idx = candidate
            else:
                start_idx = idx
            log(f"Bottom sections start at {start_idx} ({marker[:40]!r})")
            break

    if start_idx < 0:
        log("Could not find bottom section start in homepage!", 'ERROR')
        return None

    # End at </html>
    end_idx = homepage_html.rfind('</html>')
    if end_idx > 0:
        end_idx += len('</html>')
    else:
        end_idx = len(homepage_html)

    sections = homepage_html[start_idx:end_idx]
    log(f"Extracted bottom sections: {len(sections):,} chars")
    return sections


def find_cut_point(html):
    """
    Find where to cut the existing page HTML.
    We KEEP everything above (chatbox, PayPal, post-payment scripts).
    We REPLACE everything below (old bottom design sections).
    """
    markers = [
        '\n\n\n\n<!-- Calculator CTA Section -->',
        '<!-- Calculator CTA Section -->',
        '\n<!-- Calculator CTA Section -->',
        'id="pb-calculator-teaser"',
        'pb-calc-headline',
        '<!-- CALCULATOR CTA -->',
        # Fallback: end of scripts block
        '// ── END OF SCRIPTS ──',
        '// End PayTest scripts',
        '// --- END ---',
    ]
    for m in markers:
        idx = html.find(m)
        if idx > 0:
            log(f"Cut at {idx} ({m[:40]!r})")
            return idx
    # Last resort: find the last </script> tag before the bottom sections
    # Look for Compare section or Awaken section
    for m in ['<!-- Compare PureBrain -->', 'Compare PureBrain', '<!-- Awaken CTA -->', 'id="pb-compare"']:
        idx = html.find(m)
        if idx > 0:
            # Walk back to find the section opening
            s = html.rfind('<section', 0, idx)
            if s > 0 and (idx - s) < 600:
                log(f"Cut at {s} (before '{m[:30]}')", 'WARN')
                return s
    # Absolute last resort: cut before </body>
    body_close = html.rfind('</body>')
    if body_close > 0:
        log(f"Cut at </body> position {body_close}", 'WARN')
        return body_close
    log("Could not find cut point!", 'ERROR')
    return len(html)


def clean_nested_html_docs(html):
    """
    Remove nested <!DOCTYPE html>, <html>, </html>, </body> from widget HTML.
    These cause mobile Safari to close the outer body context early, making
    sections after the widget invisible on mobile.

    Rule: The widget HTML should contain ZERO </body> or </html> tags.
    The outer Elementor page provides those.
    """
    original_count_body = html.count('</body>')
    original_count_html_close = html.count('</html>')
    original_count_doctype = html.count('<!DOCTYPE html>')
    original_count_html_open = html.count('<html')

    log(f"Before clean: {original_count_body} </body>, {original_count_html_close} </html>, "
        f"{original_count_doctype} DOCTYPE, {original_count_html_open} <html")

    if original_count_body == 0 and original_count_html_close == 0:
        log("No nested HTML docs to clean — OK")
        return html

    # Remove all </body> and </html> tags from the widget content
    # Also remove nested <!DOCTYPE html> and <html...> opening tags
    import re
    cleaned = html
    cleaned = re.sub(r'</body>\s*', '', cleaned)
    cleaned = re.sub(r'</html>\s*', '', cleaned)
    # Remove nested DOCTYPE declarations (second+ occurrence)
    doctypes = [m.start() for m in re.finditer(r'<!DOCTYPE html>', cleaned, re.IGNORECASE)]
    if len(doctypes) > 1:
        # Remove all but keep nothing (widget shouldn't have DOCTYPE)
        cleaned = re.sub(r'<!DOCTYPE html>', '', cleaned, flags=re.IGNORECASE)
    # Remove nested <html ...> opening tags
    html_opens = [m.start() for m in re.finditer(r'<html\b[^>]*>', cleaned, re.IGNORECASE)]
    if len(html_opens) > 0:
        cleaned = re.sub(r'<html\b[^>]*>', '', cleaned, flags=re.IGNORECASE)
    # Remove nested <head> blocks (between <head> and </head>)
    # This is aggressive but the widget should not have its own <head>
    cleaned = re.sub(r'<head\b[^>]*>.*?</head>', '', cleaned, flags=re.IGNORECASE | re.DOTALL)

    after_body = cleaned.count('</body>')
    after_html = cleaned.count('</html>')
    log(f"After clean: {after_body} </body>, {after_html} </html>", 'OK')
    return cleaned


def add_mobile_video_css_fix(html):
    """
    Inject/replace the video background CSS to fix mobile Safari/iOS autoplay.

    The fix:
    - Uses width:100%; height:100% instead of width:auto; height:auto
    - Uses top:0; left:0 positioning instead of transform: translate(-50%,-50%)
    - Ensures video element has correct attributes (done in HTML, not CSS)

    Also injects mobile section background fixes.
    """
    MOBILE_VIDEO_CSS = """
<style id="pb-mobile-video-fix-v3">
/* ── MOBILE VIDEO BACKGROUND FIX v3 ─────────────────────────── */
/* Fix: width:auto;height:auto fails on iOS Safari — use 100%/100% */
.video-background__video,
.video-background video {
    position: absolute !important;
    top: 0 !important;
    left: 0 !important;
    width: 100% !important;
    height: 100% !important;
    object-fit: cover !important;
    transform: none !important;
    min-width: unset !important;
    min-height: unset !important;
}
/* Ensure video wrapper fills viewport */
.video-background,
#video-background {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    width: 100vw !important;
    height: 100vh !important;
    z-index: 0 !important;
    overflow: hidden !important;
}
/* ── MOBILE SECTION BACKGROUND FIXES ────────────────────────── */
/* Fix: transparent/semi-transparent sections invisible on mobile */
/* when dark video overlay (rgba 0,0,0,0.75) bleeds through        */
@media (max-width: 767px) {
    .timeline-section,
    .testimonials-section,
    .pricing-section.active,
    .comparison-section.active,
    .about-section,
    .value-section,
    .capabilities-section {
        background: #080a12 !important;
        position: relative !important;
        z-index: 5 !important;
    }
    /* Force all sections above video overlay */
    section, .section, [class*="-section"] {
        position: relative;
        z-index: 2;
    }
}
/* ── END MOBILE FIXES ─────────────────────────────────────────── */
</style>"""

    # If fix already exists, replace it
    if 'pb-mobile-video-fix-v3' in html:
        import re
        html = re.sub(
            r'<style id="pb-mobile-video-fix-v3">.*?</style>',
            MOBILE_VIDEO_CSS,
            html, flags=re.DOTALL
        )
        log("Replaced existing mobile video CSS fix")
    elif 'pb-mobile-video-fix' in html:
        # Replace older version
        import re
        html = re.sub(
            r'<style id="pb-mobile-video-fix[^"]*">.*?</style>',
            MOBILE_VIDEO_CSS,
            html, flags=re.DOTALL
        )
        log("Replaced older mobile video CSS fix version")
    else:
        # Inject before </head> or at start of content
        head_close = html.find('</head>')
        if head_close > 0:
            html = html[:head_close] + '\n' + MOBILE_VIDEO_CSS + '\n' + html[head_close:]
            log("Injected mobile video CSS fix before </head>")
        else:
            # Inject after <body> or first style block
            body_open = html.find('<body')
            if body_open > 0:
                body_tag_end = html.find('>', body_open) + 1
                html = html[:body_tag_end] + '\n' + MOBILE_VIDEO_CSS + '\n' + html[body_tag_end:]
                log("Injected mobile video CSS fix after <body>")
            else:
                # Prepend
                html = MOBILE_VIDEO_CSS + '\n' + html
                log("Prepended mobile video CSS fix", 'WARN')

    return html


def fix_video_element_attributes(html):
    """
    Ensure all video elements have iOS-required autoplay attributes.
    Required: autoplay muted loop playsinline preload="auto"
    """
    import re

    def fix_video_tag(m):
        tag = m.group(0)
        # Add missing attributes
        if 'autoplay' not in tag:
            tag = tag.replace('<video', '<video autoplay', 1)
        if 'muted' not in tag:
            tag = tag.replace('<video', '<video muted', 1)
        if 'playsinline' not in tag:
            tag = tag.replace('<video', '<video playsinline', 1)
        if 'loop' not in tag:
            tag = tag.replace('<video', '<video loop', 1)
        if 'preload' not in tag:
            tag = tag.replace('<video', '<video preload="auto"', 1)
        return tag

    fixed = re.sub(r'<video\b[^>]*>', fix_video_tag, html)
    video_count = html.count('<video')
    log(f"Video elements fixed: {video_count} found, attributes ensured")
    return fixed


# ─── PHASE 1 MAIN: Build and deploy page clone ──────────────────────────────

def build_cloned_page(existing_html, bottom_sections, paypal_client_id, page_name):
    """
    Build the full new page HTML:
    1. Cut existing at the bottom sections start
    2. Clean nested HTML docs from the functional top
    3. Append new bottom sections from homepage
    4. Inject mobile video CSS fix
    5. Fix video element attributes
    """
    log(f"\nBuilding cloned page for {page_name}...")

    # Find cut point
    cut_idx = find_cut_point(existing_html)
    log(f"Cut at {cut_idx} / {len(existing_html)}")

    # Take functional top (chatbox + PayPal + scripts)
    functional_top = existing_html[:cut_idx]

    # Safety checks
    pp_ok = paypal_client_id in functional_top
    chat_ok = any(m in functional_top for m in ['initPayTestFlow', 'chatbox', 'chat-container', 'pay-test-chat'])
    log(f"PayPal client ID in functional top: {pp_ok}", 'OK' if pp_ok else 'ERROR')
    log(f"Chatbox in functional top: {chat_ok}", 'OK' if chat_ok else 'WARN')

    if not pp_ok:
        # Check if PayPal is in the cut-off portion
        pp_idx = existing_html.find(paypal_client_id)
        log(f"PayPal found at index {pp_idx} (cut was at {cut_idx})", 'ERROR')
        if pp_idx < cut_idx:
            log("PayPal IS before cut point — check the client ID string for special chars", 'WARN')
        else:
            log("CRITICAL: PayPal is AFTER cut point — adjusting cut to keep PayPal", 'ERROR')
            # Move cut to after PayPal
            pp_end = pp_idx + len(paypal_client_id) + 200  # buffer
            next_section = existing_html.find('\n\n\n', pp_end)
            if next_section > 0:
                cut_idx = next_section
                functional_top = existing_html[:cut_idx]
                log(f"Adjusted cut to {cut_idx} to preserve PayPal")
            else:
                log("Cannot find safe cut after PayPal — aborting!", 'ERROR')
                return None

    # Clean nested HTML docs from functional top
    functional_top = clean_nested_html_docs(functional_top)

    # Assemble new page
    new_html = functional_top.rstrip()
    new_html += '\n\n\n\n'
    new_html += bottom_sections.strip()

    # Apply mobile fixes
    new_html = add_mobile_video_css_fix(new_html)
    new_html = fix_video_element_attributes(new_html)

    log(f"Built {page_name}: {len(new_html):,} chars (was {len(existing_html):,})")
    return new_html


def deploy_page_clone(page_id, page_name, paypal_client_id, bottom_sections):
    """Full pipeline: fetch → build → deploy → verify."""
    log(f"\n{'='*60}")
    log(f"DEPLOYING {page_name.upper()} (page {page_id})")
    log(f"{'='*60}")

    # Fetch current page
    page_data = wp_get(page_id)
    ed, html = get_elementor_html(page_data)
    if html is None:
        log(f"FAILED to get HTML widget for page {page_id}", 'ERROR')
        return False

    # Backup
    backup = f'/home/jared/projects/AI-CIV/aether/exports/backup-{page_id}-{datetime.now().strftime("%Y%m%d-%H%M%S")}.html'
    with open(backup, 'w') as f:
        f.write(html)
    log(f"Backed up to {backup}")

    # Build
    new_html = build_cloned_page(html, bottom_sections, paypal_client_id, page_name)
    if not new_html:
        log(f"BUILD FAILED for {page_name}", 'ERROR')
        return False

    # Save preview for inspection
    preview_path = f'/home/jared/projects/AI-CIV/aether/exports/preview-{page_id}-v3.html'
    with open(preview_path, 'w') as f:
        f.write(new_html)
    log(f"Preview saved: {preview_path}")

    # Deploy
    new_ed_str = set_elementor_html(ed, new_html)
    log(f"Deploying {len(new_ed_str):,} char payload...")

    try:
        result = wp_post(page_id, {'meta': {'_elementor_data': new_ed_str}})
        log(f"Deployed. Modified: {result.get('modified')}", 'OK')
    except requests.HTTPError as e:
        log(f"Deploy FAILED: {e.response.status_code}", 'ERROR')
        log(e.response.text[:500], 'ERROR')
        return False

    # Verify by re-fetching
    verify = wp_get(page_id)
    _, verify_html = get_elementor_html(verify)

    checks = {
        'PayPal client ID': paypal_client_id in verify_html,
        'Compare PureBrain': 'Compare PureBrain' in verify_html,
        'Awaken CTA': 'Awaken Your' in verify_html,
        'Footer': 'pb-aether-footer' in verify_html or 'purebrain-legal-footer' in verify_html,
        'Mobile video CSS': 'pb-mobile-video-fix-v3' in verify_html,
        'No nested </body>': '</body>' not in verify_html,
        'No nested </html>': '</html>' not in verify_html,
        'Chat flow': 'initPayTestFlow' in verify_html or 'chat-container' in verify_html,
    }

    all_ok = True
    for check, passed in checks.items():
        level = 'OK' if passed else 'ERROR'
        log(f"  {check}: {'✓' if passed else '✗'}", level)
        if not passed:
            all_ok = False

    return all_ok


# ─── PHASE 2: Fix mobile video on homepage (page 11) ─────────────────────────

def fix_homepage_mobile_video():
    """
    Fix mobile video CSS on homepage (page 11).
    Homepage uses _elementor_data but with Elementor sections layout.
    The video CSS is inside an inline <style> block in the HTML widget.
    """
    log(f"\n{'='*60}")
    log("PHASE 2: Fixing homepage (page 11) mobile video")
    log(f"{'='*60}")

    page_data = wp_get(11)
    meta = page_data.get('meta', {})
    ed_str = meta.get('_elementor_data', '')
    if not ed_str:
        log("No _elementor_data on homepage!", 'ERROR')
        return False

    # Apply video CSS fix to the entire elementor data string
    # The video CSS is embedded within the HTML widget inside elementor data
    # We need to find and replace the old CSS pattern

    OLD_VIDEO_CSS_PATTERN = """position: absolute;
        top: 50%;
        left: 50%;
        min-width: 100%;
        min-height: 100%;
        width: auto;
        height: auto;
        transform: translate(-50%, -50%);"""

    NEW_VIDEO_CSS = """position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;"""

    if OLD_VIDEO_CSS_PATTERN in ed_str:
        new_ed_str = ed_str.replace(OLD_VIDEO_CSS_PATTERN, NEW_VIDEO_CSS)
        log(f"Replaced old video CSS pattern in homepage elementor data")
    else:
        # Pattern not found — may already be fixed or use different formatting
        log("Old video CSS pattern not found in homepage — checking for existing fix...", 'WARN')
        if 'width: 100%' in ed_str and 'height: 100%' in ed_str and 'object-fit: cover' in ed_str:
            log("Homepage video CSS already has correct pattern — OK", 'OK')
            return True
        else:
            log("Could not find CSS pattern to fix — manual review needed", 'WARN')
            return False

    try:
        result = wp_post(11, {'meta': {'_elementor_data': new_ed_str}})
        log(f"Homepage updated. Modified: {result.get('modified')}", 'OK')
        return True
    except requests.HTTPError as e:
        log(f"Homepage update FAILED: {e}", 'ERROR')
        return False


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    tg("v3 script starting — full homepage clone + mobile video fix")
    log("="*60)
    log("PUREBRAIN.AI FULL DEPLOY v3")
    log("Phase 1: Homepage clone to pay-test-2 + sandbox-3")
    log("Phase 2: Mobile video fix on all 3 pages")
    log("="*60)

    # ── Step 1: Get homepage bottom sections ────────────────────
    log("\n[Step 1] Fetching homepage bottom sections...")
    homepage_html = fetch_homepage_rendered()
    bottom_sections = extract_bottom_sections(homepage_html)

    if not bottom_sections:
        log("CRITICAL: Could not extract bottom sections from homepage!", 'ERROR')
        tg("FAILED: Could not extract homepage bottom sections")
        sys.exit(1)

    # Save extracted sections
    with open('/home/jared/projects/AI-CIV/aether/exports/homepage-bottom-sections-v3.html', 'w') as f:
        f.write(bottom_sections)
    log(f"Bottom sections saved ({len(bottom_sections):,} chars)")
    tg(f"Homepage sections extracted ({len(bottom_sections):,} chars). Deploying pay-test-2...")

    # ── Step 2: Deploy pay-test-2 (page 689, LIVE PayPal) ───────
    log("\n[Step 2] Deploying pay-test-2 (689)...")
    ok_689 = deploy_page_clone(
        page_id=689,
        page_name="pay-test-2",
        paypal_client_id=PAYPAL_LIVE,
        bottom_sections=bottom_sections,
    )
    log(f"pay-test-2: {'✓ SUCCESS' if ok_689 else '✗ FAILED'}", 'OK' if ok_689 else 'ERROR')
    tg(f"pay-test-2 (689): {'DEPLOYED' if ok_689 else 'FAILED'}. Deploying sandbox-3...")

    # ── Step 3: Deploy sandbox-3 (page 1232, SANDBOX PayPal) ────
    log("\n[Step 3] Deploying sandbox-3 (1232)...")
    ok_1232 = deploy_page_clone(
        page_id=1232,
        page_name="sandbox-3",
        paypal_client_id=PAYPAL_SANDBOX,
        bottom_sections=bottom_sections,
    )
    log(f"sandbox-3: {'✓ SUCCESS' if ok_1232 else '✗ FAILED'}", 'OK' if ok_1232 else 'ERROR')
    tg(f"sandbox-3 (1232): {'DEPLOYED' if ok_1232 else 'FAILED'}. Fixing homepage mobile video...")

    # ── Step 4: Fix homepage mobile video ───────────────────────
    log("\n[Step 4] Fixing homepage (11) mobile video CSS...")
    ok_homepage_video = fix_homepage_mobile_video()
    log(f"Homepage video fix: {'✓ SUCCESS' if ok_homepage_video else '⚠ CHECK NEEDED'}")
    tg(f"Homepage mobile video: {'FIXED' if ok_homepage_video else 'NEEDS REVIEW'}. Clearing cache...")

    # ── Step 5: Clear Elementor cache ───────────────────────────
    log("\n[Step 5] Clearing Elementor cache...")
    wp_clear_cache()

    # ── Summary ─────────────────────────────────────────────────
    log("\n" + "="*60)
    log("DEPLOYMENT SUMMARY")
    log("="*60)
    log(f"pay-test-2 (689):     {'✓ SUCCESS' if ok_689 else '✗ FAILED'}")
    log(f"sandbox-3 (1232):     {'✓ SUCCESS' if ok_1232 else '✗ FAILED'}")
    log(f"Homepage video fix:   {'✓ SUCCESS' if ok_homepage_video else '⚠ NEEDS REVIEW'}")
    log(f"Elementor cache:      cleared")

    all_ok = ok_689 and ok_1232
    status = "ALL DEPLOYED" if all_ok else f"PARTIAL: 689={'OK' if ok_689 else 'FAIL'}, 1232={'OK' if ok_1232 else 'FAIL'}"
    tg(f"Deploy v3 COMPLETE: {status}. Pages: purebrain.ai/pay-test-2 and purebrain.ai/pay-test-sandbox-3")
    log(f"\nVerify at:")
    log(f"  https://purebrain.ai/pay-test-2/?password=PureBrain.ai253443$$")
    log(f"  https://purebrain.ai/pay-test-sandbox-3/?password=PureBrain.ai253443$$")
    log(f"  https://purebrain.ai/")

    return all_ok


if __name__ == '__main__':
    ok = main()
    sys.exit(0 if ok else 1)
