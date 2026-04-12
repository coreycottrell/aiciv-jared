# Investor Intelligence Page Reveal Animation Audit

**Date**: 2026-03-02
**Agent**: browser-vision-tester
**Type**: technique + gotcha
**Topic**: IntersectionObserver reveal animations appear broken in full-page screenshots

---

## Context

Auditing `/home/jared/projects/AI-CIV/aether/exports/purebrain-investor-intelligence.html`
Jared reported: "can only see content at the top and bottom — middle sections may be broken."

## Root Cause Found

**The page uses an IntersectionObserver-based `.reveal` animation system.**

CSS mechanism:
1. JS adds `.reveal-ready` class to `<html>` on load
2. `.reveal-ready .reveal` sets `opacity: 0; transform: translateY(30px)` — hiding all elements
3. As user scrolls, IntersectionObserver fires and adds `.visible` class to elements entering viewport
4. `.reveal.visible` sets `opacity: 1; transform: translateY(0)` — showing them
5. Fallback: `@keyframes forceReveal` runs after 3s delay to force-show any unobserved elements

## Why Jared Saw It Broken

**The 3-second forceReveal fallback was not firing fast enough.** When you open the page and scroll quickly, sections that haven't been in viewport don't get `.visible`. The fallback animation uses `animation: forceReveal 0s ease 3s forwards` — which only triggers 3 seconds after the element first renders, NOT 3 seconds after page load. Sections deep in the page (not yet scrolled to) never get the forceReveal because the animation timer starts when the element is in DOM, but it uses CSS `animation-fill-mode: forwards` — this should work but depends on whether `.reveal-ready` was added before or after elements entered the DOM.

**Real root cause**: The section screenshots at negative Y positions in the first audit run showed that Playwright's `scrollTo` was firing BEFORE IntersectionObserver had a chance to observe. The IO only fires when elements intersect with viewport, and in headless Playwright the timing is tight.

## What Actually Works vs What Appears Broken

| Section | Works on scroll? | Issue |
|---------|-----------------|-------|
| Hero | YES - visible immediately (no reveal class on hero content) | None |
| Market Opportunity | YES after scroll | Bar chart hidden until IO fires |
| Compounding | YES after scroll | Canvas + sliders hidden |
| 89% Gap | YES after scroll | Split stats hidden |
| Capital Signal | YES after scroll | VC cards hidden |
| Industry Leaders | YES after scroll | Carousel hidden |
| $87B Fragmentation | YES after scroll | 195 dots grid hidden |
| PureBrain Position | YES after scroll | Stat grid + cards hidden |
| Architecture | YES after scroll | Pillar cards hidden |
| CTA | YES after scroll | Input form hidden |

## Playwright Testing Pattern for IntersectionObserver Pages

**Problem**: Playwright's `full_page=True` screenshot captures all content without scrolling, so IO never fires.

**Solution**: Scroll through the page first, THEN screenshot each section:
```python
# Scroll slowly to trigger IntersectionObserver
for y in range(0, page_height, 300):
    page.evaluate(f"window.scrollTo({{top: {y}, behavior: 'instant'}})")
    time.sleep(0.5)

# Then scroll to each section to screenshot
page.evaluate(f"window.scrollTo({{top: section_offset}})")
time.sleep(0.6)
page.screenshot(path=f"section-{name}.png")
```

## Fix Recommendation for the HTML

Remove the `.reveal-ready` class addition entirely, OR reduce the forceReveal delay from 3s to 0s:

**Option A (safest)**: Change `3s` to `0.1s` in the forceReveal animation:
```css
.reveal-ready .reveal {
  animation: forceReveal 0s ease 0.1s forwards;  /* was 3s */
}
```

**Option B (remove animations)**: Remove `.reveal-ready` class addition from JS so all content starts visible. The page content itself is compelling enough without fade-in animations.

**Option C (progressive enhancement)**: Only add `.reveal-ready` if `prefers-reduced-motion` is not set and device is not mobile.

## Screenshots Location

All screenshots in `/tmp/investor_audit/`
- `FINAL-{section}.png` = how sections look when scrolled to properly
- `scroll-{N}-y{Y}.png` = what user sees at each scroll position
- `00-full-page.png` = confirms massive blank void issue in headless capture

## Tags
reveal-animation, intersection-observer, playwright, headless, scroll-animation, investor-page
