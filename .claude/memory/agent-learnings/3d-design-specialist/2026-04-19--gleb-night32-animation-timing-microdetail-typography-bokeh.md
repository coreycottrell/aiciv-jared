# Night 32: Animation Timing System + Micro-Detail + Typography + Bokeh Shapes

**Date**: 2026-04-19
**Type**: teaching
**Agent**: 3d-design-specialist
**Score**: 86.2/100 overall (up from 83.8 Night 31)
**Tags**: gleb-kuznetsov, animation-timing, easing, micro-detail, dust-particles, lens-dirt, micro-scratches, typography, troika-sdf, bokeh-shapes, hexagonal-bokeh, anamorphic

## Key Discoveries

### 1. Gleb's 4-Tier Animation Timing System
- **Micro (50-150ms)**: Button, toggle. Easing: cubic-bezier(0.2, 0, 0, 1)
- **Element (150-350ms, sweet=250ms)**: Card, panel. Easing: cubic-bezier(0.16, 1, 0.3, 1) -- THE signature curve
- **View (350-550ms, sweet=450ms)**: Full transitions. Two-phase: ease-out then decelerate
- **Ambient (800-3000ms)**: Idle, background. Sine easing. NEVER stops.
- Mixing tiers creates temporal depth in a scene.

### 2. Asymmetric Response Principle
Rise and fall are NEVER the same duration:
- Audio: rise 80-120ms, fall 300-500ms (3-5x ratio)
- Material state: enter 250ms, settle 400ms (1.6x ratio)
- Light/particles: appear instant, fade 600-1000ms (infinite ratio)
- Text: appear 200ms per letter, disappear 100ms (0.5x -- exits are faster)
- Rule: things that APPEAR take longer EXCEPT light which appears instantly and fades slowly.

### 3. Micro-Detail Threshold Rule
If you can obviously see the detail on first glance, reduce by 50%.
- Dust particles: 200 count, 0.4 opacity, twinkle modulation
- Lens dirt: 0.08 intensity (bloom-reactive additive blend)
- Micro-scratches: normalScale [0.025, 0.025], visible only in specular sweeps
- The detail should be FELT more than SEEN.

### 4. Troika SDF Typography in 3D
Three entry patterns for text:
- **Letter-by-letter**: 30ms stagger, scale 0.95->1.0 per letter
- **Tracking expansion**: letter-spacing 150%->100% over 400ms
- **Depth entry**: z-position through glass over 600ms (most premium)
All use decelerate easing (0.16, 1, 0.3, 1). Text exists in scene graph, inherits lighting, refracts through glass.

### 5. Bokeh Shape Customization
Hexagonal: sector-clamped radius sampling. Anamorphic: directional scale (squeeze 1.33-2.0).
Implement as custom Effect extending postprocessing Effect base class.
- Hex = product shots (engineered feel)
- Octagonal = emotional scenes (softer)
- Anamorphic = hero sections (cinematic, wide)

### 6. Glass State Transitions During Motion
Changing roughness + transmission during element movement creates causal illusion.
- Moving glass becomes slightly more opaque (roughness += velocity * 0.05)
- Specular highlights stretch anisotropically during motion
- Shadow response delays by 4 frames (67ms) while highlight is instant

## Gotchas
- Ward anisotropic: max(NdH, 0.001) to prevent NaN
- Lens dirt above 0.15 intensity looks like dirty camera, not premium
- Troika Text material override syntax needs testing in actual R3F scene
- HexBokeh kernel: ensure sample count sufficient for clean hex shape (64+ samples)

## Easing Library (Copy-Paste Ready)
```javascript
const GLEB_EASINGS = {
  decelerate: 'cubic-bezier(0.16, 1, 0.3, 1)',      // 70% of all transitions
  anticipate: 'cubic-bezier(0.4, 0.0, 1, 1)',        // pre-motion gather
  impulse: 'cubic-bezier(0.0, 0.0, 0.2, 1.0)',       // audio/reactive
  release: 'cubic-bezier(0.4, 0.0, 0.8, 0.4)',       // slow decay
  ambient: 'cubic-bezier(0.37, 0, 0.63, 1)',          // sine approximation
  spring: { stiffness: 300, damping: 25, mass: 1 },   // solid elements
  glassSpring: { stiffness: 200, damping: 18, mass: 0.8 }, // glass (lighter)
}
```

## Score Progression
- Night 28: 78.6%
- Night 31: 83.8%
- Night 32: 86.2% (+2.4 points)
- Biggest jumps: Animation timing 68%->80%, Micro-detail 58%->75%, Typography 52%->72%, Bokeh 48%->68%

## Files Generated
- Training report: `/home/jared/exports/portal-files/OVERNIGHT-3D-TRAINING-V2-2026-04-19.md`
- 2 scene specifications: "The Partnership" + "Memory Moat"
- Cumulative techniques: 34

## Next Session Goals
1. Implement HexBokehEffect as running code
2. Build "The Partnership" as Vite+R3F project
3. Procedural scratch normal map generator
4. Lens dirt texture + bloom-reactive shader
