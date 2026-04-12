# Memory: CTO Architecture Decision — Witness Birth Pipeline Integration

**Date**: 2026-02-24
**Type**: teaching + operational
**Agent**: cto
**Topic**: Architecture decisions and team assignments for wiring Witness Birth Pipeline into PureBrain post-payment chatbox (v3 → v4)

---

## Situation Summary

The v3 chatbox (deployed Feb 22 to pages 688 and 689) has `runPortalButtonWatcher` polling the WRONG endpoint
(`POST https://api.purebrain.ai/api/portal-status`) and missing the entire OAuth step that the Witness
Birth Pipeline requires. This is a 3-step integration: `/start` → OAuth UI → `/code` → poll `/portal-status/{container}`.

The Witness API (104.248.239.48:8099) is production-ready with 13 passing tests. Container naming is
`{civname}-{humanname}`, sourced from capture form metadata. No auth headers required on PureBrain's calls.

## Architecture Decisions Made

### Decision 1: Insertion Point — After "Learn more" button, Before runLearnMoreLoop
The `/start` call (runBirthInit) fires IMMEDIATELY when the customer clicks "Learn more →" inside
`runThankYouMessage`. Rationale: this is the first moment post-payment where ~60s of async waiting
is tolerable. The OAuth UI keeps the customer engaged. runLearnMoreLoop then runs CONCURRENTLY with
the portal-status polling, just as it currently does with the old watcher.

### Decision 2: containerName Plumbing via payTestData
`payTestData` gets a new `containerName` field, set from `window._pbContainerName` (injected by
the integration glue / payment metadata) with fallback to `purebrain-${orderId || 'default'}`.
This avoids requiring a backend call just to get the container name.

### Decision 3: runBirthInit is async/await (NOT setInterval)
Unlike runPortalButtonWatcher (fire-and-forget), runBirthInit is blocking: we MUST have the OAuth URL
before we can show it to the customer. 180s timeout with graceful fallback message if exceeded.

### Decision 4: runPortalButtonWatcher endpoint fix
Switch from POST to GET, change URL to `http://104.248.239.48:8099/api/birth/portal-status/{container}`.
Drop the POST body (email, aiName, orderId) — Witness uses container name in path, not body.
URL validation remains: must be https:// and hostname must end in purebrain.ai.

### Decision 5: OAuth code input is text field, not textarea
8-char alphanumeric code. Sanitized: strip whitespace, allow only [A-Za-z0-9]. Max length 8.
Render inside existing `actions` div using existing ptc-btn pattern for consistency.

### Decision 6: Error boundaries for Witness API failures
- /start timeout (180s): show "Taking longer than expected. Email delivery fallback activated."
  + fire Telegram alert to Jared. Do NOT block the rest of the flow.
- /code error response: prompt customer to re-paste the code once. On second failure: email fallback.
- Portal-status timeout (30 min, 60 polls): existing behavior is correct. Keep it.

### Decision 7: http NOT https for Witness endpoint
The Witness API runs on http://104.248.239.48:8099. This is an inter-server call from browser JS,
which means it will hit a mixed-content block on https://purebrain.ai. Resolution: PureBrain needs
a thin reverse-proxy passthrough at https://api.purebrain.ai/api/birth/* that forwards to
http://104.248.239.48:8099/api/birth/*. This keeps the browser JS calling HTTPS only.
CRITICAL: full-stack-developer must configure this proxy on api.purebrain.ai, OR the Cloudflare
Worker/tunnel must forward it. Security review must confirm this before deploy.

### Decision 8: v4 file naming
Output file: `exports/pay-test-script-chat-flow-v4.js`
Deploy to both page 688 (sandbox-2) and page 689 (pay-test-2) after QA passes on 688 only first.

## Team Assignments

| Agent | Role | Trigger |
|---|---|---|
| full-stack-developer | Build runBirthInit, fix runPortalButtonWatcher, wire containerName | Already running (agent acd595aa4dc47dc56) |
| api-architect | Review Witness API contract integration before code review | CTO sends spec |
| security-engineer-tech | Review v4 code for XSS in OAuth input, CORS on Witness calls, containerName manipulation | After full-stack builds |
| qa-engineer | Test pages 688/689 after sandbox deploy | After security sign-off |

## Key Files
- v3 source: `/home/jared/projects/AI-CIV/aether/exports/pay-test-script-chat-flow-v3.js`
- v4 output: `/home/jared/projects/AI-CIV/aether/exports/pay-test-script-chat-flow-v4.js`
- Witness contract memory: `.claude/memory/agent-learnings/collective-liaison/2026-02-24--witness-birth-pipeline-contract.md`
- Confirmed answers: `.claude/memory/agent-learnings/collective-liaison/2026-02-24--witness-api-contract-answers-confirmed.md`
