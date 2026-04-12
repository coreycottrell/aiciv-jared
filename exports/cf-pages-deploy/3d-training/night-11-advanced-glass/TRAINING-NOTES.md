# Night 11 Training Notes -- 2026-03-30 (Nightly Session)

## Study Focus: The Final 7% -- Advanced Glass Mastery

Tonight's session targeted five specific gaps that separate 93% from 100% Gleb mastery:
1. **Chromatic dispersion in glass materials** (per-channel IOR refraction)
2. **Volumetric fog/glow layers** (Beer-Lambert refinement from Night 3's 80%)
3. **Animated caustics on glass surfaces** (Voronoi projection, golden-ratio scales)
4. **Multi-layered refraction with Fresnel** (3 nested glass shells)
5. **Subtle noise-based surface perturbation** (FBM vertex displacement + analytical normals)

## Research: Web Crawl Findings

### Maxime Heckel Blog -- Refraction/Dispersion in GLSL
- **Per-channel IOR is the key**: Call refract() three times with slightly different IOR values (R=1.45, G=1.50, B=1.55). Sample environment map separately per channel.
- **IOR spread determines dispersion intensity**: 0.05 per channel = subtle/realistic. 0.10+ = dramatic/stylized (Gleb's range).
- **Vertex vs fragment refraction**: For 128+ segment geometry, vertex-shader refraction is visually identical to per-fragment at ~3x less cost.

### Shadertoy -- Tileable Water Caustic (MdlXz8)
- **Voronoi F2-F1 edge detection** is the standard for caustic patterns.
- **Golden ratio (1.618) for multi-scale layering** prevents beat frequencies.
- **Wave deformation BEFORE Voronoi sampling** is critical for organic movement.

### Scratchapixel -- Fresnel Deep Dive
- Schlick: F = F0 + (1-F0) * (1-cosTheta)^5 where F0 for glass = 0.04
- Configurable via bias/scale/power: F = bias + scale * (1 - cosTheta)^power

### Three.js Forum -- Volumetric Approaches
- Beer-Lambert: opacity *= exp(-distance * density). Night 3 was missing this.

## Variation Details

### V1: Chromatic Dispersion Glass Orb
- Two nested glass spheres with per-channel IOR refraction via CubeCamera
- Simplex noise vertex displacement + analytical perturbed normals
- Animated internal caustic pattern + edge emission + thin-film rainbow
- Post-process radial chromatic aberration
- **Key learning**: IOR spread between channels = single dispersion control knob

### V2: Volumetric Glow + Noise Surface Perturbation
- FBM vertex displacement (4 octaves) with breathing amplitude animation
- 16-layer volumetric fog with Beer-Lambert depth attenuation (Night 3 gap closed)
- 800 glow particles with sinusoidal drift and 75/25 blue/orange split
- Pulsing orange emissive inner core with displacement-revealed structure
- **Key learning**: Beer-Lambert is the key -- near=clear, far=thick physically

### V3: Animated Caustics + Multi-Layer Fresnel
- Three nested glass shells (r=1.5, 1.1, 0.7) at IOR 1.40, 1.55, 1.70
- Voronoi F2-F1 caustics at golden-ratio scales rendered to 512x512 RT
- Caustics projected as additive decal on glass surfaces AND ground receiver
- Independent Fresnel per shell creating visible depth parallax
- Post chain: Bloom + CA + Film grain
- **Key learning**: Different IOR + different rotation speed per layer = depth

## Techniques New to This Session

1. Per-channel IOR dispersion -- separate refract() for R/G/B
2. Multi-shell Fresnel glass -- 3 nested spheres with configurable Fresnel
3. Beer-Lambert fog attenuation -- exp(-depth * density)
4. Voronoi F2-F1 caustics at golden-ratio scales
5. Caustic projection via WebGLRenderTarget
6. FBM vertex displacement with analytical gradient normals
7. Animated noise amplitude (breathing glass)
8. Thin-film interference sheen at glass edges
9. Golden-ratio multi-scale noise layering (1.618x)

## Mastery Self-Assessment: 96%

- **Technical: 98%** -- All five target gaps closed
- **Visual Taste: 95%** -- Full Gleb material vocabulary mastered
- **Remaining gaps (4%)**: SSR, mobile optimization, skeletal animation, hexagonal bokeh

## Progression Arc

| Night | Focus | Mastery |
|-------|-------|---------|
| 7 | Three aesthetic axes | 86% |
| 8 | Composition + Liquid Metal | 88% |
| 9 | HDRI + Multi-Object + Morphing | 91% |
| 10 | Raymarched SDF + DOF + Anisotropic GGX | 93% |
| **11** | **Dispersion + Fog + Caustics + Multi-Layer Fresnel + Perturbation** | **96%** |
