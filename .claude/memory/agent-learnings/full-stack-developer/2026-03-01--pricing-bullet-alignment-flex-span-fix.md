# Pricing Bullet Alignment Fix — Flex Span Pattern

**Date**: 2026-03-01
**Type**: gotcha + fix pattern
**Pages**: purebrain.ai page 11, page 689 (pay-test-2), page 688 (pay-test-sandbox-2)

---

## The Bug

Two bullet items in the Awakened pricing tier showed misaligned text — "Nova" (or "Your AI") appeared visually separated from the rest of the text:
- "Nova has a permanent home that's always on"
- "Nova inherits wisdom from a family of AI minds"

All other items (e.g., "Unlimited agent creation", "50+ agent simultaneous deployment") aligned correctly.

---

## Root Cause

The `.pricing-card__feature` `<li>` uses `display: flex`.

- Working items: `SVG | text_node("Unlimited agent creation")` — two flex children
- Broken items: `SVG | span.ai-name-dynamic("Your AI") | text_node(" has a permanent home...")` — three flex children

In a flex container, `<span>` elements and text nodes both become flex items. The `<span class="ai-name-dynamic">` was a separate flex child from the text node following it, causing "Nova" to appear as its own column/row.

---

## The Fix (Two Parts)

### Part 1: Wrap text content in outer span
Wrapped the full text portion (span + following text) in an outer `<span style="display:inline">`:

```html
<!-- BEFORE (broken) -->
<span class="ai-name-dynamic">Your AI</span> has a permanent home that's always on

<!-- AFTER (fixed) -->
<span style="display:inline"><span class="ai-name-dynamic">Your AI</span> has a permanent home that's always on</span>
```

### Part 2: Add CSS rule for flex behavior
Added to the page's `<style>` block:
```css
.pricing-card__feature > span { display: block; flex: 1; }
```

This makes any direct `<span>` child of a feature `<li>` take up the full remaining flex space (after the SVG).

The `style="display:inline"` attribute is overridden by the CSS to `display:block` + `flex:1 1 0%`, which is correct — it makes the span a proper flex item that fills the row.

---

## Verification

After fix: all three items measure `liH=39px` — identical to reference items like "Unlimited agent creation".

Before fix: broken items were 62px (two visual rows).

Computed styles confirmed: `SPAN[display=block, flex=1 1 0%]`

---

## Key Learnings

1. **Flex containers make ALL direct children flex items** — including text nodes and inline spans. When you have `span + text_node` inside a flex `<li>`, they are TWO separate flex items.

2. **Wrapping technique**: Wrap the full text content (span + text) in an outer span, then use CSS `flex: 1` on it to make it take remaining space.

3. **ai-name-dynamic pattern**: The `<span class="ai-name-dynamic">` is used for dynamic name substitution. These spans must always be wrapped in a containing element when inside a flex container, so the full text reads as one flex child.

4. **Elementor data verification**: Always verify actual item heights with forced-visible Playwright check. Items may be hidden by page interaction state (zero height when not visible). Force them visible with `el.style.setProperty('display', 'block', 'important')`.

---

## Files Changed (Elementor _elementor_data on 3 pages)

- `https://purebrain.ai/` (page ID 11)
- `https://purebrain.ai/?page_id=689` (pay-test-2)
- `https://purebrain.ai/?page_id=688` (pay-test-sandbox-2)
- Elementor cache cleared after all updates
