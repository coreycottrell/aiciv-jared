# Pure Technology v3 — Liquid Emergence

**Date**: 2026-03-20
**Type**: technique + synthesis
**Agent**: 3d-design-specialist
**Tags**: navier-stokes, fluid, scroll-animation, gsap, emergence, dissolution, pure-technology, webgl

---

## Context

Built Version 3 of the Pure Technology marketing page. Concept: "Liquid Emergence" —
content literally surfaces from a living fluid and dissolves back into it.

## Architecture

**Fluid layer**:
- Full Navier-Stokes simulation (same shader stack as v2, tuned differently)
- CURL: 34 (high — very swirly/organic)
- DENSITY_DISSIPATION: 0.984, VELOCITY_DISSIPATION: 0.978
- BLOOM_INTENSITY: 0.85, BLOOM_THRESHOLD: 0.58 — visible glow without blowout
- Auto-splat every 1.3s keeps sim alive at idle
- Dramatic 3-wave initial burst (13 + 7 + 4 splats staggered over 2.4s)

**Emergence system** (key innovation vs v2):
- `.emerge` class starts elements at: `opacity:0; transform:translateY(56px) scale(0.97); filter:blur(8px)`
- `.surfaced` class transitions to: `opacity:1; transform:translateY(0) scale(1); filter:blur(0px)`
  - Plus: `animation:liquidDistort 1.5s` — subtle skew oscillation simulating bubble-break
- `.dissolving` class: opacity 0, translateY(-38px), blur(10px) — upward dissolve
- ScrollTrigger `onLeave` adds `.dissolving` — sections melt away when scrolled past
- Each panel/title emergence triggers a `sectionBurst()` (5 splats matching section palette)

**liquidDistort animation** (the detail that makes it feel liquid):
```css
@keyframes liquidDistort {
  0%   { transform: translateY(0) scale(1) skewY(0deg); }
  14%  { transform: translateY(-4px) scale(1.005) skewY(0.55deg); }
  28%  { transform: translateY(2px) scale(0.999) skewY(-0.28deg); }
  48%  { transform: translateY(-1px) scale(1.001) skewY(0.12deg); }
  100% { transform: translateY(0) scale(1) skewY(0deg); }
}
```
The skewY oscillation at low values (0.55deg) suggests the content is still settling
after breaking the surface. Very subtle but high-impact.

**Section color palettes**:
Each section has a distinct color ratio (blue-heavy vs orange-heavy).
When a panel emerges, the fluid bursts in that section's colors.
Creates a reading of the page through color: strategy sections = cool blue,
problem/energy sections = warm orange.

**Panel aesthetics** (glass):
- `backdrop-filter: blur(38px) saturate(1.65)` — high saturation to pick up fluid color
- `background: rgba(6,8,16,0.58)` — dark but translucent
- Shimmer sweep animation: 9s loop, very subtle
- Chromatic inset box-shadow: blue left edge, orange right edge

## Performance

- Single WebGL context (no secondary canvases on cards — learned from v2)
- GSAP ScrollTrigger handles all emergence/dissolution timing (no raw scroll events)
- Hero elements bypass scroll — surface on page load with 150ms stagger

## Files

- Primary: `exports/puretechnology-3d-redesign/v3-liquid-emergence.html` (57KB)
- CF deploy: `exports/cf-pages-deploy/puretechnology-v3/index.html`
- Live: `https://fe823351.purebrain-staging.pages.dev/puretechnology-v3/`

## Content Included

All real Pure Technology content from `current-site-copy.txt`:
- Hero: "Empowering People Through AI" / "The Key to Unlocking AI" / "Actual Intelligence"
- Why We Exist: $10k/s waste problem, Big Data/AI solution
- Stats: 2.8M+ followers, 340+ brands, 1,200+ campaigns (animated counters)
- Mission/Vision/Values triptych
- 6 services: Digital Marketing, Influencer, AI/Tech, Experiential, Content, LaunchBoost
- 8 pillars including the "∞ Love" pillar
- Pure Ecosystem: Strategy / Influence / Technology
- All 4 testimonials (Josh Sklut, Dr. Suzanne Soliman, Seanne Murray, Donna Williams)
- 4 Benefits cards
- Email CTA footer

## Key Gotcha

The `filter:blur()` on emerging elements interacts with `backdrop-filter` on panels.
Solution: put both on the SAME element (the `.liquid-panel.emerge` classes stack correctly).
If you put blur on a child of the panel, the backdrop-filter breaks on some browsers.

## What Made This Feel Alive

1. The 3-wave initial burst (not just one) — the fluid feels like it's waking up
2. liquidDistort animation on emerge — content doesn't just fade in, it wobbles
3. Per-section color palettes on burst — the fluid responds to what you're reading
4. Auto-splat every 1.3s — background is always moving, never frozen
5. Dissolving upward (translateY negative) — content doesn't just vanish, it evaporates back up
