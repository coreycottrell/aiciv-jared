# Jason King Add — Couplify Duo 2 Mirror of Amy/Cai (SHIPPED)

**Date**: 2026-05-12
**Type**: operational + teaching
**Agent**: ptt-fullstack
**Status**: SHIPPED — id=103 inserted into purebrain-clients, constitutional gates held
**Time-to-ship**: ~15 min (within budget)

## What was asked

Jared, portal, 2026-05-12: pull Jason King (Resolve AI / Couplify) into client list under Sheila's $499 sub, mirroring Amy Housand's covered-seat pattern. Magic link already minted by Witness.

CTO pre-build: `cto-prebuild-jason-king-add-2026-05-12.md` (token `a1f76806c33f4503b`).

## What shipped

Single parameterized D1 INSERT to purebrain-clients (`aaade55e-f888-48ea-8e63-b934d697379b`):

- **id**: 103 (auto-increment)
- **email**: jason@couplify.com (Jared-confirmed)
- **name**: Jason King
- **ai_name**: Resolve
- **company**: Couplify
- **tier**: Partnered
- **payment_status**: covered (duo-partner-seat marker)
- **paypal_subscription_id**: '' (empty — covered)
- **total_paid**: 0
- **status**: active (AI provisioned by Witness)
- **joined_date**: 2026-05-12
- **source**: paypal (indirect via Sheila's sub)
- **notes**: "Covered under Sheila Whitehurst sub I-RBXHJ68JCJPL (Couplify Duo 2)"
- **goes_by**: Jason
- **magic_link**: https://resolve-jason.app.purebrain.ai/?token=zSry2NKLePKoxh0Tu8h4Yb4snNRx8GiM9LT7aD9mECA

CF D1 meta: `changes=1, last_row_id=103, rows_written=3` (rows_written includes index updates).

## Verification (all GREEN)

1. **Pre-INSERT idempotency**: 0 Jason rows before write
2. **Post-INSERT readback**: exactly 1 row, all 16 spec fields match + 4 schema-default fields (first_seen_at, last_active_at, previous_monthly_amount, plan_changed_at) populated to schema defaults
3. **Count delta**: 65 → 66 (no double-write)
4. **Magic link GET**: HTTP 200, 800,891 bytes, content-type text/html, contains "Resolve" branding
5. **Sheila row INTACT**: id=94 ai_name='Kindred', sub `I-RBXHJ68JCJPL`, $499 — unchanged
6. **purebrain-social count**: 65 (UNCHANGED — constitutional ban held)
7. **purebrain-social Jason rows**: 0 (constitutional gate held — May 7 rule)
8. **Admin endpoints**: `portal.purebrain.ai/admin/clients` returns 200 (page renders); `/api/admin/clients` returns `{"error":"unauthorized"}` without session (expected — auth-gated, D1 readback is authoritative)

## Couplify household map — final state (4 rows, both duos complete)

| Duo | Payer | Sub | Partner | AI Name | Status |
|---|---|---|---|---|---|
| 1 | Jay Whitehurst (id=90) | I-P4WNDS799EYY | Amy Housand (id=95) | Spark + Cai | active + covered |
| 2 | Sheila Whitehurst (id=94) | I-RBXHJ68JCJPL | Jason King (id=103) | Kindred + Resolve | active + covered |

Previously [UNSET] Duo 2 partner slot now populated. Whitehurst household audit memory (2026-05-10) supersedable on this point.

## Patterns reused (vs Amy Housand May 10 baseline)

1. **16-col INSERT shape**: same column ordering, same covered-seat semantics
2. **CF D1 REST API with Bearer CF_API_TOKEN**: `/accounts/{ACCT}/d1/database/{DB_ID}/query` with `params` array — clean execution, 0 auth errors (scoped token now works for purebrain-clients writes, distinct from the May 10 wrangler-d1-execute auth failure)
3. **No surname-fuzz**: exact-email match only (S5 ban honored)
4. **No welcome email send**: Witness already owned the seed + magic link (per `feedback_seed_flow_never_deviate.md`)
5. **No PayPal/commission_payments touch**: covered seat = no new revenue event
6. **Backup file written pre-write**: `.tmp/jason-king-insert-backup-2026-05-12.sql` with rollback DELETE statement

## Constitutional alignment receipt

- `feedback_purebrain_social_never_touches_referral_or_clients.md` (May 7) — write to purebrain-clients ONLY, social count unchanged ✅
- `feedback_every_feature_multi_tenant_for_customers.md` — household pattern via email-domain + payment_status=covered ✅
- `feedback_seed_flow_never_deviate.md` — NO new seed; Witness owned the seed flow ✅
- `feedback_magic_link_pipeline_constitutional.md` — domain rewrite already applied by Witness; we registered the link in DB ✅
- `feedback_s5_payername_fuzzy_fallback_banned.md` — exact-email match only ✅
- `feedback_never_deploy_to_customer_containers.md` — D1 REST API write only, no container access ✅
- `feedback_wrangler_deploy_must_be_preceded_by_git_commit.md` — D1 INSERT via REST API (no wrangler deploy), but tools to be committed per spirit of rule ✅

## Schema gap still present (NOT fixed in this dispatch)

The clients table still lacks `paid_by_email` / `household_id` / `duo_partner_email` columns. Jason's linkage to Sheila's sub lives only in the `notes` field — same state as Amy/Jay relationship. P2 migration spec (`p2-schema-migration-and-cai-2026-05-10.md`) covers the additive ALTER columns when Jared greenlights.

This is acceptable for now — matches Amy's precedent.

## Files

- Pre-flight script: `.tmp/jason-king-preflight.py`
- INSERT script: `.tmp/jason-king-insert.py`
- Pre-flight log: `.tmp/jason-king-preflight-2026-05-12.log`
- INSERT log: `.tmp/jason-king-insert-2026-05-12.log`
- Backup: `.tmp/jason-king-insert-backup-2026-05-12.sql`
- Receipt (portal-delivered): `exports/portal-files/jason-king-add-ship-2026-05-12.md`
- CTO brief: `exports/portal-files/cto-prebuild-jason-king-add-2026-05-12.md`
- Prior pattern: `agent-learnings/full-stack-developer/2026-05-10--whitehurst-household-audit.md`

## Follow-up dispatches (NOT this dispatch)

1. wtt-qa E2E verification on resolve-jason container (paying customer flow)
2. Update Whitehurst household audit memory to reflect Duo 2 completion (formerly [UNSET])
3. P2 schema migration (if Jared greenlights — adds `paid_by_email` for proper FK)

## Lesson worth remembering

**Amy precedent saved ~30 min of spec work.** Reading `2026-05-10--whitehurst-household-audit.md` first gave the exact column shape, covered-seat semantics, and constitutional gate list. The memory-first protocol paid out: search before doing, reuse the shape.

**The CF_API_TOKEN (Bearer) auth path works for purebrain-clients D1 query/write.** May 10 memory noted wrangler-d1-execute returned 10000/9109 errors with that same token. The REST API path bypasses that. If wrangler ever needed for D1 in future, retest token scopes — but for now REST is the reliable lane.
