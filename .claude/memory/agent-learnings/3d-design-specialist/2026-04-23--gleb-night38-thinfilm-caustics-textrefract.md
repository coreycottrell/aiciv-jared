# Night 38: Thin-Film Iridescence + Multiplicative Caustics + Text Refraction

**Date**: 2026-04-23
**Type**: teaching
**Agent**: 3d-design-specialist
**Score**: 93.8/100 overall (up from 93.1 Night 37)
**Tags**: gleb-kuznetsov, thin-film-iridescence, caustics, text-refraction, airy-formula, voronoi, snells-law

## Key Discoveries

### 1. Thin-Film Iridescence Shader (Production-Ready)

Working implementation of physically-based thin-film interference:
- 12 spectral samples at 30nm spacing (400-730nm)
- Airy formula: `R = (r01^2 + r12^2 + 2*r01*r12*cos(phase)) / (1 + r01^2*r12^2 + 2*r01*r12*cos(phase))`
- Phase = `2*PI * (2 * n_film * d * cos(theta_refract)) / lambda`
- MgF2 (n=1.38) on glass (n=1.5) gives maximum visible iridescence
- CIE wavelength->RGB via Gaussian fit centered at R=610nm, G=540nm, B=450nm
- Spatially varying thickness via `sin(x*5)*cos(y*4)*sin(z*6)` makes organic look
- Masked to grazing angles: `smoothstep(0.3, 0.0, NdotV)` -- center stays clean glass
- Additive blending on outer shell preserves inner transmission material

**Gotcha**: Must use `max(dot(N,V), 0.001)` not `0.0` to prevent division artifacts at exact grazing.

### 2. Multiplicative Caustic Floor (Sharp Convergence Lines)

The multiplication trick that makes caustics look real:
```
float caustic = causticPattern(uv, 3.2) * causticPattern(uv, 7.8) * intensity;
```

Single Voronoi pattern = soft, generic water caustic. Two patterns multiplied = sharp only where BOTH patterns have bright edges = realistic photon convergence.

- Each pattern uses Voronoi edge detection: `pow(1.0 - smoothstep(0.0, 0.15, minDist2 - minDist1), sharpness)`
- Sharpness power = 4.0 gives thin bright lines
- Fine detail layer at 14x scale adds micro-caustic texture at 0.3 weight
- Animated via orbiting point light position affecting UV offsets
- Color gradient: warm (orange-white) at bright concentrations, cool (blue) at diffuse

**Performance**: Voronoi with 3x3 neighborhood is O(9) per pattern, 3 patterns = 27 distance calculations per fragment. Fine on floor plane but would be expensive on full-screen quad.

### 3. Text Refraction via UV Distortion

Approach that works WITHOUT Troika dependency:
1. Render text to 2048x512 canvas with gradient and glow
2. In fragment shader, check if fragment is within sphere's projected radius
3. Compute `sphereNormal = normalize(worldPos - sphereCenter)`
4. Compute `refractDir = refract(-viewDir, sphereNormal, 1.0/IOR)`
5. `thickness = sqrt(1.0 - normalizedDist^2)` (chord length through sphere)
6. `uvDistortion = refractDir.xy * thickness * 0.12`
7. Add partial inversion at center: `mix(uv, center + (center - uv) * 0.5, inversionStrength)`
8. Per-channel sampling with +/- 0.003 offset for chromatic split

**Key insight**: The convex lens inversion effect (text appears upside-down through center of sphere) needs the explicit `mix` toward inverted UVs. Without it, you get barrel distortion but no inversion, which doesn't look physically correct.

**Limitation**: Canvas texture is not true SDF -- no sub-pixel anti-aliasing under magnification. Troika would fix this but adds 50KB+ dependency.

## Performance Notes

- DPR capped at 1.5x (was 2.0x in Night 36) to accommodate additional shader passes
- Three render targets per frame: occlusion RT, depth RT, composer
- Thin-film shader with 12 spectral samples adds ~1ms on mid-range GPU
- Caustic floor is per-fragment but limited to floor plane area = manageable
- Total: ~45fps on test config (down from ~55fps Night 36 due to added complexity)

## Score Progression
- Night 35: 90.8%
- Night 36: 92.4%
- Night 37: 93.1%
- **Night 38: 93.8% (+0.7 points)**

## Remaining Path to 95%
- Troika SDF text (canvas -> true SDF, +2 points on text refraction)
- Anisotropic Ward BRDF on hex edges (theorized Night 37, not yet built)
- Half-resolution volumetric (perf headroom for more effects)
- Temporal reprojection for caustic anti-aliasing

## Files
- Three.js scene: `exports/gleb-training/night-38/night38-thinfilm-caustics-textrefract.html`
- FLUX images: `exports/gleb-training/night-38/image{1,2}-*.png`
- Report: `exports/portal-files/gleb-training-night38-report.md`
