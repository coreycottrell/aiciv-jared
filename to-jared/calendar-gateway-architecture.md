# Pure Technology Communications Gateway — Architecture Document

**Date**: 2026-02-28
**Author**: dept-systems-technology (Aether Engineering Team)
**Status**: DRAFT v2 — Expanded Scope (Calendar + Email)
**Task Trigger**: ST# Communications Gateway Architecture Update

---

## Executive Summary

We are building a **custom Communications Gateway** that sits between Jared's existing calendars and email (Outlook/Microsoft and Google Workspace) and all users (Jared, Aether, Mireille). This gateway is OUR infrastructure — a FastAPI service running on our existing Linux server — not a dependency on any single cloud provider.

**What changed from v1 (Calendar Gateway)**: Scope expanded to include email. The gateway now syncs and serves both calendar events AND the `jared@puretechnology.nyc` inbox. The web UI gains an Email tab alongside the Calendar tab. The name is updated accordingly to reflect the broader mission.

**Recommended Approach**: Option 3 — Hybrid (Custom Sync Engine + CalDAV Server + REST API + Email Sync)

**Total Build Time**: ~3 days of engineering work (MVP, updated for email)
**Hosting Cost**: $0 — runs on existing server
**Subdomain**: TBD — default `comms.purebrain.ai` (confirm with Jared)

---

## 1. What Changed: Calendar Gateway → Communications Gateway

| Area | v1 (Calendar Gateway) | v2 (Communications Gateway) |
|------|-----------------------|------------------------------|
| Scope | Calendar only | Calendar + Email |
| Microsoft permissions | `Calendars.ReadWrite`, `offline_access`, `User.Read` | + `Mail.Read`, `Mail.ReadWrite`, `Mail.Send`, `MailboxSettings.Read` |
| Web UI | Calendar tab only | Calendar tab + Email tab |
| Sync workers | Google Calendar + MS Calendar | + MS Mail (inbox polling) |
| Email actions | None | Mark read, flag, assign to team member |
| Email polling | N/A | Every 2 minutes (same as calendar) |
| Email real-time option | N/A | Microsoft Graph webhooks (Phase 2) |
| Subdomain | `calendar.purebrain.ai` (proposed) | `comms.purebrain.ai` (TBD, confirm with Jared) |
| Build time | ~2.5 days | ~3 days |

Everything from v1 is unchanged unless noted above.

---

## 2. Recommended Approach: Option 3 — Hybrid Architecture

### Why Option 3 Still Wins

| Concern | Option 1 (Pure CalDAV) | Option 2 (Pure Web App) | Option 3 (Hybrid) |
|---------|----------------------|------------------------|-------------------|
| Aether API access | Needs CalDAV client wrapper | Native REST — best | Native REST — best |
| iCal native support | Native CalDAV | Needs CalDAV bolt-on | CalDAV included |
| Mireille access | CalDAV credentials (technical) | Web UI or CalDAV | Web UI + CalDAV |
| Email support | Not possible | Possible | Included |
| Conflict resolution | Hard in CalDAV | Configurable | Configurable |
| Bidirectional sync | Manual polling needed | Manual polling needed | Sync daemon handles it |
| MS Outlook sync | Not native | Via Graph API | Via Graph API |

Option 3 gives us: a CalDAV endpoint for iCal (Apple Calendar) to connect natively, a REST API for Aether to call directly, a web UI for Mireille, a sync daemon that handles the bidirectional bridge to Microsoft and Google, and now a full email layer on top of the same infrastructure.

---

## 3. Architecture Diagram

```
+------------------------------------------------------------------------+
|               PURE TECHNOLOGY COMMUNICATIONS GATEWAY                   |
|               (comms.purebrain.ai -- subdomain TBD)                    |
|                                                                        |
|  +------------------------------------------------------------------+  |
|  |                       FastAPI Application                         |  |
|  |                                                                   |  |
|  |  +--------------+  +--------------+  +------------------------+  |  |
|  |  |  CalDAV      |  |  REST API    |  |  Web UI                |  |  |
|  |  |  Server      |  |  /api/v1/    |  |  (Jared + Mireille)    |  |  |
|  |  |  (Radicale)  |  |  (Aether)   |  |  /dashboard            |  |  |
|  |  +------+-------+  +------+-------+  +----------+-------------+  |  |
|  |         |                 |                       |               |  |
|  |         |                 |          +------------+-------------+ |  |
|  |         |                 |          |  Web UI Tabs             | |  |
|  |         |                 |          |  [Calendar] [Email]      | |  |
|  |         |                 |          +--------------------------+ |  |
|  |         +-----------------+-----------------------+              |  |
|  |                           v                        |              |  |
|  |                  +----------------+                |              |  |
|  |                  |  Data Store    |                |              |  |
|  |                  |  (SQLite)      |                |              |  |
|  |                  |  - events      |                |              |  |
|  |                  |  - emails      |                |              |  |
|  |                  |  - assignments |                |              |  |
|  |                  |  - users       |                |              |  |
|  |                  |  - sync_log    |                |              |  |
|  |                  +-------+--------+                |              |  |
|  |                          |                         |              |  |
|  +--------------------------|-------------------------+--------------+  |
|                             |                                          |
|  +--------------------------|------------------------------------------+ |
|  |              Sync Engine (Background Daemon)                        | |
|  |                                                                     | |
|  |  +---------------------------+   +------------------------------+   | |
|  |  | Microsoft Graph Workers   |   |  Google Calendar API         |   | |
|  |  | - Calendar sync worker    |   |  Sync Worker                 |   | |
|  |  | - Mail sync worker (NEW)  |   |  (support@puremarketing.ai)  |   | |
|  |  |   (jared@puretechnology   |   |                              |   | |
|  |  |    .nyc inbox)            |   |                              |   | |
|  |  +-------------+-------------+   +-------------+----------------+   | |
|  +----------------|-------------------------------|--------------------+ |
|                   |                               |                     |
+-------------------|-------------------------------|---------------------+
                    |                               |
                    v                               v
    +------------------------------+   +------------------------------+
    |  Microsoft / M365            |   |  Google Workspace            |
    |  jared@puretechnology.nyc    |   |  support@puremarketing.ai    |
    |  - M365 Calendar             |   |  (specific calendar)         |
    |  - M365 Inbox (NEW)          |   |                              |
    +------------------------------+   +------------------------------+

USERS:
  - Apple iCal  -- connects via CalDAV to gateway (calendar only)
  - Outlook     -- synced through Graph API (calendar + email)
  - Aether AI   -- calls REST API directly (calendar + email)
  - Mireille    -- Web UI (calendar view + email read + assignment actions)
  - Jared       -- Web UI + CalDAV + REST API (full access)
```

---

## 4. Technology Stack

| Layer | Technology | Why |
|-------|------------|-----|
| Application framework | FastAPI (Python) | Already use Python + FastAPI on this server; uvicorn already installed |
| CalDAV server | Radicale 3.x | Lightweight, pure Python, easy to embed, iCal-compatible |
| Event + email store | SQLite3 | Already available; zero dependencies; good for single-node |
| Calendar sync (MS) | Microsoft Graph API -- `/me/events` | Bidirectional Outlook calendar sync |
| Email sync (MS) | Microsoft Graph API -- `/me/messages` | Read jared@puretechnology.nyc inbox |
| Calendar sync (Google) | Google Calendar API | Already have service account + gcal_manager.py |
| Auth (users) | JWT + API keys | Simple; JWT for web UI, API key for Aether |
| Background sync | Python asyncio + APScheduler | Runs as systemd service, polls every 2 min |
| Web UI | Vanilla HTML/JS (Pure Tech styling) | No framework bloat; consistent with purebrain.ai visual language |
| Hosting | Existing Linux server | Port 8870 -- Cloudflare tunnel -- comms.purebrain.ai |
| HTTPS | Cloudflare tunnel | Already running; add one line to cloudflared config |
| Email webhooks (Phase 2) | Microsoft Graph subscriptions | Real-time email notifications instead of polling |

**No new server required. No new hosting costs.**

---

## 5. What We Build vs What Jared Sets Up

### What We Build (Engineering Team)

| Component | Description | Complexity | Time |
|-----------|-------------|------------|------|
| Gateway FastAPI app | Core app structure, routing, auth | Medium | 4h |
| SQLite event + email store | Schema: events, emails, assignments, sources, sync_log, users | Simple | 2h |
| CalDAV server (Radicale) | Embedded Radicale with custom auth hook | Medium | 3h |
| REST API -- calendar endpoints | CRUD for events, Aether-facing | Simple | 3h |
| REST API -- email endpoints | Read emails, mark read, flag, assign | Simple | 2h |
| Google Calendar sync worker | Pull/push support@puremarketing.ai calendar | Simple | 2h |
| MS Graph calendar sync worker | Pull/push jared@puretechnology.nyc calendar | Complex | 6h |
| MS Graph mail sync worker | Poll inbox /me/messages, store in SQLite | Medium | 3h |
| Conflict resolution engine | Calendar: last-write-wins with source priority | Medium | 2h |
| Web UI -- calendar tab | Month/week view, create/edit events | Medium | 4h |
| Web UI -- email tab (NEW) | Inbox view, read/unread, flags, assignment | Medium | 4h |
| Assignment system (NEW) | Assign email to Jared / Aether / Mireille | Simple | 1h |
| Mireille invite system | Account creation + CalDAV credentials page | Simple | 1h |
| Systemd service | Auto-restart, logging | Simple | 1h |
| Cloudflare tunnel entry | Add comms subdomain | Simple | 30m |

**Total MVP build: ~38h engineering time (~3 days)**

### What Jared Sets Up (One-Time Actions)

| Action | Difficulty | Time |
|--------|------------|------|
| **Microsoft Graph App Registration** -- Register app in Azure portal. Permissions: `Calendars.ReadWrite`, `Mail.Read`, `Mail.ReadWrite`, `Mail.Send`, `MailboxSettings.Read`, `offline_access`, `User.Read`. Generate client secret. Copy Application ID, Client Secret, Tenant ID. | Medium | 15-20 min |
| **Google Calendar share** -- Share the specific calendar from support@puremarketing.ai with service account `aether-drive-access@aether-integration.iam.gserviceaccount.com` (grant "Make changes to events" permission) | Simple | 2 min |
| **Domain DNS** -- Point `comms.purebrain.ai` to Cloudflare (already done for purebrain.ai -- just need to add the tunnel route) | We handle this | 0 min |
| **First OAuth consent** -- Visit `https://comms.purebrain.ai/auth/microsoft` once to complete the Microsoft OAuth flow (one-time browser redirect) | Simple | 2 min |
| **Invite Mireille** -- After gateway is live, visit `/admin/invite` and enter her email | Simple | 1 min |

---

## 6. Microsoft Graph API Requirements

### Azure Permissions -- Updated for Email

The permissions Jared is registering in Azure now cover both calendar and email:

| Permission | Type | Why |
|------------|------|-----|
| `Calendars.ReadWrite` | Delegated | Read and write Jared's M365 calendar |
| `Mail.Read` | Delegated | Read jared@puretechnology.nyc inbox |
| `Mail.ReadWrite` | Delegated | Mark messages as read, flag, move |
| `Mail.Send` | Delegated | Send email on behalf of Jared (Phase 2 feature) |
| `MailboxSettings.Read` | Delegated | Read mailbox settings (timezone, auto-reply status) |
| `offline_access` | Delegated | Get refresh token so we do not re-auth constantly |
| `User.Read` | Delegated | Get user profile for display |

All are Delegated permissions. Jared does the one-time OAuth consent; the gateway stores an offline refresh token that auto-renews as long as the gateway is running.

### App Registration Steps (Azure Portal)

1. Go to https://portal.azure.com and sign in with `jared@puretechnology.nyc`
2. Navigate to: Azure Active Directory > App registrations > New registration
3. Settings:
   - Name: `Pure Technology Communications Gateway`
   - Supported account types: `Accounts in this organizational directory only`
   - Redirect URI: `https://comms.purebrain.ai/auth/microsoft/callback` (Web platform)
4. After creation, go to: API permissions > Add a permission > Microsoft Graph > Delegated and add all seven permissions listed above
5. Go to: Certificates & secrets > New client secret
   - Description: `comms-gateway-2026`
   - Expiry: 24 months
   - **Copy the secret VALUE immediately** (shown once)
6. Record from the app Overview page:
   - Application (client) ID
   - Directory (tenant) ID
   - The client secret you copied

### What We Store (in .env)

```
MS_GRAPH_CLIENT_ID=<Application ID>
MS_GRAPH_CLIENT_SECRET=<Client Secret>
MS_GRAPH_TENANT_ID=<Tenant ID>
MS_GRAPH_REDIRECT_URI=https://comms.purebrain.ai/auth/microsoft/callback
```

---

## 7. Email Sync Layer -- How It Works

### Polling Endpoint

Every 2 minutes, the mail sync worker calls:

```
GET https://graph.microsoft.com/v1.0/me/messages
    ?$select=id,subject,from,receivedDateTime,isRead,flag,bodyPreview,body
    &$filter=receivedDateTime gt <last_sync_timestamp>
    &$orderby=receivedDateTime desc
    &$top=50
```

New messages are stored in the local SQLite `emails` table. Updated messages (read status, flag changes) are detected by comparing `lastModifiedDateTime`.

### Email Data Model

```sql
CREATE TABLE emails (
    id              TEXT PRIMARY KEY,        -- MS Graph message ID
    subject         TEXT,
    from_name       TEXT,
    from_email      TEXT,
    received_at     DATETIME,
    body_preview    TEXT,                    -- First ~255 chars
    body_html       TEXT,                    -- Full HTML body (optional)
    is_read         BOOLEAN DEFAULT 0,
    is_flagged      BOOLEAN DEFAULT 0,
    assigned_to     TEXT DEFAULT NULL,       -- 'jared' | 'aether' | 'mireille'
    ms_message_id   TEXT,                    -- Mirror of id, for clarity
    last_synced_at  DATETIME,
    folder          TEXT DEFAULT 'inbox'
);
```

### Email Actions

The gateway supports the following email actions, callable via REST API and web UI:

| Action | REST endpoint | MS Graph call |
|--------|--------------|---------------|
| List inbox | `GET /api/v1/emails` | Reads from local SQLite (fast) |
| Get single email | `GET /api/v1/emails/{id}` | Reads from local SQLite |
| Mark as read | `PATCH /api/v1/emails/{id}/read` | `PATCH /me/messages/{id}` |
| Mark as unread | `PATCH /api/v1/emails/{id}/unread` | `PATCH /me/messages/{id}` |
| Flag email | `PATCH /api/v1/emails/{id}/flag` | `PATCH /me/messages/{id}` |
| Remove flag | `PATCH /api/v1/emails/{id}/unflag` | `PATCH /me/messages/{id}` |
| Assign to team | `PATCH /api/v1/emails/{id}/assign` | Local only (stored in SQLite) |

### Assignment System

Email assignment is a gateway-native concept -- it does not sync back to Outlook. An email assigned to "Aether" means Aether should handle it. An email assigned to "Mireille" means Mireille is responsible.

```json
PATCH /api/v1/emails/{id}/assign
{ "assigned_to": "aether" }   // or "jared", "mireille", null
```

Assignments are visible in the web UI with color-coded labels.

### Email Polling Interval

Default: every 2 minutes (same as calendar sync). This is configurable per deployment.

### Phase 2: Real-Time Webhooks (Microsoft Graph Subscriptions)

Instead of polling, we can subscribe to push notifications:

```
POST https://graph.microsoft.com/v1.0/subscriptions
{
  "changeType": "created,updated",
  "notificationUrl": "https://comms.purebrain.ai/webhooks/mail",
  "resource": "/me/messages",
  "expirationDateTime": "<72h from now>"
}
```

Graph subscriptions expire every 72 hours and must be renewed. This adds complexity but eliminates the 2-minute polling lag. Scheduled for Phase 2 along with recurring calendar event support.

---

## 8. Web UI -- Email Tab

The web UI gains a second tab alongside the calendar:

### Email Tab Features

- **Inbox view**: List of recent emails, sender, subject, preview, timestamp
- **Read/unread indicator**: Bold = unread, dimmed = read
- **Flag indicator**: Flag icon, toggleable
- **Assignment badges**: Color-coded tag showing who the email is assigned to
- **Click to expand**: Full email body (HTML rendered in a sandboxed iframe)
- **Action bar**: Mark read, mark unread, toggle flag, assign dropdown (Jared / Aether / Mireille)
- **Search bar**: Client-side search across subject, sender, preview (local SQLite -- fast)
- **Pagination**: 50 emails per page

### Access by User

| User | Calendar Tab | Email Tab |
|------|-------------|-----------|
| Jared | Full (read + write) | Full (read + all actions) |
| Aether / AI | REST API (no web UI) | REST API (all actions via API) |
| Mireille | Read + create events | Read + flag + assign (no delete, no mark unread for others) |

### Mireille Email Access Scope

Mireille sees the same inbox as Jared but with limited actions: she can read emails, flag them, and assign them to a team member. She cannot mark as unread (to avoid confusion), cannot delete, cannot send. This is appropriate for an EA-style role.

---

## 9. User Access Matrix

| Feature | Jared (Web + API) | Aether (API) | Mireille (Web) |
|---------|-------------------|--------------|----------------|
| View calendar | Full | Full | Full |
| Create / edit events | Full | Full | Full |
| Delete events | Full | Full | No |
| View inbox | Full | Full | Full |
| Mark email read/unread | Full | Full | Read only (mark read) |
| Flag email | Full | Full | Full |
| Assign email | Full | Full | Full |
| Send email (Phase 2) | Full | Full | No |
| Admin (invite users) | Full | No | No |
| CalDAV credentials | Full | No | Full |
| API key management | Full | N/A | No |

---

## 10. Hosting Plan

### Current Server Ports (Occupied)

| Port | Service |
|------|---------|
| 8443 | api.purebrain.ai |
| 8765 | video.purebrain.ai |
| 8888 | Internal Python service |
| 8890 | Internal Python service |
| 8200 | Internal Python service |

### Communications Gateway

| Port | Service |
|------|---------|
| 8870 | Communications Gateway (FastAPI + Radicale) |

Add to `/etc/cloudflared/config.yml`:

```yaml
- hostname: comms.purebrain.ai
  service: http://localhost:8870
  originRequest:
    connectTimeout: 30s
```

Systemd service: `aether-comms-gateway.service`

**Disk space note**: Server is at 75% capacity (27G/38G used). SQLite database with calendar events and email previews will remain small (under 50MB for years of data). Full email bodies stored optionally (toggle in config). No concern.

---

## 11. MVP Scope vs Full Scope

### MVP -- Ship First (~3 days)

- FastAPI app on port 8870 behind `comms.purebrain.ai`
- SQLite store for events AND emails
- CalDAV endpoint -- Apple iCal connects bidirectionally
- REST API -- Aether calls calendar and email endpoints with API key
- Google Calendar sync worker (every 2 min)
- Microsoft Calendar sync worker (every 2 min)
- Microsoft Mail sync worker (every 2 min, `/me/messages`)
- Conflict resolution for calendar events
- JWT auth for web users, API key for Aether
- Web UI -- Calendar tab (month view, create/edit/delete)
- Web UI -- Email tab (inbox, read/unread, flag, assign)
- Assignment system (Jared / Aether / Mireille)
- Mireille account + invite email
- Systemd service + Cloudflare tunnel

### Full Scope -- Phase 2 (~2 weeks after MVP)

- Recurring calendar event support (RRULE parsing)
- Microsoft Graph webhooks for real-time email (no more 2-min lag)
- Google Calendar push notifications (real-time calendar)
- Email send capability via `Mail.Send` permission (already registered)
- Email reply threading view
- Availability / free-busy API for scheduling assistant
- Aether natural language interface ("schedule a call with Mireille next Tuesday at 2pm")
- Meeting invite flows (create event + send invite email via Brevo or Graph)
- Calendar analytics (how Jared spends time)
- Teams meeting link auto-generation via Graph API
- Mobile-responsive web UI
- Email filtering rules (auto-assign by sender domain, etc.)

---

## 12. Complexity Ratings

| Component | Complexity | Notes |
|-----------|------------|-------|
| FastAPI skeleton + auth | Simple | We do this routinely |
| SQLite schema (events + emails) | Simple | Standard CRUD, two tables added |
| CalDAV (Radicale) | Medium | Config + auth hook -- tricky but documented |
| REST API -- calendar | Simple | Standard CRUD |
| REST API -- email | Simple | Read + action endpoints |
| Google Calendar sync | Simple | gcal_manager.py already exists |
| MS Graph calendar sync | Complex | OAuth2 flow, token refresh, event mapping |
| MS Graph mail sync | Medium | Same OAuth token as calendar; just different endpoint |
| Email action write-back | Simple | PATCH /me/messages -- single-field updates |
| Conflict resolution | Medium | Calendar-only; email has no conflict scenario |
| Web UI -- calendar tab | Medium | Custom month view is ~300 lines of JS |
| Web UI -- email tab | Medium | Inbox list + expand + action bar |
| Assignment system | Simple | Local SQLite only, no MS Graph involved |
| Systemd + Cloudflare | Simple | Copy existing pattern from other services |
| Mireille invite system | Simple | Account create + CalDAV creds page |

**Biggest risk**: Microsoft Graph OAuth flow. Same as v1. The mail sync worker reuses the same OAuth token as the calendar worker -- no additional OAuth complexity introduced by adding email.

---

## 13. Security Considerations

### Multi-User Access

| User | Calendar Access | Email Access | Auth Method |
|------|----------------|--------------|-------------|
| Jared | Full read/write | Full read/write + actions | JWT (web) + CalDAV credentials |
| Aether AI | Full read/write | Full read/write + actions | API key (stored in .env) |
| Mireille | Full read/write | Read + flag + assign | JWT (web) + CalDAV credentials |

### Token Storage

| Secret | Storage Location | Method |
|--------|-----------------|--------|
| MS Graph client secret | .env file | Same as other secrets |
| MS Graph OAuth refresh token | .credentials/ms-oauth-token.json | Same as Google OAuth pattern |
| Google service account | .credentials/google-drive-service-account.json | Already secure |
| Aether API key | .env as COMMS_API_KEY | Auto-generated UUID on setup |
| Mireille credentials | Gateway DB (bcrypt hashed) | Standard web auth |
| JWT signing secret | .env as COMMS_JWT_SECRET | Generated on setup |

### Network Security

- Gateway only accessible via Cloudflare tunnel (no direct port exposure)
- All traffic HTTPS via Cloudflare
- CalDAV over HTTPS (Cloudflare handles TLS)
- API key header: `X-API-Key` (not query param -- avoids logging)
- JWT expiry: 24h with refresh token flow

### Email Data Privacy

- Email bodies stored locally on our server only
- Body text is NOT forwarded to third-party services
- Email sync worker is read-only from MS Graph side during MVP (write-back for read/flag status only)
- Mireille sees email content but cannot delete or export
- Full HTML bodies stored only if `STORE_FULL_EMAIL_BODIES=true` in .env (default: preview only, 255 chars)

### Threat Model

| Threat | Mitigation |
|--------|------------|
| Unauthorized calendar or email access | Auth required on all endpoints |
| Token theft | .env not in git, Cloudflare hides server IP |
| Sync loop (event bouncing) | sync_source tracking on each event prevents re-sync |
| Microsoft token expiry | Refresh token auto-renewed; alert if refresh fails |
| Data loss | SQLite WAL mode + daily backup to Google Drive |
| Email content exposure | Full bodies off by default; preview only |
| Mireille over-reach | Role-based action limits enforced at API layer |

---

## 14. Bidirectional Calendar Sync (Unchanged from v1)

### Change Detection + Source Tagging

Each calendar event in the database has:
- `gateway_uid` -- our canonical ID
- `ms_event_id` -- the ID in Microsoft
- `google_event_id` -- the ID in Google
- `last_modified_gateway` -- timestamp of last change WE made
- `last_modified_ms` -- timestamp from Microsoft's last response
- `last_modified_google` -- timestamp from Google's last response
- `source_of_truth` -- which system made the latest change

### Sync Loop (Every 2 Minutes)

```
1. Pull all events from Microsoft modified since last check
2. Pull all events from Google modified since last check
3. For each remote change:
   a. If event not in gateway: CREATE in gateway + push to other source
   b. If event in gateway and remote is newer: UPDATE gateway + push to other source
   c. If event deleted remotely: DELETE from gateway + delete from other source
4. For any gateway events modified via API/CalDAV since last sync:
   a. Push to Microsoft
   b. Push to Google
```

### Conflict Resolution Rule

Priority order: `Gateway > Microsoft > Google`

If the same event was modified on Microsoft AND Google since the last sync, and the gateway was not touched, Microsoft wins (Jared's primary work calendar). Configurable in gateway settings.

---

## 15. Recommended Build Sequence -- Updated for Email

**Day 1 (Jared does Azure registration while we build)**

Morning:
- Jared registers Azure AD app with all seven permissions (15-20 min, instructions in Section 6)
- Jared shares support@puremarketing.ai calendar with service account (2 min)

Meanwhile, we build:
1. FastAPI skeleton with auth (JWT + API key)
2. SQLite schema -- events table + emails table + assignments table
3. REST API -- calendar CRUD endpoints for Aether
4. REST API -- email read + action endpoints for Aether
5. Google Calendar sync worker (using existing gcal_manager.py pattern)

**Day 2 -- Core sync + email layer**

1. Microsoft Graph calendar sync worker (OAuth flow + calendar polling)
2. Microsoft Graph mail sync worker (same OAuth token, /me/messages polling, every 2 min)
3. Email write-back actions (mark read, flag -- PATCH to Graph API)
4. Conflict resolution engine for calendar
5. Radicale CalDAV server integration
6. Cloudflare tunnel entry + systemd service

**Day 3 -- Web UI + security review + ship**

1. Web UI -- Calendar tab (month view, create/edit/delete)
2. Web UI -- Email tab (inbox list, expand, action bar, assignment dropdown)
3. Mireille invite system + role enforcement
4. Assignment system (local SQLite, color-coded labels in UI)
5. Security review pass (security-engineer-tech)
6. End-to-end test: create event in iCal → appears in Outlook → appears in gateway UI; new email in Outlook → appears in gateway email tab → mark read from gateway → confirmed read in Outlook
7. QA sign-off (qa-engineer)
8. Ship

---

## 16. File Structure (What We Will Build)

```
tools/comms_gateway/
├── main.py                    # FastAPI app entry point
├── config.py                  # Config from .env
├── database.py                # SQLite schema + CRUD (events + emails)
├── auth.py                    # JWT + API key auth
├── models.py                  # Pydantic models for events and emails
├── api/
│   ├── events.py              # Calendar REST endpoints
│   ├── emails.py              # Email REST endpoints (NEW)
│   ├── auth_routes.py         # Login, OAuth callbacks
│   └── admin.py               # Mireille invite, user mgmt
├── sync/
│   ├── sync_daemon.py         # Background scheduler (calendar + email workers)
│   ├── google_worker.py       # Google Calendar sync
│   ├── ms_calendar_worker.py  # Microsoft Graph calendar sync
│   └── ms_mail_worker.py      # Microsoft Graph mail sync (NEW)
├── caldav/
│   └── radicale_config.py     # Radicale embedded config
├── ui/
│   ├── index.html             # Web UI entry (Calendar + Email tabs)
│   ├── calendar.js            # Month view + CRUD
│   ├── email.js               # Inbox view + actions (NEW)
│   └── style.css              # Pure Tech dark theme
└── requirements.txt
```

Systemd service: `config/aether-comms-gateway.service`

New .env variables:
```
MS_GRAPH_CLIENT_ID
MS_GRAPH_CLIENT_SECRET
MS_GRAPH_TENANT_ID
MS_GRAPH_REDIRECT_URI
COMMS_API_KEY
COMMS_JWT_SECRET
STORE_FULL_EMAIL_BODIES      # true | false (default false)
```

---

## 17. What Jared Needs to Do Before We Build

These are blocking items:

### REQUIRED -- Block 1 (15-20 min)

**Azure App Registration** -- Jared is currently doing this. Permissions to confirm are registered:
- `Calendars.ReadWrite`
- `Mail.Read`
- `Mail.ReadWrite`
- `Mail.Send`
- `MailboxSettings.Read`
- `offline_access`
- `User.Read`

All Delegated (not Application). Redirect URI: `https://comms.purebrain.ai/auth/microsoft/callback`

Once done, share with Aether: Application ID, Tenant ID, Client Secret value.

### REQUIRED -- Block 2 (2 min)

**Google Calendar share** for support@puremarketing.ai -- share the specific calendar with `aether-drive-access@aether-integration.iam.gserviceaccount.com`, permission level "Make changes to events".

### CONFIRMATION NEEDED

- **Subdomain preference**: Default is `comms.purebrain.ai`. Alternatives: `gateway.purebrain.ai`, `hub.purebrain.ai`, `comms.puretechnology.nyc`. Jared confirms.
- **Which Google calendar**: Which specific calendar on support@puremarketing.ai should sync? (Name or calendar ID -- there may be multiple.)
- **Mireille access**: Web UI only, or also CalDAV so she can sync to Apple Calendar?
- **Store full email bodies?**: Default is preview only (255 chars). Full HTML bodies stored locally if Jared wants. Adds ~2MB/month of SQLite storage for moderate inbox volume.

---

## 18. Decisions Made (Architecture)

| Decision | Choice | Reasoning |
|----------|--------|-----------|
| Storage | SQLite | Fits scale; zero ops overhead; Python sqlite3 built-in |
| CalDAV | Radicale embedded | Pure Python, tiny, iCal-compatible, no separate process |
| REST framework | FastAPI | Already deployed on this server; team knows it |
| Calendar sync method | Polling (2 min) | Reliable MVP; webhooks are Phase 2 |
| Email sync method | Polling (2 min) | Same daemon, same interval as calendar; no added complexity |
| Email write-back | PATCH via Graph API | Same OAuth token used for calendar; no new auth needed |
| Email conflict resolution | Not needed | Gateway is read-mirror for email; no bidirectional write conflict |
| Conflict resolution (calendar) | Gateway wins, then MS | Jared's primary work = M365; gateway writes take priority |
| Auth | JWT + API key | JWT for humans, key for machines |
| Hosting | Existing server | No new infrastructure needed |
| DB backup | Daily to Google Drive | Uses existing gdrive_manager.py pattern |
| Email body storage | Preview only by default | Reduces storage; full bodies optional via .env toggle |
| Assignment system | Local SQLite only | Not synced to MS/Google; internal team coordination layer |

---

## Summary

**What changed**: Calendar Gateway is now the Communications Gateway. Same architecture, same tech stack, build extends from ~2.5 days to ~3 days. Email is added as a second sync channel using the same Microsoft Graph OAuth token already required for calendar. The email tab in the web UI gives Jared and Mireille a unified view of inbox and calendar in one place.

**What it gives you**:
- `comms.purebrain.ai` (subdomain TBD) -- your own gateway
- Apple iCal connects natively via CalDAV (calendar, bidirectional)
- Outlook calendar syncs via Microsoft Graph (bidirectional)
- Outlook inbox syncs via Microsoft Graph (read + actions)
- Google Workspace calendar syncs via Google API (bidirectional)
- Aether has a clean REST API: calendar CRUD + email read/action with API key
- Mireille gets web login, calendar access, email inbox read + assignment actions
- Email assignment system: route emails to Jared / Aether / Mireille with one click
- Zero additional hosting cost

**What's needed from Jared to start**:
- Azure app registration with all 7 permissions (in progress now)
- Google Calendar share (2 min)
- Subdomain confirmation

**Build timeline**: 3 days to MVP

**Team**: full-stack-developer builds, security-engineer-tech reviews before ship, qa-engineer tests end-to-end

---

*Generated by dept-systems-technology | 2026-02-28*
*File: `to-jared/calendar-gateway-architecture.md`*
*Version: 2.0 -- Communications Gateway (Calendar + Email)*
