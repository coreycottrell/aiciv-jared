# Memory: Witness Birth Pipeline Chatflow Visual Audit

**Date**: 2026-02-24
**Type**: teaching + operational
**Topic**: pay-test-sandbox-2 and pay-test-2 visual audit for Witness birth pipeline integration

---

## Key Discoveries

### 1. Witness v4 Code Already Deployed in sandbox-2

`pay-test-chat-flow-v4.js` is embedded in the sandbox-2 page. Contains:
- `runBirthInit()` - calls POST /api/birth/start -> shows OAuth button
- `runPortalButtonWatcher()` - polls GET /api/birth/portal-status/{container}
- Container name falls back to `purebrain-{humanFirstName}` slug
- Birth start timeout: 180s (production is ~145s)
- Data fields: containerName, birthOauthUrl, birthAuthenticated

### 2. Witness Slots Into Phase 5 (After Telegram, Before Learn-More)

UX flow order:
1. Name, Email, Company, Role (text fields)
2. Claude auth ("Before we go deeper") - Phase 1
3. Primary Goal - Phase 3
4. Behind the Curtain 10 slides - Phase 4
5. Telegram setup - Phase 5
6. Thank You message
   --> runBirthInit() fires HERE <--
7. Portal Button Watcher (polls Witness)
8. Learn More loop (5 deeper questions)

### 3. Role Question Changed: Now Free Text (Not Buttons)

v3 memory said role had choice buttons. As of 2026-02-24, it's a free-text field:
"What's your role or title? What do you actually do day-to-day? (Optional.)"
No buttons - user types their role.

### 4. Claude Auth Prompt (Exact Copy)

After typing role, Keen says:
"Before we go deeper - I need one thing to think at full power, [Name].
Keen runs on Claude, Anthropic's most capable model. To link your account,
paste your Claude API key below. It starts with sk-ant- - you can grab it
from platform.claude.com -> API keys -> Create Key."
- Orange button: "Open Claude Console" (opens platform.claude.com in new tab)
- Orange button: "I have my key ->"
- Then user types key in textarea (gets masked)

### 5. No User-Visible Witness/AiCIV Language Currently

All Witness references are:
- In JS code comments (not rendered)
- In error fallback messages (only on auth failure)
- Backend API comments: `/api/log-conversation` "required by AICIV"

### 6. pay-test-2 Differences vs sandbox-2

- pay-test-2 has 4 pricing tiers (Awakened, Bonded, Partnered, Unified, Enterprise)
- pay-test-2 does NOT have #pb-sandbox-bypass-btn (not in DOM, not in scripts)
- pay-test-2 does NOT have Witness v4 code
- pay-test-2 is a more complete/production-facing page
- sandbox-2 is the development/testing page

### 7. API Endpoints

- Payment: https://api.purebrain.ai/api/verify-payment
- Logging: https://api.purebrain.ai/api/log-conversation (AICIV required)
- Witness start: http://104.248.239.98:8099/api/birth/start
- Witness code: http://104.248.239.98:8099/api/birth/code
- Witness status: http://104.248.239.98:8099/api/birth/portal-status/{container}

### 8. WAF Rate Limit Still Active

After ~4 test runs, GoDaddy WAF blocks with 3-char response.
Must wait 20+ minutes between test batches.

---

## Selector Reference (2026-02-24 Confirmed)

- Password field: `input[id^="pwbox-"]`
- Begin Awakening: `.chat-initial__btn`
- Pre-payment input: `#userInput`
- Discover button: `#seeWhatBtn`
- Activate Now: `#proCta`
- Sandbox bypass: `#pb-sandbox-bypass-btn`
- Post-payment container: `#pay-test-post-payment`
- Post-payment textarea: `textarea[placeholder="Message Keen..."]`
- Post-payment send: `button.ptc-send-btn`
- AI messages: `.ptc-msg--ai`
- Choice buttons: `.ptc-btn`

---

## Report Location

Full visual report: `/home/jared/projects/AI-CIV/aether/exports/witness-chatflow-visual-audit-report-20260224.md`
Screenshots: `/home/jared/projects/AI-CIV/aether/exports/screenshots/witness-audit-20260224/`

**Tags**: purebrain, pay-test, witness, aiciv, birth-pipeline, chatflow, sandbox-2, paytest-2, questionnaire, claude-auth, role-question, v4
