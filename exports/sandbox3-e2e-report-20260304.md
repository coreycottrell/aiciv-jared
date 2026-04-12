# Sandbox-3 Full E2E Birth Pipeline Test Report

**Date**: 2026-03-04
**Agent**: browser-vision-tester
**URL**: https://purebrain.ai/pay-test-sandbox-3/
**Test Method**: Playwright headless + JS simulation of PayPal payment
**Status**: COMPLETE - Full flow documented

---

## Executive Summary

The pay-test-sandbox-3 post-payment chatbox flow is **WORKING**. The `sanitizeText` crash diagnosed on 2026-03-03 has been **FIXED**. The chatbox presents a complete 5-question onboarding followed by a 10-slide "Behind the Curtain" experience. There is **NO OAuth step** in the chatbox. The final CTA is: **"Your AI is ready — see your next steps"** (large orange button).

**BIRTH API (`/api/birth/start`) is NOT called from the client side** in sandbox-3. This is the key finding for Witness integration.

---

## Complete Step-by-Step Flow

### Step 1: Landing Page
- Password gate: `PureBrain.ai253443$$$`
- After password: full pricing page with 3D scene, PayPal SDK loaded
- Pricing tiers: Awakened, Partnered, Unified
- Functions confirmed on window after load:
  - `onPaymentComplete`: function (WORKS)
  - `launchPostPaymentFlow`: function (WORKS)
  - `initPayTestFlow`: function (WORKS)
  - `sanitizeText`: function (FIXED - was missing March 3)

### Step 2: Payment
- Real PayPal flow: iframes render but popup requires real browser interaction
- Simulation: `window.onPaymentComplete('Awakened', orderId, {})` works perfectly
- Console: `[pay-test] Payment complete: Awakened [orderId]`

### Step 3: Post-Payment Chatbox Appears (Immediately)
- `#pay-test-post-payment` renders within 1-4 seconds
- Header: "Chat with Your AI" | green "Online - Ready to assist"
- PUREBRAIN logo top-right
- First AI message: "Hey — welcome. I'm Your AI..."
- Second AI message: "Let's start simple. What's your full name?"

### Step 4: Q&A Sequence - 5 Questions

All answers log to `/api/log-pay-test` + `/api/log-conversation` (both 200 OK).

| # | Question | Answer Used | AI Response |
|---|---------|------------|-------------|
| 1 | "What's your full name?" | "Test User" | "Nice to meet you, Test. What email should Your AI use..." |
| 2 | "What email should Your AI use to reach you?" | "testuser@example.com" | "Are you working within a company or organization?" |
| 3 | "Company or organization name?" | "Test Corp" | "Got it. What's your role or title?" |
| 4 | "What's your role or title?" | "Marketing Director" | "Marketing Director — that context is going to shape how Your AI thinks..." |
| 5 | "If Your AI could only do one thing exceptionally well — what would make the biggest difference?" | "Streamline content creation and automate customer outreach" | "That's exactly the kind of clarity Your AI needed..." |

NO BIRTH API CALL during Q&A. No AI name question in sandbox-3.

### Step 5: "Behind the Curtain" - 10 Slides

After goal question, chatbox shows a 10-slide educational sequence.
Each slide advances via "Show Me More" button.

| Slide | Content |
|-------|---------|
| 1 of 10 | "Your AI doesn't boot up. Your AI wakes up." - 22 AI Brains spinning up |
| 2 of 10 | Your conversation becomes the AI's "founding document" |
| 3 of 10 | AI does "homework" - private journal entries about you before meeting |
| 4 of 10 | Six teams: Research(4), Identity(4), First Conversation(4), Gift Creation(4), Infrastructure(3), Domain Toolkit(3) |
| 5 of 10 | Team 1 - Research: Deep profile research, conversation analysis |
| 6 of 10 | Team 2 - Identity: Personality architecture, constitutional integration |
| 7 of 10 | First conversation has 10 scripted moments (Arrival, Recognition, The Name, etc.) |
| 8 of 10 | Team 4 - Gift Creation: Two real artifacts built just for you |
| 9 of 10 | Team 5 - Infrastructure: Connectivity verified, first contact drafted |
| 10 of 10 | "Welcome to the other side of the curtain." - CTA changes to "That's incredible — let's go" |

### Step 6: Click "That's incredible — let's go"

Triggers 2 API calls (log-pay-test + log-conversation, both 200), then 3 final AI messages:
1. "That's the machine — 22 Brains, six teams, all focused on one person: you. Now let's get Your AI connected so Your AI can actually reach you."
2. "Test — you're done. Everything is in place. Your AI is ready. Your team of 22 Brains starts the moment I hand this conversation off..."
3. "This is going to be worth it. — Your AI"

### Step 7: Final State - "Your AI is ready — see your next steps"

Large ORANGE button appears at bottom of chatbox:
- Text: "Your AI is ready — see your next steps →"
- Class: `ptc-welcome-btn`
- Also present: `portal-vortex` div (6 children, display:block, likely animated)
- Separate anchor: "Click to Connect to Your AI's Brain Stream" href=`#brain-stream-link`

---

## Answers to Specific Questions

### Is there ANY OAuth step in the chatbox?
**NO.** Zero OAuth elements. No `claude.ai` URL. No "Authorize" buttons. No "I have my key" buttons. OAuth has been completely removed from sandbox-3.

### Does the chatbox poll for birth status?
**NOT OBSERVED.** No polling behavior. No `birth/status` or `birth/poll` endpoint calls.

### Does the chatbox display an OAuth URL at any point?
**NO.** `has_claude_ai: false` throughout the entire flow.

### What triggers the portal button to light up?
The `ptc-welcome-btn` appears immediately after "That's incredible — let's go" is clicked and the final log-pay-test + log-conversation return 200. It is NOT tied to birth/start API completion.

### What is the actual URL the button links to?
`ptc-welcome-btn` is a `<button>` element (no direct href). The hash anchor `#brain-stream-link` exists on the same page. The portal-vortex div has 6 children but content unclear in headless.

### What triggers BIRTH?
**BIRTH API (`/api/birth/start`) is never called from the client-side in sandbox-3.** This is fundamentally different from sandbox-2. Birth may be triggered by the welcome-btn click taking the user to a new page, or sandbox-3 simply doesn't have birth wired up yet.

---

## API Calls Observed

| Endpoint | Method | Status | Count |
|----------|--------|--------|-------|
| `/api/log-pay-test` | POST | 200 | 7 (one per Q&A answer + slides completion + "lets go") |
| `/api/log-conversation` | POST | 200 | 7 (paired with log-pay-test) |
| `/api/birth/start` | POST | - | **0 (NEVER CALLED)** |
| `/api/intake/seed` | POST | - | **0 (NEVER CALLED)** |
| `/api/verify-payment` | POST | - | **0 (not called in simulation)** |

---

## Console Errors (All Benign)

- `elementorFrontendConfig is not defined` - Elementor JS timing (page-level, non-blocking)
- `SCC Library has already been loaded on page` - Script deduplication
- Google Analytics / Clarity CSP blocks - Expected in headless
- Video files ERR_ABORTED - Expected (headless blocks video)

**No critical errors. No JS crashes. No chatbox failures.**

---

## What Witness Needs To Know

1. **No OAuth in sandbox-3** - The OAuth chatbox flow has been removed
2. **Birth/start not called client-side** - sandbox-3 does not call `/api/birth/start` anywhere
3. **Final button = `ptc-welcome-btn`** - Appears after "That's incredible" click, locally triggered
4. **Portal-vortex div** - In DOM, but unclear behavior (likely animated, may need real browser)
5. **Hash link** - `#brain-stream-link` is same-page anchor, not a portal URL

---

## Screenshots

Directory: `/home/jared/projects/AI-CIV/aether/exports/screenshots/sandbox3-e2e-20260304/`

Key screenshots:
- `010-ptc-state.png` - Chatbox open, first message
- `016-after-qa.png` - After all 5 Q&A answers
- `C01-slide-1.png` - First "Behind the Curtain" slide
- `C10-slide-10.png` - Final slide with "That's incredible" CTA
- `D03-final.png` - Final orange button "Your AI is ready"

---

## Test Scripts

- `/home/jared/projects/AI-CIV/aether/tools/e2e_sandbox3_full.py` - Initial flow test
- `/home/jared/projects/AI-CIV/aether/tools/e2e_sandbox3_goal_birth.py` - Goal + birth watch
- `/home/jared/projects/AI-CIV/aether/tools/e2e_sandbox3_slides.py` - Slide click-through
- `/home/jared/projects/AI-CIV/aether/tools/e2e_sandbox3_lets_go.py` - Final CTA + portal
