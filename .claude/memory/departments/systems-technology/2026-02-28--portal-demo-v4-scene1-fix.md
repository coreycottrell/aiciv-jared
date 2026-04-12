# Portal Demo v4 — Scene 1 Awakening Fix

**Date**: 2026-02-28
**Type**: pattern + gotcha
**Agent**: dept-systems-technology

---

## What Was Fixed

The v3 recording script had a broken Scene 1 that couldn't interact with the purebrain.ai awakening chatbox. v4 fixes this completely.

## Verified Selector Map (purebrain.ai as of 2026-02-28)

| Purpose | Selector |
|---------|----------|
| Hero CTA (scrolls to chatbox) | `button.btn--primary` — "Awaken Your PURE BRAIN" |
| Begin Awakening button | `.chat-initial__btn` — in chatbox section |
| Chat text input | `#userInput` — hidden until Begin Awakening clicked |
| Submit button | `#submitBtn` — disabled while AI is streaming |
| Discover CTA | `#seeWhatBtn` / `.chat-cta__btn` — appears after ~12 conversation turns |

## Conversation Flow

The chatbox goes through ~12 turns before `#seeWhatBtn` appears:
1. AI sends 4 opening messages in sequence (philosophical awakening)
2. Asks "What should I call you?" (user's name)
3. Multiple turns of philosophical conversation about AI and the user's work
4. Eventually asks to be named (user says "Aria")
5. More conversation rounds
6. Eventually: "Would you like me to show you what I can really do?"
7. `#seeWhatBtn` appears alongside this question

The conversation is non-deterministic — the AI takes different paths. Having 15 backup conversation turns is recommended.

## Critical Bugs Found and Fixed

### Bug 1: False positive `offsetParent !== null` check
```js
// BROKEN: when element doesn't exist, ?. returns undefined
// undefined !== null evaluates to TRUE in JS
document.getElementById('seeWhatBtn')?.offsetParent !== null

// FIXED: explicit null check first
const el = document.getElementById('seeWhatBtn');
if (!el) return false;
```

### Bug 2: `wait_for(state='visible')` timeout on visible element
Playwright's `.wait_for(state='visible')` was timing out even when the element was genuinely visible. Root cause unclear (possibly sync API in video-recording context).
**Fix**: Use `.fill()` directly without `.wait_for()`.

### Bug 3: Background thread calling Playwright sync API
The `wait_for_response()` threading pattern from v3 Scene 2 generates greenlet errors. These are non-fatal warnings but should be noted. They occur because Playwright sync API cannot be called from background threads.

### Bug 4: `wait_for_ai_response` returning too early
The AI sends multiple messages in succession (especially the 4-message opening sequence). Polling only for `submitBtn.disabled == False` could return between two AI messages.
**Fix**: Wait for both disabled=False AND message count stable for 2.5 seconds.

## Input Method: fill() is Correct

Using `page.locator("#userInput").fill(text)` then `#submitBtn.click()` is the correct approach for the chatbox. JS `inp.value = text` + dispatching `input` events bypasses the chatbox's internal state machine and causes the AI to produce garbled/off-topic responses.

## Script Location

`/home/jared/projects/AI-CIV/aether/tools/video-pipeline/record_portal_demo_v4.py`

## R2 Output

Same R2 key as v3 (overwrites):
- Key: `videos/demo/portal-demo-v3/portal-demo-v3.mp4`
- Public URL: `https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/videos/demo/portal-demo-v3/portal-demo-v3.mp4`

## Video Stats

- Duration: 760s (12.7 minutes)
- WebM: 71.8 MB
- MP4: 36.5 MB
- All 3 scenes: Scene 1 (awakening) + Scene 2 (portal chat) + Scene 3 (features)
