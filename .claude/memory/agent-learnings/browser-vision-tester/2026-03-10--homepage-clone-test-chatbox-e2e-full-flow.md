# Memory: homepage-clone-test Full E2E Chatbox Flow

**Date**: 2026-03-10
**Agent**: browser-vision-tester
**Type**: technique + pattern + synthesis
**Tags**: homepage-clone-test, chatbox, e2e, bypass, waitlist, pricing, keen, confirmation

---

## Context

Full E2E test of https://purebrain.ai/homepage-clone-test/ chatbox flow.
Entered "pb-full-bypass" as name, navigated to pricing, selected Awakened tier, filled waitlist form, verified confirmation.

---

## RESULT: FULL PASS

All 9 stages passed. Form submitted. Confirmation popup appeared.

---

## Chat System Architecture (NEW - Different from sandbox-3)

This is NOT the PTC chat system (no #ptc-input, no .ptc-msg--ai). It's a custom chat:

```
Begin button: button.chat-initial__btn (inside #chatInitial)
Input: #userInput (type=text, class=chat-input__field, placeholder='Type your response...')
Submit: #submitBtn (class=chat-input__submit) or Enter
AI messages: .message.message--ai
User messages: .message.message--user
Chat discovery CTA: #seeWhatBtn (onclick=window.showPersonalizedCapabilities())
```

## Bypass Flow (CONFIRMED WORKING)

Entering "pb-full-bypass" as name triggers:
- AI: "Welcome back, Jared. Bypass mode activated."
- AI: "I am Keen. Ready to go."
- Shows #seeWhatBtn: "CLICK TO DISCOVER WHAT KEEN CAN DO"

## Pricing Section (JS-Gated)

- `window.revealPricing()` exists but does NOT reveal pricing (bug? or sequence issue)
- `window.closeCelebrationAndShowPricing()` DOES reveal pricing
- After reveal: `.pricing-section` gets `.active` class, display=block, height=2496px

## 4 Pricing Tiers

| Tier | Button ID | onclick |
|------|-----------|---------|
| Awakened (featured) | #proCta | openWaitlistModal('Awakened') |
| Partnered | #partnerCta | openWaitlistModal('Partnered') |
| Unified | #unifiedCta | openWaitlistModal('Unified') |
| Enterprise | (none) | inline JS sets tier + opens modal |

## Waitlist Form

```
Modal: #waitlistModal (class=waitlist-modal, display:flex when open)
Tier display: #waitlistTierDisplay
Fields:
  #waitlistName (text, placeholder='Your name')
  #waitlistEmail (email, placeholder='you@example.com')
  #waitlistRatingValue (hidden, set by rating buttons)
  #waitlistUseCase (textarea)
  #waitlistCompany (text, optional)
  #waitlistRole (text, optional)
  #waitlistUrgency (SELECT: ASAP / Within 30 days / Within 90 days / Just exploring)
Rating: .waitlist-form__rating-btn[data-rating="1"-"5"] - clickable buttons
Submit: #waitlistSubmitBtn (class=waitlist-form__submit, text='JOIN PRIORITY WAITLIST')
Success: .waitlist-success (personalized confirmation with name from form)
```

## Confirmation Text (Personalized)

"Congratulations [Name]! Keen has been reserved. Your Brain. Your AI. Actual Intelligence. We take awakening your AI very seriously, and so we will get in touch with [email] as soon as a spot opens up with PureBrain.ai. Thanks for being part of the future, today."

## Known Bugs

1. Pricing section shows as black when revealed (transparent bg + dark video overlay)
2. revealPricing() doesn't work; closeCelebrationAndShowPricing() is the correct function
3. Waitlist modal offsetParent=null despite display:flex (visual OK, interaction OK)

## Console Errors (Non-Blocking)

- GTM blocked by CSP (3x)
- Elementor CSS returning text/html MIME type (2x) - post-1502.css and post-11.css 404ing
- wsimg.com scripts blocked (3x)
- Blob worker CSP violation for WonderPush (3x)

IMPORTANT: Elementor CSS 404 (`post-1502.css`) may affect styling. Worth investigating.

## Timing

- Page load to chatbox ready: ~5s
- Begin click to AI greeting: ~0.5s
- Bypass response: ~4.5s
- Pricing reveal (closeCelebrationAndShowPricing): instant
- Waitlist form submit to confirmation: instant (0s)

## Scripts

- `/home/jared/projects/AI-CIV/aether/tools/e2e_clone_test_v3_full.py` - Full working E2E test
- `/home/jared/projects/AI-CIV/aether/exports/e2e-clone-test-report-20260310.md` - Full report

## Screenshots

`/home/jared/projects/AI-CIV/aether/exports/screenshots/clone-test-e2e-20260310/`
Key: 003 (before-begin), 007 (bypass activated), 014 (pricing), 022 (form filled), 024 (confirmation)
