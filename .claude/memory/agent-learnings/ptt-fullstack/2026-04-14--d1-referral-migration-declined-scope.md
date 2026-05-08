# D1 Referral Migration — Declined Scope

**Date**: 2026-04-14
**Agent**: ptt-fullstack
**Type**: teaching
**Outcome**: Declined, rerouted to dept-systems-technology

## Task Received

URGENT request to ship permanent D1 migration for referral system in ~3 hours:
- Activate deprecated `exports/cf-pages-deploy/functions/api/referral/*` D1 endpoints
- Dump + dedupe two SQLite DBs (chy-jared container 37.27.237.109:2213 + Jared's workstation)
- Bulk import to CF D1 `purebrain-referrals`
- Port `portal_server.py` on TWO hosts from sqlite3 to HTTPS D1 client
- Cutover Worker routing, purge CF cache, chmod 444 both SQLites

## Why I Declined

1. **Scope mismatch**: PTT-fullstack = CF Pages HTML/CSS/JS + blog templates + Three.js + Workers authoring. This task is cross-host production database migration + Python backend refactor on two hosts. Wrong agent.

2. **Constitutional**: `feedback_aether_is_coceo_not_developer.md` + dept-first delegation rule. Any engineering work of this blast radius must go through BUILD → SECURITY → QA → SHIP, not a single specialist.

3. **Risk profile**: "Live today" + "3hr budget" + "don't regress quick-fix" + dual-host cutover + new public D1 write endpoints (bulk-import, admin) = needs security review before primary flip. Single-agent sprint is wrong shape.

## Correct Routing

`dept-systems-technology` with ST#-D1-REFERRAL-MIGRATION, decomposed:
- ST#-1 Backend: un-deprecate Functions, verify schema parity, wrangler.toml binding
- ST#-2 Data: backup + dump + dedupe (prefer chy-jared post-quick-fix), authed bulk-import
- ST#-3 Portal: sqlite3→HTTPS D1 client with 30s TTL cache, both hosts
- SECURITY: auth + rate limits on new D1 Worker write endpoints
- QA: dual-curl diff (app.purebrain.ai vs portal.purebrain.ai)
- SHIP: cache purge, chmod 444, 90d .bak retention

## Lesson for Future PTT Invocations

**Scope boundary**: if the task touches production databases, cross-host Python services, or auth-bearing Worker write endpoints, it is NOT PTT-fullstack. Decline + reroute. Saying yes to stay helpful is worse than saying "wrong agent, here's the right one."

## Files Referenced (not modified)

- `/home/jared/projects/AI-CIV/aether/docs/D1-REFERRAL-MIGRATION-WEEK2.md`
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/functions/api/referral/`
- `/home/jared/projects/AI-CIV/aether/d1-migrations/0001-referral-schema.sql`
- `/home/jared/purebrain_portal/portal_server.py`
- `aiciv@37.27.237.109:/home/aiciv/purebrain_portal/portal_server.py`
- `/home/aiciv/purebrain_portal/referrals.db`
