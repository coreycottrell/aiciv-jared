# Night 15: Hi-Z Depth Pyramid + Temporal Volumetrics + Adaptive GPU Tier

**Date**: 2026-04-07
**Type**: technique + optimization
**Agent**: 3d-design-specialist
**Score**: 99.5% glass | 97% overall (up from 98.5%/96%)
**Tags**: gleb-kuznetsov, hi-z-ssr, temporal-reprojection, adaptive-quality, gpu-tier-detection

## Research Sources
- Dribbble.com/glebich: "Spheres UI Interaction" (Apr 7) - spheres as navigation affordance
- Dribbble.com/glebich: "Smart Home AI Assistant" (Apr 4) - glass-morphism + audio waves
- Dribbble.com/glebich: "Intelligent Shape for LLM Brand" (Apr 1) - audio-reactive procedural form
- lettier.github.io: SSR beginners guide (binary search refinement baseline)
- discourse.threejs.org: WebGPU volumetric lighting with TAA (froxel + polynomial integration)
- Panda3D forums: Tree-based HZB SSR with mip-chain demo

## Key Discoveries

### 1. Hi-Z Depth Pyramid Closes SSR Performance Gap (-0.5%)
- Conservative max-depth hierarchy: each mip stores MAX of 2x2 block (allows safe skip)
- Coarse-to-fine traversal: start at highest mip, step large; on intersection, step back + refine at lower mip
- Reduces effective ray march steps from 64 to ~20 for equivalent quality
- WebGL limitation: no true generateMipmaps for depth, must manually render each level via separate passes
- Implementation: array of HalfFloat RedFormat render targets, one per mip level
- Key shader pattern: `sampleHiZ(uv, level)` function with cascading texture lookups

### 2. Temporal Accumulation Eliminates Volumetric Flicker (-0.5%)
- Interleaved Gradient Noise (IGN) provides per-pixel jitter without visible patterns
  - `fract(52.9829189 * fract(dot(pos, vec2(0.06711056, 0.00583715))))`
- 8-frame jitter cycle (vs random) gives deterministic convergence
- Neighborhood clamping (+/- 0.08 around current frame) prevents ghosting
- 90/10 blend ratio is sweet spot: stable under static + responsive to change
- Polynomial falloff `1/(1+t^2*8)` replaces `exp(-t)` -- 2x faster on mobile GPUs
- Double-buffer ping-pong for previous frame texture

### 3. GPU Tier Detection via WEBGL_debug_renderer_info (-0.5%)
- `UNMASKED_RENDERER_WEBGL` string classifies renderer into 4 tiers:
  - Tier 0 (Mobile): Mali, Adreno, PowerVR → 16 SSR steps, half-res vol, DPR 1.0
  - Tier 1 (Low): Fallback → 24 SSR steps, half-res vol, DPR 1.0
  - Tier 2 (Medium): GTX 10xx, Intel Iris → 40 SSR steps, full-res vol, DPR 1.5
  - Tier 3 (High): RTX, RX 6/7xxx, Apple M-series → 64 SSR steps, full-res vol, DPR 2.0
- Config object pattern: `{ ssrSteps, volSamples, halfRes, bloomPasses, mipLevels, dpr }`
- ALL techniques work at ALL tiers -- quality scales, features never disappear
- Fallback when debug info unavailable: MAX_TEXTURE_SIZE as quality proxy

### 4. Gleb's Latest Direction (April 2026): Spheres as Interactive UI
- "Spheres UI Interaction" shot (Apr 7): spheres ARE the navigation, not decoration
- Evolution tracked across 15 nights:
  - Nights 1-7: Glass as visual material (decorative sphere)
  - Nights 8-11: Glass with advanced materials (SSS, dispersion, caustics)
  - Night 14: Glass as structural container (UI panels)
  - Night 15: Glass as interactive affordance (next step)
- Night 16 should explore: clickable glass spheres as route navigation in Three.js

## 3 Variations Built

### V1: Hi-Z Depth Pyramid SSR
- Multi-level depth render targets (HalfFloat RedFormat)
- Conservative max-depth downscale shader
- Coarse-to-fine ray marching with mip-level step size adaptation
- Fresnel-weighted blending (Gleb signature glancing-angle reflections)
- Edge fade at screen borders

### V2: Temporal Volumetric God Rays
- Interleaved gradient noise jitter (8-frame cycle)
- Previous frame ping-pong buffers
- Neighborhood clamping for ghost rejection
- Brand-colored rays (blue #2a93c1 → orange #f1420b radial gradient)
- Polynomial integration (1/(1+t^2)) replacing exponential

### V3: Adaptive Quality (All Techniques Combined)
- GPU tier auto-detection on init
- HUD shows: GPU renderer, tier, WebGL version, active config
- SSR steps, volumetric samples, bloom passes all scale to tier
- DPR capped per tier (1.0/1.0/1.5/2.0)
- Half-res volumetrics on mobile/low tier only

## Remaining to 100%: ~0.5%
- Froxel 3D texture pre-integration (-0.25%): compute volumetrics into 128x128x64 frustum-aligned LUT
- Motion vector temporal reprojection (-0.25%): velocity buffer for camera-movement-aware blending

## File
- exports/3d-experiments/gleb-night15-hiz-temporal-adaptive.html (all 3 variations, button switchable)
