# Portal Bug Fix Session — 6 Regressions from Background Agent Overwrite

**Date**: 2026-03-03
**File**: `/home/jared/purebrain_portal/portal-pb-styled.html`
**Trigger**: ST# URGENT — background file-upload-staging agent overwrote portal

---

## What Happened
A background agent overwrote `portal-pb-styled.html`, causing 6 regressions. All were fixed in one session using Python-based programmatic edits (not Edit tool, due to large file size ~5400 lines).

---

## Bug 1: THREE Duplicate Function Blocks (DELETE COPIES 2+3)

**Root cause**: Background agent duplicated the entire WELCOME HERO block 3x.

**Fix**: Python line-range deletion. Copy 2 started at line 3436 (1-indexed), Copy 3 ended at line 3902. Deleted lines 3435-3901 (0-indexed). Verified by checking `function renderWelcomeHero` count dropped from 3 to 1.

**Key pattern**: Copies 2 and 3 used `document.getElementById('chat-messages')` (WRONG — scrolls with messages). Copy 1 (KEEP) uses `document.getElementById('panel-chat')` (CORRECT — sits behind scrolling).

---

## Bug 2: Missing Context Menu (Right-click/Long-press Reply)

**Old**: Simple click-on-bubble triggered reply.

**New**:
- Desktop: right-click shows context menu
- Mobile: 500ms long-press shows context menu
- Menu items: Reply + Copy text

**Parts added**:
1. CSS: `.msg-context-menu`, `.msg-context-menu-item`, `@keyframes ctxFadeIn` (after `.reply-cancel-btn:hover`)
2. JS: `showMsgContextMenu()`, `hideMsgContextMenu()`, click listeners (after `replyCancelBtn` listener)
3. HTML: `<div id="msg-context-menu">` (before `</body>`)
4. Replaced click IIFE with contextmenu + touchstart IIFE in `addMessage()`

---

## Bug 3: Static Thinking Dots

**Old**: `bubble.textContent = '...';`
**New**: `bubble.innerHTML = '<span class="thinking-dots">...</span>'` with `@keyframes dotBounce` CSS

---

## Bug 4: Optimistic Message Rendering

**Problem**: Thinking dots appeared above the user's message.

**Fix**:
1. Added `var lastSentOptimisticText = null;` near `replyingTo` declaration
2. In `_dispatchChatMessage()`: added `addMessage(fullMsg, 'user', ...)` and `lastSentOptimisticText = fullMsg` BEFORE `addThinkingIndicator()`
3. In `chatWs.onmessage`: added early return if `msg.role === 'user'` matches `lastSentOptimisticText` (prevents double display)

---

## Bugs 5 & 6: Already Working

- Drag/drop: `dragover` already had `e.preventDefault()` — no fix needed
- Context meter stale after compact: resolved by next API poll — no fix needed

---

## Technical Notes

- File is ~5000 lines — Edit tool struggles with it; Python `content.replace()` is faster and safer
- Script 0 is `<script type="importmap">` JSON — `node --check` correctly reports syntax error on it, but it's not real JS
- Scripts 1, 2, 3: all passed `node --check` clean
- Portal runs on port 8097

---

## Verification
- `grep -c "function renderWelcomeHero"` = 2 (one definition + one call)
- Node syntax check: Scripts 1, 2, 3 clean
- Portal server restarted and accepting connections
- Telegram confirmation sent to Jared
