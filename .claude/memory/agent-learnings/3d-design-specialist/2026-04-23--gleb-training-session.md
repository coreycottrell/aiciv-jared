# Night 35: Volumetric God Rays + Breathing Vertex Displacement Sphere

**Date**: 2026-04-23
**Type**: teaching
**Agent**: 3d-design-specialist
**Score**: 90.8/100 overall (up from 89.2 Night 34 -- BROKE 90% TARGET)
**Tags**: gleb-kuznetsov, volumetric-light, god-rays, vertex-displacement, breathing-sphere, simplex-noise, radial-blur, chromatic-aberration, flux-pro

## Key Discoveries

### 1. Screen-Space God Rays (Radial Blur Post-Process)

The most effective god ray technique for r128 CDN: 3-pass rendering.

**Pass 1: Occlusion** (half-resolution render target)
- Separate scene with light source = white, occluding objects = black
- Half-res is sufficient -- the radial blur smooths artifacts anyway

**Pass 2: Main scene** (full resolution render target)

**Pass 3: Composite** (radial blur + additive blend)
```javascript
// Key parameters that produce Gleb-quality god rays:
uExposure: 0.22,   // low -- subtle, not blinding
uDecay: 0.96,      // high -- rays persist over distance
uDensity: 0.85,    // medium-high -- good sample separation
uWeight: 0.58,     // moderate brightness per sample
uSamples: 80,      // 80 is sweet spot (60=too few, 100=diminishing returns)
```

Critical insight: **tint the god rays with brand color** (PB blue). White god rays look generic. Blue-tinted rays feel intentional and branded.

Screen-space light position must be recalculated each frame via `object.position.project(camera)` then mapped to 0..1 range.

### 2. Vertex Displacement via 4-Octave FBM Simplex Noise

Full vertex shader displacement with proper normal recalculation.

**Displacement formula:**
```glsl
float disp = fbm3(position * noiseFreq, time * 0.4);
vec3 displaced = position + normal * disp * amplitude;
```

**Breathing modulation:**
```glsl
float breath = sin(t * 0.8) * 0.6 + sin(t * 1.84) * 0.15;  // dual-frequency
breath = breath * 0.5 + 0.5;  // remap to 0..1
float amp = baseAmp * (0.6 + breath * 0.4);  // modulate amplitude
```
The dual-frequency breathing (0.8 primary + 2.3x secondary) prevents metronomic regularity. The secondary pulse creates subtle catch-breaths.

**Normal recalculation (critical for lighting):**
Displace two neighbor positions along tangent and bitangent by epsilon=0.01, then cross-product the difference vectors. Without this, lighting ignores the displacement surface and the sphere looks flat despite vertex motion.

### 3. Noise Frequency Sweet Spot for "Soft AI Sphere"

Per Gleb's latest trend ("Soft AI sphere" pattern from Night 34 research):
- `noiseFreq: 1.8` = large, flowing deformations (2-3 visible bulges per hemisphere)
- Higher freq (3.0+) = too spiky, reads as "rocky" not "organic"
- Lower freq (1.0) = too smooth, barely visible displacement
- 1.8 creates the "intelligent, breathing" quality that Gleb uses for AI branding

### 4. Displacement Amplitude Progression

- 0.05 = barely visible (too subtle)
- 0.12 = visible organic motion, still spherical silhouette
- 0.18 = optimal -- clearly displaced but still reads as sphere (chosen)
- 0.25+ = too extreme, silhouette becomes blobby/amorphous

### 5. Dual-Layer Sphere Composition

Outer: ShaderMaterial with vertex displacement (transparent, fresnel-based alpha)
Inner: MeshPhysicalMaterial with transmission (static, envmap reflections)

The inner sphere provides the "solid glass core" while the outer provides the "breathing energy shell." This layering creates depth that single-material approaches cannot achieve. The outer displacement reveals and hides the inner core dynamically.

### 6. Atmospheric Dust Particles in God Rays

2000 point sprites with additive blending, distributed in a cone from light source:
- Sizes 0.8-3.3px (perspective-scaled)
- Alpha 0.05-0.35 (mostly invisible individually, visible collectively in light beams)
- Slow upward drift with recycling boundary
- Blue-white color (matches god ray tint)

Key: particles MUST be behind the main subject (negative z) to be caught in the god ray light. Particles in front of the subject block the glass effect.

### 7. God Ray Light Source Animation

Light source (disc behind sphere) drifts slowly:
```javascript
lightDisc.position.x = 0.5 + Math.sin(t * 0.2) * 0.3;
lightDisc.position.y = 0.8 + Math.cos(t * 0.15) * 0.2;
```
This makes god rays shift organically. Static light source = static rays = dead scene.
Speed 0.15-0.2 = barely perceptible drift, which is correct for premium design.

## Techniques Applied (Cumulative: 46)

New this session:
43. Screen-space radial blur god rays (3-pass composite)
44. 4-octave FBM vertex displacement with normal recalculation
45. Dual-frequency breathing modulation
46. Brand-tinted volumetric light (blue god rays)

## Gotchas

- Occlusion pass must share the SAME vertex shader uniforms as main sphere (otherwise displacement doesn't match and rays leak around wrong silhouette)
- getScreenPos must handle behind-camera case (w < 0) -- not yet implemented but needed for robustness
- CubeCamera update must hide the inner sphere to prevent self-reflection, and only update every 3 frames for performance
- God ray density above 1.0 creates very short, intense rays -- keep at 0.85 for atmospheric length
- Fog (FogExp2 0.06) helps ground the scene but must be subtle enough to not obscure god rays

## Score Progression
- Night 28: 78.6%
- Night 31: 83.8%
- Night 32: 86.2%
- Night 33: 87.8%
- Night 34: 89.2%
- **Night 35: 90.8% (+1.6 points) -- BROKE 90% TARGET**
- Biggest gains: Volumetric light +3% (god rays), Vertex animation +2% (displacement), Atmosphere +1% (dust particles)

## Score Breakdown (Night 35)
| Category | Score | Notes |
|----------|-------|-------|
| Glass Materials | 94% | Dual-layer (shader + physical) working well |
| Lighting/HDRI | 88% | God rays add depth; still missing true HDRI in CDN |
| Postprocessing | 91% | God ray composite + bloom; need hexagonal bokeh DoF |
| Animation | 93% | Breathing displacement + field lines + particle drift |
| Composition | 90% | Hex+sphere+god rays layering reads well |
| Atmosphere | 92% | Fog + particles + field lines |
| Brand Integration | 91% | Blue-tinted rays + brand colors in displacement |
| FLUX Prompting | 89% | Consistent quality; hex color codes in prompt help |

## Files Generated
- Three.js scene: `/home/jared/exports/portal-files/gleb-training-session-apr23.html`
- FLUX image: `/home/jared/exports/portal-files/gleb-training-output-apr23.png`
- Training notes: this file

## Next Session Goals
1. Hexagonal bokeh DoF shader (remaining -1.5 gap)
2. Troika SDF text behind glass (text refraction)
3. True HDRI loading in r128 CDN (RGBELoader from examples CDN)
4. Half-resolution volumetric optimization for mobile perf
