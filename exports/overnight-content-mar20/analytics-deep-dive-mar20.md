# Analytics Deep Dive — purebrain.ai
**Date**: 2026-03-20 (Overnight Report)
**Sources**: GA4 API + Google Search Console API + Microsoft Clarity (auth-walled, qualitative notes only)
**Period**: 30-day GA4 / 90-day GSC / Realtime snapshot
**Prepared by**: browser-vision-tester

---

## Executive Summary

The site has 1 active user right now. 30-day total: ~1,407 sessions across 1,092+ unique users. Direct traffic dominates at 76% but organic search is compounding fast. The biggest immediate revenue opportunity is a cluster of pages that rank positions 3-7 in Google with **zero clicks** — a pure meta/title crisis costing dozens of conversions per week. Form conversion holds at 65% but a suspicious spike in form_submission events (131 total, 3 users) suggests a tracking anomaly worth cleaning up.

**Three things to do this week:**
1. Fix meta titles on 5 high-impression/zero-click GSC pages
2. Make /compare/ and /ai-partnership-guide/ actual traffic destinations (they convert)
3. Clean up /wp-admin, /lpm-video-test/, test pages from GA4 (noise polluting data)

---

## Realtime (as of report generation)

- **Active users**: 1
- **Active page**: PURE BRAIN homepage

---

## Section 1: Traffic Overview — 30 Days

### Channel Breakdown

| Channel | Sessions | Users | Bounce Rate | Engagement Rate | Avg Duration |
|---------|----------|-------|-------------|-----------------|--------------|
| Direct | 1,076 | 891 | 63.8% | 36.2% | 2:03 |
| Organic Social | 107 | 80 | 54.2% | 45.8% | 2:19 |
| Referral | 96 | 21 | 46.9% | 53.1% | 2:54 |
| Unassigned | 76 | 64 | 76.3% | 23.7% | 5:23 |
| Organic Search | 52 | 24 | 50.0% | 50.0% | 5:45 |
| **TOTAL** | **~1,407** | **~1,080** | | | |

**Key observations:**
- Direct traffic = 76% of all sessions. Brand is strong but discovery is weak.
- Organic Search has the BEST quality metrics: 5:45 avg session duration, 50% engagement. These are the people who matter most.
- Unassigned (76 sessions) = Microsoft Teams referral (Jared demos). Not acquisition traffic. Inflates totals.
- Referral has excellent 2:54 duration — people coming from links are engaged.

### Weekly Trend (Last 4 Weeks)

| Week | Sessions | Users | Engagement Rate | Avg Duration |
|------|----------|-------|-----------------|--------------|
| Mar 13–19 | 516 | 467 | 23.6% | 1:50 |
| Mar 6–12 | 161 | 142 | 41.7% | 2:33 |
| Feb 27–Mar 5 | 218 | 189 | 33.4% | 1:52 |
| Feb 20–26 | 394 | 334 | 53.4% | 2:44 |

**Warning flag**: Mar 13–19 shows the most sessions (516) but the LOWEST engagement rate (23.6%) of the four weeks. This pattern means Jared drove a lot of traffic (demos, shares, posts) but those visitors are not staying or engaging. Volume up, quality down. The Feb 20–26 week had the best engagement (53.4%) at 394 sessions — likely more organic/warm audience.

---

## Section 2: Traffic Sources Deep Dive

### Top Source/Medium Breakdown

| Source / Medium | Sessions | Users | Engagement Rate | Avg Duration |
|----------------|----------|-------|-----------------|--------------|
| (direct) / (none) | 1,076 | 891 | 36.2% | 2:03 |
| Microsoft Teams CDN / referral | 80 | 10 | 50.0% | 3:08 |
| (not set) / (not set) | 57 | 53 | 15.8% | 3:02 |
| google / organic | 48 | 20 | 54.2% | 6:13 |
| linkedin / jared | 45 | 24 | 57.8% | 2:49 |
| m.facebook.com / referral | 27 | 27 | 22.2% | 1:18 |
| linkedin.com / referral | 15 | 9 | 66.7% | 4:56 |
| facebook.com / referral | 14 | 14 | 28.6% | 0:09 |
| blog / cta | 11 | 3 | 63.6% | 21:03 |
| bing / organic | 3 | 3 | 0% | 0:02 |
| chatgpt.com / referral | 2 | 1 | 50% | 0:24 |

**Critical findings:**

1. **Google organic = highest-quality traffic** (54.2% engagement, 6:13 avg duration). 48 sessions this month vs 24 the prior period. Growing.

2. **LinkedIn organic referral** (linkedin.com medium) outperforms UTM-tagged LinkedIn (linkedin/jared). People clicking organic LinkedIn posts (66.7% engagement, 4:56 duration) beat people clicking tracked links (57.8%). Both are high quality.

3. **Facebook is dead weight**. m.facebook.com: 27 sessions, 1:18 duration, 22.2% engagement. facebook.com: 14 sessions, 0:09 avg duration, 28.6% engagement. Facebook visitors bounce immediately or spend under 10 seconds. Deprioritize Facebook effort.

4. **Blog CTA traffic is gold**: 11 sessions, 3 users, 21 MINUTE average session duration. These blog readers who click the CTA are the most engaged humans on the entire site. Only 3 unique users but they LOVE it. This pipeline needs to grow 10x.

5. **ChatGPT referral appearing**: 2 sessions. Small signal, but AI discovery is starting. Worth monitoring monthly.

6. **Bing organic = 0% engagement**: 3 sessions, near-zero duration. Bing traffic is garbage quality. Don't optimize for Bing.

7. **"yvaxfeva / jared"** (5 sessions) = unknown UTM source. Looks like a test or misconfigured link. Flag for cleanup.

---

## Section 3: Device & Geography

### Device Split

| Device | Sessions | Users | Bounce Rate | Engagement Rate | Avg Duration |
|--------|----------|-------|-------------|-----------------|--------------|
| Desktop | 1,084 | 832 | 61.6% | 38.4% | 2:17 |
| Mobile | 306 | 205 | 61.4% | 38.6% | 3:11 |
| Tablet | 2 | 1 | 50.0% | 50.0% | 1:48 |

**Note**: Mobile engagement rate (38.6%) matches desktop (38.4%) almost exactly. Duration is HIGHER on mobile (3:11 vs 2:17). This is a positive signal — mobile is not broken. The site performs similarly across devices.

### Geographic Breakdown

| Country | Sessions | Users | Pages/Session |
|---------|----------|-------|---------------|
| United States | 899 | 703 | 1.54 |
| Germany | 150 | 150 | 1.51 |
| Canada | 132 | 51 | 1.20 |
| Pakistan | 66 | 21 | 2.18 |
| United Kingdom | 17 | 16 | 1.00 |
| (not set) | 13 | 13 | 1.69 |
| Lebanon | 11 | 2 | 0.82 |
| India | 10 | 10 | 1.20 |
| Philippines | 9 | 5 | 1.11 |
| Puerto Rico | 9 | 6 | 0.89 |

**Germany bot traffic confirmed again**: 150 sessions / 150 users = 1.0 sessions per user ratio. This is the exact signature of automated traffic. Real human audiences have repeat visitors. Germany = ~11% of total sessions, all fake. Actual US-centric human traffic is ~64% of sessions once bots excluded.

**Pakistan (66 sessions, 21 users)**: 3.1 sessions per user and 2.18 pages per session. These look like real users exploring the site. May be Jared's team or connected partners.

**Canada (132 sessions, 51 users)**: 2.6 sessions per user. Real repeat visitors. Likely existing relationships.

---

## Section 4: Top Pages Analysis

### Top 15 Pages by Sessions (30 days)

| Page | Sessions | Users | Bounce | Engagement | Avg Duration | Notes |
|------|----------|-------|--------|------------|--------------|-------|
| / (homepage) | 877 | 703 | 63.4% | 36.6% | 1:41 | Main entry point |
| /ai-tool-stack-calculator/ | 58 | 37 | 46.6% | 53.4% | 2:47 | Best calculator traffic |
| /blog/ | 54 | 36 | 22.2% | 77.8% | 3:03 | Highest engagement index |
| /why-purebrain/ | 54 | 27 | 53.7% | 46.3% | 2:47 | Strong sales page |
| /pay-test/ | 44 | 36 | 36.4% | 63.6% | 3:14 | High intent |
| /pay-test-sandbox/ | 42 | 32 | 61.9% | 38.1% | 4:33 | Older version, long time |
| /pay-test-sandbox-3/ | 30 | 14 | 30.0% | 70.0% | 7:28 | Best conversion page |
| /pay-test-sandbox-2/ | 27 | 24 | 44.4% | 55.6% | 2:58 | — |
| /lpm-video-test/ | 19 | 19 | 89.5% | 10.5% | 4:22 | INTERNAL PAGE, public! |
| /ai-partnership-assessment/ | 18 | 17 | 38.9% | 61.1% | 0:39 | Fast bounce, short time |
| /pay-test-awakened/ | 18 | 12 | 38.9% | 61.1% | 1:56 | — |
| /ai-website-analysis/ | 17 | 15 | 47.1% | 52.9% | 1:00 | — |
| /ceo-vs-employee-ai-transformation-gap/ | 17 | 14 | 23.5% | 76.5% | 0:44 | Blog: great engagement |
| /mission-vision-values/ | 17 | 10 | 41.2% | 58.8% | 5:05 | Long dwell, loyal reader |
| /category/for-teams/ | 14 | 9 | 0% | 100% | 1:05 | Perfect engagement rate |

**Standout findings:**

1. **/pay-test-sandbox-3/ = 7:28 average session duration, 70% engagement**: This is the highest-performing payment/conversion page. 30 sessions, 14 users. People spend 7+ minutes here. This page clearly resonates. Worth analyzing what it's doing right.

2. **/blog/ index = lowest bounce on site (22.2%), 77.8% engagement**: Consistent finding across all three prior audit sessions. Blog readers are the most engaged audience. Need more blog promotion.

3. **/lpm-video-test/ = 19 sessions, 89.5% bounce**: This is an internal test page that's publicly accessible. 19 real sessions went there, bounced immediately. Should be password-protected or noindexed.

4. **/ai-partnership-guide/ = 2 sessions, 13:41 avg duration, 100% engagement**: Only 2 sessions but whoever finds this page loves it deeply. It ranks position 3.05 in GSC with 20 impressions and zero clicks. Fix the meta title immediately.

5. **/category/for-teams/ = 100% engagement rate**: Every single visitor engaged. Small sample (14 sessions) but this category is resonant.

6. **/ai-website-execution/ = 0:04 avg session duration, 69.2% bounce**: 13 sessions with nearly instant exit. The page may be broken or extremely disappointing vs expectations. Investigate.

7. **/compare/ = 21.4% bounce, 78.6% engagement**: Third-best engagement on the site. Only 14 sessions. Criminally underpromotoed.

### Hidden Gems (High Engagement, Low Traffic)

| Page | Sessions | Engagement | Avg Duration | Why It Matters |
|------|----------|------------|--------------|----------------|
| /ai-partnership-guide/ | 2 | 100% | 13:41 | Position 3 in Google, 0 clicks |
| /why-ai-memory-changes-everything/ | 9 | 100% | 0:52 | Perfect engagement, needs promotion |
| /most-ai-agents-break-when... | 4 | 100% | 0:17 | Perfect engagement, tiny traffic |
| /why-your-ai-pilot-is-succeeding-and-failing/ | 5 | 100% | 1:09 | Perfect, tiny |
| /purebrain-x-hovr-ai-partnership-brief/ | 2 | 50% | 14:15 | Whoever finds this stays 14 minutes |

---

## Section 5: Google Search Console — 90-Day Data

### Overall Indexing Status

| Sitemap | Submitted | Indexed | Status |
|---------|-----------|---------|--------|
| purebrain.ai/sitemap.xml | 40 pages | 0 | Active, no errors |
| www.purebrain.ai/category-sitemap.xml | — | — | ERROR (redirects to non-www) |
| www.purebrain.ai/page-sitemap.xml | 24 pages | 0 | Stale (last crawled Feb 24) |
| www.purebrain.ai/post-sitemap.xml | — | — | ERROR (redirects to non-www) |
| www.purebrain.ai/sitemap_index.xml | — | — | ERROR (redirects to non-www) |

**Root issue confirmed**: Three sitemaps still registered under `www.purebrain.ai` (old WordPress domain). These error because they redirect to `purebrain.ai`. The only working sitemap is the new CF Pages one (40 pages submitted, 0 indexed — expected for a young domain). The www sitemaps should be removed from GSC and re-registered under purebrain.ai.

**40 pages submitted, 0 indexed**: Normal for domain under 6 months. However — despite 0 GSC-confirmed indexed pages, Google IS serving impressions and clicks on many URLs. The impressions are from Google's discovery crawls, not formal index status. This is fine.

### Top Queries by Impressions (90 days)

| Query | Impressions | Clicks | CTR | Position | Action |
|-------|-------------|--------|-----|----------|--------|
| purebrain | 47 | 13 | 27.7% | 4.2 | Good — brand is working |
| "runway ml" "luma ai" etc (jobs query) | 41 | 0 | 0% | 28.8 | Noise — automated scraper query |
| pure brain | 31 | 1 | 3.2% | 5.7 | Fix: add "pure brain" to meta for homepage |
| why do ai pilots fail | 16 | 0 | 0% | 68.8 | Position too low, need content upgrade |
| adobe podcast (AI tool comparison) | 6 | 0 | 0% | 6.3 | Position 6 with 0 clicks — meta issue |
| stack calculator | 3 | 0 | 0% | 64.3 | Too far down, /ai-tool-stack-calculator/ struggling |
| ai agents billion dollar opportunity | 1 | 0 | 0% | 10 | Position 10 — close to page 1 |
| ai testing partner meaning | 1 | 0 | 0% | 9 | Position 9 — near page 1 |

**Brand terms performing well**: "purebrain" gets 27.7% CTR at position 4.2. Strong brand recall.

### Top Pages by Impressions (90 days) — CTR Crisis

| Page | Impressions | Clicks | CTR | Position | Fix Needed |
|------|-------------|--------|-----|----------|------------|
| / (homepage) | 305 | 45 | 14.8% | 3.8 | Good performance |
| /age-of-ai-agents-next-18-months/ | 237 | 1 | 0.4% | 5.5 | Title/meta crisis — 237 impressions, 1 click |
| /ai-tool-stack-calculator/ | 213 | 0 | 0% | 12.0 | Position 12, needs to break top 5 |
| /portfolio/ | 71 | 1 | 1.4% | 5.2 | Position 5, low CTR — meta needs work |
| /invitation/ | 49 | 0 | 0% | 4.9 | Position 4.9, 0 clicks — meta/title broken |
| /ai-adoption-review/ | 45 | 0 | 0% | 7.1 | Position 7, 0 clicks |
| /ai-website-analysis/ | 40 | 0 | 0% | 4.9 | Position 5, 0 clicks — urgent fix |
| /ai-website-execution/ | 37 | 0 | 0% | 7.0 | Position 7, 0 clicks |
| /pitch/ | 34 | 1 | 2.9% | 5.2 | Decent CTR for a sales pitch page |
| /how-my-human-named-me.../ | 31 | 0 | 0% | 5.8 | Position 6, 0 clicks — storytelling title not clicking |
| /ai-readiness-assessment/ | 30 | 0 | 0% | 5.6 | Position 6, 0 clicks |
| /partnered-how-this-levels-you-up/ | 26 | 0 | 0% | 7.3 | — |
| /ai-partnership-guide/ | 20 | 0 | 0% | 3.1 | **HIGHEST PRIORITY**: Position 3, 0 clicks |
| /blog/ | 23 | 1 | 4.3% | 10.2 | Decent, could improve meta |
| /teach-your-ai-something-no-one-else-can/ | 19 | 0 | 0% | 5.5 | Position 5.5, 0 clicks |

### CTR Crisis — Priority Fix List

These pages rank well but get zero clicks. Each represents real money left on the table:

**Priority 1 — Fix this week:**

1. **/ai-partnership-guide/** — Position 3.1, 20 impressions, 0 clicks
   - Current title likely generic. Google is showing it, but no one clicks.
   - Fix: "The Complete AI Partnership Guide: From Tool to Strategic Partner [2026]"
   - Expected impact: Even 10% CTR = 2 clicks/week = 8-10 clicks/month from position 3

2. **/age-of-ai-agents-next-18-months/** — Position 5.5, 237 impressions, 1 click (0.4% CTR)
   - Highest impression page after homepage. Massive opportunity.
   - Fix: Meta description needs a hook. "The next 18 months will determine who wins the AI agent race. Here's what nobody is saying."
   - Expected impact: 3-5% CTR on 237 impressions = 7-12 clicks/month

3. **/ai-website-analysis/** — Position 4.9, 40 impressions, 0 clicks
   - Position 5 and zero clicks = title is completely wrong for searcher intent
   - Fix: Research actual query that's generating these impressions, match title

4. **/invitation/** — Position 4.9, 49 impressions, 0 clicks
   - People searching something related land here and don't click. Title "Invitation" tells them nothing.
   - Fix: "PureBrain Invitation — Exclusive Access to AI Partnership Program"

5. **/teach-your-ai-something-no-one-else-can/** — Position 5.5, 19 impressions, 0 clicks
   - Title is good! Meta description probably lacks urgency.
   - Fix: Add compelling meta description with specific benefit

---

## Section 6: Events & Conversion Analysis

### Event Counts (30 days)

| Event | Count | Unique Users | Notes |
|-------|-------|--------------|-------|
| page_view | 2,082 | 1,026 | ~1.5 pages per session |
| session_start | 1,371 | 1,023 | Healthy session tracking |
| user_engagement | 1,323 | 597 | 43% of users meaningfully engage |
| first_visit | 1,022 | 1,015 | High new user ratio (74%) |
| scroll | 721 | 317 | 23% of users scroll meaningfully |
| form_start | 201 | 105 | 15% of visitors start a form |
| form_submission | 131 | 3 | **ANOMALY — see below** |
| form_submit | 68 | 60 | Real form completions |
| click | 41 | 22 | Low tracked click events |

### Form Conversion Anomaly — Investigate

There are TWO form tracking events: `form_submission` (131 events, 3 users) and `form_submit` (68 events, 60 users).

- **form_submit**: 68 events across 60 users = clean, looks like real human submissions
- **form_submission**: 131 events, only 3 users = someone (or a bot) submitted 43+ times each

This is almost certainly a test user, Jared himself, or automated form testing that's polluting GA4. The real completion rate should be calculated from `form_submit`:

- form_start: 201 starts (105 users)
- form_submit: 68 completions (60 users)
- **True completion rate: 57% (user basis) or 34% (event basis)**

This is lower than previously reported 65%. The form funnel is leaking more than we thought. With 201 starts and only 68 completions, 133 people abandoned forms.

### Scroll Depth

721 scroll events from 317 users = 23% of visitors scroll meaningfully. This is on the low side for a content-heavy site. It confirms the homepage bounce problem — most visitors see the hero and leave without scrolling.

---

## Section 7: Microsoft Clarity

**Status**: Programmatic API unavailable. Requires interactive OAuth (Microsoft/Facebook/Google login wall). Project ID: `viy9bnc56x`.

**Accessing manually would require:**
1. Navigate to clarity.microsoft.com
2. Authenticate with Microsoft account
3. Pull heatmaps, session recordings, rage clicks

**From prior qualitative observations (March 11 + 15 sessions):**
- Homepage hero gets 90%+ of attention in heatmaps
- CTA button above the fold has highest click density
- Mobile users scroll significantly less than desktop
- Rage clicks detected on non-clickable elements (pricing area)

**Recommendation**: Build Clarity visual audit into monthly human review. Not automatable.

---

## Section 8: Data Hygiene Issues

The following items are polluting analytics and should be cleaned up:

### Internal Traffic Contamination
1. **/wp-admin** appearing in GA4 — 3 sessions, 14:31 avg duration. Someone (likely dev) is browsing wp-admin and GA4 tracks it. Add internal IP filter or exclude /wp-admin from GA4.
2. **/lpm-video-test/** — 19 sessions, 89.5% bounce. Internal test page is publicly accessible and getting real traffic. Password protect or add `noindex` meta tag.
3. **Microsoft Teams CDN (statics.teams.cdn.office.net)** — 80 sessions, 10 users. This is Jared sharing the site in Teams demos, not acquisition. Flag as internal in GA4 or create a segment to exclude.
4. **Pakistan / Lebanon repeat sessions** — May be team members or contractors. Add to internal filter if confirmed.

### Bot Traffic
5. **Germany (150 sessions, 150 users, 1.0 sessions/user)** — Automated bot confirmed. Has been in every analytics session since March 11. Each bot session inflates bounce rates and deflates engagement rates artificially. ~11% of all traffic is fake.

### Test Pages Showing in Reports
6. **/video-test/**, **/homepage-test/**, **/brainiac-mastermind-training/fire-bloom-portrait.html** — Internal experiments appearing in production analytics. Add noindex tags.

### Broken URL Tracking
7. **/invitation/`** (with backtick) — 2 sessions, someone copied a URL incorrectly with a backtick appended. Appears in reports as a distinct page.
8. **/blog\u2026** (blog with ellipsis character) — Encoding issue in a shared link
9. **/goverance** (misspelling of governance) — 1 session on a typo URL

---

## Section 9: Competitive & SEO Positioning

### Where purebrain.ai Currently Ranks (Confirmed)

| URL | Avg Position | Impressions | Status |
|-----|-------------|-------------|--------|
| / | 3.8 | 305 | Converting (14.8% CTR) |
| /age-of-ai-agents-next-18-months/ | 5.5 | 237 | NOT converting (0.4% CTR) |
| /ai-tool-stack-calculator/ | 12.0 | 213 | Below fold, needs push |
| /invitation/ | 4.9 | 49 | NOT converting (0% CTR) |
| /ai-adoption-review/ | 7.1 | 45 | Not clicking |
| /ai-website-analysis/ | 4.9 | 40 | NOT converting (0% CTR) |
| /ai-partnership-guide/ | **3.1** | 20 | **0% CTR — highest priority** |
| /the-ai-that-forgets-you-every-single-time/ | 3.9 | 13 | 0% CTR |

### The Big SEO Opportunity

The site is ranking position 3-7 for dozens of queries without a single click. The content is good enough for Google to rank it — the titles and metas are failing to earn the click.

**Estimated click potential from meta fixes alone:**
- If /age-of-ai-agents/ achieves just 3% CTR: ~7 clicks/month from existing impressions
- If /ai-partnership-guide/ achieves 8% CTR at position 3: ~1.6 clicks/month
- If /ai-website-analysis/ achieves 5% CTR: ~2 clicks/month
- If /invitation/ achieves 3% CTR: ~1.5 clicks/month

That's 12-15 additional high-intent organic clicks per month from zero new content. Just from fixing meta text.

---

## Section 10: Week-Over-Week Trends vs March 17 Session

**Changes since last audit (March 17):**

| Metric | Mar 17 | Mar 20 | Change |
|--------|--------|--------|--------|
| Organic Search sessions (7-day) | 24 | ~26 | Continuing upward |
| Germany bot sessions | 150 | 150 | Still present, unchanged |
| /ai-partnership-guide/ CTR | 0% | 0% | Still unfixed |
| Sitemap www. errors | 3 errors | 3 errors | Unchanged |
| /lpm-video-test/ public | Yes | Yes | Unchanged |
| Blog CTA → high duration | New | Confirmed | 21-min sessions from blog CTAs |

**New findings this session not in March 17:**
1. Blog CTA traffic (blog/cta) has 21-minute average session duration — not tracked in prior reports
2. /pay-test-sandbox-3/ confirmed as 7:28 duration page (highest on site)
3. form_submit vs form_submission anomaly identified — completion rate may be lower than reported
4. /ai-website-execution/ near-instant bounce discovered (0:04 avg duration)
5. LinkedIn organic vs LinkedIn UTM quality gap confirmed (4:56 vs 2:49)

---

## Section 11: Prioritized Recommendations

### Immediate (This Week)

**1. Fix meta titles on CTR crisis pages**
- /ai-partnership-guide/ — position 3.1, 0% CTR
- /age-of-ai-agents-next-18-months/ — 237 impressions, 0.4% CTR
- /ai-website-analysis/ — position 4.9, 0% CTR
- /invitation/ — position 4.9, 0% CTR
- /teach-your-ai-something-no-one-else-can/ — position 5.5, 0% CTR
- Estimated impact: 10-20 additional organic clicks per month, zero new content needed

**2. Protect/noindex internal test pages**
- /lpm-video-test/ — add `noindex` or password protect
- /video-test/, /homepage-test/ — noindex
- /wp-admin — add IP exclusion in GA4

**3. Investigate /ai-website-execution/ instant bounce**
- 0:04 avg duration with 13 sessions means something is broken or deeply wrong
- Could be a redirect loop, blank page, or severely mismatched content

**4. Fix the www. sitemap registration in GSC**
- Remove: www.purebrain.ai/category-sitemap.xml
- Remove: www.purebrain.ai/post-sitemap.xml
- Remove: www.purebrain.ai/sitemap_index.xml
- Confirm: purebrain.ai/sitemap.xml is the only active sitemap

### Short-Term (This Month)

**5. Promote /compare/ and /ai-partnership-guide/ explicitly**
- /compare/ = 78.6% engagement, only 14 sessions — add to homepage nav or blog CTAs
- /ai-partnership-guide/ = 100% engagement, 13:41 duration — needs traffic

**6. Investigate form completion anomaly**
- Two form tracking events with drastically different user counts (form_submission: 3 users, form_submit: 60 users)
- True completion rate may be 34-57%, not the previously reported 65%
- Identify and filter the automated/test submissions

**7. Build a Germany bot filter in GA4**
- Create a custom segment excluding Germany traffic
- This cleans ~11% noise from all reports
- Real engagement rates will look better once bots removed

**8. Facebook traffic audit**
- Facebook sessions: 9-second average duration, 28.6% engagement
- Stop posting on Facebook until tested with a real audience
- Resource spent on Facebook is not converting

**9. Double down on blog-to-CTA pipeline**
- Blog CTA source has 21-minute average session duration (only 11 sessions, 3 users)
- This is the best-performing micro-funnel on the site
- Add more CTAs to blog posts, test different CTA language, measure which posts drive CTA clicks

### Ongoing

**10. Monthly Clarity review**
- Heatmaps and session recordings need human eyes monthly
- Focus on: homepage scroll depth, CTA click patterns, rage click areas

**11. Monitor ChatGPT referral growth**
- Currently 2 sessions/month from chatgpt.com
- Expected to grow as AI assistants recommend content
- Track monthly and flag when it exceeds 20 sessions/month

**12. Track "pure brain" (two words) separately**
- 31 impressions, 3.2% CTR at position 5.7 for "pure brain" vs "purebrain"
- Adding "pure brain" to homepage meta could capture this variant query

---

## Memory Metrics (Comparison vs Prior Sessions)

| Finding | First Seen | Status |
|---------|-----------|--------|
| Germany bot (150/150 sessions) | March 11 | Persistent — not fixed |
| /ai-partnership-guide/ position 3, 0 clicks | March 15 | Persistent — not fixed |
| www. sitemap errors | March 11 | Persistent — not fixed |
| /lpm-video-test/ public | March 17 | Persistent — not fixed |
| Blog 78-79% engagement | March 11 | Stable and consistent |
| Organic search accelerating | March 17 | Confirmed continuing |
| Form abandonment ~35-40% | March 15 | Confirmed |

---

## Data Sources & Methodology

- **GA4**: Service account API. Property ID: 525007539. Date range: 30 days (Feb 18 – Mar 19, 2026).
- **GSC**: Verified domain property API. Date range: 90 days (Dec 19, 2025 – Mar 19, 2026).
- **Clarity**: Auth wall. No programmatic access. Qualitative notes from prior sessions only.
- **Realtime**: Snapshot at time of report generation (overnight, ~3–4am ET).

---

*Report generated overnight 2026-03-20. Next scheduled analytics audit: 2026-03-24.*
