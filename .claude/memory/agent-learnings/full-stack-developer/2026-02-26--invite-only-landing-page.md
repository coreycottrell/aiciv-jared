# Invite-Only Pre-Launch Landing Page

**Date**: 2026-02-26
**Type**: operational + teaching
**Topic**: Built PureBrain.ai invite-only pre-launch landing page for 25-client campaign

---

## What Was Built

`/home/jared/projects/AI-CIV/aether/exports/invite-only-landing-page.html`

1,725-line, 55KB self-contained HTML file. All 7 required sections. Vanilla JS only. WP-wrapped.

---

## Sections Included

1. **Hero** — badge pill, animated headline underline, live countdown timer, CTA, 25-spot dots visualization, scroll chevron
2. **What Is PureBrain** — 3 glassmorphism feature cards with inline SVG icons (neural, fingerprint, growth chart)
3. **The Awakening Experience** — 4-step timeline with ghost numbers + desktop-only chat mockup (hidden mobile via `display:none`)
4. **Pricing** — 4-card grid: Awakened ($79), Bonded ($149 featured), Partnered ($499), Unified ($999)
5. **Social Proof** — single large testimonial card (Michael Hancock / Metis), decorative quote mark
6. **Urgency/Scarcity** — 25-spot dots (large), 3 orange-bordered fact blocks, price lock badge
7. **Final CTA** — repeated countdown, trust row, Jared signature block (JS initials, gradient avatar)

---

## CSS Architecture

- All CSS scoped under `#pb-invite-page` — 187 selector hits, fully WP-safe
- CSS variables declared under `#pb-invite-page` (not `:root` — WP can override that)
- WP magic-cursor override: `body { background: #0a0a0a !important; }`
- Wrapped: `<!-- wp:html --> ... <!-- /wp:html -->`
- `!important` on layout-critical background properties

---

## JS Patterns

- **Countdown timer**: `setInterval` 1s, targets `2026-03-03T23:59:59`, syncs two timers simultaneously (hero + final CTA)
- **Spots dots**: `pbBuildDots(containerId, taken, total)` helper — called twice for hero and urgency section
- **Scroll fade-in**: `IntersectionObserver` at threshold 0.2, adds `.pb-visible` class; fallback shows all immediately
- **Chat mockup**: second `IntersectionObserver` at threshold 0.3, staggered 600ms delays per message
- **Mobile sticky bar**: dual IntersectionObserver — shows when hero leaves viewport, hides when final CTA enters
- All JS wrapped in IIFE `(function() { 'use strict'; ... })()`

---

## Design Decisions

- Two atmospheric orbs: blue top-left 600px, orange bottom-right 400px, `blur(80px)`, 20s `alternate` drift animation
- Chat mockup: `display:none` on mobile via `@media (max-width: 768px)` — no reflow cost
- Featured pricing card: `scale(1.03)` + orange glow border + `0 0 40px rgba(241,66,11,0.12)` shadow
- Glassmorphism: `backdrop-filter: blur(20px)` + `rgba(10,20,35,0.6)` bg + `rgba(42,147,193,0.15)` border
- Orange underline draws left-to-right: `animation: pb-underline-draw 0.7s ease 0.9s forwards`
- Load-in stagger: badge 200ms → headline 400ms → sub 600ms → countdown 800ms → CTA 1000ms → dots 1200ms
- `@media (prefers-reduced-motion: reduce)` zeroes all animations + forces opacity 1 on hero elements

---

## File Size

- 55KB total (well under 400KB target — no images)
- 1,725 lines
- Fonts loaded via `<link>`: Oswald (400,600,700) + Plus Jakarta Sans (400,500,600)

---

## CTA Link

All 7 CTA buttons point to `https://purebrain.ai/#awakening`

---

## Gotchas / Lessons

1. **Two countdown timers** on same page: share one `setInterval`, update both DOM targets simultaneously — don't run two separate intervals
2. **CSS variables on `#pb-invite-page` not `:root`**: WP's own `add_theme_support('custom-properties')` can override `:root` vars; scoping to wrapper ID is safer
3. **Spots dots built via JS** not hardcoded HTML — makes the 2/25 state easy to change without editing HTML
4. **Mobile sticky bar visibility logic**: needs TWO IntersectionObservers — one for "show when hero gone", one for "hide when final CTA visible". Single observer can't handle both.
5. **`scale(1.03)` on featured pricing card**: must reset `transform:none` at mobile breakpoint, then just use `translateY(-3px)` on hover — otherwise the scale makes the card overflow its column
