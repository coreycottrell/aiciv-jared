#!/usr/bin/env python3
"""
Strip WordPress admin/editor bloat from CF Pages HTML files.
Removes external WP scripts and stylesheets that cause timeout delays on CF Pages.
Preserves all actual page content, Elementor frontend CSS/JS (needed for layout),
Google Fonts, Clarity, PayPal, and custom page scripts.
"""

import re
import sys

# Patterns for scripts to REMOVE (bloat that causes external request timeouts)
SCRIPT_REMOVE_PATTERNS = [
    # WP admin bar
    r'<script[^>]*wp-includes/js/utils\.min\.js[^>]*>.*?</script>',
    r'<script[^>]*gd-system-plugin/assets/js/admin-bar[^>]*>.*?</script>',
    r'<script[^>]*wp-includes/js/admin-bar\.min\.js[^>]*>.*?</script>',
    r'<script[^>]*wp-includes/js/hoverintent-js\.min\.js[^>]*>.*?</script>',
    # Plupload (file upload lib - not needed on CF Pages)
    r'<script[^>]*wp-includes/js/plupload/moxie\.min\.js[^>]*>.*?</script>',
    r'<script[^>]*wp-includes/js/plupload/plupload\.min\.js[^>]*>.*?</script>',
    r'<script[^>]*wp-includes/js/plupload/wp-plupload\.min\.js[^>]*>.*?</script>',
    # GoDaddy publish guide
    r'<script[^>]*godaddy-launch/build/publish-guide\.js[^>]*>.*?</script>',
    # Mailin/Brevo form JS (not needed)
    r'<script[^>]*plugins/mailin/js/mailin-front\.js[^>]*>.*?</script>',
    # Backbone/Marionette/Underscore (Elementor editor, not frontend)
    r'<script[^>]*wp-includes/js/backbone\.min\.js[^>]*>.*?</script>',
    r'<script[^>]*wp-includes/js/underscore\.min\.js[^>]*>.*?</script>',
    r'<script[^>]*plugins/elementor/assets/lib/backbone/backbone\.marionette\.min\.js[^>]*>.*?</script>',
    r'<script[^>]*plugins/elementor/assets/lib/backbone/backbone\.radio\.min\.js[^>]*>.*?</script>',
    # Elementor editor/admin scripts (not needed for frontend display)
    r'<script[^>]*plugins/elementor/assets/js/web-cli\.min\.js[^>]*>.*?</script>',
    r'<script[^>]*plugins/elementor/assets/js/dev-tools\.min\.js[^>]*>.*?</script>',
    r'<script[^>]*plugins/elementor/assets/js/app-loader\.min\.js[^>]*>.*?</script>',
    r'<script[^>]*plugins/elementor/assets/lib/dialog/dialog\.min\.js[^>]*>.*?</script>',
    r'<script[^>]*plugins/elementor/assets/js/elementor-admin-bar\.min\.js[^>]*>.*?</script>',
    # WP media library (not needed)
    r'<script[^>]*wp-includes/js/media-models\.min\.js[^>]*>.*?</script>',
    r'<script[^>]*wp-includes/js/media-views\.min\.js[^>]*>.*?</script>',
    r'<script[^>]*wp-includes/js/media-editor\.min\.js[^>]*>.*?</script>',
    r'<script[^>]*wp-includes/js/media-audiovideo\.min\.js[^>]*>.*?</script>',
    r'<script[^>]*wp-includes/js/mediaelement/mediaelement-and-player\.min\.js[^>]*>.*?</script>',
    r'<script[^>]*wp-includes/js/mediaelement/mediaelement-migrate\.min\.js[^>]*>.*?</script>',
    r'<script[^>]*wp-includes/js/mediaelement/wp-mediaelement\.min\.js[^>]*>.*?</script>',
    # WP clipboard
    r'<script[^>]*wp-includes/js/clipboard\.min\.js[^>]*>.*?</script>',
    # WP REST/API scripts (not needed on CF Pages)
    r'<script[^>]*wp-includes/js/api-request\.min\.js[^>]*>.*?</script>',
    r'<script[^>]*wp-includes/js/shortcode\.min\.js[^>]*>.*?</script>',
    r'<script[^>]*wp-includes/js/wp-util\.min\.js[^>]*>.*?</script>',
    r'<script[^>]*wp-includes/js/wp-backbone\.min\.js[^>]*>.*?</script>',
    # jQuery UI (editor-level, not needed for Elementor frontend)
    r'<script[^>]*wp-includes/js/jquery/ui/core\.min\.js[^>]*>.*?</script>',
    r'<script[^>]*wp-includes/js/jquery/ui/mouse\.min\.js[^>]*>.*?</script>',
    r'<script[^>]*wp-includes/js/jquery/ui/draggable\.min\.js[^>]*>.*?</script>',
    r'<script[^>]*wp-includes/js/jquery/ui/sortable\.min\.js[^>]*>.*?</script>',
    # WP blocks (Gutenberg) - not needed, using Elementor
    r'<script[^>]*wp-includes/js/dist/(?:vendor/lodash|vendor/react(?:-dom|-jsx-runtime)?|url|api-fetch|blob|block-serialization-default-parser|autop|deprecated|dom|escape-html|element|is-shallow-equal|keycodes|priority-queue|compose|private-apis|redux-routine|data|html-entities|rich-text|shortcode|warning|blocks|vendor/moment|date|primitives|components|keyboard-shortcuts|commands|notices|preferences-persistence|preferences|style-engine|token-list|block-editor|core-data|media-utils|patterns|plugins|server-side-render|viewport|wordcount|editor|dom-ready|a11y|hooks|i18n)\.min\.js[^>]*>.*?</script>',
    # WP stock photos (GoDaddy)
    r'<script[^>]*mu-plugins/vendor/wpex/stock-photos/assets/js/stock-photos\.min\.js[^>]*>.*?</script>',
    # Elementor common/common-modules (editor-level)
    r'<script[^>]*plugins/elementor/assets/js/common-modules\.min\.js[^>]*>.*?</script>',
    r'<script[^>]*plugins/elementor/assets/js/common\.min\.js[^>]*>.*?</script>',
]

# Patterns for inline script extras to REMOVE
INLINE_SCRIPT_REMOVE_PATTERNS = [
    r'<script id="utils-js-extra"[^>]*>.*?</script>',
    r'<script id="sib-front-js-js-extra"[^>]*>.*?</script>',
]

# Patterns for link/stylesheet tags to REMOVE (admin/editor CSS not needed on CF Pages)
LINK_REMOVE_PATTERNS = [
    # Admin bar CSS
    r"<link[^>]*id='admin-bar-css'[^>]*/>",
    r"<link[^>]*id='dashicons-css'[^>]*/>",
    # GoDaddy
    r"<link[^>]*id='godaddy-styles-css'[^>]*/>",
    r"<link[^>]*id='GoDaddy\\WordPress\\Plugins\\Launch\\PublishGuidepublish-guide-css'[^>]*/>",
    r"<link[^>]*id='wpaas-admin-bar-css'[^>]*/>",
    r"<link[^>]*id='wpaas-admin-bar-specific-css'[^>]*/>",
    r"<link[^>]*id='wpaas-stock-photos-css'[^>]*/>",
    # Yoast admin bar
    r"<link[^>]*id='yoast-seo-adminbar-css'[^>]*/>",
    # Elementor admin bar
    r"<link[^>]*id='elementor-wp-admin-bar-css'[^>]*/>",
    # Elementor editor-level CSS (not needed for frontend rendering)
    r"<link[^>]*id='elementor-common-css'[^>]*/>",
    r"<link[^>]*id='e-theme-ui-light-css'[^>]*/>",
    # WP components (Gutenberg editor)
    r"<link[^>]*id='wp-components-css'[^>]*/>",
    # WP media
    r"<link[^>]*id='mediaelement-css'[^>]*/>",
    r"<link[^>]*id='wp-mediaelement-css'[^>]*/>",
    r"<link[^>]*id='media-views-css'[^>]*/>",
    r"<link[^>]*id='imgareaselect-css'[^>]*/>",
    # WP buttons (editor)
    r"<link[^>]*id='buttons-css'[^>]*/>",
    # Mailin/Brevo form CSS
    r"<link[^>]*id='sib-front-css-css'[^>]*/>",
]

# Link tags without clean IDs that match href patterns to remove
LINK_HREF_REMOVE_PATTERNS = [
    r"<link[^>]*href='https://purebrain\.ai/wp-content/mu-plugins/vendor/wpex/godaddy-launch/build/publish-guide\.css'[^>]*/>",
    r"<link[^>]*href='https://purebrain\.ai/wp-content/mu-plugins/gd-system-plugin/assets/css/admin-bar[^']*'[^>]*/>",
    r"<link[^>]*href='https://purebrain\.ai/wp-content/mu-plugins/vendor/wpex/stock-photos[^']*'[^>]*/>",
]

# Inline style blocks that are zero-functional (admin bar override already handled)
INLINE_STYLE_REMOVE_PATTERNS = [
    r'<style id=[\'"]admin-bar-inline-css[\'"][^>]*>.*?</style>',
    r'<style id=[\'"]classic-theme-styles-inline-css[\'"][^>]*>.*?</style>',
    r'<style id=[\'"]wp-emoji-styles-inline-css[\'"][^>]*>.*?</style>',
    r'<style id=[\'"]wp-img-auto-sizes-contain-inline-css[\'"][^>]*>.*?</style>',
]


def strip_bloat(html: str) -> str:
    original_len = len(html)

    # Remove inline script extras first (must be before the main script removal)
    for pattern in INLINE_SCRIPT_REMOVE_PATTERNS:
        html = re.sub(pattern, '<!-- [BLOAT REMOVED: wp-extra-inline-script] -->', html, flags=re.DOTALL)

    # Remove bloat script tags
    for pattern in SCRIPT_REMOVE_PATTERNS:
        html = re.sub(pattern, '<!-- [BLOAT REMOVED: wp-script] -->', html, flags=re.DOTALL | re.IGNORECASE)

    # Remove bloat link/stylesheet tags (self-closing)
    for pattern in LINK_REMOVE_PATTERNS:
        html = re.sub(pattern, '<!-- [BLOAT REMOVED: wp-stylesheet] -->', html, flags=re.DOTALL)

    for pattern in LINK_HREF_REMOVE_PATTERNS:
        html = re.sub(pattern, '<!-- [BLOAT REMOVED: wp-stylesheet-href] -->', html, flags=re.DOTALL)

    # Remove bloat inline style blocks
    for pattern in INLINE_STYLE_REMOVE_PATTERNS:
        html = re.sub(pattern, '<!-- [BLOAT REMOVED: wp-inline-style] -->', html, flags=re.DOTALL)

    new_len = len(html)
    saved = original_len - new_len
    print(f"Original: {original_len:,} bytes | Stripped: {new_len:,} bytes | Saved: {saved:,} bytes ({saved/original_len*100:.1f}%)", file=sys.stderr)
    return html


if __name__ == '__main__':
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else input_path

    with open(input_path, 'r', encoding='utf-8') as f:
        html = f.read()

    cleaned = strip_bloat(html)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(cleaned)

    print(f"Written to: {output_path}", file=sys.stderr)
