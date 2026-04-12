# Gleb Night 8: Liquid Metal + Glass Morphism

**Date**: 2026-03-29
**Type**: technique + teaching
**Tags**: three-js, liquid-metal, glass-morphism, chrome-pbr, gleb-training, hex-sdf

## Context

Night 8 of ongoing Gleb training. NEW MATERIAL BRANCH: liquid metal (chrome PBR). Previous 7 sessions focused on glass transmission. This session establishes liquid metal as a parallel capability.

## Key Techniques -- Liquid Metal PBR

### Chrome F0 Values (MEMORIZE)
```glsl
vec3 F0_chrome = vec3(0.78, 0.76, 0.82);  // Chrome/platinum
vec3 F0_gold   = vec3(1.00, 0.76, 0.33);  // Gold
vec3 F0_copper = vec3(0.95, 0.64, 0.54);  // Copper
```
These are physically-based. Metal = high F0 + very low roughness (0.03-0.06).

### GGX Cook-Torrance Stack
Three functions needed: `ggxDistribution(NdotH, roughness)`, `geometrySmith(NdotV, NdotL, roughness)`, `fresnelSchlick(cosTheta, F0)`. Combine as `(D * G * F) / (4 * NdotV * NdotL + 0.001)`.

### Analytical Normals from FBM Displacement
When displacing vertices with noise, MUST compute new normals:
```glsl
float eps = 0.05;
float dX = fbm(posX) - displacement;
float dZ = fbm(posZ) - displacement;
vec3 tangent = normalize(vec3(eps, dX, 0.0));
vec3 bitangent = normalize(vec3(0.0, dZ, eps));
vec3 N = normalize(cross(bitangent, tangent));
```
Two extra FBM evals per vertex. Non-negotiable for correct lighting.

### Emissive Streaks (Not Colored Metal)
Energy veins must be ADDITIVE to final color, not multiplied into base:
```glsl
vec3 color = baseColor + metalReflection + pbrResult + streakEmission;
// NOT: vec3 color = mix(baseColor, streakColor, streakMask);
```
Additive = glows through metal. Multiplicative = looks painted on.

## CSS Glass Over WebGL Pattern
`backdrop-filter: blur(20px) saturate(140%)` on CSS panels genuinely blurs the WebGL canvas behind them. This creates real glassmorphism over 3D without Three.js tricks:
- CSS does the frosted glass effect
- Three.js renders the dynamic 3D
- `::before` for specular gradient highlight
- `::after` for chromatic edge line

## Score: 87% (Liquid Metal Specific)

Lower than Night 7 (92% glass) because liquid metal is a newer capability branch. For first dedicated session, 87% is strong.

### Combined Capability:
- Glass/transmission: 92%
- Liquid metal/chrome: 87%
- GLSL shaders: 88%
- Scene composition: 90%

## Gaps for Future Sessions

1. Screen-space reflections (SSR) -- self-reflections on curved metal
2. Raymarched SDF liquid (smooth minimum merging)
3. Anisotropic GGX (flow-direction specular stretching)
4. Thick glass cards (BoxGeometry, not Plane)
5. Depth of field (still missing from entire pipeline)

## Files

- `/home/jared/exports/portal-files/gleb-training-march29.html`
- `/home/jared/exports/portal-files/3d-training-notes-march29.md`
