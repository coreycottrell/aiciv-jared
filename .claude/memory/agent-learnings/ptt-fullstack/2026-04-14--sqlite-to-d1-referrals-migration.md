# SQLite → D1 Referrals Migration (2026-04-14)

**Type**: teaching + operational
**Topic**: Merging two SQLite databases with different ID spaces into D1

## What happened
Migrated referrals from two SQLite sources (local `/home/jared/purebrain_portal/referrals.db` + chy-jared container `aiciv@37.27.237.109:2213:/home/aiciv/purebrain_portal/referrals.db`) into Cloudflare D1 `purebrain-referrals` (id `cdd9a522-f947-42a6-b9a3-c30534e02c3f`).

## Key patterns

### 1. D1 disallows `BEGIN TRANSACTION` / `COMMIT`
Wrangler errors: *"To execute a transaction, please use the state.storage.transaction() APIs..."*. Write import SQL as plain INSERT statements. D1 wraps the whole file in an atomic unit internally.

### 2. Two SQLite sources had different ID spaces
- Local: JAREDSB0 was `id=1`, 25 referrers total
- chy-jared: JAREDSB0 was `id=3`, 28 referrers total
- Natural key for dedupe = `referral_code` (UNIQUE + NOCASE in schema)
- Strategy: preserve chy-jared IDs verbatim (it's newer, has today's fixes), then append local-only referrers with IDs starting at `max(chy_id)+1`. Remap local FKs via `local_id_map[old] -> new`.

### 3. "Prefer chy-jared post-fix" rule
For JAREDSB0: use chy-jared's referrals + commission_payments ONLY (skip all local). For other overlapping codes: merge both, dedupe by `(referrer_id, email.lower(), created_at)`.

### 4. Final counts
- referrers: 25+28 → 28 (all chy + 0 local-only; local's 25 all had chy equivalents)
- referrals: 26+11 → 27 (11 chy + 16 local non-JAREDSB0; 10 local JAREDSB0 skipped)
- commission_payments: 25+10 → 25 (10 chy + 15 local)
- rewards: 25+7 → 22 (7 chy + 15 local)
- referral_clicks: 216+87 → 303 (no FK, dedupe by code+ip+time)

## Scripts (reusable)
- `/tmp/dump_referrals.py` — standalone dumper, takes db path arg, outputs JSON to stdout
- `/tmp/merge_referrals.py` — merges two JSON dumps with configurable "authoritative source" rule
- `/tmp/gen_import_sql.py` — emits D1-safe INSERT statements from merged JSON

## Verification command
```
npx wrangler@latest d1 execute purebrain-referrals --remote \
  --command="SELECT r.id, r.referred_name, cp.commission_value, cp.tier FROM referrals r LEFT JOIN commission_payments cp ON r.id=cp.referral_id WHERE r.referrer_id=3 ORDER BY r.id"
```
Returned exactly the 10 expected rows (ids 1-9, 16) with correct commission values + tiers.

## Next step (for cutover)
SQLite files NOT touched. ptt-fullstack must port `portal_server.py` queries to D1 REST API (or D1 HTTP binding), then flip reads/writes. Only after cutover should we lock SQLite.
