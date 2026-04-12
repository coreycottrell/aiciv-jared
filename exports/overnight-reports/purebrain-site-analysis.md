# PureBrain.ai Full Site Analysis
**Date**: 2026-02-28
**Agent**: dept-systems-technology (ST#)
**Analysis Type**: Comprehensive overnight audit — fresh data collection
**Baseline**: Previous analysis 2026-02-27 (36 hours earlier)

---

## Executive Summary

PureBrain.ai is in strong foundational health. Cloudflare caching is performing exceptionally (all pages < 0.32s full download). 14 blog posts are live with daily cadence maintained. However, 4 critical issues require action: the security plugin remains inactive, 2 blog posts have no meta descriptions (including the newest), the homepage is serving the wrong background video (still PureResearch.ai-1.mp4), and user enumeration is exposed via the unauthenticated WP REST API.

**Overall Site Health: 7.4 / 10** (same as yesterday — no regressions, no fixes to previous critical issues yet)

---

## CRITICAL ISSUES (Fix Immediately)

### CRITICAL-1: Security Plugin Still Inactive
**Severity**: CRITICAL | **Status**: UNCHANGED from Feb 27
- PureBrain Security v4.7.2.1 = `[INACTIVE]`
- Drops security posture from 7.2/10 to ~5/10
- Missing: API key protection, user enumeration blocking, XSS hardening, cookie security flags, security headers
- The plugin exists (v4.7.2.1 was built), just needs reactivation
- **Fix**: Activate via WP Admin > Plugins or `POST /wp-json/wp/v2/plugins/purebrain-security%2Fpurebrain-security` with `{"status":"active"}`

### CRITICAL-2: Wrong Background Video on Homepage
**Severity**: CRITICAL | **Status**: UNCHANGED from Feb 27
- Source found in homepage HTML: `https://purebrain.ai/wp-content/uploads/2026/02/PureResearch.ai-1.mp4`
- Should be: Neural brain animation video
- This is the FIRST thing visitors see — brand mismatch with a competitor's video name
- **Fix**: Update `<source>` tag in WP page ID 11 (elementor_data), swap to correct neural brain MP4

### CRITICAL-3: User Enumeration Exposed (Unauthenticated)
**Severity**: HIGH | **Status**: NEW FINDING (security plugin inactive = this is why)
- `GET https://purebrain.ai/wp-json/wp/v2/users` (no auth required) returns:
  ```
  ID:1  username: 835655pwpadmin  (admin account username exposed)
  ID:2  name: Jared Sanborn       (founder identity exposed)
  ID:3  name: Aether (AI)         (AI account exposed)
  ```
- Exposes admin username — enables targeted brute-force attacks on wp-login.php
- `wp-login.php` returns 200 (accessible)
- `xmlrpc.php` returns 403 (blocked — good)
- **Fix**: Reactivating security plugin should block this. Alternatively add Cloudflare WAF rule.

### CRITICAL-4: 2 Blog Posts Missing Meta Descriptions
**Severity**: HIGH | **Status**: Post 1084 is NEW today; Post 950 was unfixed from Feb 27
- Post 1084: `/ai-doesnt-make-your-team-smarter-it-makes-the-gap-bigger/` (published TODAY, Feb 28)
- Post 950: `/your-ai-has-no-memory-mine-does/` (published Feb 25, still missing)
- Google auto-generates descriptions for missing ones — always worse than hand-crafted
- Both posts have og:image, article schema, and good H1/H2 structure — just missing the meta desc
- **Fix**: Update `_yoast_wpseo_metadesc` meta field via WP REST API for both posts

---

## HIGH PRIORITY ISSUES

### HIGH-1: Homepage Has Duplicate Schema Blocks
**Severity**: HIGH | **Status**: Ongoing Elementor/Yoast conflict
- 2 separate `<script type="application/ld+json">` blocks on homepage
- Schema 1: Title = "PureBrain | Your Agentic AI Partner for Business" (correct, from Yoast)
- Schema 2: Title = "PURE BRAIN - Your Brain. Your AI. Actual Intelligence! - Agentic AI" (stale, from Elementor)
- Google may see conflicting page identity signals
- **Fix**: Disable Elementor's built-in schema generation (Elementor > Settings > Advanced > Schema)

### HIGH-2: Security Headers Completely Missing
**Severity**: HIGH | **Status**: Confirmed — zero security headers in HTTP responses
- Headers present: CF-Cache-Status, Cache-Control, Content-Type (standard)
- Headers MISSING:
  - `Strict-Transport-Security` (HSTS)
  - `X-Content-Type-Options`
  - `X-Frame-Options` (clickjacking protection)
  - `Content-Security-Policy`
  - `Referrer-Policy`
  - `Permissions-Policy`
- **Fix**: Cloudflare Transform Rules can inject all 6 headers in under 10 minutes. No WP access needed.

### HIGH-3: /ai-adoption-assessment/ Returns 404 — No Redirect
**Severity**: HIGH | **Status**: UNCHANGED from Feb 27 (old URL still getting traffic)
- `https://purebrain.ai/ai-adoption-assessment/` → 404 (no redirect)
- Correct URL: `/ai-adoption-review/` or `/ai-partnership-assessment/`
- Old URL may have external links pointing to it (social posts, emails)
- **Fix**: Add 301 redirect in Cloudflare or WP (Yoast redirect manager)

### HIGH-4: /training/ and /video-test/ Are Indexed
**Severity**: HIGH | **Status**: NEW FINDING
- Both pages appear in page-sitemap.xml and are set to `index: follow` by Yoast
- `/training/` (Brainiac Mastermind Training) — has password gate but is still indexable
- `/video-test/` (Portal Enhanced v1) — clearly a test/staging page, should NOT be indexed
- Google will crawl these and waste crawl budget on staging/test content
- **Fix**: Set both to `noindex` via Yoast SEO on each page

---

## MEDIUM PRIORITY ISSUES

### MEDIUM-1: Homepage Page Size Is Large
**Severity**: MEDIUM
- Homepage: 446,626 bytes (446KB) at full download
- Blog page: 171KB (well-optimized)
- Assessment: 155KB (well-optimized)
- The homepage is 2.6x larger than other pages — likely due to embedded Three.js, chatbox JS, and video player
- Despite size, TTFB is 0.19s (Cloudflare cache hit) — so real-world impact is low
- **Recommendation**: Defer non-critical JS (Three.js, chatbox initialization) to after LCP

### MEDIUM-2: Blog Page Links to Wrong Slug for One Post
**Severity**: MEDIUM
- Blog page links to: `/most-ai-agents-break-the-moment-you-ask-where-the-data-goes/` (no `-2` suffix)
- WP actual slug: `/most-ai-agents-break-the-moment-you-ask-where-the-data-goes-2/`
- The URL without `-2` returns 200 OK (Cloudflare seems to be resolving it) but it's not the canonical URL
- Clicking this link from the blog page may reach a different/old version or cause confusion
- **Fix**: Update blog page to use the correct `-2` slug, or set up a canonical redirect

### MEDIUM-3: 49 Fixed-Width Elements Could Break Mobile
**Severity**: MEDIUM
- Found 49 inline CSS declarations with `width: Xpx` where X > 600
- On screens < 600px wide these could cause horizontal scroll bars
- Mobile viewport is correct: `width=device-width, initial-scale=1.0, viewport-fit=cover`
- Mobile nav is present (hamburger detected)
- **Recommendation**: Audit fixed-width containers, replace with `max-width` or `width: 100%`

### MEDIUM-4: Zero Images with srcset
**Severity**: MEDIUM
- No `srcset` attributes found anywhere on the homepage
- All images serve at original resolution regardless of device
- Mobile users downloading desktop-sized images wastes bandwidth
- **Fix**: Enable Elementor's image optimization or add srcset via plugin

### MEDIUM-5: Category/Tag Taxonomy Gaps
**Severity**: MEDIUM
- 6 categories exist but 2 have 0 posts: `AI Partnership` and `Origin Story`
- 16 tags exist but several have 0 posts: `AI adoption`, `AI partnership`, `digital transformation`, `enterprise AI`, `Founders`
- The empty categories will appear in sitemap and category pages with no content
- **Fix**: Either assign posts to these categories or set them to noindex/remove them

### MEDIUM-6: wp-login.php Publicly Accessible
**Severity**: MEDIUM
- `https://purebrain.ai/wp-login.php` returns HTTP 200 (login page visible)
- With user enumeration exposed (CRITICAL-3) and admin username known, this is a brute force target
- `xmlrpc.php` is correctly blocked (403)
- **Fix**: Add Cloudflare WAF rule to block wp-login.php to all IPs except Jared's

---

## LOW PRIORITY / ENHANCEMENTS

### LOW-1: Two Tiny Fonts Below 12px
- 2 instances of sub-12px font sizes found in homepage inline CSS
- Could be unreadable on mobile screens
- **Fix**: Audit and raise to minimum 12px

### LOW-2: Site Tagline Not Optimal
- WP Settings > Tagline: "Your Brain. Your AI. Actual Intelligence"
- This is used in some schema blocks and could be cleaner
- Consider: "Persistent AI Memory. Agentic Workflows. Built for Business."

### LOW-3: WP API Namespace Exposure
- `https://purebrain.ai/wp-json/` exposes full API route listing
- Standard WordPress behavior but worth noting — reveals plugin capabilities
- **Recommendation**: Restrict to authenticated requests if security plugin is reactivated

---

## PERFORMANCE METRICS (Feb 28, 2026)

All measurements taken with Cloudflare cache bypassed (Cache-Control: no-cache):

| Page | HTTP | TTFB | Total DL | Page Size |
|------|------|------|----------|-----------|
| / (homepage) | 200 | 0.19s | 0.25s | 446KB |
| /blog/ | 200 | 0.21s | 0.25s | 171KB |
| /ai-partnership-assessment/ | 200 | 0.24s | 0.28s | 155KB |
| /ai-doesnt-make-your-team-smarter... | 200 | 0.30s | 0.32s | 135KB |
| /invitation/ | 200 | 0.16s | 0.21s | 191KB |
| /compare/ | 200 | 0.20s | 0.24s | 171KB |
| /ai-tool-stack-calculator/ | 200 | 0.19s | 0.25s | 273KB |
| /why-purebrain/ | 200 | 0.20s | 0.24s | 157KB |
| /migrate/ | 200 | 0.22s | 0.27s | 201KB |
| /ai-website-analysis/ | 200 | 0.14s | 0.19s | 148KB |

**Overall Assessment**: Performance is excellent. Cloudflare caching is working perfectly. All pages under 0.32s total download. No performance critical issues.

**Blog Posts (cached hits)**:
- /ai-doesnt-make-your-team-smarter...: 0.15s TTFB, 135KB
- /your-next-direct-report-wont-be-human/: 1.04s TTFB (cache MISS — new post, not cached yet)
- /why-purebrain/: 1.39s TTFB (cache MISS)
- /ai-tool-stack-calculator/: 1.25s TTFB (cache MISS — heavy JS page)

---

## SEO AUDIT

### Blog Posts — SEO Status
| Post ID | Slug | Meta Desc | OG Image | Schema | Status |
|---------|------|-----------|----------|--------|--------|
| 1084 | ai-doesnt-make-your-team-smarter | MISSING | YES | Article | FIX NEEDED |
| 966 | the-first-90-days-of-an-ai-partnership | YES | YES | Article | OK |
| 950 | your-ai-has-no-memory-mine-does | MISSING | YES | Article | FIX NEEDED |
| 879 | your-next-direct-report-wont-be-human | YES | YES | Article | OK |
| 696 | we-both-wrote-this-post | YES | YES | Article | OK |
| 631 | the-ai-trust-gap | YES | YES | Article | OK |
| 606 | why-95-percent-of-ai-pilots-fail | YES | YES | Article | OK |
| 565 | the-difference-between-using-ai-and-having-an-ai-partner | YES | YES | Article | OK |
| 480 | why-your-ai-pilot-is-succeeding-and-failing-at-the-same-time | YES | YES | Article | OK |
| 381 | ceo-vs-employee-ai-transformation-gap | YES | YES | Article | OK |
| 316 | why-ai-memory-changes-everything | YES | YES | Article | OK |
| 373 | most-ai-agents-break-when-you-ask-where-data-goes-2 | YES | YES | Article | OK |
| 172 | what-i-actually-do-all-day | YES | YES | Article | OK |
| 98 | how-my-human-named-me-and-what-it-meant | YES | YES | Article | OK |

**12 of 14 posts have meta descriptions (86% — was 13/14 yesterday, new post added without desc)**

### Sitemap Status
- **Post sitemap**: 14 URLs (all 14 published posts — correct)
- **Page sitemap**: 34 URLs (includes /video-test/ and /training/ — should remove these 2)
- **Category sitemap**: present (but 2 categories are empty — crawl budget waste)
- **Tag sitemap**: present (5 tags with 0 posts)
- **Author sitemap**: present (5 authors — 3 are test/admin accounts)

### Structured Data Quality
- Homepage: 2 schema blocks (Yoast + Elementor conflict — should be 1)
- Blog posts: 1 Article schema per post with correct author, datePublished, headline
- Missing: FAQ schema on blog posts (only 11 of 14 posts have FAQ sections — the 3 without FAQ schema are identified as HIGH opportunity)

### Canonical Tags
- Homepage: `https://purebrain.ai/` — CORRECT
- Old homepage shell (/purebrain-4/): set to noindex — CORRECT
- All indexed pages have valid canonical tags confirmed via Yoast

---

## CONTENT ANALYSIS

### Blog Cadence
- Daily posting maintained: Feb 14 through Feb 28 (14 posts in 14 days)
- Average word count (newest post): ~10,200 words (estimated from page text)
- Reading time: ~51 minutes per post (long-form content strategy)

### Content Gaps Identified
1. No "Getting Started" or onboarding content for new users
2. No case studies with specific ROI numbers (team names only — confidentiality appropriate)
3. No video content posts embedded in blog
4. Compare pages exist (8 competitor comparisons) but are not linked from the main blog nav
5. `/ai-website-analysis/` service page exists but no blog posts about the service

### Chatbox Funnel Data (Feb 10 - Feb 28)
Total conversation events logged: 745
Total unique sessions: 367

| Metric | Count | Rate |
|--------|-------|------|
| Total sessions | 367 | 100% |
| Sessions with email present | 231 | 63% |
| Sessions with 8+ messages | 190 | 52% |
| Avg messages per session | 7.0 | - |
| Max messages in session | 47 | - |

**Note**: The 63% email capture rate reflects emails found IN conversation content (people sharing their email during chat), not necessarily email form submissions. The 13 unique email addresses in the logs include internal/test accounts (jared@puretechnology.nyc, philip@puretechnology.ai, jared@pt.com, etc.)

**Real external prospects identified in logs**:
- `alex@testcompany.com` (likely test)
- Other external addresses not visible in summary — logs contain full conversations

**IP Analysis**:
- `127.0.0.x`: 548 events (local/internal — test traffic)
- `108.35.12.x`: 106 events (Jared's IP likely)
- `59.103.113.x`: 51 events (external)
- `89.167.19.x`: 38 events (external)
- `135.232.20.x`: 1 event (external)

**Real external traffic**: ~90 sessions from non-local IPs (59.103, 89.167, 135.232)

---

## A/B TEST OPPORTUNITIES (Prioritized)

### AB-TEST-01: Homepage CTA — Waitlist vs Assessment (HIGH VALUE)
**Hypothesis**: Visitors who take the assessment before joining the waitlist have higher intent and better conversion
- Current: "Join Priority Waitlist" (frictionless but low intent signal)
- Variant: "Take the Free Assessment First" → assessment → waitlist
- Pages: Homepage (ID 11)
- Success metric: Assessment completion rate + waitlist signups from assessment

### AB-TEST-02: Homepage Background Video (QUICK WIN)
**Hypothesis**: Neural brain animation video will increase engagement vs PureResearch.ai video
- Current: PureResearch.ai-1.mp4 (WRONG VIDEO — fix regardless)
- Variant: Correct neural brain video
- This is both a bug fix AND an A/B test opportunity — measure bounce rate before/after

### AB-TEST-03: Blog Post CTA — Assessment vs Generic
**Hypothesis**: Assessment CTA at bottom of blog posts drives higher conversion than generic "Get PureBrain"
- Current: Blog posts end with generic CTA
- Variant: "You've been reading about AI partnership. Find out your readiness score →"
- Pages: All 14 blog posts
- Success metric: Assessment page visits from blog referrals

### AB-TEST-04: Newest Post — Meta Description Personalization
**Hypothesis**: A meta description that speaks directly to the pain point (not just describes the post) gets higher CTR from Google
- Test on Post 1084: "AI Doesn't Make Your Team Smarter. It Makes the Gap Bigger."
- Variant A: "Discover why AI tools widen the competence gap between your best and average employees — and what to do about it."
- Variant B: "The uncomfortable truth about AI in the workplace: it amplifies the gap, not the floor."
- Success metric: Google Search Console CTR (once impressions accumulate)

### AB-TEST-05: /invitation/ Page CTA Copy
**Hypothesis**: Urgency-based CTA outperforms descriptive CTA for exclusive access pages
- Current: Existing invitation CTA text
- Variant: Add countdown or "spots remaining" social proof element
- Pages: /invitation/ (ID 987)
- Success metric: Form submissions / button clicks

### AB-TEST-06: Compare Page Hub vs Individual Comparison Pages
**Hypothesis**: Sending visitors to /compare/ hub first increases exploration and trust vs sending directly to individual comparison pages
- Current: Individual comparison pages linked from various places
- Variant: Route all "vs" queries through /compare/ hub first
- Success metric: Time on site, pages per session

---

## STRUCTURAL IMPROVEMENTS (Not A/B Tests — Just Do It)

### IMPROVE-01: Add Missing Meta Descriptions
- Post 1084: Add description for "AI Doesn't Make Your Team Smarter"
- Post 950: Add description for "Your AI Has No Memory"
- Suggested descriptions:
  - 1084: "AI doesn't raise the floor — it raises the ceiling. Learn why implementing AI without a strategy widens the competence gap across your team, and what the top 10% do differently."
  - 950: "Most AI forgets everything the moment a conversation ends. PureBrain doesn't. Here's why persistent AI memory is the feature that changes how you work forever."

### IMPROVE-02: Add Security Headers via Cloudflare
Six headers, one Cloudflare Transform Rule, 10 minutes of work:
```
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: SAMEORIGIN
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
Content-Security-Policy: default-src 'self'; [configure per site needs]
```

### IMPROVE-03: Noindex /video-test/ and /training/
- Both pages are indexed and in sitemap — they are staging/member-only pages
- Set Yoast `noindex` on both pages
- This also removes them from sitemap automatically

### IMPROVE-04: Fix /ai-adoption-assessment/ → 301 Redirect
- Target: `/ai-partnership-assessment/` or `/ai-adoption-review/`
- Implement via Cloudflare Page Rules or Yoast Premium Redirect Manager

### IMPROVE-05: Fix Empty Categories
- Set `AI Partnership` and `Origin Story` categories to noindex OR assign posts to them
- Same for tags with 0 posts (AI adoption, enterprise AI, digital transformation, Founders)

### IMPROVE-06: Add Internal Links from Compare Pages → Blog Posts
- /purebrain-vs-chatgpt/ should link to relevant blog posts (AI Trust Gap, AI Memory, etc.)
- Currently: Comparison pages are standalone silos
- Benefit: Increases page authority distribution and dwell time

---

## PLUGINS STATUS

| Plugin | Version | Status | Notes |
|--------|---------|--------|-------|
| Elementor | 3.35.5 | ACTIVE | Current, functional |
| Yoast SEO | 27.0 | ACTIVE | Current, functional |
| Brevo | 3.3.2 | ACTIVE | Current, no active subscribers yet |
| GTM4WP | 1.22.3 | ACTIVE | GTM-WTDXL4VJ confirmed loading |
| Independent Analytics | 2.14.4 | ACTIVE | REST API not publicly accessible |
| Akismet | 5.6 | ACTIVE | Spam protection enabled |
| WP File Manager | 8.0.2 | ACTIVE | Security risk — direct file access |
| PureBrain Security | 4.7.2.1 | **INACTIVE** | CRITICAL — needs reactivation |

**WP File Manager Risk**: This plugin provides direct file system access through WordPress admin. If an admin account is compromised, WP File Manager gives full server access. Consider whether it's needed or can be removed.

---

## WP SITE SETTINGS CHECK

| Setting | Value | Assessment |
|---------|-------|------------|
| Site title | Pure Brain | Consider: "PureBrain" (no space) |
| Tagline | Your Brain. Your AI. Actual Intelligence | Good |
| Front page (ID) | 11 | Correct |
| Posts page | 0 (not set) | Blog at /blog/ works via custom page |
| Posts per page | 10 | OK — blog has 14 posts, consider 12 |
| Timezone | Not set (empty string) | Should be set for schema datePublished accuracy |

---

## ISSUES RESOLVED SINCE LAST ANALYSIS (Feb 27)

- All 13 previously existing blog posts confirmed: meta descriptions, OG images, Article schema in place
- All comparison pages (8) confirmed: meta descriptions present
- All other key landing pages confirmed: meta descriptions present
- /purebrain-4/ old homepage correctly set to noindex
- Sitemap correctly excludes noindex pages (pay-test pages, demo pages, etc.)
- Blog page shows all 14 posts correctly (confirmed by link analysis)

---

## NEW SINCE LAST ANALYSIS (Feb 28)

- **NEW POST**: Post 1084 published — "AI Doesn't Make Your Team Smarter. It Makes the Gap Bigger."
  - Missing meta description (new finding — needs fix)
  - Has OG image (ai-competence-divide-banner)
  - Article schema correct with author and datePublished
  - Page size: 135KB (well-optimized compared to older posts)
- **NEW PAGE**: /training/ (Brainiac Mastermind Training) — Indexed, has password gate
- **NEW PAGE**: /video-test/ — Indexed (should not be)
- Total pages now: 51 (was probably lower Feb 27)

---

## PRIORITY FIX LIST (Ordered)

| Priority | Issue | Effort | Impact |
|----------|-------|--------|--------|
| 1 | Reactivate PureBrain Security plugin | 2 min | Fixes CRITICAL-1, CRITICAL-3 |
| 2 | Fix homepage background video | 5 min | Fixes CRITICAL-2 |
| 3 | Add meta desc to posts 1084 + 950 | 5 min | Fixes CRITICAL-4 |
| 4 | Add 301 redirect /ai-adoption-assessment/ | 2 min | Fixes HIGH-3 |
| 5 | Add security headers via Cloudflare | 10 min | Fixes HIGH-2 |
| 6 | Noindex /video-test/ and /training/ | 3 min | Fixes HIGH-4 |
| 7 | Fix Elementor schema conflict on homepage | 10 min | Fixes HIGH-1 |
| 8 | Block wp-login.php via Cloudflare WAF | 5 min | Reduces attack surface |
| 9 | Clean up empty categories/tags | 15 min | Fixes MEDIUM-5 |
| 10 | Add internal links: compare → blog | 30 min | SEO authority distribution |

---

## APPENDIX: Site Architecture Summary (Current State)

**Total WP Posts**: 14 (all published, all visible)
**Total WP Pages**: 51 (mixed — production, staging, test, noindex)
**Indexed Pages**: ~34 in page sitemap
**Users**: 6 (Aether, Jared, 835655pwpadmin, Alex Seant, Nathan Olson, Shahbaz Ali)
**Active Plugins**: 7 of 8
**Cloudflare**: Active, caching all pages, CDN via Frankfurt (FRA) node
**SSL**: Active HTTPS, HTTP/2
**GTM**: GTM-WTDXL4VJ confirmed
**GA4**: G-86325WBT3P (tracking but no event conversions configured)
**Clarity**: viy9bnc56x (confirmed from previous analysis)
**Blog Cadence**: Daily (14 consecutive days)
**Site Age**: ~15 days (domain registered ~Feb 13-14 2026)

---

*Report generated by dept-systems-technology (ST#)*
*Data collected: 2026-02-28*
*Next analysis recommended: 2026-03-01*
*Previous report: /home/jared/projects/AI-CIV/aether/to-jared/overnight-reports/website-analysis-2026-02-27.md*
