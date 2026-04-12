# Portal Light Mode: Commands & Shortcuts Panel Fix

**Date**: 2026-03-20
**Type**: teaching
**Topic**: Portal CSS light mode gap — Commands panel dark-themed while rest of portal was light

## What Was Wrong

The portal has a `body.light-mode` CSS class system with overrides at the top of `portal-pb-styled.html`. The Commands & Troubleshooting panel appeared still in dark mode because several key elements had hardcoded dark-mode colors with no light mode override:

- `.cmd-section-title` — `color: #22c55e` (dark mode neon green) with no light override
- `.cmd-warn` — dark amber background with no light override
- `.cmd-ref-table th` — dark border, no light override
- `.cmd-panel-header` — no explicit light background override
- `.sc-panel-header` — no explicit light background override
- `.sc-section-title` — no light override
- `.sc-table th` — no light override
- `.sc-cmd` — slash command pills had no light override
- `.sc-tab-card` — no light override

## The Fix

Added 10 new `body.light-mode` CSS rule blocks in `portal-pb-styled.html`. Key decisions:

- Section titles: `#1a6a91` (PT Blue dark, readable on light bg)
- Warning blocks: amber-on-white variant (`rgba(180,130,0,0.08)` bg, `#7a5800` text)
- Panel headers: `var(--surface)` (white in light mode)
- All borders: `var(--border)` (resolves to `#c8ccdc` in light mode)

## File Changed

`/home/jared/purebrain_portal/portal-pb-styled.html`

## Pattern: How Light Mode Works in This Portal

1. CSS variables defined in `:root` for dark mode defaults
2. `body.light-mode` block (~line 49) overrides core variables
3. Individual component overrides in blocks labeled `/* ===== LIGHT MODE: [PANEL] ===== */`
4. When adding new components, ALWAYS add `body.light-mode` overrides for hardcoded dark colors

## Commands content is dynamic

Content fetched from `/api/commands`, rendered by `static/commands-shortcuts.js`. CSS classes in JS match classes in portal HTML. No JS changes needed — CSS handles it.

## Deployment

- Committed and pushed to `git@github-interciv:coreycottrell/purebrain-portal.git main`
- Portal restarted, healthy on port 8097
