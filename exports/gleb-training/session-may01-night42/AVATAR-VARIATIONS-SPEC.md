# Night 42 — 3 Avatar Variation Specs

**Date**: 2026-05-01
**Theme**: AI-entity avatars in the Gleb Kuznetsov aesthetic
**Format**: Three.js / R3F scene specifications
**Brand colors**: PUREBRAIN_BLUE #2a93c1, PUREBRAIN_ORANGE #f1420b, DARK #060606

---

## Variation A — Glass Portrait Bust

**Concept**: A polished crystal "bust" silhouette — abstract head + shoulders form rendered as a single piece of dispersive optical glass. Reads as identity (a being is here) without specific human features. Inspired by Gleb's Glass Blower visual + Codrops glass torus IOR oscillation (March 2025).

### Geometry Approach
- Base: a hand-built abstract bust SDF OR a sculpted GLB ("simplified mannequin head + shoulders, no facial detail")
- Subdivision: 256+ segments / SubdivisionModifier level 2 for transmission clarity
- Slight low-frequency surface displacement (FBM, amplitude 0.015) for "hand-blown glass" imperfection
- Mesh scale: 1.6 units tall, 0.9 wide
- Floats at 0.5Hz with 0.05u vertical bob, 0.02 rotational drift Y axis

### Material / Shader Stack
```jsx
<MeshTransmissionMaterial
  samples={20}              // higher than default 10 for cleaner refraction
  resolution={512}          // backside texture buffer
  transmission={1}
  thickness={1.4}           // dense bust = strong magnification
  roughness={0.04}
  ior={1.45}                // animated 1.42 -> 1.52 over 6s loop (GSAP)
  chromaticAberration={1.1} // strong dispersion at silhouette edges
  anisotropy={0.25}
  distortion={0.15}
  distortionScale={0.4}
  temporalDistortion={0.08} // animated noise — looks "alive"
  attenuationDistance={2.5}
  attenuationColor="#5fb6dc" // tinted PureBrain blue
  backside={true}
  backsideThickness={0.4}
/>
```

Behind the bust (visible THROUGH the glass):
- A small inner orb (radius 0.3) with `meshBasicMaterial` color #f1420b emissive — appears as a glowing "soul/core" magnified by the bust glass
- The bust ACTS AS A LENS — viewer looks through it and sees the brand-orange core pulsing

### Lighting Rig
- HDRI: Poly Haven `studio_small_09_2k.hdr` — clean studio bounce
- Environment intensity 0.8
- Key light: directional, 3-point classic position (top-front-right), color #ffffff, intensity 1.5
- Fill: PureBrain blue #2a93c1 directional, intensity 0.4 (gives glass the brand tint in shadows)
- Rim: PureBrain orange #f1420b directional from behind-below, intensity 1.8 — wraps the silhouette in fire

### Post FX
```jsx
<EffectComposer multisampling={4}>
  <N8AO halfRes aoRadius={0.6} intensity={1.2} />
  <Bloom luminanceThreshold={0.7} luminanceSmoothing={0.04} intensity={0.55} mipmapBlur />
  <DepthOfField focusDistance={0.012} focalLength={0.08} bokehScale={4} />
  <ChromaticAberration offset={[0.0018, 0.0022]} />
  <Vignette eskil={false} offset={0.15} darkness={0.85} />
</EffectComposer>
```

### Why this advances mastery
- Combines Codrops 2025 IOR-animation technique with our existing dispersion + thin-film knowledge
- Tests whether we can carry "identity readability" through pure form (no face) — a Gleb signature
- Lens-as-character: the orange core seen through blue glass = brand metaphor in 3D

---

## Variation B — Plasma Energy Being

**Concept**: A volumetric, semi-formless cloud of plasma + electric tendrils suggesting a humanoid silhouette without solid surface. Inspired by R3F Plasma Ball forum showcase + Voronoi plasma technique.

### Geometry Approach
- Base: NO solid mesh. Instead a `points` system (8000–12000 GPU particles) constrained to a humanoid attractor field
- Attractor field: anisotropic SDF approximating a standing figure (sphere head + tapered torso + arm/leg fields)
- Particles are confined to within `distance < 0.15` of the SDF surface
- Each particle has random angular velocity around the body's central axis → subtle whirling
- Secondary: 12 lightning-strike geometries (`THREE.LineCurve3` polylines) flickering between random surface points, lifetime 0.2s each, stochastic spawn

### Material / Shader Stack
**Particles** (custom ShaderMaterial, additive blending):
```glsl
// vertex
gl_PointSize = 2.0 + sin(time * 4.0 + vRandom * 6.28) * 1.5;
// fragment
float d = length(gl_PointCoord - 0.5);
float core = smoothstep(0.5, 0.0, d);
float halo = smoothstep(0.5, 0.15, d) * 0.4;

// color: gradient from BLUE core -> ORANGE rim based on velocity
vec3 col = mix(vec3(0.16, 0.58, 0.76), vec3(0.94, 0.26, 0.04), vSpeed);
gl_FragColor = vec4(col, core + halo);
```

**Lightning lines**:
- `THREE.Line` with `LineBasicMaterial` `transparent`, `blending: AdditiveBlending`
- Color animated through HSV cycle: blue → cyan → white-hot core during 0.2s lifetime
- Fade alpha from 0.9 → 0 across lifetime

**Outer aura** (single billboarded plane behind):
- Radial gradient sprite, additive, scale 3x figure size
- Slow opacity pulse 0.3 → 0.5 at 0.4Hz

### Lighting Rig
- HDRI: minimal — `Environment` preset `"night"` with intensity 0.15 (we're emissive, don't need much env)
- 1 PointLight at center of figure: PureBrain blue, intensity 8, distance 4 — illuminates dust/floor below
- 1 PointLight near top: PureBrain orange, intensity 4, distance 2 — head halo

### Post FX
```jsx
<EffectComposer multisampling={4}>
  <Bloom luminanceThreshold={0.2} luminanceSmoothing={0.025} intensity={1.4} mipmapBlur radius={0.85} />
  {/* HEAVY bloom — the figure IS the bloom */}
  <DepthOfField focusDistance={0.015} focalLength={0.06} bokehScale={3} />
  <ChromaticAberration offset={[0.003, 0.0035]} />
  <GodRays sun={centerOrb} samples={60} density={0.95} weight={0.4} decay={0.92} />
  <Noise opacity={0.03} />
  <Vignette offset={0.1} darkness={0.9} />
</EffectComposer>
```

### Why this advances mastery
- First production-level plasma being: tests whether we can make an avatar with NO solid geometry that still reads as "an entity"
- Pushes additive blending + bloom interaction — a known Gleb technique
- GPU particle attractor SDF is new — extends our SDF morphing knowledge from Session 41 into particle systems

---

## Variation C — Crystalline Geometric Form

**Concept**: A faceted polyhedral "head" — like a low-poly D20 sculpted into something that suggests AI/cognition. Fully solid, sharp-edge crystal aesthetic. Inspired by Crysal Figma collection (40 holographic crystal shapes) + Pure Tech hex iconography.

### Geometry Approach
- Base: an icosphere (`detail=1`, ~80 triangles) — the FACETS are the aesthetic
- Apply SubdivisionModifier 0 (keep flat shading on)
- Optionally fuse with a slightly smaller, rotated hexagonal prism via CSG → asymmetric crystal cluster
- Hovers + slowly rotates: 0.15 rad/s Y, 0.05 rad/s X
- Gentle "breathing" scale: 1.0 ↔ 1.04 at 0.3Hz

### Material / Shader Stack
This is where Variation C gets interesting — **dual-layer material**:

**Layer 1 (outer): Thin-film iridescent glass**
```jsx
<MeshPhysicalMaterial
  transmission={0.85}       // not full — we want SOME color
  thickness={0.6}
  roughness={0.02}          // sharp facets, sharp reflections
  ior={1.55}
  iridescence={1}           // KEY: thin-film iridescence
  iridescenceIOR={1.3}
  iridescenceThicknessRange={[100, 800]}
  clearcoat={1}
  clearcoatRoughness={0.03}
  flatShading={true}        // critical — keeps crystal facets sharp
  attenuationColor="#2a93c1"
  attenuationDistance={1.2}
/>
```

**Layer 2 (inner glow): a slightly smaller (0.85x) inner icosphere**
```jsx
<meshBasicMaterial
  color="#f1420b"
  transparent
  opacity={0.6}
  blending={THREE.AdditiveBlending}
/>
```
The inner glow shows through the iridescent shell at a different intensity per facet → the crystal looks *charged*.

**Plus**: a custom GLSL fresnel rim pass for that signature wet-edge highlight:
```glsl
float fresnel = pow(1.0 - dot(normalize(vNormal), normalize(viewDir)), 3.0);
gl_FragColor.rgb += vec3(0.95, 0.5, 0.2) * fresnel * 0.7; // orange rim
```

### Lighting Rig
- HDRI: Poly Haven `dikhololo_night_2k.hdr` — dramatic dark with strong stage lights
- Environment intensity 1.2 (iridescence NEEDS env contribution)
- 3-point rig:
  - Key: directional cool white (#e6f0ff), intensity 2.0, top-front-left
  - Fill: PureBrain blue, intensity 0.7, bottom-front-right
  - Rim: PureBrain orange, intensity 2.2, behind the form
- A single soft area light overhead (rect light 2x2 unit) intensity 1.5 — gives the facets long sweeping reflections

### Post FX
```jsx
<EffectComposer multisampling={8}>
  <SSR
    intensity={0.4}
    distance={4}
    thickness={0.6}
    blur={0.05}
    minDepthThreshold={0.9}
  />  {/* floor reflections of the crystal */}
  <N8AO halfRes aoRadius={0.5} intensity={1.0} />
  <Bloom luminanceThreshold={0.85} luminanceSmoothing={0.03} intensity={0.45} mipmapBlur />
  <DepthOfField focusDistance={0.013} focalLength={0.07} bokehScale={3.5} />
  <ChromaticAberration offset={[0.0014, 0.0017]} radialModulation modulationOffset={0.4} />
  {/* radial CA — strongest at edges, learned in night36 */}
  <Vignette offset={0.18} darkness={0.82} />
</EffectComposer>
```

### Why this advances mastery
- Tests dual-layer material composition (outer iridescent + inner emissive) — a Gleb signature for "alive" objects
- Combines MOST advanced techniques we've learned: thin-film iridescence (n10), SSR reflections (n11), radial CA (apr15), n8AO (n10)
- The flatShading + iridescence combo is rare and produces the strongest "premium" read

---

## Comparison Matrix

| Aspect | A: Glass Portrait | B: Plasma Being | C: Crystalline |
|---|---|---|---|
| **Geometry** | Solid bust mesh | GPU particles + SDF attractor | Faceted icosphere + inner sphere |
| **Material core** | MeshTransmissionMaterial | Custom shader points | MeshPhysicalMaterial w/ iridescence |
| **Brand integration** | Orange core through blue glass | Blue→orange velocity gradient | Orange inner glow through blue iridescent shell |
| **Hardest technique** | Animated IOR oscillation | Particle SDF confinement | Dual-layer additive composition |
| **Mood** | Contemplative, premium | Volatile, mystical | Sharp, cognitive, crystalline |
| **Best use** | Hero portrait section | Loading state, "thinking" indicator | Logo / brand identity placement |
| **Performance** | Medium (1 transmission mesh) | Heavy (12k particles + bloom) | Medium-heavy (SSR + iridescence) |
| **Closest Gleb piece** | Glass Blower / Voice visual | Milkinside energy work | Crysal-style holographic forms |

---

## Production Recommendation

If we had to pick ONE for shipping to purebrain.ai right now: **Variation C (Crystalline)** — best perf/quality ratio, most distinct from competitor 3D, and the dual-layer technique is a real mastery flex.

Variation A is the strongest pure aesthetic but reads "humanlike" which may not be the brand direction (we are "your AI partner", not "an AI human").

Variation B is the most experimental and best for non-static contexts (loading, voice-input states).

---

## Files
- This spec: `exports/gleb-training/session-may01-night42/AVATAR-VARIATIONS-SPEC.md`
