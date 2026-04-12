# Night 9 Training Notes — 2026-03-28 (Nightly Session)

## Study Focus: Closing the Final 3 Gaps to 90%+ Mastery

Tonight targeted all three remaining gaps identified in Night 8:
1. Real-world asset integration (HDRI environments)
2. Complex multi-object composition
3. Animated transitions between composition states

### V1: HDRI Glass Refraction — Procedural Studio Environment
- **Technique**: Procedural equirectangular HDRI generation with 3-light studio setup (warm key upper-right, cool blue fill lower-left, orange rim from behind). Physical glass with transmission, thickness, IOR, attenuation color. Chrome counterbalance sphere + orange emissive pip.
- **Gleb Reference**: His product renders use professional studio HDRIs. The warm key + cool fill is his signature lighting recipe.
- **What worked**: Procedural HDRI avoids external asset dependencies while replicating the visual quality. The `attenuationColor` on thick glass creates that blue-tinted depth that makes glass feel REAL — not just transparent but volumetric.
- **Key learning**: `thickness: 2.5` with `attenuationColor` is the magic combination. Thin glass (thickness < 1.0) looks like a window. Thick glass with attenuation looks like a MATERIAL. The HDRI's warm/cool split creates natural color variation in the refraction — you see warm highlights AND blue shadows through the glass simultaneously.
- **Research applied**: Shadertoy glass sphere refraction techniques (XdVfDd) informed the IOR choice. Thick glass shader (3dSXRy) confirmed that internal absorption (attenuation) is what separates good glass from great glass.

### V2: Multi-Object Constellation — Visual Hierarchy in 3D
- **Technique**: 4-tier hierarchy system: PRIMARY (large glass icosahedron at PHI-offset), SECONDARY (chrome torus + glass octahedron), TERTIARY (5 orange accent pips), CONNECTORS (subtle light beams linking forms). Structural wireframe overlay on primary. FogExp2 for depth atmosphere.
- **Gleb Reference**: His dashboard/product shots never have equal-weight elements. There's always a clear hero with supporting cast.
- **What worked**: The wireframe overlay at 6% opacity is a subtle but powerful "structural reveal" — it hints at the geometry underlying the glass without competing with the refraction. The connector beams (8% and 6% opacity) create invisible relationships between objects that the eye follows subconsciously.
- **Key learning**: **Hierarchy is exponential, not linear.** The primary is ~4x the volume of secondary A, which is ~3x secondary B, which is ~10x each pip. Equal-sized objects create chaos; exponential scale difference creates instant readability. The 5 pips work because they're so small they register as "energy" not "objects" — they're compositional seasoning, not ingredients.
- **Composition rule discovered**: In multi-object 3D compositions, you need exactly 3 relationship types: (a) proximity grouping, (b) scale hierarchy, (c) material contrast. V2 uses all three: proximity creates primary/secondary clusters, scale creates reading order, material contrast (glass vs chrome vs emissive) creates visual variety without color chaos.

### V3: Morph Transitions — Shape-Shifting Particle System
- **Technique**: 5,000 particles with dual position attributes (current + target). Custom vertex shader with per-particle staggered easing (each particle has a random seed that offsets its morph timing by 0-400ms). Turbulence injection at morph midpoint. 4 states: Sphere → Torus → Icosahedron → Dispersed Cloud. Click-triggered transitions.
- **Gleb Reference**: His animated transitions between UI states use similar staggered timing — not everything moves at once
- **What worked**: The stagger is EVERYTHING. Without it (uniform morph), all 5,000 particles move identically and it looks robotic. With per-particle stagger, the morph has a wave-like organic quality. The turbulence injection at morph midpoint (`sin(morph * PI) * 0.15`) creates a brief "chaos" moment that makes the transition feel physical — like the particles are briefly unbound before reorganizing.
- **Key learning**: **Morph quality = stagger range + turbulence envelope.** Too little stagger (< 100ms) looks mechanical. Too much (> 600ms) looks sloppy. The 400ms range with cubic easing hits the sweet spot. The turbulence envelope (zero at start/end, peak at midpoint) is a sine-of-morph pattern — this creates the "dissolve → reform" feeling that Gleb's transitions achieve.
- **Research applied**: Codrops' March 2026 tutorial on 3D transitions with GSAP confirmed the stagger approach. GSAP's `stagger` parameter in timeline animations uses the same principle we implemented in pure GLSL.

## Techniques New to This Session

1. **Procedural equirectangular HDRI**: Generate Float32 DataTexture with directional light sources calculated from dot products with light direction vectors. Power function controls light spread (higher = sharper spotlight, lower = soft fill).

2. **Multi-tier visual hierarchy**: PRIMARY → SECONDARY → TERTIARY → CONNECTOR. Each tier has distinct material language (glass, chrome, emissive, line).

3. **Per-particle stagger morphing**: `aSeed` attribute (0-1 random) offsets each particle's morph timing. Clamp + remap in vertex shader creates wave effect.

4. **Turbulence injection**: `sin(morph * PI)` envelope ensures turbulence only appears during transition, not at rest states.

## Post-Processing Techniques Practiced
- Chromatic aberration (all 3 variations: 0.0005-0.0007 range)
- Film grain (all 3: 3.5-4% intensity)
- Asymmetric vignette (V1: center shifted to 0.45)
- Standard vignette (V2, V3)
- Additive blending for particles (V3)

## Mastery Self-Assessment: 91%

- **Technical: 95%** (procedural HDRI, physical glass pipeline, custom morph shaders, multi-pass post-processing — all executing fluently)
- **Visual Taste: 87%** (composition hierarchy is now intuitive, transition timing feels natural)
- **Gaps remaining**:
  - Texture integration (procedural noise textures as roughness/normal maps — haven't explored PBR texture stacking yet)
  - Complex rigged animation (skeletal morph targets for character-like forms)
  - Performance profiling on mobile (all demos target desktop GPU — mobile fallback strategy needed)

## Progression Arc

| Night | Focus | Mastery |
|-------|-------|---------|
| 7 | Three aesthetic axes (Crystal, Plasma, Chrome) | 86% |
| 8 | Composition & Negative Space | 88% |
| **9** | **HDRI + Multi-Object + Morphing** | **91%** |

The 85% → 91% jump reflects closing all three identified gaps simultaneously. The remaining 9% is specialized territory (PBR textures, rigged animation, mobile optimization) that requires a different kind of study — less Gleb-specific, more production engineering.
