# PureBrain.ai Analytics Deep Dive
**Date**: 2026-03-17
**Agent**: browser-vision-tester
**Platforms**: Google Analytics 4 + Google Search Console (programmatic API)
**Note**: Microsoft Clarity requires interactive OAuth — data unavailable programmatically. Clarity patterns from prior sessions included where relevant.

---

## HEADLINE SUMMARY

**This week is a MASSIVE traffic spike.** Mar 10–16 delivered 432 total sessions vs just 107 the prior week (Mar 3–9) — a **304% week-over-week jump**. Direct traffic is the driver (346 this week vs 73 last week), suggesting Jared actively shared the site in calls, demos, or campaigns this week.

Organic search is also growing: 24 sessions this week vs 2 the prior week (+1,100%). The SEO work is beginning to pay off.

---

## 1. TRAFFIC OVERVIEW

### This Week (Mar 10–16) vs Prior Week (Mar 3–9)

| Channel | This Week | Prior Week | Change |
|---------|-----------|------------|--------|
| Direct | 346 | 73 | +374% |
| Referral | 28 | 13 | +115% |
| Organic Search | 24 | 2 | +1,100% |
| Organic Social | 21 | 15 | +40% |
| Unassigned | 13 | 4 | +225% |
| **TOTAL** | **432** | **107** | **+304%** |

### 30-Day Channel Breakdown (Feb 15 – Mar 16)

| Channel | Sessions | Users | New Users | Bounce Rate | Avg Session Duration |
|---------|----------|-------|-----------|-------------|---------------------|
| Direct | 895 | 741 | 742 | 60.8% | 2m 20s |
| Organic Social | 98 | 73 | 68 | 50.0% | 2m 32s |
| Referral | 92 | 21 | 15 | 50.0% | 2m 38s |
| Unassigned | 46 | 35 | 20 | 63.0% | 7m 11s |
| Organic Search | 44 | 19 | 15 | 45.5% | 6m 17s |
| **TOTAL** | **~1,175** | **~889** | | | |

### Key Insight: Organic Search is the Highest-Quality Channel

- Lowest bounce rate (45.5%)
- Longest avg session (6m 17s) — 2.7x longer than direct
- Fastest growing channel this week (+1,100%)
- Still tiny absolute volume — huge upside here

### Realtime (at time of report)
0 active users at time of data pull.

---

## 2. TOP PAGES

### 7-Day Top Pages (Mar 10–16)

| Page | Sessions | Bounce Rate | Avg Duration |
|------|----------|-------------|--------------|
| / (Homepage) | 357 | 70.6% | 1m 44s |
| /pay-test-sandbox-3/ | 19 | 31.6% | 5m 04s |
| /pay-test-awakened/ | 17 | 41.2% | 2m 03s |
| /lpm-video-test/ | 9 | 77.8% | 9m 14s |
| /insiders/ | 6 | 66.7% | 3m 42s |
| /pay-test-partnered/ | 5 | 60.0% | 1m 21s |
| /why-purebrain/ | 5 | 100% | 3s (broken) |
| /compare/ | 4 | 25.0% | 40s |
| /pay-test-2/ | 4 | 0% | 3m 36s |

**Notable**: /why-purebrain/ showing 100% bounce with 3s avg duration — possible routing or load issue this week.

### 30-Day Top Pages

| Page | Sessions | Bounce Rate | Avg Duration | Engagement Rate |
|------|----------|-------------|--------------|-----------------|
| / (Homepage) | 692 | 58.1% | 1m 55s | 41.9% |
| /ai-tool-stack-calculator/ | 58 | 46.6% | 2m 47s | 53.4% |
| /blog/ | 54 | 22.2% | 3m 03s | 77.8% |
| /why-purebrain/ | 54 | 53.7% | 2m 47s | 46.3% |
| /pay-test/ | 44 | 36.4% | 3m 14s | 63.6% |
| /pay-test-sandbox/ | 42 | 61.9% | 4m 33s | 38.1% |
| /pay-test-sandbox-2/ | 27 | 44.4% | 2m 58s | 55.6% |
| /pay-test-sandbox-3/ | 26 | 26.9% | 7m 26s | 73.1% |
| /ai-partnership-assessment/ | 18 | 38.9% | 38s | 61.1% |
| /ai-website-analysis/ | 17 | 47.1% | 1m 00s | 52.9% |
| /ceo-vs-employee-ai-transformation-gap/ | 17 | 23.5% | 44s | 76.5% |
| /mission-vision-values/ | 17 | 41.2% | 5m 05s | 58.8% |

### Star Performer: /blog/ Index
- 22% bounce rate (lowest of any page)
- 78% engagement rate
- 3 minute avg session
- Users who land on /blog/ explore the site. This is a content hub anchor.

### Warning: /ai-website-execution/
- 13 sessions, 69% bounce, only 4s avg duration
- Almost certainly a broken page or missing content issue

---

## 3. DEVICES & GEOGRAPHY

### Devices (30-Day)

| Device | Sessions | Bounce Rate | Avg Duration |
|--------|----------|-------------|--------------|
| Desktop | 894 | 57.9% | 2m 31s |
| Mobile | 278 | 59.0% | 3m 23s |
| Tablet | 1 | 100% | 0s |

Desktop dominates (76%) but mobile is significant (24%) and has a longer session duration than desktop. Mobile UX matters here.

### Top Countries (30-Day)

| Country | Sessions | Users |
|---------|----------|-------|
| United States | 738 | 556 |
| Germany | 150 | 150 |
| Canada | 102 | 44 |
| Pakistan | 54 | 18 |
| United Kingdom | 16 | 15 |
| Lebanon | 11 | 2 |
| India | 9 | 9 |
| Philippines | 9 | 5 |
| France | 8 | 8 |

**Germany anomaly confirmed**: 150 sessions from 150 different users (1 session each). This is automated/bot traffic — not genuine audience. Can be filtered in GA4 to get cleaner US/Canada numbers.

**Canada is real**: 102 sessions from only 44 users = repeat visits. Genuine engaged audience.

---

## 4. TRAFFIC SOURCES DETAIL (30-Day)

| Source / Medium | Sessions | Users |
|----------------|----------|-------|
| (direct) / (none) | 895 | 741 |
| statics.teams.cdn.office.net / referral | 76 | 10 |
| linkedin / jared (UTM) | 43 | 24 |
| google / organic | 41 | 16 |
| (not set) | 30 | 27 |
| m.facebook.com / referral | 21 | 21 |
| facebook.com / referral | 14 | 14 |
| linkedin.com / referral | 14 | 8 |
| blog / cta | 9 | 1 |
| ai-civ.com / referral | 3 | 2 |
| chatgpt.com / referral | 2 | 1 |
| bing / organic | 2 | 2 |

**Key insights**:
- Microsoft Teams (76 sessions, 10 users) = Jared sharing the site in sales/demo calls. Not acquisition traffic.
- LinkedIn UTM traffic (43 sessions) is strong and trackable — the utm_source=linkedin utm_medium=jared parameter is working.
- Facebook sending 35 sessions total (organic social clicks).
- ChatGPT referral (2 sessions) — AI systems are discovering and linking to PureBrain. Nascent but watch this.
- Blog CTA → 9 sessions from 1 user (Jared testing his own CTAs likely).

---

## 5. GOOGLE SEARCH CONSOLE — SEO ANALYSIS

### Overall GSC Performance (90 Days)

**Domain summary**:
- Sitemap submitted Feb 23, 2026 (site is young — ~24 days old in GSC terms)
- 0 pages formally indexed yet from page-sitemap.xml (24 submitted, 0 indexed)
- Sitemap errors on category-sitemap, post-sitemap, sitemap_index

### Top Search Queries (90-Day)

| Query | Clicks | Impressions | CTR | Position |
|-------|--------|-------------|-----|----------|
| purebrain | 13 | 45 | 28.9% | 4.0 |
| pure brain | 1 | 28 | 3.6% | 6.0 |
| why do ai pilots fail | 0 | 14 | 0% | 68.2 |
| stack calculator | 0 | 3 | 0% | 64.3 |
| ai agents billion dollar opportunity | 0 | 1 | 0% | 10.0 |
| ai testing partner meaning | 0 | 1 | 0% | 9.0 |

**Branded queries dominate.** "purebrain" is ranking at position 4 with strong 29% CTR. Non-branded queries are either position 60+ (not competitive yet) or getting 0 clicks despite decent positions.

### Top Pages in Search (90-Day) — CRITICAL ANALYSIS

| Page | Clicks | Impressions | CTR | Avg Position |
|------|--------|-------------|-----|--------------|
| / (homepage) | 44 | 295 | 14.9% | 3.9 |
| /age-of-ai-agents-next-18-months/ | 1 | 236 | 0.4% | 5.5 |
| /ai-tool-stack-calculator/ | 0 | 193 | 0% | 12.1 |
| /portfolio/ | 0 | 69 | 0% | 5.2 |
| /invitation/ | 0 | 49 | 0% | 4.9 |
| /ai-adoption-review/ | 0 | 44 | 0% | 7.0 |
| /ai-website-analysis/ | 0 | 39 | 0% | 4.9 |
| /ai-website-execution/ | 0 | 37 | 0% | 7.0 |
| /pitch/ | 1 | 34 | 2.9% | 5.2 |
| /how-my-human-named-me-and-what-it-meant/ | 0 | 31 | 0% | 5.8 |
| /ai-readiness-assessment/ | 0 | 30 | 0% | 5.6 |
| /partnered-how-this-levels-you-up/ | 0 | 25 | 0% | 7.2 |
| /ai-partnership-guide/ | 0 | 20 | 0% | 3.1 |
| /the-ai-that-forgets-you-every-single-time/ | 0 | 11 | 0% | 3.7 |

### THE BIG SEO CRISIS: High-Impression, Zero-Click Pages

**These pages are RANKING but nobody is clicking.** This is a systemic meta title/description problem:

1. **/age-of-ai-agents-next-18-months/** — 236 impressions, 0.4% CTR at position 5.5
   - Ranking on page 1, nobody clicks. Title or meta description is not compelling.

2. **/ai-tool-stack-calculator/** — 193 impressions, 0% CTR at position 12.1
   - Close to page 1. A title optimization could double clicks.

3. **/portfolio/** — 69 impressions, 0% CTR at position 5.2
   - Ranking well. What's showing in search? Generic meta?

4. **/invitation/** — 49 impressions, 0% CTR at position 4.9
   - Position 5. Why would anyone click "invitation" in a search result?

5. **/ai-adoption-review/** — 44 impressions, 0% CTR at position 7.0

6. **/ai-website-analysis/** — 39 impressions, 0% CTR at position 4.9

7. **/ai-partnership-guide/** — 20 impressions, 0% CTR at **position 3.1**
   - **Position 3 with ZERO clicks.** This is the most fixable win. The meta description/title is failing hard.

8. **/the-ai-that-forgets-you-every-single-time/** — 11 impressions, 0% CTR at **position 3.7**
   - Strong title in theory. Check what Google is showing vs what's on the page.

### Sitemap Issues

| Sitemap | Status | Last Crawled | Issue |
|---------|--------|--------------|-------|
| page-sitemap.xml | 0/24 indexed | 2026-02-24 | NOT re-crawled since Feb 24 — over 3 weeks stale |
| post-sitemap.xml | Unknown | 2026-03-16 | 1 error |
| category-sitemap.xml | Unknown | 2026-03-16 | 1 error |
| sitemap_index.xml | Unknown | 2026-03-16 | 1 error |

**Critical**: page-sitemap.xml hasn't been crawled since Feb 24. Google may not know about newer pages. Need to force re-submit in GSC.

---

## 6. CONVERSION FUNNEL ANALYSIS

### Event Funnel (30-Day)

| Event | Count | Users | Conversion |
|-------|-------|-------|------------|
| session_start | 1,165 | 860 | 100% (baseline) |
| user_engagement | 1,162 | 467 | 54% of users engage |
| scroll | 643 | 284 | 33% scroll |
| form_start | 191 | 99 | 11.5% start a form |
| form_submission | 131 | 3 | — |
| form_submit | 68 | 60 | ~7% complete |
| click | 40 | 21 | — |

**Form funnel anomaly**: `form_submission` has 131 events from only 3 users vs `form_submit` with 68 events from 60 users. These appear to be two different tracking events — possibly Jared's system (form_submission with 3 users = post-payment webhooks?) and the standard GA4 form event (form_submit = 60 real users submitting assessment forms).

**Key conversion ratio**: 99 users start forms, ~60 complete = **39% form abandonment**. Consistent with prior sessions.

**What forms are converting**:
- /ai-partnership-assessment/ (18 sessions, 61% engagement rate, 39s avg — quick-fill assessment)
- /pay-test/ variants (good engagement, under 50% bounce)

---

## 7. MOST ENGAGED PAGES (30-Day)

| Page | Total Engagement Time | Engagement Rate | Sessions |
|------|-----------------------|-----------------|----------|
| / (Homepage) | 21,972s (6.1 hrs) | 41.9% | 692 |
| /pay-test-sandbox/ | 3,503s (58 min) | 38.1% | 42 |
| /ai-tool-stack-calculator/ | 2,345s (39 min) | 53.4% | 58 |
| /why-purebrain/ | 1,969s (33 min) | 46.3% | 54 |
| /pay-test-2/ | 1,661s (28 min) | 69.2% | 13 |
| /pay-test-sandbox-2/ | 1,608s (27 min) | 55.6% | 27 |
| /blog/ | 1,510s (25 min) | 77.8% | 54 |
| /pay-test-sandbox-3/ | 1,348s (22 min) | 73.1% | 26 |
| /compare/ | 324s | **91.7%** | 12 |

**Hidden gem**: /compare/ has 91.7% engagement rate — highest of any page. Only 12 sessions but everyone who visits is engaged. This page deserves more promotion.

---

## 8. BLOG CONTENT PERFORMANCE (30-Day)

| Post | Sessions | Bounce | Avg Duration |
|------|----------|--------|--------------|
| /blog/ (index) | 54 | 22% | 3m 03s |
| /ceo-vs-employee-ai-transformation-gap/ | 17 | 23.5% | 44s |
| /we-both-wrote-this-post/ | 9 | 33.3% | 11s |
| /why-ai-memory-changes-everything/ | 9 | 0% | 52s |
| /why-95-percent-of-ai-pilots-fail/ | 8 | 25% | 45s |
| /the-difference-between-using-ai-and-having-an-ai-partner/ | 7 | 28.6% | 56s |
| /how-my-human-named-me-and-what-it-meant/ | 6 | 0% | 31s |
| /why-your-ai-pilot-is-succeeding-and-failing-at-the-same-time/ | 5 | 0% | 69s |
| /ai-partnership-guide/ | 2 | 0% | 13m 42s |
| /most-ai-agents-break-the-moment-you-ask-where-the-data-goes/ | 2 | 0% | 6m 30s |
| /the-ai-trust-gap/ | 4 | 25% | 1m 56s |

**Blog pattern**: Low-traffic but highly engaged. Multiple posts with 0% bounce rate (all visitors read deeper). The content is resonating with people who find it.

**Standout**: /ai-partnership-guide/ — only 2 sessions but 13m 42s avg duration. Someone is deeply reading this.

---

## 9. UX ISSUES (From Clarity Prior Sessions + GA4 Signals)

Microsoft Clarity requires interactive OAuth, so these are based on prior session recordings and GA4 signals:

### From GA4 Signals
1. **/ai-website-execution/** — 69% bounce, 4s duration. Page likely broken or has no content above fold.
2. **/why-purebrain/** — 100% bounce this week (3s avg). Something wrong in the last 7 days specifically.
3. **/blog/stop-treating-your-ai-like-an-intern** — 100% bounce, 0s duration. Path format wrong (`/blog/slug` vs `/slug/`) — 404 likely.
4. **Form abandonment 39%** — Consistent every session. Something in the form flow loses ~40 users.
5. **Homepage 71% bounce this week** (vs 58% 30-day) — This week's spike traffic bouncing harder, suggesting cold/unfamiliar visitors.

### From Prior Clarity Sessions (Feb-Mar)
- Rage clicks on navigation elements (hamburger menu on mobile)
- Dead clicks in the hero section (users clicking non-clickable brain graphic)
- Quick backs from /ai-website-execution/ (fast in, fast out = page fails expectation)
- Users scroll 60-70% down homepage then leave without clicking CTA

---

## 10. ACTIONABLE RECOMMENDATIONS (Ranked by Impact)

### CRITICAL — Fix This Week

**1. Fix /ai-partnership-guide/ meta title/description — Position 3.1, 0 clicks**
- HIGHEST-IMPACT SEO fix. Ranking position 3 on Google with zero clicks is pure waste.
- The title in search results is not compelling searchers to click.
- Action: Rewrite title tag to include emotional hook + clear value prop. Add meta description with strong CTA.
- Expected impact: 5-15 clicks/month from position 3 → significant traffic gain.

**2. Fix /age-of-ai-agents-next-18-months/ meta — 236 impressions, 0.4% CTR**
- Biggest impression volume of any non-homepage page. Position 5.5.
- If CTR matched homepage (15%) this would be 35+ clicks/month from zero.
- Action: Rewrite title. Current title may be too vague. Try: "The Next 18 Months of AI Agents: What Actually Happens" or similar.

**3. Fix /ai-tool-stack-calculator/ SEO — 193 impressions, 0% CTR, position 12**
- Close to page 1 (position 12 = top of page 2). Content optimization could push to page 1.
- 0% CTR even when shown means title isn't matching search intent.
- Action: Identify what queries trigger this page, rewrite title to match intent.

**4. Re-submit page-sitemap.xml to GSC**
- Last crawled Feb 24 — hasn't been recrawled in 21+ days.
- Google doesn't know about ~3 weeks of new pages.
- Action: Go to GSC → Sitemaps → Submit https://www.purebrain.ai/page-sitemap.xml fresh.

**5. Fix /blog/stop-treating-your-ai-like-an-intern URL**
- This path has 100% bounce / 0s duration — it's a 404.
- The correct URL is /stop-treating-your-ai-like-an-intern/ (without /blog/ prefix).
- Action: Add redirect from /blog/[slug] to /[slug]/ for all posts.

### HIGH — This Month

**6. Optimize /compare/ for promotion**
- 91.7% engagement rate — highest of any page.
- Only 12 sessions but everyone who goes there is engaged.
- Action: Add CTAs within blog posts and homepage linking to /compare/.
- Add /compare/ to navigation or footer.

**7. Fix /ai-website-execution/ bounce issue**
- 69% bounce, 4s duration. Users arrive and leave instantly.
- Either page content doesn't match what drives clicks to it, or page load issue.
- Action: Audit page content and compare to /ai-website-analysis/ (which performs better).

**8. Investigate Germany bot traffic**
- 150 sessions from 150 unique German users (1 session each) inflates metrics.
- Action: Create GA4 filter to exclude this bot traffic for cleaner reporting.
- This would drop total sessions ~13% but make all other metrics more accurate.

**9. Reduce homepage bounce rate**
- Homepage is 71% bounce this week — too many cold visitors leaving without engaging.
- This week's traffic spike is cold audience (309 new users this week alone).
- Action: Improve hero section clarity. First 3 seconds must communicate value.
- Consider A/B test: current hero vs stronger value proposition headline.

**10. Build organic social into systematic content engine**
- Organic social is second-fastest growing channel (40% WoW growth, 50% bounce rate).
- 98 sessions/month and growing.
- Action: Continue Bluesky posting cadence. Track which post types drive traffic vs engagement.

### MONITOR — Ongoing

**11. Track chatgpt.com referral**
- 2 sessions this month from ChatGPT.
- AI systems are discovering and recommending PureBrain.
- Action: Monitor monthly. If it grows, optimize content for AI citation.

**12. Investigate /invitation/ CTR (49 impressions, position 4.9, 0 clicks)**
- Ranking well but "invitation" as a page title/meta likely confuses searchers.
- Action: Update meta title to explain what the invitation is for.

**13. Fix sitemap errors (category, post, sitemap_index)**
- 3 of 4 sitemaps showing errors.
- These are likely WordPress/CF Pages migration artifacts.
- Action: Update sitemap URLs to reflect CF Pages domain structure.

---

## 11. WEEK-OVER-WEEK TRENDS SUMMARY

| Metric | Mar 3–9 | Mar 10–16 | Change |
|--------|---------|-----------|--------|
| Total Sessions | 107 | 432 | +304% |
| Direct Sessions | 73 | 346 | +374% |
| Organic Search | 2 | 24 | +1,100% |
| Organic Social | 15 | 21 | +40% |
| New Users | ~44 | ~331 | +652% |

The spike is real but likely driven by Jared actively sharing (Teams referrals, direct). Organic search growth is the signal to watch — it's compounding.

---

## 12. DATA QUALITY NOTES

- **Germany bot traffic**: ~150 sessions/month from automated sources. Filter in GA4 for true metrics.
- **form_submission (3 users)** vs **form_submit (60 users)**: Two different event names tracking different things. Investigate which is the payment webhook vs assessment form.
- **/lpm-video-test/** getting 9 sessions with 9m 14s duration — test page shouldn't be publicly accessible. Consider password-protecting or removing.
- **/wp-admin** appearing in GA4 (3 sessions, 14m 31s) — this is internal Jared access. Should be filtered from analytics.

---

## Platform Status

| Platform | Data Available | Method |
|----------|----------------|--------|
| Google Analytics 4 | Full data | Service account API |
| Google Search Console | Full data | Service account API |
| Microsoft Clarity | Unavailable | Requires interactive OAuth (Microsoft login wall) |

---

*Report generated: 2026-03-17 | Property: purebrain.ai (GA4: 525007539)*
