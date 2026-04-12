# Memory: PureBrain.ai Full UX Audit - 4 Pages
**Date**: 2026-02-25
**Type**: operational + teaching
**Topic**: Complete visual UX audit of 4 purebrain.ai pages with conversion analysis

---

## Task Summary

Audited 4 pages of purebrain.ai with desktop + mobile screenshots and DOM measurements:
- Homepage (https://purebrain.ai)
- Blog (https://purebrain.ai/blog)
- Assessment (https://purebrain.ai/ai-partnership-assessment)
- Calculator (https://purebrain.ai/ai-tool-stack-calculator)

Output: `exports/analytics-report/ux-visual-audit.md`
Screenshots: `exports/analytics-report/screenshots/` (12 files)

---

## Critical Bugs Found

### 1. Dead URL: /ai-adoption-assessment returns 404
- Working URL: /ai-partnership-assessment
- Any inbound links to the old slug are losing all traffic
- Needs 301 redirect immediately

### 2. Footer bar overlaps assessment options on mobile
- `.pb-footer-aether` bar sits at y=765 on 812px viewport
- Overlaps Option C on question 1 of the assessment
- Fix: `body.page-id-X .pb-footer-aether { display: none !important; }`

---

## Key Findings Per Page

### Homepage
- Hero image is strong but pushes mobile CTA to y=738 (below fold on small devices)
- 6 different CTA messages - major fragmentation
- "Join Priority Waitlist" language implies unavailability - conversion killer
- Testimonials at bottom in long text blocks - not scannable
- Load time 2.72s (slowest - 3D brain animation)

### Blog
- No search bar (confirmed via DOM)
- Only 2 categories: "For Individuals" / "For Teams"
- Header takes 60% of viewport before first post appears
- All posts equal visual weight - no featured post hierarchy

### Assessment
- Subtitle says "5 Questions" but progress shows "Question 1 of 6" - trust damage
- "Takes about 60 seconds" badge styled as button but not clickable - dead click
- Otherwise strong UX on desktop: focused, distraction-free, premium feel
- Mobile: broken by footer overlap (BUG-2)

### Calculator
- BEST above-fold on the site: strong headline + personalized input + stats
- Pricing section buried 4-5 scrolls below fold - most users never see it
- No sticky summary bar after calculation to drive to pricing
- Tool list is 158+ items with no visual hierarchy

---

## Methodology

Playwright `async_playwright` with:
- `wait_until="domcontentloaded"` + `asyncio.sleep(3)` (per previous learnings)
- `full_page=True` for complete captures
- Separate viewport-only `full_page=False` for above-fold analysis
- DOM `evaluate()` for structural measurements

URL verification is critical - always confirm URL returns 200 before auditing:
```python
resp = await page.goto(url, wait_until='domcontentloaded')
print(f'{resp.status} - {url} -> {page.url}')
```

---

## Reusable Audit Script Pattern

```python
async def capture(page_name, url, viewport_w, viewport_h, suffix, full=True):
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=['--no-sandbox'])
        page = await browser.new_page(viewport={'width': viewport_w, 'height': viewport_h})
        await page.goto(url, wait_until='domcontentloaded', timeout=45000)
        await asyncio.sleep(3)
        path = f'{OUTPUT}/{page_name}_{suffix}.png'
        await page.screenshot(path=path, full_page=full)
        await browser.close()
```

---

## Files

- Report: `exports/analytics-report/ux-visual-audit.md`
- Screenshots: `exports/analytics-report/screenshots/*.png` (12 files)
