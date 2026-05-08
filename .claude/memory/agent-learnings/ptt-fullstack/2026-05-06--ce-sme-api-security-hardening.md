# CE SME API Security Hardening

**Date**: 2026-05-06
**Type**: operational
**Agent**: full-stack-developer

## What Was Done

Applied 7 security fixes to `/home/jared/projects/AI-CIV/aether/workers/ce-sme-api/src/worker.js`:

1. **CRITICAL - PBKDF2 password hashing**: Replaced unsalted SHA-256 with PBKDF2 (100k iterations, 16-byte random salt). Added `verifyPassword()` with legacy hash detection and auto-upgrade on login.

2. **Rate limiting**: D1-backed via `rate_limits` table. Login=5/min/IP, Register=3/hr/IP, AI endpoints=20/hr/user. Fails open for availability.

3. **Session hardening**: 30-day sessions reduced to 24 hours. Added `POST /api/auth/logout` endpoint.

4. **User scoping on child entities**: Added JOIN-based user_id verification on `proposal_items` (2 queries) and `milestones` (2 queries) that previously only filtered by parent entity ID.

5. **Error sanitization**: All `e.message` leaks replaced with generic messages. Added `console.error` for server-side logging.

6. **Security headers**: X-Frame-Options: DENY, HSTS (1 year + includeSubDomains), Referrer-Policy: strict-origin-when-cross-origin.

7. **Input length validation**: All create handlers validate text field lengths (names: 200, content: 50000, email: 254 + format check).

## Key Patterns

- CF Workers use `crypto.subtle` for PBKDF2 -- `deriveBits` not `deriveKey`
- Legacy hash migration: detect old format (no colon separator), verify with SHA-256, re-hash with PBKDF2 on success
- Rate limit fail-open: if D1 rate_limit check throws, allow the request (availability > strictness)
- `cf-connecting-ip` header for real client IP on Cloudflare

## Deployed

- Worker version: `7f7ae89c-95e4-4d82-9347-e8c3fe02b091`
- D1 table `rate_limits` created
- Git commit: `af951b1`
