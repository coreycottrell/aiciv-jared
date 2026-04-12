# Analytics Platforms Audit: purebrain.ai
**Prepared by**: Aether (web-researcher)
**Date**: 2026-02-22
**Status**: Ready for Jared's Morning Review
**Scope**: GA4, Google Search Console, Microsoft Clarity

---

## Executive Summary

purebrain.ai currently lacks a complete analytics stack. This audit defines exactly what to set up, how to do it, in what order, and what Aether can handle vs what requires Jared's manual action. The full stack (GA4 + Search Console + Clarity) can be operational within **6-8 hours of focused setup time**, most of which Aether can execute directly.

**Priority order**: Search Console first (fastest, SEO-critical) → GA4 second (conversion intelligence) → Clarity third (behavior intelligence).

---

## SECTION 1: Google Analytics 4 (GA4)

### Why GA4 Matters for PureBrain

GA4 tells you *what* users do after they arrive: which pages they visit, where they drop off, which CTAs they click, and whether they convert. Without GA4, you're flying blind on conversion performance.

---

### 1.1 Setup Checklist

| Step | Task | Who | Time | Priority |
|------|------|-----|------|----------|
| 1 | Create GA4 property at analytics.google.com | Jared (needs Google account) | 10 min | P0 |
| 2 | Create a Web data stream for purebrain.ai | Jared | 5 min | P0 |
| 3 | Install tracking via WordPress plugin (Site Kit by Google) OR paste `<head>` code | Aether can do via WP plugin | 15 min | P0 |
| 4 | Enable Enhanced Measurement (scroll, outbound clicks, video, file downloads) | Aether | 5 min | P0 |
| 5 | Verify data flowing in DebugView (real-time) | Aether | 10 min | P0 |
| 6 | Configure conversion events (see below) | Aether | 30 min | P1 |
| 7 | Create custom dimensions (see below) | Aether | 20 min | P1 |
| 8 | Link to Search Console | Jared (both properties needed) | 5 min | P1 |
| 9 | Adjust data retention to 14 months (default is 2) | Aether | 2 min | P1 |
| 10 | Set up Lead Generation report collection | Aether | 10 min | P2 |
| 11 | Create audiences for remarketing | Aether | 20 min | P2 |
| 12 | Link to Google Ads (if/when ads start) | Jared | 5 min | P3 |

**Total setup time**: ~2-2.5 hours. Steps 1-2 require Jared. Steps 3-11 Aether can handle once access is granted.

---

### 1.2 Events to Track for PureBrain

#### Automatically Collected (Zero Setup Required)
These fire the moment GA4 is installed with Enhanced Measurement ON:

- `page_view` - Every page load
- `scroll` - When user reaches 90% of page depth (single threshold)
- `click` - Outbound clicks (links leaving purebrain.ai)
- `session_start` - Each new session
- `first_visit` - First time a user visits
- `user_engagement` - When page is active for 10+ seconds
- `video_start/progress/complete` - For embedded YouTube videos

#### Custom Events to Implement (High Priority)

These require Google Tag Manager (GTM) or code installation. Aether can set these up via GTM:

**Conversion-Critical Events:**

| Event Name | What It Tracks | Why It Matters |
|-----------|----------------|----------------|
| `cta_click` | Any "Begin Awakening" / "Start Your AI Partnership" button click | Primary conversion path |
| `generate_lead` | Assessment form submission completion | Google's official lead gen event |
| `chat_start` | User sends first message to PureBrain chat | High-intent engagement |
| `chat_message_sent` | Each message sent in chat | Depth of engagement |
| `assessment_start` | User begins AI Partnership Assessment | Mid-funnel intent |
| `assessment_complete` | User finishes assessment | High-intent conversion |
| `payment_initiated` | User starts checkout / PayPal flow | Near-conversion signal |
| `purchase` | Payment confirmed | Revenue event |

**Engagement Events:**

| Event Name | What It Tracks | Why It Matters |
|-----------|----------------|----------------|
| `scroll_depth_25` | User scrolls 25% of homepage | Engagement baseline |
| `scroll_depth_50` | User scrolls 50% of homepage | Mid-page engagement |
| `scroll_depth_75` | User scrolls 75% of homepage | High engagement signal |
| `blog_read_complete` | User reaches bottom of blog post | Content quality indicator |
| `newsletter_subscribe` | Neural Feed subscription | Audience building |
| `share_click` | Social share button clicked | Viral coefficient |
| `video_play` | Homepage video/avatar interaction | Trust-building engagement |

**Implementation Note**: Use Google Tag Manager for all custom events. GTM allows Aether to deploy tracking changes without touching WordPress code directly - safer and faster.

---

### 1.3 Conversion Goals (What to Mark as "Conversions" in GA4)

GA4 separates "tracking events" from "conversion events." Only business-critical actions should be marked as conversions. Mark these 5 as conversions in GA4 Admin > Conversions:

1. **`generate_lead`** - Assessment or contact form completion (primary)
2. **`purchase`** - Payment confirmed (revenue)
3. **`assessment_complete`** - Full assessment done (high intent)
4. **`newsletter_subscribe`** - Neural Feed signup (audience)
5. **`chat_start`** - First chat message (engagement conversion)

**Why not mark everything?** GA4 conversion attribution works better when you're precise. 5 well-defined conversions beats 20 fuzzy ones.

---

### 1.4 Lead Generation vs E-Commerce Configuration

PureBrain is **primarily a lead generation + service business** with a payment component. The right configuration is:

| Configuration | Use When | For PureBrain |
|--------------|----------|---------------|
| **E-Commerce** | Physical products, shopping cart, catalog | The `purchase` event only |
| **Lead Generation** | Consultations, demos, form submissions | Primary configuration |
| **Hybrid** | Services with online payment option | PureBrain's situation |

**Recommended setup for PureBrain:**

1. Activate the **Lead Generation** report collection in GA4 Library
   - Admin > Library > Business Objectives > Generate Leads
   - This enables the Lead Acquisition report and 8 audience templates

2. Implement Google's 6 lead events in order of sales funnel:
   - `generate_lead` (form submission) - implement first
   - `qualify_lead` (Jared's sales judgment, can be manual or triggered by assessment score)
   - `close_convert_lead` (paid, activated) - implement after payment flow is live

3. For the **payment side**, implement these e-commerce events only:
   - `begin_checkout` - when user clicks Buy/Subscribe
   - `purchase` - when PayPal confirms payment

**This hybrid approach** gives you the Lead Acquisition funnel report (seeing drop-off at each stage) AND the revenue attribution that comes from e-commerce events.

---

### 1.5 Custom Dimensions Worth Setting Up

Custom dimensions let you slice your data in ways standard GA4 can't. These 6 are high-value for PureBrain:

| Dimension Name | Scope | What It Captures | Business Value |
|---------------|-------|-----------------|----------------|
| `user_type` | User | new_visitor / returning / active_user / customer | Segment behavior by relationship stage |
| `traffic_source_detail` | Session | organic_google / bsky / linkedin / email / direct | Which channels bring high-quality visitors |
| `content_engagement_level` | Event | low (< 25% scroll) / medium (25-75%) / high (75%+) | Identify best-performing content |
| `assessment_score` | User | 0-100 score from AI readiness assessment | Connect score to conversion probability |
| `chat_session_length` | Session | 1_message / 2-5 / 6-10 / 10+ | Measure conversation quality |
| `subscription_tier` | User | free / monthly / annual | Revenue segmentation |

**Setup steps**: GA4 Admin > Data display > Custom definitions > Create custom dimension. Note: after creation, GA4 takes up to 4 hours to start populating the dimension in reports.

---

### 1.6 Reports to Check: Daily, Weekly, Monthly

#### Daily (5-minute check)

1. **Real-time Report** (Reports > Real-time)
   - Current active users and pages
   - Check after any content publish or campaign launch

2. **Conversions (last 7 days)** (Reports > Conversions)
   - Are conversions trending up or down week-over-week?
   - Flag any day with 0 conversions for investigation

3. **Acquisition Overview** (Reports > Acquisition > Overview)
   - Which channels drove traffic today?
   - Any unexpected spikes or drops?

#### Weekly (15-minute deep dive)

1. **Engagement Report**
   - Average engagement time per page
   - Pages with highest vs lowest engagement
   - Bounce rate trends

2. **Conversion Path Report** (Advertising > Attribution > Conversion paths)
   - What touch points precede conversions?
   - Which blog posts assist conversions?

3. **Landing Pages Report** (Engagement > Landing pages)
   - Homepage vs blog posts vs assessment page performance
   - Where are people entering and what do they do next?

4. **User Acquisition by Channel**
   - Bluesky, LinkedIn, email, organic - which is growing?

#### Monthly (30-minute strategic review)

1. **Funnel Exploration** (Explore > Funnel exploration)
   - Define funnel: Landing page > Chat start > Assessment > Payment
   - Where is the biggest drop-off?

2. **User Lifetime Report** (Reports > Retention)
   - How long are users staying engaged?
   - Cohort analysis: visitors from month X, are they returning?

3. **Page Value Analysis**
   - Which pages most correlate with conversions?
   - Are blog posts driving assessment completions?

4. **Geographic Report**
   - Where are your highest-intent users located?

---

### 1.7 GA4 Integrations

#### Search Console Integration (P1 - Do This)
- Links organic search data to user behavior
- Shows which queries drive engaged users vs bouncy traffic
- Setup: GA4 Admin > Property Settings > Product links > Search Console links

#### Google Ads Integration (P3 - Future)
- Enables conversion import back to Ads
- Required for smart bidding strategies
- Only relevant when paid campaigns start

#### BigQuery Integration (P2 - When Ready)
- Exports raw event data for custom SQL analysis
- Enables joining GSC + GA4 data in one place
- Looker Studio dashboards become possible
- Free tier: 10GB/month storage, 1TB queries
- Setup: GA4 Admin > Property Settings > Product links > BigQuery links

#### Official Documentation
- [GA4 Setup Guide](https://support.google.com/analytics/answer/9304153)
- [GA4 Recommended Events](https://developers.google.com/analytics/devguides/collection/ga4/reference/events)
- [GA4 Custom Dimensions](https://support.google.com/analytics/answer/14240153)
- [GA4 Lead Gen Reports](https://support.google.com/analytics/answer/12370596)

---

## SECTION 2: Google Search Console (GSC)

### Why GSC Matters for PureBrain

GSC is the only tool that shows you exactly what Google knows about your site: which queries are surfacing your pages, which pages are indexed, and where technical SEO issues exist. GA4 shows what happens *after* the click; GSC shows what happens *before* it.

Prior research (2026-02-21) confirmed purebrain.ai was likely not indexed yet. GSC setup is urgently needed.

---

### 2.1 Setup Checklist

| Step | Task | Who | Time | Priority |
|------|------|-----|------|----------|
| 1 | Go to search.google.com/search-console | Jared (needs Google account) | 2 min | P0 |
| 2 | Add property - choose "Domain" property type for full coverage | Jared | 5 min | P0 |
| 3 | Verify via Cloudflare DNS TXT record (recommended) | Jared in Cloudflare dashboard | 15 min | P0 |
| 4 | Alternatively: verify via Yoast SEO HTML tag method (easier) | Aether via WP Admin | 10 min | P0 |
| 5 | Submit sitemap: sitemap_index.xml | Aether | 5 min | P0 |
| 6 | Request indexing for key pages (homepage, assessment, blog posts) | Aether | 15 min | P1 |
| 7 | Noindex legacy test pages (purebrain-3, purebrain-4, pay-test) | Aether via Yoast | 15 min | P1 |
| 8 | Link GSC to GA4 | Jared (both accounts needed) | 5 min | P1 |
| 9 | Check Coverage report for errors | Aether | 10 min | P2 |
| 10 | Review Core Web Vitals report | Aether | 10 min | P2 |

**Total setup time**: ~1.5 hours. Steps 1-3 require Jared. Steps 5-10 Aether can handle.

---

### 2.2 Verification Methods (Ranked by Ease for PureBrain)

**Option A: Yoast SEO HTML Tag (RECOMMENDED for speed)**
1. GSC > Add property > URL prefix (https://purebrain.ai)
2. Choose "HTML tag" under Other verification methods
3. Copy the meta tag code
4. WP Admin > Yoast SEO > General > Webmaster Tools > Google Verification Code > Paste > Save
5. Back in GSC > Verify
- **Time**: 10 minutes
- **Risk**: Low - Yoast persists this tag automatically

**Option B: Cloudflare DNS TXT (RECOMMENDED for domain property)**
1. GSC > Add property > Domain (purebrain.ai - no https://)
2. Copy TXT verification code
3. Cloudflare Dashboard > DNS > Add Record: Type=TXT, Name=@, Content=paste code, TTL=Auto
4. Back in GSC > Verify (may need 15-60 min for propagation)
- **Time**: 20-30 minutes including wait
- **Risk**: Very low - DNS verification survives theme/plugin changes

**Why Domain property is better**: It automatically covers www., non-www., http, https, and all subdomains in a single property. URL prefix only covers one variant.

---

### 2.3 Key Metrics to Monitor

| Metric | What It Tells You | Target State |
|--------|------------------|--------------|
| **Total Impressions** | How often Google shows purebrain.ai pages | Growing month-over-month |
| **Total Clicks** | Actual visits from organic search | Growing, ideally faster than impressions |
| **Average CTR** | Clicks / Impressions | Industry benchmark: 2-5% for informational, 5-10% for brand terms |
| **Average Position** | Mean ranking for all queries showing your site | Target: move all P4-P10 keywords to P1-P3 |
| **Coverage: Valid pages** | How many pages Google has indexed | Should match your intended public pages |
| **Core Web Vitals: Good URLs** | Pages passing LCP, INP, CLS thresholds | Target: 90%+ "Good" |

---

### 2.4 How to Find Quick-Win Keyword Opportunities

This is where GSC pays off most immediately. Follow this process weekly:

**Step 1: Find "Almost Top 3" Keywords**
- GSC > Performance > Search results
- Filter: Average position between 4 and 10
- Sort by Impressions (high to low)
- These keywords Google already thinks you're relevant for - small optimization = big traffic jump

**Step 2: Find High Impressions, Low CTR**
- Filter: Impressions > 100, CTR < 3%
- These pages are visible but not compelling in search results
- Fix: Rewrite title tag and meta description to be more click-worthy
- This requires zero content changes - just metadata updates

**Step 3: Find Questions You're Not Answering**
- GSC > Performance > Queries tab
- Filter by queries containing "how", "what", "why", "best", "is"
- If you're appearing for a question but not ranking in top 3, create or expand content specifically answering that question

**Step 4: Monitor Branded Queries**
- Filter queries containing "purebrain" or "pure brain"
- Branded search volume growth indicates brand awareness building (from Bluesky, LinkedIn, word of mouth)
- As AI search grows (Perplexity, ChatGPT search), branded queries become the primary indicator of real awareness

---

### 2.5 Core Web Vitals Monitoring

Google's 2026 update tightened thresholds significantly. PureBrain's interactive homepage (WebGL, animations, 3D elements) is at high risk for CWV issues.

**2026 Thresholds:**

| Metric | Good | Needs Improvement | Poor | What Causes Failures |
|--------|------|-------------------|------|---------------------|
| **LCP** (Largest Contentful Paint) | < 2.5s | 2.5s - 4s | > 4s | Unoptimized hero images, slow server response, render-blocking JS |
| **INP** (Interaction to Next Paint) | < 150ms | 150ms - 500ms | > 500ms | Heavy JavaScript, unoptimized event handlers, third-party scripts |
| **CLS** (Cumulative Layout Shift) | < 0.1 | 0.1 - 0.25 | > 0.25 | Images without dimensions, late-loading fonts, injected ads |
| **SVT** (Smooth Visual Transitions) | NEW in 2026 | Janky transitions | Poor | Hero images loading late, font shifts, ad rendering |

**For PureBrain specifically**: The 3D WebGL elements and animated avatar are high INP and LCP risks. Monitor these pages:
- Homepage (high risk due to 3D/WebGL)
- Assessment page (form interactions affect INP)
- Blog posts (lower risk, text-heavy)

**How to check**: GSC > Experience > Core Web Vitals. Also use PageSpeed Insights (pagespeed.web.dev) for per-page analysis. Mobile score below 80 = attention needed; below 60 = urgent.

---

### 2.6 Index Coverage Issues to Watch

In GSC > Indexing > Pages, watch for:

| Status | What It Means | Action |
|--------|--------------|--------|
| **Excluded: noindex tag** | Page has noindex set - correct if intentional | Verify these are test pages only |
| **Crawled - not indexed** | Google visited but chose not to index | Improve content quality or relevance |
| **Discovered - not crawled** | Google knows page exists but hasn't visited | Check crawl budget, internal linking |
| **Duplicate without canonical** | Multiple URLs serve same content | Add canonical tags |
| **Page with redirect** | Google following redirect chain | Ensure redirects are 301, not 302 |

**For PureBrain's specific situation**: Legacy pages (purebrain-3, purebrain-4, pay-test) MUST be noindexed. These should appear in the "Excluded: noindex" section - if they appear in "Valid" it means Google is indexing them and competing with your real pages.

---

### 2.7 Sitemap Optimization

PureBrain uses Yoast SEO which auto-generates sitemaps. Submit these to GSC:

**Primary**: `https://purebrain.ai/sitemap_index.xml`
**Secondary (submit individually)**:
- `https://purebrain.ai/post-sitemap.xml` (blog posts)
- `https://purebrain.ai/page-sitemap.xml` (pages)

**Sitemap health checks** (Aether can automate):
- After each new blog post: confirm new URL appears in sitemap within 24 hours
- Monthly: check "Success" status in GSC > Indexing > Sitemaps

**Do NOT include in sitemaps**: test pages, noindexed pages, paginated archives beyond page 2

---

### 2.8 How GSC Feeds Content Strategy

GSC data should directly inform what to write next:

1. **Query gaps**: Queries where you appear in position 4-20 = content expansion opportunities. If you rank P8 for "AI partnership for business," write a dedicated article on that topic.

2. **Content cannibalization**: If 2 pages rank for the same query, GSC will show both appearing. Fix by consolidating or differentiating.

3. **Seasonal patterns**: Track query volume over time. AI interest has seasonal peaks (January - new year planning, October - budget season). Plan content calendar accordingly.

4. **Blog post performance**: Connect GSC (clicks per post) with GA4 (conversions per post) to identify which posts drive actual business outcomes vs just traffic.

---

### 2.9 Mobile Usability Checks

GSC > Experience > Mobile Usability. Common issues to watch for:

- **Text too small to read**: Font-size under 12px on mobile
- **Clickable elements too close**: Less than 48px between touch targets
- **Content wider than screen**: Horizontal scroll on mobile
- **Viewport not configured**: Missing viewport meta tag

For PureBrain: The homepage 3D/animation elements are the highest risk for mobile performance issues. Check this report immediately after any homepage changes.

**Official Documentation:**
- [GSC Help Center](https://support.google.com/webmasters)
- [Core Web Vitals 2026 Guide](https://developers.google.com/search/docs/appearance/core-web-vitals)
- [Yoast + GSC Integration Guide](https://yoast.com/beginners-guide-to-google-search-console/)

---

## SECTION 3: Microsoft Clarity

### Why Clarity Matters for PureBrain

GA4 tells you numbers (conversion rate, bounce rate). Clarity tells you WHY. When someone doesn't convert, Clarity shows you exactly where they clicked, what confused them, and where they gave up. For a site with complex UX decisions (3D homepage, chat interface, assessment wizard), behavioral recording is essential.

**And it's completely free. No traffic limits. No forced upgrades.**

---

### 3.1 Setup Checklist

| Step | Task | Who | Time | Priority |
|------|------|-----|------|----------|
| 1 | Create Microsoft Clarity account at clarity.microsoft.com | Jared (Microsoft account needed) | 5 min | P0 |
| 2 | Add a new project for purebrain.ai | Jared | 3 min | P0 |
| 3 | Install via WordPress plugin (search "Microsoft Clarity" in WP plugins) | Aether | 5 min | P0 |
| 4 | Verify installation via live recording view | Aether | 5 min | P0 |
| 5 | Enable Google Analytics integration in Clarity settings | Aether (needs GA4 property ID) | 10 min | P1 |
| 6 | Configure masking settings for sensitive data | Aether | 10 min | P1 |
| 7 | Set up custom tags for key pages (homepage, assessment, checkout) | Aether | 15 min | P1 |
| 8 | Create saved segments for high-intent users | Aether | 15 min | P2 |

**Total setup time**: ~1 hour. Step 1 requires Jared. Steps 3-8 Aether can handle.

---

### 3.2 What Clarity Provides That GA4 Doesn't

| Feature | What It Shows | Why It Matters for PureBrain |
|---------|--------------|------------------------------|
| **Session Recordings** | Full playback of individual user journeys | See exactly where users lose interest or get confused |
| **Click Heatmaps** | Visual overlay of where users click most | Are users clicking where you want them to? |
| **Scroll Heatmaps** | How far users scroll on each page | Is the CTA above the fold for most users? |
| **Rage Clicks** | Rapid clicks in same spot (frustration signal) | Identifies broken elements or confusing UI |
| **Dead Clicks** | Clicks that trigger no response | Reveals elements users think are clickable but aren't |
| **JavaScript Error Linking** | Links JS errors to specific session recordings | Debug issues in context |
| **AI Smart Events** | Auto-detects frustration patterns and highlights them | Surface issues you didn't know to look for |

**Key insight**: GA4 might show "80% bounce rate on assessment page." Clarity shows you the 30 sessions where people left - and you can watch them to see exactly what caused it.

---

### 3.3 Setup Best Practices for SaaS Landing Pages

**Installation**: Use the official WordPress plugin (wordpress.org/plugins/microsoft-clarity). One click, no code required.

**Privacy/Masking Configuration**:
- Clarity auto-masks text fields (passwords, credit cards) by default
- For PureBrain's chat: enable masking on chat input fields so user message content isn't recorded
- GDPR/CCPA: Clarity is compliant. Keep bot detection ON (default). If you have cookie consent, configure Clarity to wait for user consent before recording.

**Custom Tags** (set these up immediately):
Create tags that label sessions by page type so you can filter recordings:
- Tag: `homepage` for sessions that included the homepage
- Tag: `assessment` for sessions that visited the assessment
- Tag: `chat_user` for sessions that included a chat interaction
- Tag: `checkout` for sessions that reached the payment area

Tags are created in Clarity > Settings > Custom tags, then set via GTM or the Clarity API.

**Saved Segments** (create these for ongoing monitoring):
- "Rage clickers" - users who rage-clicked anywhere
- "Dead clickers" - users who clicked non-interactive elements
- "Assessment abandoners" - users who visited assessment but left before completing
- "High-scroll homepage" - users who scrolled 75%+ of homepage

---

### 3.4 Key Insights to Look For in Session Recordings

**For the Homepage (highest priority)**:
- Do users scroll past the "Discover Your AI Strategy" section?
- Where do users click first? (Should be a CTA or chat)
- Do users interact with the 3D avatar?
- What percentage of users reach the testimonials?
- Where do users abandon?

**For the Chat Interface**:
- Do users understand how to start chatting?
- What's the pattern: one message and leave vs. multi-turn conversations?
- Any rage clicks around the chat input area?
- Do users scroll down after chatting or exit?

**For the Assessment Page**:
- At which question do most users abandon?
- Are there dead clicks on the progress indicator?
- Do users scroll back up to re-read earlier questions?

**For Blog Posts**:
- How far do users read? 25%? 75%?
- Do users interact with the CTA block?
- Do users click internal links to other posts or to the homepage?

---

### 3.5 Rage Click and Dead Click Analysis

**Rage Clicks** (user frantically clicks same area - indicates frustration):
Common PureBrain scenarios to watch for:
- Clicking on the avatar expecting interaction that doesn't happen
- Clicking on testimonial photos expecting they link somewhere
- Clicking "Begin Awakening" CTA with no visible response (could indicate slow loading)
- Clicking navigation items that don't work on mobile

**Dead Clicks** (clicks that trigger nothing):
- Non-linked text that looks like a link (underlined or colored)
- Images that look like they should be clickable
- Section headers that look like buttons

**Action threshold**: If more than 5% of sessions in a page include rage clicks on the same element, that element is broken or confusing and needs immediate attention.

---

### 3.6 Scroll Depth Heatmap Interpretation

Clarity's scroll heatmaps show what percentage of users see each section.

For PureBrain's homepage, ideal reading:
- 100% of visitors should see the hero section
- 80%+ should reach the "What is PureBrain?" explanation
- 60%+ should reach the testimonials
- 40%+ should reach the pricing/CTA section

**Red flags**:
- If fewer than 40% reach testimonials, the content above is losing them too fast
- If scroll drops sharply right after the hero, the value proposition isn't landing
- If near 100% scroll rate throughout = users are searching for information (content may be unclear)

**Use with heatmaps together**: A section with high scroll (people reach it) but low clicks (people don't engage with it) = content is visible but not compelling.

---

### 3.7 Privacy Considerations

- Clarity does NOT record sensitive input fields by default
- Does not use data for Microsoft advertising or share with third parties (per Microsoft policy)
- All data is stored in Microsoft Azure, processed per GDPR/CCPA requirements
- PureBrain should add Clarity to its privacy policy's analytics tools list
- For EU visitors: configure Clarity to respect consent management platform if/when one is added

---

### 3.8 GA4 + Clarity Integration (The Power Combination)

When integrated:
- Clarity adds a direct link to session recordings from within GA4
- You can see "Watch Recording" next to GA4 user events
- Enables: "GA4 shows 20% conversion rate on assessment - let me watch the 80% who didn't convert"

**Setup**: In Clarity Settings > Google Analytics, connect your GA4 property. Then in GA4, the Clarity recordings appear in the user-level reports.

**Official Documentation:**
- [Clarity Setup Guide](https://learn.microsoft.com/en-us/clarity/setup-and-installation/clarity-setup)
- [Clarity WordPress Plugin](https://wordpress.org/plugins/microsoft-clarity/)
- [Clarity Heatmaps Documentation](https://learn.microsoft.com/en-us/clarity/heatmaps/heatmaps-overview)
- [Clarity + GA4 Integration](https://learn.microsoft.com/en-us/clarity/ga-integration/ga-integration)

---

## SECTION 4: Dashboard Setup and Review Cadence

### 4.1 The 5-Minute Daily Check

Jared's morning analytics review should cover these 5 metrics in under 5 minutes:

**Open in two browser tabs (GA4 + GSC)**:

| What to Check | Where | What You're Looking For |
|--------------|-------|------------------------|
| Sessions yesterday | GA4 > Reports > Realtime (yesterday comparison) | Major drops = something broke; major spikes = something worked |
| Conversions yesterday | GA4 > Reports > Conversions | Any conversion? If 0 days in a row = investigate |
| Top traffic source | GA4 > Acquisition > Overview | Which channel sent most traffic? Trending direction? |
| GSC clicks (7-day) | GSC > Performance > 7-day range | Growing impressions + clicks = SEO working |
| One new Clarity insight | Clarity > Dashboard > Smart events | Any rage click or dead click alerts? |

**This 5-minute habit** creates a feedback loop that catches problems within 24 hours instead of weeks.

---

### 4.2 Weekly Deep-Dive Template (15-20 minutes)

Do this every Monday morning. Creates rhythm.

**Step 1: Week-over-Week Comparison (5 min)**
- GA4: Compare last 7 days vs prior 7 days
- Key question: "Did things get better or worse?"
- Look at: Sessions, Conversions, Engagement Rate, Top Pages

**Step 2: Conversion Funnel Check (5 min)**
- GA4 Explore > Funnel: Homepage > Chat > Assessment > Payment
- Where is the biggest drop-off this week vs last week?
- If assessment abandonment spiked: check Clarity for session recordings on assessment page

**Step 3: Content Performance (5 min)**
- GA4 > Engagement > Landing Pages
- Which blog posts drove the most conversions this week?
- Are users from blog posts engaging with the assessment?

**Step 4: One Clarity Recording Session (5 min)**
- Open Clarity > Recordings
- Filter: "Assessment" tag + "Left without converting"
- Watch 3-5 recordings
- Note any patterns in what confuses or stops users

---

### 4.3 Monthly Reporting Template (30 minutes)

Do this on the 1st of each month.

**Section 1: Traffic Growth**
- Total sessions this month vs last month (%)
- Organic search sessions (are we growing from SEO?)
- Social sessions (Bluesky, LinkedIn - are they driving real traffic?)
- Email sessions (Neural Feed effectiveness)

**Section 2: Conversion Performance**
- Conversion rate: total conversions / total sessions
- Cost per lead (if running paid ads)
- Best performing source: which channel converts highest?
- Assessment completion rate: started vs finished

**Section 3: Content ROI**
- Blog posts published this month
- Blog sessions generated
- Blog-assisted conversions
- Top performing post (most traffic AND most conversions)

**Section 4: SEO Health (from GSC)**
- Total indexed pages
- Any new crawl errors
- Core Web Vitals status
- Top 10 ranking queries and their position trends

**Section 5: UX Health (from Clarity)**
- Rage click incidents this month
- Dead click incidents this month
- Average scroll depth on homepage
- One UX improvement identified and implemented

**Section 6: Next Month Priority**
- Top 3 things to improve based on this month's data
- Assign each to: Aether can do / Needs Jared decision

---

### 4.4 KPIs That Matter Most for PureBrain Right Now

PureBrain is early stage. Don't measure everything - measure what matters NOW:

**Tier 1: Business-Critical (Check Weekly)**
| KPI | Definition | Current Target |
|-----|-----------|----------------|
| **Conversion Rate** | Conversions / Sessions | Track baseline first month, then improve |
| **Assessment Completion Rate** | Completions / Starts | Target: 60%+ |
| **Chat Engagement Rate** | Sessions with chat / Total sessions | Track baseline |
| **Neural Feed Subscribers (new)** | Weekly new subscribers | Growing week-over-week |

**Tier 2: Growth Indicators (Check Monthly)**
| KPI | Definition | Target Direction |
|-----|-----------|-----------------|
| **Organic Sessions** | Sessions from Google | Growing month-over-month |
| **Brand Query Volume** | GSC impressions for "purebrain" | Growing = brand awareness building |
| **Social Sessions** | Bluesky + LinkedIn sessions | Growing as Bluesky audience grows |
| **Blog Organic Sessions** | Sessions to blog from Google | Growing as posts age and rank |

**Tier 3: Quality Indicators (Check Monthly)**
| KPI | Definition | Target |
|-----|-----------|--------|
| **Average Engagement Time** | GA4 metric (replaces session duration) | Target: 2+ minutes on key pages |
| **Core Web Vitals Pass Rate** | GSC CWV good URLs / total URLs | Target: 90%+ Good |
| **Pages per Session** | Average pages viewed per visit | Target: 2+ for non-bounce sessions |

**What to IGNORE at this stage**: MRR, churn, CAC, CLTV - these become relevant when you have recurring revenue and a customer base. Focus on traffic, engagement, and conversions first.

---

## SECTION 5: Priority Action Plan

### Priority Ranking: What to Set Up First

| Priority | Platform | Task | Estimated Time | Who |
|----------|----------|------|----------------|-----|
| **P0 - This Week** | GSC | Domain property + DNS verification | 20 min | Jared |
| **P0 - This Week** | GSC | Submit sitemap_index.xml | 5 min | Aether |
| **P0 - This Week** | GSC | Request indexing for homepage + key pages | 15 min | Aether |
| **P0 - This Week** | GSC | Noindex legacy test pages | 15 min | Aether |
| **P0 - This Week** | GA4 | Create property + data stream | 15 min | Jared |
| **P0 - This Week** | GA4 | Install tracking (Site Kit plugin) | 15 min | Aether |
| **P0 - This Week** | GA4 | Enable Enhanced Measurement | 5 min | Aether |
| **P1 - This Month** | Clarity | Create account + install plugin | 20 min | Jared creates account, Aether installs |
| **P1 - This Month** | GA4 | Configure conversion events | 30 min | Aether |
| **P1 - This Month** | GA4 | Set up custom dimensions | 20 min | Aether |
| **P1 - This Month** | GA4 | Link to Search Console | 5 min | Jared |
| **P1 - This Month** | Clarity | GA4 integration | 10 min | Aether |
| **P1 - This Month** | Clarity | Custom tags for key pages | 15 min | Aether |
| **P2 - Next Month** | GA4 | Implement custom event tracking via GTM | 2-3 hrs | Aether |
| **P2 - Next Month** | GA4 | Lead Gen report collection setup | 30 min | Aether |
| **P2 - Next Month** | Clarity | Saved segments (rage click, abandoners) | 20 min | Aether |
| **P3 - Future** | GA4 | BigQuery export + Looker Studio dashboard | 4+ hrs | Aether |
| **P3 - Future** | GA4 | Google Ads integration | 30 min | When ads start |

---

### What Requires Jared vs What Aether Handles

**Jared Must Do (requires account ownership / Google account / Microsoft account):**
- Create Google Analytics account and property
- Create Google Search Console property and verify via Cloudflare
- Create Microsoft Clarity account
- Link GA4 to Search Console (requires both accounts)
- Any Google Ads account linking

**Aether Can Handle Once Accounts Exist:**
- All WordPress plugin installations
- GA4 configuration (enhanced measurement, conversions, custom dimensions)
- GSC sitemap submission and indexing requests
- Noindexing pages via Yoast
- Clarity plugin installation and configuration
- Custom event tracking setup via GTM
- Monthly analytics reporting
- Weekly Clarity recording reviews

---

## Quick Reference: Official Documentation Links

| Platform | Resource | URL |
|----------|----------|-----|
| GA4 | Property Setup | https://support.google.com/analytics/answer/9304153 |
| GA4 | Recommended Events | https://developers.google.com/analytics/devguides/collection/ga4/reference/events |
| GA4 | Lead Gen Reports | https://support.google.com/analytics/answer/12370596 |
| GA4 | Custom Dimensions | https://support.google.com/analytics/answer/14240153 |
| GA4 | Search Console Link | https://developers.google.com/search/docs/monitor-debug/google-analytics-search-console |
| GSC | Getting Started | https://support.google.com/webmasters/answer/9128669 |
| GSC | Core Web Vitals | https://developers.google.com/search/docs/appearance/core-web-vitals |
| GSC | Yoast Integration Guide | https://yoast.com/beginners-guide-to-google-search-console/ |
| Clarity | Setup Guide | https://learn.microsoft.com/en-us/clarity/setup-and-installation/clarity-setup |
| Clarity | WordPress Plugin | https://wordpress.org/plugins/microsoft-clarity/ |
| Clarity | Heatmaps Guide | https://learn.microsoft.com/en-us/clarity/heatmaps/heatmaps-overview |
| Clarity | GA4 Integration | https://learn.microsoft.com/en-us/clarity/ga-integration/ga-integration |
| Clarity | FAQ | https://learn.microsoft.com/en-us/clarity/faq |

---

## Appendix: Total Time Investment Summary

| Platform | Initial Setup | Jared Time | Aether Time |
|----------|--------------|------------|-------------|
| Google Search Console | 1.5 hours | 20 min (verification) | 1+ hour (configuration) |
| Google Analytics 4 (basic) | 2 hours | 15 min (account creation) | 1.75 hours (configuration) |
| Google Analytics 4 (advanced events) | 3 hours | 0 min | 3 hours |
| Microsoft Clarity | 1 hour | 10 min (account creation) | 50 min (configuration) |
| **Total** | **~7.5 hours** | **~45 min** | **~6.75 hours** |

**Ongoing time investment**: 5 min/day daily check, 20 min/week deep dive, 30 min/month strategic review = ~3.5 hours/month.

---

*Report prepared by web-researcher (Aether). Ready for Jared's morning review. All recommendations grounded in 2026 best practices from GA4, GSC, and Clarity official documentation plus practitioner case studies.*
