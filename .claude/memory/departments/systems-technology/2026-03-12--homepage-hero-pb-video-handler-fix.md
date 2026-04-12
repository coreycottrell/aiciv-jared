# Homepage Hero Fix: pb-video-handler-css Clone from pay-test-2

**Date**: 2026-03-12
**Type**: bug-fix, CSS-sync
**Agent**: dept-systems-technology

## Root Cause Found

The homepage had `pb-video-handler-css` v1.4.0/v1.5.0 while pay-test-2 had v1.3.0. The newer versions introduced:
1. iOS play button hide CSS (`.video-background__video::-webkit-media-controls-*`)
2. `body.video-playing` conditional hiding of living-background (instead of always hiding it on mobile)
3. Keeping vortex rings visible on mobile as iOS fallback (v1.5.0 change)

This broke the mobile appearance and caused visual inconsistency vs pay-test-2.

## What Was Different: Homepage vs pay-test-2

| Element | pay-test-2 | homepage (broken) |
|---------|------------|-------------------|
| `pb-video-handler-css` | v1.3.0 | v1.4.0 (wrong) |
| Mobile living-background | Always hidden | Only hidden when `body.video-playing` |
| Vortex on mobile | Removed from DOM entirely | Only hidden with `body.video-playing` conditional |
| `outer-shell-reset` | Had immediate preloader hide | Did NOT have immediate preloader hide |
| HTML margin-top | `margin-top: 0 !important` | Missing (added by WP admin bar) |

## Fixes Applied

1. **pb-video-handler-css reverted to v1.3.0** - matches pay-test-2 exactly
   - Removed iOS play button pseudo-element CSS
   - Restored always-hide living-background on mobile (not conditional on video-playing)
   - Restored unconditional vortex/particles hide on mobile
2. **outer-shell-reset enhanced** - added:
   - `html { margin-top: 0 !important }` - prevents admin bar gap
   - Immediate preloader hide CSS (matching pay-test-2's cf-pages-flash-fix)
3. **JS mobile block updated** - matches pay-test-2:
   - Physically removes `.portal-vortex` and `.hero__particles` from DOM
   - Force-hides living-background with inline `!important` styles

## Key Lesson

When "clone from pay-test-2" is the directive, diff ALL style blocks including `pb-video-handler-css`. The CSS block versions are significant - v1.3.0 is the known-good baseline for the hero background design.

## Files Changed

- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/index.html`

## Deployment

Cloudflare Pages staging: https://5d6a65a9.purebrain-staging.pages.dev/
