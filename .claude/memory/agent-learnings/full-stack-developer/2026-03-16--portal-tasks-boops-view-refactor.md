# Portal Tasks Panel: BOOPs View Refactor

**Date**: 2026-03-16
**Type**: operational + teaching
**Agent**: full-stack-developer

## What Was Done

Refactored the PureBrain portal Tasks panel to move the "Automated BOOPs" section from a collapsed accordion at the bottom to a first-class toggle view in the header.

## Key Changes

### portal-pb-styled.html

1. **Header**: Added `<button class="sched-boops-toggle-btn" id="sched-view-boops">` pill button between the count badge and the List/Board toggle group.

2. **BOOPs view**: Replaced the old `boops-section` accordion div with `<div class="sched-boops-view" id="sched-boops-view">` — a full-panel scrollable view with its own header row (title + count badge + filter selects inline).

3. **CSS**: Added `.sched-boops-toggle-btn` (pill style, teal border, rounds to 20px), `.sched-boops-view` (flex column, scrollable), `.boops-view-header` (flex row with inline filters).

4. **JS `_wireSchedViewToggle`**: Extended from 2-view to 3-view. List/Board use the same logic as before. BOOPs view hides list+board+filterBar and shows `sched-boops-view`, then calls `window._loadBoopsData()`.

5. **BOOPs IIFE**: Replaced the accordion toggle logic with `window._loadBoopsData = function()` — called on demand when BOOPs view activates. Added `_boopsLoaded` flag to avoid redundant fetches. Removed the MutationObserver (was triggering load on panel open but data was hidden and never displayed).

### portal_server.py (route table)

**Root cause of "Loading BOOPs..." stuck**: The route table had:
- `Route("/api/boops", ...)` at position 5349
- `Route("/api/boops/{name}", endpoint=api_boop_read)` at position 5350 — this was the OLD skills reader
- `Route("/api/boops", ...)` AGAIN at position 5361 (duplicate)
- `Route("/api/boops/{boop_id}", endpoint=api_boop_update, methods=["PATCH"])` at 5362

Because Starlette uses first-match routing, PATCH requests to `/api/boops/some-id` were matching the `{name}` route (no method restriction) instead of the PATCH-only `{boop_id}` route. The duplicate GET route was also noise.

**Fix**: Removed the old `{name}` route and the duplicate GET route. Left two clean routes:
```python
Route("/api/boops", endpoint=api_boops_list),
Route("/api/boops/{boop_id}", endpoint=api_boop_update, methods=["PATCH"]),
```

## Python Gotcha

When two functions have the same name in a Python module, the SECOND definition wins. So both `api_boops_list` definitions existed, but the route table used the second (correct) one that reads from `scheduled-tasks-state.json`. The OLD function (line 1592 reading from SKILLS_DIR) was effectively dead code.

## Data Format

`/api/boops` returns:
```json
{
  "boops": [
    {"id": "...", "description": "...", "frequency": "daily", "status": "active",
     "category": "communication", "agent": "human-liaison", "last_run": "...",
     "schedule_slot": "...", "override_max_daily": false}
  ],
  "rules": {...}
}
```

Source file: `/home/jared/projects/AI-CIV/aether/.claude/scheduled-tasks-state.json`
32 BOOPs total as of 2026-03-16.
