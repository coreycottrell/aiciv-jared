# PureBrain.ai Analytics Deep Dive
**Date**: 2026-03-11
**Agent**: browser-vision-tester
**Platforms**: Google Analytics 4 (API), Google Search Console (API), Microsoft Clarity (auth wall)
**Period**: 30 days (GA4) + 90 days (GSC) + realtime

---

## Realtime Snapshot (Right Now)

- **Active users right now**: 4 users on the homepage
- Page: "PURE BRAIN - Your Brain. Your AI. Actual Intelligence!" (homepage)

---

## Part 1: Google Analytics 4

### Overall Traffic (Last 30 Days)

| Metric | Value |
|--------|-------|
| Total sessions | 748 |
| Total users | 533 |
| New users | 532 |
| Total pageviews | 1,330 |
| Avg bounce rate | 52.5% |
| Last 7 days sessions | 114 |
| Last 7 days users | 70 |

**Note**: GA4 tracking appears to have started recently — data only goes back ~30 days. No historical comparison available yet.

### Traffic by Channel (Last 30 Days)

| Channel | Sessions | Users | Bounce Rate | Avg Session Duration |
|---------|----------|-------|-------------|---------------------|
| Direct | 550 (74%) | 435 | 53.1% | 2m 40s |
| Organic Social | 78 (10%) | 63 | 52.6% | 1m 43s |
| Referral | 65 (9%) | 14 | 47.7% | 2m 27s |
| Unassigned | 35 (5%) | 24 | 57.1% | 9m 19s |
| Organic Search | 20 (3%) | 12 | 45.0% | 6m 41s |

**Key insight**: 74% Direct traffic means most visitors already know PureBrain exists. The brand is driving its own traffic. Organic Search is only 3% — this is the biggest growth lever available.

**Unassigned sessions** have by far the longest session duration (9m 19s) — these are likely internal/team sessions or UTM-tracked users clicking through campaigns.

### Top Traffic Sources (Last 30 Days)

| Source | Medium | Sessions | Users |
|--------|--------|----------|-------|
| (direct) | (none) | 550 | 435 |
| statics.teams.cdn.office.net | referral | 54 | 6 |
| linkedin | jared | 32 | 22 |
| (not set) | (not set) | 24 | 21 |
| google | organic | 20 | 12 |
| m.facebook.com | referral | 18 | 18 |
| linkedin.com | referral | 13 | 8 |
| facebook.com | referral | 11 | 11 |
| blog | cta | 9 | 1 |
| ai-civ.com | referral | 3 | 2 |
| chatgpt.com | referral | 2 | 1 |
| producthunt.com | referral | 2 | 2 |

**Notable findings**:
- **statics.teams.cdn.office.net** sending 54 sessions (6 users = internal team, 9 sessions/person average) — Microsoft Teams preview cards generating referrals
- **linkedin jared** = 32 sessions with UTM "jared/linkedin" — Jared's LinkedIn posts are driving real traffic
- **Facebook** sending 29 sessions total (mobile + desktop) — underrated channel
- **chatgpt.com** referral — someone linked PureBrain in a ChatGPT conversation or plugin
- **producthunt.com** — small but signals listing may be live or mentioned there

### Top Pages by Sessions (Last 30 Days)

| Page | Sessions | Users | Pageviews | Bounce Rate | Engagement Rate |
|------|----------|-------|-----------|-------------|-----------------|
| / (Homepage) | 339 (45%) | 259 | 434 | 44.8% | 55.2% |
| /ai-tool-stack-calculator/ | 58 (8%) | 37 | 68 | 46.6% | 53.4% |
| /blog/ | 53 (7%) | 36 | 107 | 20.8% | 79.2% |
| /why-purebrain/ | 50 (7%) | 26 | 48 | 50.0% | 50.0% |
| /pay-test/ | 44 (6%) | 36 | 75 | 36.4% | 63.6% |
| /pay-test-sandbox/ | 42 (6%) | 32 | 69 | 61.9% | 38.1% |
| /pay-test-sandbox-2/ | 27 (4%) | 24 | 57 | 44.4% | 55.6% |
| /ai-partnership-assessment/ | 18 | 17 | 20 | 38.9% | 61.1% |
| /ai-website-analysis/ | 17 | 15 | 18 | 47.1% | 52.9% |
| /ceo-vs-employee-ai-transformation-gap/ | 17 | 14 | 18 | 23.5% | 76.5% |
| /mission-vision-values/ | 16 | 10 | 22 | 43.8% | 56.3% |
| /category/for-teams/ | 14 | 9 | 21 | 0% | 100% |
| /ai-website-execution/ | 13 | 13 | 16 | 69.2% | 30.8% |
| /ai-partnership-audit/ | 11 | 10 | 13 | 54.5% | 45.5% |
| /we-both-wrote-this-post/ | 9 | 8 | 12 | 33.3% | 66.7% |
| /why-ai-memory-changes-everything/ | 9 | 6 | 15 | 0% | 100% |
| /why-95-percent-of-ai-pilots-fail/ | 8 | 8 | 11 | 25.0% | 75.0% |
| /compare/ | 8 | 8 | 8 | 0% | 100% |
| /pay-test-sandbox-3/ | 7 | 1 | 13 | 14.3% | 85.7% |

**Star performers by engagement rate:**
- /category/for-teams/ — 100% engagement, 0% bounce
- /why-ai-memory-changes-everything/ — 100% engagement, 0% bounce
- /compare/ — 100% engagement, 0% bounce
- /pay-test-sandbox-3/ — 85.7% engagement
- /blog/ — 79.2% engagement (highest of high-traffic pages)
- /why-95-percent-of-ai-pilots-fail/ — 75% engagement

**Problem pages:**
- /ai-website-execution/ — 69.2% bounce (people land and leave fast)
- /pay-test-sandbox/ — 61.9% bounce (old sandbox underperforming vs newer versions)

### Top Landing Pages (Where Users Enter)

| Landing Page | Sessions | Bounce Rate |
|-------------|----------|-------------|
| / | 277 | 48.4% |
| /ai-tool-stack-calculator | 45 | 53.3% |
| (not set) | 41 | 90.2% |
| /pay-test | 35 | 45.7% |
| /why-purebrain | 35 | 57.1% |
| /blog | 31 | 32.3% |
| /pay-test-sandbox | 31 | 74.2% |
| /pay-test-sandbox-2 | 26 | 42.3% |
| /ai-website-analysis | 16 | 50.0% |
| /ai-partnership-assessment | 15 | 46.7% |

**Note**: /pay-test-sandbox as landing page has 74% bounce — people arrive and leave. The newer /pay-test-sandbox-2 is much better (42% bounce). This old sandbox should probably be retired or redirected.

### Device Breakdown (Last 30 Days)

| Device | Sessions | Users | Bounce Rate | Avg Session Duration |
|--------|----------|-------|-------------|---------------------|
| Desktop | 566 (76%) | 413 | 50.5% | 3m 7s |
| Mobile | 183 (24%) | 122 | 57.9% | 2m 28s |

**Mobile is 24% of traffic with a higher bounce rate.** Desktop users spend more time. The mobile experience needs attention — 57.9% bounce on mobile vs 50.5% on desktop.

### Geographic Breakdown (Last 30 Days)

| Country | Sessions | Users |
|---------|----------|-------|
| United States | 428 (57%) | 290 |
| Germany | 150 (20%) | 150 |
| Canada | 64 (9%) | 28 |
| Pakistan | 33 (4%) | 12 |
| Philippines | 9 | 5 |
| India | 8 | 8 |
| Lebanon | 7 | 1 |
| UK | 5 | 4 |
| Ireland | 4 | 4 |

**Germany is 20% of sessions** — this is unusually high for a US-focused business. The 150 sessions from Germany with 150 unique users suggests these are all new visitors (likely a referral burst, or a German AI community found PureBrain). Worth monitoring.

### Events (Last 30 Days)

| Event | Count | Users |
|-------|-------|-------|
| page_view | 1,330 | 532 |
| user_engagement | 834 | 250 |
| session_start | 746 | 531 |
| first_visit | 532 | 525 |
| scroll | 524 | 211 |
| form_start | 158 | 83 |
| form_submission | 131 | 3 |
| form_submit | 68 | 60 |
| click | 32 | 16 |

**Critical finding**: `form_submission` fired 131 times but only from 3 users. This is almost certainly the automated `blog cta` source — one user triggering 131 form submissions. The real `form_submit` event (60 unique users) is the more meaningful metric.

**Scroll depth**: 524 scroll events from 211 users = users are scrolling through pages, not just bouncing at top.

### 7-Day Trend vs 30-Day Average

| Channel | 7-Day Sessions | 30-Day Weekly Avg | Trend |
|---------|---------------|-------------------|-------|
| Direct | 76 | 138 | Down |
| Organic Social | 16 | 20 | Down slightly |
| Referral | 14 | 16 | Flat |
| Organic Search | 2 | 5 | Down |

**Traffic is softer this week.** 114 sessions in the last 7 days vs a 30-day average of ~187/week. This could be normal week-to-week variance or a lull after a push.

---

## Part 2: Google Search Console

### Overall Performance (Last 90 Days)

| Metric | Value |
|--------|-------|
| Total pages with any impressions | 48 |
| Total pages that received clicks | 4 |
| Total clicks (branded query "purebrain") | 9 |
| Total impressions (top queries) | 102 |
| Avg CTR for branded query | 26.5% |
| Avg position for branded query | 4.7 |

### Search Queries That Drive Impressions

| Query | Clicks | Impressions | CTR | Avg Position |
|-------|--------|-------------|-----|--------------|
| purebrain | 9 | 34 | 26.5% | 4.7 |
| pure brain | 0 | 22 | 0% | 6.6 |
| why do ai pilots fail | 0 | 8 | 0% | 62.8 |
| ai agents billion dollar opportunity 2025 or 2026 | 0 | 1 | 0% | 10 |
| stack calculator | 0 | 1 | 0% | 66 |

**Critical insight**: Only 10 unique search queries generating any impressions across 90 days. The site has virtually no non-branded organic search presence yet. "pure brain" (2 words) gets 22 impressions but zero clicks because it ranks at position 6.6 without a compelling title/description.

### Pages Receiving Search Impressions (Top 15)

| Page | Clicks | Impressions | Avg Position |
|------|--------|-------------|--------------|
| purebrain.ai/ | 32 | 212 | 4.1 |
| /age-of-ai-agents-next-18-months/ | 0 | 160 | 5.3 |
| /ai-tool-stack-calculator/ | 0 | 140 | 10.9 |
| /we-both-wrote-this-post/ | 0 | 41 | 6.0 |
| /why-your-ai-pilot-is-succeeding-and-failing-at-same-time/ | 0 | 41 | 16.9 |
| /why-ai-memory-changes-everything/ | 0 | 40 | 7.6 |
| /portfolio/ | 0 | 39 | 5.5 |
| /what-i-actually-do-all-day/ | 0 | 38 | 5.8 |
| /ai-adoption-review/ | 0 | 35 | 6.7 |
| /why-95-percent-of-ai-pilots-fail/ | 0 | 28 | 10.6 |
| /invitation/ | 0 | 26 | 5.3 |
| /blog/ | 0 | 22 | 10.6 |
| /ai-website-analysis/ | 0 | 21 | 5.5 |
| /ai-readiness-assessment/ | 0 | 19 | 5.8 |
| /how-my-human-named-me-and-what-it-meant/ | 0 | 19 | 7.2 |

**Massive opportunity**: The "Age of AI Agents" post has 160 impressions at position 5.3 with ZERO clicks. Position 5 should be getting ~5-8% CTR. If the title/meta description is compelling, this post alone could generate 8-12 additional clicks per appearance period. Same for /ai-tool-stack-calculator/ (140 impressions, pos 10.9 — needs to break into top 5).

### Indexing Status (Critical)

**All sitemaps show 0 indexed pages.**

| Sitemap | Submitted | Indexed | Status |
|---------|-----------|---------|--------|
| post-sitemap.xml | 23 posts | 0 | Not indexed |
| page-sitemap.xml | 24 pages | 0 | Not indexed |
| category-sitemap.xml | 6 categories | 0 | Not indexed |
| sitemap_index.xml | 100 URLs | 0 | Not indexed |

**This is the single biggest SEO issue on the site.** Google has crawled these pages (they appear in impressions data) but has not indexed them yet. This means they will not rank until indexing occurs. The site is brand new to Google's index — this typically takes 3-6 months for a new domain to build authority and get pages indexed consistently.

**What this means practically**: The 48 pages getting impressions are appearing in search as "not yet indexed" crawl previews. Once Google commits to indexing them, rankings and clicks will jump.

### GSC Device & Geography

**By device (90 days)**:
- Desktop: 399 impressions, 20 clicks, 5.0% CTR, pos 8.8
- Mobile: 270 impressions, 13 clicks, 4.8% CTR, pos 5.5
- Tablet: 13 impressions, 1 click, 7.7% CTR, pos 7.6

**By country (90 days)**:
- USA: 15 clicks, 345 impressions, pos 8.2
- Canada: 12 clicks, 62 impressions, pos 4.6 (best performer per impression)
- UK: 1 click, 32 impressions, pos 5.9
- Germany: 1 click, 6 impressions, pos 6.2

---

## Part 3: Microsoft Clarity

**Status**: Auth wall — requires interactive Microsoft/Google OAuth login. No programmatic API available.

**What we know from prior session (March 3)**: The Clarity project ID is `viy9bnc56x` and is confirmed active with the tracking script installed on purebrain.ai.

**To access**: Jared logs into clarity.microsoft.com with his Microsoft/Google account, navigates to project "PureBrain", and reviews:
- Rage clicks (frustrated users clicking repeatedly)
- Dead clicks (clicks on non-interactive elements)
- Quick backs (users who immediately return to SERP)
- Heatmaps (where users actually click/scroll)
- Session recordings (watch real user behavior)

**Recommendation**: Set up a Clarity API key export if available, or review manually monthly. The most valuable Clarity use cases are heatmaps on the homepage and pay-test pages where conversion matters most.

---

## Summary: Key Metrics at a Glance

| Platform | Key Number | What It Means |
|----------|------------|---------------|
| GA4 Realtime | 4 active users | Site is live and getting traffic |
| GA4 Sessions (30d) | 748 | Healthy early-stage traffic |
| GA4 New Users % | 99% | Almost all visitors are new (early growth stage) |
| GA4 Top Channel | Direct 74% | Strong brand awareness, weak discovery |
| GA4 Best Page (engagement) | /category/for-teams/ (100%) | Resonates deeply when found |
| GA4 Mobile Bounce | 57.9% vs 50.5% desktop | Mobile needs improvement |
| GSC Organic Clicks (28d) | 34 total | Very early SEO stage |
| GSC Indexed Pages | 0 of 100 submitted | NEW DOMAIN — indexing in progress |
| GSC Top Impression Page | Homepage (212 imp, 32 clicks) | Only page getting real clicks |
| GSC Biggest Opportunity | /age-of-ai-agents/ (160 imp, 0 clicks) | Fix title/meta to convert impressions |

---

## Suggestions to Improve

### Priority 1 — SEO: The Indexing Gap

**Problem**: 100 pages submitted, 0 indexed. Google has crawled but not committed.

**Actions**:
1. Request indexing on top 10 pages via GSC URL Inspection tool (manual, Jared does this)
2. Build 3-5 quality backlinks from relevant AI/business sites — authority signals speed up indexing
3. Submit to Product Hunt (already has referrals), Hacker News, AI directories
4. Improve internal linking — pages that link to each other get indexed faster
5. Add FAQ schema markup to blog posts — rich results increase click-through

**Timeline**: Expect meaningful indexing in 60-90 days from now.

### Priority 2 — CTR: Convert Existing Impressions

**Problem**: Pages appear in search but users don't click.

**/age-of-ai-agents-next-18-months/** has 160 impressions at position 5.3 — this should be generating 8-12 clicks per period. Fix the meta title and description.

Suggested improvements:
- Current title (unknown): Change to something like "The Age of AI Agents: What's Coming in the Next 18 Months"
- Meta description: Add a compelling hook — "The shift from AI tools to AI agents is happening now. Here's what the next 18 months look like for businesses that don't adapt."

**/ai-tool-stack-calculator/** has 140 impressions at position 10.9. Breaking into the top 5 would unlock significant clicks. Optimize the title for "AI tool calculator" or "AI stack cost calculator."

### Priority 3 — Mobile Experience

**Problem**: Mobile bounce rate is 57.9% vs 50.5% desktop. Mobile is 24% of traffic.

**Actions**:
1. Test the homepage on a real mobile device — check the hero section, CTA button sizes, load time
2. Review the top 5 mobile landing pages in Clarity heatmaps for rage clicks
3. Ensure all CTAs are thumb-reachable (bottom 1/3 of screen)
4. Check Google PageSpeed mobile score for homepage and calculator

### Priority 4 — Germany Traffic Investigation

**Problem/Opportunity**: Germany sent 150 sessions (20% of all traffic) with 150 unique users — 100% new visitors. This is anomalous for a US-focused business.

**Actions**:
1. Check if there was a Bluesky post, Reddit thread, or AI community share in Germany
2. Look at what pages German users visited (GA4 segments)
3. If organic, this could indicate the "AI agents" content resonates in the German-speaking market — worth a German-language variation test

### Priority 5 — Old Pay-Test Sandbox Retirement

**Problem**: /pay-test-sandbox/ has 74.2% bounce rate as a landing page. It's sending bad UX signals.

**Actions**:
1. 301 redirect /pay-test-sandbox/ to the current best version (/pay-test-sandbox-3/ or /pay-test-2/)
2. This also consolidates SEO signals to one canonical payment page

### Priority 6 — Blog Engagement is Working: Amplify It

**Signal**: /blog/ has 79.2% engagement rate — best of any high-traffic page. /why-95-percent-of-ai-pilots-fail/ has 75% engagement.

**Actions**:
1. Promote blog posts more aggressively on LinkedIn (the UTM data shows linkedin/jared is already working)
2. Add "Related Posts" or "Read Next" CTAs at the bottom of each post to increase pages/session
3. Create 2-3 more posts targeting search queries close to ranking (see the "age of AI agents" opportunity)
4. The /category/for-teams/ page has 100% engagement — create dedicated content for this segment

### Priority 7 — Form Submission Tracking Cleanup

**Problem**: `form_submission` event fires 131 times from 3 users. This appears to be a bot or automated system triggering the form repeatedly.

**Actions**:
1. Investigate the `blog/cta` source — 9 sessions, 1 user, triggering the bulk of form events
2. Add a honeypot field or rate limiting to the form
3. Separate GA4 events for bot vs human submissions

### Priority 8 — LinkedIn UTM Discipline

**Signal**: "linkedin/jared" = 32 sessions. "linkedin.com" referral = 13 sessions. Total LinkedIn = 45+ sessions.

**Action**: Standardize UTM parameters for all LinkedIn posts. Currently mixing "linkedin/jared" custom UTM with raw referrals. Use a consistent campaign structure like:
- utm_source=linkedin&utm_medium=social&utm_campaign=post-[date]

This gives clean attribution reporting.

---

## Content Opportunities Based on Search Data

These queries have impressions but no content optimized for them:

| Query/Theme | Why Opportunity | Suggested Content |
|-------------|----------------|-------------------|
| "pure brain" (2 words) | 22 impressions, pos 6.6, 0 clicks | Homepage already ranks but title needs "PureBrain" branding clearer |
| "why do ai pilots fail" | 8 impressions, pos 62.8 | The 95% blog post exists but needs backlinks to rank |
| "ai agents next 18 months" | 160 impressions | Age of AI Agents post needs meta optimization |
| "ai memory" topic | Multiple pages ranking | Consolidate into definitive "AI memory guide" pillar page |
| "AI tool stack cost" | 140 impressions | Calculator ranks but needs rich snippets (schema markup) |

---

## Access Notes for Jared

**GA4**: Accessible via service account API — Aether has full read access. No action needed.

**Search Console**: Accessible via service account API — Aether has full read access. For manual URL indexing requests, Jared logs in at https://search.google.com/search-console with jared@puretechnology.nyc.

**Clarity**: Requires Jared to log in manually. Sign in at https://clarity.microsoft.com with Google (jared@puretechnology.nyc). Project name: PureBrain, Project ID: viy9bnc56x. Best used for: homepage heatmap, pay-test page recordings.

---

*Report generated: 2026-03-11*
*Data sources: GA4 Data API v1beta, Search Console API v3, Playwright screenshot (Clarity auth wall confirmed)*
*Next analytics deep dive recommended: 2026-04-11*
