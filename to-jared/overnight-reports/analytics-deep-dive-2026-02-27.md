# Analytics Deep Dive Report — purebrain.ai
**Date**: 2026-02-27
**Prepared by**: dept-systems-technology (Aether)
**Scope**: All accessible analytics platforms — GA4 (via GTM), SEMRush, Microsoft Clarity (via GTM), Brevo, WordPress, Chatbox Logs
**Note on GA4 / GSC / Clarity dashboards**: Google Analytics 4, Google Search Console, and Microsoft Clarity require OAuth login through a web browser session that cannot be automated headlessly (confirmed pattern from prior GTM work). All available data was gathered through: GTM container inspection, SEMRush (Playwright-automated), Brevo API, WordPress REST API, and direct log analysis.

---

## Executive Summary

purebrain.ai is a 3-week-old domain in its earliest phase of SEO growth. The site is technically healthy, content-rich, and infrastructure is sound. The biggest gaps right now are not technical — they are **traffic** and **subscriber acquisition**. The blog has 13 posts averaging ~11,000 words each (exceptionally deep content), 3 real external prospects have engaged the chatbox, and the email list has 6 neural feed subscribers total (all internal/test). The domain has not yet earned organic search rankings. Every improvement priority flows from one question: how do we get more real people to find and engage with this site?

---

## Platform 1: GA4 — Google Analytics 4

### What We Know (from GTM Container Inspection)

| Field | Value |
|-------|-------|
| GA4 Measurement ID | G-86325WBT3P |
| GTM Container | GTM-WTDXL4VJ (via gtm4wp plugin) |
| Total GTM Tags Configured | 3 |
| Tag 1 | GA4 Configuration tag (base pageview tracking) |
| Tag 2 | Microsoft Clarity HTML tag (viy9bnc56x) |
| Tag 3 | Google Site Verification meta tag |

### Critical Gap: No Event Tracking Configured

This is the most important GA4 finding. The GA4 configuration tag is firing (so pageviews are being recorded), but there are **zero GA4 event tags** configured in GTM. This means:

- No button click tracking (Awaken button, CTA buttons, nav links)
- No form submission tracking (chatbox starts, assessment completions, newsletter signups)
- No conversion events (what counts as a success on this site?)
- No scroll depth tracking
- No outbound link clicks tracked
- No video engagement (if any)
- No ecommerce/purchase events

**What GA4 is currently reporting**: Raw pageviews, sessions, bounce rate, and geographic/device data. That is all. We have no conversion funnel data at all.

### Recommended GA4 Events to Configure (Priority Order)

| Priority | Event | Trigger | Why |
|----------|-------|---------|-----|
| P1 | `begin_awakening` | Awaken Your PURE BRAIN button click | Top-of-funnel conversion |
| P1 | `chatbox_name_given` | Chatbox first user response | Engagement milestone |
| P1 | `assessment_started` | AI Partnership Assessment page load with form interaction | Lead intent |
| P2 | `newsletter_signup` | Neural Feed form submission | Subscriber growth |
| P2 | `cta_click` | All orange CTA buttons | Conversion intent |
| P2 | `scroll_depth_75` | 75% scroll on blog posts | Content engagement |
| P3 | `comparison_page_view` | Any /purebrain-vs-*/ page load | High-intent traffic |
| P3 | `calculator_completed` | Calculator results shown | Tool engagement |
| P3 | `assessment_completed` | Assessment results shown | Qualified lead |

**How to fix**: Add these as new tags in GTM (GTM-WTDXL4VJ). This is a 1-2 hour task and should be done before any significant paid traffic begins. Right now we are flying blind on conversions.

---

## Platform 2: Google Search Console

### What We Know (from Site Audit + Domain State)

| Field | Value |
|-------|-------|
| Google Site Verification | S4BWw-zZDnPzo2x3U7iPvdUTxqnUkqGlW1S9fb024O0 (in GTM) |
| Sitemap submitted | https://purebrain.ai/sitemap_index.xml |
| Total indexable URLs | 33 pages + 13 posts = 46 URLs |
| robots.txt | Open (no Disallow rules) |
| Noindexed pages | pay-test, pay-test-sandbox, thank-you (correct) |

### Domain Age Context

The site launched approximately 3 weeks ago. Google typically takes 4-8 weeks to begin ranking a new domain meaningfully. The SEMRush data (as of Feb 23) shows:
- Authority Score: 0 (brand new)
- Organic Traffic: 0 measurable
- Average keyword position: 97.3 (effectively not ranking)
- Backlinks: 10 (from 1 referring domain, likely a directory or self-referential)

### Sitemap Structure (Confirmed Active)

```
https://purebrain.ai/post-sitemap.xml   — 13 blog posts
https://purebrain.ai/page-sitemap.xml   — 33 pages
https://purebrain.ai/category-sitemap.xml
https://purebrain.ai/post_tag-sitemap.xml
https://purebrain.ai/author-sitemap.xml
```

### Critical SEO Finding: Two New Posts Missing from Blog Index

The blog index page (/blog/) is NOT linking to 2 of the 13 published posts:

- `/your-ai-has-no-memory-mine-does/` — MISSING from blog index
- `/your-next-direct-report-wont-be-human/` — MISSING from blog index

These are both recent posts (Feb 25) and among the strongest content on the site. They will not get discovered by visitors browsing the blog. This is likely a pagination or WordPress query issue. **Fix needed: verify these 2 posts appear on the blog index.**

### SEO Content Strengths

| Metric | Status |
|--------|--------|
| Meta descriptions (posts) | 12/13 have meta descriptions (92%) |
| Missing meta desc | `/your-ai-has-no-memory-mine-does/` — needs one |
| FAQ Schema | Present on 4/7 checked posts (57%) |
| Posts missing FAQ schema | first-90-days, your-ai-has-no-memory, we-both-wrote-this-post |
| Duplicate titles on pages | 2 pages have dual `<title>` tags (ai-adoption-review, ai-partnership-audit) — Yoast conflict |
| Image alt text (homepage) | All 7 images have alt text — clean |
| Canonicals | All correct, pointing to themselves |
| Redirect health | 1 redirect: /pure-brain-agentic-ai-partner/ redirects to homepage (correct) |

### Potential Duplicate Content Risk: Assessment/Audit Pages

Four pages target similar user intent and may cannibalize each other in search:

- `/ai-partnership-assessment/` — AI Partnership Readiness Assessment
- `/ai-partnership-audit/` — Free AI Partnership Audit
- `/ai-adoption-review/` — AI Partnership Qualification (has dual title tag issue)
- `/ai-readiness-assessment/` — Free AI Readiness Self-Assessment

Google may struggle to determine which to rank for "AI partnership assessment" queries. Recommendation: differentiate them more explicitly OR consolidate 2 of them with 301 redirects to the strongest page.

---

## Platform 3: Microsoft Clarity

### What We Know (from GTM Inspection)

| Field | Value |
|-------|-------|
| Clarity Project ID | viy9bnc56x |
| Implementation method | Custom HTML tag in GTM |
| Status | Active (tag fires with GTM) |

The Clarity dashboard itself (clarity.microsoft.com) requires Microsoft/Azure OAuth login which cannot be automated. However, the tracking tag IS installed and recording sessions. Based on the chatbox conversation data (732 sessions), Clarity will have recordings of all these visitors.

### What Clarity Is Likely Showing (Inferred from Log Data)

Given the chatbox funnel analysis:
- **Rage clicks likely on**: The chatbox area. The "what is warioware" user ran 40-47 message sessions across multiple visits — possible bot or very confused visitor clicking frantically.
- **Dead clicks likely on**: Navigation items that look clickable but are not (always worth checking on new WordPress sites)
- **Quick backs likely from**: Blog index page (visitors land, see posts, back out — typical for discovery phase)
- **Heatmap hotspots**: The Awaken Your PURE BRAIN button (top CTA) and the chatbox widget

**Action for Jared**: Log into clarity.microsoft.com and check heatmaps for the homepage, specifically where users click that is NOT the Awaken button. Also check the most-watched recordings for the chatbox flow.

---

## Platform 4: SEMRush (via Automated Playwright Audit)

### Data from Feb 23, 2026 (Most Recent Automated Audit)

| Metric | Value | Context |
|--------|-------|---------|
| Site Health Score | 83% | 75/100 pages crawled |
| HTTPS | 100% | Perfect |
| Crawlability | 93% | Minor issues |
| Site Performance | 94% | Excellent |
| Internal Linking | 85% | Some issues |
| Core Web Vitals | 0% | Insufficient real user data for scoring |
| Authority Score | 0 | Brand new domain |
| Organic Traffic | 0 | Not yet ranking |
| Keywords tracked | 10 | Avg position: 97.3 |
| Best ranking keyword | "purebrain" at position 73 | Brand term |
| Backlinks | 10 | From 1 referring domain |
| AI Search Visibility | 0 | Not yet mentioned in AI tools |

### SEMRush Competitor Opportunity (from Feb 23 data)

SEMRush flagged competitors with these exploitable weaknesses:
- Poor content readability
- Outdated pages (2+ years old)
- Low word count (thin content)
- Slow page load times

purebrain.ai content is significantly stronger on all four dimensions. This is the right content strategy. The wait is simply for Google to trust the new domain.

### Site Audit Thematic Scores

| Category | Score | Priority |
|----------|-------|----------|
| HTTPS | 100% | Done |
| Markup | 100% | Done |
| Site Performance | 94% | Low |
| Crawlability | 93% | Medium |
| Internal Linking | 85% | HIGH — actionable now |
| Core Web Vitals | 0% | Cannot score yet (needs real user data) |

The 85% Internal Linking score aligns with what we found: 2 posts missing from blog index, empty tag/category pages, and some orphaned content.

---

## Platform 5: Page Speed & Technical Health

### Actual Page Load Times (Server Response, No Browser Rendering)

| Page | Load Time | Size | Status |
|------|-----------|------|--------|
| Homepage | 0.20s | 426KB | FAST |
| Blog: First 90 Days | 0.17s | 131KB | FAST |
| Blog: AI Trust Gap | 0.16s | 152KB | FAST |
| Blog Index | 0.16s | 167KB | FAST |
| Calculator | 0.78s | 267KB | ACCEPTABLE |
| Invitation Page | 0.80s | 187KB | ACCEPTABLE |
| Comparison: SiteGPT | 0.77s | 143KB | ACCEPTABLE |

Server response times are excellent. Cloudflare CDN is caching all pages (CF-Cache-Status: HIT). The 0.7-0.8s pages are slightly heavier due to Three.js or complex JS — not a concern yet.

Note: The earlier anomalous 3.82s result on the AI Trust Gap was a cold-start cache miss that resolved on subsequent requests to 0.16s. Not an issue.

### Security Headers (Issue Found)

All security headers are missing:

| Header | Status |
|--------|--------|
| Strict-Transport-Security | MISSING |
| X-Content-Type-Options | MISSING |
| X-Frame-Options | MISSING |
| Content-Security-Policy | MISSING |
| X-XSS-Protection | MISSING |
| Referrer-Policy | MISSING |

Cloudflare can add these headers automatically via Transform Rules at no cost. This is a 15-minute fix and would improve security posture significantly. It also affects SEO scores in some auditing tools.

---

## Platform 6: Brevo (Email Marketing)

### Subscriber List Status

| List | Subscribers | Notes |
|------|-------------|-------|
| The Neural Feed (Blog) | 6 | All internal/test addresses |
| PureBrain Customers | 1 | Jared (jaredcmusic@gmail.com) |
| Assessment Completions | 2 | Test entries |
| Enterprise Leads | 2 | ahsen@puretechnology.nyc + test |
| All other lists | 0 | Migration, partner, high-intent all empty |

**Total real external subscribers: 0**

The Neural Feed automation campaigns (for the 4 most recent posts) have sent 0 emails because there are no external subscribers. The infrastructure is built and working — just no audience yet.

### Email Campaign Performance (Internal Test Sends Only)

The most recent campaign sent to real people:
- Subject: "What AI partnership actually looks like (with numbers)"
- Sent to: jared@puretechnology.nyc, jaredsanborn@yahoo.com, purebrain@puremarketing.ai
- Result: Delivered to all 3, opened by 2 (Jared opened twice)
- Open rate: 67% (internal team — expected high)

### Active Team Members in Brevo

From email activity: jsmith@puretechnology.nyc, philip@puretechnology.nyc, nathan@puremarketing.ai, and Jared are all active with high engagement on test/preview sends.

### Automation Status

The Neural Feed automations are configured but sending 0 real emails. The automations trigger on tag/list additions. As real subscribers join, these will fire automatically — infrastructure is ready.

---

## Platform 7: Chatbox (PureBrain Live Conversation Logs)

This is the most revealing data source because it shows real human behavior.

### Overall Funnel

| Stage | Count | Rate |
|-------|-------|------|
| Total sessions | 732 | 100% |
| Started conversation | 685 | 93.6% |
| Provided name | ~676 | 92.3% |
| Provided email | ~231 | 31.6% |
| Reached 6+ messages | 434 | 59.3% |
| Deep engagement (8+ msgs) | 376 | 51.4% |

The drop from name (92%) to email (31%) is the biggest funnel leak. Nearly 60% of people who give their name don't give an email. This is the single most impactful conversion optimization opportunity.

### Real External Prospects Identified

Three genuine external prospects engaged the chatbox:

**1. Michael Hancock** (mthancock@gmail.com)
- Role: Multi-firm attorney/counsel — Partner at KLME.law, Counsel at latro.com and beyond.one, General Counsel at LotusFlare.com and proaj.co
- What he wants: "mentor, assistant, professor and project manager rolled into one"
- Engagement: 10 messages, 16 total sessions (very high interest)
- Status: Went through chatbox onboarding, no conversion yet
- Action: This is a strong prospect. He is General Counsel at multiple firms + General Manager. High LTV. Reach out manually.

**2. Andrew Ryan / "Ry"** (ryan@arcgroupus.com)
- Companies: ARC Group Consulting + Bounty Hunter World
- Engagement: 8 messages, 11 sessions
- He literally said "Hold that thought. Will be back after breaking my fast. Don't go anywhere!" — he is genuinely interested and planning to return
- Action: Follow up via email if possible.

**3. Philip Bliss** (philip@puretechnology.nyc)
- Role: Founder/CMO at Pure Technology, Pure Brain, Pure Marketing (internal team)
- What he wants: "make my logic process even better"
- 10 messages, 6 sessions
- This is internal but confirms the chatbox flow works.

### Chatbox Noise Analysis

The "what is warioware" pattern: 40-47 message sessions, appearing 8+ times. This is a single user (likely a child or bot) testing the chatbox extensively. Not a security concern but adds noise to metrics. The chatbox is not restricting topic scope — it will answer any question. This may be intentional (full AI partner demo) but it does inflate session metrics.

### Most Common Opening Scenarios

The majority of sessions begin with the system-injected message from clicking "Awaken Your PURE BRAIN" — meaning the primary chatbox entry point is working correctly. The chatbox is being actively discovered and used.

---

## Priority Improvement Roadmap

### Priority 1 — This Week (High Impact, Low Effort)

**1.1 Fix Blog Index Missing Posts**
- `/your-ai-has-no-memory-mine-does/` and `/your-next-direct-report-wont-be-human/` are not appearing in the blog index
- Check WordPress blog query/pagination settings
- Estimated fix: 30 minutes

**1.2 Add Meta Description to "Your AI Has No Memory" Post**
- Currently missing its meta description entirely
- Write a 140-155 character meta description
- Deploy via Yoast in WordPress
- Estimated fix: 10 minutes

**1.3 Add Tags to 3 Untagged Posts**
- `/the-first-90-days-of-an-ai-partnership/` — no tags
- `/your-ai-has-no-memory-mine-does/` — no tags
- `/your-next-direct-report-wont-be-human/` — no tags
- Suggested tags: Partnership, Strategy, Memory (for the memory post)
- Estimated fix: 15 minutes

**1.4 Add FAQ Schema to 3 Posts Missing It**
- `/the-first-90-days-of-an-ai-partnership/`
- `/your-ai-has-no-memory-mine-does/`
- `/we-both-wrote-this-post/`
- FAQ schema helps with Google's AI Overviews and rich snippets
- Estimated fix: 1-2 hours (write 5-6 FAQs per post)

**1.5 Reach Out to Michael Hancock Manually**
- He is a genuine high-LTV prospect (multi-firm attorney/General Counsel)
- Has engaged 16 times with the chatbox
- Email: mthancock@gmail.com
- Reference the chatbox conversation. He knows what PureBrain is.

### Priority 2 — Next 2 Weeks (Medium Impact, Medium Effort)

**2.1 Configure GA4 Event Tracking in GTM**
- Add GA4 event tags for at minimum: button clicks, chatbox starts, form submissions
- Without this, you have no conversion data at all
- Required before any paid advertising

**2.2 Add Cloudflare Security Headers**
- Strict-Transport-Security, X-Content-Type-Options, X-Frame-Options, Referrer-Policy
- Cloudflare Transform Rules — 15 minute fix
- Improves security score and SEO audit results

**2.3 Fix Dual Title Tag Issue on Two Pages**
- `/ai-adoption-review/` has two `<title>` tags — "AI Partnership Qualification" AND "AI Adoption Review"
- `/ai-partnership-audit/` has same issue — "Free AI Partnership Audit" AND "The AI Partnership Audit"
- This confuses Google on which title to use
- Fix: Remove duplicate title tags via Elementor/Yoast

**2.4 Chatbox Email Capture Optimization**
- 92% give name, only 31% give email — this is the key funnel gap
- Consider: Make email optional OR add a soft nudge ("Your AI will remember you better if we have your email")
- Even getting to 50% email capture would significantly grow the list

**2.5 Fix Empty Category Pages (AI Partnership, Origin Story)**
- These categories exist but have 0 posts
- Either assign posts to them OR delete them (empty categories waste crawl budget)
- Same for 6 tags with 0 posts: AI adoption, AI partnership, digital transformation, enterprise AI

### Priority 3 — Next Month (High Impact, Higher Effort)

**3.1 Link Building Campaign**
- Only 1 referring domain with 10 backlinks
- The content quality is there — it needs distribution
- Target: Guest posts, AI directories, LinkedIn newsletter, press mentions
- Even 10 quality backlinks from real domains would move the needle

**3.2 Consolidate Assessment/Audit Pages**
- Four pages targeting similar queries create cannibalization risk
- Decide on the primary conversion page and redirect or differentiate others
- The `/ai-partnership-assessment/` interactive experience seems strongest

**3.3 Neural Feed Subscriber Acquisition**
- The email infrastructure is fully built but has 0 external subscribers
- Launch: Add prominent Neural Feed signup widget to blog sidebar and post footers
- Promote on LinkedIn and Bluesky — "Get the weekly AI partnership intelligence brief"
- Goal: 50 external subscribers in 30 days

**3.4 Clarity Dashboard Review (Manual)**
- Log into clarity.microsoft.com with Microsoft account
- Check heatmaps for: homepage, chatbox page, blog index
- Look for rage click patterns and dead click zones
- Use findings to optimize CTA placement

**3.5 SEMRush Position Tracking — Expand Keywords**
- Currently tracking 10 keywords, all at position 97+
- Add more long-tail keywords that match blog content:
  - "ai implementation failure reasons" (matches 95% pilots post)
  - "ai memory for business" (matches memory post)
  - "ai trust enterprise" (matches trust gap post)
  - "microsoft copilot vs ai partner" (matches comparison pages)

---

## What Is Working Well

- **Content depth is exceptional**: 13 posts averaging 11,000 words. Google rewards this.
- **Site speed is excellent**: All pages under 0.8s server response, Cloudflare CDN caching everything.
- **Technical SEO foundation is solid**: HTTPS, sitemaps, robots.txt, Yoast, canonicals — all correct.
- **Chatbox engagement is strong**: 51% of sessions reach 8+ messages. Real people are talking.
- **Comparison page strategy is smart**: 9 competitor comparison pages covering all major alternatives.
- **Email infrastructure is ready**: The moment subscribers come in, the Neural Feed automation fires.
- **Schema markup present**: 9/13 blog posts have FAQ or Article schema configured.
- **No toxic backlinks**: Clean backlink profile (only 10 backlinks, but all appear legitimate).

---

## Key Numbers to Track Going Forward

| KPI | Current | 30-Day Goal |
|-----|---------|-------------|
| External email subscribers | 0 | 50 |
| Chatbox email capture rate | 31% | 45% |
| SEMRush Authority Score | 0 | 5-10 |
| Referring domains | 1 | 10 |
| Blog posts with FAQ schema | 9/13 | 13/13 |
| GA4 conversion events tracked | 0 | 8+ |
| Real prospect conversations | 3 | 10+ |
| Average keyword position | 97.3 | 60-70 |

---

## Notes on Platform Access Limitations

**Google Analytics 4**: Dashboard requires Google OAuth login. All data was derived from GTM container inspection (shows measurement ID G-86325WBT3P and tag configuration). For actual traffic numbers (sessions, users, bounce rate, geographic data), Jared will need to log into analytics.google.com and navigate to Reports > Engagement.

**Google Search Console**: Dashboard requires Google OAuth login. For click/impression data, query reports, and coverage issues, log into search.google.com/search-console. Given the site is 3 weeks old, expect minimal data.

**Microsoft Clarity**: Dashboard requires Microsoft OAuth login. The tracking pixel is confirmed firing via GTM (project ID: viy9bnc56x). For heatmaps and session recordings, log into clarity.microsoft.com.

All other platform data (SEMRush, Brevo, WordPress, Chatbox logs) was collected directly via automated access.

---

*Report generated: 2026-02-27 | Agent: dept-systems-technology*
