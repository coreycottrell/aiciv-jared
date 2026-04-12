# Memory: Portal Mobile Portrait Overflow Audit

**Date**: 2026-03-08
**Agent**: browser-vision-tester
**Type**: technique + gotcha + pattern
**Tags**: portal, mobile, overflow, msg-row, msg-bubble, flex, CSS, app.purebrain.ai

---

## Summary

Full mobile portrait overflow audit of https://app.purebrain.ai at 375x812.

**Result**: 3 overflowing .msg-bubble elements found. Root cause identified. Two separate bugs.

---

## Root Cause #1: .msg-row has no max-width constraint (CRITICAL)

### The Bug

`.msg-row` is a flex row container with `max-width: none`. It sits INSIDE `.msg.assistant` which has `max-width: 90%` = 323px. But `.msg-row` stretches to fill its own content (530px+) because it has NO width constraint.

The `.msg-bubble` inside `.msg-row` is `flex: 1 1 0%` — it grows to fill `.msg-row`. Since `.msg-row` has no max-width, the bubble grows without bound.

### Container chain at 375px viewport:

```
#chat-messages (359px wide, overflow-x: hidden)
  .msg.assistant (max-width: 90% = 323px, overflow-x: visible)
    .msg-row (max-width: none, offsetWidth: 530px!!!)  ← THIS IS THE BUG
      .msg-avatar-hex (28px, flex: 0 0 auto)
      .msg-bubble (flex: 1 1 0%, maxWidth: 100% = 494px!!)
```

### Why overflow-x:hidden on #chat-messages doesn't fix it

The bubbles overflow visually even though #chat-messages clips scroll. The children's
getBoundingClientRect().right = 538 (163px past viewport). The VISUAL render clips but
the CSS layout engine positions the bubble outside the viewport box.

### Fix

Add to `.msg-row`:
```css
.msg-row {
    max-width: 100%;
    overflow: hidden;
    box-sizing: border-box;
}
```

OR constrain the bubble directly:
```css
.msg-bubble {
    max-width: calc(100% - 36px);  /* subtract avatar width + gap */
}
```

---

## Root Cause #2: .welcome-hero canvas is 640px wide on 375px screen

### The Bug

`.welcome-hero` has `width: 640px` with no responsive override. The canvas inside it
is also 600px wide. This causes `#panel-chat.scrollWidth = 508` even though `offsetWidth = 375`.

### Fix

```css
.welcome-hero {
    width: 100% !important;
    max-width: 100vw !important;
}
.welcome-hero__canvas {
    width: 100% !important;
    max-width: 100% !important;
}
```

---

## Root Cause #3: .header-right is 541px on 375px screen

`.header-right` contains ctx-gauge + conn-badge + resume-btn + restart-btn + settings-btn + share-btn + logout-btn.
Total computed: 541px. On mobile the `.ctx-gauge` is hidden via CSS but remaining buttons still total > 375px.

### Fix

On mobile, further hide/collapse elements in `.header-right`. Or use `overflow: hidden` on the header.

---

## Specific Overflowing Messages (by content)

1. Bubble #54: Message containing a regex `/^\[replying to...` — `.msg-row` = 530px wide
2. Bubble #108: "Mobile view (375x812 iPhone): Vercel homepage..." — `.msg-row` = 507px wide
3. Bubble #109: "Mobile view (375x812 iPhone): WordPress purebrain.ai..." — `.msg-row` = 544px wide

All 3 are `.msg.assistant` class bubbles. User bubbles are NOT overflowing (they use `align-self: flex-end` which constrains them differently).

---

## Key Metrics

- Viewport: 375px
- #chat-messages offsetWidth: 359px (correct, clipped)
- #chat-messages scrollWidth: 544px (WRONG — children overflow)
- document.body.scrollWidth: 512px (WRONG — horizontal scroll exists)
- Overflowing .msg elements: 0 (max-width 90% works)
- Overflowing .msg-bubble elements: 3
- Overflowing .msg-row elements: 3

---

## Existing Mobile Media Query (max-width: 600px)

The mobile CSS DOES have rules for `.msg`, `.msg-bubble`, `.msg-row`-related fixes.
But `.msg-row` itself has NO max-width rule in the media query. That's the gap.

The existing fix for `.msg { max-width: 90% }` constrains the flex column parent,
but since `.msg-row` is INSIDE `.msg` and has `max-width: none`, it escapes the parent constraint.

---

## Screenshots

Dir: `/home/jared/projects/AI-CIV/aether/exports/screenshots/portal-mobile-overflow-20260308/`
- 001-login-page.png — Login page at 375x812
- 004-chat-loaded.png — Chat loaded, overflow visible
- 006-chat-top.png — Scrolled to top
- 007-chat-middle.png — Middle of conversation
- 008-chat-bottom.png — Bottom of conversation (most recent)
