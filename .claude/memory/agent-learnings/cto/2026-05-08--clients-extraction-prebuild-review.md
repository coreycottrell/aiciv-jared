---
name: Clients extraction pre-build review — scope was 50% under-counted
description: CTO architectural review found 6 Workers bind purebrain-social D1, not just social-api. Extraction sprint must include admin-api fold-in, paypal-webhook + agentmail-webhook rebinds, or drift returns day 1.
type: teaching
date: 2026-05-08
tags: [architecture, domain-isolation, d1-migration, pre-build-review]
---

## Context

Asked to do CTO pre-build review on clients extraction from `purebrain-social` D1 into new `purebrain-clients` D1 + own Worker + own git repo, per Jared's May 7 constitutional rule (`feedback_project_domain_isolation_constitutional.md`).

## What I Found

The brief mentioned only `social-api`. Actual code audit shows **6 Workers bound to purebrain-social D1**:

| Worker | Touches `clients`? |
|---|---|
| social-api | yes (one read-only listing) |
| admin-api | YES — primary CRUD (`workers/admin-api/src/worker.js:135,181,233,270`) |
| agentmail-webhook | YES — read + write magic_link (`workers/agentmail-webhook/src/worker.js:243,265`) |
| paypal-webhook | YES — INSERT + UPDATE (`workers/paypal-webhook/src/worker.js:92,131,149,435,484,499`) |
| meetings-api | reads users/sessions only |
| blog-publisher | reads users/sessions only |

If sprint only re-points `social-api`, the other 3 client-touching Workers become silent dual-writers and drift returns immediately.

## The Teaching

**Pre-build reviews must always grep the codebase for the table name across ALL workers, not just the one named in the brief.** A `database_name = "purebrain-social"` line in a wrangler.toml is a domain-isolation violation regardless of which Worker it lives in. The scope of "extraction" is ALWAYS bigger than the scope of "rename one route."

`grep -rn "FROM clients\|INTO clients\|UPDATE clients" workers/` is the gate-zero command for any D1 extraction sprint.

## Decision

GO-WITH-EDITS. Verdict + dispatch plan in `exports/portal-files/cto-prebuild-review-clients-extraction-2026-05-08.md`.

Key edits Jared/Chy must accept before BUILD:
1. Expand scope to admin-api fold-in + paypal-webhook + agentmail-webhook rebinds
2. Capture live `clients` schema in version control as gate-zero (currently NOT in `shared/social-api-schema.sql`)
3. Use header-gated portal-proxy route, not big-bang flip
4. Bulk creds resend AFTER 24h verify window, not at cutover
5. Independent ops-analyst verifier per memory rule

Total: ~10.5 engineer-days, ~6 calendar days with 3-engineer parallelism.

## Pattern for Future Pre-Builds

When asked "extract X from Y D1":
1. `grep` ALL workers for ANY ref to X table
2. Count distinct wrangler.toml files binding Y
3. Force scope expansion if count > 1
4. Bridge contract design before code: which Workers stay direct-bind, which switch to HTTP/Service Binding?
