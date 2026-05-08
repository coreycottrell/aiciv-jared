# Night 34: PureBrain Hex Glass + Soft AI Sphere + Magnetic Fields

**Date**: 2026-04-22
**Type**: teaching
**Agent**: 3d-design-specialist
**Score**: 89.2/100 overall (up from 87.8 Night 33)
**Tags**: gleb-kuznetsov, hex-icon, glass-morphism, magnetic-fields, soft-sphere, chromatic-aberration, dust-particles, cursor-reactive, flux-pro

## Key Discoveries

### 1. New Gleb Portfolio Insights (April 2026 research)

From studying Gleb's latest Dribbble work:
- **"Soft AI sphere"** pattern: Glass spheres for AI branding are SOFTER now -- less sharp caustics, more diffuse internal glow. IOR stays 1.45-1.5 but roughness drops to 0.02 (mirror-smooth).
- **"Intelligent shape for LLM brand"** pattern: Organic, not geometric. Shape language for AI = flowing/breathing, not hard-edged.
- **"Magnetic 3D Illustration"** pattern: Field lines as thin tube geometries (r=0.005) at very low opacity (0.08-0.15) with additive blending. Creates "energy field" without cluttering scene.
- **Agentic UI shift**: Latest work integrates pulsing orbs with UI overlays. Glass as CONTAINER for UI information, not just decoration.

### 2. Hex + Sphere Composition Works

Central hexagon (flat glass) + inner sphere (volumetric glass) = dual-layer depth:
- Hex reads as "brand shape" (PureBrain identity)
- Sphere reads as "intelligence" (AI core)
- Together they create focal depth: eye goes to sphere (sharp, bright) then reads hex (structured, dim)
- This is a reusable composition: brand-shape wrapping intelligence-shape.

### 3. Magnetic Field Lines as Scene Atmosphere

12 CatmullRom tube curves (r=0.005, 40 segments each) with additive blending at 0.08-0.15 opacity:
- Creates "energy field" that grounds the hex in space
- Alternating blue/orange per Gleb's accent color rules
- Slow rotation (0.02 rad/s) makes them barely perceptible
- Key: they MUST be slower than main subject animation or they steal focus

### 4. Radial Chromatic Aberration (Refined)

Custom shader with distance-based strength:
```
strength = smoothstep(0.1, 0.7, dist_from_center)
offset = base_offset * strength * (1.0 + sin(time * 0.5) * 0.1)
```
- Base offset: 0.0015 (conservative)
- Stronger at edges, zero at center -- mimics real lens behavior
- Time-based pulse at 0.1 amplitude adds "living lens" quality
- This is MORE physically accurate than flat CA and reads better

### 5. Glass Material Parameter Sweet Spot (r128 MeshPhysicalMaterial)

For Three.js r128 (no MeshTransmissionMaterial available in CDN):
```javascript
{
  transmission: 0.92,
  thickness: 0.8,
  ior: 1.45,
  roughness: 0.03,       // near-mirror for glass
  clearcoat: 1.0,
  clearcoatRoughness: 0.05,
  envMapIntensity: 1.5,   // env map essential for reflections
  attenuationDistance: 2.0, // how deep color penetrates
}
```
- Without envMap, glass looks flat (must use CubeCamera or HDRI)
- attenuationColor should match brand color (blue for PureBrain)
- DoubleSide rendering essential for glass (see backface through front)

### 6. Bloom Parameters (Night 32 Refinement Applied)

```javascript
UnrealBloomPass(resolution, 0.45, 0.6, 0.88)
// intensity=0.45, radius=0.6, threshold=0.88
```
- Threshold 0.88 = only brightest specular highlights bloom (NOT the whole glass)
- Intensity 0.45 = visible glow without washing out
- Radius 0.6 = medium spread (not too tight, not too diffuse)
- This combination produces the "selective glow" Gleb achieves -- bloom on edges/highlights only

### 7. Cursor Reactivity Sweet Spot

```javascript
hexGroup.rotation.x = mouseY * 0.04;
hexGroup.rotation.y = mouseX * 0.04;
```
- 0.04 multiplier = barely perceptible tilt
- Affects WHOLE group (hex + sphere + satellites) for unified motion
- No damping needed at this subtlety level
- Higher values (0.1+) make it feel like a game, not premium design

### 8. FLUX Pro Prompt Engineering for Gleb Style

Effective prompt structure:
1. Subject: "glowing neural network brain structure made of transparent glass"
2. Material: "deep blue (#2a93c1) tint with orange (#f1420b) synaptic connections"
3. Effects: "subsurface scattering, chromatic aberration, volumetric bloom"
4. Atmosphere: "micro-particles of light dust, photons"
5. Background: "pure dark (#060606)"
6. Lighting: "Studio HDRI lighting from above-right, sharp specular highlights"
7. Quality: "Octane render quality, hyperrealistic glass material"
8. Style: "Gleb Kuznetsov aesthetic, dark luxury 3D design, premium CGI product shot"

Key: include hex colors directly in prompt. FLUX responds to color codes.

## Techniques Applied (Cumulative: 42)

New this session:
40. Magnetic field line atmosphere (CatmullRom tubes, additive, 0.08-0.15 opacity)
41. Hex + Sphere dual-layer composition
42. Radial CA with time-based pulse

## Gotchas

- CubeCamera in r128 must hide the target mesh before rendering to avoid self-reflection artifacts
- FogExp2 density 0.08 works for this scene scale but would need adjustment for larger/smaller scenes
- Satellite hex glass state transition (roughness += velocity * 0.03) is subtle but adds realism during orbital drift
- FLUX prompt_upsampling: true helps with detail quality -- always enable for Gleb-style renders

## Score Progression
- Night 28: 78.6%
- Night 31: 83.8%
- Night 32: 86.2%
- Night 33: 87.8%
- Night 34: 89.2% (+1.4 points)
- Biggest gains: Composition +2% (hex+sphere layering), Atmosphere +3% (magnetic fields), FLUX prompting +2%

## Files Generated
- Three.js scene: `/home/jared/exports/portal-files/gleb-training-session-apr22.html`
- FLUX image: `/home/jared/exports/portal-files/gleb-training-output-apr22.png`
- Training notes: this file

## Next Session Goals
1. Push past 90% by implementing volumetric light shafts (god rays) in r128
2. Test Troika SDF text IN the glass scene (text-behind-glass refraction)
3. Implement hexagonal bokeh DoF shader
4. Try "soft AI sphere" with animated displacement (vertex shader noise)
