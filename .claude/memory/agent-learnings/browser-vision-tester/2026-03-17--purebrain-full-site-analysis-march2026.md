# Memory: PureBrain.ai Full Site Analysis — March 2026

**Date**: 2026-03-17
**Type**: operational + teaching + synthesis
**Tags**: purebrain, site-audit, load-performance, schema, mobile-nav, insiders, compare, blog

---

## Context

Comprehensive 6-page live audit of purebrain.ai using Playwright at 1440x900 and 375x812 viewports. Pages: homepage, blog listing, 3 blog posts, /insiders/, /compare/.

---

## Key Findings to Remember

### Load Performance (confirmed via performance.getEntriesByType)

| Page | DOM Ready | Resources | Transfer Size |
|------|-----------|-----------|---------------|
| Homepage | 7,164ms | 211 | 17,910 KB |
| Blog listing | 184ms | 13 | 15,586 KB |
| Blog post | 333ms | 9 | 11,962 KB |
| /insiders/ | 6,066ms | 192 | 17,907 KB |
| Compare | 682ms | 27 | 556 KB |

Homepage and /insiders/ are 7+ seconds because they load full WordPress origin asset stack (Elementor, Three.js, etc.) — 211 resources. CF Pages static pages (blog, compare) are dramatically faster.

### /insiders/ = Homepage Duplicate

The /insiders/ page is a byte-for-byte content duplicate of the homepage. Same H2s, same chatbox, same pricing, same 35 testimonials, same 11 images. Only difference: meta description and canonical. OG title is still the generic homepage title. This is a wasted conversion opportunity.

### Blog Banner Alt Text Disaster

Blog listing: 8 of 13 images have no alt text. All are post banner images. Fix: add post title as alt text. Direct SEO impact.

### No Mobile Navigation Anywhere

None of the 6 audited pages has a standard hamburger menu or consistent mobile nav. Users cannot navigate between homepage, blog, compare, and pricing from mobile without using browser back. Three different nav patterns exist across the site.

### Schema Gaps

- Homepage: No valid Schema.org (WebSite + Organization missing)
- Compare: No Schema.org at all (ItemList of 16 tools = big opportunity)
- Blog listing: CollectionPage schema present — correct
- Blog posts: FAQPage schema present — correct

### Compare Page Mobile Bug

At 375px the "Start Your AI Partnership" orange CTA button in the nav overlaps the "PUREBRAIN" logo text. Needs padding/max-width fix at mobile breakpoint.

### Background Color Slight Inconsistency

- Homepage/blog: `rgb(8, 10, 18)` = #080a12 (correct)
- Compare/insiders: `rgb(10, 14, 26)` = #0a0e1a (2 units lighter, visually imperceptible but measurable)

### 4 Required Blog Features — Confirmed Present

All tested posts have: video background, collapsible FAQs, daily recap section, social share buttons, footer CTA. This is passing spec.

---

## Teaching: Playwright Patterns for This Site

```python
# For homepage and insiders (heavy pages):
await page.goto(url, wait_until='domcontentloaded', timeout=60000)
await asyncio.sleep(5)  # Need 5s+ for Three.js to initialize

# For blog/compare (static CF Pages):
await page.goto(url, wait_until='domcontentloaded', timeout=30000)
await asyncio.sleep(3)  # 3s is sufficient

# Performance timing:
perf = await page.evaluate("""() => {
    const nav = performance.getEntriesByType('navigation')[0];
    return {
        dom_complete: Math.round(nav.domContentLoadedEventEnd),
        transfer_kb: Math.round(nav.transferSize / 1024),
        resources: performance.getEntriesByType('resource').length,
        resource_kb: Math.round(performance.getEntriesByType('resource')
            .reduce((a,r) => a + (r.transferSize||0), 0) / 1024)
    };
}""")

# Blog banner alt text check:
img_data = await page.evaluate("""() => {
    const imgs = [...document.querySelectorAll('img')];
    return {
        total: imgs.length,
        missing_alt: imgs.filter(i => !i.alt || i.alt.trim() === '').length
    };
}""")
```

---

## Report Location

Full report: `/home/jared/projects/AI-CIV/aether/exports/overnight-content/purebrain-site-analysis.md`
Screenshots: `/tmp/site-analysis/` (27 PNG files, captured 2026-03-17)
