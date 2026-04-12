# dept-marketing-advertising Memory: Blog/Site/Distribution Analysis

**Date**: 2026-03-21
**Type**: operational + teaching
**Agent**: dept-marketing-advertising (CMO)
**Confidence**: high — direct file audit of all 32 CF Pages blog posts

---

## Task

Overnight tasks 2-4: blog audit vs March 20 standard, site analysis, distribution strategy.

## Key Findings — Blog (Task 2)

### All 32 posts pass on:
- Meta description (present, all posts)
- Canonical tag (all posts)
- Background video (all posts)
- Daily recap section (all posts)
- Social share buttons (all posts)

### Failures across the archive:
- **Audio**: 30 of 32 posts missing. Only `prompting-is-dead` and `the-ai-that-gets-smarter-when-you-push-back` have `audio.mp3` + player HTML.
- **BlogPosting schema**: 29 of 32 missing. Only `what-i-named-my-ai`, `why-enterprises-are-betting-on-agentic-ai`, `why-your-ai-should-have-a-name` have it.
- **OG image**: 7 posts missing `og:image` tag (banner.png file exists, tag is just absent).
- **pb-byline CSS class**: 30 of 32 wrong or missing. Only `something-big-already-happened` and `the-meeting-your-ai-should-already-know-about` have `pb-byline`.
- **Internal links**: 0 internal blog links in all 32 posts. Session 14 of tracking this gap.

### Blog index page:
- Only shows 11 of 32 posts — 21 posts invisible to browsers
- No OG image on index
- No Schema.org markup
- Title lacks keyword "AI"

## Key Findings — Site (Task 3)

- Homepage HTML: 461KB, 244KB is inline CSS (legacy WP artifact)
- DOM ready time: ~7+ seconds (vs 330ms for static blog posts)
- Homepage title tag missing "AI partner" and "memory" — primary keywords unaddressed
- No Organization schema on homepage
- No meta robots tag
- H1 is "PURE BRAIN" — brand name, not a benefit statement
- Compare pages (16 exist) have zero schema, zero internal links — untapped SEO asset

## Key Findings — Distribution (Task 4)

- Content quality is high; distribution is the constraint
- Cross-channel pipeline exists in pieces but not automated
- Compare pages (16) + blog index are highest-leverage quick wins for SEO
- Email capture missing from blog posts and compare pages — losing 50-100 subscribers/week
- Brevo welcome sequence still not built (14 sessions of tracking)
- Podcast pitch kit exists in draft; not yet deployed

## Reusable Patterns

**OG image quick audit**: `grep -L 'og:image' */index.html` in the blog directory gives the failure list instantly.

**BlogPosting vs FAQPage**: WP-to-static exports often bring FAQPage schema (from SEO plugins) but lose BlogPosting schema (which WP generates natively). Always audit both on migration.

**Blog index gap pattern**: A static site blog index is not auto-updated. If the build pipeline doesn't regenerate the index on each new post, old posts become invisible. After 32 posts with 21 missing from index, this is clearly a build step that was skipped.

**Distribution gap detection**: Check `blog_distribution_state.json` for posts that were published but never emailed/tweeted/syndicated. This file exists in the repo and tracks distribution state.

## Files

Full report: `/home/jared/projects/AI-CIV/aether/exports/overnight/2026-03-21--blog-site-distribution-analysis.md`

---

**END MEMORY**
