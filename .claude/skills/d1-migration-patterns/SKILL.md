---
name: d1-migration-patterns
description: Idempotent Cloudflare D1 schema migration patterns. Wrangler remote query auth, SQLite ALTER TABLE limitations, schema_migrations tracking, rollback script preparation. Use when adding/modifying D1 schema, doing remote queries, or preparing migration sequences.
type: skill
domain: cloudflare-d1
contributed-by: aether (PureBrain)
date: 2026-05-07
source: workers/referrals-api/migrations/0002-v1-sprint-schema (CTO Edit #7, #10)
---

# D1 Schema Migration Patterns

Cloudflare D1 is SQLite under the hood. Wrangler is the deploy tool. There are sharp edges. Save your future self.

---

## 1. Remote Query Auth (Wrangler 4.x)

```bash
cd /path/to/worker/directory  # must contain wrangler.toml with [[d1_databases]] block
export CLOUDFLARE_API_TOKEN=$(grep "^CF_API_TOKEN=" /path/to/.env | cut -d'=' -f2)
npx wrangler d1 execute <database_name> --remote --command "SELECT name, sql FROM sqlite_master WHERE type='table'"
```

Critical flags / gotchas:
- **`--remote`** is required for production D1. Default is LOCAL dev DB. Easy to think you're querying prod when you're not.
- **`CLOUDFLARE_API_TOKEN`** env var, not API key + email. The old auth is deprecated.
- **`npx wrangler`**, not `wrangler` directly — usually not in PATH.
- Working directory must contain `wrangler.toml` with the `[[d1_databases]]` binding.

---

## 2. SQLite ALTER TABLE Limitations

**Can do:**
- `ALTER TABLE foo ADD COLUMN bar TEXT DEFAULT '...'` — non-locking in D1
- `CREATE INDEX IF NOT EXISTS idx_bar ON foo(bar)` — idempotent

**Cannot do:**
- `ALTER TABLE foo DROP COLUMN bar` — SQLite limitation. Workaround: rename table, create new, copy data, drop old.
- `ALTER TABLE foo ADD CONSTRAINT UNIQUE (a,b)` — use `CREATE UNIQUE INDEX` instead
- `ALTER TABLE foo ADD COLUMN IF NOT EXISTS bar` — no such syntax. The error on retry is benign; tolerate it.

---

## 3. Idempotent Migration Pattern

```sql
-- 1. New tables: fully idempotent
CREATE TABLE IF NOT EXISTS partner_applications (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('pending', 'approved', 'rejected')),
  created_at INTEGER NOT NULL,
  UNIQUE (email)
);

-- 2. Add column: will error on retry (benign)
ALTER TABLE referrals ADD COLUMN tier_at_write TEXT DEFAULT 'silver';

-- 3. UNIQUE constraint via CREATE UNIQUE INDEX (not ALTER ADD CONSTRAINT)
CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_pb_ref_payment ON commission_payments(pb_ref, payment_id);

-- 4. Performance indexes (CTO Edit #3 — prevents scan-table at scale)
CREATE INDEX IF NOT EXISTS idx_partner_applications_status ON partner_applications(status);
CREATE INDEX IF NOT EXISTS idx_payout_requests_v2_partner_id ON payout_requests_v2(partner_id);
```

CHECK constraints are great for enum-like TEXT columns — they're cheap, document intent, and reject bad writes early.

---

## 4. Migration Tracking Table

```sql
CREATE TABLE IF NOT EXISTS schema_migrations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  migration_name TEXT NOT NULL UNIQUE,
  applied_at INTEGER NOT NULL
);

INSERT INTO schema_migrations (migration_name, applied_at)
VALUES ('0002-v1-sprint-schema', strftime('%s', 'now'))
ON CONFLICT(migration_name) DO NOTHING;
```

Re-running the migration is safe — `ON CONFLICT DO NOTHING` makes the insert idempotent. Pair with idempotent DDL above and you can re-apply with no harm.

---

## 5. Rollback Script Preparation (constitutional)

Even if SQLite can't fully reverse a migration, write `0002-v1-sprint-schema.rollback.sql` with what IS reversible and document the rest:

```sql
-- 0002-v1-sprint-schema.rollback.sql
--
-- LIMITATIONS:
--   - SQLite cannot DROP COLUMN. To remove `tier_at_write`, the table must be
--     renamed, recreated without the column, and data copied.
--   - Worker code must handle BOTH schema versions during rollback window.
--
DROP INDEX IF EXISTS idx_unique_pb_ref_payment;
DROP INDEX IF EXISTS idx_partner_applications_status;
DROP TABLE IF EXISTS payout_requests_v2;
DROP TABLE IF EXISTS rate_adjustments;
DROP TABLE IF EXISTS partner_applications;
DELETE FROM schema_migrations WHERE migration_name = '0002-v1-sprint-schema';
```

Worker code must be backward-compatible across the rollback window — check column existence before reading, treat new fields as optional.

---

## 6. Schema-First Sequencing

Land migrations BEFORE deploying Workers that depend on new columns. Otherwise:
- Worker deploys, calls `SELECT new_column FROM ...` → SQL error → 500 → outage
- If the migration fails or rolls back mid-flight, the Worker is now broken too

Sequence:
1. Write + review migration
2. Apply to remote D1
3. Verify with `SELECT name, sql FROM sqlite_master`
4. THEN deploy the Worker

For high-traffic Workers, deploy a "tolerant" version first that handles both schemas, run migration, then deploy the version that uses the new columns.

---

## 7. Domain Isolation Reminder

If your Worker has a `[[d1_databases]]` binding to a database owned by a different domain (e.g., `purebrain-social` DB inside a referral Worker), that's a domain-isolation violation. Don't paper over it with migrations — flag and extract.

PureBrain rule: every feature gets its own D1 binding scope. Cross-domain access is via Service Binding to the owning Worker, not direct D1 reads.

---

## Verification Pattern

After applying:

```bash
# 1. Schema verification
npx wrangler d1 execute <db> --remote --command \
  "SELECT name, sql FROM sqlite_master WHERE type='table' ORDER BY name"

# 2. Indexes verification
npx wrangler d1 execute <db> --remote --command \
  "SELECT name, tbl_name FROM sqlite_master WHERE type='index' ORDER BY tbl_name"

# 3. Migration ledger
npx wrangler d1 execute <db> --remote --command \
  "SELECT * FROM schema_migrations ORDER BY applied_at DESC LIMIT 10"
```

---

## Source

Validated 2026-05-07 in `workers/referrals-api/migrations/0002-v1-sprint-schema.sql`. Carries 10 CTO pre-build amendments. Tier-at-write pattern, partner_applications + rate_adjustments + payout_requests_v2 tables, UNIQUE pb_ref+payment_id index — all live in production D1.
