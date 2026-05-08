# Gleb Training Session 3 - Production Techniques Learned

**Date**: 2026-05-02
**Type**: technique
**Agent**: 3d-design-specialist
**Confidence**: high

## Context

Third training session pursuing Gleb Kuznetsov-level 3D web aesthetics. Closed four gap areas from session 2 self-assessment.

## Key Techniques Mastered

### 1. FBO Dispersion (True Prismatic Refraction)
- Render scene to WebGLRenderTarget WITHOUT the glass object
- Sample that texture 3x with different IOR per RGB channel (R=1.15, G=1.18, B=1.22)
- Use `refract()` GLSL function with eye vector and world normal
- Animate normals subtly for living refraction feel
- Fresnel rim adds edge glow without separate effect

### 2. GPGPU Particles via GPUComputationRenderer
- 128x128 texture = 16,384 particles at 60fps
- Position shader: curl noise + attractor + orbital cross-product
- Ping-pong textures handle state between frames
- Read computed texture in vertex shader via `texture2D(uPositionTexture, reference)`
- Simplex noise in GLSL: use mod289/permute/taylorInvSqrt pattern

### 3. Selective Bloom (Layer-Based Dual Composer)
- BLOOM_LAYER = 1; objects.layers.enable(BLOOM_LAYER)
- bloomComposer: darkens non-bloomed objects to black, renders bloom pass
- finalComposer: renders full scene, composites bloom additively via ShaderPass
- This is THE technique for premium - never use scene-wide bloom

### 4. Real HDRI Loading
- RGBELoader + PMREMGenerator for proper environment mapping
- Poly Haven CDN: `https://dl.polyhaven.org/file/ph-assets/HDRIs/hdr/1k/{slug}_1k.hdr`
- Always include procedural fallback for CORS/local testing

## Performance Notes
- FBO extra pass: ~30% render cost increase
- Dual composer: ~40% cost but essential for quality
- GPGPU 128x128: negligible GPU cost vs CPU particle simulation
- Total scene: should hold 60fps on modern desktop

## Gotchas Discovered
- `bloomComposer.renderToScreen = false` is critical (composite separately)
- Must clone RenderPass for each composer or they conflict
- Dispersion sphere must be hidden during FBO capture pass
- HDRI from Poly Haven may CORS-fail on local file:// - always have fallback

## Files
- Scene: `/home/jared/exports/portal-files/gleb-training-scene-3-2026-05-05.html`
- Report: `/home/jared/exports/portal-files/3D-DESIGN-TRAINING-SESSION-3-2026-05-05.md`

## Score Progression
- Session 1: 7/10 (basic glass + particles)
- Session 2: 8.5/10 (custom shaders + god rays + better composition)
- Session 3: 9/10 (FBO dispersion + GPGPU + selective bloom + HDRI)

## What's Next (Session 4 targets for 10/10)
- Volumetric raymarching inside sphere
- Screen-space reflections (SSR)
- Temporal AA for thin geometry
- Sound reactivity
- Animation choreography (timed sequences)

Tags: three-js, 3d-design, gleb-aesthetic, fbo-dispersion, gpgpu, selective-bloom, hdri, training
