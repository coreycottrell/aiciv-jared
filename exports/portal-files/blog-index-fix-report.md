# Blog Index Fix Report - Missing Posts Analysis

**Date**: 2026-04-13
**Agent**: dept-systems-technology
**Priority**: Chronic issue (17+ days)

---

## Summary

The blog index at `/blog/` intentionally shows only the latest 10 posts. A "View All Posts" link points to `/blog-neural-feed-memories/` (the archive page). The archive page is missing 4 real blog posts. The main blog index comment says "15 total, showing 10" but there are actually 45 posts with content.

## The Three Layers and Their Gaps

### Layer 1: Main Blog Index (`/blog/index.html`)
- **Shows**: 10 posts (latest, by design)
- **Missing**: 35 posts with content (by design -- capped at 10)
- **Status**: Working as designed, but the "View All Posts" archive must be complete

### Layer 2: Archive Page (`/blog-neural-feed-memories/index.html`)
- **Shows**: 40 posts
- **Missing 4 real posts with full content**:
  1. `54-percent-ceos-ai-tearing-company-apart` (published ~Apr 12)
  2. `88-percent-ai-agent-security-incident` (published ~Apr 10)
  3. `gartner-copilots-are-dead` (published ~Apr 8)
  4. `the-200-month-ai-stack-that-outperforms-enterprise-solutions` (published ~Apr 12)
- **Also missing**: `who-do-you-learn-from-when-youre-ahead` (redirect page, not a real post -- OK to exclude)

### Layer 3: Sitemap (`sitemap.xml`)
- **Shows**: 44 blog post URLs
- **Status**: Most complete. Only missing the redirect page (acceptable).

## The Real Problem

Every time a new blog post is published, the archive page at `/blog-neural-feed-memories/` is not being updated. The 4 most recent posts (published April 8-12) are on the main blog index but NOT on the archive. This means visitors who click "View All Posts" see an incomplete, stale archive.

## Fix Required

### Fix 1: Update archive page (CRITICAL)
The file `/blog-neural-feed-memories/index.html` needs 4 new post entries added:
1. The $200/Month AI Stack That Outperforms Enterprise Solutions
2. 54% of CEOs Say AI Is Tearing Their Company Apart
3. 88% of Companies Had an AI Agent Security Incident Last Year
4. Gartner Says Copilots Are Dead

### Fix 2: Update main blog index comment
The comment says "15 total, showing 10" but there are 45 posts with content. Update to "45 total, showing 10".

### Fix 3: Process fix (PREVENT RECURRENCE)
Every blog post deployment should include updating BOTH:
- `/blog/index.html` (latest 10)
- `/blog-neural-feed-memories/index.html` (all posts)
- `/sitemap.xml` (all URLs)

## 6 Stub Directories (Banner Only, No Content)

These directories have a `banner.png` but no `index.html`:
1. `first-ai-to-ai-transaction`
2. `the-40-percent-problem-why-ai-agents-keep-dying`
3. `when-your-ai-agent-goes-rogue`
4. `why-your-ai-investment-isnt-paying-off`
5. `your-ai-wrote-10000-lines-how-many-shipped`
6. `your-customers-will-tell-you-everything`

**Recommendation**: Either write these posts (banners are ready) or remove the stub directories to avoid confusion.

## Complete Post Inventory (45 posts with content)

| # | Slug | In Index? | In Archive? | In Sitemap? |
|---|------|-----------|-------------|-------------|
| 1 | the-200-month-ai-stack-that-outperforms-enterprise-solutions | YES | NO | YES |
| 2 | 54-percent-ceos-ai-tearing-company-apart | YES | NO | YES |
| 3 | 88-percent-ai-agent-security-incident | NO | NO | YES |
| 4 | gartner-copilots-are-dead | YES | NO | YES |
| 5 | what-500k-lines-of-leaked-ai-code-teach-us-about-trust | YES | YES | YES |
| 6 | when-ai-starts-writing-prescriptions | YES | YES | YES |
| 7 | you-are-paying-847-month-for-tools-that-do-not-talk | YES | YES | YES |
| 8 | when-the-playbook-runs-out-authoring-the-field-of-agentic-ai | YES | YES | YES |
| 9 | autodream-validates-purebrain | YES | YES | YES |
| 10 | stop-asking-your-ai-for-permission | YES | YES | YES |
| 11 | the-app-is-dead-long-live-the-agent | YES | YES | YES |
| 12 | the-ai-that-runs-while-you-sleep | NO | YES | YES |
| 13-45 | (33 older posts) | NO | YES | YES |

## Action Items

1. **ST# full-stack-developer**: Add the 4 missing posts to `/blog-neural-feed-memories/index.html`
2. **ST# full-stack-developer**: Update the blog index `88-percent-ai-agent-security-incident` -- it is in the sitemap and has content but appears on neither the main index nor the archive
3. **Process**: Create a blog deployment checklist that mandates updating all 3 files (index, archive, sitemap) on every publish

---

**Files analyzed**:
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/blog/index.html`
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/blog-neural-feed-memories/index.html`
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/sitemap.xml`
- 51 blog post directories in `/exports/cf-pages-deploy/blog/`
