# Memory: Investor Page v4 — Black Orange Liquid Metal Design

**Date**: 2026-03-17
**Type**: operational
**Agent**: full-stack-developer

## What Was Built

Complete redesign of investor engagement page at:
`exports/cf-pages-deploy/investors-ask-aether-v4/index.html`

82KB, 1605 lines, single HTML file.

## Key Design Patterns

### Black Obsidian Shader with Orange Veins
- Fragment shader uses `veinPattern()` function — FBM noise run twice at different frequencies, thresholded to create thin crack lines
- Veins glow orange (`vec3(0.95,0.22,0.02)`) scaled by `heightBoost` from vertex height
- Base surface is near-black `vec3(0.012,0.010,0.016)` — NOT chrome, NOT blue
- Fresnel edge glow is dark orange not blue
- Background gradient includes faint orange at horizon band (`smoothstep(0.25,0.42,t)*smoothstep(0.62,0.42,t)`)

### Avatar Emergence from Liquid
- Avatar starts at `y = -3.0` (below surface), emerges to `y = 1.0`
- `emergeT` counter increments 0.008/frame, ease-out-cubic applied
- Scale animates from 0.3 → 1.0 during rise
- Three ripples triggered at offsets: 200ms, 600ms, 900ms
- Triggered by `IntersectionObserver` on hero section leaving viewport

### Depth Emergence CSS for Cards
- Cards use `transform: translateZ(-500px) scale(0.62)` + `filter: blur(10px)` as hidden state
- `.emerged` class: `translateZ(0) scale(1)` + `filter: blur(0)`
- `.sinking` class: `translateZ(-350px) scale(0.7)` + `filter: blur(14px)` with faster transition (0.7s)
- `perspective: 1400px` on `.content-section` container

### Final Section — Orbit Layout
- Uses absolute positioning on `.final-avatar-ring` (280x280px)
- 4 `.orbit-btn` elements at `.top`, `.right`, `.bottom`, `.left` positions
- Each has staggered `animation-delay` for float offset
- Central orb is CSS-only (no Three.js), uses radial gradient + box-shadow for glow
- Chat section starts `opacity:0; transform:translateY(30px)` then `.visible` class shows it

### Color Palette Key Values
- Orange: `#f1420b`
- Orange dim: `#b83008`
- PMREM probe uses orange-dominant lights: `0xff8833`, `0xf1420b`
- Particle aura fragment shader: `vec4(0.95,0.28,0.05,a)` — orange particles

## Password Gate
- SHA-256: `ac33e72f151c5707a15a46ca7aa929d7ffb674143d61bdd0a61fc8ebff0d4f28`
- Plain text list: `purebrain2026, investor2026, aether, pure2026, aethereal, pureinvestor2026`
- `?open=1` URL param bypasses gate
- Gate panel uses orange border/glow instead of v3's blue

## What Was Dropped vs v3
- No fixed `#avatar-orb` div (CSS only) — avatar is fully Three.js, starts submerged
- Section transitions changed from `translateY(90px)` to `translateZ(-500px)` depth effect
- All blue accents on gate/progress changed to orange
- Chart colors changed: bar chart orange, line chart gold (was orange/blue)

## Data Sources (unchanged from v3)
All financial data identical to v3: $55M pre-money, $3.36/share, $332,500 raised,
scenarios base/bull/bear, MAKR $25M Series-A at $105M, all table data preserved.
