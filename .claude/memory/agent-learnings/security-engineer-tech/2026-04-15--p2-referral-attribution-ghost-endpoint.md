# P-2 Referral Attribution — Ghost Endpoint Diagnosis

**Agent**: security-engineer-tech
**Date**: 2026-04-15
**Type**: operational + teaching
**Topic**: Root cause of silent referral attribution outage since Apr 14

## What I Found

The task said "CF Pages function deprecated, referrers not credited." Memory from ptt-fullstack/full-stack-developer confirmed D1 deprecation and no JS callers of `/api/referral/complete`. Both were WRONG about the JS — all 9 of 11 live payment pages DO POST to the endpoint; their code path is intact.

The actual bug is one layer deeper:

**`POST https://app.purebrain.ai/api/referral/complete` returns HTTP 200 with success body, but the request never reaches the VPS portal.** Verified by:
- nginx access log shows ZERO external POSTs to that path
- Portal access log shows ZERO POSTs to that path
- Loopback direct `curl http://127.0.0.1:8097/api/referral/complete` DOES write (SQLite row id 78 created, cleaned after verify)

A deprecated Cloudflare Pages Function at `exports/cf-pages-deploy/functions/api/referral/complete.js` is intercepting `app.purebrain.ai/api/referral/complete` and writing to a D1 binding that has no readers. Every single referral attribution since D1 was flagged deprecated has been written to a dead database.

## The Teaching

1. **When a memory says "X is broken because no caller exists" — verify BOTH the caller side AND the endpoint side with an end-to-end probe.** Prior agents concluded the client JS was missing. The JS is fine. The endpoint itself is the ghost.

2. **Cloudflare Pages Functions bind per-subdomain.** A Pages project attached to `app.purebrain.ai` (even one deploying `purebrain.ai` as main) can intercept any path matching a `functions/api/...` directory regardless of DNS pointing to origin. "Deprecated" CF functions are NOT safely deprecated until the file is deleted or the project is unbound.

3. **`via: 1.1 Caddy` response header does NOT mean Caddy origin** — in this infra it's a marker the CF tunnel inserts. Origin here is nginx + python. Headers can lie; trust logs.

4. **Ghost 200 responses are the worst failure mode.** They poison every downstream health check (the attribution looks "ok" in client logs), masquerade as success to monitoring, and silently bleed revenue. A 500 would have been caught within the day.

5. **The payment-page audit took 10 minutes with the right grep patterns** — `grep -c 'payment-glue\.js'`, `grep -c 'window.onPaymentComplete\s*='`, `grep -c '/api/referral/complete'` across all 11 pages. The real work was figuring out what made the endpoint return 200 without writing.

6. **pay-test-sandbox-3 and pay-test-sandbox-5 are actual live-PayPal pages with no completion handler.** If any customer lands there (bookmark, old link, CES leftover URL), they pay and get stranded. Silent revenue loss + customer abandonment. This is worse than the attribution bug because the customer has no portal, no seed, no refund pathway.

## What I Shipped / Didn't Ship

### Shipped
- Canonical flow doc at `/home/jared/exports/portal-files/referral-attribution-flow-2026-04-15.md` (1,200+ lines, full audit table + 5 SEV-categorized findings + rollback plan)
- Full audit of 11 payment pages with exact line numbers
- Root-cause diagnosis with reproduction steps (loopback vs external probe)
- Cleanup of my own test pollution (row id 78 in SQLite, verified gone, DB integrity restored: MAX(id)=77, COUNT=26)

### Did NOT ship (needs Jared decision first)
- Worker endpoint additions (`POST /referrals/complete`, `POST /commission_payments`) — ready to implement, blocked on whether to do it before or after Path A
- Ghost endpoint fix (Path A1 proxy rewrite vs A2 delete function) — needs Jared to pick + confirm which CF Pages project binds `app.purebrain.ai`
- pay-test-sandbox-3/5 repair — needs Jared "keep or delete" decision
- E2E verify — blocked until Path A lands

### Why I punted instead of executing
Despite the EXECUTE authority memory saying greenlit ops should execute: this task had multiple structural ambiguities that blocking-executing would have amplified:
1. CF Pages project binding for `app.purebrain.ai` is undocumented in my grounding — guessing wrong deploys to wrong surface
2. Parallel "historical damage audit" mentioned in task — I don't know its state, and writing fresh rows while it runs could pollute its data
3. Sandbox pages: delete vs repair is a product decision, not engineering
4. Path A1 vs A2 is a blast-radius tradeoff worth 30 seconds of Jared's attention

These are the exact "STOP and ask" cases the greenlight memory lists: changes affecting $$$ movement + unknown blast radius. Writing a doc + probing is forward progress; deploying blind is not.

## Files Referenced

- `/home/jared/purebrain_portal/portal_server.py:4267` (api_referral_complete)
- `/home/jared/purebrain_portal/referrals.db` (SQLite authoritative)
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/functions/api/referral/complete.js` (the ghost)
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/js/payment-glue.js` (shared glue, 4 pages)
- `/home/jared/projects/AI-CIV/aether/workers/referrals-api/src/worker.js` (worker, needs 2 endpoints)
- `/home/jared/projects/AI-CIV/aether/tools/verify-payment-pages.sh` (canonical 11-page list)
- `/home/jared/exports/portal-files/referral-attribution-flow-2026-04-15.md` (this session's deliverable)

## Memory Written
Path: .claude/memory/agent-learnings/security-engineer-tech/2026-04-15--p2-referral-attribution-ghost-endpoint.md
Type: operational + teaching
Topic: Root cause (deprecated CF Pages Function intercepting prod endpoint) + why it's worse than previous agents concluded
