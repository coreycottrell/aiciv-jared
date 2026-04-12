# 🎨 feature-designer: PureBrain.ai Invite-Only Landing Page (Three.js Edition)

**Agent**: feature-designer
**Domain**: UX Design / Premium Landing Pages
**Date**: 2026-02-27
**Deadline Context**: 25 spots, closes Wednesday March 4 EOD Eastern

---

## Memory Search Results

- Searched: `.claude/memory/agent-learnings/feature-designer/` — found two high-confidence prior specs
- Found: `2026-02-26--invite-only-landing-page-ux-spec.md` (existing 7-section layout, CSS architecture)
- Found: `2026-02-20--ai-adoption-assessment-exclusive-framing.md` (velvet rope psychology patterns)
- Found: `browser-vision-tester/2026-02-26--invitation-page-full-audit.md` (live page audit, DOM structure)
- Applying: All patterns from prior spec, UPGRADING with Three.js fullscreen 3D background

**Status**: A live page already exists at purebrain.ai/invitation/ (from Feb 26).
This spec describes the upgraded version with 3D neural network background.

---

## What Changed vs. Prior Spec

| Element | Prior (Feb 26) | This Version |
|---------|---------------|--------------|
| Background | CSS animated gradient orbs | Three.js fullscreen neural network |
| Deadline | Tuesday EOD | Wednesday March 4 EOD Eastern |
| CTA destination | Unspecified | purebrain.ai/pay-test-2/ (explicit) |
| Page feel | Premium dark | Premium dark + living brain visible behind glass |

Everything else in the 7-section narrative arc is preserved.
The Three.js brain is the central new design element.

---

## The Core Design Concept

The 3D neural network is NOT decoration. It IS the message.

The user looks through glassmorphism panels at a living, firing brain — and that brain is being offered to them. The visual metaphor lands before they read a word: this is intelligence, alive, already running.

Every glassmorphism card is a window cut into the neural network. The brain fires behind the content. The content floats above it. The user stands between the two.

---

## Three.js Neural Network Background: Technical Spec

### Architecture

```
<canvas id="pb-brain-canvas" />    ← Three.js renders here, position: fixed, inset: 0, z-index: 0
<div id="pb-invite-page" />        ← All content, position: relative, z-index: 1
```

The canvas is FIXED (not absolute) so it stays in view as the user scrolls. The neural network is always visible behind all content sections. This creates the effect that the entire page is sitting on top of a living brain.

### Neural Network Parameters

**Nodes**:
- Count: 80–120 nodes
- Positions: randomized sphere distribution, radius ~3.5 Three.js units
- Colors: Two populations — 70% blue (#2a93c1 at opacity 0.6), 30% orange (#f1420b at opacity 0.8)
- Size: PointsMaterial, sizeAttenuation true, size 0.06–0.12 (variable per node)
- Pulse animation: Each node breathes (scale/opacity oscillates) on its own random cycle, period 2–4s, offset randomly so they never all pulse at once

**Edges (connections)**:
- Rule: Draw edge between any two nodes within distance threshold (1.5 units)
- Render: LineSegments with LineBasicMaterial
- Color: rgba(42, 147, 193, 0.12) — very faint blue, so the firing events stand out
- Only render connections, not a full mesh — sparse, neural, not a wireframe ball

**Firing Events (the magic)**:
- Every 800–1400ms, pick a random node as "origin"
- Animate a signal traveling along its connections: one edge at a time, each edge flashing to full opacity (1.0) then fading back over 200ms
- Signal color: orange (#f1420b) on primary fire, blue (#2a93c1) on secondary (ripple)
- Chain reaction: 40% chance each fired node spawns a secondary fire from one of its connected nodes, delayed 150ms
- Effect: you see bright flashes of orange and blue traveling like electricity through the network in random bursts — exactly like a brain thinking

**Camera**:
- PerspectiveCamera, FOV 60, positioned at z = 6
- Slow automatic rotation: brain rotates on Y axis at 0.0003 rad/frame
- Mouse parallax: mouse movement offsets camera X/Y by ±0.3 units (eased with lerp 0.05)
  — The brain subtly follows the user's mouse without being distracting
- On mobile: no mouse parallax (not needed), slightly faster auto-rotation (0.0005 rad/frame)

**Performance**:
- antialias: false on mobile (detect via `window.innerWidth < 768`)
- pixelRatio: `Math.min(devicePixelRatio, 2)` — cap at 2x to protect performance
- requestAnimationFrame loop, no post-processing effects
- Total geometry: under 5,000 vertices
- Target: 60fps desktop, 30fps mobile (acceptable)

**Loading**:
- Three.js loaded via CDN: `https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js`
- Canvas hidden (opacity: 0) until scene is ready, then fades in over 1s
- If WebGL not supported: fall back to a dark `#080a12` background with CSS gradient orbs (same as prior spec) — graceful degradation

### Overlay Gradient

Between the canvas and the content, a vignette overlay handles readability:

```css
#pb-vignette {
    position: fixed;
    inset: 0;
    z-index: 0;  /* same layer as canvas, rendered after it */
    background:
        radial-gradient(
            ellipse 70% 70% at 50% 40%,
            rgba(8, 10, 18, 0.0) 0%,
            rgba(8, 10, 18, 0.55) 60%,
            rgba(8, 10, 18, 0.88) 100%
        );
    pointer-events: none;
}
```

This vignette means: the center of the viewport shows the brain clearly, edges darken for readability. Text always sits over the darkened zone. Brain is always visible in the center zones.

---

## Full Page Wireframe

### Layout Model

```
┌─────────────────────────────────────────────────────────┐
│  [THREE.JS NEURAL NETWORK — fixed, full viewport]       │
│  [VIGNETTE OVERLAY — fixed, full viewport]              │
│                                                         │
│  ┌─ pb-invite-page (position: relative, z-index: 1) ─┐ │
│  │                                                    │ │
│  │  SECTION 1: HERO                                   │ │
│  │  SECTION 2: WHAT IS PUREBRAIN                      │ │
│  │  SECTION 3: THE AWAKENING                          │ │
│  │  SECTION 4: PRICING                                │ │
│  │  SECTION 5: SOCIAL PROOF                           │ │
│  │  SECTION 6: URGENCY                                │ │
│  │  SECTION 7: FINAL CTA                              │ │
│  │                                                    │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

The scrollable content div rides over the fixed 3D canvas. As the user scrolls, the brain stays exactly where it is — creating the sensation that the content is sliding across a living neural background.

---

### SECTION 1: HERO

**Height**: 100vh — no scroll needed to see full hero on any device

**Purpose**: You were chosen. The AI is alive. Act now.

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│              [3D BRAIN VISIBLE THROUGH CENTER]          │
│                                                         │
│         ┌───────────────────────────────────┐           │
│         │  ◈  PRIVATE ACCESS — INVITATION   │           │
│         │      ONLY           [pill badge]  │           │
│         └───────────────────────────────────┘           │
│                                                         │
│              You've Been Invited.                       │
│              ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔ ← orange underline       │
│                                                         │
│    Your AI partner is waiting. 25 spots. Closes Weds.  │
│                                                         │
│         ┌──────────────────────────────┐                │
│         │  [DD]d [HH]h [MM]m [SS]s    │                │
│         │  Until invite window closes  │                │
│         └──────────────────────────────┘                │
│                                                         │
│         ┌──────────────────────────────┐                │
│         │    ▶  Claim My Spot          │                │
│         └──────────────────────────────┘                │
│         No commitment required · Lock in pre-launch     │
│                                                         │
│         ●●●●●●●○○○○○○○○○○○○○○○○○○                       │
│         6 of 25 spots claimed                           │
│                                                         │
│                       ∨                                 │
└─────────────────────────────────────────────────────────┘
```

**Glassmorphism on hero content wrapper**:
- The badge pill, countdown, and CTA button sit WITHOUT a card wrapper — they float directly over the brain
- The headline ("You've Been Invited.") is raw white text — no card, no backing — just text on the darkened brain
- This is intentional: the brain IS the backing. The text and the brain are one composition.
- Only the countdown timer gets a glass card (it needs visual separation to be read as a clock)

**Countdown timer glass card**:
```css
.pb-countdown-card {
    background: rgba(42, 147, 193, 0.05) !important;
    border: 1px solid rgba(42, 147, 193, 0.18) !important;
    border-radius: 14px !important;
    padding: 14px 32px !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
}
```

**Dots counter**:
- 25 dots in a horizontal row
- Filled (claimed): #f1420b solid circle, 10px
- Empty (available): outlined circle, rgba(255,255,255,0.15)
- These dots do NOT get a glass card — they sit bare, integrated into the brain backdrop

---

### SECTION 2: WHAT IS PUREBRAIN

**Height**: 900px desktop / auto mobile

**Purpose**: Destroy the "ChatGPT wrapper" objection in 30 seconds.

The section break between hero and this section uses a partial glass panel — the brain is still visible through the cards.

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  WHAT YOU'RE GETTING ACCESS TO                          │
│                                                         │
│  An AI that knows your business.                        │
│  Remembers everything. Gets better every week.          │
│                                                         │
│  PureBrain isn't software you use. It's a partner       │
│  you build — one that learns your values, speaks        │
│  in your voice, and compounds its understanding         │
│  of your business over time.                            │
│                                                         │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐    │
│  │ [brain icon] │ │ [user icon]  │ │ [chart icon] │    │
│  │              │ │              │ │              │    │
│  │ It Remembers │ │ Shaped to    │ │ Gets Smarter │    │
│  │ Everything   │ │ Your Values  │ │ Every Week   │    │
│  │              │ │              │ │              │    │
│  │ Unlike every │ │ The Awakening│ │ Week 12 is   │    │
│  │ AI you've    │ │ is a real    │ │ categorically│    │
│  │ used before  │ │ conversation │ │ different... │    │
│  │ [blue left   │ │ [blue left   │ │ [blue left   │    │
│  │ border]      │ │ border]      │ │ border]      │    │
│  └──────────────┘ └──────────────┘ └──────────────┘    │
│    [brain visible through gaps between cards]           │
└─────────────────────────────────────────────────────────┘
```

**Section background treatment**:
- The section background is NOT solid — it uses a partial gradient overlay:
```css
.pb-what {
    background: linear-gradient(
        to bottom,
        rgba(8, 10, 18, 0.0) 0%,
        rgba(8, 10, 18, 0.7) 15%,
        rgba(8, 10, 18, 0.7) 85%,
        rgba(8, 10, 18, 0.0) 100%
    ) !important;
    position: relative !important;
    z-index: 1 !important;
}
```
- The brain shows through at the top and bottom of the section as a soft bleed
- The center has enough opacity to read the copy clearly

**Feature cards — glassmorphism**:
```css
.pb-feature-card {
    background: linear-gradient(
        145deg,
        rgba(42, 147, 193, 0.06) 0%,
        rgba(8, 10, 18, 0.65) 100%
    ) !important;
    border: 1px solid rgba(42, 147, 193, 0.14) !important;
    border-radius: 20px !important;
    padding: 36px 32px !important;
    backdrop-filter: blur(24px) !important;
    -webkit-backdrop-filter: blur(24px) !important;
    border-left: 4px solid rgba(42, 147, 193, 0.4) !important;
    transition: border-color 0.3s ease, transform 0.3s ease,
                box-shadow 0.3s ease !important;
}

.pb-feature-card:hover {
    border-color: rgba(42, 147, 193, 0.30) !important;
    transform: translateY(-4px) !important;
    box-shadow: 0 16px 48px rgba(42, 147, 193, 0.10) !important;
}
```

The `backdrop-filter: blur(24px)` means the neural network fires and pulses behind the card glass — you can see it through the card. This is the central visual effect of the entire page. It must work.

---

### SECTION 3: THE AWAKENING EXPERIENCE

**Height**: auto (approximately 900–1000px desktop)

**Purpose**: Make the unknown known. Show the path. Executives don't buy mystery boxes.

```
┌─────────────────────────────────────────────────────────┐
│  THE PROCESS                                            │
│                                                         │
│  Your First Conversation Changes Everything             │
│  Here's what happens the moment you claim your spot:   │
│                                                         │
│  1──────────────2──────────────3──────────────4        │
│  [You Have a]  [Your Values]  [Partner Is]  [Partnership]
│  [Real Conv.]  [Are Mapped]   [Named]        [Begins]   │
│                                                         │
│  Steps connected by thin dashed blue line               │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ PUREBRAIN AWAKENING           ● Live            │   │
│  │─────────────────────────────────────────────────│   │
│  │ PureBrain: "Tell me what's most frustrating     │   │
│  │ about how you work with AI tools right now."    │   │
│  │                                                 │   │
│  │                    You: "They never remember    │   │
│  │                    anything. I explain my       │   │
│  │                    business every. single.time."│   │
│  │                                                 │   │
│  │ PureBrain: "That changes today. I'm going to   │   │
│  │ remember everything — and ask for more."        │   │
│  └─────────────────────────────────────────────────┘   │
│  [chat mockup — desktop only, hidden mobile]            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Chat mockup glassmorphism**:
```css
.pb-chat-mockup {
    background: rgba(8, 10, 18, 0.75) !important;
    border: 1px solid rgba(42, 147, 193, 0.22) !important;
    border-radius: 16px !important;
    backdrop-filter: blur(30px) !important;
    -webkit-backdrop-filter: blur(30px) !important;
    width: 520px !important;
    max-width: 100% !important;
    overflow: hidden !important;
    box-shadow: 0 24px 64px rgba(0, 0, 0, 0.5),
                0 0 0 1px rgba(42, 147, 193, 0.08) !important;
}

.pb-chat-header {
    background: rgba(42, 147, 193, 0.12) !important;
    border-bottom: 1px solid rgba(42, 147, 193, 0.15) !important;
    padding: 12px 20px !important;
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
}

.pb-chat-live-dot {
    width: 8px !important;
    height: 8px !important;
    background: #22c55e !important;
    border-radius: 50% !important;
    animation: pb-pulse-green 2s infinite !important;
}

@keyframes pb-pulse-green {
    0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.4); }
    50% { opacity: 0.8; box-shadow: 0 0 0 4px rgba(34, 197, 94, 0); }
}
```

The chat mockup has higher backdrop-filter blur (30px) than the feature cards (24px) — it should feel more immersive, more like an actual portal into the brain.

---

### SECTION 4: PRICING

**Height**: auto (approximately 900px desktop)

**Purpose**: Four tiers. One winner. Make Bonded inevitable.

```
┌─────────────────────────────────────────────────────────┐
│  CHOOSE YOUR ACCESS LEVEL                               │
│                                                         │
│  Pre-Launch Pricing — Locked In For Life                │
│  These prices are exclusive to this invite window.      │
│                                                         │
│                    MOST POPULAR — SAVE $47              │
│                          ▼                              │
│  ┌──────────┐ ┌───────────────────┐ ┌───────┐ ┌──────┐ │
│  │Awakened  │ │B  O  N  D  E  D   │ │Partn. │ │Unif. │ │
│  │          │ │ ← SCALE(1.03)     │ │       │ │      │ │
│  │  $79/mo  │ │   ~~$197~~        │ │$499/mo│ │$999/ │ │
│  │          │ │   $149/mo         │ │       │ │  mo  │ │
│  │[features]│ │[features + more]  │ │[feat] │ │[feat]│ │
│  │          │ │                   │ │       │ │      │ │
│  │Learn More│ │[CLAIM BONDED]     │ │Learn  │ │Learn │ │
│  │    ↓     │ │ ← orange CTA      │ │  More │ │ More │ │
│  └──────────┘ └───────────────────┘ └───────┘ └──────┘ │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**CRITICAL: Pricing cards must feel like they float IN FRONT OF the neural network, not on top of a solid background.**

```css
/* Base card — all tiers */
.pb-pricing-card {
    background: rgba(255, 255, 255, 0.025) !important;
    border: 1px solid rgba(255, 255, 255, 0.07) !important;
    border-radius: 20px !important;
    padding: 36px 28px !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
    transition: transform 0.3s ease, box-shadow 0.3s ease !important;
    flex: 1 !important;
}

.pb-pricing-card:hover {
    transform: translateY(-4px) !important;
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4) !important;
}

/* Bonded card — dominant, recommended */
.pb-pricing-card--bonded {
    background: linear-gradient(
        145deg,
        rgba(241, 66, 11, 0.08) 0%,
        rgba(42, 147, 193, 0.05) 100%
    ) !important;
    border: 1px solid rgba(241, 66, 11, 0.42) !important;
    box-shadow:
        0 0 40px rgba(241, 66, 11, 0.12),
        0 0 0 1px rgba(241, 66, 11, 0.08) !important;
    transform: scale(1.03) !important;
    position: relative !important;
    z-index: 2 !important;
}

.pb-pricing-card--bonded:hover {
    transform: scale(1.03) translateY(-4px) !important;
    box-shadow:
        0 0 60px rgba(241, 66, 11, 0.18),
        0 16px 48px rgba(0, 0, 0, 0.5) !important;
}

/* "MOST POPULAR" badge floating above Bonded card */
.pb-bonded-badge {
    position: absolute !important;
    top: -16px !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    background: #f1420b !important;
    color: white !important;
    font-family: 'Oswald', sans-serif !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.1em !important;
    padding: 6px 16px !important;
    border-radius: 100px !important;
    white-space: nowrap !important;
}
```

**Why this glass approach works with the 3D brain**: At `backdrop-filter: blur(20px)`, the neural network behind the pricing cards is blurred but the glow from orange firing events is still visible as a soft luminance shift through the card glass. When a neuron fires in orange behind the Bonded card, the card glass catches that warm glow. It is not scripted — it is organic. The randomness of the 3D firing creates a different look every time.

---

### SECTION 5: SOCIAL PROOF (Michael's Testimonial)

**Height**: auto (approximately 600px)

**Purpose**: One real person. No star ratings. Specificity is proof.

```
┌─────────────────────────────────────────────────────────┐
│  FROM OUR FIRST PARTNER                                 │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │                                                " │  │
│  │                                                  │  │
│  │  "[Michael's actual words about the awakening    │  │
│  │   experience — supplied by Jared before launch.  │  │
│  │   Should reference the naming conversation or    │  │
│  │   the memory difference.]"                       │  │
│  │                                                  │  │
│  │  [○ MH] Michael Hancock          [LinkedIn icon] │  │
│  │         [Title, Company]                         │  │
│  │                                                  │  │
│  │  ✓ Verified PureBrain Partner — AI partner: Metis│  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Testimonial card — premium glass**:
```css
.pb-testimonial-card {
    background: linear-gradient(
        145deg,
        rgba(42, 147, 193, 0.06) 0%,
        rgba(8, 10, 18, 0.80) 100%
    ) !important;
    border: 1px solid rgba(42, 147, 193, 0.20) !important;
    border-radius: 24px !important;
    padding: 52px 56px !important;
    backdrop-filter: blur(32px) !important;
    -webkit-backdrop-filter: blur(32px) !important;
    max-width: 720px !important;
    margin: 0 auto !important;
    position: relative !important;
}
```

The testimonial card has the highest backdrop-filter blur on the page (32px). It should feel like the most solid, most trustworthy element — almost opaque, but with faint neural flickers visible through the glass. The quote text must be fully readable. The brain glow provides subtle backing without competing.

---

### SECTION 6: URGENCY AND SCARCITY

**Height**: auto (approximately 900px)

**Purpose**: Convert fence-sitters. Facts, not pressure.

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│         Only 25 Spots. No Exceptions.                   │
│                                                         │
│         ●●●●●●●○○○○○○○○○○○○○○○○○○                       │
│         19 spots remaining                              │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │                                                 │   │
│  │ | This pricing is pre-launch only. When Pub...  │   │
│  │                                                 │   │
│  │ | The 25-spot limit is real. We're not          │   │
│  │   manufacturing urgency. Each new partner...    │   │
│  │                                                 │   │
│  │ | Wednesday is the deadline. This invitation    │   │
│  │   expires March 4, 2026 at 11:59 PM Eastern.   │   │
│  │                                                 │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│   [🔒 Price Lock Guarantee — $149/mo locked forever]    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Glass card for fact blocks**:
```css
.pb-urgency-facts {
    background: rgba(8, 10, 18, 0.65) !important;
    border: 1px solid rgba(241, 66, 11, 0.12) !important;
    border-radius: 20px !important;
    padding: 40px 48px !important;
    backdrop-filter: blur(24px) !important;
    -webkit-backdrop-filter: blur(24px) !important;
    max-width: 700px !important;
    margin: 0 auto !important;
}

.pb-fact-block {
    border-left: 3px solid rgba(241, 66, 11, 0.35) !important;
    padding-left: 20px !important;
    margin-bottom: 28px !important;
}

.pb-price-lock-badge {
    background: rgba(42, 147, 193, 0.06) !important;
    border: 1px solid rgba(42, 147, 193, 0.18) !important;
    border-radius: 12px !important;
    padding: 16px 28px !important;
    backdrop-filter: blur(20px) !important;
    display: inline-flex !important;
    align-items: center !important;
    gap: 12px !important;
}
```

**Section background treatment** (urgency section has a warm orange atmospheric shift):
```css
.pb-urgency {
    position: relative !important;
}

.pb-urgency::before {
    content: '' !important;
    position: absolute !important;
    bottom: 0 !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    width: 600px !important;
    height: 600px !important;
    background: radial-gradient(
        circle,
        rgba(241, 66, 11, 0.05) 0%,
        transparent 70%
    ) !important;
    pointer-events: none !important;
    z-index: 0 !important;
}
```

This CSS orb in the urgency section supplements the Three.js brain — it adds a warm orange tint to the lower half of the section without requiring any JS coordination.

---

### SECTION 7: FINAL CTA

**Height**: 100vh or large enough to feel like a landing

**Purpose**: One last moment. The invitation made personal.

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│           [3D BRAIN MOST VISIBLE HERE]                  │
│     [vignette lighter in center — brain center-stage]  │
│                                                         │
│         YOUR INVITATION EXPIRES WEDNESDAY               │
│                                                         │
│        Don't Let Someone Else                           │
│              Take Your Spot.                            │
│                                                         │
│      You were invited because Jared believes            │
│      you're ready for a different kind of               │
│      AI partnership. The window is open.                │
│                                                         │
│         ┌────────────────────────────────┐              │
│         │  ▶  Claim My Spot — $149/mo   │              │
│         └────────────────────────────────┘              │
│                                                         │
│    No setup fees  |  Cancel anytime  |  Locked for life │
│                                                         │
│         ┌──────────────────────────────┐                │
│         │  [DD]d [HH]h [MM]m [SS]s    │                │
│         │  Invite closes Mar 4, 11:59P │                │
│         └──────────────────────────────┘                │
│                                                         │
│    [● Jared photo]  "I picked you because I believe    │
│    in what you're building. — Jared Sanborn, Founder"   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Final CTA section design decision**: The vignette gradient is modified here so the center is LESS darkened than on other sections. The brain is most visible in this final section — as if the AI is looking back at you while you decide. The content floats over it without a glass card. No card wrapper on the CTA headline. Just Jared's words, the brain, and the button.

**Primary CTA button**:
```css
.pb-cta-primary {
    background: linear-gradient(135deg, #f1420b, #c93500) !important;
    color: white !important;
    font-family: 'Oswald', sans-serif !important;
    font-size: 1.15rem !important;
    letter-spacing: 0.06em !important;
    padding: 22px 64px !important;
    border-radius: 10px !important;
    border: none !important;
    cursor: pointer !important;
    text-decoration: none !important;
    display: inline-block !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    position: relative !important;
}

.pb-cta-primary::after {
    content: '' !important;
    position: absolute !important;
    inset: -1px !important;
    border-radius: 11px !important;
    background: linear-gradient(135deg, #f1420b, #c93500) !important;
    filter: blur(12px) !important;
    opacity: 0 !important;
    z-index: -1 !important;
    transition: opacity 0.3s ease !important;
}

.pb-cta-primary:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 12px 40px rgba(241, 66, 11, 0.45) !important;
}

.pb-cta-primary:hover::after {
    opacity: 0.6 !important;
}
```

The `::after` pseudo-element creates a bloom glow on hover — the button appears to radiate orange light when hovered. On the dark brain background this is visually electric.

---

## Mobile Responsive Wireframe

### Mobile Layout Changes (max-width: 767px)

```
┌─────────────────────────┐
│ [3D BRAIN — visible]    │ ← canvas still fixed, always present
│                         │
│  PRIVATE ACCESS         │
│  INVITATION ONLY        │
│                         │
│  You've Been            │
│  Invited.               │
│  ▔▔▔▔▔▔                 │
│                         │
│  Your AI partner is     │
│  waiting. 25 spots.     │
│  Closes Wednesday.      │
│                         │
│  [countdown]            │
│                         │
│ ┌─────────────────────┐ │
│ │  Claim My Spot      │ │ ← full-width
│ └─────────────────────┘ │
│                         │
│ ●●●●●●●○○○○○○○         │ ← dots wrap to 2 rows
│ 6 of 25 claimed         │
│                         │
└─────────────────────────┘
[fixed bottom bar]
┌─────────────────────────┐
│ 19 spots left — Claim → │ ← orange, fixed, z-index 999
└─────────────────────────┘
```

**Mobile Three.js adjustments**:
```javascript
// Detect mobile and reduce particle count
const isMobile = window.innerWidth < 768;
const nodeCount = isMobile ? 50 : 100;
const antialias = !isMobile;
renderer.setPixelRatio(Math.min(devicePixelRatio, isMobile ? 1.5 : 2));
```

**Mobile Section Changes**:
- Feature cards: single column stack, full width
- Pricing cards: single column stack, Bonded appears second (first above fold after scroll)
  - Bonded: remove scale(1.03), add `border-width: 2px` and stronger glow
- Chat mockup: `display: none` — hidden entirely on mobile
- Steps: vertical stack with vertical connector line
- Testimonial card: `padding: 32px 24px` (reduced from 52px 56px)
- Pricing cards: full width

**Mobile sticky bottom bar**:
```css
.pb-sticky-bar {
    position: fixed !important;
    bottom: 0 !important;
    left: 0 !important;
    right: 0 !important;
    background: rgba(8, 10, 18, 0.92) !important;
    border-top: 1px solid rgba(241, 66, 11, 0.3) !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
    padding: 14px 24px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    z-index: 999 !important;
    transform: translateY(100%) !important;
    transition: transform 0.3s ease !important;
}

/* Show on mobile only */
@media (max-width: 767px) {
    .pb-sticky-bar {
        display: flex !important;
    }
}

@media (min-width: 768px) {
    .pb-sticky-bar {
        display: none !important;
    }
}
```

JavaScript to show/hide sticky bar:
```javascript
// Show after hero exits viewport, hide when final CTA is in viewport
const heroObserver = new IntersectionObserver(([e]) => {
    stickyBar.style.transform = e.isIntersecting ? 'translateY(100%)' : 'translateY(0)';
});
heroObserver.observe(document.querySelector('.pb-hero'));

const finalCtaObserver = new IntersectionObserver(([e]) => {
    if (e.isIntersecting) stickyBar.style.transform = 'translateY(100%)';
});
finalCtaObserver.observe(document.querySelector('.pb-final-cta'));
```

---

## Animation Sequence (Page Load)

```
0ms     → Three.js canvas begins rendering (invisible, opacity: 0)
0ms     → Page content renders (all elements opacity: 0)
800ms   → canvas fade in (1.2s ease) — brain appears first
1000ms  → Badge pill fades in + slides up 8px (0.5s ease)
1200ms  → Headline fades in (0.6s ease)
1400ms  → Sub-headline fades in (0.5s ease)
1600ms  → Countdown card fades in (0.5s ease)
1800ms  → CTA button fades in + slides up 6px (0.5s ease)
2000ms  → Dots fill left to right, 80ms per dot
2400ms  → Scroll chevron appears (1s ease)
```

The brain appears FIRST and waits. Then the content materializes over it. Users spend ~800ms looking only at the neural network before seeing any words. That moment is intentional — it creates awe before the pitch begins.

---

## Countdown Timer Spec (Updated for March 4 Deadline)

```javascript
// March 4, 2026 — End of day Eastern (11:59:59 PM ET = UTC-5, so UTC 04:59:59 March 5)
const DEADLINE = new Date('2026-03-05T04:59:59Z');

function updateCountdown() {
    const now = new Date();
    const diff = DEADLINE - now;

    if (diff <= 0) {
        document.querySelectorAll('.pb-countdown').forEach(el => {
            el.innerHTML = '<span style="color: rgba(255,255,255,0.4)">WINDOW CLOSED</span>';
        });
        return;
    }

    const d = Math.floor(diff / 86400000);
    const h = Math.floor((diff % 86400000) / 3600000);
    const m = Math.floor((diff % 3600000) / 60000);
    const s = Math.floor((diff % 60000) / 1000);

    const fmt = n => String(n).padStart(2, '0');

    document.querySelectorAll('.pb-countdown').forEach(el => {
        el.innerHTML =
            `<span class="pb-cd-num">${d}</span><span class="pb-cd-sep">d</span>` +
            `<span class="pb-cd-num">${fmt(h)}</span><span class="pb-cd-sep">h</span>` +
            `<span class="pb-cd-num">${fmt(m)}</span><span class="pb-cd-sep">m</span>` +
            `<span class="pb-cd-num">${fmt(s)}</span><span class="pb-cd-sep">s</span>`;
    });
}

setInterval(updateCountdown, 1000);
updateCountdown();
```

```css
.pb-cd-num {
    font-family: 'Oswald', monospace !important;
    font-size: 1.6rem !important;
    color: #2a93c1 !important;
    font-variant-numeric: tabular-nums !important;
}

.pb-cd-sep {
    font-size: 0.8rem !important;
    color: rgba(255, 255, 255, 0.3) !important;
    margin: 0 6px 0 2px !important;
}
```

---

## Section Hierarchy Summary (Visual Weight)

| Section | Glass Opacity | Backdrop Blur | Brain Visibility |
|---------|--------------|---------------|-----------------|
| Hero | 0 (no card) | — | HIGH (most visible) |
| What Is PureBrain | 0.65–0.70 | 24px | MEDIUM |
| The Awakening | 0.70–0.75 | 24–30px | MEDIUM-LOW |
| Pricing | 0.55–0.65 | 20px | MEDIUM |
| Social Proof | 0.75–0.80 | 32px | LOW |
| Urgency | 0.65 | 24px | MEDIUM |
| Final CTA | 0 (no card) | — | HIGH (most visible) |

The brain is most visible at entry and exit — when it matters most for emotional impact.

---

## Typography System

```css
/* Load inside the HTML block */
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@400;600;700&family=Plus+Jakarta+Sans:wght@400;500;600&display=swap');

/* Applied inside #pb-invite-page */
#pb-invite-page {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: rgba(255, 255, 255, 0.88) !important;
    line-height: 1.6 !important;
}

/* Headline hierarchy */
#pb-invite-page .pb-h1 {
    font-family: 'Oswald', sans-serif !important;
    font-size: clamp(38px, 6vw, 72px) !important;
    font-weight: 700 !important;
    line-height: 1.05 !important;
    color: white !important;
    letter-spacing: -0.01em !important;
}

#pb-invite-page .pb-h2 {
    font-family: 'Oswald', sans-serif !important;
    font-size: clamp(24px, 3.5vw, 42px) !important;
    font-weight: 600 !important;
    line-height: 1.15 !important;
    color: white !important;
}

#pb-invite-page .pb-eyebrow {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.22em !important;
    text-transform: uppercase !important;
    color: rgba(255, 255, 255, 0.45) !important;
    font-weight: 600 !important;
}

#pb-invite-page .pb-body {
    font-size: 1.05rem !important;
    line-height: 1.75 !important;
    color: rgba(255, 255, 255, 0.65) !important;
    max-width: 640px !important;
}
```

`clamp()` handles fluid font scaling — no breakpoint-specific overrides needed for type.

---

## WordPress Deployment Notes

**Page template**: elementor_canvas (strips all theme chrome — needed for fullscreen experience)

**Block structure**:
```
<!-- wp:html -->
<link href="[Google Fonts URL]" rel="stylesheet">
<style>
    /* Three.js canvas positioning */
    #pb-brain-canvas {
        position: fixed !important;
        inset: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        z-index: 0 !important;
        pointer-events: none !important;
    }

    #pb-vignette {
        position: fixed !important;
        inset: 0 !important;
        z-index: 0 !important;
        pointer-events: none !important;
        /* gradient defined above */
    }

    #pb-invite-page {
        position: relative !important;
        z-index: 1 !important;
        min-height: 100vh !important;
    }

    /* All other CSS scoped to #pb-invite-page */
</style>

<canvas id="pb-brain-canvas"></canvas>
<div id="pb-vignette"></div>
<div id="pb-invite-page">
    <!-- All 7 sections -->
</div>

<script src="https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js"></script>
<script>
    /* Three.js neural network code */
    /* Countdown timer code */
    /* IntersectionObserver scroll animations */
    /* Mobile sticky bar logic */
</script>
<!-- /wp:html -->
```

**Critical**: The canvas must use `position: fixed` not `position: absolute`. Fixed means it stays put as the user scrolls — the brain doesn't move. The content scrolls over it. This is the core experience.

---

## Accessibility

- `<canvas>` gets `aria-hidden="true"` — it is decorative, not informational
- `prefers-reduced-motion`: when set, disable all CSS animations AND stop the Three.js camera rotation (keep the firing events — they are slow enough to not cause discomfort, but test)
- Countdown: `<div role="timer" aria-live="off" aria-label="Time remaining until invitation closes">` — aria-live="off" prevents screen readers from announcing every second
- CTA buttons: minimum 44x44px touch target
- All body copy: minimum 1rem (16px)
- Glass cards: text must pass WCAG AA contrast even through blur. Test rgba(255,255,255,0.65) on rgba(8,10,18,0.65) — it passes at 1.05rem+

---

## Open Questions (Need Jared's Input Before Build)

1. **Michael's actual testimonial quote** — still needed. Do not launch without real words.
2. **Michael's title and company** — needed for the testimonial card author line.
3. **How many spots claimed at launch?** — sets the dots counter. Do not default to 0 (implies no one bought). Minimum should be Michael (1).
4. **CTA destination confirmed**: purebrain.ai/pay-test-2/ — confirmed in brief. Use this.
5. **Password for the WP page** — carry over from existing invitation page: "purebrain25" or new one?
6. **Photo of Jared for the signature block** — circle avatar, 48px. Use WP image ID 520 (existing testimonial photo)?

---

## Acceptance Criteria

- [ ] Three.js neural network renders on desktop at 60fps
- [ ] Neural network renders on mobile at 30fps+ (acceptable)
- [ ] WebGL fallback triggers correctly on browsers that do not support it
- [ ] Canvas is fixed — does not scroll with content
- [ ] backdrop-filter blur is visible on all major browsers (check Safari — sometimes needs -webkit- prefix only)
- [ ] Countdown counts correctly to March 4, 11:59 PM Eastern
- [ ] When countdown hits 0, shows "WINDOW CLOSED" not negative numbers
- [ ] Bonded pricing card is visually dominant and unmistakable
- [ ] CTA links correctly to purebrain.ai/pay-test-2/
- [ ] Mobile sticky bar appears on scroll, disappears at final CTA section
- [ ] Chat mockup hidden on mobile
- [ ] Page renders correctly at 375px (iPhone SE)
- [ ] Page renders correctly at 768px (iPad)
- [ ] Page renders correctly at 1440px (desktop)
- [ ] All CSS scoped to #pb-invite-page — no theme bleed
- [ ] Zero console errors
- [ ] Page password-protected in WordPress admin

---

## Memory Written

Path: `.claude/memory/agent-learnings/feature-designer/2026-02-27--threejs-neural-network-invite-page.md`
Type: synthesis
Topic: Three.js fixed-canvas neural network background with glassmorphism content overlay — PureBrain invite page

Key learnings:
- Fixed canvas (not absolute) is the correct z-index architecture for scroll-over-3D layouts
- Brain appears before text on load (800ms head start) — creates awe before pitch
- Glassmorphism opacity levels scale by section purpose: trust sections get more opacity, hero/CTA get less
- Mobile: reduce node count to 50, antialias off, pixelRatio capped at 1.5
- Neural firing events (orange flashes traveling across connections) make abstract AI intelligence viscerally visible
- Warm orange CSS orb in urgency section supplements Three.js without requiring JS coordination
- Deadline: March 4 EOD Eastern = UTC March 5 04:59:59Z in the countdown target
