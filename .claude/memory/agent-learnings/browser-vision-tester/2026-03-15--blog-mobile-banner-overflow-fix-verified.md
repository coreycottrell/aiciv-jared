# Memory: Blog Mobile Banner Overflow Fix — Verified Pass

**Date**: 2026-03-15
**Agent**: browser-vision-tester
**Type**: technique + pattern
**Tags**: mobile, blog, banner, overflow, wp-block-latest-posts, object-fit, playwright

---

## Context

Verified that a CSS fix for `.wp-block-latest-posts__featured-image` (and img children) resolved banner image overflow on purebrain.ai/blog/ at 375px mobile viewport.

---

## Fix That Worked

CSS rules applied to the featured image container and its img:
- Container: `overflow: hidden`, negative margins to go edge-to-edge within card
- img: `width: 100%`, `object-fit: cover`

Computed styles confirmed via Playwright `page.evaluate()`:
- All 11 cards showed `overflow: hidden` on container
- All 11 cards showed `object-fit: cover` on img
- Card right edge: 347px (well inside 375px viewport)
- Image container width: 317px

---

## How to Verify Mobile Overflow Fixes

```python
# Check horizontal scroll
has_overflow = page.evaluate("""() => {
    return document.documentElement.scrollWidth > document.documentElement.clientWidth;
}""")

# Check all card right edges vs viewport
card_data = page.evaluate("""() => {
    return [...document.querySelectorAll('.wp-block-latest-posts li')].map((card, i) => ({
        index: i,
        cardRight: Math.round(card.getBoundingClientRect().right),
        imgObjectFit: card.querySelector('img') ?
            window.getComputedStyle(card.querySelector('img')).objectFit : null,
        containerOverflow: card.querySelector('[class*="featured-image"]') ?
            window.getComputedStyle(card.querySelector('[class*="featured-image"]')).overflow : null
    }));
}""")
```

---

## Key Selector for WP Blog Cards

`.wp-block-latest-posts li` — correct selector (NOT `.wp-block-latest-posts__list-item`)
`[class*="featured-image"]` — works for image container inside each li

---

## When to Apply

Any time WordPress Latest Posts block is used and mobile banner overflow is suspected. Always verify with `scrollWidth === clientWidth` check plus per-card right-edge measurement.
