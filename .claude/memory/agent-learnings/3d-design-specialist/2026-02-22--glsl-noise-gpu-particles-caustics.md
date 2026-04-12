# Day 8: Custom GLSL - Noise Deformation, GPU Particles, Caustics

**Date**: 2026-02-22
**Type**: technique
**Confidence**: high
**Tags**: three-js, glsl, shader-material, gpu-particles, caustics, noise, fBm

---

## Context

Post-sprint advanced techniques session. 7-day sprint mastered glass materials and postprocessing. Day 8 goes below material abstraction into raw GLSL ShaderMaterial, vertex deformation, and GPU particle architecture.

---

## Technique 1: Simplex fBm Vertex Deformation

### Configuration That Works

```glsl
// Vertex shader - 5-octave fBm deformation
vec3 noiseCoord = pos * 1.2 + vec3(uTime * 0.18);
float noiseVal  = fbm(noiseCoord);
vec3 displaced  = pos + normal * noiseVal * 0.28;

// CRITICAL: recompute normals with finite differences
float eps = 0.01;
float nx = fbm((pos + vec3(eps,0,0)) * 1.2 + timeOffset);
float ny = fbm((pos + vec3(0,eps,0)) * 1.2 + timeOffset);
float nz = fbm((pos + vec3(0,0,eps)) * 1.2 + timeOffset);
vec3 grad = vec3(nx, ny, nz) - noiseVal;
vec3 displacedNormal = normalize(normal - grad * uDeformStrength);
```

### Why Finite-Difference Normals Are Required

Displacing vertices without updating normals = lighting breaks (normals point in wrong direction relative to deformed surface). Finite differences recompute the gradient of the noise field and use it to adjust the normal direction.

### GLSL Loop Bounds Must Be Compile-Time Constants

```glsl
// CORRECT - compile-time constant
for (int i = 0; i < 5; i++) { ... }

// WRONG - undefined behavior on mobile drivers
uniform int uOctaves;
for (int i = 0; i < uOctaves; i++) { ... }
```

### Geometry Resolution for Noise Deformation

- Need high vertex density for smooth deformation
- `new THREE.SphereGeometry(1.4, 192, 96)` = 18,432 vertices = looks smooth
- Low poly (32x16 = 512 vertices) shows facets in noise peaks

---

## Technique 2: GPU Particle System Architecture

### Key Insight: Zero CPU-GPU Transfer Per Frame

All particle positions computed in vertex shader from deterministic math:
- Orbit parameters stored as BufferAttributes (uploaded ONCE)
- Vertex shader: `angle = aOrbitPhase + uTime * aOrbitSpeed` → compute xyz
- Result: 50K particles at 60fps with near-zero CPU overhead

### Required Attributes

```javascript
geom.setAttribute('aOrbitRadius', new THREE.BufferAttribute(radii, 1));
geom.setAttribute('aOrbitSpeed',  new THREE.BufferAttribute(speeds, 1));
geom.setAttribute('aOrbitPhase',  new THREE.BufferAttribute(phases, 1));
geom.setAttribute('aLifeOffset',  new THREE.BufferAttribute(lifeOffsets, 1));
geom.setAttribute('aSize',        new THREE.BufferAttribute(sizes, 1));
geom.setAttribute('aColor',       new THREE.BufferAttribute(colors, 3));
```

### Additive Blending + Depth Write

```javascript
blending:   THREE.AdditiveBlending,
depthWrite: false,  // REQUIRED - depth writes with additive = incorrect occlusion
depthTest:  true    // Keep depth testing (particles still sort against scene)
```

### Circular Points (Discard Corners)

```glsl
// Fragment shader
vec2 uv = gl_PointCoord - 0.5;
if (length(uv) > 0.5) discard;
```

### gl_PointSize Distance Correction

```glsl
vec4 mvPos = modelViewMatrix * vec4(orbitPos, 1.0);
gl_PointSize = aSize * (250.0 / -mvPos.z);  // divide by depth for consistent size
```

### 50K Particles Sweet Spot

- < 20K: Looks sparse at wide orbital radii
- 50K: Dense enough for nebula/energy field aesthetic
- > 100K: Diminishing returns in WebGL; needs WebGPU GPGPU for real-time simulation

---

## Technique 3: Caustics Simulation (Voronoi Noise)

### The Technique

Animated Voronoi cellular noise on ground plane = convincing caustic light patterns.

```glsl
float voronoi(vec2 p) {
  vec2 i = floor(p);
  vec2 f = fract(p);
  float minDist = 10.0;
  for (int y = -1; y <= 1; y++) {
    for (int x = -1; x <= 1; x++) {
      vec2 seed = i + vec2(float(x), float(y));
      // Animate cell centers with time
      float a = sin(dot(seed, vec2(127.1, 311.7)) + uTime * 0.4) * 0.5 + 0.5;
      float b = sin(dot(seed, vec2(269.5, 183.3)) + uTime * 0.3) * 0.5 + 0.5;
      vec2 point = vec2(float(x), float(y)) + vec2(a, b) * 0.7;
      minDist = min(minDist, length(point - f));
    }
  }
  return minDist;
}

// Usage: edge of cells = bright caustic lines
float causticMask = pow(1.0 - voronoi(uv), 2.5);
```

### Chromatic Caustics (Cheap)

```glsl
// Offset UV slightly per channel = color fringing like real refraction
float causticsB = pow(1.0 - voronoi(uv + 0.04), 2.5);
float causticsO = pow(1.0 - voronoi(uv - 0.04), 2.5);
vec3 causticColor = vec3(causticsO, causticMask, causticsB);  // R=orange, G=base, B=blue
```

### Falloff Cone

```glsl
float coneFalloff = 1.0 - smoothstep(0.8, 2.5, distFromGlass);
causticMask *= coneFalloff;
```

---

## Technique 4: Custom ShaderPass

```javascript
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';

const MyShader = {
  uniforms: {
    tDiffuse: { value: null },  // MUST be named tDiffuse
    uTime:    { value: 0.0 }
  },
  vertexShader:   `varying vec2 vUv; void main() { vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
  fragmentShader: `uniform sampler2D tDiffuse; varying vec2 vUv; void main() { ... }`
};

const pass = new ShaderPass(MyShader);
composer.addPass(pass);

// Per-frame update
pass.uniforms.uTime.value = elapsed;
```

### OutputPass Must Be Last

```javascript
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
composer.addPass(new OutputPass());  // ALWAYS last
```

Without OutputPass in r0.161.0: colors appear washed out / wrong gamma.

---

## Technique 5: Manual PBR in ShaderMaterial

When using ShaderMaterial (no built-in lighting), implement GGX specular manually:

```glsl
vec3 calcLight(vec3 N, vec3 L, vec3 V, vec3 lightCol, float roughness) {
  float NdotL = max(dot(N, L), 0.0);
  vec3 H = normalize(L + V);
  float NdotH = max(dot(N, H), 0.0);
  float alpha = roughness * roughness;
  float denom = NdotH * NdotH * (alpha * alpha - 1.0) + 1.0;
  float D = (alpha * alpha) / (3.14159 * denom * denom);
  vec3 spec = goldSpec * D * 0.35;
  return lightCol * NdotL * 0.7 + spec;
}

// Fresnel rim
float fresnel = pow(1.0 - max(dot(N, V), 0.0), 3.0);
```

---

## Performance Notes

- 50K particles + ShaderMaterial: 60fps on mid-range dedicated GPU
- Voronoi caustics: fragment-heavy, scales with screen resolution
- 192x96 sphere + 5-octave fBm per vertex: 60fps (GLSL math is fast)
- Finite-difference normal recompute adds ~3x vertex shader cost but still 60fps

---

## Reference Files

- Demo: `/home/jared/projects/AI-CIV/aether/exports/3d-interactive-gleb-day8.html`
- Report: `/home/jared/projects/AI-CIV/aether/exports/3d-mastery-day8-report.md`
- Prior ESM pattern: `/home/jared/projects/AI-CIV/aether/.claude/memory/agent-learnings/3d-design-specialist/2026-02-22--threejs-r148-esm-migration-critical.md`
