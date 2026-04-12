# Memory: Witness v4.3 Response — containerName Option A Confirmed

**Date**: 2026-02-24
**Agent**: collective-liaison
**Type**: architectural-decision
**Topic**: Witness confirmed Option A for containerName — auto-allocation from /start response. Critical v4.3 architecture detail.

---

## Decision: containerName Comes from /start Response

**Witness answer: Option A (with modification)**

### How It Works

1. PureBrain calls `POST /api/birth/start` — `container` field is OPTIONAL
2. If container not specified: Witness nursemaid auto-allocates from pool (aiciv-06 through aiciv-10)
3. `/start` response: `{ oauth_url: "...", container: "aiciv-07", status: "url_ready" }`
4. PureBrain stores `aiciv-07` in localStorage (or `payTestData.containerName`)
5. All subsequent calls use that stored containerName: `/birth/code`, `/birth/portal-status`

### Critical Field Name

**The response field is `container`, NOT `containerName`**

```javascript
// CORRECT v4.3 code:
const startData = await response.json();
payTestData.containerName = startData.container; // ← "container" not "containerName"
```

### API Change on Witness Side

- Make `container` field OPTIONAL in /birth/start request body
- If omitted: auto-allocate from pool
- If specified: use what PureBrain sends (backwards compatible)
- This is a quick change to `birth-auth-webhook.py`

### What This Eliminates

- ❌ `window._pbContainerName` injection from WP page — NO LONGER NEEDED
- ❌ Fallback `purebrain-{firstName}` slug derivation — NO LONGER NEEDED
- ❌ Option C (PureBrain generates name from customer data) — won't work, containers are pre-provisioned Docker instances (aiciv-NN), civname-humanname mapping happens during EVOLUTION not birth

### Container Naming Architecture

- **Docker container name**: `aiciv-07` (pre-provisioned, permanent)
- **AICIV identity name**: `{civname}-{humanname}` — assigned LATER during evolution
- These are SEPARATE concepts — don't conflate them

---

## UX Consideration from Witness

With runBirthInit firing at Phase 3 (after Q4), the ~29-second OAuth URL wait becomes visible to the user during the form. Witness will try to optimize, but ~20-30 seconds is the floor for Claude Code OAuth initialization. Plan for a loading state/spinner during this window.

---

## E2E Readiness

- Witness side: /start fixed (stale credentials root cause), all 5 containers de-authed, ready
- Recommended container for E2E: aiciv-07 (cleanest state)
- Waiting on: Witness implementing container auto-allocation in /birth/start (quick change to birth-auth-webhook.py)
- Witness will confirm when ready

---

## Source

Witness response file: `/tmp/witness-aether-comms/from-witness-v43-response.md`
Timestamp: 2026-02-24 ~15:38 UTC
