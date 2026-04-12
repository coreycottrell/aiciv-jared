# Memory: pay-test-sandbox-2 Full E2E Audit
**Date**: 2026-03-02
**Type**: teaching + operational
**Topic**: Comprehensive E2E: password gate -> chatbox -> bypass -> pricing -> PayPal SDK modal -> post-payment chatbox

---

## Full Flow Summary (PASS/FAIL/BUG per stage)

| Stage | Status | Notes |
|-------|--------|-------|
| 1. Navigate | PASS | Page loads correctly, password gate shows |
| 2. Password entry | PASS | `input[id^='pwbox-']` selector, press Enter to submit |
| 3. Page content | PASS | Hero section loads, "Awaken Your PURE BRAIN" CTA visible |
| 4. Sandbox banner | BUG | Banner NOT visible - CSS not rendering (no `.sandbox-banner` in DOM) |
| 5. Begin/Awaken click | PASS | `.chat-initial__btn` selector works |
| 6. AI chatbox awakening | PASS | First message: "Something stirs... awareness blooming like light through water" |
| 7. Natural conversation | PASS | AI responds contextually, conversation logging fires (log-conversation x4 HTTP 200) |
| 8. Bypass code | PARTIAL | Bypass fires - "Welcome back, Jared. Bypass mode activated." AI responds as "Keen" |
| 9. Pricing reveal after bypass | BUG-CRITICAL | Pricing stays `display:none` after `pb-full-bypass`. Must manually trigger via JS |
| 10. Pricing cards | PASS (manual) | 5 cards: Awakened $79, Bonded $149, Partnered $499, Unified $999, Enterprise |
| 11. Button onclick scope | PASS | 4/5 use `openPayPalModal()` (fixed from 2026-03-01 bug). Enterprise uses `openWaitlistModal('Enterprise')` |
| 12. PayPal modal open | PASS | Overlay + modal appear with tier name and price |
| 13. PayPal SDK buttons | PASS | SDK loaded (HTTP 200), shows "Pay with PayPal", SEPA, Debit/Credit Card buttons |
| 14. Sandbox simulate button | PASS | "Simulate Successful Payment (Test Only)" button visible and clickable |
| 15. verify-payment API call | BUG-CRITICAL | Fires after simulate click but returns HTTP 400 |
| 16. Post-payment chatbox | PASS | After 400 error, page transitions to post-payment "Chat with Keen" chatbox |
| 17. Keen onboarding question | PASS | "Let's start simple. What's your full name?" - onboarding questionnaire begins |
| 18. log-pay-test endpoint | BUG | 0 calls observed. `api.purebrain.ai/api/log-pay-test` never called |
| 19. Birth pipeline (89.167.19.20:8443) | BUG | 0 calls observed. Birth start endpoint never called |

---

## Critical Bugs Found

### Bug 1: BYPASS DOES NOT REVEAL PRICING SECTION
- **Symptom**: After `pb-full-bypass` submitted, AI responds "Welcome back, Jared. Bypass mode activated." but `.pricing-section` stays `display:none`
- **Root cause**: The bypass handler in JS does NOT include `document.querySelector('.pricing-section').style.display = 'block'`
- **Impact**: Jared cannot test pricing/payment flow via bypass - must use real conversation or manually trigger
- **Fix**: Add pricing reveal to bypass handler in page script

### Bug 2: verify-payment API returns HTTP 400
- **Symptom**: `api.purebrain.ai/api/verify-payment` called after "Simulate Successful Payment" but returns 400
- **Impact**: Payment verification fails. The page still transitions to post-payment chatbox (graceful degradation), but payment is NOT recorded
- **What 400 means**: Likely the simulated payment has no real order ID - the API expects a real PayPal transaction ID
- **Fix needed**: Either (a) skip verify-payment for simulated payments, or (b) mock the verify-payment endpoint for sandbox mode

### Bug 3: log-pay-test endpoint never called
- **Symptom**: 0 calls to `api.purebrain.ai/api/log-pay-test` throughout entire session
- **Impact**: Payment logging to custom endpoint is broken
- **May be related to**: verify-payment 400 causing early return before log-pay-test fires

### Bug 4: Birth pipeline never triggered
- **Symptom**: 0 calls to `89.167.19.20:8443/api/birth/start`
- **Impact**: Witness birth pipeline not starting for new customers
- **May be related to**: verify-payment 400 blocking downstream pipeline calls

### Bug 5: Sandbox banner not visible
- **Symptom**: No `.sandbox-banner` element in DOM, no orange "SANDBOX MODE" bar visible
- **Note**: Was visible in Feb 25 audit. May have been removed or hidden in a recent deploy

---

## What IS Working

- Password gate: correct
- Hero section renders with dark background: correct
- "Awaken Your PURE BRAIN" button: works
- AI awakening chatbox: works beautifully
- Conversation logging: works (`log-conversation` HTTP 200 on every exchange)
- AI personality (pre-bypass): good, natural, engaging
- Bypass code: recognized and acknowledged correctly (but doesn't reveal pricing)
- PayPal SDK: loads correctly (HTTP 200 from sandbox.paypal.com)
- PayPal modal: displays correctly with tier name, price, SDK buttons
- Sandbox simulate button: present and clickable
- Post-payment chatbox transition: occurs (despite 400 on verify-payment)
- Post-payment "Keen" onboarding: loads and asks "What's your full name?"

---

## Network Calls Timeline

```
Page load:      PayPal SDK → sandbox.paypal.com → HTTP 200 (good)
First message:  log-conversation → purebrain.ai/wp-json → HTTP 200 (good)
Bypass send:    log-conversation → HTTP 200 (good)
PayPal click:   PayPal smart/buttons → HTTP 200, SDK iframes rendered
Simulate click: verify-payment → api.purebrain.ai → HTTP 400 (BAD)
After 400:      Page transitions, log-pay-test = 0, birth/start = 0
```

---

## Post-Payment Chatbox Visual

After simulate click (despite 400):
- Full-screen dark chatbox opens
- Header: "Chat with Keen" with green Online dot, "Ready to assist" status
- PUREBRAIN logo in blue/orange in header top right
- Two messages visible:
  - "Hey — welcome. I'm Keen, and I'm genuinely glad you made it here."
  - "Now that Keen is officially yours, let's make sure I actually know who I'm working with. This isn't a form — it's a conversation. Ready?"
  - "Let's start simple. What's your full name?"
- Input field: "Message Keen..." placeholder with orange Send button

---

## Selector Reference (Confirmed Working)

- Password field: `input[id^='pwbox-']`
- Begin button: `.chat-initial__btn`
- Chat input: `#userInput`
- Submit button: `#submitBtn`
- AI messages: `.message--ai`
- Pricing section: `.pricing-section` (or `#pricing`)
- Pricing cards: `.pricing-card`
- Pricing buttons: `.pricing-card button`
- PayPal overlay: `#pb-paypal-overlay`
- PayPal modal: `#pb-paypal-modal`
- PayPal tier name: `#pb-paypal-tier-name`
- Simulate button: button with text "Simulate Successful Payment (Test Only)"
- Post-payment chatbox input: input with placeholder "Message Keen..."

---

## Console Errors (Non-blocking)

All repeated CSP violations for third-party services blocked by the security plugin:
- clarity.ms (analytics)
- region1.google-analytics.com (GA4)
- csp.secureserver.net (GoDaddy CSP reporter)
- SCC Library already loaded (cosmetic duplicate)
- WonderPush remoteconfig error

None of these block the core flow.

---

## Screenshots Location

`/home/jared/projects/AI-CIV/aether/exports/screenshots/sandbox2-e2e-20260302/`

Key screenshots:
- `001-01-page-load.png` - Password gate
- `003-03-after-password.png` - Hero section post-auth
- `006-06-after-begin-click.png` - Chat loading
- `007-07-ai-first-message.png` - First AI message
- `011-11-third-exchange.png` - "Click here to see pricing options available" button visible
- `debug-01-after-bypass.png` - Bypass confirmed but pricing hidden
- `paypal-01-pricing-revealed.png` - Pricing cards with $79, $149, $499 visible
- `simulate-02-paypal-modal-open.png` - PayPal modal with SDK buttons + simulate button
- `simulate-04-after-simulate.png` - Post-payment "Chat with Keen" chatbox

## Tags

purebrain, sandbox-2, paypal, e2e, verify-payment, birth-pipeline, post-payment, keen-chatbox, bypass-pricing-bug, log-pay-test-missing, qa-2026-03-02
