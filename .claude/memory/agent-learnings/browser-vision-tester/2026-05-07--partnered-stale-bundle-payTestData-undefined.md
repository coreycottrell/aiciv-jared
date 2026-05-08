# 2026-05-07 — /partnered/ stale bundle: payTestData undefined, free-form chat instead of structured ceremony

**Type**: gotcha + operational
**Topic**: Customer-impact onboarding regression on https://purebrain.ai/partnered/
**Confidence**: high

## Context

URGENT live E2E test of the partnered payment page. Jared said "worked perfectly few days ago, broken now." Two events today: `git reset --hard` 15:33 UTC, `purebrain-portal-proxy` worker deployed 16:27 UTC.

## Discovery

The page is NOT 5xx. HTTP 200, 455KB, chat opens, AI responds, log-conversation POSTs return 200 (server JSONL count growing). The break is **client-side state machine regression**:

1. **`window.payTestData` is undefined** — spec §2 mandates this globally to carry sessionUuid/aiName/name/email/tier through the funnel. Without it, `/api/verify-payment` and `/api/send-seed` cannot be called by the client → no seed → no magic link → no portal access.
2. **Naming ceremony is free-form** — AI chats philosophically about names instead of structurally capturing inputs. Customer types AI name "Sage", AI replies "I don't have a name yet". Customer types email, AI doesn't advance.
3. **`fireSeedAddendum` still in HTML** — spec §16 says it was REMOVED 2026-04-01. Its presence is a fingerprint of an older bundle.
4. **Pricing/CTAs render correctly below-fold** with `pb-cta-unlocked` class — but unreachable while chat modal blocks the page.

## Why portal-proxy was NOT the cause

api.purebrain.ai is fully healthy. All 7 endpoints (health, pipeline-health, log-conversation, verify-payment, send-seed, magic-link, stats) returned correct codes. CF still proxies to 89.167.19.20.

## Why this matters

- **Customer impact**: Anyone landing on `/partnered/` since the regression cannot complete payment. They chat forever, never see PayPal, never seed, never get magic link.
- **Trust**: This is THE money-flow page for the $499 tier.
- **Rollback target**: NOT the worker — it's the static HTML at `exports/cf-pages-deploy/partnered/index.html` reverted by today's `git reset --hard 15:33 UTC`.

## How to apply in future

When Jared says "X was working a few days ago" and there's been a recent `git reset --hard` in the same session:

1. **First trace the static asset** (HTML/JS in `exports/cf-pages-deploy/`) NOT the workers. Reset wipes runtime logs but also unstages frontend changes.
2. Run a real Playwright session on the live URL — vision-only inspection misses state-machine bugs (chat *looks* right but `window.payTestData` is undefined).
3. Test this specific assertion every time: `await page.evaluate(() => typeof window.payTestData)`. If `"undefined"`, the client funnel is broken regardless of what the chat appears to do.
4. Verify by spec §16 fingerprints: presence of `fireSeedAddendum` = old bundle; absence = new bundle.

## Test commands that worked

```bash
# Live page fetch + structural audit
curl -s -o /tmp/p.html -w "%{http_code}\n" https://purebrain.ai/partnered/
grep -c "fireSeedAddendum\|payTestData\|onConsentChange" /tmp/p.html

# API endpoint sweep (fast)
for ep in health pipeline-health stats; do
  curl -s "https://api.purebrain.ai/api/$ep" -w "[%{http_code}]\n"
done

# Playwright key assertion
# await page.evaluate(() => typeof window.payTestData)  # should be "object" not "undefined"
```

## Files / evidence

- Test report: `exports/portal-files/partnered-live-e2e-test-2026-05-07.md`
- Screenshots: `/tmp/partnered-shots/` and `/tmp/partnered-shots-v2/`
- Spec: `exports/portal-files/NEW-ONBOARDING-FLOW-SPEC-2026-04-01.md` §2, §6, §16

## Tags
browser-vision, partnered, onboarding-regression, payTestData, stale-bundle, git-reset-impact, payment-funnel, constitutional-onboarding-spec
