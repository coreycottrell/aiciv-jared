# 2026-05-07 — Phase 2 E2E Sweep: window.pbSessionUuid escape hatch verified, payment-background.js drift discovered

**Type**: operational + gotcha + teaching
**Topic**: Post-SHIP verification of MED-003 fix on all 10 payment pages
**Confidence**: high

## Context

Jared shipped 4 changes today before this sweep:
1. S5 fuzzy fallback DISABLED in dispatcher
2. `window.pbSessionUuid` exposed on 5 LIVE pages
3. `createSubscription` blocks now include `custom_id: 'PB-{tier}-{sessionUuid}'`
4. Chat-side logger reads `window.pbSessionUuid`

Phase 2 sweep ran a real Playwright walkthrough of all 10 payment pages × 12 checks per page (120 cells).

## Discovery 1: Homepage works end-to-end (gold standard)

`window.pbSessionUuid = 07b886f6-...` flows correctly to:
- `payTestData.sessionUuid` (in inline IIFE)
- `sessionStorage.getItem('pb_sessionUuid')` (set on page load)
- chat-side `/api/log-conversation` POST `session_uuid` + `metadata.sessionUuid` field
- `custom_id: 'PB-' + tier.toUpperCase() + '-' + (window.pbSessionUuid || '')` template
- `/thank-you/` magic-link polling URL

## Discovery 2: Tier pages send `session_uuid: null` in chat-side log-conversation

Tier pages (awakened/partnered/unified/insiders) load `payment-background.js` which has line 414:

```js
session_uuid: (typeof payTestData !== 'undefined' && payTestData.sessionUuid) ? payTestData.sessionUuid : null,
```

This was supposedly updated to read `window.pbSessionUuid` per task context, but `grep -n "pbSessionUuid" payment-background.js` returns ZERO matches. The script still reads `payTestData` which is `const`-scoped inside an inline IIFE per MED-003 — so `typeof payTestData` returns `undefined` from the external script's scope.

**Real network capture from `/partnered/`**:
```json
{"source":"purebrain","aiName":null,"session_uuid":null,"metadata":{...,"sessionUuid":null}}
```

Homepage doesn't have this drift because its inline chat logger uses `sessionStorage.getItem('pb_sessionUuid')` fallback (line 15660 of homepage HTML). Tier pages do not.

## Discovery 3: /insiders/ pricing violation persists 5+ days

Same finding as `2026-05-02--nightly-onboarding-qa-findings.md`: `/insiders/` serves $74.50 + plan `P-8AU427...` instead of spec-required $149 + plan `P-2SA65600...`. Per `feedback_day3_default_policy_unblocks_jared_dependency.md`, Day-3 default applies (>3 days = ship documented default).

## Discovery 4: pay-test-sandbox-5 is a 5KB stub

Returns 200, listed in spec §1, but has no PayPal SDK, no PRICES, no consent gate, no chat. Either complete or remove from spec inventory.

## How to apply

When the task brief says "X is shipped + production verified", verify the claim with:

1. **Real Playwright walkthrough** with network capture — not just static grep. Static grep would have missed this drift because `custom_id: 'PB-' + tier.toUpperCase() + '-' + (window.pbSessionUuid || '')` IS in the HTML. The bug is in a SEPARATE file (`payment-background.js`) that wasn't updated.

2. **Check both files when claim says "chat-side logger reads X"**:
   - Inline `<script>` blocks in HTML
   - External `/js/payment-background.js`, `/js/homepage-payment.js`, etc.
   - Use `grep -n "X" exports/cf-pages-deploy/js/*.js` to verify external file actually reads X.

3. **Don't trust `typeof payTestData !== 'undefined'` checks** when MED-003 has scoped `payTestData` to an IIFE. The external script's check will always be `undefined`. Use `window.X` escape hatches.

4. **Sandbox-safe test markers** that prevent real seed pollution:
   - `orderId: 'E2E-TEST-{timestamp}'` (matches spec §8 starts-with detection)
   - `isSandbox: true` + `testRun: true` flags
   - email `qa-test-{slug}@aether-test.invalid` (NOT @example.com — those go to Jared per Rule 9)

## Tags

browser-vision, phase2-sweep, payment-funnel, window-pbSessionUuid, MED-003, payment-background-js, IIFE-scoping, custom-id, magic-link-polling, insiders-pricing-drift, constitutional-violation

## Files

- Test runner: `/tmp/phase2-sweep/e2e_sweep_v2.py`
- Results JSON: `/tmp/phase2-sweep/results_v2.json`
- Deliverable: `exports/portal-files/phase2-e2e-sweep-2026-05-07.md`
- 40 screenshots: `/tmp/phase2-sweep/v2_*_*.png`
- 10 HTML snapshots: `/tmp/phase2-sweep/{slug}.html`
