# D1 Schema Migration Apply Receipt — 2026-05-07

**Status**: STOPPED at Step 1 (pre-check) — schema/database mismatch detected
**Migration**: `workers/referrals-api/migrations/0002-v1-sprint-schema.sql`
**Target D1**: `purebrain-referrals` (cdd9a522-f947-42a6-b9a3-c30534e02c3f)
**Operator**: PTT (full-stack-developer) under greenlit-execute authority
**Backup taken**: NO (halted before backup per STOP protocol)
**Migration applied**: NO

---

## STOP Condition Fired

Step 1 pre-check revealed: **the `clients` table does NOT exist in `purebrain-referrals` D1.**

The migration SQL contains 3 ALTER TABLE statements targeting `clients`:
- Line 80: `ALTER TABLE clients ADD COLUMN previous_monthly_amount REAL;`
- Line 81: `ALTER TABLE clients ADD COLUMN plan_changed_at INTEGER;`
- Line 84: `ALTER TABLE clients ADD COLUMN is_support_tier INTEGER DEFAULT 0;`

These will fail with `no such table: clients` because the `clients` table lives in a different D1 database.

---

## Evidence

### Tables present in `purebrain-referrals`
```
admin_tokens
affiliate_sessions
calculator_leads
_cf_KV
commission_payments       (target of migration)
commission_splits
login_attempts
password_reset_tokens
payout_requests
rate_limits
referral_clicks
referrals                 (target of migration)
referrers
rewards
sessions
sqlite_sequence
trio_messages
```
**No `clients` table.**

### Where `clients` actually lives
Cross-database scan:
- `purebrain-social` → **HAS `clients` table** (this is the onboarding/seed flow DB)
- `purebrain-creator-ai` → no
- `brainiac-platform` → no
- `pureapex-db` → no

### Pre-check command output
```
$ npx wrangler d1 execute purebrain-referrals --remote \
    --command "SELECT name FROM sqlite_master WHERE type='table' AND name='clients'"

🚣 Executed 1 command in 0.16ms
"results": []   ← empty, confirms clients table absent
```

---

## Diagnosis

The migration spec assumes `clients` lives in `purebrain-referrals`, but per current production state `clients` lives in `purebrain-social`. Three possibilities, in order of likelihood:

1. **Spec drift** — migration was authored against an outdated mental model where the referrals API owned its own `clients` table. The 3 ALTER TABLE clients lines were never validated against the actual target DB.

2. **Cross-DB design intent unrealized** — referrals API may need to read `clients` data, but D1 doesn't support cross-database queries. If clients data is needed inside referrals-api Worker, options are: (a) replicate clients table, (b) add a foreign-data fetch via Service Binding, (c) move clients to referrals DB.

3. **Wrong target DB** — Jared/CTO may have intended this migration to land on `purebrain-social`, where `clients` lives. But the migration ALSO touches `commission_payments`, `referrals`, and creates `partner_applications` / `rate_adjustments` / `payout_requests_v2` — those tables are referrals-domain, so split-DB application is required if so.

---

## Recommended Resolution Paths

**Option A — Split the migration** (cleanest)
- Carve the 3 `ALTER TABLE clients` statements + `is_support_tier` logic out into `0002a-clients-support-tier.sql` → apply against `purebrain-social`
- Keep `0002-v1-sprint-schema.sql` for `purebrain-referrals` (drop the 3 clients ALTERs)
- Update spec to document which DB each chunk targets

**Option B — Add `clients` table to `purebrain-referrals`**
- Pre-pend `CREATE TABLE clients (...)` to migration
- Requires sync mechanism so onboarding writes to BOTH DBs (or replicates)
- More moving parts; not recommended unless there's a strong reason

**Option C — Move `clients` table to `purebrain-referrals`**
- High-risk: would require migrating existing rows from `purebrain-social.clients` and updating every Worker that reads/writes `clients`
- NOT recommended

---

## Why This Stop Was Correct

Per the spec's idempotency comment (line 78): "If column already exists, this will error — acceptable for idempotent retry (error is benign)." That assumes the **table exists**. With table missing, error is NOT benign — it would mean partial migration: new tables created, then ALTER fails mid-script. SQLite executes statements sequentially and CF wrangler does NOT wrap in a transaction by default for `--file` mode. Halting now keeps the DB clean.

---

## What Did NOT Happen

- No D1 backup was created (would have been wasted; nothing was about to change)
- No CREATE TABLE statements ran
- No ALTER TABLE statements ran
- No data was modified
- `purebrain-referrals` D1 is in identical state to before this run
- `referral-v1` branch was NOT pushed (still local-only, per constraints)

---

## Next Action Required (Decision Owner: Jared + CTO)

Pick a resolution path (A / B / C above), update the migration SQL accordingly, then re-greenlit. PTT will re-run the apply sequence with backup-first once the DB-target alignment is fixed.

**Suggested**: Option A. I can draft the split (`0002a` for clients on `purebrain-social`, `0002` cleaned for `purebrain-referrals`) under a fresh greenlit if Jared confirms.

---

## Full Verification Commands Run

```bash
# Pre-check
export CLOUDFLARE_API_TOKEN=$(grep "^CF_API_TOKEN=" .env | cut -d'=' -f2)
npx wrangler d1 execute purebrain-referrals --remote \
    --command "SELECT name FROM sqlite_master WHERE type='table' AND name='clients'"
# → results: []  (HALT trigger)

# Confirmation: full table list of purebrain-referrals
npx wrangler d1 execute purebrain-referrals --remote \
    --command "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
# → 17 tables, no 'clients'

# Cross-DB hunt
for db in purebrain-social purebrain-creator-ai brainiac-platform pureapex-db; do
    npx wrangler d1 execute "$db" --remote \
        --command "SELECT name FROM sqlite_master WHERE type='table' AND name='clients'"
done
# → only purebrain-social returned a row
```

---

**Receipt timestamp**: 2026-05-07
**File path**: `/home/jared/projects/AI-CIV/aether/exports/portal-files/d1-schema-apply-receipt-2026-05-07.md`
