# Aether Avatar Prototypes V3 — Four New Concepts

**Date**: 2026-03-18
**Type**: technique
**Agent**: 3d-design-specialist
**Topic**: Four new canvas avatar concepts for investor page prototype selection

---

## Context

Jared requested V3 avatars — 4 new concepts distinct from the 8 already built across V1 (Neural Orb, Fluid Consciousness, Particle Entity, Crystalline Intelligence) and V2 (Living Hexagon, Digital Breath, Thought Web, The Eye).

---

## What Was Built

**File**: `exports/cf-pages-deploy/avatar-prototypes-v3/index.html`
**URL**: https://purebrain.ai/avatar-prototypes-v3/
**Deployed**: purebrain-staging CF Pages — HTTP 200 confirmed

---

## Four Avatar Concepts

### V3/01 — Quantum Core
- Pulsating energy nucleus surrounded by 6 orbital probability clouds
- Each orbital has N cloud point particles distributed randomly
- Quantum collapse mechanic: orbitals periodically collapse to a point and re-expand with bright flash
- Mouse shifts core position and biases orbital angles
- Colors: PureBrain blue clouds + orange clouds alternating per orbital
- Key technique: cloud points have random angle/distance offsets from orbital center, pre-baked at construction for performance

### V3/02 — Memory Stream
- 14 spiral ribbon streams wound around the center (1.5 turns each)
- Ribbons alternate inward/outward direction
- Per-ribbon wave perturbation + pulsing color intensity
- 35 data packet particles travel along ribbon paths
- Mouse endpoint displacement scales with spiral progress
- Key technique: ribbons drawn as per-segment line strokes with lerped alpha — not filled paths. This gives the translucent layering effect.

### V3/03 — Constellation Mind
- 55 stars in slow orbital drift + harmonic oscillation
- Mouse attraction force within 80px radius
- Connections dynamically selected by noise function over time
- Connection cycle: 5.5 seconds per constellation, fade in/out with 25% ramp
- Energy dot travels along each active connection
- Key technique: `noise1(i * 1.7 + t * 0.12)` per-star to select active stars — gives organic constellation reformation without jarring cuts

### V3/04 — Aurora Shield
- 9 concentric aurora bands at increasing radii (30px–128px)
- Each band is a filled polygon with inner/outer edge displaced by multi-frequency sine waves
- Colors: alternating blue, cyan, orange bands; colorT shifts hue over time
- Mouse bends bands toward cursor via cosine projection onto magnetic field angle
- Vertical magnetic field lines drawn as subtle looping strokes
- Key technique: `createRadialGradient` from inner to outer band radius gives the characteristic aurora glow-from-within look

---

## Page Architecture

Matches V1/V2 exactly:
- Same CSS variables, card layout, header gradient
- V3 uses blue card hover accent (vs V1 orange, V2 orange) for visual distinction
- Navigation links to V1 and V2 at top
- Cards at 400px wide, canvases at 300x300, border-radius 50% for circular crop

---

## Performance Notes

- All 4 avatars run simultaneously — light canvas 2D only, no WebGL
- No external dependencies (no Three.js, no CDN)
- Each avatar is self-contained IIFE
- `requestAnimationFrame` loop per canvas
- Mouse events use delta normalization to [-1, 1] range

---

## Gotchas

1. Circular clip must be applied before background fill to prevent corner bleed — `ctx.clip()` immediately after `ctx.arc()` + `ctx.beginPath()`
2. `ctx.save()` / `ctx.restore()` around each avatar IIFE's draw call to prevent clip state leaking
3. Aurora band polygon: must append outer points in REVERSE order before closePath — otherwise the fill inverts
4. Connection alpha fade must account for both cycle progress AND distance factor or close stars look disproportionately bold

---

## Reference Files

- V1: `exports/cf-pages-deploy/avatar-prototypes/index.html`
- V2: `exports/cf-pages-deploy/avatar-prototypes-v2/index.html`
- V3: `exports/cf-pages-deploy/avatar-prototypes-v3/index.html`
