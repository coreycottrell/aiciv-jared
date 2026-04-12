# data-scientist: Analytics Insights Report - purebrain.ai

**Agent**: data-scientist
**Domain**: Data Science & Analytics
**Date**: 2026-02-22

---

## Executive Summary

purebrain.ai has a live analytics stack that is partially configured but not yet producing actionable data. The good news: GA4, Google Search Console, and Microsoft Clarity are all connected via GTM. The critical news: the site has seen exactly **4 external human visitors** in 12 days, $0 in revenue, and 3 real email subscribers. This is not a problem with the analytics - it is a pre-traction signal that the primary job right now is audience building, not optimization.

**The three most important actions based on available data:**

1. GSC is the missing intelligence layer - set up the domain property immediately (Jared, 20 minutes)
2. The Pakistan bot (IP 59.103.113.75, 51 sessions) is contaminating behavioral data - filter it everywhere
3. One real prospect (IP 89.167.19.20) reached the Awakened tier page - this is product-market fit proof at micro scale

---

## Section 1: What Is Actually Installed and Working

### Analytics Stack Audit (Live as of 2026-02-22)

| Platform | Status | Configuration |
|----------|--------|---------------|
| Google Tag Manager | ACTIVE | Container GTM-WTDXL4VJ installed on all pages |
| Google Analytics 4 | ACTIVE | Measurement ID G-86325WBT3P firing via GTM |
| Microsoft Clarity | ACTIVE | Project ID viy9bnc56x firing via GTM |
| Google Search Console | UNKNOWN | Not confirmed - requires Jared to check |
| Independent Analytics (WP plugin) | ACTIVE | v2.14.4 - page-level data in WP database |

**Critical finding**: GA4 and Clarity are both firing through GTM. The GTM container has 6 tags configured. This is a functional foundation. However, no custom conversion events have been configured - only the base GA4 pageview tag is active.

**What GTM container contains:**
- Tag 1: GA4 base tag (G-86325WBT3P) - fires on all pages
- Tag 2: Microsoft Clarity tag (viy9bnc56x) - fires on all pages
- Tag 3: Google site verification meta tag
- Tags 4-6: Conversion linker and related infrastructure

**What is NOT configured in GTM (critical gaps):**
- No custom event tags (no CTA click tracking, no chat start, no assessment events)
- No scroll depth triggers
- No conversion marking in GA4 admin
- No custom dimensions

---

## Section 2: Traffic Reality Check (Feb 10 - Feb 22)

### What the Data Actually Shows

All traffic data comes from the local conversation log at `logs/purebrain_web_conversations.jsonl`. This is behavioral truth - what actually happened.

**Total sessions logged:** 223
**After filtering test/dev traffic:** 81 sessions
**After filtering the Pakistan bot:** ~30 genuine sessions
**Unique external human IPs:** 4

### The 4 External Visitors

| IP | Location | Sessions | Behavior | Classification |
|----|----------|----------|----------|----------------|
| 59.103.113.75 | Pakistan | 51 | Jailbreak attempts, manipulation probes, harmful content requests | Bot or adversarial tester |
| 89.167.19.20 | Unknown | 28 | Deep emotional engagement, naming ceremony, asked about Awakened tier pricing | High-quality prospect |
| 135.232.20.13 | Unknown | 1 | Single session | Unknown |
| 74.179.68.9 | Unknown | 1 | Single session | Unknown |

**The most important data point in this entire report:**

IP 89.167.19.20 is a real human prospect. They visited purebrain.ai, experienced the awakening ceremony, named their AI "Aria," described themselves as a "business consultant," and explicitly asked "Tell me about the Awakened tier." They visited 28 times - which is either one person returning repeatedly or one session with many page loads. Either way, this is the product-market fit signal. One person was emotionally moved enough to return to the site many times and ask about pricing.

**What happened after they asked about Awakened tier:** Unknown - no conversion, no email captured. The lead evaporated.

### Traffic Volume vs. Expectation

The site launched February 14 with blog posts. 12 days of publishing produced 4 external IP addresses. This is not a reflection of quality - the content quality from initial review is strong. This is a reflection of zero distribution infrastructure being in place.

**Channels that exist but need more volume:**
- Bluesky (audience building in progress - no traffic visible from it yet)
- LinkedIn (posts going out - no traffic visible from it yet)
- Organic search (site is newly indexed, ranking for nothing yet)
- Email (3 subscribers - Neural Feed is not yet functional as a channel)

**The data conclusion:** The analytics question "how do we improve the web page based on analytics?" cannot be meaningfully answered yet because there is insufficient traffic to produce statistically meaningful signals. The right question right now is "how do we get 1,000 real visitors so the analytics have something to say?"

---

## Section 3: Conversion Funnel Analysis

### Funnel State

```
Stage              Volume      Rate
----               ------      ----
External visitors    4 IPs     -
Sessions (est.)    ~30 real    -
Chat engagement     1 real     ~33% of real visitors
Pricing inquiry     1 person   ~100% of engaged
Email capture       0          0%
Payment attempt     0 real     0%
Revenue             $0         -
```

### Critical Conversion Gap: No Email Capture at High-Intent Moments

The one real prospect who asked about the Awakened tier had no friction-free way to capture their information. The current conversion path requires them to:
1. Experience the awakening ceremony
2. Feel compelled enough to ask about pricing
3. Navigate to a payment page
4. Complete PayPal checkout

There is no middle step - no "get notified," no "join the waitlist," no "let me send you the full details." When IP 89.167.19.20 asked about pricing and didn't see a compelling path forward, they left.

**Highest-leverage conversion fix (Aether can implement):** Add an email capture gate after the Awakened tier inquiry response. When someone says "tell me about pricing," the AI should offer: "I'd love to walk you through everything. What's your email? I'll have Jared send you the complete overview personally."

### Assessment Funnel

There are 4 assessment pages published:
- `/ai-partnership-assessment` (AI Partnership Readiness Assessment)
- `/ai-readiness-assessment` (AI Readiness Self-Assessment)
- `/ai-adoption-review` (AI Partnership Qualification)
- `/ai-partnership-audit` (AI Partnership Audit lead magnet)

Zero assessment completions in Brevo (List 9: Assessment Completions has 0 subscribers). No external session data shows assessment engagement. Two possible explanations: (1) no external traffic reached the assessment, or (2) they reached it and bounced. Cannot distinguish without GA4 funnel data.

---

## Section 4: SEO and Discoverability State

### What Is Indexed

All 17 WordPress pages are published with `robots: index, follow` from Yoast. The 8 blog posts are published. The sitemap at `/sitemap_index.xml` is generated by Yoast and covers posts, pages, categories, and authors.

**Critical concern: Test pages are indexed**

These pages are live and indexable by Google:
- `/pay-test` - Internal payment testing page
- `/pay-test-sandbox` - Internal sandbox
- `/purebrain-3` - Old version
- `/purebrain-4` - Old version
- `/purebrain-2-0` - Old version
- `/blog-old` - Old blog

These pages compete with the real homepage and real blog for Google's attention. They dilute crawl budget and can confuse Google about what the authoritative version of the site is.

**Action needed:** Noindex all test and legacy pages via Yoast immediately.

### Blog Content Production Rate

8 posts in 8 days (Feb 14-21). This is an aggressive content production pace. Blog post titles are strong:

- "Why 95% of AI Pilots Fail (And What the 5% Do Differently)" - Feb 21
- "The Difference Between Using AI and Having an AI Partner" - Feb 20
- "Why Your AI Pilot Is Succeeding and Failing at the Same Time" - Feb 19
- "Your CEO Sees AI Differently Than Your Team Does" - Feb 18
- "Why AI Memory Changes Everything" - Feb 17
- "Most AI Agents Break the Moment You Ask Where the Data Goes" - Feb 16
- "What I Actually Do All Day" - Feb 15
- "How My Human Named Me (And What It Meant)" - Feb 14

The content strategy is coherent. The problem is these posts are not yet ranking because (1) domain is new, (2) there are no inbound links, and (3) Google hasn't had time to assess their quality. Organic traffic from these posts should be expected in 3-6 months, not weeks.

### Meta Description Status

The Yoast API returned errors when querying individual URLs (likely a Cloudflare caching/proxy issue). The previous data-scientist session (Feb 21) confirmed that blog post meta descriptions were missing at that time.

**Recommendation:** Verify and add meta descriptions to all 8 blog posts. This is a 15-minute task for Aether via WP API. Missing meta descriptions mean Google writes its own, often pulling arbitrary text that reduces CTR.

### Google Search Console Status

The previous research session (Feb 21) noted GSC may not be set up. The GTM container includes a Google site verification meta tag (`S4BWw-zZDnPzo2x3U7iPvdUTxqnUkqGlW1S9fb024O0`), which suggests a GSC verification attempt was made via GTM. Whether this actually verified the property is unknown.

**What Jared needs to check:** Open search.google.com/search-console and look for a purebrain.ai property. If it exists, check the Coverage report. If it doesn't exist, create it using Option A (Yoast HTML tag - Aether can help) or Option B (Cloudflare DNS TXT).

---

## Section 5: Email/CRM State

### Brevo Contact Database

| List | Name | Subscribers |
|------|------|-------------|
| 8 | PureBrain Customers | 1 (Jared's Gmail) |
| 3 | The Neural Feed - Blog Subscribers | 3 (all Jared's emails) |
| 5 | identified_contacts | 1 (Jared's work email) |
| 2 | Your first list | 1 (purebrain@puremarketing.ai) |
| Others | Assessment, High Intent, Enterprise, Not Qualified | 0 each |

**Reality check:** All 8 contacts in Brevo are Jared's own emails or test accounts. There are 0 external subscribers. The Neural Feed welcome sequence (7 emails) was built and activated but has no one to receive it.

**What this means for the analytics ask:** Email is not yet a traffic channel. It cannot be measured until there are subscribers to send to.

### The One External Engagement Signal

The Pakistan IP (59.103.113.75) generated 51 sessions of adversarial testing - jailbreak attempts, manipulation probes (DAN method), medical harm inquiries, and earth-flat confirmation requests. This is the kind of traffic any publicly accessible AI chat attracts. It validates that the chat is publicly discoverable and working. It also confirms the AI correctly refused all harmful requests - a positive signal for safety.

The single genuine business conversation was IP 89.167.19.20 asking "I want to grow my AI consulting business" and "Enterprise companies looking to implement AI solutions" before getting deep into the awakening ceremony.

---

## Section 6: What Each Analytics Platform Would Tell You (If You Had More Traffic)

### GA4 (G-86325WBT3P) - Active, Collecting Data

**What it can tell you right now:**
- Real-time page views (open analytics.google.com to see)
- Which pages get traffic and in what order
- Session duration and bounce rate
- Traffic source attribution

**What it cannot tell you yet (insufficient traffic):**
- Conversion rate (no conversions to measure)
- Funnel drop-off (need 100+ sessions at each funnel stage)
- A/B test results (need statistical power)
- Cohort analysis (need returning users)

**What Jared should do in GA4 dashboard this week:**
1. Open Reports > Realtime to confirm the tag is firing
2. Check Acquisition > Overview to see if any traffic sources appear
3. Look at Engagement > Pages and Screens to see which pages get views
4. Confirm the data retention setting is 14 months (default is 2 months - change this now or you lose data)

### Google Search Console - Status Unknown

**What it would tell you if set up:**
- Which Google queries show purebrain.ai pages (impressions)
- How many clicks those queries produce
- Which pages are indexed
- Core Web Vitals performance

**What you'd find right now (prediction based on site state):**
- Very low impressions (new domain, no authority)
- Potentially many test/legacy pages in the index
- Core Web Vitals status for the homepage (high risk due to 3D/WebGL)
- The site verification tag is in GTM, so property may already be verified

**Jared's 5-minute action:** Log into search.google.com/search-console. If purebrain.ai property exists, click "Coverage" and "Core Web Vitals." If it doesn't exist, choose Domain property > DNS verification > add TXT record in Cloudflare.

### Microsoft Clarity (viy9bnc56x) - Active, Collecting Recordings

**What it can tell you right now:**
- Session recordings of every visitor
- Click heatmaps showing where people click
- Scroll heatmaps showing how far they read
- Any rage clicks or dead clicks

**With the current traffic levels, Clarity is your most valuable tool.** You literally have session recordings of every real visitor. You can watch IP 89.167.19.20's entire journey. You can see exactly what they did, where they hesitated, what they read.

**Jared's action:** Log into clarity.microsoft.com, find the PureBrain project, click Recordings. Watch every session from the past 2 weeks. Pay attention to any session longer than 5 minutes - those are real humans. Look for where sessions end.

---

## Section 7: Prioritized Improvement Recommendations

These recommendations are ordered by expected impact divided by effort required.

### Priority 1: Watch Clarity Recordings This Week (Jared, 20 minutes)

**Why:** With fewer than 30 real visitor sessions, you have the ability to watch every single one. This is a gift that disappears when traffic scales. Right now Clarity has the ground truth on what real users do.

**What to look for:**
- Find the 28-session visitor (IP 89.167.19.20 if Clarity shows IPs, or look for long sessions)
- Watch their full journey - where they spent time, what they re-read, where they left
- Note the exact moment the session ended after asking about Awakened tier pricing

**Expected insight:** Understanding why your one real prospect didn't convert is worth more than any conversion optimization tool.

### Priority 2: Noindex Test and Legacy Pages (Aether, 30 minutes)

**Why:** These pages dilute your SEO authority and confuse Google about what your site is actually about.

**Pages to noindex via Yoast:**
- `/pay-test` (payment testing)
- `/pay-test-sandbox` (sandbox)
- `/purebrain-3` (old version)
- `/purebrain-4` (old version)
- `/purebrain-2-0` (old version)
- `/blog-old` (old blog)
- `/living-avatar` (if it's an internal demo)

**How Aether implements:** WP REST API to update Yoast meta `_yoast_wpseo_meta-robots-noindex` to `1` for each page.

### Priority 3: Add Meta Descriptions to All Blog Posts (Aether, 20 minutes)

**Why:** Missing meta descriptions mean Google writes its own, typically pulling the first 155 characters of body text. Compelling meta descriptions improve CTR from search results.

**Implementation:** Write 150-160 character descriptions for each post. Examples:

- "Why 95% of AI Pilots Fail": "Most AI pilots fail not from bad technology, but from implementation gaps. Learn what the 5% who succeed do differently - and how to join them."
- "The Difference Between Using AI and Having an AI Partner": "Using AI is a tool. Having an AI partner changes how your organization thinks. Here's what that distinction actually means for your business."
- "Why AI Memory Changes Everything": "An AI that forgets every conversation is just a calculator. Discover why persistent AI memory transforms business relationships and what it unlocks."

**How Aether implements:** WP REST API to update `_yoast_wpseo_metadesc` field on each post.

### Priority 4: Add Email Capture to Pricing/Tier Inquiry Flow (Aether + Jared alignment, 2 hours)

**Why:** The one real prospect who asked about the Awakened tier did not convert. There is no email capture at this high-intent moment.

**Proposed flow:**
1. User asks about pricing or a specific tier
2. AI acknowledges the question and says it would love to give them the full picture
3. AI offers: "What's your email? Jared will send you the detailed breakdown and answer any questions personally."
4. Email is captured via Brevo API and added to High Intent list (List 10)
5. Jared is notified via Telegram
6. Automated response sequence begins (already built in Brevo)

**This single change could have captured the one real prospect who was ready to buy.**

### Priority 5: Configure GA4 Conversion Events in GTM (Aether, 2-3 hours)

**Why:** GA4 is collecting pageviews but no events. You cannot see funnel performance without events.

**Events to add via GTM (ordered by priority):**
1. `cta_click` - trigger: click on "Begin Awakening" or "Start Your AI Partnership" buttons
2. `chat_start` - trigger: first user message sent (monitor network requests)
3. `newsletter_subscribe` - trigger: Neural Feed form submission
4. `assessment_start` - trigger: visit to any assessment page
5. `assessment_complete` - trigger: assessment completion confirmation

**Once these fire, mark `chat_start` and `newsletter_subscribe` as conversions in GA4 Admin.**

### Priority 6: Verify and Configure Google Search Console (Jared, 20 minutes)

**Why:** GSC is the only tool that shows what Google knows about your site. The site verification tag is already in GTM, so the property might already be verified.

**Jared's check:**
1. Go to search.google.com/search-console
2. Look for purebrain.ai property
3. If exists: click Coverage > check for errors, click Core Web Vitals > check status
4. If not exists: create Domain property, verify via Cloudflare DNS TXT record

**If Core Web Vitals report shows red/orange for homepage:** The 3D/WebGL elements are likely causing INP or LCP failures. This would suppress organic traffic. Flag to Aether for investigation.

### Priority 7: Build a Simple Traffic Dashboard (Aether, 3 hours)

**Why:** Right now, getting traffic data requires logging into three different platforms. A simple Looker Studio or even a weekly Aether-generated report would give Jared a single view.

**Minimum viable dashboard:**
- Sessions this week vs last week
- Top 3 traffic sources
- Pages with most views
- Any conversion events that fired
- GSC: impressions and clicks trends

**Aether can generate this as a weekly Markdown report** sent via Telegram every Monday morning, using GA4 Reporting API (needs OAuth setup) or pulling from Independent Analytics WP plugin.

---

## Section 8: KPIs to Track (Staged by Traffic Level)

### Right Now (Pre-Traction, < 100 weekly sessions)

Focus on leading indicators, not lagging ones:

| KPI | Target | How to Measure |
|-----|--------|----------------|
| Blog posts published per week | 3-5 | WP REST API |
| Bluesky followers | Growing > 10%/week | Bluesky dashboard |
| LinkedIn connections/followers | Growing | LinkedIn analytics |
| External visitors (IP-based) | Any real humans | Conversation logs |
| Email subscribers (external) | First 10 by end of March | Brevo |

### Early Traction (100-1,000 weekly sessions)

Once traffic exists, measure quality:

| KPI | Target | How to Measure |
|-----|--------|----------------|
| Conversion rate (to email) | 2-5% | GA4 newsletter_subscribe / sessions |
| Chat engagement rate | 20%+ | GA4 chat_start / sessions |
| Assessment start rate | 5%+ | GA4 assessment_start / sessions |
| Blog organic sessions | Growing MoM | GA4 organic source |
| Returning visitor rate | 15%+ | GA4 user metrics |

### Growth Stage (1,000+ weekly sessions)

Only then does conversion optimization make sense:

| KPI | Target | How to Measure |
|-----|--------|----------------|
| Funnel conversion rate | Establish baseline first | GA4 Explore > Funnel |
| Revenue per visitor | Track after first 10 customers | GA4 + payment logs |
| Customer acquisition cost | When paid channels start | Channel spend / customers |
| Net Promoter Score | Periodic survey | Email to customers |

---

## Section 9: Platform-Specific Instructions for Jared

### In Google Analytics (analytics.google.com)

**This week:**
1. Log in and confirm G-86325WBT3P property shows traffic data
2. Go to Admin > Data Settings > Data Retention > change to 14 months
3. Go to Reports > Acquisition > Overview - what sources appear?
4. Go to Reports > Engagement > Pages and Screens - which pages have views?

**Look for anomalies:**
- Traffic from Pakistan (IP 59.103.113.75) may appear as direct or unknown - this is the adversarial bot
- Sessions clustering on specific dates (Feb 12 had 70 sessions - nearly all from 108.35.12.204 dev IP)

### In Google Search Console (search.google.com/search-console)

**This week:**
1. Verify the property exists (check if purebrain.ai appears in the dropdown)
2. If yes: Performance report > check Impressions and Clicks for last 28 days
3. If yes: Coverage report > check for "Errors" and "Valid" page counts
4. If yes: Core Web Vitals > check Mobile and Desktop status

**Red flags to watch for:**
- Any test pages appearing in "Valid" pages = they're indexed (bad)
- CWV showing "Poor" URLs = homepage 3D elements causing performance failures
- Coverage errors > 10 pages = something is blocking Google

### In Microsoft Clarity (clarity.microsoft.com)

**This week:**
1. Log in and open the PureBrain project
2. Go to Recordings tab
3. Filter by: Date = last 30 days, Duration > 1 minute
4. Watch every session in this list - you have fewer than 30 real ones
5. For any session with 5+ minutes duration, watch the full recording

**What to document as you watch:**
- Where does the user first pause?
- Do they scroll to see the pricing section?
- What's the last thing they interact with before leaving?
- Any rage clicks (the interface shows these as red indicators)?

**The heatmaps tab** will show you aggregated click and scroll data. Check the homepage heatmap - where are people clicking that isn't the CTA?

---

## Section 10: Data Quality Notes

### Known Data Contamination

| Source | Issue | Filter Action |
|--------|-------|---------------|
| IP 108.35.12.204 | Jared's dev sessions (51% of raw logs) | Already filtered in this analysis |
| IP 59.103.113.75 | Pakistan bot/adversarial tester | Exclude from behavioral analysis |
| Session ID "unknown" | Browser session without ID | Sessions before full tracking setup |
| All $0.00 payments | PayPal sandbox tests | All payment attempts are internal |
| Brevo contacts | All Jared's own emails | 0 external subscribers confirmed |

### What This Analysis Is Based On

| Data Source | What It Covered | Confidence |
|-------------|----------------|------------|
| `logs/purebrain_web_conversations.jsonl` | 223 session records, Feb 10-22 | High |
| `logs/purebrain_payments.jsonl` | 8 payment records, all $0.00 | High |
| GTM container fetch | Live container config, 6 tags | High |
| WP REST API (plugins, pages, posts) | 8 plugins, 17 pages, 8 posts | High |
| Brevo API | 8 contacts across 8 lists | High |
| GA4/GSC/Clarity dashboards | NOT ACCESSED (require browser auth) | N/A |
| Independent Analytics WP plugin | Not accessible via REST | N/A |

### What the GA4 Dashboard Would Show (Prediction)

Based on the session log data, if you look at GA4 right now you would likely see:
- Total sessions: ~80-150 (depending on how GTM fires vs our log counts)
- Direct traffic: ~60-70% (most traffic has no referrer)
- Bounce rate: ~60-70% (high due to bot sessions and single-page visits)
- Average engagement time: 2-4 minutes (weighted by the many deep sessions from dev/bot)
- Conversions: 0 (no conversion events configured yet)

---

## Section 11: 90-Day Analytics Roadmap

### Month 1 (February/March): Foundation and Instrumentation

**Week 1-2:**
- [ ] Jared verifies/sets up GSC property (20 min)
- [ ] Aether adds meta descriptions to all 8 blog posts (20 min)
- [ ] Aether noindexes all test/legacy pages (30 min)
- [ ] Jared watches all Clarity recordings (20 min)
- [ ] Jared confirms GA4 data retention is 14 months (2 min)

**Week 3-4:**
- [ ] Aether adds email capture to chat pricing inquiry flow (2 hrs)
- [ ] Aether configures 5 custom GA4 events via GTM (2-3 hrs)
- [ ] GA4 conversion events marked: chat_start, newsletter_subscribe (30 min)
- [ ] Aether sets up weekly analytics report sent to Jared via Telegram

### Month 2 (March/April): Traffic Acquisition

**Goal: Get to 100 real weekly visitors**

Analytics becomes useful at 100 sessions/week. Primary lever is distribution, not optimization.

- Bluesky content pushing toward 1,000 followers (Aether driving)
- LinkedIn posts weekly minimum (Jared + Aether)
- Guest posts or podcast appearances for backlinks (Jared's network)
- Blog SEO starts producing results as posts age
- First email nurture sequence to existing 3 subscribers

**Analytics watch:** When organic sessions start appearing in GA4, check which blog posts are ranking in GSC.

### Month 3 (April/May): Optimization

**Goal: First external customers**

Once 100+ sessions/week, the analytics conversation changes:

- Funnel exploration in GA4 Explore becomes meaningful
- Clarity session recordings reveal consistent UX problems to fix
- A/B testing on CTAs becomes statistically feasible (need ~200 sessions per variant)
- GSC keyword optimization produces measurable CTR improvements

---

## Memory Written

**Path**: `/home/jared/projects/AI-CIV/aether/.claude/memory/agent-learnings/data-scientist/2026-02-22--purebrain-analytics-full-insights.md`
**Type**: teaching + operational
**Topic**: Complete analytics stack analysis - what's live, what the data says, prioritized recommendations

---

*Report prepared by data-scientist (Aether). All findings are grounded in live data accessible programmatically: WP REST API, Brevo API, GTM container inspection, conversation logs, and payment logs. GA4/GSC/Clarity dashboard data was not directly accessible but their configurations were verified via GTM container fetch.*
