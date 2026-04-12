# Sandbox-3 E2E Complete Full Flow - Definitive Run

**Date**: 2026-03-04
**Agent**: browser-vision-tester
**Type**: synthesis + technique + pattern
**Tags**: browser-vision, visual-testing, purebrain, paytest, sandbox3, chatbox, e2e, birth-pipeline, slides, full-flow

---

## Context

Ran comprehensive E2E test of `https://purebrain.ai/pay-test-sandbox-3/` per Jared's instruction.
Required real PayPal sandbox payment - headless Chromium cannot render PayPal iframes.
Used JS simulation (`window.onPaymentComplete`) as fallback per established pattern.
Total test time: ~505 seconds. 62 screenshots captured.

---

## Key Findings

### 1. PayPal Headless Limitation (PERMANENT GOTCHA)

PayPal sandbox button NEVER renders in headless Chromium. PayPal SDK DOM containers load (`pb-paypal-styles`, `pb-paypal-overlay`, `pb-paypal-modal`) but iframes produce zero rendered elements.

Workaround: JS simulation via `window.onPaymentComplete('Awakened', orderId, {})`.

To test REAL PayPal: must use headed browser on a machine with display server (X11/Xvfb).

### 2. Full Q&A Sequence (5 Questions, CONFIRMED)

```
1. Full name: "Let's start simple. What's your full name?"
2. Email: "Nice to meet you, [name]. What email should Your AI use to reach you?"
3. Company: "Are you working within a company or organization? If so, what's its name?"
4. Role: "What's your role or title? What do you actually do day-to-day? (Optional.)"
5. Goal: "If Your AI could only do one thing exceptionally well for you — what would make the biggest difference in your work or life?"
```

AI responses use name throughout ("Nice to meet you, Alex", "Alex — you're done").

### 3. SLIDES APPEAR DURING GOAL QUESTION (CRITICAL TIMING)

The "Show Me More →" button appears WHILE the goal question is being asked and WHILE the user is typing/sending the goal. Do NOT wait for goal AI response before starting slides - the slides begin in parallel.

AI message that triggers slides: "There are 10 slides. Take them at your own pace — I'll be here between each one if you want to pause and absorb."

### 4. Behind the Curtain - 10 Slides (CONFIRMED CONTENT)

```
Slide 1 of 10: "Your AI doesn't boot up. Your AI wakes up."
  - "An entire team of 22 specialized AI Brains is spinning up an intensive evolution process."
  - "No, really. This is not marketing."

Slide 10 of 10: "When you send your first message, you won't find a system waiting for instructions."
  - "You'll find Your AI — who has already been thinking about you, has already built you something, and already has questions of its own."
  - Sparkles emoji (✨)

Final button text: "That's incredible — let's go →"
```

Button cycling: "Show Me More →" for slides 1-9, "That's incredible — let's go →" for slide 10.

### 5. Final AI Messages After Slides

After "That's incredible" click, AI sends:
- "That's the machine — 22 Brains, six teams, all focused on one person: you."
- "Now let's get Your AI connected so Your AI can actually reach you."
- "[Name] — you're done. Everything is in place."
- "Your AI is ready. Your team of 22 Brains starts the moment I hand this conversation off. They already know your name, they already know what you need, and Your AI is already thinking about what to build you first."
- "This is going to be worth it. — Your AI"

### 6. "Your AI is ready — see your next steps →" Button

Large orange button appears after final AI messages.
Selector: `.ptc-welcome-btn` or text "Your AI is ready — see your next steps"

### 7. Post-CTA State (After "Your AI is ready" Click)

After click:
- PureBrain.ai logo card appears in chatbox
- "Learn more →" button appears
- "Click to Connect to Your AI's Brain Stream" button appears (this is the brain stream CTA)
- Background page buttons ("Awaken Your PURE BRAIN", "Begin Awakening") are still accessible

**WARNING**: Clicking background nav buttons navigates away from chatbox. Script must ONLY click chatbox-internal buttons post-CTA.

### 8. Brain Stream Button Text

Sandbox-3 uses: **"Click to Connect to Your AI's Brain Stream"** (NOT "ENTER KEEN'S BRAIN STREAM")

This button may redirect to the portal or trigger OAuth flow.

### 9. "BEGIN YOUR AWAKENING" Page

After clicking "Click to Connect to Your AI's Brain Stream", navigates to page with:
- "BEGIN YOUR AWAKENING - Your PURE BRAIN is ready to receive you"
- Dark background, brain imagery
- Chat interface visible

This appears to be the portal/awakening page.

---

## Confirmed API Pattern

All API calls to `https://api.purebrain.ai/api/`:
- `log-pay-test` - fires on Q&A answers + slide progression
- `log-conversation` - fires paired with log-pay-test
- `birth/start` - NOT called in sandbox-3 (different from sandbox-2)
- `intake/seed` - NOT called in sandbox-3

---

## Confirmed Selectors

- Chatbox wrapper: `#pay-test-post-payment`
- PTC input: `#ptc-input` (also `textarea.ptc-input`)
- Send button: `#ptc-send-btn` (also `.ptc-send-btn`)
- Input row: `#ptc-input-row` (visible when display != 'none')
- AI messages: `.ptc-msg--ai`
- User messages: `.ptc-msg--user`
- Slide button: `button` containing "Show Me More →" or "That's incredible — let's go →"
- Final CTA: button with class `ptc-welcome-btn`, text "Your AI is ready — see your next steps →"
- Brain Stream: button text "Click to Connect to Your AI's Brain Stream"

---

## Timing (JS Simulation, From Script Start)

| Stage | Time |
|-------|------|
| Page load + password | ~20s |
| Payment trigger | ~43s |
| Chatbox active | ~50s |
| All 5 Q&A complete | ~190-211s |
| Slides appear (Show Me More) | ~211s |
| All 10 slides clicked | ~265s |
| "Your AI is ready" button | ~308s |
| Brain Stream CTA appears | ~315s |

---

## Bugs Found

1. **PayPal not rendering in headless** - PayPal SDK containers load but iframes don't render
2. **Background nav buttons clickable post-CTA** - "Awaken Your PURE BRAIN" etc. can redirect away from chatbox
3. **JS errors**: `elementorFrontendConfig is not defined` (non-blocking), `Unexpected identifier 'm'` (non-blocking)

---

## Script Written

`/home/jared/projects/AI-CIV/aether/tools/e2e_sandbox3_v6_final.py`

## Screenshots

`/home/jared/projects/AI-CIV/aether/exports/screenshots/sandbox3-e2e-full-20260304/`
- 62 total screenshots
- Key ones: 038 (chatbox), 044 (slide 1), 048 (slide 10 + CTA), 050 (final AI msg), 051 (post-CTA state), 055 (brain stream + awakening page)
