# PureBrain.ai Comprehensive Analytics Report
**Date**: 2026-04-24 (compiled from data through April 16)
**Data Sources**: GA4 (property 525007539), Google Search Console (sc-domain:purebrain.ai), Microsoft Clarity (viy9bnc56x), Internal Logs, Public Search Index
**Method**: GA4/GSC via service account API (`tools/analytics_api.py`), Clarity auth-blocked (no API token), web index analysis

---

## Executive Summary

PureBrain.ai has grown from ~750 sessions/month (March 11) to ~2,900 sessions/month (April 15) -- a **3.9x traffic increase in 5 weeks**. Revenue stands at $10,596 across 61 payments (avg $174). However, the site is flying blind on conversions (zero GA4 conversion events wired), the blog ecosystem is broken (95.5% bounce), and the single biggest SEO asset -- `/age-of-ai-agents-next-18-months/` with 320 search impressions -- captures only 0.3% CTR due to poor meta tags. Fixing 3 things (conversion tracking, meta tags on top pages, WordPress sitemap cleanup) would unlock the majority of available growth.

---

## 1. Traffic Overview

### 1.1 Growth Trajectory (30-Day Snapshots)

| Period | Sessions | Users | Pageviews | Bounce Rate |
|--------|----------|-------|-----------|-------------|
| Feb 10 - Mar 11 | 748 | 533 | 1,330 | 52.5% |
| Feb 14 - Mar 15 | 1,065 | 802 | 1,707 | 58.6% |
| Mar 16 - Apr 15 | **2,902** | **2,225** | **3,657** | **65.2%** |

**Key takeaway**: Sessions nearly 4x'd in 5 weeks. Users 4.2x'd. However, bounce rate climbed from 52.5% to 65.2% -- the new traffic is lower quality than the early core audience. This is expected during a growth phase but needs monitoring.

### 1.2 Traffic Sources (30 Days ending Apr 15)

| Channel | Sessions | % | Users | Bounce | Avg Duration |
|---------|----------|---|-------|--------|--------------|
| Direct | 2,249 | 78% | 1,965 | 67.3% | 1:38 |
| Referral | 260 | 9% | 48 | 45.0% | 7:02 |
| Organic Search | 203 | 7% | 81 | 64.0% | 3:59 |
| Organic Social | 114 | 4% | 79 | 71.9% | 1:33 |
| Unassigned | 76 | 3% | 69 | 98.7% | 0:06 |

**Organic Search has grown from 3% to 7%** (20 sessions in March to 203 in April -- a 10x increase). This is the healthiest growth signal. Referral traffic (7-minute avg sessions) is the highest-quality channel.

**Unassigned traffic (98.7% bounce, 6 seconds)** is confirmed bot/scraper -- should be filtered in GA4.

### 1.3 Top Named Traffic Sources

| Source / Medium | Sessions | Quality Signal |
|-----------------|----------|----------------|
| (direct) / (none) | 2,249 | Brand strength |
| google / organic | 185 | Growing -- 10x vs March |
| statics.teams.cdn.office.net / referral | 85 | Internal (Teams demos) |
| sendibm3.com (Brevo email) | 53 | Email campaigns working |
| linkedin / jared (custom UTM) | 48 | 79% bounce -- landing page problem |
| linkedin.com / referral (organic) | 35 | 46% bounce -- much better |
| blog / cta | 28 | **96% bounce -- BROKEN** |

### 1.4 Device Breakdown

| Device | Sessions | Bounce | Duration |
|--------|----------|--------|----------|
| Desktop | 2,403 (83%) | 64.5% | -- |
| Mobile | 470 (16%) | 72.6% | -- |
| Tablet | 8 | -- | -- |

Mobile bounce is 8 points higher than desktop. However, GSC shows mobile CTR is 2.5x desktop (7.58% vs 3.08%) -- mobile searchers WANT to click but the mobile landing experience fails them.

### 1.5 Geography

| Country | Sessions | Users | Notes |
|---------|----------|-------|-------|
| United States | 2,129 | -- | Core market (73%) |
| Canada | 213 | -- | Strong secondary |
| Pakistan | 124 | -- | Likely bot/scraper (low user:session) |
| Germany | 82 | -- | Down from 150 in March (bot burst subsided) |
| Singapore | 75 | -- | New -- investigate |

---

## 2. Top Performing Content

### 2.1 Top Pages by Sessions (30 Days)

| Page | Sessions | Bounce | Duration | Verdict |
|------|----------|--------|----------|---------|
| `/` (homepage) | 1,837 | 67.6% | 0:57 | Workhorse but shallow |
| `/investment-opportunity` | 165 | 49.7% | **8:20** | High-intent converts |
| `/lpm-video-test` | 81 | 96.3% | 0:12 | Test page -- ignore |
| `/refer` | 70 | 48.6% | **13:22** | Best engagement on site |
| `/brainiac-mastermind-training` | 63 | 61.9% | 2:39 | Training content works |
| `/investor-avatar` | 44 | **29.5%** | **15:14** | Best page on entire site |
| `/blog` | 22 | **95.5%** | **0:03** | BROKEN -- instant bounce |
| `/invitation` | 22 | 27.3% | 6:46 | Strong conversion intent |
| `/ai-tool-stack-calculator` | 19 | 73.7% | 0:12 | Needs work |

### 2.2 Star Performers (by Engagement)

1. **`/investor-avatar`** -- 29.5% bounce, 15:14 avg session. The Claude API + Chy persona conversational page is the best-performing landing experience on the entire site. Users stay and engage.
2. **`/refer`** -- 48.6% bounce, 13:22 avg session. Referral portal drives deep engagement.
3. **`/invitation`** -- 27.3% bounce, 6:46 avg session. People who reach this page are genuinely evaluating.
4. **`/investment-opportunity`** -- 49.7% bounce, 8:20 avg session. Investor content converts attention.

### 2.3 Problem Pages

1. **`/blog` index** -- 95.5% bounce, 3-second avg session. Users land and immediately leave. The CTA chain from blog is broken.
2. **`blog / cta` source** -- 28 sessions, 96% bounce. Whatever the blog CTAs link to is failing.
3. **`/lpm-video-test`** -- 81 sessions, 96.3% bounce. Test page receiving real traffic -- should redirect or clean up.
4. **`/pay-test-awakened`** -- 25 sessions, 96% bounce. Old payment test page still live.

---

## 3. Search Visibility (Google Search Console - 90 Days)

### 3.1 Overall Search Performance

| Metric | Value | Trend vs March |
|--------|-------|----------------|
| Total Clicks | 120 | Up from ~55 (+118%) |
| Total Impressions | 2,988 | Up from ~1,650 (+81%) |
| Average CTR | 4.01% | Up from 3.3% |
| Average Position | 8.0 | Improved from ~5-6 to 8.0 (wider query set = higher avg) |
| Indexed Pages (reporting) | 0/104 | Artifact -- pages ARE ranking |

### 3.2 Top Search Queries

| Query | Clicks | Impressions | CTR | Position |
|-------|--------|-------------|-----|----------|
| purebrain | 43 | 129 | 33.3% | 3.1 |
| pure brain | 7 | 111 | 6.3% | 5.9 |
| *all other queries combined* | 70 | 2,748 | 2.5% | -- |

Brand queries ("purebrain" + "pure brain") account for 42% of all clicks. Outside brand, the site is struggling to convert impressions to clicks.

### 3.3 Top Pages by Search Impressions

| Page | Clicks | Impressions | CTR | Position | Opportunity |
|------|--------|-------------|-----|----------|-------------|
| `/` (homepage) | 108 | 688 | 15.7% | 3.7 | Solid |
| `/ai-tool-stack-calculator/` | 1 | **499** | **0.2%** | 15.2 | PAGE 2 -- needs to reach page 1 |
| `/age-of-ai-agents-next-18-months/` | 1 | **320** | **0.3%** | 5.7 | **#1 PRIORITY FIX** |
| `app.purebrain.ai` | 3 | 112 | 2.7% | 4.4 | App subdomain leaking |
| `/portfolio/` | 1 | 90 | 1.1% | 5.2 | Meta needs work |
| `/partnered-how-this-levels-you-up/` | 1 | 54 | 1.9% | 6.5 | Meta needs work |
| `/invitation/` | 0 | 46 | 0% | 4.8 | Position 5 with ZERO clicks |

### 3.4 The Big SEO Fires

**Fire #1: `/age-of-ai-agents-next-18-months/`**
- 320 impressions at position 5.7 with 0.3% CTR
- At position 5.7, expected CTR should be ~8-10%
- Fixing title + meta description could yield **25-30 additional clicks/month** from this single URL
- This has been flagged in every report since March 11. Still not fixed.

**Fire #2: `/ai-tool-stack-calculator/`**
- 499 impressions (highest on entire site!) but position 15.2 (page 2)
- 1 click in 90 days
- Breaking into top 10 would dramatically increase clicks
- Needs content expansion, schema markup, internal linking

**Fire #3: WordPress Sitemap Ghosts**
- 4 old WordPress sitemaps (www.purebrain.ai/category-, post-, sitemap_index, page-sitemap) still submitted in GSC
- All erroring
- Site is on CF Pages, not WordPress
- These create indexing ambiguity and waste crawl budget

### 3.5 Search by Device

| Device | Clicks | Impressions | CTR |
|--------|--------|-------------|-----|
| Desktop | 73 | 2,367 | 3.08% |
| Mobile | 46 | 607 | **7.58%** |
| Tablet | 1 | 14 | 7.14% |

Mobile CTR is **2.5x desktop**. Mobile searchers are more ready to click. This suggests our meta titles/descriptions work better on mobile SERP layouts, or mobile searchers have higher brand intent.

### 3.6 Google Index Status

- **Site is on Google** -- confirmed 7+ pages indexed and appearing in search results
- `purebrain.ai/sitemap.xml` -- 104 URLs submitted, reporting 0 indexed (reporting artifact for CF Pages)
- 21 warnings on the main sitemap need investigation
- Blog posts: only 1 blog result appears in `site:purebrain.ai/blog` search -- most blog content is NOT indexed yet
- **Total indexed pages visible in public search**: ~7-10 URLs across all `site:purebrain.ai` queries

---

## 4. User Behavior Insights

### 4.1 Conversion Funnel (GA4 Events)

| Event | Count | Users | Notes |
|-------|-------|-------|-------|
| page_view | 3,657 | ~2,225 | Total pageviews |
| scroll | 903 | 324 | Only 15% of users scroll |
| form_start | 64 | 43 | 43 unique users start forms |
| click | 42 | 29 | Outbound/CTA clicks |
| form_submit | **0** | **0** | **NOT WIRED** |
| purchase | **0** | **0** | **NOT WIRED** |
| sign_up | **0** | **0** | **NOT WIRED** |

**CRITICAL**: Zero conversion events are configured in GA4. There is no visibility into form completions, payment initiations, portal signups, or seed sends. This is the single biggest analytics gap -- the entire funnel below "form start" is invisible.

### 4.2 Session Quality by Source

| Source | Avg Session | Bounce | Quality Score |
|--------|-------------|--------|---------------|
| Referral traffic | 7:02 | 45.0% | Excellent |
| Organic Search | 3:59 | 64.0% | Good |
| Direct | 1:38 | 67.3% | Moderate |
| Organic Social | 1:33 | 71.9% | Poor |
| Unassigned | 0:06 | 98.7% | Bot traffic |

### 4.3 Internal Log Insights (Apr 16 snapshot)

- 3,869 total chat sessions logged
- 96.2% from localhost/dev IPs (internal testing)
- ~23 real external sessions from ~3 unique external IPs
- 61 payments totaling $10,596 (avg $173.70)
- Onboarding funnel: `flowCompleted` field never set in logs -- data quality issue

### 4.4 Site Performance

| Page | TTFB | Size | Issue |
|------|------|------|-------|
| Homepage `/` | 171ms | 643KB | **76% is inline JS+CSS** (not cacheable) |
| Blog `/blog/` | 208ms | 70KB | Good |
| Training | 150ms | 148KB | Good |
| Referral `/refer/` | 247ms | 79KB | Good |

Homepage at 643KB raw HTML is a performance concern. 249KB inline JS + 238KB inline CSS cannot be separately cached by browsers and must be re-downloaded every page load. Mobile devices parse ~487KB of JS+CSS before showing content.

---

## 5. Microsoft Clarity

### Status: AUTH-BLOCKED (No API Token)

**Project ID**: viy9bnc56x (confirmed active in site HTML via GTM-WTDXL4VJ)

**What Clarity tracks** (collecting data but we cannot access it):
- Heatmaps (where users click on each page)
- Session recordings (watch real user behavior)
- Rage clicks (frustrated repeated clicking)
- Dead clicks (clicks on non-interactive elements)
- Quick-back rate (users who immediately return to Google)
- Scroll depth per page
- JavaScript errors

**To unblock**: Clarity project settings -> Data Export -> Generate new API token -> Add to `.env` as `CLARITY_API_TOKEN=bearer_token_here`. The API endpoint is `https://www.clarity.ms/export-data/api/v1/project-live-insights` with JWT Bearer auth. Supports up to 3 dimensions (Browser, Device, Country, Source, URL, etc.) and returns Traffic, Engagement Time, Scroll Depth, Rage Clicks, Dead Clicks, Quick-backs, Script Errors.

**Priority pages to review manually in Clarity** (login at clarity.microsoft.com):
1. Homepage heatmap -- where do 1,837 monthly visitors click?
2. `/blog` recordings -- why 95.5% bounce in 3 seconds?
3. `/age-of-ai-agents-next-18-months/` -- do organic visitors scroll or immediately back out?
4. Mobile sessions on homepage -- is the hero CTA reachable?

---

## 6. Critical Issues (robots.txt)

**Discovered Apr 16**: Cloudflare's managed robots.txt section BLOCKS AI crawlers:
- GPTBot (ChatGPT browse/citations)
- ClaudeBot (Anthropic search)
- Google-Extended (AI Overviews)

A custom section below tries to ALLOW these same crawlers, but the contradiction means different crawlers interpret it differently. Some may be fully blocked.

**Impact**: PureBrain likely has zero visibility in AI-powered search (Perplexity, ChatGPT, Google AI Overviews). For a company selling AI partnerships, being invisible to AI search engines is existential.

**Fix**: Disable CF AI bot blocking in Cloudflare dashboard. Manage all crawler rules via custom robots.txt only.

---

## 7. Trend Analysis: March vs April

| Metric | March (30d) | April (30d) | Change |
|--------|-------------|-------------|--------|
| Sessions | 748 | 2,902 | **+288%** |
| Users | 533 | 2,225 | **+317%** |
| Pageviews | 1,330 | 3,657 | **+175%** |
| Organic Search Sessions | 20 | 203 | **+915%** |
| GSC Clicks (90d) | ~55 | 120 | **+118%** |
| GSC Impressions (90d) | ~1,650 | 2,988 | **+81%** |
| Bounce Rate | 52.5% | 65.2% | +12.7 pts (worse) |
| Revenue | -- | $10,596 | 61 payments |

The growth trajectory is strong. Organic search is the standout channel with 10x growth. The bounce rate increase is the primary concern -- it suggests either bot traffic inflation or lower-quality acquisition channels growing faster than high-quality ones.

---

## 8. Top 5 Actionable Recommendations

### Recommendation 1: Wire GA4 Conversion Events (HIGHEST PRIORITY)
**Impact**: Unlocks entire funnel visibility
**Effort**: 2-4 hours (ST# ticket)
**What to wire**:
- `form_submit` (all forms)
- `payment_initiated` (PayPal/Stripe click)
- `payment_completed` (webhook confirmation)
- `portal_signup` (new account creation)
- `seed_sent` (email seed dispatch)
- `magic_link_clicked` (onboarding flow)

**Without this**: Every other optimization is guesswork. We can see traffic and engagement but not revenue attribution.

### Recommendation 2: Fix `/age-of-ai-agents-next-18-months/` Title & Meta
**Impact**: Est. 25-30 additional organic clicks/month
**Effort**: 15 minutes
**Current**: 320 impressions, position 5.7, 0.3% CTR
**Target**: 8-10% CTR at position 5.7 = 25-32 clicks/month
**Suggested title**: "AI Agents in 2026: What the Next 18 Months Will Look Like for Business"
**Suggested meta**: "The shift from AI chatbots to AI agents is already underway. Here's what businesses that adopt now will look like in 18 months -- and what happens to those that don't."

*This has been the #1 recommendation in every analytics report since March 11. Still not executed.*

### Recommendation 3: Remove WordPress Sitemap Ghosts from GSC
**Impact**: Cleaner indexing signals, faster page discovery
**Effort**: 10 minutes
**Action**: GSC -> Sitemaps -> Remove these 4 entries:
- `www.purebrain.ai/category-sitemap.xml`
- `www.purebrain.ai/post-sitemap.xml`
- `www.purebrain.ai/sitemap_index.xml`
- `www.purebrain.ai/page-sitemap.xml`
Keep only: `purebrain.ai/sitemap.xml`

Also: 301 redirect `www.purebrain.ai` to `purebrain.ai` at the server level.

### Recommendation 4: Fix robots.txt AI Crawler Contradiction
**Impact**: Enables AI search engine discovery (Perplexity, ChatGPT, Google AI Overviews)
**Effort**: 5 minutes in Cloudflare dashboard
**Action**: Cloudflare Dashboard -> purebrain.ai -> AI -> Turn OFF "Block AI Crawlers" setting. Then manage all bot rules in the custom robots.txt section only.
**Why**: An AI partnership company that's invisible to AI search engines is a contradiction that costs real traffic.

### Recommendation 5: Diagnose and Fix Blog Bounce (95.5%)
**Impact**: Unlocks blog as acquisition channel (currently net-negative)
**Effort**: 1-2 hours investigation + fix
**Problem**: `/blog` index page bounces at 95.5% with 3-second avg session. `blog / cta` source bounces at 96%.
**Investigation needed**:
- What URL do blog CTAs point to?
- Is the blog index loading correctly or showing an error?
- Does the blog render properly on mobile?
**Benchmark**: In March, `/blog` had 79.2% engagement rate (20.8% bounce). Something broke between March and April.

---

## Appendix A: What's Working Well

1. **Investor pages are exceptional**. `/investor-avatar` (29.5% bounce, 15-min sessions) is the best-performing page on the entire site. The conversational Claude API format holds attention.
2. **Brand search converts**. "purebrain" query: 33.3% CTR at position 3.1. People searching for the brand click.
3. **Organic search is growing 10x**. From 20 sessions in March to 203 in April. The SEO foundation is building.
4. **Homepage CTR is strong**. 15.7% CTR from search at position 3.7 -- well above industry average.
5. **Referral traffic is high-quality**. 7-minute avg sessions, 45% bounce -- best engagement of any channel.
6. **Revenue is happening**. 61 payments, $10,596, avg $174 -- proving product-market fit.
7. **Site is fast**. Sub-300ms TTFB on all pages thanks to Cloudflare edge.

## Appendix B: Access & Credentials Reference

| Platform | Access Method | Status |
|----------|---------------|--------|
| GA4 (property 525007539) | Service account API | Working |
| GSC (sc-domain:purebrain.ai) | Service account API | Working |
| Clarity (viy9bnc56x) | Bearer token API | **BLOCKED -- no token** |
| GTM | Container GTM-WTDXL4VJ | Active on site |
| GA4 Measurement ID | G-86325WBT3P | Active via GTM |

**API module**: `tools/analytics_api.py` -- production-ready, import `ga4_report`, `gsc_query`, `get_ga4_summary`, `get_gsc_summary`
**Service account**: `.credentials/google-drive-service-account.json` (aether-drive-access@aether-integration.iam.gserviceaccount.com)

## Appendix C: Recommended Next Report

Pull fresh GA4 + GSC data using `analytics_api.py` to get April 16-24 numbers. Once Clarity token is added to `.env`, include Clarity metrics. Schedule weekly automated pulls to track the 5 recommendations above.

---

*Compiled by web-researcher from GA4 API data (Apr 15), GSC API data (Apr 15), site performance audit (Apr 16), public search index analysis (Apr 23), and historical reports (Mar 11 - Apr 16). Microsoft Clarity data unavailable due to missing API token.*
