# Portal Task 7: CTX Info Card — Context Compaction Tooltip

**Date**: 2026-03-05
**Type**: operational
**Topic**: CTX gauge info card for portal.purebrain.ai/pb — educational hover panel

## What Was Built

Patch script: `/home/jared/purebrain_portal/apply_task7_ctx_tooltip.py`

Adds an educational info card to the CTX gauge in the portal header. Users can hover
over the gauge area to see a rich 280px card explaining context windows and compaction.

## Architecture Decisions

### Separate from Task 6 Tooltip System
- Task 6 system is a shared single-line tooltip — text-only, 1.5s delay, 200px max
- Task 7 card is its own system: richer content, 0.5s delay, positioned relative to gauge
- Using a separate system avoids complexity in the Task 6 engine and keeps concerns isolated

### Hover Bridge Pattern
- Both `#ctx-gauge` and `#ctx-info-card` have mouseenter/mouseleave listeners
- mouseleave on gauge checks `e.relatedTarget` — if cursor moved to card, card stays open
- mouseleave on card checks `e.relatedTarget` — if cursor moved back to gauge, card stays open
- This prevents the card from flickering when cursor crosses the gap between gauge and card
- Pattern: check `card.contains(to) || to === card` on gauge leave; vice versa on card leave

### Position: Relative on Gauge
- `#ctx-gauge` gets `position: relative` so the absolutely-positioned card anchors to it
- Card uses `bottom: calc(100% + 10px); left: 50%; transform: translateX(-50%)` for centred-above
- Flip class `ctx-card-below` switches to `top: calc(100% + 10px)` for below-gauge position
- JS measures `gaugeRect.top` vs estimated card height (220px fallback) to decide which way

### "i" Icon Design
- `<i id="ctx-info-icon">` — 13x13 circle, blue border rgba(42,147,193,0.55)
- Letter "i" at 9px bold — clearly a help/info indicator
- Hover state brightens border and adds subtle blue bg fill
- `title=""` attribute set so native browser tooltip doesn't fire
- `aria-label="Context window info"` for accessibility

### Zone Bar
- Proportional flex segments: green=50, yellow=30, orange=15, red=5
  (reflects actual context usage zones: 0-50%, 50-80%, 80-95%, 95%+)
- Portal JS uses different thresholds: warn at 60%, crit at 85%
  — card zones approximate the UX zones at slightly rounder numbers for user clarity

### CSS Anchor (Patch 1)
- Injects before `  /* ===== END HOVER TOOLTIPS ===== */\n</style>`
- This was added by Task 6. Confirmed present at line 2622.
- Fallback anchor also coded: `</style>\n\n<!-- THREE.JS` (pre-Task6 pattern)

### HTML Anchor (Patch 2)
- Exact 7-line block starting with `    <div class="ctx-gauge" id="ctx-gauge" title="Context health">`
- 4-space indentation throughout
- Removes the `title="Context health"` plain tooltip (replaced by rich card)
- New block adds icon after CTX label, and embeds the card div inside the gauge wrapper

### JS Anchor (Patch 3)
- Standard `\n</body>\n</html>` anchor — consistent with all previous portal tasks

## File Sizes
- Portal input: ~346KB (grew from ~340KB after Tasks 1-6)
- Task 7 adds ~3.5KB (CSS ~1.8KB, HTML ~0.7KB, JS ~1KB)

## Patch Count
- 3 patches total: CSS, HTML, JS
- All are hard-fail (sys.exit(1)) — no optional/warning patches needed
