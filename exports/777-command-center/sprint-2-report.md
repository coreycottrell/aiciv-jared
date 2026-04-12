# 777 Command Center -- Sprint 2 Report

**Sprint**: Night 2 (Mar 21-23, 2026)
**Status**: Complete + Verified
**Deploys**: Vercel (static + serverless functions)

---

## What Was Built

### 1. 60-Second Cron Sync (Google Sheets -> Dashboard)

**File**: `tools/777_sync_cron.sh`

- Runs the Python data fetcher every 60 seconds via cron
- Lockfile mechanism prevents overlapping runs
- Checks for pending UI edits and triggers Sheets writeback
- Now includes D1 cache warming after each fetch (Step 1.5)
- Logs all activity with timestamps to `logs/777-sync.log`
- Cron installed: `* * * * * bash tools/777_sync_cron.sh`

**Verification (Mar 23)**: Cron confirmed active. Live Sheets data pulled successfully (source: "live", 90 heatmap entries, 20 questions, 31,807 proof wall tasks). Sync completed in 44s.

### 2. D1-Compatible SQLite Cache

**File**: `tools/777_d1_cache.py`
**Database**: `data/777-cache.db`

6-table schema matching Cloudflare D1 SQLite:
- `sync_state` -- tracks last sync time, etags
- `daily_scores` -- per-day scores with question breakdowns (90 rows)
- `seven_fs` -- weekly 7 F's ratings (2 rows)
- `goals` -- vision + 7 yearly + 95 top-77 goals (103 total)
- `proof_wall` -- task completion history (10 recent)
- `pending_edits` -- queue for bidirectional sync

Functions: `init_db`, `cache_data`, `get_cached_data`, `add_pending_edit`, `get_pending_edits`, `mark_edits_synced`, `needs_refresh`

Schema is D1-ready for migration when broader CF API token is available.

**Bugs Fixed (Mar 23)**:
- Fixed `daily_pulse` key mismatch (cache expected `daily_reflection`, live data uses `daily_pulse`)
- Fixed `proof_wall` parsing (cache iterated dict keys instead of `recent` array)
- Added cache warming to cron (Step 1.5) so cache stays fresh automatically

### 3. Bidirectional Edit API

**File**: `exports/777-command-center/api/edit.js`

Vercel serverless function:
- POST `/api/edit` with `{password, table, key, field, value}`
- Password validation (same 777grind gate)
- Per-IP rate limiting (10 edits/minute)
- Whitelist validation for table names and field names
- Writes to `pending-edits.json` queue
- Returns `{ok: true, queued: true, edit_id: N}`

**Bug Fixed (Mar 23)**: Added question index fields ("0" through "19") to `daily_scores` whitelist. Dashboard sends individual question toggles by index, but the whitelist only allowed "score".

### 4. Sheets Writer (Bidirectional Sync)

**File**: `tools/777_sheets_writer.py`

- Reads unsynced edits from `pending-edits.json` and `data/777-cache.db`
- Maps edits back to correct Google Sheets cells:
  - `daily_scores` -> Sheet [30] (TOTAL SCORE row)
  - `seven_fs` -> Sheet [36] (finds date col + F row)
  - `goals` -> Sheet [15]/[14]
  - `proof_wall` -> Sheet [28]
- Uses GDriveManager OAuth2 auth (same as fetcher)
- Rate-limited: 0.3s pause between writes
- Audit trail in `logs/777-sync.log`

### 5. Mandala Real Data Integration

**File**: `exports/777-command-center/mandala-business.html` (updated)

- Fetches `data.json` on page load for real Sheets data
- Maps vision -> center cell, top77 year-8 items -> 8 pillars, remaining -> task cells
- Local-first merge: localStorage edits override sheet data
- Sync button in nav sends dirty edits to `/api/edit`
- Sync status indicator (grey=local, yellow=unsaved, green=synced)

### 6. Dashboard Live Editing

**File**: `exports/777-command-center/index.html` (updated)

- Interactive daily score questions (click to toggle 0/1, POSTs to /api/edit)
- Freshness indicator chip (green=fresh, yellow=stale, red=offline)
- 60-second auto-refresh (re-fetches data.json, smooth update if changed)
- Green flash animation on successful edits

---

## Architecture

```
Google Sheets
    |
    v (every 60s via cron)
Python Fetcher (777_data_fetcher.py)
    |
    v
data.json + SQLite cache (D1-compatible)
    |              ^
    |              | (Step 1.5: cache warming)
    v              |
Dashboard (index.html + mandala-business.html)
    |
    v (user edits)
/api/edit (Vercel serverless) -> pending-edits.json
    |
    v (every 60s via cron)
Python Writer (777_sheets_writer.py) -> Google Sheets
```

Data flows bidirectionally. Dashboard is local-first with opportunistic sync.

---

## Verified Data Flow (Mar 23, 2026)

| Component | Status | Evidence |
|-----------|--------|----------|
| Google Sheets fetch | LIVE | source: "live", 90 heatmap entries |
| D1 SQLite cache | POPULATED | 90 daily_scores, 103 goals, 10 proof_wall |
| Cron job | ACTIVE | `* * * * * bash tools/777_sync_cron.sh` |
| Cache warming | ADDED | Step 1.5 in cron, auto-runs after fetch |
| Edit API whitelist | FIXED | Question indices 0-19 now allowed |
| Mandala data load | VERIFIED | Fetches data.json, maps goals to cells |
| Dashboard editing | VERIFIED | Toggle questions, POST to /api/edit |

---

## Files Created/Modified

| File | Action | Purpose |
|------|--------|---------|
| `tools/777_sync_cron.sh` | Created + Updated | 60s cron wrapper + cache warming |
| `tools/777_d1_cache.py` | Created + Fixed | SQLite cache (key mapping + proof_wall) |
| `tools/777_sheets_writer.py` | Created | Bidirectional Sheets writer |
| `data/777-cache.db` | Created | SQLite database (90+ rows populated) |
| `exports/777-command-center/api/edit.js` | Created + Fixed | Edit API (whitelist fix) |
| `exports/777-command-center/vercel.json` | Modified | Added /api/edit route |
| `exports/777-command-center/mandala-business.html` | Modified | Real data + sync |
| `exports/777-command-center/index.html` | Modified | Inline edit + auto-refresh |

---

## Known Issues

1. **Sync duration**: Latest sync took 44s (above 30s target). The Google Sheets API is slow with 68+ sheet tabs. Consider caching only changed sheets.
2. **CF D1 migration pending**: The SQLite schema is D1-ready but actual CF D1 deployment requires a broader API token (current CF_PAGES_TOKEN lacks D1 permissions).
3. **Vercel cold starts**: The `/api/edit` endpoint may have ~500ms cold start latency on first request.
4. **OAuth token refresh**: Token may expire during long-running overnight sessions. Fetcher falls back to cached/sample data gracefully.

## Sprint 3 Plan (Night 3)

- Deploy updated dashboard to Vercel
- Team invite system (Phase 2 users)
- Thinking exercises integration with real data
- CF D1 migration (if token is upgraded)
- Performance optimization (sub-30s sync target)
