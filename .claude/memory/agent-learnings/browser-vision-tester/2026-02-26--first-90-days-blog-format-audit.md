# Memory: First 90 Days Blog Format Audit

**Date**: 2026-02-26
**Type**: teaching + operational
**Topic**: Blog post deployed with wrong content container - cascading CSS failures

---

## Task

Visual comparison audit of new post (the-first-90-days-of-an-ai-partnership) vs known good post (your-ai-has-no-memory-mine-does) to identify all formatting differences.

---

## Critical Discovery: Wrong Container Pattern

The new post used `.pb-blog-content` (a bare div in body) instead of the standard `.post-content` container. This caused ALL scoped CSS rules to fail because they target `.post-content h2`, `.post-content ul li`, `.post-content hr`, etc.

### Symptom: DOM selectors that caught this

```python
# This found nothing in the new post:
document.querySelector('.entry-content, .post-content')

# This found the content container:
document.querySelector('.pb-blog-content')

# Parent chain for H2 in bad post: h2 -> .pb-blog-content -> body
# Parent chain for H2 in good post: h2 -> article.pb-blog-post -> .post-entry -> .post-content -> .col-md-12
```

### Visual symptoms to look for

1. No hero banner image at top
2. H2 headings cramped (zero margin-top, zero margin-bottom)
3. Bullet lists styled with browser default (disc marker, white text) instead of brand blue (no disc, #2a93c1 text)
4. HRs very faint (opacity: 0.25) vs correct (opacity: 1)
5. Page feels "compressed" (6298px tall vs 12081px for comparable content)

---

## Specific CSS Differences Found

| Element | GOOD (.post-content) | BAD (.pb-blog-content) |
|---|---|---|
| H2 font-size | 36px | 32px |
| H2 margin-top | 36px | 0px |
| H2 margin-bottom | 25.2px | 0px |
| H3 margin | 36px/25.2px | 0px/0px |
| UL list-style | none (custom) | disc (browser default) |
| UL paddingLeft | 0px | 32px |
| LI color | rgb(42,147,193) blue | rgba(255,255,255,0.9) white |
| LI font-size | 18px | 16px |
| HR opacity | 1 | 0.25 |
| HR color | rgba(255,255,255,0.1) | rgb(232,237,245) |
| Inline link color | orange #f1420b | blue #2a93c1 |
| Container max-width | 760px | none (1440px full) |
| Hero image | PRESENT | MISSING |

---

## Detection Method

```python
# Quick check to catch this pattern fast
container_check = await page.evaluate("""() => {
    const good = document.querySelector('.post-content, .entry-content');
    const bad = document.querySelector('.pb-blog-content');
    return {
        good_container: !!good,
        bad_container: !!bad,
        h2_margin_top: (() => {
            const h2 = document.querySelector('h2');
            return h2 ? window.getComputedStyle(h2).marginTop : 'none';
        })()
    };
}""")
# If good_container=False and h2_margin_top='0px' -> wrong container deployed
```

---

## Fix

The post content needs to be re-published through the standard WordPress blog template so content renders inside `.post-content` (not `.pb-blog-content`). Also set the Featured Image in WP post settings to restore the hero banner.

---

## Files

- Report: `exports/screenshots/blog-format-audit/BLOG-FORMAT-AUDIT-REPORT.md`
- Screenshots: `exports/screenshots/blog-format-audit/NEW_*.png` and `GOOD_*.png` (18 total)
- Scripts: `capture_blog_comparison.py`, `deep_inspect_new_post.py`, `css_comparison.py`
