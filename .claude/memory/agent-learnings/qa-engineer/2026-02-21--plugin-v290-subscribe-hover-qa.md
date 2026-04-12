# QA Memory: Plugin v2.9.0 Subscribe Hover Fix - Full Verification

**Date**: 2026-02-21
**Type**: operational
**Agent**: qa-engineer
**Topic**: purebrain.ai plugin v2.9.0 - JS data-pb-subscribe tagging + CSS hover isolation

---

## Task

QA verify plugin v2.9.0 deployment on purebrain.ai:
1. Plugin version active
2. Subscribe hover CSS (orange, data-pb-subscribe)
3. CTA hover CSS (blue, href*=awakening)
4. No cross-contamination between the two
5. Page integrity

## Result

**PASS - All 8 verification categories pass on 2 posts tested.**

## Key Findings

### v2.9.0 Mechanism
- JS function `initSubscribeLinks()` is injected at Script #26 in page HTML (footer)
- It runs on DOMContentLoaded: `link.setAttribute('data-pb-subscribe', '1')`
- Targets: `a[href*="subscribe"], a[href*="newsletter"], a[href*="neural-feed"]`
- Also carries v2.8.0 behavior: `link.removeAttribute('style')`

### Specificity Architecture
- Plugin subscribe hover: `body.single-post .blog-cta-block p a[data-pb-subscribe]:hover` = 6 qualifiers
- wp-custom-css CTA hover: `body.single-post .blog-cta-block a[href*="awakening"]:hover` = 5 qualifiers
- Subscribe wins with data-pb-subscribe (one extra attribute selector)

### Additional CSS (wp-custom-css) is CLEAN
- The broad `blog-cta-block a:hover` rule was successfully removed (mentioned in comment)
- All actual selectors are scoped to `[href*="awakening"]`
- GOTCHA: My regex `blog-cta-block[^{]*a:hover` was a FALSE POSITIVE - matched the CSS comment text
  mentioning the removed rule. Always verify regex matches are actual CSS selectors, not comment text.

### JS Attribute is Runtime-Only
- Static curl HTML will NOT show `data-pb-subscribe` attribute on subscribe anchors
- This is EXPECTED and CORRECT - JS adds it after DOM is ready
- Verify JS presence in HTML (Script #26) as proxy for runtime behavior

## Posts Tested

- Post 565: `/the-difference-between-using-ai-and-having-an-ai-partner/` (159KB)
- Post 480: `/why-your-ai-pilot-is-succeeding-and-failing-at-the-same-time/` (165KB)

## Method

1. WP REST API `GET /wp-json/wp/v2/plugins?search=purebrain` → version + status check
2. `curl -s [URL] -o /tmp/postN.html` for 2 posts in parallel
3. Python regex analysis on style blocks, script blocks, anchor tags
4. Separate inline script extraction to find initSubscribeLinks() function
5. Line-by-line CSS analysis to distinguish selectors from comment text

## CSS Block Location

- Plugin CSS: style block #5 in `<head>` (~5836 chars, comment header: "BLOG CTA BLOCK — v2.7.0")
- Plugin JS: Script #26 (inline, footer)
- wp-custom-css: `<style id="wp-custom-css">` block in `<head>`

## False Positive Lesson

When checking for "broad hover" rules in CSS, always verify the match is an actual CSS selector
line, not embedded in a comment. Use line-by-line analysis with comment detection:
```python
lines = css.split('\n')
for i, line in enumerate(lines):
    if 'blog-cta-block' in line and 'hover' in line:
        in_comment = line.strip().startswith('*') or line.strip().startswith('/*')
        if not in_comment:
            print(f"SELECTOR: {line}")
```
