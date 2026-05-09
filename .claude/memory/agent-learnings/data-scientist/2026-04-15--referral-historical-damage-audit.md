# Referral Historical Damage Audit — 2026-04-15

**Type**: operational
**Window audited**: 2026-04-14 00:00 UTC → 2026-04-15 16:02 UTC
**Outcome**: $0 damage, 0 missed attributions, structural risk flagged

## Headline
- clients.db max first_seen = 2026-04-11T22:09 → no new signups in 3.5 days
- D1 max referral.created_at = 2026-04-12T18:09 → matches portal referrals.db (reconcile working)
- 24 referral clicks on Apr 14, all from 1 IP (ip_hash eec919e78ba64856) across 4 codes (JAREDSB0, PB-6TUA, PB-FKWC, PB-V2CJ) — Jared smoke-testing the /refer/ fix, not real traffic
- 0 conversions ⇒ 0 commissions owed ⇒ no backfill required

## Architecture learned (for future audits)
1. referrals-api Worker (CF) has NO public referral-attribution write path. Only admin `/referrers/upsert` + `/r/:code` click tracker.
2. Actual attribution write = `POST /api/referral/complete` on portal_server.py (line 4267), called from BROWSER JS on landing page after PayPal onApprove.
3. That means attribution survival requires localStorage/cookie intact through click → PayPal redirect → return → JS call. Fragile.
4. Portal's `/home/jared/purebrain_portal/referrals.db` is source of truth; D1 is synced by `referral_reconciliation.py` (runs in dry-run-by-default; first enforce run was 2026-04-15T14:02:47Z, provisioned 36 drift referrers).
5. `clients.referral_code` column is 100% empty across all 48 rows — never populated at signup. Dead column.

## Gotcha: CF_MANAGEMENT_TOKEN fails D1, use CF_API_TOKEN
In aether/.env, `CF_MANAGEMENT_TOKEN` returns 1000/7403 auth errors on D1 queries. `CF_API_TOKEN` ([REDACTED-2026-05-09-LEAK-CFUT]...) works. Account ID d526a3e9498dd167509003004df03290. D1 database_id cdd9a522-f947-42a6-b9a3-c30534e02c3f for purebrain-referrals. Endpoint: `https://api.cloudflare.com/client/v4/accounts/$ACCT/d1/database/$DB/query`.

## Gap noted
- CF Pages access logs not queryable from this host (no Logpush destination)
- PayPal webhook receiver runs on purebrain_log_server (different host) — not inspected
- So a PayPal subscription that failed to reach clients.db AT ALL would be invisible. Low probability (pipeline stable since Mar 14) but not zero. Recommended sanity: Jared check PayPal Merchant directly for 2026-04-14→2026-04-15 subscription activations.

## P3 test pollution flagged
referrers.id=44 `test-p3-mirror-1776268169@purebrain.ai` added 2026-04-15T15:49:30 — parallel security agent's E2E. Exclude from backfills, remove post-test.

## Report delivered
`/home/jared/exports/portal-files/referral-historical-damage-audit-2026-04-15.md`
