# Calculator Pricing Tiers: Bonded Removed, 3 Tiers Only
**Date**: 2026-03-03
**Type**: fix + deployment
**Agent**: dept-systems-technology
**Page**: https://purebrain.ai/ai-tool-stack-calculator/ (WP page ID 777)

## Summary
Removed Bonded tier from AI Tool Stack Calculator. PureBrain now has 3 tiers only.

## Changes Made (8 changes, 9/9 checks passed)

### 1. TIERS array: Bonded removed
Before: 4 tiers [awakened, bonded, partnered, unified]
After: 3 tiers [awakened, partnered, unified]

### 2. Partnered features updated
Before: "Everything in Bonded"
After: "Everything in Awakened"

### 3. Grid updated
Before: grid-template-columns: repeat(4, 1fr)
After: grid-template-columns: repeat(3, 1fr)
(2 occurrences updated - one in .calc-tiers-grid, one in mobile breakpoint area)

### 4. Static $179 references updated to $249
Updated 7 locations:
- stickyPB (sticky bar)
- heroStartsAt (hero stat)
- recTierPrice (sidebar recommended)
- savRow2 (sidebar savings row)
- sheetTierPrice (mobile bottom sheet)
- sheetPBPrice (mobile sheet PB price)
- sheetSavRow2 (mobile sheet savings row)
Note: $179 was stale value from when Awakened was wrongly priced at $79 (79+100=179).
Correct: $249 (149 base + 100 Claude Max = 249 display price).

### 5. Claude note updated (3 occurrences)
Before: "$100/mo for Awakened & Bonded, $200/mo for Partnered & Unified"
After: "$100/mo for Awakened, $200/mo for Partnered & Unified"

### 6. Most Popular badge moved from Bonded to Partnered
Bonded was the only tier with badge: 'Most Popular'. After removal,
Partnered gets the Most Popular badge.

### 7. Missing comma fixed
After removing Bonded (which started with `,\n  {`), the Awakened tier
was missing its trailing comma. Fixed to ensure valid JS array syntax.

## Actual Prices (from page 688 live pricing)
- Awakened: $149/mo base + $100 Claude Max = $249 display
- Partnered: $499/mo base + $200 Claude Max = $699 display
- Unified: $999/mo base + $200 Claude Max = $1199 display

## Technical Notes
- Source file: `exports/ai-tool-stack-calculator-v3.html`
- WordPress page ID: 777
- Deployed wrapped in `<!-- wp:html -->` block
- Elementor cache cleared after deployment
- Local source file updated to match deployment
- Verification: fetched back from WP API, 8/8 checks passed

## Gotchas
- The local source file (exports/ai-tool-stack-calculator-v3.html) was STALE
  before this fix - it had old price=79 for Awakened. Always use WP REST API
  as source of truth for this calculator.
- The calculator uses displayPrice getter: price + claudeMaxCost
  Awakened: 149+100=249, Partnered: 499+200=699, Unified: 999+200=1199
