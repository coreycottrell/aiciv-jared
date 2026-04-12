# Bypass Blocker v2.0 — Blocking All Three Plugin Bypass Methods

**Date**: 2026-03-01
**Type**: fix + pattern
**Pages affected**: 11 (homepage), 688 (pay-test-sandbox-2), 689 (pay-test-2 LIVE)

---

## Problem

Bypass code on purebrain.ai homepage (page 11) was triggering duplicate messages and buttons.
Root cause: the plugin has THREE bypass methods but the v1.0 blocker only blocked two.

### Plugin's Three Bypass Methods

1. **Method 1**: Document-level capturing-phase `submit` handler (checks `isBypassCode`)
2. **Method 2**: Document-level capturing-phase `keydown` handler (checks `isBypassCode`)
3. **Method 3**: URL parameter check `window.location.search.indexOf('bypass=true')` — runs directly in IIFE, not event-based

The v1.0 blocker overrode `addEventListener` to block Methods 1 and 2, but Method 3 ran regardless.

Additionally, plugin's `executeBypass()` calls `showPersonalizedCapabilities()` which duplicated what the chatbox's own bypass flow does. Result: BOTH plugin and chatbox ran, creating duplicate messages and buttons.

---

## Solution: Bypass Blocker v2.0

Three-layer fix:

1. **Method 3 block**: Before plugin IIFE runs, remove `bypass=true` from URL using `history.replaceState()`. Save original URL to `window.__pb_original_bypass_url` in case chatbox needs it.
2. **Methods 1+2 block**: Same `addEventListener` override as v1.0.
3. **Safety net**: Wrap `showPersonalizedCapabilities` with `Object.defineProperty` getter/setter so it only fires once even if called multiple times.

---

## Deployment Pattern

The bypass blocker lives in `_elementor_data` (NOT `content.raw` or the security plugin).

**Key facts**:
- Elementor data is double-encoded: quotes appear as `\\"` and newlines as `\\n` in Python strings
- Closing `</script>` tag is NOT escaped in elementor_data (no `\\/`)
- Locate script: `el_data.rindex('<script', 0, el_data.index('pb-bypass-blocker'))`
- Close tag: `el_data.index('</script>', script_tag_start)`

**Page 688 gotcha**: The first attempt with `json={'meta': {'_elementor_data': el_data[:100]}}` TRUNCATED the page data and returned 200. The REST API accepted the truncated data without complaint. Recovery: use the most recent revision's `_elementor_data` (fetch via `/revisions/{id}?context=edit`, revision meta includes `_elementor_data`).

**After deploy**: Always `DELETE /elementor/v1/cache` to flush Elementor's rendered HTML cache.

---

## Verification Checklist

For each page after deploy:
- `_elementor_data` length > 50000 chars (confirms not truncated)
- `Bypass Blocker v2.0` present
- `Bypass Blocker v1.0` not present
- `BLOCK METHOD 3` present (URL stripping)
- `showPersonalizedCapabilities` present (safety net)

---

## Files

The bypass blocker is embedded in `_elementor_data` on:
- Page 11: `https://purebrain.ai/` (homepage)
- Page 688: `https://purebrain.ai/pay-test-sandbox-2/`
- Page 689: `https://purebrain.ai/pay-test-2/` (LIVE customer-facing)
