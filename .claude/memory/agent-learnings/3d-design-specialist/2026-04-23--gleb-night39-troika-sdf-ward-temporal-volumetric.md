# Night 39: Troika SDF + Ward BRDF + Half-Res Volumetric + Temporal Reprojection

**Date**: 2026-04-23
**Type**: teaching
**Agent**: 3d-design-specialist
**Score**: 94.5/100 overall (up from 93.8 Night 38)
**Tags**: gleb-kuznetsov, troika-sdf, ward-brdf, anisotropic, volumetric, temporal-reprojection, caustics

## Key Discoveries

### 1. Troika SDF Text via Render Target Pipeline

Troika `Text` component generates SDF atlas on the fly from any WOFF2 font. To use with custom refraction shader:
1. Create invisible Troika Text in main scene (opacity 0)
2. Create visible Troika Text clone in separate `sdfTextScene`
3. Render `sdfTextScene` to `WebGLRenderTarget(2048, 512)` with ortho camera
4. Sample that RT texture in the glass refraction shader

**Key insight**: Troika's `outlineWidth` + `outlineBlur` produce a soft glow around SDF text that looks natural through glass refraction. Set `outlineWidth: 0.012, outlineBlur: 0.02` for subtle glow without smearing.

**Import path**: `import { Text } from 'troika-three-text'` via `https://unpkg.com/troika-three-text@0.49.1/dist/troika-three-text.esm.js`

**Gotcha**: Must call `.sync()` after setting properties. Text won't render until sync completes.

### 2. Ward Anisotropic BRDF Implementation

Full Ward BRDF in GLSL:
```
f_s = (1 / (4*PI*ax*ay * sqrt(NdotL*NdotV))) * exp(-2 * ((HdotT/ax)^2 + (HdotB/ay)^2) / (1 + HdotN))
```

For brushed-glass hex edges:
- `ax = 0.04` (tight along tangent) produces visible directional streaks
- `ay = 0.35` (wide perpendicular) gives natural falloff
- Edge detection via `abs(position.z)` in extrude geometry (z = depth direction after extrude)
- Overlay on existing transmission material at 1.005x scale avoids z-fight cleanly
- Two lights evaluated separately and summed for richer multi-directional streaks

**Gotcha**: Tangent computation for extruded geometry needs fallback when normal is parallel to up vector. Use `cross(normal, vec3(0,1,0))` with length check, fallback to `cross(normal, vec3(1,0,0))`.

### 3. Half-Resolution Volumetric Fog

Raymarched at 0.5x resolution with 24 steps:
- 3-octave FBM noise for turbulent density
- Henyey-Greenstein phase function (g=0.3)
- Sphere exclusion: `smoothstep(0.0, 0.3, sphereDist)` prevents fog penetrating glass
- Front-to-back compositing with early exit at alpha > 0.95
- Composited via additive blend: `scene.rgb + fog.rgb * fog.a`

**Performance**: 75% fewer fragments vs full-res. Linear filter on RT provides acceptable upscale quality. No visible boundary artifacts.

**Gotcha**: Must reconstruct ray direction from UV using inverse projection + inverse view matrix. Pass both as uniforms every frame.

### 4. Temporal Reprojection for Caustic Anti-Aliasing

Ping-pong RT pair (A and B) at 0.75x resolution:
- Current frame: evaluate Voronoi caustic pattern fresh
- Previous frame: sample from opposite ping-pong buffer using screen-space UV
- Blend: `mix(currentFrame, prevFrame, 0.78)` -- 78% history, 22% current
- Clamp output to 3.0 to prevent runaway brightness accumulation

**Key insight**: Screen-space UV lookup (gl_FragCoord.xy / resolution) works for static camera. For moving camera would need proper motion vectors, but our camera is fixed so this is sufficient.

**Visual result**: Dramatically reduces caustic shimmer. Voronoi patterns appear photographed with ~1/4s exposure instead of instant.

## Performance Notes

- 5 render targets per frame: SDF text RT, occlusion RT, depth RT, volumetric RT, caustic ping-pong
- Half-res volumetric saves ~2ms per frame vs full-res
- Temporal caustic blend adds negligible cost (single texture sample per fragment)
- Ward BRDF evaluation: 2 lights x 1 shader = ~0.5ms on mid-range GPU
- Estimated 42-48fps on test config (similar to Night 38 despite added techniques, thanks to half-res optimization)

## Score Progression
- Night 35: 90.8%
- Night 36: 92.4%
- Night 37: 93.1%
- Night 38: 93.8%
- **Night 39: 94.5% (+0.7 points)**

## Remaining Path to 95%
- Stochastic SSR on floor plane (caustics reflecting off sphere)
- Micro-displacement on hex edges (physically worn glass)
- Motion vector temporal AA (proper velocity buffer reprojection)

## Files
- Three.js scene: `exports/gleb-training/night-39/night39-troika-sdf-ward-brdf-temporal-caustics.html`
- FLUX images: `exports/gleb-training/night-39/image{1,2}-*.png`
- Report: `exports/portal-files/gleb-training-night39-report.md`
