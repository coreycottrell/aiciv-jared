# Memory: Witness Birth Pipeline — Integration Audit vs Chatbox v3

**Date**: 2026-02-24
**Type**: operational + teaching
**Agent**: full-stack-developer
**Topic**: Audit of what Witness birth pipeline IS vs IS NOT wired into the post-payment chatbox on pages 688/689

---

## Audit Result: NOT YET WIRED

The Witness birth pipeline (POST /api/birth/start → OAuth URL → POST /api/birth/code → polling GET /api/birth/portal-status/{container}) is **NOT integrated into the chatbox code on pay-test-sandbox-2 (Page 688) or pay-test-2 (Page 689)**.

---

## What IS Built (v3 chatbox, deployed Feb 22)

### Portal button watcher: YES
`runPortalButtonWatcher()` exists and is wired in. It:
- Polls `POST https://api.purebrain.ai/api/portal-status` every 30 seconds (max 60 polls = 30 min)
- Uses email + aiName + orderId as the poll body (NOT container name)
- On `ready: true`: replaces `#ptc-portal-placeholder` div with a `<a class="ptc-portal-btn">` anchor
- Validates portalUrl is `https://` and hostname ends in `purebrain.ai`
- Fires in chat: "Your portal is ready. {aiName}'s Brain Stream is live — the button just appeared above."
- Runs CONCURRENTLY with `runLearnMoreLoop()` (setInterval, non-blocking)

### Trigger point: After "Learn more" button click inside `runThankYouMessage()`
Flow: runCompletion → click "{aiName} is ready → see next steps" → runThankYouMessage → user clicks "Learn more →" → runPortalButtonWatcher starts + runLearnMoreLoop starts concurrently

### What the portal watcher is NOT doing:
- It does NOT call `POST /api/birth/start`
- It does NOT display an OAuth URL to the customer
- It does NOT ask the customer to authorize on claude.ai
- It does NOT relay an auth code via `POST /api/birth/code`
- It polls `api.purebrain.ai/api/portal-status` (our own internal endpoint), NOT the Witness webhook at `104.248.239.98:8099/api/birth/portal-status/{container}`

---

## What Needs to Be Built

The full Witness integration requires two new phases in the chatbox:

### Phase A: Birth Start + OAuth URL Display (new, after questionnaire or at thankyou)
```
1. Call POST http://104.248.239.98:8099/api/birth/start
   Body: { "container": "{civname}-{humanname}" }
   (container name comes from capture form metadata)
2. Show OAuth URL to customer with loading animation (~29s wait)
   "Your AI is being born — click this link to authorize, then paste the code back here"
3. Show clickable link to claude.ai/authorize?...
4. Prompt customer to paste back the auth code
5. Call POST http://104.248.239.98:8099/api/birth/code
   Body: { "container": "{civname}-{humanname}", "code": "<auth_code>" }
```

### Phase B: Portal Status Polling Update
Switch `runPortalButtonWatcher` from polling `api.purebrain.ai/api/portal-status` (our stub) to polling `http://104.248.239.98:8099/api/birth/portal-status/{container}` (Witness live endpoint).

### Phase C: Container Name Plumbing
The chatbox needs to receive/know the container name (`{civname}-{humanname}`) from payment metadata. Currently payTestData has: email, aiName, orderId, name, role, company. Needs: containerName.

### Phase D: One Remaining Unknown
What triggers Witness nursemaid to provision the container before `/start`? This was an open question as of 2026-02-24 — needs answer from Witness before full integration can be wired.

---

## Current Poll Endpoint Mismatch

| What's coded | What Witness expects |
|---|---|
| `POST https://api.purebrain.ai/api/portal-status` | `GET http://104.248.239.98:8099/api/birth/portal-status/{container}` |
| Body: { email, aiName, orderId } | Path param: container name |
| Method: POST | Method: GET |

These are two different endpoints entirely. The current watcher would need to be updated.

---

## Key Files

- v3 chatbox source: `/home/jared/projects/AI-CIV/aether/exports/pay-test-script-chat-flow-v3.js`
- Deployed to: WordPress pages 688 (sandbox) and 689 (pay-test-2)
- Witness API contract: `.claude/memory/agent-learnings/collective-liaison/2026-02-24--witness-birth-pipeline-contract.md`
- Phase 1 integration plan: `exports/master-backup-2026-02-24/witness/witness-phase1-reply.md`
- The portal button watcher lives at line 1860 of the v3 source
- The trigger point (runThankYouMessage) is at line 1666, triggers watcher at line 1739
