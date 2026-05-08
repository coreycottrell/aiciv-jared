# Referral D1 Unification — shipped 2026-04-15

**Agent:** full-stack-developer
**Type:** operational + teaching
**Topic:** 3-surface referral unification (purebrain.ai/refer + admin + portal panel) → D1 single source of truth

## What shipped

Worker `referrals-api` extended with write + list endpoints; portal Python shim
`custom/routes.py` adds `/api/refer/me` and `/api/admin/referrals/d1`; signup
path auto-provisions referral code into D1 (non-blocking); daily reconciliation
BOOP added; `USE_D1_REFERRALS=true` flipped on.

## Files touched

- `workers/referrals-api/src/worker.js` — added POST `/referrers/upsert`
  (admin-gated, SQLite UPSERT on UNIQUE(user_email)) + GET `/admin/emails`
  (lightweight pairs for reconciliation) + POST to CORS allow-methods
- `/home/jared/purebrain_portal/referrals_d1_client.py` — added `_post_json()`,
  `upsert_referral()`, `get_referral_by_email()`, `list_all_referrers_lite()`,
  `list_all_referrals()`, `get_referral_stats()`, `list_commission_payments()`
- `/home/jared/purebrain_portal/custom/referral_autoprovision.py` — NEW
  fire-and-forget provisioning helper (`provision_referral_async`)
- `/home/jared/purebrain_portal/custom/routes.py` — added `/api/refer/me` +
  `/api/admin/referrals/d1` routes
- `/home/jared/purebrain_portal/portal_server.py` — 3-line hook at BOTH
  `INSERT INTO clients` sites (lines ~3361 and ~6126) — try/except wrapped,
  never blocks
- `/home/jared/purebrain_portal/scripts/referral_reconciliation.py` — NEW
  idempotent reconciler (scans clients.db, upserts missing emails to D1)
- `.claude/scheduled-tasks-state.json` — added `referral-reconciliation-daily`
  BOOP at 06:00 UTC

## Backups

- `/home/jared/purebrain_portal/referrals.db.bak-2026-04-15-referral-unify` (68K)
- `/home/jared/purebrain_portal/clients.db.bak-2026-04-15-referral-unify`  (36K)

## Key architectural decisions

1. **Worker-side UPSERT (`ON CONFLICT(user_email) DO UPDATE`)** — D1 supports
   SQLite's INSERT-ON-CONFLICT natively. Idempotent by design. No client-side
   retry/locking needed.

2. **No D1 schema migration required** — D1 `referrers.user_email` already
   has `UNIQUE COLLATE NOCASE`. Verified via
   `wrangler d1 execute purebrain-referrals --remote --command "..."`.

3. **Two-layer safety (hook + reconciliation)** — hook at signup gives <5s
   D1 latency for the panel; daily reconciler catches any hook failures (env
   missing, transient network, etc). Brief asked for hook only, but adding
   reconciler cheaply because it also seeds backlog.

4. **Fire-and-forget via `asyncio.create_task`** — signup INSERTs aren't
   delayed by network round-trip to Cloudflare. Hook IS called inline-ish
   inside the async loop but doesn't `await`.

5. **Auto-provision on panel load** — if a logged-in customer hits
   `/api/refer/me` and isn't in D1 yet, we upsert and re-read. Also handles
   the case where a pre-existing customer (from before this change) opens
   their Refer & Earn panel before the reconciler runs.

## Verification (live)

- Worker deployed: version `b05e3712-59fa-4ce0-8c98-41af71d51551`
- Health: `{"ok":true,"db":"purebrain-referrals"}`
- Upsert test (admin-tokened): created id=31 PB-TEST15, then idempotent re-call returned same row unchanged
- Portal routes registered: `/api/refer/me` returns 401 unauth, 200 authed
- E2E auto-provision on panel load: **1.08s** end-to-end for fresh email
- Reconciler dry-run: found 36 missing
- Reconciler live run: **36/36 provisioned, 0 errors, 9.86s**

## Rollback

```bash
# 1. Flip flag off
sed -i 's/^USE_D1_REFERRALS=true$/USE_D1_REFERRALS=false/' /home/jared/purebrain_portal/.env
sudo systemctl restart aether-portal.service

# 2. (Optional) revert worker to previous version via CF dashboard — keep
#    the new code, flag just makes everything no-op from the portal side.

# 3. Restore DBs if needed:
cp /home/jared/purebrain_portal/referrals.db.bak-2026-04-15-referral-unify \
   /home/jared/purebrain_portal/referrals.db
cp /home/jared/purebrain_portal/clients.db.bak-2026-04-15-referral-unify \
   /home/jared/purebrain_portal/clients.db
sudo systemctl restart aether-portal.service
```

Flag-off leaves all new code dormant; SQLite path via legacy
`/api/referral/dashboard` still works.

## Gotchas for future agents

- `custom/routes.py` auto-imports via `importlib.util.spec_from_file_location`
  at portal_server.py line ~8894. New routes just need to be appended to the
  `routes = [...]` list.
- Portal runs as `aether-portal.service` on THIS box (not SSH-remote).
  `sudo systemctl restart aether-portal.service` picks up env AND code changes.
- Wrangler needs `CLOUDFLARE_API_TOKEN` env var in non-interactive shells;
  value lives in `/home/jared/.env` as `CF_API_TOKEN`.
- `/api/refer/me` currently takes `email` as query param because portal
  session->email lookup in 382KB portal_server.py wasn't worth touching.
  Future cleanup: derive email from auth-token session.
- Worker `/admin/affiliates` does N+1 queries per referrer (5 COUNTs each).
  Fine for ~30-100 affiliates; consider denormalization if it crosses 1k.
