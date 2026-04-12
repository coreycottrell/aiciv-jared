# AI Tool Stack Calculator - Orange Border Fix + Dynamic Badge

**Date**: 2026-02-23
**Type**: teaching + gotcha
**Topic**: Root cause of orange borders on page 777 and fix pattern

## Root Cause (Important!)

The previous "fix" for the WordPress plugin `[class*="magic"]` CSS added:
```css
body.page-id-777 * {
    border-color: inherit;
}
```

This was WRONG. When the plugin sets `color: #f1420b !important` on `body`, all elements with `border-color: inherit` inherit that orange color as their border color. The rule intended to prevent the cascade actually made it WORSE for borders.

## The Correct Fix Pattern

Remove the global `border-color: inherit` override. Replace with SURGICAL overrides for specific elements:

```css
/* Surgical border-color overrides to prevent orange bleeding from plugin CSS */
body.page-id-777 .calc-search { border-color: rgba(42, 147, 193, 0.15) !important; }
body.page-id-777 .calc-preset-btn { border-color: rgba(42, 147, 193, 0.15) !important; }
body.page-id-777 .calc-category { border-color: rgba(42, 147, 193, 0.15) !important; }
/* ... etc for each component */
```

The key insight: when a WordPress plugin poisons `color` on `body`, the only safe way to fix borders is explicit `border-color` values with `!important` on each component class, NOT a global `border-color: inherit` which propagates the orange.

## Dynamic Badge Fix

The header eyebrow badge (`<div class="calc-eyebrow">`) had hardcoded "140+ Tools". Added `id="calcEyebrow"` to the HTML and added one line to the existing JS init block:

```javascript
// This already existed:
const totalTools = CATEGORIES.reduce((sum, cat) => sum + cat.tools.length, 0);
if (heroToolCount) heroToolCount.textContent = totalTools + '+';

// Added:
const calcEyebrow = document.getElementById('calcEyebrow');
if (calcEyebrow) calcEyebrow.textContent = 'Free AI Tool Stack Calculator - ' + totalTools + '+ Tools';
```

## Elements Affected by Orange Border Bug
- `.calc-search` (search bar)
- `.calc-preset-btn` (persona pills: Solopreneur Starter, Marketing Team, etc.)
- `.calc-category` (left side category cards)
- `.calc-personal-box` (Personalize Your Savings section)
- `.calc-personal-input` (textarea inside chatbox)
- Sticky bar left/right panels
- Tier cards and panels
- Comparison table borders

## File Affected
Page ID: 777 on purebrain.ai (`/ai-tool-stack-calculator/`)
Content stored in WordPress REST API only (no local copy maintained for this deployed version)

## Pattern for Future Reference

When WordPress plugin CSS poisons `color` on body, for border fixes:
1. NEVER use `border-color: inherit` globally — it inherits the poisoned color
2. DO use explicit `border-color: [value] !important` per component
3. The dark theme border value for PureBrain: `rgba(42, 147, 193, 0.15)` (blue-tinted subtle)
4. Hover state: `rgba(42, 147, 193, 0.35)` or `#2a93c1`
