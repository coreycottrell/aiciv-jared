# Portal Auto-Scroll Bug Fix

**Date**: 2026-03-12
**File**: `_comms_hub/packages/purebrain-portal/portal-server/portal-pb-styled.html`
**Type**: Bug fix — UX

---

## Root Cause

The `smartScroll` function had a dual-condition guard:

```js
if (_userWasNearBottom || isNearBottom(el, 300)) {
```

The secondary `isNearBottom(el, 300)` call ran inside `requestAnimationFrame`, **after** a new message was appended to the DOM. When a streaming message grows `scrollHeight`, the user's current `scrollTop` can fall within 300px of the new bottom purely because content grew below them — not because they scrolled there. This triggered the forced scroll even when `_userWasNearBottom` was `false`.

## Fix Applied

Removed the secondary `isNearBottom` check from `smartScroll`. The function now relies solely on the scroll-event-tracked `_userWasNearBottom` flag:

```js
if (_userWasNearBottom) {
  el.scrollTop = el.scrollHeight;
}
```

`_userWasNearBottom` is updated on every `scroll` event, giving accurate intent tracking.

## Also Fixed

- Two async `image.load` event handlers that called `chatMessages.scrollTop = chatMessages.scrollHeight` directly (no guard). Changed to `smartScroll(chatMessages)`.
  - Line ~5621: user image in `addMessage`
  - Line ~6965: image in `addFileImageMessage`

## Scroll Behavior Summary (post-fix)

| Situation | Behavior |
|-----------|----------|
| User is at/near bottom, Aether responds | Auto-scroll to show new message |
| User has scrolled up to read history | Message appends silently, no scroll |
| User sends their own message | Unconditional scroll to bottom (correct) |
| User switches to chat panel | Unconditional scroll to bottom (correct) |
| User clicks scroll-to-bottom arrow | Unconditional scroll to bottom (correct) |
| Initial chat history load | Unconditional scroll to bottom (correct) |

## Portal Core UX Rules Reference

This fix implements Portal Core UX Rules #4 and #5 (locked 2026-03-08):
- Rule 4: Only auto-scroll when user is at/near bottom
- Rule 5: Scroll-to-bottom arrow appears when user has scrolled up
