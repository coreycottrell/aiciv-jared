# Referrals API Worker - Session/Auth Endpoints Added

**Date**: 2026-04-30
**Type**: operational
**Agent**: full-stack-developer

## What Was Done

Added 4 session/auth endpoints to the referrals-api Cloudflare Worker to move login/session management from local SQLite to D1.

### New Endpoints
1. **POST /session** - Login with email/code + password, returns session token (7-day TTL)
2. **POST /forgot-password** - Generate reset token, return it + email for portal SMTP sending
3. **POST /reset-password** - Verify reset token (1hr TTL), update password hash
4. **GET /verify-session?token=XXX** - Validate session token, return referral_code

### Key Decisions / Gotchas
- **D1 schema discovery**: The existing `sessions` table uses `token` (not `session_token`) and `referrer_id` (not `referral_code`). Similarly `password_reset_tokens` uses `referrer_id` not `referral_code`/`email`. Had to match worker code to actual D1 schema.
- **Password hashing**: SHA-256 in Worker (no bcrypt in CF Workers without wasm). Legacy `salt:hexdigest` format also supported for verification. Bcrypt hashes ($2b$) return false — portal handles those via fallback.
- **SMTP limitation**: CF Workers can't send email. `/forgot-password` returns `_reset_token` + `_email` in response so the portal proxy can handle SMTP sending.
- **Session creation stores referrer_id**: JOINs with referrers table on verify to get referral_code.

### Files
- `/home/jared/projects/AI-CIV/aether/workers/referrals-api/src/worker.js` - updated worker (29.46 KiB)
- `/tmp/portal-referral-proxy-patch.py` - portal proxy integration instructions

### Verification
- Wrangler dry-run: PASS (29.46 KiB / gzip: 5.28 KiB)
- D1 tables confirmed: `sessions` and `password_reset_tokens` both exist with matching schemas
