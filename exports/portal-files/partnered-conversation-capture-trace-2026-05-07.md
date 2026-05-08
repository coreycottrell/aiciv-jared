# `/partnered/` Conversation Capture Trace — 2026-05-07

**Status**: SILENT FAILURE confirmed. The chat UI on `/partnered/` (and 3 other production payment pages) is non-functional. Sheila has no captured conversation because the page literally cannot capture one.

## 1. Pipeline Map

- Chat init: `_pbPrePurchaseSession = {…}` (window var) — **NOT INITIALIZED on partnered/**
- "Begin Awakening" button (line 1550): `onclick="startConversation()"` -> `/api/log-conversation` -> `logs/purebrain_web_conversations.jsonl` (`purebrain_log_server.py:441`)
- Chat send (line 1557): `onsubmit="handleSubmit(event)"` -> same endpoint
- Post-pay questionnaire (line 6794-6804): collects `payTestData.email`, then `fireSeed()` -> `/api/send-seed` -> seed dispatcher
- Payment approve (line 5058 `verifyPaymentServerSide`): -> `/api/verify-payment` -> seed dispatcher
- `session_uuid` line 5705; `customer_email` collected POST-payment only.

## 2. Sheila's Conversation — NOT FOUND ANYWHERE

Searched: `purebrain_web_conversations.jsonl` (3,163 entries), `portal_server.log`, `purebrain_log_server.log`, `agentmail_*.log`, `gmail_monitor.log`, all repo `*.json{,l}` recursively. **Zero chat records, zero awakening artifacts.** Only finding: `.magic-links.json` key `email:Sheila@couplify.com` containing the corrupted `ai_name=Torque, human_name=Jay Whitehurst, container=pb2-42` record (the cross-contaminated link).

## 3. Root Cause: Dead Chat UI in Production

`exports/cf-pages-deploy/partnered/index.html` and live `https://purebrain.ai/partnered/` (8284 lines, 444 KB, fetched 16:48 UTC):

- Line 1550: `<button onclick="startConversation()">` — **`startConversation` undefined** on this page (`grep -c = 0`)
- Line 1557: `<form onsubmit="handleSubmit(event)">` — **`handleSubmit` undefined** (`grep -c = 0`)
- Lines 5740, 7889, 8227, 8246 read `window._pbPrePurchaseSession` but **nothing assigns it** (`grep -c "_pbPrePurchaseSession\s*=" = 0`)

## 4. Other-Page Parity (systemic)

`partnered/`, `awakened/`, `unified/`, `insiders/awakened/`: ALL show `initSession=0, startConv=0, handleSubmit=0`. `pay-test*` sandboxes (4 of them) and homepage have handlers (homepage uses different Claude-proxy chat path). **All four production customer-facing payment pages are broken identically.**

## 5. What Happened to Sheila

1. Landed `/partnered/`, clicked PayPal subscribe.
2. PayPal subscription `createSubscription` (line 5132) — does **NOT** pass `custom_id`, so no UUID reaches verify-payment.
3. `verifyPaymentServerSide` POSTed `{orderId, tier, payerInfo, sessionUuid:""}` (UUID empty for subscription path).
4. `handlePaymentSuccess` runs: referral fire, banner shown, scroll to `#awakening`. **`window.onPaymentComplete` is never defined on partnered/, so `initPayTestFlow` never starts.** The post-payment questionnaire never runs. `fireSeed`/`/api/send-seed` never fires.
5. Server-side `/api/verify-payment` fires seed dispatcher with `uuid=, email=Sheila@couplify.com, name=Jay Whitehurst`. S1-S4 all 0. S5-payerName fuzzy-matches "Jay" -> 26 of Jay Hutton's messages -> binds Sheila to Torque container.

## 6. Seed Dispatcher Diagnosis

S1 orderId 0 (correct, fresh order). S2 sessionUuid 0 (UUID empty in payload + no JSONL entry exists). S3 payer-email 0 (no chat to contain it). S4 recent-chat 0 (no chat ran). S5 first-name 26 messages (false positive on "Jay" matching Jay Hutton's history). **S5 fired and bound Sheila to Torque container.**

## 7. Constitutional Gaps

1. Production payment pages serve chat UI wired to undefined handlers. Customer sees working UX, nothing captures.
2. `/api/verify-payment` fires seed unconditionally even with no chat session. AI-name-must-populate satisfied numerically, violated semantically.
3. No customer email collected pre-payment. PayPal payer email ≠ customer email when third party pays.
4. PayPal subscription flow omits `custom_id` (line 5132 vs line 5163 for one-time). Subscription tiers can't link payment to chat session even when chat works.
5. Silent-failure UX. No console error. Customer believes awakening completed.

## 8. Root Cause

`/partnered/` is a `pay-test-partnered/` template with chat-handler functions stripped (likely deploy regression) but chat markup retained. Customers click a fake chat, proceed to PayPal, pay; seed dispatcher operating on PayPal payer info alone fuzzy-matches them to a stranger's container by first name. The "AI name must populate" guard passed numerically (Torque exists) but semantically failed (Torque belongs to Jay Hutton). This is systemic: every customer paying via `/partnered/`, `/awakened/`, `/unified/`, `/insiders/awakened/` is exposed to S5 cross-contamination on common first names.

## 9. Fix Path (Constitutional)

**Today**: Disable S5 or gate behind email-domain match. Hard-block verify-payment seed when S2-uuid=0 AND S3-email=0; Telegram-alert + manual review.

**This week**: Restore `startConversation/handleSubmit/_pbPrePurchaseSession` on all production payment pages or remove dead chat markup. Thread `payTestData.sessionUuid` into PayPal subscription path.

**Lock**: Amend `feedback_seed_flow_never_deviate.md` — seed requires UUID/email match or human review, never first-name fuzzy. Pre-deploy guard: grep-fail pages with `onclick="startConversation()"` whose bundle doesn't export the function.

## Memory Search
Searched `.claude/memory/` for `seed`, `magic.link`, `birth.pipeline`, `partnered`. Found: prior trace, S5 memo, `feedback_seed_flow_never_deviate.md`, ONBOARDING-SPEC-DEFINITIVE.md. Applied: AI-name-must-populate (violated), UUID-pipeline-lock (violated by subscription path).

## Memory Written
Path: `.claude/memory/agent-learnings/full-stack-developer/2026-05-07--partnered-chat-ui-dead-handlers-undefined.md`
Type: gotcha
Topic: All production payment pages (`partnered`, `awakened`, `unified`, `insiders/awakened`) have chat UI markup wired to undefined JS handlers — silent capture failure.
