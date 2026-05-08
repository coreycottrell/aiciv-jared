# Referral Unification Brief — 3 surfaces → D1

**Date:** 2026-04-15
**Trigger:** ST# executive brief (Jared greenlit for full-stack-developer to execute)

## Architecture Target

- `purebrain.ai/refer/` (public) → D1 `purebrain-referrals` (db_id `cdd9a522-f947-42a6-b9a3-c30534e02c3f`) ✅ already migrated
- Admin dashboard (portal) → needs to point at D1
- Portal "Refer & Earn" panel → needs to point at D1 + auto-provision code on load
- Customer signup hook → auto-provision referral code in D1 (non-blocking)

## Corrected File Paths (from Aether's verification)

**Real databases:**
- `/home/jared/purebrain_portal/referrals.db` (68K — active referral data, SQLite fallback)
- `/home/jared/purebrain_portal/clients.db` (36K — active customer data)
- `portal.db` is an empty stub — IGNORE IT

**Backup targets (before any writes):**
```
cp /home/jared/purebrain_portal/referrals.db /home/jared/purebrain_portal/referrals.db.bak-2026-04-15-referral-unify
cp /home/jared/purebrain_portal/clients.db  /home/jared/purebrain_portal/clients.db.bak-2026-04-15-referral-unify
```

**Code paths:**
- D1 client: `/home/jared/purebrain_portal/referrals_d1_client.py` (already exists, may need methods added)
- Route shim: `/home/jared/purebrain_portal/custom/routes.py` (USE THIS — do not edit the 382KB portal_server.py directly)
- Worker: `/home/jared/projects/AI-CIV/aether/workers/referrals-api/src/worker.js`

## Tasks

### 1A — Admin dashboard → D1 (feature-flagged)
Gate admin referral read with `USE_D1_REFERRALS` env flag. When true, use `referrals_d1_client.py` methods. When false, fall back to `referrals.db` SQLite (read-only rollback safety).

### 1B — Portal Refer & Earn → D1 with auto-provision
On panel load:
1. Look up referral by logged-in customer email
2. If missing, upsert a new code (`generate_referral_code(email)`, `tier='starter'`)
3. Render panel with their code + stats + URL `purebrain.ai/refer/?code={code}`

### 1C — Auto-provision on customer creation
Hook into customer signup (where rows hit `clients.db customers`). After commit:
- Call `upsert_referral(email, code, tier='starter')`
- Wrap in try/except — NEVER block signup on D1 failure
- Log failures for reconciliation

### 1D — Daily reconciliation
Script `/home/jared/purebrain_portal/scripts/referral_reconciliation.py`:
- Iterate all `clients.db customers` emails
- For each missing in D1, provision
- Log drift count to `/home/jared/purebrain_portal/logs/referral_reconciliation.log`
- Add BOOP at 06:00 UTC daily

## Constraints

- D1 is source of truth; SQLite read-only fallback behind flag
- Wrangler ALLOWED for workers (`cd workers/referrals-api && wrangler deploy`); BANNED for Pages
- VPS portal deploy via SSH + `systemctl restart purebrain-portal`
- D1 `referrals` table MUST have UNIQUE(email) — add migration if missing
- Idempotent upserts (no duplicate codes per email)
- Auto-provision NEVER blocks signup
- Verification: live test customer `reftest-20260415@example.com` — signup → D1 row in <5s → admin + panel both render

## Deliverables

1. Backup paths + sizes (referrals.db + clients.db)
2. File diffs (referrals_d1_client.py, custom/routes.py, signup handler, reconciliation script)
3. Any D1 migration SQL run
4. Test customer E2E proof (D1 row ID, admin view confirmation, panel confirmation)
5. Deploy log (portal restart + worker deploy output)
6. Rollback command (flag off + restart)

## Execute Authority

Jared greenlit this. Execute all 4 tasks. If blocked on a SPECIFIC decision (schema breaking change, data delete), punt with detail. Otherwise: proceed, backup, ship, prove.
