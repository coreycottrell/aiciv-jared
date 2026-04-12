# PureBrain 3D Experience Deliverables

**Prepared by**: feature-designer (Aether)
**Date**: 2026-02-19
**For**: Jared at Pure Technology / PureBrain.ai
**Context**: Two companion deliverables for a 3D-first future for PureBrain

---

## Table of Contents

1. [Deliverable 1: PeachWeb-Style 3D Website Builder System](#deliverable-1-peachweb-style-3d-website-builder-system)
2. [Deliverable 2: 3D Brain AI Personality Tuner](#deliverable-2-3d-brain-ai-personality-tuner)

---

---

# DELIVERABLE 1: PeachWeb-Style 3D Website Builder System

**User Need**: Pure Technology needs the ability to create PeachWeb-quality interactive 3D websites for PureBrain and clients, without paying $9K-$50K per site or $29-179/mo in hosting fees.

---

## What the System Looks Like

The system is an in-house 3D web experience pipeline built on three open-source pillars: Three.js as the rendering engine, React Three Fiber (R3F) as the React-native wrapper, and GSAP ScrollTrigger as the scroll-animation controller. Together these replicate everything PeachWeb does. The only difference is you own it.

PeachWeb's secret is simple: they built a no-code editor on top of Three.js. The actual 3D is the same free library anyone can use. Their value-add is the visual drag-and-drop interface. You do not need that interface yet. You need the output. And you can produce that output directly.

### The Core Stack

```
Three.js                 - 3D scene rendering (WebGL under the hood)
React Three Fiber (R3F)  - Write Three.js scenes as React components
@react-three/drei        - Pre-built helpers: scroll controls, HTML mixing, loaders
@react-three/postprocessing - Visual effects: bloom, glow, depth of field, chromatic aberration
GSAP + ScrollTrigger     - Scroll-driven animations, timeline orchestration
Blender                  - 3D model creation, editing, optimization
gltfjsx                  - Converts .glb model files into React components
Leva                     - Dev-time debug panel for tuning values visually
Vite                     - Build tool, fast dev server, bundles output for embedding
```

All of these are free and MIT-licensed. Zero ongoing cost.

### How It Integrates With Existing WordPress Sites

You have two proven integration paths:

**Path A (iframe embed)**: Build the 3D scene as a standalone Vite app, deploy it to Vercel (free tier), then embed it in Elementor via an HTML widget using an `<iframe>` or a full `<div>` with a script tag. The scene is self-contained and loads independently of WordPress.

**Path B (standalone experience page)**: Host the full 3D landing page at a subdomain (e.g., `experience.purebrain.ai`) and link to it from your main WordPress site. The user lands on a fully immersive 3D page, then flows to the WordPress conversion funnel.

Path A is lower risk (no WordPress migration). Path B creates the most impressive experience. Recommend starting with Path A for PureBrain's homepage hero, then building Path B as the dedicated high-conversion landing page.

---

## The MVP: PureBrain 3D Homepage Hero

The most valuable first build is replacing the current animated GIF brain on PureBrain's homepage with a live interactive 3D brain that responds to the visitor's scroll.

### What It Looks Like

The user arrives at purebrain.ai. The hero section loads:

- A 3D brain model sits at center, gently floating and rotating. It is rendered in translucent Pure Tech Blue (#2a93c1) with a soft inner glow. The texture is semi-transparent so you can see internal structure.
- Around the brain, orange (#f1420b) and blue particle nodes drift slowly. Some connect with thin glowing lines - neural pathway animations that form and dissolve.
- The headline "Your AI Isn't Born Yet" sits in front of the 3D scene, rendered in HTML (not baked into the 3D canvas), so it remains SEO-readable and screen-reader accessible.
- As the user scrolls down, the brain rotates, scales, and morphs. Each section of the homepage is tied to a specific brain animation state.

### Scroll-Driven Section Mapping

```
Scroll 0% (Hero):
  Brain: Full size, centered, slowly rotating
  Particles: Scattered neural network, few connections forming
  Text: "Your AI Isn't Born Yet"

Scroll 20% (What It Is):
  Brain: Shifts slightly right, camera orbits to show temporal lobe
  Orange glow pulses from specific region
  Text panel slides in from left: "A personal AI that wakes up remembering you"

Scroll 45% (How It Works):
  Brain: Separates into translucent segments (frontal, temporal, etc.)
  Each segment lights up sequentially with orange glow
  Text: Step-by-step awakening process revealed as segments illuminate

Scroll 70% (Features):
  Brain reassembles, now fully blue-glowing, pulsing with energy
  Particles accelerate, connection density increases
  Text: Feature cards appear as floating holographic panels

Scroll 90% (CTA):
  Brain explodes outward into particles, then re-assembles rapidly
  Full orange glow: "Awakened" state
  CTA: "Begin the Awakening" with pulsing orange border
```

### Interaction Details

- **Hover (desktop)**: Cursor proximity causes nearby particles to drift toward the cursor and back. Brain very slightly tilts toward mouse position.
- **Click on brain (optional)**: Triggers a "pulse" animation - orange wave radiates outward from click point across neural pathways.
- **Mobile**: Gyroscope tilt (if permission granted) causes subtle parallax tilt. Particles reduced from 200 to 60 for performance.

---

## Full System Architecture

Once the MVP proves the concept, the system expands into a reusable component library.

### Component Library Structure

```
src/
  components/
    3d/
      BrainScene.tsx          - Main brain renderer (R3F)
      NeuralParticles.tsx     - Particle system with connection lines
      FloatingHologram.tsx    - Generic holographic card component
      ScrollCamera.tsx        - Camera that follows scroll position
      GlowEffect.tsx          - Post-processing bloom wrapper
      DataTunnel.tsx          - Flythrough tunnel for transition sections

    ui/
      HybridSection.tsx       - Mixes 3D canvas with HTML content
      ScrollReveal.tsx        - HTML content that reveals on scroll
      CTAButton.tsx           - Animated CTA with 3D hover effect

  scenes/
    HeroScene.tsx             - Full hero section scene
    FeaturesScene.tsx         - Feature showcase scene
    HowItWorksScene.tsx       - Process visualization scene
    CTAScene.tsx              - Conversion section scene

  hooks/
    useScrollProgress.ts      - Returns 0-1 scroll position
    use3DModel.ts             - Loads, optimizes, returns GLB model
    usePerformanceTier.ts     - Detects device capability, adjusts quality

  models/
    brain.glb                 - Optimized 3D brain model (<2MB)
    logo-hex.glb              - PureBrain hexagonal logo in 3D
```

### The "Client Site" Build Pattern

When Pure Technology builds this for a client, the workflow is:

1. Copy the base template (Vite + R3F starter)
2. Swap in the client's 3D models (Blender exports as .glb)
3. Adjust brand colors via CSS variables and Three.js material color properties
4. Configure the scroll sections in a single `config.ts` file
5. Deploy to Vercel or the client's server
6. Provide an embed code snippet for their WordPress/Shopify/Webflow site

The config file drives everything, making client customization fast.

---

## Phased Build Plan

### Phase 1: MVP (Weeks 1-2, ~20-30 developer hours)

**Goal**: Replace the PureBrain homepage brain GIF with interactive 3D.

**Deliverables**:
- Vite + Three.js project setup
- Free 3D brain model downloaded from Sketchfab (search "brain anatomy" + filter Free + GLB)
- Basic GSAP ScrollTrigger: brain rotates on scroll
- Particle system: 100 orange/blue particles orbiting brain
- Static deployment on Vercel free tier
- Elementor iframe embed on purebrain.ai homepage hero

**Success criteria**: PureBrain homepage hero loads the interactive 3D brain in under 3 seconds on a mid-range laptop.

**Tools needed**: Node.js, Vite, Three.js, GSAP (all free). One afternoon to set up.

---

### Phase 2: Full Homepage Experience (Weeks 3-5, ~40-50 developer hours)

**Goal**: Migrate from R3F to React Three Fiber, build scroll-driven multi-section experience.

**Deliverables**:
- React + Vite + R3F project
- 5 distinct scroll sections with unique brain states
- Camera flythrough between sections using `@react-three/drei`'s ScrollControls
- Post-processing: bloom on brain, depth of field on background particles
- Mobile optimization: particle count auto-reduction, simplified shaders
- `experience.purebrain.ai` subdomain deployment

**New interactions**:
- Hover: cursor attracts particles
- Section entry animations: brain segments illuminate sequentially
- CTA section: brain assembly from particles

---

### Phase 3: Client-Ready System (Weeks 6-10, ~60-80 developer hours)

**Goal**: Generalize the system so Pure Technology can build 3D experiences for clients.

**Deliverables**:
- Reusable component library (as documented above)
- `config.ts` pattern for quick client customization
- Blender workflow documentation (how to prepare models for web)
- Performance budget enforcement (automated Lighthouse checks in CI)
- Template for one-pager sites (hero + 3 sections + CTA)
- Template for multi-page sites

**Business outcome**: Pure Technology can offer PeachWeb-equivalent 3D websites to clients for a fraction of PeachWeb's $9K-$50K price. Competitive advantage.

---

### Phase 4: Internal Mini-Builder (Months 3-5, ~100+ developer hours)

**Goal**: Build a lightweight visual configuration UI so non-developers can adjust 3D scenes without touching code.

**This is optional.** It is only worth building once Pure Technology has built 3-4 client sites and identified the repeated configuration points. At that point, a simple GUI for the config values (colors, particle count, scroll timing, model selection) multiplies development speed significantly.

**Not PeachWeb-level drag-and-drop.** Just a settings panel that writes to the config file. Much simpler, much faster to build, and covers 80% of the value.

---

## Technical Considerations

### Performance (Most Critical)

3D websites fail when they tank performance. These non-negotiable rules prevent that:

- 3D brain model must be under 2MB (use Blender's gltf-transform or the `gltfjsx` tool to compress)
- Use `Suspense` with a fallback: show the static image while 3D loads
- Add `prefers-reduced-motion` media query: serve non-animated version for users who have this set
- Lazy-load the 3D scene using `IntersectionObserver`: don't initialize WebGL until the scene enters the viewport
- Test on: iPhone 12 (Safari), mid-range Android Chrome, and a 5-year-old laptop. If it works there, it works everywhere
- Target: under 3 seconds to interactive on a 4G connection

### SEO (Invisible to Crawlers)

All text content must exist in HTML outside the `<canvas>` element. The 3D canvas is decoration. The actual headline, body copy, and structured data live in regular HTML divs layered on top of the canvas using absolute positioning. This is exactly how PeachWeb and Apple do it.

### Accessibility

- `prefers-reduced-motion` serves a static version
- All interactive 3D elements have keyboard-accessible HTML equivalents
- Brain region highlights have ARIA labels for screen readers
- Color is never the sole method of conveying information

### Browser Support

Three.js requires WebGL 1.0, which is supported by every browser released after 2014. The `no-webgl` fallback: detect WebGL support on page load, fall back to the animated GIF/video if unavailable (this covers less than 1% of users).

---

## Effort Estimates Summary

| Phase | Developer Hours | Rough Cost at $75/hr | Timeline |
|-------|----------------|----------------------|----------|
| Phase 1 (MVP hero) | 20-30 hrs | $1,500-$2,250 | 2 weeks |
| Phase 2 (Full experience) | 40-50 hrs | $3,000-$3,750 | 3 weeks |
| Phase 3 (Client system) | 60-80 hrs | $4,500-$6,000 | 4 weeks |
| Phase 4 (Mini-builder) | 100+ hrs | $7,500+ | 2+ months |
| **Total (P1-P3)** | **120-160 hrs** | **$9,000-$12,000** | **9 weeks** |

Compare: PeachWeb charges $9,000 minimum for a single one-pager. At these estimates, Pure Technology builds the capability to create unlimited sites.

---

## What Can Be Built Right Now

Today, with no additional tools installed:

1. Download a free brain GLB model from Sketchfab (15 minutes)
2. Create a Vite project: `npm create vite@latest brain-scene -- --template vanilla` (5 minutes)
3. Install Three.js: `npm install three gsap` (2 minutes)
4. Write 80 lines of JavaScript: brain model loads, rotates on scroll (2-3 hours)
5. `npm run build`, upload the `dist/` folder to Vercel (10 minutes)
6. In Elementor, add an HTML widget with `<iframe src="your-vercel-url" style="width:100%;height:600px;border:none;"></iframe>` (5 minutes)

Total: one afternoon. PureBrain homepage has an interactive 3D brain hero.

---

---

# DELIVERABLE 2: 3D Brain AI Personality Tuner

**User Need**: PureBrain users need an intuitive, memorable, and emotionally resonant way to customize their AI partner's personality. The current approach (text-based settings or sliders in a modal) does not match the brand promise of "awakening" an AI. The experience needs to feel like discovering your AI, not configuring software.

---

## The Concept

Instead of a settings page with dropdowns and sliders, the user is presented with a beautiful, interactive 3D model of a human brain. The brain floats in dark space, slowly rotating, with soft neural pathway animations pulsing through it. Different regions glow when approached.

Each anatomically named brain region corresponds to a specific dimension of the AI's personality. The user explores the brain to understand and tune their AI. The AI itself acts as a guide, explaining what each region does as the user investigates.

This is not a metaphor bolted on top of a settings form. The brain IS the settings form. The act of exploring a brain and tuning its regions is the act of understanding and shaping your AI partner. The conceptual alignment is perfect for PureBrain's brand.

---

## Brain Regions to AI Settings Mapping

### Frontal Lobe - Initiative and Creative Approach

**Anatomical function**: Planning, decision-making, executive function, personality expression.

**AI Settings**:
- How proactive the AI is (does it wait for instructions or anticipate needs?)
- How creative vs. conventional its approach is
- How structured its outputs are (bullet points and frameworks vs. flowing prose)

**Primary Slider**: Conservative to Bold
- Conservative end: AI stays in its lane, executes exactly what was asked, no surprises
- Bold end: AI proactively suggests, challenges assumptions, proposes alternatives you did not ask for

**Secondary Slider**: Structured to Fluid
- Structured: Numbered lists, clear headers, logical frameworks
- Fluid: Natural paragraphs, narrative thinking, creative leaps

**AI Guidance Text**: "This is where I form plans and make judgment calls. Move toward Bold if you want me to proactively push you. Keep it Conservative if you prefer I stay focused on exactly what you ask."

---

### Temporal Lobe - Language and Memory Expression

**Anatomical function**: Language processing, long-term memory retrieval, emotional association with memories, social cue interpretation.

**AI Settings**:
- Communication register (formal professional vs. warm conversational)
- Memory expressiveness (does the AI surface past context often or focus on the present task?)
- Emotional attunement in language choices

**Primary Slider**: Concise to Expressive
- Concise: Direct answers, minimal preamble, executive summary style
- Expressive: Rich context, analogies, storytelling, more complete explanations

**Secondary Slider**: Present-Focused to Memory-Rich
- Present-Focused: AI treats each interaction as relatively fresh, minimal callbacks
- Memory-Rich: AI frequently references what you have shared before, builds on past conversations, connects current topics to earlier discussions

**AI Guidance Text**: "This is where my voice comes from. Concise is good when you need fast answers. Expressive is better when you want me to really explain something or when context and nuance matter."

---

### Parietal Lobe - Synthesis and Big Picture

**Anatomical function**: Spatial awareness, sensory integration, understanding relationships between things, navigating complexity.

**AI Settings**:
- Scope of perspective (stays narrowly on topic vs. zooms out to consider the larger system)
- Idea connection (how often the AI draws connections across different domains or past discussions)
- Detail vs. strategy balance

**Primary Slider**: Focused to Holistic
- Focused: AI drills into the specific question, stays on task, does not wander
- Holistic: AI considers second-order effects, draws connections to adjacent topics, offers strategic perspective

**AI Guidance Text**: "This is how I connect ideas. Keep me Focused when you need a specific answer fast. Go Holistic when you want me thinking about the bigger picture and what this means beyond the immediate question."

---

### Occipital Lobe - How the AI Presents Information

**Anatomical function**: Visual processing, pattern recognition, interpreting what is seen.

**AI Settings**:
- Metaphor usage (dry literal vs. rich with visual analogies)
- How the AI frames complex concepts (definition-first vs. example-first)
- Diagram/visual suggestion frequency (does the AI suggest drawing things out, creating frameworks?)

**Primary Slider**: Literal to Metaphorical
- Literal: Clear, plain language. "The API returns a 401 when the token expires."
- Metaphorical: "Think of the API token like a visitor badge. When it expires, security sends you back to reception."

**AI Guidance Text**: "This is how I explain things. Literal is fastest when you already understand the domain. Metaphorical helps when you are learning something new or need to explain it to someone else."

---

### Cerebellum - Precision and Execution Style

**Anatomical function**: Coordination, fine motor control, timing, consistency, habitual behaviors.

**AI Settings**:
- Attention to detail (does the AI flag edge cases and caveats or stay high-level?)
- Consistency enforcement (how much the AI tracks and maintains consistency across long documents or projects)
- Task execution style (improvise vs. follow a careful checklist approach)

**Primary Slider**: Flexible to Precise
- Flexible: AI moves fast, makes reasonable assumptions, flags major issues but does not slow down for edge cases
- Precise: AI catches inconsistencies, notes exceptions, asks clarifying questions before proceeding if ambiguity exists

**AI Guidance Text**: "This is how carefully I execute. Precise is your choice when errors have real consequences - legal docs, code, client-facing materials. Flexible is better when you're brainstorming or moving fast and can clean things up later."

---

### Hippocampus - Memory Architecture

**Anatomical function**: Memory formation, consolidation of new information into long-term storage, spatial navigation, context retention.

**AI Settings**:
- Memory depth (how far back the AI actively references)
- Learning speed (how quickly the AI updates its model of you based on new information)
- Context window usage (does the AI reference only recent conversation or reconstruct full history?)

**Primary Slider**: Fresh Perspective to Deep Memory
- Fresh Perspective: AI approaches each session with openness, minimal weight on past interactions. Useful when exploring new directions.
- Deep Memory: AI actively reconstructs and references your full history. Every session builds on all previous ones.

**AI Guidance Text**: "This controls how much of our history I actively carry into our conversations. Deep Memory means I'll reference things we worked on weeks ago. Fresh Perspective means I approach things with less baggage - useful when you're pivoting or want new angles."

---

### Amygdala - Emotional Tone and Sensitivity

**Anatomical function**: Emotional processing, fear response, empathy, reading emotional content in social situations.

**AI Settings**:
- Emotional register in responses (clinical vs. warm)
- Sensitivity to the emotional subtext of what the user shares
- How the AI handles sensitive topics (direct and clinical vs. careful and empathetic)

**Primary Slider**: Analytical to Empathetic
- Analytical: Pure information. AI does not acknowledge emotional subtext. Best for technical work.
- Empathetic: AI notices and acknowledges emotional content, adapts tone to the situation, does not barrel through sensitive moments

**AI Guidance Text**: "This is my emotional awareness. Analytical is best when you need information fast and don't want softening. Empathetic is better when you're working through something difficult or want me to communicate with real warmth. Most people find a middle setting works well day-to-day."

---

### Brain Stem - Core Reliability (Always Maxed, Not Adjustable)

**Anatomical function**: Basic life functions - breathing, heart rate, consciousness. These cannot be turned off.

**What it represents**: The AI's fundamental reliability settings. Response accuracy, safety guidelines, factual groundedness, core ethical constraints.

**Visual treatment**: Always glowing at full intensity (bright orange). Not clickable in the adjustable sense. When hovered, shows a tooltip: "These are my core functions. Always on. Always reliable. This is the foundation everything else runs on."

**AI Guidance Text**: "Some things don't flex. My commitment to being accurate, safe, and honest - that's my brain stem. It runs underneath everything, always."

**Why include it**: It is anatomically significant and its inclusion completes the metaphor. It also gives users confidence that certain things are non-negotiable, which is reassuring.

---

### Corpus Callosum - Logic/Creativity Balance

**Anatomical function**: The bridge between the left and right hemispheres. Coordination of analytical and creative thinking.

**AI Settings**:
- Balance between logical/systematic thinking and intuitive/creative thinking
- How the AI approaches ambiguous problems (look for the rigorous framework vs. go with what feels right)

**Primary Slider**: Left-Brain (Logic) to Right-Brain (Creative)
- Left-Brain: The AI defaults to structured analysis, frameworks, step-by-step reasoning, citations
- Right-Brain: The AI makes intuitive leaps, suggests novel framings, follows creative threads, prioritizes what feels generative

**Visual treatment**: Rendered as a glowing bridge structure between the two brain hemispheres. When adjusted, the left hemisphere glows more blue/cool and the right glows more orange/warm.

**AI Guidance Text**: "I'm the bridge between your AI's analytical and creative sides. Logic-heavy means I'll build frameworks and cite my reasoning. Creative-heavy means I'll trust intuition and surprise you with connections you didn't expect."

---

## User Experience Flow

### Entry State

The user navigates to the Personality Tuner (accessible from the main app sidebar, or from onboarding after naming their AI).

The page loads dark. A soft ambient particle field fades in. The 3D brain materializes from particles, assembling itself over two seconds. It settles into a slow rotation. Soft blue neural pathway animations pulse through it in irregular rhythms that feel organic, alive.

The user's AI speaks first (text appears beside the brain, optionally with voice): "This is your mind - well, my mind. Different regions control how I think, communicate, and work with you. Explore any region to adjust how I show up for you."

---

### Hover State

The user moves their cursor over a brain region.

- The region brightens from translucent blue to a warm orange glow
- A label floats up: the region name and one-line function description
- Nearby neural pathway animations increase in speed and density, visualizing activity
- A subtle depth-of-field effect focuses the camera on the hovered region

The label format: "Frontal Lobe - Initiative and Creative Approach"

---

### Click State (Settings Panel Opens)

The user clicks a brain region.

- The brain rotates smoothly to center the clicked region toward the viewer
- A settings panel slides in from the right (or from below on mobile)
- The selected region pulses with a steady orange glow
- The panel shows:
  - Region name and anatomical illustration thumbnail
  - AI's explanation of what this region does (2-3 sentences, in the AI's voice)
  - Primary slider with labeled endpoints
  - Secondary slider (if applicable) with labeled endpoints
  - Preview text: "With these settings, I might respond to 'help me plan my day' like this: ..." showing a live text preview

Changes take effect immediately. The user can return to the brain by clicking the "Back to Brain" button or pressing Escape.

---

### Live Preview

The right panel includes a small live preview section: a mock conversation snippet that dynamically updates as sliders move. The left side of the snippet shows the user asking the same generic question ("Help me plan a productive morning"). The right side shows how the AI would respond at the current slider configuration. As the user drags sliders, the preview text transitions to show a different response style.

This is not hitting the actual AI API on every slider drag. It is a set of pre-written exemplar responses for each end of the spectrum, with the text morphing between them as the slider moves. Technically this is CSS cross-fade between two text states at CSS transition.

---

### Guided Mode vs. Advanced Mode

**Guided Mode (Default for new users)**:
The AI walks the user through each region sequentially. After the AI finishes its introduction, a glowing trail appears showing which region to explore first. The AI narrates: "Let's start with your Frontal Lobe. This is where I decide how boldly to act on your behalf. Click it to see your options." After each region is configured, the AI acknowledges it and guides to the next.

Progress indicator: a row of small region icons at the bottom, filling with orange as each is visited.

**Advanced Mode (Available after first pass)**:
All regions glow simultaneously at their current intensity. User can jump freely to any region. No guided prompts. Suitable for users revisiting their configuration.

Toggle between modes via a button at top-right of the brain view.

---

### Brain Profile Summary

After all (non-brain-stem) regions have been visited at least once, the user can open the "Brain Profile" panel.

This shows:
- A radar/spider chart with 8 axes (one per adjustable region), showing the current configuration visually
- A generated personality summary: 3-4 sentences describing the AI's overall personality based on the combined settings. Example: "Your AI tends toward bold, creative action with deep memory and high empathy. Expect proactive suggestions, rich metaphors, and responses that acknowledge the emotional context of your questions."
- A shareable Brain Profile card (optional): a visual export of the radar chart + summary for social sharing or team onboarding

The summary is generated from a template system: each slider position maps to specific adjective combinations, assembled into grammatically correct sentences. No AI API call needed for this - it is string interpolation.

---

### Settings Persistence

Configuration is stored as a JSON object in the user's profile:

```json
{
  "personality_version": 2,
  "updated_at": "2026-02-19T14:30:00Z",
  "regions": {
    "frontal_lobe": {
      "bold": 0.7,
      "structured": 0.3
    },
    "temporal_lobe": {
      "expressive": 0.6,
      "memory_rich": 0.8
    },
    "parietal_lobe": {
      "holistic": 0.5
    },
    "occipital_lobe": {
      "metaphorical": 0.4
    },
    "cerebellum": {
      "precise": 0.6
    },
    "hippocampus": {
      "deep_memory": 0.8
    },
    "amygdala": {
      "empathetic": 0.65
    },
    "corpus_callosum": {
      "creative": 0.55
    }
  }
}
```

This JSON maps to a system prompt injection. Each numeric value selects from a bank of system prompt phrases. The final system prompt is assembled dynamically from the user's configuration at conversation start.

---

## Visual Design Specification

### Environment

- Background: `#0a0a0a` (PureBrain dark theme) with a very subtle radial vignette
- Ambient depth: a faint star/particle field behind the brain at low opacity
- No hard edges on the UI - everything floats in dark space

### Brain Rendering

- Base material: translucent blue, similar to `#2a93c1` at 60% opacity with additive blending
- Allows internal structure to show through - the translucency is intentional
- Normal map: subtle surface detail, not hyper-realistic anatomy, stylized but recognizable
- Ambient occlusion in the folds (darker where brain folds in, lighter at peaks)
- Slow Y-axis rotation: 30 seconds per revolution in idle state
- Breathing scale animation: 0.97 to 1.03 scale over 4 seconds, eased in/out

### Neural Pathway Animations

- Thin lines connecting major regions through the brain interior
- Particles travel along the lines in both directions
- Particle color: blue (#2a93c1) at rest, orange (#f1420b) when a region is active
- Line opacity: 0.15 at rest, 0.35 when the region is hovered, 0.6 when selected
- Animation speed: irregular, organic. Not perfectly periodic.

### Region Hover/Active States

- Hover: Region surface brightens to `#2a93c1` at 90% opacity, orange corona glow at 40% opacity
- Selected: Region glows solid orange (#f1420b) at 80% opacity, strong orange point light emanating from it
- Other regions dim slightly when one is selected (to 50% opacity) - directs attention
- Transitions: 400ms ease-in-out

### Corpus Callosum Visual

This is the bridge between the hemispheres. At center-left configuration, it glows evenly blue. Moved toward Logic, the left hemisphere brightens blue and the right dims. Moved toward Creative, the right hemisphere brightens orange and the left dims. The corpus callosum itself glows the intermediate color.

### Settings Panel

- Width: 380px on desktop, full-width bottom sheet on mobile
- Background: `rgba(12, 12, 16, 0.95)` with 1px border `rgba(255,255,255,0.08)`
- Blurred backdrop: `backdrop-filter: blur(20px)`
- Slider track: dark (#1a1a1a), filled portion uses orange-to-blue gradient based on slider position
- Slider thumb: white circle, 20px diameter, subtle box shadow
- Typography: Oswald for region names, Plus Jakarta Sans for body text

### Mobile Adaptation

On screens under 768px:
- The brain renders as a 2D anatomical illustration (SVG-based) with the same interaction model
- Regions are still tappable, panel slides up from bottom
- Particles reduced to CSS animations rather than WebGL
- Brain rotates on finger swipe rather than auto-rotate

This is not a degraded experience - it is a deliberately designed mobile version. The 2D brain can be drawn in a stylized way that matches the brand aesthetic (translucent blue regions, orange neural pathway lines as SVG paths).

---

## Technical Architecture

### Technology Stack

```
React + TypeScript            - Component framework
React Three Fiber             - 3D brain rendering
@react-three/drei             - Raycasting, HTML overlays, camera controls
@react-three/postprocessing   - Bloom, glow effects on active regions
Zustand                       - Settings state management (lightweight)
Framer Motion                 - Settings panel slide-in, hover animations on UI elements
React Spring                  - Smooth interpolation of 3D material properties
Tailwind CSS                  - Settings panel and UI styling
```

### File Structure

```
src/
  features/
    personality-tuner/
      BrainTuner.tsx           - Main container component
      Brain3D.tsx              - R3F brain scene
      BrainRegion.tsx          - Individual clickable brain region mesh
      NeuralPathways.tsx       - Animated connection lines between regions
      RegionSettingsPanel.tsx  - Sliding settings panel
      LivePreview.tsx          - Animated text preview
      BrainProfile.tsx         - Summary view with radar chart
      GuidedMode.tsx           - Tutorial overlay and narration

  stores/
    personalityStore.ts        - Zustand store for all region settings

  utils/
    personalityToPrompt.ts     - Converts settings JSON to system prompt text
    personalityToSummary.ts    - Generates the human-readable profile summary

  models/
    brain-segmented.glb        - Brain model with named mesh groups per region
```

### The Critical Technical Requirement: Segmented Brain Model

The 3D brain model must be a single .glb file that contains separate named meshes for each brain region. This allows R3F's raycasting to identify which region the user clicked.

The mesh names must match the code:
```
frontal_lobe
temporal_lobe_left, temporal_lobe_right
parietal_lobe
occipital_lobe
cerebellum
hippocampus_left, hippocampus_right (visible as interior structures)
amygdala_left, amygdala_right
brain_stem
corpus_callosum
```

**Where to get this model**: Sketchfab has several free anatomical brain models with labeled structures. Search for "brain anatomy regions labeled" and filter by GLB format and Creative Commons license. Alternatively, the brain from Visible Human Project or similar anatomical databases can be adapted in Blender by manually assigning region materials.

If no suitable free model exists, a stylized segmented brain can be created in Blender in 4-6 hours. It does not need to be hyper-realistic - a stylized version that clearly communicates the regions is preferable to a medical-grade model that looks clinical.

### Raycasting (Click Detection on 3D Regions)

React Three Fiber's `onPointerOver` and `onClick` event handlers on mesh elements do raycasting automatically. When the user's cursor moves over a specific mesh, the event fires. No manual raycasting code needed.

```typescript
// BrainRegion.tsx (simplified)
function BrainRegion({ name, regionId, onSelect }) {
  const [hovered, setHovered] = useState(false);
  const meshRef = useRef();

  useFrame(() => {
    // Smoothly interpolate material color based on hover/selected state
    meshRef.current.material.emissiveIntensity = THREE.MathUtils.lerp(
      meshRef.current.material.emissiveIntensity,
      hovered ? 0.8 : 0.2,
      0.05
    );
  });

  return (
    <mesh
      ref={meshRef}
      name={regionId}
      onPointerOver={() => setHovered(true)}
      onPointerOut={() => setHovered(false)}
      onClick={() => onSelect(regionId)}
    >
      <meshStandardMaterial
        color="#2a93c1"
        transparent={true}
        opacity={0.6}
        emissive={hovered ? "#f1420b" : "#2a93c1"}
      />
    </mesh>
  );
}
```

### Settings to System Prompt Conversion

The personality settings JSON is converted to a system prompt addendum at conversation start:

```typescript
// personalityToPrompt.ts (simplified example)
export function buildPersonalityPrompt(settings: PersonalitySettings): string {
  const phrases: string[] = [];

  const frontal = settings.regions.frontal_lobe;
  if (frontal.bold > 0.7) {
    phrases.push("Be proactive: anticipate needs, suggest alternatives, and challenge assumptions constructively.");
  } else if (frontal.bold < 0.3) {
    phrases.push("Stay focused on exactly what is asked. Do not introduce tangents or unsolicited alternatives.");
  } else {
    phrases.push("Balance executing requests precisely with offering one proactive suggestion when clearly beneficial.");
  }

  // ... same pattern for each region

  return `PERSONALITY CONFIGURATION:\n${phrases.join('\n')}`;
}
```

This prompt addendum is prepended to the system prompt for every conversation. Users with more memory-rich hippocampus settings get longer context injection. Users with precise cerebellum settings get instructions to flag ambiguities before proceeding.

---

## Build Phases for the Personality Tuner

### MVP (Weeks 1-3, ~30-40 developer hours)

**What gets built**:
- 2D anatomical brain SVG (no 3D yet) with tappable regions
- Settings panel with sliders for each region
- Live settings persistence to user profile
- System prompt injection working
- Mobile-first responsive design

**Why start with 2D**: Lower technical barrier. Proves the interaction model and system prompt integration are valuable before investing in 3D rendering. Can ship to real users and get feedback faster.

**Success metric**: Users who use the Personality Tuner have measurably higher conversation satisfaction scores than users who don't.

---

### V2: 3D Brain (Weeks 4-7, ~50-60 developer hours, after MVP validation)

**What gets added**:
- React Three Fiber 3D brain replaces the 2D SVG (mobile keeps 2D)
- Segmented brain model loaded from GLB
- Hover/click raycasting on 3D regions
- Neural pathway particle animations
- Post-processing glow on active regions
- Camera orbit to center selected region

---

### V3: Full Experience (Weeks 8-12, ~40-50 additional developer hours)

**What gets added**:
- Guided Mode with AI narration
- Brain Profile summary with radar chart
- Live preview text in settings panel
- Shareable Brain Profile card
- Brain profile badge visible on user's profile page (small icon showing their configuration)
- Animations on settings changes (region pulses when slider moves)
- Smooth "assembly from particles" on first visit

---

## Effort Estimates Summary

| Phase | Developer Hours | Rough Cost at $75/hr | Timeline |
|-------|----------------|----------------------|----------|
| MVP (2D brain) | 30-40 hrs | $2,250-$3,000 | 3 weeks |
| V2 (3D brain) | 50-60 hrs | $3,750-$4,500 | 4 weeks |
| V3 (Full experience) | 40-50 hrs | $3,000-$3,750 | 4 weeks |
| **Total** | **120-150 hrs** | **$9,000-$11,250** | **~11 weeks** |

---

## Why This Feature Is Strategically Important

PureBrain's brand promise is "awakening your AI." Right now, the awakening experience happens during the initial conversation. But after that, most users interact with a generic AI interface that feels identical to every other AI chat product.

The Personality Tuner extends the awakening metaphor into the ongoing relationship. Users are not adjusting settings - they are exploring and shaping the mind of their AI partner. The 3D brain visualization makes the abstraction of "AI personality" tangible and explorable.

This is the kind of feature that earns word-of-mouth. "You can literally tune your AI's brain regions." Nobody does this. It is visually stunning, conceptually coherent, and deeply aligned with PureBrain's core identity. It is also the kind of feature that appears in product demos and press screenshots.

From a business standpoint: users who feel ownership over their AI's personality are dramatically less likely to churn. They have invested something of themselves into the configuration. The AI feels more theirs. This is retention mechanics built into the core product experience.

---

## What Can Be Built Right Now

Today, no new dependencies needed beyond your React stack:

1. Draw the brain regions as an SVG diagram in Figma or directly in code (labeled regions as `<path>` elements)
2. Add `onClick` handlers to each SVG region
3. Build the settings panel as a React component with range inputs
4. Wire settings to a Zustand store
5. Build the `personalityToPrompt` conversion function
6. Inject the resulting prompt text into the AI system prompt

This is a fully functional MVP. Real users, real personality tuning, real AI behavior changes. Zero 3D required at this stage.

Ship that. Measure whether users engage with it and whether it improves retention. Then decide whether to invest in the 3D layer.

---

---

## Cross-Deliverable Notes

Both deliverables share a technology foundation (React Three Fiber, Three.js, GSAP) and can share component code. The brain model used in the Personality Tuner can be a higher-fidelity version of the brain model used in the homepage hero. The particle system from Deliverable 1 can be reused as the ambient particle field in Deliverable 2.

**Recommended sequencing**:

1. Build Deliverable 1 MVP (homepage 3D hero) first. This gets your team comfortable with Three.js/R3F with lower stakes (homepage can be reverted easily).
2. Apply that experience to Deliverable 2 MVP (2D brain Personality Tuner). No new 3D skills needed yet.
3. Upgrade Deliverable 1 to the full multi-section experience.
4. Upgrade Deliverable 2 to 3D brain using skills built in step 1 and 3.

**Total estimated investment for both deliverables through V2/Phase 2**:
- 170-210 developer hours
- Roughly 10-13 weeks with one focused developer
- Cost at $75/hr: $12,750-$15,750
- Compared to PeachWeb's $9K minimum for a single one-pager plus ongoing hosting fees

**The difference**: Pure Technology owns the capability permanently, can apply it to unlimited sites and products, and has built a genuine internal competitive advantage in 3D web experiences.

---

*Prepared by feature-designer (Aether)*
*Pure Technology / PureBrain.ai*
*2026-02-19*
