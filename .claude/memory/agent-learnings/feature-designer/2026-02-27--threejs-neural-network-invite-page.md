# feature-designer Memory: Three.js Neural Network Background + Glassmorphism Invite Page

**Date**: 2026-02-27
**Agent**: feature-designer
**Type**: synthesis
**Topic**: Three.js fixed-canvas neural network background with glassmorphism content overlay — PureBrain invite page
**Confidence**: high
**Tags**: ux, threejs, glassmorphism, purebrain, invite-only, neural-network, 3d-background, premium

---

## Context

Designed the upgraded UX spec for PureBrain.ai's invite-only landing page. This is an upgrade over the Feb 26 spec (CSS orbs) — the core difference is a fullscreen Three.js neural network firing in real time as the background, with all content overlaid as glassmorphism panels.

Full spec written to: `/home/jared/projects/AI-CIV/aether/exports/invite-only-threejs-ux-spec.md`

---

## Key Architectural Pattern: Fixed Canvas + Scrollable Content Overlay

```
canvas (position: fixed, z-index: 0) — THREE.JS BRAIN
vignette div (position: fixed, z-index: 0) — OVERLAY GRADIENT
content div (position: relative, z-index: 1) — ALL TEXT/CARDS
```

The canvas uses `position: fixed`, not `position: absolute`. This means the neural network stays put while the content scrolls over it. The brain is always in viewport. This creates the sensation of content sliding across a living neural background.

**If you use `position: absolute` on the canvas, the brain only appears in the first viewport and users scroll away from it.**

---

## Neural Network Firing Events (The Key Visual)

The magic is NOT the static nodes/edges. It is the firing events:

- Every 800–1400ms, pick a random origin node
- Flash its connected edges one at a time (200ms each): opacity 0.12 → 1.0 → fade back
- Flash color: orange (#f1420b) primary, blue (#2a93c1) secondary ripple
- 40% chance: chain reaction to adjacent node with 150ms delay

This makes the network look like a thinking brain rather than a static 3D graph. Orange flashes through the glassmorphism card glass create organic warm glow — impossible to script intentionally, but the randomness creates it automatically.

---

## Glassmorphism Opacity Hierarchy by Purpose

| Section | Backdrop Blur | Brain Visibility | Reason |
|---------|--------------|-----------------|--------|
| Hero | None (bare text) | HIGH | Awe before pitch |
| Feature cards | 24px | MEDIUM | Read through the glass |
| Chat mockup | 30px | MEDIUM-LOW | Immersive portal feel |
| Pricing cards | 20px | MEDIUM | Cards feel like windows |
| Testimonial | 32px | LOW | Trust needs solid backing |
| Urgency | 24px | MEDIUM | Facts over atmosphere |
| Final CTA | None (bare text) | HIGH | Brain + person face to face |

Rule: **Trust sections get most opacity. Emotional/action sections get least.**

---

## Brain Reveals Before Text (800ms Lead)

Page load sequence:
- 0ms → canvas renders, opacity 0
- 800ms → canvas fades in
- 1000ms → text begins materializing

Users spend 800ms watching only the firing brain before seeing any copy. This is not a performance issue — it is intentional design. Awe before pitch.

---

## Mobile Performance

- Node count: 50 (not 100)
- antialias: false
- pixelRatio: capped at 1.5 (not 2)
- Mouse parallax: disabled
- Auto-rotation: slightly faster (0.0005 vs 0.0003 rad/frame)
- Chat mockup: hidden entirely

Firing events: kept on mobile. They are slow enough (800–1400ms interval) to not cause motion sickness and are the primary emotional payload of the 3D scene.

---

## Deadline Conversion (Eastern Time)

March 4, 2026 EOD Eastern (UTC-5 in winter):
```javascript
const DEADLINE = new Date('2026-03-05T04:59:59Z');
```

**Never use local time strings in countdown JS.** Use UTC and let JavaScript convert.
When you write `new Date('2026-03-04T23:59:59')` without a timezone, browsers interpret it inconsistently (some as UTC, some as local). Always use the Z suffix.

---

## Supplementing Three.js with CSS Orbs

In the urgency section, a CSS pseudo-element adds a warm orange atmospheric orb:
```css
.pb-urgency::before {
    background: radial-gradient(circle, rgba(241, 66, 11, 0.05) 0%, transparent 70%);
    position: absolute; bottom: 0; left: 50%;
}
```

This supplements the Three.js scene without requiring any JS coordination. If the brain fires orange near this section's scroll position, the CSS orb reinforces the orange urgency tone. Both are independent and both work.

---

## CTA Button Bloom Glow Technique

```css
.pb-cta-primary::after {
    content: '';
    position: absolute;
    inset: -1px;
    border-radius: 11px;
    background: linear-gradient(135deg, #f1420b, #c93500);
    filter: blur(12px);
    opacity: 0;
    z-index: -1;
    transition: opacity 0.3s ease;
}

.pb-cta-primary:hover::after {
    opacity: 0.6;
}
```

The `::after` pseudo-element creates a blurred copy of the button's gradient that appears as a radiance glow on hover. On the dark 3D brain background this is visually electric — the button appears to emit light.

---

## Files

- Full spec: `/home/jared/projects/AI-CIV/aether/exports/invite-only-threejs-ux-spec.md`
- Prior spec (CSS orbs version, Feb 26): `/home/jared/projects/AI-CIV/aether/exports/invite-only-page-ux-spec.md`
- Live page: purebrain.ai/invitation/ (password: purebrain25)
