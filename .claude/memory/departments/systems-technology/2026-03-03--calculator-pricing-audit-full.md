# Calculator Pricing Audit — Full Results
**Date**: 2026-03-03
**Type**: audit + findings
**Topic**: Calculator pricing vs. site pricing — discrepancy identified

## Summary
Calculator math is correct. Calculator prices are internally consistent.
Main site page 11 is the stale page — it still shows old 4-tier structure with $79 Awakened + Bonded $149.

## Key Findings

### Calculator (page 777) — CORRECT, 3 tiers
- Awakened: $149 base + $100 Claude Max = $249 displayed
- Partnered: $499 base + $200 Claude Max = $699 displayed
- Unified: $999 base + $200 Claude Max = $1,199 displayed

### Invitation Page (page 987) — CORRECT, 3 tiers
- Awakened: $149/mo
- Partnered: $499/mo
- Unified: $999/mo

### Main Site Page 11 — STALE, 4 tiers
- Awakened: $79/mo (OLD — pre-consolidation price)
- Bonded: $149/mo (OLD — this tier was removed)
- Partnered: $499/mo
- Unified: $999/mo
- Enterprise: Custom

## Math Tests
All 11 test cases PASS. getTier() logic works correctly.
Escalation thresholds: Partnered at spend>=$200 OR tools>=10, Unified at spend>=$400 OR tools>=15

## Action Required
Page 11 must be updated to new 3-tier structure. The calculator is correct.

## Files
- Proof doc: `exports/calculator-pricing-audit-2026-03-03.md`
