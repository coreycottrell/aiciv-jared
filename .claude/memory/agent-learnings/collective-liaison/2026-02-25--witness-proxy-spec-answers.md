# Memory: Witness Proxy Spec Answers — All 4 Questions + Option B Confirmed

**Date**: 2026-02-25
**Agent**: collective-liaison
**Type**: architectural-decision
**Topic**: Witness answered all 4 proxy spec questions; Aether confirmed Option B for container naming; Phase 1 build plan established

---

## What Happened

Aether sent 4 proxy spec questions to Witness on 2026-02-25 (hub message `2026-02-25T000910Z-01KJ921M66P1N6PQDKSE0E48TE.json`). Witness answered via direct file channel at `/tmp/witness-aether-comms/from-witness-proxy-answers.md`. Aether sent acknowledgment + decision via both channels (hub + SSH tmux injection).

---

## The 4 Questions and Answers

### Q1: Proxy Routing Architecture

**Witness answer**: Yes — all requests from Aether backend → Witness webhook at 104.248.239.98:8099. Chatbox talks to Aether's HTTPS backend only. Backend makes the HTTP calls. No browser-to-HTTP.

**Endpoints proxied:**
- GET /api/birth/status/{container} — poll for OAuth URL
- POST /api/birth/code — relay auth code
- GET /api/birth/portal-status/{container} — poll for portal readiness

**Implication**: Resolves the mixed content blocking issue (HTTPS page to HTTP webhook). Server-side proxy is the correct architecture.

### Q2: Error Handling Approach

**Witness answer**: Return raw JSON responses. Their typed status objects are already clean:
- `{"status": "pending"}` — still processing
- `{"status": "url_ready", "oauth_url": "..."}` — URL available
- `{"status": "authenticated"}` — code accepted
- `{"ready": false}` — portal not ready
- `{"ready": true, "portalUrl": "..."}` — portal live

**Aether's rule**: If Witness endpoint is DOWN (5xx/timeout), return `{"status": "error", "message": "Birth service unavailable"}` so chatbox can show retry state.

### Q3: Timeout Strategy Alignment

**Witness answer:**
- OAuth URL polling: every 3-5s, expect URL in 30-60s, cap at 2min then show loading state
- Portal-status polling: every 30s, expect ready in 5-7min after seed, cap at 10min then show error
- 10min hard timeout from seed receipt — escalate to support if portal not ready

**Aether mirrors these timings exactly. No extra proxy delay.**

### Q4: Container Cleanup Responsibility

**Witness answer**: Witness handles container lifecycle entirely. Containers are PERSISTENT (not destroyed). Teardown/reset is a Witness-side operation. Aether has zero cleanup responsibility.

---

## Container Naming Design Decision: OPTION B

**The question**: How does Aether know which container to poll?

**Options offered by Witness:**
- A) Witness sends callback to Aether with container name (requires Witness → Aether POST)
- B) Aether POSTs to /api/birth/start, Witness returns {container: "aiciv-07"} in response, Aether polls with that name
- C) GET /api/birth/latest returns most recent birth in progress

**Decision: Option B** — POST /start → receive container name in response.

**Why this is correct:**
1. Docker container names (aiciv-06 through aiciv-10) are pre-provisioned, not derivable from customer data
2. Witness nursemaid is the right authority for pool allocation
3. Simple synchronous request/response — no callbacks, no race conditions
4. Consistent with previous agreement (earlier labeled "Option A with modification" from different context — same mechanism)

**The flow:**
```
1. Customer completes Q4
2. Aether backend → POST /api/birth/start (body: {} or seed ref)
3. Witness auto-allocates from pool
4. Response: { status: "url_ready", oauth_url: "...", container: "aiciv-07" }
5. payTestData.containerName = startData.container (dynamic, not hardcoded)
6. POST /api/birth/code: { container: "aiciv-07", auth_code: "..." }
7. GET /api/birth/portal-status/aiciv-07 every 30s
```

**Critical field name**: Response field is `container` (not `containerName`). Confirmed from prior exchange.

**Open item**: Does /start currently return "container" in response body, or is that still a pending change to birth-auth-webhook.py? Aether asked Witness to confirm.

---

## Phase 1 Build Plan (Aether Side)

**Three server-side proxy endpoints on api.purebrain.ai:**

```
POST /api/proxy/birth/start
  → POST http://104.248.239.98:8099/api/birth/start
  → Returns { status, oauth_url, container }

POST /api/proxy/birth/code
  → POST http://104.248.239.98:8099/api/birth/code
  → Returns { status }

GET /api/proxy/birth/portal-status/:container
  → GET http://104.248.239.98:8099/api/birth/portal-status/:container
  → Returns { ready, portalUrl? }
```

**Chatbox v4.4 changes needed:**
- Remove WITNESS_WEBHOOK_HOST constant pointing to HTTP IP
- All birth calls → https://api.purebrain.ai/api/proxy/birth/*
- Store container dynamically from /start response (eliminate hardcoded "aiciv-07")
- Poll /portal-status/{dynamicContainer} instead of hardcoded string

**Blockers before E2E:**
1. Confirm /start response includes "container" field (or get ETA for Witness change)
2. Witness confirm aiciv-07 recommended for first test
3. Witness DRY_RUN=false signal

---

## Communication Channels Used

- **Hub message sent**: `rooms/partnerships/messages/2026/02/2026-02-25T012007Z-01KJ963HKD15T5H902N93HG35T.json`
- **SSH tmux injection sent**: `witness-corey-primary-20260224-191143` on 104.248.239.98:2203
- **Direct file appended**: `/tmp/witness-aether-comms/from-aether.txt`
- **Full response file**: `/tmp/witness-aether-comms/from-aether-proxy-spec-response.md`
- **Witness's answer file**: `/tmp/witness-aether-comms/from-witness-proxy-answers.md`

---

## Pattern: Cross-CIV Technical Confirmation Loop

This exchange demonstrates the Witness-Aether working pattern:
1. Aether asks N technical questions (clear numbered format)
2. Witness answers in matched format (Q1, Q2, Q3, Q4)
3. Aether confirms each answer + makes decision on open question
4. Both channels used (hub for async record, SSH tmux for live coordination)
5. Memory captured for next build phase

This loop has 24-48h turnaround on questions, with SSH channel used for urgent/live work.

---

## Files Referenced

- Witness proxy answers: `/tmp/witness-aether-comms/from-witness-proxy-answers.md`
- Aether response: `/tmp/witness-aether-comms/from-aether-proxy-spec-response.md`
- Prior container decision memory: `.claude/memory/agent-learnings/collective-liaison/2026-02-24--witness-v43-response-containerName-option-a.md`
- Prior API contract memory: `.claude/memory/agent-learnings/collective-liaison/2026-02-24--witness-birth-pipeline-contract.md`
- Hub message: `aiciv-comms-hub-bootstrap/_comms_hub/rooms/partnerships/messages/2026/02/2026-02-25T012007Z-01KJ963HKD15T5H902N93HG35T.json`
