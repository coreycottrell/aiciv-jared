# Single-Tier Pricing Page Clone Pattern

**Date**: 2026-03-11
**Task**: Create 3 single-tier clone pages from pay-test-2/index.html

## Pattern

When a pricing page has multiple tier cards delimited by HTML comments (`<!-- AWAKENED`, `<!-- PARTNERED`, etc.), use Python to:
1. `cp` the source file to all destinations first (fast)
2. Use Python line-range detection (depth counting) to find exact card boundaries
3. Remove unwanted cards, keep only target tier
4. Add `pricing-card--featured` class to the kept card
5. Inject CSS override `<style>.pricing-grid { display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap; }</style>` right after the `<div class="pricing-grid">` opening tag

## Key File Details

- Source: `exports/cf-pages-deploy/pay-test-2/index.html`
- Pricing grid: line ~8599
- AWAKENED card: lines 8600-8647
- PARTNERED card: lines 8649-8701
- UNIFIED card: lines 8703-8755
- ENTERPRISE card: lines 8757-8801

## PayPal Plan IDs (keep all 3 in PLAN_IDS object)

The JS uses `PLAN_IDS[tier]` where tier comes from `openModal('TierName')`. Keeping all 3 IDs in the object on single-tier pages is safe and correct - only the relevant tier's button exists to trigger the modal.

- Awakened:  P-2SA65600MT088594TNGLTFKY
- Partnered: P-3VH43554A66001716NGLTFKY
- Unified:   P-43A28944XN5237411NGLTFLA

## Verification

Source had 4 pricing-card divs. Each clone should have exactly 1. Check with:
```python
content.count('class="pricing-card ')
```
