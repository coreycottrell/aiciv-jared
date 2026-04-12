# Mandala Charts Feature — cc.purebrain.ai
**Date**: 2026-03-21
**Type**: feature-build
**Agent**: dept-systems-technology

## Summary
Added multi-chart personal mandala feature to cc.purebrain.ai and linked Command Center from portal sidebar.

## What Was Built

### 1. New DB Tables (models.py)
- `mandala_charts` — user-owned charts (user_email, name, created_at, updated_at)
- `mandala_cells` — cell data per chart (chart_id, row 0-8, col 0-8, content, checked)
- Tables auto-created on startup via init_db() / SQLAlchemy metadata.create_all

### 2. New API Routes (api/mandala.py)
- GET    /api/charts — list charts for current user
- POST   /api/charts — create chart
- PUT    /api/charts/{id} — rename chart
- DELETE /api/charts/{id} — delete chart + all cells
- GET    /api/charts/{id}/cells — load 9x9 grid cells
- POST   /api/charts/{id}/cells — upsert one cell
- POST   /api/charts/{id}/cells/batch — save all cells at once (used for auto-save)

### 3. New Page (templates/mandala.html)
- Route: /mandala (GET, auth-gated, redirects to /auth/login)
- Full 9x9 grid: center goal (gold), 8 quality cells (teal), 8 quality mirrors, 64 task cells
- Auto-save on blur + 1.2s debounce after input
- Save indicator (saving / saved / error)
- Sidebar with chart list, create new, delete
- Progress tracker (done/64 tasks)
- Export to text
- Session injection from server so user doesn't need re-login

### 4. Dashboard Link (main.py)
- "My Mandala Charts" gold button added to existing business mandala view
- Navigates to /mandala

### 5. Portal Sidebar (portal-pb-styled.html)
- Added "Command Center" nav item (desktop + mobile) below Brainiac Training
- Opens https://cc.purebrain.ai/dashboard in new tab
- Pushed to coreycottrell/purebrain-portal via github-interciv

## Key Technical Notes
- Grid layout: 9x9, center is (4,4)=goal, (3,3)(3,4)(3,5)(4,3)(4,5)(5,3)(5,4)(5,5)=quality, mirror cells auto-reflect quality text
- Block index to quality mapping: 8 outer 3x3 blocks map to 8 quality positions
- Batch save approach prevents N+1 requests when typing
- Quality mirror cells are read-only, sync via DOM JS when quality cell changes
- All auth handled via session middleware (same as rest of cc.purebrain.ai)

## Files Changed
- /home/jared/projects/AI-CIV/aether/tools/comms-gateway/models.py
- /home/jared/projects/AI-CIV/aether/tools/comms-gateway/api/mandala.py
- /home/jared/projects/AI-CIV/aether/tools/comms-gateway/main.py
- /home/jared/projects/AI-CIV/aether/tools/comms-gateway/templates/mandala.html (new)
- /home/jared/purebrain_portal/portal-pb-styled.html

## Verification
- Python syntax: all 3 .py files pass ast.parse()
- Service: aether-comms-gateway restarted, health check 200 OK
- DB: mandala_charts and mandala_cells tables confirmed in comms.db
- /mandala: 303 redirect to /auth/login (correct for unauthenticated)
- /api/charts: 401 without auth (correct)
- /dashboard: still redirects correctly (existing feature intact)
- Portal: pushed to Corey repo commit 0ef6243
