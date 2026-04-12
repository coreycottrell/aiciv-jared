# CF Pages WordPress Bloat Strip Pattern
**Date**: 2026-03-19
**Type**: operational + teaching

## Problem Pattern
When WordPress pages are exported as HTML by a logged-in admin, the export includes ~109 external script/stylesheet requests pointing to wp-includes/ and wp-content/ on the WP server. On CF Pages, every one of these either times out (worst case) or succeeds (fast case). Timeout scenario causes severe page lag.

## Root cause categories of bloat
1. Gutenberg/WP Blocks stack (30+ js/dist/*.min.js)
2. WP Media Library (media-views, mediaelement player)
3. Plupload file upload lib
4. Elementor EDITOR scripts (web-cli, dev-tools, app-loader, dialog, common)
5. WP Admin Bar JS + GoDaddy admin bar JS
6. Backbone/Underscore/Marionette
7. GoDaddy plugins (publish-guide.js, stock-photos.js)
8. Mailin/Brevo form JS/CSS
9. jQuery UI editor-level (draggable, mouse, sortable)
10. Admin CSS (dashicons, wpaas, yoast adminbar, elementor admin bar)

## Tool
/home/jared/projects/AI-CIV/aether/tools/strip_wp_bloat.py [input] [output]

## Impact on sandbox-3
116 resources removed. 849KB -> 837KB. 87 fewer stalling external requests.

## Homepage status
index.html has same 109 WP scripts — not yet fixed as of 2026-03-19.
