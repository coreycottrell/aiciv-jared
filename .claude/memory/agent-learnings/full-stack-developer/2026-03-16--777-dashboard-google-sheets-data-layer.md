# 777 Dashboard — Google Sheets Data Layer

**Date**: 2026-03-16
**Type**: operational + teaching
**Agent**: full-stack-developer

---

## What Was Built

Connected the 777 Command Center dashboard to Jared's Google Sheets life planner.

**Files created/modified:**
- `tools/777_data_fetcher.py` — Python script that reads Google Sheets and writes `data.json`
- `exports/777-command-center/data.json` — Output JSON consumed by dashboard (LIVE DATA — 28.7 KB)
- `exports/777-command-center/index.html` — Updated to load `data.json` on unlock
- `tools/777_explore_sheets.py` — Discovery/debug script

---

## Status (2026-03-16 v2)

**LIVE DATA WORKING.** The fetcher successfully reads from:
`1HuJIWEEXpkHgpL2iI6Zit9_cxw3dNd_8zZkOzsK4BGk`

Auth method: `GDriveManager` OAuth2 → `gspread.authorize(gm.service._http.credentials)`

```
Daily Pulse:  90 heatmap days, 70 with scores, today=0/20
7 F's:        avg=3.0/10 (data stops at 7/25/21 — sheet not updated since 2022)
Proof Wall:   31,807 total tasks, 2026=1,482
Goals:        7 yearly, 95 of 77, vision loaded
Money Map:    target=$60,000,000 ($250k/month × 12 × 20yr)
Legacy:       10 micro laws, 3 eulogies loaded
Gratitude:    5 recent entries
Achievements: 378 total
```

---

## Actual Sheet Structure (CRITICAL — verified by exploration)

**Sheet [30] Daily Reflection Process (2026-2028):**
- Row 1 (index 1): Date headers in cols 2+ ('1/4/26', '1/5/26'...) — spans to 2029
- Row 2 (index 2): Day names (Sun/Mon/Tue...)
- Rows 3-22 (0-indexed): 20 questions with scores (0/0.5/1/2/3 — with bonuses)
- Row 23: `TOTAL SCORE` — formula sum (USE THIS for daily totals)
- Row 24: `AVERAGE SCORE`
- Rows 25+: Legend notes AND compound interest financial projections (large numbers — NOT scores)
- **Max score: 20 (+ up to 6 bonus pts = ~26 max)**
- Today is col 73 (0-indexed) for 3/16/26

**Sheet [36] Weekly Edit (7 F's):**
- Row 0: Date headers from 6/30/19 to 1/2/22 (134 total cols, last data ~col 110)
- Row 0 col 1: 'My Weekly Edits'
- Rows 13-19: 7 F labels in col B, scores in date cols
  - Row 13: Family/Foundation/Love
  - Row 14: Freedom/Business/Career
  - Row 15: Fitness/Physical Health
  - Row 16: Faith/Spiritual
  - Row 17: Financial/Money
  - Row 18: Fellowship/Friends
  - Row 19: Fun/Hobbies
- **NOTE: Data stops at July 2021. Jared stopped tracking 7Fs weekly.**
- Fetcher returns last week that has non-zero scores.

**Sheet [28] Proof Self-Discipline (2026):**
- Row 0: `['Information Related to Tasks or Dates', 'Total Past Completed Tasks -->', '1482', ...]`
- Row 1: Column headers
- Rows 2+: Date in col A ('1/1/2026') + tasks in cols B, C (sparse — many rows share same date)
- Total tasks (all years): 31,807

**Historical proof sheets by index:**
- [28]=2026, [56]=2025, [58]=2024, [60]=2023, [63]=2022, [65]=2021, [67]=2020, [68]=2019

**Sheet [9] The Number:**
- Row 3: `['Cash Spent Per Month', '$250,000.00']`
- Row 4: `['Cash Spent Per Year', '$3,000,000.00']`
- Retirement target: $60M (250k × 12 × 20yr)

**Sheet [10] Vision:**
- Row 3, col A: Vision statement wrapped in `"` quotes

**Sheet [17] Legacy:**
- Row 2: `['Family', 'Friend']`
- Row 3: `[family_eulogy, friend_eulogy]`
- Row 4: `['Business Partner', 'Client']`
- Row 5: `[biz_eulogy, client_eulogy]`

**Sheet [7] 10 Micro Laws:**
- Row 5-14 (0-indexed): `['1', 'law text', '']`

---

## Architecture Pattern

**Static-first data layer**: Python fetcher → `data.json` → static HTML dashboard.

No backend required. Dashboard stays on Vercel as static HTML. Data refreshes when fetcher is re-run.

**Auth: GDriveManager OAuth2** — runs as `purebrain@puremarketing.ai` via domain-wide delegation.
No spreadsheet sharing required (OAuth = account owner access).

```python
from tools.gdrive_manager import GDriveManager
import gspread

gm = GDriveManager(verbose=False)
creds = gm.service._http.credentials
gc = gspread.authorize(creds)
ss = gc.open_by_key('1HuJIWEEXpkHgpL2iI6Zit9_cxw3dNd_8zZkOzsK4BGk')
```

---

## Key Gotchas

1. **Daily Reflection rows 25+ have financial tracking data** (compound interest calcs) — large numbers like `142,275`. Only use rows 3-22 for questions, and row 23 for the TOTAL SCORE formula value.

2. **7 F's data stopped at July 2021** — Jared stopped tracking weekly. Fetcher finds last column with non-zero data.

3. **Sheet date range goes to 2029** — pre-filled date headers for future years. Must filter to `date <= today` to avoid processing thousands of empty future columns.

4. **Monthly task counts** for Proof Wall require re-counting from the raw data (the sheet doesn't have a monthly summary row).

5. **Net worth sheet has `#REF!` cells** from broken formulas (last updated 2018). Returns $0.

---

## Next Steps

1. Deploy updated `data.json` to Vercel with the dashboard
2. Set up daily cron: `0 6 * * * cd /home/jared/projects/AI-CIV/aether && python3 tools/777_data_fetcher.py`
3. Dashboard `applyLiveData()` function reads from `data.json` structure — verify field names match
