# Calculator Mobile/Sticky Bar Number Sync Fix

**Date**: 2026-02-24
**Type**: teaching
**Topic**: Mobile sticky bar showed different total than inline savings bar — root cause and fix

## The Bug

Page 777 (purebrain.ai/ai-tool-stack-calculator/) showed two different numbers on mobile:
- TOP sticky bar: "YOUR AI STACK $234" (wrong — was `stackTotal`, tool prices only)
- Inline savings bar / bottom bar: "YOUR AI SPEND $1.9k/mo" (correct — was `sidebarTotal = stackTotal + personalSavingsMonthly`)

## Root Cause

In `refreshUI()`, variables were computed in wrong order:
1. `stackTotal` computed first
2. Sticky bar updated with `stackTotal` (missing `personalSavingsMonthly`)
3. `sidebarTotal = stackTotal + personalSavingsMonthly` computed later
4. Mobile bars updated with `sidebarTotal` — different number

## The Fix

Moved `sidebarTotal` computation to the TOP of `refreshUI()`, before any display updates. Then unified ALL display elements to use `sidebarTotal`:

```javascript
// NEW order in refreshUI():
const tier = getTier(stackTotal, selectedTools.size);
const toolSavings = stackTotal - tier.displayPrice;        // for savings breakdown table
const sidebarTotal = stackTotal + personalSavingsMonthly;  // ALL spend displays use this
const totalSavingsMonthly = toolSavings + personalSavingsMonthly;

// Sticky bar — now uses sidebarTotal
document.getElementById('stickyStack').textContent = formatMoney(sidebarTotal);

// Bottom bar — uses sidebarTotal
document.getElementById('bottomAmount').textContent = formatMoney(sidebarTotal) + '/mo';

// Mobile inline savings bar — uses sidebarTotal
updateMobileSavingsBar(sidebarTotal, tier, mobileSavings);
```

## Variables Renamed for Clarity

- `savings` → `toolSavings` (raw tool cost minus PureBrain price, used in breakdown table)
- `mobileSpend` → removed (was duplicate of `sidebarTotal`)
- `totalSavingsMonthly` — new computed value = `toolSavings + personalSavingsMonthly`

## Key Lesson

When multiple UI elements must show the same number, compute it ONCE at the top of the function and pass that single variable to all display updates. Never let the same logical value be computed separately in different sections — they will drift.

## File Changed

`/home/jared/projects/AI-CIV/aether/exports/ai-tool-stack-calculator-v3.html`

Deployed to WordPress page 777 via REST API — verified live.
