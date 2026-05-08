# Nightly Onboarding Flow QA — 2026-04-29

**Run by**: browser-vision-tester (BOOP `onboarding-flow-qa-nightly`)
**Time**: 2026-04-29 (UTC)
**Method**: HTTP probes + content-integrity grep checks against live `purebrain.ai`
**Reference**: `.claude/ONBOARDING-SPEC-DEFINITIVE.md` (Section 1, Landing Pages Inventory)

---

## Summary

| Status | Count |
|--------|-------|
| PASS (200, payment infra intact) | 9 |
| FAIL (404 / not deployed) | 6 |
| Non-payment lead magnet (200, expected) | 1 |

**Critical finding**: 5 of the 8 BOOP-listed payment URLs return 404. Inspection of `ONBOARDING-SPEC-DEFINITIVE.md` confirms these paths are **NOT** part of the constitutional landing-pages inventory. They are either deprecated, vanity URLs that were never deployed, or external references in stale docs. Spec-listed live payment pages are healthy. **One spec-listed page (`/insiders/awakened/`) IS missing — that is a real regression.**

---

## Per-Page Results (BOOP-listed order)

### 1. `https://purebrain.ai/` (HOMEPAGE) — PASS
- HTTP 200, 644,685 bytes
- PayPal SDK loaded, button container `#pb-paypal-buttons-container` present
- 3 LIVE subscription Plan IDs present (P-2SA…, P-3VH…, P-43A…)
- Pricing visible: $149 / $499 / $999 (correct tier pricing)
- Brand colors confirmed: `#2a93c1` (142 occurrences), `#f1420b` (177 occurrences)
- Naming ceremony, consent gate, seed pipeline references all present
- Viewport meta tag set (mobile responsive)
- Title: "PURE BRAIN - Your Brain. Your AI. Actual Intelligence! - Agentic AI"

### 2. `https://purebrain.ai/get-started/` — PASS (NOT a payment page)
- HTTP 200, 63,159 bytes
- Title: "Tether Revival Guide — PureBrain AI"
- This is a **lead magnet / guide page**, not a payment page. No PayPal SDK expected. Brand colors present.
- BOOP task incorrectly listed this as a payment page; treating as info-only.

### 3. `https://purebrain.ai/get-purebrain/` — FAIL (404)
- Serves PureBrain's branded "Page Not Found" template (1,201 bytes)
- **Not in ONBOARDING-SPEC inventory**. Likely deprecated vanity URL.

### 4. `https://purebrain.ai/start/` — FAIL (404)
- 404 PureBrain template. Not in spec.

### 5. `https://purebrain.ai/launch/` — FAIL (404)
- 404 PureBrain template. Not in spec.

### 6. `https://purebrain.ai/begin/` — FAIL (404)
- 404 PureBrain template. Not in spec.

### 7. `https://purebrain.ai/activate/` — FAIL (404)
- 404 PureBrain template. Not in spec.

### 8. `https://purebrain.ai/home-test/` — PASS
- HTTP 200, 641,585 bytes
- PayPal SDK + button container present, 3 Plan IDs
- Brand colors and onboarding gates intact
- Mirror of homepage as expected per spec

---

## Spec-Listed Live Pages (additional coverage)

| URL | Status | Notes |
|-----|--------|-------|
| `/live/` | PASS | 200, PayPal+plans+brand colors |
| `/awakened/` | PASS | 200, PayPal+plans+brand colors |
| `/partnered/` | PASS | 200, PayPal+plans+brand colors |
| `/unified/` | PASS | 200, PayPal+plans+brand colors |
| `/insiders/` | PASS | 200, PayPal+plans+brand colors |
| `/insiders/awakened/` | **FAIL** | **404 — IS in spec, should be deployed at $74.50 insider price** |
| `/thank-you/` | PASS | 200, post-payment redirect destination |

---

## Regressions Requiring Action

### REGRESSION 1 (HIGH): `/insiders/awakened/` returns 404
- Listed in `ONBOARDING-SPEC-DEFINITIVE.md` as a LIVE subscription page at $74.50 insider price.
- Currently 404. Either undeployed or deleted.
- **Route to**: ST# (Systems & Technology) — verify `exports/cf-pages-deploy/insiders/awakened/index.html` exists and is in latest deploy of `purebrain-production`.

### CLARIFICATION (LOW): BOOP task page list is stale
- The BOOP task lists `/get-purebrain/`, `/start/`, `/launch/`, `/begin/`, `/activate/` as payment pages.
- None of these are in the constitutional spec. They are likely vanity URLs from older marketing experiments.
- **Recommendation**: Update the `onboarding-flow-qa-nightly` BOOP definition to use the spec-listed pages: `/`, `/live/`, `/awakened/`, `/partnered/`, `/unified/`, `/insiders/`, `/insiders/awakened/`, `/home-test/`. This brings the nightly check into alignment with the constitutional source of truth.

---

## What Passed Cleanly (No Action Needed)

- Homepage payment integrity (the most-trafficked page) — fully intact
- All 5 individual tier pages (`/awakened/`, `/partnered/`, `/unified/`, `/insiders/`, `/live/`)
- Brand color compliance across all live pages
- LIVE PayPal subscription Plan IDs (3 distinct plans on each tier page)
- `/home-test/` and `/thank-you/` working

---

## Verification Method (Read-Only)

Per payment-flow-qa rules, no code was modified. Checks performed:
1. `curl -L -w "%{http_code}|%{size_download}"` HTTP probe with redirect follow
2. Content grep: `paypal.com/sdk`, `pb-paypal-buttons-container`, `P-[A-Z0-9]+` (Plan IDs), `2a93c1`, `f1420b`, `consent`, `<title>`, viewport meta
3. Cross-reference against `.claude/ONBOARDING-SPEC-DEFINITIVE.md` Section 1

---

## Memory Written

- Path: `.claude/memory/agent-learnings/browser-vision-tester/2026-04-29--nightly-qa-boop-page-list-stale.md`
- Type: gotcha
- Topic: BOOP page list drift from constitutional spec — always cross-check spec
