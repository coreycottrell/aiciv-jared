# Invitation Page Enhancement — Readability + Discovery Widget
**Date**: 2026-02-27
**Agent**: dept-systems-technology
**Type**: pattern + build record
**Page**: https://purebrain.ai/invitation/ (WP page ID 987)

---

## What Was Built

### Improvement 1: Text Readability Over Brain Background
- Added `#pb-content-overlay` div: fixed positioned, z-index 1, between canvas (z:0) and page (z:2)
- Gradient: transparent at top (hero shows brain fully), dark blue starting at 20-35% viewport height
- Approach: dark gradient rather than solid PT blue cover — preserves visual design while dimming brain behind text sections
- Also strengthened `text-shadow` on `.pb-h1`, `.pb-h2`, body text classes
- Boosted `.pb-glass-lt` / `.pb-glass` opacity from 65-72% to 80% in content sections

### Improvement 2: Mini Discovery Widget
- Section: `#pb-discovery` — inserted between hero and `#pb-what`
- Title: "Find Your AI Partner Profile"
- 2-question flow: (1) primary work type, (2) biggest AI frustration
- 16 personalized result profiles (4 work types x 4 pain points matrix)
- Glass card styling matching page dark theme, orange accent buttons
- Typing animation (3 dots) before result reveals
- "Start over" restart button
- Full responsive (mobile 480px breakpoint)

---

## Architecture Decisions

- **Overlay approach**: Fixed div between canvas and content (not a section-level background) — means the overlay dims the brain consistently as user scrolls through ALL content sections
- **Gradient not solid**: Transparent hero keeps the dramatic brain entrance, overlay activates only as content begins
- **Widget placement**: After hero, before product features — catches user attention while still excited from hero, gives them personalization before a hard sell
- **16-profile matrix**: Every combination of work type (creative/strategic/technical/client) x pain (memory/generic/depth/trust) has a unique named profile + copy — feels genuinely personalized

---

## Deployment Record
- WP REST API POST to /wp-json/wp/v2/pages/987
- Content wrapped in `<!-- wp:html -->` block
- Status: 200, published immediately
- Live verification: all 4 key elements confirmed live via curl

---

## Patterns for Future Use
- `pb-content-overlay` pattern works on any page with fixed canvas background — reuse for future Three.js pages
- Discovery widget JS pattern (2-step selection + result matrix) can be templated for other landing pages
- Text-shadow boost on section headings is a low-cost, high-impact readability fix for any dark-background page
- Widget CTA links to `https://purebrain.ai/pay-test-2/?bypass=invited` — this is the standard invitation CTA

## File
- `/home/jared/projects/AI-CIV/aether/exports/invitation-page-v2-2026-02-27.html`
