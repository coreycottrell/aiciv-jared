# ui-ux-designer: PureBrain Aether Avatar - Premium Design Specification

**Agent**: ui-ux-designer
**Domain**: UI/UX Design
**Date**: 2026-02-20

---

## Executive Summary

The current avatar (`avatar-fluid.html`) is technically complex but visually broken. The raymarched form renders as a lumpy, muddy sphere that reads like a rock or asteroid rather than glass or AI. It needs a complete visual direction reset - not more shader features, but **the right geometry, the right light story, and the right restraint**.

Gleb Kuznetsov's quality comes from one core insight: **premium materials feel real because of what they hold back, not what they add**. His glass spheres are mostly empty - mostly background. His lighting has one clear source, not six competing ones. His forms are simple - a sphere, not a hex-prism-sphere-liquid hybrid.

This spec tears down the current approach and rebuilds it with that philosophy.

---

## Part 1: Critique of the Current Avatar

### What You See in the Screenshots

The live WebGL render at idle state shows:
- A rough, heavily textured sphere sitting in a shallow liquid pool
- The surface reads as **rocky and opaque**, not glassy or transparent
- Dominant colors are muddy orange-brown tones from the texture noise layered over the "glass" - the PureBrain blue is nearly invisible
- The liquid pool beneath is a gray-green distraction with no relationship to the sphere
- The overall scene reads as dense and crowded - the eye has nowhere to rest
- 8 orbital particles are distracting dots that cheapen the premium feel

### Root Cause Analysis

**Problem 1: The SDF form is wrong for glass**

The `smin` blend between a sphere, a hex prism, and a liquid surface creates a shape that is neither. Glass needs a **clean, recognizable base silhouette**. The current hybrid reads as geological noise.

**Problem 2: The deformation is too aggressive**

The fbm noise deformation (`deformAmt = 0.025 + audio*0.14`) is applied globally. On glass this creates the asteroid-rock appearance. Gleb's glass has deformation only at the micro-scale (surface scratches, dust) not at the macro-scale (blobby form). The form itself stays smooth.

**Problem 3: Lighting competes with itself**

Four light sources (L1/L2/L3/L4) plus an environment sample plus caustics plus subsurface plus core glow plus volume scatter plus atmospheric glow = visual noise. The eye cannot find the primary light source because everything is equally lit. Gleb's work typically has ONE dominant key light with everything else subordinate.

**Problem 4: The color composition is muddy at idle**

At idle state, the dominant visual is the orange-brown texture noise, not the blue brand color. This is backwards. The idle state should be clean, cool, and predominantly the PureBrain blue (#2a93c1). The orange should be a speaking-state reward, not a constant presence.

**Problem 5: The liquid pool breaks the concept**

A liquid metal pool beneath an AI avatar is visually incoherent. It adds complexity without meaning. Gleb's compositions are singular - one hero element, one clear subject, refined negative space.

**Problem 6: The hex lattice interior is invisible**

The internal lattice that should read as a glowing circuit pattern inside glass is overwhelmed by all the other effects. The one genuinely strong idea in the current design is never actually visible.

**Problem 7: No surface imperfection = no credibility**

Real glass has micro-scratches, fingerprint smudges, dust particles, edge chips. The current "glass" is too mathematically perfect - which paradoxically reads as fake. A single subtle fingerprint smudge on the upper face and micro-scratches near the bottom would make it feel more real.

---

## Part 2: Design Direction - What We Are Building

### The Concept: Suspended Intelligence

A single sphere of premium optical glass, slightly larger than a human fist, suspended in a dark studio void. Inside the glass, a slowly rotating geometric intelligence - a nested icosahedral structure, not hex - radiates cool blue light from within. The glass refracts and bends this light. The outside is mostly dark studio, with one strong key light from upper-left creating a clean bright highlight arc, a subtle orange warmth from the right (Fresnel rim), and absolute darkness everywhere else.

This is inspired directly by the Gleb approach: **strong negative space, one dominant light source, one hero material, micro-detail as the proof of craft**.

### Visual References (Gleb Kuznetsov Work Descriptions)

**Reference A: Glass Sphere with Internal Light**
Gleb has produced work showing a perfect glass sphere with an internal glowing element. Key observations:
- The sphere surface is approximately 70% dark (showing the dark studio environment through it)
- The key light creates a single bright crescent highlight at the upper-left, roughly 15% of the total sphere area
- The refracted internal element is visible through the center as a warm glow, subtly distorted by the glass
- Thin chromatic aberration fringe (red/blue split, roughly 2px width) appears only at the silhouette edge
- Background is pure near-black (#0a0a0f) with a very subtle warm glow cast on the backdrop behind the sphere

**Reference B: Parametric Crystal Form**
A different Gleb piece uses a faceted crystal form with these properties:
- Clean sharp edges catch light as thin bright lines - not glowing neon, but specular reflections
- The crystal interior has colored inclusions - like frozen light suspended inside
- The form rotates very slowly (approximately 1 revolution per 30 seconds)
- Occasional micro-sparkle on sharp vertices (1-2 frame bright flash, random timing)

**Reference C: Premium UI Element with Depth**
Gleb's interface work uses glass panels with:
- Backdrop filter blur creating frosted glass background
- 1px border at 15% white opacity
- Inner shadow (inset, 1px, white at 8%) creating thickness illusion
- Drop shadow: 0px 20px 40px rgba(0,0,0,0.5)
- The glass panel itself tinted at maximum 8% opacity - nearly invisible

---

## Part 3: Material Specification

### Base Form

**Shape**: Single smooth sphere. No hex prism blending.
```glsl
float map(vec3 p) {
    // Primary form: pure sphere
    float sphere = length(p) - 1.0;

    // Macro deformation: NONE - glass is smooth

    // Micro surface texture only (very subtle scratches and fingerprints)
    // Applied at high frequency so it reads as surface texture not blobbing
    float scratch = fbm(p * 28.0 + uTime * 0.005) * 0.003;  // Micro only
    float fingerprint = fbm(p * 8.0) * 0.0015;               // Even subtler

    return sphere + scratch + fingerprint;
}
```

**Why sphere, not hex**: The sphere's silhouette is immediately readable as "glass ball" - one of the most credible premium material signals in visual design. The hex can live **inside** the glass as an internal geometric element, not as the exterior form.

### Glass IOR (Index of Refraction)

Premium optical glass (Schott N-BK7, the gold standard):
```glsl
// Per-channel for chromatic dispersion
float iorR = 1.5110;   // Red channel - least bent
float iorG = 1.5168;   // Green channel - reference
float iorB = 1.5220;   // Blue channel - most bent, creates blue fringe at edges

// Chromatic aberration split on silhouette: approximately delta 0.011
// This produces the signature red-blue fringe at the sphere edge
// that reads immediately as "real glass"
```

### Glass Absorption (Beer's Law)

Glass is not perfectly clear - it absorbs certain wavelengths over thickness:
```glsl
// Thickness-dependent absorption - glass gets more blue/green with depth
// This is what separates optical glass from "magic crystal"
vec3 absorption = exp(-vec3(0.08, 0.04, 0.02) * thickness);
// Red is absorbed most, blue least = glass looks slightly blue-tinted at depth
// Thickness range typically 0.0 to 2.0 in scene units
```

### Surface Roughness

Current avatar: surface is mathematically rough from noise = looks like rock.

Correct approach:
```glsl
// Glass roughness: essentially zero for the primary surface
// Add ONLY micro-roughness via normal perturbation, not SDF deformation
float microRough = 0.0008;  // Near-zero for optical glass quality

// Fingerprint smudge: ONE instance, upper face, subtle
// Position: offset from center toward upper-left
vec3 smudgeCenter = normalize(vec3(-0.3, 0.5, 0.4));
float smudgeDist = length(normalize(p) - smudgeCenter);
float smudge = exp(-smudgeDist * smudgeDist * 40.0) * 0.002;
// This perturbs the normal slightly in that region - increases roughness locally
```

### Transmission Weight

```glsl
// Glass is mostly transmission (what you see through it), not reflection
// Fresnel controls the blend:
// - Center of sphere (normal facing camera): ~4% reflection, 96% transmission
// - Edge of sphere (grazing angle): ~100% reflection, 0% transmission
// This is physically correct and what makes glass feel real

// The Fresnel curve should feel dramatic - the transition from transparent to
// mirror-like as you scan from center to edge is the glass money-shot
float f0 = 0.04;  // 4% reflectance at 0 degrees = real glass value
float fresnel = f0 + (1.0 - f0) * pow(1.0 - NdotV, 5.0);
// Do NOT use schlick with IOR directly - use the f0=0.04 version
// for more accurate glass behavior
```

---

## Part 4: Lighting Specification

### The Single Key Light Principle

Cut ALL current lights except one key + one very subtle fill. This is the most important change.

**Key Light (Primary)**
```glsl
// Position: upper-left, slightly forward
vec3 keyPos = normalize(vec3(-0.8, 1.4, 0.6));
// Color: near-white with very slight warmth
vec3 keyColor = vec3(1.0, 0.97, 0.93);
// Intensity: 3.5
float keyIntensity = 3.5;

// This creates the classic premium glass arc highlight:
// - Bright crescent on upper-left of sphere (~20% of surface area)
// - Sharp specular highlight at specular lobe (shininess 450-600)
// - The rest of the sphere is relative darkness
float spec_key = pow(max(dot(n, normalize(keyPos + V)), 0.0), 520.0) * 4.5;
```

**Fill Light (Ambient + Secondary)**
```glsl
// Very subtle blue fill from lower right - barely visible
vec3 fillPos = normalize(vec3(0.6, -0.3, -0.8));
vec3 fillColor = vec3(0.12, 0.28, 0.45);  // Cool blue
float fillIntensity = 0.15;  // Barely present
```

**Rim Light (State Color)**
```glsl
// Thin colored rim from behind-right
// This is where the PureBrain blue appears on the silhouette
vec3 rimPos = normalize(vec3(0.5, 0.1, -1.0));
// Color = current state color (blue at idle, orange at speaking)
float rimIntensity = 0.4;

// The rim should catch the Fresnel edge and color it
// At idle: a cool blue arc on the right silhouette edge
// At speaking: a warm orange arc (this is the state transition money-shot)
```

**No other lights.** Remove L2, L3, L4. Remove the accentLobe. Remove the underlight. Cut the 6 volumetric light rays. The darkness around the sphere is not a failure - it is premium. It is negative space. It is what makes the sphere the hero.

### Environment Map

The procedural environment should describe a photography studio with a single softbox:

```glsl
vec3 studioEnv(vec3 dir) {
    // Base: near-black studio void
    vec3 env = vec3(0.006, 0.007, 0.010);

    // Key light softbox - wide but not a point, soft gaussian lobe
    // Upper left quadrant
    float keyLobe = pow(max(0.0, dot(dir, normalize(vec3(-0.8, 1.4, 0.6)))), 8.0);
    // Softer exponent than current (18 is too tight) = more studio-like
    env += vec3(1.0, 0.97, 0.93) * keyLobe * 1.8;

    // Subtle ground plane (very dark warm reflection of nothing)
    float ground = smoothstep(0.0, -0.3, dir.y) * 0.02;
    env += vec3(0.12, 0.10, 0.08) * ground;

    // Everything else: dark
    return env;
}
```

### Caustic Projection (on Background)

One of the signature Gleb elements: the glass sphere casts caustic light patterns on the background behind it.

```glsl
// In the background calculation (miss case, not hit):
// Cast a "phantom" caustic behind where the sphere would be

// Project simplified caustic for background pixels "behind" the sphere
float causticMask = length(uv) < 0.55 ? 1.0 : 0.0;  // Roughly sphere footprint
if (!hit && causticMask > 0.0) {
    // Simulated caustic pool - bright spots where glass focuses the key light
    float c1 = sin(uv.x * 14.0 + uTime * 0.4) * sin(uv.y * 11.0 + uTime * 0.3);
    float c2 = sin(length(uv) * 18.0 - uTime * 0.6) * 0.5;
    float caustic = pow(max((c1 + c2) * 0.5 + 0.5, 0.0), 3.0);
    // State color caustics
    bgColor += stateColor * caustic * 0.035 * smoothstep(0.55, 0.2, length(uv));
}
```

---

## Part 5: Internal Geometry

### Replace Hex Lattice with Nested Icosahedra

The hex lattice idea is correct but the wrong geometry for glass. Inside a glass sphere, a slowly rotating icosahedron (or nested spherical wireframe) reads immediately as premium and mysterious.

```glsl
// Internal element: a slowly rotating wireframe icosahedron
// Rendered as distance to the nearest edge of the icosahedron
// Lit by the state color from within - appears to glow through the glass

float internalElement(vec3 p, float t) {
    // Rotate the interior at a different speed than any surface elements
    float angle = t * 0.08;  // Very slow - approximately 1 rotation per 78 seconds
    float cs = cos(angle), sn = sin(angle);
    vec3 rp = vec3(p.x*cs - p.z*sn, p.y, p.x*sn + p.z*cs);

    // Scale to fit inside sphere (approximately 0.5 radius)
    rp /= 0.5;

    // Distance to icosahedron edges
    // ... (icosahedron edge distance implementation)

    // Returns: 0.0 at edge, 1.0 at center of face
    float edgeDist = icosahedronEdge(rp);
    return smoothstep(0.04, 0.0, edgeDist) * 0.85;
}

// The interior glow should have a subtle breathing animation
float interiorPulse = 0.85 + sin(t * 0.4) * 0.15;
// Slower pulse than current (current at some states simulates heartbeat speed)
// Glass intelligence breathes slowly - it is calm, not anxious
```

### Secondary Internal: Particle Cloud (Subtle)

Deep inside the glass, a very faint cloud of micro-particles that shift with audio:
```glsl
// 12-15 micro-particles inside the sphere
// Size: 0.004 to 0.008 world units (barely visible)
// They are interior to the glass - their positions jitter slowly
// This creates the "something alive inside" effect at close inspection
// At normal viewing distance: just a subtle shimmer
// Audio reactive: particles drift further apart when speaking
```

---

## Part 6: Animation Specification

### Guiding Principle: Organic Timing, Mechanical-Free

All animations should use sine-based or perlin-noise-based timing with no abrupt starts or stops. Nothing should feel like a CSS transition or a timer tick.

### Idle State

**Breathing (Primary)**
```glsl
// Very slow scale pulse - the sphere "breathes"
// Period: 4.2 seconds (not round numbers - avoid mechanical feel)
float breathe = sin(uTime * (2.0 * PI / 4.2)) * 0.5 + 0.5;
// Scale range: 0.985 to 1.005 (barely perceptible on sphere radius)
float sphereRadius = 1.0 + breathe * 0.02 - 0.01;

// The internal element breathes OPPOSITE phase - contracts when sphere expands
// This creates a living tension inside the form
float interiorScale = 0.5 - breathe * 0.008;
```

**Slow Rotation**
```glsl
// Camera very slowly orbits around the sphere
// Period: approximately 45 seconds per revolution
float camAngle = uTime * (2.0 * PI / 45.0);
// Add very subtle sine drift to break the mechanical circular path
camAngle += sin(uTime * 0.07) * 0.06;

// The internal element rotates on a different axis
// Axis: tilted 23.5 degrees from vertical (like Earth's tilt)
// This tilt means you never see the same face twice
```

**Micro-Drift**
```glsl
// The sphere drifts slightly in space - not floating, but alive
// Position offset: maximum 0.02 in any direction
// Driven by layered slow noise, not sine waves
vec3 drift = vec3(
    snoise(vec3(uTime * 0.08, 0.0, 0.0)),
    snoise(vec3(0.0, uTime * 0.06, 0.0)),
    snoise(vec3(0.0, 0.0, uTime * 0.09))
) * 0.015;
```

### Listening State

When the user speaks, the avatar should LISTEN - not react excessively.

```glsl
// Listening: subtle pulsing that responds to audio input
// The sphere's internal glow brightens with voice amplitude
// But only the interior responds - the glass shell stays calm
// Audio level range: 0.0 to 1.0
// Interior brightness: base 0.7 + audio * 0.3
// Breathing rate increases slightly: 4.2s period -> 3.5s period

// Add a very subtle surface ripple at high audio levels:
// amplitude: audio * 0.006 (one third of current values)
// frequency: 8.0 on sphere surface (current is 12.0 - too aggressive)
float ripple = sin(length(p) * 8.0 - uTime * 3.5) * audioLevel * 0.006;
```

### Thinking State

```glsl
// Thinking: the internal element spins faster
// Normal: 0.08 rad/s
// Thinking: 0.22 rad/s (eased in and out, not instant)
// The sphere gets a very subtle purple-blue shift in its refracted interior

// Also: a subtle "scanning" effect - a bright band rotates around the interior
// Like a lighthouse beam inside the glass - one revolution per 2.5 seconds
// Implemented as: a second internal element at 90 degrees to the first
float scanAngle = uTime * (2.0 * PI / 2.5);
float scanBeam = smoothstep(0.08, 0.0, abs(mod(dot(rp, vec3(sin(scanAngle), 0.0, cos(scanAngle))), 1.0) - 0.5));
// Intensity: 0.15 * thinkingMix (only visible in thinking state)
```

### Speaking State

```glsl
// Speaking: the most energetic state - but still controlled
// Orange takes over the interior from the center outward
// The rim light shifts from blue to warm orange
// The caustic projection behind the sphere gets brighter and more complex

// Audio response: the surface ripple amplitude increases
// The sphere "projects" - slightly more front-facing light

// Key change: a visible energy field slightly outside the sphere surface
// Not a ring - a very subtle heat-haze distortion of background pixels
// Implemented: slightly perturb background UV by normal at surface when near sphere
float energyField = exp(-abs(hitDist - 1.05) * 20.0);  // Thin shell at r=1.05
// Distort background by energyField * 0.01 in tangential direction
```

### State Transitions

```glsl
// Transitions use a sigmoid ease, not linear interpolation
// Duration: 0.8 seconds for idle<->speaking, 0.5s for listening
// The state float blends smoothly:
// uState: 0.0=idle, 1.0=speaking, 2.0=listening, 3.0=thinking

// Interior color transition:
// Ease function: smoothstep(prevState, nextState, t) where t goes 0->1 over duration
// The transition should feel like a fluid shift, not a crossfade
```

---

## Part 7: Color Specification

### Idle State (Blue - Intelligence at Rest)

```
Primary glass tint (interior glow):    #1a4d7a  (deep ocean blue, dimmed)
Interior element emissive:             #2a93c1  (PureBrain Blue, full saturation)
Rim light on silhouette:               #5bb8d4  (lighter blue, almost cyan)
Specular highlight (key light):        #f5f5ff  (near-white, very slight blue)
Caustic projection:                    #1a3d5a  (very dark blue, barely visible)
Background atmosphere:                 #060810  (near-black, cooler than current)
```

The glass should look like this: mostly dark (the dark studio showing through), with one bright clean highlight from the key light, and a calm blue glow from the interior element. The blue is subtle at idle - present, not insistent.

### Speaking State (Orange - Intelligence Engaged)

```
Primary glass tint (interior glow):    #6b2200  (deep ember, not burnt)
Interior element emissive:             #f1420b  (PureBrain Orange, full)
Accent hot core:                       #ff7a3d  (lighter orange, visible at center)
Rim light on silhouette:               #e8621a  (warm orange rim)
Specular highlight (key light):        #fff4e8  (warm white)
Caustic projection:                    #4a1a00  (very dark orange)
Background atmosphere:                 #0d0804  (near-black, warmer)
```

The transition from blue to orange when speaking should feel like someone turning on a lamp inside the glass. The center brightens first, then the color pushes outward to the rim.

### Thinking State (Purple - Intelligence Processing)

```
Primary glass tint (interior glow):    #2a0a5a  (deep violet)
Interior element emissive:             #7b4fc9  (mid purple, not neon)
Scanning beam:                         #9b6fe0  (lighter purple)
Rim light on silhouette:               #5a2a9a  (violet rim)
Specular highlight (key light):        #f8f0ff  (near-white, slight violet warmth)
Caustic projection:                    #1a0835  (very dark purple)
Background atmosphere:                 #080510  (near-black, slightest violet)
```

### Accent Colors (Unexpected)

Gleb always includes an unexpected accent. For Aether:

```
Gold accent:    #c8a84a  (appears only on interior icosahedron vertices, micro-sparkle)
Ice white:      #e8f4ff  (specular highlight at the shiniest point - pure white-blue)
```

These appear sparingly - the gold on 2-3 vertices of the interior element, the ice white as the peak of the key light specular. They create the "jewelry" quality.

---

## Part 8: Post-Processing Specification

### Bloom

Current bloom is too broad and washes out the dark areas that are crucial for drama.

```glsl
// Threshold: only the brightest points get bloomed
float bloomThreshold = 0.85;  // Current: 0.45 - way too low, blooms everything
float bloomIntensity = 0.25;   // Current: 0.4 - too strong

// Use two passes:
// Pass 1: Wide soft bloom (radius 12 pixels equiv) at 0.15 intensity
//         Catches the specular highlight and internal glow
// Pass 2: Tight bright sparkle (radius 3 pixels equiv) at 0.35 intensity
//         Only fires at lum > 1.2 - makes the specular sparkle
float wideBoom = smoothstep(bloomThreshold, bloomThreshold + 0.3, lum) * 0.15;
float sparkle  = smoothstep(1.2, 1.8, lum) * 0.35;

col += bloomCol * wideBoom;
col += bloomCol * sparkle;
```

### Chromatic Aberration

Current: applied as `edgeFringe` on the glass surface. Correct approach:

```glsl
// Apply AFTER all rendering, as a screen-space post effect
// Only at the silhouette of the glass sphere (where normal is near perpendicular to view)
// Width: 1.5-2.5 pixel equivalent in UV space

// Sample scene color at 3 slightly offset UVs:
float aberrationStrength = 0.0012;  // Very subtle - it is detail, not feature
vec3 finalR = sampleScene(uv + vec2(aberrationStrength, 0.0)).r;
vec3 finalG = sampleScene(uv).g;
vec3 finalB = sampleScene(uv - vec2(aberrationStrength, 0.0)).b;
// Mask to sphere silhouette only
float caAberrationMask = edgeFresnel * silhouetteMask;
```

### Film Grain

Current implementation is fine in concept but the noise frequency and amount need tuning:

```glsl
// Current: 0.009 - acceptable
// Recommend: 0.006 - slightly less, the glass should feel clean
// Current frequency multiplier 0.7 on coords: increase to 1.4
// Rationale: smaller grain = more photographic, less video-game
float grain = snoise(vec3(gl_FragCoord.xy * 1.4, uTime * 18.0)) * 0.003;
// Only add grain to bright regions - dark areas should stay clean
col += grain * smoothstep(0.15, 0.6, lum);
```

### Vignette

Current vignette is functional. Keep parameters but soften slightly:

```glsl
// Current: smoothstep(0.55, 1.0, length(uv)*1.1) * 0.15
// Recommend: smoothstep(0.50, 1.05, length(uv)*1.05) * 0.18
// Slightly wider/softer, slightly more intensity
// Rationale: frames the sphere without darkening the sphere itself
float vign = 1.0 - smoothstep(0.50, 1.05, length(uv) * 1.05);
col *= 0.82 + vign * 0.18;
```

### Tone Mapping

Keep ACES but adjust gamma:
```glsl
// Current gamma: 0.86 (slightly aggressive)
// Recommend: 0.91 - more neutral, less punchy shadows
// The current 0.86 lifts blacks too much and reduces the drama
col = pow(max(col, vec3(0.0)), vec3(0.91));
```

### Lens Sharpening (New)

Add a subtle unsharp mask on the specular highlights to make them feel like a real camera:
```glsl
// Subtle sharpening: enhances the specular highlights specifically
float sharpMask = smoothstep(0.6, 0.9, lum) * 0.08;
// Add slight boost to high-luminance areas
col += col * sharpMask;
```

---

## Part 9: Things to Remove

These are current features that actively hurt quality:

1. **The liquid pool** - Remove entirely. `smin(base, liquid, ...)` and all liquid metal code. It makes the avatar look geological, not technological.

2. **The 8 orbital particles** - Remove entirely. They are cheap effects that break premium feel. If you want micro-particles, they should be INSIDE the glass, not orbiting it.

3. **The 6 volumetric light rays** - Remove entirely. These are the kind of effect that signals "I'm trying to look impressive" rather than actually being impressive. Gleb never uses obvious light rays.

4. **The hex-prism SDF** - Remove from the exterior form. Keep the hex concept but move it INSIDE as an internal texture/lattice element.

5. **Four light sources** - Cut to one key + one very subtle fill. The multi-light setup creates even, undramatic illumination.

6. **The `bgRing1` and `bgRing2` concentric rings** - Remove. They are decorative clutter on what should be a dark, clean background.

7. **The `core` glow that applies `exp(-length(p)*3.5)`** - This is the source of the muddy orange-brown everywhere. It casts warm color across all surface normals uniformly, destroying any sense of directional lighting.

---

## Part 10: Implementation Priority

If rebuilding is phased, here is the sequence of changes ordered by visual impact:

**Phase 1 (Immediate, highest impact - do these first):**
1. Remove the liquid pool SDF
2. Remove orbital particles
3. Remove light rays
4. Remove the core glow (`exp(-length(p)*3.5)`) from the glass material path
5. Cut lights from 4 to 1 key + 1 fill
6. Fix bloom threshold from 0.45 to 0.85

Expected result: the avatar will look dramatically cleaner after only these changes. The muddy quality comes mostly from (4) and (5).

**Phase 2 (High impact):**
7. Replace fbm macro-deformation with micro-only noise
8. Remove hex prism from SDF, use pure sphere
9. Implement correct f0=0.04 Fresnel for glass
10. Fix glass absorption (Beer's law tint)

**Phase 3 (Polish):**
11. Add internal icosahedron geometry
12. Implement screen-space chromatic aberration
13. Add fingerprint/micro-scratch surface detail
14. Caustic projection on background
15. Tune state color transitions

---

## Part 11: Canvas and Layout Recommendations

### Avatar Size and Cropping

Current: 480x480px canvas, avatar fills the frame edge to edge.

Recommendation: The sphere should occupy approximately **55-60% of the canvas diameter**. Negative space around it is not wasted space - it is compositional air that makes the sphere feel precious.

```
Canvas: 480x480px (keep current)
Sphere radius in canvas: approximately 130-140px
Sphere center: offset slightly upward from center (center at 47% from top)
Background: pure dark, no rings, no atmosphere gradient
```

### Background Treatment

The background should be near-black, not pitch black:
- Center of canvas (behind sphere): `#080a12` (very dark blue-black)
- Edges of canvas: `#050508` (almost black)
- No visible atmosphere glow unless audio is very high (then barely perceptible state-color)

This creates a dark photographic studio feel. The sphere floats in it rather than sitting on it.

---

## Part 12: CSS Fallback Improvement

The CSS fallback (when WebGL fails) also needs to improve. Current fallback is a simple radial gradient orb with two rings. It has no personality.

Recommendation for CSS fallback:

```css
/* The glass sphere concept translated to CSS */
#cssAvatar .orb-glow {
    /* Multiple gradient layers to fake glass */
    background:
        /* Key light highlight - upper left */
        radial-gradient(ellipse at 28% 25%, rgba(255,255,255,0.18) 0%, transparent 35%),
        /* State color glow - center */
        radial-gradient(ellipse at 50% 50%, var(--state-color-light) 0%, var(--state-color-dark) 40%, transparent 70%),
        /* Dark ambient - fills most of sphere */
        radial-gradient(ellipse at 50% 50%, transparent 30%, rgba(4,6,14,0.85) 80%);

    /* Rim light simulated via box-shadow */
    box-shadow:
        /* Key light halo (outside) */
        -4px -4px 20px rgba(255,255,255,0.06),
        /* State color rim (inside right edge) */
        inset 6px 0px 20px rgba(var(--state-rgb), 0.15),
        /* Depth shadow */
        0 20px 40px rgba(0,0,0,0.6);
}

/* Highlight crescent - the key light on glass */
#cssAvatar .orb-highlight {
    /* Current: centered. Better: upper-left, small, bright */
    top: 22%;
    left: 22%;
    width: 28%;
    height: 18%;
    transform: rotate(-15deg);
    background: radial-gradient(ellipse, rgba(255,255,255,0.22) 0%, transparent 70%);
    border-radius: 50%;
}
```

---

## Summary: The One-Sentence Direction

**Build the avatar as a single premium glass sphere in a dark studio, lit by one key light, with an icosahedral intelligence glowing inside it - and let the darkness do half the work.**

Everything else follows from that sentence. Restraint is the craft.

---

*Prepared by ui-ux-designer for the PureBrain Aether avatar visual direction upgrade.*
*Reference file analyzed: `/home/jared/projects/AI-CIV/aether/exports/avatar-fluid.html`*
*Screenshots reviewed: avatar-fluid-idle.png, avatar-fluid-speaking.png, avatar-conv-alive.png, avatar-glass-v1.png*
*Concept images reviewed: avatar_aether_v2_gleb.png through v11_hex_portal.png*
