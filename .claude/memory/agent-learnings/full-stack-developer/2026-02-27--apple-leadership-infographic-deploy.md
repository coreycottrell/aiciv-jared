# Apple Leadership Infographic — Two Eras

**Date**: 2026-02-27
**Type**: operational + teaching
**Topic**: Built self-contained HTML infographic comparing Steve Jobs vs Tim Cook Apple eras; deployed to page 993

---

## File Delivered

`/home/jared/projects/AI-CIV/aether/exports/apple-leadership-infographic.html`

699 lines / 26KB. Self-contained HTML/CSS/SVG/JS. No external images.

---

## What Was Built

Two macOS-window-chrome panels stacked vertically:

- **Panel 1 (Jobs)**: Blue color scheme, 15-bar SVG chart (1997-2011), milestone dots for iPhone/iPad, product icon chips row
- **Panel 2 (Cook)**: Green color scheme, 15-bar SVG chart (2011-2025), milestone dots for M1/Vision Pro, product icon chips row
- **Insight callout**: Gradient border box below both panels explaining Cook's 10x multiplier thesis
- Scroll-in animation via IntersectionObserver (panels fade+translateY in)
- macOS chrome dots: #FF5F57 / #FFBD2E / #28C840

---

## Deployment

Inserted into page 993 (purebrain.ai/your-ai-tim-cook/) between:
- **AFTER**: Section 2 (The Problem — Hero's Delusion) closing `</section>`
- **BEFORE**: `<!-- SECTION 3: SOUL vs SKELETON FRAMEWORK -->` comment

Wrapped in: `<div style="width:100%;max-width:1200px;margin:0 auto 48px;padding:0 24px;box-sizing:border-box;">`

---

## SVG Bar Chart Pattern

All bars use viewBox="0 0 680 200". Bar width = 32px, total x-space per bar = 45.3px (15 bars × 45.3 = 679.5).
Y scale: value / maxValue * 200. Bar y = 200 - height, with 0.2px minimum floor to keep visible.

Key formula:
- Jobs: scale = 200/347 = 0.576. Height for $174B = 100.1px
- Cook: scale = 200/3700 = 0.054. Height for $3700B = 199.8px

---

## Scoping Pattern

Infographic CSS scoped under `#tc-apple-infographic`. White/light backgrounds contrast against page's dark `#0d1117` background. Uses `#pb-tc-page` page's existing `tc-reveal` class for scroll-in on the image containers already on page.

---

## Gotchas

1. **SVG bar animation**: CSS transitions on `height` and `y` attributes only work if the initial values are set in the SVG (not animated from 0). Set bars at their real values in HTML — the IntersectionObserver fade handles the reveal.
2. **Y-axis labels**: Positioned absolutely outside the SVG using flexbox column. Must match SVG viewBox height exactly.
3. **macOS dots order**: Red, Yellow, Green (not RGB). #FF5F57, #FFBD2E, #28C840.
4. **Insertion into existing page**: Use Python `str.replace(marker, insert + marker, 1)` — the `1` count is critical to only replace once.
5. **amplify-founder image preserved**: Confirmed present after update. Always verify existing images survive PUT operations.
