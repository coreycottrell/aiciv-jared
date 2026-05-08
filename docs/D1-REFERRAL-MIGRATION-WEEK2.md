# D1 Referral Migration — Week 2 Project

**Status**: QUEUED (Jared approved as Week 2 project on 2026-04-14)
**Owner**: ptt-fullstack (dispatched by Aether)
**Estimated effort**: ~3 hours
**Blocker to start**: Week 1 referral quick-fix must land + stabilize first

## Problem

Two-database split-brain between:
- `portal_server.py` local SQLite (Jared's workstation)
- `chy-jared` container SQLite (Witness VPS, what `/refer/` actually hits)
- CF D1 `purebrain-referrals` (exists, unused since Apr 6 migration)

Result: data drift, wrong display, wasted agent cycles diagnosing.

## Target Architecture

**ONE source of truth**: CF D1 `purebrain-referrals`
- Both `portal_server.py` instances read/write via HTTP to D1 Worker API
- SQLite files become retired backups, not data source
- CF Worker owns auth + CORS + schema

## Migration Steps

### 1. Activate D1 endpoints
- Re-enable `/api/referral/*` CF Pages Functions (currently marked DEPRECATED)
- Add `/api/admin/*` mirror endpoints (admin needs D1 access too, not just public)
- Add proper auth per endpoint (session token for public, admin token for admin)

### 2. Port portal_server.py queries to HTTP calls
- Replace `sqlite3.connect()` blocks with `requests.get/post` to D1 Worker
- Preserve identical function signatures — no upstream code changes
- Cache responses locally for 30s to avoid hammering D1 on every page load

### 3. One-time reconcile
- Dump both SQLite DBs to JSON
- Merge with dedup rules (prefer chy-jared rows, fill gaps from local)
- Fix the 4 broken rows during merge (id=16 → rejected, id=1/2 → CP backfilled, etc)
- Load into D1 via Worker `/admin/bulk-import` (build this endpoint)

### 4. Test parity
- Run both instances pointed at D1
- Run existing `/refer/` + `/admin/referrals` against D1 in staging
- Compare outputs to pre-migration state — JAREDSB0 total, row count, earnings
- Zero-diff required

### 5. Cutover
- Flip Worker route from local SQLite fallback to D1-primary
- Monitor for 48 hours
- If stable, mark SQLite files read-only
- If issues, rollback = revert Worker route

### 6. Retire
- After 7 days of D1 running clean, decommission one portal_server instance
- Keep the other as write-proxy if needed, or kill both if Worker handles all writes
- SQLite backups archived for 90 days then deleted

## Risks

- D1 rate limits at free tier (~1000 req/s soft cap) — should be fine for our traffic
- HTTP latency adds ~50-100ms vs local SQLite — cache layer compensates
- Single-region D1 — if CF has regional issues, our referrals go offline. Worth backing up to a secondary DB?
- Migration may reveal more broken rows than the 4 we know about — budget for +1 hr if so

## Not In Scope

- Changing the referral SCHEMA (stays same)
- Changing commission math rules (stays $35 × 5%)
- Changing frontend (refer/index.html) — it just hits the same endpoint URLs
- Migrating other DBs (investor DB, gift pages, etc) — separate projects

## Dependencies

- Wave 2 Corey package vetting complete (may inform whether we use D1 or adopt a different shared-DB pattern from Corey)
- 777 Trio Comms panel stable (not blocking, just context)
- Week 1 quick-fix landed + verified (Jared's view clean)

## Success Criteria

- `/refer/` + `/admin/referrals` both read from D1, show identical data
- JAREDSB0 total matches between both views
- No duplicate data writes across two DBs possible
- Single source of truth locked in MEMORY.md
- Backup retention policy documented

## Scheduling

Earliest start: **2026-04-21** (Monday Week 2)
Latest start: **2026-04-28** (if Waves 2 + 3 of Corey packages take longer)

Will re-open this doc when scheduling firm.
