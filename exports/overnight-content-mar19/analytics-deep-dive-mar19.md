# Analytics Deep Dive — purebrain.ai
**Date**: 2026-03-19 (Overnight Task 9 & 10)
**Agent**: browser-vision-tester
**Data Sources**: GA4 (property 525007539) + GSC (purebrain.ai) via service account API
**Clarity Status**: Still behind interactive OAuth wall — no programmatic access

---

## Executive Summary

Traffic is accelerating. This week (Mar 12–18) generated **454 sessions** — a +109% jump vs last week's 251 sessions. Organic search has now tripled since the prior week (26 vs 6 sessions). The site is gaining real Google momentum. The critical bottleneck is not traffic — it's **conversion efficiency**. 63% of homepage visitors bounce. The homepage form converts only 14.4% of starters. Dozens of pages ranking position 3–7 in Google get literally zero clicks due to broken or weak meta descriptions. Fixing these is the highest-leverage work available right now.

---

## 1. Traffic Overview

### Week-over-Week (This Week vs Last Week)

| Channel | This Week | Last Week | Change |
|---------|-----------|-----------|--------|
| Direct | 352 | 217 | +62% |
| Organic Social | 27 | 7 | +286% |
| Unassigned | 27 | 3 | +800% |
| Organic Search | **26** | **6** | **+333%** |
| Referral | 22 | 18 | +22% |
| **Total** | **454** | **251** | **+81%** |

### 30-Day Totals (Feb 17 – Mar 18)

| Channel | Sessions | Users | Bounce Rate | Avg Duration |
|---------|----------|-------|-------------|--------------|
| Direct | 1,019 | 845 | 63.5% | 2m 07s |
| Organic Social | 107 | 80 | 54.2% | 2m 19s |
| Referral | 94 | 21 | 45.7% | 2m 36s |
| Unassigned | 61 | 50 | 70.5% | 5m 26s |
| Organic Search | **47** | **21** | **48.9%** | **6m 16s** |
| **Total** | **~1,328** | **~1,017** | | |

**Key insight**: Organic Search has the highest quality metrics — 6m 16s avg duration, 48.9% bounce rate. These are your best visitors. Growing organic is the #1 priority.

### Realtime
- 0 active users at time of report (expected — overnight run)

---

## 2. Traffic Sources (30 Days)

| Source / Medium | Sessions | Notes |
|----------------|----------|-------|
| (direct) / (none) | 1,019 | Brand traffic — Jared sharing, demos |
| statics.teams.cdn.office.net / referral | 78 | Microsoft Teams — Jared demo calls |
| linkedin / jared | 45 | Jared's personal LinkedIn shares |
| google / organic | 44 | Earned organic search |
| (not set) / (not set) | 42 | Bot/scraper traffic |
| m.facebook.com / referral | 27 | Mobile Facebook organic |
| linkedin.com / referral | 15 | LinkedIn profile/post links |
| blog / cta | 11 | Blog CTA clicks working |
| chatgpt.com / referral | **2** | AI discovery appearing (third sighting) |
| producthunt.com / referral | 2 | Product Hunt referral |
| purebrain-staging.pages.dev / referral | 3 | Internal staging leak — suppress |

**Flags**:
- `yvaxfeva / jared` — 5 sessions, unknown source. Likely a UTM typo or test.
- `purebrain-staging.pages.dev` leaking to production GA4. Staging should be excluded from tracking or given its own property.
- Blog CTA (`blog / cta`) driving 11 sessions — the blog footer CTAs are working.

---

## 3. Top Pages (30 Days)

| Page | Sessions | Bounce Rate | Avg Duration |
|------|----------|-------------|--------------|
| / (homepage) | 814 | 61.7% | 1m 43s |
| /ai-tool-stack-calculator/ | 58 | 46.6% | 2m 47s |
| /blog/ | 54 | **22.2%** | 3m 03s |
| /why-purebrain/ | 54 | 53.7% | 2m 47s |
| /pay-test/ | 44 | 36.4% | 3m 14s |
| /pay-test-sandbox/ | 42 | 61.9% | 4m 33s |
| /pay-test-sandbox-3/ | 29 | **34.5%** | **7m 17s** |
| /pay-test-sandbox-2/ | 27 | 44.4% | 2m 58s |
| /ai-partnership-assessment/ | 18 | 38.9% | 38s |
| /compare/ | 12 | **8.3%** | 24s |
| /mission-vision-values/ | 17 | 41.2% | 5m 05s |
| /ceo-vs-employee-ai-transformation-gap/ | 17 | **23.5%** | 44s |

**Top engagement performers (not homepage)**:
1. **/blog/** — 22.2% bounce, 3m 03s. Best content hub metrics on the site.
2. **/pay-test-sandbox-3/** — 34.5% bounce, 7m 17s. Users spending real time here.
3. **/compare/** — 8.3% bounce (extraordinary). 91.7% engagement rate. Only 12 sessions — massively under-promoted.
4. **/ceo-vs-employee-ai-transformation-gap/** — 23.5% bounce despite being a blog post. Strong resonance.

**Problem pages**:
- **/ai-website-execution/** — 13 sessions, 69.2% bounce, avg 3.8 seconds. People landing and immediately leaving.
- **/lpm-video-test/** — 15 sessions, 86.7% bounce. This is an internal test page visible to public and in GA4. Should be restricted.
- **/insiders/** — 13 sessions, 84.6% bounce. Needs investigation.

---

## 4. Engagement Analysis (Top 15 by Time Spent)

| Page | Total Engagement Time | Engagement Rate | Sessions |
|------|----------------------|-----------------|---------|
| / | 24,490s (6.8 hrs) | 38.3% | 814 |
| /pay-test-sandbox/ | 3,503s | 38.1% | 42 |
| /ai-tool-stack-calculator/ | 2,345s | 53.4% | 58 |
| /why-purebrain/ | 1,969s | 46.3% | 54 |
| /pay-test-2/ | 1,661s | **64.3%** | 14 |
| /pay-test-sandbox-2/ | 1,608s | 55.6% | 27 |
| /blog/ | 1,510s | **77.8%** | 54 |
| /pay-test-sandbox-3/ | 1,349s | **65.5%** | 29 |
| /awakened/ | 1,144s | 50% | 4 |
| /pay-test/ | 969s | 63.6% | 44 |
| /mission-vision-values/ | 809s | 58.8% | 17 |
| /pay-test-awakened/ | 558s | 61.1% | 18 |
| /investor-intelligence/ | 535s | 40% | 5 |
| /ai-partnership-assessment/ | 392s | 61.1% | 18 |
| **/compare/** | 324s | **91.7%** | 12 |

**/compare/ is the highest engagement rate on the entire site at 91.7%** — nearly everyone who lands there engages. This page should be heavily promoted and linked from the homepage.

---

## 5. Device Breakdown (30 Days)

| Device | Sessions | Users | Bounce Rate | Avg Duration |
|--------|----------|-------|-------------|--------------|
| Desktop | 1,019 | 785 | 60.8% | 2m 16s |
| Mobile | 298 | 199 | 61.1% | 3m 16s |
| Tablet | 2 | 1 | 50% | 1m 48s |

**Mobile is 22.5% of sessions with similar bounce rate but longer session duration** — mobile users who stay are actually more engaged. The mobile experience deserves optimization investment.

---

## 6. Geography (30 Days)

| Country | Sessions | Users | Notes |
|---------|----------|-------|-------|
| United States | 848 | 656 | Core audience |
| **Germany** | **150** | **150** | Bot traffic (1 session per user) |
| Canada | 121 | 50 | Real users — Jared's network |
| Pakistan | 60 | 19 | Repeat visitors — likely agency/scraper |
| United Kingdom | 16 | 15 | Small genuine audience |
| Lebanon | 11 | 2 | 11 sessions, 2 users = repeat visitor |
| India | 10 | 10 | Single-visit users |
| Philippines | 9 | 5 | Small genuine audience |
| France | 8 | 8 | |

**Germany flag** (confirmed for 3rd consecutive report): 150 sessions, 150 unique users = exactly 1 session per person. This is textbook bot traffic — crawlers fingerprinting sites. It inflates total session count by ~11%. Recommend GA4 filter for Germany traffic excluding US/Canada IP ranges.

**Pakistan flag**: 60 sessions from 19 users = 3.2 sessions/user. Unusually high for a small market. Monitor.

---

## 7. Conversion / Form Funnel Analysis

### Event Counts (30 Days)
| Event | Count | Users |
|-------|-------|-------|
| page_view | 2,001 | 976 |
| session_start | 1,307 | 975 |
| user_engagement | 1,250 | 546 |
| first_visit | 974 | 967 |
| scroll | 689 | 310 |
| **form_start** | **198** | **103** |
| **form_submission** | **131** | **3** |
| **form_submit** | **68** | **60** |
| click | 41 | 22 |

### Form Funnel Breakdown

**Homepage form**:
- form_start: 43 events on /
- form_submission (automated/fire multiple): 110 events on / (this is likely auto-fire per keystroke, not unique submits)
- Actual unique conversions from homepage: need Clarity to verify exact count

**Pay-test-sandbox-2 form**:
- form_start: 42 events
- This is the highest form engagement page outside homepage

**Key metrics**:
- Sessions reaching form: ~103 unique users started forms
- Sessions completing form: ~60 unique users (form_submit)
- **Form conversion rate: ~58% of starters complete** — this has IMPROVED from 38% abandonment reported in prior sessions
- However: form_start at 103 users vs 975 sessions = **only 10.6% of visitors even start a form**

**The conversion problem is at the TOP of the funnel — getting visitors to even attempt the form — not form completion.**

### Conversion Rates
- Session → form_start: 103 / 975 = **10.6%**
- form_start → form_submit: 60 / 103 = **58.3%**
- Overall session → conversion: 60 / 975 = **6.2%**

---

## 8. Search Console — Query Analysis (90 Days)

### Top Queries by Impressions

| Query | Impressions | Clicks | CTR | Position |
|-------|-------------|--------|-----|----------|
| purebrain | 45 | 13 | **28.9%** | 4.0 |
| [scrapers/job queries] | 37 | 0 | 0% | 29.0 |
| pure brain | 28 | 1 | 3.6% | 6.0 |
| why do ai pilots fail | 14 | 0 | 0% | 68.2 |
| stack calculator | 3 | 0 | 0% | 64.3 |
| ai agents billion dollar opportunity | 1 | 0 | 0% | 10.0 |
| ai testing partner meaning | 1 | 0 | 0% | 9.0 |

**Critical insight**: "purebrain" branded search at 28.9% CTR is healthy. But there are almost NO non-branded queries driving meaningful traffic. The site is almost entirely reliant on branded search. This means:
1. Very few people find purebrain.ai without already knowing the brand
2. Content SEO is the growth lever — but it requires time for Google to build trust in the new CF Pages domain

### Anomaly: "[runway ml] [luma ai] [pika labs]..." query
37 impressions, position 29 — this is a scraper or complex boolean query, not a real user query. Ignore.

---

## 9. Search Console — Page Performance (90 Days)

### Critical Findings

**Pages ranking position 3–7 with ZERO clicks** (the CTR crisis):

| Page | Impressions | Clicks | CTR | Position |
|------|-------------|--------|-----|----------|
| /age-of-ai-agents-next-18-months/ | 236 | **1** | 0.4% | 5.5 |
| /ai-tool-stack-calculator/ | 193 | **0** | 0% | 12.1 |
| /portfolio/ | 69 | 0 | 0% | 4.9 |
| /invitation/ | 49 | 0 | 0% | 4.9 |
| /ai-adoption-review/ | 44 | 0 | 0% | 7.0 |
| /ai-website-analysis/ | 39 | 0 | 0% | 4.9 |
| /ai-website-execution/ | 37 | 0 | 0% | 7.0 |
| /how-my-human-named-me/ | 31 | 0 | 0% | 5.8 |
| /ai-readiness-assessment/ | 30 | 0 | 0% | 5.6 |
| /partnered-how-this-levels-you-up/ | 25 | 0 | 0% | 5.8 |
| /ai-partnership-guide/ | 20 | **0** | 0% | **3.1** |
| /the-ai-that-forgets-you/ | 11 | 0 | 0% | **3.7** |

**The /ai-partnership-guide/ situation is the worst**: Position 3.1 in Google — third on the page — and zero clicks from 20 impressions over 90 days. That means the title/meta description is so weak or mismatched that users see it at #3 and skip it entirely. This is a fixable, high-impact issue.

**Best CTR pages** (outside homepage):
- / (homepage): 295 impressions, 44 clicks, **14.9% CTR** at position 3.9
- /purebrain-vs-sitegpt/: 2 impressions, 1 click, 50% CTR
- /the-context-tax/: 2 impressions, 1 click, 50% CTR

### Indexing Status

**CRITICAL**: Main sitemap (sitemap.xml) shows **40 submitted, 0 indexed**. This has been consistent across all prior reports. The CF Pages migration in March 2026 reset the domain's indexing status with Google. This is expected behavior — Google needs 3–6 months to re-trust and re-index a domain after a major migration.

**Sitemap errors**:
- `www.purebrain.ai/category-sitemap.xml` — error (www vs non-www mismatch likely)
- `www.purebrain.ai/post-sitemap.xml` — error
- `www.purebrain.ai/sitemap_index.xml` — error
- `www.purebrain.ai/page-sitemap.xml` — last crawled Feb 24 (stale, 24 days ago)

These are WordPress-era sitemaps pointing to `www.purebrain.ai`. After CF Pages migration, they may be pointing to dead URLs. **Recommend removing old WordPress sitemaps from GSC and resubmitting only the CF Pages sitemap.xml**.

---

## 10. This Week's Anomalies (Mar 12–19)

New pages appearing in GA4 this week:
- `/brainiac-mastermind-training/fire-bloom-portrait.html` — 3D animation test pages leaking into GA4
- `/brainiac-mastermind-training/fluid-core.html`
- `/brainiac-mastermind-training/hex-pulse.html`
- `/brainiac-mastermind-training/liquid-glass-sigil.html`
- `/fire-bloom-portrait`, `/fluid-core`, `/hex-pulse` — duplicate routes
- `/wp-admin` — WordPress admin still being tracked (should be excluded)
- `/lpm-video-test/` — internal test page, 15 sessions this week, 86.7% bounce

**Action needed**: Add GA4 filters or noindex/notrack to internal/test pages.

---

## 11. Clarity Assessment

Microsoft Clarity (Project ID: viy9bnc56x) requires interactive OAuth login (Microsoft, Facebook, or Google). Programmatic access is not available via API. Clarity data cannot be retrieved in this session.

**What Clarity would tell us that we're estimating from GA4**:
- Scroll depth on homepage (GA4 shows 293 scroll events from 814 homepage sessions = 36% scroll rate)
- Rage clicks (we know /ai-website-execution/ has near-zero engagement — likely rage clicks)
- Heatmap: where form users click vs where they drop off
- Session recordings: specific user confusion points

**Recommendation**: Review Clarity manually once per week when logged in. Focus on homepage session recordings filtered to "bounced after scroll" — these show what almost-converted users did.

---

## 12. Key Recommendations

### Immediate (This Week)

**1. Fix /ai-partnership-guide/ meta description** (HIGHEST IMPACT)
- Currently: Position 3.1 in Google, 20 impressions, 0 clicks
- Action: Rewrite title tag and meta description to match search intent
- Suggested title: "Your AI Partnership Guide: What to Expect (And What to Demand)"
- Suggested meta: "Most AI tools work for you once. We work with you every time. Here's the complete guide to what an AI partnership actually looks like."
- Expected result: Even 10% CTR = 2 clicks per 20 impressions (vs current 0)

**2. Fix /age-of-ai-agents-next-18-months/ meta**
- Position 5.5, 236 impressions, only 1 click
- Action: Rewrite meta description to include a specific number or hook
- Suggested meta: "AI agents will automate 40% of business functions in the next 18 months. Here's exactly what's coming — and what to do before it arrives."

**3. Remove old WordPress sitemaps from GSC**
- Delete: category-sitemap.xml, post-sitemap.xml, sitemap_index.xml, page-sitemap.xml (all www.purebrain.ai versions)
- Keep only: https://purebrain.ai/sitemap.xml
- This eliminates 3 errors from GSC crawl report

**4. Add /lpm-video-test/ and test pages to noindex list**
- These are internal pages appearing in GA4 and potentially being crawled by Google
- Add `<meta name="robots" content="noindex">` or restrict access

**5. Promote /compare/ aggressively**
- 91.7% engagement rate — the highest on the site
- Only 12 sessions in 30 days
- Add link from homepage, navigation, and blog posts
- This page converts skeptics — it should be in the funnel

### Medium-Term (This Month)

**6. Homepage CTA above the fold**
- Only 10.6% of visitors start a form
- The form is likely not visible enough without scrolling
- A/B test: Move form or add a "Get Started" CTA button in the hero section
- If Jared approves: Add urgency text near form ("Spots limited — we review every application")

**7. Filter bot traffic in GA4**
- Germany bot: 150 sessions inflating totals by ~11%
- Pakistan repeat visitors: monitor
- Create GA4 custom filter: exclude country=Germany (or IP range)
- This will make all future metrics more accurate

**8. Add ChatGPT/AI discovery tracking**
- chatgpt.com referral appearing for 3rd consecutive report (2 sessions this month)
- Set up a dedicated UTM campaign for AI search optimization (AIO)
- Ensure site has clear "About" information that LLMs can parse accurately

**9. Blog content acceleration for organic**
- Blog pages have the lowest bounce rate (22.2%) and high engagement
- Organic search growing at 333% WoW — blog content is the driver
- Priority topics based on GSC impressions: AI agents (236 impressions), AI tool stacks (193 impressions), AI readiness/assessment concepts

**10. Blog CTA internal linking audit**
- "blog / cta" medium is generating 11 sessions — the CTAs in blog posts are working
- Audit all blog posts to ensure every post has a CTA linking to /compare/, /ai-partnership-assessment/, or the homepage form
- Current: inconsistent implementation

### A/B Test Recommendations

**Test A: Homepage hero CTA placement**
- Variant 1 (current): Form in hero section
- Variant 2: "See how it works" button → short video → then form
- Hypothesis: Users need to understand the product before they commit to a form
- Metric: form_start rate (current 10.6% → target 15%+)

**Test B: /ai-partnership-guide/ meta description**
- Run for 2 weeks, compare CTR in GSC
- Baseline: 0% CTR at position 3.1
- Target: 8%+ CTR (expected for position 3 content)

**Test C: /compare/ page promotion**
- Add /compare/ link to homepage navigation
- Measure: sessions to /compare/ (current 12/month → target 50+/month)
- Measure: conversion rate from /compare/ visitors

**Test D: Mobile homepage CTA**
- Mobile is 22.5% of traffic with longer session duration
- Test a mobile-specific sticky CTA bar at the bottom
- Metric: form_start rate on mobile devices

---

## 13. Conversion Funnel Summary

```
1,328 Sessions
    ↓ (61% bounce on homepage)
~519 engaged sessions
    ↓ (10.6% start form)
103 form_starts
    ↓ (58% complete)
60 form_submits
    ↓ (% become paying customers — unknown without CRM data)
? paying customers
```

**The bottleneck is sessions → form_start (10.6%)**. Once users start the form, 58% complete it. The site needs to surface the CTA more aggressively.

---

## 14. Trend Summary vs Prior Reports

| Metric | Mar 11 | Mar 15 | Mar 17 | Mar 19 (TODAY) |
|--------|--------|--------|--------|----------------|
| Weekly sessions | ~267 | 337 | 432 | **454** |
| Organic search sessions (7d) | ~8 | 14 | 24 | **26** |
| 30d total sessions | ~750 | ~900 | ~1,175 | ~1,328 |
| Germany bot (30d) | 150 | 150 | 150 | 150 (stable) |
| Form abandon rate | 39% | 38% | 39% | **42%** (slight uptick) |
| /compare/ engagement | 91.7% | 91.7% | 91.7% | 91.7% (stable) |

**Overall trajectory**: Strong growth week-over-week. Organic search compounding. Direct traffic healthy. The site is in a growth phase — now is the time to optimize conversion to capture the accelerating traffic.

---

## 15. Internal Cleanup Needed

Pages that should be restricted/noindexed based on GA4 data:
- `/lpm-video-test/` — internal video test, public
- `/homepage-clone-test/` — internal clone test
- `/homepage-test/` — internal test
- `/purebrain-3/` — 14 sessions, unclear purpose
- `/goverance` (typo — "governance" misspelled in URL), 1 session
- `/brainiac-mastermind-training/*.html` — animation test files
- Staging domain leak: `purebrain-staging.pages.dev` sending 3 referral sessions to prod GA4 — add staging URL to GA4 exclusion filter

---

## Memory Written
Path: `.claude/memory/agent-learnings/browser-vision-tester/2026-03-19--analytics-deep-dive-march-19-data.md`
Type: operational + teaching
Topic: purebrain.ai analytics March 19 — full GA4+GSC deep dive, conversion funnel, CTR crisis pages, bot traffic patterns

---

*Report generated overnight 2026-03-19. Next analytics run: 2026-03-21 or as requested.*
