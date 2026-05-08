# /insiders/ Regression Repair (May 2 nightly QA findings)

**Date**: 2026-05-02
**Type**: operational + teaching
**Agent**: dept-systems-technology
**Trigger**: ST# routing from Aether after nightly-onboarding-qa-findings (browser-vision-tester) crossed 3+-failure threshold

## Context

Nightly E2E QA found three /insiders/ regressions. Two were ship-able as spec-compliance fixes
(no pricing changes); one was blocked on Jared input (pricing drift on /insiders/ index).

## What Shipped

### Item 1: /insiders/awakened/ -> /awakened/ redirect (404 fix)

- Before: HTTP 404 in production. Source at `exports/cf-pages-deploy/insiders/awakened/index.html`
  was the rotted (Apr 21) homepage clone with WRONG `$74.50` and WRONG plan
  `P-8AU4270420374002JNGY3VYQ` (vs spec `$149` + `P-2SA65600MT088594TNGLTFKY`).
- Action:
  1. Backed up rotted source to `_archived/insiders-awakened-2026-05-02/index.html` (446066 bytes).
  2. First attempt: added redirect rules to `_redirects` (lines 6-8). Deployed. **Did not fire.**
     This matches the Apr 15 "gotcha" memo. Discovered root cause (see Pattern below).
  3. Second attempt: replaced source with a meta-refresh + JS HTML redirect to `/awakened/`.
     This works because CF Pages serves it as a static page (the Apr 15 "fallback" pattern
     applied deliberately).
  4. Deployed to `purebrain-production` (deploy `5240b841-1a69-4752-a1dd-a76b950b2f65`).
  5. CF cache purged via API.
- After: HTTP 200, meta-refresh + JS redirect to `/awakened/`. Canonical `/awakened/` carries
  spec-compliant `$149` + plan `P-2SA65600MT088594TNGLTFKY`.
- File: `exports/cf-pages-deploy/insiders/awakened/index.html` (~1.3 KB, redirect-only)

### Item 2: /insiders/pay-test-awakened/ forbidden markers + fireSeed restoration

- Before:
  - `launchPostPaymentFlow`: 4 occurrences (forbidden per spec Rule 5)
  - `_postPaymentLaunched`: 3 occurrences (forbidden per spec Rule 5)
  - `postPaymentOverlay`: 0 (already clean)
  - `fireSeed`: 0 (CONCERNING — seed flow broken)
  - Pricing: correct (`$149` + `P-2SA65600MT088594TNGLTFKY`)
- Action (surgical Python edit):
  1. Backed up to `_archived/insiders-awakened-2026-05-02/pay-test-awakened-index.html.bak` (784595 bytes).
  2. Removed entire forbidden IIFE block (`/* === Integration Glue === */` through closing `})();`),
     ~135 lines / 4685 bytes. This block defined the deprecated post-payment chatbox flow.
  3. Replaced with spec-compliant code:
     - `fireSeed()` function modeled on canonical `/awakened/` line 7789 (with safe `typeof` guards
       since `payTestData` may not be defined at all callsites here).
     - `window.onPaymentComplete(tier, orderId, payerInfo)` that:
       - Stamps `payTestData.tierPaid` and `payTestData.orderId`.
       - Calls `fireSeed()` immediately.
       - 300ms delay (per spec Rule 4) then `window.location.href = '/thank-you/' + qs`
         where `qs` includes `order_id`, `tier`, `session_uuid`.
  4. Added `fireSeed();` call to questionnaire flow right after `payTestData.email = email;`
     (line 15643) per spec section 3.
  5. Deployed to `purebrain-production` (deploy `3fad7adb-199f-45e1-9047-f0deb4fc8217`).
  6. CF cache purged.
- After:
  - Forbidden markers: 0
  - `fireSeed` occurrences: 5 (function def + email-time call + post-payment call + 2 internal refs)
  - `postPaymentOverlay`: 0
  - Pricing: unchanged (`$149` + correct plan) — DID NOT TOUCH per routing rule

## What Did NOT Ship (correctly held)

- **/insiders/ index pricing drift**: $74.50 -> $149 + plan ID swap.
  Per investor-codes-frozen rule + nightly guard rules, NEVER auto-fix pricing.
  Remains alerted-to-Jared. Not in this ship.

## Verification (production curl)

```
$ curl -sI https://purebrain.ai/insiders/awakened/
HTTP/2 200

$ curl -s https://purebrain.ai/insiders/awakened/ | grep -E 'meta http-equiv="refresh"|window\.location\.replace|/awakened/'
    <meta http-equiv="refresh" content="0; url=/awakened/">
    <link rel="canonical" href="https://purebrain.ai/awakened/">
    <title>Redirecting to /awakened/ - PureBrain</title>
    [...]
        window.location.replace('/awakened/' + window.location.search + window.location.hash);

$ curl -s https://purebrain.ai/awakened/ | grep -E "P-2SA65600MT088594TNGLTFKY|'149\.00'"
    Awakened:  'P-2SA65600MT088594TNGLTFKY',
    Awakened:  '149.00',

$ curl -sI https://purebrain.ai/insiders/pay-test-awakened/
HTTP/2 200

$ curl -s https://purebrain.ai/insiders/pay-test-awakened/ | grep -c -E "launchPostPaymentFlow|_postPaymentLaunched|postPaymentOverlay"
0

$ curl -s https://purebrain.ai/insiders/pay-test-awakened/ | grep -c "fireSeed"
5

$ curl -s https://purebrain.ai/insiders/pay-test-awakened/ | grep -E "P-2SA65600MT088594TNGLTFKY|'149\.00'"
    Awakened:  'P-2SA65600MT088594TNGLTFKY',
    Awakened:  '149.00',
```

All assertions per ST# routing pass.

## Pattern Discovered (TEACHING)

**`_redirects` rules deployed via `cf-deploy.py` are NOT processed as redirect rules by CF Pages.**

- The Apr 15 ptt-fullstack memo flagged this as a gotcha but didn't isolate root cause.
- Today confirmed empirically: NO redirect rule (mine or any of the existing 733 blog/wp-content
  rules) actually fires on a `purebrain-production` deployment created via `cf-deploy.py`.
- The `_redirects` file IS in the deployment manifest at `/_redirects`, served as
  `application/octet-stream`, but CF Pages doesn't parse it as redirect rules.
- Root cause hypothesis: CF Pages parses `_redirects` only on **build-pipeline deploys**
  (Wrangler / Direct Upload via build hook). The Pages API used by `cf-deploy.py` adds files
  to an existing deployment without re-parsing build-time configs.
- Wrangler is BANNED constitutionally (deletes pages, lost 30hr investor build).
- **Workaround pattern**: serve a static HTML page with `<meta http-equiv="refresh">` +
  `window.location.replace()` for path redirects. Works for any path that needs to bounce
  to another path within the same site. This is what Apr 15 implicitly relied on
  (CF Pages serving the parent `/insiders/` index as fallback) but is now an explicit pattern.
- **Implication**: any future redirect via this deploy path MUST use HTML redirect pages,
  not `_redirects` entries.

## Files Touched

- Created: `exports/cf-pages-deploy/insiders/awakened/index.html` (HTML redirect, ~1.3 KB)
- Modified: `exports/cf-pages-deploy/insiders/pay-test-awakened/index.html`
  (removed 135-line forbidden IIFE; added spec-compliant fireSeed + onPaymentComplete)
- Modified: `exports/cf-pages-deploy/_redirects` (added 3 redirect lines at top — they don't fire,
  but they document the intent and act as a no-op fallback if CF Pages config changes later)
- Backups in: `exports/cf-pages-deploy/_archived/insiders-awakened-2026-05-02/`
  - `index.html` (rotted insiders/awakened source)
  - `pay-test-awakened-index.html.bak` (pre-edit pay-test-awakened source)
  - `_redirects.bak` (pre-edit _redirects)

## Deploys (purebrain-production)

| ID | Purpose |
|---|---|
| `686838a4-11b9-45ad-bace-6d7552f12ec6` | _redirects update + delete rotted insiders/awakened (didn't fix - rules don't fire) |
| `4e2481e0-1e75-4270-97d6-2a5f5af583e1` | Refined _redirects rules (still didn't fire) |
| `5240b841-1a69-4752-a1dd-a76b950b2f65` | HTML redirect page for /insiders/awakened/ — FIXED Item 1 |
| `3fad7adb-199f-45e1-9047-f0deb4fc8217` | Forbidden markers removed + fireSeed restored on /insiders/pay-test-awakened/ — FIXED Item 2 |

## Pair-Verification Handoff to OP#

Per `feedback_routed_items_need_verification_boop.md` + `feedback_verifier_independence_audit_separation.md`:

**Verifier**: operations-analyst (OP#) — independent from ST#.
**What to verify**:
1. `curl -sI https://purebrain.ai/insiders/awakened/` returns 200, HTML contains
   `<meta http-equiv="refresh"...url=/awakened/`. (Or use Playwright and confirm browser
   lands on `/awakened/` after meta refresh.)
2. `curl -s https://purebrain.ai/awakened/` HTML contains both `P-2SA65600MT088594TNGLTFKY`
   and `'149.00'`.
3. `curl -s https://purebrain.ai/insiders/pay-test-awakened/` HTML contains:
   - 0 occurrences of `launchPostPaymentFlow`
   - 0 occurrences of `_postPaymentLaunched`
   - 0 occurrences of `postPaymentOverlay`
   - >=4 occurrences of `fireSeed`
   - Both `P-2SA65600MT088594TNGLTFKY` and `'149.00'` (pricing untouched)
4. (Stretch) Run a no-money click-through with Playwright on /insiders/pay-test-awakened/
   to confirm naming ceremony still works and no JS errors fire on payment-button click.

**Status**: Handoff queued. Aether (Primary) needs to dispatch OP# verification BOOP.
This memo is the artifact for that BOOP.

## Anti-Patterns Avoided

1. **Did NOT touch /insiders/ pricing** despite verification expectation pressure. Per nightly guard
   + investor-frozen rule, only Jared can approve pricing changes. Held that line.
2. **Did NOT use Wrangler** despite `_redirects` not firing. Wrangler is BANNED. Found the
   meta-refresh workaround instead.
3. **Did NOT skip the `_redirects` attempt** before falling back to HTML redirect — empirically
   verified the failure on this code path so the memo can teach future agents.
4. **Did NOT touch the canonical `/awakened/` page** — it's the source of truth for spec pricing.
   Only redirected TO it, never modified it.
