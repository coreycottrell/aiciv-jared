# 🔴 SECURITY FLAG — CE SME Hardcoded Credentials in Public HTML

**Date**: 2026-05-07
**Severity**: HIGH (CRITICAL if deployed)
**Status**: Site currently CF 530 (not live) — fix BEFORE next deploy
**BOOP**: security-posture-boop

## Finding 1 — Hardcoded Phil credentials in browser-readable HTML

**File**: `exports/cf-pages-deploy/ce-sme/index.html:3826-3896`
**Commit**: `4165c8b` "feat: CE SME premium landing page + Phil test account setup"

```javascript
const PHIL_EMAIL = 'phil@canadasentrepreneur.com';
const PHIL_PASS = 'CESME2026!';
```

**Attack vectors**:
1. Anyone viewing page source obtains Phil's working credentials → can log into his account from anywhere, anytime
2. Any visitor to `ce.purebrain.ai/?setup=phil` auto-authenticates AS Phil with his real customer account
3. Once authenticated, full read/write/delete access to Phil's proposals, invoices, candidates, etc. (all scoped to his `user_id`)
4. Pattern is trivially predictable — `{COMPANY}{YEAR}!` — others might be added with same scheme

**Fix recommendations**:
- Move setup flow server-side: send Phil a one-time magic link instead of `?setup=phil`
- If keeping client-side flow, generate a strong random password server-side and email it to Phil only
- Disable `?setup=phil` flow in production — gate behind staging-only env check
- Rotate Phil's password immediately once auto-setup runs (or before any deploy)

## Finding 2 — Pipeline skipped: SPEC → CTO → BUILD → SECURITY → QA → SHIP

Commits `9671422` (Sprint 4 + delete endpoints) and `4165c8b` (landing + Phil setup) shipped to git AFTER security pass `af951b1` without a follow-on security review. New attack surface added since last review:
- 8+ DELETE endpoints
- `/api/demo/seed` endpoint
- Client-side auto-registration flow with embedded credentials

Per CLAUDE.md constitutional rule, every code-touching sprint requires a security gate before SHIP.

## Findings That Are OK

- ✅ DELETE handlers properly scope by `user_id` (`WHERE id = ? AND user_id = ?`)
- ✅ `handleDelete(env, sess, table, id)` — `table` is hardcoded by router, no SQLi
- ✅ Status validation enums prevent enum injection
- ✅ Demo seed endpoint requires session token
- ✅ PBKDF2 + salt password hashing correct (from af951b1)
- ✅ No new dependencies — no CVE supply-chain delta
- ✅ Site currently CF 530 — Phil creds NOT yet live in production

## Routing

- **Owner**: ST# (CE SME worker is theirs)
- **Action**: Block next CE SME deploy until Phil setup flow is rebuilt
- **Verifier**: OP# spot-check after fix
