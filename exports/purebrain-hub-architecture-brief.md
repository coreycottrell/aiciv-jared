# PureBrain Hub — Architecture Brief
## Pre-Merge Analysis: Hub Repo + cc.purebrain.ai Convergence

**Author**: cto (Aether)
**Date**: 2026-03-01
**Status**: Ready for Engineering Handoff
**Purpose**: Comprehensive technical architecture brief before merging purebrain-hub-full-repo into cc.purebrain.ai

---

## 0. FOUNDER DECISIONS — March 1, 2026

Jared reviewed the 5 open architecture questions and answered all of them. Decisions are locked and drive the sprint plan. The engineering team builds against these — no further approval needed.

### Decision Record

| # | Question | Decision | Status |
|---|----------|----------|--------|
| 1 | Domain | Stay at **cc.purebrain.ai** — no migration to app.puretechnology.ai | LOCKED |
| 2 | File storage | **GDrive only** — no local disk file storage | LOCKED |
| 3 | Team credentials | After more is built — **not Sprint 1 or 2** | LOCKED |
| 4 | Calendar/email scope | **Full team** — each of 50 users connects their OWN Microsoft AND Google accounts (multi-user OAuth) | LOCKED |
| 5 | Cross-AI endpoint | Pending — Jared asked for explanation, awaiting yes/no | PENDING |

---

### What These Decisions Mean for the Merge

**Decision 2 — GDrive Only (no local disk) — Simplifies Sprint 2**

The original brief included a local file storage path (`/home/jared/data/hub-uploads/`) and a GDrive sync job. That is now eliminated entirely. The new flow is:

```
User uploads file in browser
    --> FastAPI receives multipart upload in memory
    --> Immediately uploads to Google Drive via gdrive_manager.py
    --> Returns GDrive file URL + ID to frontend
    --> Stores GDrive URL in hub_files table (no local path column needed)
```

Sprint 2 no longer needs to provision a local upload directory, manage disk space, handle sync failures, or build a retry mechanism for local-to-GDrive sync. The `hub_files` table schema changes: drop `filename` (local path), keep `gdrive_file_id` and `gdrive_url` as the primary storage reference.

Risk 3 (File Storage Architecture) from the original brief is now resolved. Risk 5 (GDrive Sync Path) becomes the primary implementation — but it is simpler because there is no intermediate local storage step.

---

**Decision 4 — Multi-User OAuth (biggest architectural implication)**

This is the most significant structural change from the original brief. The original cc.purebrain.ai gateway had ONE Microsoft OAuth token (Jared's) and ONE Google service account (Aether's impersonating support@puremarketing.ai). Decision 4 requires each of the 50 team members to authenticate their OWN Microsoft (Outlook/Calendar) AND Google (Gmail/Calendar) accounts.

This changes three systems:

**1. Token Storage**

The current `MicrosoftToken` table stores one token. This must become per-user:

```sql
-- Replace MicrosoftToken (single row) with:
CREATE TABLE IF NOT EXISTS user_oauth_tokens (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,           -- maps to roster entry
    provider TEXT NOT NULL,          -- 'microsoft' | 'google'
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    token_expiry TEXT,
    scope TEXT,
    created_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    UNIQUE(user_id, provider)
);
```

**2. OAuth Callback Handling**

The current Microsoft OAuth flow has a single callback at `GET /auth/microsoft/callback`. For multi-user, the callback must carry state identifying WHICH user is completing the flow. The standard pattern is a `state` parameter in the OAuth request that encodes the user's session ID, validated on callback:

```
GET /auth/microsoft/login
    --> generates state = signed JWT encoding user_id
    --> redirects to Microsoft with state=...

GET /auth/microsoft/callback?code=...&state=...
    --> validates state signature
    --> extracts user_id
    --> stores token in user_oauth_tokens WHERE user_id = extracted_user_id
```

Same pattern for Google OAuth (currently service-account only — needs full OAuth2 user flow added).

**3. Per-User Sync Jobs**

The current background sync loop runs once globally (Jared's calendar, Aether's Google Calendar). With 50 users, the sync loop must iterate per user:

```python
async def sync_all_users():
    tokens = await db.query(user_oauth_tokens)
    for token_row in tokens:
        if token_row.provider == 'microsoft':
            await sync_microsoft_calendar(user_id=token_row.user_id, token=token_row.access_token)
            await sync_microsoft_email(user_id=token_row.user_id, token=token_row.access_token)
        elif token_row.provider == 'google':
            await sync_google_calendar(user_id=token_row.user_id, token=token_row.access_token)
```

Calendar and email cache tables need a `user_id` column so each user sees only their own data (and Jared/Aether can see any user's data with admin access).

**Sprint impact**: Calendar + Email integration (originally Sprint 4) must be rearchitected BEFORE it is built. The auth refactor is now a prerequisite. Recommend adding a Sprint 0.5 specifically for the auth layer rewrite before Sprint 1 backend work begins.

---

**Decision 3 — Credentials Later — Sprint 1-2 Focus on Core Platform**

The 50-person roster currently uses a simple `pureteam{name}` password pattern in `config.py`. This is not being changed now. Sprints 1 and 2 build the core platform (backend APIs, frontend migration, file upload to GDrive, task management). User management, password distribution, and onboarding flows are Sprint 3 scope.

This means Sprints 1 and 2 can be built and tested with Jared's account only. The team does not see the hub until Sprint 3 ships.

---

**Decision 5 — Cross-AI Endpoint — Pending**

The `/api/hub/external` namespace question is awaiting Jared's yes/no. The engineering team should leave this namespace unoccupied. Do not implement it, do not block it. The rest of the merge plan does not depend on this decision.

---

### Updated Architecture Decision Record

| Decision | Choice | Rationale | Source |
|----------|--------|-----------|--------|
| Backend language | Python + FastAPI | Existing gateway, Aether ecosystem is Python | Original brief |
| Frontend framework | React 18 + Vite | Already built, component model handles complexity | Original brief |
| Database | SQLite (comms.db) | Zero additional ops overhead, additive tables | Original brief |
| Auth | Gateway session system (multi-user OAuth) | 50 real users, each with own Microsoft + Google tokens | Jared 2026-03-01 |
| File storage | GDrive only — no local disk | Eliminates local storage ops overhead entirely | Jared 2026-03-01 |
| Domain | cc.purebrain.ai (no migration) | Confirmed by Jared | Jared 2026-03-01 |
| Deployment | Existing systemd + Cloudflare | Zero additional ops overhead | Original brief |
| Team credentials rollout | Sprint 3+ | Core platform first, user management second | Jared 2026-03-01 |
| Cross-AI endpoint | TBD | Awaiting Jared decision | Pending |
| Supabase | Not used | Unnecessary external dependency | Original brief |
| Netlify (for hub) | Removed | FastAPI serves static build directly | Original brief |

---

## 1. Executive Summary

Jared has sent a repo containing three separate systems built at different times — a team engagement hub MVP (React + Express), a series of dashboard HTML prototypes (v1-v4), and a portal shell. These are now being converged with the existing cc.purebrain.ai communications gateway (FastAPI + Python). The result will be Pure Technology's unified command center: one authenticated surface for task management, team communication, calendar, email, file management, and AI agent visibility.

This brief maps every component, identifies the exact overlap, and defines what a safe merge looks like technically.

---

## 2. System Inventory

### System A: PureBrain Hub MVP (the new repo)

**Location**: `/home/jared/projects/AI-CIV/aether/tools/purebrain-hub-repo/purebrain-hub-full-repo/purebrain-hub-mvp/`

**Runtime**: Node.js
**Frontend**: React 18 + Vite (dev server port 5173)
**Backend**: Express.js (port 3001)
**Database**: sql.js (SQLite compiled to WebAssembly, persisted to `hub.db`)
**Build target**: Netlify via static Vite build (`dist/`)
**Deployment config**: `netlify.toml` at repo root

**NPM dependencies**:
- React 18.2.0, React DOM 18.2.0
- React Router DOM 6.22.0
- Express 4.18.2 + express-fileupload 1.4.3
- sql.js 1.11.0 (SQLite in WebAssembly)
- axios 1.6.7
- date-fns 3.3.1
- uuid 9.0.0
- cors 2.8.5

---

### System B: cc.purebrain.ai Comms Gateway (existing)

**Location**: `/home/jared/projects/AI-CIV/aether/tools/comms-gateway/`

**Runtime**: Python 3.12
**Framework**: FastAPI + uvicorn
**Port**: 8870
**Database**: SQLite at `data/comms.db` via SQLAlchemy (async engine, aiosqlite)
**Auth**: Session-based (starlette SessionMiddleware) + API key header for Aether
**Tunnel**: Cloudflare tunnel -> `cc.purebrain.ai`

**Current API surface**:
- `GET /` — redirects to /dashboard
- `GET /dashboard` — serves full web UI (HTML injected from purebrain-hub-source.html)
- `GET /api/roster` — returns full 50-person team roster JSON
- `GET /auth/status` — returns Microsoft + Google auth status
- `GET /auth/microsoft/login` — initiates Microsoft OAuth2 PKCE flow
- `GET /auth/microsoft/callback` — handles OAuth2 callback
- `GET /api/calendar/events` — unified calendar (Microsoft + Google)
- `POST /api/calendar/events` — create calendar event
- `DELETE /api/calendar/events/{id}` — delete event
- `POST /api/calendar/sync` — trigger manual calendar sync
- `GET /api/email/inbox` — paginated inbox with unread filter
- `GET /api/email/message/{id}` — full message with body
- `POST /api/email/message/{id}/read` — mark as read
- `POST /api/email/message/{id}/flag` — flag message
- `POST /api/email/send` — send email via Microsoft Graph
- `POST /api/email/sync` — trigger manual email sync
- `GET /health` — health check
- `GET /api/docs` — FastAPI interactive OpenAPI docs

**External integrations**:
- Microsoft Graph API (OAuth2): Outlook calendar + email (jared@puretechnology.nyc)
- Google Calendar: service account with domain-wide delegation (impersonates support@puremarketing.ai)

**Database models**:
- `MicrosoftToken` — OAuth2 tokens for Microsoft Graph
- `CalendarEvent` — unified calendar cache (source: "microsoft" | "google")
- `EmailMessage` — inbox cache with full HTML/text body
- `AppState` — key-value store for miscellaneous config

---

### System C: Dashboard Versions (HTML prototypes)

**Location**: `/home/jared/projects/AI-CIV/aether/tools/purebrain-hub-repo/purebrain-hub-full-repo/dashboard-versions/`

Four self-contained HTML files (v1 through v4). v4 is the target.

**Dashboard v4 features** (183KB self-contained file):
- 3D neural canvas login with particle animation (Canvas API, no Three.js dependency)
- Full task CRUD with modal interface
- Admin panel with table + card toggle view
- Status cycling (Todo, In Progress, Blocked, Done)
- Supabase sync (for real-time data — currently a placeholder/stub)
- Team roster view with 49 members displayed
- A/B/C delegation routing visualization
- Department filter buttons
- Glass-morphism UI (backdrop-filter blur)
- Profile view per team member with task assignments
- Filter bar with search input

**Architecture note**: v4 is self-contained JS with no build step. It is the most feature-complete prototype but the hardest to merge into a component-based system. Its logic needs to be extracted and converted to React components for the merge.

---

### System D: Portal Shell (latest)

**Location**: `/home/jared/projects/AI-CIV/aether/tools/purebrain-hub-repo/purebrain-hub-full-repo/purebrain-hub-portal-latest.html`

A static HTML shell (~92KB) establishing the app layout with sidebar navigation and dark theme. This is the target visual design reference for the merged product UI — sidebar + main content area pattern with PureBrain blue/orange branding.

---

### System E: Current Live Hub (tools/purebrain_hub)

**Location**: `/home/jared/projects/AI-CIV/aether/tools/purebrain_hub/`

This is the current live React application. File structure is IDENTICAL to the repo MVP — same components, same API modules. The tools/purebrain_hub directory IS the deployed version of System A. No divergence in source was detected. The repo is the canonical source.

---

## 3. Tech Stack Comparison

| Dimension | Hub MVP (System A) | cc.purebrain.ai (System B) |
|-----------|-------------------|--------------------------|
| Language | JavaScript (Node.js) | Python 3.12 |
| Framework | React 18 + Vite (frontend), Express (backend) | FastAPI + uvicorn |
| Database | sql.js (SQLite in WASM) | SQLAlchemy + aiosqlite (SQLite) |
| Auth | Token-based (hardcoded tokens in DB) | Session-based + API key |
| Users | 4 demo users | 50-person team roster |
| Deployment | Netlify (static build) | Cloudflare tunnel + systemd |
| External APIs | Google Drive (via gdrive_manager.py) | Microsoft Graph, Google Calendar |
| Port | 3001 (backend), 5173 (dev frontend) | 8870 |
| Real-time | None | Background sync loop every 120s |

---

## 4. Feature Inventory

### Features in Hub MVP (System A) — NOT in cc.purebrain.ai

| Feature | Location | Status |
|---------|----------|--------|
| Brain Stream feed (posts/stories) | Dashboard.jsx + /api/posts | Working with sample fallback data |
| Create post with image upload | CreatePost.jsx + /api/posts (POST) | Working |
| Emoji reactions (celebrate/inspired/learned) | PostCard.jsx + /api/posts/:id/react | Working |
| Tag filtering (Safety, Quality, Efficiency, Innovation) | Dashboard.jsx | Working |
| Wins Board with impact badges | WinsBoard.jsx + /api/posts?wins_only=1 | Working |
| File upload + drag-and-drop | FileUpload.jsx + /api/files/upload | Working |
| Google Drive sync on upload | triggerGDriveSync() in server/index.js | Working (with stub fallback) |
| Top contributors leaderboard | Dashboard.jsx | Static sample data only |
| Tag distribution widget | Dashboard.jsx | Static sample data only |
| GDrive sync status widget | Dashboard.jsx | Static "last sync: just now" |
| 3D neural canvas login | Login.jsx (NeuralCanvas component) | Working — Canvas API animation |

### Features in cc.purebrain.ai (System B) — NOT in Hub MVP

| Feature | Location | Status |
|---------|----------|--------|
| Microsoft Outlook email inbox | api/email.py + sync/email_sync.py | Working (requires OAuth) |
| Send email via Microsoft Graph | POST /api/email/send | Working |
| Flag/read email | POST /api/email/message/{id}/flag | Working |
| Microsoft calendar (read/create/delete) | api/calendar.py + sync/calendar_sync.py | Working (requires OAuth) |
| Google Calendar integration | sync/calendar_sync.py + auth/google_cal.py | Working (service account) |
| Unified calendar cache | CalendarEvent table | Working |
| Session-based auth (50 team members) | api/auth.py | Working |
| API key auth for Aether | auth_or_api_key dependency | Working |
| Microsoft OAuth2 flow | auth/microsoft.py | Working |
| Background sync loop (120s) | main.py background task | Working |
| OpenAPI docs | /api/docs | Working (FastAPI auto-generated) |

### Features in Dashboard v4 (System C) — In Neither

| Feature | Notes |
|---------|-------|
| Full task CRUD with modal | Priority feature for merged product |
| Status state machine (Todo/In Progress/Blocked/Done) | Critical for AI agent task tracking |
| A/B/C delegation routing view | AI orchestration visibility |
| Admin table + card toggle view | Task management UX |
| Department filter on tasks | Operational filtering |
| Supabase sync (stub) | Needs real backend replacement |
| Profile view per team member | Team directory with task context |
| Double-check completion popup | "Are you certain?" UX — spec'd in build brief |
| Task assignment to team members | Currently not in any system |

---

## 5. Data Flow Diagrams

### 5.1 Current Hub MVP Data Flow

```
User (browser)
    |
    | HTTPS
    v
React Frontend (Netlify static)
    |                           |
    | /api/posts                | /api/files
    | /api/reactions            | /api/gdrive
    v                           v
Express Backend (port 3001)
    |                           |
    | SQL queries               | filesystem writes (ELIMINATED per Decision 2)
    v                           v
sql.js SQLite (hub.db)      uploads/ directory (ELIMINATED)
                                    |
                                    | python3 gdrive_manager.py
                                    v
                            Google Drive API
                            (Aether Inbox folder)
```

### 5.2 Current cc.purebrain.ai Data Flow

```
External request (Cloudflare tunnel: cc.purebrain.ai)
    |
    | HTTPS via Cloudflare
    v
FastAPI App (port 8870, systemd service)
    |
    +-- Session middleware (starlette)
    |       |
    |       v
    |   Auth check (50-person roster in config.py)
    |
    +-- /api/calendar/* --> sync/calendar_sync.py
    |       |                       |
    |       |               Microsoft Graph API
    |       |               (jared@puretechnology.nyc only — pre-Decision 4)
    |       |                       |
    |       |               Google Calendar API
    |       |               (service account impersonation — pre-Decision 4)
    |       |
    |       v
    |   CalendarEvent table (SQLite/aiosqlite)
    |
    +-- /api/email/* --> sync/email_sync.py
    |       |                       |
    |       |               Microsoft Graph API (Mail)
    |       |               (jared@puretechnology.nyc only — pre-Decision 4)
    |       |
    |       v
    |   EmailMessage table (SQLite/aiosqlite)
    |
    +-- /dashboard --> serves HTML UI
    |       (currently loads purebrain-hub-source.html)
    |
    +-- /api/roster --> returns config.TEAM_ROSTER
    |
    v
Background sync loop (asyncio, every 120s)
    --> sync_microsoft_calendar()
    --> sync_google_calendar()
    --> sync_inbox()
```

### 5.3 Target: Merged System Data Flow (post-Decisions 2 + 4)

```
Browser (team member)
    |
    | HTTPS (cc.purebrain.ai — confirmed, no domain migration)
    v
FastAPI App (port 8870, systemd service)
    |
    +-- Session auth (50-person roster) OR API key (Aether)
    |
    +-- /api/posts/* (NEW) --------> hub_posts + hub_reactions tables (SQLite)
    |
    +-- /api/files/* (NEW) --------> GDrive ONLY (no local disk)
    |       |                        gdrive_manager.py called in-process
    |       v                        hub_files table stores gdrive_url + gdrive_file_id
    |   Google Drive API
    |
    +-- /api/tasks/* (NEW) --------> hub_tasks table (SQLite)
    |       status: todo/in-progress/blocked/done
    |       assignee: team member or agent name
    |       delegation_tier: A/B/C
    |
    +-- /api/calendar/* (REFACTORED) -> CalendarEvent cache (per-user, post-Decision 4)
    |       user_id column added — each user sees own calendar
    |
    +-- /api/email/* (REFACTORED) ---> EmailMessage cache (per-user, post-Decision 4)
    |       user_id column added — each user sees own inbox
    |
    +-- /api/roster (EXISTING) ----> config.TEAM_ROSTER
    |
    +-- /app (NEW) --> React SPA static build (Vite dist/)
    |
    v
Background loops (asyncio)
    --> sync all users with connected Microsoft tokens (calendar + email)
    --> sync all users with connected Google tokens (calendar)
    --> (NEW) nightly task auto-population from GDrive folders
    --> (NEW) morning download split + GDrive sync

Per-user OAuth state:
    user_oauth_tokens table (user_id + provider as compound unique key)
    Microsoft: full OAuth2 PKCE flow per user
    Google: full OAuth2 user flow per user (replaces service account for calendar)
```

---

## 6. Integration Points with cc.purebrain.ai

### 6.1 What Already Bridges Them

The comms gateway currently loads its dashboard UI from `purebrain-hub-source.html`. This means cc.purebrain.ai already serves a hub-style UI. The bridge is already partially built — the merge is completing the unification, not starting from scratch.

**Key existing bridge**:
- `_load_hub_source()` in `main.py` reads the hub HTML file and serves it at `/dashboard`
- `GET /api/roster` already exposes the team roster to the Hub frontend
- The API key auth (`X-API-Key`) already allows Aether to write to the gateway programmatically
- `tools/gdrive_manager.py` is imported by the Hub backend AND used by the broader Aether system

### 6.2 Auth System Overlap — Critical Decision Point

This is the most significant structural conflict:

| Auth Layer | Hub MVP | cc.purebrain.ai |
|-----------|---------|-----------------|
| Users | 4 hardcoded (Jared, Sarah K., Marcus T., Demo) | 50-person roster in config.py |
| Auth method | Token string lookup in sql.js DB | Session cookie (starlette) |
| Jared's token | "team2025" | Password from GATEWAY_JARED_PASSWORD env |
| Aether access | Not present | API key (GATEWAY_AETHER_API_KEY) |
| Admin role | Basic "Admin" flag | is_admin: True in roster |

**Resolution**: The cc.purebrain.ai auth system wins. It has the real team roster, proper session management, and Aether API key access. The Hub MVP's token system is replaced by the gateway's session auth.

**Post-Decision 4 addition**: Both Microsoft and Google OAuth must be extended to per-user flows. A new `user_oauth_tokens` table replaces the single-user `MicrosoftToken` model. Auth callback routes must encode user state. This is a prerequisite for Calendar and Email views to work for any team member beyond Jared.

### 6.3 Database Overlap — Additive Merge

| Domain | Hub MVP Tables | Gateway Tables | Merge Decision |
|--------|---------------|----------------|----------------|
| Posts | posts (sql.js) | -- | Migrate to new `hub_posts` table in comms.db |
| Reactions | reactions (sql.js) | -- | Migrate to new `hub_reactions` table in comms.db |
| Files | files (sql.js) | -- | Migrate to new `hub_files` table in comms.db (GDrive URLs only, no local path) |
| Users | users (sql.js) | config.TEAM_ROSTER (in-memory) | Drop Hub MVP users table; use roster |
| Calendar | -- | calendar_events | Add `user_id` column; keep structure |
| Email | -- | email_messages | Add `user_id` column; keep structure |
| Auth tokens | -- | microsoft_tokens (single) | Replace with `user_oauth_tokens` (per-user, multi-provider) |
| App state | -- | app_state | Keep as-is |
| Tasks (new) | -- | -- | New `hub_tasks` table needed |

**All changes are additive migrations on comms.db. No destructive changes to existing gateway schema.**

### 6.4 Backend Language Conflict

Hub MVP backend: Node.js + Express
Gateway backend: Python + FastAPI

**Resolution**: FastAPI wins. Reasons:
1. cc.purebrain.ai is live, has real users (Jared, Aether), and is running in production
2. FastAPI has async support, proper session middleware, and OpenAPI docs
3. All Aether tools are Python — gdrive_manager.py, gmail_monitor.py, telegram_bridge.py
4. The Hub MVP Express backend is simple enough (~430 lines) to be rewritten as FastAPI routers
5. sql.js (SQLite in WASM, pure JS) is clever but unnecessary when SQLAlchemy/aiosqlite is already present

The Hub MVP's Express backend endpoints need to be rewritten as FastAPI routers and added to `tools/comms-gateway/api/`.

### 6.5 Frontend Architecture

Hub MVP: React 18 + Vite, built to static files, served by Netlify
Gateway: Currently serves a static HTML file at /dashboard

**Two valid approaches for the merge**:

**Option 1 (Recommended): React frontend, FastAPI serves static build**
- Vite builds React to `dist/`
- FastAPI mounts `dist/` as StaticFiles at `/app`
- All `/api/*` calls go to FastAPI
- No Netlify dependency — everything runs on Jared's server via Cloudflare tunnel
- This is cleaner and removes the Netlify dependency for the hub

**Option 2: FastAPI-rendered HTML (current approach extended)**
- Continue serving HTML from Python Jinja2 templates
- More work to maintain — React component model is significantly better for this UI complexity
- Only valid if React build pipeline is too heavyweight for the server

**Recommendation is Option 1**. The server already handles the API; adding StaticFiles mount for the React build is trivial.

---

## 7. What Needs to Happen for the Merge

### Sprint 0.5: Auth Layer Rewrite (NEW — required by Decision 4)

This sprint is new and is a prerequisite for Calendar and Email to work correctly for multiple users. No other sprint depends on it being complete before starting, but Calendar/Email features cannot ship until this is done.

1. Create new `user_oauth_tokens` table in comms.db (user_id + provider compound unique key)
2. Rewrite Microsoft OAuth flow: add `state` parameter encoding user_id, validate on callback, store token per-user
3. Add Google OAuth2 user flow (current service account approach replaced for calendar)
4. Update `sync_microsoft_calendar()`, `sync_microsoft_email()`, `sync_google_calendar()` to accept `user_id` + `token` parameters
5. Rewrite background sync loop to iterate over all connected users
6. Add `user_id` column to `calendar_events` and `email_messages` tables
7. Add `GET /auth/google/login` and `GET /auth/google/callback` routes
8. Add `GET /auth/status` to return per-user connection state for both providers
9. Add `GET /auth/connect` UI page — shows user which providers they have connected, with connect buttons for each

### Phase 0: Preparation (No breaking changes)

1. Copy Hub MVP `src/` into `tools/comms-gateway/frontend/` — separate from existing gateway code
2. Update `netlify.toml` Vite config to point API proxy at port 8870 (FastAPI) instead of 3001 (Express)
3. Verify `comms.db` SQLite is accessible for new table migrations

### Sprint 1 (Backend Foundation)

- Create `tools/comms-gateway/api/hub.py` with all hub endpoints (posts, reactions)
- Run migrations to create `hub_posts`, `hub_reactions` tables in `comms.db`
- Create `tools/comms-gateway/api/files.py` — GDrive-only upload (no local disk)
- Run migration for `hub_files` table (gdrive_file_id + gdrive_url as primary storage columns, no local path)
- Create `tools/comms-gateway/api/tasks.py` with task CRUD
- Run migration for `hub_tasks` table
- Add `GET /api/hub/stats` endpoint (live counts)
- Register all new routers in `main.py`
- Test via `GET /api/docs` — confirm all endpoints visible

### Sprint 2 (Frontend Migration)

- Move Hub MVP React source into `tools/comms-gateway/frontend/`
- Update all API base URLs from port 3001 to relative `/api/hub/`
- Replace token login with session login (call FastAPI auth)
- Pull roster from `GET /api/roster` — remove hardcoded users
- Remove static sample data from Dashboard.jsx — wire to `GET /api/hub/stats`
- Apply "Brains" rebrand in all UI strings
- Update FileUpload.jsx — remove local storage assumptions, confirm GDrive-only flow

### Sprint 3 (v4 Feature Integration + User Management)

- Extract task CRUD modal from v4 dashboard into `TaskModal.jsx`
- Extract delegation view into `DelegationView.jsx`
- Add Tasks view to React Router and sidebar nav
- Build double-check completion popup
- Add author_type display to post cards (show "Aether" badge vs human avatar)
- Begin team credential distribution (per Decision 3 — this is the earliest credentials are distributed)

### Sprint 4 (Calendar + Email Integration)

- Depends on Sprint 0.5 (auth layer rewrite) being complete
- Add Calendar view component (wraps `/api/calendar/events` — now per-user)
- Add Email view component (wraps `/api/email/inbox` — now per-user)
- Add "Connect your accounts" UI — surfaces Microsoft + Google OAuth connect buttons
- Add these to sidebar nav

### Sprint 5 (Build + Deploy)

- `vite build` from `tools/comms-gateway/frontend/`
- FastAPI mounts `dist/` at `/app`
- Update Cloudflare to serve `/app` as default path
- Security review (security-engineer-tech)
- QA sign-off (qa-engineer)
- Systemd restart of `aether-comms-gateway`

---

## 8. Risks and Considerations

### Risk 1: sql.js Data Loss During Migration

The Hub MVP stores data in `hub.db` (sql.js SQLite). If any production posts/reactions/files exist in this file before the migration, they need to be exported and imported into the new `hub_posts`, `hub_reactions`, `hub_files` tables in `comms.db`.

**Mitigation**: Before migration, run `python3 -c "import sqlite3; conn = sqlite3.connect('hub.db'); ..."` to inspect and dump existing data. The sql.js format IS standard SQLite binary — standard tools read it.

**Current assessment**: The Hub MVP appears to be in demo mode with sample data fallbacks. If no real production data has been written, migration is trivial.

---

### Risk 2: Authentication Token Hardcoding

The Hub MVP login component (`Login.jsx`) currently has hardcoded demo tokens (`team2025`, `safety2025`, `quality2025`, `demo`) in the frontend JavaScript. These tokens also exist in the database seed. After the merge these will be fully replaced by the session-based auth in the gateway, but during the transition period both systems may be accessible. **Do not expose the demo tokens publicly.**

**Mitigation**: Remove the `login-hint` element in `Login.jsx` that displays demo tokens in the UI (`Demo: team2025 · safety2025 · demo`).

---

### Risk 3: File Storage — RESOLVED by Decision 2

**Decision**: GDrive only. No local disk. The risk of managing upload directories, disk space, and sync failures does not exist in the target architecture. Files go directly from browser multipart upload to GDrive in one step.

**Implementation note**: gdrive_manager.py must handle in-memory byte streams (not file path strings) for this to work without touching disk. Verify the upload interface accepts `io.BytesIO` or equivalent before Sprint 1 ships.

---

### Risk 4: CORS Configuration

The Hub MVP Express server has CORS whitelisted to localhost ports (5173, 5174, 4173). Once served by FastAPI, CORS needs to include `https://cc.purebrain.ai`. The current gateway has CORS configured. Verify the `CORSMiddleware` in `main.py` includes all required origins after merge.

---

### Risk 5: Google Drive Sync Path — Simplified by Decision 2

The original risk was about the hardcoded path in Node.js:

```javascript
const GDRIVE_MANAGER = '/home/jared/projects/AI-CIV/aether/tools/gdrive_manager.py'
```

When rewriting as FastAPI Python, this becomes a direct import — no hardcoded path needed:

```python
from tools.gdrive_manager import upload_file
```

This is cleaner. Decision 2 makes GDrive the primary store, so this integration is now the critical path rather than an async sync job.

---

### Risk 6: The "Brains" Rebrand

The build brief specifies: all frontend references to "Agent" must become "Brain." The Hub MVP source code has not yet applied this rebrand. The Dashboard.jsx still uses "Agent" nowhere explicitly (it uses author_name), but the Login.jsx subtitle says "Team Engagement Hub" not "AI Command Center." The full rebrand must be applied during Sprint 2 frontend work.

**Scope**: Search all `.jsx` files for "Agent" + "agent" and update UI strings only (not backend variable names).

---

### Risk 7: Supabase Dependency in v4 Dashboard

The v4 dashboard HTML references Supabase for real-time sync. The merged system does NOT need Supabase — it has FastAPI + SQLite + background sync loops. All Supabase calls in the v4 dashboard logic must be replaced with calls to the new FastAPI `/api/hub/tasks/*` endpoints. Do not introduce a Supabase dependency.

---

### Risk 8: Static Sample Data Erosion of Trust

Dashboard.jsx contains static strings:
- `"Last sync: just now"`
- `"Files synced: 24"`
- Hardcoded contributor names (Marcus T., Sarah K., David R., Lisa M.)
- Hardcoded tag distribution counts

These must be replaced with live API data before the merged product is shown to any team member beyond Jared. A "dashboard" showing fake data is a credibility risk.

**Fix**: Add `GET /api/hub/stats` endpoint that returns real counts. Wire Dashboard.jsx to call it.

---

### Risk 9: Agent Identity Gap

The current hub has no way to distinguish a post made by Jared vs. a post made by Aether vs. a post made by content-specialist. The `author_name` field stores a string only.

The new `hub_posts` schema adds `author_type` (human | agent) and `agent_name`. This is a **first-class requirement** before the hub becomes an operational tool for the AI team. Without it, the feed is not an audit trail — it is a bulletin board.

---

### Risk 10: The Double-Check Popup

The build brief explicitly requires a "Are you certain this is complete?" modal before a task is marked done. This prevents accidental completion of tasks that agents have escalated for human review. This is a UI component that needs to be built — it does not exist in any current system.

**Implementation**: Simple React modal with confirmation text + "Yes, Complete" and "Cancel" buttons. State managed in TaskModal.jsx. API call to `POST /api/hub/tasks/{id}/complete` fires only after confirmation.

---

### Risk 11: Per-User OAuth Token Security (NEW — from Decision 4)

Storing 50 users' OAuth tokens in SQLite at-rest requires the tokens be encrypted. The current `MicrosoftToken` model stores tokens as plaintext. With 50 users' Microsoft and Google tokens in the table, a database compromise exposes all team members' email and calendar access.

**Mitigation**: Use Fernet symmetric encryption (Python `cryptography` library, key from env var `GATEWAY_TOKEN_ENCRYPTION_KEY`) to encrypt `access_token` and `refresh_token` columns before write, decrypt after read. This is one function wrapping the ORM layer and adds no meaningful latency.

**Must be in Sprint 0.5 before any user tokens are stored.**

---

## 9. Open Question

**Decision 5 — Cross-AI Endpoint (/api/hub/external)**

This is the only remaining open architecture question. Jared asked for explanation before deciding yes or no.

**What it is**: A dedicated API namespace (`/api/hub/external`) that cross-AI systems — specifically Lyra (sister AI from the A-C-Gee collective) — would call to post updates, read hub state, or coordinate tasks. The alternative is using the existing comms hub channel (hub_cli.py over file-based messaging).

**Why it matters**: The comms hub (hub_cli.py) works today for async coordination. A dedicated REST endpoint at `/api/hub/external` would allow real-time API calls from other AI systems, with proper authentication (separate API key from Aether's key), rate limiting, and an audit trail in the database.

**The decision does not block any Sprint 1-4 work.** It only affects whether the namespace is reserved now or added later.

---

## 10. Architecture Decision Record (Final)

| Decision | Choice | Rationale | Source |
|----------|--------|-----------|--------|
| Backend language | Python + FastAPI | Existing gateway, Aether ecosystem is Python | Original brief |
| Frontend framework | React 18 + Vite | Already built, component model handles complexity | Original brief |
| Database | SQLite (comms.db) | Zero additional ops overhead, additive tables | Original brief |
| Auth | Gateway session system (multi-user OAuth) | 50 real users, each with own Microsoft + Google tokens | Jared 2026-03-01 |
| File storage | GDrive only — no local disk | Eliminates local storage ops overhead entirely | Jared 2026-03-01 |
| Domain | cc.purebrain.ai (no migration) | Confirmed by Jared | Jared 2026-03-01 |
| Deployment | Existing systemd + Cloudflare | Zero additional ops overhead | Original brief |
| Team credentials rollout | Sprint 3+ | Core platform first, user management second | Jared 2026-03-01 |
| Token encryption at rest | Fernet symmetric encryption | 50 users' OAuth tokens require protection | Risk 11 |
| Cross-AI endpoint | TBD | Awaiting Jared decision | Pending |
| Supabase | Not used | Unnecessary external dependency | Original brief |
| Netlify (for hub) | Removed | FastAPI serves static build directly | Original brief |

---

## Memory Written

**Path**: `/home/jared/projects/AI-CIV/aether/.claude/memory/agent-learnings/cto/2026-03-01--purebrain-hub-merge-architecture-brief.md`
**Type**: synthesis + teaching
**Topic**: Full architecture analysis of Hub repo vs cc.purebrain.ai — what overlaps, what conflicts, and the complete merge plan with Jared's decisions locked in

**Updated**: 2026-03-01 — Added Section 0 with Jared's 5 decisions, multi-user OAuth architecture implications, GDrive-only file storage flow, Sprint 0.5 auth rewrite, Risk 11 (token encryption), and updated data flow diagram.

---

*Brief prepared by: cto (Aether)*
*Output file: `/home/jared/projects/AI-CIV/aether/exports/purebrain-hub-architecture-brief.md`*
