# Portal Welcome Hero: Neural Network Brain Animation

**Date**: 2026-03-16
**Type**: technique
**Topic**: Replacing spinning rings canvas animation with 2D neural net brain

## What Was Done

Replaced the `startAetherCanvas()` function in `/home/jared/purebrain_portal/portal-pb-styled.html`
with a neural network brain animation. Also added `.welcome-hero__brain-stream` label element.

## Key Patterns

### Portal Canvas Animation Architecture
- Function: `startAetherCanvas(canvas)` at ~line 8860
- Canvas: 600x600px logical, HiDPI scaled via `dpr = devicePixelRatio`
- Scale factor: `S = cssWidth / 500` (reference 500px)
- Loop throttled to 30fps via `lastFrameTime` + `FRAME_MS = 1000/30`
- Stop condition: `if (!document.getElementById('welcomeHero')) return;`
- LOGO_URL: base64 PNG defined at line ~8805

### Neural Net Animation Structure
- 27 nodes: 1 center + 8 inner (r=62) + 12 mid (r=122) + 6 outer (r=180)
- Edges: auto-built between nodes < 160*S apart
- Pulses: travelling dot signals along edges, 22 max, cascade-fire on arrival
- Fire: `fireNode(idx)` — sets glow=1, spawns 2-4 pulses, decays over 22-44 frames
- Random trigger: `maybeFireRandom()` every 16-44 frames

### Brand Colors
- Orange: #f1420b (RGB 241,66,11) — used for orange-flagged nodes + pulses
- Blue: #2a93c1 (RGB 42,147,193) — used for edges + blue nodes + pulses
- Edges always draw in blue; pulse color matches source node

### Gotcha: `var` re-declaration in loops
- In the node-building loop, used `OR2` (not `OR`) to avoid conflict with
  built-in `OR` concept and naming ambiguity across for-loop vars.

### Brain Stream Label
- Added `.welcome-hero__brain-stream` CSS class (mono, small-caps, 0.7rem, blue 0.5 alpha)
- Added div with id `welcomeHeroBrainStream` to `renderWelcomeHero()`
- Updated `updateAIName()` section (~line 7387) to sync label text on name change

### File Edit Approach
- The Edit tool kept failing with "modified since read" after earlier partial edits
- Used Python string manipulation to safely replace the entire function block
- Located function boundaries by searching for unique start/end markers

## Files Modified
- `/home/jared/purebrain_portal/portal-pb-styled.html`
  - Line ~2021: added `.welcome-hero__brain-stream` CSS
  - Line ~7387: added `welcomeHeroBrainStream` update in `updateAIName`
  - Line ~8840: added brain stream label element in `renderWelcomeHero`
  - Line ~8855-9141: full replacement of `startAetherCanvas` with neural net

## Verification
- Old animation fully removed (rings/particles/scanbeam gone from welcome hero)
- HMI voice overlay rings/particles untouched (confirmed at line 14029+)
- Portal restarted cleanly via restart.sh, health check passed
