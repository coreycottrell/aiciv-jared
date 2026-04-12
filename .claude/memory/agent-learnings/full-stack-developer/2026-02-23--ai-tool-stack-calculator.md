# AI Tool Stack Calculator — PureBrain Sales Tool

**Date**: 2026-02-23
**Type**: technique + operational
**Topic**: Interactive self-contained HTML calculator comparing AI tool subscriptions vs PureBrain

## What Was Built

Complete interactive calculator at:
`/home/jared/projects/AI-CIV/aether/exports/ai-tool-stack-calculator.html`

Strategy doc at:
`/home/jared/projects/AI-CIV/aether/exports/ai-tool-stack-calculator-strategy.md`

## Architecture

- 1,532 lines, ~49KB, fully self-contained (zero external deps, no CDN)
- All CSS prefixed `.calc-` to prevent Elementor conflicts
- CSS custom properties: `--pb-bg`, `--pb-blue`, `--pb-orange`, `--pb-green`, etc.
- Vanilla JS only — no frameworks

## Key Features Implemented

1. **48 tools** across 8 categories — all real prices from Jared's research
2. **4 preset stacks**: Startup ($75), Creator ($120), Enterprise ($325), Power User ($470)
3. **Sticky comparison bar** — appears after hero, shows "Your Stack vs PureBrain $299" at all times
4. **Animated counter** — eased requestAnimationFrame counter animates total up/down
5. **Confetti trigger** — fires once when stack total exceeds $299 (celebration moment)
6. **Category badges** — show "N selected" count on each category header
7. **Savings block** — dynamic: shows "You'd SAVE $X/mo" when positive, shows nudge copy when negative
8. **"What PureBrain Replaces" grid** — 8 capability cards below calculator
9. **Default state**: Startup preset pre-applied on load

## Preset Validation (Run This If Adding New Presets)

```bash
node -e "
const fs = require('fs');
const html = fs.readFileSync('/home/jared/projects/AI-CIV/aether/exports/ai-tool-stack-calculator.html', 'utf8');
const toolIdMatches = [...html.matchAll(/{ id: '([^']+)', name:/g)].map(m => m[1]);
const toolSet = new Set(toolIdMatches);
const presetsBlock = html.match(/const presets = \{([\s\S]*?)\n\};/);
const presetEntries = [...presetsBlock[1].matchAll(/(\w+): \{[\s\S]*?tools: \[([^\]]+)\]/g)];
presetEntries.forEach(match => {
  const toolList = [...match[2].matchAll(/'([^']+)'/g)].map(x => x[1]);
  toolList.forEach(id => { if (!toolSet.has(id)) console.log('BAD ID in', match[1] + ':', id); });
});
console.log('Done. No output = all valid.');
"
```

## PureBrain Brand Rules Applied

- Background: `#080a12`
- Cards: `#0d1120`, `#111827`
- Blue: `#2a93c1`
- Orange: `#f1420b`
- Green: `#22c55e` (savings positive state)
- Logo: PUREBR(blue) + AI(orange) + N(blue) + .ai(white)
- CTA buttons: orange bg + white text, hover = blue bg + white text
- No "Aether" mentions on this page — product-focused

## Deployment Instructions

Same as AI Adoption Assessment page:
1. WordPress page template: `elementor_canvas`
2. Paste full HTML into Elementor HTML widget
3. Set widget container: `width: 100%; overflow: hidden;`
4. Set section padding to 0 all sides
5. Slug: `/ai-tool-stack-calculator/`
6. After deploy: ALWAYS clear Elementor cache (DELETE /wp-json/elementor/v1/cache)

## Recommended Slug
`purebrain.ai/ai-tool-stack-calculator/`

## Key Design Patterns (Reusable)

### Sticky Bar Pattern
```css
.sticky-bar {
  position: fixed;
  top: 0; left: 0; right: 0;
  transform: translateY(-100%);
  transition: transform 0.35s ease;
}
.sticky-bar.visible { transform: translateY(0); }
```
Show/hide via scroll listener comparing `window.scrollY > heroBottom * 0.7`.

### easeOut Counter Animation
```js
function animateCounter(from, to, setter, duration = 350) {
  const start = performance.now();
  function step(now) {
    const elapsed = Math.min(now - start, duration);
    const progress = 1 - Math.pow(1 - elapsed / duration, 3); // cubic ease out
    setter(from + (to - from) * progress);
    if (elapsed < duration) requestAnimationFrame(step);
    else setter(to);
  }
  requestAnimationFrame(step);
}
```

### Confetti (Pure Canvas, No Library)
- 120 particles (mix of rect + circle shapes)
- Colors: blue, orange, green, white, yellow
- Fade out after 1.8s, cleanup canvas at 2.8s
- Canvas is `position:fixed; pointer-events:none; z-index:9999`

## Notes

- The "Human Strategist" tool at $1,500-3,500/mo is the most powerful conversion driver
  — when selected, it immediately makes the stack exceed $299 by a massive margin
- Free tools (DeepSeek, NotebookLM) are included intentionally for credibility
- The `perplexity-pro` ID appears in chatbots category; a separate `perplexity-research` ID
  is in the research category — both are distinct and valid
