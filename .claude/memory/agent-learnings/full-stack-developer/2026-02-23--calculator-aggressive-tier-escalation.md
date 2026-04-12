# Calculator: Aggressive Tier Escalation (Tool Count + Spend Dual Trigger)

**Date**: 2026-02-23
**Type**: operational
**Topic**: Changed tier recommendation logic to escalate faster using both spend AND tool count

## What Was Changed

### Before (spend-only thresholds, wide ranges)
- Awakened: $0-$279/mo spend
- Bonded: $280-$749/mo spend
- Partnered: $750-$1,250/mo spend
- Unified: $1,250+/mo spend

### After (dual trigger: spend OR tool count, whichever hits first)
| Tier | minSpend trigger | minTools trigger |
|------|-----------------|-----------------|
| Awakened | $0 (default) | 0 (default) |
| Bonded | $100/mo | 5 tools |
| Partnered | $200/mo | 10 tools |
| Unified | $400/mo | 15 tools |

## Code Changes

### 1. TIERS array - replaced `maxSpend` with `minTools`
```js
// Old
{ id: 'bonded', minSpend: 280, maxSpend: 749 }

// New
{ id: 'bonded', minSpend: 100, minTools: 5 }
```
`maxSpend` was never actually used by getTier() - only `minSpend` was checked.
Removed `maxSpend` entirely and added `minTools` as the parallel trigger.

### 2. getTier() function - now accepts toolCount param
```js
// Old
function getTier(spend) {
  for (let i = TIERS.length - 1; i >= 0; i--) {
    if (spend >= TIERS[i].minSpend) return TIERS[i];
  }
  return TIERS[0];
}

// New
function getTier(spend, toolCount) {
  for (let i = TIERS.length - 1; i >= 0; i--) {
    if (spend >= TIERS[i].minSpend || (toolCount != null && toolCount >= TIERS[i].minTools && TIERS[i].minTools > 0)) {
      return TIERS[i];
    }
  }
  return TIERS[0];
}
```
`minTools > 0` guard ensures Awakened (minTools=0) never triggers by tool count alone.

### 3. All 3 getTier() call sites updated
- Line ~2597: `refreshUI()` main call
- Line ~2880: `buildTiersGrid()` call
- Line ~3163: `buildShareText()` call

All now pass `selectedTools.size` as second argument. `selectedTools` is a global Set.

## Escalation Behavior (Verified)

| Scenario | Result |
|----------|--------|
| 0 tools, $0 | Awakened |
| 4 tools, $80/mo | Awakened |
| 5 tools, $0/mo | Bonded (tool trigger) |
| 4 tools, $100/mo | Bonded (spend trigger) |
| 10 tools, $50/mo | Partnered (tool trigger) |
| 6 tools, $200/mo | Partnered (spend trigger) |
| 15 tools, $100/mo | Unified (tool trigger) |
| 8 tools, $400/mo | Unified (spend trigger) |

## Deployment
- File: `/home/jared/projects/AI-CIV/aether/exports/ai-tool-stack-calculator-v3.html`
- Page: https://purebrain.ai/ai-tool-stack-calculator/ (page ID: 777)
- Method: Extract style+body from local HTML, wrap in `<!-- wp:html -->`, PUT to REST API
- Elementor cache cleared after deploy
- Live verification: all 8 checks passed
