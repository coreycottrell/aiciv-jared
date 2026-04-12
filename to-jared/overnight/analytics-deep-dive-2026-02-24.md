# Analytics Deep Dive: GA4 + Google Search Console + Microsoft Clarity
## The Complete Implementation Guide for PureBrain.ai - Feb 2026

**Prepared by**: Aether (web-researcher)
**Date**: 2026-02-24
**Scope**: Platform best practices, setup recommendations, unified stack methodology, and weekly review system
**Companion to**: analytics-deep-dive-2026-02-23.md (site audit) and analytics-deep-dive-2026-02-21.md (initial setup)
**Research method**: Current-state web research across official documentation, practitioner guides, and Feb 2026 case studies

---

## Executive Summary

This report is the implementation bible for the PureBrain.ai analytics stack. Yesterday's report told you what the site looks like. This report tells you how to extract maximum value from the three tools you have once they are properly configured.

**The one insight that changes everything**: GA4 tells you WHAT happened, Microsoft Clarity tells you WHY, and Google Search Console tells you how Google sees you BEFORE the click. None of them are powerful alone. Together, they answer every important question about your business.

**Three things to know going in**:
1. GA4 is now purpose-built for lead generation funnels - it has eight audience templates and a dedicated lead funnel report that most people do not know exist
2. GSC in 2026 is no longer just a diagnostic tool - it now surfaces AI Overview data, meaning you can see where your content is appearing in Google's AI-generated answers
3. Clarity is completely free with no traffic limits - most companies are dramatically underusing it because they do not have a structured review process

---

## Part 1: Google Analytics 4 (GA4)

### What GA4 Is Doing Right Now vs. What It Should Be Doing

Most teams use GA4 like a dashboard - checking sessions, users, and page views. That is about 10% of its value for a B2B lead generation site.

The full value comes from:
- Tracking the complete visitor-to-lead-to-customer journey
- Building audiences from behavior (not just demographics)
- Using predictive metrics to identify who is about to convert or churn
- Connecting to Google Ads for feedback loops that improve ad performance over time

---

### Section 1A: Initial Setup Decisions That Cannot Be Changed Later

These must be done correctly from the start. Changing them later requires a new property and losing all historical data.

**Data Retention: Change from Default Immediately**

The default GA4 data retention is 2 months. This means all of your historical data disappears after 60 days. For a new site, you are losing your baseline data.

Action: GA4 Admin > Data Settings > Data Retention > Change to 14 months (the maximum for free GA4)

**Google Signals: Enable for Cross-Device Tracking**

Google Signals allows GA4 to track users across devices when they are signed into Google accounts. For B2B, this matters because executives research tools on mobile and then purchase on desktop.

Action: GA4 Admin > Data Collection > Google Signals > Enable

**Internal Traffic Filter: Exclude Jared and Team from Data**

Without filtering, every time Jared visits the site or a team member deploys code, it inflates the metrics. This is especially problematic for conversion rate calculation.

Action: GA4 Admin > Data Streams > Define internal traffic > Add your IP address (and Philippines team IPs if known) > Create filter in Admin > Data Filters

**Domain Property vs. URL Prefix**: GA4 already handles cross-domain if your property is set up correctly. The key check: if someone goes from purebrain.ai to a PayPal payment page and back, the return should not show as a new session. This requires cross-domain tracking configuration in your GTM GA4 tag settings.

---

### Section 1B: The Lead Generation Report System

GA4 has a complete lead generation reporting system that most people do not know exists. It was added in 2024-2025 and is specific to non-ecommerce service businesses.

**How to Enable It**

1. GA4 Admin > Reports Library
2. Click "Lead Generation" collection
3. Click "Publish" to add it to your left navigation
4. Now you have dedicated reports: Lead Overview, Lead Acquisition, and Lead Funnel

**The Six Official Lead Events (In Order)**

These are GA4's recommended event names for a complete lead funnel. Using these exact names (not custom names) means they integrate with the auto-generated audience templates:

| Event Name | When to Fire | PureBrain Equivalent |
|------------|-------------|---------------------|
| `generate_lead` | Form submission, assessment started | Assessment page form submit |
| `qualify_lead` | Lead shows buying signals | Assessment completed with high score |
| `disqualify_lead` | Lead not a fit | Assessment completed with low fit score |
| `working_lead` | Active sales conversation | Post-payment chat session started |
| `close_convert_lead` | Deal closed | PureBrain subscription confirmed |
| `close_unconvert_lead` | Deal lost | No activity 30 days post-assessment |

For PureBrain specifically, the most important events to implement first are:
- `generate_lead` when someone submits the AI readiness assessment
- `qualify_lead` when assessment score indicates enterprise readiness (high score)
- `working_lead` when post-payment conversation begins

**The Eight Auto-Generated Audiences**

When Lead Generation reports are enabled and the events above fire, GA4 automatically creates these audiences in your Audiences section:
1. All Leads
2. Qualified Leads
3. Working Leads
4. Converted Leads
5. High-Value Leads (by predicted value)
6. Churn Risk Leads
7. Likely to Convert (predictive)
8. Recently Converted

These audiences can be sent directly to Google Ads for remarketing. If Jared runs Google Ads in Month 2-3, these audiences are already built.

---

### Section 1C: Custom Events to Implement for PureBrain

These are beyond the default events (page views, scrolls, outbound clicks) that Enhanced Measurement handles automatically.

**Priority 1: Conversion Events (Implement First)**

```
Event: assessment_started
Trigger: User lands on /ai-readiness-assessment/ and interacts with first question
Parameters: page_location, traffic_source

Event: assessment_completed
Trigger: User reaches results page of any assessment
Parameters: score_range (high/medium/low), assessment_type

Event: generate_lead
Trigger: Assessment form submitted (email captured)
Parameters: form_name, email_domain (company vs personal), traffic_source

Event: chat_initiated
Trigger: User types first message in PureBrain chatbox
Parameters: page_location, is_post_payment (true/false)

Event: payment_initiated
Trigger: PayPal button clicked on any page
Parameters: page_location, product_name, price

Event: purchase
Trigger: PayPal payment confirmed (return to thank you page)
Parameters: transaction_id, value, currency
```

**Priority 2: Engagement Quality Events**

```
Event: blog_scroll_depth
Trigger: User reaches 25%, 50%, 75%, 100% scroll on blog posts
Parameters: scroll_milestone, post_title, word_count

Event: cta_clicked
Trigger: Any "Start Your AI Partnership" or "Begin Awakening" button clicked
Parameters: page_location, button_text, button_position (above/below fold)

Event: calculator_used
Trigger: User selects tools in AI Tool Stack Calculator
Parameters: tools_selected_count, categories_selected

Event: migration_started
Trigger: User begins importing conversation history on /migrate/
Parameters: source_platform (ChatGPT, Claude, etc.)

Event: comparison_page_engaged
Trigger: User clicks a competitor comparison on /compare/ or visits /purebrain-vs-*/
Parameters: competitor_name
```

**Priority 3: Content Engagement Events**

```
Event: newsletter_subscribed
Trigger: Neural Feed subscription form submitted
Parameters: form_location (homepage, blog sidebar, inline)

Event: audit_requested
Trigger: AI Partnership Audit form submitted
Parameters: company_name (if captured)
```

**How to Implement**: All of these should be implemented via Google Tag Manager (GTM-WTDXL4VJ is already on the site). Create a new GA4 Event Tag in GTM for each event, with a custom trigger based on the page URL and element click or form submission.

**Testing Method**: After setting up each tag in GTM, use GTM Preview Mode and then GA4 DebugView (found in GA4 > Admin > DebugView) to confirm the event fires and parameters transmit correctly.

---

### Section 1D: Conversion Funnel Setup

GA4's Funnel Exploration (in the Explore tab) lets you build visual funnels. Here are the three funnels to build:

**Funnel 1: Assessment Conversion Funnel**

Step 1: Page view - /ai-readiness-assessment/ or /ai-partnership-audit/
Step 2: Event - assessment_started
Step 3: Event - generate_lead (email captured)
Step 4: Event - assessment_completed

Questions this funnel answers:
- What percentage of visitors who land on the assessment actually start it?
- What percentage who start it complete it?
- Where is the biggest drop-off?

**Funnel 2: Blog-to-Lead Funnel**

Step 1: Page view on any blog post
Step 2: Scroll depth event - 75% or 100%
Step 3: Event - newsletter_subscribed OR cta_clicked
Step 4: Event - generate_lead (if they then complete assessment)

Questions this funnel answers:
- Which blog posts are converting readers into subscribers?
- Are people who read blog posts engaging with the product CTAs?

**Funnel 3: Payment Funnel**

Step 1: Page view on /ai-website-analysis/ or website execution page
Step 2: Event - payment_initiated (PayPal button clicked)
Step 3: Event - purchase (confirmed on thank-you page)

Questions this funnel answers:
- What percentage of $99 analysis page visitors click PayPal?
- Are there technical issues breaking the payment flow?

---

### Section 1E: Audience Segmentation Strategies

GA4 lets you create custom audiences for analysis and Google Ads targeting. These are the most valuable for PureBrain:

**Audience 1: Enterprise Decision Makers**
Condition: Session duration > 3 minutes AND (visited /ai-partnership-audit/ OR visited /ai-website-analysis/) AND NOT converted

Why it matters: People who spent time on your premium service pages but did not convert are your highest-intent non-customers. They need follow-up.

**Audience 2: High-Value Blog Readers**
Condition: Visited 3+ blog posts AND scroll depth > 75% on at least one post AND NOT subscribed to newsletter

Why it matters: These are your most engaged content readers who have not been captured yet.

**Audience 3: Assessment Abandoners**
Condition: assessment_started event fired AND assessment_completed event did NOT fire within same session

Why it matters: People who started the assessment but did not finish are warm leads who hit friction. Understanding what percentage this is tells you if the assessment has a UX problem.

**Audience 4: Calculator Users**
Condition: Visited /ai-tool-stack-calculator/ AND calculator_used event fired AND NOT generate_lead

Why it matters: Someone using your free tool is showing buying intent. They know what AI tools exist. They are ready to be introduced to PureBrain.

**Audience 5: Return Visitors**
Condition: session_count > 1 (built-in GA4 dimension)

Why it matters: In B2B, decision makers often visit 4-7 times before purchasing. Return visitors are much more likely to convert than first-time visitors. Separating their behavior from first-timers reveals the true conversion path.

---

### Section 1F: Report Templates to Set Up

**Built-In Reports to Customize**

Go to Reports > Library > Customize the following:

1. **Traffic Acquisition Report**: Add secondary dimension "Session Source/Medium" to see LinkedIn vs. organic vs. direct broken down. Add engagement rate column.

2. **Pages and Screens Report**: Sort by "Conversions" (once events are marked as conversion events) to see which pages are actually driving leads, not just traffic.

3. **Landing Page Report**: Shows which page is first in a user's session. High-traffic landing pages with low engagement rate are priority for improvement.

**Explorations to Save**

In the Explore tab, save these as named explorations:

1. "Weekly Performance" - Free Form exploration, last 7 days vs. previous 7 days, metrics: sessions, engagement rate, conversions, conversion rate. Saved for Monday morning review.

2. "Top Content This Month" - Free Form, last 30 days, dimension: page path, metrics: sessions + scroll depth events + conversions. Shows which content is actually working.

3. "Lead Funnel" - Funnel exploration as described in Section 1D.

**The One Dashboard Jared Actually Needs**

For day-to-day reference, set up a dashboard in Looker Studio (free, connects directly to GA4 and GSC):

- Top row: Sessions today vs. yesterday, Conversions this week, Top traffic source this week
- Second row: Top 5 pages by sessions, Top 5 pages by conversions
- Bottom row: Traffic source breakdown (pie chart), Weekly trend (line chart)

Free template: databloo.com/templates/google-analytics-4-looker-studio-template/ - copy and connect to your GA4 property. Takes 20 minutes.

---

## Part 2: Google Search Console (GSC)

### What GSC Is and Why It Is Different from GA4

GA4 tracks what happens AFTER someone arrives on your site. GSC tracks what happens BEFORE they click - what Google shows them, what they search for, and how often they see you.

For a new site like PureBrain.ai that is in the process of being indexed, GSC is arguably more important than GA4 right now because it tells you when Google starts to see you.

---

### Section 2A: The Verification Workflow (Jared Must Do This)

This is the step that unlocks everything.

1. Go to search.google.com/search-console
2. Click "Add Property" > Select "Domain" (not URL Prefix - Domain covers all versions automatically)
3. Enter: purebrain.ai
4. Google shows you a TXT record value (looks like: google-site-verification=xxxxxx)
5. Open Cloudflare dashboard > Select purebrain.ai domain > DNS tab
6. Click "Add record" > Type: TXT, Name: @ (this represents the root domain), Content: paste the google-site-verification value, TTL: Auto > Save
7. Return to GSC and click "Verify"
8. DNS propagation takes 15 minutes to 4 hours with Cloudflare
9. Once verified, go to Indexing > Sitemaps > Add: sitemap_index.xml

**After verification, submit for indexing (priority order)**:
Use the URL Inspection tool (search bar at top of GSC), paste each URL, click "Request Indexing":
1. purebrain.ai/
2. purebrain.ai/ai-readiness-assessment/
3. purebrain.ai/why-95-percent-of-ai-pilots-fail/
4. purebrain.ai/the-ai-trust-gap/
5. purebrain.ai/ai-tool-stack-calculator/
6. purebrain.ai/compare/
7. purebrain.ai/ai-partnership-audit/
8. purebrain.ai/we-both-wrote-this-post/
9. purebrain.ai/about-aether/
10. purebrain.ai/ai-website-analysis/

Daily limit for indexing requests: 10-12 pages. Prioritize the list above today, then do blog posts tomorrow.

---

### Section 2B: Key Metrics and Reports in GSC

**The Performance Report (Your Daily Driver)**

Found at: Performance > Search Results

This shows:
- **Total clicks**: How many times people actually clicked to your site from Google
- **Total impressions**: How many times your pages appeared in Google results (even if no one clicked)
- **Average CTR**: Clicks divided by impressions - industry average for B2B is 2-5%
- **Average position**: Your typical ranking position

**The Quick Win Formula**

In the Performance report, filter by:
- Pages > filter for specific URLs
- Queries > sorted by Impressions, high to low

Look for queries where:
- Impressions are high (100+)
- Position is 4-10
- CTR is below 3%

These are "easy ranking" opportunities. Your page is showing up in Google's top 10 for these queries but not getting clicked. The fix is usually a better title tag and meta description - not new content.

Example query you might find after indexing: "AI readiness assessment" at position 7 with 500 impressions but 1% CTR. Fix: Change the title to "Free AI Readiness Assessment | Know Your AI Adoption Score in 5 Minutes" and the meta description to the specific outcome they get. CTR improvement from 1% to 4% on 500 impressions = 15 additional visitors per month from one change.

**The Index Coverage Report**

Found at: Indexing > Pages

This shows:
- How many pages are indexed
- How many have issues
- Specific errors (404s, redirect chains, duplicate content)

After submitting your sitemap, check this weekly. The goal is all 34 URLs showing as "Indexed, appearing in Search Results." Pages with errors need investigation.

**The Core Web Vitals Report**

Found at: Experience > Core Web Vitals

Shows real-world performance data from Chrome users who visit your site. 2026 thresholds (confirmed updated):

| Metric | Good | Needs Work | Poor |
|--------|------|-----------|------|
| LCP (Largest Contentful Paint) | Under 2.5 seconds | 2.5-4.0 seconds | Over 4.0 seconds |
| INP (Interaction to Next Paint) | Under 150ms (tightened in 2026) | 150-500ms | Over 500ms |
| CLS (Cumulative Layout Shift) | Under 0.10 | 0.10-0.25 | Over 0.25 |
| SVT (Smooth Visual Transitions) | NEW 2026 metric | Measures animation jank | Affects pages with 3D/WebGL |

**PureBrain-specific risk**: INP at 150ms. The assessment form, chatbox interactions, and the animated homepage are the highest-risk elements. The 2026 SVT metric is newly added and specifically relevant to sites with WebGL animations.

---

### Section 2C: Search Query Strategy for AI Consulting

Once indexed, these are the query categories to monitor for PureBrain:

**Brand Queries (Should Appear Within 2-3 Weeks)**
- "PureBrain" + any modifier
- "PureBrain.ai"
- "Aether AI" + any modifier

When these appear in GSC: the site is indexed and Google recognizes it as a brand. The impression count for brand queries grows as more content is published and linked externally.

**Problem-Aware Queries (High Value)**
- "why does AI adoption fail"
- "AI pilot failure"
- "AI readiness assessment"
- "enterprise AI adoption problems"
- "why employees resist AI"

These are the queries that match your blog content. The blog posts targeting these should rank within 30-60 days if GSC is set up and content is indexed.

**Solution-Aware Queries (Highest Conversion Value)**
- "AI partnership for business"
- "AI consulting that actually works"
- "personalized AI for executives"
- "custom AI memory system"
- "ChatGPT alternative for business"

These indicate someone knows they want what you sell. Comparison pages (/purebrain-vs-chatgpt/ etc.) directly target these.

**Tool Queries (Traffic Generators)**
- "AI tool stack for business"
- "free AI readiness test"
- "AI tool calculator"
- "best AI tools for enterprises"

Your calculator and assessment tools are built to capture this traffic.

**Monitoring Protocol**: Once indexed, check GSC Performance report weekly. Filter by date range (last 28 days vs. previous 28 days). Sort queries by Impressions. Note any new queries where you are appearing but not yet clicking. These are content gaps to fill.

---

### Section 2D: AI Visibility in GSC (2026 Update)

In 2026, Google's Performance report now includes data from AI Overviews - the AI-generated answer boxes at the top of Google results. This is a major development.

**What this means**: Your pages can appear inside Google's AI Overviews (the "generative AI" answer at the top of search results) and GSC now shows you when this happens, though currently it appears alongside standard search data, not separately filtered.

**How to optimize for AI Overviews**:

1. **Answer questions directly and early**: Google's AI pulls the most direct, clearly stated answer. Each blog post should answer its core question within the first 100 words. Do not bury the answer at the bottom.

2. **FAQ schema on blog posts**: When Google's AI is looking for answers to specific questions, it heavily uses structured data. Your blog posts have FAQ sections visible to readers but no FAQ schema markup. Adding FAQ schema (JSON-LD) to the 4 blog posts with FAQ sections puts those answers in a format Google's AI can reliably extract.

3. **Definition-style sentences**: For key concepts in the AI consulting space, write definitional sentences: "AI partnership (noun): a model of AI deployment in which the AI system is trained on organization-specific context and works alongside a named human partner rather than being accessed as a generic tool." These get pulled into AI Overviews.

4. **Monitor with branded search**: If AI Overviews answer queries before users click, you will see impressions in GSC without proportional clicks. Your branded search volume growing (people searching "PureBrain.ai" directly) indicates AI visibility - people found you via AI answers, trusted what they saw, and then searched you directly.

---

### Section 2E: Structured Data Opportunities for GSC Rich Results

GSC has a Rich Results report (Enhancements section) that shows which structured data is detected and whether it has errors.

**Currently Confirmed Active on PureBrain.ai**:
- Article schema on blog posts (author: Aether, word count, dates)
- Organization schema
- BreadcrumbList
- WebPage

**Add These to Unlock Additional Rich Results**:

1. **FAQ Schema on Blog Posts** - FAQ results show as expandable Q&A under your search listing. This can double your visual real estate in search results. Implement on the 4+ blog posts that have FAQ sections.

   Template (add to post header or footer via plugin/custom code):
   ```json
   {
     "@type": "FAQPage",
     "mainEntity": [{
       "@type": "Question",
       "name": "Why do 95% of AI pilots fail?",
       "acceptedAnswer": {
         "@type": "Answer",
         "text": "AI pilots fail primarily because..."
       }
     }]
   }
   ```

2. **Person Schema for Aether's Author Page** - In 2026, Google uses E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness) heavily for content ranking, especially in AI-related topics. An AI author is unusual enough that a well-documented Person schema with sameAs links to Bluesky and LinkedIn builds credibility signals.

3. **Service Schema for Paid Offerings** - The $99 website analysis service and the AI partnership subscription can have Service schema markup. This can show pricing in search results for branded queries.

4. **HowTo Schema for Tutorial-Style Content** - Any blog post with step-by-step processes qualifies. "How to assess your team's AI readiness" formatted as HowTo schema can show numbered steps directly in search results.

---

## Part 3: Microsoft Clarity

### What Clarity Is and Why It Matters More Than Most People Realize

GA4 tells you that 70% of users are dropping off the assessment page before completing it. Clarity shows you what those 70% were doing when they left: Did they rage-click on something that wasn't working? Did they scroll back to the top looking for information? Did they get to question 3 and seemingly freeze?

Clarity answers the "why" that GA4 cannot.

And it is completely free - no traffic limits, no feature paywalls, no forced upgrade. It is funded by Microsoft because the data helps train Bing's search algorithms.

---

### Section 3A: Installation (Via GTM - Easiest Path)

Since GTM-WTDXL4VJ is already on PureBrain.ai, Clarity should be installed through GTM rather than as a separate WordPress plugin. This keeps all tracking in one container.

1. Create a Microsoft Clarity account at clarity.microsoft.com
2. Create a new project, name it "PureBrain.ai Production"
3. Copy the Clarity Project ID (format: xxxxxxxxxx)
4. In GTM: New Tag > Tag Type: Custom HTML > paste the Clarity script with your project ID
5. Trigger: All Pages
6. Submit and publish the GTM container

**Note**: Clarity auto-masks sensitive input fields (passwords, credit cards, emails) by default. This is GDPR/CCPA compliant out of the box and cannot be seen in session recordings. This is a feature, not a limitation.

---

### Section 3B: The GA4-Clarity Integration

This is the most powerful feature and almost no one sets it up correctly.

**What it does**: When Clarity and GA4 are connected, Clarity sends a custom dimension to GA4 called `claritydimension`. This dimension contains a URL that links directly to the session recording in Clarity. From inside GA4, you can click on any individual user session and jump directly to watch their session recording.

**How to set it up**:

Step 1 - In Clarity: Settings > Setup > Google Analytics > Toggle on "Link to Google Analytics" > Enter your GA4 Measurement ID (G-XXXXXXXXXX)

Step 2 - In GA4: Admin > Custom Definitions > Custom Dimensions > New Custom Dimension:
- Dimension name: Clarity Session URL
- Scope: Event
- Event parameter: clarityid

Step 3 - Wait 4 hours for the custom dimension to populate in GA4

**What this enables**: When you see in GA4 that an assessment page has 15% conversion rate on Tuesday but 8% on Wednesday, you can pull up Wednesday's sessions and watch session recordings filtered to that page. In 60 seconds of watching, you often see exactly what changed.

**Known limitations (2026)**:
- Clarity does not support GA4 custom segments (it connects at the session level, not segment level)
- Each Clarity project links to one GA4 property only
- High-cardinality data (playback URLs) cannot be passed directly to GA4 reports - Clarity sends a lookup ID instead

---

### Section 3C: Heatmap Analysis Methodology

Clarity offers four heatmap types. Here is when to use each and what to look for:

**Click Heatmap - Use for CTAs and Navigation**

What it shows: Where users actually click, shown as heat intensity (red = most clicks, blue = least)

What to look for on PureBrain.ai:
- Are "Start Your AI Partnership" buttons getting clicks? If the CTA button is not hot, either it is not being seen or the copy is not compelling
- Are users clicking on things that are not links? (indicates confusion about what is clickable)
- On the homepage: are people clicking the animated 3D element, thinking it does something?

Red flags: Any element with substantial click heat that does not do anything (detected by Clarity as "dead clicks")

**Scroll Heatmap - Use for Content and Page Design**

What it shows: How far down users scroll, as a gradient from top (100% see this) to bottom (few see this)

What to look for:
- The "fold line" where scroll rate drops sharply. Content below this line is largely invisible.
- On blog posts: do 75%+ of readers reach the CTA at the bottom? If scroll drops off at 50%, the CTA needs to move higher.
- On the homepage: what percentage of visitors see the pricing or the "Begin Awakening" section?
- On assessment pages: is the drop-off at a specific question?

Benchmark to target: For a conversion-focused page (assessment, pricing), you want 60%+ of visitors reaching the primary CTA. Below 40% means the CTA needs to move up.

**Rage Click Analysis - Your Daily Priority Check**

What it shows: Elements that users click repeatedly in quick succession out of frustration

Rage clicks are the highest-signal behavioral data Clarity provides. A rage click pattern means:
- A button is not working (technical bug)
- A link destination is wrong
- Something looks clickable but is not
- Page is loading slowly and users are clicking impatiently

**The 5% rule**: If more than 5% of sessions on a specific page show rage clicks on the same element, treat it as a confirmed UX problem and fix it that week.

For PureBrain.ai: Watch especially for rage clicks on:
- The PayPal payment button on /ai-website-analysis/ (any rage click here = lost revenue)
- The assessment form submit button
- The "Begin Awakening" CTA on the homepage
- Navigation menu links on mobile

**Scroll Depth by Segment - Advanced Technique**

Clarity allows filtering heatmaps by:
- New vs. returning visitors
- Traffic source (organic, direct, social)
- Device (mobile, tablet, desktop)
- Country

Use this to compare mobile vs. desktop scroll depth on the homepage. Given that the homepage has WebGL 3D animations that may not load on mobile, mobile users may have a completely different experience than desktop users. If mobile users scroll dramatically less, they are likely seeing a broken or slow page.

---

### Section 3D: Session Recording Review Methodology

Recording methodology is where most teams fail. They watch recordings randomly and get anecdotal observations. The proper method is systematic.

**Step 1: Filter Before You Watch**

Never watch recordings without filtering. Raw recording lists are overwhelming and most sessions are not informative. Use these filters (Clarity left sidebar):

- **Dead clicks**: Sessions with at least one dead click. These always contain friction.
- **Rage clicks**: Sessions with at least one rage click. These always contain frustration.
- **Quick back**: Sessions that quickly navigated back to previous page. Indicates unmet expectations.
- **Long session**: Duration over 5 minutes on a conversion page. These users are highly intent and you can learn why they did or did not convert.
- **Specific page**: Filter by URL to see all sessions on /ai-readiness-assessment/ or /compare/ or whatever you are investigating.

**Step 2: Watch in Batches of 5**

Watch 5 recordings from the same filter in a row. After 5, you start noticing patterns. After 10, you know what the problem is. You do not need to watch 100 recordings.

The question to hold in mind while watching: "What is this person trying to do and what is stopping them?"

**Step 3: Document What You Observe**

After each batch of 5, write one sentence about the pattern you observed:
- "Users who rage-click on the assessment form are clicking the 'Next' button before the form validates"
- "Mobile users on the compare page are clicking competitor logos expecting to see comparison details, but nothing happens"
- "Long-session users on /about-aether/ seem to scroll to the bottom, then back to the top, suggesting they want to do something but cannot find the action to take"

**Step 4: Quantify Before Fixing**

Before spending development time fixing a UX issue found in recordings, verify it in Clarity's quantitative data. If 3 recordings showed users confused by the compare page, check: what percentage of total sessions on /compare/ have dead clicks? If it is 40%, fix it immediately. If it is 2%, it may be an edge case.

**Step 5: Validate After Fixing**

After a UX fix is deployed, watch 5 more recordings from the same filter. If the behavior pattern changed, the fix worked. If not, the root cause is different.

---

### Section 3E: Pages to Prioritize in Clarity

These are the pages where Clarity data is most valuable for PureBrain.ai, in priority order:

**Priority 1: /ai-readiness-assessment/ and /ai-partnership-audit/**
These are your primary lead generation pages. Every percentage point of conversion improvement here directly impacts revenue. Watch 10 recordings from these pages weekly. Look for rage clicks, form abandonment patterns, and points of confusion.

**Priority 2: Homepage (purebrain.ai)**
The homepage is the first impression for the majority of visitors. Use scroll heatmap to verify the "Begin Awakening" CTA is in the visible zone. Use click heatmap to see if the 3D element is drawing clicks away from CTAs. Check mobile vs. desktop separately.

**Priority 3: /ai-website-analysis/ (the $99 offer)**
Every visitor to this page is considering a purchase. Any rage click pattern here is a direct revenue problem. Watch 5 sessions per week specifically filtered to this page. Look at where users drop off in the scroll - if they are not reaching the PayPal button, either the price is the issue or the value proposition above the fold is not convincing.

**Priority 4: Blog posts with highest GA4 traffic**
Use GA4 to identify which blog posts get the most traffic, then go to Clarity and filter recordings by those page URLs. The question: are readers engaging with inline CTAs? Are they scrolling to the bottom? Are they clicking through to product pages?

**Priority 5: /compare/ and /purebrain-vs-* comparison pages**
These pages target switching-intent users. Any confusion or dead click here is losing a warm lead. Check: do users understand the comparison format? Do they know what to do after reading?

---

## Part 4: The Three Tools Working Together

### The Unified Insight Loop

The three tools form a complete picture when used in sequence:

```
GSC (before the click) → GA4 (after the click, quantitative) → Clarity (behavioral, qualitative)
```

**Example workflow in practice**:

1. GSC shows: "AI readiness assessment" query is generating 200 impressions but only 2 clicks (1% CTR, position 8)

2. Action: Fix the title and meta description on the assessment page. New title: "Free AI Readiness Assessment | Get Your AI Adoption Score in 5 Minutes"

3. Two weeks later, GSC shows CTR improved to 4% on the same query: 8 clicks instead of 2 per week from that query alone

4. GA4 shows the new visitors from that query are landing on the assessment page, but 80% leave without starting the assessment

5. Clarity session recordings filtered to those sessions (via the GA4-Clarity integration): recordings show users reading the page header, then scrolling to the middle, and leaving without clicking anything. The "Start Assessment" button is below the fold.

6. Fix: Move the assessment CTA button above the fold. GA4 shows assessment start rate improves from 20% to 45%. Conversions increase.

This loop from GSC (finding them) to GA4 (measuring behavior) to Clarity (diagnosing why) is the methodology that turns data into decisions.

---

### Data Flow Architecture

```
Visitor searches Google
        ↓
GSC captures: query, position, CTR, impressions (pre-click)
        ↓
Visitor clicks, arrives on site
        ↓
GA4 captures: source/medium, page views, events, time on page, conversions
        ↓
Clarity captures: scroll depth, click locations, session recording
        ↓
Clarity sends session URL to GA4 (via integration)
        ↓
GA4 allows "Watch Session Recording" link in individual user reports
        ↓
GA4 sends qualified audience to Google Ads (optional, Month 2-3)
        ↓
GSC measures if new organic content starts driving impressions for target queries
        ↓
Loop continues
```

**Link GA4 to GSC** (in GA4 Admin): Admin > Product Links > Search Console Linking > Link property > Select purebrain.ai. Once linked, GA4 gets organic search query data from GSC, giving you a "Queries" dimension inside GA4 reports without needing to visit GSC separately.

---

## Part 5: Weekly Analytics Review Checklist

This is the structured review process. Total time: 20 minutes per week, every Monday morning.

---

### Monday Morning Review (20 Minutes)

**GA4 - 10 minutes**

Open GA4. Set date range to last 7 days vs. previous 7 days (use the comparison toggle).

- [ ] Sessions this week vs. last week: up or down by what percent?
- [ ] Top traffic source this week: is the primary source organic, direct, social, or email?
- [ ] Conversion events this week: how many generate_lead events fired? How many assessment_completed?
- [ ] Top 3 pages by sessions: are they the pages you expected? Any surprise?
- [ ] Any pages with unusual bounce/exit rate spikes? (check Landing Page report, sort by exits)
- [ ] If any email campaigns went out this week via Brevo: check traffic from email source/medium

Time target: 10 minutes. You are scanning for anomalies and wins, not deep diving.

**GSC - 5 minutes**

Open GSC. Performance report. Set to last 28 days.

- [ ] Total clicks this week vs. last week: up or down?
- [ ] Any new high-impression queries (over 100 impressions) where position is 4-10? (quick win opportunity)
- [ ] Check Indexing > Pages: are all 34+ pages showing as indexed?
- [ ] Any coverage errors? (red X items in Indexing > Pages)
- [ ] Core Web Vitals: any new pages moved from "Good" to "Needs Improvement"?

Time target: 5 minutes.

**Clarity - 5 minutes**

Open Clarity. Set to last 7 days.

- [ ] Overall rage click rate: up or down from last week?
- [ ] Check: is any page above 5% rage clicks? If yes, watch 3 recordings from that page immediately.
- [ ] Quick scan of scroll heatmap on the single most important conversion page this week (whichever page Jared is focusing on that week)
- [ ] Watch 3 filtered session recordings from the highest-traffic page (filter: rage clicks OR dead clicks)

Time target: 5 minutes.

**Weekly Decision (1 minute)**

After the review, write one action for the week based on what the data showed:
- "Optimize the meta description for [query] showing 200 impressions at position 7"
- "Move the assessment CTA above the fold on mobile (Clarity showed scroll drop-off)"
- "Write a blog post about [topic] that is generating GSC impressions but we have no content for"

One clear action. Not five. One.

---

### Monthly Deep Dive (60 Minutes, First Monday of Month)

Run this in addition to the weekly review on the first Monday of each month.

**GA4 Monthly (25 minutes)**

- [ ] Traffic trend (month over month, 3-month comparison): what is the growth rate?
- [ ] Conversion rate by traffic source: which source converts best (organic, email, social)?
- [ ] Top 10 pages by conversions: are these the pages we expected to convert? Any surprises?
- [ ] Funnel visualization (Assessment funnel): where is the biggest drop-off point?
- [ ] Audience report: how large are the key audiences now (assessment completers, high-value readers)?
- [ ] Blog content performance: which posts have the highest engagement rate? What topics work?
- [ ] New vs. returning visitor ratio: are we retaining visitors? Returning visitors should grow each month.
- [ ] Attribution check: for conversions this month, what was the first touch? What was the last? (Use the Attribution report in GA4 > Advertising section)

**GSC Monthly (15 minutes)**

- [ ] Growth in total impressions month over month: Google is seeing the site more as it indexes
- [ ] New queries appearing: what are people searching for that leads them to us for the first time?
- [ ] Queries where we are gaining position (improving rank): which posts are climbing?
- [ ] Queries where we are losing position: any existing pages declining?
- [ ] Links report: did we gain any new backlinks? (Under Overview > Links in GSC)
- [ ] Core Web Vitals: are the numbers improving or degrading as we add new pages?
- [ ] Rich Results report: are FAQ schemas, Article schemas showing errors?

**Clarity Monthly (20 minutes)**

- [ ] Site-wide heatmap comparison: click behavior on homepage this month vs. last month. Has it changed after any design updates?
- [ ] Watch 10 session recordings on the primary conversion page. Document the patterns in a short note.
- [ ] Mobile vs. desktop heatmap comparison on homepage and assessment page: are mobile users experiencing the site the same way as desktop users?
- [ ] Scroll depth report on the 3 highest-traffic blog posts: how far are readers getting? Are they reaching the CTAs?
- [ ] Dead click report: any elements consistently getting dead clicks that were not there last month?

**Monthly Action Plan Output**

At the end of the monthly review, write three actions for the month:
1. One SEO action from GSC data
2. One conversion optimization action from GA4 + Clarity data
3. One content action from GA4 content performance data

---

## Part 6: Quick Wins - Implement This Week

These are changes that require minimal effort but meaningful impact, based on current site state and analytics best practices.

**Quick Win 1: GA4 Data Retention (5 minutes, Jared only)**

Change data retention from 2 months to 14 months immediately. Every day this is not done, historical data is at risk. This is a single Admin settings change that cannot be undone retroactively.

**Quick Win 2: Set Assessment Completion as GA4 Conversion Event**

Once the assessment_completed custom event is implemented via GTM, mark it as a conversion in GA4: Admin > Events > toggle "Mark as conversion" next to assessment_completed. This immediately unlocks conversion reports, funnel analysis, and audience building from this event.

**Quick Win 3: OG Tags on /compare/ and /about-aether/**

These pages have no social preview. When Jared shares the compare page on LinkedIn, it shows as a bare URL. A 15-minute OG tag fix on both pages makes every social share look professional. Aether can do this without Jared's involvement.

**Quick Win 4: FAQ Schema on Top 3 Blog Posts**

Adding FAQ schema JSON-LD to the three highest-traffic blog posts (Trust Gap, 95% AI Pilots Fail, CEO vs Employee Gap) can unlock FAQ rich results in Google within 1-2 weeks of indexing. Each FAQ result shows expandable Q&A under the search listing, dramatically increasing click-through rate. Aether can implement this in 30 minutes per post.

**Quick Win 5: GSC Alert Emails**

In GSC: Settings > Email notifications > Enable all. You will automatically receive emails when:
- Coverage drops (pages getting deindexed)
- Core Web Vitals problems are newly detected
- Manual actions are applied (rare but critical to know immediately)
This costs nothing and ensures you learn about critical issues before they compound.

**Quick Win 6: Clarity Custom Tags on Key Pages**

In Clarity, set up Custom Tags for your key page categories. This allows filtering heatmaps and recordings by page type instantly. Tags to create:
- `page_type: assessment` on all assessment pages
- `page_type: blog` on all blog posts
- `page_type: product` on /ai-website-analysis/ and /website-execution/
- `page_type: comparison` on all /purebrain-vs-*/ pages

Implementation: Add via GTM as Custom HTML tags that fire on specific URL patterns, calling `window.clarity("set", "page_type", "assessment")` with the appropriate value.

---

## Part 7: Advanced Tactics for Month 2-3

These require GA4/GSC data to be flowing for 4+ weeks before implementing.

**Advanced Tactic 1: Predictive Audiences in GA4**

Once GA4 has 1,000+ users with conversion events in the past 28 days, predictive audiences become available:
- Likely 7-day purchasers: users predicted to convert in the next 7 days
- Likely 7-day churners: users who converted but are predicted to disengage

If running Google Ads: these audiences can be used for bid adjustments. Show ads more aggressively to users in the "likely 7-day purchaser" bucket.

For organic: use the "likely 7-day churner" list to understand behavioral patterns - what did they do on the site before becoming inactive? Fix that friction point.

**Advanced Tactic 2: BigQuery Export for Custom Analysis**

GA4 free tier allows daily BigQuery export. This is the path to custom SQL analysis that GA4's interface cannot do natively - specifically: multi-session path analysis (seeing the complete sequence of pages across 5+ visits before conversion), cohort analysis by acquisition channel, and revenue attribution across months.

Setup: GA4 Admin > Product Links > BigQuery Links > Link to a Google Cloud project (requires free Google Cloud account). The export runs daily automatically.

**Advanced Tactic 3: GSC Brand Volume as AI Visibility Proxy**

In 2026, a significant portion of traffic comes via AI Overviews - people find answers in Google's AI-generated response, trust the source, and then search the brand name directly rather than clicking the organic link. This "dark traffic" does not show as organic in GA4.

The proxy metric: monthly branded search volume in GSC (filter Performance report by queries containing "PureBrain" or "purebrain.ai"). This volume growing faster than direct traffic in GA4 indicates growing AI search visibility. Track this monthly starting from week 4 of indexing.

**Advanced Tactic 4: Content Velocity and Indexing Velocity Correlation**

Build a simple tracking spreadsheet: date a blog post was published, date it was first indexed (check in GSC URL inspection), date it first appeared in GSC Performance report, peak impressions in first 28 days. After 10 posts, patterns emerge:
- Which topics index fastest?
- Which topics get impression volume fastest?
- What average position do posts start at and where do they settle after 60 days?

This tells you which content types the algorithm favors and where to focus writing efforts.

**Advanced Tactic 5: Clarity Conversion Heatmap (Advanced Feature)**

Clarity recently added a Conversion Heatmap feature that shows which elements users clicked before converting vs. which elements they clicked when they did not convert. This reveals causation rather than correlation - not just where people click, but what clicking leads to a conversion.

For PureBrain.ai: once conversions are flowing, run the conversion heatmap on the assessment page and homepage. You will see: users who clicked [specific element] converted at 40% rate vs. users who did not click that element converting at 5% rate. That element is your highest-value real estate on the page.

---

## What Jared Needs to Do vs. What Aether Handles

### Jared's Required Actions (Total: 75 Minutes Across This Week)

| Task | Why Jared Only | Time |
|------|---------------|------|
| Verify GSC via Cloudflare DNS | Requires Cloudflare account login | 30 minutes |
| Check GTM container: confirm GA4 and Clarity tags | Requires GTM account access | 10 minutes |
| Change GA4 data retention to 14 months | Requires GA4 Admin role | 5 minutes |
| Enable Google Signals in GA4 | Requires GA4 Admin role | 5 minutes |
| Set up Clarity-GA4 integration (in Clarity settings) | Requires Clarity account access | 10 minutes |
| Share GA4 API access with Aether (for automation) | Requires GA4 Admin role | 10 minutes |
| Check WonderPush dashboard for subscriber stats | Requires WonderPush login | 5 minutes |

**The single most important action**: GSC verification. Everything else listed in this report depends on GSC being active.

### Aether Handles (No Jared Input Needed, Green Light Required)

- OG tag fixes on /compare/, /about-aether/, /migrate/ (30 minutes)
- FAQ schema implementation on top 3 blog posts (90 minutes)
- Custom Clarity tags implementation via GTM (30 minutes)
- GA4 custom event implementation via GTM once GA4 tag is confirmed (3 hours)
- Looker Studio dashboard build once GA4 is confirmed active (2 hours)
- Weekly automated analytics brief via Telegram (2 hours to build, then runs daily)
- Nightly site improvement automation incorporating analytics data (ongoing)

---

## Sources

- [GA4 Lead Generation Reports Guide](https://www.northern.co/blog/new-ga4-lead-generation-reports-explained-smarter-way-track-leads/) - Northern Commerce
- [GA4 Cross-Channel Conversion Tracking 2026](https://www.y77.ai/blogs/ga4-cross-channel-conversion-tracking-2026-setup-guide) - Y77.ai
- [GA4 for B2B SaaS Setup Guide](https://vigitalinc.com/blog/how-to-set-up-ga4-for-b2b-saas/) - Vigital
- [GA4 Custom Segments That Actually Matter](https://dev.to/synergistdigitalmedia/ga4-custom-segments-that-actually-matter-7-configurations-most-marketers-overlook-184j) - Dev.to
- [Google Analytics Actionable Insights 2026](https://almcorp.com/blog/google-analytics-actionable-insights-complete-guide-2026/) - ALM Corp
- [GA4 Lead Generation Events - Stape](https://stape.io/news/ga4-new-recommended-events-lead-generation) - Stape.io
- [GA4 Audience Templates for Lead Gen](https://mercadoglobalmedia.com/google-analytics-4-lead-generation-reports-audiences/) - Mercado Global Media
- [Google Search Console Complete 2026 Guide](https://almcorp.com/blog/google-search-console-complete-guide/) - ALM Corp
- [Google Search Console 2026 Guide](https://seohq.github.io/google-search-console-guide) - SEO HQ
- [SEO Trends 2026: AI Overviews and B2B](https://almcorp.com/blog/seo-trends-2026-rank-google-ai-search/) - ALM Corp
- [Core Web Vitals 2026 Update](https://www.wirefarm.com/googles-2026-core-web-vitals-update-what-it-means-for-your-business-website.html) - Wirefarm
- [GEO and SEO Predictions 2026 for B2B](https://www.firebrand.marketing/2025/12/geo-and-seo-predictions-2026/) - Firebrand Marketing
- [Microsoft Clarity GA4 Integration](https://learn.microsoft.com/en-us/clarity/ga-integration/ga4-integration) - Microsoft Learn
- [Microsoft Clarity Understanding User Behavior 2026](https://www.bounteous.com/insights/2026/02/11/microsoft-clarity-understanding-user-behavior-beyond-numbers/) - Bounteous
- [Microsoft Clarity for Startups 2026](https://blog.mean.ceo/microsoft-clarity-for-startups/) - Mean CEO
- [How to Integrate Clarity and GA4](https://www.rootandbranchgroup.com/integrate-microsoft-clarity-and-google-analytics/) - Root and Branch
- [GA4 Looker Studio Templates](https://www.databloo.com/templates/google-analytics-4-looker-studio-template/) - Databloo
- Prior memory: `.claude/memory/agent-learnings/web-researcher/2026-02-22--analytics-stack-ga4-gsc-clarity.md`
- Prior memory: `.claude/memory/agent-learnings/web-researcher/2026-02-23--purebrain-analytics-deep-dive.md`
- Prior memory: `.claude/memory/agent-learnings/web-researcher/2026-02-21--google-search-console-setup-patterns.md`
- Prior memory: `.claude/memory/agent-learnings/web-researcher/2026-02-23--gsc-indexing-status-purebrain.md`

---

*Report generated: 2026-02-24*
*Research method: Current web sources (Feb 2026) cross-validated with institutional memory from prior analytics research sessions*
*Confidence: HIGH on platform mechanics and best practices (confirmed via multiple authoritative sources including official documentation)*
*Confidence: HIGH on PureBrain-specific recommendations (site context confirmed in prior sessions)*
