# D1 Schema Migration STOP — `clients` Table Lives in Wrong DB

**Date**: 2026-05-07
**Type**: gotcha / operational
**Domain**: D1 schema migrations, multi-DB architecture
**Outcome**: STOP fired correctly at Step 1 pre-check; production DB untouched

## What happened

Greenlit-execute task: apply `workers/referrals-api/migrations/0002-v1-sprint-schema.sql` to `purebrain-referrals` D1 with backup-first protocol. Step 1 pre-check (existence of `clients` table) returned empty, halting execution before any backup or DDL was issued.

## Root cause

Migration SQL contains 3 `ALTER TABLE clients` statements (lines 80, 81, 84), but `clients` table lives in `purebrain-social` D1 — NOT `purebrain-referrals`. Spec was authored without validating against current production DB layout.

## Verified table locations (2026-05-07)

| Table | Lives in | Notes |
|-------|----------|-------|
| `clients` | `purebrain-social` | onboarding/seed flow DB |
| `referrals` | `purebrain-referrals` | partner attribution |
| `commission_payments` | `purebrain-referrals` | payout audit |
| `referrers` | `purebrain-referrals` | partner registry |

D1 does NOT support cross-database joins. Migrations that touch tables in 2 DBs MUST be split into 2 files, applied separately.

## Pattern: pre-check ALL referenced tables before any migration

When a migration SQL references multiple tables, run an existence check for **every** unique table name **before** taking backup. The cost is ~5 seconds. Avoids:

- Wasted backup on a DB that won't be modified
- Partial-application states (CREATE TABLE succeeds, then ALTER fails mid-file)
- Wrangler `--file` mode does NOT auto-wrap in a transaction; failed ALTERs leave new tables behind

```bash
# Extract all referenced tables, then loop:
grep -oE 'ALTER TABLE \w+|CREATE TABLE (IF NOT EXISTS )?\w+' migration.sql \
  | awk '{print $NF}' | sort -u | while read tbl; do
    npx wrangler d1 execute $TARGET --remote \
      --command "SELECT name FROM sqlite_master WHERE type='table' AND name='$tbl'"
done
```

## Wrangler ban does NOT apply to D1

Constitutional `feedback_wrangler_banned_cf_deploy_only.md` bans `wrangler pages deploy` (deletes pages). `wrangler d1 execute` is REQUIRED and remains the canonical D1 tooling. Don't second-guess this — `cf-deploy.py` is for Pages only.

## CF API token env var deprecation warning

`CF_API_TOKEN` env var still works but wrangler 4.89 logs deprecation: "Please use CLOUDFLARE_API_KEY instead." Keep using `CF_API_TOKEN` for now (it's what `.env` exports), but consider bumping to `CLOUDFLARE_API_TOKEN` in next ops sweep.

## Files

- Migration (blocked from apply): `workers/referrals-api/migrations/0002-v1-sprint-schema.sql`
- Receipt for Jared: `exports/portal-files/d1-schema-apply-receipt-2026-05-07.md`
- Rollback (unused — nothing to roll back): `workers/referrals-api/migrations/0002-v1-sprint-schema.rollback.sql`

## What I'd do differently next time

Add a "table existence sweep" stanza at the TOP of every D1 migration SQL file as a comment block, listing every table the migration assumes exists, with a note on which DB it must be in. Spec authors then have a checklist when validating against production. Could ship as a 30-line `pre-migration-check.sh` skill.
