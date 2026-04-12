# Seed Addendum — Brain Stream Button Click Implementation

**Date**: 2026-03-15
**Type**: feature
**Status**: SHIPPED

---

## What Was Built

Added a second "addendum" seed email that fires when the user clicks the "Enter [AI]'s Brain Stream" portal button. The initial seed email fires early (at email collection) with just name + email. This addendum fires at the very end of the flow and contains all the rich data collected afterward.

## Architecture

### Backend: `/api/seed-addendum`
- File: `tools/purebrain_log_server.py`
- New function `_send_seed_addendum(data)` at line 614
- New Flask route `/api/seed-addendum` (POST) at line 2637
- Runs in background thread (fire-and-forget, does not block user)
- No dedup — expected to send once per flow completion
- Sandbox detection via `_is_sandbox_seed()` — adds TEST prefix to subject/body
- Email: FROM purebrain@puremarketing.ai TO aiciv-seed-inbox@agentmail.to, CC jared@puretechnology.nyc + aether-aiciv@agentmail.to
- Saves .md attachment to `exports/{name}-{ai}-seed-addendum.md`
- Gmail SMTP primary, AgentMail fallback (same pattern as `_forward_seed_to_witness`)
- Subject format: `[PureBrain Seed Addendum] {ai_name} ({tier}) — {human_name}`
- Includes magic link in email and .md

### Frontend: `fireSeedAddendum()` helper
Added to three CF Pages HTML files:
- `exports/cf-pages-deploy/pay-test-2/index.html`
- `exports/cf-pages-deploy/insiders/index.html`
- `exports/cf-pages-deploy/pay-test-sandbox-3/index.html`

The helper is defined once per file (just before `runPortalButtonWatcher`) and wired to all three button activation paths:
1. **Immediate-activation path** (in `runThankYouMessage`, ~line 16545 in pay-test-2) — when magic link already arrived before button rendered
2. **Witness endpoint watcher** (`runPortalButtonWatcher`, ~line 16983) — polls Witness API
3. **Magic link poller** (`activateButton` in `runMagicLinkPoller`, ~line 17075) — polls `/api/magic-link/{uuid}`

The click listener is `portalBtn.addEventListener('click', function() { fireSeedAddendum(); })` added after portalBtn is created and before `replaceWith`.

## Gotcha: UTF-8 Right Single Quote
The `activateButton` function in `runMagicLinkPoller` uses a UTF-8 right single quote character (\xe2\x80\x99 = ') in the backtick string `` `Enter ${safeAiName}'s Brain Stream` ``. This looks identical to a plain apostrophe in the terminal but is not. Must use binary mode (`rb`/`wb`) when patching these files or the string replacement will silently fail.

## Payload Fields Sent
session_uuid, aiName, name, email, tier, company, role, primaryGoal, orderId, learnMoreAnswers, magicLink, prePurchaseSessionId, naming_session_id, timestamp, page_url

## Pages NOT Requiring Change
pay-test-awakened, pay-test-partnered, pay-test-unified — WordPress-only pages, not in cf-pages-deploy with standalone JS. Would need separate investigation if addendum needed there.

## Verification
- Python syntax check: passed
- Live endpoint test: `{"ok": true, "message": "Seed addendum queued"}`
- SMTP confirmed sent in logs: `Seed addendum sent via SMTP: aiName=TestAI, session=test-verify-001`
- .md saved to exports confirmed in logs
- CF Pages deployed (3 files uploaded)
- CF cache purged for all three pages
