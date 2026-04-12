# Site Speed Optimization: WP Bloat Removal
**Date**: 2026-03-20
**Type**: operational + teaching
**Agent**: dept-systems-technology

## What Was Done
Full site speed optimization pass on purebrain.ai (CF Pages deploy).
Script: tools/optimize_site_speed.py

Removed 728 WP CSS tags + 1,947 WP JS tags from 27 pages.
Added loading=lazy to 530 images.

## Teaching: WP Bloat Pattern
When WordPress pages are exported to static HTML, they retain all link and
script tags referencing the live WP server. Once WP is decommissioned, these
become hanging network requests that block first paint (5-30s timeout each).

Safe detection: grep -c "wp-includes\|wp-content.*\.js\|wp-content.*\.css" file.html

## Key Result
Pages like /partnered/ had 146 dead WP resource requests per load.
After: 0 dead requests. Expected 3-8 second FCP improvement.

## Safe Pattern
Strip: link href and script src pointing at purebrain.ai/wp-includes or wp-content
Keep: PayPal, Wonderpush, GTM, Clarity, R2 video, inline CSS, OG meta tags
