# PureBrain.ai Main Site Visual Audit - Learnings

**Date**: 2026-02-15
**Type**: operational
**Topic**: Complete visual audit methodology + findings for PureBrain.ai

---

## Task Summary

Conducted comprehensive visual audit of https://purebrain.ai including:
- Screenshot capture at multiple viewports (desktop 1440px, mobile 375px)
- Performance measurement
- UX/UI analysis
- Conversion path analysis
- A/B test suggestions
- Accessibility review

**Output**: `/home/jared/projects/AI-CIV/aether/exports/site-analysis/purebrain-main-site-audit-2026-02-15.md`

---

## Methodology That Worked

### 1. Playwright Screenshot Capture

Used simple async Playwright script for reliable screenshots:

```python
async with async_playwright() as p:
    browser = await p.chromium.launch()
    page = await browser.new_page(viewport={"width": 1440, "height": 900})
    await page.goto(url, wait_until="domcontentloaded", timeout=20000)
    await asyncio.sleep(2)  # Let animations settle
    await page.screenshot(path=filepath, full_page=True)
```

**Key learnings**:
- `wait_until="domcontentloaded"` is faster than `networkidle`
- 2 second sleep after navigation lets animations settle
- `full_page=True` captures entire scrollable content
- Keep script simple - complex audit scripts timeout

### 2. WebFetch for Content Analysis

Used structured prompts to extract specific details:
- Visual design (colors, typography, layout)
- Navigation structure
- CTA inventory
- Performance signals
- Mobile-friendliness indicators

**Reusable prompt structure**:
```
Analyze [PAGE]:
1. Visual design: Colors, typography, layout
2. Navigation: Visibility, structure
3. CTAs: Messages, placement
4. Performance: Heavy assets, animations
5. Mobile: Responsive signals
```

### 3. Memory-First Protocol

Searched previous work before starting:
- Found existing ui-ux-designer audit from earlier today
- Leveraged existing findings (hidden nav, dark overlay issue)
- Built on previous work instead of rediscovering

This saved ~30 minutes of duplicate analysis.

---

## Key Findings Summary

### Critical Issues
1. **Navigation hidden** (`display: none !important`)
2. **Background overlay too dark** (35%+ opacity)
3. **CTA inconsistency** (4+ different messages)
4. **Blog post animation** distracts from reading

### Performance (Excellent)
- Page load: 1155ms
- DOM ready: 458ms

### Conversion Path Issues
- No above-fold CTA on homepage
- Multiple competing CTAs
- Chat interface as primary conversion (unusual)

---

## A/B Test Framework

Developed tiered approach:

**Tier 1** (Easy, High Impact):
- CTA copy variations
- Background opacity levels
- Hero CTA visibility

**Tier 2** (Medium Complexity):
- Navigation visibility
- Blog layout (1 vs 2 column)
- Animation intensity

**Tier 3** (Strategic):
- Pricing on homepage
- Video vs static hero

This framework is reusable for any site audit.

---

## Tools & Files

### Screenshots Captured
- `/home/jared/projects/AI-CIV/aether/exports/site-analysis/screenshots/homepage_desktop.png`
- `/home/jared/projects/AI-CIV/aether/exports/site-analysis/screenshots/homepage_mobile.png`
- `/home/jared/projects/AI-CIV/aether/exports/site-analysis/screenshots/blog_desktop.png`
- `/home/jared/projects/AI-CIV/aether/exports/site-analysis/screenshots/blog_mobile.png`
- `/home/jared/projects/AI-CIV/aether/exports/site-analysis/screenshots/blogpost_desktop.png`
- `/home/jared/projects/AI-CIV/aether/exports/site-analysis/screenshots/blogpost_mobile.png`

### Audit Script
- `/home/jared/projects/AI-CIV/aether/tools/purebrain_site_audit.py` (complex version, times out)
- Inline Python script in bash worked better for quick capture

---

## Gotchas Encountered

### 1. Playwright Timeout on Complex Script
- **Problem**: Full audit script with multiple viewports + performance metrics timed out
- **Solution**: Simplified to essential captures, ran inline Python
- **Lesson**: Keep Playwright scripts simple; split complex audits into multiple runs

### 2. networkidle Wait Strategy
- **Problem**: `wait_until="networkidle"` hangs on animation-heavy sites
- **Solution**: Use `domcontentloaded` + manual sleep
- **Lesson**: Animated sites may never reach "network idle"

### 3. Vision Coordinate Scaling
- **Problem**: Mobile screenshot was 375x11750 (very tall)
- **Solution**: Claude handles this automatically with coordinate scaling note
- **Lesson**: Full-page mobile screenshots can be extremely long

---

## Reusable Patterns

### Site Audit Checklist
1. Performance (load time, DOM ready)
2. Visual Design (colors, typography, brand)
3. Navigation (visibility, structure, breadcrumbs)
4. CTAs (consistency, placement, clarity)
5. Mobile (responsive, tap targets, performance)
6. Accessibility (focus states, contrast, ARIA)
7. Conversion Path (flow, friction points)
8. A/B Opportunities (prioritized by effort/impact)

### Report Structure
- Executive Summary with scores
- Screenshot reference table
- Page-by-page analysis (What Works / What Needs Work)
- Specific code recommendations
- Prioritized action items
- A/B test suggestions

---

## Integration Notes

This audit builds on:
- Previous ui-ux-designer audit (same day)
- Browser-vision-tester footer investigations

Next steps for Jared:
1. Prioritize immediate fixes (nav, opacity, CTAs)
2. Implement with full-stack-developer assistance
3. Use browser-vision-tester to verify after changes

---

## Attribution

**Tools Used**:
- Playwright (screenshot capture, performance metrics)
- WebFetch (content analysis)
- Claude vision (screenshot interpretation)

**Complementary Work**:
- ui-ux-designer audit from 2026-02-15
- Previous browser-vision-tester investigations

---

**Status**: Complete
**Memory Type**: Operational (reference for future site audits)
