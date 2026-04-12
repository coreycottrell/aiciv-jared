# Per-User Google OAuth Calendar + Email Isolation

**Date**: 2026-03-21
**Type**: operational + teaching
**Topic**: Per-user OAuth 2.0 isolation for cc.purebrain.ai calendar and email tabs

---

## What Was Built

Full per-user Google Calendar OAuth 2.0 flow for cc.purebrain.ai Command Center.
Each team member connects their own Google account. Zero data leakage between users.

---

## Files Created

- `tools/comms-gateway/auth/google_oauth.py` — Full per-user OAuth 2.0 flow
  - `build_google_auth_url()` — builds consent screen URL
  - `exchange_code_for_tokens()` — exchanges auth code for tokens
  - `refresh_access_token()` — refreshes expired access token
  - `save_google_token()` — upserts token to DB
  - `get_valid_google_token()` — gets valid token, auto-refreshes
  - `has_google_token()` — quick check if user is connected
  - `revoke_google_token()` — removes token (disconnect)

---

## Files Modified

- `tools/comms-gateway/models.py`:
  - Added `UserOAuthToken` table (user_email, provider, access_token, refresh_token, expires_at)
  - Added `owner_email` column to `CalendarEvent`
  - Added `owner_email` column to `EmailMessage`

- `tools/comms-gateway/config.py`:
  - Added `GOOGLE_OAUTH_CLIENT_ID` (from env)
  - Added `GOOGLE_OAUTH_CLIENT_SECRET` (from env)
  - Added `GOOGLE_OAUTH_REDIRECT_URI = "https://cc.purebrain.ai/auth/google/callback"`

- `tools/comms-gateway/api/auth.py`:
  - Replaced stub `/auth/google/login` with full OAuth redirect
  - Added `/auth/google/callback` — exchanges code, stores token, kicks off sync
  - Added `/auth/google/disconnect` — removes token
  - Added `/auth/google/status` — checks if user is connected

- `tools/comms-gateway/api/calendar.py`:
  - `list_events` now checks `has_google_token()` for current user
  - Returns `{connect_required: true}` if no token — triggers Connect UI in browser
  - Passes `owner_email` to `get_events()` so users only see their own events

- `tools/comms-gateway/api/email.py`:
  - `inbox` endpoint filters by `owner_email`
  - Returns `{connect_required: true}` for non-Jared users without email connected
  - Jared continues to see his Microsoft emails (unchanged behaviour)

- `tools/comms-gateway/sync/calendar_sync.py`:
  - `_upsert_ms_event()` and `_upsert_google_event()` now accept `owner_email` param
  - `get_events()` accepts `owner_email` filter param
  - NEW: `sync_google_calendar_for_user(db, user_email)` — per-user Google sync using OAuth token
  - NEW: `_upsert_google_event_for_user()` — upserts with user-specific key (external_id + owner_email)

- `tools/comms-gateway/sync/email_sync.py`:
  - `get_inbox()` accepts `owner_email` filter param
  - Existing rows default to Jared's email

- `tools/comms-gateway/main.py`:
  - `gwLoadCalendar()` JS: checks `data.connect_required`, shows "Connect Google Calendar" button
  - `gwLoadEmail()` JS: checks `data.connect_required`, shows "Connect Outlook" button
  - Calendar/email view subtitles updated to "each team member sees only their own"

---

## DB Migration

Run via direct SQLite:
```python
ALTER TABLE calendar_events ADD COLUMN owner_email VARCHAR(255);
ALTER TABLE email_messages ADD COLUMN owner_email VARCHAR(255);
UPDATE calendar_events SET owner_email = 'jared@puretechnology.nyc';
UPDATE email_messages SET owner_email = 'jared@puretechnology.nyc';
CREATE TABLE user_oauth_tokens (...);
```

2149 existing calendar events retroactively tagged as Jared's.

---

## CRITICAL: Google OAuth Credentials Still Needed

The code is fully built but GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET
are blank in .env. Jared must:

1. Go to https://console.cloud.google.com/apis/credentials
2. Create OAuth 2.0 Client ID (Web application)
3. Add redirect URI: https://cc.purebrain.ai/auth/google/callback
4. Copy Client ID and Secret to .env:
   ```
   GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
   GOOGLE_OAUTH_CLIENT_SECRET=GOCSPX-your-secret
   ```
5. Restart comms-gateway: `kill $(fuser 8870/tcp); cd tools/comms-gateway && python3 main.py &`

Without these, /auth/google/login returns a 503 "Not Configured" page.

---

## Isolation Architecture

```
User A logs in:
  GET /api/calendar/events
  -> checks user_oauth_tokens for user_a@email.com
  -> not found -> returns {connect_required: true}
  -> UI shows "Connect Google Calendar" button

User A clicks Connect:
  GET /auth/google/login
  -> session stores user_a@email.com
  -> redirects to Google consent
  -> /auth/google/callback stores token for user_a@email.com
  -> syncs user_a's calendar (tagged owner_email = user_a@email.com)

User A visits calendar:
  GET /api/calendar/events
  -> has token -> passes owner_email filter
  -> returns ONLY user_a's events

Jared visits calendar:
  GET /api/calendar/events
  -> has token (from Google OAuth)
  -> returns ONLY jared@puretechnology.nyc events
  -> The 2149 existing service-account events are still his
```

---

## Verification

```bash
# All checks pass
curl http://localhost:8870/health  # 200 OK
curl http://localhost:8870/auth/google/status  # {"connected": false}
curl http://localhost:8870/auth/google/callback?error=test  # Error page HTML
# DB: user_oauth_tokens exists, 2149 events tagged as Jared
```

---

## Pattern: connect_required API Pattern

When a data endpoint requires user-specific auth setup, return:
```json
{"data": [], "connect_required": true, "message": "Connect your X to see data"}
```
The frontend checks `data.connect_required` and shows the appropriate connect button.
This is cleaner than a 401/403 error and allows graceful empty states.
