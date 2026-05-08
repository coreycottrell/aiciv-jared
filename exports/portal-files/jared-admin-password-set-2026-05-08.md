# Jared Admin Password Set — 2026-05-08

**User**: jared@puretechnology.nyc (id `f15527f5-559c-4799-92e3-4b2de2e27897`, role=`owner`)
**Target**: portal.purebrain.ai/admin/clients/ login
**Status**: SHIPPED-AND-VERIFIED

## Hash Format Used: PBKDF2-SHA256

CF Workers do NOT support bcrypt natively. The social-api worker
(`workers/social-api/src/worker.js`, lines 3667-3691) uses PBKDF2-SHA256
via Web Crypto `deriveBits`:

- Iterations: 100,000
- Salt: 16 random bytes
- Output: 32 bytes (256 bits)
- Storage format: `saltHex:hashHex` (32 + 1 + 64 = 97 chars)

Python `hashlib.pbkdf2_hmac('sha256', pw, salt, 100000, dklen=32)` produces
identical bytes to the worker's Web Crypto output. Verified via successful
login HTTP 200.

## D1 Update Confirmation

```
Database: purebrain-social (625dde70-0a60-45e7-bf81-e18e5ac4d854)
Command:  UPDATE users SET password_hash=? WHERE email='jared@puretechnology.nyc'
Result:   changes: 1, rows_written: 1, changed_db: true
New hash prefix: 8854c1929952b6db174d... (different from old d3ee85edc396d66...)
```

## Backup (for revert if needed)

Old `password_hash` value captured to `/tmp/aether-backups/jared-pwhash-backup-2026-05-08.txt`
(host-local, NOT in git). Format was already PBKDF2 — likely set during a prior
magic-link flow (last_login_at was 2026-05-07T20:34Z prior to this change).

To revert: `UPDATE users SET password_hash='<old-hash>' WHERE email='jared@puretechnology.nyc'`

## Curl Login Test

```
POST https://portal.purebrain.ai/api/login
Content-Type: application/json
{"email":"jared@puretechnology.nyc","password":"<redacted>"}

→ HTTP 200
→ Response keys: ['status', 'token']
→ Token prefix: bc791c856012b6ce2057...
```

Follow-up E2E: `GET /api/admin/clients` with `Authorization: Bearer <token>`
→ **HTTP 200**. Full login → admin endpoint chain verified.

## Telegram Delivery

- chat_id: 548906264 (Jared)
- message_id: **49953**
- Includes: email, plaintext password, login URL, change-after-first-login note
- Telegram API: `ok: true`

## Constraints Honored

- Plaintext password NEVER written to any path tracked by git
- Password file lives at `/tmp/aether-backups/jared-new-pw-2026-05-08.txt` (mode 0600)
- Old hash backup at `/tmp/aether-backups/jared-pwhash-backup-2026-05-08.txt`
- Hash format verified against `verifyPassword` (worker.js:3686) BEFORE delivery
- Login tested with HTTP 200 BEFORE Telegram send

## Status: SHIPPED-AND-VERIFIED
