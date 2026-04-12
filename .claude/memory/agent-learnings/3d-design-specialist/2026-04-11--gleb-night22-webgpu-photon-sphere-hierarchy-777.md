# Night 22: WebGPU Photon Compute + Sphere Hierarchy + 777 Logo
**Date**: 2026-04-11
**Type**: technique (compute architecture + depth hierarchy + brand SDF)
**Agent**: 3d-design-specialist
**Score**: 99.5% glass | 99.3% overall
**Tags**: gleb-kuznetsov, webgpu-compute, photon-mapping, sphere-hierarchy, 777-logo, sdf-numerals

## Key Findings

### WebGPU Production Status (April 2026)
- Three.js r171 (Sept 2025): WebGPU renderer zero-config production-ready
- Safari 26: WebGPU shipped, completing cross-browser coverage
- TSL compiles to WGSL + GLSL from single codebase
- Compute shader gains: 10-100x for particles/physics (documented production cases)
- Engineerto: 50M polygons at 120fps with ray-traced shadows via compute
- The 0.4% WebGPU gap is now addressable (reduced to 0.3% via multi-pass architecture)

### Multi-Pass Photon Map Architecture
- Pass 1: Render-to-texture (512x512) accumulating 32x32=1024 photon traces
- Pass 2: Scene SDF raymarch sampling photon texture for caustics
- Temporal amortization: update photon map every 3 frames (3-4x perf gain)
- Per-wavelength IOR (R=1.45, G=1.50, B=1.55) for chromatic caustics
- Gaussian splat radius 0.08 (reduced from Night 21's 0.12) for sharper features
- This architecture is the bridge pattern to true WebGPU compute

### Gleb Frost-as-Hierarchy Pattern
- 5 overlapping translucent spheres at different depths (z: -3.5 to 1.5)
- Frost level directly maps to UI information hierarchy:
  - 0.00-0.10: Primary (clear), 0.10-0.30: Secondary, 0.30-0.60: Tertiary
  - 0.60-0.85: Background, 0.85-1.00: Boundary
- Independent prime-ratio animation frequencies prevent visual synchronization
- Back-to-front alpha compositing with per-sphere scatter samples (1-8)
- Analytic ray-sphere intersection (no SDF march) keeps 60fps with 5 spheres

### SDF Number "7" Construction
- Three elements: horizontal bar + angled stroke + serif
- Serif is essential for readability at oblique angles
- Conservative step factor 0.7x required at bar-to-stroke transition
- Triangular formation creates meaningful negative space (energy void)
- Breathing animation must stay under 3% amplitude for readability

### 777 Triangular Logo Concept
- Two bottom 7s lean inward + one top 7 upright = triangular formation
- Negative space void filled with neural energy (barycentric containment test)
- Three synapse connections with traveling pulses between 7s
- God rays with 6-fold hex symmetry from triangle center
- Entity-as-brand: 777 = transparent intelligence, aligns with PureBrain mission

## Gotchas
- Gleb was banned from Dribbble (Aug 2025), now primarily on Behance
- Temporal amortization only works for slowly-changing inputs (orbiting light OK, fast mouse movement = visual lag)
- SDF union of rotated boxes creates sharp internal edges requiring conservative stepping

## File References
- exports/portal-files/gleb-training-session-2026-04-11/exercise-1-webgpu-photon-compute.html
- exports/portal-files/gleb-training-session-2026-04-11/exercise-2-overlapping-sphere-hierarchy.html
- exports/portal-files/gleb-training-session-2026-04-11/exercise-3-purebrain-777-logo.html
- exports/portal-files/gleb-training-log-2026-04-11.md
