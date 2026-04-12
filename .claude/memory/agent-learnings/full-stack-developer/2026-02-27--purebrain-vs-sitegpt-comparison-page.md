# Memory: PureBrain vs SiteGPT Comparison Page

**Date**: 2026-02-27
**Type**: operational
**Topic**: Built and deployed brutally honest comparison page for PureBrain vs SiteGPT

---

## What Was Built

Self-contained HTML comparison page positioning PureBrain vs SiteGPT with genuine honesty — acknowledging SiteGPT's strengths AND PureBrain's weaknesses.

**File**: `/home/jared/projects/AI-CIV/aether/exports/purebrain-vs-sitegpt.html`

---

## WordPress Deployment

- **Site**: purebrain.ai
- **Page ID**: 1044
- **Slug**: `purebrain-vs-sitegpt`
- **URL**: https://purebrain.ai/purebrain-vs-sitegpt/
- **Template**: `elementor_canvas`
- **Status**: publish
- **Content size**: 40,114 chars

---

## Page Sections Built

1. **Nav** — sticky, backdrop blur, back to /compare/ link
2. **Hero** — badge, H1, two product cards (SiteGPT gray/PureBrain blue)
3. **Compare Strip** — inline stat comparison bar (1 function vs 12, resets vs permanent)
4. **Different Products** — honest framing that these solve different problems; honest box explaining when to pick SiteGPT
5. **Where SiteGPT Wins** (6 cards) — price, speed, no-code, multilingual, integrations, ticket reduction
6. **Where PureBrain Wins** (6 cards) — scope, memory, content creation, named partner, briefings, 24/7 ops
7. **Honest Weaknesses box** — explicitly calls out PureBrain's higher price, longer onboarding, newer product status
8. **Feature Table** — 25-row side-by-side with ✓, ✗, and "Partial" indicators
9. **Pricing Table** — cost-per-function math showing ~$15/function vs $39-$259/function for SiteGPT
10. **Verdict callout** — the $15/function math framing
11. **Decision Grid** — "right for you if..." two-column cards
12. **CTA section** — primary to /#awakening, secondary to /portfolio/
13. **Footer** — links to /compare/, audit, capabilities

---

## CSS Scoping Pattern

```css
body.page { background-color: #080a12 !important; }
#pb-vs-sitegpt { ... }
#pb-vs-sitegpt * { box-sizing: border-box !important; }
```

All rules scoped under `#pb-vs-sitegpt`. Competitor color: `#6b7f99` (neutral gray-blue for SiteGPT, not snarky).

---

## Yoast SEO Set

- SEO title: "PureBrain vs SiteGPT | AI Executive Team vs AI Chatbot — Honest Comparison"
- Meta desc: "Honest comparison of PureBrain vs SiteGPT. One is a $39/mo support chatbot. The other is a $179/mo AI executive team running 12 business functions 24/7."
- OG title + description set
- Featured media: 694

---

## Key Design Decisions

- **SiteGPT brand color**: neutral `#6b7f99` gray-blue — not dismissive, not their actual brand (avoids trademark territory)
- **Honest weaknesses section**: explicitly inside the "Where PureBrain Wins" section to avoid appearing like we're hiding it
- **Compare strip**: quick-scan stat bar immediately below hero to anchor the fundamental scope difference
- **Cost-per-function math**: $15/function vs $39-$259/function flips the perceived price gap
- **Decision grid**: "right for you if..." framing for both products treats readers as adults

---

## Verification Checklist

- [x] File saved to exports/
- [x] Status: publish
- [x] Template: elementor_canvas
- [x] content.raw: 40,114 chars
- [x] wp:html block present
- [x] pb-vs-sitegpt wrapper present
- [x] All CTAs → /#awakening
- [x] Elementor cache cleared
- [x] Live at https://purebrain.ai/purebrain-vs-sitegpt/
