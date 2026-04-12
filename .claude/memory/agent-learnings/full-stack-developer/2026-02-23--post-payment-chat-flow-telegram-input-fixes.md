# Memory: Post-Payment Chat Flow - Telegram Messaging + Input Visibility Fixes

**Date**: 2026-02-23
**Type**: teaching + operational
**Agent**: full-stack-developer
**Pages fixed**: 688 (pay-test-sandbox-2), 689 (pay-test-2)

## Summary

Two issues fixed in the post-payment chat flow on both pay-test pages.

---

## Issue 1: Telegram Positioned as Primary Channel (Fixed)

### What Was Wrong
In `runTelegramSetup()`, the "Connected" confirmation message said:
```
`Your Telegram bridge is live. ${aiName} will reach you there when your AI is ready.`
```
This implied Telegram was the primary way to interact with the AI.

### New Messaging Rule
**Brain Stream portal (app.purebrain.ai) = PRIMARY**
**Telegram = BACKUP only**

### Fix Applied
Changed to:
```
`Your Telegram bridge is live. Other than ${aiName}'s Brain Stream portal (app.purebrain.ai), you can also communicate with ${aiName} via Telegram as a backup.`
```

### Note on Other Telegram References
The intro message in `runTelegramSetup()` (line 9849) already correctly said:
> "Outside of [aiName]'s main portal (Their Brain Stream), which will be set up by the end of this chat, you can also communicate with [aiName] on Telegram."
This was already correct - Brain Stream as primary, Telegram as secondary. Only the "Connected" confirmation needed fixing.

---

## Issue 2: Input Box Disappears While AI Thinks (Fixed)

### Root Cause
When user submits text in `promptText()`, the `submit()` function did:
```javascript
inputRow.style.display = 'none';  // PROBLEM: hides input immediately
textarea.value = '';
resolve(val);
```
This made the entire input area vanish while the AI was "thinking" (typing delay + sleep).
Same pattern existed in the `learnMoreLoop` inline submit handler.

### Fix Applied (4 changes)

**1. `promptText()` function START** - re-enable in case disabled:
```javascript
textarea.disabled = false;
sendBtn.disabled = false;
textarea.style.opacity = '';
```

**2. `promptText()` submit handler** - disable instead of hiding:
```javascript
// Keep input row visible but disable it while AI processes
textarea.disabled = true;
sendBtn.disabled = true;
textarea.style.opacity = '0.5';
// removed: inputRow.style.display = 'none';
```

**3. `learnMoreLoop` input show** - re-enable at each question:
```javascript
textarea.disabled = false;
sendBtn.disabled = false;
textarea.style.opacity = '';
```

**4. `learnMoreLoop` submit handler** - disable instead of hiding:
```javascript
// Keep input row visible but disable while AI processes
textarea.disabled = true;
sendBtn.disabled = true;
textarea.style.opacity = '0.5';
// removed: inputRow.style.display = 'none';
```

### UX Result
- Input box stays visible throughout the entire chat flow
- While AI is thinking: textarea and send button are grayed out (opacity 0.5) and non-interactive
- When AI asks next question: textarea and button re-enable automatically
- Users always know where to type - never confused by disappearing input

---

## Deployment Details

- Page 688 (_elementor_data): 448,954 → 449,655 chars
- Page 689 (_elementor_data): 446,539 → 447,240 chars
- Widget ID: `292c72a` (same on both pages)
- Cache cleared: `DELETE /wp-json/elementor/v1/cache` (status 200 on both)
- All 6 verification checks passed on both pages

## Lessons

1. **Both pages (688 + 689) must always be updated together** - they share the same chat flow code but are separate WordPress pages.

2. **The input row pattern**: Initial state is `display: none`. `promptText()` shows it, submit hides it. The fix changes "hide on submit" to "disable on submit" and "enable on next promptText call".

3. **Brain Stream = app.purebrain.ai** is the PRIMARY portal - any language implying Telegram or other channels are primary should be corrected.

4. **Intro message was already correct** - only the "Connected" confirmation message had the wrong framing.
