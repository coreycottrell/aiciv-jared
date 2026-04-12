# Liquid Metal Hex Shader — Investors Page v4

**Date**: 2026-03-17
**Type**: technique
**Agent**: 3d-design-specialist
**Topic**: Replacing FBM vein shader with SDF hexagonal grid + PBR liquid metal

---

## Context

Upgraded the background shader on `/investors-ask-aether-v4/index.html` from abstract FBM lava-vein look to proper liquid metal + hexagonal honeycomb grid aesthetic (reference: iStock "Futuristic Information Technology Glowing Hexagon Grid").

Target: dark liquid metal surface with glowing orange hex grid embossed into it, like obsidian mercury with luminous honeycomb veins.

## Key Techniques

### 1. Hex Grid SDF

Used a pointy-top hex grid via paired modular grids:
```glsl
vec2 hexSDF(vec2 p, float scale){
  p*=scale;
  const float sq3=1.7320508;
  vec2 r=vec2(1.0,sq3);
  vec2 h=r*0.5;
  vec2 a=mod(p,r)-h;
  vec2 b=mod(p-h,r)-h;
  vec2 gv=(dot(a,a)<dot(b,b))?a:b;
  gv=abs(gv);
  float d=max(gv.x+gv.y*0.57735,gv.x*2.0*0.57735)-0.5;
  // ...
}
```
Returns signed distance: negative inside cell, 0 at edge, positive outside.
The `smoothstep(-0.055,0.0,edgeDist)` gives clean thin glowing lines.

### 2. Per-Cell Independent Pulsing

Each cell gets a unique ID from `hash2(floor(cellP))`. Then:
```glsl
float hexPulse(float id, float t){
  float phase=id*6.2831;
  float speed=0.3+id*0.4;
  return 0.5+0.5*sin(t*speed+phase);
}
```
Creates organic, non-uniform breathing across the grid.

### 3. Traveling Wave for Drama

A diagonal sweep wave adds motion:
```glsl
float waveAngle=uTime*0.18;
float wavePos=flatPos.x*cos(waveAngle)+flatPos.z*sin(waveAngle);
float wave=smoothstep(-0.8,0.0,sin(wavePos*0.45-uTime*0.6))*0.5+0.5;
```

### 4. Embossed Normal Perturbation

SDF gradient gives approximate hex edge normals:
```glsl
float dX=(hexSDF(p+vec2(eps,0)).x - hexSDF(p-vec2(eps,0)).x)/(2.0*eps);
float dZ=(hexSDF(p+vec2(0,eps)).x - hexSDF(p-vec2(0,eps)).x)/(2.0*eps);
float blend=smoothstep(0.12,-0.0,abs(edgeDist))*0.55;
N=normalize(mix(N, normalize(vec3(-dX*blend,1.0,-dZ*blend)), 0.65));
```
This makes the hex edges look raised/embossed into the liquid surface.

### 5. PBR Liquid Metal Specular

Three-light GGX setup:
- Key light: cold white from upper-right — dominant chrome specular
- Fill: warm left fill — subtle secondary highlight
- Rim: dark orange from below — catches hex edge geometry

F0 for chrome/platinum: `vec3(0.78,0.76,0.82)` — gives realistic metallic appearance.

Roughness: 0.045 base (mirror-like) + micro-variation from FBM + slightly rougher in cell centers.

### 6. Scroll Reactivity

`uScroll` uniform passes scroll progress 0-1 to increase hex glow intensity as user scrolls. Subtle but adds interactivity feel.

## Performance Notes

- Mobile: 80 subdivisions, Desktop: 200 subdivisions (same as before)
- hexSDF called 5x per fragment (1 main + 2 secondary + 2 for normal gradient) — runs fine at 60fps on mid-range desktop
- Bloom pass: strength 0.55, radius 0.38, threshold 0.72 — captures orange hex glow without overblowing

## Color Values

- Hex edge: `mix(vec3(1.0,0.38,0.0), vec3(1.0,0.62,0.0), wave)` — deep orange to amber
- Node intersections: `vec3(1.0,0.85,0.5)` — white-hot
- Base metal: `vec3(0.008,0.007,0.012)` — near-black gunmetal

## Gotchas

1. **GLSL `const` in function scope**: GLSL ES doesn't allow `const float sq3` inside functions in some drivers — use bare `float` or define outside.
2. **SDF gradient for normals**: Works only if hexScale is consistent between gradient samples and main call.
3. **hex cell ID**: `floor(cellP*10.0+0.5)` — the multiplier affects cell grouping. Adjust for correct cell-unique IDs.
4. **FBM kept in vertex shader**: The liquid surface displacement (FBM-based undulation) is kept — only the fragment shader changed. This preserves the viscous mercury feel.

## Files Modified

- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/investors-ask-aether-v4/index.html`
  - Replaced `NOISE_GLSL` constant with extended version including `hexSDF`, `hexPulse`, `hexEdge`, `hash2`
  - Replaced `metalFS` entirely with PBR hex shader
  - Added `uScroll` uniform to `metalU`
  - Updated bloom pass parameters

## Deployed

- URL: `https://purebrain.ai/investors-ask-aether-v4/`
- HTTP 200 verified
- CF Pages deployment: `purebrain-staging`
