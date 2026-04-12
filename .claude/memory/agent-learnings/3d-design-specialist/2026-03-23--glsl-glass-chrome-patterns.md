# 3D Design: GLSL Glass + Chrome Patterns
**Date**: 2026-03-23
**Type**: technique
**Agent**: 3d-design-specialist
**Session**: Nightly Gleb training — night 3

## Domain Warping Stack (the core pattern — memorize)
```glsl
vec2 q = vec2(fbm(st + t_a), fbm(st + t_b));
vec2 r = vec2(fbm(st + q + offset_a), fbm(st + q + offset_b));
float f = fbm(st + r);
```
Three layers. Each warps by the previous. This creates organic non-repeating fields.

## IQ Palette Function (banding-free color)
```glsl
vec3 palette(float t) {
  return a + b * cos(6.28318 * (c * t + d));
}
```
Tweak `d` vector to shift hues to brand colors. Never use linear gradient maps in GLSL.

## Mouse Gaussian Warmth
```glsl
float warmth = exp(-dist * dist * k);
f = smax(f, warmth * strength, blend_r);
```
`k` controls tightness. `smax()` blends smoothly (no hard edges).

## smax() — soft maximum
```glsl
float smax(float a, float b, float k) {
  float h = max(k - abs(a-b), 0.0) / k;
  return max(a,b) + h*h*k*0.25;
}
```
Replace all max() calls with this in interactive shaders.

## Chrome Specular Band
```glsl
float spec = exp(-pow(abs(uv.x - mouseX), 2.0) * 25.0) * 0.3;
// Add secondary dimmer specular offset for depth
float spec2 = exp(-abs(uv.x - mouseX*0.7 - 0.15) * 30.0) * 0.12;
```
Two specular highlights = chrome depth. One = flat plastic.

## CSS Glass Over WebGL Canvas Pattern
- WebGL canvas renders live fluid/chrome behind the element
- CSS `backdrop-filter: blur(16-20px) saturate(150-160%)` glass layer on top (z-index 1)
- `::before` pseudo-element adds specular highlight (linear-gradient from rgba(255,255,255,0.13) to transparent)
- `::after` pseudo-element adds chromatic aberration edge (blue-to-orange gradient line)

## Performance Budget
- Full viewport FBM (4 oct): 60fps desktop, ~45fps mobile
- 3 simultaneous card canvases: ~45fps desktop, ~30fps mobile
- Small element WebGL (buttons/badges): <1ms GPU each, fine for 10+ elements
- Precision: highp for full-viewport, mediump for small elements

## Files Produced
- /home/jared/exports/3d-training/night-2026-03-23/variation-a-glass-card.html
- /home/jared/exports/3d-training/night-2026-03-23/variation-b-fluid-gradient.html
- /home/jared/exports/3d-training/night-2026-03-23/variation-c-chrome-elements.html
- /home/jared/exports/3d-training/training-notes-2026-03-22.md

## Mastery update: 85% → 88%
Gaps remaining: MeshTransmissionMaterial in actual R3F scene, real SDF-based two-pass refraction, HDRI-driven IOR, true WebGL particles.
