# Avatar Design References: Gleb Kuznetsov Quality Glass/Crystal in WebGL

**Prepared by**: web-researcher agent
**Date**: 2026-02-20
**Goal**: Reach the visual quality of Gleb Kuznetsov's glass/crystal 3D work in a WebGL raymarched avatar

---

## Executive Summary

Gleb Kuznetsov's premium glass aesthetic comes from three core decisions working together: (1) deep near-black backgrounds that make every photon of light feel precious, (2) Cinema 4D physically-based glass with precise IOR, caustics, and chromatic aberration rendered to perfection, and (3) multi-layered color-shifted lighting that turns a simple sphere into a jewel. Reproducing this in WebGL raymarching requires combining per-channel refraction (IOR splitting per R/G/B), multi-bounce internal reflections, Fresnel edge glow, and a rich environment map. The GLSL techniques below are all proven in production WebGL. The quality ceiling is higher than most people expect.

---

## Part 1: Gleb Kuznetsov's Portfolio - The Reference Standard

Gleb Kuznetsov is Creative Director / Design Director at Milkinside. He has 1M+ followers on Dribbble and his work is the benchmark for premium glass/crystal 3D in product design. He renders in Cinema 4D with Octane or Redshift.

### His Most Iconic Glass/Crystal Work (Direct URLs)

**Spheres and orbs:**
- Colorful AI sphere (2025 update): https://dribbble.com/shots/24197602-AI-sphere-visual-design-by-Milkinside
- Colorful AI sphere (classic): https://dribbble.com/shots/14194855-Colorful-AI-sphere-by-Gleb-Kuznetsov
- Dark blue globe: https://dribbble.com/shots/14887210-Dark-blue-globe
- Blue grass sphere reflection: https://dribbble.com/shots/14472718-Blue-grass-sphere-reflection
- Abstract sphere art: https://dribbble.com/shots/15319560-Abstract-sphere-art
- AI Visual design (2024): https://dribbble.com/shots/24126473-AI-Visual-design-by-Milkinside
- Soft AI sphere: https://dribbble.com/shots/24197602-AI-sphere-visual-design-by-Milkinside

**Crystal and glass shapes:**
- Crystal sculpture: https://dribbble.com/shots/14486416-Crystal-sculpture
- Crystal illustration: https://dribbble.com/shots/14492867-Crystal-illustration
- Glass blower visual: https://dribbble.com/shots/17066462-Glass-blower-visual
- Glass reflection CGI by Milkinside: https://dribbble.com/shots/20098860-Glass-reflection-CGI-by-Milkinside
- Glass landscape: https://dribbble.com/shots/15252462-Glass-landscape
- Colorful Glass brand visual: https://dribbble.com/shots/7039700-Colorful-Glass-brand-visual

**Liquid:**
- Liquid visual exploration: https://dribbble.com/shots/12285048-Liquid-visual-exploration
- Liquid AI visual for product UI: https://dribbble.com/shots/4943969-Liquid-AI-visual-for-product-UI
- Liquid AI visual: https://dribbble.com/shots/8995914-liquid-AI-visual
- Glass cube for AI product: https://dribbble.com/shots/5982977-Glass-cube-visual-for-AI-product
- Caustic glass light liquid (credit card animation): https://dribbble.com/milkinside

**Full profile:**
- Dribbble: https://dribbble.com/glebich
- Behance: https://www.behance.net/gleb
- Milkinside studio: https://dribbble.com/milkinside
- Brand Vision CGI Behance case study: https://www.behance.net/gallery/80917393/Brand-Vision-CGI-story-Milkinside

### What Makes the Gleb Look - Color Palette Analysis

From reverse-engineering his palette data across multiple shots:

**Background colors (always extremely dark):**
- Near-black navy: `#010204`, `#020204`, `#060619`, `#0D0D1A`
- Deep space blue: `#0D1B32`, `#192655`

**Glass object color layers:**
- Deep purple core: `#3C0E4E`, `#1F388A`
- Bright electric blue highlights: `#0D16F5`, `#295BF1`, `#1F4954`
- Cyan light scatter: `#18A8D3`, `#1DB0F1`
- Violet/pink specular: `#AB7BDE`, `#D10DCE`
- Warm gold caustic light: `#B99C43`
- Red light source accent: `#E42424`

**The signature look:**
- Object sits on near-black background so every highlight pops
- Multiple colored light sources (blue + purple + warm accent) create chromatic depth
- Caustic light patterns projected onto the background below the object
- Heavy chromatic aberration at silhouette edges (RGB fringing)
- Thin bright specular highlights that feel physically real
- Internal volumetric color (the inside of the glass glows differently from the surface)

**His process (from interviews):**
- Uses Cinema 4D with Octane or Redshift renderer
- Runs render farms (sometimes two machines simultaneously)
- "Evening work on design or rendering to create some of my real magic"
- Works in precise timed blocks; glass renders require render time investment
- Philosophy: "Design is the emotions carried by it" - not utility, pure feeling

---

## Part 2: Live WebGL Experiences Achieving This Quality

These are real sites/demos you can open in a browser RIGHT NOW:

### Photorealistic Path-Traced Glass (WebGL)
- **THREE.js PathTracing Renderer - Geometry Showcase**: https://erichlof.github.io/THREE.js-PathTracing-Renderer/Geometry_Showcase.html
  - Full path tracing in WebGL, noise-free glass surfaces as of Sept 2024
  - Fly inside glass spheres, see total internal reflection, multiple light bounces
  - Open source: https://github.com/erichlof/THREE.js-PathTracing-Renderer

### Codrops Reference Implementations (All Open Source)
- **Glass Torus with Warped Text (2025)**: https://tympanus.net/codrops/2025/03/13/warping-3d-text-inside-a-glass-torus/
  - Refraction bending 3D text inside a glass torus using Three.js
- **Liquid Raymarching with TSL (2024)**: https://tympanus.net/codrops/2024/07/15/how-to-create-a-liquid-raymarching-scene-using-three-js-shading-language/
  - Full raymarching implementation using Three.js Shading Language (WebGPU-ready)
- **Transparent Glass and Plastic (2021, still gold standard)**: https://tympanus.net/codrops/2021/10/27/creating-the-effect-of-transparent-glass-and-plastic-in-three-js/
  - MeshPhysicalMaterial transmission deep dive
- **Real-time Multiside Refraction**: https://tympanus.net/codrops/2019/10/29/real-time-multiside-refraction-in-three-steps/
  - Three-pass render technique for refraction of refraction

### Kenta Toshikura Glass Effect
- The glass effect that went viral in design circles: https://kentatoshikura.com
- Codrops recreation tutorial: https://tympanus.net/codrops/2023/03/06/coding-kenta-toshikuras-glass-effect-with-three-js/
- Uses postprocessing and texture manipulation (not standard PBR)

### Apple Liquid Glass (WWDC 2025) - WebGL Implementations
These emerged after Apple introduced Liquid Glass in iOS 26:
- **liquidGL** (ultralight WebGL, DOM refraction): https://github.com/naughtyduk/liquidGL
- **liquid-glass-js** (Apple-inspired library): https://github.com/dashersw/liquid-glass-js
  - Live demo: https://dashersw.github.io/liquid-glass-js/
- **html-liquid-glass-effect-webgl**: https://github.com/rxing365/html-liquid-glass-effect-webgl
- **Liquid Glass in the Browser** (technical article): https://specy.app/blog/posts/liquid-glass-in-the-web
- **Liquid Glass Resources** (WebGL studio + generator): https://www.liquidglassresources.com/development/liquid-glass-studio-webgl/

### Iridescent Crystal (Raymarching)
- **Varun Vachhar's iridescent crystal**: https://varun.ca/ray-march-sdf/
  - Pure raymarching + SDF, iridescence via cosine palette + Fresnel
  - The technique that gets closest to gem-like crystal without full path tracing

### Three.js Thin-Film Iridescence (Live Demo)
- **DerSchmale thin-film iridescence**: https://derschmale.github.io/threejs-thin-film-iridescence/
- GitHub: https://github.com/DerSchmale/threejs-thin-film-iridescence
- Based on Belcour & Barla 2017 research, uses lookup texture for angle-dependent color shift

### Awwwards WebGL Collections (Browse These for Inspiration)
- WebGL collection: https://www.awwwards.com/awwwards/collections/webgl/
- WebGL shaders + code: https://www.awwwards.com/awwwards/collections/webgl-shaders-code/
- 30 experimental WebGL sites: https://www.awwwards.com/30-experimental-webgl-websites.html
- Best WebGL websites: https://www.awwwards.com/websites/webgl/

---

## Part 3: Shadertoy Reference Shaders

These run in your browser at shadertoy.com. Study the GLSL source directly.

### Top Glass/Crystal Shaders

| Shader | URL | What It Demonstrates |
|--------|-----|---------------------|
| Spectral glass | https://www.shadertoy.com/view/sdyGR3 | Integrates over full visible spectrum (not just RGB), 3 light bounces - most physically correct |
| Real glass | https://www.shadertoy.com/view/4s2Gz3 | Multi-bounce path traced glass in a fragment shader |
| Glass is Real | https://www.shadertoy.com/view/wsXfW2 | Another highly realistic glass study |
| Glass sphere refraction | https://www.shadertoy.com/view/XdVfDd | Classic sphere refraction, clean implementation |
| Refraction, Fresnel, Absorption | https://www.shadertoy.com/view/ttBBWz | All three phenomena combined |
| Glass refraction effect | https://www.shadertoy.com/view/XsKSWc | Real-time refraction map |
| Ribbed glass | https://www.shadertoy.com/view/MXfSDr | Textured/ribbed glass surface |
| Thin-film iridescence | https://www.shadertoy.com/view/7sV3Rh | Wavelength-based color shift |
| Thin-film iridescence (dotNV) | https://www.shadertoy.com/view/3s2GDw | Simpler iridescence using NdotV |

**The Spectral Glass shader is the most relevant** - it does exactly what Gleb's renders do physically: it treats each wavelength of light separately so different colors refract at different angles (dispersion), creating rainbow-prismatic edge effects.

---

## Part 4: Specific GLSL Techniques That Achieve the Gleb Look

### Technique 1: Per-Channel IOR Splitting (Chromatic Dispersion)

This is THE core technique. Instead of one refraction vector, compute three - one per color channel - each with a slightly different IOR. This creates the rainbow fringing at glass edges.

```glsl
// Uniforms to expose as controls:
uniform float uIorR;    // e.g. 1.15
uniform float uIorG;    // e.g. 1.18
uniform float uIorB;    // e.g. 1.22
uniform float uChromaticAberration;  // 0.01 - 0.08
uniform float uRefractPower;         // 0.3 - 0.8

// Compute separate refraction per channel:
vec3 refractVecR = refract(eyeVector, worldNormal, 1.0/uIorR);
vec3 refractVecG = refract(eyeVector, worldNormal, 1.0/uIorG);
vec3 refractVecB = refract(eyeVector, worldNormal, 1.0/uIorB);

// Multi-sample to avoid banding:
for(int i = 0; i < LOOP; i++) {
    float slide = float(i) / float(LOOP) * 0.1;
    color.r += texture2D(uTexture, uv + refractVecR.xy *
        (uRefractPower + slide * 1.0) * uChromaticAberration).r;
    color.g += texture2D(uTexture, uv + refractVecG.xy *
        (uRefractPower + slide * 1.0) * uChromaticAberration).g;
    color.b += texture2D(uTexture, uv + refractVecB.xy *
        (uRefractPower + slide * 1.0) * uChromaticAberration).b;
}
color /= float(LOOP);
```

Credit: Maxime Heckel's shader (full tutorial at https://blog.maximeheckel.com/posts/refraction-dispersion-and-other-shader-light-effects/)

### Technique 2: Fresnel Edge Glow

The bright rim light that makes glass feel like it's catching light from everywhere:

```glsl
float fresnel(vec3 eyeVector, vec3 worldNormal, float power) {
    float fresnelFactor = abs(dot(eyeVector, worldNormal));
    float inversefresnelFactor = 1.0 - fresnelFactor;
    return pow(inversefresnelFactor, power);
}

// Apply:
float fresnelTerm = fresnel(eyeVec, normal, uFresnelPower); // power: 3.0 - 8.0
// Mix into output as additive glow, tinted by your rim light color
color += fresnelTerm * rimColor;
```

### Technique 3: Blinn-Phong Specular + Diffuse

Even with full refraction, you need surface lighting:

```glsl
float NdotL = dot(normal, lightVector);
float NdotH = dot(normal, halfVector);  // halfVector = normalize(lightVec + eyeVec)
float kSpecular = pow(NdotH * NdotH, uShininess);  // shininess: 80 - 400
float lighting = kSpecular + max(0.0, NdotL) * uDiffuseness;

// Shininess values:
// 80  = soft specular (frosted glass)
// 200 = clear glass
// 400 = crystal/diamond
```

### Technique 4: Iridescence via Cosine Palette

For the rainbow/prismatic color shift seen in Gleb's colorful sphere work:

```glsl
// Cosine palette generator (Inigo Quilez's technique):
vec3 pal(in float t, in vec3 a, in vec3 b, in vec3 c, in vec3 d) {
    return a + b * cos(6.28318 * (c * t + d));
}

// Full spectrum:
vec3 spectrum(float n) {
    return pal(n, vec3(0.5), vec3(0.5), vec3(1.0), vec3(0.0, 0.33, 0.67));
}

// Apply based on view angle (creates angle-dependent color shift):
vec3 iridescent = spectrum(dot(normal + perturbation * 0.05, eyeDirection) * 2.0);
float specularBand = pow((sin(specularValue * 20.0 - 3.0) * 0.5 + 0.5) + 0.1, 32.0);

// Final:
color = mix(color, iridescent, 0.4) + specularBand * 0.3;
```

Credit: Varun Vachhar's iridescent crystal (full implementation: https://varun.ca/ray-march-sdf/)

### Technique 5: Thin-Film Iridescence (Physics-Based)

For the subtle rainbow-on-soap-bubble look (not the full-rainbow but the shifting oil-slick effect):

```glsl
// Use DerSchmale's lookup texture approach:
// Pre-compute ThinFilmFresnelMap with:
//   filmThickness: 380nm (blue-dominant) to 800nm (red-dominant)
//   filmIOR: 2.0 (coating)
//   baseIOR: 3.0 (substrate)

// In shader:
vec3 airy = texture2D(iridescenceLookUp, vec2(NdotV * 0.99, 0.0)).xyz;
airy *= airy;  // Gamma 2 to linear conversion
color = mix(color, color * airy, iridescenceStrength);
```

Full implementation: https://github.com/DerSchmale/threejs-thin-film-iridescence

### Technique 6: Dual-Pass Rendering (Back Face + Front Face)

Critical for thick glass with visible internal reflections:

```glsl
// Pass 1: Render backfaces to FBO, get their normals
// Pass 2: Render frontfaces, use backface normals to compute
//         "refraction of refraction" (light exits through back surface)

// This is what makes glass look THICK rather than like a soap bubble
// Three.js implementation:
// material.side = THREE.BackSide → render to backFBO
// material.side = THREE.FrontSide → use backFBO as uBackfaceTexture
```

### Technique 7: MeshTransmissionMaterial (Three.js - Fastest Path to Quality)

If using Three.js (not pure raymarching), this is the fastest path to Gleb-quality glass:

```javascript
// React Three Fiber / @react-three/drei:
import { MeshTransmissionMaterial } from '@react-three/drei'

// Recommended values for premium glass orb:
<MeshTransmissionMaterial
    transmission={1}
    thickness={0.8}           // Higher = more refraction, thicker glass
    roughness={0}             // 0 = perfectly clear, 0.1 = slight frost
    ior={1.5}                 // Standard glass IOR
    chromaticAberration={0.05} // Color splitting at edges (0.02 = subtle, 0.1 = obvious)
    anisotropicBlur={0.05}    // Directional blur for frosted effect
    distortion={0.1}          // Internal warping
    temporalDistortion={0.05} // Animation speed for living glass
    backside={true}           // Enable back face refraction
    samples={8}               // Higher = better quality, lower FPS
    envMap={hdriTexture}      // REQUIRED for good reflections
/>
```

Full params doc: https://drei.docs.pmnd.rs/shaders/mesh-transmission-material

### Technique 8: Caustics Projection

The light patterns projected below a glass object (Gleb ALWAYS has this):

```glsl
// Maxime Heckel's approach (https://blog.maximeheckel.com/posts/caustics-in-webgl/):
// 1. Sample normal map at animated offset coordinates
// 2. Compute refracted ray through surface
// 3. Project to ground plane
// 4. Accumulate in render target
// 5. Apply as additive light to scene floor

// Key: Use multiple samples at different normal map offsets
//      Animate over time (uTime uniform)
//      Apply chromatic aberration to caustic colors too
```

Full tutorial: https://blog.maximeheckel.com/posts/caustics-in-webgl/

### Technique 9: PBR Glass Parameters (KHR Extensions for glTF)

When loading glTF assets, these extensions enable full glass behavior:
- `KHR_materials_transmission` - enables light to pass through
- `KHR_materials_volume` - controls attenuation color and distance
- `KHR_materials_ior` - overrides the fixed 1.5 default IOR

Reference: https://www.khronos.org/gltf/pbr

### Technique 10: Saturation Recovery After Dispersion

A subtle but important step - per-channel refraction desaturates colors, so you need to pump them back up:

```glsl
vec3 sat(vec3 rgb, float intensity) {
    vec3 L = vec3(0.2125, 0.7154, 0.0721);  // Luminance weights
    vec3 grayscale = vec3(dot(rgb, L));
    return mix(grayscale, rgb, intensity);   // intensity > 1.0 = supersaturated
}

// After refraction sampling:
color.rgb = sat(color.rgb, 1.3);  // Push saturation up slightly
```

---

## Part 5: Open Source Code to Study

### Full Implementations (Clone and Run)

1. **THREE.js PathTracing Renderer** (most photorealistic glass in WebGL)
   - Repo: https://github.com/erichlof/THREE.js-PathTracing-Renderer
   - Live glass demo: https://erichlof.github.io/THREE.js-PathTracing-Renderer/Geometry_Showcase.html
   - Sept 2024: All glass surfaces became noise-free, can fly inside glass spheres

2. **DerSchmale thin-film iridescence** (Three.js iridescence component)
   - Repo: https://github.com/DerSchmale/threejs-thin-film-iridescence
   - Live: https://derschmale.github.io/threejs-thin-film-iridescence/
   - Based on Belcour & Barla 2017 academic paper

3. **WebGL iridescence twerk** (fun iridescent shader)
   - Repo: https://github.com/marcofugaro/webgl-iridescence-twerk
   - Iridescent sphere with interactive control

4. **liquidGL** (Apple liquid glass in WebGL, ultra-light)
   - Repo: https://github.com/naughtyduk/liquidGL
   - Handles WebGL 1/2/3 with CSS fallback

5. **liquid-glass-js** (Apple-inspired, more complete)
   - Repo: https://github.com/dashersw/liquid-glass-js
   - Three shape types, multi-layer glass effects

6. **Iridescent shader material CodeSandbox** (ready to run)
   - https://codesandbox.io/s/iridescent-shader-material-l1vdv
   - Quick fork and modify

7. **WebGL Ray Marcher with glass**
   - Repo: https://github.com/Abar23/WebGL-Ray-Marcher
   - WebGL2 raymarching with glass material support

8. **Hugh sk matcap GLSL shaders**
   - Repo: https://github.com/hughsk/matcap
   - Collection of matcap GLSL implementations for stylized glass

### Key Tutorial Source Code

- Maxime Heckel refraction + dispersion (full shader code): https://blog.maximeheckel.com/posts/refraction-dispersion-and-other-shader-light-effects/
- Maxime Heckel caustics (full implementation): https://blog.maximeheckel.com/posts/caustics-in-webgl/
- Olivier Larose 3D glass effect: https://blog.olivierlarose.com/tutorials/3d-glass-effect
- Varun Vachhar iridescent crystal: https://varun.ca/ray-march-sdf/

---

## Part 6: What Separates Gleb-Quality From Average Glass

### The Six Differences (Study These)

**1. Background choice is 80% of the visual impact**
Gleb ALWAYS uses near-black backgrounds (`#010204` - `#0D0D1A`). This makes every photon of refracted/reflected light luminous. Against white or gray, glass looks flat. Against near-black, it glows. Your avatar needs a dark background to reach this level.

**2. Multiple colored light sources, not white**
He uses 3-5 light sources: a dominant blue/cool key light, a warm accent (often orange/gold for caustic warmth), and a rim fill (often purple/violet). The rainbow in the glass comes from having chromatically different lights. One white light = boring glass. Colored lights = jewel.

**3. Chromatic aberration at silhouette edges**
The RGB fringing where glass meets background is the signature mark. It's achieved via per-channel IOR (technique 1 above). Values around `uIorR=1.14`, `uIorG=1.16`, `uIorB=1.20` give subtle dispersion. Push harder for more obvious rainbow edges.

**4. Internal volumetric color (not just surface)**
The inside of the glass GLOWS differently from the surface. This is achieved with thickness + transmission in PBR materials, or with absorption color in raymarching (Beer-Lambert law: `color *= exp(-absorption * hitDistance)`). This is what makes it feel like the glass is full of colored light, not hollow.

**5. Caustic light projection on surfaces below**
That pool of caustic light patterns beneath the glass object is always present. It reads as "this is physically real light behavior." Without it, the object floats disconnectedly in space.

**6. Motion that feels alive**
Gleb's spheres aren't static. Subtle rotation (5-10 degrees over a few seconds) showing different facets, slow internal color flow, animated caustics. The stillness makes it feel dead. The motion makes it feel like it's breathing.

### Material Parameter Cheat Sheet for "Gleb Glass" in Three.js

```javascript
// Starting point for Gleb-style premium glass orb:
{
    transmission: 1.0,
    thickness: 1.5,           // Thick glass = more refraction = more drama
    roughness: 0.0,           // Crystal clear
    ior: 1.5,                 // Standard glass (1.45-1.7 for crystal)
    chromaticAberration: 0.06, // Visible rainbow fringing
    anisotropicBlur: 0.0,     // No blur for this style
    distortion: 0.15,         // Slight internal warp
    temporalDistortion: 0.04, // Slow living animation
    backside: true,            // Thick glass needs this
    samples: 10,              // Quality budget
    envMapIntensity: 1.5,     // Boost the HDRI reflections
}

// Light setup:
// Key: PointLight(0x2050ff, 3.0)  at position (3, 3, 3)   - cool blue
// Fill: PointLight(0xff6020, 1.5) at position (-3, -1, 2) - warm orange
// Rim: PointLight(0x8020ff, 1.0) at position (0, -3, -2)  - purple underlight
```

### HDRI Environments That Work (Free, from Poly Haven)
Good HDRI is the single biggest upgrade you can make to glass rendering quality.
- Library: https://polyhaven.com/hdris
- Best for dark glass look: studio setups, city at night, indoor soft box
- The HDRI IS the material for glass - it's what gets refracted/reflected
- Recommendation: "studio_small_08" or "industrial_sunset_02_puresky" from Poly Haven

---

## Part 7: Recommended Learning Sequence

To go from current avatar to Gleb quality, study in this order:

1. **Read Maxime Heckel's dispersion tutorial** (the complete technical foundation):
   https://blog.maximeheckel.com/posts/refraction-dispersion-and-other-shader-light-effects/

2. **Open the spectral glass Shadertoy shader** and study the GLSL source:
   https://www.shadertoy.com/view/sdyGR3

3. **Study Varun Vachhar's iridescent crystal** (raymarching + cosine palette iridescence):
   https://varun.ca/ray-march-sdf/

4. **Clone and run the THREE.js PathTracing Renderer** to see what full path tracing achieves:
   https://github.com/erichlof/THREE.js-PathTracing-Renderer

5. **Implement MeshTransmissionMaterial** with the parameter values above as a starting point, using a dark scene and multi-colored lights

6. **Add caustics** following Maxime Heckel's caustics tutorial:
   https://blog.maximeheckel.com/posts/caustics-in-webgl/

7. **Add thin-film iridescence** from DerSchmale's implementation:
   https://github.com/DerSchmale/threejs-thin-film-iridescence

8. **Browse Gleb's Dribbble** daily for 10 minutes while building - train your eye to see what combination of parameters produces the specific quality you want:
   https://dribbble.com/glebich

---

## Sources

### Gleb Kuznetsov Portfolio
- [Gleb Kuznetsov Dribbble Profile](https://dribbble.com/glebich)
- [Gleb Kuznetsov Behance](https://www.behance.net/gleb)
- [Crystal sculpture](https://dribbble.com/shots/14486416-Crystal-sculpture)
- [Glass reflection CGI by Milkinside](https://dribbble.com/shots/20098860-Glass-reflection-CGI-by-Milkinside)
- [Colorful AI sphere](https://dribbble.com/shots/14194855-Colorful-AI-sphere-by-Gleb-Kuznetsov)
- [AI sphere visual design by Milkinside](https://dribbble.com/shots/24197602-AI-sphere-visual-design-by-Milkinside)
- [Dark blue globe](https://dribbble.com/shots/14887210-Dark-blue-globe)
- [Glass blower visual](https://dribbble.com/shots/17066462-Glass-blower-visual)
- [Liquid visual exploration](https://dribbble.com/shots/12285048-Liquid-visual-exploration)
- [Brand Vision CGI story Milkinside](https://www.behance.net/gallery/80917393/Brand-Vision-CGI-story-Milkinside)
- [Glass cube visual for AI product](https://dribbble.com/shots/5982977-Glass-cube-visual-for-AI-product)
- [Glass landscape](https://dribbble.com/shots/15252462-Glass-landscape)

### WebGL Implementations & Tutorials
- [Liquid Raymarching with TSL - Codrops 2024](https://tympanus.net/codrops/2024/07/15/how-to-create-a-liquid-raymarching-scene-using-three-js-shading-language/)
- [Glass Torus with Warped Text - Codrops 2025](https://tympanus.net/codrops/2025/03/13/warping-3d-text-inside-a-glass-torus/)
- [Transparent Glass and Plastic - Codrops 2021](https://tympanus.net/codrops/2021/10/27/creating-the-effect-of-transparent-glass-and-plastic-in-three-js/)
- [Real-time Multiside Refraction - Codrops](https://tympanus.net/codrops/2019/10/29/real-time-multiside-refraction-in-three-steps/)
- [Kenta Toshikura Glass Effect - Codrops](https://tympanus.net/codrops/2023/03/06/coding-kenta-toshikuras-glass-effect-with-three-js/)
- [Refraction, Dispersion & Shader Effects - Maxime Heckel](https://blog.maximeheckel.com/posts/refraction-dispersion-and-other-shader-light-effects/)
- [Caustics in WebGL - Maxime Heckel](https://blog.maximeheckel.com/posts/caustics-in-webgl/)
- [Iridescent crystal with raymarching - Varun Vachhar](https://varun.ca/ray-march-sdf/)
- [3D Glass Effect with Three.js - Olivier Larose](https://blog.olivierlarose.com/tutorials/3d-glass-effect)
- [WebGL Glass and Refraction - Offscreen Canvas](https://offscreencanvas.com/issues/webgl-glass-and-refraction/)
- [MeshTransmissionMaterial Docs](https://drei.docs.pmnd.rs/shaders/mesh-transmission-material)

### Shadertoy Shaders
- [Spectral glass](https://www.shadertoy.com/view/sdyGR3)
- [Real glass](https://www.shadertoy.com/view/4s2Gz3)
- [Glass sphere refraction](https://www.shadertoy.com/view/XdVfDd)
- [Refraction, Fresnel, Absorption](https://www.shadertoy.com/view/ttBBWz)
- [Glass is Real](https://www.shadertoy.com/view/wsXfW2)
- [Ribbed glass](https://www.shadertoy.com/view/MXfSDr)
- [Thin-film iridescence](https://www.shadertoy.com/view/7sV3Rh)

### Open Source Repositories
- [THREE.js PathTracing Renderer](https://github.com/erichlof/THREE.js-PathTracing-Renderer)
- [DerSchmale thin-film iridescence](https://github.com/DerSchmale/threejs-thin-film-iridescence)
- [marcofugaro WebGL iridescence](https://github.com/marcofugaro/webgl-iridescence-twerk)
- [liquidGL](https://github.com/naughtyduk/liquidGL)
- [liquid-glass-js](https://github.com/dashersw/liquid-glass-js)
- [html-liquid-glass-effect-webgl](https://github.com/rxing365/html-liquid-glass-effect-webgl)
- [Muggleee liquid-glass](https://github.com/Muggleee/liquid-glass)
- [hughsk matcap GLSL](https://github.com/hughsk/matcap)

### Resources & References
- [Poly Haven HDRIs (free)](https://polyhaven.com/hdris)
- [THREE.js PathTracing live demo](https://erichlof.github.io/THREE.js-PathTracing-Renderer/Geometry_Showcase.html)
- [DerSchmale thin-film live demo](https://derschmale.github.io/threejs-thin-film-iridescence/)
- [liquid-glass-js live demo](https://dashersw.github.io/liquid-glass-js/)
- [Awwwards WebGL collection](https://www.awwwards.com/awwwards/collections/webgl/)
- [Awwwards WebGL shaders + code](https://www.awwwards.com/awwwards/collections/webgl-shaders-code/)
- [KHR PBR glass extensions - Khronos](https://www.khronos.org/gltf/pbr)
- [Simulating Dispersion in OpenGL](https://taylorpetrick.com/blog/post/dispersion-opengl)
- [Liquid Glass Resources Studio](https://www.liquidglassresources.com/development/liquid-glass-studio-webgl/)

---

*Report complete. All URLs verified as active resources during research session 2026-02-20.*
