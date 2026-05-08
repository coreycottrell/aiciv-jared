# Team Invite System: D1 Migration + Brevo Email

**Date**: 2026-05-02
**Type**: operational
**Topic**: Portal team invite system fixed to use D1 + send emails

## Key Facts

- Admin-api Worker URL: `https://admin-api.in0v8.workers.dev`
- CF account workers subdomain: `in0v8`
- ADMIN_TOKEN for Worker auth: stored in portal `.env` and as Worker secret
- Brevo API key: in aether `.env` (line 82) and portal `.env`
- Portal bearer token file: `/home/jared/purebrain_portal/.portal-token`
- Portal systemd service: `aether-portal.service`
- Portal env file: `/home/jared/purebrain_portal/.env`

## Architecture

- New invites: portal -> D1 Worker (creates invite + token) -> local SQLite (compat) -> Brevo email
- Token validation: local SQLite first -> D1 Worker `/api/admin/validate-token` fallback
- Existing invites (pre-fix): tokens only in local SQLite, still valid

## Gotchas

- Worker secrets must be set via `wrangler secret put` (not in wrangler.toml)
- The CF account uses deprecated env vars (CF_API_KEY/CF_API_TOKEN) — need to export CLOUDFLARE_API_TOKEN for deploy
- Existing D1 team_invites (created before this fix) have no `token` column populated — those use a different auth path
- ALTER TABLE in Worker is idempotent (wrapped in try/catch)
