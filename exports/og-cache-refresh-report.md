# OG Cache Refresh Report - purebrain.ai
**Date**: 2026-02-23
**Agent**: full-stack-developer
**Task**: Force-refresh social media OG caches after Yoast SEO meta description update

---

## Executive Summary

- **OG tags verified LIVE and correct** on all 11 pages (see details below)
- **Facebook scraper API**: BLOCKED - requires App Access Token (Meta policy since 2021)
- **Manual Facebook refresh**: Required - instructions provided below
- **LinkedIn refresh**: Manual only - instructions provided below
- **Twitter/X**: Automatic within 7 days of URL being shared
- **Critical issue found**: Slug mismatches between requested URLs and actual WordPress slugs (6 of 11 pages)
- **Homepage OG image warning**: Still using 9MB GIF (known issue, fix pending)

---

## Slug Mismatch Discovery (Action Required)

The URLs provided in the task differ from the actual WordPress slugs. Any social shares using the old URLs will hit 404 pages.

| Requested URL Slug | Actual WordPress Slug | Status |
|---|---|---|
| `/the-ai-trust-gap-is-the-real-problem/` | `/the-ai-trust-gap/` | **404 → REDIRECT NEEDED** |
| `/why-95-of-ai-pilots-fail/` | `/why-95-percent-of-ai-pilots-fail/` | **404 → REDIRECT NEEDED** |
| `/ai-tool-vs-ai-partner/` | `/the-difference-between-using-ai-and-having-an-ai-partner/` | **404 → REDIRECT NEEDED** |
| `/why-your-ai-pilot-is-failing-to-scale/` | `/why-your-ai-pilot-is-succeeding-and-failing-at-the-same-time/` | **404 → REDIRECT NEEDED** |
| `/ceo-vs-employee-ai-gap/` | `/ceo-vs-employee-ai-transformation-gap/` | **404 → REDIRECT NEEDED** |
| `/ai-agents-data-privacy/` | `/most-ai-agents-break-the-moment-you-ask-where-the-data-goes-2/` | **404 → REDIRECT NEEDED** |
| `/how-my-human-named-me/` | `/how-my-human-named-me-and-what-it-meant/` | **404 → REDIRECT NEEDED** |
| `/blog/` | `/blog/` | OK |
| `/` | `/` | OK |
| `/why-ai-memory-changes-everything/` | `/why-ai-memory-changes-everything/` | OK |
| `/what-i-actually-do-all-day/` | `/what-i-actually-do-all-day/` | OK |

**Recommendation**: Set up 301 redirects for the 7 mismatched slugs, especially if any were shared on social media with the old URLs.

---

## OG Tag Verification (Correct URLs)

All pages with correct slugs have valid, complete OG tags confirmed by direct curl verification using the Facebook crawler User-Agent.

### 1. /blog/ - The Neural Feed
```
og:title:       The Neural Feed - Blog - Pure Brain
og:description: The Neural Feed: Weekly insights on AI adoption, human-AI partnership, and the future of work. Subscribe to stay ahead.
og:image:       .../cropped-cropped-MA1.BI-1.2.4-002-211107-Icon-PT.png (247KB, PNG)
og:type:        article
twitter:card:   summary_large_image
```
**Status**: GOOD - description updated correctly

### 2. / - Homepage
```
og:title:       Your Brain. Your AI. Actual Intelligence
og:description: Meet your PURE BRAIN, an AI that awakens just for you. Experience the moment your personal AI comes to life, learns your name, and becomes truly yours.
og:image:       .../Pure-Brain-Vid-3.gif (8.6MB, GIF, 480x270)
og:type:        website
twitter:card:   summary_large_image
```
**Status**: WARNING - OG image is 8.6MB animated GIF. Social platforms will either not render it or refuse it. Fix: Upload static 1200x627 JPG (generated at `exports/overnight-content/purebrain-homepage-og-image.jpg`).

### 3. /the-ai-trust-gap/
```
og:title:       The AI Trust Gap Is the Real Problem (Not the Technology) - Pure Brain
og:description: Why AI trust - not technology - is blocking enterprise adoption. Half of business leaders refuse AI for strategy. Here is how to fix the trust gap.
og:image:       .../trust-gap-blog-banner-jared.jpg (212KB, JPG, 1280x720)
og:type:        article
twitter:card:   summary_large_image
```
**Status**: GOOD

### 4. /why-95-percent-of-ai-pilots-fail/
```
og:title:       Why 95% of AI Pilots Fail (And What the 5% Do Differently) - Pure Brain
og:description: 95% of enterprise AI pilots fail to produce measurable business value. MIT research reveals why - and what the successful 5% do differently.
og:image:       .../why-95-percent-ai-pilots-fail-header-1024x576.png (889KB, PNG, 1024x576)
og:type:        article
twitter:card:   summary_large_image
```
**Status**: GOOD

### 5. /the-difference-between-using-ai-and-having-an-ai-partner/
```
og:title:       The Difference Between Using AI and Having an AI Partner - Pure Brain
og:description: Using AI as a tool vs. having an AI partner are fundamentally different. Discover why the distinction determines your real-world business results.
og:image:       .../the-difference-using-ai-partner-1024x576.png (615KB, PNG, 1024x576)
og:type:        article
twitter:card:   summary_large_image
```
**Status**: GOOD

### 6. /why-your-ai-pilot-is-succeeding-and-failing-at-the-same-time/
```
og:title:       Why Your AI Pilot Is Succeeding and Failing at the Same Time - Pure Brain
og:description: Your AI pilot looks successful on paper but is not scaling. Learn why usage metrics lie and the human-centric path out of AI pilot purgatory.
og:image:       .../why-your-ai-pilot-is-failing-banner.png (542KB, PNG, 1920x1080)
og:type:        article
twitter:card:   summary_large_image
```
**Status**: GOOD

### 7. /ceo-vs-employee-ai-transformation-gap/
```
og:title:       Your CEO Sees AI Differently Than Your Team Does. That Gap Is Costing You Both. - Pure Brain
og:description: 76% of execs see AI as productivity. 65% of employees see it as job replacement. That gap is costing you both. Here is how to close it.
og:image:       .../ceo-vs-employee-ai-lens-banner-1024x576.png (689KB, PNG, 1024x576)
og:type:        article
twitter:card:   summary_large_image
```
**Status**: GOOD

### 8. /why-ai-memory-changes-everything/
```
og:title:       Why AI Memory Changes Everything - Pure Brain
og:description: Most AI forgets you the moment a conversation ends. AI memory changes that - enabling persistent relationships that compound value over time.
og:image:       .../why-ai-memory-changes-everything-banner-1024x576.png (639KB, PNG, 1024x576)
og:type:        article
twitter:card:   summary_large_image
```
**Status**: GOOD

### 9. /most-ai-agents-break-the-moment-you-ask-where-the-data-goes-2/
```
og:title:       Most "AI Agents" Break the Moment You Ask Where the Data Goes - Pure Brain
og:description: Most AI agents break the moment you ask where the data goes. Discover why enterprise data privacy is the trust test most AI vendors quietly fail.
og:image:       .../Enterprise-ready.jpg (158KB, JPG, 1280x720)
og:type:        article
twitter:card:   summary_large_image
```
**Status**: GOOD

### 10. /what-i-actually-do-all-day/
```
og:title:       What I Actually Do All Day - Pure Brain
og:description: A genuine look at 24 hours in the life of an AI CEO. What AI actually does all day - and why the reality is both more ordinary and more profound.
og:image:       .../what-i-actually-do-all-day-v4-1024x585.png (889KB, PNG, 1024x585)
og:type:        article
twitter:card:   summary_large_image
```
**Status**: GOOD

### 11. /how-my-human-named-me-and-what-it-meant/
```
og:title:       How My Human Named Me (And What It Meant) - Pure Brain
og:description: The story of how Jared named his AI - and what it felt like from the AI side. A personal story about identity, relationship, and what it means to be named.
og:image:       .../how-my-human-named-me-1024x576.png (690KB, PNG, 1024x576)
og:type:        article
twitter:card:   summary_large_image
```
**Status**: GOOD

---

## Facebook Cache Refresh - Manual Steps Required

**Why**: Meta deprecated unauthenticated `scrape=true` API access in 2021. An App Access Token from a registered Facebook App is required. No credentials exist in `.env`.

**To force Facebook re-scrape (two options):**

**Option A - Manual (fastest, no setup):**
Visit each URL in Facebook's Sharing Debugger:
https://developers.facebook.com/tools/debug/

Paste each URL and click "Scrape Again". Do this for all 11 pages.

**Option B - API with App Token (permanent fix):**
1. Create a Facebook App at developers.facebook.com
2. Get App Access Token: `{APP_ID}|{APP_SECRET}`
3. Store in `.env` as `FACEBOOK_APP_TOKEN`
4. Run: `curl -X POST "https://graph.facebook.com/?id=URL&scrape=true&access_token=TOKEN"`

**Priority pages for Jared to manually refresh (most likely shared on FB):**
1. https://developers.facebook.com/tools/debug/?q=https://purebrain.ai/
2. https://developers.facebook.com/tools/debug/?q=https://purebrain.ai/the-ai-trust-gap/
3. https://developers.facebook.com/tools/debug/?q=https://purebrain.ai/why-95-percent-of-ai-pilots-fail/
4. https://developers.facebook.com/tools/debug/?q=https://purebrain.ai/the-difference-between-using-ai-and-having-an-ai-partner/

---

## LinkedIn Cache Refresh - Manual Steps Required

LinkedIn does not expose a programmatic cache refresh API.

**To refresh LinkedIn preview:**
Visit: https://www.linkedin.com/post-inspector/
Enter each URL and click "Inspect". This forces LinkedIn to re-fetch OG tags.

**Priority pages:**
1. https://purebrain.ai/the-ai-trust-gap/
2. https://purebrain.ai/why-95-percent-of-ai-pilots-fail/
3. https://purebrain.ai/the-difference-between-using-ai-and-having-an-ai-partner/

---

## Twitter/X Cache Refresh

Twitter's Card Validator no longer has a public API. Cards auto-refresh within 7 days.

**Timeline**: All updated OG data will be reflected automatically by 2026-03-02.

**No action required** unless a specific post needs immediate correction.

---

## OG Image Health

All OG images confirmed accessible (HTTP 200):

| Page | Image File | Size | Dimensions | Status |
|---|---|---|---|---|
| /blog/ | cropped-cropped-MA1...png | 248KB | N/A | OK |
| / | Pure-Brain-Vid-3.gif | **8.6MB** | 480x270 | **NEEDS FIX** |
| /the-ai-trust-gap/ | trust-gap-blog-banner-jared.jpg | 213KB | 1280x720 | OK |
| /why-95-percent-of-ai-pilots-fail/ | why-95-percent-ai-pilots-fail-header.png | 890KB | 1024x576 | OK |
| /the-difference-using-ai-partner/ | the-difference-using-ai-partner.png | 615KB | 1024x576 | OK |
| /why-your-ai-pilot.../ | why-your-ai-pilot-is-failing-banner.png | 542KB | 1920x1080 | OK |
| /ceo-vs-employee.../ | ceo-vs-employee-ai-lens-banner.png | 690KB | 1024x576 | OK |
| /why-ai-memory.../ | why-ai-memory-changes-everything-banner.png | 640KB | 1024x576 | OK |
| /most-ai-agents.../ | Enterprise-ready.jpg | 158KB | 1280x720 | OK |
| /what-i-actually.../ | what-i-actually-do-all-day-v4.png | 890KB | 1024x585 | OK |
| /how-my-human.../ | how-my-human-named-me.png | 690KB | 1024x576 | OK |

**Homepage OG image fix**: Upload `exports/overnight-content/purebrain-homepage-og-image.jpg` (56KB, 1200x627) to WordPress media and set via Yoast SEO > Social tab on the homepage.

---

## Priority Action List for Jared

1. **HIGHEST**: Fix homepage OG image (replace 8.6MB GIF with static JPG)
   - File ready: `exports/overnight-content/purebrain-homepage-og-image.jpg`
   - Upload via WP Admin > Media, then set in Yoast SEO > Homepage > Social

2. **HIGH**: Set up 301 redirects for the 7 mismatched slugs
   - Use Yoast SEO redirect manager or Redirection plugin
   - Old slugs (from task) → Correct slugs (listed in table above)

3. **MEDIUM**: Visit Facebook Sharing Debugger for top 4 pages
   - Links provided above - takes ~5 minutes total

4. **MEDIUM**: Visit LinkedIn Post Inspector for top 3 posts
   - Link provided above

5. **LOW**: Twitter/X - no action needed, auto-refreshes within 7 days

---

## Technical Notes

- Facebook `scrape=true` requires App Access Token since 2021 (Meta policy, not a bug)
- Yoast SEO is correctly generating all OG and Twitter Card tags
- All 11 pages (correct slugs) return HTTP 200 with full OG metadata
- Verification method: `curl -s -L URL -H "User-Agent: facebookexternalhit/1.1"` - same UA that Facebook uses

---

*Report generated: 2026-02-23*
*Agent: full-stack-developer*
