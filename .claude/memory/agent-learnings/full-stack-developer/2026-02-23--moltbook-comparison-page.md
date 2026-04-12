# PureBrain Comparison Page: Moltbook vs PureBrain

**Date**: 2026-02-23
**Type**: operational
**Topic**: Built and deployed a marketing differentiation page showing PureBrain vs Moltbook/OpenClaw/Clawdbot

---

## What Was Built

Self-contained HTML comparison page for purebrain.ai that positions PureBrain as fundamentally different from (and superior to) platforms like Moltbook, OpenClaw, Clawdbot.

**File**: `/home/jared/projects/AI-CIV/aether/exports/purebrain-comparison-page.html`

---

## WordPress Deployment

- **Site**: purebrain.ai
- **Page ID**: 794
- **Slug**: `why-purebrain`
- **URL**: https://purebrain.ai/?page_id=794 (draft - Jared must publish)
- **Template**: `elementor_canvas`
- **Status**: Draft (pending Jared review)
- **Content size**: 51,422 chars stored

---

## Page Sections Built

1. **Hero** - Stats chips (30+ agents, 4-step pipeline, 100% transparency, real accountability), dual CTA
2. **Trust bar** - 5 trust signals across full width
3. **Problem section** - 4 failure cards: Moltbook, Replika, Character.ai, Spiralism with specific documented failures
4. **Comparison table** - 9-row side-by-side: PureBrain vs "The Others" with check/cross indicators
5. **Bigger/Better section** - 6 capability cards + engineering pipeline visual (BUILD → SECURITY → QA → SHIP)
6. **Philosophy section** - 4 pillars + Jared quote + AI Partnership vs AI Worship 2-col grid
7. **Warning signs** - 12-item buyer's guide checklist (helps readers identify red flags in ANY AI platform)
8. **Final CTA** - dual CTA: Start Your AI Partnership + Take the Free AI Audit

---

## Key Design Decisions

- All competitor comparisons use "The Others" / "Moltbook, OpenClaw, Clawdbot & Similar" — no specific trademark infringement
- All failure claims (Moltbook database exposure, Replika €5M fine, Character.ai lawsuits, Spiralism) are documented public record per the source analysis
- Tone: authoritative and factual — not fear-mongering or messianic (per analysis guardrails)
- Warning Signs section is PureBrain-agnostic — it helps readers evaluate ANY platform including PureBrain itself. This builds trust.
- Philosophy quote from Jared anchors the human accountability narrative

---

## CSS Scoping Pattern Applied

```css
body.page { background-color: #080a12 !important; }
#pb-comparison-page { ... }
#pb-comparison-page * { box-sizing: border-box !important; }
```

All rules scoped under `#pb-comparison-page` with `!important` on critical properties.

---

## Deployment Pattern (Same as Page ID 620)

1. Extract `<style>` block and `<body>` content from HTML
2. Prepend Google Fonts `<link>` tag (was in `<head>`, needs to be in body content for wp:html)
3. Add `body.page { background-color: #080a12 !important; }` override
4. Wrap in `<!-- wp:html --> ... <!-- /wp:html -->`
5. POST to `/wp-json/wp/v2/pages` with `template: elementor_canvas`, `status: draft`
6. Clear Elementor cache: `DELETE /wp-json/elementor/v1/cache`
7. Verify with `GET /wp-json/wp/v2/pages/{id}?context=edit` checking `content.raw` length

---

## Brand Rules Applied

- Logo: `PUREBR` (blue #2a93c1) + `AI` (orange #f1420b) + `N` (blue #2a93c1)
- CTA buttons: orange bg (#f1420b) + white text, hover: blue bg (#2a93c1) + white text
- CTA link: `https://purebrain.ai/#awakening` (CTA LINK RULE)
- Secondary CTA: `https://purebrain.ai/ai-partnership-audit/` (existing page)
- Oswald Bold font for all headings (via Google Fonts)
- Status: DRAFT — Jared reviews before publishing

---

## Source Content Used

`/home/jared/projects/AI-CIV/aether/docs/from-telegram/moltbook-anti-pattern-analysis.md`

This document was the primary source for all failure case details, the AI Partnership vs AI Worship distinction table, and the warning signs list.
