# QA Memory: Plugin v2.8.0 Subscribe Link Fix Verification

**Date**: 2026-02-21
**Type**: operational
**Agent**: qa-engineer
**Topic**: purebrain.ai plugin v2.8.0 subscribe link fix - all 7 posts verified

---

## Task

Verify 5 checks on all 7 PureBrain blog posts after plugin v2.8.0 deployed:
1. Subscribe link exists
2. href contains `#neural-feed-subscribe`
3. No inline `style=` on subscribe anchor
4. Plugin JS (`removeAttribute('style')`) present
5. Orange gradient CSS (`#f1420b`) present

## Result

**35/35 checks passed. All 7 posts PASS.**

## Key Evidence Patterns (Consistent Across All Posts)

- href: `https://purebrain.ai/blog/#neural-feed-subscribe?utm_source=blog&utm_medium=cta&utm_campaign=...`
- C3: Each post has exactly 1 subscribe anchor, 0 with inline style
- C4 JS: `link.removeAttribute('style');` present in plugin-injected script block
- C5 CSS: `background: linear-gradient(135deg, #f1420b 0%, #d13608 100%) !important;`

## Method

1. `curl -s [URL] -o /tmp/postN.html` - download all 7 posts in parallel
2. Python regex for precise anchor/attribute matching
3. Evidence extraction run for audit trail (specific hrefs, JS snippets, CSS context)

## Patterns for Future Plugin QA

- All 7 posts are consistent - if one fails, likely all fail (plugin is global)
- Subscribe anchor count per post = 1 (blog footer CTA block)
- Plugin JS injection is reliable: always appears as `link.removeAttribute('style');`
- CSS block contains both the default and hover states in same `<style>` block (plugin-injected)
- Page HTML size: ~161KB per post (consistent with v2.7.0 baseline)
- Use parallel curl fetches + single Python pass for speed
