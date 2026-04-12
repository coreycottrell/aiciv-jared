# Migration Portal Quiz Continue Button Fix
**Date**: 2026-02-24
**Type**: gotcha + pattern
**Page**: https://purebrain.ai/migrate/ (WP page ID 800)

## Root Cause: pointer-events: all is Invalid for HTML

The quiz Continue button was permanently disabled because the CSS used:
```css
#pb-migration-quiz .mq-next { pointer-events: none; }
#pb-migration-quiz .mq-next.ready { pointer-events: all; }  /* BUG */
```

`pointer-events: all` is NOT a valid CSS value for HTML elements. It is only valid for SVG elements. The browser silently ignores it, so the `.ready` class override never worked - pointer events stayed `none` forever.

**Fix**: Change to `pointer-events: auto` (the correct CSS value to re-enable events).

## Files Modified
- `/home/jared/projects/AI-CIV/aether/exports/migration-portal-v2-updated.html`

## All Fixes Applied in This Session

1. **pointer-events: all → auto** (quiz Continue button AND portal unlock section - same bug in both places)
2. **SVG glass orbs replaced with brand icon** - Both logo placements (nav 24px, portal 38px) now use `<img src="https://purebrain.ai/wp-content/uploads/2026/02/purebrain-icon-1.png">`
3. **PUREBRAIN color split** - Corrected from `PUREBR`+`AI`+`N` (three spans) to `PUREBR`+`AIN` (two spans: blue + orange)

## Deployment Pattern
- Deployed via Python `requests.post` to `https://purebrain.ai/wp-json/wp/v2/pages/800`
- Auth: Aether user + PUREBRAIN_WP_APP_PASSWORD from .env
- Content field: full HTML with `<!-- wp:html -->` wrapper (already present)
- Verified via `context=edit` GET that raw content deployed correctly

## Key Lesson
When CSS has `pointer-events: none` on an element and you want to re-enable it, always use `pointer-events: auto` NOT `pointer-events: all`. The latter only works in SVG contexts. This is a silent failure - the browser ignores invalid CSS values without errors.
