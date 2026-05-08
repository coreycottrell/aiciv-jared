# Gleb Kuznetsov 3D Training Session - Key Discoveries

**Date**: 2026-05-02
**Agent**: 3d-design-specialist
**Type**: technique
**Tags**: three-js, glass-material, bloom, postprocessing, gleb-aesthetic

## Key Discoveries

### 1. thickness is the Secret Weapon for Glass
MeshPhysicalMaterial with `transmission: 1` looks flat without `thickness`. Setting thickness to 0.5-1.5 enables the refractive lensing distortion that defines Gleb's aesthetic. Without it, glass is just colored transparency.

### 2. Bloom Threshold > Bloom Strength
Set `threshold: 0.85+` on UnrealBloomPass. This makes ONLY emissive elements (emissiveIntensity > 2) glow. Low threshold washes everything out. The contrast between dark surfaces and selective bloom = premium.

### 3. Procedural HDRI via PMREMGenerator
For CDN-only HTML delivery (no HDR file download), create a studio environment using:
- Warm emissive plane above (key)
- Cool blue plane behind (rim)
- Accent color plane to side
PMREMGenerator.fromScene() produces 70% quality of a real HDRI at zero network cost.

### 4. DoubleSide Essential for Transmission
Glass without `side: THREE.DoubleSide` looks hollow from behind. Always enable.

### 5. FogExp2 at Very Low Density
density=0.08 adds subtle depth fade without obscuring content. Free atmosphere.

### 6. Gleb's Complete Formula
- Dark bg (#060608, never pure black)
- Hero glass element center stage
- Orbital floating elements (rings, panels, small spheres)
- Emissive accents for selective bloom
- Mouse parallax for interactivity
- Slow breathing animation (scale pulse 0.02 amplitude)
- Three-point lighting + internal point light

## Files
- Training scene: /home/jared/exports/portal-files/gleb-training-scene-2026-05-03.html
- Training report: /home/jared/exports/portal-files/3D-DESIGN-TRAINING-2026-05-03.md

## Next Steps
1. Real Poly Haven HDRI integration
2. Chromatic aberration pass
3. Meshy API generated hero models
4. Panel UI textures
5. Volumetric lighting
