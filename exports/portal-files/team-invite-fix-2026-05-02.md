# Team Invite System Fix - 2026-05-02

## Summary

Fixed the team invite system at portal.purebrain.ai/admin/clients (Team Access tab).

## Problems Fixed

### 1. Invites moved from local SQLite to D1

**Before**: Invites stored in `referrals.db` → `admin_tokens` table (local, not persistent across deploys)
**After**: New invites go through the admin-api Worker → D1 `team_invites` table (persistent, production-grade)

- Portal `api_admin_invite` now proxies to `https://admin-api.in0v8.workers.dev/api/admin/invite`
- Worker generates a `token` field for dashboard URL auth
- Local SQLite still used as fast-path for token validation (backwards compat)
- D1 Worker has `/api/admin/validate-token` endpoint for token validation fallback

### 2. Invite emails now sent via Brevo

**Before**: System created a token but NEVER emailed the invitee
**After**: Branded HTML email sent via Brevo transactional API on every invite

Email includes:
- PUREBRAIN.AI branded header (dark theme, correct brand colors)
- "You've been invited!" heading
- CTA button linking to their dashboard URL
- "Sent by [invited_by]" attribution
- BCC to jared@puretechnology.nyc

### 3. Existing invites resent

All 7 current invitees received their invite emails:

| Name | Email | Status |
|------|-------|--------|
| Ahsen Awan | ahsen@puretechnology.nyc | Sent |
| Alex Seant | alex.seant@puretechnology.nyc | Sent |
| Shahbaz Ali | shahbaz@puretechnology.nyc | Sent |
| Corey Cottrell | coreycmusic@gmail.com | Sent |
| Russel Korus | russell@russellkorus.com | Sent |
| Melanie Salvador | melanie@puretechnology.nyc | Sent |
| Nathan Olson | nathan@puremarketing.ai | Sent |

## Files Modified

| File | Change |
|------|--------|
| `/home/jared/projects/AI-CIV/aether/workers/admin-api/src/worker.js` | Added token generation, name field, validate-token endpoint |
| `/home/jared/purebrain_portal/portal_server.py` | `api_admin_invite` proxies to D1 + sends Brevo email; `_is_valid_admin_token` checks D1 fallback |
| `/home/jared/purebrain_portal/.env` | Added ADMIN_TOKEN and BREVO_API_KEY |

## Architecture

```
User clicks "Invite" in Team Access tab
  → POST /api/admin/invite (portal)
    → POST admin-api Worker (D1 team_invites)
    → INSERT local SQLite (backwards compat)
    → POST Brevo API (transactional email)
  ← Returns { token, dashboard_url }

Invitee clicks email link
  → portal.purebrain.ai/admin/clients?admin_token=XXX
    → _is_valid_admin_token checks local SQLite first
    → Falls back to D1 Worker /api/admin/validate-token
    → Grants read-only access
```

## Deployment

- Admin-api Worker: deployed (Version 8ec4386e)
- Portal: restarted via systemctl (active, watchdog healthy)
- ADMIN_TOKEN secret synced on Worker
