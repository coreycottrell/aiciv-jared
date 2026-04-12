# Memory: PureBrain Mission/Vision/Values Page Build

**Date**: 2026-02-24
**Agent**: full-stack-developer
**Type**: operational + teaching
**Topic**: Self-contained HTML page for PureBrain mission/vision/values — WordPress-ready

---

## What Was Built

File: `/home/jared/projects/AI-CIV/aether/exports/purebrain-mission-vision-values.html`

A full dark-theme HTML page for purebrain.ai covering:
- Hero section with Oswald logo + atmospheric gradient background
- Mission section with blockquote + 6 unpacked phrase cards
- Vision section with blockquote + context paragraphs
- Values section — 7 value cards (Integrity through Love), each with description + "How This Shows Up"
- Brand Promise section with 5 promise bullets as icon cards
- Key Differentiators — 6 feature cards
- CTA → https://purebrain.ai/#awakening
- Sticky nav + gradient footer

## Key Patterns Applied

1. **CSS scoping**: All styles under `#pb-mvv-page` to prevent WordPress theme conflicts
2. **WordPress wrap**: `<!-- wp:html -->` / `<!-- /wp:html -->` around full document
3. **Font loading**: Google Fonts (Oswald + Plus Jakarta Sans) via `<link>` in `<head>`
4. **Brand system**: --bright-orange: #f1420b, --light-blue: #2a93c1, --dark-blue: #3a60ab
5. **Hover states**: Cards lift translateY(-4px) + border-color glow on hover
6. **Blockquote styling**: Left border (orange for mission, blue for vision) + subtle background tint
7. **Section labels**: Small uppercase eyebrow with preceding line decoration

## Source Content

Read from: `/home/jared/projects/AI-CIV/aether/docs/from-telegram/purebrain-mission-vision-values.md`
Used: PART 2 only (PureBrain Mission, Vision & Values)
Excluded: PART 1 (Proof of Understanding) and PART 3 (Hierarchy) — internal docs

## Design Decisions

- Dark gradient hero with radial blue glow from top — matches purebrain.ai aesthetic
- Mission phrase cards: 2-column grid, orange accent on phrase terms
- Value cards: numbered 01–07, tagline in orange, hover lifts card
- Differentiator cards: hover orange instead of blue (visual distinction from values)
- Promise bullets: checkmark circles in dark blue, grid layout
- CTA section: radial orange glow from bottom, orange button with shadow on hover

## Deployment Notes

- Page uses Elementor Canvas template on purebrain.ai (no WordPress header/footer needed — page has its own)
- WordPress REST API: POST to `/wp-json/wp/v2/pages` with `template: "elementor_canvas"`
- Must include `<!-- wp:html -->` wrapper or wpautop will destroy inline styles
