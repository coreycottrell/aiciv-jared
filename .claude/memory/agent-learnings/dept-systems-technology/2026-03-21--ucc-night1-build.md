# Memory: UCC Night 1 Build — Unified Command Center

**Date**: 2026-03-21
**Type**: operational
**Topic**: Night 1 build of the Unified Command Center on cc.purebrain.ai

---

## What Was Built

Added the Business Mandala to the existing FastAPI comms-gateway app (cc.purebrain.ai).

### Files Created
- `/home/jared/projects/AI-CIV/aether/tools/comms-gateway/api/mandala.py` — Mandala CRUD API
- `/home/jared/projects/AI-CIV/aether/tools/comms-gateway/sync/sheets_sync.py` — Google Sheets sync
- `/home/jared/projects/AI-CIV/aether/tools/comms-gateway/data/seed_mandala.py` — seed data

### Files Modified
- `models.py` — added 5 new tables: mandala_segments, goals, tasks, team_assignments, sheets_sync_log
- `main.py` — added mandala router, mandala tab in nav, mandala view HTML, mandala CSS+JS, FCF tiles

### DB State
- 8 mandala segments seeded
- 64 tasks seeded (8 per segment)
- 19 goals seeded
- DB at: tools/comms-gateway/data/comms.db

## Key Architectural Patterns

### How Dashboard Injection Works
The dashboard at /dashboard in main.py serves inline HTML injected into `purebrain-hub-source.html`.
- INJECTION 1: CSS + sessionStorage bridge (in `gateway_head_injection` f-string)
- INJECTION 2: New tab buttons added to `new_view_tabs` string
- INJECTION 3: View divs added to `calendar_email_views` string (ends with `<!-- Toast -->"""`)
- INJECTION 4: JavaScript added to `gateway_script` string (ends with `</body>"""`)

CRITICAL: The `calendar_email_views` variable is a regular `"""` string (NOT an f-string).
Insert mandala HTML INSIDE that string, before the closing `<!-- Toast -->"""`.

If HTML accidentally lands outside a string (as happened in this build), Python syntax breaks.
Fix: use Python script to extract and reinsert into the correct string variable.

### Gotcha: Em dashes in strings
The character U+2014 (—) causes SyntaxError in Python. Replace with `&mdash;` for HTML context.

### Gotcha: $ in strings
`$500K` type strings in triple-quoted Python strings are fine (not f-strings), but if accidentally
inside an f-string they break. Keep mandala HTML out of f-strings.

## Known Blocker: Google Sheets Access
Service account (purebrain@puremarketing.ai via DWD) cannot read the spreadsheet:
`1HuJIWEEXpkHgpL2iI6Zit9_cxw3dNd_8zZkOzsK4BGk`

Fix for Night 2: Share the spreadsheet with the service account email.
Get service account email: `python3 -c "import json; print(json.load(open('.credentials/google-drive-service-account.json'))['client_email'])"`

## Verification Commands
```bash
curl -s http://localhost:8870/health  # should return {status: ok}
python3 -c "import sqlite3; c=sqlite3.connect('data/comms.db').cursor(); c.execute('SELECT COUNT(*) FROM mandala_segments'); print(c.fetchone())"  # expect (8,)
```

## PayPal Live Data
Live PayPal credentials work for MRR tile.
Night 1 result: ~$2,000/mo (10 active subscribers).

## Drive Uploads (Night 1 docs)
Folder: https://drive.google.com/drive/folders/1l277sH4gdAlg55_OhTdy845ibcQKqqZr
- architecture-doc.md: 12ZnHed8Nv3uvpMWBmTd4Sxt6HjBpaKL-
- sprint-1-report.md: 1cAC41FXRlEIyheFWroRdmjUJayy640vt
- data-model.md: 1p-fbxz7IUxaWYXgySgcPdI6kf1hZntQa
