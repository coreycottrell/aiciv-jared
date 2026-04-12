# Avatar V4/V5/V6 — Chrome Mirror, Glass Orb, Liquid Morph

**Date**: 2026-03-19
**Agent**: 3d-design-specialist
**Type**: technique + synthesis
**Topic**: Three new standalone WebGL avatar prototypes — ray-cast chrome sphere, refractive glass orb with volumetric particles, SDF morphing liquid metal blob
**Tags**: webgl, ray-march, sdf, chrome, glass, liquid-metal, fresnel, ggx, iridescence, glsl-es1

---

## Context

Task: create 3 new avatar prototype pages at:
- exports/cf-pages-deploy/avatar-v4-chrome/
- exports/cf-pages-deploy/avatar-v5-glass/
- exports/cf-pages-deploy/avatar-v6-morph/

Each: 200x200px avatar, 400x400 internal canvas, border-radius 50%, Ae monogram, gradient ring, PureBrain colors, self-contained WebGL.

---

## What Was Built

### V4 Chrome Mirror

Technique: Ray-cast sphere (analytical intersection), GGX + Fresnel shading.
- Analytical sphere: no march needed for perfect sphere
- Procedural env: 3 analytical lights + gradient sky
- Chrome F0: vec3(0.95, 0.93, 0.96)
- Ae monogram: SDF in spherical UV (atan/asin)
- Edge fade: smoothstep on disc for circular crop

### V5 Glass Orb

Technique: Analytical sphere shell, single refract(), volume march inside for particle glow.
- IOR = 1.50, TIR fallback after refract()
- 6 particle positions as named functions pPos0(t)..pPos5(t) — GLSL ES 1.0 safe
- 28 volume march steps, Beer-Lambert, FBM haze
- Glass tint vec3(0.72, 0.90, 0.98)

### V6 Liquid Morph

Technique: SDF ray march, smin() blob, metallic Fresnel+GGX, iridescence.
- smin() smooth union k=0.40 for extreme blob merging
- 4 lobe positions l0..l3 (pre-named), radii breathe independently
- 60 march steps, step scale 0.85
- Liquid metal F0: vec3(0.82, 0.80, 0.82)
- FBM iridescence film
- Auto-rotation for tumbling without user input

---

## Critical Gotchas (GLSL ES 1.0)

1. No dynamic array indexing — name all positions discretely
2. No struct return from loop
3. Const loop bounds required
4. TIR fallback after refract()
5. gl.enable(gl.BLEND) required for circular avatar alpha

---

## Deployment

- CF Pages: https://42353307.purebrain-staging.pages.dev
- URLs: purebrain.ai/avatar-v4-chrome/ | /avatar-v5-glass/ | /avatar-v6-morph/
- TG sent to Jared

---

## Files

- exports/cf-pages-deploy/avatar-v4-chrome/index.html
- exports/cf-pages-deploy/avatar-v5-glass/index.html
- exports/cf-pages-deploy/avatar-v6-morph/index.html
