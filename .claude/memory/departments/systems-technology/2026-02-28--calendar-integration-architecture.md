# Calendar Integration Architecture Research
**Date**: 2026-02-28
**Type**: architecture | research | recommendation
**Status**: Complete — Deliverable produced

---

## Key Findings

### Our Google Calendar Setup (Current State)
- Auth type: **Service Account** (aether-drive-access@aether-integration.iam.gserviceaccount.com)
- Project: aether-integration
- **No OAuth token exists** — service account cannot write to Jared's personal Google Calendar without domain-wide delegation OR Jared sharing the calendar with the service account email
- Tool: `tools/gcal_manager.py` + `tools/gcal_oauth_setup.py`
- OAuth setup path: `.credentials/oauth-token-calendar.json` (does not exist yet)
- **Fix needed**: Either (a) OAuth flow for Jared's account, or (b) Jared shares calendar with service account email

### The Apple iCal Problem (The Hard Constraint)
- Apple has NO public Calendar API
- CalDAV is the ONLY programmatic access method for iCloud Calendar
- iCloud CalDAV endpoint: `caldav.icloud.com` (port 443)
- Requires Apple ID + app-specific password
- This means Aether CANNOT directly write to iCal/iCloud — only via CalDAV

### Google Calendar CalDAV
- Google supports CalDAV at: `https://apidata.googleusercontent.com/caldav/v2/{calid}/events`
- Apple Calendar app can connect to Google Calendar via CalDAV — THIS IS BIDIRECTIONAL
- Apple Calendar ↔ Google CalDAV = true read/write sync

### Microsoft Outlook
- Microsoft Graph API: full read/write calendar access
- Requires OAuth2 with Microsoft account
- Outlook can subscribe to external ICS feeds (READ-ONLY)
- True bidirectional = must use Graph API or EAS (Exchange ActiveSync)

---

## Recommended Architecture: Google Calendar as Hub + CalDAV Bridge

### The Winning Pattern
1. Google Calendar = source of truth (Aether has full API access)
2. Apple Calendar connects to Google via CalDAV (bidirectional, native macOS feature)
3. Outlook connects to Google via CalDAV (bidirectional, supported by Outlook for Mac)
4. Aether writes to Google Calendar → changes flow to both Apple and Outlook automatically

### What Jared Does (One-Time)
- Add Google account to Apple Calendar (System Preferences > Internet Accounts > Google) — enables CalDAV
- Add Google account to Outlook for Mac — enables CalDAV sync
- Share his Google Calendar with service account email (if using service account path)

### What We Do
- Run `python3 tools/gcal_oauth_setup.py` to get OAuth token for Jared's account
- OAuth gives Aether full owner-level access to Jared's Google Calendar
- All calendar operations via `tools/gcal_manager.py`

---

## Three-Way Sync Options Comparison

| Option | Bidirectional | Aether Access | Cost | Complexity |
|--------|--------------|---------------|------|------------|
| Google as hub + CalDAV | YES (all 3) | Full via OAuth | Free | Low |
| Third-party (SyncGene) | YES | Indirect | $4-8/mo | Low |
| Custom daemon (3 APIs) | YES | Full | Free | High |
| ICS subscription | Read-only | N/A | Free | None |

---

## Gotchas

1. **Service account cannot directly manage user calendars** — needs calendar shared with it, OR use OAuth
2. **Apple CalDAV sync has ~1-5 min lag** — not real-time, but close enough for scheduling
3. **Outlook ICS subscriptions are READ-ONLY** — must use CalDAV account, not ICS feed
4. **iCloud-to-Google requires third-party** if Apple is the source of truth — keep Google as hub
5. **OAuth token expires** — gcal_manager.py auto-refreshes if refresh_token is stored

---

## Action Items to Activate
1. Jared: run OAuth setup `python3 tools/gcal_oauth_setup.py` (browser flow, 2 min)
2. Jared: on Mac, add Google account to System Preferences > Internet Accounts (enables Apple Calendar ↔ Google CalDAV)
3. Jared: in Outlook for Mac, add Google account (File > Add Account > Google)
4. Aether: verify `python3 tools/gcal_manager.py auth-info` shows `oauth` not `service_account`
5. Done — all three calendars sync through Google as hub

---

## Related Files
- Skill: `.claude/skills/google-calendar/SKILL.md`
- Tool: `tools/gcal_manager.py`
- OAuth setup: `tools/gcal_oauth_setup.py`
- Deliverable: `exports/departments/systems-technology/2026-02-28--calendar-integration-architecture.md`
