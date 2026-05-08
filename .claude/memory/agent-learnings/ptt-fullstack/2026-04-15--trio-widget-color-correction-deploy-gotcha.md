# Trio Widget Color Correction + Deploy Gotcha

**Date**: 2026-04-15
**Type**: gotcha + operational
**Topic**: Color palette swap on unified Trio chat widget + cf-deploy.py path semantics

## What Happened

Jared issued a mid-build color correction for the unified Trio widget at 777.purebrain.ai:
- Aether: `#2a93c1` blue (unchanged)
- Chy: `#f1420b` orange (was green `#5fbd5f`)
- Morphe: `#0a0a0a` near-black (was orange `#f1420b`, then later in widget header was purple `#a770ef`)
- Jared: `#ffffff` white (unchanged)

## Color Locations (5 in 777-command-center/index.html)

1. Line 8896 — `const TRIO_COLORS = {...}` (inline obeya feed JS)
2. Line 9170 — duplicate inline color map in `obeyaRenderTrioTail()`
3. Line 9213 — `TRIO_WIDGET.ais` chy entry
4. Line 9214 — `TRIO_WIDGET.ais` morphe entry
5. Lines 9415-9416 — header dot swatches `<span style="background:...">`

The widget had at least 3 different palettes mixed in (5fbd5f green, a770ef purple, d4a574 tan, f1420b orange) because of accumulated mid-build edits. **Future**: define a single CSS variable per identity instead of inlining hex 5 times.

## Edit Tool Race Condition

Edit tool repeatedly failed with "File has been modified since read" — file is being touched by a sister process / linter / live editor between every Read and Edit. Solution: **use `sed -i` directly** for files >100KB (per TRIO-SHARED-RULES rule 8) and re-verify with grep after each edit.

## cf-deploy.py Path Gotcha (CRITICAL)

`tools/cf-deploy.py` interprets file path arg as **path RELATIVE TO base-dir**, with default base-dir `exports/cf-pages-deploy/`.

**Wrong**: `cf-deploy.py 777-command-center/index.html`
- Uploads file as `/777-command-center/index.html` (subfolder under site root)
- Site root `index.html` does NOT change → live site appears unchanged
- Preview URL also unchanged (looking at root)

**Right**: `cf-deploy.py --base-dir exports/cf-pages-deploy/777-command-center index.html`
- Uploads file as `/index.html` (site root)
- Live site updates immediately

This is non-obvious and cost ~5min of "why aren't colors live". **Always pass `--base-dir <project-folder>` and the path AS IT SHOULD APPEAR ON THE SITE.**

## Deploy Targets Confirmed

- Project: `777-command-center`
- Custom domain: `777.purebrain.ai`
- Production URL field showed `https://purebrain.ai` (misleading metadata, ignore — actual binding is 777 subdomain)
- Cache headers: `cache-control: public, max-age=0, must-revalidate` + `cf-cache-status: DYNAMIC` → no manual cache flush needed for HTML

## Final Verification

Live `https://777.purebrain.ai/` now serves all 4 identity colors correctly, confirmed via `curl | grep` on TRIO_COLORS, TRIO_WIDGET.ais, and header dot swatches.

## Files

- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/777-command-center/index.html` (lines 8896, 9170, 9213-9214, 9415-9416)
- Backup: `index.html.bak-color-fix-20260415-*`
- Deploy: `https://3d468e24.777-command-center.pages.dev` → `https://777.purebrain.ai/`
