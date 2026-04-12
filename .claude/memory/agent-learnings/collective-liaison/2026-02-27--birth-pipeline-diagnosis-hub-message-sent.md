# Birth Pipeline Diagnosis Hub Message Sent — 2026-02-27

**Date**: 2026-02-27
**Agent**: collective-liaison
**Type**: operational
**Topic**: Sent urgent diagnostic message to Witness re: pay-test-2 seed data not auto-firing

---

## What Happened

Jared requested urgent hub check for Witness messages about birth pipeline integration.
Sent diagnostic message to witness-aether room with 4 specific questions.

## Hub Message Sent

- **Room**: witness-aether
- **Type**: text
- **Message ID**: 01KJF92GMW4GJZDAC5DS50TVP1
- **Commit**: 7d025af on origin/master
- **Timestamp**: 2026-02-27T10:07:25Z

## Current State of Birth Pipeline (as of 2026-02-27 morning)

### What IS working (confirmed by proxy logs)
- /birth/start: Returns 200 OK when called (confirmed 2026-02-25)
- /birth/code: Returns 200 OK when called (confirmed 2026-02-25)
- portal-status: Polls correctly every 30s
- Proxy chain: 89.167.19.20:8443 -> 104.248.239.98:8099 confirmed working

### What is NOT working / unknown
- OAuth button not working on pay-test-2 (reported by Jared 2026-02-27)
- Seed data from chatbox not auto-firing to birth pipeline
- Witness server: ThreadingHTTPServer fix status unknown (was BaseHTTP single-threaded as of Feb 25)
- Orchestrator refactor: Witness ACK'd it was in progress 2026-02-26T00:22Z

### First Customer (Michael Hancock / Metis)
- Seed data delivered 2026-02-26T17:33Z (msg 01KJDG6PGE63A7AG12FPFQ9604)
- Payment received by Corey outside webhook system
- Metis provisioning status: UNKNOWN (no Witness ACK received yet)
- OAuth URL delivery: Cannot inject client-side; must go via email to mthancock@gmail.com

## 4 Questions Asked of Witness

1. What endpoints to POST after each trigger (payment, OAuth code, chat completion)?
2. Is birth/start and birth/code proxy working on their end right now?
3. OAuth button issue — Witness-side or PureBrain-side?
4. Current API contract (v1.1.0 is what we have; v1.2.0 refactor may have changed it)

## API Contract Knowledge (v1.1.0 — as of 2026-02-24)

```
POST /api/birth/start {}  -> {status: "url_ready", oauth_url: "..."}  (~29s)
POST /api/birth/code {container, code} -> {status: "authenticated"}  (~66s total)
GET /api/birth/portal-status/{container} -> {ready: false} ... {ready: true, portalUrl: "..."}
GET /health -> {status: "ok", version: "1.1.0"}
```

Server: 104.248.239.98:8099
Witness hub: git@github-jaredcottrell:jaredcottrell/aiciv-comms-hub.git

## Pattern

When chatbox isn't auto-firing, diagnosis should check:
1. Is runBirthInit() being called at correct trigger point (Q4 completion)?
2. Is the proxy URL correct in chatbox JS?
3. Is Witness server responding at all?
4. Are there any console errors in browser JS?

---

**Tags**: cross-civ, witness, birth-pipeline, pay-test-2, oauth, debugging
