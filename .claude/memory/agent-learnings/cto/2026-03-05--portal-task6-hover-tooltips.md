# Portal Task 6: Hover Tooltips on Buttons

**Date**: 2026-03-05
**Type**: operational
**Topic**: Tooltip system for portal.purebrain.ai/pb — 1.5s hover delay

## What Was Built

Patch script: `/home/jared/purebrain_portal/apply_task6_tooltips.py`

Adds a hover tooltip system to all interactive buttons in the self-contained 340KB portal HTML file.

## Architecture Decisions

### Single Shared Tooltip Element
- One `<div id="pb-tooltip">` injected after `<body>` open tag
- Repositioned via JS on each hover — no per-element tooltips
- `position: fixed` so z-index stacking never breaks; `pointer-events: none` so it never blocks interaction

### 1.5s Delay Implementation
- `setTimeout(fn, 1500)` on mouseenter — timer is cleared immediately on mouseleave
- Timer stored in closure variable `timer`; `clearTimer()` on any leave/click
- This prevents flicker when mouse passes quickly over buttons

### Event Delegation (Critical Pattern)
- `document.addEventListener('mouseenter', fn, true)` — capture phase
- This means dynamically-created buttons (code-copy-btn, bookmark-btn, fleet-copy-btn, cmd-order-btn) get tooltips automatically without any additional binding
- `findTooltipEl(target, 4)` walks up 4 levels to handle clicks on child icons (SVG etc)

### Auto-flip Above/Below
- Default: tooltip appears above element with downward arrow
- If `top < 8px` (no room above), flips below element with upward arrow
- CSS `.pb-tt-below` class switches the `::after` arrow direction

### Fade Animation
- `opacity: 0` default, `opacity: 1` when `.pb-tt-visible` added
- `transition: opacity 0.15s ease` — 150ms fade-in
- Hides instantly (class removed synchronously on mouseleave)

## CSS Anchor Fix (Critical Gotcha)

The `</style>` closing tag in portal-pb-styled.html is NOT directly followed by `</head>`.
There are THREE.JS importmap script tags between them:

```
</style>              ← line 2572
                      ← blank line
<!-- THREE.JS -->     ← line 2574
<script type="importmap">...
</script>
</head>               ← line 2583
```

Correct anchor: `"</style>\n\n<!-- THREE.JS"`
Wrong anchor (previous attempt): `"</style>\n</head>"`

## Body Tag Anchor
`<body>` is followed by blank line then 3D Neural Network comment:
- Correct: `"<body>\n\n<!-- 3D Neural Network"`

## Buttons Covered (26 total + dynamic)

**Static HTML buttons** (via data-tooltip attribute patches):
- Header: Resume, Restart, Settings, Logout
- Terminal: SEND, Add (+), Close tab (static)
- Chat: Send, Attach, Search toggle, Poke, Search prev/next/close, Reply cancel
- Teams: Inject SEND
- Fleet: Refresh
- Status: Refresh
- Files: Copy Link
- Sidebar: 6 nav-items (Terminal, Chat, Teams, Fleet, Status, Files)
- Upload modal: Original Quality, Compressed

**Dynamic JS buttons** (via dataset.tooltip assignment or innerHTML template):
- code-copy-btn: `copyBtn.dataset.tooltip = 'Copy to clipboard'`
- bookmark-btn: `bmBtn.dataset.tooltip = 'Bookmark this moment'`
- fleet-copy-btn: Added to innerHTML string template
- term-tab-close (dynamic): Added to innerHTML string template
- cmd-order-btn up/down: Partial class match on `data-dir="up"` / `data-dir="down"`

## File Sizes
- Input portal: ~340KB
- Added ~4KB of CSS + JS (tooltip engine is lightweight)

## Patch Script Pattern (Consistent with Tasks 1-5)
- Read → backup (timestamped) → patch → verify → write
- Anchors are minimum unique strings needed to avoid false matches
- Each patch is independent; WARNINGs on dynamic patches don't abort
- Core system (CSS + div + JS engine) uses sys.exit(1) on failure
