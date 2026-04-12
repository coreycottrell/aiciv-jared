#!/usr/bin/env python3
"""
Deploy the fixed AI Partnership Audit lead magnet page to WordPress.

Fixes deployed:
1. .page > .orb { position: absolute; z-index: 0; } — prevents orbs from
   being overridden to position:relative by the .page > * rule, eliminating
   the dark void layout bug in Chrome.
2. Replaced SVG feTurbulence data-URI noise texture with CSS repeating-linear-gradient
   (Chrome cannot resolve #fragment refs inside SVG CSS background-image data URIs).
3. All CSS scoped under #pb-audit-page for WordPress theme override protection.
4. CSS variables replaced with hard values for WordPress compatibility.
"""

import base64
import json
import os
import re
import sys

import requests
from dotenv import load_dotenv

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

WP_BASE = 'https://purebrain.ai/wp-json/wp/v2'
WP_USER = 'Aether'
WP_PASS = os.getenv('PUREBRAIN_WP_APP_PASSWORD')
PAGE_ID = 620  # ai-partnership-audit page

HTML_FILE = '/home/jared/projects/AI-CIV/aether/exports/ai-partnership-audit-lead-magnet.html'

# From memory of successful deployment pattern (2026-02-21--ai-partnership-audit-interactive-deployment.md)
HEADERS = {
    'Authorization': f"Basic {base64.b64encode(f'{WP_USER}:{WP_PASS}'.encode()).decode()}",
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
}


def load_html():
    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        return f.read()


def extract_css(html):
    """Extract CSS from <style> block."""
    m = re.search(r'<style>(.*?)</style>', html, re.DOTALL)
    if not m:
        raise ValueError('No <style> block found')
    return m.group(1)


def extract_body(html):
    """Extract body content (everything between <body> and </body>)."""
    m = re.search(r'<body>(.*?)</body>', html, re.DOTALL)
    if not m:
        raise ValueError('No <body> block found')
    return m.group(1).strip()


# Hard-coded CSS variable values (from :root in the source file)
CSS_VARS = {
    'var(--blue)':          '#2a93c1',
    'var(--blue-light)':    '#3eb0e0',
    'var(--blue-dim)':      '#1a5a7a',
    'var(--orange)':        '#f1420b',
    'var(--orange-dim)':    '#a02d07',
    'var(--bg-page)':       '#080a12',
    'var(--bg-card)':       '#0e1120',
    'var(--bg-card-alt)':   '#111628',
    'var(--border)':        'rgba(42, 147, 193, 0.2)',
    'var(--border-mid)':    'rgba(42, 147, 193, 0.35)',
    'var(--text-primary)':  '#e0e6f0',
    'var(--text-secondary)': '#94a3b8',
    'var(--text-muted)':    '#5a6a82',
    'var(--white)':         '#ffffff',
}


def replace_css_vars(css):
    """Replace all CSS var() references with hard values."""
    for var, val in CSS_VARS.items():
        css = css.replace(var, val)
    return css


def scope_css(css):
    """
    Scope all CSS selectors under #pb-audit-page.

    Strategy:
    - Remove the :root { ... } block (variables replaced with hard values)
    - Keep *, *::before, *::after reset but scope it
    - Keep html and body rules but convert to global overrides with !important
    - All other rules get prefixed with #pb-audit-page
    - @media and @page blocks are handled recursively
    - @print blocks preserved
    """
    # First replace all CSS vars with hard values
    css = replace_css_vars(css)

    # Remove :root block
    css = re.sub(r'/\*.*?DESIGN TOKENS.*?\*/', '', css, flags=re.DOTALL)
    css = re.sub(r'\s*:root\s*\{[^}]*\}', '', css)

    # Build the scoped CSS output
    lines = []

    # Global overrides for body/html (must beat WordPress theme)
    lines.append("""
/* === WordPress theme overrides (global scope) === */
html, body {
  background-color: #080a12 !important;
  color: #e0e6f0 !important;
}
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif !important;
  min-height: 100vh !important;
}
/* Hide WordPress theme chrome */
.site-header, .site-footer, .entry-header, .entry-footer,
.wp-block-post-title, h1.entry-title, .page-title {
  display: none !important;
}
""")

    # The reset rule (*, *::before, *::after) scoped to our wrapper
    reset_block = """
/* Reset scoped to our page */
#pb-audit-page *,
#pb-audit-page *::before,
#pb-audit-page *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}
"""
    lines.append(reset_block)

    # Remove the original *, html, body, and :root blocks from css before scoping
    # We'll handle them with the overrides above
    css_clean = re.sub(r'\*\s*,\s*\*::before\s*,\s*\*::after\s*\{[^}]*\}', '', css)
    css_clean = re.sub(r'html\s*\{[^}]*\}', '', css_clean)
    css_clean = re.sub(r'body\s*\{[^}]*\}', '', css_clean)

    # Now scope all remaining rules under #pb-audit-page
    # We need to handle @media blocks specially
    scoped = scope_css_block(css_clean, '#pb-audit-page')
    lines.append(scoped)

    return '\n'.join(lines)


def scope_css_block(css, prefix):
    """
    Scope a block of CSS under a given prefix.
    Handles @media and @page at-rules by scoping their contents.
    """
    result = []
    i = 0
    css = css.strip()
    n = len(css)

    while i < n:
        # Skip whitespace
        while i < n and css[i].isspace():
            i += 1
        if i >= n:
            break

        # Comment: /* ... */
        if css[i:i+2] == '/*':
            end = css.find('*/', i + 2)
            if end == -1:
                end = n - 2
            result.append(css[i:end+2])
            i = end + 2
            continue

        # At-rule: @media, @page, @keyframes, @print
        if css[i] == '@':
            # Find opening brace or semicolon
            brace_or_semi = find_first(css, i, ['{', ';'])
            if brace_or_semi == -1 or css[brace_or_semi] == ';':
                # Simple at-rule (e.g., @import ;)
                end = css.find(';', i)
                if end == -1:
                    end = n - 1
                result.append(css[i:end+1])
                i = end + 1
                continue
            # Block at-rule
            at_keyword_end = brace_or_semi
            at_header = css[i:at_keyword_end].strip()
            # Find matching closing brace
            open_brace = brace_or_semi
            close_brace = find_matching_brace(css, open_brace)

            inner = css[open_brace+1:close_brace]

            # @print and @page: scope inner rules
            if at_header.startswith('@media') or at_header.startswith('@print'):
                scoped_inner = scope_css_block(inner, prefix)
                result.append(f'{at_header} {{\n{scoped_inner}\n}}')
            elif at_header.startswith('@keyframes') or at_header.startswith('@-webkit-keyframes'):
                # Don't scope keyframes selectors
                result.append(f'{at_header} {{\n{inner}\n}}')
            elif at_header.startswith('@page'):
                result.append(f'{at_header} {{\n{inner}\n}}')
            else:
                # Unknown at-rule: scope inner
                scoped_inner = scope_css_block(inner, prefix)
                result.append(f'{at_header} {{\n{scoped_inner}\n}}')

            i = close_brace + 1
            continue

        # Regular rule: selector { declarations }
        open_brace = css.find('{', i)
        if open_brace == -1:
            # Remaining text with no brace - skip
            break

        selector = css[i:open_brace].strip()
        close_brace = find_matching_brace(css, open_brace)
        declarations = css[open_brace+1:close_brace]

        if selector:
            # Scope the selector
            scoped_selector = scope_selector(selector, prefix)
            result.append(f'{scoped_selector} {{\n{declarations}\n}}')

        i = close_brace + 1

    return '\n'.join(result)


def find_first(s, start, chars):
    """Find first occurrence of any char in chars, starting from start."""
    best = -1
    for c in chars:
        idx = s.find(c, start)
        if idx != -1 and (best == -1 or idx < best):
            best = idx
    return best


def find_matching_brace(css, open_pos):
    """Find the matching closing brace for opening brace at open_pos."""
    depth = 0
    i = open_pos
    n = len(css)
    while i < n:
        if css[i] == '{':
            depth += 1
        elif css[i] == '}':
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return n - 1


def scope_selector(selector, prefix):
    """
    Add prefix to each comma-separated selector part.
    """
    parts = selector.split(',')
    scoped_parts = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        # Don't re-scope if already has our prefix
        if prefix in part:
            scoped_parts.append(part)
            continue
        # html and body selectors: scope inside the page wrapper
        if part in ('html', 'body'):
            # These are handled globally, skip in scoped block
            scoped_parts.append(f'{prefix}')
            continue
        scoped_parts.append(f'{prefix} {part}')
    return ', '.join(scoped_parts)


def build_wordpress_content(css, body_html):
    """
    Build the final WordPress page content:
    - Scoped <style> block
    - Body content wrapped in #pb-audit-page div
    """
    page_content = f"""<style>
{css}
</style>

<div id="pb-audit-page">
{body_html}
</div>"""
    return page_content


def deploy_to_wordpress(content):
    """Deploy content to WordPress via REST API."""
    url = f'{WP_BASE}/pages/{PAGE_ID}'

    payload = {
        'content': content,
        'status': 'publish',
        'template': 'elementor_canvas',
    }

    print(f'Deploying to {url}...')
    response = requests.post(url, headers=HEADERS, json=payload, timeout=30)

    if response.status_code in (200, 201):
        data = response.json()
        print(f'Deploy SUCCESS: HTTP {response.status_code}')
        print(f'Page URL: {data.get("link", "unknown")}')
        return True
    else:
        print(f'Deploy FAILED: HTTP {response.status_code}')
        print(f'Response: {response.text[:500]}')
        return False


def clear_elementor_cache():
    """Clear Elementor's PHP rendering cache after updating page content."""
    url = 'https://purebrain.ai/wp-json/elementor/v1/cache'
    print('Clearing Elementor cache...')
    response = requests.delete(url, headers=HEADERS, timeout=15)
    print(f'Elementor cache clear: HTTP {response.status_code}')
    return response.status_code in (200, 204)


def verify_page():
    """Verify the deployed page returns HTTP 200."""
    import urllib.request
    url = 'https://purebrain.ai/ai-partnership-audit/'
    print(f'Verifying {url}...')
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            status = resp.status
            print(f'Page verification: HTTP {status}')
            return status == 200
    except Exception as e:
        print(f'Verification error: {e}')
        return False


def main():
    print('=== AI Partnership Audit Lead Magnet Fix - WordPress Deploy ===')
    print(f'Source: {HTML_FILE}')
    print(f'Target: purebrain.ai page ID {PAGE_ID}')
    print()

    # Load HTML
    html = load_html()
    print(f'Loaded HTML: {len(html)} chars')

    # Extract parts
    raw_css = extract_css(html)
    body_html = extract_body(html)
    print(f'Extracted CSS: {len(raw_css)} chars')
    print(f'Extracted body: {len(body_html)} chars')

    # Scope CSS for WordPress
    scoped_css = scope_css(raw_css)
    print(f'Scoped CSS: {len(scoped_css)} chars')

    # Build final content
    wp_content = build_wordpress_content(scoped_css, body_html)
    print(f'Final WP content: {len(wp_content)} chars')
    print()

    # Deploy
    success = deploy_to_wordpress(wp_content)
    if not success:
        print('Deployment failed. Aborting.')
        sys.exit(1)

    # Clear Elementor cache
    clear_elementor_cache()

    # Verify
    print()
    verified = verify_page()
    if verified:
        print()
        print('=== DEPLOYMENT COMPLETE ===')
        print('Page: https://purebrain.ai/ai-partnership-audit/')
        print('Fixes deployed:')
        print('  1. .page > .orb position:absolute fix (eliminates dark void layout bug)')
        print('  2. CSS repeating-gradient noise texture (replaces broken SVG feTurbulence)')
        print('  3. All CSS scoped under #pb-audit-page for WordPress theme isolation')
        print('  4. CSS variables replaced with hard values for WP compatibility')
    else:
        print('WARNING: Page verification failed - check manually')
        sys.exit(1)


if __name__ == '__main__':
    main()
