# PureBrain Command Center v4 — Hub Merge

**Date**: 2026-02-28
**Type**: architecture + build
**Agent**: dept-systems-technology

---

## What Was Built

Merged two platforms into a single unified Command Center at `cc.purebrain.ai`:

1. **comms-gateway** (existing) — Calendar sync, Email inbox, OAuth, session auth
2. **purebrain-hub** (new) — Glass-morphism login, Task management, Team roster, Supabase

Result: Single FastAPI app serving all functionality from `tools/comms-gateway/`

---

## Files Modified

- `/home/jared/projects/AI-CIV/aether/tools/comms-gateway/main.py` — Complete rewrite (v4.0.0). Full merged UI served as inline HTML from `/dashboard` endpoint.
- `/home/jared/projects/AI-CIV/aether/tools/comms-gateway/config.py` — Extended from 3 hardcoded users to full 50-person TEAM_ROSTER. Builds `USERS` dict + `USERS_BY_DISPLAY_NAME` dict.
- `/home/jared/projects/AI-CIV/aether/tools/comms-gateway/api/auth.py` — New glass-morphism login page. Extended login POST to resolve username from `display_name` field (typeahead autocomplete flow).

---

## Architecture Decisions

### Login flow
- Hub originally: JS-side auth (roster hardcoded in HTML, session in sessionStorage)
- New: Server-side session auth (FastAPI SessionMiddleware, session in HttpOnly cookie)
- Login page: POST `/auth/login` with `username` (hidden field populated by autocomplete) + `password`
- Fallback: if hidden `username` not set, resolves from `display_name` field via USERS_BY_DISPLAY_NAME

### Supabase task backend
- Still entirely client-side (localStorage + Supabase REST API calls from browser)
- No server-side task storage — Supabase credentials entered in Settings tab, stored in localStorage
- URL/key saved under `pt_supabase_cfg_v1` localStorage key

### Navigation
- 6 tabs: Dashboard, Tasks, Calendar, Email, Team, Settings
- Panel switching via `switchPanel()` JS function (show/hide `panel-*` divs)
- Team tab is full-height (flex row: roster panel + profile panel)

### Multi-user per-tab routing
- IS_ADMIN JS const injected server-side based on session role
- Admin sees all tasks; non-admin sees only tasks assigned to their display_name
- Team roster shows full 50 people with dept filtering

---

## Key Patterns

- Inline HTML pattern maintained (no separate template files)
- `roster_json` serialized server-side, injected as JS const in dashboard HTML
- Backups: `main.py.bak` and `config.py.bak` exist in same directory

---

## Verification Results

```
GET /health          -> 200 {"status":"ok","version":"4.0.0"}
GET /               -> 303 /auth/login
GET /auth/login     -> 200 (glass-morphism login page with neural canvas)
POST /auth/login (jared/puretech2026) -> 303 /
GET /dashboard (with session) -> 200 (full 6-tab UI)
GET /api/roster      -> 50 team members
Wrong password       -> 303 /auth/login?error=...
Timothy login        -> 303 / (success)
```

---

## Service

- systemd: `aether-comms-gateway`
- Port: 8870
- Tunnel: Cloudflare -> cc.purebrain.ai
- Restart: `sudo systemctl restart aether-comms-gateway`
