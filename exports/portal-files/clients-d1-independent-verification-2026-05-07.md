# Clients D1 — Independent Verification

**Date**: 2026-05-07
**Verifier**: WTT (full-stack-developer, fresh evidence, read-only)
**Trigger**: Jared questioned ptt-fullstack claim; Chy reportedly said clients was on its own setup separate from social

---

## 1. Wrangler D1 List (raw, abridged)

12 D1 databases on the CF account. Names (no standalone "purebrain-clients" or "clients-db" exists):

```
ce-sme-db, hancock-law-staging, ara-index, brainiac-platform,
face-platform-staging, voice-platform-staging, purebrain-social-staging,
pureapex-staging-db, purebrain-social, purebrain-referrals,
pureapex-db, purebrain-creator-ai
```

Full list captured in this session (uuids + sizes verified via `npx wrangler d1 list`).

## 2. Per-DB `clients` Table Presence (re-queried fresh)

| Database | `clients` table? | Row count | Notes |
|---|---|---|---|
| **purebrain-social** | YES | **64** | PROD — 19 cols incl email, ai_name, magic_link, payment_status, paypal_subscription_id |
| purebrain-social-staging | YES | 0 | Staging mirror, 18 cols (no magic_link col) |
| hancock-law-staging | YES | 6 | UNRELATED — customer-facing schema (firm_id, contact_name) — Hancock Law tenant data |
| **purebrain-referrals** | **NO** | n/a | Confirmed: `SELECT name FROM sqlite_master WHERE name='clients'` returns empty |
| ce-sme-db, ara-index, brainiac-platform, face-platform-staging, voice-platform-staging, pureapex-staging-db, pureapex-db, purebrain-creator-ai | NO | n/a | None have a clients table |

ptt-fullstack's claim "`clients` is in `purebrain-social`, not `purebrain-referrals`" is **factually correct**.

## 3. portal.purebrain.ai/admin/clients Trace

Routing chain (verified by reading source):

1. `purebrain-portal-proxy` worker (`workers/purebrain-portal-proxy/src/worker.js:206-217`) catches `*.purebrain.ai/*` and forwards `/api/admin/clients*` → `social-api.in0v8.workers.dev`
2. **`social-api` worker** (`workers/social-api/src/worker.js:6201` handles GET `/api/admin/clients`) — wrangler.toml binds `DB` → `purebrain-social` (uuid `625dde70-0a60-45e7-bf81-e18e5ac4d854`)
3. **`admin-api` worker** also serves the same routes (`workers/admin-api/src/worker.js:378`) — wrangler.toml binds `DB` → `purebrain-social` (same uuid). Both workers point at the same D1.
4. HTML at `exports/cf-pages-deploy/admin/clients/index.html` is served via CF Pages.

LEGACY path still on disk: `/home/jared/purebrain_portal/portal_server.py` has its own local SQLite `/home/jared/purebrain_portal/clients.db` (40KB, mtime 2026-05-07 15:46) and `/admin/clients` Flask routes (lines 5766-6143). The portal proxy (line 149) routes `/admin/clients*` away from this Python service to CF Pages + Workers. The local SQLite is not the live source for portal.purebrain.ai admin UI.

## 4. Architecture Intent vs Reality (DRIFT FOUND)

**Recorded intent** (`.claude/memory/agent-learnings/ptt-fullstack/2026-04-20--admin-clients-recovery-strategy.md` line 33):
> "Migrate to D1 (purebrain-clients OR add clients table to purebrain-referrals)."

**Reality**: Neither option was taken. Clients landed in **`purebrain-social`** D1 instead. Confirmed by:
- `2026-04-21--paypal-webhook-cf-worker.md`: "Upserts/updates the `clients` table in `purebrain-social` D1"
- `2026-04-30--agentmail-webhook-worker-build.md`: "PayPal email looked up from D1 clients table" (in social DB)
- `2026-05-05--api-check-name-endpoint-missing.md`: "admin-api worker has D1 binding to `purebrain-social` db with `clients` table containing `ai_name` column"

**Chy's reported architectural intent** (per Jared): clients on its own separate setup that does NOT touch social. **This intent was NOT implemented.** The clients table was co-located with social tables in `purebrain-social` D1, presumably for transactional convenience with social/PayPal flows.

No standalone `purebrain-clients` D1 exists. No clients table exists in `purebrain-referrals`.

## 5. Verdict

**Where `clients` ACTUALLY lives**: `purebrain-social` D1 (uuid `625dde70-8a66-4c97-a5f8-e310402a8c15` — PROD), 64 rows, 19 columns. Bound to BOTH `social-api` and `admin-api` workers. This is the live source for portal.purebrain.ai/admin/clients.

**Does this match Chy's stated architecture?** **NO.** Drift documented. Chy reportedly intended a separate setup; reality co-located clients in `purebrain-social`. ptt-fullstack's halt of the migration is justified BUT the deeper question is whether to (a) accept the drift and proceed, or (b) extract clients into a standalone `purebrain-clients` D1 to match original intent.

**Recommendation**: Do not modify `purebrain-social` until Jared + Chy align on whether to ratify drift or refactor to separate DB. ptt-fullstack's halt was the correct call.

**Conflict flag**: Architectural intent (Chy) conflicts with implementation reality. Both prior `clients.db` SQLite (legacy, on portal server) and current `purebrain-social.clients` (live D1) violate the "separate setup" mandate.
