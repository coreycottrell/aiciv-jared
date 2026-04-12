# WebGL Photorealistic Glass Shader Overhaul

**Date**: 2026-02-19
**Type**: technique
**Topic**: Raymarched GLSL glass/crystal rendering for PureBrain avatar

## What Was Built

Completely rewrote the avatar fragment shader at `exports/avatar-fluid.html` to achieve photorealistic glass quality.

## Key Techniques Applied

### 1. True Glass Material (Fresnel + Refraction + Reflection)
- Schlick Fresnel approximation with per-channel IOR (1.42/1.44/1.46 for R/G/B)
- `refractRay()` function traces actual refracted ray through the glass
- Secondary march (20 steps) finds exit point of refracted ray
- Environment sample at exit point = what you see THROUGH the glass

### 2. Chromatic Dispersion
- Different IOR per color channel (R=1.42, G=1.44, B=1.46)
- Causes color separation at edges (prism effect)
- Subtle but adds premium optical realism

### 3. Procedural Studio Environment (`sampleEnv()`)
- Replaces flat color ambient with HDRI-approximation
- Key light (top-left warm), rim light (back-right state-color), accent (underneath)
- Ground plane darkening
- Sampled for both reflections and refractions

### 4. Color Absorption Through Glass Thickness
- `absorption = exp(-vec3(0.35, 0.18, 0.08) * thickness * 2.0)`
- Red attenuated more than blue = natural blue-tinted glass at depth
- Thickness computed from exit march distance

### 5. Internal Hexagonal Lattice
- `internalLattice()` samples hex grid at the EXIT point (inside the glass)
- Triplanar hex blend using normal weighting
- Lights up with state color = glowing inner crystal structure

### 6. Subsurface Scattering Approximation
- `subsurface()` marches 8 steps through interior along light direction
- Exponential density = warm glow in thin areas, deep in thick
- Creates the "translucent" gel/frosted look

### 7. Caustic Pattern
- `causticPattern()` procedural caustics using sin interference
- Applied to surface modulated by NdotL = light focusing effect

### 8. Multi-threshold Bloom
- Separate bloom threshold (0.45) and sparkle threshold (1.2)
- Slight chromatic bloom (more blue than red) for glass "glare"

### 9. Liquid Metal Pool
- Normal perturbation from noise = ripple surface
- Mirror-like env sampling for metallic sheen
- Caustic overlay on liquid surface

## Architecture

```
Glass = refracted_env * (1 - fresnel) + reflected_env * fresnel
      + internal_lattice * state_color
      + subsurface_scatter
      + caustic
      + specular_highlights
      + hex_edge_glow
      + chromatic_fringe_at_edges
```

## SDF Improvements
- Smoother object (less deformation for cleaner glass look)
- Tetrahedral normal sampling for higher quality normals
- Audio-reactive surface ripples (sin wave modulated by audio)

## Files Changed
- `/home/jared/projects/AI-CIV/aether/exports/avatar-fluid.html` (desktop + mobile shaders rewritten)

## Server
- Served at https://89.167.19.20:8765 via tools/avatar_chat_server.py
- Server restart: kill existing PID, then `venv/bin/python3 tools/avatar_chat_server.py &`

## Gotchas
- WebGL doesn't render in headless Playwright (swiftshader can't handle complexity)
- Canvas toDataURL() returns black in headless = not a bug in the shader
- Must be tested in a real browser
- Mobile shader uses single-channel refraction (no exit march) to stay within mediump+40iter budget

## Performance Notes
- Desktop: 80 ray march steps + 20 refraction steps + 8 SSS steps = ~108 operations per pixel
- Within highp float capability
- Mobile: 40 steps, single refraction, no SSS march = suitable for mediump
