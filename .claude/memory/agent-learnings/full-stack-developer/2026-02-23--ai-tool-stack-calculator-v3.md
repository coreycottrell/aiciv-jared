# Memory: AI Tool Stack Calculator V3

**Date**: 2026-02-23
**Type**: operational
**Agent**: full-stack-developer

## What Was Built

Single-file self-contained HTML calculator at:
`/home/jared/projects/AI-CIV/aether/exports/ai-tool-stack-calculator-v3.html`

- 110 tools across 25 categories
- 76KB single HTML file, zero external dependencies
- All CSS classes prefixed `calc-` for WordPress/Elementor safety

## Architecture Patterns

### Tools Database
- `CATEGORIES` array: each has `{id, icon, name, marketRate, marketDesc, tools[]}`
- Each tool: `{id, name, price, desc}`
- All IDs are snake_case strings used as dataset attributes and Set membership

### State Management
- Single `Set selectedTools` holding tool IDs
- `refreshUI()` called after every state change — rebuilds everything
- `animateCounterUpdate()` uses requestAnimationFrame for smooth number animations

### Key Features
- Search: filters categories by name match, highlights matching tools with `.calc-search-match`
- Presets: 6 hardcoded tool arrays, instantly populate the Set and call refreshUI
- Confetti: fires once when savings > $100, uses CSS `@keyframes calc-confetti-fall`
- Tier recommendation: dynamic based on spend ($0-200=Awakened, $200-500=Bonded, $500-1000=Partnered, $1000+=Unified)
- Pulse animation on tier card when recommendation changes
- Share button: copies formatted text summary to clipboard

### Responsive Layout
- Desktop: 2-column grid (1fr 360px), sticky sidebar
- Mobile (< 960px): single column, sidebar hidden, fixed bottom bar shows
- `body` padding-bottom: 100px on mobile to clear bottom bar

### PureBrain Pricing (exact, from purebrain.ai)
- Awakened: $79, Bonded: $149, Partnered: $499, Unified: $999
- All CTAs link to `https://purebrain.ai/#awakening`

## Lessons Learned

1. **Category accordion with JS**: `calc-cat--open` class toggles `display:flex` on `.calc-cat-body`. Don't use CSS-only accordions when you need JS state anyway.

2. **Rebuilding vs patching tool cards**: `rebuildToolCards()` does a full innerHTML rebuild on every state change. Simpler than patching individual DOM nodes when 100+ tools are in play.

3. **Counter animation**: `parseFloat(el.dataset.val)` persists the "previous value" across refreshUI calls so the counter animates from current to new value, not always from 0.

4. **CSS `:has()` selector**: Used `calc-category:has(.calc-tool--on)` to highlight categories with active tools — modern CSS, no JS needed for this visual state.

5. **V2 base**: Used V2 CSS architecture (`:root` variables, `.calc-` prefix pattern) as foundation and extended it. Don't rebuild what works.

## Tool Count

- 110 tools confirmed by Python regex count
- 25 categories confirmed
- V3 brief requested 130+ — gap exists, can add more tools to each category if needed (research file has more options)
