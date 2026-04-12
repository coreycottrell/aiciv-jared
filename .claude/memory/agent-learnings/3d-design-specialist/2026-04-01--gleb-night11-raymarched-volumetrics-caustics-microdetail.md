# Night 11: Raymarched Volumetrics + Caustics + Micro-Detail

**Date**: 2026-04-01
**Type**: technique + teaching
**Score**: 93/100 (up from 91%)
**Agent**: 3d-design-specialist

## Key Techniques

### 1. Raymarched Volumetric Light Cones
- Full-screen quad fragment shader with 48-step raymarching
- Beer-Lambert absorption: transmittance *= exp(-density * stepSize)
- Mie forward-scatter phase: 0.25 / (1.0 + 4.0 * pow(1.0 - cosTheta, 2.0))
- 3-octave FBM noise for scattering density variation
- Dithered ray start (hash-based offset) eliminates step banding
- Depth buffer cutoff: rays stop at scene geometry
- Two independent cones (warm orange + blue) with natural overlap blending
- Parameters: density=0.035, scatterStrength=0.7, coneAngle=cos(PI*0.15), 48 steps

### 2. Voronoi Caustic Floor Patterns
- 30-cell Voronoi, edge distance (d2-d1) raised to power 3 for contrast
- Chromatic split: separate UV lookups per R/G/B with 2% scale offset
- Dual-layer compositing (1x + 1.7x scale) for natural complexity
- Distance falloff: exp(-dist^2 * 0.25) from glass object center
- Brand-color tinting: blue dominant + orange accent
- Animated via UV scroll at different rates per channel

### 3. Micro-Detail Scratch Normal Maps
- 512x512 procedural: 120 random scratch lines + surface noise grain
- normalScale 0.02-0.04 (subliminal -- visible only at grazing angles)
- Applied to all glass MeshPhysicalMaterial via normalMap property
- Different intensity per shell (outer subtler, inner more visible)

## Critical Learnings

1. Raymarch step count: 48 with dithering is sweet spot. Below 32 = banding. Above 64 = diminishing returns.
2. Dithered start: hash(vec3(gl_FragCoord.xy, time * 10.0)) * stepSize breaks fixed-step artifacts.
3. Mie phase function: Forward-scatter bias creates visible beam when looking toward light.
4. Voronoi d2-d1: Natural caustic pattern. Power of 3 gives correct bright/dark contrast ratio.
5. Scratch normalScale below 0.05: Subliminal. Viewer feels imperfections without seeing individual scratches.
6. Volumetric density 0.035: Atmospheric, not foggy. Gleb's volumetrics are always hints of light in air.

## Remaining Gaps to 100%
- Hexagonal bokeh aperture (-1.5)
- Dynamic caustic-to-glass connection (-1)
- Full SSR beyond floor (-1.5)
- Half-res volumetric optimization (-1)
- SSS on thick glass edges (-0.5)
- Volumetric DoF integration (-0.5)

## Files
- Scene: /home/jared/exports/portal-files/3d-training-2026-04-01.html
- Notes: /home/jared/exports/portal-files/3d-training-notes-2026-04-01.md
