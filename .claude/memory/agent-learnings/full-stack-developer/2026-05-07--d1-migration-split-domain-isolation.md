# D1 Migration Split for Domain Isolation — Pattern + Gotchas

**Date**: 2026-05-07
**Type**: teaching
**Topic**: When a monolithic D1 migration spans tables that should not co-locate, split it.

## Trigger

Constitutional rule (May 7, 2026): `purebrain-social` must NEVER touch referrals/clients. The original `0002-v1-sprint-schema.sql` ALTERed both `commission_payments`/`referrals` (in `purebrain-referrals`) AND `clients` (currently still in `purebrain-social`, drift). Applying it as-is would have either failed (clients table not in target DB) or violated the isolation rule.

## Pattern

Split the migration into:
- `0002a-{domain}-only-schema.sql` — applies cleanly to the domain D1
- `0002b-{other-domain}-additions.sql` — held with explicit "DO NOT APPLY" header and target D1 documented for post-extraction

Mark the original monolithic file as SUPERSEDED with a comment block pointing to the split files. This prevents future operators from running it accidentally.

Companion rollback files: only create rollback for the half that gets applied. The held half has nothing to roll back yet.

## Gotchas

### 1. Wrangler 4.89.0 dropped `d1 backup create`

The runbook said `npx wrangler d1 backup create purebrain-referrals` — that subcommand no longer exists. Use:
```bash
npx wrangler d1 export <db> --remote --output <file.sql>
```
This produces an addressable SQL dump. Time Travel (automatic 30-day point-in-time recovery) is the new "always-on" backup; explicit export is the addressable artifact for receipts.

### 2. SQLite ALTER TABLE ADD COLUMN cannot use IF NOT EXISTS

If columns already exist on retry, the apply errors out. Acceptable for first-apply but means re-running 0002a on an already-migrated DB will fail on the first ALTER. Future-proof retry strategy: split the file into "create new objects" (idempotent via IF NOT EXISTS) and "ALTER existing" (must be one-shot or use schema_migrations log to skip).

### 3. UNIQUE constraints can't be added via ALTER TABLE in SQLite

Use `CREATE UNIQUE INDEX ... ON table(cols) WHERE clause` instead. The WHERE clause filters legacy NULL rows so the constraint applies only to new attribution writes.

### 4. Verification miss bug

Earlier session today wrote a receipt and didn't read it back, missing a partial write. New rule: after Write tool on a receipt, always Read or `ls -la` to confirm size + content before claiming completion.

## Reusable Recipe

```bash
# 1. Pre-check ALTER targets exist
npx wrangler d1 execute <db> --remote --command "SELECT name FROM sqlite_master WHERE type='table' AND name IN (...)"

# 2. Backup as addressable file
BACKUP_FILE="/path/backups/d1/<db>-pre-<migration>-$(date -u +%Y%m%dT%H%M%SZ).sql"
npx wrangler d1 export <db> --remote --output "$BACKUP_FILE"

# 3. Apply
npx wrangler d1 execute <db> --remote --file <migration.sql>

# 4. Verify (3-5 queries minimum)
#    - new tables present
#    - PRAGMA table_info on ALTERed tables
#    - new indexes present
#    - schema_migrations log entry present
#    - confirm OUT-OF-DOMAIN tables NOT touched

# 5. Write receipt + Read it back
```

## File Paths Referenced

- Migration files: `workers/referrals-api/migrations/0002a-referrals-only-schema.sql`, `0002a-referrals-only-schema.rollback.sql`, `0002b-clients-additions.sql`
- Receipt: `exports/portal-files/d1-schema-apply-receipt-2026-05-07-v2.md`
- Backup: `backups/d1/purebrain-referrals-pre-0002a-20260507T155851Z.sql`
- Branch: `referral-v1` (HEAD `b1c10a3`)
- Final D1 bookmark: `000000ba-0000000c-00005064-bb07ea881fb884d8858bd66f13f1a34f`

## Outcome

- 16 queries executed, 0 errors
- 3 new tables, 4 new columns (2 per existing table), 1 unique index, 1 migration log entry
- 0 cross-domain pollution verified (clients still absent from purebrain-referrals)
- 0002b held for clients extraction sprint
