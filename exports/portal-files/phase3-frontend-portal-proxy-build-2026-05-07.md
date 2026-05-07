# Phase 3 BUILD — Frontend + portal-proxy (referral-v1 branch)

**Agent**: full-stack-developer
**Date**: 2026-05-07
**Branch**: `referral-v1`
**Constraint honored**: Code only, NO deploy, NO `wrangler deploy`, NO `wrangler pages deploy`.
**Scope**: B1 (portal-proxy path mismatch), D1 (admin/referrals frontend host-gate),
B3 (4 payment pages → pb_ref POST at onApprove).

---

## Coordination note (parallel work conflict)

While I was working, ptt-fullstack/wtt-fullstack landed several commits
on `referral-v1` in parallel. That stomped slightly on the B1 commit
sequencing — the B1 fix to `workers/purebrain-portal-proxy/src/worker.js`
ended up bundled into commit `37cdf89` ("A1 + CTO Edit #5") rather
than landing as its own discrete B1 commit. The fix is in the tree
and correct; only the commit message understates the change.

If a clean B1 commit is required for audit/cherry-pick purposes, run:

```bash
git revert --no-commit 37cdf89  # then split, or
git log -p 37cdf89 -- workers/purebrain-portal-proxy/src/worker.js
```

…to see the B1 hunk by itself (the diff inside that commit). Per Jared's
"create new commits" rule, I did NOT amend `37cdf89`. The B1 change is
clearly identifiable inside it via the inline `B1 (referral-v1):` comment.

---

## Commits delivered (this session, full-stack-developer)

| Commit | Work item | Files |
|---|---|---|
| (in `37cdf89`) | **B1** | `workers/purebrain-portal-proxy/src/worker.js` |
| `0e417f2` | **D1** | `exports/cf-pages-deploy/admin/referrals/index.html` |
| `557f307` | **B3** | 4 × payment page (awakened, insiders, partnered, unified) |

Other parallel commits on the same branch (NOT mine):
- `37cdf89` A1 (Service Binding wrangler.toml) — ptt-fullstack
- `fa7a4da` A2 (real PayPal webhook signature verification) — wtt-fullstack
- `0021852` A3 (canonical commission formula + tier_at_write) — wtt-fullstack

---

## B1 — portal-proxy path mismatch fix

**File**: `workers/purebrain-portal-proxy/src/worker.js` (line ~166-188)
**Commit**: `37cdf89` (bundled — see coordination note above)

### What it does

Rewrites the `/api/referral/<path>` route to forward `<path>` correctly
to the referrals-api Worker, prefixing with `/referrals` instead of
stripping to bare `/`.

```javascript
// BEFORE (broken):
const workerPath = url.pathname.replace('/api/referral', '') || '/';
// /api/referral/complete → /complete   ← 404 on referrals-api

// AFTER (B1 fix):
const tail = url.pathname === '/api/referral'
  ? ''
  : url.pathname.slice('/api/referral'.length);
const workerPath = '/referrals' + tail;
// /api/referral/complete → /referrals/complete   ← matches handler
```

### Acceptance criteria satisfied

- ✅ `/api/referral/complete` (proxy) now forwards to `/referrals/complete`
  (referrals-api), which is the actual handler path.
- ✅ Other paths under `/api/referral/*` (e.g. `/track` if added) get
  the same `/referrals/<x>` namespace mapping — clean and predictable.
- ✅ The `/api/referral` route block is gated by
  `subdomain === 'portal'`, so this is portal.purebrain.ai-only behavior.
- ✅ No live deploy. Branch only.
- ✅ Phase 0 (ptt-fullstack A1 Service Binding) landed and the B1 fix
  sits cleanly on top of it without conflict.

### Test stub (for SEC/QA)

```bash
# Negative test: pre-fix path, should be 404 on referrals-api
curl -X POST https://referrals-api.in0v8.workers.dev/complete \
  -H 'Content-Type: application/json' \
  -d '{"pb_ref":"PB-TEST","payment_id":"X","customer_email":"a@b.c"}'
# Expect: 404 (handler doesn't exist)

# Positive test: B1 fix path, should reach /referrals/complete handler
# (After B2 lands the new pending-row handler — until then it's the
#  legacy admin-only handler at line 142 of referrals-api/src/worker.js
#  which expects {referral_id} not {pb_ref}, so will return 400.)
curl -X POST https://portal.purebrain.ai/api/referral/complete \
  -H 'Content-Type: application/json' \
  -d '{"pb_ref":"PB-TEST","payment_id":"X","customer_email":"a@b.c"}'
# Pre-B2: expect 400 "referral_id required" (proves path forwards correctly)
# Post-B2: expect 200 with {ok:true, pending: true}
```

---

## D1 — Admin referrals autocomplete fallback fix

**File**: `exports/cf-pages-deploy/admin/referrals/index.html` (line ~1333-1382)
**Commit**: `0e417f2`

### What it does

1. **Removes the host gate** on the admin-api fallback. Previously the
   fallback was gated to `hostname !== 'portal.purebrain.ai'`, leaving
   production with no autocomplete data when admin-api failed (CORS,
   timeout, expired token). Now fires on every host.

2. **Merges affiliates + partners** when fallback runs. Previously only
   loaded affiliates (a strict subset of the client roster). Now does
   parallel `Promise.all` on `/api/admin/affiliates` AND
   `/api/admin/partners`, dedupes by lowercase email, and sets
   `state.clients` to the union.

3. **Surfaces a UI hint** (yellow text) under the autocomplete input
   so the user knows the dataset is partial:
   > "Showing affiliates+partners only — full client list unavailable
   > (admin-api error)."

### Acceptance criteria satisfied

- ✅ Fallback fires on `portal.purebrain.ai` now (host gate removed).
- ✅ Dataset is broader than affiliates-only — merges with partners.
- ✅ UI hint visible when fallback runs.
- ✅ Frontend-only change. No SEC review required per SPEC §6 (D1 row).
- ✅ Primary path (`/api/admin/clients`) unchanged — still preferred.

### Better long-term fix (not in this commit, coordinate with wtt-fullstack)

Add `https://staging.purebrain.ai` and `https://portal.purebrain.ai`
to admin-api's CORS allowlist for `/api/admin/clients` so the primary
path works on every host. That requires a Worker change on admin-api
and SEC/QA gate. This frontend commit hardens the fallback regardless.

### Test stub (for QA)

1. Deploy `referral-v1` branch admin/referrals/index.html to a CF Pages
   preview. Hit `https://<preview>.pages.dev/admin/referrals/`.
2. Open browser DevTools → Network. Block `/api/admin/clients`
   (right-click → Block request URL).
3. Open Assign Modal. Type 2+ chars in client search.
4. Confirm: yellow hint appears, autocomplete dropdown shows merged
   affiliates+partners. Console log: `Fallback: loaded N from
   affiliates+partners merge`.
5. Repeat on simulated `portal.purebrain.ai` host (or by spoofing
   `Host` header). Confirm fallback STILL fires (host gate gone).

---

## B3 — 4 payment pages → pb_ref POST at onApprove

**Files**:
- `exports/cf-pages-deploy/awakened/index.html` (line ~5301-5330)
- `exports/cf-pages-deploy/insiders/index.html` (line ~5182-5211)
- `exports/cf-pages-deploy/partnered/index.html` (line ~5370-5399)
- `exports/cf-pages-deploy/unified/index.html` (line ~5318-5347)

**Commit**: `557f307`

### What it does

Adds a fire-and-forget IIFE at the top of `handlePaymentSuccess()` (the
universal hook called by both subscription and one-time PayPal SDK
`onApprove` handlers). When the visitor arrived via `?ref=PB-XXXX`
(captured by the existing pb_ref tracking script that already lives on
these pages and exposes `window.getPbRef`), it POSTs the attribution
data to the portal-proxy.

```javascript
(function() {
  try {
    var refCode = typeof window.getPbRef === 'function' ? window.getPbRef() : null;
    if (!refCode) return;
    var customerEmail = (payerInfo && payerInfo.email_address) ? payerInfo.email_address : '';
    fetch('https://portal.purebrain.ai/api/referral/complete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        pb_ref: refCode,
        payment_id: orderId || '',
        customer_email: customerEmail,
        tier: tier || '',
        source_page: '<page-slug>'
      }),
      keepalive: true
    }).catch(function() { /* fire-and-forget */ });
  } catch (e) { /* never block redirect on attribution failure */ }
})();
```

### Frozen request contract (for B2 — wtt-fullstack)

`POST https://portal.purebrain.ai/api/referral/complete`
(routes through portal-proxy B1 fix → `referrals-api /referrals/complete`)

```json
{
  "pb_ref":         "PB-XXXX",          // referral code from getPbRef()
  "payment_id":     "<paypal order id>", // PayPal order or subscription ID
  "customer_email": "buyer@example.com",  // payerInfo.email_address (may be "")
  "tier":           "Awakened|Insider|Partnered|Unified",
  "source_page":    "awakened|insiders|partnered|unified"
}
```

Expected response (B2 to confirm):
- `200 {ok:true, pending:true, referral_id:N}` on first hit
- `200 {ok:true, pending:true, referral_id:N, idempotent:true}` on
  second hit with same `(pb_ref, payment_id)` (per CTO Edit #4 UNIQUE)
- `400` on missing/invalid pb_ref
- Anything else: B3 swallows it (fire-and-forget).

### Design rationale

- **Inserted at the top of handlePaymentSuccess()** so it fires BEFORE
  the redirect/scroll, with maximum chance of completing.
- **`keepalive: true`** so the request survives page unload.
- **Outer try/catch + .catch()**: attribution failure never breaks
  payment UX. The user's redirect is sacred.
- **Payment guard logic UNTOUCHED** (constitutional per Aether memory).
- **/partners/ page UNTOUCHED** per Jared 5/7 directive.
- **Existing payment behavior preserved** — onApprove flow gets exactly
  ONE additional fire-and-forget fetch.
- **Per CTO §6.Q1**: webhook joins on `payment_id` (more reliable than
  email). Per CTO Edit #4: `(pb_ref, payment_id)` UNIQUE on `referrals`
  table makes this POST idempotent against page-reload double-fires.

### Acceptance criteria satisfied

- ✅ All 4 target pages updated with the IIFE.
- ✅ No deletions — `git diff --stat` shows pure additions (25 lines/page,
  100 lines total).
- ✅ Each insertion verified by `Read` tool after `Edit`.
- ✅ `getPbRef` already defined in each page (lines ~477-490 and
  ~2820-2830 ranges) — no new tracking infrastructure needed.
- ✅ Payment guard untouched.
- ✅ /partners/ untouched.
- ✅ All other onApprove behavior preserved (verifyPaymentServerSide,
  handlePaymentSuccess flow, redirect, callback hooks).

### Integration test stub (for SEC/QA, runs after B2 ships)

Manual flow:
1. Visit `https://<preview>/?ref=PB-TESTQA` — confirms pb_ref captured
   in localStorage (open DevTools → Application → localStorage →
   `pb_ref` should be `PB-TESTQA`).
2. Navigate to one of the 4 payment pages without losing storage:
   `https://<preview>/awakened/`.
3. Verify `window.getPbRef()` returns `PB-TESTQA` in the console.
4. Run a sandbox PayPal payment.
5. In DevTools → Network, confirm a POST to
   `https://portal.purebrain.ai/api/referral/complete` fires AT
   `onApprove` time, with the body shape above.
6. Confirm the redirect to `#awakening` still happens (i.e. attribution
   POST didn't block).
7. Repeat for /insiders/, /partnered/, /unified/.
8. **Idempotency test**: reload the success page (or mash the PayPal
   approve button repeatedly via DevTools network replay). Confirm
   referrals D1 has exactly ONE row per `(pb_ref, payment_id)` pair
   (relies on B2 + CTO Edit #4 UNIQUE constraint).
9. **Failure-mode test**: with admin-api or referrals-api offline,
   confirm the payment redirect STILL completes. Console may show a
   CORS/network error from the fire-and-forget fetch, but UX must be
   unaffected.

Automated test (Playwright stub — to be implemented by qa/browser-vision-tester):

```javascript
// playwright/tests/b3-attribution.spec.js
test.describe('B3 — pb_ref attribution at onApprove', () => {
  for (const page of ['awakened', 'insiders', 'partnered', 'unified']) {
    test(`${page}: fires POST to /api/referral/complete with pb_ref`, async ({ page: p }) => {
      // Set pb_ref in localStorage before navigation
      await p.goto(`https://<preview>/${page}/`);
      await p.evaluate(() => localStorage.setItem('pb_ref', 'PB-AUTOTEST'));

      // Intercept the POST
      const postPromise = p.waitForRequest(req =>
        req.url().includes('/api/referral/complete') && req.method() === 'POST'
      );

      // Trigger handlePaymentSuccess directly (bypass PayPal SDK)
      await p.evaluate(() => {
        window.handlePaymentSuccess('TestTier', 'TEST_ORDER_123', { email_address: 'qa@example.com' });
      });

      const req = await postPromise;
      const body = JSON.parse(req.postData());
      expect(body.pb_ref).toBe('PB-AUTOTEST');
      expect(body.payment_id).toBe('TEST_ORDER_123');
      expect(body.customer_email).toBe('qa@example.com');
      expect(body.source_page).toBe(page);
    });
  }
});
```

---

## Constraints honored (checklist)

- ✅ Code on `referral-v1` branch only — no deploys.
- ✅ No `wrangler deploy` or `wrangler pages deploy` invoked.
- ✅ Live referral system + payment pages on production untouched.
- ✅ Each commit passes pre-commit hooks (verified by successful
  `git commit` exit code 0 — except B1 which got swept into a
  parallel commit but landed correctly).
- ✅ After every Edit on a payment page, READ-back verification done.
- ✅ Payment guard logic NOT modified.
- ✅ /partners/ page NOT touched.
- ✅ All other payment-page behavior preserved — additive change only.

---

## Open coordination items

1. **B2 (wtt-fullstack)**: needs to ship the `/referrals/complete`
   handler rewrite that accepts the frozen contract above and inserts
   into the `referrals` table with `(pb_ref, payment_id)` UNIQUE +
   `INSERT OR IGNORE`. Until B2 ships, B3 POSTs will hit the legacy
   admin-only handler and return 400 — but the fire-and-forget swallows
   it cleanly, so production is safe.

2. **D1 (better fix, optional)**: admin-api CORS allowlist for
   `staging.purebrain.ai` + `portal.purebrain.ai`. Coordinate with
   wtt-fullstack who is touching admin-api.

3. **Payment guard re-check**: My memory note says all 10 payment
   pages must have payment guard logic. I did NOT add or modify that
   logic on these 4 pages — I only added the pb_ref POST inside
   `handlePaymentSuccess`. If guard is missing on any of these 4,
   that is a pre-existing condition, not introduced by this work.

---

## Memory Written

Path: `.claude/memory/agent-learnings/full-stack-developer/2026-05-07--phase3-b1-d1-b3-build.md`
Type: operational + teaching
Topic: Phase 3 BUILD execution — portal-proxy path fix, admin frontend
host-gate removal, 4-page onApprove pb_ref wiring, parallel-agent
commit collision pattern.
