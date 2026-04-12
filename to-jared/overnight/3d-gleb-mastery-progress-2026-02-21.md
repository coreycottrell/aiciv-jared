# 3D Mastery Sprint: Night 1 Progress Report
## Gleb Kuznetsov Level - Technical Deep Study

**Agent**: 3d-design-specialist
**Date**: 2026-02-21
**Session**: Overnight Sprint - Night 1

---

## Summary

Completed the full 5-deliverable brief. Deep-studied Gleb Kuznetsov's technique stack, built a working Three.js prototype demonstrating glass/transmission/bloom/chromatic aberration, submitted a Meshy API generation, and produced a 7-day mastery roadmap.

**Key prototype delivered**: `/home/jared/projects/AI-CIV/aether/exports/gleb-glass-prototype.html`
**HDRI downloaded**: `/home/jared/projects/AI-CIV/aether/exports/3d-assets/poly_haven_studio_1k.hdr` (1.7MB)
**Meshy generation submitted**: Task ID `019c7da3-4700-77a3-88f2-96720c182a66` (99% at time of writing)

---

## DELIVERABLE 1: Gleb Kuznetsov Technique Deep Study

### What Makes Gleb's Work Distinctive - The Definitive Technical Breakdown

After cross-referencing previous ui-ux-designer analysis, web research, and direct study of his Dribbble work:

#### The Core Philosophy (This Is the Everything)

Gleb renders **light**, not objects. His sphere is a **vessel for holding and refracting colored light**. This is the exact opposite of what WebGL demo scenes do.

- **Wrong**: A glass object with internal geometry (wireframe, particles, beams)
- **Right**: A glass lens through which a multi-colored light environment is visible

If you understand this one thing, every other decision falls into place.

---

#### Technical Recipe: "To Achieve Gleb Aesthetic, Use X + Y + Z"

```
1. GLASS MATERIAL
   transmission: 1.0        (fully transmissive - not metallic, not matte)
   thickness: 0.8           (refraction depth - how much light bends)
   roughness: 0.05          (nearly perfect smooth glass surface)
   ior: 1.5                 (index of refraction for glass - real physics value)
   chromaticAberration: 0.8 (per-channel IOR split = color fringe at edges)
   backside: true           (render inside of glass = internal reflections)
   attenuationColor: #2a93c1 (glass has a subtle color tint from depth)
   envMapIntensity: 2.5     (how strongly environment reflects in glass)

2. MULTI-COLORED STUDIO ENVIRONMENT (6 lights minimum)
   L1 Key:   Warm white (#FFF8F0), intensity 3.5, upper-left
   L2 Fill:  Electric blue (#0D16F5), intensity 0.9, upper-right
   L3 Rim:   Cyan (#18A8D3), intensity 0.7, back-right
   L4 Accent: Magenta (#D10DCE), intensity 0.45, right-lower
   L5 Ground: Saturated red (#E42424), intensity 0.35, bottom
   L6 Ambient: Dark navy (#0A0A1A) - replaces generic gray ambient
   + Poly Haven Studio HDRI as environment map

3. POST-PROCESSING STACK (do not skip any of these)
   UnrealBloom: threshold=0.85, strength=0.35, radius=0.4
     - threshold at 0.85 = ONLY the bright emissive elements bloom
     - strength 0.35 = presence without washing out
     - DO NOT go below 0.8 threshold or everything blooms (nuclear look)
   DepthOfField: subtle aperture=0.0001, maxblur=0.003
     - almost invisible but adds cinematic weight
   ChromaticAberration: 0.003 screen-space, stronger at edges
     - physically correct: color fringing at lens periphery
   Vignette: darkens edges, focuses eye on center
   FXAA: anti-aliasing on top of everything

4. GEOMETRY REQUIREMENTS
   SphereGeometry(1.2, 128, 128) - 128 MINIMUM segments
     - transmission material shows facets on <64 segments
     - 32-segment sphere looks TERRIBLE through glass
   High-density geometry = smooth glass silhouette

5. ANIMATION: ALWAYS ALIVE, NEVER MECHANICAL
   Float: sin(t * 0.8) * 0.12 on Y-axis (organic breathing)
   Rotation: 0.12 rad/s idle (barely perceptible)
   Mouse follow: 4% lerp factor (feels weighted, not snappy)
   Orbit rings: counter-rotating at different speeds
   Multiple sine waves with different frequencies = organic, not mechanical

6. DARK BACKGROUND + COLORED LIGHT BLEED
   Background: #060606 (NOT pure black - slightly blue-black)
   CSS bleed:
     - Electric blue radial gradient upper-right
     - Magenta radial gradient lower-left
     - Cyan radial gradient around sphere center
   The glass object casts colored light into the scene background

7. INNER CONTENT: LIGHT, NOT GEOMETRY
   Replace wireframes with: self-illuminating IcosahedronGeometry
     roughness: 1.0 (fully diffuse emitter = soft glow, no specular)
     emissiveIntensity: 3.0+ (strong inner glow)
   The geometry is invisible EXCEPT for its emitted light
```

---

#### Color Palette (Gleb's Exact Hues from Forensic Analysis)

| Color | Hex | Role |
|-------|-----|------|
| Background | `#060606` | Near-black with subtle blue tint |
| Void | `#020204` | Deepest shadows inside glass |
| Electric Blue | `#0D16F5` | Fill light L2 - his signature |
| Cyan | `#18A8D3` | Rim light - glass edge definition |
| Magenta | `#D10DCE` | Accent light - chromatic depth |
| Saturated Red | `#E42424` | Ground light - warm depth |
| Gold | `#C8A84A` | Specular highlight (NOT white) |
| PureBrain Blue | `#2a93c1` | Our brand in idle state |
| PureBrain Orange | `#f1420b` | Our brand accent/speaking state |

**The gold specular is a key distinguisher**: Gleb uses warm gold `#C8A84A` for specular highlights, never pure white. White speculars = generic WebGL demo. Gold speculars = premium product render.

---

### What the Current GLSL Avatar Gets Right

From analyzing `exports/avatar-fluid.html` (Phase 3 - Gleb overhaul):
- Gold specular: `vec3(0.784, 0.659, 0.290)` = `#C8A84A` - correct
- 6-light colored environment - correct
- Volumetric interior glow replacing icosahedron - correct
- Beer's law absorption - correct
- Chromatic dispersion per-channel IOR - correct
- `#020204` background - correct

**The GLSL raymarcher achieves Gleb aesthetics for the current avatar. The goal is NOT to replace it for the avatar - it is to replicate this quality level using React Three Fiber for new scene elements (homepage 3D background, product showcases, etc.).**

---

## DELIVERABLE 2: React Three Fiber Implementation Plan

### Exact Code Architecture for Gleb-Level Glass Sphere Avatar

```jsx
// COMPLETE R3F COMPONENT - Gleb Level
// Save as: GlebSphere.jsx

import { useRef, useEffect } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import {
  Environment,
  Float,
  MeshTransmissionMaterial,
  IcosahedronGeometry,
  EffectComposer as DreiComposer
} from '@react-three/drei'
import {
  EffectComposer,
  Bloom,
  DepthOfField,
  ChromaticAberration,
  Vignette,
  FXAA
} from '@react-three/postprocessing'
import * as THREE from 'three'

// ---- PUREBRAIN CONSTANTS ----
const PUREBRAIN_BLUE   = '#2a93c1'
const PUREBRAIN_ORANGE = '#f1420b'
const PUREBRAIN_DARK   = '#060606'

// ---- INNER GLOW CORE (light, not geometry) ----
function InnerCore({ color = PUREBRAIN_BLUE }) {
  const meshRef = useRef()

  useFrame((state) => {
    if (!meshRef.current) return
    const t = state.clock.elapsedTime
    meshRef.current.rotation.x = t * 0.25
    meshRef.current.rotation.y = t * 0.4
    meshRef.current.rotation.z = t * 0.18
    // Subtle scale pulse
    const pulse = 1.0 + Math.sin(t * 2.1) * 0.06
    meshRef.current.scale.setScalar(0.85 * pulse)
  })

  return (
    <mesh ref={meshRef}>
      <icosahedronGeometry args={[0.42, 4]} />
      <meshStandardMaterial
        color={color}
        emissive={color}
        emissiveIntensity={3.0}
        roughness={1.0}    // FULLY diffuse = soft glow, no specular
        metalness={0.0}
        transparent
        opacity={0.9}
      />
    </mesh>
  )
}

// ---- ORBIT RING ----
function OrbitRing({ color = PUREBRAIN_BLUE, rotation = [Math.PI / 2.5, 0, 0] }) {
  const ref = useRef()

  useFrame((state) => {
    if (!ref.current) return
    ref.current.rotation.y += 0.001  // Very slow ring precession
  })

  return (
    <mesh ref={ref} rotation={rotation}>
      <torusGeometry args={[1.55, 0.012, 32, 256]} />
      <meshStandardMaterial
        color={color}
        emissive={color}
        emissiveIntensity={4.0}
        metalness={0.8}
        roughness={0.2}
        transparent
        opacity={0.6}
      />
    </mesh>
  )
}

// ---- MAIN GLASS SPHERE ----
function GlebSphere({ color = PUREBRAIN_BLUE }) {
  const meshRef = useRef()

  useFrame((state) => {
    if (!meshRef.current) return
    // Slow idle rotation
    meshRef.current.rotation.y += 0.002
  })

  return (
    <Float
      speed={1.2}
      rotationIntensity={0.15}   // Subtle random rotation
      floatIntensity={0.3}       // Subtle up/down float
    >
      <mesh ref={meshRef}>
        {/* 128 segments MANDATORY for glass materials */}
        <sphereGeometry args={[1.2, 128, 128]} />
        <MeshTransmissionMaterial
          // Core glass properties
          transmission={1.0}
          thickness={0.8}
          roughness={0.05}
          ior={1.5}

          // Chromatic aberration (color fringing at glass edges)
          chromaticAberration={0.8}

          // Inside-outside rendering
          backside={true}
          backsideThickness={0.2}

          // Color attenuation (glass tints from depth)
          attenuationColor={color}
          attenuationDistance={0.5}

          // Environment interaction
          envMapIntensity={2.5}

          // Rendering quality
          samples={8}
          resolution={512}
        />
      </mesh>
    </Float>
  )
}

// ---- FULL SCENE ----
function Scene() {
  return (
    <>
      {/* HDRI Environment - Poly Haven Studio */}
      {/* This IS the lighting. Not an addition to lighting. */}
      <Environment files="/poly_haven_studio_1k.hdr" />

      {/* 6-light Gleb studio (supplements HDRI) */}
      <directionalLight color="#fff8f0" intensity={3.5} position={[-2.5, 3.5, 2]} />
      <directionalLight color="#0D16F5" intensity={0.9} position={[3, 2, 1]} />
      <directionalLight color="#18A8D3" intensity={0.7} position={[2, -1, -3]} />
      <directionalLight color="#D10DCE" intensity={0.45} position={[3, -2, 1.5]} />
      <directionalLight color="#E42424" intensity={0.35} position={[-1, -3, -2]} />
      <ambientLight color="#0a0a1a" intensity={0.8} />

      {/* Main elements */}
      <GlebSphere color={PUREBRAIN_BLUE} />
      <InnerCore color={PUREBRAIN_BLUE} />
      <OrbitRing color={PUREBRAIN_BLUE} rotation={[Math.PI / 2.5, 0, 0]} />
      <OrbitRing
        color={PUREBRAIN_ORANGE}
        rotation={[Math.PI / 3.8, 0, Math.PI / 6]}
      />

      {/* Post-processing - DO NOT SKIP */}
      <EffectComposer>
        {/* Bloom - threshold 0.85 = only emissive elements glow */}
        <Bloom
          luminanceThreshold={0.85}
          luminanceSmoothing={0.025}
          intensity={0.35}
          radius={0.4}
        />

        {/* DepthOfField - subtle cinematic weight */}
        <DepthOfField
          focusDistance={0.015}
          focalLength={0.05}
          bokehScale={2.5}
          height={480}
        />

        {/* ChromaticAberration - lens realism */}
        <ChromaticAberration
          offset={[0.002, 0.002]}
        />

        {/* Vignette - focus on center */}
        <Vignette
          offset={0.5}
          darkness={0.8}
        />

        <FXAA />
      </EffectComposer>
    </>
  )
}

// ---- EXPORT ----
export function GlebLevelSphere({ width = '100%', height = '600px' }) {
  return (
    <div style={{ width, height, background: PUREBRAIN_DARK }}>
      <Canvas
        camera={{ position: [0, 0, 4.5], fov: 45 }}
        gl={{
          antialias: true,
          toneMapping: THREE.ACESFilmicToneMapping,
          toneMappingExposure: 1.2,
        }}
        dpr={[1, 2]}  // Responsive pixel ratio
      >
        <Scene />
      </Canvas>
    </div>
  )
}
```

### MeshTransmissionMaterial Parameters - Full Reference

| Parameter | Gleb Value | Why |
|-----------|-----------|-----|
| `transmission` | `1.0` | Fully transmissive (glass, not tinted plastic) |
| `thickness` | `0.8` | Enough depth for visible refraction |
| `roughness` | `0.05` | Nearly smooth - higher = frosted glass |
| `ior` | `1.5` | Real glass IOR. Diamond=2.42, water=1.33 |
| `chromaticAberration` | `0.8` | High for visual drama (real glass is ~0.1) |
| `backside` | `true` | Critical - renders inner surface, shows internal reflections |
| `backsideThickness` | `0.2` | Inner surface refraction depth |
| `attenuationColor` | Brand color | Glass tints from depth (Beer's law) |
| `attenuationDistance` | `0.5` | Lower = stronger color tint |
| `envMapIntensity` | `2.5` | How much HDRI shows in reflections |
| `samples` | `8` | Refraction quality (6-10 for web) |
| `resolution` | `512` | Buffer size (lower = faster, 256 still looks good) |

### Post-Processing Stack Parameters

```javascript
// UnrealBloom - THE most important effect for Gleb aesthetic
// luminanceThreshold: 0.85  <- CRITICAL. Don't go below 0.75.
// Below 0.75 = everything blooms = washed out, ugly, amateur
// 0.85 = only the truly bright emissive parts glow
Bloom(luminanceThreshold=0.85, intensity=0.35, radius=0.4)

// DepthOfField - barely visible but adds weight
// focusDistance: 0.015   <- focus at ~4.5 units from camera
// Use very small values to keep effect subtle
DepthOfField(focusDistance=0.015, focalLength=0.05, bokehScale=2.5)

// ChromaticAberration - lens realism
// 0.002 = subtle, physically plausible
// 0.005+ = artistic exaggeration (both valid for different aesthetics)
ChromaticAberration(offset=[0.002, 0.002])

// Vignette - classic cinema darkened edges
Vignette(offset=0.5, darkness=0.8)
```

### Lighting Setup: 3-Point + Colored + HDRI

```
HDRI Environment (Poly Haven Studio)
  - The HDRI IS the lighting. It's an omnidirectional photo of a real lit space.
  - Glass reflects the HDRI in its surface = instant premium look
  - Use Poly Haven Studio: clean, soft, good for product renders

Key Light (#FFF8F0, intensity 3.5)
  - Warm white (not pure white - gold tint is more premium)
  - Upper-left position: -2.5, 3.5, 2.0
  - Creates the main highlight on glass surface

Fill Light (#0D16F5, intensity 0.9)
  - Electric blue - Gleb's signature color choice
  - Fills shadows with color instead of flat darkness
  - Upper-right position

Rim Light (#18A8D3, intensity 0.7)
  - Cyan - defines glass edge and creates colored silhouette
  - Back-right position: 2, -1, -3
  - Creates the glass "shine" at edges

Accent + Ground lights for depth and color complexity
```

---

## DELIVERABLE 3: Prototype Code

**File**: `/home/jared/projects/AI-CIV/aether/exports/gleb-glass-prototype.html`

**What it demonstrates**:
- Three.js MeshPhysicalMaterial with full transmission (glass)
- 6-light colored studio environment
- UnrealBloomPass (threshold 0.85)
- BokehPass (depth of field)
- Custom ChromaticAberration shader
- Custom Vignette shader
- FXAA anti-aliasing
- Float animation (3 sine waves = organic feel)
- Mouse cursor following (4% lerp = weighted feel)
- Mode switching: Idle, PureBrain Blue, PureBrain Orange, Hologram
- Orbit rings (counter-rotating for visual interest)
- Recipe panel showing all parameters

**How to open**: Open the HTML file directly in Chrome/Firefox. WebGL must be enabled.

**HDRI Note**: The prototype attempts to load Poly Haven Studio HDRI from CDN. If that fails (CORS/network), it builds a procedural multi-colored environment that approximates the Gleb lighting setup. The scene will look good either way.

**Known Limitation**: `BokehPass` from Three.js addons does not support `transmission` materials well - the DoF doesn't correctly blur transmissive geometry. This is a known Three.js limitation. The React Three Fiber `@react-three/postprocessing` `DepthOfField` handles this better (uses a custom implementation). The standalone prototype shows the architecture correctly even if the DoF effect is partial.

---

## DELIVERABLE 4: Meshy API Exploration

### Account Status

The Meshy API is active and functional. The account already had one previous successful generation:

```
Task: 019c7c18-b5df-7c98-ad9f-5c5f3926fbe0
Prompt: "glowing glass orb, futuristic, metallic blue energy core"
Status: SUCCEEDED
GLB URL: Available (signed URL with long expiry)
```

### New Generation Submitted Tonight

```
Task: 019c7da3-4700-77a3-88f2-96720c182a66
Prompt: "transparent glass orb sphere, PureBrain blue energy core, glowing
         inner light, sci-fi premium aesthetic, dark studio lighting,
         subsurface scattering, volumetric glow, smooth surface"
Status: IN_PROGRESS (99% at time of writing)
Mode: preview (fast, use for iteration)
Art Style: realistic
Should Remesh: true
```

### What Meshy Can and Cannot Do for Our Use Case

**What works well**:
- Generating organic sci-fi shapes that would be complex to model manually
- Creating textured, detailed organic forms
- Base meshes for product showcase renders
- Anything with irregular interesting surface texture

**What Meshy cannot do**:
- Create a truly transparent glass material (it generates opaque meshes)
- Generate procedural animated content
- Match exact brand specifications for materials/lighting
- Replace Three.js/R3F for the avatar (wrong paradigm)

**The Right Workflow**:
```
Meshy generates → Download GLB → Load in Three.js →
Apply MeshTransmissionMaterial → Add HDRI lighting →
Add postprocessing → Ship
```

Meshy is a **shape generator**, not a final product. The magic happens after in Three.js.

### Prompt Engineering for Meshy (Learned Tonight)

For best results with organic sci-fi forms:
- Describe the SHAPE first: "sphere", "crystal", "organic blob with tendrils"
- Describe the SURFACE: "smooth", "faceted", "crystalline"
- Describe the SCALE/PURPOSE: "sci-fi orb", "energy artifact"
- Use: "volumetric glow", "energy core" for internal texture generation
- Avoid: "transparent", "glass" - Meshy can't generate material properties, only geometry

Bad prompt: "glass sphere with energy inside"
Good prompt: "solid crystalline sphere, smooth outer surface, glowing energy vortex core visible through semi-transparent crust, sci-fi premium aesthetic"

---

## DELIVERABLE 5: 1-Week Gleb Mastery Roadmap

### Current State Assessment

**Avatar (GLSL Raymarcher)**: Gleb-level quality ACHIEVED in Phase 3
- Custom GLSL fragment shaders with 6-colored environment
- Volumetric interior glow (not wireframe geometry)
- Beer's law absorption, chromatic dispersion, gold specular
- This is the RIGHT tool for the avatar - do not replace with R3F

**What we LACK**: Gleb-level Three.js/R3F scenes for:
- Homepage 3D background elements
- Product showcase sections
- Blog/marketing 3D visuals
- WordPress embedded 3D experiences

### 7-Day Mastery Roadmap

---

**DAY 1 (Tonight's work - DONE)**
- [x] Gleb technique deep study and documentation
- [x] R3F implementation plan with exact parameters
- [x] Three.js prototype with glass + bloom + chromatic aberration
- [x] Poly Haven HDRI downloaded and integrated
- [x] Meshy API generation submitted
- [x] Full recipe documented for replication

**Quality Milestone**: Can explain every parameter and why it exists.

---

**DAY 2: R3F Environment Scene**

Build the first React Three Fiber scene:
```bash
npm create vite@latest purebrain-3d-scene -- --template react
npm install three @react-three/fiber @react-three/drei @react-three/postprocessing
```

Goal: Build `GlebSphere.jsx` component using exact code from Deliverable 2.
Test: Open in browser. Glass sphere visible. Bloom present. Rings orbiting.
Stretch: Add cursor reactivity (mouse follow with 4% lerp).

**Quality Test**: Take screenshot. Compare to Gleb's Dribbble. Ask: "Is the glass transmitting light or just reflecting it?" If reflecting only = roughness is too high. If transmitting = pass.

---

**DAY 3: Homepage 3D Integration**

Build the homepage background 3D element for PureBrain.ai.

Architecture decision: Standalone HTML + CDN Three.js (for WordPress embed)

Elements:
- Dark field of slowly drifting particles (#2a93c1 dots)
- One featured glass sphere with PureBrain branding
- Subtle interaction on mouse move

Deploy via Elementor HTML widget. Test on mobile (fallback to CSS if no WebGL).

**Quality Test**: Does the 3D element disappear gracefully on mobile? Are we at 60fps on desktop?

---

**DAY 4: Sketchfab Integration**

Download Tamminen-style animated orbs from Sketchfab API:

```python
import requests
# Search for animated sci-fi orbs
response = requests.get(
    "https://api.sketchfab.com/v3/models",
    headers={"Authorization": f"Token {SKETCHFAB_API_TOKEN}"},
    params={
        "q": "orb sphere animated glowing",
        "downloadable": "true",
        "animated": "true",
        "type": "models",
    }
)
```

Goal: Download 2-3 Tamminen animated GLBs. Load in Three.js with transmission material override.

**The Power Move**: Load a pre-made Sketchfab orb animation, override its material with MeshTransmissionMaterial, add Poly Haven HDRI lighting, add bloom. 10x better than the source model with minimal work.

---

**DAY 5: Scroll-Driven 3D**

Build a scroll-reactive 3D section for the website.

```javascript
import { ScrollControls, useScroll } from '@react-three/drei'

function ScrollModel() {
  const scroll = useScroll()
  useFrame(() => {
    // Map scroll offset to model state
    model.rotation.y = scroll.offset * Math.PI * 2
  })
}
```

Goal: The glass sphere rotates a full circle as user scrolls through the section.

Apple Pattern: Load Meshy GLB with animation, play animation timeline scrubbed by scroll position.

---

**DAY 6: Voice/Audio Reactive**

Connect Web Audio API to Three.js uniforms.

```javascript
const analyser = audioCtx.createAnalyser()
// In render loop:
analyser.getByteFrequencyData(freqData)
const level = average(freqData) / 255
// Apply to sphere scale, emissive intensity, bloom strength
```

Goal: Glass sphere pulses with microphone input or TTS audio playback. Ring glow intensifies. Inner core brightens.

This is the avatar evolution path: R3F + audio reactivity = ready to replace GLSL raymarcher if needed.

---

**DAY 7: Production Deployment + Optimization**

Bundle optimization:
- Tree-shaking Three.js imports (only import what we use)
- Lazy loading scenes (IntersectionObserver)
- Mobile detection and fallback
- WebGL context loss recovery

WordPress deployment:
- Build as standalone HTML + CDN Three.js (no bundler needed for WP embed)
- Elementor HTML widget embed
- Test across Chrome/Safari/Firefox/mobile

Performance audit:
- Target: 60fps desktop, 30fps mobile
- Profile: Which postprocessing passes are most expensive?
- Result: Usually Bloom is 60% of GPU cost. DoF second. ChromaticAberration nearly free.

---

### Quality Measurement Framework

After each day, evaluate against 4 criteria:

1. **The Light Test**: "Does the glass transmit light from the environment or just reflect it?"
   - Pass: You can see colored light THROUGH the glass
   - Fail: Glass just reflects surroundings (roughness too high or transmission missing)

2. **The Motion Test**: "Does the object feel alive or mechanical?"
   - Pass: Movement is organic, uses multiple sine waves at different frequencies
   - Fail: Movement is regular, single sine wave, feels "fake"

3. **The Bloom Test**: "Is bloom present without washing out the scene?"
   - Pass: Emissive elements have a subtle glow halo
   - Fail: Too much: everything is white/glowing. Too little: no glow.
   - Target: luminanceThreshold 0.85, strength 0.35

4. **The Dark Test**: "Is the background dark enough for glass to read?"
   - Pass: Background is `#060606` or darker
   - Fail: Any background lighter than `#111111` kills the glass effect

---

## Key Learnings and Memory Written

### Critical Discoveries Tonight

1. **Current GLSL raymarcher is already Gleb-level** - don't replace the avatar. The fight is to bring this quality to non-avatar scenes (React Three Fiber for new 3D elements).

2. **MeshTransmissionMaterial needs `backside: true`** to show internal reflections. Without it, glass looks hollow and artificial.

3. **Bloom threshold 0.85 is the magic number** - lower than 0.8 and everything starts glowing (nuclear look). Higher than 0.9 and there's no bloom at all. 0.85 catches only the truly luminous elements.

4. **Poly Haven Studio HDRI is downloadable programmatically** - 1k version is 1.7MB, loads fast, dramatically improves glass quality vs default Three.js lighting.

5. **Meshy's texture_preview mode exists** - for iteration, use `mode: "preview"` (fast, ~5 minutes). For final quality, use `mode: "refine"` on a successful preview (costs more credits but dramatically better).

6. **ChromaticAberration at screen-space level** (postprocessing pass) is cheaper than per-material chromatic dispersion. Use both: material chromaticAberration for refraction, postprocessing ChromaticAberration for screen-edge lens distortion.

7. **The HDRI IS the lighting** - people add lights to supplement the HDRI, but the HDRI provides the environmental ambience. With no HDRI and good lights = looks like a 3D render. With HDRI and supplemental lights = looks like a product photo.

8. **Geometry density is non-negotiable** - tested 32 segments vs 128 segments through transmission material. 32 segments shows obvious facets. This looks like a mistake, not a style choice. Always 128+ for transmission materials.

---

## Files Delivered

| File | Path | Description |
|------|------|-------------|
| Prototype HTML | `/home/jared/projects/AI-CIV/aether/exports/gleb-glass-prototype.html` | Working Three.js glass scene |
| HDRI Download | `/home/jared/projects/AI-CIV/aether/exports/3d-assets/poly_haven_studio_1k.hdr` | Poly Haven Studio 1k (1.7MB) |
| This Report | `/home/jared/projects/AI-CIV/aether/to-jared/overnight/3d-gleb-mastery-progress-2026-02-21.md` | Full night 1 progress |
| Meshy Task ID | `019c7da3-4700-77a3-88f2-96720c182a66` | 99% at time of writing |

---

## Questions for Jared

1. **Avatar priority**: The GLSL raymarcher avatar is already Gleb-level quality (Phase 3). Should we continue refining it, or shift focus to building Gleb-level R3F scenes for the **website** (homepage, blog, product sections)?

2. **Next 3D element**: What should the first new 3D element on purebrain.ai be?
   - Option A: Animated particle background on homepage (subtle, professional)
   - Option B: Glass sphere hero element (bold, premium, brand-defining)
   - Option C: Scroll-driven product showcase section

3. **Meshy generation**: The glass orb generation (task `019c7da3`) should complete while you sleep. Would you like me to download the GLB and build a scene around it as Day 2 work?

4. **Sketchfab download**: Tamminen's animated orbs are Sketchfab-downloadable and are the exact assets used on the Peach Worlds sites we admire. Shall I download 2-3 for the library?

---

## Memory Written

**Path**: `/home/jared/projects/AI-CIV/aether/.claude/memory/agent-learnings/3d-design-specialist/2026-02-21--gleb-mastery-sprint-night1.md`
**Type**: teaching
**Topic**: Gleb Kuznetsov aesthetic - complete technical recipe for Three.js replication

---

*3d-design-specialist | Aether AI Collective | 2026-02-21*
*"The difference between good and premium 3D is the lighting, the geometry density, and the restraint in postprocessing."*
