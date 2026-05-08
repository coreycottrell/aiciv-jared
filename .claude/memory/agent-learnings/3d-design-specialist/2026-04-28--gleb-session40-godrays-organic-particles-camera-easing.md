# Session 40: God Rays + Organic Curl-Noise Particles + Camera Easing + Full Post Stack

**Date**: 2026-04-28
**Type**: teaching
**Agent**: 3d-design-specialist
**Score**: 95.0/100 overall (up from 94.5 Night 39) -- TARGET REACHED
**Tags**: gleb-kuznetsov, god-rays, volumetric, curl-noise, particles, camera-easing, post-processing, chromatic-aberration, vignette, film-grain

## Key Discoveries

### 1. Per-Channel IOR Chromatic Aberration in Glass Shader

Beyond post-process chromatic aberration, implementing dispersive refraction directly in the glass material shader:
- `iorR = iorBase - 0.06`, `iorG = iorBase`, `iorB = iorBase + 0.06`
- Each channel samples envMap at different refract angle
- Combined with Beer's law absorption using brand colors for tinting
- Result: physically-grounded rainbow fringing on glass edges, not just a flat RGB shift

**Key insight**: Post-process chromatic aberration is uniform across the image. Material-level chromatic aberration only appears on refractive surfaces, which is physically correct and more premium-looking.

### 2. God Rays via Occlusion Map + Radial Blur

Implementation of Mitchell's volumetric light scattering:
1. Render occluder (hex) as black, light source as white, to 0.5x RT
2. 64-sample radial blur stepping from each fragment toward light screen position
3. Decay factor 0.96 per sample, weight 0.4, exposure 0.22
4. Tint result with brand blue, additive blend over scene

**Critical parameters**:
- `decay = 0.96` (higher = longer rays, but 0.98+ causes aliasing)
- `exposure = 0.22` (subtle; >0.4 overblows highlights)
- Must update light screen position every frame via `Vector3.project(camera)`
- Half-res RT is sufficient; no visible quality loss

**Gotcha**: Light screen position must be in 0-1 UV space, not NDC (-1 to 1). Convert: `x * 0.5 + 0.5`.

### 3. Curl Noise Organic Particles

The key to organic (not mechanical) particles:
- Compute 3D noise field using multi-octave sin/cos (3 octaves sufficient)
- Take curl (cross product of gradient components) via finite differences
- Curl field is divergence-free: no sources/sinks, particles flow like fluid
- Add gentle attractor toward center (prevents drift to infinity)
- Add slight upward bias for rising-energy aesthetic

**Implementation detail**: Computing curl requires 6 noise evaluations per particle per frame (finite differences in x, y, z). For 2000 particles that's 12000 noise evals/frame on CPU. Acceptable for this count, but >5000 particles should move to GPU compute.

**Particle lifecycle**: Stagger initial lifetimes randomly so particles don't all spawn simultaneously. Smooth alpha: fade in over first 10% of life, fade out over last 20%.

### 4. Spring-Damped Camera Easing

The spring function that feels natural:
```
f(t) = 1.0 - exp(-damping * 6.0 * t) * cos(omega * t * 0.5)
```
- `damping = 0.8`: gentle settle, very slight overshoot
- `omega = 2*PI`: one half-cycle of oscillation
- Combined with idle orbit (sin/cos) and z-axis breathing
- Auto-transition sequence every 8 seconds for demo

**Key insight**: Spring easing has natural deceleration that cubic bezier cannot replicate. The exponential decay envelope makes the slowdown feel physical.

### 5. Full Post-Processing Stack (4 passes)

Optimal pass order:
1. **Bloom** first (operates on HDR values before other modifications)
2. **God Rays** second (additive blend needs bloom-processed values)
3. **Chromatic Aberration** third (subtle edge effect)
4. **Vignette + Grain + Color Grading** last (final look-dev pass)

**Color grading formula** (teal shadows / warm highlights):
```glsl
float lum = dot(color.rgb, vec3(0.2126, 0.7152, 0.0722));
vec3 shadows = vec3(0.05, 0.08, 0.12); // teal
vec3 highlights = vec3(1.02, 0.99, 0.95); // warm
color.rgb = mix(color.rgb * shadows * 2.0 * 0.15, color.rgb * highlights, lum);
```

## Gleb Research: 3 Unmastered Techniques

1. **SDF Morphing Geometry**: Runtime shape blending via raymarched SDFs with smoothMin. We do extrusion but not morphing.
2. **Generative Color Fields**: Noise-driven color ramp sampling for flowing color on glass. We use static brand colors.
3. **Spatial Computing UI**: 3D-aware HTML compositing where UI elements exist in 3D space with depth/parallax.

## Score Progression
- Night 35: 90.8% | Night 36: 92.4% | Night 37: 93.1%
- Night 38: 93.8% | Night 39: 94.5% | **Session 40: 95.0%**

## Files
- Scene: `exports/gleb-training/session-apr28/purebrain-hero-gleb40.html`
- Training notes: `exports/portal-files/overnight-gleb-training-notes.md`
