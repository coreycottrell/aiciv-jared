# Phase 3 BUILD — referral-v1 branch (B1 + D1 + B3)

**Date**: 2026-05-07
**Branch**: `referral-v1`
**Type**: operational + teaching
**Tags**: referral-v1, portal-proxy, admin-referrals, paypal-onapprove, parallel-agent-coordination

## What

Executed Phase 3 BUILD on the referral-v1 branch:

- **B1**: Path mismatch fix in `workers/purebrain-portal-proxy/src/worker.js`.
  Rewrites `/api/referral/<x>` → `/referrals/<x>` (was → bare `/<x>`,
  which 404s on referrals-api).
- **D1**: Admin/referrals autocomplete fallback fix in
  `exports/cf-pages-deploy/admin/referrals/index.html`. Removes the
  `hostname !== 'portal.purebrain.ai'` host gate and merges affiliates
  + partners. Adds yellow UI hint when fallback runs.
- **B3**: Wires 4 payment pages (awakened, insiders, partnered, unified)
  to fire a fire-and-forget POST to portal-proxy
  `/api/referral/complete` with `{pb_ref, payment_id, customer_email,
  tier, source_page}` at the top of `handlePaymentSuccess()`.

Final deliverable doc:
`exports/portal-files/phase3-frontend-portal-proxy-build-2026-05-07.md`

## Commits

- B1: bundled into `37cdf89` (parallel-agent collision — see below)
- D1: `0e417f2`
- B3: `557f307`

## Key learnings

### 1. Parallel-agent commit collisions are real on shared branches

While I was working, another full-stack agent (ptt-fullstack /
wtt-fullstack) committed three times to `referral-v1`:
- `37cdf89` A1 + Service Binding
- `fa7a4da` A2 webhook signature
- `0021852` A3 commission formula

My B1 staged change to `workers/purebrain-portal-proxy/src/worker.js`
got swept into `37cdf89` because the other agent ran `git add` after
my edit and before my commit. My subsequent `git commit` exit-1'd
with "nothing to commit" because the file was already in HEAD via
their commit.

**The fix in the tree is correct.** Only the commit message understates
the change. I documented this clearly in the deliverable so cherry-pick
auditing isn't broken.

**Future pattern**: when working in parallel on the same branch with
other agents, prefer either:
- Working in feature-sub-branches and merging at the end, OR
- Coordinating via the handshake queue / scratch pad before each
  `git add`, OR
- Committing immediately after each edit (don't accumulate staged
  changes across multiple files).

### 2. handlePaymentSuccess is the universal hook

All 4 target payment pages have an identical pattern:
- Two `onApprove` handlers (subscription + one-time)
- Both call `verifyPaymentServerSide()` → `handlePaymentSuccess()`

Inserting at the top of `handlePaymentSuccess()` is one edit per page
that covers BOTH onApprove paths. Much cleaner than editing each
onApprove handler separately.

### 3. fire-and-forget contract

For attribution POSTs on payment pages, the rule is: NEVER block
the redirect. Pattern:

```javascript
fetch(url, { method, body, keepalive: true })
  .catch(function() { /* swallow */ });
```

Plus an outer try/catch around the whole IIFE to catch any synchronous
error (e.g. `getPbRef` throwing, `JSON.stringify` failing).
`keepalive: true` lets the request survive page unload during redirect.

### 4. Read-back verification after Edit on critical pages

For payment pages (constitutional), I read back EVERY edit before
moving to the next file. This caught zero bugs this session, but the
discipline is what prevents the next disaster. The Edit tool also
errors if old_string mismatches, so this is double-belt.

### 5. Frozen request contract enables parallel B2/B3 work

By pinning the request body shape in the deliverable doc, B2
(wtt-fullstack) can build the `/referrals/complete` handler in parallel
without round-trips to me. The shape:

```json
{
  "pb_ref":         "PB-XXXX",
  "payment_id":     "<paypal order id>",
  "customer_email": "buyer@example.com",
  "tier":           "Awakened|Insider|Partnered|Unified",
  "source_page":    "awakened|insiders|partnered|unified"
}
```

Per CTO §6.Q1 + Edit #4: webhook joins on `payment_id`, and
`(pb_ref, payment_id)` UNIQUE on referrals table makes the POST
idempotent against page-reload double-fires.

## Files touched

- `workers/purebrain-portal-proxy/src/worker.js` (lines ~166-188) — B1
- `exports/cf-pages-deploy/admin/referrals/index.html` (lines ~1333-1382) — D1
- `exports/cf-pages-deploy/awakened/index.html` (lines ~5301-5330) — B3
- `exports/cf-pages-deploy/insiders/index.html` (lines ~5182-5211) — B3
- `exports/cf-pages-deploy/partnered/index.html` (lines ~5370-5399) — B3
- `exports/cf-pages-deploy/unified/index.html` (lines ~5318-5347) — B3
- `exports/portal-files/phase3-frontend-portal-proxy-build-2026-05-07.md` (new) — deliverable

## Constraints honored

- No deploys — branch only.
- Payment guard logic untouched.
- /partners/ page untouched.
- Existing payment behavior preserved (additive change).
- Read-back verification after every Edit on payment pages.

## Open follow-ups

- B2 (wtt-fullstack): rewrite `/referrals/complete` handler to accept
  the frozen contract.
- D1 better fix: add staging.purebrain.ai + portal.purebrain.ai to
  admin-api CORS allowlist.
- Cleanup: B1 commit message understates change — could re-write
  history later if Jared wants discrete commits per work item, but
  the working tree is correct.
