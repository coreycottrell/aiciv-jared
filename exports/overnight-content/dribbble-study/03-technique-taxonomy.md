# Technique Taxonomy: All Visual Techniques from 35 Dribbble References
**Agent**: 3d-design-specialist
**Date**: 2026-02-23
**Purpose**: Categorized library of techniques observed across Milkinside/Gleb work

---

## Overview: The Technique Stack

After studying 35 references across 8+ years of Milkinside/Gleb work, a clear technique stack emerges. Each layer enables the layers above it. The base is geometry; the apex is behavioral design.

```
┌─────────────────────────────────────────┐
│     6. BEHAVIORAL DESIGN (States)       │  ← AI personality expressed through all layers
├─────────────────────────────────────────┤
│     5. INTERACTION RESPONSE             │  ← Voice, cursor, scroll reactivity
├─────────────────────────────────────────┤
│     4. POST-PROCESSING EFFECTS          │  ← Bloom, DoF, ChromaticAberration, Vignette
├─────────────────────────────────────────┤
│     3. ANIMATION SYSTEM                 │  ← Float, rotate, morph, pulse, breath
├─────────────────────────────────────────┤
│     2. LIGHTING & ENVIRONMENT           │  ← HDRI, color lights, caustics, bloom
├─────────────────────────────────────────┤
│     1. GEOMETRY & MATERIALS             │  ← Glass, IOR, transmission, surface
└─────────────────────────────────────────┘
```

---

## Category 1: Glass / Transmission Materials

### 1.1 Clear Glass (Pure Transmission)

**What it is**: The foundational Gleb material. A sphere/object that transmits light through it, refracting the background as it passes.

**Parameters** (C4D Octane terms → Three.js equivalents):
| Octane Parameter | Three.js (MeshTransmissionMaterial) | Value |
|-----------------|-------------------------------------|-------|
| IOR (Index of Refraction) | `ior` | 1.5 (glass), 1.33 (water), 1.77 (crystal) |
| Transmission | `transmission` | 1.0 (fully transparent) |
| Roughness (glass quality) | `roughness` | 0.02-0.08 (premium = very low) |
| Thickness | `thickness` | 0.5-1.5 (affects refraction depth) |
| Specular | `specularColor` | "#C8A84A" (Gleb's gold specular) |
| Chromatic dispersion | `chromaticAberration` | 0.6-0.9 |

**Used in**: Shots 2, 5, 8, 11, 14, 24, 25, 26

**Three.js implementation**:
```jsx
<MeshTransmissionMaterial
  transmission={1}
  thickness={0.8}
  roughness={0.04}
  ior={1.5}
  chromaticAberration={0.8}
  backside={true}
  backsideThickness={0.2}
  samples={8}
  resolution={1024}
  specularColor="#C8A84A"
  color="#88ccff"
/>
```

### 1.2 Tinted Glass

**What it is**: Glass with a color bias in the transmission. Light passing through the glass picks up the tint color while still transmitting the environment behind it.

**Color applications observed**:
- **PureBrain blue** (#2a93c1): Electric, digital, intelligent
- **Deep navy** (#1B2A4A): Enterprise, professional, serious
- **Violet/indigo** (#4B0082): Contemplative, deep, mysterious
- **Warm amber** (#C8A84A): Organic, warm, approachable

**When to use each**:
- Idle state → blue tint
- Thinking state → violet tint
- Response state → warm amber tint
- Enterprise context → deep navy tint

```jsx
// State-responsive glass tint
const stateColors = {
  idle: "#2a93c1",
  thinking: "#7C3AED",
  speaking: "#C8A84A",
  listening: "#00D4FF"
}
<MeshTransmissionMaterial color={stateColors[mode]} />
```

### 1.3 Iridescent Glass

**What it is**: Glass that shifts hue based on viewing angle (thin film interference physics). The Samsung R3 and Cirus sphere use this.

**Physical basis**: Thin film of material (like soap bubbles) creates interference patterns that shift with angle.

**Three.js implementation** (requires custom ShaderMaterial):
```glsl
// Vertex shader
varying vec3 vNormal;
varying vec3 vViewPosition;

void main() {
  vNormal = normalize(normalMatrix * normal);
  vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
  vViewPosition = -mvPosition.xyz;
  gl_Position = projectionMatrix * mvPosition;
}

// Fragment shader - iridescence
varying vec3 vNormal;
varying vec3 vViewPosition;

void main() {
  float cosAngle = dot(normalize(vViewPosition), vNormal);
  // Shift hue based on viewing angle
  float hue = cosAngle * 0.5 + 0.5;
  // Convert hue to RGB (HSL with L=0.5, S=0.8)
  vec3 iridColor = hsl2rgb(vec3(hue, 0.8, 0.5));
  gl_FragColor = vec4(iridColor, 0.9);
}
```

**Used in**: Shots 12 (Cirus), 21 (Infinity sculpture)

### 1.4 Frosted Glass (Rough Transmission)

**What it is**: Glass with roughness > 0.2. Background visible through it but blurred rather than sharp. Creates a soft, diffused look.

**When Gleb uses it**:
- UI chrome elements (panels, cards) - not the hero sphere
- "Reading state" in voice UI (output delivered, waiting for next input)
- Night mode contexts (softer material matches subdued emotional register)

```jsx
<MeshTransmissionMaterial
  transmission={0.9}
  roughness={0.25}
  thickness={0.3}
  color="#ffffff"
/>
```

### 1.5 Dark Glass (Tinted + Reduced Transmission)

**What it is**: Highly tinted glass with transmission reduced to 0.6-0.7. Appears dark but still shows depth and internal movement.

**Used for**: Enterprise contexts, automotive HMI elements, night mode

```jsx
<MeshTransmissionMaterial
  transmission={0.65}
  thickness={1.0}
  roughness={0.05}
  ior={1.5}
  color="#0a1520"  // very dark blue-black
/>
```

---

## Category 2: Particle Systems

### 2.1 Orbital Particles (Sphere Surface Particles)

**What it is**: Points constrained to move on or near a sphere surface, creating the impression of an energy field.

**Used in**: Shots 12 (Cirus rings), 20 (AVA particles), 27 (Generative AI)

**Three.js implementation**:
```javascript
const particleCount = 2000
const positions = new Float32Array(particleCount * 3)
const angles = new Float32Array(particleCount)

for (let i = 0; i < particleCount; i++) {
  // Random point on sphere surface
  const theta = Math.random() * Math.PI * 2
  const phi = Math.acos(Math.random() * 2 - 1)
  const radius = 1.5 + Math.random() * 0.3  // slight radius variation

  positions[i * 3] = radius * Math.sin(phi) * Math.cos(theta)
  positions[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta)
  positions[i * 3 + 2] = radius * Math.cos(phi)
  angles[i] = Math.random() * Math.PI * 2
}

// In useFrame: animate each particle along its orbit
useFrame((state) => {
  const posArray = particleGeom.current.attributes.position.array
  for (let i = 0; i < particleCount; i++) {
    angles[i] += 0.001 * (1 + i * 0.0001)  // vary speed per particle
    // Update position along latitude circle
    posArray[i * 3] = radius * Math.cos(angles[i])
    posArray[i * 3 + 2] = radius * Math.sin(angles[i])
  }
  particleGeom.current.attributes.position.needsUpdate = true
})
```

### 2.2 Internal Particles (Inside Glass)

**What it is**: Particle cloud INSIDE the glass sphere. Visible through transmission material. Creates impression of contained universe or active cognition.

**Used in**: Shot 16 (Universe icon), Shot 1 (Brain icon)

**Critical Three.js note**: Particles inside a transmission sphere WILL be visible if:
1. The sphere uses `backside={true}` (renders inside surface)
2. Particles have additive blending (THREE.AdditiveBlending)
3. Particles are slightly smaller than sphere radius

```jsx
// Particles inside glass sphere
<mesh>
  <sphereGeometry args={[1.2, 128, 128]} />
  <MeshTransmissionMaterial transmission={1} backside={true} />
</mesh>

<points>
  <bufferGeometry>
    <bufferAttribute ... />
  </bufferGeometry>
  <pointsMaterial
    size={0.02}
    color="#ffffff"
    transparent={true}
    opacity={0.6}
    blending={THREE.AdditiveBlending}
    sizeAttenuation={true}
  />
</points>
```

### 2.3 Forming Particles (Particles That Build a Shape)

**What it is**: Particles that start dispersed and converge to form the shape of the geometric object. The reverse is also used: particles that explode from the geometry.

**Used in**: Shot 20 (AVA particles forming), Shot 17 (loader materializing)

**Animation pattern**:
- Frame 0: Particles scattered randomly in a sphere of radius 3x object size
- Frames 0-90: Particles animate toward their final position on the object surface
- Frame 90+: Particles orbit the surface in their converged position

### 2.4 Audio-Reactive Particles

**What it is**: Particle emission rate, velocity, and size modulated by audio amplitude.

**Relationship to audio frequency bands**:
- Bass (20-250Hz): Large particles, slow movement (foundation)
- Midrange (250-4000Hz): Medium particles, medium speed (speech body)
- Treble (4000-20000Hz): Small particles, fast movement (sibilance, sparkle)

**Three.js implementation**:
```javascript
useFrame((state) => {
  const freq = audioAnalyser.getFrequencyData()
  const bass = average(freq.slice(0, 10))
  const mid = average(freq.slice(10, 100))
  const treble = average(freq.slice(100, 256))

  // Scale particle size by frequency band
  particleMat.size = 0.02 + (bass / 255) * 0.08
  particleMat.opacity = 0.3 + (mid / 255) * 0.7
  emissionRate = Math.floor((treble / 255) * 20)
})
```

---

## Category 3: Shape Morphing / Animation

### 3.1 Vertex Displacement (Organic Deformation)

**What it is**: The sphere/object vertices move based on a noise function, creating an organic breathing/pulsing effect. This is how Gleb's spheres look "alive" rather than mechanical.

**The key insight**: Simplex noise (3D) evaluated at each vertex position + time creates coherent, organic deformation.

```glsl
// Vertex shader for organic sphere deformation
uniform float uTime;
uniform float uAmplitude;

float snoise(vec3 v) { /* simplex noise implementation */ }

void main() {
  vec3 pos = position;

  // Evaluate noise at vertex position + time
  float noise = snoise(pos * 1.5 + uTime * 0.3);

  // Displace along normal direction
  vec3 newPos = pos + normal * noise * uAmplitude;

  gl_Position = projectionMatrix * modelViewMatrix * vec4(newPos, 1.0);
}
```

**Used in**: Shot 6 (Voice visual - sphere deforms with audio), Shot 10 (Thinking - internal motion)

**Audio-reactive deformation**:
```javascript
// Amplitude drives deformation
material.uniforms.uAmplitude.value = 0.05 + audioAmplitude * 0.15
```

### 3.2 Float Animation

**What it is**: The object slowly rises and falls in Y position while gently rotating. Creates the impression of weightlessness and life.

**Multiple frequency composition** (organic vs mechanical):
```javascript
// Mechanical (avoid):
y = Math.sin(time) * 0.1  // single frequency = robotic

// Organic (use):
y = Math.sin(time * 0.8) * 0.08 + Math.sin(time * 0.5) * 0.03  // multi-frequency = alive
x = Math.sin(time * 0.6) * 0.03 + Math.sin(time * 1.1) * 0.01
```

**In R3F**: The `<Float>` component from `@react-three/drei` handles this correctly:
```jsx
<Float speed={1.5} rotationIntensity={0.3} floatIntensity={0.4}>
  {/* object */}
</Float>
```

### 3.3 Breath Animation

**What it is**: Very slow scale oscillation (0.2-0.5Hz) making the object appear to inhale and exhale. Foundational to Gleb's "alive" aesthetic.

```javascript
useFrame(({ clock }) => {
  const t = clock.elapsedTime
  // Breath: 0.3Hz (about once every 3 seconds)
  const breath = 1.0 + Math.sin(t * 0.3 * Math.PI * 2) * 0.03
  meshRef.current.scale.setScalar(breath)
})
```

**State-responsive breath rate**:
- Idle: 0.25Hz (slow, resting)
- Thinking: 0.15Hz (very slow, suspended)
- Speaking: 0.5Hz (faster, energized)
- Listening: 0.35Hz (attentive)

### 3.4 State Transition Morphing

**What it is**: Smooth interpolation between distinct geometric states (e.g., sphere to faceted crystal, cube from hex view to face-on).

**Spring physics** (organic transitions):
```javascript
const spring = useSpring({
  rotation: targetRotation,
  scale: targetScale,
  config: {
    mass: 2,        // heavier = more momentum
    tension: 120,   // stiffer spring = faster
    friction: 40    // more friction = less oscillation
  }
})
```

**Easing functions observed in Gleb's work**:
- State entry: ease-out (fast start, settles smoothly)
- State exit: ease-in (gentle start, exits quickly)
- Idle float: ease-in-out (sinusoidal, organic)
- Acknowledgment pulse: spring (physical bounce)

### 3.5 Ring/Orbital Animation

**What it is**: Thin torus geometries orbiting the central sphere/hex at different speeds and inclinations. Creates "planetary system" visual.

**Used in**: Shot 12 (Cirus), Shot 7 (Voice reaction 2024)

```jsx
function OrbitalRings({ active }) {
  return (
    <group>
      {/* Ring 1: equatorial, fast */}
      <mesh rotation={[Math.PI/2, 0, 0]}>
        <torusGeometry args={[1.6, 0.008, 16, 128]} />
        <meshStandardMaterial
          color="#2a93c1"
          emissive="#2a93c1"
          emissiveIntensity={active ? 2.0 : 0.3}
          transparent
          opacity={active ? 0.8 : 0.2}
        />
      </mesh>

      {/* Ring 2: 30-degree inclination, medium */}
      <mesh rotation={[Math.PI/2 + 0.52, 0, 0]}>
        <torusGeometry args={[2.0, 0.005, 16, 128]} />
        <meshStandardMaterial
          color="#ffffff"
          emissive="#ffffff"
          emissiveIntensity={active ? 1.5 : 0.2}
          transparent
          opacity={active ? 0.5 : 0.1}
        />
      </mesh>

      {/* Ring 3: 60-degree inclination, slow */}
      <mesh rotation={[Math.PI/2 + 1.05, 0, 0]}>
        <torusGeometry args={[2.4, 0.004, 16, 128]} />
        <meshStandardMaterial
          color="#f1420b"
          emissive="#f1420b"
          emissiveIntensity={active ? 1.0 : 0.1}
          transparent
          opacity={active ? 0.3 : 0.05}
        />
      </mesh>
    </group>
  )
}

// In useFrame: rotate rings at different speeds
ring1.rotation.z += 0.003   // fast
ring2.rotation.z -= 0.0015  // medium, reverse
ring3.rotation.z += 0.0008  // slow
```

---

## Category 4: Light / Bloom / Glow Effects

### 4.1 The 6-Color Studio Lighting Rig (Gleb Signature)

**What it is**: Multiple colored point/spot lights around the object creating multi-directional color cast. The glass refracts each differently, creating iridescence-like effects without iridescence shader.

**Gleb's signature configuration** (reverse-engineered from sprint):
```jsx
// The 6 lights that create Gleb's aesthetic
<ambientLight intensity={0.1} />

<directionalLight  // Key light (top)
  position={[3, 5, 3]}
  intensity={1.5}
  color="#ffffff"
/>

<pointLight  // Electric blue fill (THE SIGNATURE LIGHT)
  position={[-3, 0, -2]}
  intensity={2.0}
  color="#0D16F5"
/>

<pointLight  // Warm bounce
  position={[2, -2, 1]}
  intensity={0.8}
  color="#C8A84A"
/>

<pointLight  // Cyan rim
  position={[0, 3, -3]}
  intensity={1.2}
  color="#00D4FF"
/>

<spotLight  // Bottom up light (adds depth)
  position={[0, -4, 0]}
  intensity={0.5}
  color="#2a93c1"
  angle={0.5}
  penumbra={0.8}
/>
```

### 4.2 HDRI Environment Lighting

**The most important element**. The HDRI provides:
1. Ambient lighting from all directions
2. Reflections in glass surface
3. Refraction pattern inside glass
4. Background environment

**Poly Haven sources** (free, CC0):
- `studio_small_08`: Neutral studio, warm key, cool fill = Gleb's default
- `abandoned_workshop_02`: Industrial atmosphere = dramatic
- `sunflowers_puresky`: Outdoor warm = organic/natural contexts
- `dancing_hall`: Ballroom lighting = luxury/premium

```jsx
<Environment files="/poly_haven_studio_1k.hdr" background={false} />
```

### 4.3 Bloom (Self-Luminance Suggestion)

**What it is**: Objects bright enough to exceed the camera's dynamic range appear to glow, bleeding light into surrounding pixels.

**The three bloom regimes**:
1. **Nuclear (wrong)**: `luminanceThreshold={0.5}, intensity={2.0}` - everything glows, washed out
2. **Premium (correct)**: `luminanceThreshold={0.85}, intensity={0.4}` - only true emissives glow
3. **Off (also wrong)**: No bloom at all - objects look flat, CGI-obvious

```jsx
<Bloom
  luminanceThreshold={0.88}   // Only above this brightness level
  luminanceSmoothing={0.025}  // Edge softness
  intensity={0.4}             // Glow strength (never above 0.6 for premium)
  mipmapBlur={true}          // Smoother, more natural bloom
/>
```

**State-responsive bloom**:
- Idle: threshold=0.92, intensity=0.3
- Speaking: threshold=0.80, intensity=0.6
- Thinking: threshold=0.88, intensity=0.3

### 4.4 Energy Emission Lines

**What it is**: Thin bright line geometry that appears self-luminous (no material lighting needed). Used for energy fields, charging effects, data flow visualization.

```jsx
<lineSegments>
  <bufferGeometry>
    {/* Line vertex positions */}
    <bufferAttribute ... />
  </bufferGeometry>
  <lineBasicMaterial
    color="#2a93c1"
    linewidth={1}
    // No emission needed - lineBasicMaterial ignores lighting
  />
</lineSegments>
```

For glowing lines (requires EffectComposer bloom):
```jsx
<mesh>
  <tubeGeometry args={[curve, 64, 0.002, 8, false]} />
  <meshStandardMaterial
    color="#2a93c1"
    emissive="#2a93c1"
    emissiveIntensity={3.0}  // This pushes it above bloom threshold
  />
</mesh>
```

### 4.5 Caustics (Approximate)

**What it is**: The colored light patterns that glass casts on surrounding surfaces when light passes through it. The most expensive effect in Gleb's toolkit (87 hours rendering).

**Real-time approximation for Three.js**:
```jsx
// Fake caustics: animated noise texture on floor plane
// Below the hex avatar, a plane with an animated ShaderMaterial
const CausticFloor = () => (
  <mesh rotation={[-Math.PI/2, 0, 0]} position={[0, -1.5, 0]}>
    <planeGeometry args={[6, 6]} />
    <shaderMaterial
      uniforms={{ uTime: { value: 0 } }}
      vertexShader={causticVertexShader}
      fragmentShader={causticFragmentShader}
      transparent={true}
      blending={THREE.AdditiveBlending}
    />
  </mesh>
)
```

---

## Category 5: Reactive Behaviors

### 5.1 Voice Reactivity

**The three voice states Gleb designs for**:
1. **Silence**: Object at idle baseline
2. **Input receiving** (user speaking): Object expands, brightens, particles activate
3. **Processing/output** (AI speaking): Object enters thinking → speaking transition

**Web Audio API implementation**:
```javascript
const analyser = audioContext.createAnalyser()
analyser.fftSize = 2048
analyser.smoothingTimeConstant = 0.8

function getAmplitude() {
  const data = new Uint8Array(analyser.frequencyBinCount)
  analyser.getByteFrequencyData(data)
  return data.reduce((a, b) => a + b) / data.length / 255
}

// In useFrame:
const amplitude = getAmplitude()
sphere.scale.setScalar(1.0 + amplitude * 0.3)
bloomPass.intensity = 0.3 + amplitude * 0.4
```

### 5.2 Cursor/Gaze Reactivity

**The "alive" feeling from cursor tracking**:
- Object rotates to "look" at cursor position
- Closer cursor = more intense tracking
- Lerped (not instant) = organic feel

```javascript
useFrame(({ mouse }) => {
  // Lerp current rotation toward cursor direction
  const targetX = mouse.y * 0.3
  const targetY = mouse.x * 0.3

  mesh.rotation.x += (targetX - mesh.rotation.x) * 0.05  // lerp factor
  mesh.rotation.y += (targetY - mesh.rotation.y) * 0.05
})
```

**State-responsive cursor tracking intensity**:
- Idle: 0.3 (subtle gaze)
- Listening: 1.6 (intensely tracking)
- Thinking: 0.1 (barely aware of cursor)
- Speaking: 0.5 (moderate tracking)

### 5.3 Scroll-Driven Animation

**Gleb's approach**: Objects evolve as user scrolls, revealing depth progressively.

```javascript
const { scrollYProgress } = useScroll()

// Map scroll position to rotation
const rotation = useTransform(scrollYProgress, [0, 0.5, 1.0], [0, Math.PI/3, Math.PI])

// Map scroll to material state
const transmission = useTransform(scrollYProgress, [0, 1], [0.8, 1.0])
```

### 5.4 Hover Micro-Interactions

**The Gleb hover pattern**:
- Scale: 1.0 → 1.05 (5% scale up, spring animated)
- Bloom: +0.1 intensity
- Float speed: 1.0 → 1.3
- Chromatic aberration: +0.2

```javascript
const [hovered, setHovered] = useState(false)
const { scale } = useSpring({
  scale: hovered ? 1.05 : 1.0,
  config: { tension: 300, friction: 20 }
})

<animated.mesh
  scale={scale}
  onPointerEnter={() => setHovered(true)}
  onPointerLeave={() => setHovered(false)}
>
```

---

## Category 6: Post-Processing Effects

### 6.1 The Full Gleb Post-Processing Stack

**Order matters**. Wrong order = incorrect visual result:

```jsx
<EffectComposer>
  {/* 1. FIRST: DepthOfField (must calculate depth before adding glow) */}
  <DepthOfField
    focusDistance={0.01}
    focalLength={0.05}
    bokehScale={2}
  />

  {/* 2. SECOND: Bloom (must see undistorted scene first) */}
  <Bloom
    luminanceThreshold={0.88}
    luminanceSmoothing={0.025}
    intensity={0.4}
    mipmapBlur={true}
  />

  {/* 3. THIRD: ChromaticAberration (adds lens defect after all effects) */}
  <ChromaticAberration
    offset={[0.002, 0.002]}
    radialModulation={true}  // stronger at edges, like real lens
    modulationOffset={0.5}
  />

  {/* 4. LAST: Vignette (darkens edges of frame, always last) */}
  <Vignette
    eskil={false}
    offset={0.05}
    darkness={0.5}
  />
</EffectComposer>
```

### 6.2 Depth of Field

**Gleb's use case**: Selective focus creates cinematic quality. Background elements blur, hero element is sharp.

**For floating object scenes**:
```jsx
<DepthOfField
  focusDistance={0.0}   // Focus at scene center (where sphere is)
  focalLength={0.02}    // Very short = aggressive falloff = cinematic
  bokehScale={3}        // Larger bokeh circles at background
  height={700}          // Render resolution
/>
```

### 6.3 Chromatic Aberration

**Two levels simultaneously**:

1. **Material level**: Aberration inside the glass (prism effect)
```jsx
<MeshTransmissionMaterial chromaticAberration={0.8} />
```

2. **Post-processing level**: Aberration at screen edges (camera lens effect)
```jsx
<ChromaticAberration offset={[0.002, 0.002]} />
```

The combination creates physical realism: you feel both the glass physics AND the camera optics.

### 6.4 Vignette

**Subtle but critical**: Darkens screen edges, focuses eye on center. Subliminal quality indicator.
```jsx
<Vignette offset={0.05} darkness={0.5} />
```
**Without vignette**: Scene looks like WebGL demo.
**With vignette**: Scene feels like professional product render.

---

## Category 7: Loading / Thinking States

This is Gleb's most refined design area - the visual language of AI cognition.

### 7.1 The Three Core States

| State | Visual Metaphor | Physical Properties |
|-------|----------------|---------------------|
| **Idle** | Sleeping tiger | Minimal motion, low glow |
| **Processing** | Contained storm | High internal motion, reduced external |
| **Responding** | Sunrise | Maximum luminance, outward expansion |

### 7.2 State Transition Design

**Critical insight from research**: The TRANSITION between states is as important as the states themselves.

| Transition | Duration | Easing | Visual |
|-----------|----------|--------|--------|
| Idle → Listening | 0.3s | ease-out | Brightness surge + size increase |
| Listening → Thinking | 0.5s | ease-in-out | Brightness decrease + internal motion begins |
| Thinking → Speaking | 0.4s | spring | Scale increase + bloom surge |
| Speaking → Idle | 1.5s | ease-in | Gradual withdrawal, slow dimming |

### 7.3 Loading Animation Taxonomy

**Three types observed across the 35 references**:

1. **Materialization**: Particles converge to form object (SHOT 17: Gen AI loader)
2. **Energy fill**: Object fills from bottom (SHOT 13: Galaxy charging shape)
3. **Internal activation**: Object was there, internal motion increases (SHOTS 10, 19: Thinking reaction)

**For PureBrain/Aether**: Type 3 is most appropriate - Aether is always present, it just ACTIVATES when called.

---

## Category 8: Color Gradient Systems

### 8.1 The Electric Blue Spectrum (Gleb's Primary Palette)

The core color system observed across all 35 references:

```
Deep Space Black → Midnight Navy → Electric Blue → Cyan → White
#030308          → #0a1520      → #0D16F5      → #00D4FF → #FFFFFF
```

The gradient from dark to bright along this spectrum IS the energy level indicator:
- Dark end = rest, calm, night
- Bright end = active, energized, maximum response

**PureBrain mapping**:
- `#060606` = background (darkest)
- `#2a93c1` = PureBrain blue (mid-spectrum, brand identity)
- `#00D4FF` = peak activation (cyan at maximum)
- `#f1420b` = PureBrain orange (energy burst, calls-to-action)

### 8.2 Warm-Cool Tension

**Gleb always has warm-cool tension in his scenes**:
- Cool dominant: Electric blue, cyan (rationality, intelligence)
- Warm accent: Gold specular (#C8A84A), amber, orange (warmth, humanity)

**The tension creates**: Objects that feel both precise AND alive. Pure cool = cold/robotic. Pure warm = organic/muddled. The tension = intelligent life.

**PureBrain application**:
- Cool: #2a93c1 (primary)
- Warm: #f1420b (accent)
- This duality IS the brand: precision (blue) + energy (orange)

### 8.3 State Color Mapping

| State | Primary Hue | Secondary | Reason |
|-------|------------|-----------|--------|
| Idle | Blue (#2a93c1) | Gold specular | Confident, present |
| Listening | Cyan (#00D4FF) | Bright white | Open, receptive |
| Thinking | Violet (#7C3AED) | Deep indigo | Contemplative, deep |
| Speaking | White-gold (#C8A84A) | Orange (#f1420b) | All frequencies, energy |
| Night/rest | Deep navy (#1B2A4A) | Dim amber | Calm, intimate |

---

## The Technique Priority Matrix

For practical implementation, which techniques give the highest visual impact per development hour:

| Technique | Visual Impact | Implementation Time | Priority |
|-----------|--------------|--------------------|-|
| MeshTransmissionMaterial (glass) | CRITICAL | 2 hours | P0 |
| HDRI lighting | CRITICAL | 0.5 hours | P0 |
| Bloom (correct threshold) | HIGH | 0.5 hours | P0 |
| Gold specular (#C8A84A) | HIGH | 0.1 hours | P0 |
| ChromaticAberration (both levels) | HIGH | 0.5 hours | P1 |
| Float animation (multi-frequency) | HIGH | 1 hour | P1 |
| State machine (4 states) | HIGH | 4 hours | P1 |
| Depth of field | MEDIUM | 0.5 hours | P1 |
| Vertex displacement noise | MEDIUM | 3 hours | P2 |
| Orbital particle rings | MEDIUM | 2 hours | P2 |
| Iridescence shader | MEDIUM | 4 hours | P2 |
| Caustic approximation | LOW | 3 hours | P3 |
| Full particle systems | LOW | 5 hours | P3 |
