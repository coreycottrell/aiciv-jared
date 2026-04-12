# Portal Thinking Dots — Restored & Enhanced

**Date**: 2026-03-09
**Agent**: dept-systems-technology
**Type**: bug fix + enhancement
**Status**: Shipped

---

## What Was Fixed

Thinking dots (●) were not visually prominent in the portal. Jared wanted to see the animated spinning indicator next to dots to know Aether is actively working, before responses appear.

---

## Root Cause

Two gaps:
1. The dots used period characters (`.`) instead of filled circles (`●`) — less visible
2. The live spinning indicator only appeared when Jared sent a message via the portal (`_dispatchChatMessage`). It did NOT appear when the thinking monitor pushed thinking blocks from background Aether work. So if Jared opened the portal while Aether was thinking, he only saw thinking text blocks arriving but no live animated indicator.

---

## Fix Applied

**File**: `/home/jared/purebrain_portal/portal-pb-styled.html`
**Backup**: `portal-pb-styled.html.bak.thinking-dots-fix-20260309`

### Change 1 — Dots visual (line ~6046)
```js
// Before
bubble.innerHTML = '... <span class="td">.</span><span class="td">.</span><span class="td">.</span> ...'
// After
bubble.innerHTML = '... <span class="td">●</span><span class="td">●</span><span class="td">●</span> ...'
```
CSS `dotBounce` animation still applies — now bouncing filled circles instead of periods.

### Change 2 — Live indicator from WS thinking blocks (line ~6362)
```js
if (msg.role === 'thinking') {
  var LIVE_THINKING_ID = 'thinking-live-indicator';
  if (!document.getElementById(LIVE_THINKING_ID)) {
    addThinkingIndicator(LIVE_THINKING_ID);  // spinning hex + ●●● dots
  }
  // Auto-hide 8s after last thinking block
  if (window._liveThinkingTimer) clearTimeout(window._liveThinkingTimer);
  window._liveThinkingTimer = setTimeout(function() {
    removeThinkingIndicator(LIVE_THINKING_ID);
    window._liveThinkingTimer = null;
  }, 8000);
  addMessage(msg.text, 'thinking', msg.timestamp, msg.id);
  return;
}
```

### Change 3 — Timer cleanup when assistant message arrives (line ~6385)
```js
if (window._liveThinkingTimer) { clearTimeout(window._liveThinkingTimer); window._liveThinkingTimer = null; }
```
Prevents timer firing after response already started streaming.

---

## Behavior After Fix

1. **Portal message sent** → thinking indicator appears immediately (existing behavior)
2. **WS thinking block arrives** → thinking indicator appears (new behavior)
3. **Multiple thinking blocks** → single indicator, timer resets each time
4. **Assistant response starts** → all thinking indicators removed, timer cancelled
5. **No response after 8s of thinking** → indicator auto-hides (graceful edge case)

---

## Architecture Notes

- `LIVE_THINKING_ID = 'thinking-live-indicator'` is a stable element id — prevents duplicate indicators
- The cleanup at WS assistant handler (`querySelectorAll('[id^="thinking-"]')`) catches this id too — doubly safe
- No server restart needed: `FileResponse` reads HTML from disk on each request
- The `dotBounce` CSS animation produces bouncing ●●● — same visual language as Claude Code white dots

---

## Memory Written

Path: `.claude/memory/departments/systems-technology/2026-03-09--portal-thinking-dots-restored.md`
Type: bug fix + enhancement
