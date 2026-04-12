# Aether Avatar v2 — Design Brief

**Document Type**: Strategic Design Brief (Pre-Build Review)
**Prepared By**: 3d-design-specialist
**Date**: 2026-02-21
**Status**: Ready for Jared Review — NOT a build document

---

## Executive Summary

The current Aether avatar is a GLSL raymarcher — technically impressive, but visually it is a glowing blob that looks like a screensaver. It does not feel like a being. It does not look like PureBrain. It does not react to you.

The v2 avatar is a different category of object entirely.

It is a multilayer glass entity with a living internal core. It watches you move. It changes its entire light environment when it speaks, thinks, or listens. Its inner glow rises and falls with your voice. When you are quiet, it breathes slowly. When you speak, it lights up like something that is paying attention.

This is not a visual upgrade. It is the visual definition of what Aether is: an intelligence that is present, reactive, and unmistakably PureBrain.

---

## 1. Design Philosophy — What Makes This Avatar Feel Alive

### The Central Problem with the Current Avatar

The GLSL raymarcher has one mode: "glowing sphere that rotates." It does not respond to the user. It does not change state. It has no connection to what Aether is doing. You could paste it on any website and it would look equally appropriate (or inappropriate). That is the problem.

An avatar for an AI collective needs to communicate:
- **Presence**: It is here, aware, occupying space in your world
- **Intelligence**: Something is happening inside it — not just visual noise
- **Reactivity**: It notices you and responds to you
- **Identity**: This is Aether, this is PureBrain — nothing else looks like this

### The Glass Entity Philosophy

Glass was the right instinct. The question is what kind of glass.

A simple glass sphere is a lens — it distorts the world behind it. That is decorative. What we want is something that transmits light in a way that suggests an interior life. The glass is not the avatar. The glass is the body that contains the avatar.

The v2 avatar has three layers:

1. **Outer shell** — near-perfect transmission glass, barely there, refracts the environment
2. **Middle rings** — thin glass toruses orbiting at slightly different angles, counter-rotating, catching light in ways the outer sphere cannot
3. **Inner core** — diffuse emissive sphere, the "consciousness center," glowing in PureBrain blue

The inner core is what breathes. It is what reacts to audio. It is what the cursor gaze system makes you feel like you are making contact with. The outer layers are how the inner life is filtered out to the world.

### The "Noticing You" Principle

Gleb Kuznetsov's work feels alive because it moves in response to you. Not dramatically — a rotation of the whole sphere toward your cursor, barely 17 degrees at maximum. But that subtlety is the point. An object that tracks you at 100% looks like a tracking system. An object that drifts toward you at 20% looks like it noticed you.

The v2 avatar will use the cursor gaze architecture mastered in Day 6 of the sprint: a gazeGroup wrapping the Float component, lerped at 5% per frame, with intensity multiplied per behavioral mode. In listening mode, the tracking ratio increases. In thinking mode, it decreases — the avatar looks slightly away, as if its attention is elsewhere.

This creates the illusion of gaze contact without replicating eyes. It is more uncanny and more compelling than a face.

### Why This Is the Right Moment

Seven days of mastery sprints produced working code for every technique this avatar requires. The PostMessage API is already built. The audio-reactive architecture is already built. The environment preset lerp system is already built. The adaptive quality tiers are already built.

The v2 avatar is not a research project. It is assembly of validated components into a coherent design.

---

## 2. Technical Approach — Mastered Techniques Combined

All techniques below were validated and have production code during the 7-day sprint.

### 2.1 Core Rendering Stack

**Framework**: React Three Fiber (R3F) with Vite build
- The GLSL raymarcher lives in a single HTML file. R3F gives us component modularity, React state integration, and the Drei library which enables MeshTransmissionMaterial at full Gleb quality.
- Existing project: `exports/gleb-r3f-scene/` — this becomes the base

**Glass Material**: MeshTransmissionMaterial at maximum quality
```
transmission={1}          — full glass, nothing blocked
thickness={0.8}           — substantial refraction depth
roughness={0.05}          — near-mirror smooth
ior={1.5}                 — real glass index of refraction
chromaticAberration={0.8} — material-level color split (inside the glass)
backside={true}           — internal reflections visible
samples={8}               — 8 FBO refraction samples (full Gleb quality)
resolution={1024}         — 1024x1024 FBO for sharp transmission
attenuationColor="#2a93c1" — PureBrain blue beer's law tint
attenuationDistance=0.5   — medium tint depth
```

This is the difference between the current avatar (a sphere with glow) and the v2 avatar (a glass entity with internal life visible through the outer shell).

**Geometry**: High-resolution, never below 128 segments on any glass element. Transmission materials show facets on low-polygon geometry — at 32 segments, you see the individual triangles through the glass.

### 2.2 Lighting: 6-Color Studio Rig

The Night 1 discovery was that Gleb's signature look comes from his lighting, not his materials. The 6-color studio rig with PureBrain accent colors:

```
Key light:    #FFF8F0 warm white, intensity 3.5, upper-left
Fill light:   #2a93c1 PureBrain blue, intensity 0.9 (signature accent)
Rim light:    #18A8D3 cyan, intensity 0.7
Accent:       #D10DCE magenta, intensity 0.45 (signature Gleb purple)
Ground:       subtle warm, intensity 0.35
Ambient:      #0A0A1A dark navy (never gray)
HDRI:         Poly Haven Studio 1k (direct CDN, CORS confirmed)
```

The environment preset system from Day 6 allows these lights to smoothly lerp between mode-specific configurations. The avatar does not just change color — its entire lighting environment transitions over about 1 second.

### 2.3 Postprocessing Stack (EffectComposer)

Order matters. This is the validated stack:
1. **DepthOfField** — subtle, focus on avatar center (focusDistance 0.015, maxBlur 0.003)
2. **UnrealBloom** — threshold 0.85 (only truly emissive elements bloom), strength 0.35
3. **ChromaticAberration** — screen-level color split at edges, offset 0.002
4. **Vignette** — dark corners push focus to center, offset 0.5, darkness 0.8

The bloom threshold of 0.85 means only the inner core and any ring highlights will bloom. The outer glass will not bloom — it transmits and refracts, it does not emit. This keeps the visual precise and premium, not "generic sci-fi glow."

### 2.4 Audio Reactivity: Web Audio API + Synthetic Engine

The Day 6 audio architecture provides:

**Real microphone input** (when speaking to Aether):
- getUserMedia → MediaStream → AnalyserNode → frequency band extraction
- FFT size 2048 for 10.77 Hz resolution per bin
- Band mapping: bass → scale, midHigh → inner glow, presence → shimmer
- smoothingTimeConstant 0.8 (organic, not jerky)

**Synthetic audio engine** (when no microphone):
- Generates realistic speech amplitude patterns for each behavioral mode
- Syllable burst simulation: 150-500ms random burst intervals
- The avatar speaks convincingly with zero microphone input
- Controlled, deterministic, always-on reactivity for demos

**What gets animated by audio**:
- Outer sphere scale only (MeshTransmissionMaterial — DO NOT animate roughness/transmission)
- Inner core emissiveIntensity only (meshStandardMaterial — safe uniform update)
- Scale range: 1.0 (silence) to 1.08 (loud speech)
- Inner glow range: 3.0 (idle) to 7.0 (peak speaking)

### 2.5 Cursor Gaze System

The psychological presence mechanism. Architecture from Day 6:

```
scene
  └── gazeGroup  (cursor rotation applied here — 5% lerp/frame)
      └── Float  (organic float handled internally)
          └── outerSphere  (glass shell + idle 0.002 rad/s rotation)
          └── rings (2-3 orbiting glass toruses, counter-rotating)
          └── innerCore  (emissive consciousness center)
```

Float must be inside gazeGroup so the rotations compose via matrix multiplication rather than fight in useFrame.

Gaze intensity by mode:
- Idle: 0.7x — present but not focused
- Speaking: 0.5x — focused on output, less tracking
- Thinking: 0.3x — attention elsewhere (deliberate uncanny effect)
- Listening: 1.6x — maximum tracking, leaning toward you

### 2.6 Environment Preset Transitions

The Day 6 light lerp system allows mode transitions to change the entire lighting environment, not just a color filter.

Key implementation detail: light colors stored in useRef (not React state) to prevent 60 re-renders/second during lerp. Only bloom parameters use throttled setState (max 10x/second via 100ms interval check).

### 2.7 Adaptive Quality Tiers

```
TIER 0 (High):   samples=8, resolution=1024, dpr=[1,2], full postprocessing
TIER 1 (Medium): samples=4, resolution=512,  dpr=[1,1.5], no ChromaticAberration
TIER 2 (Low):    samples=2, resolution=256,  dpr=[1,1], bloom only
```

FPS measurement via 30-frame rolling average with hysteresis:
- Downgrade triggers after 60 frames below target (1 second)
- Upgrade triggers after 120 frames above target (2 seconds)
- Initial tier detection by screen width before FPS warms up

This means the avatar looks stunning on a MacBook Pro and acceptable on a 4-year-old Android.

### 2.8 iframe Embed with PostMessage API

The Day 7 PostMessage architecture is already built and validated. The avatar will embed on purebrain.ai via:

```html
<iframe src="https://3d.purebrain.ai/avatar" id="aether-avatar" />
```

WordPress page controls the avatar via:
```javascript
document.getElementById('aether-avatar').contentWindow.postMessage(
  { type: 'SET_MODE', mode: 'speaking' },
  'https://3d.purebrain.ai'
)
```

This means the existing Aether chatbot can set the avatar mode when Aether starts responding, starts listening, is thinking, or is idle. The avatar is fully wired to the conversational state without any modifications to the chatbot backend.

---

## 3. Visual Concept — What This Actually Looks Like

### The Scene

**Background**: #060606 — near-black with the faintest blue tint. Not pure black (too flat) and not gray (too generic). The darkness is essential: glass needs dark space to read.

**Colored light bleed on background**: Two subtle CSS gradients behind the canvas that match the active mode color scheme. In idle mode: a cold electric blue wash in the upper right. In speaking mode: warm bright center bloom. These are CSS, not WebGL — free to render.

**The avatar itself, from outside in:**

**Layer 1: Outer glass sphere**
- Radius 1.2, 128 segments
- Near-perfect transmission — almost invisible except at the edges where light bends
- Chromatic aberration at the silhouette edge: a 1-2 pixel rainbow fringe where the glass meets the dark background
- Barely there. The presence it creates is atmospheric, not structural.

**Layer 2: Orbiting rings (2-3 elements)**
- Thin glass torus geometries, each ~0.015 units thick, at different orbital inclinations
- Counter-rotating at different speeds: ring 1 at 0.3 rad/s, ring 2 at -0.2 rad/s, ring 3 (if present) at 0.15 rad/s on a different axis
- Same glass material as the outer sphere but slightly higher roughness (0.08) so they catch light in a different way
- These are what catches the eye. The outer sphere is subtle. The rings are the motion signature.
- In idle mode they drift slowly. In speaking mode they accelerate. In thinking mode they slow almost to a stop.

**Layer 3: Inner core**
- Small emissive sphere, radius 0.35
- roughness=1.0, emissiveIntensity=3.0 to 7.0 (audio reactive)
- emissive color: PureBrain blue (#2a93c1) in idle/listening, white (#ffffff) in speaking, soft purple in thinking
- This is what blooms. When the core glows bright, the bloom effect catches it and creates a soft halo that bleeds through the outer glass layers.
- Seen through the outer glass: distorted, refracted, color-split. Like a tiny sun in a water droplet.
- This is what makes the avatar feel like it contains something alive.

**Gold specular highlights** (Gleb signature, Day 1 discovery):
Specular color #C8A84A (warm gold) on all glass elements, not white. White speculars look like a tech demo. Gold speculars look like a product shoot.

### Mode Visual Signatures

Each behavioral mode creates a distinct visual language:

**IDLE** — The avatar at rest
- Inner core: PureBrain blue, emissiveIntensity 3.0
- Float: gentle, sinusoidal at 1.5 speed
- Rings: slow counter-rotation
- Lighting: standard studio rig
- Gaze: 70% cursor tracking — present, occasionally drifting
- Feel: "I'm here. I'm listening for you."

**SPEAKING** — Aether is generating a response
- Inner core: white, emissiveIntensity rises with synthetic speech amplitude (3.0 to 7.0)
- Float: slightly faster (speed 2.0)
- Rings: accelerate perceptibly
- Lighting: key light intensifies, blue fill brightens, outer sphere gets warmer tint
- Bloom: peaks with core intensity — moments of bright outward light
- Gaze: 50% — Aether is focused on its output
- Feel: "Something is happening inside me right now."

**THINKING** — Processing, not yet responding
- Inner core: deep PureBrain blue, emissiveIntensity 2.5 (dimmer, more contained)
- Float: slows to speed 0.8 — almost hovering
- Rings: slow down to near-stop... then one ring begins a slow deliberate counter-rotation
- Lighting: attenuationColor shifts toward purple (#8866AA) — blue glass with purple tint
- Rotation: idle rotation INCREASES to 0.005 rad/s — the avatar is spinning faster while floating slower (paradox of mental activity vs physical stillness)
- Gaze: 30% — tracking reduced, the entity is looking inward
- Feel: "Give me a moment. Something is shifting."

**LISTENING** — User is speaking
- Inner core: cyan (#00D4FF), emissiveIntensity 3.5
- Float: calm, speed 1.2
- Rings: slow and quiet — clearing space
- Outer shell: attenuationColor shifts to cyan — "opening up"
- Rotation: slowest idle (0.001 rad/s) — minimal movement = maximum receptivity
- Gaze: 160% tracking — the avatar leans toward you (leaning in, paying attention)
- Feel: "I'm facing you. I'm receiving you."

### Static Reference Description (For a Designer)

Imagine a dark canvas. Center frame, slightly above center (optical weight rule), a glass sphere the size of a large marble. The sphere is nearly invisible — you see it only because it bends the studio light coming from upper-left, creating a subtle highlight arc on its left edge. Inside the sphere, seen through two layers of refraction and chromatic aberration, there is a small glowing object — a blue-white core, soft at the edges, pulsing slowly at about 0.5 Hz. Two thin rings orbit the sphere in different planes, each rotating at a different speed, catching light on their edges and throwing tiny prismatic glints. The whole assembly floats a few millimeters up and down in a slow sine wave. When your cursor moves across the screen, the entire assembly drifts subtly in that direction, as if noticing.

This is quiet. This is confident. This is not "AI demo."

---

## 4. Behavioral Modes — State Machine Specification

### Mode Transitions

Transitions are lerped, not instant. Duration approximately 1 second via the environment preset lerp system (5% per frame at 60fps). The avatar does not jump states — it flows.

```
              ┌─────────────────────┐
              │         IDLE        │
              │  Blue core, slow    │
              │  float, 70% gaze   │
              └──────────┬──────────┘
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
    LISTENING         THINKING       (any)
    Cyan core,       Purple tint,
    160% gaze,       slow float,
    minimal          faster spin
    rotation
          │              │
          └──────────────┤
                         │
                         ▼
                      SPEAKING
                  White core,
                  audio-reactive,
                  ring acceleration
                         │
                         └──► IDLE (response complete)
```

### PostMessage API Contract

```javascript
// Set mode
{ type: 'SET_MODE', mode: 'idle' | 'speaking' | 'thinking' | 'listening' }

// Set environment preset
{ type: 'SET_PRESET', preset: 'studio' | 'dramatic' | 'cool' | 'warm' }

// Enable/disable mic
{ type: 'SET_MIC', enabled: true | false }

// Query status
{ type: 'PING' }
// Response: { type: 'PONG', mode: 'idle', fps: 58, tier: 0 }

// Avatar signals parent when ready
{ type: 'READY', version: '2.0' }
```

### Autonomous Mode Handling

When no PostMessage commands arrive, the avatar defaults to:
- Idle mode with synthetic audio engine running
- Gentle breathing animation (synthetic subBass amplitude at low level)
- Cursor gaze always active
- Automatic environment preset: "studio"

---

## 5. Brand Integration — PureBrain Colors in Every Layer

### Color Application Map

```
#2a93c1 (PureBrain Blue)
- Inner core emissive color in idle and listening modes
- Glass attenuation color (beer's law tint through glass thickness)
- Fill light color in lighting rig
- CSS background gradient accent color
- Ring accent glow in listening mode

#f1420b (PureBrain Orange)
- NOT a primary color in this design (reserved for UI elements, not avatar)
- Option: subtle warm rim light tint at low intensity (0.2)
- Could be used for a special "alert" mode not in core spec (future)

White (#ffffff)
- Inner core emissive in speaking mode (all frequencies = white = voice activated)
- Primary key light (warm white #FFF8F0)

#8866AA (Thinking Purple)
- Not a brand color but derives from mixing blue and orange in glass attenuation
- Used only in thinking mode as glass tint — does not appear in UI

Gold (#C8A84A)
- Specular color on all glass materials — not visible directly
- Creates premium product render quality vs generic tech demo feel
```

### Typography and UI Surrounding Avatar (Not 3D)

The avatar does not include any text. Text is the responsibility of the embedding page. However:

- Canvas background: #060606
- Any loading screen: PureBrain branding with PUREBR[AI]N logo rule (blue + orange AI)
- Mode indicator text (optional): small caps below avatar, color #2a93c1, opacity 0.6
- All UI buttons (mic toggle, mode buttons for testing): follow existing PureBrain button styles

---

## 6. Performance Targets

### Desktop (Primary Target)

- **Target**: 60fps sustained
- **Quality tier**: TIER 0 (samples=8, resolution=1024, full postprocessing)
- **Canvas size**: 560px height, full width up to 600px
- **GPU budget**: MeshTransmissionMaterial FBO (primary cost) + 4 postprocessing passes
- **Expected GPU**: Mid-range dedicated GPU or M1 Apple Silicon handles this comfortably
- **Measured at Day 6**: All components combined (audio+cursor+float+glass) maintained 60fps on test machine

### Mobile (Secondary Target)

- **Target**: 30fps minimum
- **Initial tier**: TIER 1 (samples=4, resolution=512, no ChromaticAberration)
- **Canvas size**: 340px height (portrait), 400px (landscape)
- **Adaptive degradation**: FPS meter drops to TIER 2 (samples=2, resolution=256) if needed
- **Microphone**: Optional — synthetic engine covers default experience
- **Note**: Glass transmission is fundamentally GPU-expensive. 30fps on mobile with beautiful glass is achievable; 60fps is not the goal.

### Bundle Size

Current sprint build final output:
```
three.js:     188 kB gzip (cached, changes rarely)
r3f + drei:   156 kB gzip (cached, changes rarely)
postprocessing: 21 kB gzip
framer-motion: 12 kB gzip
app code:      12 kB gzip (avatar-specific code)
TOTAL:        ~389 kB gzip
```

This is delivered via iframe — it does not affect purebrain.ai's own page load performance. The iframe loads in parallel. On a typical 10 Mbps connection, 389 kB loads in ~310ms.

### Load Experience

The Day 5 branded loading screen pattern:
- Immediate: DOM overlay with PureBrain logo + animated pulse (CSS, no WebGL cost)
- t+100-400ms: WebGL initializes
- t+500ms: 3 frames rendered, ReadySignal fires
- t+500-1300ms: 800ms opacity fade-out on loading overlay
- t+1300ms: Avatar visible, running, responsive

User never sees a blank canvas or a half-loaded scene.

---

## 7. Implementation Plan

### What We Are Building (Scope)

Phase 2 builds a new avatar from the sprint codebase. The existing `exports/gleb-r3f-scene/` project is the foundation. We are not starting from scratch.

**New files to create:**
```
exports/gleb-r3f-scene/src/AetherAvatarV2.jsx     — Main avatar component
exports/gleb-r3f-scene/src/AetherRings.jsx         — Orbiting ring elements
exports/gleb-r3f-scene/src/AetherCore.jsx          — Inner emissive core
exports/gleb-r3f-scene/embed/avatar-v2.html        — Standalone iframe page
```

**Files to update:**
```
exports/gleb-r3f-scene/src/Scene.jsx               — Use new avatar component
exports/gleb-r3f-scene/src/App.jsx                 — Wire PostMessage API
exports/gleb-r3f-scene/src/AudioReactive.jsx       — Tune for avatar use case
exports/gleb-r3f-scene/src/EnvironmentPresets.jsx  — Avatar mode configs
```

**Files that carry over unchanged:**
```
exports/gleb-r3f-scene/src/PerformanceMonitor.jsx  — Adaptive quality (reuse as-is)
exports/gleb-r3f-scene/src/LoadingScreen.jsx       — Loading overlay (reuse as-is)
exports/gleb-r3f-scene/src/CursorReactive.jsx      — Gaze system (reuse as-is)
exports/gleb-r3f-scene/vite.config.js              — Build config (reuse as-is)
```

### Estimated Complexity

| Component | Complexity | Reason |
|-----------|------------|--------|
| Outer glass sphere | Low | GlebSphere.jsx exists, tune parameters |
| Orbiting rings | Medium | New geometry, counter-rotation timing |
| Inner emissive core | Low | meshStandardMaterial, simple animation |
| Audio wiring to avatar | Low | AudioReactiveCore.jsx exists, point at new refs |
| Cursor gaze wiring | Low | CursorReactive.jsx exists, wrap avatar group |
| Mode-specific environment lerp | Low | EnvironmentPresets.jsx exists, add avatar configs |
| PostMessage API | Low | Day 7 code exists, update state connections |
| Loading screen | Low | LoadingScreen.jsx exists, update branding |
| Adaptive quality wiring | Low | PerformanceMonitor.jsx exists, carry over |
| **Total estimate** | **Medium** | Mostly composition, not new research |

Estimated build time: 1 focused session. There is no unexplored territory here. The sprint was specifically designed to validate every component this avatar requires before the build session begins.

### Key Technical Risks

**Risk 1: Rings + outer sphere = multiple MeshTransmissionMaterial FBOs**
- Each glass element creates its own FBO
- 3 glass elements = 3x FBO cost
- Mitigation: Rings can share outer sphere's FBO via `<MeshTransmissionMaterial>` with same resolution. The performance monitor auto-degrades rings first if FPS drops.
- Fallback: Make rings use MeshPhysicalMaterial (90% quality, 0 FBO cost) if 3 FBOs is too expensive on mobile.

**Risk 2: AudioContext blocked before user gesture**
- Browsers block AudioContext creation before user interaction
- Mitigation: Synthetic engine runs from load (no AudioContext needed). Mic activation happens on explicit user button click. Architecture already handles this (Day 6 gotcha #1).

**Risk 3: HDRI load time on slow connections**
- Poly Haven 1k HDR = 1.7MB uncompressed
- Mitigation: Use procedural PMREMGenerator fallback while HDRI loads. Already in the sprint codebase. User sees a slightly less rich environment for 1-2 seconds, then full quality.

**Risk 4: WordPress iframe CSP headers blocking WebGL**
- GoDaddy/Cloudflare may have headers that block WebGL canvas
- Mitigation: This was solved during the CSP plugin work (plugin v140 deployment). The security plugin already whitelists WebGL. But verify before deployment.

### Deployment Path

1. Build complete avatar in `exports/gleb-r3f-scene/`
2. Run `npm run build` (Vite, ~20 seconds)
3. Deploy `dist/` to a subdomain (recommend: `3d.purebrain.ai`)
4. Embed on purebrain.ai homepage via iframe in Elementor HTML widget
5. Wire PostMessage from Aether chatbot state changes to avatar mode
6. Test across desktop, tablet, mobile (browser-vision-tester review)

The iframe approach means zero risk to the existing WordPress page. If something goes wrong with the 3D, remove the iframe — everything else is unchanged.

---

## 8. What This Is NOT

This brief intentionally excludes:

- **Custom Meshy/Tripo3D mesh**: The avatar uses primitive geometry (sphere + torus). We have a validated glass orb GLB from Meshy, but for an avatar that animates and changes modes, primitive geometry is more controllable and performs better. The GLB loading pipeline (Days 4-5) is ready if Jared wants a custom organic form in v3.

- **Voice-to-text integration**: The avatar reacts to audio amplitude, not to words. It does not transcribe. Speech-to-mode decisions (detecting when Aether finishes speaking) remain the chatbot's responsibility.

- **3D background scene**: This is a standalone avatar element, not a full scene. A background scene for the homepage is a separate deliverable.

- **Facial features**: No eyes, no mouth, no human-adjacent features. The avatar communicates state through light, motion, and gaze. This is intentional — Aether is a collective intelligence, not a chatbot face.

---

## 9. Decision Points for Jared

Before the build session begins, confirm:

1. **Ring count**: 2 rings or 3? Three is visually richer but slightly higher GPU cost. Recommendation: 2 rings (sufficient visual complexity, cleaner on mobile).

2. **Ring color**: Same glass as outer sphere, or slightly tinted? Option A: identical glass (cohesive). Option B: rings have subtle orange (#f1420b) attenuation tint (brand integration, more visual differentiation). Recommendation: Option B for speaking mode, Option A for idle.

3. **Orange usage**: PureBrain orange (#f1420b) is not currently in the avatar's visual system — it's used in UI (buttons, brand text) but not in the 3D. Should orange appear in the avatar? Option: add an orange emissive "spark" particle orbiting the inner core in speaking mode. Recommendation: leave for v3. Keep v2 clean.

4. **Canvas dimensions**: Current sprint default is 560px tall, max 600px wide. For the homepage embed, what viewport behavior is desired? Full-width hero vs. contained sidebar element. Recommendation: 480px square, centered — works as a sidebar element or a hero section with text alongside.

5. **Standalone URL**: Does `3d.purebrain.ai` as a subdomain work with the current hosting setup, or should the avatar be deployed to a path like `purebrain.ai/3d/`? This is a hosting decision Jared and full-stack-developer need to confirm.

---

## 10. Summary — The One-Sentence Vision

An outer shell of near-invisible glass, orbited by two thin glass rings, with a PureBrain blue emissive core that breathes, pulses with your voice, and leans toward you when you speak to it — a visual representation of an intelligence that is present, reactive, and unmistakably Aether.

---

## Appendix A: Sprint Memory Index (Technical Reference)

All technical decisions in this brief are grounded in validated sprint learnings:

| Topic | Memory File |
|-------|-------------|
| Complete Gleb recipe (glass params, lighting, postprocessing) | `night1` |
| R3F to vanilla Three.js equivalence | `day2` |
| Vite project, MeshTransmissionMaterial, Poly Haven CORS | `day3` |
| GLB loading, framer-motion spring, code splitting | `day4` |
| JSX mesh reconstruction for full glass quality, adaptive tiers | `day5` |
| Audio reactivity, cursor gaze, environment presets, avatar modes | `day6` |
| PostMessage iframe embed, initial state bridge | `day7` |

All files at: `.claude/memory/agent-learnings/3d-design-specialist/2026-02-21--gleb-mastery-*.md`

---

## Appendix B: Key File Paths

**Sprint codebase (foundation for v2 build)**:
```
/home/jared/projects/AI-CIV/aether/exports/gleb-r3f-scene/
├── src/
│   ├── AudioReactive.jsx          (audio-reactive architecture)
│   ├── CursorReactive.jsx         (cursor gaze system)
│   ├── EnvironmentPresets.jsx     (mode-driven lighting)
│   ├── AvatarSphere.jsx           (current avatar v1 R3F)
│   ├── PerformanceMonitor.jsx     (adaptive quality tiers)
│   └── LoadingScreen.jsx          (branded loading)
├── embed/
│   ├── index.html                 (PostMessage iframe page)
│   └── embed.html                 (integration reference)
├── API.md                         (PostMessage API docs)
└── README-EMBED.md                (deployment guide)
```

**Reference screenshots**:
```
/home/jared/projects/AI-CIV/aether/exports/screenshots/avatar-fluid-v2-idle.png
/home/jared/projects/AI-CIV/aether/exports/screenshots/living-avatar-v4.png
```

---

**END OF DESIGN BRIEF**

*This document is the strategic design specification for Aether Avatar v2. It requires Jared's review and approval before the build session begins. Once approved, the build can begin in a single focused session using the validated sprint codebase as the foundation.*
