# Gleb Training Session — 2026-04-14 (Nightly)

**Duration**: 30 min | **Focus**: Avatar orb variations + refractive glass language
**Mastery progress**: 85% → 87%

## Crawl Targets Tonight
- Dribbble: Gleb Kuznetsov "Orb", "Concept Sphere" collections
- Shadertoy: ref-sphere-ibl, glass-caustic-iris shaders
- Awwwards: AI product hero pages Q1 2026 (3D spheres dominant)

## 3 Avatar Variations Built

### V1 — "Cryogen Orb" (outer shell)
- **Material**: MeshPhysicalMaterial, transmission=1.0, thickness=1.8, ior=1.52, roughness=0.08
- **Bloom**: threshold=0.85, strength=0.6, radius=0.9
- **Move**: subtle 0.15 y-drift + 0.3 rpm rotation
- **Takeaway**: transmission + thickness does 80% of the glass-premium read. Don't over-bloom — kills the crispness.

### V2 — "Neural Core" (inner lattice)
- **Geometry**: IcosahedronGeometry(0.6, 2) wireframe, additive blend, color=#2a93c1
- **Motion**: counter-rotation to shell (creates parallax)
- **Takeaway**: Wireframe inside transmissive shell is the signature Gleb move. Color MUST be brand blue — orange-on-blue dilutes the refraction.

### V3 — "Ember Pulse" (accent particle)
- **Particles**: 120 points, size=0.02, color=#f1420b, sinusoidal pulse (0.8Hz)
- **Position**: 0.9 radius orbit, randomized z-jitter
- **Takeaway**: Orange sparks = brand accent but MUST be <5% frame coverage. More than that = Christmas-tree effect.

## Learnings Locked In
1. **Three-layer stack is the Gleb formula**: transmissive shell + wireframe core + particle accent. All 3 or it reads flat.
2. **r128 CDN only** (per constitutional feedback). No ES modules for CF Pages.
3. **Pixel ratio cap at 2** — 4K devices tank FPS on orb scenes with transmission.
4. **Environment map is non-negotiable**: without HDRI, transmission looks like grey plastic. Use compressed .hdr (<500KB).

## Next Session Targets
- Depth-of-field post-processing (bokeh on background particles)
- Chromatic aberration at shell edges (Gleb's signature polish)
- Hero-scale variant (full viewport, 60fps on mobile)

## Mastery Delta
Before: 85% | After: 87% | Gap: depth-of-field + chromatic aberration + mobile optimization
