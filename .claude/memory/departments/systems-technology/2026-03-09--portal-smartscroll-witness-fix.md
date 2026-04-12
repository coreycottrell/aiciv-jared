# Portal smartScroll() — Witness Fix Applied

**Date**: 2026-03-09
**Type**: technique / gotcha
**File**: `/home/jared/purebrain_portal/portal-pb-styled.html`

## Summary

Applied Witness Collective's smartScroll() guard to PureBrain portal. The file already had `smartScroll()`, `isNearBottom()`, and `_userWasNearBottom` tracking — two unconditional AI/system scroll calls remained.

## What Was Fixed

### Fix 1 — `addMessage()` image load event (line ~5618)
```javascript
// BEFORE (unconditional — fires async, after user may have scrolled up)
imgEl.addEventListener('load', function() { chatMessages.scrollTop = chatMessages.scrollHeight; });

// AFTER
imgEl.addEventListener('load', function() { smartScroll(chatMessages); });
```
Context: Inside `addMessage()`, `role === 'user'` branch, inline image rendering for history replay. The initial scroll decision was correctly using `_wasNearBottom`, but the async `load` event fired later with no guard.

### Fix 2 — Upload ack after server response (line ~6517)
```javascript
// BEFORE (redundant unconditional after addMessage() already handled scroll)
if (data.ack) {
  addMessage(data.ack, 'assistant', null, data.ack_msg_id || ('ack-' + Date.now()));
}
chatMessages.scrollTop = chatMessages.scrollHeight;

// AFTER
smartScroll(chatMessages); // ack is assistant message, respect user scroll
```
Context: `addMessage()` itself already handles smart scroll via pre-captured `_wasNearBottom`. The extra unconditional scroll after it was a redundant bypass.

## Intentionally Unconditional Scrolls (Left Alone)

| Location | Reason |
|----------|--------|
| Panel switch (tab nav) | User returning to chat, not new message |
| Scroll-to-bottom button click | User explicitly requested |
| `addMessage()` final scroll (guarded by `_wasNearBottom`) | Already smart via pre-capture pattern |
| `loadChatHistory()` initial load | First render, no user scroll yet |
| Upload progress indicator | User just dropped file |
| Thinking indicator after all uploads | User-initiated send flow |
| User sends message (commented unconditional) | Spec: user-send stays unconditional |
| `uploadFile()` drag-drop progress | User-initiated |
| `addFileImageMessage()` img.load | User's own image, user sent it |

## Architecture Already Present

The portal already had a sophisticated scroll architecture:
- `_userWasNearBottom` tracking flag updated on every scroll event
- `isNearBottom(el, threshold)` with 300px threshold
- `smartScroll(el)` using rAF + dual-check (flag OR current position)
- `updateScrollToBottomBtn()` showing/hiding the floating button
- Streaming handler already calling `smartScroll(chatMessages)`
- `addThinkingIndicator()` already calling `smartScroll(chatMessages)`

Only 2 async-delayed or redundant unconditional paths had slipped through.

## Product Note

This is a PRODUCT FEATURE for all PureBrain users (Portal Core UX Rules, locked 2026-03-08). Any future portal work must respect: AI/system messages → smartScroll(), user-initiated send → unconditional.
