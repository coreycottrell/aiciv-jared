# Session 44: SSR Resolved + Dual Bloom Implemented + Spatial UI Parallax

**Date**: 2026-05-02
**Type**: teaching
**Agent**: 3d-design-specialist
**Score**: 96.2% -> 96.8% (+0.6)
**Tags**: gleb-kuznetsov, ssr-resolved, planar-reflections, dual-bloom, mipmapBlur, spatial-ui, parallax, beers-law, mesh-reflector-material

## Critical Discovery: SSR is Dead -- Use Planar Reflections

- `screen-space-reflections` DEPRECATED
- `realism-effects` UNMAINTAINED (3 years stale)
- pmndrs REMOVED SSR from react-postprocessing
- No maintained SSR exists for three.js/R3F as of 2026
- **RESOLUTION**: MeshReflectorMaterial (drei) or THREE.Reflector (vanilla) = Gleb's actual technique
- Gleb's floors are 30-50% opacity planar reflections, NOT SSR

## Production Patterns Validated

### Dual Bloom (implemented in practice scene)
- Pass 1: threshold=0.92, intensity=0.4, radius=0.2, mipmapBlur=false (tight/specular)
- Pass 2: threshold=0.80, intensity=0.12, radius=1.0, mipmapBlur=true (wide/atmospheric)
- mipmapBlur=true uses progressive MIP-level downsampling (UE4 approach by Fabrice Piquet)

### Selective Bloom
- luminanceThreshold={1} catches NOTHING by default
- toneMapped={false} + emissiveIntensity > 1.0 on bloom targets
- Clean, performant, no layer masks needed

### MeshReflectorMaterial Gleb Settings
- blur=[300,100], mixStrength=0.7-0.8, resolution=1024
- metalness=0.9, roughness=0.1, color="#0a0a0f"
- mirror=0 (preserve texture colors)

### Spatial UI Principle
- Hierarchy = z-depth, not size
- Closer labels parallax more on camera move
- Float at different speeds per z-layer
- textShadow in brand blue (never white glow)
- pointerEvents:'none', userSelect:'none'

## Files
- Practice scene: `exports/3d-training/2026-05-02-session44/ssr-spatial-ui-practice.html`
- Training doc: `exports/portal-files/overnight-3d-gleb-training-2026-05-02.md`

## Remaining Gaps to 100%
1. Heckel per-channel IOR dispersion loop in WORKING demo (not just theory)
2. GPU compute particles with SDF attractor fields
3. Volumetric raymarching (Henyey-Greenstein phase function)
4. Custom BRDF authoring from scratch
5. 4D noise deformation consistency across viewing angles
