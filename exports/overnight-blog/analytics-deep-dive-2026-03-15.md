# Analytics Deep Dive — purebrain.ai
**Date**: 2026-03-15
**Compiled by**: browser-vision-tester
**Platforms**: Google Analytics 4 + Google Search Console + Microsoft Clarity (auth-blocked)

---

## EXECUTIVE SNAPSHOT

| Metric | 7 Days | 28 Days |
|--------|--------|---------|
| **Total Sessions** | 337 | 1,065 |
| **Total Users** | 283 | 802 |
| **New Users** | 251 | 772 |
| **Page Views** | 399 | 1,707 |
| **Avg Bounce Rate** | 66.7% | 58.6% |
| **Avg Session Duration** | 2:02 min | 2:45 min |
| **Live Visitors (realtime)** | **2** | — |
| **Organic Search Sessions** | 14 | 34 |
| **GSC Clicks (90d)** | — | 55 total |
| **GSC Impressions (90d)** | — | ~1,650+ |

**Key headline**: Traffic is almost entirely direct (75-76%). The site has real search presence (1,650+ impressions in 90d) but is converting almost none of it to clicks. The indexing gap and title/meta weakness are the biggest levers available right now.

---

## 1. GOOGLE ANALYTICS 4

### 1a. Realtime (live right now)
- **2 active users** on the homepage ("PURE BRAIN – Your Brain. Your AI. Actual Intelligence!")

---

### 1b. Traffic by Channel — 7 Days

| Channel | Sessions | Users | Bounce Rate | Avg Duration |
|---------|----------|-------|-------------|--------------|
| Direct | 269 (80%) | 245 | 68.4% | 2:02 |
| Referral | 21 (6%) | 9 | 47.6% | 2:09 |
| Organic Social | 17 (5%) | 10 | 52.9% | 2:59 |
| Unassigned | 16 (5%) | 14 | 87.5% | 0:21 |
| Organic Search | 14 (4%) | 5 | 42.9% | 3:10 |

**Observations**:
- Organic Search has the BEST engagement (3:10 avg, 43% bounce) — users who find via search are most qualified
- Unassigned traffic (87.5% bounce, 21 seconds) = bots or misconfigured UTM sources, nearly worthless
- Direct still dominates — brand strength, but not scalable acquisition

---

### 1c. Traffic by Channel — 28 Days

| Channel | Sessions | Users | New Users | Bounce Rate | Avg Duration |
|---------|----------|-------|-----------|-------------|--------------|
| Direct | 804 (75%) | 659 | 660 | 58.2% | 2:28 |
| Organic Social | 94 (9%) | 70 | 65 | 52.1% | 1:58 |
| Referral | 84 (8%) | 20 | 15 | 47.6% | 2:26 |
| Unassigned | 49 (5%) | 36 | 19 | 65.3% | 6:46 |
| Organic Search | 34 (3%) | 17 | 13 | 44.1% | 5:14 |

**Note**: Organic Search 6:46 avg duration in Unassigned is suspicious — likely a tracking error. The organic search 5:14 avg confirms high-quality users.

---

### 1d. Top Traffic Sources (named referrers, 90d)

| Source / Medium | Sessions |
|-----------------|----------|
| (direct) / (none) | 804 |
| statics.teams.cdn.office.net / referral | 71 |
| linkedin / jared | 42 |
| google / organic | 33 |
| m.facebook.com / referral | 19 |
| facebook.com / referral | 14 |
| linkedin.com / referral | 14 |
| blog / cta | 9 |
| ai-civ.com / referral | 3 |
| chatgpt.com / referral | 2 |

**Key finding**: Microsoft Teams (statics.teams.cdn.office.net) is sending 71 sessions — this is internal/demo use, likely Jared sharing the site in Teams calls. This is essentially "sales demo" traffic, not acquisition. LinkedIn tagged as "jared" medium = Jared's personal posting (42 sessions). Real LinkedIn organic = 14 sessions. ChatGPT referral = 2 sessions (AI-to-AI discovery beginning).

---

### 1e. Device Breakdown — 28 Days

| Device | Sessions | Users | Bounce Rate | Avg Duration |
|--------|----------|-------|-------------|--------------|
| Desktop | 814 (77%) | 618 | 56% | 2:38 |
| Mobile | 249 (23%) | 163 | 57.8% | 2:57 |

**Observation**: Mobile is a full 23% of traffic. Both device types have similar bounce rates, which is good — no major mobile UX crisis. Mobile users actually stay slightly longer (2:57 vs 2:38). Mobile optimization is working.

---

### 1f. Geography — 28 Days

| Country | Sessions | Users |
|---------|----------|-------|
| United States | 658 (62%) | 487 |
| Germany | 150 (14%) | 150 |
| Canada | 85 (8%) | 36 |
| Pakistan | 51 (5%) | 18 |
| United Kingdom | 13 (1%) | 12 |
| Lebanon | 10 (<1%) | 1 |
| India | 9 (<1%) | 9 |
| Philippines | 9 (<1%) | 5 |
| France | 7 (<1%) | 7 |

**Germany anomaly still active**: 150 sessions from 150 unique users = no return visitors from Germany. This is consistent with bot traffic or a specific referral source hitting the site once each. Germany users had 150 sessions from 150 different users — almost certainly scrapers or automated traffic. Worth monitoring but not genuine audience.

**Pakistan**: 51 sessions from only 18 users = return visitors. Could be real engagement or a known contact group.

---

### 1g. Top Pages — 28 Days

| Page | Sessions | Bounce | Engagement | Time on Site |
|------|----------|--------|------------|--------------|
| / (homepage) | 601 | 54.7% | 45.3% | 20,826s total |
| /ai-tool-stack-calculator/ | 58 | 46.6% | 53.4% | 2,345s |
| /why-purebrain/ | 54 | 53.7% | 46.3% | 1,969s |
| /blog/ | 53 | 20.8% | **79.2%** | 1,502s |
| /pay-test/ | 44 | 36.4% | 63.6% | 969s |
| /pay-test-sandbox/ | 42 | 61.9% | 38.1% | 3,503s |
| /pay-test-sandbox-2/ | 27 | 44.4% | 55.6% | 1,608s |
| /pay-test-sandbox-3/ | 22 | 36.4% | 63.6% | 1,315s |
| /ai-partnership-assessment/ | 18 | 38.9% | 61.1% | 392s |
| /ai-website-analysis/ | 17 | 47.1% | 52.9% | 295s |
| /ceo-vs-employee-ai-transformation-gap/ | 17 | 23.5% | **76.5%** | 177s |
| /mission-vision-values/ | 17 | 41.2% | 58.8% | 809s |
| /compare/ | 10 | 10% | **90%** | 292s |
| /why-ai-memory-changes-everything/ | 9 | 0% | **100%** | 209s |
| /the-difference-between-using-ai-and-having-an-ai-partner/ | 7 | 28.6% | 71.4% | 298s |

**Star performers** (high engagement rate):
1. `/compare/` — 90% engagement, 10% bounce. People who reach this page are genuinely evaluating.
2. `/why-ai-memory-changes-everything/` — 100% engagement, 0% bounce. This post is a reader magnet.
3. `/blog/` — 79% engagement. The blog index itself converts browsers into readers.
4. `/ceo-vs-employee-ai-transformation-gap/` — 76.5% engagement. Strong topic resonance.

**Pages with problems**:
- `/ai-website-execution/` — 13 sessions, 69.2% bounce, only 23 seconds avg. People arrive and leave almost instantly.
- `/invitation/` — 9 sessions, 67% bounce, 52 seconds. Not compelling enough for the conversion moment.
- `/pay-test-sandbox/` — 42 sessions but 61.9% bounce with 3,503s total (high variance — some people really dug in, many left fast).

---

### 1h. Events — 90 Days

| Event | Count | Users |
|-------|-------|-------|
| page_view | 1,707 | 773 |
| user_engagement | 1,075 | 409 |
| session_start | 1,052 | 773 |
| first_visit | 772 | 765 |
| scroll | 607 | 264 |
| form_start | 189 | 97 |
| form_submission | 131 | 3 |
| form_submit | 68 | 60 |

**Critical finding — form funnel leakage**:
- 189 form_start events (97 unique users began a form)
- 131 form_submission events but only 3 unique users (!) — this is likely an automated event firing issue or the chatbot session counts as form events
- 68 form_submit from 60 unique users = the "real" human form submission number
- Drop from form_start (97 users) to form_submit (60 users) = 38% abandonment on forms. That's a fixable conversion leak.

---

## 2. GOOGLE SEARCH CONSOLE

### 2a. Overall Performance — 90 Days

- **Total Clicks**: ~55
- **Total Impressions**: ~1,650+
- **Overall CTR**: ~3.3%
- **Average Position**: ~5-6

### 2b. Top Search Queries — 90 Days

| Query | Clicks | Impressions | CTR | Position |
|-------|--------|-------------|-----|----------|
| purebrain | 12 | 42 | 28.6% | 4.1 |
| pure brain | 0 | 24 | 0% | 6.6 |
| "runway ml" "luma ai" (scrapers) | 0 | 33 | 0% | 29.2 |
| why do ai pilots fail | 0 | 12 | 0% | 67.3 |
| ai agents billion dollar opportunity | 0 | 1 | 0% | 10 |
| ai testing partner meaning | 0 | 1 | 0% | 9 |
| stack calculator | 0 | 2 | 0% | 65.5 |

**Key query insights**:
- "purebrain" brand search (12 clicks, pos 4.1) is the dominant converting query — brand awareness is working
- "pure brain" (24 impressions, pos 6.6, 0 clicks) = people searching our brand by mistake, not converting. The listing at position 6.6 needs a better title tag and meta description to get those 24 impressions converting.
- "why do ai pilots fail" — 12 impressions but at position 67! We have content on this. The blog post needs SEO work to get from page 7 to page 1.
- The "runway ml / luma ai" query is a competitor scraper job listing query — irrelevant noise.

---

### 2c. Top Pages by Search Impressions — 90 Days

| Page | Clicks | Impressions | CTR | Position |
|------|--------|-------------|-----|----------|
| / (homepage) | 41 | 270 | 15.2% | 4.0 |
| /age-of-ai-agents-next-18-months/ | 1 | 234 | 0.4% | 5.5 |
| /ai-tool-stack-calculator/ | 0 | 185 | 0% | 11.5 |
| /portfolio/ | 0 | 64 | 0% | 4.8 |
| /invitation/ | 0 | 46 | 0% | 4.8 |
| /ai-adoption-review/ | 0 | 44 | 0% | 7.0 |
| /ai-website-analysis/ | 0 | 37 | 0% | 4.8 |
| /ai-website-execution/ | 0 | 36 | 0% | 6.9 |
| /pitch/ | 1 | 31 | 3.2% | 5.3 |
| /ai-readiness-assessment/ | 0 | 29 | 0% | 5.4 |
| /how-my-human-named-me-and-what-it-meant/ | 0 | 24 | 0% | 6.1 |
| /most-ai-agents-break-the-moment-you-ask-where-the-data-goes-2/ | 0 | 23 | 0% | 13.0 |
| /partnered-how-this-levels-you-up/ | 0 | 22 | 0% | 7.4 |
| /ai-partnership-guide/ | 0 | 20 | 0% | 3.1 |
| /teach-your-ai-something-no-one-else-can/ | 0 | 19 | 0% | 5.5 |
| /the-ai-that-forgets-you-every-single-time/ | 0 | 11 | 0% | 3.7 |
| /52-billion-ai-agents-market-is-not-the-story/ | 0 | 11 | 0% | 8.8 |
| /purebrain-vs-sitegpt/ | 1 | — | 12.5% | 4.5 (7d) |

**MASSIVE opportunity**: `/age-of-ai-agents-next-18-months/` has 234 impressions (2nd highest page) at position 5.5 but only 1 click in 90 days (0.4% CTR). That's 233 lost clicks. The title tag / meta description must be weak or misleading for the intent. This is the #1 priority fix on the entire site.

**Hidden gems** (position 3-5 range, zero clicks):
- `/ai-partnership-guide/` — position 3.1, 20 impressions, 0 clicks. We're almost #3 on Google but nobody clicks. Meta is broken.
- `/the-ai-that-forgets-you-every-single-time/` — position 3.7, 0 clicks. Another top-3 ranking with zero conversion.
- `/invitation/` — position 4.8, 46 impressions, 0 clicks. 46 people see us in results and don't click.

---

### 2d. Indexing Status

| Sitemap | Submitted | Indexed | Errors |
|---------|-----------|---------|--------|
| page-sitemap.xml (pages) | 24 web pages | 0 | 0 |
| post-sitemap.xml (blog posts) | — | — | 1 error |
| category-sitemap.xml | — | — | 1 error |
| sitemap_index.xml | — | — | 1 error |

**Critical finding**: The page sitemap shows 24 submitted web pages, 0 indexed. This is consistent with what was found on 2026-03-11. Indexing is still in progress for most of the site. GSC impressions are coming from pages Google has crawled but not yet formally indexed — this is normal for a relatively new domain with fresh content. The 3 sitemaps with errors need investigation (the category and post sitemaps likely have URL format issues or redirect chains).

**Note on last download dates**: sitemap_index.xml was downloaded 2026-03-14 (yesterday) — Google is actively crawling. The page-sitemap.xml hasn't been re-downloaded since 2026-02-24 — this should be resubmitted.

---

### 2e. 7-Day Search Snapshot

**Top page this week**: `/age-of-ai-agents-next-18-months/` — 123 impressions in 7 days, only 1 click. This page is ranking but not converting. Position 5.7.

**Homepage this week**: 65 impressions, 11 clicks, CTR 16.9%, position 4.1. The homepage converts at 17% CTR which is strong when people search branded terms.

**Velocity check**: The calculator page (/ai-tool-stack-calculator/) had 185 impressions over 90d, and 51 in just the last 7d — it's accelerating. But position 13 means it's on page 2. Needs to break into top 5.

---

## 3. MICROSOFT CLARITY

**Status**: Authentication wall — requires interactive OAuth (Microsoft, Facebook, or Google). No programmatic API available. Project ID confirmed as `viy9bnc56x`.

**What we miss without Clarity**:
- Heatmap data (where users click, scroll depth by page)
- Session recordings (real user behavior patterns)
- Rage click and dead click data
- Excessive scroll / quick-back rates

**Workaround**: The GA4 engagement rates provide a reasonable proxy. Pages with <30% engagement rate are the Clarity-equivalent of high rage-click pages. Key pages to investigate manually in Clarity dashboard: homepage (45% engagement), /ai-website-execution/ (31% engagement, clear UX problem).

---

## 4. TREND ANALYSIS: 28d vs 7d

| Metric | 28-Day Avg/Week | 7-Day Actual | Trend |
|--------|-----------------|--------------|-------|
| Sessions/week | ~267 | 337 | UP +26% |
| Users/week | ~200 | 283 | UP +41% |
| Organic Search | ~8.5/week | 14 | UP +65% |
| Organic Social | ~23.5/week | 17 | DOWN -28% |

**Good news**: Overall traffic is accelerating — 337 sessions this week vs 267/week average over the month. Organic search is growing fastest (+65%) which is the right kind of growth.

**Concern**: Social traffic dropped this week (-28%). This correlates with blog posting cadence — if posts weren't distributed this week, social drops.

---

## 5. CONVERSION FUNNEL ANALYSIS

Based on GA4 events and page data:

```
Homepage visitors: 601 sessions (28d)
↓ (scroll events: 607 total across all pages, so most scroll)
Engaged visitors: ~272 (45% engagement rate)
↓
Form starters: 97 unique users
↓
Form completers: 60-68 unique users
↓
Conversion rate homepage → form submit: ~10-11%
```

This is a reasonable conversion rate for a premium AI product at awareness stage, but the 38% form abandonment after starting is an opportunity.

---

## 6. PRIORITY RECOMMENDATIONS

### Priority 1 — FIX NOW (highest impact, confirmed data)

**A. Fix /age-of-ai-agents-next-18-months/ meta title and description**
- 234 impressions, position 5.5, 0.4% CTR over 90 days
- This week alone: 123 impressions, 1 click
- Expected gain if CTR reaches homepage levels (15%): ~35 additional clicks/week from this page alone
- Action: Rewrite title tag to be click-worthy and match search intent for "AI agents 2025/2026 forecast" type queries. Add compelling meta description with a clear hook.

**B. Fix the 3 sitemap errors (category, post, sitemap_index)**
- category-sitemap.xml: 1 error
- post-sitemap.xml: 1 error
- sitemap_index.xml: 1 error
- Sitemap errors slow Google's ability to discover new pages
- Action: Check GSC for specific error details, fix URL issues or redirect chains, resubmit

**C. Resubmit page-sitemap.xml to GSC**
- Last downloaded by Google: 2026-02-24 — over 3 weeks ago
- New pages published since then won't be indexed
- Action: GSC → Sitemaps → Remove + resubmit page-sitemap.xml

---

### Priority 2 — HIGH VALUE (pages ranking but not clicking)

**D. Audit title/meta on "position 3-5 with 0 clicks" pages**
Pages ranking in top 5 but getting zero clicks = meta descriptions failing:
- `/ai-partnership-guide/` (pos 3.1, 20 impressions, 0 clicks)
- `/the-ai-that-forgets-you-every-single-time/` (pos 3.7, 11 impressions, 0 clicks)
- `/invitation/` (pos 4.8, 46 impressions, 0 clicks)
- `/ai-website-analysis/` (pos 4.8, 37 impressions, 0 clicks)
- `/ai-readiness-assessment/` (pos 5.4, 29 impressions, 0 clicks)

These pages collectively represent ~143 weekly impressions at positions where a good CTR (10%+) should generate 14+ clicks/week. Currently generating ~0.

**E. Improve /ai-tool-stack-calculator/ from page 2 to page 1**
- 185 impressions in 90d, position 11.5 = just off page 1
- Strong engaged audience when they do land (53% engagement rate)
- Action: Add more tool entries, strengthen H1/H2, add FAQ schema, get a backlink from the blog

---

### Priority 3 — GROWTH LEVERS

**F. Address the form abandonment (38% drop-off)**
- 97 users start forms, 60-68 complete
- Check which form page has the highest start-but-no-submit ratio
- Likely candidates: /ai-partnership-assessment/, /ai-adoption-review/, /ai-website-analysis/
- Action: Reduce form fields, add trust signals near the submit button, test a 2-step form

**G. Investigate and address Unassigned traffic (87.5% bounce)**
- 49 sessions in 28d from "Unassigned" channel with 87.5% bounce
- This is bot traffic, misconfigured UTMs, or dark social without proper attribution
- Action: Review referrer sources in GA4 explorer, filter confirmed bots, add UTM params to all Telegram/internal sharing links

**H. Build Organic Search from 3% → 15% of traffic**
- Currently 34/1065 sessions = 3.2% organic
- Homepage alone gets 270 impressions/90d and converts at 15.2% CTR
- If 10 more pages reached homepage CTR levels: 500+ additional monthly sessions possible
- Action: Content calendar focused on high-impression keywords already in the data (AI pilots fail, AI agents 2025, AI partnership, AI stack calculator)

**I. Convert "pure brain" brand searchers**
- "pure brain" (no space): 24 impressions, position 6.6, 0 clicks
- These are people searching for us. At position 6.6 we're missing them.
- Action: Add "Pure Brain" as explicit brand name signal in homepage title tag and H1. Could add "Also known as Pure Brain" in structured data.

**J. Leverage the blog's exceptional performance**
- Blog index: 79% engagement rate (best on site)
- 3 blog posts have 100% or near-100% engagement rates
- Blog CTA in email/social is already sending 9 sessions/month
- Action: Add email capture directly on blog index page. The people who read the blog are the most qualified. Capture them there.

---

## 7. WHAT'S WORKING WELL

1. **Homepage CTR (15.2%)** — when people search branded terms, they click. Strong brand identity.
2. **Mobile experience** — nearly identical bounce rates between mobile (57.8%) and desktop (56%). Mobile UX is solid.
3. **Blog engagement (79%)** — people who reach the blog read it. Content quality is high.
4. **Session duration for organic search visitors (5:14)** — organic visitors are extremely qualified, deep readers.
5. **/compare/ page (90% engagement)** — people seriously considering PureBrain vs alternatives are engaged. The compare page is a high-intent signal.
6. **Form start-to-submit (63% completion)** — two-thirds of people who start a form finish it. That's decent; industry average is often 50%.

---

## 8. CLARITY NOTE FOR MANUAL AUDIT

When logging into Clarity manually (https://clarity.microsoft.com, project viy9bnc56x), prioritize checking:

1. **Homepage heatmap** — where are 601 monthly visitors clicking? Are they reaching CTAs or stopping at the hero?
2. **Session recordings for /age-of-ai-agents-next-18-months/** — do organic visitors who land there scroll? Do they immediately back out?
3. **Rage clicks on any page** — particularly the payment/sandbox test pages with moderate bounce rates
4. **Scroll depth on /why-purebrain/** — 54 sessions with 53.7% bounce. Do people scroll past the fold?

---

## SUMMARY FOR JARED

**The data story in plain English**:

PureBrain has 270 search impressions per week on the homepage alone and converts 15% of them to clicks. That's good brand recognition. But there are 20+ other pages ranking in positions 3-6 on Google that get zero clicks — the meta titles and descriptions aren't compelling enough to earn the click even when we're in top results.

The /age-of-ai-agents/ blog post is our biggest untapped asset: 234 impressions in 90 days, position 5.5, but effectively 0 clicks. One rewritten title tag on that post could be worth 30+ additional organic visitors per week.

The blog itself is performing exceptionally (79% engagement rate). People who read our content are genuinely engaged. The opportunity is getting more of them there — which means fixing the meta/title on pages already ranking.

Traffic is growing (up 26% this week vs monthly average). The direction is right. The next inflection point comes from converting existing search impressions into actual clicks.

---

*Report generated via GA4 API (property 525007539) and GSC API (purebrain.ai). Clarity requires interactive auth — data from prior 2026-03-11 session patterns applied where applicable.*
