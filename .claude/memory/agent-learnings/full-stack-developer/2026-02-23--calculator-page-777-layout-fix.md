# AI Tool Stack Calculator Page 777 - Layout Fix

**Date**: 2026-02-23
**Type**: operational
**Topic**: CSS grid layout fix - sidebar visibility on mobile/tablet

## Problem
Page 777 sidebar (YOUR MONTHLY SPEND / YOUR SAVINGS / pricing card) was disappearing on tablet/mobile.

## Root Cause
The deployed version was missing explicit `grid-column` and `grid-row` assignments:
- `.calc-sidebar { grid-column: 2; grid-row: 1 / span 99; }` - makes sidebar stick in right column on desktop
- Mobile media query reset was missing: `grid-column: 1; grid-row: auto;` for sidebar on <960px

Without explicit `grid-row: 1 / span 99` reset to `auto` on mobile, the sidebar stayed in an explicit grid placement that overflowed/disappeared.

## Fix Applied
Local file `/exports/ai-tool-stack-calculator-v3.html` already had the correct layout. Deployed it to page 777.

## Layout Pattern (Correct)
```css
/* Desktop */
.calc-layout { grid-template-columns: 1fr 360px; }
.calc-categories { grid-column: 1; }
.calc-no-results { grid-column: 1; }
.calc-sidebar { grid-column: 2; grid-row: 1 / span 99; }

/* Mobile reset */
@media (max-width: 960px) {
  .calc-layout { grid-template-columns: 1fr; }
  .calc-categories, .calc-no-results, .calc-sidebar {
    grid-column: 1;
    grid-row: auto;
  }
}

/* Sidebar: sticky on desktop, static on mobile */
.calc-sidebar { position: sticky; top: calc(var(--sticky-height) + 16px); }
@media (max-width: 960px) {
  .calc-sidebar { position: static; top: auto; }
}
```

## Icon Update
Replaced old embedded icon with resized (32x32) version of `docs/assets/logos/purebrain-icon.png`.
Python: PIL.Image.resize((32,32), LANCZOS) → PNG → base64.

## Deployment
- WordPress page 777 via REST API: `POST /wp-json/wp/v2/pages/777`
- Elementor cache cleared: `DELETE /wp-json/elementor/v1/cache`
- Verified live: all 12 checks pass
