# Memory: PureBrain Invite-Only Pre-Launch Landing Page (v2)

**Date**: 2026-02-26
**Type**: operational
**Agent**: full-stack-developer
**Topic**: Built complete self-contained invite-only pre-launch landing page for purebrain.ai

---

## What Was Built

Full 7-section pre-launch landing page for purebrain.ai invite-only campaign.

**Output file**: `/home/jared/projects/AI-CIV/aether/exports/purebrain-invite-only-page.html`
**Size**: ~70 KB, 2035 lines
**Type**: Self-contained HTML, wp:html compatible, scoped under `#pb-invite-page`

---

## Page Architecture

### 7 Sections
1. **Hero** — Full viewport, countdown timer (deadline: 2026-03-04T04:59:59Z), 25-spot dots
2. **What is PureBrain** — 3 glassmorphism feature cards with blue left border accent
3. **Awakening Experience** — 4-step timeline + chat mockup (desktop only)
4. **Pricing** — 4 tiers (Awakened $79, Bonded $149 featured, Partnered $499, Unified $999)
5. **Social Proof** — Michael Hancock testimonial, "Verified PureBrain Partner — AI partner: Metis"
6. **Urgency/Scarcity** — 25 large dots, 3 scarcity points, price lock badge
7. **Final CTA** — "Claim My Spot — $149/mo", trust row, mini countdown, Jared signature

---

## Technical Patterns Used

### WP Compatibility
- Entire file wrapped in `<!-- wp:html -->` block
- All CSS scoped under `#pb-invite-page` with `!important` on 830+ rules
- CSS variables defined with `!important` at root level

### JS Features (zero external dependencies)
- Countdown timer to `2026-03-04T04:59:59Z` (end of day Tuesday EST)
- Dots animation: 2 of 25 claimed, staggered 80ms fill-in
- IntersectionObserver for scroll-triggered reveal animations
- Chat mockup: sequential message appearance (900ms between messages)
- Mobile sticky bar: hides when final section is visible

### Animations
- Page load: 7-element staggered fade-in via nth-child delays
- Background orbs: slow CSS drift animations (18s, 22s, 26s cycles)
- Underline draw-in on hero headline
- Badge pulsing border (2.4s cycle)
- Scroll chevron bounce + fade
- `prefers-reduced-motion` media query disables all animations

### Brand
- Logo pattern: `PUREBR(blue)AI(orange)N(blue).ai(white)` — 3 instances
- Blue: #2a93c1, Orange: #f1420b, BG: #0a0a0a, Dark BG: #060d14
- Fonts: Oswald (headings) + Plus Jakarta Sans (body) via Google Fonts

---

## CTA Links
- ALL "Claim" and "Get Started" buttons: `https://purebrain.ai/pay-test-2/` (7 total)

---

## Deployment Notes
- Template: `elementor_canvas` (clean canvas, no WP theme header/footer)
- Password protection: set at WP level via REST API `password` field
- Auth: Basic base64(Aether:PUREBRAIN_WP_APP_PASSWORD)
- See memory: `2026-02-26--demo-no-bs-password-protected-wp-deploy.md` for full deploy pattern
