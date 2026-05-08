# D1 Schema Apply Receipt — v2 (Split Migration)

**Date**: 2026-05-07
**Operator**: PTT (Full-Stack Developer, Pure Brain Tech Team)
**Authority**: Jared (CEO) greenlit "yes go with that" — split + apply
**Database**: `purebrain-referrals` (UUID `cdd9a522-f947-42a6-b9a3-c30534e02c3f`)
**Status**: ✅ **SUCCESS**

---

## Summary

The monolithic `0002-v1-sprint-schema.sql` migration was split into two halves to honor the May 7 constitutional domain-isolation rule (purebrain-social must NEVER touch referrals/clients). The clients-INDEPENDENT half (`0002a`) was applied to production `purebrain-referrals` D1 with a backup-first protocol. The clients-DEPENDENT half (`0002b`) is HELD pending extraction of the clients table from `purebrain-social` to its own dedicated D1.

---

## Branch State Post-Commit

**Branch**: `referral-v1`
**HEAD commit**: `b1c10a3` — "refactor(d1): split v1 sprint schema into 0002a (referrals-only, applyable now) + 0002b (clients additions, held pending extraction per domain isolation rule)"
**Remote push**: NOT pushed (per instructions — SHIP-gate decision held for Aether)

**Recent commits**:
```
b1c10a3 refactor(d1): split v1 sprint schema into 0002a + 0002b
d8a0306 feat(d1): v1 sprint schema migrations — partner_applications, rate_adjustments, payout_requests_v2, tier_at_write, UNIQUE pb_ref+payment_id
11443b5 feat: Add referral admin + partner CF Pages content (split from 107019b)
```

---

## Files Changed

| File | Status | Purpose |
|------|--------|---------|
| `workers/referrals-api/migrations/0002a-referrals-only-schema.sql` | NEW | Applied to purebrain-referrals |
| `workers/referrals-api/migrations/0002a-referrals-only-schema.rollback.sql` | NEW | Rollback for 0002a |
| `workers/referrals-api/migrations/0002b-clients-additions.sql` | NEW | HELD — clients ALTERs, pending extraction |
| `workers/referrals-api/migrations/0002-v1-sprint-schema.sql` | MARKED SUPERSEDED | Original monolith, now redirect comment |
| `workers/referrals-api/migrations/0002-v1-sprint-schema.rollback.sql` | MARKED SUPERSEDED | Original rollback, now redirect comment |

---

## Backup

| Field | Value |
|-------|-------|
| **Method** | `wrangler d1 export` (full SQL dump) |
| **File path** | `/home/jared/projects/AI-CIV/aether/backups/d1/purebrain-referrals-pre-0002a-20260507T155851Z.sql` |
| **Size** | 3,598,022 bytes (3.6 MB) |
| **Timestamp (UTC)** | 2026-05-07T15:58:51Z |
| **Time Travel** | Automatic 30-day point-in-time recovery active (D1 default) |

**NOTE**: Wrangler 4.89.0 deprecated the `d1 backup create` subcommand. Used `d1 export` instead — produces an addressable SQL dump file. Time Travel provides additional automatic point-in-time recovery up to 30 days for catastrophic restore scenarios.

---

## Apply

| Field | Value |
|-------|-------|
| **File** | `migrations/0002a-referrals-only-schema.sql` |
| **Target** | `purebrain-referrals` D1 (remote) |
| **Apply timestamp (UTC)** | 2026-05-07T15:59:13Z (approx, server bookmark time) |
| **Queries executed** | 16 |
| **Rows read** | 273 |
| **Rows written** | 24 |
| **DB size after** | 3,928,064 bytes (3.93 MB) |
| **Final bookmark** | `000000ba-0000000c-00005064-bb07ea881fb884d8858bd66f13f1a34f` |
| **Errors** | 0 |
| **Result** | ✅ SUCCESS |

---

## Verification (5 queries, all passed)

### 1. New tables present (3/3)

```sql
SELECT name FROM sqlite_master WHERE type='table'
  AND name IN ('partner_applications','rate_adjustments','payout_requests_v2')
```

Result:
```json
["partner_applications", "payout_requests_v2", "rate_adjustments"]
```

✅ All 3 expected tables present.

### 2. commission_payments has new columns (2/2)

```sql
PRAGMA table_info(commission_payments)
```

Result includes:
- `tier_at_write` (TEXT)
- `commission_source` (TEXT)

✅ Both new columns present (12 total columns vs 10 pre-migration).

### 3. referrals has new columns (2/2)

```sql
PRAGMA table_info(referrals)
```

Result includes:
- `pb_ref` (TEXT, NULL)
- `payment_id` (TEXT, NULL)

✅ Both new columns present (9 total columns vs 7 pre-migration).

### 4. UNIQUE index present

```sql
SELECT name FROM sqlite_master WHERE type='index' AND name='uniq_referrals_pbref_payment'
```

Result:
```json
[{"name": "uniq_referrals_pbref_payment"}]
```

✅ Partial unique index created.

### 5. schema_migrations log entry present

```sql
SELECT migration_name, applied_at FROM schema_migrations
```

Result:
```json
[{"migration_name": "0002a-referrals-only-schema", "applied_at": 1778169553}]
```

✅ Migration logged.

### 6. Bonus: clients table NOT in purebrain-referrals

```sql
SELECT name FROM sqlite_master WHERE type='table' AND name='clients'
```

Result: **empty** — `clients` is correctly absent from `purebrain-referrals`. No cross-DB pollution. Domain isolation honored.

---

## 0002b Status — Confirmed UN-APPLIED

**File**: `workers/referrals-api/migrations/0002b-clients-additions.sql`
**Status**: 🔴 HELD
**Apply target (when ready)**: `purebrain-clients` D1 (does not yet exist — created during extraction sprint)
**Block reason**: clients table currently lives in `purebrain-social` D1 (drift). Constitutional rule (May 7) bans purebrain-social from touching referrals/clients. Extraction sprint must complete before this file can be applied.

**No ALTER on clients was attempted in this session.** The `purebrain-social` D1 was NOT touched. The `purebrain-referrals` D1 does not contain a `clients` table (verified above).

---

## Constraints Honored

- [x] Backup-first (file dump + Time Travel)
- [x] Did NOT apply 0002b (clients ALTERs)
- [x] Did NOT touch `purebrain-social` D1
- [x] Did NOT push `referral-v1` branch to origin (SHIP-gate decision held for Aether)
- [x] Verification queries run BEFORE writing receipt
- [x] Receipt file Read back after write (see below)

---

## Next Steps for Aether

1. **Phase 3 BUILD unblocked**: `purebrain-referrals` D1 now has the schema needed for partner applications, rate adjustments, payout requests v2, tier_at_write commission tracking, and idempotent /referrals/complete via `(pb_ref, payment_id)` unique index.

2. **0002b deferred**: Aether dispatches clients-extraction sprint before the clients-dependent half can ship. Suggested owner: ST# (Systems-Technology) for Worker binding rewrites + new D1 provisioning.

3. **`referral-v1` push decision**: Branch has 2 commits ahead of `origin/main` (d8a0306 + b1c10a3). Push when SHIP-gate clears.

4. **Backup retention**: The 3.6 MB SQL dump at `/home/jared/projects/AI-CIV/aether/backups/d1/purebrain-referrals-pre-0002a-20260507T155851Z.sql` should be retained until v1 sprint Phase 3 ships and stabilizes (recommend 30 days minimum).

---

## Receipt File

**Path**: `/home/jared/projects/AI-CIV/aether/exports/portal-files/d1-schema-apply-receipt-2026-05-07-v2.md`
**Verified existence**: see post-write Read confirmation in chat
