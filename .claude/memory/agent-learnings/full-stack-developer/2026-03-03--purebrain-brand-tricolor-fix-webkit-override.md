# Memory: PureBrain Brand Tri-Color Fix — -webkit-text-fill-color Override

**Date**: 2026-03-03
**Type**: pattern + gotcha
**Topic**: Fixing PureBrain tri-color brand coloring when CSS gradient gradient overrides inline color

---

## Root Cause

`.pb-demo-section__heading span` in the demo section CSS applies:

```css
.pb-demo-section__heading span {
    background: linear-gradient(135deg, #f1420b 0%, #ff6b35 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
```

This causes any `<span>` inside the heading to render with the orange gradient regardless of what `color:` attribute you set. Standard `style="color:#2a93c1"` does NOT override `-webkit-text-fill-color: transparent`.

## Fix Pattern

To override a parent CSS `-webkit-text-fill-color` gradient, each inline span must explicitly set:

```html
<span style="color:#2a93c1;-webkit-text-fill-color:#2a93c1;background:none;background-clip:unset;-webkit-background-clip:unset">PureBr</span>
<span style="color:#f1420b;-webkit-text-fill-color:#f1420b;background:none;background-clip:unset;-webkit-background-clip:unset">ai</span>
<span style="color:#2a93c1;-webkit-text-fill-color:#2a93c1;background:none;background-clip:unset;-webkit-background-clip:unset">n</span>
```

Three properties required per span:
1. `color: #hex` — standard color
2. `-webkit-text-fill-color: #hex` — overrides webkit gradient fill
3. `background: none` + `background-clip: unset` + `-webkit-background-clip: unset` — removes gradient background that would be clipped to text

## Pages Fixed

- Page 11 (Homepage): 5 changes, delta +2012 chars
- Page 688 (pay-test-sandbox-2): 5 changes, delta +2012 chars
- Page 689 (pay-test-2): 5 changes, delta +2012 chars

## Changes Applied Per Page

1. `<span>PureBrain</span>` in "Watch PureBrain Come Alive" heading
2. `>Compare PureBrain</p>` in compare section
3. `>See Why PureBrain Is Different &#x2192;</a>`
4. `Understand what sets PureBrain apart from other AI tools</p>`
5. `PureBrain saves you every month.</p>` in calculator CTA

## Verification

All 15 checks passed (5 per page × 3 pages):
- Old plain spans removed
- New -webkit-text-fill-color values present
- Tri-color PureBr split structure present

## What Was NOT Changed

- URLs containing purebrain.ai
- meta tags (content=, og:, twitter: attributes)
- JSON-LD schema blocks
- JavaScript variables (const, let, var)
- alt= and title= attributes
- CSS comment blocks

## Script Location

`/tmp/fix_purebrain_colors.py` (not committed — one-shot fix script)

## Brand Standard Reference

- PUREBR = #2a93c1 (Pure Tech Blue)
- AI = #f1420b (Pure Tech Orange) — the "AI" within "BRAIN" highlighted
- N = #2a93c1 (Pure Tech Blue)
- Split: PureBr | ai | n (mixed case) or PUREBR | AI | N (all caps)
