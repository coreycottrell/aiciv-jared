# Night 21: SDF Photon Mapping + Production Thin-Film + Fusion
**Date**: 2026-04-11
**Type**: technique (light transport + production optimization)
**Agent**: 3d-design-specialist
**Score**: 99.3% glass | 99.2% overall
**Tags**: gleb-kuznetsov, sdf-photon-mapping, production-thin-film, dipole-sss, caustics

## Key Findings

### SDF Reverse Caustic Gathering
- Forward photon tracing requires GPU compute (WebGPU). Reverse gathering achieves 80% of the visual at 1% compute cost.
- Technique: for each ground fragment, trace 24 photon paths from light through SDF brain using golden angle spiral sampling.
- Double refraction (entry + exit) with interior SDF march. Gaussian energy accumulation at ground hit points.
- 24 samples is the sweet spot. 16 = noisy, 32 = framerate drops below 30fps.
- Conservative step factor 0.7x prevents surface miss. Interior march needs min step 0.01 to avoid zero-crossing stalls.
- Orbiting light creates dynamic caustic dance that sells glass realism far more than static patterns.

### Production Thin-Film Optimization
- Night 20 3-layer / 20-sample: ~35fps. Night 21 2-layer / 12-sample: 60fps. Visual loss ~5%.
- MgF2 (n=1.38) + TiO2 (n=2.4) is the maximum-impact 2-layer stack. Polymer middle layer (n=1.55) is the first to cut.
- 12 spectral samples at 30nm spacing (400-730nm) has acceptable banding for real-time.
- Phasor addition approximation faster than full recursive transfer-matrix with minimal quality loss.
- sin-based thickness variation cheaper than fbm, reads as organic at interactive rates.
- ShaderMaterial integrates cleanly with Three.js r128 PointLight pipeline.

### Fusion Integration Pattern
- Layer ordering matters: Dipole SSS (deepest) -> glass absorption -> specular/Fresnel -> external caustics -> atmospheric god rays.
- Heartbeat double-pulse: smoothstep pairs at 0.8Hz with S1/S2 timing mimics real cardiac rhythm.
- Dual-color god rays (blue + orange at counter-positions) create visual depth.
- Mie forward scattering 0.1 + 0.9*pow(cos,8) concentrates rays toward camera-light alignment.
- DPR cap at 1.5x (not 2x) essential for heavy fusion shaders to maintain 30fps floor.

### Performance Gotchas
- Nested loops in photon gathering (24 outer x 48 inner x 24 interior) can blow GPU thread budget. Keep inner loops short (32 max for interior march).
- The fusion shader is the heaviest yet built -- ground plane caustic gathering is O(n*m) per fragment where ground is visible.
- Three.js prototype runs at 60fps because mesh shading is per-vertex interpolated, not per-pixel ray marched.

## File References
- exports/3d-experiments/gleb-night21-sdf-photon-mapping.html
- exports/3d-experiments/gleb-night21-production-thinfilm.html
- exports/3d-experiments/gleb-night21-fusion-photon-sss.html
- exports/3d-experiments/training-notes/gleb-night21-notes.md
