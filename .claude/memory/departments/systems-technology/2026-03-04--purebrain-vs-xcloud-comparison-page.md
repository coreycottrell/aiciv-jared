# Memory: PureBrain vs xCloud Comparison Page Build

**Date**: 2026-03-04
**Agent**: dept-systems-technology
**Type**: build-completion
**Topic**: Competitor comparison page — xCloud vs PureBrain

---

## What Was Built

Full comparison page at: https://purebrain.ai/purebrain-vs-xcloud/

**WordPress Page ID**: 1256
**Slug**: purebrain-vs-xcloud
**Template**: elementor_canvas
**Status**: Published

**File**: `/home/jared/projects/AI-CIV/aether/exports/purebrain-vs-xcloud.html`

---

## Key Research Findings on xCloud

- xCloud is a managed hosting platform for WordPress, Laravel, and PHP — NOT an AI product
- Target audience: developers and agencies managing multiple sites
- Their AI is incidental (BetterDocs-style documentation chatbot), not a core product
- Pricing is not prominently displayed on their homepage — a known gap
- No persistent memory, no session retention, no business intelligence features
- Core value proposition: simplified cloud hosting without manual server config

---

## Design Patterns Used

This page follows the exact same pattern as `purebrain-vs-glbgpt.html`:
- Scoped CSS under `#pb-vs-xcloud` to avoid WordPress theme conflicts
- WordPress Dark Theme Override CSS block at top
- `<!-- wp:html -->` wrapper for WordPress deployment
- elementor_canvas template
- Oswald font for headings, Inter for body
- Colors: pb-blue (#2a93c1), pb-orange (#f1420b), dark bg (#080a12), dark2 (#0d1120)
- Gradient strip at top (blue to orange)
- Sticky nav with PUREBR[AI]N logo and CTA button
- All inline, self-contained — no external CSS dependencies except Google Fonts

---

## Page Sections Built

1. Gradient strip (blue-to-orange)
2. Sticky nav with logo + CTA
3. Hero with badge, H1, subtitle, 3 stats
4. "First, Let's Be Honest" — context setter (what xCloud is vs is not)
5. "What Generic Hosting AI Cannot Do" — pain points (dark2 bg)
6. Feature comparison table (13 rows)
7. "What PureBrain Does Differently" — 6 differentiator cards (dark2 bg)
8. Real-world scenarios — 4 cards in 2x2 grid
9. Pricing comparison — xCloud vs PureBrain 3-tier
10. Decision framework grid — who should use which
11. CTA section with orange button
12. Footer with Aether attribution

---

## WordPress Credentials Pattern

Env keys for purebrain.ai WordPress:
- `PUREBRAIN_WP_USER` = "Aether"
- `PUREBRAIN_WP_APP_PASSWORD` = application password string
(NOT WP_USER / WP_APP_PASSWORD — those keys returned None)

---

## Unique Positioning Angle

This comparison required a different framing than ChatGPT or GLBGPT comparisons: xCloud is not even in the same category as PureBrain. The page is honest about this — xCloud is a hosting tool and does hosting well. PureBrain is an AI memory partner. The comparison exists because users searching for AI tools encounter xCloud. The page redirects the category question before the feature comparison.

---

## Verification Completed

- HTTP 200 on live page
- All 6 content checks passed (div IDs, sections, CTA text)
- WordPress API confirmed: ID 1256, status publish, template elementor_canvas
- Telegram notification delivered (message_id: 18307)
