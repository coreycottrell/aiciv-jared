# Memory: Tim Cook Sales Page QA - Feb 27 2026
**Date**: 2026-02-27
**Type**: technique + pattern
**Topic**: Self-contained sales page QA on Elementor Canvas - passing audit

---

## Page Details
- URL: https://purebrain.ai/your-ai-tim-cook/
- WordPress page ID: 993
- Template: Elementor Canvas (correct for non-blog pages)

## Orange Background Check Result
PASS. Body background = #0d1117 (dark navy). This page correctly uses literal hex + !important on body, unlike the invitation page which had the var(--bg) cascade bug. The fix documented in 2026-02-27--invitation-page-orange-bg-bug.md is the right pattern for all future pages.

## Scroll Reveal Pattern (.tc-reveal)
The page uses a custom `.tc-reveal` + `.tc-visible` IntersectionObserver pattern:
- Initial state: `opacity: 0, transform: translateY(30px)`
- After intersection: `.tc-visible` class added → `opacity: 1, transform: translateY(0)`
- Stagger delays via `.tc-reveal-delay-1` through `.tc-reveal-delay-4`

In headless Playwright, elements start at opacity:0. After a force-scroll loop:
```python
for y in range(0, total_height, 200):
    await page.evaluate(f"window.scrollTo(0, {y})")
    await page.wait_for_timeout(50)
```
All elements transition to visible. This is the correct technique for testing scroll-reveal pages.

## Mobile "Black Sections" False Alarm
On a 10,502px tall full-page mobile screenshot, sections between y=2000-5000 appeared solid black. Root cause: these are the dark navy (#0a0e1a to #0d1117) padding/gap areas between sections. Not blank content. Content IS there - just very dark. Confirmed by scrolling through at 700px intervals.

## Hero Orb Overflow (Design Pattern)
The `.tc-hero-orb` decorative blur elements intentionally extend beyond viewport width (700px+ on 375px screen). They are clipped by `overflow:hidden` on the `.tc-hero` section. Playwright reports them as "overflowing" but this does NOT cause horizontal scroll (body overflow-x: hidden). This is a correct decorative blur pattern.

Detection script to confirm no real overflow:
```javascript
document.body.scrollWidth > viewportWidth  // returns false if contained
```

## Wordmark Color Verification Pattern
```javascript
document.querySelectorAll('span, div').forEach(el => {
    const text = el.innerText ? el.innerText.trim() : '';
    if (text === 'PUREBR' || text === 'AI' || text === 'N') {
        const color = window.getComputedStyle(el).color;
        results.push({text, color});
    }
});
```
Expected: PUREBR = rgb(42, 147, 193), AI = rgb(241, 66, 11), N = rgb(42, 147, 193)

## Clock Section (24/7)
The `.tc-clock-display` renders a live time ("2:10") with `.tc-clock-am` label and `.tc-clock-dot` pulsing status indicator. Cannot verify tick animation in headless Playwright - only static capture. Verify manually in browser if animation is critical.

## CTA Link Target
Both CTA buttons link to `https://purebrain.ai/#awakening` - correct.

## Files
- Report: `exports/tim-cook-page-qa-report.md`
- Screenshots: `exports/screenshots/tim-cook-qa-2026-02-27/` (15+ files)
- Test scripts: `tools/test_tim_cook_page.py`, `tools/test_tim_cook_mobile_deep.py`
