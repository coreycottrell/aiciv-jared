# Liquid Metal Study — Aether 3D Training

**Date**: 2026-03-22
**Series**: Gleb Kuznetsov–Level 3D Aesthetic Training
**Stack**: Three.js / WebGL / React Three Fiber (R3F) + Drei
**Purpose**: Learn liquid metal visual effects for use on purebrain.ai investor pages, hero sections, and product showcases

---

## Table of Contents

1. [What Is Liquid Metal Visually](#1-what-is-liquid-metal-visually)
2. [Pixabay Reference Library](#2-pixabay-reference-library)
3. [The Physics Behind the Look](#3-the-physics-behind-the-look)
4. [Implementation Approaches](#4-implementation-approaches)
5. [Approach A: MeshPhysicalMaterial (Fastest — PBR)](#approach-a-meshphysicalmaterial-fastest--pbr)
6. [Approach B: MatCap Shader (Most Controllable)](#approach-b-matcap-shader-most-controllable)
7. [Approach C: Custom GLSL Vertex + Fragment Shader (Most Powerful)](#approach-c-custom-glsl-vertex--fragment-shader-most-powerful)
8. [Approach D: Fluid Simulation (Navier-Stokes)](#approach-d-fluid-simulation-navier-stokes)
9. [Environment Maps — The Secret Weapon](#9-environment-maps--the-secret-weapon)
10. [Animate It — Making Metal Flow](#10-animate-it--making-metal-flow)
11. [React Three Fiber Implementation](#11-react-three-fiber-implementation)
12. [MetalFlow Reference Analysis](#12-metalflow-reference-analysis)
13. [Connection to Gleb Aesthetic](#13-connection-to-gleb-aesthetic)
14. [Production Checklist](#14-production-checklist)
15. [Further Study](#15-further-study)

---

## 1. What Is Liquid Metal Visually

Liquid metal is one of the most visually complex materials in CG because it combines four simultaneous phenomena:

### 1a. Perfect Specular Reflection (Mirror-Like)
- Metalness = 1.0 means all light reflects rather than scatters
- Roughness near 0 means that reflection is sharp, not blurry
- The surface reads as a mirror that has color — not a painted surface

### 1b. Viscous Flow Dynamics
- Surface undulates with slow, heavy movement — not water-fast ripples
- Blob forms maintain surface tension (edges pull inward)
- When two blobs merge they don't splash — they slowly coalesce
- The silhouette morphs continuously but coherently

### 1c. Chromatic Shifts at Edges (Fresnel + Iridescence)
- At grazing angles, metallic surfaces show iridescent color
- Mercury shifts from silver to dark blue at edges
- Chrome picks up cyan, purple, gold depending on environment
- This is Fresnel: at 0° you see through, at 90° you see total reflection

### 1d. Environment Dependency
- Liquid metal has no "own color" — it reflects its surroundings
- The same metal sphere looks completely different in a studio vs. outdoors
- Professional liquid metal renders use HDR environment maps (high dynamic range)
- The reflection stretches, distorts, and wraps around surface curvature

### Summary: What You Must Get Right

| Property | Correct Value | Wrong Value |
|----------|--------------|-------------|
| Metalness | 0.95 – 1.0 | 0.5 (makes it look plastic) |
| Roughness | 0.0 – 0.15 | 0.8 (too matte, kills it) |
| Environment Map | HDR, high contrast | Flat color light |
| Animation | Slow, viscous, surface tension | Fast/jittery (looks wrong) |
| Iridescence | Subtle at edges | None (too flat) |
| Clearcoat | 0.8–1.0 | 0 (loses that wet sheen) |

---

## 2. Pixabay Reference Library

Pixabay has **2,023+ free liquid metal video clips** — all royalty-free, no attribution required, available in 4K and HD. URL: https://pixabay.com/videos/search/liquid%20metal/

### Key Video Categories to Study

**Category 1: Chrome/Mercury Blobs**
- Tags: metal, liquid, chrome, mercury, fluid, blob, morph
- Visual: Single silver sphere deforming, stretching, splitting
- What to learn: Blob morphing, surface tension simulation, reflection mapping
- Search: https://pixabay.com/videos/search/liquid%20metal/

**Category 2: Liquid Gold/Bronze**
- Tags: gold, liquid, molten, pour, flow
- Visual: Warm amber metallic fluid pouring, pooling
- What to learn: Warm metalness values, viscosity animation, caustics
- Search: https://pixabay.com/videos/search/gold%20liquid/

**Category 3: Holographic/Iridescent Metal**
- Tags: holographic, iridescent, chrome, gradient, liquid
- Visual: Rainbow-shifting metal surfaces, oil-slick color transitions
- What to learn: Iridescence implementation, thin-film interference simulation
- Search: https://pixabay.com/videos/search/metal%20liquid/

**Category 4: Metal Flow Backgrounds**
- Tags: metal, wave, background, abstract, flowing
- Visual: Wavy metal surface rippling like slow water
- What to learn: Displacement maps, wave functions on flat planes, looping animations

### Recommended Specific Video to Analyze

**Video ID 66980** — "Metal, Liquid, Chrome, Gold"
URL: https://pixabay.com/videos/metal-liquid-chrome-gold-66980/
This is one of the top results for chrome + liquid and is a strong reference for:
- Perfect mirror-surface quality
- How reflections distort on curved fluid geometry
- The dark void background that makes chrome pop (matches our #080a12 brand)

### Visual Reference Notes From Study

When studying Pixabay liquid metal videos, note these specific characteristics:

1. **The dark halo** — liquid metal always has a darker shadow at its thinnest points where light passes through edge rather than reflecting directly
2. **No true black** — even in shadow, liquid metal shows subtle environment color reflection
3. **Silhouette highlight** — a rim light effect appears at the silhouette edge, created by the Fresnel effect
4. **Blob merge moment** — when two metal blobs touch, there's a moment of contact highlight that's brighter than either blob alone (caustic concentration)
5. **Drip tail** — liquid metal drips form elongated tails that thin to a fine point before separating

---

## 3. The Physics Behind the Look

Understanding the physics lets you fake it convincingly.

### Fresnel Effect
When light hits a surface at a shallow (grazing) angle, more of it reflects. At steep angles (straight-on), some transmits into the material.

For metals: at 0° incidence, reflectance is still high (metals don't transmit). At 90° (grazing), it's total reflection.

```glsl
// Fresnel approximation in GLSL (Schlick's)
float fresnel(vec3 viewDir, vec3 normal, float F0) {
  float cosTheta = max(dot(normalize(viewDir), normalize(normal)), 0.0);
  return F0 + (1.0 - F0) * pow(1.0 - cosTheta, 5.0);
}
```

### Iridescence (Thin-Film Interference)
When a very thin transparent film sits on the metal surface (like an oxide layer), light reflecting from the top and bottom of the film interferes with itself. The interference depends on film thickness and viewing angle — producing rainbow colors.

Three.js `MeshPhysicalMaterial` now has native `iridescence` support that simulates this.

### Environment Reflection
The environment map is projected onto the sphere using the reflection vector:
```glsl
vec3 reflectedDir = reflect(-viewDir, normal);
vec4 envColor = textureCube(envMap, reflectedDir);
```
For animated liquid metal, this reflection naturally updates as the surface normal changes with the fluid animation.

### Surface Tension (Visual Simulation)
True SPH (Smoothed Particle Hydrodynamics) is too expensive for real-time web. We fake it with:
- Metaball/SDF (Signed Distance Field) blending for blob merging
- Simplex noise displacement on a high-poly mesh
- Slow sinusoidal oscillation of blob vertices with damping

---

## 4. Implementation Approaches

Four approaches ranked by complexity and visual quality:

| Approach | Complexity | Visual Quality | Performance | Best For |
|----------|-----------|---------------|------------|----------|
| A. MeshPhysicalMaterial | Low | High | Excellent | Product showcases, hero orbs |
| B. MatCap Shader | Low | Very High | Excellent | Consistent look without HDRI |
| C. Custom GLSL | High | Maximum | Good | Signature effects, interactive |
| D. Fluid Simulation | Very High | Cinematic | Poor mobile | Hero showcases only |

---

## Approach A: MeshPhysicalMaterial (Fastest — PBR)

The fastest path to convincing liquid metal. Three.js's PBR material with the right settings.

### Core Material Setup

```javascript
import * as THREE from 'three';
import { RGBELoader } from 'three/examples/jsm/loaders/RGBELoader.js';

// Load HDR environment (CRITICAL for liquid metal)
const rgbeLoader = new RGBELoader();
const envTexture = await rgbeLoader.loadAsync('./hdri/studio-chrome.hdr');
envTexture.mapping = THREE.EquirectangularReflectionMapping;

scene.environment = envTexture;
scene.background = new THREE.Color(0x080a12); // Our brand dark bg

// The liquid metal material
const liquidMetalMaterial = new THREE.MeshPhysicalMaterial({
  color: 0xffffff,           // White base — the env map provides color
  metalness: 1.0,            // Full metal — no diffuse scattering
  roughness: 0.05,           // Near-mirror smooth surface
  envMapIntensity: 2.0,      // Boost reflections (key for drama)

  // Clearcoat — adds the wet lacquer layer over the metal
  clearcoat: 1.0,
  clearcoatRoughness: 0.05,

  // Iridescence — thin-film color shifting at edges
  iridescence: 0.8,
  iridescenceIOR: 1.8,
  iridescenceThicknessRange: [100, 800],  // Nanometers — wider = more color
});

// High-poly sphere (more faces = smoother reflections)
const geometry = new THREE.SphereGeometry(1, 128, 128);
const mesh = new THREE.Mesh(geometry, liquidMetalMaterial);
scene.add(mesh);
```

### Animating the Blob Shape

```javascript
// Animate with vertex displacement via morph targets OR shader injection
// Simple approach: animate roughness to create "breathing" effect
function animate(time) {
  // Subtle roughness breathing — makes it feel alive
  liquidMetalMaterial.roughness = 0.03 + Math.sin(time * 0.5) * 0.02;

  // Rotate slowly — reflections shift and reveal environment
  mesh.rotation.y += 0.003;
  mesh.rotation.x = Math.sin(time * 0.2) * 0.1;

  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}
```

### PBR Material Quick Reference

```javascript
// CHROME MIRROR
{ metalness: 1.0, roughness: 0.0, clearcoat: 1.0, iridescence: 0.0 }

// LIQUID MERCURY
{ metalness: 1.0, roughness: 0.05, clearcoat: 0.8, iridescence: 0.3, color: 0xc0c0c0 }

// MOLTEN GOLD
{ metalness: 0.9, roughness: 0.1, clearcoat: 0.5, color: 0xd4a017 }

// HOLOGRAPHIC LIQUID METAL
{ metalness: 0.95, roughness: 0.08, clearcoat: 1.0, iridescence: 1.0, iridescenceIOR: 2.0, iridescenceThicknessRange: [200, 1000] }
```

---

## Approach B: MatCap Shader (Most Controllable)

MatCap (Material Capture) uses a pre-baked sphere photograph as a view-space texture. It requires no environment map, no lighting setup — it just works everywhere and looks the same everywhere.

### Why MatCap Works for Liquid Metal

- The matcap image IS the lighting — it's a photograph of a chrome sphere in a real environment
- View-space mapping means it doesn't depend on geometry rotation — only normal direction
- Instant, cheap, consistent — perfect for animated blobs

### Three.js MatCap Setup

```javascript
const textureLoader = new THREE.TextureLoader();
const matcap = textureLoader.load('./matcaps/chrome-studio.png');

const material = new THREE.MeshMatcapMaterial({
  matcap: matcap,
  // Optional: add slight color tint
  color: new THREE.Color(0.9, 0.9, 1.0), // Slight blue-chrome
});
```

### R3F + Drei MatCap

```jsx
import { useMatcapTexture } from '@react-three/drei';

function LiquidMetalSphere() {
  // Drei's useMatcapTexture hooks into the emmelleppi/matcaps repository
  // Chrome matcaps to try: '3E2335_D36A1B_8E4A2E_2842A5' or '2E763A_78A0B7_B3D1CF_14F209'
  const [matcap] = useMatcapTexture('3D3C3C_999999_7B7171_898282', 1024);

  return (
    <mesh>
      <sphereGeometry args={[1, 128, 128]} />
      <meshMatcapMaterial matcap={matcap} />
    </mesh>
  );
}
```

### Free Chrome MatCap Sources

- **nidorx/matcaps** (GitHub): https://github.com/nidorx/matcaps — massive free library
- **emmelleppi/matcaps**: Used by Drei's `useMatcapTexture` hook automatically
- **Three.js examples**: https://threejs.org/examples/webgl_materials_matcap.html — drag/drop your own

### Best Chrome MatCap Hashes for Drei

```
// Pure chrome mirror:     '3D3C3C_999999_7B7171_898282'
// Blue chrome:            '3E2335_D36A1B_8E4A2E_2842A5'
// Gold chrome:            'C7C7D7_4C4E5A_818393_70738E'
// Iridescent oil slick:   '2E763A_78A0B7_B3D1CF_14F209'
```

---

## Approach C: Custom GLSL Vertex + Fragment Shader (Most Powerful)

This is where you get full control — morphing geometry, custom lighting, procedural pattern generation.

### The Liquid Metal Vertex Shader

Displaces sphere vertices using multiple layered simplex noise octaves to create organic fluid shape.

```glsl
// vertex.glsl
uniform float u_time;
uniform float u_amplitude;
uniform float u_frequency;
uniform float u_speed;

varying vec3 vNormal;
varying vec3 vPosition;
varying vec3 vWorldPos;

// 3D simplex noise (Stefan Gustavson implementation)
// Include via: https://github.com/ashima/webgl-noise
#include <simplex3d>

void main() {
  vNormal = normal;
  vPosition = position;

  // Multi-octave noise for organic fluid look
  float noise1 = snoise(position * u_frequency + u_time * u_speed * 0.3);
  float noise2 = snoise(position * u_frequency * 2.1 + u_time * u_speed * 0.5) * 0.5;
  float noise3 = snoise(position * u_frequency * 4.3 + u_time * u_speed * 0.7) * 0.25;

  float displacement = (noise1 + noise2 + noise3) * u_amplitude;

  // Displace along normal direction (maintains spherical base)
  vec3 newPosition = position + normal * displacement;

  vWorldPos = (modelMatrix * vec4(newPosition, 1.0)).xyz;
  gl_Position = projectionMatrix * modelViewMatrix * vec4(newPosition, 1.0);
}
```

### The Liquid Metal Fragment Shader

```glsl
// fragment.glsl
uniform samplerCube u_envMap;
uniform sampler2D u_matcap;
uniform float u_time;
uniform float u_iridescence;
uniform vec3 u_cameraPos;

varying vec3 vNormal;
varying vec3 vPosition;
varying vec3 vWorldPos;

// Fresnel approximation
float fresnelSchlick(float cosTheta, float F0) {
  return F0 + (1.0 - F0) * pow(clamp(1.0 - cosTheta, 0.0, 1.0), 5.0);
}

// Iridescence color from angle
vec3 iridescenceColor(float angle) {
  // Cycle through hue based on angle — simulates thin-film interference
  vec3 col;
  float t = angle * 6.283;
  col.r = 0.5 + 0.5 * cos(t + 0.0);
  col.g = 0.5 + 0.5 * cos(t + 2.094); // 120 degrees offset
  col.b = 0.5 + 0.5 * cos(t + 4.189); // 240 degrees offset
  return col;
}

void main() {
  vec3 normal = normalize(vNormal);
  vec3 viewDir = normalize(u_cameraPos - vWorldPos);

  // Reflection vector for environment sampling
  vec3 reflectDir = reflect(-viewDir, normal);

  // Sample environment map
  vec4 envColor = textureCube(u_envMap, reflectDir);

  // Fresnel term
  float cosTheta = dot(viewDir, normal);
  float fresnel = fresnelSchlick(cosTheta, 0.04);

  // Iridescence overlay
  vec3 iridColor = iridescenceColor(fresnel * 2.0 + u_time * 0.1);
  vec3 metalColor = mix(envColor.rgb, iridColor, u_iridescence * fresnel);

  // Rim light — brightens silhouette edge
  float rim = pow(1.0 - max(cosTheta, 0.0), 3.0);
  metalColor += rim * vec3(0.3, 0.4, 0.6); // Blue-tinted rim

  gl_FragColor = vec4(metalColor, 1.0);
}
```

### Three.js ShaderMaterial Wiring

```javascript
const liquidMetalShader = new THREE.ShaderMaterial({
  uniforms: {
    u_time:        { value: 0.0 },
    u_amplitude:   { value: 0.12 },    // How much surface moves
    u_frequency:   { value: 1.8 },     // Noise scale
    u_speed:       { value: 0.4 },     // Animation speed
    u_iridescence: { value: 0.6 },     // Color shifting intensity
    u_envMap:      { value: envTexture },
    u_cameraPos:   { value: camera.position },
  },
  vertexShader: vertexGLSL,
  fragmentShader: fragmentGLSL,
});

// High-poly sphere — 256 segments for smooth displacement
const geometry = new THREE.SphereGeometry(1, 256, 256);

// CRITICAL: Compute normals AFTER displacement for accurate lighting
// This happens in the vertex shader automatically but for lighting to work
// correctly with displacement, you need correct normals at displaced positions

const clock = new THREE.Clock();
function animate() {
  liquidMetalShader.uniforms.u_time.value = clock.getElapsedTime();
  liquidMetalShader.uniforms.u_cameraPos.value.copy(camera.position);
  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}
```

---

## Approach D: Fluid Simulation (Navier-Stokes)

The highest visual fidelity — actual fluid simulation running on GPU. Used for interactive hero sections where user mouse movement disturbs the metal.

### How GPU Fluid Simulation Works

1. Store velocity field in a floating-point render target (texture)
2. Each frame, run advection pass: move velocity along itself
3. Run pressure projection: make fluid incompressible (divergence-free)
4. Optional: add vorticity confinement for spiral detail
5. Render result with metallic material

### Reference Implementations

- **Pavel Dobryakov's WebGL Fluid Sim**: https://paveldogreat.github.io/WebGL-Fluid-Simulation/
  - Source: GitHub `PavelDoGreat/WebGL-Fluid-Simulation`
  - This is the gold standard — add mouse interaction, render with metallic tones

- **GPU Fluid Experiments**: https://haxiomic.github.io/GPU-Fluid-Experiments/html5/

### Simplified Fluid for Production

For web pages, a simplified approach uses a ping-pong render target:

```javascript
// Ping-pong render targets for fluid state
const options = {
  type: THREE.FloatType,
  format: THREE.RGBAFormat,
  minFilter: THREE.LinearFilter,
  magFilter: THREE.LinearFilter
};

let rtA = new THREE.WebGLRenderTarget(512, 512, options);
let rtB = new THREE.WebGLRenderTarget(512, 512, options);

// Each frame: swap targets, simulate step, use result as metallic displacement
function simulationStep() {
  renderer.setRenderTarget(rtB);
  // Run advection + pressure solve shaders here
  renderer.setRenderTarget(null);
  [rtA, rtB] = [rtB, rtA]; // Swap
}
```

**Performance note**: Fluid simulation is GPU-intensive. Run at 256x256 or 512x512 resolution, not full screen. Use requestAnimationFrame throttling on mobile (target 30fps, not 60fps).

---

## 9. Environment Maps — The Secret Weapon

**This is the single most impactful thing you can do for liquid metal quality.**

### Why Environment Maps Are Non-Negotiable

Without an environment map, metalness = 1.0 makes an object go completely black (metal has no diffuse, only specular reflection — with nothing to reflect, it's black).

With a high-contrast HDR environment map, liquid metal comes alive.

### Finding Free HDR Environment Maps

1. **Polyhaven** (best free HDRIs): https://polyhaven.com/hdris
   - Filter by: Studio, Interior
   - Best for liquid metal: `studio_small_08`, `studio_small_09`, `photoStudio_01`
   - All free, CC0 license

2. **Three.js built-in presets** (via Drei Environment component):
   ```jsx
   <Environment preset="studio" />
   // Other presets: sunset, dawn, night, warehouse, forest, apartment, city, park, lobby
   ```

3. **Creating custom environment**: For branded look, render a simple HDR with Blender
   - Dark background + 2-3 bright colored area lights (matches our #080a12 + accent colors)

### Loading HDRI in Three.js

```javascript
import { RGBELoader } from 'three/examples/jsm/loaders/RGBELoader.js';

const loader = new RGBELoader();
loader.load('./hdri/studio-small-08.hdr', (texture) => {
  texture.mapping = THREE.EquirectangularReflectionMapping;
  scene.environment = texture;
  // Do NOT set scene.background — keep our dark #080a12 bg
});
```

### R3F + Drei Environment

```jsx
import { Environment, useEnvironment } from '@react-three/drei';

// Option 1: Built-in preset (easiest)
<Environment preset="studio" />

// Option 2: Custom HDR file
<Environment files="/hdri/studio-small-08.hdr" />

// Option 3: Only affect material reflections, not background
<Environment preset="studio" background={false} />
```

### Designing a Branded Environment

For purebrain.ai's dark aesthetic, a custom environment with:
- Near-black ambient (matches #080a12)
- 1 pure white key light (creates the primary chrome highlight)
- 1 electric blue fill (#0066ff area) (matches brand accent)
- 1 warm white rim (creates separation from dark bg)

This gives chrome the "dark room chrome" look — dramatic, high-contrast, luxurious.

---

## 10. Animate It — Making Metal Flow

### The Three Levels of Animation

**Level 1: Rotation (Simplest)**
```javascript
mesh.rotation.y += 0.003;
```
This alone changes which environment light is reflected — creates the feeling of life.

**Level 2: Vertex Displacement (Intermediate)**
```javascript
// On each frame, displace sphere vertices
const posAttr = geometry.attributes.position;
const time = clock.getElapsedTime();

for (let i = 0; i < posAttr.count; i++) {
  const ox = posAttr.getX(i);
  const oy = posAttr.getY(i);
  const oz = posAttr.getZ(i);

  // Spherical coordinates
  const r = Math.sqrt(ox*ox + oy*oy + oz*oz);
  const theta = Math.atan2(oy, ox);
  const phi = Math.acos(oz / r);

  // Layered sine wave displacement
  const d = 0.08 * (
    Math.sin(3 * phi + time * 0.5) * Math.cos(5 * theta + time * 0.3) +
    Math.sin(5 * phi + time * 0.7) * Math.cos(3 * theta - time * 0.4) * 0.5
  );

  const newR = 1.0 + d;
  posAttr.setXYZ(i, ox/r * newR, oy/r * newR, oz/r * newR);
}

posAttr.needsUpdate = true;
geometry.computeVertexNormals(); // CRITICAL — recompute normals after displacement
```

Note: CPU-side displacement is slow for high-poly meshes. For 64x64 segments this is fine. For 256x256 use GPU vertex shader.

**Level 3: GPU Vertex Shader (Best Performance)**
Use Approach C's vertex shader — displacement happens on GPU, no CPU bottleneck.

### Viscosity / Surface Tension Feel

Real liquid metal moves slowly and deliberately. Achieve this through:

```javascript
// Low frequency, high amplitude = slow, rolling blobs
u_frequency: { value: 1.2 }   // Fewer, larger waves
u_speed:     { value: 0.25 }  // Slow time evolution
u_amplitude: { value: 0.15 }  // Significant displacement

// High frequency, low amplitude = choppy surface (wrong for liquid metal)
// u_frequency: { value: 4.0 }  -- too many wrinkles
// u_speed:     { value: 1.5 }  -- too fast, looks like water not metal
```

### Mouse Interaction

```javascript
// Track mouse position
const mouse = new THREE.Vector2();
window.addEventListener('mousemove', (e) => {
  mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
  mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;
});

// Pass to shader as gravity well that distorts the fluid
liquidMetalShader.uniforms.u_mouse = { value: mouse };
```

In vertex shader:
```glsl
uniform vec2 u_mouse;
// ...
// Add mouse attraction to displacement
float mouseDist = length(position.xy - u_mouse * 1.5);
float mouseInfluence = exp(-mouseDist * 2.0) * 0.15;
displacement += mouseInfluence * sin(u_time * 2.0);
```

---

## 11. React Three Fiber Implementation

### Full R3F Liquid Metal Component

```jsx
import { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Environment, useMatcapTexture } from '@react-three/drei';
import * as THREE from 'three';

// Vertex shader (import as string or use inline template literal)
const vertexShader = `
  uniform float u_time;
  uniform float u_amplitude;
  varying vec3 vNormal;
  varying vec3 vPosition;

  // Simplex noise functions omitted here — include from glsl-noise library
  // or inline from: https://gist.github.com/patriciogonzalezvivo/670c22f3966e662d2f83

  void main() {
    vNormal = normalMatrix * normal;
    vPosition = position;

    float noise = sin(position.x * 3.0 + u_time) *
                  cos(position.y * 2.0 + u_time * 0.7) *
                  sin(position.z * 4.0 + u_time * 0.5);

    vec3 newPos = position + normal * noise * u_amplitude;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(newPos, 1.0);
  }
`;

const fragmentShader = `
  varying vec3 vNormal;
  varying vec3 vPosition;
  uniform samplerCube u_envMap;
  uniform vec3 u_cameraPos;

  void main() {
    vec3 normal = normalize(vNormal);
    vec3 viewDir = normalize(u_cameraPos - vPosition);
    vec3 reflectDir = reflect(-viewDir, normal);

    vec4 envSample = textureCube(u_envMap, reflectDir);

    // Fresnel rim
    float fresnel = pow(1.0 - max(dot(viewDir, normal), 0.0), 4.0);
    vec3 rimColor = vec3(0.4, 0.6, 1.0) * fresnel;

    gl_FragColor = vec4(envSample.rgb + rimColor, 1.0);
  }
`;

function LiquidMetalBlob() {
  const meshRef = useRef();
  const materialRef = useRef();

  const uniforms = useMemo(() => ({
    u_time:      { value: 0.0 },
    u_amplitude: { value: 0.12 },
    u_cameraPos: { value: new THREE.Vector3() },
    u_envMap:    { value: null }, // Set after environment loads
  }), []);

  useFrame(({ clock, camera }) => {
    if (materialRef.current) {
      materialRef.current.uniforms.u_time.value = clock.getElapsedTime();
      materialRef.current.uniforms.u_cameraPos.value.copy(camera.position);
    }
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.003;
    }
  });

  return (
    <mesh ref={meshRef}>
      <sphereGeometry args={[1, 128, 128]} />
      <shaderMaterial
        ref={materialRef}
        vertexShader={vertexShader}
        fragmentShader={fragmentShader}
        uniforms={uniforms}
      />
    </mesh>
  );
}

// Simpler version using MeshPhysicalMaterial (recommended starting point)
function LiquidMetalPBR() {
  const meshRef = useRef();
  const matRef = useRef();

  useFrame(({ clock }) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.003;
      meshRef.current.rotation.x = Math.sin(clock.getElapsedTime() * 0.2) * 0.08;
    }
    if (matRef.current) {
      // Breathing roughness effect
      matRef.current.roughness = 0.04 + Math.sin(clock.getElapsedTime() * 0.5) * 0.02;
    }
  });

  return (
    <mesh ref={meshRef}>
      <sphereGeometry args={[1, 128, 128]} />
      <meshPhysicalMaterial
        ref={matRef}
        color="#ffffff"
        metalness={1.0}
        roughness={0.05}
        envMapIntensity={2.5}
        clearcoat={1.0}
        clearcoatRoughness={0.05}
        iridescence={0.8}
        iridescenceIOR={1.8}
        iridescenceThicknessRange={[100, 800]}
      />
    </mesh>
  );
}

// Full scene export
export default function LiquidMetalScene() {
  return (
    <Canvas
      camera={{ position: [0, 0, 3], fov: 45 }}
      gl={{ antialias: true, toneMapping: THREE.ACESFilmicToneMapping }}
    >
      <Environment preset="studio" background={false} />
      <LiquidMetalPBR />
    </Canvas>
  );
}
```

### R3F Performance Tips

```jsx
// Use useMemo for geometries to prevent recreation each frame
const geometry = useMemo(() => new THREE.SphereGeometry(1, 128, 128), []);

// Dispose on unmount
useEffect(() => {
  return () => {
    geometry.dispose();
    material.dispose();
  };
}, []);

// DPR control for mobile performance
<Canvas dpr={[1, 2]}>  {/* Max 2x pixel ratio — prevents overdraw on mobile */}
```

---

## 12. MetalFlow Reference Analysis

**GitHub**: https://github.com/Saganaki22/MetalFlow

MetalFlow is the most directly relevant open-source liquid metal implementation. Key architectural decisions:

### Its Six Shader Uniforms (Learn These)

| Uniform | Range | What It Controls |
|---------|-------|-----------------|
| `refraction` | 0.0 – 0.03 | Metallic sheen + light distortion strength |
| `edge` | 0.0 – 1.0 | Edge softness — how hard the silhouette boundary is |
| `patternBlur` | 0.0 – 0.02 | Smoothness of the metallic pattern |
| `liquid` | 0.0 – 0.2 | Flow and movement intensity |
| `speed` | 0.0 – 0.5 | Animation tempo |
| `patternScale` | 0.5 – 5.0 | Size of metallic pattern features |

### Key Lesson from MetalFlow

The `refraction` uniform controlling "metallic sheen" is not actual refraction physics — it's a distortion amount applied to the environment sample lookup. This is a common creative shortcut:

```glsl
// "Refraction" as distortion:
vec2 distortedUv = uv + normal.xy * u_refraction;
vec4 color = texture2D(u_envMap, distortedUv);
```

This is faster than real refraction and looks great for logos/flat surfaces. For 3D blobs, use the full `reflect()` approach instead.

---

## 13. Connection to Gleb Aesthetic

From the Feb 2026 Gleb Kuznetsov study (`2026-02-20--gleb-kuznetsov-sphere-visual-analysis.md`):

**Core principle already established**: "Gleb renders LIGHT, not objects."

Liquid metal extends this philosophy:
- The metal blob is a vehicle for **reflecting** the environment, not displaying itself
- Like Gleb's glass sphere, it's a **light container** — a dynamic mirror
- The environment IS the content; the geometry is just the lens shape

### How to Combine Them

The Gleb sphere study established:
- Multi-light colored environment (6 lights, multiple colors)
- Gold specular highlights (#C8A84A)
- Dark void background (#080a12)
- No surface noise (perfectly smooth)

Liquid metal + Gleb aesthetic =
- Keep the **smooth dark background** (#080a12)
- Keep the **colored environment lighting** (not a white studio)
- Add **liquid morphing** to the sphere shape
- Replace **glass refraction** with **metal reflection** (metalness: 1.0, roughness near 0)
- Add **iridescence** for the thin-film color shift at edges

### Brand Colors as Environment Light

From the Gleb palette, adapted for liquid metal environment:
```javascript
// These become your area lights in the HDR / environment setup
const lights = [
  { color: '#0D16F5', intensity: 2.0, position: [-3, 2, -2] },   // Electric blue
  { color: '#D10DCE', intensity: 1.5, position: [3, 1, -2] },    // Magenta
  { color: '#18A8D3', intensity: 1.0, position: [0, -2, 3] },    // Cyan fill
  { color: '#B99C43', intensity: 0.8, position: [0, 3, 0] },     // Gold top light
];
```

The metal will pick up all these colors in its reflections — the result is a purebrain.ai–branded liquid metal look.

---

## 14. Production Checklist

Before deploying any liquid metal effect to purebrain.ai:

### Performance
- [ ] Mobile tested — fluid sim disabled on `navigator.hardwareConcurrency < 4`
- [ ] DPR capped at 2.0 max (`<Canvas dpr={[1, 2]}>`)
- [ ] Geometry poly count appropriate: 64-segment for mobile, 128-segment for desktop
- [ ] Environment map served from CDN, gzipped `.hdr` or gainmap `.webp` format
- [ ] `dispose()` called on geometry and material on component unmount

### Visual Quality
- [ ] Environment map loaded and `scene.environment` set before first frame
- [ ] Vertex normals recomputed after any CPU-side displacement
- [ ] `ACESFilmicToneMapping` enabled on renderer for proper HDR tonemapping
- [ ] `renderer.outputColorSpace = THREE.SRGBColorSpace` for correct color output

### Accessibility
- [ ] `prefers-reduced-motion` check — static version shown if user prefers no animation
- [ ] Canvas has `aria-hidden="true"` — it's decorative, not content

### Code Pattern
```javascript
// Standard renderer setup for liquid metal
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;
renderer.outputColorSpace = THREE.SRGBColorSpace;
```

---

## 15. Further Study

### Immediate Next Steps

1. **Build the PBR version** (Approach A) — fastest win, can ship in 1 session
2. **Download 3 chrome matcap PNGs** from nidorx/matcaps — try them on the current Gleb sphere
3. **Download `studio_small_08.hdr`** from Polyhaven and swap into the current avatar-fluid.html

### Advanced Learning Path

1. **Book of Shaders** (noise chapter): https://thebookofshaders.com/11/
2. **Three.js Journey** (materials + environment lessons): https://threejs-journey.com
3. **Codrops WebGL tutorials**: https://tympanus.net/codrops/category/tutorials/
4. **Pavel Dobryakov's fluid sim source**: https://github.com/PavelDoGreat/WebGL-Fluid-Simulation

### Specific Experiment Queue

| Experiment | Goal | Approach |
|-----------|------|----------|
| Chrome Gleb Sphere | Swap glass for metal on existing avatar | Approach A |
| Morphing Investor Badge | Animated metal logo mark | Approach B MatCap |
| Mouse-Reactive Metal Hero | Liquid metal blob that responds to cursor | Approach C + mouse uniform |
| Full Fluid Background | Navier-Stokes metal pool for investor page | Approach D |

---

## Memory Written

**Path**: `.claude/memory/departments/systems-technology/2026-03-22--liquid-metal-3d-training-study.md`
**Type**: teaching
**Topic**: Liquid metal visual effects — full implementation guide for Three.js / R3F stack

---

*Study authored by dept-systems-technology | 2026-03-22 | Part of Aether 3D Training Series*
