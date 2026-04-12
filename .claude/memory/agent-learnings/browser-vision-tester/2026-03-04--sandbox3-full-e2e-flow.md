# Sandbox-3 Full E2E Flow - Complete Documentation

**Date**: 2026-03-04
**Agent**: browser-vision-tester
**Type**: technique + pattern + synthesis
**Tags**: browser-vision, visual-testing, purebrain, paytest, sandbox3, chatbox, e2e, birth-pipeline, slides

---

## Context

Ran comprehensive E2E test of `https://purebrain.ai/pay-test-sandbox-3/` birth pipeline. Used JS simulation of PayPal payment (`window.onPaymentComplete('Awakened', orderId, {})`).

---

## Key Findings

### 1. sanitizeText Bug FIXED
Previous (2026-03-03) crash `sanitizeText is not defined` is resolved. `sanitizeText` is now `function` on window.

### 2. NO OAuth in Chatbox (CONFIRMED)
Zero OAuth elements in sandbox-3. No `claude.ai` URL. No "Authorize" buttons. No "I have my key" buttons. OAuth flow was removed.

### 3. Complete Q&A Sequence (5 Questions - No AI Name)
- Name -> Email -> Company -> Role -> Goal (One Thing)
- Each answer triggers `log-pay-test` + `log-conversation` (both 200)
- AI refers to itself as "Your AI" throughout (not personalized name)
- Sandbox-3 does NOT ask for AI name (difference from sandbox-2)

### 4. NEW: 10-Slide "Behind the Curtain" Onboarding
After goal answer, a 10-slide educational sequence appears. Each slide advances with "Show Me More" button.
- Slides describe: 22 AI Brains, 6 teams, research process, gift creation
- Slide 10 changes button to "That's incredible — let's go"

### 5. BIRTH API NOT Called Client-Side
`/api/birth/start` is never called in sandbox-3. This is fundamentally different from sandbox-2.
Birth may fire server-side, or sandbox-3 is pre-birth-wiring.

### 6. Final CTA = "Your AI is ready — see your next steps"
- Large orange button `ptc-welcome-btn`
- Appears immediately after "That's incredible" click
- NOT tied to birth/start API completion
- `portal-vortex` div is in DOM with 6 children
- Hash anchor: `#brain-stream-link` (same-page)

---

## Selector Patterns Confirmed for Sandbox-3

- Chatbox wrapper: `#pay-test-post-payment` (position:fixed, z-index:999999)
- PTC input: `#ptc-input` (or `textarea.ptc-input`)
- Send button: `.ptc-send-btn` or `#ptc-send-btn`
- Input row: `#ptc-input-row` (starts display:none, becomes flex after payment)
- AI messages: `.ptc-msg--ai`
- User messages: `.ptc-msg--user`
- Slide button: `button` with text "Show Me More" -> "That's incredible"
- Final CTA: button with class `ptc-welcome-btn`, text "Your AI is ready — see your next steps"
- Portal div: `.portal-vortex`

---

## Flow Timing (From Tests)

| Stage | Time from script start |
|-------|----------------------|
| Password accepted | ~14s |
| Payment simulated | ~15s |
| PTC input active | ~19s |
| All 5 Q&A complete | ~85s |
| All 10 slides clicked | ~140s |
| "That's incredible" clicked | ~145s |
| "Your AI is ready" button appears | ~146s |

---

## API Pattern

All client-side API calls are to `https://api.purebrain.ai/api/`:
- `log-pay-test` (POST) - fires on each Q&A answer + slide progression (200 OK)
- `log-conversation` (POST) - fires paired with log-pay-test (200 OK)
- `birth/start` - NEVER CALLED in sandbox-3
- `intake/seed` - NEVER CALLED in sandbox-3

---

## Scripts Written

- `/home/jared/projects/AI-CIV/aether/tools/e2e_sandbox3_full.py`
- `/home/jared/projects/AI-CIV/aether/tools/e2e_sandbox3_goal_birth.py`
- `/home/jared/projects/AI-CIV/aether/tools/e2e_sandbox3_slides.py`
- `/home/jared/projects/AI-CIV/aether/tools/e2e_sandbox3_lets_go.py`

## Report Written

`/home/jared/projects/AI-CIV/aether/exports/sandbox3-e2e-report-20260304.md`
