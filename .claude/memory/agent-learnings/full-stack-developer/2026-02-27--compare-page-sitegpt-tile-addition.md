# Memory: Compare Page — SiteGPT Tile Addition

**Date**: 2026-02-27
**Type**: operational
**Topic**: Adding new comparison page link to /compare/ hub page (page 752)

---

## What Was Done

Added PureBrain vs SiteGPT to the compare hub page (ID 752) at https://purebrain.ai/compare/.

---

## Page Structure (compare/752)

The /compare/ page has two distinct places that must be updated when adding a new VS page:

1. **HTML tile grid** — Clickable tile cards in the tool grid. Located around line ~440 in the page content. Each tile with a deep-dive page gets a `<div class="tile-has-page"><span>Deep dive</span></div>` badge.

2. **TOOLS JavaScript object** — JS data starting around line ~835. Each tool entry has:
   - `icon`, `name`, `color`
   - `good`, `gap`, `diff` (three content panels)
   - `deepDive` — URL string or `null` if no comparison page exists

The JS controls the slide-out panel when a tile is clicked. The `deepDive` property controls whether a "Read full comparison →" button appears.

---

## Where to Insert New Tiles

- Tools WITH a comparison page: Insert before Midjourney (line ~442 area). Midjourney, DALL-E, Gamma, Cursor, Lovable, Notion AI, Salesforce, HubSpot all have `deepDive: null`.
- Tools WITHOUT a comparison page: After HubSpot AI tile (last tile).

---

## Audit Pattern for Future Cross-Link Tasks

When asked to add a new comparison page link to all relevant pages:

1. GET all candidate pages via REST API (context=edit)
2. Search `content.raw` for: `purebrain-vs-`, `/compare`, `switching-from-`, VS tool names
3. The compare page (752) is the ONLY page that cross-links to individual VS pages
4. Individual VS pages (753-760) have NO cross-links to each other — only nav back to /compare/
5. Homepage (11) has a feature comparison TABLE (not VS page links) — different thing entirely
6. Pay-test pages have no comparison links at all

---

## Tool Colors (Avoid Duplicates)

| Tool | Color Used |
|------|-----------|
| ChatGPT | #10a37f |
| Copilot | #0078D4 |
| Gemini | #8E75B2 |
| Claude | #D4A574 |
| DeepSeek | #4D6BFE |
| Perplexity | #20B2AA |
| Jasper | #E8540A |
| Custom GPTs | #10a37f |
| Midjourney | #8A2BE2 |
| DALL-E | #FF6B35 |
| Gamma | #7C5CBF |
| Cursor | #0080FF |
| Lovable | #FF4F64 |
| Notion AI | #000000 |
| Salesforce | #0078C1 |
| HubSpot AI | #FF7A59 |
| **SiteGPT** | **#00B4D8** |
| **Moltbook** | check memory |

Use neutral/approximate brand colors. Avoid exact brand colors (trademark territory).

---

## Verification

- Page 752 updated: HTTP 200
- Content length went from 63,669 → 65,040 chars
- All 5 verification checks passed
