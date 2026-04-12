# QA Memory: v2.7.0 CSS Deployment Verification

**Date**: 2026-02-20
**Type**: operational
**Agent**: qa-engineer
**Topic**: purebrain.ai plugin CSS-only deployment verification pattern

---

## Task

Verify 10 specific checks for plugin v2.7.0 (CSS-only change: newsletter link hover style) on live purebrain.ai blog post.

## Method That Worked

1. `curl -s [URL] > /tmp/page.html` - download full rendered HTML to temp file
2. Python `re.search()` for precise CSS rule matching (not just grep, which can miss multiline)
3. Check inline `<style>` blocks via Python - the plugin CSS is injected as inline style block index 5 (4600 chars) within the page
4. Separate "CSS rule presence" checks from "actual anchor href" checks

## Key Findings

- Plugin CSS is in style block index 5 (~4600 chars) in page HTML
- The newsletter CSS comment header is: `/* 2. NEWSLETTER / SUBSCRIBE LINKS inside .blog-cta-block p */`
- Default rule selector group: `body.single-post .blog-cta-block p a[href*="subscribe"], ...neural-feed...`
- Hover rule selector group: same pattern + `:hover`
- Actual neural-feed link href format: `https://purebrain.ai/blog/#neural-feed-subscribe?utm_source=blog&utm_medium=cta&...`

## All 10 Checks Passed for v2.7.0

See full report in qa-engineer response dated 2026-02-20.

## Patterns for Future CSS Verification

- Page size: ~161KB HTML for blog posts on purebrain.ai
- Style blocks: multiple inline `<style>` tags; plugin CSS typically block index 5
- Use `grep -c` for quick count, Python `re.search` for precise rule matching
- Always check BOTH CSS presence (rule exists) AND link href (actual element)
- Raw IP check (`89.167.19.20`) is a safety gate for Cloudflare tunnel health
