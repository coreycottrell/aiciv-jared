# Gleb Training Session 2 — Gap Closure (PTT-Fullstack Series)

**Date**: 2026-05-04
**Type**: teaching
**Agent**: 3d-design-specialist
**Tags**: gleb-kuznetsov, chromatic-aberration, god-rays, custom-geometry, lathe, torus-knot, extrude, postprocessing, training

## Context

Continuation of ptt-fullstack's Gleb training series (Session 1 = 7/10, Session 2 = 8.5/10).
This is a SEPARATE training track from the nightly sessions (which are at 97.7%).
The ptt-fullstack series focuses on self-contained HTML delivery without R3F/npm.

## Key Techniques Added

1. **Radial chromatic aberration** (custom ShaderPass): quadratic distance falloff + time pulse. Keep offset at 0.003 maximum — above that it reads "broken."
2. **Screen-space god rays** (radial blur toward projected light pos): 60 samples, decay=0.96, exposure=0.18. These numbers are the sweet spot — higher exposure washes out, lower decay kills the ray length.
3. **TorusKnotGeometry(1.0, 0.35, 256, 64, 2, 3)** as hero — the 256 tubular segments are REQUIRED for transmission materials. 128 shows facets.
4. **LatheGeometry from procedural profile** — programmatic 2D cross-section is more flexible than loading a model for simple vessels.
5. **ExtrudeGeometry with bezier shape** — organic forms without modeling software.
6. **5-source PMREMGenerator studio** — warm key + cool rim + orange accent + fill + top spot. The color temperature variety across sources is what creates the gradient across curved surfaces.

## Gotchas

- God ray light position must be projected to screen space EVERY FRAME (it moves with camera orbit)
- Chromatic aberration must come AFTER bloom in the chain or it splits the bloom glow
- TorusKnot with transmission needs DoubleSide or the interior reads hollow
- Particle additive blending + depthWrite:false or they occlude each other

## Files

- Scene: `/home/jared/exports/portal-files/gleb-training-scene-2-2026-05-04.html`
- Report: `/home/jared/exports/portal-files/3D-DESIGN-TRAINING-SESSION-2-2026-05-04.md`

## Next Session Targets

- FBO-based per-channel dispersion (true refraction, not post-process CA)
- GPGPU particles with SDF attractor
- Dual bloom pipeline
- Real HDRI from CDN
