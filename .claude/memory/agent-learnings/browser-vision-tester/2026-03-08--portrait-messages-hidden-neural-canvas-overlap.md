# Portrait: Messages Hidden by Neural Canvas Overlapping Chat Container

**Date**: 2026-03-08
**Type**: gotcha
**Agent**: browser-vision-tester
**Topic**: PureBrain portal portrait mode — #chat-messages invisible because neural canvas covers chat area

---

## Context

Jared reported chat messages are invisible on mobile portrait (375x812) but visible on landscape (812x375).

## Root Cause

The `#welcomeHero` canvas (the rotating neural animation) renders at:
- `top: 60, left: -112, width: 600, height: 600`
- It overflows the viewport (600px wide on 375px screen = hangs 337px off right)
- `pointer-events: none` — so clicks pass through
- But it **visually covers #chat-messages** because the canvas is a sibling of `.content` and paints over it

The `#chat-messages` itself is perfectly healthy:
- 200 messages in DOM
- scrollHeight=2018, scrolled to bottom (scrollTop=1474)
- BoundingRect: top=99, height=544px — occupies most of the screen
- overflow=hidden auto (scroll enabled)

The messages ARE there. The neural canvas renders on top of them visually, making the dark text/bubbles invisible against the swirling dark animation background.

## Why Portrait vs Landscape Differs

In **portrait (375x812)**:
- `.main` is 707px tall — plenty of room for both canvas and messages to overlap
- The 600x600 canvas sits over the chat area
- Messages appear invisible because canvas background obscures them

In **landscape (812x375)**:
- The sidebar is visible (desktop layout kicks in)
- `.main` has `flex-direction: row` — sidebar takes ~164px, chat gets ~634px wide
- The canvas is still there but at 812px width the geometry works differently
- Landscape viewport height=375px means `.main`=327px, chat-messages=151px
- Canvas starts at left=-112 but with sidebar offset, its overlap with chat column is reduced

## Key Data

Portrait:
- chat-messages: top=99, height=544, bottom=643
- welcomeHero canvas: top=60, left=-112, width=600, height=600
- Canvas bottom: 60+600=660 → covers all of chat-messages (99-643)
- `#pb-canvas-container` display=none (Three.js neural bg is off) — it's the WELCOME HERO canvas
- canvas.parentElement.id = 'welcomeHero', class = 'welcome-hero has-messages'

## The Fix

Option A — Hide canvas when messages are present (class `has-messages` already on parent):
```css
.welcome-hero.has-messages .welcome-hero__canvas {
    display: none;
}
```

Option B — Move canvas behind chat (z-index):
```css
#welcomeHero {
    z-index: 0;
}
#chat-messages {
    z-index: 1;  /* already is 1 */
    background: rgba(8, 10, 15, 0.9); /* opaque bg to hide canvas behind */
}
```

Option C — Constrain canvas height to not overlap:
```css
.welcome-hero {
    position: absolute; /* or relative with overflow:hidden */
    height: 0; /* collapse when has-messages */
}
.welcome-hero.has-messages {
    display: none;
}
```

**Best fix**: `.welcome-hero.has-messages { display: none !important; }` — the class is already toggled.

## Pattern

When a background animation element (canvas/WebGL) is a sibling to the main content and both use transparent backgrounds, the canvas will visually obscure content even if z-index ordering "should" be correct. The solution is to hide the animation when content is present.

The `has-messages` class already exists on `#welcomeHero` — the CSS rule just isn't there yet.
