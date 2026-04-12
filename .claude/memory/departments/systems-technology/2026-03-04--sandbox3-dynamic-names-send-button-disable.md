# Sandbox-3 (Page 1232) — Dynamic AI Names + Send Button Disable

**Date**: 2026-03-04
**Page**: purebrain.ai page 1232 (pay-test-sandbox-3)
**Agent**: dept-systems-technology
**Type**: bugfix
**Tags**: sandbox3, dynamic-name, aiName, safeAiName, send-button, showBrainStreamButton, page-1232

---

## Context

Jared sent annotated screenshots showing hardcoded "Your AI" text in multiple places on the chatbox page. All user-visible text must use the dynamic AI name from `payTestData.aiName`.

---

## Fixes Applied

### Fix 1: Welcome Card "Now" Row — Name First
- **OLD**: `Your AI partner, ${aiName}, is being set up.`
- **NEW**: `${aiName}, your AI partner, is being set up.`
- Puts the actual name first so it reads naturally ("Keen, your AI partner...")

### Fix 2: Welcome Card "Next 2 Mins" Row — Name First
- **OLD**: `Your Pure Brain, ${aiName}, is being shaped by your answers.`
- **NEW**: `${aiName}'s Pure Brain is being shaped by your answers.`
- More natural phrasing, name leads

### Fix 3: Brain Stream Label — Remove "Your AI"
- **OLD**: `<div id="pb-brain-stream-label">Your AI is ready</div>`
- **NEW**: `<div id="pb-brain-stream-label">Your Brain Stream is ready</div>`
- Static fallback that doesn't say "Your AI"
- The `showBrainStreamButton` function NOW updates this label dynamically (see Fix 5)

### Fix 4: pb-bs-ai-name Span Default — Clear Hardcoded Text
- **OLD**: `>Click to Connect to <span id="pb-bs-ai-name">Your AI</span>&#8217;s Brain Stream</a>`
- **NEW**: `>Click to Connect to <span id="pb-bs-ai-name"></span>&#8217;s Brain Stream</a>`
- The `showBrainStreamButton` function already sets `nameSpan.textContent = aiName` — so the default text just needed to be cleared.
- If JS fires before the name is available, it shows "Click to Connect to 's Brain Stream" which is acceptable vs "Your AI"

### Fix 5: showBrainStreamButton — Disable Send + Update Label
Added to `showBrainStreamButton()` before the reveal animation:

```javascript
// FIX: Also disable chat input when Brain Stream button activates
var chatInputRow = document.getElementById('ptc-input-row');
var chatTextarea = document.getElementById('ptc-input');
var chatSendBtn = document.querySelector('.ptc-send-btn');
if (chatTextarea) {
  chatTextarea.disabled = true;
  chatTextarea.placeholder = 'Session complete — enter your Brain Stream above';
}
if (chatSendBtn) {
  chatSendBtn.disabled = true;
  chatSendBtn.style.opacity = '0.35';
  chatSendBtn.style.pointerEvents = 'none';
  chatSendBtn.style.cursor = 'not-allowed';
}
if (chatInputRow) {
  chatInputRow.style.opacity = '0.4';
  chatInputRow.style.pointerEvents = 'none';
}

// Also update the brain stream label with the actual AI name
var labelEl = document.getElementById('pb-brain-stream-label');
var resolvedName = (aiName && aiName.trim()) ? aiName : (window.payTestData && window.payTestData.aiName ? window.payTestData.aiName : null);
if (labelEl && resolvedName) {
  labelEl.textContent = resolvedName + '\u2019s Brain Stream is ready';
}
```

---

## What Was NOT Changed (Intentional Fallbacks)

These three "Your AI" occurrences remain as defensive fallbacks:
1. `Chat with ${payTestData.aiName || 'Your AI'}` — header (correct, uses dynamic name when set)
2. `'Message ' + (payTestData.aiName || 'your AI') + '…'` — placeholder (correct)
3. `sanitizeText(aiName || 'Your AI')` — in portal button and runPortalButtonWatcher (correct fallback)

These are NOT bugs — they correctly prefer the dynamic name and only fall back to "Your AI" if aiName is truly unavailable.

---

## Deployment

- **Deployed**: 2026-03-04T14:09:36 UTC
- **Method**: `content.raw` update via WP REST API
- **Elementor cache cleared**: Yes (200 OK)
- **Verification**: 7/7 checks PASS on fresh fetch

---

## Key Pattern: Two Separate "Send Button Disable" Paths

Page 1232 has TWO flows that present a "enter portal" button:
1. **Flow A** — `runLearnMoreLoop()` shows `ptc-portal-placeholder` after Q&A
   - Send button disable: handled at end of `runLearnMoreLoop` (was fixed previously)
2. **Flow B** — `showBrainStreamButton()` is called externally by Witness
   - Send button disable: NOW handled in `showBrainStreamButton` (this fix)

Both paths now correctly grey out the input when the portal button appears.
