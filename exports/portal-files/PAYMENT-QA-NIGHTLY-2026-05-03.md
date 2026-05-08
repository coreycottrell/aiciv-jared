# Nightly Payment Pages QA — 2026-05-03 02:15 UTC

**Run by:** browser-vision-tester (BOOP `onboarding-flow-qa-nightly`)
**Pages tested:** 12 (10 in payment guard list + 2 insiders subpaths)

---

## 🔴 P0 BUG — `/insiders/pay-test-awakened/` IS A HOMEPAGE CLONE

**Same bug class as `/insiders/awakened/` rot fixed Apr 29. The sister page rotted next.**

URL: https://purebrain.ai/insiders/pay-test-awakened/

Symptoms (live, just confirmed):
- **Title:** `Elementor #1502 - Pure Brain` (should be PureBrain Insider Awakened tier)
- **WordPress admin bar leaking** (`wp-admin-bar-root-default`, "Howdy, Jared Sanborn" visible to public)
- **GoDaddy/WPaaS tracking present** (16 refs: `_trfq`, `_trfd`, `scc-c2`, `wpaas`, `secureserver.net`)
- **PayPal preconnect: 0** (must be ≥1 per pre-deploy gate)
- **PayPal plan IDs in file**: `P-2SA65600MT088594TNGLTFKY`, `P-3VH43554A66001716NGLTFKY`, `P-43A28944XN5237411NGLTFLA` — these are the homepage's three-tier plans, not the Awakened insider plan `P-8AU4270420374002JNGY3VYQ`
- **Pricing: $149, $499** (no $74.50 insider price)

This is the WordPress homepage from purebrain.ai bleeding through to a payment URL. The `exports/cf-pages-deploy/insiders/pay-test-awakened/index.html` file was never replaced after Elementor #1502 rot.

**Resolution path (precedent: `/insiders/awakened/` Apr 29 → May 2):**
1. Either deploy a meta-refresh redirect to `/awakened/` (matches what `/insiders/awakened/` does now), OR
2. Build a real Awakened-insider variant page with $74.50 + plan `P-8AU4270420374002JNGY3VYQ`

**Routing:** ST# (systems-technology) — same fix pattern as commit `607437e`. Then OP# to add `/insiders/pay-test-awakened/` to the pre-deploy guard's per-URL marker checks (title must NOT contain "Elementor", PayPal preconnect ≥1).

---

## ✅ PASSING (11/12)

| URL | HTTP | Title OK | PayPal SDK | Preconnect | GoDaddy/WP | Pricing |
|-----|------|----------|------------|------------|------------|---------|
| `purebrain.ai/` (HOMEPAGE) | 200 | ✅ Agentic AI | 10 | 2 | 0 | $149 / $499 / $999 |
| `purebrain.ai/live/` | 200 | ✅ Agentic AI | 10 | 2 | 0 | $149 / $499 / $999 |
| `purebrain.ai/insiders/` | 200 | ✅ Insiders Only | 10 | 2 | 0 | $74.50 |
| `purebrain.ai/awakened/` | 200 | ✅ Awaken Yours | 10 | 2 | 0 | $149 |
| `purebrain.ai/partnered/` | 200 | ✅ Awaken Yours | 10 | 2 | 0 | $149 / $499 |
| `purebrain.ai/unified/` | 200 | ✅ Awaken Yours | 10 | 2 | 0 | $149 / $999 |
| `purebrain.ai/pay-test-sandbox-3/` | 200 | ✅ Awaken Yours | 10 | 2 | 0 | $149 / $499 / $999 |
| `purebrain.ai/insiders/awakened/` | 200 | ✅ Meta-refresh → /awakened/ | n/a (redirect) | n/a | n/a | n/a |
| `purebrain.ai/home-test-live-1/` | 200 | ✅ Agentic AI + pwd gate | 10 | — | 0 | $149 / $499 |
| `purebrain.ai/home-test-sandbox/` | 200 | ✅ Agentic AI + pwd gate | 10 | — | 0 | $149 / $499 / $999 |
| `purebrain.ai/home-test/` | 200 | ✅ Agentic AI + pwd gate | 10 | — | 0 | $149 / $499 / $999 |

All passing pages have:
- Valid PayPal SDK refs
- Chatbox markers present
- UUID + seed-flow JS present
- No GoDaddy/WordPress tracking leak
- Tier-appropriate pricing

---

## 👁️ Observations (not bugs, FYI)

- `/partnered/` shows `$149 / $499` only (no $999) and `/unified/` shows `$149 / $999` only (no $499) — these may be intentional A/B variants. Verify with ONBOARDING-SPEC if these tier configs are correct.
- `/home-test-live-1/` shows `$149 / $499` only — same — verify intent.
- `/insiders/awakened/` correctly redirects via meta-refresh to `/awakened/` (May 2 fix holding).

---

## Action Required

1. **ST#** — fix `/insiders/pay-test-awakened/` (homepage clone rot). Recommend meta-refresh redirect to `/pay-test-sandbox-3/` since this is the pay-test variant. ETA: same-day fix.
2. **OP#** — add per-URL marker assertions to nightly-payment-pages-qa BOOP so future Elementor-clone rot trips alarm immediately, not 4 days later.
3. **Sweep all `/{tier}/` directories** for similar parent/child rot per the Apr 29 directive in `feedback_insiders_subpaths_in_payment_guard.md`. This is the second occurrence of the same pattern — the rot is structural.
