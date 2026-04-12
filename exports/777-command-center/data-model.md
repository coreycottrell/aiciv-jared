# 777 Command Center — Data Model

**Version**: 2.1 (Sprint 2 - Verified Mar 23, 2026)
**Database**: SQLite (D1-compatible) at `data/777-cache.db`
**Source of Truth**: Google Sheets `1HuJIWEEXpkHgpL2iI6Zit9_cxw3dNd_8zZkOzsK4BGk`
**Live Data**: Confirmed pulling live data (source: "live", 90 heatmap entries, 103 goals)

---

## Entity-Relationship Overview

```
+-------------------+     +-------------------+     +-------------------+
|   daily_scores    |     |     seven_fs      |     |      goals        |
|-------------------|     |-------------------|     |-------------------|
| date PK           |     | week_date PK      |     | id PK             |
| score             |     | family            |     | type              |
| max_score         |     | career            |     | text              |
| questions_json    |     | fitness           |     | progress          |
+-------------------+     | faith             |     | year              |
                          | finance           |     | sort_order        |
+-------------------+     | fellowship        |     +-------------------+
|   proof_wall      |     | fun               |
|-------------------|     +-------------------+     +-------------------+
| date              |                               |  pending_edits    |
| task              |     +-------------------+     |-------------------|
| sort_order        |     |   sync_state      |     | id PK AI          |
+-------------------+     |-------------------|     | table_name        |
                          | key PK            |     | record_key        |
                          | value             |     | field             |
                          | updated_at        |     | new_value         |
                          +-------------------+     | created_at        |
                                                    | synced_at         |
                                                    +-------------------+
```

---

## Table Definitions (D1/SQLite DDL)

### sync_state
Tracks synchronization metadata.

```sql
CREATE TABLE IF NOT EXISTS sync_state (
    key        TEXT PRIMARY KEY,
    value      TEXT,
    updated_at TEXT
);
```

**Keys used**:
- `last_sync` — ISO timestamp of last successful Sheets fetch
- `last_etag` — Hash of last data.json for change detection
- `last_write` — ISO timestamp of last successful Sheets write

### daily_scores
One row per day of Daily Reflection scores.

```sql
CREATE TABLE IF NOT EXISTS daily_scores (
    date           TEXT PRIMARY KEY,  -- YYYY-MM-DD
    score          INTEGER,           -- Total score (0-26, 20 base + bonus)
    max_score      INTEGER,           -- Maximum possible (typically 20)
    questions_json TEXT               -- JSON array of {label, score, max}
);
```

**Source Sheet**: `[30] Daily Reflection Process (2026-2028)`
- Row 1: Date headers (cols C+)
- Rows 3-22: 20 questions
- Row 23: TOTAL SCORE (formula sum)
- Max regular score: 20 (each question 0/0.5/1)
- Bonus points possible: up to +6

### seven_fs
Weekly self-assessment across 7 life areas (1-10 scale).

```sql
CREATE TABLE IF NOT EXISTS seven_fs (
    week_date  TEXT PRIMARY KEY,  -- YYYY-MM-DD (week start date)
    family     INTEGER,           -- Family/Foundation/Love
    career     INTEGER,           -- Freedom/Business/Career
    fitness    INTEGER,           -- Fitness/Physical Health
    faith      INTEGER,           -- Faith/Spiritual
    finance    INTEGER,           -- Financial/Money
    fellowship INTEGER,           -- Fellowship/Friends
    fun        INTEGER            -- Fun/Hobbies
);
```

**Source Sheet**: `[36] Weekly Edit`
- Rows 13-19: 7 F labels in col B, scores in date columns
- Data only through July 2021 (tracking paused)

### goals
All goals: vision, yearly, and the Top 77.

```sql
CREATE TABLE IF NOT EXISTS goals (
    id         INTEGER PRIMARY KEY,
    type       TEXT,      -- 'vision' | 'yearly' | 'top77'
    text       TEXT,
    progress   INTEGER,   -- 0-100 (percentage)
    year       TEXT,       -- Target year ('8', '9', '10', etc.)
    sort_order INTEGER
);
```

**Source Sheets**:
- `[10] Vision` — Row 3 col A
- `[14] Year Goals` — Yearly goals
- `[15] Top 77` — 77 lifetime goals with year targets
  - Year 8 = 2026, Year 9 = 2027, etc.

### proof_wall
Task completion history (31,807+ entries across 7 years).

```sql
CREATE TABLE IF NOT EXISTS proof_wall (
    date       TEXT,       -- YYYY-MM-DD
    task       TEXT,
    sort_order INTEGER
);
```

**Source Sheets** (by year):
- `[28]` = 2026, `[56]` = 2025, `[58]` = 2024, `[60]` = 2023
- `[63]` = 2022, `[65]` = 2021, `[67]` = 2020, `[68]` = 2019

### pending_edits
Queue for bidirectional sync (UI edits waiting to write to Sheets).

```sql
CREATE TABLE IF NOT EXISTS pending_edits (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name TEXT,       -- Which table was edited
    record_key TEXT,       -- Primary key of the edited record
    field      TEXT,       -- Which field was changed
    new_value  TEXT,       -- New value
    created_at TEXT,       -- When the edit was made (ISO)
    synced_at  TEXT        -- When it was written to Sheets (NULL = pending)
);
```

**Allowed edits** (validated by API whitelist in `edit.js`):
- `daily_scores`: fields `score` + `0`-`19` (question indices), key = YYYY-MM-DD
- `seven_fs`: fields `family|career|fitness|faith|finance|fellowship|fun`, key = YYYY-MM-DD
- `goals`: fields `text|progress`, key = goal id
- `proof_wall`: fields `task`, key = date

---

## data.json Format (Dashboard Consumption)

The Python fetcher writes this structure, consumed by `applyLiveData()`:

```json
{
  "last_updated": "2026-03-21T10:37:14Z",
  "source": "live",
  "daily_pulse": {
    "heatmap": [{"date": "YYYY-MM-DD", "score": 14}, ...],
    "today": {
      "score": 11,
      "max": 20,
      "questions": [{"label": "...", "score": 1, "max": 1}, ...]
    },
    "streaks": {}
  },
  "seven_fs": {
    "current": {"family": 4, "career": 4, ...},
    "previous": {"family": 2, "career": 4, ...},
    "last_date": "7/25/21"
  },
  "goals": {
    "vision": "...",
    "yearly": [{"text": "...", "progress": 0}, ...],
    "top77": [{"text": "...", "year": "8"}, ...]
  },
  "proof_wall": {
    "total_tasks": 31807,
    "by_year": {"2026": 1482, ...},
    "monthly_2026": [{"month": "Jan", "count": 344}, ...],
    "recent": [{"task": "...", "date": "Today"}, ...]
  },
  "money_map": {
    "net_worth": 0,
    "the_number": {
      "monthly_spend": 250000,
      "annual_spend": 3000000,
      "total_target": 60000000
    }
  },
  "legacy": {
    "vision": "...",
    "eulogies": {"family": "...", "friend": "...", ...},
    "micro_laws": ["...", ...]
  },
  "gratitude": [{"text": "...", "date": "3/13"}, ...],
  "achievements": {
    "total": 378,
    "latest": [{"text": "...", "date": "3/13"}, ...]
  }
}
```

---

## Sync Flow

```
   [Google Sheets]
        |
        | (Python: 777_data_fetcher.py, every 60s)
        v
   [data.json]
        |
        | (Step 1.5: 777_d1_cache.py warms cache)
        v
   [SQLite Cache]
        |
        v
   [Dashboard UI]
        |
        | (user clicks/edits)
        v
   [/api/edit endpoint] -> [pending-edits.json]
        |
        | (Python: 777_sheets_writer.py, every 60s)
        v
   [Google Sheets]
```

**Conflict Resolution**: Last-write-wins at the cell level. UI edits are timestamped and queued; the writer applies them in order. If the same cell is edited in both Sheets and UI between syncs, the UI edit takes precedence (most recent write wins).

---

## D1 Migration Path

The SQLite schema is identical to what Cloudflare D1 uses. Migration steps:

1. Create D1 database: `wrangler d1 create 777-command-center`
2. Apply schema: `wrangler d1 execute 777-command-center --file=schema.sql`
3. Create Worker that reads from D1 + Google Sheets API
4. Point dashboard fetch to Worker URL instead of static data.json
5. Point /api/edit to Worker instead of Vercel serverless function

Requires: CF API token with D1 + Workers permissions (current token is Pages-only).
