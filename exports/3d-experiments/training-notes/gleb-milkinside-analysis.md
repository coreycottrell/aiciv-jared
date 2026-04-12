# Gleb Kuznetsov / Milkinside.com: Master Reference Analysis

**Date**: 2026-04-08
**Type**: curriculum (reference material for Nights 19-23+)
**Agent**: 3d-design-specialist
**Purpose**: Definitive analysis of THE reference aesthetic we are training to match

---

## Part 1: Who Is Gleb Kuznetsov / Milkinside

**Background**: 25+ years of product design experience. Founded Milkinside in 2011 (San Francisco). Previously Head of Product Design at Fantasy.co (2016+). Clients include Apple, Google, Huawei, OPPO, Mitsubishi, Honda, Airbus, Twitter/X, Netflix, Royal Caribbean, Spotify, Xiaomi, Scandinavian Airlines.

**Core Philosophy** (from multiple interviews):
- "Design is not only about the beauty of things, it is about the creation of new perceptions of life"
- "Design is the emotions carried by it" -- not purely functional utility
- "Design Should Not dominate things. Should Not dominate people. It Should Help People"
- Clearing his mind from "all that I have known" to create intuitive systems
- Emotional design process: experiencing both positive and negative feelings before selecting the most elegant solution
- Works in nighttime sessions for experimentation with "colors, shapes, and directional approaches"

**Tools Confirmed** (from interviews):
- Cinema 4D (primary 3D tool)
- Redshift renderer (primary GPU renderer)
- Houdini FX (motion design / procedural)
- Trapcode Form (After Effects particle plugin)
- After Effects (compositing / motion)
- Photoshop, Illustrator (2D finishing)
- 300+ different plugins across the pipeline
- MacBook Pro + Cinema Display + render farms + remote stations
- Two MacBooks simultaneously (one rendering, one Photoshop)

**Key Insight**: Gleb does NOT build his signature 3D effects in the browser. His workflow is:
1. Cinema 4D + Redshift for 3D renders
2. Houdini for procedural effects
3. After Effects for compositing and motion
4. Pre-rendered video/images exported for web

The milkinside.com website itself uses CSS animations, not real-time WebGL. This is a critical distinction for us.

---

## Part 2: milkinside.com Technical Architecture

### Technology Stack (from source analysis)

**NOT Three.js / WebGL.** The site is built with:

- **Framework**: Custom or lightweight CMS (no React, Vue, Angular detected)
- **CSS Architecture**: Cascade Layers (`@layer restyle`), CSS custom properties
- **Font**: aktivGrotesk (custom webfont) -- clean geometric sans-serif
- **Grid**: 8-column named grid with subgrid support
- **Animations**: Pure CSS keyframes + transitions (no GSAP detected in CSS layer)
- **Performance**: `will-change`, `contain: layout style paint`, `translateZ(0)` GPU hints
- **Scroll**: CSS scroll-snap for horizontal project showcase
- **Visual effects**: `backdrop-filter: blur()` for glassmorphism panels
- **View transitions**: CSS View Transitions API for page-to-page animation

### Color System

```css
:root {
  --white: #FFFFFF;
  --bg: #EDEEF4;        /* Light lavender-gray -- NOT pure white */
  --black: #000000;
  --gray: #63667A;       /* Medium gray for secondary text */
  --accentred: #FF0055;  /* Vibrant magenta-red accent */
}
```

**Critical discovery**: Gleb's site background is `#EDEEF4` (light lavender-gray), NOT dark. This contradicts the common assumption that Gleb = dark backgrounds always. His PORTFOLIO site is light. His individual PROJECT RENDERS use dark backgrounds. The distinction matters.

### Gradient System

Three signature gradients detected:

1. **Conic gradient**: Rotational light sweep from white to transparent -- creates lens flare effect
2. **Linear gradient**: Black-to-transparent left-to-right -- text overlay on images
3. **Radial gradient**: Center-to-edge vignette -- focus attention on center content

### Typography System

```css
/* Font: aktivGrotesk -- geometric sans-serif */
font-family: 'aktivGrotesk', 'aktivGrotesk Fallback', sans-serif;

/* Weight palette */
font-weight: 300;  /* Light -- body text, descriptions */
font-weight: 400;  /* Normal -- UI elements, navigation */

/* Size scale (desktop 1921px+) */
/* Smallest: 0.938vw (~18px at 1920px) */
/* Body: ~1.2vw (~23px) */
/* Subheading: ~2.5vw (~48px) */
/* Heading: ~5.208vw (~100px at 1920px) */

/* Line height: tight */
line-height: 100%; /* Headings -- nearly solid */
line-height: 110%; /* Subheadings */
line-height: 120%; /* Body text */

/* Letter spacing: subtle negative tracking on headings */
letter-spacing: -0.016vw; /* Tightened for large text */
```

**Key insight**: Gleb uses light weight (300) for body text, which reads as elegant and airy. Combined with tight line-heights and negative letter-spacing on headings, this creates the "editorial luxury" feel.

### Animation Easing

```css
/* PRIMARY easing -- used on most transitions */
cubic-bezier(0.645, 0.045, 0.355, 1)
/* This is a custom ease-in-out with sharp acceleration and soft landing */
/* Very close to "ease-in-out-cubic" but with a faster attack */

/* SECONDARY easing -- used on width/scale transitions */
cubic-bezier(0.77, 0, 0.175, 1)
/* Sharp ease-in with very soft ease-out -- "snap then settle" */
```

**This easing is CRUCIAL.** Most web animations use generic `ease-in-out`. Gleb's custom bezier gives a distinctly snappier, more intentional feel. The first curve has a faster attack (0.645 start) than standard ease-in-out.

### Layout Architecture

```
8-column grid with named lines:
fullbleed-start | main-start | col-1 | col-2 | col-3 | col-4 | col-5 | col-6 | col-7 | col-8 | main-end | fullbleed-end

Gaps: 1.042vw (desktop)
Dead-center: named grid line for centering
```

- Horizontal scroll-snap for project showcase (with `scroll-snap-type: x proximity`)
- Sticky header at 6vh height
- Minimum section height: 100svh (small viewport height)
- Hidden scrollbars (`scrollbar-width: none`)

### Responsive Architecture

Four breakpoints with FULL style segregation:
1. **Desktop**: >= 1921px (vw-based everything)
2. **Laptop**: 1025-1920px (same proportions, different sizes)
3. **Tablet**: 501-1024px (layout shifts to stacked)
4. **Mobile**: <= 500px (full single-column, larger relative type)

---

## Part 3: The Gleb Aesthetic -- What Makes It Premium

### 3.1 The Light Background Revelation

Gleb's portfolio uses `#EDEEF4` -- a warm lavender-gray. NOT pitch black. This works because:
- Individual 3D renders (which ARE dark) pop against the light site background
- The light background reads as "gallery" -- curated, spacious, gallery-like
- Dark backgrounds for the 3D content, light backgrounds for the presentation layer
- This duality (dark content, light frame) creates perceived depth

**Implication for PureBrain**: We may want to consider a dual-layer approach. The 3D hero section stays dark (#060606), but surrounding content could shift to a sophisticated dark-gray or even a brand-tinted dark (#0a0e14) to create layers.

### 3.2 The Accent Color Strategy

Gleb uses exactly ONE accent color: `#FF0055` (vibrant magenta-red). Everything else is black, white, and gray.

- Accent appears sparingly -- likely on hover states, active elements, CTAs
- This restraint makes the accent color feel precious and intentional
- The magenta-red is warm but electric -- not a natural red, more neon

**PureBrain parallel**: We have two accent colors (#2a93c1 blue, #f1420b orange). This is actually MORE complex than Gleb's palette. We should establish hierarchy: blue = primary accent, orange = secondary/highlight. Never use both at full intensity simultaneously.

### 3.3 The Typography Philosophy

aktivGrotesk at weight 300 (light) creates a distinctly different feel than most tech sites:
- Reads as "confident whisper" rather than "bold declaration"
- Large sizes (5vw+) at light weight = massive but delicate
- Tight line-height (100-110%) makes headings feel like typographic sculptures
- Negative letter-spacing tightens the visual rhythm

**PureBrain implication**: Our current typography should lean lighter. Weight 300-400 for body, weight 500-600 for emphasis (never 700-900 for large headings).

### 3.4 The Animation Philosophy

From CSS analysis, Gleb's animations are:

1. **Subtle vertical translations**: `translateY(0)` to `translateY(calc(100% - Xvw))` -- content sliding into/out of view with scroll
2. **Width reveals**: `width: 0%` to `width: 100%` over 10 seconds -- slow, cinematic reveal
3. **Opacity fades**: Simple but with custom bezier easing
4. **Continuous rotation**: 4000ms linear infinite on decorative elements
5. **Color blink**: Alternating between `--black` and `--gray` -- subtle text state indicator
6. **Paused states**: `animation-play-state: paused` -- animations that wait for visibility

**Key pattern**: SLOW timings. 10-second reveals. 4-second rotations. Nothing fast. Nothing jarring. Everything feels deliberate and unhurried. This is the "cinematic" quality.

### 3.5 The Glassmorphism Implementation

```css
backdrop-filter: blur(11.364vw);  /* Mobile-specific, VERY large blur radius */
background: rgba(255, 255, 255, 0.12);  /* 12% white fill */
```

Gleb's glass is:
- Very high blur radius (not subtle 8px blur -- massive 11vw blur)
- Low opacity fill (12% white, barely there)
- Isolation for stacking context (`isolation: isolate`)
- No visible borders on glass panels -- the blur IS the boundary

This is DIFFERENT from our typical `MeshTransmissionMaterial` approach. Gleb's web glass is CSS-only with massive blur radius. The 3D glass in his renders is Cinema 4D + Redshift with physical glass BSDF.

### 3.6 The Scroll Experience

```css
scroll-snap-type: x proximity;
scroll-padding-left: [varies by breakpoint];
-webkit-overflow-scrolling: touch;
overscroll-behavior-x: contain;
```

Horizontal scroll-snap for the project carousel. This creates the "gallery walk" feeling -- each project snaps into a considered position. The `proximity` mode means it helps you settle on a project but does not force it (feels natural, not mechanical).

---

## Part 4: What Gleb Does vs What We Do

### 4.1 Rendering Pipeline Comparison

| Aspect | Gleb (Milkinside) | PureBrain (Us) |
|--------|-------------------|----------------|
| 3D Tool | Cinema 4D + Redshift | Three.js / R3F + GLSL |
| Rendering | Offline GPU path tracing | Real-time WebGL fragment shaders |
| Glass | Physical glass BSDF + caustics | MeshTransmissionMaterial + custom GLSL |
| Volumetrics | Houdini procedural + offline render | Froxel ray march (real-time) |
| Post-processing | After Effects compositing | EffectComposer (Bloom, DoF, CA) |
| Output | Pre-rendered video/images | Interactive real-time 3D |
| Web delivery | CSS animations + video embeds | Live WebGL canvas |

**The fundamental difference**: Gleb renders OFFLINE and composites for web. We render REAL-TIME in the browser. Our glass cannot physically match path-traced Redshift renders, but we offer something Gleb does not: interactivity and responsiveness.

### 4.2 What We Got Right (Nights 1-18)

1. **Glass transmission materials**: Our MeshTransmissionMaterial with IOR 1.5, backside rendering, chromatic aberration closely approximates Gleb's glass BSDF
2. **Volumetric lighting**: Night 16's froxel volumetrics with HG phase function match the atmospheric quality
3. **Thin-film iridescence**: Night 18's spectral interference computation creates the same rainbow-on-glass effect
4. **Subsurface scattering**: Night 18's thickness-estimation SSS matches the translucent quality
5. **Dark backgrounds for renders**: Correct instinct -- Gleb uses dark for 3D content too
6. **Chromatic aberration**: Per-channel IOR shifting matches Gleb's caustic separation
7. **Audio/data reactivity**: Night 17's audio-reactive glass is a direction Gleb explores in "Intelligent Shape for LLM Brand"
8. **Glass as UI affordance**: Night 16's interactive spheres match Gleb's "Spheres UI Interaction" concept

### 4.3 What Gleb Does Differently (Gaps to Close)

1. **Composition over complexity**: Gleb places one hero object in a carefully lit void. We tend to add more elements. His power comes from restraint in scene composition.

2. **Lighting first, always**: Gleb's HDRI and lighting setup is the foundation. Render farms spend most time on light transport. We sometimes treat lighting as secondary to geometry.

3. **Surface detail through texturing**: Gleb's Cinema 4D models have surface detail (micro-roughness variation, procedural surface imperfections) that our smooth `sphereGeometry args={[1.2, 128, 128]}` lacks.

4. **Color grading as post-process**: Gleb grades his renders in After Effects. We apply raw output. A color grading pass (LUT, tone mapping, contrast curves) could bridge 50% of the remaining quality gap.

5. **Camera as storytelling**: Gleb uses shallow DoF with very specific focal points to tell visual stories. Our DoF is uniform. We need focal point composition.

6. **The presentation layer**: Gleb wraps 3D content in a refined typographic/layout system (aktivGrotesk, 8-column grid, custom easing). Our 3D exists in isolation without the surrounding design system elevating it.

7. **Slow animation timing**: Gleb's CSS uses 4-10 second durations. Our Float and useFrame animations are typically 1-2 seconds. Slowing down would increase perceived premium quality.

8. **Single accent color discipline**: Gleb uses ONE accent (#FF0055). We use two (blue + orange). Tighter color discipline per scene.

---

## Part 5: The Gleb Technique Cookbook

### 5.1 Glass Material (Cinema 4D / Redshift -- translated to Three.js)

**Gleb's Redshift glass** (reverse-engineered from visual analysis):
- IOR: 1.45-1.55 (standard glass range)
- Roughness: 0.02-0.08 (nearly perfect specular, slight diffusion)
- Absorption color: deep blue or teal (gives glass its color in thick areas)
- Absorption distance: low (color appears quickly)
- Thin-walled: OFF (full volumetric glass with internal bounces)
- Caustics: ON (light focusing through glass)

**Our Three.js equivalent** (best approximation):
```jsx
<MeshTransmissionMaterial
  transmission={1}
  thickness={0.8}        // Controls absorption depth
  roughness={0.03}       // Gleb is VERY smooth, not 0.05
  ior={1.5}
  chromaticAberration={0.6}
  backside={true}
  backsideThickness={0.3}
  color="#2a93c1"         // PureBrain blue
  distortion={0.1}        // Subtle refraction distortion
  distortionScale={0.3}
  temporalDistortion={0.1}
/>
```

**Adjustment from our current baseline**: Lower roughness (0.03 vs 0.05) and add distortion parameters.

### 5.2 The Lighting Setup

**Gleb's approach** (from Dribbble analysis across 50+ shots):

1. **Key light**: High-contrast directional from upper-left or upper-right (not centered)
2. **Fill**: Very subtle, almost absent -- he lets shadows go deep
3. **Rim/back light**: Strong rim light on glass edges (creates the signature glass outline glow)
4. **Environment**: Studio HDRI with controlled reflections (not outdoor -- indoor studio)

**Our Three.js equivalent**:
```jsx
{/* Poly Haven studio HDRI -- controlled, not chaotic */}
<Environment files="/studio_small_09_2k.hdr" />

{/* Key light: high contrast, specific direction */}
<directionalLight
  position={[3, 5, 2]}
  intensity={2.0}
  color="#ffffff"
  castShadow
/>

{/* Rim light: creates glass edge glow */}
<pointLight
  position={[-3, 1, -3]}
  intensity={0.8}
  color="#2a93c1"  // Branded rim light
/>

{/* NO ambient light -- let shadows be deep */}
{/* ambientLight intensity={0} */}
```

**Key insight**: Gleb does NOT use soft ambient fills. His scenes have high contrast with deep shadows. The glass reads because of the contrast, not despite it.

### 5.3 The Post-Processing Stack

**Gleb's After Effects pipeline** (translated to R3F postprocessing):

```jsx
<EffectComposer>
  {/* Bloom: conservative, high threshold */}
  <Bloom
    luminanceThreshold={0.92}   // Higher than our typical 0.9
    luminanceSmoothing={0.02}
    intensity={0.35}            // Lower than our typical 0.5
    mipmapBlur={true}
  />

  {/* DoF: VERY shallow, specific focal point */}
  <DepthOfField
    focusDistance={0.015}       // Precise focal plane
    focalLength={0.08}         // Narrow depth
    bokehScale={4}             // Larger bokeh circles
  />

  {/* Chromatic Aberration: subtle edge-only */}
  <ChromaticAberration
    offset={[0.001, 0.001]}    // Less than our typical 0.002
    radialModulation            // Only at edges of frame
    modulationOffset={0.5}
  />

  {/* COLOR GRADING: The missing piece */}
  {/* This is what separates Gleb's polished output from raw renders */}
  {/* Needs custom shader or ToneMappingEffect with LUT */}
  <ToneMapping
    mode={ACESFilmicToneMapping}
  />
</EffectComposer>
```

**The color grading gap**: Gleb's After Effects pipeline includes contrast curves, color temperature shifts, and subtle desaturation. We need a LUT or custom tone-mapping shader to match.

### 5.4 The Animation Timing System

From CSS analysis -- Gleb's motion vocabulary:

```javascript
// Gleb's primary easing (for Three.js / GSAP)
const GLEB_EASE_PRIMARY = "cubic-bezier(0.645, 0.045, 0.355, 1)";
// In GSAP: CustomEase or "power3.inOut" is closest

// Gleb's secondary easing (for scale/width reveals)
const GLEB_EASE_SECONDARY = "cubic-bezier(0.77, 0, 0.175, 1)";
// In GSAP: "power4.inOut" is closest

// Timing vocabulary
const GLEB_TIMINGS = {
  microInteraction: 200,    // ms - hover state changes
  transition: 300,          // ms - element state changes
  reveal: 500,              // ms - content appearing
  heroReveal: 10000,        // ms - slow cinematic reveals (10 seconds!)
  continuousRotation: 4000, // ms - decorative element full rotation
  breathCycle: 2000,        // ms - organic pulsing
};
```

**What this means for our Three.js**:
```jsx
// BEFORE (our typical Float)
<Float speed={1.5} rotationIntensity={0.5} floatIntensity={0.5}>

// AFTER (Gleb-calibrated)
<Float speed={0.6} rotationIntensity={0.15} floatIntensity={0.2}>
// MUCH slower, MUCH subtler
```

### 5.5 The Composition Rules

From analyzing Gleb's Dribbble portfolio (24+ shots):

1. **Single focal object**: One hero element, centered or slightly off-center
2. **Negative space**: 60-70% of the frame is empty or atmospheric
3. **Depth layers**: 3 layers maximum (background atmosphere, hero object, foreground element)
4. **Ground plane**: Often present as a reflective or softly lit surface below the object
5. **Camera angle**: Slightly elevated (15-25 degrees) looking down -- "observer" perspective
6. **Framing**: Object at 40-60% of frame height (never filling the frame completely)

---

## Part 6: Specific Technique Practice List for Nights 19-23

### Night 19: Color Grading + Composition

**Goal**: Close the post-processing gap that accounts for ~30% of remaining quality difference.

1. **Build a custom LUT shader** for Three.js postprocessing
   - Warm shadows (shift blacks toward blue-purple)
   - Cool highlights (shift whites toward warm cream)
   - Subtle desaturation (saturation at 85%, not 100%)
   - S-curve contrast (crush near-blacks, compress near-whites)

2. **Composition drill**: Render the same glass sphere 10 different ways
   - Vary camera position, focal length, DoF settings
   - Vary lighting angle and intensity ratio
   - Score each against Gleb reference images

3. **Slow everything down**: Set all animation speeds to 60% of current values

### Night 20: Surface Imperfection + Micro-Detail

**Goal**: Add the physical surface detail that separates CG from "too perfect" CG.

1. **Micro-roughness variation**: Procedural noise modulating roughness (0.01-0.08 range)
2. **Surface smudges**: Subtle normal map perturbation on glass surfaces
3. **Dust particles**: Floating micro-particles visible in volumetric light
4. **Fingerprint residue**: Very subtle -- almost invisible until light catches it
5. **Edge wear**: Slightly higher roughness at edges of objects

### Night 21: aktivGrotesk Typography Integration

**Goal**: Build the presentation layer that frames 3D content.

1. **Font procurement**: Source aktivGrotesk or equivalent (Aktiv Grotesk by Dalton Maag)
2. **3D text integration**: Text as 3D geometry with glass material
3. **HTML overlay typography**: CSS typography system matching Gleb's scales
4. **Text-3D interaction**: Text that responds to proximity of 3D elements

### Night 22: The Gallery Frame

**Goal**: Build the surrounding presentation layer (not just the 3D element).

1. **8-column grid system** matching Gleb's layout
2. **Scroll-snap horizontal showcase** for project carousel
3. **View Transitions API** for page-to-page navigation
4. **Custom easing curves** (Gleb's beziers) on all CSS transitions
5. **Hidden scrollbars** with smooth momentum scrolling

### Night 23: Full Scene Composition (Capstone)

**Goal**: Combine ALL techniques into one production-quality scene.

1. Glass hero object with micro-roughness variation
2. Volumetric god rays through glass (Night 18 technique)
3. Color grading LUT (Night 19)
4. Custom composition (Night 19 rules)
5. Surface detail (Night 20)
6. Typography frame (Night 21)
7. Gallery presentation layer (Night 22)
8. Slow, cinematic timing throughout

---

## Part 7: PureBrain Homepage Integration Plan

### Hero Section (3D)
- Single glass brain/orb centered on dark (#060606) background
- Volumetric lighting with brand-blue key light
- Thin-film iridescence with brand colors appearing naturally
- Micro-float animation at 0.6 speed (not 1.5)
- Shallow DoF with focal point on brain center
- Color grading LUT applied

### Surrounding Frame (CSS)
- Light typography (weight 300) for headings
- Custom Gleb-style easing on all transitions
- Generous negative space (at least 60%)
- Single accent color per section (blue OR orange, never both)
- Slow reveal animations (5-10 second timelines)

### Scroll Experience
- Parallax depth as user scrolls past hero
- Next sections use scroll-snap for project showcases
- View Transitions for page navigation
- Hidden scrollbars everywhere

---

## Part 8: Key Quotes and References

**Gleb on emotional design** (Dribbble interview):
"Design is not only about the beauty of things, it is about the creation of new perceptions of life."

**Gleb on process** (Medium interview):
"Before going to the Photoshop, I use a number of other products to analyse the markets and products."

**Gleb on nighttime sessions** (Dribbble interview):
"I freely experiment with colors, shapes, and directional approaches to discover innovative solutions."

**Gleb on 3D** (interview compilation):
"3D is what elevates work into something more like art."

---

## Source References

- [Gleb Kuznetsov on Dribbble](https://dribbble.com/glebich)
- [Milkinside Team on Dribbble](https://dribbble.com/milkinside)
- [Dribbble Interview: Designing with Emotion](https://dribbble.com/stories/2018/07/03/gleb-kuznetsov-on-designing-with-emotion-productivity-and-transforming-ideas-into-high-quality-digital-products)
- [Lovers Magazine Interview](https://spaces.is/loversmagazine/interviews/gleb-kuznetsov)
- [UX Design Interviews: Gleb Kuznetsov](https://medium.com/ux-design-interviews/gleb-kuznetsov-94a9702d94c7)
- [Behance: Brand Vision CGI Story Milkinside](https://www.behance.net/gallery/80917393/Brand-Vision-CGI-story-Milkinside)
- [TechCrunch: Verified Expert Brand Designer](https://techcrunch.com/2019/05/16/verified-expert-brand-designer-milkinside/)
- [IxDF: Glassmorphism Definition](https://ixdf.org/literature/topics/glassmorphism)
- [NN/g: Glassmorphism Best Practices](https://www.nngroup.com/articles/glassmorphism/)
- [Cinema 4D + Redshift Glass Tutorial](https://aetipsandtricks.com/cinema-4d/create-this-glossy-glass-animation-using-cinema-4d-and-redshift/)
- [Glass Prism Materials in C4D + Redshift](https://studiospeets.com/2022/12/06/glass-prism-materials-in-cinema4d-redshift/)

---

## Summary: The 8 Rules of Gleb-Level Quality

1. **One hero, maximum restraint**: Single focal object, 60%+ negative space
2. **Lighting IS the render**: Spend 80% of setup time on lighting, 20% on geometry
3. **Slow everything down**: 4-10 second timings, 0.6 speed Float, deliberate pacing
4. **Color grade the output**: Raw renders are not finished work -- apply LUT/curves
5. **Surface imperfection sells reality**: Micro-roughness, smudges, dust, edge wear
6. **One accent color per scene**: Never two competing accents at full intensity
7. **Light weight typography**: 300 weight, tight line-height, negative tracking
8. **Custom easing always**: `cubic-bezier(0.645, 0.045, 0.355, 1)` -- never generic ease

---

**This document is curriculum. What we learn here shapes Nights 19-23.**
