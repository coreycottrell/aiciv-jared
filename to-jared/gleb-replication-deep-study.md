# Gleb Kuznetsov / Milkinside Glass Sphere: Deep Technical Replication Study

**Date**: 2026-02-20
**Purpose**: Understand WHY the avatar keeps drifting wrong, and what must change before writing another line of code
**Approach**: Scientific inquiry - diagnose the gap, then prescribe the fix

---

## 1. Why Our Current Approach Fails (The Fundamental Gap)

### The Rendering Paradigm Mismatch

This is the core problem and it cannot be papered over with more shaders.

Gleb renders in **Octane Render** - a **path tracer** that runs on a GPU for minutes or hours per frame. We are running a **single-pass raymarcher** inside a fragment shader at 60fps. These are categorically different rendering approaches. The gap is not about shader skill. The gap is about physics simulation depth.

**What path tracing does that we cannot do in a fragment shader:**

| Effect | Octane Path Tracing | Our Single-Pass Raymarcher |
|--------|--------------------|-----------------------------|
| Light bounces inside glass | 4-8+ recursive bounces per ray | 1 refraction, 1 reflection, done |
| Caustics | Accumulated from thousands of photon paths | Procedural noise approximation |
| Environment reflections | Samples actual HDRI every bounce | Approximated cube/sphere env map |
| Total internal reflection | Computed from actual Fresnel equations at each bounce | Either missing or approximated |
| Beer's Law absorption | Applied over real geometric thickness | Faked with distance estimate |
| Chromatic dispersion | Separate R/G/B rays traced independently | Either missing or done as offset UVs |
| Thin film interference | Full wave optics simulation possible | Not present |
| Self-shadowing inside glass | Emerges from path accumulation | Not present |

The reason Gleb's glass has that magical internal complexity - the light that bounces around inside and creates unexpected color pools, the caustic rings on the floor, the way highlights shimmer at different positions - is that **thousands of photon paths are being accumulated over many frames**. Each path bounces differently. The average of thousands of these creates the rich, physically-correct result.

We are computing one path. We see the skeleton. Gleb shows the living body.

### Specific Technical Failures in a Single-Pass Raymarcher

**Problem 1: Single refraction exit.**
When a ray enters a glass sphere, refracts, travels through the interior, and exits, it should refract AGAIN at the exit surface. It should also reflect partially at both surfaces (Fresnel). A simple raymarcher typically does one of:
- Refract at entry, ignore exit (wrong - the lens distortion is completely off)
- Refract at entry and exit but treat them as separate operations without proper Fresnel blending

The correct implementation requires: entry ray -> Fresnel split (reflect + refract) -> traverse interior -> exit surface -> Fresnel split again (reflect + refract, some internally reflected rays bounce again) -> accumulate weighted sum.

**Problem 2: No Beer's Law.**
Real glass absorbs light differently across RGB wavelengths depending on how far the ray travels through it. Blue glass looks blue because it absorbs red more than blue. Without Beer's Law (`color *= exp(-absorptionCoefficient * distanceTraveled)`), glass looks like colored plastic, not like glass.

**Problem 3: Icosahedron as inner geometry is probably wrong.**
Gleb's inner geometry - the thing you see through the glass - is typically a **fluid, organic blob or metaball**, or it IS an emission object (glowing wireframe, crystal, vortex). An icosahedron is a rigid mathematical solid with flat faces. When you look at it through a glass lens (which inverts and distorts), the flat faces create unnatural aliased edges. Organic shapes distort gracefully through glass. Polyhedra look like bad CGI.

**Problem 4: The environment is too simple.**
The glass sphere is only as interesting as what it reflects and refracts. Gleb uses a carefully crafted HDRI environment plus multiple colored area lights placed specifically to create interesting highlights in the glass. Our procedural environment map (usually a gradient or simple colors) gives the glass nothing interesting to refract or reflect, so it looks empty.

**Problem 5: Over-engineering the wrong things.**
Adding more procedural noise, more glow effects, more animated parameters on top of a fundamentally wrong refraction model produces a more complicated version of the wrong look. Each added effect costs performance without moving toward Gleb's aesthetic.

---

## 2. What Gleb Actually Does (His Exact Workflow)

### The Tools

**Cinema 4D** - 3D modeling and scene composition
**Octane Render** - GPU path tracer (now owned by OTOY, tightly integrated with C4D)
**Post-processing** - Photoshop/After Effects for final color grade

Gleb does NOT use WebGL. He does NOT use raymarching. He uses an offline renderer that simulates physics correctly.

### The Material: Octane Specular (Glass) Material

Octane's Specular material is the physically correct glass shader. Key parameters:

**Index of Refraction (IOR): 1.5**
This is standard glass. Higher values (1.7-2.4) look like crystal or diamond. Lower values (1.3) look like water. Gleb likely uses 1.45-1.55 for glass spheres.

**Roughness: near 0 (0.0 to 0.02)**
Perfect or near-perfect glass. Any roughness above 0.05 starts looking frosted. Gleb's glass is clean and clear.

**Transmission: 1.0 (full)**
Light passes through completely. Dispersion Coefficient B controls chromatic dispersion.

**Fake Shadows: OFF**
This is critical. When Fake Shadows is ON, Octane treats glass like an architectural window - it passes shadows through but does not compute caustics. When OFF, real caustics form from light path accumulation. Gleb's glass creates real caustics.

**Thin Wall: OFF**
Only for soap bubbles. A sphere has volume, so this must be OFF.

**Absorption color / Beer's Law**
Set through the Transmission color or Absorption channel. A slight blue or teal tint in the absorption creates that characteristic cool glass look where thick parts appear more saturated.

**Specular Depth: minimum 4-8**
This is how many times a ray can bounce inside specular (glass) objects. Below 4, you get black patches inside the glass. Gleb's renders likely use 8-16 bounce depth. This is THE setting that creates the internal complexity.

### The Lighting (The Most Important Part)

This is what people miss. The glass sphere is only a container. The LIGHTING is what makes it look extraordinary.

**Gleb's established color palette (extracted from work):**
- Background: near-black, `#020204` to `#0D1B32` (never pure black - always a subtle blue tint)
- Primary sphere light: purple `#3C0E4E` or blue `#0D16F5`
- Accent fill: teal `#18A8D3` or `#526594`
- Warm pop: occasional magenta `#D10DCE` or gold `#B99C43`

**The lighting technique:**
1. **HDRI environment** - A dark studio HDRI with 1-3 bright highlight zones. This provides the primary reflections and ambient fill. The HDRI is rotated carefully so highlights appear where Gleb wants them on the sphere.
2. **Multiple colored area lights** - 2-4 colored area lights placed around the sphere, each with a different color. These lights exist PRIMARILY to create colored reflections in the glass and colored caustics on the ground. The human eye sees an area light reflected in glass as a crisp colored highlight.
3. **Emission objects inside the sphere** - The internal geometry often has an emissive material. This creates the internal glow from within. The glass then lenses and warps this internal light, creating the complex internal light patterns.
4. **Dual environment technique** - Octane allows two environment objects: one Primary (for lighting and reflections into the glass) and one Visible (for what the background looks like). Gleb often uses a rich HDRI for lighting but renders with a pure dark background.

**The internal geometry:**
Looking at Gleb's work across years:
- Metaball / blob forms (most common in recent AI sphere work)
- Organic wireframe structures
- Fluid/liquid simulations frozen in position
- Sometimes: icosahedron-like crystals, but smoothed with subdivision surface
- Emission strength is typically very high (5-15x normal) so it glows intensely through the glass

### Path Tracer Settings

Octane Path Tracing kernel settings that affect glass quality:
- **Max path depth / GI depth**: 8-16 bounces (essential for glass)
- **Specular depth**: 4-8 (bounces specifically inside specular/glass objects)
- **Caustic blur**: 0 (no blur = sharp, high-quality caustics, but needs more samples)
- **Samples**: Gleb's stills are likely rendered at 2000-5000 samples for full convergence
- **Denoising**: Octane AI Denoiser used to clean noise while maintaining detail

---

## 3. The Best Path to Replicate in WebGL

### Honest Assessment: You Cannot Fully Match Gleb in Realtime

A pure GLSL fragment shader raymarcher running at 60fps will not produce Gleb's exact output. That is physics. Accept this constraint, then work within it intelligently.

The goal is not pixel-perfect replication. The goal is **capturing the aesthetic feeling** of his work - that sense of deep glass, internal complexity, and refined lighting - at interactive framerates.

### Option A: THREE.js with MeshTransmissionMaterial (RECOMMENDED)

**What it is:**
MeshTransmissionMaterial (from `@react-three/drei` or `drei-vanilla`) is the closest WebGL approximation of physically-based glass. It is an extension of THREE.MeshPhysicalMaterial that adds:
- Transmission via framebuffer sampling (captures what's behind the glass per-frame)
- Chromatic aberration (per-channel IOR simulation)
- Thickness-based refraction depth
- Distortion via simplex noise
- Beer's Law attenuation (`attenuationDistance` + `attenuationColor`)

**How it handles the inner object:**
Three.js performs a separate render pass of the scene for each transmission object. This means the inner geometry (your vortex, metaball, emission object) is rendered first, then composited through the glass material. This is NOT raytracing but it correctly handles the inner object appearing through the glass.

**Why this beats raymarching for the Gleb look:**
- The inner object renders with REAL THREE.js lighting (point lights, spotlights with colors)
- The environment map reflects correctly from an HDRI
- Multiple bounce emulation through framebuffer sampling
- Chromatic aberration splits colors at the glass edge exactly as physical dispersion would
- Can have actual HDRI environment with multiple colored lights positioned precisely

**Known limitation:**
Cannot compute caustics (light focusing patterns). Can fake them with a separate plane mesh and an animated caustic texture.

### Option B: Pure GLSL Raymarcher with Multi-Bounce (NOT Recommended for Gleb Aesthetic)

A proper raymarcher with 4+ bounces GLSL implementation is possible on Shadertoy but:
- Is expensive (caps at ~30fps on modern hardware for complex scenes)
- Still cannot do accumulated path tracing caustics (needs WebGPU compute or progressive rendering)
- The Gleb look requires an interesting environment to refract - a procedural environment is hard to make look as good as a real HDRI

The only scenario where raw GLSL raymarching wins: you want a single mathematical object (pure sphere, torus) and you need precise control over every aspect of the shader. For the Gleb aesthetic with inner objects and environment lighting, THREE.js wins.

### Option C: THREE.js + Progressive Path Tracing (The Best Long-Term Option)

Erichlof's THREE.js-PathTracing-Renderer demonstrates that WebGL path tracing is possible at 30-60fps with progressive accumulation. The approach:
- Renders multiple samples per frame, accumulates over time
- When the camera stops moving, the image converges to near-photorealistic quality
- Glass with multiple bounces, caustics, Beer's Law - all correct
- During motion: lower quality (expected)
- When still: stunning quality

This matches how Gleb actually renders - accumulating samples over time. For an avatar that can be "still" (talking/idle state), this would look extraordinary.

**Tradeoff**: Requires rewriting rendering architecture from scratch. Not a quick fix.

### Recommendation: Start with Option A (THREE.js + MeshTransmissionMaterial)

It is the fastest path from "broken" to "close to Gleb" with manageable code changes.

---

## 4. Specific Implementation Blueprint

Follow this exact order. Do not skip steps.

### Step 1: Establish the Scene Foundation (Before Any Glass)

Create the environment that the glass will reflect and refract.

```javascript
// 1. Dark HDRI environment (find a studio HDRI with 2-3 bright zones)
// Use polyhaven.com - "studio_small_03" or "leadenhall_market"
// Both have that dramatic dark-with-highlights quality

import { Environment } from '@react-three/drei'

<Environment
  files="/hdri/studio_small_03_1k.hdr"
  background={false}  // Don't show HDRI as background
/>

// 2. Set background color to near-black with blue tint
<color attach="background" args={['#0D1B32']} />
// NOT pure black. Gleb uses #020204 to #0D1B32 - always a cool tint.
```

### Step 2: Build the Inner Emission Object

This is what people see THROUGH the glass. It must be visually interesting.

```javascript
// Option A: Animated blob/metaball using vertex shader displacement
// Use IcosahedronGeometry at detail level 15+ (smooth sphere approximation)
// Apply vertex displacement in shader using FBM noise

// Option B: Particle vortex (as in Codrops 2025 tutorial)
// Particles rendered as emissive sprites
// Much more "Gleb AI sphere" feel than rigid geometry

// Key: Inner object needs EMISSIVE material
// High emission intensity (3-10x) so it glows through the glass
<mesh>
  <icosahedronGeometry args={[0.7, 15]} />
  <meshStandardMaterial
    emissive="#18A8D3"    // Teal glow
    emissiveIntensity={5}
    roughness={0.4}
    metalness={0.8}
  />
</mesh>
```

### Step 3: Apply MeshTransmissionMaterial to the Glass Sphere

```javascript
import { MeshTransmissionMaterial } from '@react-three/drei'

// Outer glass sphere (MUST be slightly larger than inner object)
<mesh>
  <sphereGeometry args={[1.0, 64, 64]} />
  <MeshTransmissionMaterial
    // Core glass properties
    transmission={1}           // Full transparency
    thickness={0.5}            // Affects refraction depth - start at 0.5, tune
    ior={1.5}                  // Standard glass IOR
    roughness={0.0}            // Perfect glass

    // Color and absorption (Beer's Law equivalent)
    attenuationColor="#a8d4f5" // Subtle blue tint for thick parts
    attenuationDistance={0.8}  // Lower = more absorption = more colored tint

    // Chromatic dispersion (R/G/B split) - KEY to Gleb look
    chromaticAberration={0.08} // Start at 0.08, Gleb probably uses 0.05-0.12

    // Refraction quality
    samples={10}               // Higher = smoother refraction, more expensive

    // Surface reflections
    reflectivity={0.15}        // Low but present
    envMapIntensity={1.5}      // How strongly it reflects the HDRI

    // Inner surface rendering (essential for visible inner object)
    backside={true}            // Renders inside surface separately
    backsideThickness={0.1}    // Thin inner surface

    // Animated distortion (Gleb's glass has slight organic movement)
    distortion={0.1}           // Noise-based surface warping
    distortionScale={0.3}
    temporalDistortion={0.05}  // Time-varying distortion
  />
</mesh>
```

### Step 4: Place Colored Lights Strategically

This is the most impactful step that most people skip.

```javascript
// Gleb's characteristic multi-colored lighting setup
// Each light is a different color - they create colored highlights IN the glass

// Primary blue-purple key light
<pointLight
  position={[2, 3, 1]}
  color="#4A0CF5"   // Deep blue-purple
  intensity={15}    // High intensity - glass materials need strong lights
/>

// Teal fill (opposite side)
<pointLight
  position={[-2, 0, -1]}
  color="#00C8D4"   // Teal
  intensity={8}
/>

// Warm accent (below or behind)
<pointLight
  position={[0, -2, 2]}
  color="#9B00FF"   // Purple
  intensity={5}
/>

// Small rim light for the edge definition Gleb loves
<spotLight
  position={[0, 4, -2]}
  color="#ffffff"
  intensity={3}
  angle={0.3}
  penumbra={0.8}
/>
```

### Step 5: Fake Caustics on Ground Plane (Optional but Impactful)

Gleb's glass creates visible caustic rings/patterns below/behind the sphere. In THREE.js this requires faking them.

```javascript
// Place a dark plane below the sphere
// Apply an animated caustic texture via a custom shader
// Use a caustic normal map from polyhaven.com + animate its UV over time

<mesh rotation={[-Math.PI/2, 0, 0]} position={[0, -1.2, 0]}>
  <planeGeometry args={[10, 10]} />
  <meshStandardMaterial
    map={causticTexture}  // animated caustic/water pattern
    color="#050510"
    transparent
    opacity={0.6}
  />
</mesh>
```

### Step 6: Post-Processing (The Final 20% of the Look)

Gleb's renders go through significant post-processing. In THREE.js:

```javascript
import { Bloom, ChromaticAberration, DepthOfField } from '@react-three/postprocessing'

// Bloom makes the emission from inner objects bleed through glass
<Bloom
  intensity={1.5}
  luminanceThreshold={0.6}
  luminanceSmoothing={0.9}
  radius={0.8}
/>

// Additional chromatic aberration on the full image
<ChromaticAberration
  offset={[0.002, 0.002]}
/>

// Slight depth of field for that "photographed" quality
<DepthOfField
  focusDistance={0}
  focalLength={0.02}
  bokehScale={2}
/>
```

---

## 5. Reference Shaders and Demos That Get Closest

### Best WebGL Implementations (Closest to Gleb)

**1. Codrops: Rendering a Procedural Vortex Inside a Glass Sphere (THREE.js + TSL)**
URL: https://tympanus.net/codrops/2025/03/10/rendering-a-procedural-vortex-inside-a-glass-sphere-with-three-js-and-tsl/
- Uses MeshPhysicalNodeMaterial with transmission=1, ior=1.5, clearcoat=0.73
- Particle vortex as inner content with FBM emission glow
- This is THE closest published implementation to the Gleb aesthetic

**2. Olivier Larose: 3D Glass Effect**
URL: https://blog.olivierlarose.com/tutorials/3d-glass-effect
- Proven parameter set: thickness=0.2, roughness=0, transmission=1, ior=1.2, chromaticAberration=0.02, backside=true
- Clean starting point

**3. Codrops: Warping 3D Text Inside a Glass Torus (2025)**
URL: https://tympanus.net/codrops/2025/03/13/warping-3d-text-inside-a-glass-torus/
- Shows the render pass architecture for inner objects through glass
- Excellent for understanding the transmission pipeline

**4. Maxime Heckel: Refraction, Dispersion and Other Shader Light Effects**
URL: https://blog.maximeheckel.com/posts/refraction-dispersion-and-other-shader-light-effects/
- Best explanation of chromatic aberration from first principles in GLSL
- Explains the 6-channel (RYGCBV) technique for smooth dispersion
- RGB to full spectrum technique prevents banding

**5. Shadertoy: Spectral Glass (sdyGR3)**
URL: https://www.shadertoy.com/view/sdyGR3
- Integrates over visible light spectrum instead of just RGB
- 3 bounces of light, physically correct dispersion
- Proof that a raymarcher CAN do multi-bounce if you accept 30fps

**6. Demo.Frog: Raytracing Reflection, Refraction, Fresnel, TIR, Beer's Law**
URL: https://blog.demofox.org/2017/01/09/raytracing-reflection-refraction-fresnel-total-internal-reflection-and-beers-law/
- The definitive tutorial on physically correct glass ray tracing
- Shows 3 bounces is sufficient for most objects
- If you ever return to GLSL raymarching, implement this exactly

**7. THREE.js PathTracing Renderer (Erichlof)**
URL: https://erichlof.github.io/THREE.js-PathTracing-Renderer/
- Demonstrates caustics, global illumination, glass multi-bounce in WebGL
- Quality during motion: good. Quality when still: extraordinary.
- The progressive accumulation approach for the best eventual quality

---

## 6. What to Change vs What to Keep

### STOP Doing

**Stop: Single-pass GLSL raymarching for the glass shell.**
It cannot compute what Gleb's renderer computes. Switch to THREE.js MeshTransmissionMaterial which uses a proper framebuffer-based approach.

**Stop: Icosahedron as inner geometry.**
The flat faces of an icosahedron look algorithmic and rigid when seen through a glass lens. Replace with either a high-subdivision smooth blob (IcosahedronGeometry detail 15+) with vertex displacement, OR a particle/vortex system with emission.

**Stop: Adding more procedural effects to the wrong foundation.**
More noise, more glow, more animation on a broken refraction model makes a more broken result. Fix the foundation first.

**Stop: Single light color or pure ambient lighting.**
Gleb uses 3-5 colored lights with deliberate placement. Each light creates a different colored highlight inside the glass. This is not decorative - it IS the look.

**Stop: Pure black background.**
Gleb's backgrounds are `#020204` to `#0D1B32`. Always a very dark blue or indigo tint, never pure black. Pure black background makes glass look like it's floating in a void rather than in a dark studio.

### KEEP or ENHANCE

**Keep: The sphere shape.**
A sphere is geometrically correct for Gleb's AI sphere work. The sphere itself is right.

**Keep: The concept of inner geometry.**
Having something inside the glass sphere is exactly right. The icosahedron concept is right. The execution (sharp polygon faces, wrong material) is wrong.

**Keep: Animation / breathing motion.**
Gleb's AI sphere visuals are typically animated. A slowly pulsing inner form, slight rotation of the internal structure, gentle temporal distortion of the glass surface. This is right.

**Keep: Dark moody color palette.**
Purple-blue-teal with near-black background is exactly Gleb's palette. The color direction is correct.

**Enhance: Post-processing.**
Add bloom from `@react-three/postprocessing`. The emission bleeding through the glass and creating that halo is a major part of the visual. Without bloom, emission objects look flat.

**Enhance: HDRI environment.**
Get a real dark studio HDRI from polyhaven.com. Do not use a procedural environment. The HDRI provides the interesting reflections that make the glass look like it has something to reflect.

---

## 7. The Honest Summary

**Why it keeps drifting wrong:** We are using a raymarcher (single-pass, single-bounce) trying to approximate results that require path tracing (multi-pass, multi-bounce, accumulated over time). Every new shader effect added is a bandage on the wrong approach.

**What Gleb actually does:** Cinema 4D + Octane Render. Specular (glass) material with IOR 1.5, zero roughness, full transmission, NO fake shadows, specular depth 8+, Beer's Law absorption for color tint. Multiple colored area lights. HDRI environment with separate visible background. Organic/emissive inner geometry. Post-processing color grade.

**The correct WebGL path:** THREE.js + MeshTransmissionMaterial + real HDRI + colored point lights + emissive inner geometry + bloom post-processing. This is Option A above. It takes maybe 4-6 hours to implement properly from scratch.

**The quality ceiling:** THREE.js MeshTransmissionMaterial will get you to ~75-80% of Gleb's quality. The remaining 20% (true caustics, perfect multi-bounce internal reflection, photon accumulation) requires either a progressive path tracer (Erichlof's approach) or accepting it as a real-time approximation. That is an honest and acceptable ceiling for a browser-based avatar.

**The icosahedron question:** Replace it. Use an animated blob - IcosahedronGeometry at detail 15 with vertex shader displacement using FBM noise and time uniform. Or use the Codrops vortex particle approach. Both look dramatically better through glass than a sharp polyhedron.

**What to do right now:** Do NOT touch the existing broken shader. Start a fresh THREE.js component using the blueprint in Section 4. Get MeshTransmissionMaterial working with a dark HDRI and three colored lights. That single change will get closer to Gleb than all the shader modifications combined.

---

## Sources

- [Greyscalegorilla: Render Glass Orbs in Octane for Cinema 4D](https://greyscalegorilla.com/blog/render-glass-orbs-in-octane-for-cinema-4d)
- [OTOY: Octane Specular Material Documentation](https://docs.otoy.com/cinema4d/SpecularMaterial.html)
- [OTOY: Avoid Glass Rendering Mistakes in Octane](https://lesterbanks.com/2021/02/avoid-these-mistakes-rendering-glass-in-octane/)
- [OTOY: Universal Material Deep Dive](https://help.otoy.com/hc/en-us/articles/360051320052-Universal-Material-Channels-Deep-Dive)
- [Codrops: Procedural Vortex Inside Glass Sphere (THREE.js TSL, 2025)](https://tympanus.net/codrops/2025/03/10/rendering-a-procedural-vortex-inside-a-glass-sphere-with-three-js-and-tsl/)
- [Codrops: Warping 3D Text Inside a Glass Torus (2025)](https://tympanus.net/codrops/2025/03/13/warping-3d-text-inside-a-glass-torus/)
- [Codrops: Creating Glass and Plastic Effects in Three.js (2021)](https://tympanus.net/codrops/2021/10/27/creating-the-effect-of-transparent-glass-and-plastic-in-three-js/)
- [pmndrs/drei-vanilla: MeshTransmissionMaterial Source](https://github.com/pmndrs/drei-vanilla/blob/main/src/materials/MeshTransmissionMaterial.ts)
- [React Three Drei: MeshTransmissionMaterial Documentation](https://drei.docs.pmnd.rs/shaders/mesh-transmission-material)
- [Maxime Heckel: Refraction, Dispersion and Other Shader Light Effects](https://blog.maximeheckel.com/posts/refraction-dispersion-and-other-shader-light-effects/)
- [Demo.Frog: Raytracing Reflection, Refraction, Fresnel, TIR and Beer's Law](https://blog.demofox.org/2017/01/09/raytracing-reflection-refraction-fresnel-total-internal-reflection-and-beers-law/)
- [THREE.js PathTracing Renderer (Erichlof)](https://erichlof.github.io/THREE.js-PathTracing-Renderer/)
- [ResearchGate: Real-Time Ray Traced Caustics](https://www.researchgate.net/publication/354065234_Real-Time_Ray_Traced_Caustics)
- [Shadertoy: Spectral Glass](https://www.shadertoy.com/view/sdyGR3)
- [Gleb Kuznetsov / Milkinside on Dribbble](https://dribbble.com/glebich)
- [Milkinside: Glass Reflection CGI (2022)](https://dribbble.com/shots/20098860-Glass-reflection-CGI-by-Milkinside)
- [Milkinside: AI Sphere Visual Design (2024)](https://dribbble.com/shots/24197602-AI-sphere-visual-design-by-Milkinside)
- [Olivier Larose: 3D Glass Effect Tutorial](https://blog.olivierlarose.com/tutorials/3d-glass-effect)
- [iRendering: Deep Dive into Caustics in Octane for Cinema 4D](https://irendering.net/a-deep-dive-into-caustics-in-octane-for-cinema-4d/)
- [OTOY: Environment Deep Dive for Octane and C4D](https://help.otoy.com/hc/en-us/articles/24029344731931-Environment-Deep-Dive-in-Octane-C4D)
