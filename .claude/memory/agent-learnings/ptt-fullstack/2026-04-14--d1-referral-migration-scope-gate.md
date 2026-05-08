# D1 Referral Migration — Scope Gate Hit

**Date**: 2026-04-14
**Type**: operational
**Agent**: ptt-fullstack

## Situation

Task: complete D1 migration for referral system by porting portal_server.py SQLite queries to D1 HTTPS API. Spec mentioned "read-only endpoints" on the worker.

## Finding

portal_server.py has ~50 query sites against `referrals.db`, of which **many are WRITES** critical to money flow:
- INSERT INTO referrers (signup)
- UPDATE password_hash (5 sites)
- UPDATE paypal_email
- INSERT INTO commission_payments (5% commission write)
- DELETE (admin)
- INSERT INTO rewards / referral_clicks

Read-only worker is insufficient — would silently break signup + commission tracking.

## Blockers

1. Spec scope vs reality mismatch (read-only ≠ sufficient for parity)
2. `wrangler whoami` returns unauthenticated; `CF_API_TOKEN` in .env line 115 but not exported as CLOUDFLARE_API_TOKEN; scopes unverified
3. Remote portal at `aiciv@37.27.237.109:2213` — SSH/restart auth unverified from agent shell

## Correct path forward

Worker should expose arbitrary SQL POST /query (D1 supports prepare().bind().all() for any SQL). Python side: aiosqlite-shim class so only `_referral_db()` context manager needs swap. Parity test harness hitting all endpoints incl write paths (signup, password set, PayPal payout webhook).

## Decision

Stopped at gate rather than ship read-only partial that breaks writes. Reported blocker honestly to Jared with A/B options.

## Key locations

- `/home/jared/purebrain_portal/portal_server.py` lines 3411-5528 = referral system
- `_referral_db()` context manager line 3418 = the single swap point if shim is built
- Worker template: `/home/jared/projects/AI-CIV/aether/workers/trio-comms/` (already has D1 binding to purebrain-referrals)
- D1 DB id: `cdd9a522-f947-42a6-b9a3-c30534e02c3f`

## Lesson

When a spec says "read-only endpoints" but the source code writes heavily, verify the write paths BEFORE accepting the spec. A half-migration on money code is worse than no migration.
