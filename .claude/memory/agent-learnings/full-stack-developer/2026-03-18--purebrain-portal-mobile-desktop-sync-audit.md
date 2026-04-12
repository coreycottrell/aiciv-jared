# Memory: PureBrain Portal Mobile/Desktop Sync Audit

**Date**: 2026-03-18
**Agent**: full-stack-developer
**Type**: operational
**Topic**: Which portal features sync across devices vs. stay device-local (localStorage)

---

## Summary

Full audit of portal-pb-styled.html (16,595 lines) + portal_server.py (5,898 lines) for cross-device state synchronization.

## SYNCS (Server-Side)

- **Chat history** — JSONL files on server (`portal-chat.jsonl`, Claude session logs). `/api/chat/history` returns last 200 messages. Full cross-device sync.
- **File uploads** — Written to `~/portal_uploads/` on server. Served via `/api/chat/uploads/{filename}`. Syncs.
- **Agent status/tasks** — SQLite (`agents.db`). Full CRUD via `/api/agents`. Syncs.
- **Scheduled tasks** — JSON file (`scheduled_tasks.json`) + in-memory list. `/api/scheduled-tasks`. Syncs.
- **Referral dashboard** — SQLite (`referrals.db`). Full API at `/api/referral/*`. Syncs.
- **Reactions (sentiment log)** — Server has `/api/reaction` POST endpoint that writes to `reaction-sentiment.jsonl`. BUT: the reaction display state (which emoji YOU added) is stored in `purebrain_reactions` localStorage. So server gets the log, but the client display state does not sync.
- **Voice settings (partial)** — `elevenlabs_api_key`, `elevenlabs_voice_id`, `hmi_engine`, `hmi_send_word` are synced to `/api/settings` → `user-settings.json`. Server wins on first load if local is empty; local wins if already set.

## DOES NOT SYNC (localStorage Only)

| localStorage Key | What It Stores |
|---|---|
| `portal_token` / `pb_token` | Auth bearer token — must be manually entered on each device |
| `purebrain_bookmarks` | Bookmarked messages — device-local, no server endpoint |
| `purebrain_reactions` | Which emoji reactions YOU applied — display state only |
| `purebrain_portal_cmds` | Custom quick-commands / shortcuts — device-local |
| `pb_last_seen_version` | Which release notes version user last saw |
| `hmi_browser_voice_name` | Browser TTS voice selection — device-local (browser voices differ per device) |
| `pb_referral_code` | Cached referral code (also on server, but read from localStorage first) |
| `pb_user_email` / `pb_user_name` | Cached identity info |

## Authentication Model

- Single static bearer token stored in `.portal-token` file on server
- Same token must be entered/pasted on every device separately
- Token stored in `portal_token` localStorage key after login
- **Note**: There are THREE token key names in use: `portal_token`, `pb_token`, `purebrain_token` — inconsistency bug. `purebrain_token` appears only in the reaction fetch (line 10022) and is likely always empty.
- Multiple devices CAN be logged in simultaneously with the same token — no session conflict

## Settings Sync Behavior (Partial/Nuanced)

The `/api/settings` endpoint uses a "first seen wins" merge strategy:
- If server has a value and local doesn't → pull from server
- If local has a value and server doesn't → push to server
- If BOTH have values → local wins (no override from server)
- This means: setting changed on Device A won't propagate to Device B if Device B already set the same key

## Responsive Design

- Has `<meta name="viewport" content="width=device-width, initial-scale=1.0">`
- Multiple breakpoints: 480px, 600px, 768px, 769px
- Touch events: `touchstart`, `touchmove`, `touchend` handlers present
- `-webkit-overflow-scrolling: touch` on scrollable areas
- `touch-action: pan-y` on main content areas

## Key Findings for Cross-Device Fix

1. **Bookmarks** need a server endpoint (`/api/bookmarks` GET/POST/DELETE) + migration from localStorage
2. **Custom commands** (`purebrain_portal_cmds`) need server storage
3. **Reactions display state** is partially server-logged but not retrieved per-user
4. **Settings sync** has a conflict: local-wins means Device B never gets updates from Device A after initial setup
5. **Token distribution** is the biggest UX friction — no magic link / email-based auth

## Files Audited

- `/home/jared/purebrain_portal/portal-pb-styled.html` (frontend)
- `/home/jared/purebrain_portal/portal_server.py` (backend)
