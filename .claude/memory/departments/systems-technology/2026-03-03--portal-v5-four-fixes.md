# Portal v5 — 4 Fixes Pattern

**Date**: 2026-03-03
**Type**: technique
**Topic**: PureBrain portal UI patch via Python string replacement

## What Was Done

Applied 4 fixes to `/home/jared/projects/AI-CIV/aether/exports/purebrain-portal-rebranded.html`:

### Fix 1: Remove Multi-Chat Features
- Removed `<button class="sidebar__new-chat">` button
- Removed entire "Recent Conversations" nav-section with `chat-history` div
- Portal is a single continuous brain stream, not a multi-chat app

### Fix 2: Spinning Hexagon Background in Chat Area
- Added CSS: `.chat-hex-bg`, `.chat-hex-bg__svg`, `@keyframes hexSpin`, `@keyframes hexSpinReverse`
- Added HTML SVG element inside `.chat-panel` with `position:relative` style
- Outer rings: blue (#2a93c1), 45s spin, 0.07 opacity
- Inner ring: orange (#f1420b), 30s reverse spin, 0.05 opacity
- Chat messages and input given `position:relative; z-index:1` to sit above

### Fix 3: Witness → Dynamic AI Name
- `addMessage()` meta label changed from hardcoded `'Witness'` to `(storedAIName || 'AI')`
- `updateSidebarAIName()` updated to also set chat header subtitle and panel title

### Fix 4: PureTech Hexagon Avatar
- `addMessage()` for assistant role: replaced `msg-avatar-inner` with `W` text
  with `msg-avatar-hex` + `msg-avatar-hex-inner` + `<img>` pointing to puremarketing.ai icon
- Added `addThinkingIndicator(id)` / `removeThinkingIndicator(id)` functions
- Thinking indicator shows spinning hexagon (CSS class `.thinking`) with `...` bubble
- `sendChat()` calls `addThinkingIndicator` before fetch, removes in `.finally()`

## Key Technical Patterns

- **Python string replacement** is reliable for large HTML file edits — use `str.replace(old, new, 1)`
- **Always verify exact string exists** before patching: `if old_string in content:` with fallback WARN
- **CSS insertion point**: find a stable comment like `/* Mobile bottom nav */` to insert before
- **Read tool requirement**: The Edit tool requires reading first; for large files use Bash reads

## File Location
`/home/jared/projects/AI-CIV/aether/exports/purebrain-portal-rebranded.html`

## Verification Done
- 16/17 checks passed (only failure: CSS class `.chat-history-empty` definition remains in stylesheet, which is correct)
- `No recent chats` text: completely absent
- `chatHistory` div id: completely absent
- `onclick="handleNewChat()"`: completely absent
- `'Witness'` in JS meta label: completely absent
