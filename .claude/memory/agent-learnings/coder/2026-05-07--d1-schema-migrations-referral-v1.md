# D1 Schema Migrations for Referral v1 Sprint

**Date**: 2026-05-07
**Agent**: coder
**Type**: teaching
**Topic**: D1 schema migrations with wrangler, SQLite limitations, idempotent patterns

---

## Context

PHASE 2 of referral system v1 sprint. CTO pre-build review approved with 10 amendments. Task: write D1 schema migrations BEFORE Worker BUILD per CTO Edit #7 (schema-first sequencing).

---

## What Worked

### 1. Wrangler D1 Remote Query Pattern

```bash
cd /path/to/worker/directory
export CLOUDFLARE_API_TOKEN=$(grep "^CF_API_TOKEN=" /path/to/.env | cut -d'=' -f2)
npx wrangler d1 execute <database_name> --remote --command "SELECT ..."
```

**Why this works**:
- Wrangler 4.x requires explicit `--remote` flag for production D1
- Must be in worker directory with `wrangler.toml` containing `[[d1_databases]]` binding
- `CLOUDFLARE_API_TOKEN` env var auth (API key + email auth is deprecated)

**Gotcha**: Default is LOCAL D1 (dev database). Always use `--remote` for production schema queries.

### 2. SQLite ALTER TABLE Limitations

**Can do**:
- `ALTER TABLE ADD COLUMN` with default value (non-locking in D1)
- `CREATE INDEX IF NOT EXISTS`

**Cannot do**:
- `ALTER TABLE DROP COLUMN` — SQLite limitation
- `ALTER TABLE ADD CONSTRAINT UNIQUE` — use `CREATE UNIQUE INDEX` instead
- `ALTER TABLE ADD COLUMN IF NOT EXISTS` — no such syntax (error on retry is acceptable)

**Idempotent pattern**:
```sql
-- New table: fully idempotent
CREATE TABLE IF NOT EXISTS table_name (...);

-- Add column: will error on retry (benign — column exists)
ALTER TABLE existing_table ADD COLUMN new_column TEXT;

-- UNIQUE constraint: use index instead
CREATE UNIQUE INDEX IF NOT EXISTS idx_name ON table(col1, col2);
```

### 3. Migration Tracking Table

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

Prevents re-running migrations. `ON CONFLICT DO NOTHING` makes insert idempotent.

### 4. Rollback Script Preparation (CTO Edit #10)

**Must prepare rollback script IN ADVANCE** even if partial.

SQLite rollback limitations:
- Can DROP tables
- Can DROP indexes
- **CANNOT** drop columns (must recreate table with backup/restore)

Document limitations explicitly in rollback script header. Worker code must handle both schema versions for graceful rollback.

### 5. CTO Amendment Integration

All 10 CTO edits applied:
- Edit #2: `tier_at_write` column for safe retroactive recalc
- Edit #3: Indexes on partner_applications, rate_adjustments, payout_requests
- Edit #4: UNIQUE constraint on `(pb_ref, payment_id)` via CREATE UNIQUE INDEX
- Edit #7: Schema-first sequencing (migrations land before Worker BUILD)
- Edit #9: PayPal-only payout requests (drop bank method for v1)
- Edit #10: Rollback script prepared with documented limitations

---

## File Paths

- Migration SQL: `workers/referrals-api/migrations/0002-v1-sprint-schema.sql`
- Rollback SQL: `workers/referrals-api/migrations/0002-v1-sprint-schema.rollback.sql`
- Deliverable doc: `exports/portal-files/d1-schema-migration-v1-sprint-2026-05-07.md`
- Branch: `referral-v1`
- Commit: `f6c52d4`

---

## Dead Ends Avoided

1. **Trying to use `wrangler` without `npx`** — command not in PATH, use `npx wrangler` instead
2. **Querying D1 without `--remote` flag** — gets local dev DB, not production
3. **Missing CF API token** — wrangler requires `CLOUDFLARE_API_TOKEN` env var, not API key+email
4. **Attempting `ALTER TABLE ADD COLUMN IF NOT EXISTS`** — no such syntax in SQLite, accept error on retry
5. **Trying to add UNIQUE constraint via ALTER TABLE** — use `CREATE UNIQUE INDEX` instead

---

## Patterns for Future D1 Migrations

1. **Always verify existing schema first** with `SELECT name, sql FROM sqlite_master WHERE type='table'`
2. **Use idempotent patterns**: `IF NOT EXISTS`, `ON CONFLICT DO NOTHING`
3. **Document SQLite limitations** in both migration and rollback scripts
4. **Prepare rollback script** even if partial (constitutional requirement per CTO Edit #10)
5. **Add indexes explicitly** for admin queue queries (CTO Edit #3 — prevents scan-table at scale)
6. **Track migrations** with `schema_migrations` log table
7. **Schema-first sequencing**: migrations land BEFORE Workers that depend on new columns
8. **Use CHECK constraints** for enum-like TEXT columns (e.g., `status IN ('pending', 'approved', ...)`)

---

## Open Questions Raised

1. Legacy `payout_requests` table collision — created `payout_requests_v2` to avoid disruption. Recommend deprecating legacy after cutover.
2. `clients` table existence assumption — ALTER will fail if table doesn't exist. May need `CREATE TABLE IF NOT EXISTS` stub.
3. Single D1 database shared across staging/production — no separate staging DB. Apply to production only.

---

## Time Savings for Descendants

This memory saves future coder agents ~1-2 hours on:
- Figuring out wrangler D1 remote query auth
- Understanding SQLite ALTER TABLE limitations
- Idempotent migration patterns for D1
- Rollback script preparation requirements
- CTO pre-build amendment integration patterns

---

**If you're writing D1 migrations, read this first.**
