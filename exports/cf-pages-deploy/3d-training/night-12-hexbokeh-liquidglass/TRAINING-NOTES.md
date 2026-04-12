# Night 12 Training Notes: Hexagonal Bokeh + Liquid Glass + Mobile Fallbacks

**Date**: 2026-03-31
**Mastery Score**: 98% (up from 96%)

## Three Variations Built

### V1: Hexagonal Bokeh DoF Glass Orb
- Custom hexagonal kernel DoF shader (rhomboid decomposition method)
- 3-shell glass orb with chromatic dispersion + depth-staged spheres
- 6 glass spheres at various depths to showcase hex bokeh shape
- Breathing focus animation for organic feel

### V2: Apple Liquid Glass Interaction
- Mouse-driven specular highlight shifting (Apple Liquid Glass technique)
- Custom vertex shader: FBM displacement + mouse-reactive liquid bulge
- Custom fragment shader: per-channel IOR chromatic dispersion + thin-film iridescence
- Interaction light follows cursor with velocity-based intensity

### V3: Mobile-Optimized Adaptive Quality
- 3-tier GPU detection system (HIGH/MEDIUM/LOW)
- Graceful degradation: MeshPhysicalMaterial with native `dispersion` property
- Runtime FPS monitoring with automatic effect stripping below 25fps
- Works on desktop GPUs down to mobile chipsets

## Key Insights
1. Hexagonal bokeh = 3 directional blurs at 60-degree offsets (not circular sampling)
2. Apple Liquid Glass = moving the LIGHT with the cursor, not moving the object
3. Mobile fallback cut order: Transmission > DPR > PostFX > Geometry > Bloom
4. Native `dispersion` on MeshPhysicalMaterial is the mobile-safe path for chromatic effects
