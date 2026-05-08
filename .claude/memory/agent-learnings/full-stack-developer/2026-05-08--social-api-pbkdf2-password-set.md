# Setting Passwords for social-api / portal.purebrain.ai Users

**Date**: 2026-05-08
**Type**: operational
**Topic**: PBKDF2 password hash compatibility between Python and CF Workers

## Context

Jared needed to login to portal.purebrain.ai/admin/clients/ (had only
used magic-link before). Set fresh password and verified end-to-end.

## Key Facts

- **D1 binding**: `purebrain-social` (625dde70-0a60-45e7-bf81-e18e5ac4d854),
  worker `social-api`, defined in `workers/social-api/wrangler.toml`.
- **Login route**: `POST /api/login` on portal.purebrain.ai is proxied by
  `purebrain-portal-proxy` worker → `https://social-api.in0v8.workers.dev/api/login`
  (see `workers/purebrain-portal-proxy/src/worker.js:155-157`).
- **Hash format**: PBKDF2-SHA256, 100k iterations, 16-byte salt, 32-byte
  output. Stored as `saltHex:hashHex` (97 chars). Worker code at
  `workers/social-api/src/worker.js:3667-3691`.
- **CF Workers do NOT support bcrypt** — confirmed across 3 prior memories
  (referrals-api 2026-04-06, ce-sme 2026-05-06, social-api).

## Python ↔ CF Workers Hash Compatibility

This Python produces a hash byte-identical to the worker's Web Crypto:

```python
import hashlib, os
salt = os.urandom(16)
hash_bytes = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'),
                                  salt, 100000, dklen=32)
stored = f"{salt.hex()}:{hash_bytes.hex()}"
```

The worker's `verifyPassword` (worker.js:3686) splits on `:`, re-hashes
the input with the stored salt, compares hash halves. Python and Web
Crypto deriveBits produce identical output for identical inputs.

## Verification Pattern (always do this before delivering)

1. UPDATE D1 → confirm `changes: 1, rows_written: 1`
2. SELECT to confirm new hash prefix differs from backup
3. `curl -X POST /api/login` → expect HTTP 200 + `{status, token}`
4. `curl -H "Authorization: Bearer <token>" /api/admin/clients` → expect 200
5. ONLY THEN deliver password to user

## Gotcha Avoided

`last_login_at` showed 2026-05-07 (today) before set, suggesting Jared had
been auto-logging via magic-link with auto-set password_hash. The OLD hash
was a real PBKDF2 hash, not a sentinel. Backup is critical for revert.

## File Locations

- Worker hash code: `/home/jared/projects/AI-CIV/aether/workers/social-api/src/worker.js:3667-3691`
- Portal proxy login route: `/home/jared/projects/AI-CIV/aether/workers/purebrain-portal-proxy/src/worker.js:155-160`
- Backup (host-local, not git): `/tmp/aether-backups/jared-pwhash-backup-2026-05-08.txt`
- Receipt: `/home/jared/projects/AI-CIV/aether/exports/portal-files/jared-admin-password-set-2026-05-08.md`

## Constraint

NEVER commit plaintext passwords to anywhere git touches. Use `/tmp/` with
mode 0600 for the working session, deliver via Telegram, then the receipt
file (which goes to portal-files and may be committed) contains only:
hash prefixes, HTTP codes, message_ids — never the password itself.
