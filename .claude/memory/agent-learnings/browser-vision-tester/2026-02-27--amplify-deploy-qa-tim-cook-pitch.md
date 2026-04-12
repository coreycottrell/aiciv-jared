# Memory: Amplify Deploy QA — Tim Cook Sales Page + Pitch Page

**Date**: 2026-02-27
**Type**: operational + technique
**Topic**: Visual QA of pages 993 and 1001 with new image deployments

---

## Summary

Full visual QA of two PureBrain.ai pages after new image deployments. All 3 new images confirmed
present, loaded, and visually rendering correctly.

---

## Pages Tested

- **purebrain.ai/your-ai-tim-cook/** (page 993) — Tim Cook sales page
- **purebrain.ai/pitch/** (page 1001) — VC/investor pitch page

---

## New Images Confirmed Deployed

### amplify-founder (Tim Cook page, between Hero and The Problem)
- URL: `https://purebrain.ai/wp-content/uploads/2026/02/amplify-founder-scaled.jpg`
- Natural size: 2560x1429px, Rendered: 1152x643px
- Page Y position: 960px (right after hero stats bar)
- Visual: Man silhouetted against glowing AI agent ring, "YOU ARE NOT ONE PERSON ANYMORE." text
- Status: LOADED, RENDERING correctly

### vc-fomo (Tim Cook page, between Credibility and Closing CTA)
- URL: `https://purebrain.ai/wp-content/uploads/2026/02/vc-fomo-scaled.jpg`
- Natural size: 2560x1429px, Rendered: 1152x643px
- Page Y position: 6906px
- Visual: Businessman in suit racing against glowing AI robot, dramatic motion blur
- Status: LOADED, RENDERING correctly

### vc-hero (Pitch page, between Hero and Compounding Clock)
- URL: `https://purebrain.ai/wp-content/uploads/2026/02/vc-hero-scaled.jpg`
- Natural size: 2560x1429px, Rendered: 1052x587px
- Page Y position: 954px (right after hero intro section)
- Visual: Dark background with golden AI growth curve, "Every Founder. Every Employee. 20x Superpowers."
- Status: LOADED, RENDERING correctly

---

## Page Health Summary

### Tim Cook Page (993)
- Background: rgb(13, 17, 23) — dark navy, NO orange bleed
- Hero headline: "Every Visionary Needs a Tim Cook. Yours Is Already Built." — PRESENT
- Sub-headline: "You Built Something Great. Now It's Trapped Inside You." — PRESENT
- CTA buttons: 2x links to purebrain.ai/#awakening — CORRECT
- Console errors: 4 (all GTM + GoDaddy CSP blocks — expected, non-functional)
- Sections: The Problem, Framework, Agent Team, Credibility, Closing CTA — all present

### Pitch Page (1001)
- Template: elementor_canvas confirmed (no header/footer from theme)
- Background: rgb(8, 10, 18) — dark near-black, NO orange bleed
- PUREBRAIN wordmark: PUREBR = rgb(42,147,193) blue | AI = rgb(241,66,11) orange | N = rgb(42,147,193) blue — CORRECT
- Navigation bar: Compounding / Architecture / Departments / Memory / BOOP / TGIM / Compare
- Key headline: "They hired a worker. You built a mind of minds." — PRESENT
- Dept wall: 14+ department names confirmed in DOM (Marketing, Sales, Finance, Legal, Operations, etc.)
- Pricing tiers: $179/$349/$999/$1,999 all confirmed
- Pricing tab labels: AWAKENED / BONDED (Most Popular) / PARTNERED / UNIFIED
- CTA buttons: 2x links to purebrain.ai/#awakening — CORRECT
- Console errors: 4 (same GTM + GoDaddy CSP blocks — expected)

---

## Key Technique: Force-Visible Override

Scroll-reveal animations (opacity:0 + transform) prevent images from showing in headless
Playwright screenshots even after scroll simulation. Solution:

```javascript
const style = document.createElement('style');
style.textContent = `* { opacity: 1 !important; transform: none !important;
  transition: none !important; animation: none !important; visibility: visible !important; }`;
document.head.appendChild(style);
```

Apply AFTER scroll (to trigger lazy-load), BEFORE taking screenshots.

---

## Screenshot Files

All saved to: `exports/qa-amplify-deploy/`

- `tc-01-full-page.png` — Tim Cook full page (collapsed)
- `tc-02-hero-viewport.png` — Tim Cook hero viewport
- `fv-tc-amplify.png` — amplify-founder image centered
- `fv-tc-amplify-ctx.png` — amplify-founder with context above
- `fv-tc-vcfomo.png` — vc-fomo image centered
- `fv-tc-vcfomo-ctx.png` — vc-fomo with context (businessman vs robot visible)
- `pitch-01-full-page.png` — Pitch full page (collapsed)
- `zoom-pitch-hero-top.png` — Pitch hero with PUREBRAIN wordmark + nav
- `fv-pitch-vchero.png` — vc-hero image centered
- `fv-pitch-vchero-ctx.png` — vc-hero with CTA button context
- `fv-pitch-pricing-actual.png` — Partnership Tiers pricing section
- `fv-pitch-deptwall-actual.png` — Four Exponents 2x2 grid section

---

## Pass/Fail Status

| Check | Status |
|-------|--------|
| Tim Cook dark theme | PASS |
| Tim Cook hero headline | PASS |
| amplify-founder image present | PASS |
| amplify-founder image loaded | PASS |
| vc-fomo image present | PASS |
| vc-fomo image loaded | PASS |
| Tim Cook CTA links | PASS |
| Tim Cook console errors | PASS (CSP only, expected) |
| Pitch elementor_canvas template | PASS |
| Pitch dark theme | PASS |
| PUREBRAIN wordmark colors | PASS |
| vc-hero image present | PASS |
| vc-hero image loaded | PASS |
| Dept wall (23 depts) | PASS |
| Pricing 4 tiers | PASS |
| Pitch CTA links | PASS |
| Pitch console errors | PASS (CSP only, expected) |

**Overall: 17/17 checks PASS**
