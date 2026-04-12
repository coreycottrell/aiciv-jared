# Portal Context Window Modal Light Mode Fix

**Date**: 2026-03-20
**Type**: operational

## Problem

In light mode, the Context Window modal (`.ctx-popup`) had hardcoded `color: #ffffff` on:
- `.ctx-popup p` — body paragraph text
- `.ctx-popup .ctx-tips li` — checkmark bullet items

These rendered as white text on the light `--surface2` (#e8eaf2) background, making them invisible.

## Root Cause

CSS file: `/home/jared/purebrain_portal/portal-pb-styled.html` (lines ~1362-1374)
Rules were hardcoded with `color: #ffffff` instead of using `var(--text)` or having light-mode overrides.

## Fix Applied

Added `body.light-mode` overrides in the light mode CSS section (after `/* END LIGHT MODE: QUICK FIRE PILLS */` at ~line 790):

```css
body.light-mode .ctx-popup { background: #ffffff; border-color: var(--border2); }
body.light-mode .ctx-popup p { color: #1a1d2e; }
body.light-mode .ctx-popup .ctx-tips li { color: #1a1d2e; }
body.light-mode .ctx-popup .ctx-tips li::before { color: #16a34a; }
body.light-mode .ctx-popup h3 { color: #0e7a3a; }
```

## Pattern

When a new modal is added in dark mode with hardcoded white text colors, always add corresponding `body.light-mode` overrides. Check for `color: #ffffff` or `color: #fff` in modal-specific CSS rules.

## Restart

`bash /home/jared/purebrain_portal/restart.sh` — portal healthy on port 8097.
