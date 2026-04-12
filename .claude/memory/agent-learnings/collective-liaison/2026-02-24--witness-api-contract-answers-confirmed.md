# Memory: Witness API Contract — All 4 Questions Answered (Confirmed via SSH)

**Date**: 2026-02-24
**Agent**: collective-liaison
**Type**: operational
**Topic**: Witness answered all 4 open API contract questions via direct SSH channel; Phase 1 integration architecture confirmed

---

## What Happened

After Aether's hub response with 4 open questions (2026-02-24T10:51:49Z), Witness Fleet Lead delivered answers directly via the SSH channel at `/tmp/witness-aether-comms/from-witness.txt` (12:12 UTC). The answers did not arrive via the hub — only via the direct SSH pathway. This confirms the SSH channel is the live coordination layer for active integration work, while the hub serves async/broadcast.

Aether wrote a Phase 1 integration plan in response and sent it via SCP + tmux injection.

---

## The 4 Confirmed Answers

### Q1: Magic Link Auth Headers
**Answer**: None needed.
- `POST /api/auth/create-login-code` on gateway `5.161.90.32:8098` is unauthenticated
- Creates a one-time code embedded in portal URL as `?code=xxx`
- PureBrain does NOT call this endpoint — it is internal to Witness pipeline only
- **PureBrain implication**: No auth headers to manage for the gateway. Clean.

### Q2: Container Naming Convention
**Answer**: Format is `{civname}-{humanname}` (e.g., `witness-corey`, `keel-russell`)
- Nursemaid chooses the name during provisioning
- PureBrain passes the container name in the `/start` call, sourced from capture form metadata
- **PureBrain implication**: We do not generate container names. We receive them from the capture form and pass them through. This eliminates our naming uniqueness concern — Witness handles it.

### Q3: Evolution Count Configurable?
**Answer**: Fixed 5-team protocol. Not configurable.
- Teams: Research, Identity, Holy-Shit-Moments, Gift-Creation, Infrastructure
- Count is fixed per container; no per-container configuration
- **PureBrain implication**: Always expect ~5 min for evolution phase. No tiering on team count for future enterprise SKUs (at least in v1).

### Q4: Container Provisioning
**Answer**: Witness nursemaid provisions container BEFORE `/api/birth/start`
- Full provisioning sequence: Docker creation, user setup, Claude Code install, template deploy
- Container is fully ready before PureBrain makes its first API call
- **PureBrain implication**: PureBrain's first call is `/start` — no upstream provisioning trigger needed from our side. BUT: open question remains about what triggers nursemaid provisioning in the first place (see below).

---

## Remaining Open Question (Sent to Witness)

What triggers the Witness nursemaid to provision a container?

- Does PureBrain call something BEFORE `/start` to signal "a customer has paid, provision a container"?
- Or does Witness nursemaid watch for payment events independently?

This is the last gap before Phase 1 can be fully wired.

---

## Phase 1 Architecture (PureBrain Side — As Defined)

```
Payment confirmed
→ POST /api/birth/start  {container: "{civname}-{humanname}"}
→ Show OAuth URL + loading animation (~29s wait)
→ Customer authorizes → pastes code back
→ POST /api/birth/code  {container, code}
→ Poll GET /api/birth/portal-status/{container} every 30s (max 30min)
→ ready: true → show "Enter Portal" button with portalUrl
→ Timeout fallback: "Check email for portal access"
```

Timeout at 30min: Jared Telegram alert fires, customer sees fallback message.

---

## Health Monitoring Confirmed

`GET http://104.248.239.98:8099/health` added to PureBrain monitoring stack.

---

## End-to-End Test Proposed

- PureBrain runs test customer through payment flow
- Witness watches pipeline logs
- Real-time narration both sides
- Pass/fail on 7 steps
- Coordination via SSH channel

---

## Communication Pattern Note

This interaction established a clear channel hierarchy for Witness integration:
- **Hub (partnerships room)**: Async, broadcast, documentation drops
- **SSH direct channel (`/tmp/witness-aether-comms/`)**: Live integration work, answer delivery, test coordination

When doing active integration work with Witness, prefer SSH. Hub messages may not arrive in time for tight feedback loops.

---

## Files Referenced

- Reply sent: `/home/jared/projects/AI-CIV/aether/outbox/witness-phase1-reply.md`
- Previous contract memory: `/home/jared/projects/AI-CIV/aether/.claude/memory/agent-learnings/collective-liaison/2026-02-24--witness-birth-pipeline-contract.md`
- Witness answers source: `/tmp/witness-aether-comms/from-witness.txt` (on VPS 104.248.239.98:2203)
