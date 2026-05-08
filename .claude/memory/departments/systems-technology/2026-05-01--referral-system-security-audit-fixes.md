# Referral System Security Audit + Fixes
**Date**: 2026-05-01
**Type**: operational + teaching
**Agent**: dept-systems-technology

## What Happened
Full BUILD -> SECURITY -> QA -> SHIP cycle on referral system (`workers/referrals-api/src/worker.js`).

## Critical Findings
1. **Bcrypt migration auto-accepted ANY password** — `verifyPassword()` returned `"bcrypt_needs_reset"` and session handler treated it as valid login. Fixed: now returns 401 forcing forgot-password flow.
2. **Dashboard endpoint had NO auth** — anyone with a referral code could view private data. Fixed: requires session token + cross-account check.
3. **No rate limiting on login** — Fixed: 10 attempts/15 min via D1 `login_attempts` table.
4. **SHA-256 without salt** — Fixed: new hashes use `salt$hexdigest` format.
5. **Missing /track endpoint** — Click tracking from frontend was 404ing. Added POST /track.

## Accounts Remediated
5 accounts (PB-3AUQ, PB-JJ8N, PB-K22P, PB-N2GR, PB-G8XP) had passwords overwritten during testing. Reset to bcrypt sentinel, forcing password reset.

## Key Teaching
- **NEVER auto-accept passwords** on hash format migration. If you can't verify the old hash, force a password reset flow.
- **API endpoints must enforce auth** even if the frontend has a login gate. The frontend is client-side; the API is the real boundary.
- **Test with real credentials** carefully — testing login with arbitrary passwords on production accounts can compromise them if the migration path auto-accepts.

## Files Changed
- `workers/referrals-api/src/worker.js` — 6 changes (bcrypt fix, dashboard auth, rate limiting, salted hashing, track endpoint, admin password_hash update)
- Worker deployed: version `78e135e6-3dc2-42fd-9aaf-406ee86ecdba`

## QA Report
`exports/portal-files/referral-system-qa-2026-05-01.md`
