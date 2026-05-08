# PureBrain.ai Overnight Site & SEO Analysis
**Date**: 2026-04-25 | **Analyst**: SEO Specialist (SEO#)
**Focus**: Follow-up on Apr 24 findings + new page audits

---

## EXECUTIVE SUMMARY

Five issues were flagged yesterday. **Zero of the five have been fixed.** All remain open and impacting the live site today. Additionally, new findings include a missing 404 page (CF Pages serves the homepage with HTTP 200 for all invalid URLs), the ai-partnership-assessment-v2 page does not exist in the deploy, and the new "Your AI Has a Memory Problem" blog post has solid SEO but is missing from the sitemap and blog index.

---

## SECTION A: YESTERDAY'S ISSUES -- STATUS CHECK

### 1. Homepage + 4 Landing Pages og:image -- STILL BROKEN

**Status**: NOT FIXED

All five pages still reference `https://purebrain.ai/wp-content/uploads/2026/02/Pure-Brain-Vid-3.gif` which is a dead WordPress path. This URL returns nothing on CF Pages. Every social share of these pages shows a broken preview image.

| Page | og:image URL | Status |
|------|-------------|--------|
| `/` (homepage) | wp-content/uploads/.../Pure-Brain-Vid-3.gif | BROKEN |
| `/awakened/` | wp-content (x3 og:image tags -- conflicting) | BROKEN |
| `/partnered/` | wp-content (x3 og:image tags -- conflicting) | BROKEN |
| `/unified/` | wp-content (x3 og:image tags -- conflicting) | BROKEN |
| `/insiders/` | wp-content (x3 og:image tags -- conflicting) | BROKEN |

**Extra finding**: /awakened/, /partnered/, /unified/, /insiders/ each have THREE conflicting og:image tags (two wp-content GIFs + one Yoast-class cropped PNG). Browsers will typically use the first one encountered, which is the broken GIF. This needs to be reduced to a single valid og:image per page.

**Impact**: HIGH -- these are the primary conversion pages. Anyone sharing on LinkedIn, Slack, or Discord sees a broken image.

### 2. Blog Index Post Count -- STILL ONLY 14 OF 53

**Status**: NOT FIXED

The /blog/ index page lists exactly 14 posts (unchanged from yesterday). There are now 53 blog post directories (up from 50), meaning the gap has widened. 39 posts are invisible from the blog index.

Posts visible on /blog/:
- 54-percent-ceos-ai-tearing-company-apart
- autodream-validates-purebrain
- gartner-copilots-are-dead
- stop-asking-your-ai-for-permission
- the-ai-that-gets-smarter-when-you-push-back
- the-ai-that-runs-while-you-sleep
- the-app-is-dead-long-live-the-agent
- the-meeting-your-ai-should-already-know-about
- what-500k-lines-of-leaked-ai-code-teach-us-about-trust
- when-ai-starts-writing-prescriptions
- when-the-playbook-runs-out-authoring-the-field-of-agentic-ai
- you-are-paying-847-month-for-tools-that-do-not-talk
- your-ai-has-no-idea-who-you-are
- your-ai-resets-to-zero-every-morning

**Not visible**: 39 other posts including the newest "Your AI Has a Memory Problem"

### 3. 7 Missing Blog Posts from Sitemap -- STILL MISSING

**Status**: NOT FIXED

Sitemap.xml still has 102 URLs. All 7 posts identified yesterday remain absent:

1. `54-percent-ceos-ai-tearing-company-apart`
2. `when-your-ai-agent-goes-rogue`
3. `the-200-month-ai-stack-that-outperforms-enterprise-solutions`
4. `why-your-ai-investment-isnt-paying-off`
5. `your-ai-has-a-memory-problem` (new post, also missing)
6. `your-ai-wrote-10000-lines-how-many-shipped`
7. `your-customers-will-tell-you-everything`

**Note**: `54-percent-ceos` IS on the blog index but NOT in the sitemap -- inverted problem from most posts.

### 4. Brainiac Training Modules -- LOADED CORRECTLY (VERIFIED FIXED)

**Status**: FIXED

Yesterday these were reportedly showing the homepage. Today the deploy directory has properly titled Brainiac pages:

| Page | Title | Status |
|------|-------|--------|
| `/brainiac-mastermind-training/` | Brainiac Mastermind Training | PureBrain AI Partnership Program | OK |
| `/brainiac-module-1-foundations/` | Brainiac -- Module 1: Foundations | OK |
| `/brainiac-training-hub/` | Brainiac Training Hub | PureBrain | OK |
| `/brainiac-training-workshop/` | Brainiac Workshop: From User to Director | PureBrain | OK |

3 of 4 Brainiac pages are in the sitemap. Missing from sitemap: `/brainiac-module-1-foundations/`

### 5. Compare Page Quiz -- EXISTS (VERIFIED)

**Status**: CONFIRMED WORKING

`/compare/index.html` exists with 125 instances of quiz/question/answer/score/result keywords. Page is deployed and accessible.

---

## SECTION B: NEW ANALYSIS

### B1. "Your AI Has a Memory Problem" Blog Post -- SEO Audit

**URL**: `/blog/your-ai-has-a-memory-problem/`
**Live Status**: HTTP 200 (confirmed live on purebrain.ai)

| Element | Status | Details |
|---------|--------|---------|
| Title tag | PARTIAL | "Your AI Has a Memory Problem" -- no brand suffix |
| Meta description | OK | 189 chars, keyword-rich, compelling |
| og:image | OK | `https://purebrain.ai/blog/your-ai-has-a-memory-problem/banner.jpg` (absolute, resolves HTTP 200, 525KB) |
| og:type | OK | article |
| Canonical | OK | Correct absolute URL |
| Twitter card | OK | summary_large_image with image |
| JSON-LD | PARTIAL | 1 block (BlogPosting) -- missing FAQ/breadcrumb schema |
| Author | Aether | Consistent with article:author meta |
| Banner files | OK | Both banner.png (2.7MB) and banner.jpg (525KB) present |
| Sitemap | MISSING | Not in sitemap.xml |
| Blog index | MISSING | Not listed on /blog/ page |
| GTM + Clarity | OK | Both tracking scripts present |

**Issues to fix**:
1. Add " | PureBrain" suffix to title tag
2. Add to sitemap.xml
3. Add to blog index
4. Add second JSON-LD block (FAQ schema if post has FAQ section, or BreadcrumbList)

### B2. /ai-partnership-assessment-v2/ -- DOES NOT EXIST

**Status**: Page does not exist in the deploy directory.

What does exist:
- `/ai-partnership-assessment/` -- deployed, in sitemap, but has NO meta description, NO og:image, NO canonical tag. Only has a `<title>` tag.
- `/ai-readiness-assessment/` -- deployed, in sitemap
- `/ai-partnership-calculator/` -- deployed, NOT in sitemap
- `/ai-tool-stack-calculator/` -- deployed, NOT in sitemap
- `/assessment-draft/` -- deployed (should this be public?)

If v2 was built, it has not been deployed to CF Pages yet.

### B3. Meeting Pages -- NONE EXIST

Tested paths: `/meeting/`, `/book-a-call/`, `/schedule-call/`, `/consultation/`

None of these directories exist in the deploy folder. If meeting pages are desired, they need to be created.

### B4. 404 Page -- DOES NOT EXIST (CRITICAL)

**Status**: No `404.html` file in deploy directory.

**Live behavior**: CF Pages serves the homepage (HTTP 200) for all nonexistent URLs. This means:
- Search engines index garbage URLs as the homepage (duplicate content)
- Users who land on broken links see the homepage instead of a helpful error
- Google Search Console will not report 404 errors because they technically return 200
- Any old WordPress URLs that were never redirected silently serve the homepage

**Fix**: Create a proper `404.html` with:
- HTTP 404 status (CF Pages handles this automatically when 404.html exists)
- Branded design matching the site
- Search box or navigation back to valid pages
- `noindex` meta tag

---

## SECTION C: FULL ISSUE TRACKER

| # | Issue | Severity | Status | Days Open |
|---|-------|----------|--------|-----------|
| 1 | Homepage + 4 landing pages broken og:image (wp-content) | CRITICAL | OPEN | 2+ |
| 2 | Blog index shows 14 of 53 posts | CRITICAL | OPEN | 2+ |
| 3 | 7+ blog posts missing from sitemap | HIGH | OPEN | 2+ |
| 4 | No 404.html -- invalid URLs serve homepage as HTTP 200 | HIGH | NEW |
| 5 | 25 comparison pages missing og:image | HIGH | OPEN | 2+ |
| 6 | Title tag duplication on /awakened/, /partnered/, /unified/ | HIGH | OPEN | 2+ |
| 7 | "Memory Problem" post missing from sitemap + blog index | MEDIUM | NEW |
| 8 | /ai-partnership-assessment/ missing meta desc, og:image, canonical | MEDIUM | NEW |
| 9 | /brainiac-module-1-foundations/ missing from sitemap | LOW | NEW |
| 10 | /assessment-draft/ publicly accessible (should it be?) | LOW | NEW |
| 11 | /ai-partnership-calculator/ and /ai-tool-stack-calculator/ not in sitemap | LOW | NEW |
| 12 | 3 blog posts have incomplete JSON-LD (1 block instead of 2) | LOW | OPEN | 2+ |
| 13 | 35 blog posts lack brand suffix in title tag | LOW | OPEN | 2+ |
| 14 | Pricing pages have 3 conflicting og:image tags each | MEDIUM | NEW |
| 15 | Brainiac modules -- titles loading correctly | RESOLVED | FIXED |
| 16 | Compare page quiz | RESOLVED | CONFIRMED |

---

## TOP 3 PRIORITIES FOR TODAY

### Priority 1: Create 404.html (15 min)
Every invalid URL currently returns HTTP 200 with homepage content. This causes duplicate content issues and poor UX. CF Pages automatically serves 404.html with proper HTTP 404 status when the file exists in the project root.

### Priority 2: Fix og:image on homepage + 4 landing pages (15 min)
Replace all `wp-content` og:image references with valid absolute URLs. Remove duplicate/conflicting og:image tags from pricing pages (each has 3). This is a 5-page edit.

### Priority 3: Rebuild blog index to show all posts (1-2 hr)
39 posts are invisible. This is the biggest content discoverability problem on the site. The index page needs to be regenerated to include all published posts.

---

## FILES REFERENCED
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/index.html` (homepage)
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/blog/index.html` (blog index)
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/blog/your-ai-has-a-memory-problem/index.html`
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/sitemap.xml`
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/{awakened,partnered,unified,insiders}/index.html`
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/ai-partnership-assessment/index.html`
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/brainiac-*/index.html`
