# Customer-Portal Recovery — Phase 1 Build

**Date**: 2026-05-15
**Type**: pattern + operational
**Branch**: `feat/customer-portal-recovery-2026-05-15`
**Spec**: `specs/customer-portal-recovery-2026-05-15.md` (Jared greenlight 22:40 UTC)
**CTO review**: `specs/cto-review-4-specs-2026-05-15.md` — verdict AMEND, 7 amendments

## Pattern: HMAC-gated host daemon pair (sister to disk-telemetry)

This is the **second** instance of the same architectural pattern in 24 hours:

| Aspect | disk-telemetry (sister sprint) | customer-portal-recovery (this build) |
|---|---|---|
| Host daemon | telemetry collector (write-only, push) | recovery-agent (HTTP server, pull) |
| Auth | HMAC(body+nonce+ts) | Same shape — same module pattern lifted |
| CF Worker | disk-telemetry-ingest | customer-portal-health |
| D1 | `disk-telemetry` | `portal-recovery` |
| Migration # | 0010 | 0011 |
| Localhost-bind | n/a (outbound only) | 127.0.0.1:9877 (CTO #5) |
| Ingress | direct HTTPS to CF | Cloudflare Tunnel (CTO #2) |

**Lesson**: when you have a working canonical (disk-telemetry-ingest worker.js
HMAC code), DON'T copy-paste — re-implement in matching style with same
constants so the next agent can grep one file to understand both. I kept the
exact `verifyHmac` / `rememberNonce` / `hmacHex` shapes byte-similar.

## Lesson: stdlib-only Python on customer-portal hosts

I chose `http.server` + `socketserver` + threading over FastAPI/uvicorn because
this daemon runs on **customer-portal hosts** — every extra pip dep is a supply
chain attack surface on Jared's customers. `pip install fastapi` was tempting
for 5 minutes of dev time; refusing it cost me 30 minutes and saved Pure
Technology from "uvicorn CVE rolls onto every Hetzner box".

## Lesson: sudoers > docker-group (CTO #1)

Docker-group membership = "I am root on this host" in disguise. CTO was right
to push back. The sudoers entry per container name is uglier (regenerate file
on each customer addition) but the blast radius is exactly the container
allowlist. `visudo -c` on the file parsed OK locally.

## Lesson: loop detection has an off-by-one

Spec says "if recovery-agent restarts same container >2 times in 10 min".
"More than 2" means the 3rd is allowed, the 4th is blocked. Initial test had
the 3rd restart blocked. Fix: condition is `len(hist) > LOOP_MAX_RESTARTS`
where `LOOP_MAX_RESTARTS = 2` — at 3 restarts in window, len==3, 3>2 → block.
Test `test_loop_detection_blocks_after_max` asserts this exact boundary.

## Files

| File | Purpose |
|---|---|
| `workers/_shared-migrations/0011-customer-portal-recovery-2026-05-15.sql` | D1 schema |
| `workers/_shared-migrations/0011-customer-portal-recovery-2026-05-15-rollback.sql` | rollback |
| `recovery-agent/recovery_agent.py` | Host daemon (stdlib only) |
| `recovery-agent/health_probe.py` | docker-exec ai_alive probe (UNWIRED Phase 2) |
| `recovery-agent/systemd/recovery-agent.{service,sudoers}` | systemd + sudoers |
| `recovery-agent/systemd/cloudflared-config.yml` | Tunnel config template |
| `recovery-agent/config/allowlist.txt.example` | container allowlist template |
| `recovery-agent/tests/test_recovery_agent.py` | 11 tests, all pass |
| `workers/customer-portal-health/src/worker.js` | CF Worker |
| `workers/customer-portal-health/test/worker.test.js` | 9 tests, all pass |
| `workers/customer-portal-health/wrangler.toml` | D1 binding + cron */5 |
| `recovery-agent/PHASE-2-CONTAINER-HEALTH-SPEC.md` | container-side /health (deferred) |

## Tests
- recovery-agent: **11/11 pass** (unittest)
- customer-portal-health: **9/9 pass** (node:test)
- D1 migration roundtrip: forward + rollback verified, CHECK constraints fire
- sudoers: `visudo -c` parsed OK

## Phase 1 deploy plan (Aether executes)

1. `wrangler d1 create portal-recovery` → substitute real ID into wrangler.toml + commit
2. `wrangler d1 execute portal-recovery --remote --file=workers/_shared-migrations/0011-customer-portal-recovery-2026-05-15.sql`
3. `wrangler secret put RECOVERY_AGENT_HMAC_KEY ADMIN_TOKEN RECOVERY_AGENT_TUNNEL_URL` (for customer-portal-health worker)
4. `cd workers/customer-portal-health && wrangler deploy` (git tree must be clean — constitutional)
5. On purebrain-3 (46.62.187.74): rsync `recovery-agent/` → `/opt/recovery-agent/`, install sudoers, systemd, /etc/recovery-agent/{allowlist.txt,recovery-agent.env}, then `cloudflared tunnel route dns`
6. Test from admin button: POST /admin/restart with customer_slug=whitehurst → 7-day clean run watch
