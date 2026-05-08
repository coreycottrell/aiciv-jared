# PureBrain Worker D1 Domain Isolation Violations — May 7 2026

## Pattern
When a monorepo grows multiple Workers organically, D1 bindings drift to a single "God database" (here: `purebrain-social` 625dde70). The social DB ends up holding: client records, payment logs, email templates, blog state, magic links, meeting data, and auth sessions — none of which belong to the social domain.

## The Concrete Map (as of 2026-05-07)

D1 binding `purebrain-social`:
- social-api (CORRECT)
- admin-api (WRONG — clients != social)
- paypal-webhook (WRONG — payments != social)
- agentmail-webhook (WRONG — onboarding reads/writes clients in social DB)
- blog-publish-hook (WRONG — blog state in social DB)
- blog-publisher (WRONG — content tracking in social DB)
- welcome-email-api (WRONG — email infra in social DB)
- meetings-api (WRONG — meetings in social DB)

D1 binding `purebrain-referrals`:
- referrals-api (CORRECT)
- trio-comms (WRONG — comms != referrals)

D1 binding dedicated:
- ara-index → `ara-index` D1 (CORRECT)

## Dead End: "Just use social DB for convenience"
Convenient at first. Gets extremely painful when:
- You need to migrate social DB schema and can't because payments data is in there
- You want to give social team write access but not expose client emails
- A social DB rollback would wipe payment logs

## Correct Pattern
One product = one D1. Cross-domain reads/writes = explicit bridge API with defined contract, auth token, and endpoint spec. No silent HTTP calls between Workers without a documented bridge.

## Fix Sequence
1. New D1s: `purebrain-clients`, `purebrain-payments`, `purebrain-comms`, `purebrain-blog`
2. Data migration (wrangler d1 execute)
3. Rebind Workers
4. Create `clients-api` bridge Worker
5. Update portal-proxy routes

## Key File Paths
- Audit: `exports/portal-files/domain-isolation-audit-2026-05-07.md`
- Constitutional rule: `.claude/memory/feedback_project_domain_isolation_constitutional.md`
- Portal proxy (greedy route risk): `workers/purebrain-portal-proxy/src/worker.js` lines 36-58
- Hardcoded admin token: `workers/purebrain-portal-proxy/src/worker.js` lines 183, 196
