# Portal UI Upgrades — Carbon Copy from Reference File
**Date**: 2026-03-03
**Type**: pattern
**Agent**: dept-systems-technology

## What Was Done

Applied 4 UI upgrades to `/home/jared/purebrain_portal/portal-pb-styled.html` by carbon-copying patterns from the reference file `purebrain-portal-rebranded FINAL.html`.

## Changes Applied

### 1. Header Logo — PT Icon
- Converted `MA1.BI-1.2.4-002-211107-Icon - PT.png` to base64 (resized to 64x64 via PIL first — original was 2100x2100 = ~3MB base64, resized = ~10KB)
- Embedded as `<img src="data:image/png;base64,..." style="width:28px;height:28px;...">` in `.header-left` before the PUREBRAIN text span
- Added `filter:drop-shadow(0 0 4px rgba(241,66,11,0.5))` for orange glow

### 2. AI Message Avatar — Spinning Hexagon
- Added CSS classes: `.msg-avatar-hex`, `.msg-avatar-hex-inner`, `.msg-avatar-hex-inner img`
- Added `@keyframes hexAvatarSpin` and `.msg-avatar-hex.thinking` for 1.2s spin
- Updated `addMessage()` to: when `role === 'assistant'`, create a `div.msg-row` with the hex avatar + bubble side by side (flex row)
- Avatar uses `https://puremarketing.ai/wp-content/uploads/2025/07/2.-Main-Icon-Orange-to-Blue-PM-2.png`

### 3. Thinking Indicator — Spinning Icon + Dots
- Added `addThinkingIndicator(id)` function — creates `.msg.assistant` with spinning hex + `...` bubble
- Added `removeThinkingIndicator(id)` function
- Updated `sendChat()` to call `addThinkingIndicator(thinkingId)` before fetch and `removeThinkingIndicator(thinkingId)` in `.finally()`

### 4. Background Spinning Wheel — Welcome Hero Canvas
- Added `renderWelcomeHero()` and `startAetherCanvas(canvas)` functions (full Aether canvas: rings, particles, scan beam, data arcs, center glow, spinning logo)
- Added `.welcome-hero` CSS positioned absolutely at center of `#chat-messages`, `z-index: 0`, `opacity: 0.22`
- `.welcome-hero.has-messages` reduces to `opacity: 0.18` when messages arrive
- `#chat-messages` and `.chat-input-bar` get `z-index: 1` so content sits on top
- `loadChatHistory()` calls `renderWelcomeHero()` after clearing messages
- `addMessage()` adds `has-messages` class to hero to fade it down when chat starts
- Canvas size: 240x240px (scaled from reference 300px to fit portal better)

## Key Technical Notes

- **PIL resize trick**: Original PNG was 2100x2100 = ~3MB base64. Resized to 64x64 = ~10KB. Always resize icons before base64-embedding.
- **addMessage row structure change**: The current portal's `addMessage` didn't use `.msg-row` div. Added one when role is assistant to hold avatar + bubble side by side. User messages keep old structure (no avatar).
- **Welcome hero is NOT removed when chat starts** — it stays faded (Jared's explicit requirement: "messages scroll over it as its happening").
- **Portal runs on port 8097** — multiple stale instances accumulate; always `ps aux | grep portal_server` and kill all before restart.

## Files Modified
- `/home/jared/purebrain_portal/portal-pb-styled.html`

## Verification
- All 6 replacement operations confirmed successful via Python script output
- Portal restarted, confirmed running on port 8097
- HTML file sent to Telegram successfully
