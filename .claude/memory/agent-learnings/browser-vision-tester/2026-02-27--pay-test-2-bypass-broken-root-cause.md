# Memory: pay-test-2 Bypass Codes NOT Deployed - Root Cause

**Date**: 2026-02-27
**Type**: operational + teaching
**Topic**: Both bypass codes broken on pay-test-2 - bypass logic missing from page source

---

## Root Cause Confirmed

The bypass codes (`pb-full-bypass` and jared bypass) were **never deployed** to pay-test-2.

The bypass interception logic exists on **pay-test-sandbox-2 (page 688)** but was not carried over when pay-test-2 was created or updated.

### handleSubmit function on pay-test-2 (broken):
```javascript
function handleSubmit(event) {
    event.preventDefault();
    const input = userInput.value.trim();
    if (input && !state.isTyping && state.conversationStarted) {
        processResponse(input);  // Goes straight to Claude - NO bypass check
    }
}
```

### What happens when bypass codes are typed:
- `pb-full-bypass`: AI responds philosophically "That's not a name — that's more like a code."
- Jared bypass: AI responds "Jared." and continues asking questions
- Pricing section: exists in DOM (display:none) but never revealed

---

## Source Check Results

- `pb-full-bypass`: NOT in pay-test-2 page source
- `i'm jared, bypass everything`: NOT in pay-test-2 page source
- `SHOW_PRICING`: EXISTS (fires when Claude outputs [SHOW_PRICING] in response)
- `handleSubmit`: EXISTS but has no bypass interception
- `processResponse`: EXISTS but has no bypass interception

---

## Fix Required

Add bypass interception to `handleSubmit` or `processResponse` in pay-test-2 script:

```javascript
const BYPASS_CODES = ['pb-full-bypass', "i'm jared, bypass everything and name yourself"];
if (BYPASS_CODES.some(code => input.toLowerCase().includes(code.toLowerCase()))) {
    addMessage("Bypass activated. Nova is ready.", true);
    document.getElementById('pricing').style.display = 'block';
    document.getElementById('pricing').scrollIntoView({behavior: 'smooth'});
    return;
}
```

---

## Test Infrastructure

- Page URL: https://purebrain.ai/pay-test-2/
- Password: PureBrain.ai253443$$$
- Begin Awakening button selector: `.chat-initial__btn`
- Input selector: `#userInput`
- Submit selector: `#submitBtn`
- AI messages: `.message--ai`
- Pricing section: `#pricing` (display:none when hidden)

---

## Console Errors on pay-test-2 (Non-critical)

- CSP violations for GTM, WonderPush (cosmetic)
- Log server CSP: api.purebrain.ai:8443 (different port blocked by CSP)
- CORS error: sageandweaver-network.netlify.app (capture proxy CORS blocked)

---

## Screenshots

Location: `/home/jared/projects/AI-CIV/aether/docs/bypass-test/`
Report: `/home/jared/projects/AI-CIV/aether/docs/bypass-test/BYPASS-TEST-REPORT.md`

**Tags**: purebrain, pay-test-2, bypass, pb-full-bypass, jared-bypass, pricing-reveal, broken
