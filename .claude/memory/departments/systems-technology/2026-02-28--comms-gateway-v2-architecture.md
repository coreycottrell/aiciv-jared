# Communications Gateway v2 Architecture

**Date**: 2026-02-28
**Type**: architecture decision
**Agent**: dept-systems-technology

## Summary

Expanded Calendar Gateway into Communications Gateway. Same FastAPI + SQLite + Cloudflare stack. Added email sync layer on top.

## Key Decisions

- Name: Communications Gateway (was Calendar Gateway)
- Subdomain: comms.purebrain.ai (TBD, Jared to confirm)
- Email sync: Microsoft Graph /me/messages, polled every 2 min (same interval as calendar)
- Email write-back: PATCH /me/messages -- same OAuth token as calendar, no new auth flow needed
- Email assignment: Gateway-local (SQLite only, not synced to Outlook)
- Email bodies: Preview only (255 chars) by default; full HTML optional via STORE_FULL_EMAIL_BODIES .env toggle
- Port: 8870 (unchanged from v1 plan)
- Build time: ~3 days (was ~2.5 days)

## Azure Permissions (Jared registering now)

Calendars.ReadWrite, Mail.Read, Mail.ReadWrite, Mail.Send, MailboxSettings.Read, offline_access, User.Read
All Delegated. Redirect URI: https://comms.purebrain.ai/auth/microsoft/callback

## New Components vs v1

- ms_mail_worker.py -- polls inbox every 2 min
- emails table in SQLite
- assignments table in SQLite
- REST API: /api/v1/emails/* endpoints
- Web UI: email.js tab (inbox, read/flag/assign)

## File

to-jared/calendar-gateway-architecture.md (v2, 700 lines)
