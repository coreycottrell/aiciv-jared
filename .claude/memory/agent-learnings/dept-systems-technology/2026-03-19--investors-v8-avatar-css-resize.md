# investors-v8 Avatar CSS Resize

**Date**: 2026-03-19
**Type**: operational
**Topic**: Avatar wrapper size increase + tight ring pattern

## What Was Done

Resized `#aether-avatar-wrap` in `/exports/cf-pages-deploy/investors-v8/index.html`:
- Desktop: 350px → 630px (1.8x per Jared spec)
- Mobile: 250px → 350px

## Key Pattern: Tight-Fitting Ring

The iframe inside `#aether-avatar-wrap` already had `position:absolute;inset:0;width:100%;height:100%` — this means it fills the wrapper exactly. Combined with `border-radius:50%;overflow:hidden` already on the wrapper, no extra CSS was needed for the tight ring. Just resizing the wrapper was sufficient.

## Edit Method Note

The Edit tool requires Read tool to be called first. For quick targeted changes to large HTML files, `sed -i` is faster. Used two separate `sed -i` commands:
1. Target the size line inside `#aether-avatar-wrap`
2. Target the mobile media query line

## Files Modified
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/investors-v8/index.html` (lines ~533-542)

## Deploy
- Target: `purebrain-staging`
- Result: Success, 0 new files uploaded (already cached)
