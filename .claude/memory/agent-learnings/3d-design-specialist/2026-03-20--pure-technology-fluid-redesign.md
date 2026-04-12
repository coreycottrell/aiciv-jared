# Pure Technology 3D Page — Full Navier-Stokes Fluid Redesign

**Date**: 2026-03-20
**Type**: technique
**Tags**: fluid-simulation, navier-stokes, webgl, pure-technology, glass-panels, scroll-animation

---

## Context

Jared requested a complete redo of the Pure Technology 3D page. The first version used particles and lines — underwhelming. He wanted FLUID DYNAMICS, mind-blowing, PeachWeb quality.

## What Was Built

Full-screen Navier-Stokes fluid simulation (same GPU shader stack as the Aether fluid-core avatar) deployed as the entire page background, with glass/frosted panels floating on top.

## Key Architecture

**Fluid simulation**:
- Full WebGL Navier-Stokes implementation (Pavel Dobryakov MIT, adapted)
- SIM_RESOLUTION: 128, DYE_RESOLUTION: 1024 — high-quality dye at full viewport
- CURL: 32 — very swirly/organic movement
- BLOOM: 8 iterations, 256 resolution — luminous glow effect
- SHADING: true — 3D depth on fluid surface

**Interaction layers**:
1. Mouse moves create real fluid splats (color follows direction)
2. Click anywhere = 4-way burst of blue+orange splats
3. Scroll triggers section-specific color burst (each section = different color ratio)
4. Autonomous splat every 1.2s keeps sim alive when idle
5. Initial dramatic burst at page load (8-13 splats)

**Glass panels**:
- `backdrop-filter: blur(40px) saturate(1.8)` — fluid shows through frosted glass
- `background: rgba(8,10,18,0.55)` — semi-transparent dark
- Blue border: `rgba(42,147,193,0.15)` — subtle brand tint
- IntersectionObserver triggers emerge animation + fluid burst on scroll into view

**Product card fluid**:
- Canvas 2D animated gradients per card (not another WebGL context — performance-smart)
- Blue or orange color-coded, smooth animated blob movement
- `opacity: 0.35` normal, `0.55` on hover

## Performance Notes

- Using `Math.min(window.devicePixelRatio, 2)` cap to prevent 3x scaling on high-DPI breaking performance
- Card fluid uses Canvas 2D not WebGL (secondary contexts add overhead)
- Single WebGL context for entire page — correct approach

## Files

- Output: `exports/puretechnology-3d-redesign/index.html`
- CF deploy: `exports/cf-pages-deploy/puretechnology-3d-redesign/index.html`
- Reference sim: `exports/cf-pages-deploy/fluid-core/index.html` (source of full shader stack)

## Gotchas

- The full Navier-Stokes shader stack must be copied intact — no partial implementations
- `correctRadius()` must account for aspect ratio or splats look elliptical
- `correctDeltaX/Y()` needed for proper mouse tracking across non-square viewports
- Initial splat count matters a LOT: 8-13 creates rich opening vs. 3-4 which looks sparse

## Deployment

Deployed to `purebrain-staging` CF Pages. URL pattern: `{hash}.purebrain-staging.pages.dev/puretechnology-3d-redesign/`
