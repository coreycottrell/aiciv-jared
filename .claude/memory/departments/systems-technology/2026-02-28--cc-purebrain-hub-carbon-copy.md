# cc.purebrain.ai — Hub Carbon Copy Implementation

**Date**: 2026-02-28
**Type**: pattern + architecture decision

## What Was Done

Replaced the custom sidebar dashboard in `tools/comms-gateway/main.py` with a surgical injection approach that serves the ACTUAL purebrain-hub HTML source directly.

## The Pattern: Surgical HTML Injection

The hub source (`purebrain-hub-source.html`, 187KB) is a complete self-contained HTML file. Rather than recreating it, the gateway now:

1. Reads the hub file on first request (cached in `_HUB_SOURCE_CACHE`)
2. Performs 4 surgical string replacements before serving

### Injection 1: Before `</head>`
- Injects `<script>` that pre-seeds `sessionStorage` with server session user data
- The hub's `DOMContentLoaded` reads `SESSION_KEY = 'pt_session_v4'` from sessionStorage and calls `showDashboard()` automatically
- Injects Calendar + Email CSS styles

### Injection 2: View Tabs Nav
- Replaces the `<div class="view-tabs">` block to add Calendar and Email buttons
- Exact string match required — must match the hub source exactly

### Injection 3: Before `<!-- Toast -->`
- Injects `#calendar-view` and `#email-view` divs with loading states
- These are hidden by default, shown when active

### Injection 4: Before final `</script>\n</body>`
- Overrides `window.switchView` to handle calendar/email tabs
- Overrides `window.handleLogout` to redirect to `/auth/logout` instead of just clearing sessionStorage
- Adds `gwLoadCalendar()` and `gwLoadEmail()` functions that call gateway API endpoints

## Key Gotcha: Hub Login is Client-Side

The hub originally handles auth entirely in the browser via `sessionStorage`. The gateway adds server-side session auth. The bridge: inject user data into `sessionStorage` BEFORE the hub JS runs, so `showDashboard()` is called automatically with the server-authenticated user.

## Calendar API Call
```
GET /api/calendar/events?start=YYYY-MM-DDTHH:MM:SSZ&end=YYYY-MM-DDTHH:MM:SSZ
Response: {"events": [{title, start, end, source, all_day, ...}]}
```

## Email API Call
```
GET /api/email/inbox
Response: {"messages": [{from, subject, received_at, is_read, ...}]}
```

## Files Modified
- `/home/jared/projects/AI-CIV/aether/tools/comms-gateway/main.py` — replaced 87KB dashboard function with 9KB hub-serving function

## File NOT Modified
- `api/auth.py` — login page was already a pixel-perfect match of the hub login (same design was already implemented)

## Verification
- Dashboard: 201KB served (187KB hub + 14KB injections)
- Session pre-seed: confirmed in curl test with Jared's credentials
- Calendar/Email tabs: confirmed present in output
- Logout: confirmed `/auth/logout` redirect injected
- Service: active, health 200
