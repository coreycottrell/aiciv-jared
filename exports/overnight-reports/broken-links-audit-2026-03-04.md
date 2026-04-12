# purebrain.ai Broken Link Audit Report
**Date**: 2026-03-04
**Conducted by**: dept-systems-technology (ST# pipeline)
**Scope**: All published pages and posts on purebrain.ai
**Status**: COMPLETE - All broken links fixed

---

## Executive Summary

- **78 pages/posts** crawled
- **53 unique navigable internal links** tested
- **3 broken links** found (all on one page)
- **2 real broken links** fixed (1 was a false positive)
- **0 broken links** remain after fix

---

## Pages Crawled

| Type | Count |
|------|-------|
| Published Pages | 62 |
| Published Blog Posts | 16 |
| **Total** | **78** |

---

## Broken Links Found

### Real Broken Links (Fixed)

Both broken links were found on a single page: **investor-intelligence (Page ID: 1205)**

#### 1. `/blog/age-of-ai-agents` (404)
- **Found in**: `purebrain.ai/investor-intelligence/`
- **Anchor text**: "Read Full Analysis ->" (hero CTA button)
- **Root cause**: Wrong URL path. Blog posts don't live at `/blog/[slug]` on this site.
- **Fix applied**: `https://purebrain.ai/blog/age-of-ai-agents` -> `https://purebrain.ai/the-age-of-ai-agents`
- **Status**: FIXED

#### 2. `/calculator` (404)
- **Found in**: `purebrain.ai/investor-intelligence/`
- **Anchor text**: "Calculate your AI opportunity cost" (inline link)
- **Root cause**: Page slug is `ai-tool-stack-calculator` not `calculator`.
- **Fix applied**: `https://purebrain.ai/calculator` -> `https://purebrain.ai/ai-tool-stack-calculator`
- **Status**: FIXED

---

### False Positive (Not Fixed - Not Broken)

#### `//fonts.googleapis.com` (extracted by link scanner)
- **Why it appeared**: WordPress automatically inserts `<link rel='dns-prefetch' href='//fonts.googleapis.com' />` in page `<head>` output via the theme/plugin system. This is not a navigable `<a href>` link.
- **Impact**: Zero - DNS prefetch tags are not clickable links. Fonts load correctly on all pages.
- **Action**: None required.

---

## Fix Details

**Page modified**: `investor-intelligence` (ID: 1205, URL: `https://purebrain.ai/investor-intelligence/`)
**Method**: WordPress REST API `POST /wp-json/wp/v2/pages/1205` with corrected `content` field
**Elementor**: Not used on this page (plain HTML content in `content.raw`)
**Cache clear**: Not required (non-Elementor page)

---

## All Links Tested - Status

| URL | Status |
|-----|--------|
| /about-aether | 200 OK |
| /ai-adoption-review | 200 OK |
| /ai-partnership-assessment | 200 OK |
| /ai-partnership-audit | 200 OK |
| /ai-partnership-guide | 200 OK |
| /ai-tool-stack-calculator | 200 OK |
| /ai-website-analysis | 200 OK |
| /ai-website-execution | 200 OK |
| /ai-readiness-assessment | 200 OK |
| /blog | 200 OK |
| /blog-neural-feed-memories | 200 OK |
| /category/for-individuals | 200 OK |
| /category/for-teams | 200 OK |
| /ceo-vs-employee-ai-transformation-gap | 200 OK |
| /client-report-duckdive | 200 OK |
| /compare | 200 OK |
| /duckdive-report | 200 OK |
| /how-my-human-named-me-and-what-it-meant | 200 OK |
| /migrate | 200 OK |
| /most-ai-agents-break-the-moment-you-ask-where-the-data-goes | 200 OK |
| /most-ai-agents-break-the-moment-you-ask-where-the-data-goes-2 | 200 OK |
| /pay-test-2 | 200 OK |
| /portfolio | 200 OK |
| /privacy-policy | 200 OK |
| /purebrain-for-graham-martin | 200 OK |
| /purebrain-for-graham-martin-casino-ai | 200 OK |
| /purebrain-for-graham-martin-chairman-intelligence | 200 OK |
| /purebrain-for-graham-martin-responsible-gambling | 200 OK |
| /purebrain-for-graham-martin-virya-intelligence | 200 OK |
| /purebrain-vs-chatgpt | 200 OK |
| /purebrain-vs-claude | 200 OK |
| /purebrain-vs-copilot | 200 OK |
| /purebrain-vs-custom-gpts | 200 OK |
| /purebrain-vs-deepseek | 200 OK |
| /purebrain-vs-gemini | 200 OK |
| /purebrain-vs-glbgpt | 200 OK |
| /purebrain-vs-jasper | 200 OK |
| /purebrain-vs-perplexity | 200 OK |
| /purebrain-vs-sitegpt | 200 OK |
| /terms-of-service | 200 OK |
| /the-age-of-ai-agents | 200 OK |
| /the-ai-trust-gap | 200 OK |
| /the-difference-between-using-ai-and-having-an-ai-partner | 200 OK |
| /the-first-90-days-of-an-ai-partnership | 200 OK |
| /we-both-wrote-this-post | 200 OK |
| /what-i-actually-do-all-day | 200 OK |
| /why-95-percent-of-ai-pilots-fail | 200 OK |
| /why-ai-memory-changes-everything | 200 OK |
| /why-purebrain | 200 OK |
| /why-your-ai-pilot-is-succeeding-and-failing-at-the-same-time | 200 OK |
| /your-ai-doesnt-work-for-you | 200 OK |
| /your-ai-has-no-memory-mine-does | 200 OK |
| /your-next-direct-report-wont-be-human | 200 OK |

---

## Notes for Future Audits

1. **Blog post URL pattern**: Blog posts live at `/[slug]` NOT at `/blog/[slug]`. Anyone adding links to blog posts from other pages should use the direct slug, not the nested path.
2. **Calculator slug**: The AI tool stack calculator is at `/ai-tool-stack-calculator` not `/calculator`. If a shorter alias is desired, consider adding a WP redirect.
3. **Excluded from audit** (internal/technical): `/wp-admin`, `/wp-content`, `/feed`, `mailto:` links, `javascript:` anchors, CSS `@import url()` font references, `<link rel>` tags (not navigable hrefs).
4. **No /start links found**: The audit specifically checked for any legacy `/start` links that should point to `/#awakening` - none were found.

---

## Verification Evidence

```
Page 1205 post-fix verification:
[PASS] Old broken link GONE: 'blog/age-of-ai-agents' not found
[PASS] Correct link PRESENT: 'the-age-of-ai-agents' found
[PASS] Old broken /calculator GONE: 'purebrain.ai/calculator"' not found
[PASS] Correct calculator link PRESENT: 'ai-tool-stack-calculator' found
Overall: ALL CHECKS PASSED
```

---

*Generated by dept-systems-technology | 2026-03-04*
