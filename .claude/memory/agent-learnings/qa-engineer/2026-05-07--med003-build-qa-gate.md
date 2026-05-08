# MED-003 BUILD QA Gate — commit 250f5f5

**Date**: 2026-05-07
**Type**: operational + teaching
**Topic**: 7-test independent QA gate for `window.pbSessionUuid` escape-hatch
**Verdict**: PASS — cleared for SHIP

## Context

CTO pre-build review (2026-05-07) flagged `const X` at script top-level does NOT create `window.X` in classic `<script>` tags — root cause of MED-003 second-order bug. BUILD shipped commit 250f5f5 on `main` (worktree only, not pushed) with `window.pbSessionUuid` minimal-projection escape hatch on 5 LIVE pages + custom_id added to PayPal `createSubscription` blocks + `js/payment-background.js` + `js/homepage-payment.js` migrated.

## QA strategy that worked

Independent re-run of BUILD's self-reported `tools/verify-payment-pages-pbsessionuuid.sh` (14/14 PASS) plus 6 additional behavioral checks:

1. **Static change-counts**: grep for exact change patterns (1 of each per page).
2. **Cross-file logger threading**: confirm L414/L421 + L457/L552 per CTO citation.
3. **PII regression**: 0 hits for `window.aiName|payTestData.name|payTestData.email` — sensitive fields stayed scope-isolated.
4. **Race-safe placement**: confirmed `crypto.randomUUID()` line precedes `window.pbSessionUuid =` line by exactly +1 on every page (no read-before-write race).
5. **Syntax validation**: `node --check` on JS files + visual line-pair inspection of HTML inline JS.
6. **Live-vs-local sanity**: `curl https://purebrain.ai/awakened/ | grep -c 'window.pbSessionUuid'` = 0; local file = 2. Confirms build on disk but not deployed.

## Key teaching

**Race-safe placement check is the high-leverage test.** A correct grep count (Test 2) doesn't catch order bugs. Diff between line numbers of generator and projector is the fastest way to confirm no consumer can race-read `undefined`. Future window-projection patterns should bake this into the assertion script, not just the QA pass.

## Specific findings

- 5 LIVE pages all have `window.pbSessionUuid =` at line N+1 where N is `crypto.randomUUID()` — race-safe.
- Local count = 2 per LIVE page (escape-hatch + custom_id), not 1 — both expected.
- `verifyPaymentServerSide` retains direct `payTestData.sessionUuid` read (same script tag, scope works) — CTO review confirmed this is correct, only cross-script-tag readers needed migration.
- Commit scope was clean: 8 files, no collateral.

## Caveats flagged (non-blocking)

- Sandbox/test pages (pay-test-sandbox-3/5, home-test-*) still have the original scope-bug pattern. Flag for future sprint.
- `/insiders/awakened/` LIVE page mentioned in CTO review but not in BUILD's 5-page scope — flag for parity audit post-deploy.
- Static-source only — full SHIP confidence wants browser-vision-tester E2E + JSONL tail per CTO §6.3.

## Files referenced

- BUILD receipt: `exports/portal-files/med003-build-receipt-2026-05-07.md`
- CTO pre-build review: `.claude/memory/agent-learnings/cto/2026-05-07--med003-fix-prebuild-review.md`
- QA deliverable: `exports/portal-files/qa-med003-build-2026-05-07.md`
- Assertion script: `tools/verify-payment-pages-pbsessionuuid.sh`

## Tags

qa-gate, MED-003, pbSessionUuid, race-safe-placement, scope-isolation, paypal-custom-id, ship-gate, build-verification
