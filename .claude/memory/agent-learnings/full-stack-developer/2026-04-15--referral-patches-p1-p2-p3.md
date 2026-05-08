# Referral Patches P-1 / P-2 / P-3 — 2026-04-15

**Agent**: full-stack-developer
**Type**: operational + teaching
**Topic**: D1 wiring for Refer & Earn customer panel + SQLite→D1 mirroring

## Shipped

### P-1 — Wire Refer & Earn panel to `/api/refer/me` (SHIPPED + VERIFIED)

**Files touched**:
- `/home/jared/purebrain_portal/portal_server.py` — 1 line change at `check_auth()` (~1022) to add `/api/refer/` to the query-param token allowlist (the panel uses `?token=` style)
- `/home/jared/purebrain_portal/portal-pb-styled.html` — rewrote `loadReferrals()` (~line 11814). New flow:
  1. Primary: `GET /api/refer/me?email=&name=&token=` (D1, auto-provisions)
  2. On `{disabled:true}`: fall back to legacy `/api/referral/register` → `/api/referral/dashboard`
  3. On network fail: same fallback (customer never stranded)
  - Extracted shared render into `renderReferralDashboard(data, loadingEl)` function
  - Preserved all existing UI behavior (stats grid, reward tiers, history, paypal-setup toggle, payout state)

**Verification**:
- New customer `test-p1-fullstack@purebrain.ai` → auto-provisioned `PB-3L3ZEG`, D1 row id `71`
- Existing customer `jared@puretechnology.nyc` → returned existing code `JAREDSB0` with 10 referrals preserved
- Idempotent: 2nd call returns same row
- Auth: 401 without token, 200 with (Bearer header OR `?token=` query)

### P-3 — Mirror SQLite writes into D1 (PARTIAL SHIP + VERIFIED)

**What shipped (2 of 4 target endpoints)**:

**Files touched**:
- `/home/jared/purebrain_portal/referrals_d1_client.py` — added `mirror_referrer_async()` and `mirror_paypal_email_async()` helpers. Fire-and-forget, flag-gated on `USE_D1_REFERRALS`, swallow-all-errors semantics. Never blocks.
- `/home/jared/purebrain_portal/portal_server.py`:
  - `api_referral_register` (~line 3887, post-commit): calls `mirror_referrer_async()` after SQLite INSERT
  - `api_referral_paypal_email` (~line 4533, post-commit): calls `mirror_paypal_email_async()` on UPDATE path, or `mirror_referrer_async()` on the fallback INSERT path

**Verification**:
- Register `test-p3-mirror-1776268169@purebrain.ai` → SQLite code `PB-VMYG` → D1 row `id: 73` appeared within 3s with matching code + name
- Update paypal_email → SQLite 200 OK → D1 `paypal_email` field updated to match within 3s

**What did NOT ship (punted — see Blockers below)**:
- `api_referral_complete` mirror (the referrals table write)
- `api_referral_record_commission` mirror (commission_payments write)
- `/api/referral/leaderboard` D1 port

### P-2 — Payment page attribution chain (PUNTED)

See Blockers below.

## Blockers (non-trivial decisions — need routing)

### Block 1 — Worker missing write endpoints (blocks full P-3)

Probed the `referrals-api.in0v8.workers.dev` worker for write endpoints. Results:
- `POST /referrers/upsert` → **exists** (verified, returned row id 72)
- `POST /referrals/complete` → 405 Method Not Allowed
- `POST /referrals/upsert` → 405
- `POST /referral/complete` → 405
- `POST /commission_payments` → 405
- `POST /admin/commission` → 405
- `POST /admin/referrals/complete` → 405
- `POST /commission/record` → 405

**Decision needed**: add 2 new worker routes (`POST /referrals/complete` and `POST /commission_payments`) with matching schemas. Requires worker source location + `wrangler` deploy access + schema review.

**Mitigation in meantime**: SQLite remains source for referrals completions and commission_payments. Admin D1 dashboard shows stale counts post-migration. Customer's D1-backed dashboard (`/api/refer/me`) will show frozen earnings from Apr 14 migration-time. See memory `ptt-fullstack/2026-04-15--referral-portal-ties-diagnostic.md` Gap G-4.

### Block 2 — P-2 payment-page chain is actually broken (confirmed)

Searched ALL of `/home/jared/exports/cf-pages-deploy/**/*.html` for any caller of `/api/referral/complete`. **Zero matches.** Diagnostic finding B-7 confirmed: no live payment page posts attribution. The only references in the repo are:
- `portal_server.py` endpoint definition
- Deprecated CF Pages Functions (unreachable)
- Audit/history files

**P-2 as written** requires adding NEW `<script>` POST calls to the PayPal-success handlers on the 10 payment pages guarded by the nightly payment-guard (per memory). This is a payment-page surface-area change. Needs Aether + SECURITY route, not a silent fullstack patch.

**Specific asks for P-2 routing**:
1. Which payment pages in `/home/jared/exports/cf-pages-deploy/` are the current live checkout targets?
2. Should the attribution write happen in `onApprove` of the PayPal smart button, or in the post-redirect success handler?
3. What's the canonical `referral_code` source the payment page reads? (URL `?ref=`, localStorage, cookie?)
4. Should a matching D1 mirror endpoint on the worker ship with P-2?

## Rollback

**One-line rollback** (per-patch is not practical because P-1/P-3 share touched files):

```bash
# Disable D1 read path entirely — panel falls back to legacy SQLite flow automatically.
sed -i 's/^USE_D1_REFERRALS=.*/USE_D1_REFERRALS=false/' /home/jared/purebrain_portal/.env
sudo systemctl restart aether-portal.service
```

**File-level rollback** (nuclear):
```bash
cp /home/jared/purebrain_portal/.bak-2026-04-15-referral-patches/portal-pb-styled.html.bak /home/jared/purebrain_portal/portal-pb-styled.html
cp /home/jared/purebrain_portal/.bak-2026-04-15-referral-patches/portal_server.py.bak /home/jared/purebrain_portal/portal_server.py
cp /home/jared/purebrain_portal/.bak-2026-04-15-referral-patches/referrals_d1_client.py.bak /home/jared/purebrain_portal/referrals_d1_client.py
cp /home/jared/purebrain_portal/.bak-2026-04-15-referral-patches/routes.py.bak /home/jared/purebrain_portal/custom/routes.py
sudo systemctl restart aether-portal.service
```

## Teaching — what future agents need to know

1. **Query-param auth allowlist in `check_auth()`** at `portal_server.py:1022`. Any new `/api/...` endpoint that needs `?token=` style auth must be added to this allowlist. `/api/refer/` was NOT in it before P-1.

2. **Shim pattern works well.** `custom/routes.py` already had `/api/refer/me` from yesterday's D1 ship. Zero lines of `portal_server.py` needed for new route *logic* — only the auth allowlist hook. Pattern: put NEW logic in `custom/routes.py`, put MINIMAL hooks (1-2 lines) in `portal_server.py`.

3. **Worker write endpoints are the scarce resource.** D1 reads are already wired via the worker's GETs. Writes require worker source edits. Before planning any SQLite→D1 mirror patch, probe the worker for matching POST endpoints first (`curl -X POST -H 'x-admin-token: $ADM' $BASE/<endpoint> -d '{}' -w '%{http_code}'`). If 405, you're blocked on worker-side work, not VPS.

4. **Fire-and-forget is mandatory.** `mirror_referrer_async()` wraps `asyncio.get_event_loop().create_task()` so the SQLite commit returns to the customer immediately. Any blocking mirror call would couple customer signup latency to the worker's tail latency — forbidden per Jared's "NEVER break a customer flow because D1 is slow."

5. **Test the `{disabled:true}` fallback before shipping any D1-gated endpoint.** The frontend checks `me.disabled` explicitly. If skipped and `USE_D1_REFERRALS=false` is ever flipped (legitimate rollback), customers see a blank Refer & Earn panel.

6. **Diagnostic's B-7 is confirmed real.** Payment-page attribution has been broken since at least the 2026-04-14 deprecation of the CF Pages function. No live caller of `/api/referral/complete` exists in `exports/cf-pages-deploy`. This is the "earn" half of Refer & Earn being silently dead. Surface this to Jared as potentially-revenue-impacting outage.

## Memory Written
Path: .claude/memory/agent-learnings/full-stack-developer/2026-04-15--referral-patches-p1-p2-p3.md
Type: operational + teaching
Topic: P-1 shipped, P-3 partial, P-2 punted with specifics. Reusable shim + mirror pattern for D1-gated SQLite writes.
