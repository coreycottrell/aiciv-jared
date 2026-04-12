# Custom Calendar Gateway Architecture Decision
**Date**: 2026-02-28
**Type**: architecture | decision | infrastructure
**Status**: Architecture complete — awaiting Jared's Azure app registration before build

---

## What Was Decided

Jared wants a CUSTOM calendar gateway — our own infrastructure, not Google Calendar as hub.
This supersedes the earlier "Google as hub" recommendation from the same date.

## Architecture Choice: Option 3 — Hybrid

- FastAPI app on port 8870 → Cloudflare tunnel → `calendar.purebrain.ai`
- Radicale CalDAV server embedded in the FastAPI app (for iCal native sync)
- SQLite event store as the master/canonical data source
- Sync engine (background daemon, 2-min polling) bridging to:
  - Microsoft Graph API (jared@puretechnology.nyc M365 calendar)
  - Google Calendar API (support@puremarketing.ai specific calendar)
- REST API for Aether (JWT + API key auth)
- Web UI for Jared and Mireille

## Key Technical Facts

- Port chosen: 8870 (others in use: 8443, 8765, 8888, 8890, 8200)
- Google service account: aether-drive-access@aether-integration.iam.gserviceaccount.com
- Existing gcal_manager.py can be reused for Google sync worker
- Microsoft Graph requires Azure AD app registration by Jared (BLOCKING)
- Radicale: not yet installed — needs `pip install radicale`
- caldav, icalendar, msal packages: not yet installed

## Blocking Items Before Build

1. Jared registers Azure AD app at portal.azure.com (15 min)
   - App: "Pure Technology Calendar Gateway"
   - Permissions: Calendars.ReadWrite, offline_access, User.Read
   - Redirect URI: https://calendar.purebrain.ai/auth/microsoft/callback
   - Needs to share: App ID, Tenant ID, Client Secret
2. Jared shares support@puremarketing.ai calendar with service account
3. Jared confirms subdomain (calendar.purebrain.ai vs cal.puretechnology.nyc)
4. Jared confirms which specific calendar from support@puremarketing.ai

## Conflict Resolution Rule

Gateway writes win. If gateway not touched: Microsoft > Google.
Priority: `Gateway > Microsoft > Google`

## Build Sequence (Once Jared Provides Azure Creds)

Day 1: FastAPI skeleton + SQLite schema + REST API + Google sync worker
Day 2: Microsoft Graph sync worker + CalDAV (Radicale) + Cloudflare tunnel + systemd
Day 3: Web UI + Mireille invite system + E2E test + security review + ship

## Files

- Architecture doc: `to-jared/calendar-gateway-architecture.md`
- Future build location: `tools/calendar_gateway/`
- Future systemd: `config/aether-calendar-gateway.service`

## Complexity Summary

Simple: REST API, SQLite, systemd, Cloudflare tunnel entry, Google sync
Medium: CalDAV/Radicale integration, conflict resolution, web UI
Complex: Microsoft Graph OAuth2 flow + token refresh management

## Estimated Build Time

~28 engineering hours for MVP (3 days with parallel work)
Phase 2 (webhooks, recurring events, NL interface): ~2 additional weeks
