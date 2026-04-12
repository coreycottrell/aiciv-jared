# ui-ux-designer: Gleb Kuznetsov / Milkinside Visual Replication Guide

**Agent**: ui-ux-designer
**Domain**: UI/UX Design
**Date**: 2026-02-20

---

## Memory Search Results

- Searched: `.claude/memory/agent-learnings/ui-ux-designer/` for "avatar", "sphere", "Gleb"
- Found: No prior avatar design work in ui-ux-designer memory
- Applying: Fresh forensic analysis from Gleb's portfolio + current code review

---

# THE GLEB KUZNETSOV / MILKINSIDE VISUAL REPLICATION GUIDE

**Purpose**: So specific that a shader developer reading only this document can produce something that looks like a Milkinside piece.

**The problem we are solving**: We keep producing WebGL demos. Gleb produces products. This document explains exactly why those are different things and how to close the gap.

---

## Part 1: What Gleb Actually Builds (The Reference Works)

### Shot 1: "Colorful AI Sphere" (Dribbble shot 14194855)

**What it is**: The defining Milkinside sphere. Tagged "All the colors in one."

**Shape**: Perfect mathematical sphere. Zero deviation. No organic deformation, no blob-iness, no surface bumps that read as "noise." The silhouette is a clean circle.

**Material**: This is NOT glass. It is not transparent. It is a sphere of TRAPPED, CONCENTRATED LIGHT. Think of it as a compressed galaxy rather than a hollow glass ball.

**Color zones (exact palette extracted from this piece)**:
- `#020204` - The background and the darkest interior void
- `#3C0E4E` - Deep violet/purple, a major interior zone (~30% of surface area)
- `#0D16F5` - Electric vivid blue, the dominant accent (~20% of visible surface)
- `#E42424` - Saturated red, appears as a hot zone or concentrated band
- `#D10DCE` - Magenta/hot pink, transition color, creates prismatic edge effects
- `#18A8D3` - Cyan/teal, the "cool" counterpoint to the warm reds
- `#B99C43` - Gold/mustard, specular highlight color (not white - gold)

**How colors are distributed on the sphere**: They are NOT blended smoothly like a rainbow gradient. They exist as distinct ZONES that bleed into each other. Imagine looking at a lit crystal where each internal facet captures a different colored light source. The transitions are sharp-ish at their source but soften through the glass material.

**Key observation**: The colors are SATURATED and VIVID. Not pastel. Not desaturated. Full chromatic intensity. `#0D16F5` is nearly pure blue at maximum saturation. `#D10DCE` is neon magenta.

**Lighting**: Multiple colored light sources, not a single studio key light. Each color zone corresponds to a differently-colored environment light. This is the central technique Gleb uses.

**Background**: `#020204` - This is not `#000000`. It is a near-black with the tiniest hint of blue (2, 2, 4). Pixel-perfect studio darkness.

**Specular highlight**: The primary highlight is small (maybe 4-6% of sphere diameter), sharp-edged, and GOLD (`#B99C43` range), not white. This is critical. White highlights say "plastic." Gold highlights say "precious material."

---

### Shot 2: "AI Sphere Visual Design by Milkinside" (shot 24197602, 2024)

**What it is**: The most recent iteration. "Procedural AI visual research."

**Shape**: Still a perfect sphere. Immutable. Gleb never deforms the sphere silhouette.

**Material evolution**: This piece moves toward a more interior-luminous approach. The sphere appears to contain a bright emissive core with colored light radiating outward through a slightly translucent shell.

**Color palette for this piece**:
- Background: Very deep navy/blue-black, approximately `#050818`
- Dominant interior: Teal-blue-violet, around `#1a3a7a` to `#2a4aaa`
- Secondary zones: Purple `#5a1a8a`, cyan `#0a9aaa`
- Primary highlight: Near-white with blue tint `#d0e8ff` (not pure white)
- Rim/edge: Soft cyan-white glow

**What changed from the colorful sphere**: This one is more monochromatic but with spectacular depth. The spectral explosion of the colorful sphere became more controlled, more "product-ready."

---

### Shot 3: "Glass Reflection CGI" (shot 20098860)

**What it is**: A more abstract glass form, not a sphere but the same material philosophy.

**Shape**: An elongated, asymmetric organic form (like a water droplet caught mid-fall). This is Gleb exploring the MATERIAL rather than the shape.

**Material (this piece makes the technique explicit)**:
- The surface is a near-perfect mirror at the edges (high Fresnel)
- The center is highly transparent (low Fresnel)
- The refraction is VISIBLE and STRONG - you can see the environment distorted dramatically through the center
- Chromatic aberration is INTENTIONAL and VISIBLE at the edges - distinct red/blue fringing

**The revelation from this piece**: Gleb's "glass" material actually has chromatic dispersion as a feature, not an artifact to hide. The color prisming IS the aesthetic.

**Background**: `#080c14` range - very dark, near-black with blue tint, possibly a very subtle radial gradient from `#0c1020` center to `#04060c` edges.

**What's inside**: The environment reflection is a carefully composed studio setup. You can see blurred out-of-focus light sources. There is no internal geometry (no icosahedron, no wireframe). The beauty is ENTIRELY from light behavior on the glass material.

---

### Shot 4: "Crystal Sculpture" (shot 14486416)

**What it is**: An organic crystal form - multiple faceted planes intersecting.

**Shape**: This is the exception - NOT a sphere. But the material rules apply.

**Key observations**:
- Each facet captures a different reflection, so the crystal appears multi-colored from different angles
- The gem/crystal has an opaque core transitioning to transparent edges
- Hard specular highlights on each facet edge (specular shininess in the 500-800 range)
- A CAUSTIC LIGHT PATTERN is projected onto the dark background below/around the crystal
- The caustics are soft, organic, and slightly colored (not sharp computer-generated lines)

**Color**: This piece is cooler - blues, cyans, with warm amber specular peaks.

---

### Shot 5: "Glass Blower Visual" (shot 17066462)

**What it is**: A hot glass form in mid-process.

**Key observations**:
- Has a HOT EMISSIVE CORE: the center glows orange-amber-white from heat
- The glass material transitions from opaque/scattering at the hot center to transparent at the cooler extremities
- This is the "subsurface scattering" look - light entering the material and scattering internally before exiting
- The background has soft chromatic light spill from the hot glass onto the dark surroundings
- This piece uses ATMOSPHERIC GLOW: the hot zone has a soft halo in the background

---

## Part 2: The Forensic Analysis - What Gleb DOES vs What We DO

### The Current Avatar (avatar-fluid.html) - Honest Assessment

After reading the full shader code, here is what we are doing:

**What we got right**:
- Perfect sphere shape (no deformation) - CORRECT
- Dark studio background near `#080a12` - CORRECT
- Single key light from upper-left - PARTIALLY CORRECT
- Fresnel glass material with refraction - CORRECT IN PRINCIPLE
- Chromatic aberration (per-channel IOR: 1.5110/1.5168/1.5220) - CORRECT
- Beer's law absorption through glass thickness - CORRECT

**What we got wrong (the gap list)**:

1. **SINGLE STUDIO KEY LIGHT ONLY**
   Current: One warm white key light `vec3(1.0, 0.97, 0.93)` at `normalize(vec3(-0.8, 1.4, 0.6))`
   Gleb: MULTIPLE COLORED LIGHT SOURCES. His spheres glow because they exist in an environment with several distinct colored lights from different directions. Not a photography studio. A color lab.

2. **WRONG INTERIOR COLOR PALETTE**
   Current: PureBrain Blue (`#2a93c1`) for idle, Orange for speaking, Purple for thinking.
   Gleb: Deep violet (`#3C0E4E`), electric blue (`#0D16F5`), red (`#E42424`), magenta (`#D10DCE`), cyan (`#18A8D3`).
   The specific colors are not the problem - the PALETTE PHILOSOPHY is. Gleb uses maximum-saturation, high-contrast, WIDE COLOR GAMUT combinations. We use brand colors which are comparatively desaturated and single-hue.

3. **WRONG SPECULAR HIGHLIGHT COLOR**
   Current: `vec3(0.910, 0.953, 1.0)` - ice blue-white
   Gleb: `#B99C43` range - GOLD. His highlights are warm gold, not white. This single change would elevate the look significantly.

4. **ICOSAHEDRON INTERIOR IS THE WRONG METAPHOR**
   Current: A rotating wireframe icosahedron inside the glass sphere.
   Gleb: No wireframes. No geometric interior structure. His sphere interiors contain LIGHT, not geometry. The interior is a volumetric GLOW, not a visible object.

5. **THE BACKGROUND IS TOO DEAD**
   Current: `vec3(0.008, 0.010, 0.018)` - flat near-black
   Gleb: The background picks up subtle colored light spill from the sphere. If your sphere contains cyan and magenta light, those colors should BLEED into the black background as soft, almost imperceptible halos around the sphere. This is what gives Gleb's pieces their atmospheric quality.

6. **MISSING SUBSURFACE GLOW EFFECT**
   Current: Light either reflects or transmits. Binary.
   Gleb: The sphere appears to EMIT from within. There is an inner core that is brighter than the surface. Light appears to be generated inside and radiating outward. This is a volumetric glow rather than surface material interaction.

7. **MICRO-SURFACE TEXTURE ON GLASS IS WRONG**
   Current: FBM noise (`scratch`, `fingerprint`) adds surface roughness
   Gleb: Perfectly smooth glass. The surface is flawless. All visual complexity comes from WHAT YOU SEE THROUGH the glass, not from texture on the glass itself.

---

## Part 3: THE SECRET SAUCE - The One Thing

**The single defining characteristic that separates "looks like a WebGL demo" from "looks like a Milkinside piece"**:

> **Gleb renders LIGHT, not OBJECTS. His sphere is a vessel for holding and refracting colored light. Every visual decision serves the light. We are rendering a GLASS OBJECT and filling it with geometry. Those are opposite philosophies.**

In practical terms: Gleb's sphere contains essentially NOTHING. No wireframe. No particles. No internal geometry. It contains carefully constructed COLORED ENVIRONMENT LIGHT that, when seen through a perfect glass sphere, produces extraordinary chromatic complexity.

The glass material is the lens. The magic lives in what the lens looks at.

We put interesting things INSIDE the sphere. Gleb puts interesting things OUTSIDE the sphere and uses the sphere as a focusing/refracting instrument.

---

## Part 4: The Complete Replication Specification

Everything below is a concrete shader specification. Every value is implementable.

### 4.1 Shape

```
Shape: Perfect sphere, radius = 1.0 in world space
Silhouette: Mathematical circle, no deviation
Surface texture: None. Zero FBM. Zero scratch/fingerprint noise.
Micro-breathing: Optional - scale 0.998 to 1.002 on a 6.0s period only
Macro deformation: PROHIBITED
```

### 4.2 Material Properties

```
Type: Clear glass (not liquid, not crystal, not metal)
IOR (Index of Refraction):
  - R channel: 1.5110
  - G channel: 1.5168
  - B channel: 1.5220
  (This split causes chromatic dispersion - mandatory, not optional)

Fresnel f0: 0.03 (slightly lower than our current 0.04 for more transparency at center)
Fresnel exponent: 5.0 (standard Schlick)

Absorption (Beer's law through glass thickness):
  - Red: exp(-0.05 * thickness)   // Red absorbed more
  - Green: exp(-0.03 * thickness) // Green absorbed medium
  - Blue: exp(-0.01 * thickness)  // Blue absorbed least (glass goes slightly blue)

Roughness: 0.0 - perfectly smooth
```

### 4.3 The Environment - MULTIPLE COLORED LIGHTS

This is the core technique. Not one light. Six to eight colored lights.

```
ENVIRONMENT LIGHT SETUP (for "colorful AI sphere" recreation):

Light 1 - KEY LIGHT (dominant, main shadow caster)
  Direction: normalize(-0.8, 1.4, 0.6)  // Upper left
  Color: #EFE8D0 (warm white, slightly golden)
  Intensity: 2.0
  Angular size: medium-soft (lobe exponent 6)

Light 2 - ELECTRIC BLUE FILL
  Direction: normalize(0.7, 0.8, -0.4)  // Upper right opposite key
  Color: #0D16F5
  Intensity: 1.2
  Angular size: soft (lobe exponent 4)

Light 3 - VIOLET/PURPLE AMBIENT
  Direction: normalize(-0.4, -0.3, 0.9) // Lower front
  Color: #5a0e8a (deeper purple than #3C0E4E to avoid saturation clipping)
  Intensity: 0.8
  Angular size: very soft (lobe exponent 2)

Light 4 - MAGENTA ACCENT
  Direction: normalize(1.0, -0.5, 0.3)  // Right lower
  Color: #D10DCE
  Intensity: 0.5
  Angular size: tight (lobe exponent 10) - creates small colored gleam

Light 5 - CYAN RIM
  Direction: normalize(-0.2, 0.1, -1.0) // Back right
  Color: #18A8D3
  Intensity: 0.6
  Angular size: tight (lobe exponent 12) - creates rim glow effect

Light 6 - RED HOT ZONE (simulates heat/energy)
  Direction: normalize(0.3, -0.8, -0.5) // Bottom back
  Color: #E42424
  Intensity: 0.4
  Angular size: medium (lobe exponent 5)

ENVIRONMENT BASE:
  vec3 env = vec3(0.003, 0.003, 0.006); // Near-absolute black, tiny blue tint
```

Implementation: Build `studioEnv()` as sum of all 6 lights evaluated against ray direction.

### 4.4 The Interior - Volumetric Glow (NOT Icosahedron)

Replace the icosahedron entirely. The interior is a volumetric soft glow.

```
INTERIOR GLOW STRUCTURE:

1. CORE EMITTER (the heart of the sphere)
   Position: Center of sphere (0, 0, 0)
   Type: Radial falloff
   Radius: 0.2 (20% of sphere radius)
   Color: Mix of the two dominant colors for current state
   Intensity: 0.8
   Falloff: exp(-dist / 0.2) - sharp concentration at center

2. SECONDARY EMITTER (offset from center)
   Position: Slowly orbits, radius 0.3
   Type: Point glow
   Orbit period: 12.0 seconds
   Color: Complementary to core color
   Intensity: 0.4
   Falloff: exp(-dist*dist / 0.04)

3. CORONA BAND (equatorial glow)
   Type: Distance-based from a tilted great circle
   Tilt: 23.5 degrees from vertical (same as Earth's axial tilt)
   Width: 0.08
   Color: Mix of all environment colors
   Intensity: 0.3 * abs(sin(time * 0.15)) // Slow pulsing

4. MIST (volumetric fog inside glass)
   Density: 0.02 per unit length (very thin)
   Color: Near-black with slight state tint
   Effect: Makes the sphere appear to have depth, not be hollow
```

GLSL pseudocode for interior:
```glsl
float interiorGlow(vec3 exitPoint, float t) {
    // Core radial glow
    float coreDist = length(exitPoint);
    float core = exp(-coreDist / 0.2) * 0.8;

    // Orbiting secondary
    float orbit = 0.3;
    float orbitAngle = t * (6.28318 / 12.0);
    vec3 secondary = vec3(sin(orbitAngle), 0.1, cos(orbitAngle)) * orbit;
    float secDist = length(exitPoint - secondary);
    float sec = exp(-secDist * secDist / 0.04) * 0.4;

    // Corona band
    vec3 bandAxis = normalize(vec3(sin(0.41), cos(0.41), 0.0)); // 23.5 degree tilt
    float bandDist = abs(dot(normalize(exitPoint), bandAxis));
    float band = exp(-bandDist * bandDist / 0.0064) * 0.3 * (0.5 + 0.5 * sin(t * 0.15));

    return core + sec + band;
}
```

### 4.5 Specular Highlights

```
PRIMARY SPECULAR:
  Shininess: 480.0 (extremely tight, like a perfect glass surface)
  Color: #C8A84A (gold, hex = vec3(0.784, 0.659, 0.290))
  Intensity: 5.5

  This creates a tiny, brilliant gold star on the sphere surface.
  Position controlled by key light direction.

SECONDARY SPECULAR (softer halo around the primary):
  Shininess: 40.0
  Color: #E0CCCC (warm near-white with red tint from key light)
  Intensity: 0.12

NOTE: Do NOT use pure white (#FFFFFF) for any specular.
Warm gold for tight highlights. Warm white for soft ones.
```

### 4.6 Background Treatment

```
BASE: vec3(0.004, 0.004, 0.008) - near-black with blue tint (NOT pure black)

LIGHT BLEED (critical for the Milkinside feel):
For each colored environment light, bleed soft halos into the background
proportional to that light's intensity and roughly positioned where the sphere
would cast colored glow.

Implementation:
float lightBleed = smoothstep(0.55, 0.0, length(uv - projected_light_uv));
bgColor += lightColor * lightBleed * 0.025;

Effective colors for bleed:
- Electric blue bleed at upper right: #0D16F5 at 0.025 max
- Magenta bleed at lower right: #D10DCE at 0.015 max
- Cyan bleed behind sphere: #18A8D3 at 0.012 max

These are nearly invisible. But their absence is what makes a background
look "dead." Their presence makes it breathe.

CAUSTIC PROJECTION:
Project simplified caustic light pattern in front/behind the sphere.
Color = glassTint (the dominant interior color)
Intensity = 0.04 maximum
Pattern = sin(uv.x * 12.0 + t * 0.3) * sin(uv.y * 9.0 + t * 0.2) mapped through smoothstep
```

### 4.7 Camera and Composition

```
DISTANCE: 2.4 - 2.5 (sphere fills approximately 65% of canvas height)
POSITION: Sphere placed at y = +0.05 (slightly above center for visual weight)
ORBIT: Optional slow orbit at 60+ second period
TILT: Camera looks slightly downward (target.y = 0.0, ro.y = 0.2)

CRITICAL: Do NOT use the 45-second orbit with obvious rotation. It draws attention
to the "this is a WebGL demo" quality. If orbiting, use minimum 90 seconds.
Alternatively: Use ONLY subtle micro-drift (sin wave, 0.02 amplitude) to give life
without telegraphing rotation.
```

### 4.8 Color State System (Aether-Specific)

Map PureBrain brand states to the Gleb palette philosophy:

```
IDLE STATE:
  Core glow: #1a4d7a (deep teal-blue, echoing #18A8D3 but darker)
  Secondary: #3C0E4E (Gleb's deep violet)
  Environment lights: Use the 6-light setup above
  Gold specular: #C8A84A (mandatory)

SPEAKING STATE:
  Core glow: #6b1505 (deep hot red, more saturated than our current #6b2200)
  Secondary: #D10DCE hot magenta (from Gleb's palette)
  Environment lights: Shift light 3 to #8a0e1e red, light 4 to #E42424
  Hot core: Add intense white-orange emitter at center vec3(1.0, 0.6, 0.1)
  Gold specular: Shifts toward #FFB830 (hotter gold)

THINKING STATE:
  Core glow: #2a0a5a (deep violet, near #3C0E4E)
  Secondary: #0D16F5 (Gleb's electric blue)
  Environment lights: Shift to cool - blues and cyans dominate
  Scanning beam: Retain but make it a soft volumetric ray, not a geometric slice

LISTENING STATE:
  Core glow: #0a3a6a
  Secondary: #18A8D3 (Gleb's cyan)
  Pulsing: Core radius breathes between 0.15 and 0.25 on 2.5s period
```

---

## Part 5: Post-Processing Stack

```
BLOOM:
  Pass 1 (wide): threshold 0.8, adds 15% to bright areas
  Pass 2 (tight): threshold 1.3, adds 40% to specular peak only

  NOTE: Gleb's bloom is RESTRAINED. His bright highlights bloom but his
  mid-tones do not. Our bloom is too aggressive on mid-tones.

TONE MAPPING: ACES filmic - keep our current implementation
  col = (col*(2.51*col + 0.03)) / (col*(2.43*col + 0.59) + 0.14)

GAMMA: 0.90 - slightly more aggressive than our current 0.91
  (Lifts shadows very slightly, makes dark areas richer)

VIGNETTE:
  Width: Starts at 0.45 from center (our current 0.50 starts too close to sphere)
  Strength: Max 22% darkening (our current is 18% - increase slightly)
  This frames the sphere without making it look masked.

CHROMATIC ABERRATION (screen-space):
  Apply at silhouette edge only (where NdotV < 0.2)
  Strength: 0.006 in Red, -0.004 in Blue (split opposing)
  NOT random noise - directional fringing aligned with sphere edge tangent.

FILM GRAIN: REMOVE or REDUCE to 0.0015 max
  Gleb's renders look CLEAN. Grain reads as "procedural art experiment."
  Remove it from highlights and midtones entirely. Grain only in pure black areas.
```

---

## Part 6: What NOT to Put in the Sphere

This list is as important as the positive specifications:

```
PROHIBITED INTERIOR ELEMENTS:
- Wireframe icosahedron (geometric, reads as "tech demo")
- Particle systems (reads as "shader playground")
- Scanning beam as a visible geometric plane
- Hexagonal prism shapes
- Neural network visualizations
- Grid patterns
- Sine wave ripples visible through the glass
- Any sharp-edged geometry

WHY: Gleb's interiors are LIGHT, not objects. The moment you put a visible
     geometric structure inside the glass, the viewer's brain processes it as
     "a thing inside a ball" rather than "a ball of pure light." The former
     is a toy. The latter is an artwork.

PERMITTED INTERIOR ELEMENTS:
- Volumetric colored glow (radial, soft)
- Slow-orbiting point emitters (invisible themselves, cast glow only)
- Corona bands (equatorial emissive zones)
- Very soft fog/mist for depth
```

---

## Part 7: Common Drift Patterns to Avoid

These are the traps that previous iterations fell into:

### Trap 1: The Hex Prism Problem
Multiple iterations added hexagonal frames around the sphere. Gleb never uses frames. The sphere exists alone in void. Frames make it look like a logo. The sphere IS the identity.

### Trap 2: The Noisy Surface Problem
FBM noise on the sphere surface makes it look like a blob of water or biological tissue. Gleb's surfaces are GLASS - optically perfect.

### Trap 3: The Wrong Black Problem
Backgrounds of pure `#000000` look digital and flat. The subtle `#020204` blue-black is what makes Gleb's backgrounds feel like photographic studio void rather than a black HTML element.

### Trap 4: The Single Light Problem
One warm white studio key light produces nice glass. Multiple colored lights produce GLEB glass. The colored environment is what creates the chromatic richness inside the sphere.

### Trap 5: The White Highlight Problem
White specular highlights signal plastic/ceramic. Gold specular highlights signal precious glass/crystal. This is a single vec3 value change that transforms perceived material quality.

### Trap 6: The Too-Much-Interior-Activity Problem
Micro-particles, scanning beams, rotating geometry, firing sparks - all of this makes the sphere look BUSY. Gleb's spheres feel CALM even when they contain intense color. The activity is in the color, not in the geometry.

---

## Part 8: Implementation Priority Order

If implementing incrementally, apply changes in this order for maximum visual impact per step:

**Step 1 (highest impact)**: Remove icosahedron wireframe, replace with volumetric core glow
**Step 2**: Add colored environment lights (change `studioEnv()` to use 6 lights)
**Step 3**: Change specular highlight color from ice-white to gold (#C8A84A)
**Step 4**: Remove surface FBM noise (set scratch and fingerprint to 0.0)
**Step 5**: Add light bleed to background from sphere color
**Step 6**: Adjust color palette to higher saturation (widen gamut toward Gleb's extremes)
**Step 7**: Fine-tune bloom (more restrained on mid-tones)

After Step 3 alone you will see a significant quality jump. After Step 4 you will see the sphere start to look "clean." After Steps 1-6 complete, it will start to look like a Milkinside piece.

---

## Part 9: Shader Code Fragments (Ready to Implement)

### Multi-light environment function

```glsl
vec3 studioEnv(vec3 dir, vec3 stateColor) {
    // Base: near-absolute black studio
    vec3 env = vec3(0.003, 0.003, 0.006);

    // LIGHT 1: Key - warm white, upper left
    vec3 L1dir = normalize(vec3(-0.8, 1.4, 0.6));
    float L1 = pow(max(0.0, dot(dir, L1dir)), 6.0);
    env += vec3(1.0, 0.96, 0.88) * L1 * 2.0;

    // LIGHT 2: Electric blue fill - upper right
    vec3 L2dir = normalize(vec3(0.7, 0.8, -0.4));
    float L2 = pow(max(0.0, dot(dir, L2dir)), 4.0);
    env += vec3(0.051, 0.086, 0.961) * L2 * 1.2; // #0D16F5

    // LIGHT 3: Violet ambient - lower front
    vec3 L3dir = normalize(vec3(-0.4, -0.3, 0.9));
    float L3 = pow(max(0.0, dot(dir, L3dir)), 2.0);
    env += vec3(0.353, 0.055, 0.541) * L3 * 0.8; // #5a0e8a

    // LIGHT 4: Magenta accent - right lower
    vec3 L4dir = normalize(vec3(1.0, -0.5, 0.3));
    float L4 = pow(max(0.0, dot(dir, L4dir)), 10.0);
    env += vec3(0.820, 0.051, 0.808) * L4 * 0.5; // #D10DCE

    // LIGHT 5: Cyan rim - back right
    vec3 L5dir = normalize(vec3(-0.2, 0.1, -1.0));
    float L5 = pow(max(0.0, dot(dir, L5dir)), 12.0);
    env += vec3(0.094, 0.659, 0.827) * L5 * 0.6; // #18A8D3

    // LIGHT 6: Red hot zone - bottom back
    vec3 L6dir = normalize(vec3(0.3, -0.8, -0.5));
    float L6 = pow(max(0.0, dot(dir, L6dir)), 5.0);
    env += vec3(0.894, 0.141, 0.141) * L6 * 0.4; // #E42424

    // State color bleed into environment (subtle)
    float stateLobe = pow(max(0.0, dot(dir, normalize(vec3(0.0, 0.0, -1.0)))), 2.0);
    env += stateColor * stateLobe * 0.05;

    return env;
}
```

### Gold specular highlight

```glsl
// Replace ice-white specular with gold
vec3 goldSpec = vec3(0.784, 0.659, 0.290); // #C8A84A
float spec_tight = pow(max(dot(perturbN, H_key), 0.0), 480.0) * 5.5;
float spec_soft  = pow(max(dot(perturbN, H_key), 0.0), 40.0)  * 0.12;

reflLayer += goldSpec * spec_tight;
reflLayer += vec3(0.88, 0.80, 0.78) * spec_soft; // warm near-white
```

### Volumetric interior glow (replace icosahedron)

```glsl
float interiorGlow(vec3 p, float t, float sMix, float tMix) {
    float glow = 0.0;

    // Core emitter - concentrated center
    float coreDist = length(p);
    glow += exp(-coreDist / 0.22) * 0.85;

    // Orbiting secondary emitter
    float orbitAngle = t * (6.28318 / 12.0);
    vec3 orbitPos = vec3(sin(orbitAngle), 0.1, cos(orbitAngle)) * 0.3;
    float secDist = length(p - orbitPos);
    glow += exp(-secDist * secDist / 0.05) * 0.45;

    // Corona band (tilted 23.5 degrees)
    vec3 bandNormal = normalize(vec3(0.0, cos(0.4102), sin(0.4102)));
    float bandDist = abs(dot(normalize(p), bandNormal));
    float pulseFactor = 0.5 + 0.5 * sin(t * 0.15);
    glow += exp(-bandDist * bandDist / 0.007) * 0.35 * pulseFactor;

    // Speaking state hot core
    glow += exp(-coreDist / 0.1) * sMix * 0.6;

    return clamp(glow, 0.0, 2.0);
}

// Color for the glow (replace icoColor calculation)
float glowAmount = interiorGlow(interiorP, t, sMix, tMix);
vec3 interiorColor = stateColor * glowAmount * (0.7 + audio * 0.5);
// Add hot white core during speaking
interiorColor += vec3(1.0, 0.7, 0.2) * sMix * exp(-length(interiorP)/0.1) * 0.8;
```

### Surface noise removal

```glsl
// REMOVE these lines entirely:
// float scratch = fbm(p * 28.0 + t * 0.005) * 0.003;
// float fingerprint = fbm(p * 8.0) * 0.0015;

// Replace map() body with:
float map(vec3 p) {
    float breathe = sin(t * (6.28318 / 6.0)) * 0.5 + 0.5;
    float sphereRadius = 1.0 + breathe * 0.004 - 0.002; // Extremely subtle breathing

    float sphere = length(p) - sphereRadius;

    // ONLY audio ripple when active
    float ripple = 0.0;
    if (uAudioLevel > 0.1) {
        float r = length(p);
        ripple = sin(r * 8.0 - t * 3.5) * uAudioLevel * 0.004;
    }

    return sphere + ripple;
}
```

---

## Part 10: The "Passing Test" - How to Know You've Got It

The implementation is correct when:

1. You can show the rendered sphere to someone who has never heard of Milkinside and they say "that looks like premium CGI" without prompting
2. The sphere looks like it could have been created in Cinema 4D with Redshift renderer - not like something that runs in a browser
3. The interior does not have visible geometric structure - it appears to glow from within with color
4. The specular highlight is gold, not white, and is smaller than you think it should be
5. The background is not black - it has almost-invisible colored halos where the sphere's colored light touches the void
6. The sphere silhouette is a perfect circle, always, in every frame
7. Removing sound/audio leaves the sphere looking exactly as good - it should not depend on audio to be beautiful

---

## Memory Written

Path: `.claude/memory/agent-learnings/ui-ux-designer/2026-02-20--gleb-kuznetsov-sphere-visual-analysis.md`
Type: teaching
Topic: Forensic visual analysis of Milkinside sphere aesthetic + concrete shader replication guide

---

## Sources

- [Colorful AI sphere by Gleb Kuznetsov](https://dribbble.com/shots/14194855-Colorful-AI-sphere-by-Gleb-Kuznetsov) - Color palette extraction
- [AI sphere visual design by Milkinside](https://dribbble.com/shots/24197602-AI-sphere-visual-design-by-Milkinside) - 2024 direction analysis
- [Glass reflection CGI by Milkinside](https://dribbble.com/shots/20098860-Glass-reflection-CGI-by-Milkinside) - Material analysis
- [Crystal sculpture](https://dribbble.com/shots/14486416-Crystal-sculpture) - Faceting and specular study
- [Glass blower visual](https://dribbble.com/shots/17066462-Glass-blower-visual) - Emissive/subsurface technique
- [Red Dot Interview with Milkinside 2022](https://www.red-dot.org/magazine/interview-with-milkinside-2022) - Design philosophy
- [Spaces Lovers Magazine interview](https://spaces.is/loversmagazine/interviews/gleb-kuznetsov) - Philosophy quote: "exquisitely detailed and fluid, immersive, and full of life"
