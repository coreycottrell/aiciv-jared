# Tim Cook Sales Page Build

**Date**: 2026-02-27
**Type**: operational + teaching
**Topic**: Built PureBrain "Your AI Tim Cook" full sales page — 7 sections, particle hero, org chart grid, animated clock

---

## File Delivered

`/home/jared/projects/AI-CIV/aether/exports/tim-cook-sales-page.html`

57KB / 1,979 lines. Self-contained. WP-wrapped.

---

## Sections Built

1. **Hero** — particle canvas, floating orbs (blue top-left, orange bottom-right), animated headline with orange underline draw, 4 stat counters, hero load-in stagger (badge 200ms → stats 1000ms)
2. **Problem** — two-column grid (story + bottleneck card), Apple origin story callout block
3. **Soul vs Skeleton** — three-column VS layout (You | VS | PureBrain), hidden divider at mobile, bridge quote with decorative quote mark
4. **Executive Team** — org chart dashboard grid with C-Suite row, Marketing/Sales two-up, then 4-column Legal/Finance/HR/IT row. Hover lift + blue top border reveal
5. **24/7 Advantage** — animated clock counting up from 2:00 AM via setInterval, 5 night-activity cards
6. **Credibility** — 3 stat cards with gradient bottom border, prose block
7. **Closing CTA** — Apple pattern callout, full-width button, trust row

---

## Design Patterns Used

- All CSS scoped under `#pb-tc-page` — safe for WordPress
- CSS custom properties on `#pb-tc-page`, not `:root` (WP can override `:root`)
- `body.tt-magic-cursor` + `body { ... !important }` override at top of style block (orange bug prevention)
- Glassmorphism: `backdrop-filter: blur(16-20px)` + `rgba(13,22,35,0.7)` bg + `rgba(42,147,193,0.18)` border
- Org chart hover: `transform: translateY(-3px)` + `border-color` + `box-shadow` + `::before` top border reveal
- VS divider: single `width:1px` div with `position:absolute` VS badge — hidden at mobile via `display:none`

---

## JS Patterns

- **Particle system**: canvas `requestAnimationFrame` loop, 55 particles, blue + orange mix, bounce wrapping at edges — no external deps
- **Clock**: `setInterval` 1s, counts minute/hour forward from 2:00 AM, updates AM/PM display simultaneously
- **Scroll fade-in**: `IntersectionObserver` at threshold 0.15 + `rootMargin 0px 0px -40px 0px`, adds `.tc-visible`; fallback shows all immediately for old browsers
- All wrapped in IIFE `(function() { 'use strict'; ... })()`

---

## Size

- 57KB (well under 100KB target)
- 1,979 lines
- Fonts: Inter (300,400,500,600,700) + Oswald (400,500,600,700) via Google Fonts link

---

## CTA Links

All 4 CTA buttons → `https://purebrain.ai/#awakening`

---

## Gotchas

1. **VS grid divider at mobile**: use `display:none` on the divider element + add `border-bottom` to each column — don't try to collapse a 3-column grid to 1 column with the divider still there, it breaks
2. **Org chart nested layout**: Mixed approach — outer flex column, inner grid rows per department cluster. Avoids overly complex grid math while keeping visual hierarchy
3. **Particle canvas sizing**: Must resize on window resize event AND set initial size from `hero.offsetWidth/Height` (not `window.innerWidth`) since the section may have padding
4. **Animated clock AM/PM sync**: The clock display and the AM/PM subtitle are separate elements — update both in the same setInterval callback
5. **CSS `tc-label` span inside headings**: `font-size: inherit` is needed on `.tc-wordmark` spans when used inside headings so the wordmark scales with the parent heading size
