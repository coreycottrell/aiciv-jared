# Memory: Sandbox-2 Seed Logging Verification Audit

**Date**: 2026-03-03
**Agent**: browser-vision-tester
**Type**: pattern + gotcha + synthesis
**Tags**: browser-vision, paytest, sandbox-2, seed-logging, birth-pipeline, orderId-linkage, conversation_complete

---

## Context

Full E2E seed logging verification test on https://purebrain.ai/pay-test-sandbox-2/.
Goal: confirm TWO seed events fire correctly:
1. Seed after payment completion
2. Seed after post-payment chat completion

---

## Key Findings

### 1. Seed 1 (Payment): PARTIAL - Two Log Files Behave Differently

**payments.jsonl**: FIRES correctly - orderId present, verified=true
**pay_test.jsonl**: Q&A entries have orderId=null - seed watcher DOES NOT fire

Root cause: Payment orderId (SANDBOX-TEST-xxx) is verified and stored in payments.jsonl,
but is NOT passed through to the Q&A logging calls in pay_test.jsonl.
The JS fires log-pay-test after each Q&A answer with `orderId: null`.
The seed-watcher-filtered.sh requires `orderId != null` to trigger Telegram alert for pay_test.

Fix needed: After payment verification, store orderId in a variable and pass it into
all subsequent Q&A log-pay-test calls.

### 2. Seed 2 (Chat Completion): DOES NOT FIRE - Birth Pipeline Down

The `conversation_complete` event in web_conversations.jsonl is the Seed 2 trigger.
This event ONLY fires after the birth pipeline succeeds (birth:init:start -> birth API -> completion).
In this test:
- birth:init:start fires after "role" Q&A answer (correct timing)
- birth:start:failed (2 attempts) - Witness server not responding
- conversation_complete NEVER logged
- Seed 2 watcher never triggers

Events sequence in web_conversations new entries:
1. conversation_start (pre-payment chatbox initial)
2. questionnaire:name
3. questionnaire:email
4. questionnaire:company
5. questionnaire:role + birth:init:start (same time)
6. birth:start:failed x2

### 3. Pay Test Log Fires Per Q&A Answer (7 entries for 4 answers = duplication)

7 new entries for 4 Q&A answers + 1 payment event. Duplication pattern:
- Payment fires at least 2 entries per action (pay_test_completion type logged multiple times)
- This matches 2026-03-02 v6 finding: "duplicate log-pay-test at role stage"
- The role stage fires 2x (questionnaire:role + birth:init:start both log)

### 4. BIRTH Still Triggers After Role (Not Goal)

Confirmed again: BIRTH pipeline fires immediately after role is answered.
`primaryGoal` = null in all Q&A log entries (automated tests cannot complete goal Q)
This is by design: OAuth gate overlays the input after birth triggers.

### 5. PTC Chatbox Timing (2026-03-03 run)

- Payment bypass clicked: ~16:39:45
- verify-payment 200: ~16:39:45 (immediate)
- PTC input row active (display:flex): ~16:40:16 (31 seconds after bypass)
- Faster than 2026-03-02 run (109s to active in that test)

### 6. Seed Watcher Infrastructure

seed-watcher-filtered.sh was RUNNING (5 PIDs).
It monitors 3 files but has different trigger criteria:
- payments.jsonl: ALWAYS notify (any entry fires) - WORKING
- pay_test.jsonl: Only notify when orderId != null - NOT WORKING (orderId always null in automated test)
- web_conversations.jsonl: Only notify for conversation_complete or capabilities_revealed - NOT WORKING (birth fails)

For a REAL user flow (not sandbox):
- A real PayPal payment would populate orderId in pay_test.jsonl IF JS is fixed
- A successful birth pipeline would fire conversation_complete

---

## Brand Colors Verified

- `.text-blue` CSS computed: `rgb(42, 147, 193)` = #2a93c1 (Pure Tech Blue - CORRECT)
- `.text-orange` CSS computed: `rgb(241, 66, 11)` = #f1420b (Pure Tech Orange - CORRECT)
- Comparison table: `PURE BR(blue)AI(orange)N(blue)` pattern correct
- PTC header: `PUREBR(blue)AI(orange)N(blue)` confirmed visually

---

## What IS Working Correctly

- Password gate
- Begin Awakening button
- pb-full-bypass code
- proCta -> PayPal modal (Awakened $149/mo)
- Sandbox bypass button click
- verify-payment API 200 OK
- payments.jsonl logging
- PTC initialization (display:flex within ~30s)
- log-pay-test API calls per Q&A answer
- log-conversation API calls per Q&A answer
- Q&A flow (name/email/company/role all captured)

---

## Action Items for Dev Team

1. **URGENT**: Check Witness server birth endpoint
   - URL: api.purebrain.ai/api/birth/start (via Cloudflare tunnel)
   - Until fixed, no users can complete the full birth pipeline

2. **MEDIUM**: Fix pay_test.jsonl orderId linkage
   - After verify-payment returns orderId, store it in `window.currentOrderId`
   - Pass `orderId: window.currentOrderId` in all subsequent log-pay-test calls
   - This will enable the seed watcher to fire Telegram alerts for Q&A completions

3. **LOW**: Consider separate seed events from birth dependency
   - conversation_complete should possibly fire on Q&A completion, not just on birth
   - This would decouple seed logging from Witness server availability

---

## Test Script

/home/jared/projects/AI-CIV/aether/tools/e2e_seed_verify_20260303.py

## Screenshots

/home/jared/projects/AI-CIV/aether/exports/screenshots/e2e-seed-test-20260303/
Key: 001 (hero), 004 (modal), 008 (PTC active), 012 (Q&A role step)

## Report

/home/jared/projects/AI-CIV/aether/exports/e2e-seed-verify-report-20260303.md
