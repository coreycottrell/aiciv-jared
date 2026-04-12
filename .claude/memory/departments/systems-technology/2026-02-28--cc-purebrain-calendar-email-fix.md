# cc.purebrain.ai Calendar and Email Fix

**Date**: 2026-02-28
**Type**: bug-fix + root-cause
**System**: comms-gateway at port 8870

---

## Root Causes Found

### Issue 1: fetch() missing credentials (CRITICAL - PRIMARY BUG)
- `gwLoadCalendar()` and `gwLoadEmail()` called `fetch(url)` without `{credentials: 'include'}`
- Browser sessions use cookies — without this flag, the cookie is NOT sent
- Server returns 401, JS catches it silently (`.catch` shows "Could not load" but actually it was auth failure)
- **Fix**: Added `{credentials: 'include'}` to both fetch calls
- **File**: `/home/jared/projects/AI-CIV/aether/tools/comms-gateway/main.py` (INJECTION 4 JS block)

### Issue 2: Email sender field mismatch
- JS used `msg.from || msg.sender || msg.from_name`
- API `to_dict()` returns `sender_name` and `sender_email` (not `from`)
- **Fix**: Changed to `msg.sender_name || msg.sender_email || msg.from || 'Unknown'`

### Issue 3: No Microsoft OAuth token (Email is 0)
- Database has 0 rows in `microsoft_tokens` table
- Email sync always skips: `[MS-AUTH] No token found for jared@puretechnology.nyc`
- **Required action**: Jared must do OAuth flow at `https://cc.purebrain.ai/auth/microsoft/login`
- Once complete, email will auto-sync every 2 minutes
- Google Calendar is working fine (1,845+ events synced, 127 in current week)

### Issue 4: Mobile CSS gaps
- `.gw-event-card` needed `flex-wrap: wrap` on mobile
- `.gw-event-time-block` needed row layout on mobile
- `.gw-event-divider` hidden on mobile
- Date picker bar needed to stack vertically
- All added to `@media (max-width: 768px)` block

---

## State After Fix

| Component | Before | After |
|-----------|--------|-------|
| Calendar events via API | 0 (401 silently) | 127 events this week |
| Calendar UI display | Empty | Populated |
| Email sync | 0 (no MS token) | 0 (awaiting OAuth) |
| Email UI | Empty | Shows "Connect Outlook" link |
| Mobile calendar | Cards overflow | Cards stack cleanly |
| Mobile email | Layout broken on small screens | Stacks properly |

---

## DB State
- `calendar_events`: 1,848 rows (all Google Calendar)
- `email_messages`: 0 rows (Microsoft OAuth not yet done)
- `microsoft_tokens`: 0 rows

---

## Action Required from Jared
Visit: `https://cc.purebrain.ai/auth/microsoft/login`
This starts the Microsoft OAuth2 flow to authorize Outlook Calendar + Email sync.
After completion, email will sync within 2 minutes automatically.

---

## Pattern: Always add credentials:include to fetch calls
When FastAPI uses `SessionMiddleware` (cookie-based auth), ALL browser `fetch()` calls
to authenticated endpoints MUST include `{credentials: 'include'}` or the cookie won't be sent.
This is a common gotcha when building SPAs on top of session-auth backends.
