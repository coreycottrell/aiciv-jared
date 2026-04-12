# PureSurf Behavioral Humanization Layer (Layers 3 + 4)

**Date**: 2026-04-06
**Agent**: dept-systems-technology
**Type**: operational
**Server**: 157.180.69.225

## What Was Built

Created `/opt/baas/humanize.py` (621 lines) — a complete behavioral humanization module with two layers:

### Layer 3: Core Behavioral Humanization
- **human_mouse_move()**: Bezier curve movement with De Casteljau algorithm, natural acceleration/deceleration, micro-tremor jitter, position tracking between calls
- **human_click()**: Click with mouse movement to target (offset from center), pre/post-click delays
- **human_type()**: Character-by-character typing at 40-80 WPM with punctuation pauses, thinking pauses, 5% typo rate with adjacent-key errors + backspace correction
- **human_scroll()**: Variable-speed chunk scrolling (60-180px chunks) with reading pauses, 10% chance of scroll-back
- **simulate_reading()**: Micro-movements + scroll adjustments for 3-15 seconds
- **human_delay()**: Gaussian-distributed delay that never lands on round numbers

### Layer 4: LinkedIn Intelligence (LinkedInHuman class)
- **start_session()**: Navigate to feed, casual browse 2-4 posts
- **find_post_to_comment()**: Natural scroll with "See more" clicks, skip 3-7 posts before first engagement, target account matching
- **drop_comment()**: Click comment button, read post, type with human timing, post, scroll away
- **react_to_post()**: Hover for reaction menu, move to target reaction, click
- **view_profile()**: Navigate, read headline, scroll experience, scroll back, leave
- **end_session()**: Smooth scroll to top, natural pause

## Integration Points

Patched `baas_server_simple.py` (Feature 21) via `patch_humanize.py`:

### New API Endpoints (11 total)
- `POST /sessions/{sid}/humanized-click` — Bezier mouse + click
- `POST /sessions/{sid}/humanized-type` — Human typing with typos
- `POST /sessions/{sid}/humanized-scroll` — Variable-speed scrolling
- `POST /sessions/{sid}/humanized-read` — Reading simulation
- `POST /sessions/{sid}/humanized-delay` — Natural random delay
- `POST /sessions/{sid}/linkedin/start-human-session` — Begin LinkedIn session
- `POST /sessions/{sid}/linkedin/find-post` — Scroll feed for target post
- `POST /sessions/{sid}/linkedin/drop-comment` — Comment with human behavior
- `POST /sessions/{sid}/linkedin/react` — Reaction with hover menu
- `POST /sessions/{sid}/linkedin/view-profile` — Natural profile viewing
- `POST /sessions/{sid}/linkedin/end-human-session` — End session naturally

### Existing Endpoint Upgrades
- Orchestration workflow steps now support `"humanize": true` flag
- Scheduled task steps now support `"humanize": true` flag
- Convenience wrappers: `humanized_fill()`, `humanized_click()`, `humanized_scroll_by()`

## Files
- `/opt/baas/humanize.py` — New module (621 lines)
- `/opt/baas/patch_humanize.py` — Patch script used for integration
- `/opt/baas/baas_server_simple.py.bak-humanize` — Backup before patch

## Test Results
- All 5 core humanized endpoints tested and working
- Session create + navigate + humanized-scroll + humanized-delay + humanized-read + humanized-click all returned success
- Service restarted and healthy on port 8901

## Key Design Decisions
- Used dedicated `/humanized-*` endpoints rather than replacing all existing `page.click()`/`page.fill()` calls — safer rollout, existing automation keeps working
- Added `humanize` flag to orchestration/scheduled-task steps so existing workflows can opt in per-step
- LinkedInHuman is stateful per-session (tracks posts seen, actions taken, session timing)
- Bezier curves use De Casteljau for arbitrary-order evaluation (supports 3-5 control points)
- Mouse position tracked via `window._hm_x`/`window._hm_y` for continuity between calls
