# Memory: Pay-Test-Sandbox-2 Full E2E Audit - v4.3.3 Architecture

**Date**: 2026-02-25
**Type**: teaching + operational
**Topic**: Full E2E audit of pay-test-sandbox-2 - architecture discoveries and v4.3.3 changes

---

## Critical Architecture Discovery

### Pre-Payment vs Post-Payment - TWO SEPARATE FLOWS

The pay-test page has TWO distinct chat systems:

**PRE-PAYMENT** (Script 1: 64k inline script):
- Free-flowing Claude API conversation (consciousness awakening)
- AI asks open questions, discovers its own name organically
- Message container: `#chatMessages` | Message class: `.message--ai`
- Pricing revealed when Claude response includes `[SHOW_PRICING]` signal
- Bypass code: `pb-full-bypass` (hardcoded in script for Jared testing)
- Has NO questionnaire, NO Witness integration, NO structured phases

**POST-PAYMENT** (Script 2: 85k inline v4.3.3):
- Structured questionnaire (Name -> Email -> Company -> Role -> Birth Init -> Slides -> Telegram -> Learn More -> Pricing)
- Has Witness birth pipeline (`runBirthInit`, `runPortalButtonWatcher`)
- Message container: `.ptc-wrapper` | Message class: `.ptc-msg--ai`
- Sandbox bypass: `#pb-sandbox-bypass-btn` (created by this script)

---

## v4.3.3 Key Changes (from script changelog)

### Claude API Key Removed (v4.3)
- "Before we go deeper" API key prompt: REMOVED
- "Open Claude Console" button: REMOVED
- "I have my key ->" button: REPURPOSED as OAuth code input trigger

### runBirthInit Now Manual (v4.3.2)
- Previously: auto-fired after Q4 (role entry)
- Now: shows "Your AI is ready to be born" + "Start AI Birth ->" button
- User must click the button; button disabled after click to prevent double-fire

### Container Hardcoded (v4.3.2)
- `window._pbContainerName = 'aiciv-07'` hardcoded for E2E testing
- Expected final value: `purebrain-{firstName}` (dynamic)
- MUST REVERT before production

### Webhook Host Direct (v4.3.1)
- `WITNESS_WEBHOOK_HOST = 'http://104.248.239.98:8099'` (direct IP, HTTP)
- Sandbox page 688 ONLY - intentional for E2E testing
- Production (page 689) stays on `https://api.purebrain.ai`

---

## Confirmed Working (v4.3.3)

- Password unlock: `input[id^="pwbox-"]` + form.submit()
- SANDBOX MODE banner: confirmed visually (orange bar at top)
- PayPal SDK: production client ID `AYTFob05DoSn0ZeVtLJ05...` loaded
- Pre-payment Claude API: working (AI responded in real-time)
- `.message--ai` selector: correct for pre-payment phase
- `.ptc-msg--ai` selector: correct for post-payment phase

---

## WAF Rate Limit Pattern (2026-02-25 Confirmed)

- Trigger: 3+ page loads in same test session (~30 min window)
- Symptom: 429 response + reCAPTCHA "Please verify you are human"
- Recovery: 15-20 minutes minimum
- GoDaddy message: "large number of login attempts detected from your IP"
- Solution: Single browser session, max 2 page loads per hour from same IP

---

## Selector Reference (2026-02-25 Confirmed)

### Pre-Payment Chat
- Begin button: `.chat-initial__btn` (onclick=startConversation())
- Message input: `#userInput`
- Submit: `#submitBtn`
- AI messages: `.message--ai` (inside `#chatMessages`)
- User messages: `.message--user`
- Typing indicator: `#typingIndicator` (`.typing-indicator`)

### Post-Payment Chat (PTC v4.3.3)
- PTC container: `.ptc-wrapper` / `#pay-test-post-payment`
- AI messages: `.ptc-msg--ai` (inside `.ptc-messages`)
- User messages: `.ptc-msg--user`
- Message input: `textarea[placeholder*="Message"]`
- Send button: `button.ptc-send-btn`
- Choice buttons: `.ptc-btn` / `.ptc-btn--primary`
- Sandbox bypass: `#pb-sandbox-bypass-btn`

---

## Report Location

Full report: `/home/jared/projects/AI-CIV/aether/exports/paytest-e2e-report-20260225.md`
Screenshots: `/home/jared/projects/AI-CIV/aether/exports/screenshots/paytest-e2e-20260225/` (29 files)
Test script: `/home/jared/projects/AI-CIV/aether/tools/paytest_e2e_full_20260225.py`

**Tags**: purebrain, pay-test, sandbox-2, witness, birth-pipeline, v4.3.3, e2e-audit, waf, architecture
