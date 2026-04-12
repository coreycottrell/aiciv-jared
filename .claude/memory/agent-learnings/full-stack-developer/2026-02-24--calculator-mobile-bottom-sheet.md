# Calculator Mobile Bottom Sheet - Page 777
**Date**: 2026-02-24
**Type**: teaching
**Topic**: Mobile sidebar replacement - tappable bottom bar with full bottom sheet drawer

## Problem
On mobile, the calculator sidebar (YOUR MONTHLY SPEND / SAVINGS / RECOMMENDED PLAN) was completely hidden (`display: none`). A thin fixed bottom bar replaced it showing only `$0/mo` and a CTA. Two issues:
1. The bottom bar only read `stackTotal` (tool selections), NOT `personalSavingsMonthly` (from the AI task questionnaire)
2. There was no way to see the full savings breakdown on mobile — the core conversion element was invisible

## Solution Built

### 1. Enhanced Bottom Bar
- Added savings badge: "Save $X/mo" (green pill, shown when savings > 0)
- Changed CTA button from link → button labeled "View Savings ↑"
- Added expand hint row: "Tap to see full breakdown & recommended plan"
- Changed container from `display: flex` to `display: block` with inner flex div
- Fixed calculation: now shows `stackTotal + personalSavingsMonthly`

### 2. Full Bottom Sheet Modal
Built a complete bottom sheet (drawer) with:
- Overlay backdrop (tap outside to close)
- Swipe handle at top (tap to close)
- Close button (×)
- Zero state when no tools selected
- Content panel (shown when tools selected or personalized savings set):
  - Spend vs PureBrain price side-by-side
  - Savings bar with % fill
  - Savings breakdown rows (current spend / PureBrain / monthly savings / annual savings)
  - Recommended plan card (mirrors desktop sidebar, with tier color theming)
  - Claude Max note
  - Share button (triggers desktop share modal after closing sheet)

### 3. Data Sync Pattern
`updateBottomSheet(sidebarTotal, tier, toolSavings)` is called inside `refreshUI()` right where the old bottom bar update was. It receives the same calculated data as the desktop sidebar.

The sheet mirrors `updateTierRec()` logic:
- `tier.features` is an array → joined with ` · `
- `tier.color` used for badge/price/CTA/border colors with hex alpha suffixes (`color + '66'`, `color + '0d'`, `color + '22'`)

## CSS Architecture
- `.calc-sheet-overlay` - full-screen backdrop (z-index: 1100)
- `.calc-sheet` - bottom drawer (z-index: 1101), `transform: translateY(100%)` default, `translateY(0)` when `.open`
- Animation: 0.35s cubic-bezier(0.32, 0.72, 0, 1) - the "spring" easing used in native mobile sheets
- `overscroll-behavior: contain` on sheet to prevent page scroll bleed-through
- `body.overflow = hidden` while sheet is open

## Open/Close Triggers
- Tap anywhere on bottom bar → open
- Tap overlay → close
- Tap handle / × button → close
- Escape key → close
- Swipe down 60px when sheet is at top of scroll → close
- Tap share button → close sheet, then open desktop share modal after 300ms

## Files Changed
- Source: `exports/ai-tool-stack-calculator-v3.html`
- Deployed: WP page 777 via REST API `PUT /wp-json/wp/v2/pages/777`
- Elementor cache cleared: `DELETE /wp-json/elementor/v1/cache`

## Verification
- Live page contains: `calcBottomBar`, `bottomSavingsBadge`, `calcSheetOverlay`, `sheetTierName`, `sheetShareBtn`, `View Savings` ✓
- HTTP 200 deploy response ✓
- Elementor cache 200 clear ✓
