# Memory: homepage-clone-test Full Visual Audit

**Date**: 2026-03-10
**Agent**: browser-vision-tester
**Type**: pattern + operational + gotcha
**Tags**: homepage-clone-test, pricing-section, comparison-section, display-none, transparent-bg, testimonials, calculator-cta, compare-pills, awaken-button, see-why-button, footer, aether-credit, video-overlay

---

## Task

Full visual audit of https://purebrain.ai/homepage-clone-test/ scrolling from top to bottom. Checking:
- Hero
- Middle content
- Testimonials
- Calculator CTA
- Compare pills
- Awaken blue button
- See Why orange button
- Pure Technology footer
- Aether credit bar

---

## CRITICAL BUGS FOUND

### Bug 1: Pricing Section HIDDEN (display:none, no active class)

**`#pricing .pricing-section`** = `display: none`, height=0, no `.active` class.

The pricing section is INTENTIONALLY GATED behind JS/chat interaction (same as sandbox-3), but on the clone page, no interaction happens so users who land on the page directly NEVER see pricing.

When forced visible via JS: height=2558px, offsetTop=6536px.

**When forced visible, the section renders as completely black** - same transparent background issue as sandbox-3. Inherited CSS: transparent background + fixed video overlay at rgba(0,0,0,0.75) = black.

### Bug 2: Comparison Section HIDDEN (display:none, no active class)

**`#compare .comparison-section`** = `display: none`, height=0, no `.active` class.

Same gating as pricing. When forced: height=2069px, offsetTop=9094px.

### Bug 3: Testimonials Section Has Transparent Background

**`#testimonials .testimonials-section`** = `display: block`, height=1124px, offsetTop=6956px.

Background = `rgba(0,0,0,0)` - fully transparent. The section DOES render (testimonial cards visible at y=6956) but is very dark/hard to read because it relies on the video background showing through.

Testimonials are VISIBLE at scroll position y=6956 despite transparent bg. Testimonial cards themselves have `rgba(30,30,30,0.6)` background which helps them stand out.

### Bug 4: LARGE DARK VOID at y~7000-9000

Page total height = 9401px. But the section map shows:
- hero: 0-900
- about: 964-1873
- pb-demo: 1874-2866
- value-pyramid: 2866-3649
- capabilities: 3649-4452
- awakening (chat): 4452-5392
- value: 5391-6536
- timeline: 6536-6957
- testimonials: 6956-8080
- calculator-cta: 8080-8429
- footer: 8936-9134

The calc-cta section (h=349) ends at 8429, then there's ~507px gap to the footer at 8936.
This creates a NOTICEABLE DARK VOID in the bottom area (~507px of empty dark space).

---

## WHAT RENDERS CORRECTLY

| Section | Status | Notes |
|---------|--------|-------|
| Hero | PASS | PURE BRAIN logo, dark navy bg, brain animation |
| About section | PASS | Content renders |
| Demo video player | PASS | Present and correct |
| Value pyramid | PASS | Renders |
| Capabilities | PASS | Renders |
| Chat/awakening section | PASS | Chat interface present |
| Value section ("What You Actually Get") | PASS | Renders |
| Timeline section | PASS | "What Happens Next" heading visible |
| Testimonials | PARTIAL PASS | Renders but transparent bg = somewhat dark |
| Calculator CTA | PASS | "How Much Are You Wasting on AI Tool Sprawl?" visible |
| Compare pills | PASS | vs ChatGPT, vs Claude, vs Copilot, vs Custom GPTs, vs DeepSeek, vs Gemini, vs Jasper, vs Perplexity (8 pills) |
| "See All Comparisons" pill | PASS | Orange pill present |
| Awaken blue button | PASS | "Awaken Your Personal AI Partner Today", bg=rgb(42,147,193) (Pure Tech Blue), 428x64px, styled properly |
| See Why orange button | PASS | "See Why PureBrain Is Different ->", bg=rgb(241,66,11) (Pure Tech Orange), 339x51px, styled properly |
| Pure Technology footer | PASS | Logo (Side-by-Side-Main-Orange-PT-scaled, 240x117px), "2026 Pure Technology Inc.", all footer links |
| Aether credit bar | PASS | "Built by AETHER (an AI) for PureBrain.ai, PureMarketing.ai & PureTechnology.ai" with nav buttons |
| Pricing section | FAIL | display:none, never shown on direct page load |
| Comparison section | FAIL | display:none, never shown on direct page load |

---

## Aether Credit Bar Detail

- Appears as a FIXED navigation bar at top of viewport (overlaid on page)
- Text: "Built by AETHER (an AI) for PureBrain.ai, PureMarketing.ai & PureTechnology.ai"
- Has nav buttons: "Why Choose PureBrain?", "Mission & Values", "Compare"
- `.pb-footer-aether` class appears 5 times in DOM (possible duplicates from plugin)

---

## Footer Logo

- File: `MA1.BI-1.2.6-001-211107-Side-by-Side-Main-Orange-PT-scaled.png`
- Rendered at: 240x117px
- This is the Side-by-Side logo (correct)
- Footer has copyright "2026 Pure Technology Inc." and full link set

---

## Screenshots

Directory: `/home/jared/projects/AI-CIV/aether/exports/screenshots/homepage-clone-audit-20260310/`

Key files:
- `001-desktop-hero.png` - Hero section, brain animation, PURE BRAIN logo
- `011-testimonials-start.png` - "What Others Have Built" testimonial section
- `013-calculator-cta.png` - Calculator CTA with compare pills visible
- `014-calculator-cta-mid.png` - Compare pills + Awaken blue button + See Why orange button
- `005-desktop-bottom.png` / `015-footer-area.png` - Pure Technology footer

---

## Comparison with sandbox-3 Behavior

Same pattern confirmed:
- `.pricing-section { display: none; }` → only shown via `.active` class from `window.revealPricing()`
- `.comparison-section { display: none; }` → same
- Transparent backgrounds on sections create black void when sections are revealed

The clone page is architecturally identical to sandbox-3's JS-gated reveal system.

---

## Fix Options

1. **If sections should ALWAYS be visible on clone** (recommended for clone/test page):
   - Add CSS: `.pricing-section, .comparison-section { display: block !important; background: #080a12; position: relative; z-index: 5; }`
   - OR add JS on DOMContentLoaded: `window.revealPricing && window.revealPricing()`

2. **If keeping gated behavior**: The chatbox UX needs to work so users can trigger reveal

3. **Footer gap**: 507px gap between calculator CTA and footer. Add `margin-bottom` or reduce gap.
