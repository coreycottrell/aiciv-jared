# /tiers/ Page Spot-Check — 2026-05-07

**Auditor**: browser-vision-tester
**Spec**: `exports/portal-files/NEW-ONBOARDING-FLOW-SPEC-2026-04-01.md` §6–7
**Mode**: READ-ONLY (no payments triggered)
**Live URL**: https://purebrain.ai/tiers/
**Local file**: `exports/cf-pages-deploy/tiers/index.html` (1853 lines, minified — newer than live)
**Live file**: 972 lines, formatted (this is what production serves)

## Page Role
**Tier comparison + checkout combo.** Three tier cards (Awakened/Partnered/Unified) → click → PayPal modal opens (live SDK, real subscriptions). NO awakening chat, NO naming ceremony — recovery checkout only.

## Per-Check Matrix (against live)

| Check | Result | Evidence |
|-------|--------|----------|
| HTTP 200 | ✅ | `curl -s -o /dev/null -w "%{http_code}"` → 200 |
| PayPal SDK live ClientId | ✅ | line 550: `AWgWNlBQAy5BMXKB5xbaMwSk01WkatC08b5rTj_…` (matches awakened) |
| Plan IDs (real subscriptions) | ✅ | lines 552–556: P-2SA…/P-3VH…/P-43A… |
| `createSubscription` for tiers w/ planId | ✅ | line 712 |
| `createOrder` fallback | ✅ | line 738 |
| `window.onPaymentComplete` callback fires | ✅ | line 900 (inline, not via `/js/payment-glue.js`) |
| Redirect to `/thank-you/` | ⚠️ **PARTIAL** | line 565 `RETURN_URL = 'https://purebrain.ai/thank-you/'`; line 907–909: `setTimeout(…RETURN_URL, 2000)` — **redirects to bare `/thank-you/`, NO query params** |
| `aiName/name/email/tier` query params | ❌ **MISSING** | spec §6 line 238 mandates `?aiName=…&name=…&email=…&tier=…`; live tiers redirects to `/thank-you/` with zero params |
| `custom_id` includes session UUID | ❌ **MISSING** | line 742: `custom_id: 'PB-' + tier.toUpperCase() + '-TIERS'` (static label, no UUID) |
| `fireSeed()` BEFORE redirect | ❌ **MISSING** | spec §6 rule: seed fires → 300ms → redirect. `handlePaymentSuccess` (line 887) has NO `fireSeed()` call. Witness gets no seed from /tiers/ payments. |

## Severity: 🔴 RED

## What's Missing (vs spec)
1. **No session UUID generated** — no `_pbSessionId`/`crypto.randomUUID()` at page load
2. **No `fireSeed()`** — Witness never receives seed payload from /tiers/ checkouts → magic link pipeline never triggers → customer stuck on bare `/thank-you/`
3. **No URL params in redirect** — thank-you page can't personalize (no aiName/email to poll magic link with)
4. **No naming ceremony state** — `aiName` is never collected on this page; would need either (a) own ceremony or (b) recovery query-string ingestion (`?aiName=…` on landing) preserved through to redirect
5. **`custom_id` lacks session UUID** — Witness UUID-matching strategy (spec §8 S2) cannot match payments back to session

## Estimated Fix
~45–90 min for ST# (full-stack-developer):
- Lift `<script>` block from `/awakened/index.html` (`fireSeed`, sessionUuid, payment-glue) — already proven on 5 sister pages
- Either gate /tiers/ behind ceremony OR accept `?aiName=…&name=…&email=…` from inbound recovery link and persist into seed/redirect
- Add `custom_id: 'PB-{TIER}-TIERS-{sessionUuid}'`
- Update `RETURN_URL` builder to append params before `window.location.href`

## Behavior on Post-Payment (current)
Modal closes → green success banner (6s) → 2s timeout → `window.location.href = 'https://purebrain.ai/thank-you/'` (no params, no seed, no UUID). Customer reaches /thank-you/ but polling URL has no email/UUID → permanent spinner.

## Recommendation
Route /tiers/ to ST# for spec §6 alignment. Until fixed, do NOT advertise /tiers/ as recovery page — customers paying through it become orphaned (paid + no seed + no magic link). Either fix or temporarily redirect /tiers/ → /awakened/.
