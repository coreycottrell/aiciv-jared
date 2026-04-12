#!/usr/bin/env python3
"""
Scorched Earth WordPress Cleanup for index.html
Removes all WP artifacts from CF Pages homepage (document-wide).
"""

import re

FILE = "/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/index.html"

with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

original_len = len(content)
removals = []

# =========================================================================
# KEEP list: these WP/Elementor resources must NOT be removed
# =========================================================================

KEEP_PATTERNS = [
    r'elementor-icons-css',
    r'elementor-common-css',
    r'elementor-frontend-css',
    r'elementor-post-10-css',
    r'elementor-post-1502-css',
    r'e-theme-ui',
    r'artistic-css-variable',
    r'artistic-style',
    r'artistic-woo',
    r'fontawesome',
    r'bootstrap-5',
    # Elementor frontend JS (needed for rendering)
    r'elementor/assets/js/frontend\.min\.js',
    r'elementor/assets/js/elementor\.min\.js',
    r'elementor/assets/js/libraries/swiper',
]

def should_keep(line):
    for pat in KEEP_PATTERNS:
        if re.search(pat, line, re.IGNORECASE):
            return True
    return False

# =========================================================================
# PASS 1: Line-by-line — remove WP link and script src tags
# =========================================================================

lines = content.split('\n')
out_lines = []
link_removed = 0
script_removed = 0

for line in lines:
    stripped = line.strip()

    # WP <link> tag
    if re.match(r'<link\b', stripped, re.IGNORECASE):
        if re.search(r'purebrain\.ai/(?:wp-includes|wp-content)', stripped):
            if not should_keep(line):
                link_removed += 1
                continue

    # WP <script src> tag (single-line, self-closing with </script>)
    if re.match(r'<script\b', stripped, re.IGNORECASE):
        if re.search(r'purebrain\.ai/(?:wp-includes|wp-content)', stripped):
            if re.search(r'</script>', stripped, re.IGNORECASE):
                if not should_keep(line):
                    script_removed += 1
                    continue

    out_lines.append(line)

content = '\n'.join(out_lines)
removals.append(f"WP <link> tags removed: {link_removed}")
removals.append(f"WP <script src> tags removed: {script_removed}")

# =========================================================================
# PASS 2: Targeted multi-line block removals
# =========================================================================

# --- WP emoji inline style blocks ---
n, c = re.subn(
    r'<style id=["\']wp-emoji-styles-inline-css["\'][^>]*>.*?</style>\n?',
    '', content, flags=re.DOTALL | re.IGNORECASE
)
content = n; removals.append(f"WP emoji inline styles removed: {c}x")

# --- classic-theme-styles inline style ---
n, c = re.subn(
    r'<style id=["\']classic-theme-styles-inline-css["\'][^>]*>.*?</style>\n?',
    '', content, flags=re.DOTALL | re.IGNORECASE
)
content = n; removals.append(f"Classic theme styles inline removed: {c}x")

# --- WP emoji settings + loader script ---
n, c = re.subn(
    r'<script id="wp-emoji-settings"[^>]*>.*?</script>\s*<script>.*?sourceURL=https://purebrain\.ai/wp-includes/js/wp-emoji-loader.*?</script>\n?',
    '', content, flags=re.DOTALL | re.IGNORECASE
)
content = n; removals.append(f"WP emoji script block removed: {c}x")

# --- wpadminbar display:none style overrides ---
# Match <style> blocks that only contain the wpadminbar rule(s)
n, c = re.subn(
    r'<style[^>]*>\s*(?:#wpadminbar\s*\{[^}]+\}\s*)+(?:@media[^{]+\{[^}]*#wpadminbar[^}]*\}[^}]*\}\s*)?\s*</style>\n?',
    '', content, flags=re.DOTALL | re.IGNORECASE
)
content = n; removals.append(f"wpadminbar CSS override style blocks removed: {c}x")

# --- Yoast SEO plugin comment blocks ---
n, c = re.subn(
    r'\n?\s*<!-- This site is optimized with the Yoast SEO plugin[^\-]*-->\n?',
    '', content, flags=re.IGNORECASE
)
content = n; removals.append(f"Yoast SEO comments removed: {c}x")

# --- Yoast schema-graph JSON-LD script blocks ---
n, c = re.subn(
    r'<script type="application/ld\+json" class="yoast-schema-graph">.*?</script>\n?',
    '', content, flags=re.DOTALL | re.IGNORECASE
)
content = n; removals.append(f"Yoast schema-graph JSON-LD removed: {c}x")

# --- Yoast SEO meta/link tags ---
n, c = re.subn(
    r'\n?\s*<(?:meta|link)[^>]+class="yoast-seo-meta-tag"[^>]*/?>',
    '', content, flags=re.IGNORECASE
)
content = n; removals.append(f"Yoast SEO meta tags removed: {c}x")

# --- TWO theme-preloader divs ---
n, c = re.subn(
    r'\t?<div class="theme-preloader" style="[^"]*">\s*'
    r'<div class="loading-container"[^>]*>\s*'
    r'<div class="loading"></div>\s*'
    r'<div id="loading-icon">[^<]*<img[^>]*>[^<]*</div>\s*'
    r'</div>\s*'
    r'</div>\n?',
    '', content, flags=re.DOTALL | re.IGNORECASE
)
content = n; removals.append(f"theme-preloader blocks removed: {c}x")

# --- Elementor editor script blocks (web-cli, dev-tools, app-loader, common) ---
EDITOR_SCRIPT_IDS = [
    'elementor-web-cli-js-before', 'elementor-web-cli-js',
    'elementor-dev-tools-js-before', 'elementor-dev-tools-js',
    'elementor-app-loader-js-before', 'elementor-app-loader-js',
    'elementor-common-js-before', 'elementor-common-js', 'elementor-common-js-after',
]
editor_removed = 0
for sid in EDITOR_SCRIPT_IDS:
    n, c = re.subn(
        r'<script\b[^>]*\bid=["\']' + re.escape(sid) + r'["\'][^>]*>.*?</script>\n?',
        '', content, flags=re.DOTALL | re.IGNORECASE
    )
    content = n; editor_removed += c
removals.append(f"Elementor editor script blocks removed: {editor_removed}x")

# --- WP API / plupload / wpaas script blocks ---
WP_SCRIPT_IDS = [
    'wp-api-request-js-extra', 'wp-api-request-js',
    'wp-api-fetch-js', 'wp-api-fetch-js-after',
    'wp-backbone-js', 'utils-js', 'moxiejs-js', 'plupload-js',
    'wpaas-stock-photos-js-extra', 'sib-front-js-js',
    'jquery-core-js', 'jquery-migrate-js',
]
wp_api_removed = 0
for sid in WP_SCRIPT_IDS:
    n, c = re.subn(
        r'<script\b[^>]*\bid=["\']' + re.escape(sid) + r'["\'][^>]*>.*?</script>\n?',
        '', content, flags=re.DOTALL | re.IGNORECASE
    )
    content = n; wp_api_removed += c
removals.append(f"WP API/plupload/wpaas script blocks removed: {wp_api_removed}x")

# --- GoDaddy/wpaas inline data scripts ---
n, c = re.subn(
    r'<script[^>]*>\s*(?:var _trfd|var gdvLinks)\s*=.*?</script>\n?',
    '', content, flags=re.DOTALL | re.IGNORECASE
)
content = n; removals.append(f"GoDaddy _trfd/gdvLinks scripts removed: {c}x")

# --- wsimg.com traffic/tracking scripts ---
n, c = re.subn(
    r"<script src='https://img1\.wsimg\.com/[^']*'[^>]*></script>\n?",
    '', content, flags=re.IGNORECASE
)
content = n; removals.append(f"wsimg.com script tags removed: {c}x")

n, c = re.subn(
    r"<script>window\.addEventListener\('click', function \(elem\).*?</script>\n?",
    '', content, flags=re.DOTALL | re.IGNORECASE
)
content = n; removals.append(f"GoDaddy click tracking script removed: {c}x")

# --- wpadminbar HTML div ---
n, c = re.subn(
    r'<div id="wpadminbar"[^>]*>.*?</div>\s*(?:<!-- /wpadminbar -->)?\n?',
    '', content, flags=re.DOTALL | re.IGNORECASE
)
content = n; removals.append(f"wpadminbar HTML div removed: {c}x")

# --- speculationrules block ---
n, c = re.subn(
    r'<script type="speculationrules">.*?</script>\n?',
    '', content, flags=re.DOTALL | re.IGNORECASE
)
content = n; removals.append(f"speculationrules removed: {c}x")

# --- Speed Optimizer script ---
n, c = re.subn(
    r'<script>\s*// Do not change this comment line otherwise Speed Optimizer.*?</script>\n?',
    '', content, flags=re.DOTALL | re.IGNORECASE
)
content = n; removals.append(f"Speed Optimizer script removed: {c}x")

# --- admin-bar and logged-in classes from body tags ---
n, c = re.subn(r'(<body\b[^>]*\bclass="[^"]*)\badmin-bar\b\s?', r'\1', content)
content = n; removals.append(f"admin-bar class removed from body: {c}x")

n, c = re.subn(r'(<body\b[^>]*\bclass="[^"]*)\blogged-in\b\s?', r'\1', content)
content = n; removals.append(f"logged-in class removed from body: {c}x")

# --- elementor-wp-admin-bar CSS link (any remaining) ---
n, c = re.subn(
    r'<link[^>]+elementor-wp-admin-bar[^>]+>\n?',
    '', content, flags=re.IGNORECASE
)
content = n; removals.append(f"elementor-wp-admin-bar CSS removed: {c}x")

# =========================================================================
# Write output
# =========================================================================

with open(FILE, "w", encoding="utf-8") as f:
    f.write(content)

new_len = len(content)
print(f"SCORCHED EARTH COMPLETE")
print(f"Original size: {original_len:,} bytes ({original_len // 1024} KB)")
print(f"New size:      {new_len:,} bytes ({new_len // 1024} KB)")
print(f"Removed:       {original_len - new_len:,} bytes ({(original_len - new_len) // 1024} KB)")
print(f"\nRemovals log:")
for r in removals:
    print(f"  - {r}")
