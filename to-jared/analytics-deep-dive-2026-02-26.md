# Analytics Deep Dive: purebrain.ai
## GA4 + Google Search Console + Microsoft Clarity Strategy Report

**Prepared by**: Aether (web-researcher)
**Date**: 2026-02-26
**Site**: purebrain.ai (WordPress + Elementor)
**Goal**: Subscription sign-ups across 4 tiers ($79–$999/mo)

---

## Executive Summary

This report provides a complete analytics strategy for purebrain.ai covering three platforms. The core thesis: GA4 tells you WHAT is happening (traffic, conversions, revenue), Google Search Console tells you HOW people are finding you (and where to grow), and Microsoft Clarity tells you WHY people are converting or leaving (behavioral patterns). All three are free, all three are running on the site (or should be immediately), and together they form a complete picture that most competitors are missing.

Do not treat these as three separate tools. They are one intelligence system. Each week you cross-reference findings from all three before making any decisions.

---

## Platform 1: Google Analytics 4 (GA4)

### Core Philosophy for PureBrain

GA4 is built for event-based tracking, which perfectly matches a SaaS with a multi-step acquisition funnel. The key shift from traditional analytics: stop measuring sessions and start measuring user journeys across multiple visits. B2B buyers typically require 3–7 touches before signing up — GA4 is built to track exactly that.

---

### 1.1 Key KPIs to Track

**Acquisition KPIs**
- New users by channel (which source brings sign-ups, not just visits)
- Engagement rate by channel (organic vs. paid vs. direct — which brings people who actually read)
- Cost per acquisition by channel (once ads are running)

**Activation KPIs**
- Assessment completion rate (started vs. finished)
- Calculator engagement rate (loaded vs. calculated)
- Pricing page view rate (% of users who reach /pricing)
- Sign-up form initiation vs. completion (drop-off point)

**Conversion KPIs**
- Visitor-to-sign-up conversion rate (baseline: establish in first 30 days)
- Tier distribution at sign-up (which $79/$149/$499/$999 tier converts most)
- Multi-touch path to conversion (how many sessions before sign-up)

**Retention KPIs** (once subscribers exist)
- 7-day, 30-day, 90-day active user retention
- Subscription renewal rate
- Tier upgrade rate
- Churn rate by tier

**Content KPIs**
- Blog engagement rate (scroll depth is captured via custom event)
- Blog → assessment conversion path
- Blog → calculator conversion path
- Which blog posts drive sign-up more than others

---

### 1.2 Custom Events: Complete Implementation List

Implement these via Google Tag Manager (GTM). Use lowercase with underscores. Maximum 40 characters per event name.

**Assessment Events**
```javascript
// User starts the assessment
gtag('event', 'assessment_started', {
  'source_page': document.referrer,
  'assessment_type': 'ai_adoption'
});

// User completes a question (track drop-off by question number)
gtag('event', 'assessment_question_completed', {
  'question_number': 3,
  'total_questions': 10
});

// User completes the full assessment
gtag('event', 'assessment_completed', {
  'score': calculated_score,
  'tier_recommendation': 'Bonded',
  'time_to_complete_seconds': elapsed_time
});

// User clicks CTA after seeing results
gtag('event', 'assessment_result_cta_click', {
  'recommended_tier': 'Bonded',
  'cta_destination': 'pricing'
});
```

**Calculator Events**
```javascript
// Calculator loaded and visible
gtag('event', 'calculator_loaded', {
  'page': 'ai_tool_stack'
});

// User submits calculator inputs
gtag('event', 'calculator_calculated', {
  'tools_count': 12,
  'estimated_cost': 847,
  'tier_shown': 'Partnered'
});

// User clicks upgrade CTA from calculator result
gtag('event', 'calculator_cta_click', {
  'recommended_tier': 'Partnered',
  'calculated_value': 847
});
```

**Blog Events**
```javascript
// User reaches 50% scroll depth on blog post
gtag('event', 'blog_scroll_50', {
  'post_title': document.title,
  'post_category': 'ai-adoption',
  'word_count': 1200
});

// User reaches 90% scroll depth (true reader)
gtag('event', 'blog_scroll_90', {
  'post_title': document.title,
  'post_category': 'ai-adoption'
});

// User clicks internal CTA in blog post
gtag('event', 'blog_cta_click', {
  'post_title': document.title,
  'cta_type': 'assessment',
  'cta_position': 'mid_post'
});

// User subscribes to Neural Feed from blog
gtag('event', 'newsletter_signup', {
  'source': 'blog_footer',
  'post_title': document.title
});
```

**Sign-Up Flow Events**
```javascript
// User views pricing page
gtag('event', 'pricing_page_view', {
  'source': previous_page
});

// User clicks a specific tier on pricing
gtag('event', 'tier_selected', {
  'tier_name': 'Bonded',
  'tier_price': 149
});

// User initiates sign-up form
gtag('event', 'signup_form_started', {
  'tier': 'Bonded',
  'source': 'pricing_page'
});

// Sign-up completed (CONVERSION EVENT — mark as conversion in GA4)
gtag('event', 'signup_completed', {
  'tier': 'Bonded',
  'value': 149,
  'currency': 'USD'
});
```

**Competitor Exodus Page Events**
```javascript
// User views a competitor comparison page
gtag('event', 'competitor_page_view', {
  'competitor': 'chatgpt',
  'page': '/switching-from-chatgpt'
});

// User clicks migration quiz on exodus page
gtag('event', 'migration_quiz_started', {
  'source_competitor': 'chatgpt'
});
```

**Mark These as Conversions in GA4** (Admin > Events > Mark as conversion):
- `signup_completed`
- `assessment_completed`
- `pricing_page_view`
- `calculator_calculated`
- `newsletter_signup`

---

### 1.3 Conversion Funnel Setup

Create these funnels in GA4 Explore > Funnel Exploration:

**Primary Acquisition Funnel**
1. `session_start` (any page)
2. `page_view` (blog or homepage)
3. `assessment_started` OR `calculator_loaded`
4. `pricing_page_view`
5. `signup_form_started`
6. `signup_completed`

This funnel shows you exactly where you are losing people. If step 3→4 has a 90% drop, the assessment/calculator is not driving people to pricing. If step 5→6 has a 70% drop, the sign-up form itself is the problem.

**Assessment-Specific Funnel**
1. `assessment_started`
2. `assessment_question_completed` (question 3 — early drop-off indicator)
3. `assessment_question_completed` (question 7 — mid-funnel indicator)
4. `assessment_completed`
5. `assessment_result_cta_click`

Track this weekly. If question 5 has a big drop, the question itself is causing abandonment.

**Blog-to-Conversion Funnel**
1. `blog_scroll_50` (engaged reader)
2. `blog_scroll_90` (true reader)
3. `blog_cta_click`
4. `pricing_page_view`
5. `signup_completed`

This tells you which blog posts are worth writing more of.

---

### 1.4 Audience Segment Recommendations

Build these segments in GA4 (Admin > Audiences) and sync them to Google Ads:

**High-Intent Visitors** (for remarketing)
- Visited `/pricing` in last 30 days AND did NOT complete `signup_completed`
- Rule: Page path contains `/pricing`, Event `signup_completed` is 0

**Assessment Abandoners** (warm leads)
- Fired `assessment_started` but NOT `assessment_completed` in last 14 days
- These people know about PureBrain and were curious enough to start

**Calculator Users** (high commercial intent)
- Fired `calculator_calculated` in last 30 days
- They quantified their own problem — they know what AI tools cost them

**Deep Blog Readers** (education-mode ICP)
- Fired `blog_scroll_90` at least 2 times in last 30 days
- These are people doing research — prime for nurture sequences

**Pricing Tier Researchers** (bottom-funnel)
- Fired `tier_selected` but not `signup_completed` in last 7 days
- These are the hottest prospects — they clicked a tier but did not buy

**Power Readers** (brand advocates)
- 5+ sessions AND blog_scroll_90 at least 3 times AND no `signup_completed`
- These people love the content but have not converted — show them a direct offer

---

### 1.5 GA4 + Google Ads Integration

**Setup Steps:**
1. Link GA4 to Google Ads: GA4 Admin > Product Links > Google Ads Links
2. Enable Audience Sharing: Toggle on for each linked Ads account
3. Import GA4 conversions into Google Ads: Use `signup_completed` as primary conversion

**Remarketing Campaigns to Run:**

| Audience | Campaign Type | Bid Strategy | Message |
|----------|--------------|--------------|---------|
| Pricing page visitors (30 days) | Search + Display | Target CPA | "Still thinking? Start with Awakened at $79/mo" |
| Assessment abandoners (14 days) | Display | Max Conversions | "Finish your AI audit — takes 3 minutes" |
| Calculator users (30 days) | Search | Target ROAS | "Your AI tools cost $[X]/mo. PureBrain is $79." |
| Deep blog readers (30 days) | Display | Max Conversions | "You read the research. Now try the tool." |

**Important:** Allow 24–48 hours for new audiences to populate in Google Ads after linking. Audiences must have at least 100 users before they can be used for targeting.

---

### 1.6 User Journey Tracking: Landing Page → Assessment → Blog → Pricing → Sign-up

Set up a custom Path Exploration in GA4 Explore:

1. Go to Explore > Path exploration
2. Starting point: `session_start`
3. Ending point: `signup_completed`
4. This will show you every path users take to sign up

Additionally, set up a User Lifetime report to see:
- How many sessions a user had before converting
- Which channels first touched converting users
- Average days between first visit and sign-up

This is critical intelligence. If the average user signs up after 4 sessions over 8 days, you need email sequences timed to that cadence.

---

### 1.7 Dashboards to Build

**Dashboard 1: Daily Health Check** (5-minute morning review)
- New users today vs. yesterday
- Sessions by channel today
- Conversion events today (assessment completions, sign-ups, calculator uses)
- Real-time active users

**Dashboard 2: Weekly Growth Report** (30-minute Monday review)
- New users by channel (week over week)
- Assessment completion rate (target: 60%+)
- Blog scroll-90 rate (which posts are performing)
- Pricing page → sign-up conversion rate
- Newsletter sign-ups

**Dashboard 3: Monthly Business Review** (60-minute monthly)
- All conversion funnel drop-off rates
- Audience segment sizes and trends
- Tier distribution of sign-ups
- Blog posts sorted by conversion contribution
- Top acquisition sources by sign-up (not just visit)

Use Looker Studio (free, connected directly to GA4) to build these dashboards and share a link with Jared.

---

### 1.8 Automated Alerts to Configure

In GA4, go to Admin > Custom Insights to set up:

**Critical Alerts (Daily)**
- Conversion rate drops more than 30% vs. previous day → Email alert
- New users drop more than 40% vs. same day last week → Email alert
- `signup_completed` events = 0 for the day → Immediate alert

**Warning Alerts (Weekly)**
- Assessment completion rate drops below 50% → Email alert
- `pricing_page_view` events drop more than 25% week over week → Email alert
- Direct traffic drops more than 20% (potential brand awareness issue) → Email alert

**Opportunity Alerts**
- Organic traffic increases more than 50% week over week → Note for content analysis
- Any single blog post drives 50+ `blog_scroll_90` events in a day → Write a follow-up post on that topic

---

### 1.9 Review Cadence

| Frequency | Duration | Focus |
|-----------|----------|-------|
| Daily | 5 min | Anomaly detection — did something break? |
| Weekly (Monday) | 30 min | Growth metrics — are we trending right? |
| Monthly (1st) | 60 min | Funnel optimization — what needs fixing? |
| Quarterly | 2 hours | Strategy review — which channels to invest in? |

---

## Platform 2: Google Search Console

### Core Philosophy for PureBrain

GSC is the only tool that shows you what real humans typed into Google to find you — or almost find you. This is the purest signal you have about what your market wants. Every query with high impressions but low clicks is money left on the table. Every question someone typed that you have not answered is a blog post you should write.

For an AI SaaS in 2026, GSC is especially critical because AI Overviews (Google's AI-generated summaries) are stealing clicks from traditional results. Knowing which queries trigger these overviews — and optimizing for them — is a competitive edge most businesses have not caught up to yet.

---

### 2.1 Key Queries to Monitor

**Priority Query Categories for PureBrain:**

**High-Intent Purchase Queries** (monitor weekly)
- "AI business tools [month] [year]"
- "best AI for business owners"
- "AI assistant for companies"
- "AI adoption platform"
- "ChatGPT alternative for business"
- "purebrain ai" (branded — should be #1 always)

**Competitor Research Queries** (monitor monthly)
- "switching from ChatGPT to [x]"
- "ChatGPT vs [competitor] for business"
- "Jasper alternative"
- "Copy.ai vs"

**Problem-Aware Queries** (blog content drivers)
- "why AI tools not working for business"
- "AI implementation fails"
- "AI ROI measurement"
- "how to train employees on AI"

**Assessment and Calculator Queries** (track if showing up)
- "AI adoption assessment for business"
- "AI tool cost calculator"
- "how ready is my business for AI"

Set up weekly GSC performance reports filtered by these categories. Export monthly to a Google Sheet for trend analysis.

---

### 2.2 Content Gap Identification: The Exact Process

Do this every Monday. It takes 20 minutes and will generate better blog topics than any AI brainstorm session.

**Step 1: High Impressions, Low Position (Position 11–30)**
In GSC Performance > Queries, sort by Impressions, then filter to positions 11–30.

These are queries where Google ALMOST shows your content — meaning it thinks you are relevant but not quite good enough. These are the easiest wins: update existing content for these queries rather than writing new pages.

**Step 2: High Impressions, Low CTR (<2%)**
Filter to impressions > 50, CTR < 2%. This means people see your page in results but do not click.

Fix: Rewrite the meta title and description for these pages to better match search intent. The content exists — the packaging is wrong.

**Step 3: Questions You Rank For But Have Not Targeted**
Filter queries containing "how," "why," "what," "best," "vs." Sort by clicks. Find any query driving traffic that does not have a dedicated blog post answering it.

Write that blog post. This is free traffic you are leaving on the table.

**Step 4: Zero-Click Queries with High Impressions**
These appear in Google's AI Overview or featured snippets. To capture these, reformat existing content with direct Q&A structure:
- Question as H2 header
- Direct 2-sentence answer immediately below
- Supporting evidence in paragraph after

This format gets cited 67% more often by AI-generated search summaries.

---

### 2.3 Core Web Vitals Optimization Priorities

Target thresholds (Google's current requirements for "Good" status):
- **LCP (Largest Contentful Paint)**: Under 2.5 seconds
- **INP (Interaction to Next Paint)**: Under 200 milliseconds
- **CLS (Cumulative Layout Shift)**: Under 0.1

**PureBrain-Specific Priorities:**

WordPress + Elementor sites commonly fail on:

1. **LCP**: Usually caused by hero images loading slowly. Fix: Compress all hero images to WebP format under 100KB. Use Cloudflare CDN (already running) to serve from edge.

2. **INP**: Elementor adds significant JavaScript. Fix: Use a caching plugin (WP Rocket or LiteSpeed Cache) with JS deferral. Test the assessment page specifically — interactive elements often cause INP failures.

3. **CLS**: Font loading and images without defined dimensions. Fix: Add explicit width/height to all images. Use `font-display: swap` in CSS.

Check CWV in GSC: Experience > Core Web Vitals. Fix mobile first — most business leaders will check purebrain.ai on mobile before committing.

**Priority order**: Assessment page > Homepage > Pricing page > Blog pages

---

### 2.4 Indexing Strategy for Daily Blog Posts

With daily publishing, indexing speed matters. Here is the exact workflow:

**Automatic (Set Once):**
1. Submit XML sitemap to GSC: Settings > Sitemaps > Add new sitemap
   - Submit: `https://purebrain.ai/sitemap_index.xml` (Rank Math or Yoast auto-generates this)
2. Google recrawls your sitemap regularly and discovers new posts within hours to days

**Manual Fast-Track (Do For Every New Post):**
1. In GSC, click the URL bar at the top and paste the new post URL
2. Click "Request Indexing"
3. Google typically crawls within hours

**Limit**: GSC has a daily quota for manual indexing requests — do not burn it on old posts. Use only for new and updated high-priority posts.

**IndexNow Protocol (Already Installed via Plugin v430)**:
Based on memory records, the IndexNow plugin is already deployed on purebrain.ai. This automatically notifies search engines (Google, Bing, Yandex) the moment a post is published. This is the fastest possible indexing path.

**Monitor Indexing Issues**:
Check GSC > Indexing > Pages weekly. Look for:
- "Discovered — currently not indexed" (crawl budget issue — see fix below)
- "Crawled — currently not indexed" (content quality signal)
- "Duplicate without canonical" (check canonical tags on blog posts)

---

### 2.5 Using GSC Data to Inform Blog Topic Selection

**Weekly Topic Mining Process** (20 minutes every Friday):

1. **Export last 7 days of query data** from GSC Performance as CSV
2. **Filter to queries in position 5–30** (close enough to rank, not yet winning)
3. **Look for questions** containing "how," "why," "what," "can AI," "should I"
4. **Map each to existing content** — does a blog post already address this?
5. **Gaps = next week's blog calendar**

**Content Priority Matrix:**
- High impressions + position 11–20 + question format = UPDATE existing post to better answer it
- High impressions + position 21–50 + no existing post = WRITE new dedicated post
- High impressions + position 1–5 + low CTR = REWRITE meta title/description only

**Specific Queries to Watch for PureBrain's Blog:**
Set up GSC filters for queries containing:
- "AI for business" — high volume, moderate competition
- "AI implementation" — problem-aware, high intent
- "AI tools [year]" — high commercial intent, update monthly
- "ChatGPT vs" — switcher intent, competitor pages apply

---

### 2.6 International Targeting

Unless you are actively building content for non-English markets, keep international targeting set to "Unlisted" (not targeted to any specific country) rather than "United States only."

Why: If you set it to US-only, you lose traffic from UK, Canada, Australia, India — all major English-speaking markets with high AI adoption rates.

Monitor your geographic data in GSC: Performance > Country filter. If you see 20%+ of your traffic from a specific non-US country, consider adding location-specific content or pricing.

---

### 2.7 Dashboards to Build in GSC

GSC does not have full custom dashboards, but set these filters and save them:

**Saved Filter 1: Brand Health**
- Filter: Query contains "purebrain"
- See weekly: Are branded impressions growing? Is CTR above 40%?

**Saved Filter 2: High-Opportunity Queries**
- Filter: Position between 11 and 30
- See weekly: Which pages are almost ranking?

**Saved Filter 3: Top Blog Posts**
- Filter: Page contains "/blog"
- See monthly: Which posts drive the most clicks?

**Connect GSC to GA4**: Link them in GA4 Admin > Product Links > Search Console Links. This lets you see GSC query data alongside GA4 behavior data — you can see which queries drive sign-ups, not just which drive traffic.

---

### 2.8 Automated Alerts in GSC

GSC has limited native alerting. Set up email notifications for:
- Indexing errors (Settings > Notifications)
- Security issues (automatic)
- Manual actions (automatic)

For traffic alerts, use GA4's anomaly detection instead — it is more sophisticated and covers search traffic since GA4 and GSC are linked.

**Manual alert workaround**: Export GSC performance data to Google Sheets monthly and use Google Sheets' built-in alert rules to email you if any top-10 pages drop position significantly.

---

### 2.9 Review Cadence

| Frequency | Duration | Focus |
|-----------|----------|-------|
| Weekly (Monday) | 20 min | Content gap mining + index status |
| Weekly (Friday) | 15 min | Blog topic selection from query data |
| Monthly | 30 min | Position trends, CWV status, top posts |
| Quarterly | 1 hour | Full query audit, sitemap health, link report |

---

## Platform 3: Microsoft Clarity

### Core Philosophy for PureBrain

GA4 tells you a 10% drop in assessment completions happened. GSC tells you organic traffic is up 20%. Clarity tells you WHY the 10% drop happened — someone is rage-clicking the "Next" button on question 4 because it is not responding on mobile. Without Clarity, you are flying blind on the "why."

Clarity is free, captures 100% of sessions (no sampling unlike many tools), and integrates with GA4 natively. It is the missing layer between your quantitative data and your actual user experience.

---

### 3.1 Session Replay Best Practices

**Do NOT watch every session.** That is a waste of time. Filter first, then watch.

**High-Value Filters to Use Before Watching Replays:**

1. **Assessment abandoners**: Filter > User Actions > Started assessment_started event AND did NOT fire assessment_completed → Watch 10 sessions → Find the drop-off point
2. **Pricing page visitors who did not convert**: Filter > Page contains `/pricing` AND session duration > 60 seconds AND no purchase event → Watch 10 sessions → What is causing hesitation?
3. **Rage click sessions**: Filter > Semantic Metrics > Rage clicks = true → Watch all → Find broken elements immediately
4. **Mobile sessions with high bounce**: Filter > Device = mobile AND scroll depth < 30% → Watch 5 sessions → Find UX breaks

**Session Replay Cadence:**
- Daily: Check if any rage click sessions appeared on key conversion pages
- Weekly: Watch 5 filtered sessions per conversion page (assessment, calculator, pricing)
- Monthly: Watch 20 random sessions from new users (first visit behavior)

---

### 3.2 Heatmap Analysis for Landing Page Optimization

Set up heatmaps on these specific pages (not your whole site):

**Page Priority Order:**
1. `/` (Homepage)
2. Assessment page
3. AI Tool Stack Calculator page
4. `/pricing` (or wherever the sign-up CTA lives)
5. Top 3 blog posts by GA4 conversion contribution

**What to Look for on Each Heatmap:**

**Click Heatmaps:**
- Are people clicking non-clickable elements? (Dead click problem)
- Are the primary CTAs getting clicks, or are secondary elements stealing attention?
- On mobile: Are users tapping the menu instead of the main CTA?

**Scroll Heatmaps:**
- What percentage of users reach your main CTA? If it is below 60%, move it higher.
- On blog posts: Does the in-post newsletter signup CTA appear above the 70% scroll line?
- On pricing page: Can users see all 4 tiers without scrolling? If not, tier structure needs redesigning.

**Move Heatmaps:**
- On desktop, cursor movement approximates attention. Look for hesitation clusters.
- If users hover over pricing tier names repeatedly, they are comparing but uncertain — add a "Most Popular" badge or comparison table.

---

### 3.3 Rage Click Detection and Action Plan

Rage clicks are your fastest wins. They tell you exactly where users are frustrated.

**Rage Click Response Protocol:**
1. Clarity Dashboard > Insights > Rage clicks
2. Click the page URL where rage clicks appeared
3. Filter to sessions with rage clicks on that page
4. Watch 3–5 session recordings
5. Identify the element being rage-clicked
6. Fix it within 24 hours

**Common Rage Click Sources for WordPress + Elementor:**
- Accordion FAQ sections that are slow to expand on mobile
- CTA buttons where the link target is slightly off (Elementor button padding issue)
- Forms where the submit button does not respond immediately
- Images that look clickable but are not linked
- Navigation menu items on mobile that have small touch targets

**For PureBrain specifically:** Monitor assessment question "Next" buttons. Rage clicks there indicate either the button is not working or users are frustrated by a question and want to skip it.

---

### 3.4 Dead Click Identification

Dead clicks mean users click something expecting a response and nothing happens. This is different from rage clicks — dead clicks are one deliberate click, not repeated frustrated tapping.

**High-Priority Dead Click Investigations:**
- Any click on the PureBrain logo that does not navigate (should go to homepage)
- Blog post category labels that look clickable but are styled spans, not links
- Assessment result tier badges that look interactive but have no action
- Calculator result tier suggestions without a direct sign-up button

**Find Dead Clicks:**
Clarity > Heatmaps > Click map > Toggle "Dead clicks" filter. Red zones = investigate immediately.

---

### 3.5 Scroll Depth Analysis for Blog Engagement

Use Clarity's scroll heatmaps on your top 10 blog posts.

**What the Data Tells You:**

**If 80%+ reach the bottom**: Post length is appropriate, content is engaging. Add a stronger CTA at the bottom.

**If 50–80% reach the bottom**: Normal for long-form content. Ensure your main CTA appears at both the 50% and 90% scroll positions.

**If under 50% reach the bottom**: Content is either too long, not matching reader intent, or losing them at a specific section. Look for the scroll "cliff" — the exact line where 30%+ of users stop scrolling — and rewrite that section.

**Blog-Specific Insight for PureBrain:**
With daily publishing, you cannot optimize every post. Use this process monthly: pull the 5 blog posts with the worst scroll depth from Clarity, fix them one at a time. This compounds over time.

---

### 3.6 Fury Events and JavaScript Errors

**Fury Events** = Rage clicks + Excessive scrolling + Quick backs combined. These are sessions where the user was clearly frustrated.

Check Clarity > Insights weekly for:
- Sudden spikes in fury events (suggests a specific page broke)
- Fury events concentrated on mobile (suggests mobile-specific UX problem)
- Fury events concentrated on a specific traffic source (suggests landing page mismatch with ad copy)

**JavaScript Errors:**
Clarity > Insights > JavaScript errors shows:
- Total JS errors and breakdowns by specific error
- Option to filter session recordings to only those with JS errors

**For PureBrain's WordPress + Elementor setup:**
Watch for JS errors on:
- Assessment page (custom scoring JS can break on certain browsers)
- Calculator page (calculation logic)
- Payment pages (critical — any JS error here = lost sale)

Check JavaScript errors weekly. Any new error that appears after a site update should trigger immediate investigation.

---

### 3.7 Filters and Segments for SaaS Conversion

Set up and save these Clarity segments:

**Segment 1: Pricing Intent**
Filter: Page contains `/pricing` > Save as "Pricing Visitors"
Use: Watch these sessions to understand pricing page hesitation

**Segment 2: Assessment Starters**
Filter: Smart Event = assessment_started > Save as "Assessment Starters"
Use: Identify where in the assessment flow users drop off

**Segment 3: Mobile High-Frustration**
Filter: Device = Mobile AND Rage clicks = true > Save as "Mobile Frustration"
Use: Mobile UX problems that need fixing

**Segment 4: New Visitors**
Filter: Visit number = 1 > Save as "First Visit"
Use: Watch how people experience the homepage for the first time

**Segment 5: Returning Non-Converters**
Filter: Visit number > 2 AND No purchase event > Save as "Returning No Convert"
Use: Understand why repeat visitors are not signing up

**Funnels to Build in Clarity** (code-free, built directly in Clarity):

**Primary Conversion Funnel:**
Step 1: Homepage (`/`)
Step 2: Assessment OR Calculator page
Step 3: Pricing page
Step 4: Thank you / confirmation page

**Assessment Funnel:**
Step 1: Assessment question 1
Step 2: Assessment question 5
Step 3: Assessment question 10
Step 4: Assessment results page

Clarity will show you exactly how many sessions completed each step and the % drop at each transition.

---

### 3.8 Clarity's Watchlist (Personal Dashboard)

Use the Watchlist card in Clarity's dashboard to monitor your highest-priority metrics at a glance:

**Recommended Watchlist Items:**
1. Sessions with rage clicks (%) — target: below 3%
2. Sessions with dead clicks (%) — target: below 5%
3. Sessions with JavaScript errors (%) — target: below 1%
4. Assessment funnel conversion rate — track weekly
5. Pricing page sessions (daily count)

The Watchlist updates dynamically when you apply filters — you can quickly see "of sessions from organic search, what % had rage clicks?"

---

### 3.9 Clarity + GA4 Integration

Connect Clarity to GA4 for the most powerful combination:

1. Clarity > Settings > Integrations > Google Analytics > Connect
2. Clarity will now tag GA4 sessions with Clarity data
3. In GA4, you can filter by Clarity segments (e.g., "sessions with rage clicks") to see their GA4 behavior

**Key Cross-Platform Insight:**
Find users who rage-clicked in Clarity AND had `pricing_page_view` in GA4 but NOT `signup_completed`. These are the most important sessions to watch — frustrated people who were ready to buy.

---

### 3.10 Automated Alerts in Clarity

Clarity has limited native alerting. Set up monitoring through:

1. **Weekly Slack/Email Digest**: Clarity sends a weekly email summary — subscribe to it
2. **Watchlist Review**: Check the Watchlist every Monday morning (2 minutes)
3. **For Critical Breaks**: Set up a GA4 alert for `signup_completed` dropping to 0 — then immediately check Clarity for rage clicks and JS errors on the payment page

---

### 3.11 Review Cadence

| Frequency | Duration | Focus |
|-----------|----------|-------|
| Daily | 3 min | Watchlist check — any new rage click spikes? |
| Weekly (Monday) | 20 min | Watch 5 filtered sessions, check fury events |
| Monthly | 45 min | Heatmap review of top 5 pages, scroll depth analysis |
| After every site update | 10 min | Check JS errors + rage clicks on updated pages |

---

## Cross-Platform Integration: How to Use All Three Together

### The Weekly Intelligence Loop (45 minutes every Monday)

1. **GA4** (10 min): Check weekly dashboard — what are the numbers? Any conversion drops?
2. **GSC** (15 min): Content gap mining — what queries are we missing?
3. **Clarity** (20 min): Watch sessions related to any GA4 anomalies — why did conversions drop?

### The Monthly Optimization Cycle

**Week 1**: GA4 funnel analysis — identify the biggest conversion drop-off
**Week 2**: Clarity deep dive — watch sessions around that drop-off, identify root cause
**Week 3**: Implement fix (content update, UX change, or CTA adjustment)
**Week 4**: GSC review — what new content opportunities emerged?

### Trigger: Conversion Rate Drops

1. GA4 alert fires: `signup_completed` down 40% vs. last week
2. GA4 drill-down: Which step in the funnel dropped? (Assessment completions? Pricing page views?)
3. Clarity: Watch 10 sessions on the problem page from the same time period
4. GSC: Has organic traffic to that page dropped? (External cause vs. UX cause)
5. Fix: Either update content (GSC-driven) or fix UX (Clarity-driven)

---

## Quick Setup Priority Order

If starting from scratch today, set up in this order:

**Day 1 (2 hours):**
- Verify GA4 is installed and collecting data
- Mark 3 conversion events: `signup_completed`, `assessment_completed`, `pricing_page_view`
- Install Clarity WordPress plugin
- Submit XML sitemap to GSC

**Week 1 (4 hours):**
- Implement all custom events via GTM
- Set up GA4 conversion funnels (Primary and Assessment)
- Create Clarity segments (5 segments listed above)
- Build Clarity funnels (Primary + Assessment)

**Week 2 (3 hours):**
- Build GA4 dashboards in Looker Studio
- Set up GA4 automated alerts
- Link GA4 to GSC
- Link Clarity to GA4
- First GSC content gap mining session

**Month 1 (ongoing):**
- First full monthly review across all three platforms
- First heatmap analysis of top 5 pages
- First batch of session replays
- Build first remarketing audience in GA4 > Google Ads

---

## Key Metrics Summary Table

| Metric | Platform | Target | Alert Threshold |
|--------|----------|--------|----------------|
| Assessment completion rate | GA4 | 60%+ | Below 50% |
| Pricing page → signup conversion | GA4 | 5%+ | Below 3% |
| Organic traffic | GSC | +10% MoM | -20% WoW |
| Core Web Vitals LCP | GSC | <2.5s | Any "Poor" rating |
| Indexed pages | GSC | All blog posts | Any indexing errors |
| Rage click rate | Clarity | <3% sessions | >5% sessions |
| Dead click rate | Clarity | <5% sessions | >8% sessions |
| JS error rate | Clarity | <1% sessions | >2% sessions |
| Blog scroll-50 rate | GA4 | 70%+ | Below 50% |
| Newsletter signup rate | GA4 | 2%+ of blog visits | Below 1% |

---

## Sources

Research compiled from:

- [GA4 Metrics for SaaS - Analytify](https://analytify.io/ga4-metrics-for-saas/)
- [GA4 for SaaS Complete Guide - Analyzify](https://analyzify.com/hub/ga4-guide-for-saas/)
- [GA4 for SaaS Companies: Key Metrics - Goodish Agency](https://goodish.agency/ga4-for-saas-companies-key-metrics-to-track/)
- [Optimize B2B SaaS User Journeys with GA4 - MarTech](https://martech.org/how-to-optimize-b2b-saas-user-journeys-with-ga4/)
- [GA4 Best Practices 2026 - Measure Marketing](https://www.measuremarketing.pro/post/ga4-best-practices-2026)
- [Advanced GA4 Event Tracking Implementation Guide](https://www.easyseo.online/blog/advanced-ga4-event-tracking-complete-implementation-guide)
- [GA4 Custom Alerts Guide - Analytify](https://analytify.io/google-analytics-alerts/)
- [GA4 Anomaly Detection - NextFly](https://nextflywebdesign.com/blog/ga4-anomaly-detection/)
- [GA4 Audiences for Remarketing - Analytify](https://analytify.io/google-analytics-4-audiences/)
- [Google Search Console Complete 2026 Guide - ALM Corp](https://almcorp.com/blog/google-search-console-complete-guide/)
- [Google Search Console for Keyword Research 2026 - Analytify](https://analytify.io/google-search-console-for-keyword-research/)
- [GSC 2026 Guide - Pansofic Solutions](https://www.pansofic.com/blog/google-search-console-in-2026-pansofic-solutions/)
- [Core Web Vitals Report - Google Search Central](https://developers.google.com/search/docs/appearance/core-web-vitals)
- [GSC Indexing Request - Google Search Central](https://developers.google.com/search/docs/crawling-indexing/ask-google-to-recrawl)
- [Microsoft Clarity - Free Heatmaps and Session Recordings](https://clarity.microsoft.com/)
- [Clarity Semantic Metrics - Microsoft Learn](https://learn.microsoft.com/en-us/clarity/insights/semantic-metrics)
- [Clarity Funnels - Microsoft Learn](https://learn.microsoft.com/en-us/clarity/setup-and-installation/funnels)
- [Clarity Filters and Segments Blog](https://clarity.microsoft.com/blog/elevate-your-analysis-using-filters-and-segments-in-microsoft-clarity/)
- [Clarity Smart Events Overview](https://clarity.microsoft.com/blog/an-overview-of-smart-events/)
- [Clarity WordPress Integration - Microsoft Learn](https://learn.microsoft.com/en-us/clarity/third-party-integrations/wordpress)
- [Rage Clicks Analysis - Microsoft Clarity Blog](https://clarity.microsoft.com/blog/rage-clicks-user-behavior/)
- [Dead Clicks Analysis - Momentic Marketing](https://momenticmarketing.com/blog/dead-clicks)
- [SEO Trends 2026 - ALM Corp](https://almcorp.com/blog/seo-trends-2026-rank-google-ai-search/)
- [AI Search Optimization 2026 - First Page Sage](https://firstpagesage.com/seo-blog/ai-search-optimization-strategy-and-best-practices/)

---

*Report end. Total estimated setup time: 9 hours across 2 weeks. Ongoing maintenance: 45 minutes per week.*
