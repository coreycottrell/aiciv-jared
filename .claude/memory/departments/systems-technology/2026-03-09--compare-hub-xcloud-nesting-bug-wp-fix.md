# Compare Hub xCloud Nesting Bug Fix — WordPress Sync

**Date**: 2026-03-09
**Type**: gotcha / fix
**Topic**: WordPress compare hub page (ID 752) missing closing div on xCloud tile

## Bug

Page: `https://purebrain.ai/compare/` (WP page ID 752, slug: `compare`)

xCloud tile was missing its closing `</div>` tag. This caused all 5 subsequent tiles
(OpenClaw, Enso.bot, Supercool/Deal.ai, Billie Review, Boardy.ai) to be nested INSIDE
the xCloud tile's DOM node instead of being sibling grid tiles.

## Root Cause

The Vercel version (`/public/compare/index.html`) had already been fixed with a proper
closing `</div>` on the xCloud tile. The WordPress version never received that fix —
the two versions had drifted out of sync.

## Fix Applied

In `/tmp/wp_compare_hub.html` (fetched via WP REST API), changed:

```html
<!-- BEFORE (missing </div> on xCloud tile) -->
      <div class="tile-cta-hint">Click to see full comparison &rarr;</div>

    <div class="tool-tile" style="--tile-color:#E84B3A" onclick="openPanel('openclaw')">

<!-- AFTER (closing div added) -->
      <div class="tile-cta-hint">Click to see full comparison &rarr;</div>
    </div>

    <div class="tool-tile" style="--tile-color:#E84B3A" onclick="openPanel('openclaw')">
```

## Deployment

- Fetched live content via `GET /wp-json/wp/v2/pages/752`
- Applied fix to local copy
- Redeployed via `POST /wp-json/wp/v2/pages/752` with full content payload
- Verified live: all 6 tiles (xcloud, openclaw, enso, supercool, billiereview, boardy) present as siblings

## New Rule Established

From 2026-03-09: ALL changes to Vercel site MUST also be applied to WordPress, and vice versa.
Both versions must stay in sync until full Vercel migration is complete.

## WP API Pattern

- Auth: `purebrain@puremarketing.ai` + app password from `.env` `PUREBRAIN_WP_APP_PASSWORD`
- Compare hub page ID: 752
- Large payloads: use `--data-binary @/tmp/file.json` (not inline `-d`) to avoid shell quoting issues
- Template: `elementor_canvas` (confirmed correct for this page)
