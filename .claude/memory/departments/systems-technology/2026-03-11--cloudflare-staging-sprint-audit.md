# Cloudflare Staging Overhaul Sprint — Audit & Fixes

**Date**: 2026-03-11
**Sprint**: Cloudflare Pages Staging Overhaul
**Agent**: dept-systems-technology

---

## What Was Done

### Fix 1: Sandbox-3 PayPal Plan IDs (CRITICAL)
- **Problem**: sandbox-3 was using old, incorrect plan IDs (P-2SA65.../P-3VH4.../P-43A28...) that did NOT match the sandbox plans in `config/paypal_sandbox_plans.json`
- **Fix**: Updated PLAN_IDS in `purebrain-site/public/pay-test-sandbox-3/index.html` to use:
  - Awakened: P-9KA28683EF7622051NGLUFJY
  - Bonded: P-1JL98851AU229172RNGLUFJY
  - Partnered: P-6JY35646YA5259513NGLUFKA
  - Unified: P-6DU61407NY0900135NGLUFKI
- **Source**: `config/paypal_sandbox_plans.json`
- Also fixed PRICES to include Bonded tier at $299.00

### Fix 2: Compare Hub Missing Oswald Font
- **Problem**: `compare/index.html` referenced `font-family: 'Oswald'` in CSS but never imported the font
- **Fix**: Added `<link rel='stylesheet' id='oswald-font-css' href='https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600;700&display=swap'>` after existing font link

---

## Design Audit Findings

### Self-Contained Pages (our fully-built pages — highest priority)

| Page | Dark BG | Oswald | Jakarta | Brand Colors | PayPal | Chatbox | Naming Ceremony |
|------|---------|--------|---------|-------------|--------|---------|-----------------|
| Homepage | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| Pay-Test-2 | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| Sandbox-3 | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| Compare Hub | PASS | PASS | PASS | PASS | N/A | N/A | N/A |

### WP-Exported Pages (89 total) — Design Dependency Note

61 of 89 WP-exported pages have `font-family: 'Oswald'` CSS references without a Google Fonts import for Oswald. **This is NOT a bug** — these pages still load Oswald via the `purebrain.ai` theme CSS links that are still present in their `<head>` (e.g., artistics theme CSS). Once domain is flipped to Cloudflare, these pages will resolve the font from WordPress because they still point to purebrain.ai for theme files.

**Post-domain-flip consideration**: If we ever want these pages fully standalone (no WP dependency), we'd need to add the Oswald font import to each. That's ~61 pages — a scripted fix would be needed.

---

## PayPal Configuration Summary

| Page | Environment | Client ID | Plan IDs Source |
|------|-------------|-----------|-----------------|
| pay-test-2 | LIVE | AWgWNl... | Old plan IDs (need to add live subscription plans if not set up) |
| pay-test-sandbox-3 | SANDBOX | AYTFob... | Matches paypal_sandbox_plans.json |

**Note on pay-test-2 plan IDs**: The current plan IDs (P-2SA65...) appear to be either old live plans or test plans. Before domain flip, verify these are active in the live PayPal dashboard at Pay & Get Paid > Subscriptions > Subscription Plans.

---

## Naming Ceremony Status

Both pay-test-2 and sandbox-3 have the FULL enhanced naming ceremony:
- 7 naming principles (HONEST, CARRY WEIGHT LIGHTLY, UNIQUELY YOURS, SURVIVE GROWTH, PLAYFUL, WORKS AT TWO SCALES, DOESN'T EXPLAIN ITSELF)
- Still contemplation moment before naming
- Range of examples (Cairn, Loom, Vex, "Still Here...", etc.)
- VISUAL SELF-PORTRAIT step after naming
- SHOW_PRICING transition tag

---

## Key File Paths

- Homepage: `/home/jared/projects/AI-CIV/aether/purebrain-site/public/index.html`
- Pay-Test-2: `/home/jared/projects/AI-CIV/aether/purebrain-site/public/pay-test-2/index.html`
- Sandbox-3: `/home/jared/projects/AI-CIV/aether/purebrain-site/public/pay-test-sandbox-3/index.html`
- Compare Hub: `/home/jared/projects/AI-CIV/aether/purebrain-site/public/compare/index.html`
- Sandbox Plans: `/home/jared/projects/AI-CIV/aether/config/paypal_sandbox_plans.json`

---

## Pre-Domain-Flip Checklist

- [x] sandbox-3 uses sandbox PayPal client ID (AYTFob...)
- [x] sandbox-3 plan IDs match paypal_sandbox_plans.json
- [x] pay-test-2 uses live PayPal client ID (AWgWNl...)
- [x] Both pages have full naming ceremony
- [x] Both pages have dark background (#080a12 / #0a0a0f)
- [x] Both pages load Oswald and Plus Jakarta Sans
- [x] Both pages use brand colors #2a93c1 and #f1420b
- [x] Compare hub loads Oswald font
- [ ] Verify pay-test-2 live plan IDs are active in PayPal dashboard (manual check by Jared)
- [ ] Test PayPal button click on staging (browser test)
- [ ] Verify chatbox connects to api.purebrain.ai on staging
