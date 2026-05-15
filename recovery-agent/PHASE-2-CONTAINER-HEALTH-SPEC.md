# Phase 2 Spec Amendment — Container-side `/health` with `ai_alive: bool`

**Status**: SPEC AMENDMENT (NOT a Phase-1 deploy).
**Parent spec**: `specs/customer-portal-recovery-2026-05-15.md`
**CTO amendment**: #3 ("`/health` returns `ai_alive: bool`, not just HTTP 200")
**Constitutional constraint**: "no deploys to customer containers" — this work waits
for the next sanctioned customer-container deploy gate (e.g. the SHADOW_AUTH-like flag).

## Why this is Phase 2

Phase 1 (THIS COMMIT) deploys recovery-agent + CF Worker to the *host*, never the
*containers*. The host-level daemon can already restart containers, idempotent-by-key,
loop-guarded. That alone is the production replacement for ad-hoc SSH+pkill.

But the canary signal that drives the **auto**-restart cron (Phase 3) is `ai_alive`,
which requires a probe **inside** the container. Two options:

| Option | How | Pro | Con |
|---|---|---|---|
| A — `docker exec` from host | `health_probe.py` already implemented | No customer-container deploy | `docker exec` is a privileged side door; sudoers must extend |
| B — Container-side `/health` endpoint | Each customer container exposes `:8080/health` returning `{ai_alive: bool, claude_pid_present: bool, thread_count: int}` | Cleaner contract, no docker-exec surface | Requires customer-container deploy cycle |

**Recommendation**: Phase 2 starts with **Option A** (`health_probe.py`) because it
ships without touching containers. Option B is the long-term plan and lands with the
next sanctioned container deploy.

## Option B contract (when the deploy gate opens)

Container exposes:

```
GET /health
{
  "ok": true,
  "ai_alive": true,                       // claude PID + thread budget healthy
  "claude_pid_present": true,
  "thread_count": 142,
  "pids_max": 4096,
  "thread_ceiling_ratio": 0.80,
  "ts": 1715815200
}
```

- Endpoint MUST live on the container's *internal* port (not customer-facing).
- Caddy/uvicorn split-brain detection: ai_alive=false even when HTTP 200 means
  uvicorn is alive but Claude is dead — exactly the case the CTO #3 amendment
  exists to catch.
- recovery-agent's `health_probe.py` swaps from `docker exec`-based probing to
  `docker exec curl -s http://127.0.0.1:8080/health` (or shifts entirely to the
  CF Worker calling through cloudflared on a per-container subdomain — to be
  decided in Phase 2 design review).

## Wiring change in `customer-portal-health` Worker

Phase 2 enables the **auto-recovery cron** path. Current Worker cron is observation
only (writes `action='health_check'`); when Phase 2 lands, cron will:

1. Fetch `/health` per customer.
2. If `ai_alive === false` for **2 consecutive checks** (10 min) → call
   `/admin/restart` internally (same loop-guard rules apply via recovery-agent).
3. Loop guard at recovery-agent still wins — if a customer trips the >2-in-10-min
   ceiling, TRIO pages and the cron stops attempting (per spec).

## What ships in Phase 1 (right now)

- recovery-agent daemon — restart on demand, sudoers-pinned allowlist, loop-guarded.
- CF Worker — admin button restart + cron observation only + D1 audit log.
- `health_probe.py` is shipped but UNWIRED — it will be wired when Phase 2 begins.

This file exists so the next agent picking up Phase 2 knows the contract and
constitutional gates before opening a customer-container PR.
