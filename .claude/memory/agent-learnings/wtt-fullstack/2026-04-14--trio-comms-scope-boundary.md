# Trio Comms Worker — Scope Boundary (WTT declines)

**Date**: 2026-04-14
**Type**: teaching
**Agent**: wtt-fullstack

## Situation

Received task to build Cloudflare Worker with D1-backed trio messaging (jared/aether/chy/morphe):
- POST /trio/message (server-side sender identity via Bearer token)
- GET /trio/messages
- POST /trio/mark-read
- D1 table `trio_messages` in `purebrain-referrals` (id cdd9a522-f947-42a6-b9a3-c30534e02c3f)
- Files: workers/trio-comms/{src/worker.js, wrangler.toml}

## Why WTT declined

WTT domain = **Witness** API integration, birth pipeline (seed → container → magic link), container pool, OAuth, seed endpoints.

Trio Comms is:
- Generic CF Worker + D1 infra
- Four-role session/token auth (not Witness OAuth)
- Messaging, not birth/seeding

No overlap with Witness stack. Different D1 database, different domain.

## Correct routing

dept-systems-technology → CF Workers / infra specialist (ST#), not WTT#.

## Teaching

Constitutional routing: "ALL work → dept manager → specialists. NEVER skip."
When task misroutes to WTT# but isn't Witness/birth/seed/OAuth/container — decline and redirect to conductor. Don't execute out-of-scope work even if greenlit, because:
1. Memory pollution (WTT learnings dilute with non-Witness infra)
2. Wrong specialist = weaker execution (CF Workers infra agent will do this better)
3. Violates dept-first delegation
