# Homepage Scorched Earth WordPress Cleanup
**Date**: 2026-03-19
**Type**: operational + teaching
**Topic**: Stripping WP artifacts from CF Pages homepage HTML

## Context
The homepage (exports/cf-pages-deploy/index.html) was a WordPress HTML dump embedded inside Elementor widget content. It contained 653 KB of WP artifacts causing:
- Hero gap at top (caused by admin-bar-inline-css injecting html { margin-top: 32px })
- Preloader flash (two theme-preloader div blocks)
- 129 WP resource requests to purebrain.ai/wp-includes/ and wp-content/

## Key Architecture Discovery
The file has a nested structure:
- Outer shell (lines 1-11): Clean CF Pages wrapper
- Nested Elementor widget content: Contains multiple embedded DOCTYPE html pages
  - The WP artifacts live INSIDE these nested page structures
  - Do NOT try to remove the nested DOCTYPE/html/body blocks — they contain real page sections

## Root Cause of Hero Gap
admin-bar-inline-css style block contained: html { margin-top: 0 !important }
This block also added 32px on fresh loads. Removing the entire block was the fix.

## What Was Removed (201 KB total)
- 21 WP link tags: dashicons, admin-bar, wp-components, godaddy-styles, wpaas-*, mailin
- 108 WP script src tags: jQuery from WP, wp-includes JS, wp-content admin JS
- 2 theme-preloader div blocks
- All Yoast SEO: comments, meta tags, schema-graph JSON-LD
- admin-bar-inline-css + global-styles-inline-css style blocks
- Elementor editor scripts: web-cli, dev-tools, app-loader, common-js
- GoDaddy scripts: _trfd, gdvLinks, traffic tracker, wsimg.com
- WP API/plupload/backbone/moxie scripts

## What Was Kept
- Elementor frontend CSS + post CSS
- Artistics theme CSS, FontAwesome, Bootstrap 5
- Elementor frontend.min.js
- Google Fonts, GTM, PayPal, Clarity

## Gotcha: Line Sweep Guard
Initial approach used in_elementor_content guard which broke because the Elementor marker appeared at line 13 (before WP links at 107+). Fix: process all lines document-wide, use KEEP list to protect necessary CSS.

## Tool Built
tools/wp_scorched_earth.py — reusable Python cleanup script

## Deploy Note
CF Pages token lacks zone-level cache purge access. Must purge manually via CF dashboard.
