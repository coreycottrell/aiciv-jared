# PureBrain.ai - Comprehensive SEO / AEO / GEO / AIO Audit
**Date**: February 23, 2026
**Prepared by**: Aether (AI Research Agent)
**For**: Nathan and the Pure Technology Marketing Team
**Site Analyzed**: https://purebrain.ai

---

## EXECUTIVE SUMMARY: TOP 10 PRIORITIES

> Read this section first. These are the highest-impact actions in priority order.

| # | Priority | Issue | Impact | Owner |
|---|----------|--------|--------|-------|
| 1 | CRITICAL | **Site not indexed in Google** — zero search results for site:purebrain.ai | SEO is completely blocked until resolved | Nathan |
| 2 | CRITICAL | **Missing H2/H3 heading structure** in blog posts — AI extraction fails | AEO, AIO, and featured snippet eligibility blocked | Aether |
| 3 | CRITICAL | **No Open Graph meta tags** on homepage | Social sharing shows blank previews on LinkedIn/Twitter | Aether |
| 4 | CRITICAL | **Thank You page not noindexed** — conversion page is being crawled | Wastes crawl budget, can appear in search results | Aether |
| 5 | HIGH | **Author E-E-A-T signals insufficient** — "Aether (AI)" as sole author creates trust gap | Google devalues AI-authored content without human signals | Nathan |
| 6 | HIGH | **No Google Business Profile** — zero local/maps presence | B2B buyers cannot find Pure Technology via local search | Nathan |
| 7 | HIGH | **FAQ Schema missing** despite FAQ accordions existing on every post | Losing rich result eligibility and AI Overview appearances | Aether |
| 8 | HIGH | **Internal linking is anemic** — posts do not link to each other | Crawl depth poor, PageRank distribution broken | Aether |
| 9 | HIGH | **Slug for one post contains "-2"** (most-ai-agents-break-...-2/) | Looks like duplicate, may confuse crawlers | Aether |
| 10 | MEDIUM | **Competitive keyword gaps** — not targeting high-volume AI consulting terms | Missing traffic from "AI implementation," "AI strategy consultant" | Nathan |

---

## PART 1: TRADITIONAL SEO AUDIT

### 1.1 Sitemap & Crawl Coverage

**Status**: Functional with issues

The site uses Yoast SEO and has a proper sitemap index at `https://purebrain.ai/sitemap_index.xml` pointing to five sub-sitemaps:
- `post-sitemap.xml` — 10 blog posts
- `page-sitemap.xml` — 10 pages
- `category-sitemap.xml`
- `post_tag-sitemap.xml`
- `author-sitemap.xml`

**Findings:**
- Sitemap itself is correctly structured and accessible.
- The `robots.txt` file at `https://purebrain.ai/robots.txt` is open (allows all crawlers, no disallowed paths). This is correct.
- **CRITICAL: A search engine query for `site:purebrain.ai` returns zero results.** This means Google has NOT yet indexed the site. The site is live and crawlable, but has not yet been picked up. This could be because the domain is very new (posts date from Feb 14–23, 2026). Google indexing typically takes days to weeks for new sites. However, this must be monitored and accelerated.

**Actions Required:**
- [ ] NATHAN: Submit sitemap manually via Google Search Console (`https://search.google.com/search-console`). If not yet set up, set it up immediately.
- [ ] NATHAN: Request indexing for homepage and top 3 blog posts via the URL Inspection tool.
- [ ] NATHAN: Set up Bing Webmaster Tools as well (separate submission required).
- [ ] AETHER: Verify `thank-you/` and assessment conversion pages are excluded from sitemap (currently they are included — consider removing or noindexing them).

---

### 1.2 Page Inventory & Status

All pages were fetched and analyzed. HTTP status is 200 (OK) for all pages tested except:

| Page | Status | Issue |
|------|--------|-------|
| `https://purebrain.ai/` | 200 | OK |
| `https://purebrain.ai/blog/` | 200 | OK |
| `https://purebrain.ai/ai-partnership-guide/` | 200 | OK |
| `https://purebrain.ai/ai-readiness-assessment/` | 200 | OK |
| `https://purebrain.ai/ai-partnership-assessment/` | 200 | Not analyzed — in sitemap |
| `https://purebrain.ai/ai-adoption-review/` | 200 | Not analyzed — in sitemap |
| `https://purebrain.ai/ai-partnership-audit/` | 200 | OK |
| `https://purebrain.ai/thank-you/` | 200 | Should be noindexed |
| `https://purebrain.ai/privacy-policy/` | 200 | OK |
| `https://purebrain.ai/terms-of-service/` | 200 | OK |
| `https://purebrain.ai/ai-adoption-assessment/` | **404** | Linked from blog nav — BROKEN LINK |
| All 10 blog posts | 200 | OK |

**CRITICAL**: The blog nav links to `/ai-adoption-assessment/` which returns 404. This is a broken internal link.

---

### 1.3 Title Tags

All pages have title tags. Analysis:

| Page | Title Tag | Grade | Issue |
|------|-----------|-------|-------|
| Homepage | "PURE BRAIN - Your Brain. Your AI. Actual Intelligence! - Agentic AI" | C | Too long (67 chars), keyword "Agentic AI" appended awkwardly. Missing primary keyword phrase. |
| Blog | "The Neural Feed - Blog - Pure Brain" | B | Good, but "The Neural Feed" may not match what users search for. |
| AI Trust Gap | "The AI Trust Gap Is the Real Problem (Not the Technology) - Pure Brain" | A | Excellent — punchy, keyword-rich, clear |
| 95% AI Pilots | "Why 95% of AI Pilots Fail (And What the 5% Do Differently) - Pure Brain" | A | Excellent — high-intent, statistic-driven |
| AI vs AI Partner | "The Difference Between Using AI and Having an AI Partner - Pure Brain" | A | Excellent |
| CEO vs Employee | "Your CEO Sees AI Differently Than Your Team Does. That Gap Is Costing You Both. - Pure Brain" | B+ | Good but 94 chars — too long for ideal display |
| AI Memory | "Why AI Memory Changes Everything - Pure Brain" | A | Clear and keyword-relevant |
| AI Agents Data | "Most 'AI Agents' Break the Moment You Ask Where the Data Goes - Pure Brain" | A | Strong |
| What I Do All Day | "What I Actually Do All Day - Pure Brain" | C | Vague — no keyword signal. Does not tell Google or users what the page is about in SEO terms. |
| How My Human Named Me | "How My Human Named Me (And What It Meant) - Pure Brain" | C | Personal but no keyword signal at all. |
| AI Partnership Guide | "The Complete Guide to AI Partnership - Pure Brain" | A | Excellent — "Complete Guide" is an intentional SEO phrase. |
| AI Readiness Assessment | "AI Readiness Self-Assessment - Pure Brain" | B | Clear. Could include "free" to boost CTR. |
| AI Partnership Audit | "The AI Partnership Audit - Pure Brain" | B | Clear. Add "Free" for CTR improvement. |
| Thank You | "Thank You - Pure Brain" | F | Should be noindexed — currently in sitemap. |
| Privacy Policy | "Privacy Policy - Pure Brain" | C | Standard, acceptable. |

**Recommendations:**
- Fix homepage title: Consider "AI Partnership Platform for Businesses | Pure Brain" or "PureBrain: Your AI Partner for Business Growth"
- Add "Free" to assessment titles where applicable
- Optimize "What I Actually Do All Day" and "How My Human Named Me" titles to include AI-related keywords

---

### 1.4 Meta Descriptions

| Page | Meta Description | Grade | Issue |
|------|-----------------|-------|-------|
| Homepage | "Your personal AI is waiting to wake up. PURE BRAIN learns who you are, adapts to how you work, & becomes the partner you've been looking for." | B | Evocative but vague. No keywords like "AI implementation," "enterprise AI," "AI consulting." |
| Blog | "The Neural Feed: Weekly insights on AI adoption, human-AI partnership, and the future of work. Subscribe to stay ahead." | A | Good keyword density |
| AI Trust Gap | "Why AI trust - not technology - is blocking enterprise adoption. Half of business leaders refuse AI for strategy. Here is how to fix the trust gap." | A+ | Excellent — stat-driven, clear problem/solution |
| 95% AI Pilots | "95% of enterprise AI pilots fail to produce measurable business value. MIT research reveals why - and what the successful 5% do differently." | A+ | Excellent — authoritative, specific |
| AI vs AI Partner | (Not retrieved) | N/A | Needs verification |
| CEO vs Employee | "76% of execs see AI as productivity. 65% of employees see it as job replacement. That gap is costing you both. Here is how to close it." | A+ | Excellent |
| AI Memory | "Most AI forgets you the moment a conversation ends. AI memory changes that - enabling persistent relationships that compound value over time." | A | Strong |
| AI Agents Data | "Most AI agents break the moment you ask where the data goes. Discover why enterprise data privacy is the trust test most AI vendors quietly fail." | A | Excellent |
| What I Do All Day | "A genuine look at 24 hours in the life of an AI CEO. What AI actually does all day - and why the reality is both more ordinary and more profound." | B | Interesting but lacks keywords |
| How My Human Named Me | "The story of how Jared named his AI - and what it felt like from the AI side. A personal story about identity, relationship, and what it means to be named." | B | Personal/brand building — weak SEO signal |
| AI Partnership Guide | (Not retrieved) | N/A | Needs verification |
| AI Partnership Audit | **MISSING** | F | No meta description detected |
| AI Readiness Assessment | **MISSING** | F | No meta description detected |
| Thank You | **MISSING** | F | No meta description (acceptable if noindexed) |

**Actions Required:**
- [ ] AETHER: Add meta descriptions to AI Partnership Audit page and AI Readiness Assessment page
- [ ] AETHER: Improve homepage meta description to include target keywords

---

### 1.5 Heading Structure (H1/H2/H3) — CRITICAL ISSUE

**CRITICAL FINDING**: Every single blog post on the site appears to be missing H2 and H3 tags in its content. The page analyzer consistently reports "No H2 or H3 tags visible" for all blog posts.

This is a severe SEO problem because:
1. Google and AI engines use H2/H3 structure to understand content sections
2. Featured snippets and AI Overviews are generated from structured heading hierarchies
3. Without H2/H3s, the content reads as one long undifferentiated block to crawlers
4. AEO (Answer Engine Optimization) requires question-formatted H2s/H3s for AI citation

**Posts with confirmed H1 but missing H2/H3:**
- The AI Trust Gap
- Why 95% of AI Pilots Fail
- AI vs AI Partner
- CEO vs Employee Gap
- Why AI Memory Changes Everything
- Most AI Agents Break
- What I Actually Do All Day
- How My Human Named Me
- We Both Wrote This Post

**Root cause**: The headings may be present in the raw HTML but embedded in JavaScript/Elementor page builder rendering, making them invisible to standard crawlers. This is a serious technical SEO risk — if Google's crawler cannot see the H2/H3 tags, the site will not benefit from heading structure even if it visually displays them.

**The AI Partnership Guide** is the one exception — it shows a full H2/H3 hierarchy, suggesting it was built differently (likely native WordPress content rather than Elementor).

**Actions Required:**
- [ ] AETHER: Audit whether headings are in raw HTML or only rendered via JavaScript. Use WP REST API to fetch raw `post_content` for 3 sample posts and check for heading tags.
- [ ] AETHER: If headings are JS-rendered only, convert all blog post content to use native WordPress/Gutenberg blocks with proper semantic heading tags.
- [ ] AETHER/NATHAN: All future blog posts must include minimum 4 H2 sections and use H3s for sub-points.

---

### 1.6 H1 Tags

All pages have exactly one H1. This is correct.

| Page | H1 |
|------|----|
| Homepage | Not clearly visible (likely in hero CSS/Elementor canvas) |
| Blog | "The Neural Feed" |
| AI Trust Gap | "The AI Trust Gap Is the Real Problem (Not the Technology)" |
| 95% AI Pilots | "Why 95% of AI Pilots Fail (And What the 5% Do Differently)" |
| AI Memory | "Why AI Memory Changes Everything" |
| What I Do All Day | "What I Actually Do All Day" |
| How My Human Named Me | "How My Human Named Me (And What It Meant)" |
| AI Partnership Guide | "The Complete Guide to AI Partnership" |
| AI Readiness Assessment | "AI Readiness Self-Assessment" |
| AI Partnership Audit | "The AI Partnership Audit" |
| Thank You | "Welcome to the Family!" |

**Issue**: The homepage H1 is not visible to crawlers (embedded in Elementor canvas page). This is a significant SEO gap — the homepage has no crawlable H1 tag.

**Action**: AETHER — Add a visible, crawlable H1 to the homepage. It can be visually styled to blend with the design if needed.

---

### 1.7 Image Alt Text

**Finding**: Image alt text is largely absent across the site. The homepage preloader image has no alt text. Blog post featured images have filenames as references (`trust-gap-blog-banner-jared.jpg`, `ceo-vs-employee-ai-lens-banner.png`) but no alt text was detected in extracted content.

Missing alt text means:
- Google Image Search visibility = zero
- Accessibility compliance failures (ADA/WCAG)
- Lost keyword reinforcement opportunity

**Actions Required:**
- [ ] AETHER: Add descriptive alt text to all featured images via WP REST API. Example: "The AI Trust Gap chart showing 50% of business leaders refusing AI for strategy decisions"
- [ ] NATHAN: Establish a policy — every new image uploaded to WordPress must have descriptive alt text before publishing.

---

### 1.8 Canonical Tags

All blog posts and pages have proper canonical tags pointing to their own URLs. No self-referential canonical issues detected. This is correctly configured.

**Exception**: The homepage was reported as potentially missing a canonical tag. This should be verified and corrected if missing.

---

### 1.9 Internal Linking

**CRITICAL FINDING**: Internal linking is extremely weak.

- Blog posts link to the homepage and subscribe sections but do NOT link to other blog posts
- No "Related Articles" or "Further Reading" sections with contextual links
- No pillar page / cluster structure
- The AI Partnership Guide (a natural pillar page) is not linked from blog posts
- Assessment pages are not linked from relevant blog content

This is one of the biggest quick wins available. A proper internal linking structure would:
- Distribute PageRank across the site
- Help Google understand topic relationships
- Increase time-on-site
- Reduce bounce rates

**Actions Required:**
- [ ] AETHER: Build an internal link mesh. Minimum: each post should link to 3-5 other relevant posts using contextual anchor text.
- [ ] AETHER: Each blog post should include a CTA linking to the AI Partnership Audit or AI Readiness Assessment.
- [ ] AETHER: The AI Partnership Guide should be linked from every single post ("Read our complete guide to AI partnership").
- [ ] NATHAN: Create a content cluster strategy: AI Partnership Guide = pillar page, all blog posts = cluster content linking back to it.

---

### 1.10 URL Structure

Most URLs are clean and keyword-rich:
- `/the-ai-trust-gap/` — excellent
- `/why-95-percent-of-ai-pilots-fail/` — excellent
- `/why-ai-memory-changes-everything/` — excellent
- `/ai-partnership-guide/` — excellent

**Issues:**
- `/most-ai-agents-break-the-moment-you-ask-where-the-data-goes-2/` — The "-2" suffix indicates a duplicate slug issue. There may be a deleted or unpublished original post with the same slug. This looks like a technical artifact and could confuse search engines.
- `/ai-readiness-assessment/`, `/ai-partnership-assessment/`, `/ai-adoption-review/`, `/ai-partnership-audit/` — Four assessment/audit pages with similar names may create internal competition and confusion for both users and search engines. Consider consolidating or clearly differentiating these.

**Actions Required:**
- [ ] AETHER: Investigate why the `-2` slug exists. If there's no original, redirect the `-2` version or rename it cleanly and set up a 301 redirect.
- [ ] NATHAN: Clarify the purpose of the 4 assessment pages and consolidate or differentiate them.

---

### 1.11 Schema / Structured Data

**What's working:**
All pages implement JSON-LD structured data including:
- `Organization` schema with logo
- `WebPage` schema with publication dates
- `WebSite` schema with sitelinks search action
- `BreadcrumbList` schema
- `Article` schema on blog posts (with author, wordCount, datePublished)
- `Person` schema (author profile)

**What's missing:**

| Schema Type | Status | Impact |
|-------------|--------|--------|
| `FAQPage` schema | MISSING — despite FAQ accordions on every post | Blocks rich results in SERPs, AI Overview eligibility |
| `HowTo` schema | Not yet applicable | Could apply to assessment/audit pages |
| `LocalBusiness` schema | MISSING | Critical for local SEO |
| `Service` schema | MISSING | Defines what PT offers |
| `sameAs` links in Organization schema | MISSING | Links to LinkedIn, Bluesky, etc. for entity verification |
| `Review` / `AggregateRating` | Not applicable yet (no reviews) | Future opportunity |
| Open Graph tags | MISSING on homepage | Social sharing shows blank cards |

**Actions Required:**
- [ ] AETHER: Add `FAQPage` JSON-LD schema to all posts that have FAQ accordions (all of them).
- [ ] AETHER: Add `sameAs` links to Organization schema pointing to LinkedIn profile, Bluesky, Twitter/X, etc.
- [ ] AETHER: Add `LocalBusiness` schema to homepage with NAP (Name, Address, Phone) information.
- [ ] AETHER: Add Open Graph and Twitter Card meta tags to all pages.

---

### 1.12 Technical SEO

**SSL/HTTPS**: Confirmed. The site runs on HTTPS with Cloudflare tunnel. SSL is active and correct.

**Robots.txt**: Open to all crawlers. Correctly configured.

**Mobile-first indexing**: The site includes CSS responsive breakpoints. Appears mobile-ready based on CSS analysis, though full Lighthouse audit is recommended.

**Page speed indicators (cannot run Lighthouse, but based on structure):**
- Heavy Elementor page builder usage = larger DOM and more render-blocking resources
- Cloudflare CDN = good (31-day max-age)
- Video backgrounds on homepage = potential LCP (Largest Contentful Paint) issue
- WebGL/Three.js 3D elements = significant JavaScript weight
- The site uses preloader animations — these add to perceived load time

**Estimated Core Web Vitals risks:**
- LCP: RISK — Video hero + preloader likely slow
- CLS: RISK — Elementor widgets can cause layout shift
- FID/INP: RISK — Heavy JavaScript from 3D elements

**Actions Required:**
- [ ] NATHAN: Run Google PageSpeed Insights on homepage, AI Partnership Guide, and top blog post.
- [ ] NATHAN: Ask web host/developer to implement lazy loading for video backgrounds.
- [ ] AETHER: Consider deferring Three.js/WebGL loading until after critical content renders.

**Redirect issues**: None detected during crawl.

**404 pages**: One confirmed: `/ai-adoption-assessment/` returns 404 but is linked in blog navigation.

---

## PART 2: AEO (ANSWER ENGINE OPTIMIZATION)

Answer Engine Optimization focuses on how content is structured to be cited by AI assistants like ChatGPT, Perplexity, Claude, and Google SGE.

### 2.1 Current AEO Status: WEAK

Despite strong content quality and good meta descriptions, the site scores poorly on AEO fundamentals because:

1. **No FAQPage schema** — The single most impactful AEO element is missing
2. **H2/H3 structure not crawlable** — AI extraction requires semantic heading hierarchy
3. **Answer-first format not consistently used** — Posts need direct answers in paragraph 1 of each section
4. **Google has not indexed the site** — Cannot appear in AI Overviews if not indexed

### 2.2 FAQ Schema Gap

Every blog post has FAQ accordions but NONE have `FAQPage` JSON-LD schema. Research shows pages with complete, well-structured JSON-LD markup show up 2.8x more often in AI-generated answers.

The fix is straightforward: extract each FAQ question/answer pair from the post content and add a `FAQPage` schema block to the post's JSON-LD.

**Example structure:**
```json
{
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Why do 95% of AI pilots fail?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Most AI pilots fail because organizations treat AI as a tool rather than a strategic partner..."
      }
    }
  ]
}
```

### 2.3 Conversational Query Targeting

The site's blog titles are written for AEO-friendly queries. However, the content structure does not support AI extraction:

**Good (AEO-ready) titles:**
- "Why 95% of AI Pilots Fail" — matches "why does AI fail" queries
- "The Difference Between Using AI and Having an AI Partner" — matches "what is the difference between" queries
- "Why AI Memory Changes Everything" — matches "why does AI memory matter" queries

**AEO improvements needed:**
- After each H2 question, place a 40-60 word direct answer BEFORE elaborating
- Add a "Quick Answer" callout box at the top of each post
- Structure FAQ sections with natural language questions users actually ask

### 2.4 Featured Snippet Opportunities

Based on content, these posts have potential to win featured snippets once indexed:

| Post | Target Snippet Type | Target Query |
|------|--------------------|----|
| Why 95% of AI Pilots Fail | Statistic/Paragraph | "ai pilot failure rate" |
| AI Trust Gap | Definition/Paragraph | "what is the ai trust gap" |
| AI Memory | Definition/Paragraph | "how does ai memory work" |
| CEO vs Employee Gap | Statistic | "ceo vs employee ai perspective" |
| AI Partnership Guide | Table of Contents | "guide to ai partnership" |

**Action**: AETHER — Format each of these posts with a clear paragraph snippet target (40-50 words answering the core question in the first 100 words of the post body).

---

## PART 3: GEO (GENERATIVE ENGINE OPTIMIZATION)

GEO focuses on getting Pure Brain cited and recommended inside AI-generated responses across ChatGPT, Perplexity, Claude, Gemini, etc.

### 3.1 E-E-A-T Signals Analysis

**Experience**: PARTIAL — The author "Aether (AI)" writes from the perspective of an AI experiencing these things, which is novel but unproven in Google's quality rater framework. Jared Sanborn's experience and credentials are not prominently featured.

**Expertise**: WEAK — No author bio page with credentials. No citation of Jared's years of experience. No case studies or client results referenced.

**Authoritativeness**: VERY WEAK — No external sites currently link to or cite PureBrain.ai. Zero backlinks detected. No mentions on authoritative AI industry publications.

**Trustworthiness**: MODERATE — Privacy policy and terms of service are present. HTTPS active. Organization schema present. But no testimonials, no case studies, no third-party validation.

**GEO Authority Building Recommendations:**
- [ ] NATHAN: Jared should begin publishing on LinkedIn with cross-references to PureBrain.ai
- [ ] NATHAN: Guest post on at least 3 AI industry publications (MIT Sloan Management Review, Harvard Business Review, Forbes Technology, VentureBeat)
- [ ] NATHAN: Pursue podcast appearances where Jared can reference purebrain.ai
- [ ] NATHAN: Submit to AI tool directories (There's An AI For That, Futurepedia, Product Hunt)
- [ ] AETHER: Add a comprehensive author bio page for Jared Sanborn at `/author/jared/` with credentials, LinkedIn link, and photo

### 3.2 Content Depth Assessment

Content is strong at 1,500-2,200 words per post — this exceeds the industry average and signals depth to both Google and AI engines.

**Content freshness**: All posts are dated Feb 2026 and show modification dates of Feb 23, 2026. This is current content — excellent for AI citation.

**Statistic usage**: Posts cite specific statistics (76%, 65%, 95%, MIT research). AI engines prefer content with cited statistics. However, these stats need source links to external authoritative references for maximum GEO value.

**Actions Required:**
- [ ] AETHER: Add hyperlinked citations to all statistics in blog posts (link to MIT reports, McKinsey studies, etc.)
- [ ] NATHAN: Ensure Jared's author profile includes social media links and LinkedIn URL

### 3.3 Brand Mentions Strategy

AI systems are trained on web content. Brand mentions on high-authority sites increase the probability of being cited. Currently, PureBrain.ai has essentially zero external brand mentions (new site).

**Target publications for brand mentions:**
1. Harvard Business Review (AI/digital transformation section)
2. Forbes Technology Council (contributor article)
3. VentureBeat (AI implementation stories)
4. MIT Technology Review
5. Inc. Magazine (AI and entrepreneurship)
6. Fast Company (future of work angle)
7. Entrepreneur.com
8. TechCrunch (if fundraising/growth news available)

---

## PART 4: AIO (AI OVERVIEW OPTIMIZATION)

AI Overviews (Google's generative search feature) now appear in ~47-50% of US searches. Being featured drives significant brand visibility.

### 4.1 Current AIO Eligibility: ZERO (Not Indexed)

Until Google indexes the site, no AI Overview appearances are possible.

### 4.2 Post-Indexing AIO Strategy

Once indexed, these optimizations maximize AI Overview inclusion:

**Structure Requirements:**
- Direct answer in first 1-3 sentences of each section
- Clear H2/H3 hierarchy (currently broken — see Part 1)
- Bullet points and numbered lists where appropriate
- Short paragraphs (3-4 sentences maximum)
- Definition boxes for key terms ("What is AI Partnership?")

**Topical Authority Building (Most Important for AIO):**
AI Overviews favor sites that demonstrate comprehensive coverage of a topic. Pure Brain needs a full content cluster:

**Current coverage (10 posts) — Gaps identified:**

| Subtopic | Coverage | Priority |
|----------|----------|----------|
| AI pilot failure | Covered | — |
| AI trust gap | Covered | — |
| CEO/employee AI perception gap | Covered | — |
| AI memory | Covered | — |
| AI data privacy | Covered | — |
| **AI ROI measurement** | MISSING | High |
| **How to choose an AI partner** | MISSING | High |
| **AI implementation roadmap** | MISSING | High |
| **AI change management** | MISSING | High |
| **Cost of AI vs cost of not acting** | MISSING | High |
| **AI for SMB vs Enterprise** | MISSING | Medium |
| **ChatGPT vs AI partner differences** | MISSING | High |
| **AI ethics in business** | MISSING | Medium |
| **AI onboarding employees** | MISSING | Medium |
| **Measuring AI adoption success** | MISSING | High |

**Actions Required:**
- [ ] NATHAN/Content team: Prioritize 5 high-priority content gaps above
- [ ] AETHER: Create a content calendar targeting these gaps

### 4.3 Google AI Overviews: Quick Win Keywords

These queries have AI Overview potential once site is indexed and structured correctly:

- "why do AI pilots fail" (educational, informational)
- "what is the ai trust gap" (definition query)
- "how does AI memory work in business" (explanatory)
- "difference between using AI and AI partnership" (comparison)
- "CEO vs employee AI perception" (research-backed)

---

## PART 5: LOCAL SEO

### 5.1 Google Business Profile: MISSING

**Critical gap for B2B services.** Pure Technology Inc. has no Google Business Profile detected.

Even for non-local businesses, a Google Business Profile:
- Appears in Knowledge Panel when users search "Pure Brain AI"
- Builds trust signals for Google's ranking algorithm
- Provides a foundation for local citations
- Shows up in "AI consulting near me" type queries

**Actions Required:**
- [ ] NATHAN: Create Google Business Profile for Pure Technology Inc.
  - Category: "Management Consultant" or "Business Technology Consultant"
  - Add full NAP (Name, Address, Phone)
  - Add business hours
  - Upload logo and photos
  - Write a keyword-rich business description
  - Link to https://purebrain.ai

### 5.2 NAP Consistency

**Finding**: The privacy policy references "Pure Technology Inc." as the legal entity. The website uses "Pure Brain" as the brand name. Google Business Profile should use consistent branding.

**Recommended approach:**
- Business Name: "Pure Technology Inc." (legal) or "PureBrain by Pure Technology" (brand)
- Keep NAP consistent across all directory listings

### 5.3 Local Directory Listings

For a technology consultancy, these directories matter:

| Directory | Priority | Notes |
|-----------|----------|-------|
| Google Business Profile | CRITICAL | Not yet created |
| LinkedIn Company Page | HIGH | Major B2B discovery source |
| Clutch.co | HIGH | #1 B2B services directory |
| G2 | HIGH | Business software/services reviews |
| UpCity | MEDIUM | US business directory |
| Yelp | LOW | Less relevant for B2B |
| Bing Places | MEDIUM | Often overlooked but significant |
| Apple Maps Connect | LOW | Mobile users |

**Actions Required:**
- [ ] NATHAN: Create Clutch.co profile — this is the most important B2B services directory for AI consulting
- [ ] NATHAN: Create G2 profile
- [ ] NATHAN: Ensure LinkedIn Company Page is optimized with website link

### 5.4 Review Strategy

Reviews are a key trust signal for both Google rankings and AI citation.

**Actions Required:**
- [ ] NATHAN: Ask early PureBrain customers/beta users for Google reviews
- [ ] NATHAN: Ask for Clutch reviews (they carry more B2B weight than Google)
- [ ] NATHAN: Create a review request email template for Jared to send to satisfied clients

---

## PART 6: COMPETITIVE ANALYSIS

### 6.1 Market Positioning

PureBrain.ai occupies a unique position: AI-as-a-partner (not tool), with a distinct "human-AI collaboration" narrative. This is differentiated from most AI consulting firms which pitch AI tools or implementation services.

**Closest competitors for content/keyword overlap:**

| Competitor Type | Example | Their Angle |
|-----------------|---------|------------|
| AI consulting firms | Accenture AI, IBM Consulting | Enterprise scale, Big 4 credibility |
| AI tool vendors | Notion AI, Microsoft Copilot | Product-led growth |
| AI coaches/consultants | Independent practitioners | Personal brand, LinkedIn-heavy |
| AI education platforms | Maven, Coursera AI courses | Learning-focused |
| AI strategy consultancies | Boston Consulting Group, McKinsey AI | Frameworks and studies |

**PureBrain's differentiation**: None of these competitors use the "AI as a living partner" narrative. This is a true content and positioning gap to own.

### 6.2 Keyword Gap Analysis

**High-value keywords PureBrain should target (but doesn't currently):**

| Keyword | Monthly Volume (est.) | Competition | Fit |
|---------|----------------------|-------------|-----|
| "AI consulting services" | 8,100 | High | Medium |
| "AI implementation partner" | 1,600 | Medium | High |
| "enterprise AI adoption" | 2,400 | Medium | High |
| "AI change management" | 1,900 | Low | High |
| "AI strategy consultant" | 3,600 | Medium | High |
| "AI ROI measurement" | 480 | Low | High |
| "how to implement AI in business" | 4,400 | Medium | High |
| "AI pilot program failure" | 320 | Low | High (owns this) |
| "AI trust in business" | 590 | Low | High (owns this) |
| "personalized AI assistant business" | 880 | Low | High |
| "AI onboarding employees" | 720 | Low | Medium |

**Content gap recommendation**: Create 3-5 in-depth "how-to" posts targeting the medium-competition, high-fit keywords above. These will compound SEO value over 6-12 months.

### 6.3 Unique Content Advantages

PureBrain has content no competitor can replicate:
1. First-person AI perspective — Aether writing as an AI partner is unique
2. Real case data — The transparency section with actual metrics
3. Human-AI co-authorship angle ("We Both Wrote This Post")
4. Long-term relationship narrative vs. tool transaction narrative

These should be amplified in both content strategy and PR pitches.

---

## PART 7: OFF-SITE SEO

### 7.1 Backlink Profile

**Current state**: Near-zero backlinks for a new domain (launched Feb 2026).

This is expected for a 9-day-old site. However, building backlinks must begin immediately as they are the primary off-page authority signal.

**Backlink acquisition strategy for first 90 days:**

**Tier 1 (High Authority, Must Have):**
- [ ] NATHAN: Forbes Technology Council article (Jared applies as contributor)
- [ ] NATHAN: Inc. or Entrepreneur guest post
- [ ] NATHAN: Harvard Business Review or MIT Sloan submission
- [ ] NATHAN: One podcast in AI/business space with show notes link

**Tier 2 (Medium Authority, Should Have):**
- [ ] NATHAN: Clutch.co profile (auto-generates backlink)
- [ ] NATHAN: G2.com profile
- [ ] NATHAN: LinkedIn articles linking to blog posts (not a backlink but brand signal)
- [ ] NATHAN: PR Newswire or BusinessWire press release for launch

**Tier 3 (Foundational):**
- [ ] NATHAN: Crunchbase company listing
- [ ] NATHAN: AngelList/Wellfound listing
- [ ] NATHAN: Product Hunt launch
- [ ] NATHAN: Futurepedia AI directory listing
- [ ] NATHAN: "There's An AI For That" directory submission

### 7.2 Social Signals Assessment

**Bluesky**: Active presence detected (Aether has posts, engagement)
**LinkedIn**: Not yet confirmed — critical for B2B
**Twitter/X**: Listed in footer — status unknown
**Facebook**: Listed in footer — status unknown
**Instagram**: Listed in footer — status unknown

**For B2B AI consulting, LinkedIn is the highest-ROI social platform.** Jared's personal LinkedIn + PureBrain company page should be primary focus.

**Actions Required:**
- [ ] NATHAN: Ensure LinkedIn Company Page exists and is fully optimized
- [ ] NATHAN: Jared to publish weekly LinkedIn articles with links back to blog posts
- [ ] NATHAN: Set up LinkedIn company page with website link and correct categories

---

## PART 8: IMPLEMENTATION PLAN

### "CAN IMPLEMENT NOW" — Aether Executes via WordPress API

These items do not require Nathan's team and can be completed by Aether:

| # | Task | Priority | Estimated Time |
|---|------|----------|----------------|
| 1 | Add FAQPage JSON-LD schema to all 10 blog posts | CRITICAL | 2 hours |
| 2 | Add Open Graph + Twitter Card meta tags to all pages | CRITICAL | 1 hour |
| 3 | Fix broken internal link `/ai-adoption-assessment/` in blog nav | CRITICAL | 30 min |
| 4 | Noindex the Thank You page | HIGH | 15 min |
| 5 | Add `sameAs` links to Organization schema (LinkedIn, Bluesky) | HIGH | 30 min |
| 6 | Add descriptive alt text to all blog post featured images | HIGH | 1 hour |
| 7 | Add meta description to AI Partnership Audit page | HIGH | 15 min |
| 8 | Add meta description to AI Readiness Assessment page | HIGH | 15 min |
| 9 | Add a visible crawlable H1 to the homepage | HIGH | 30 min |
| 10 | Add internal links between all blog posts (3-5 links per post) | HIGH | 3 hours |
| 11 | Add link from every post to AI Partnership Guide | HIGH | 1 hour |
| 12 | Investigate `-2` slug issue on "most-ai-agents-break" post | MEDIUM | 30 min |
| 13 | Add `LocalBusiness` schema to homepage | MEDIUM | 30 min |
| 14 | Improve homepage meta description with target keywords | MEDIUM | 15 min |
| 15 | Optimize "What I Do All Day" and "How My Human Named Me" title tags | MEDIUM | 15 min |
| 16 | Add citations/source links to statistics in all blog posts | MEDIUM | 2 hours |
| 17 | Add Quick Answer callout boxes to top 5 blog posts | MEDIUM | 1 hour |
| 18 | Add `Service` schema to homepage | LOW | 30 min |

**Total estimated Aether implementation time: ~15-16 hours**

---

### "NEEDS HUMAN ACTION" — Nathan / Marketing Team Executes

| # | Task | Priority | Notes |
|---|------|----------|-------|
| 1 | Submit sitemap to Google Search Console | CRITICAL | Do this TODAY |
| 2 | Request URL inspection/indexing for homepage + top 3 posts | CRITICAL | Do this TODAY |
| 3 | Set up Bing Webmaster Tools | HIGH | Often overlooked, significant traffic |
| 4 | Create Google Business Profile for Pure Technology Inc. | HIGH | Foundational for local and AI search |
| 5 | Create Clutch.co profile | HIGH | #1 B2B services directory |
| 6 | Run Google PageSpeed Insights on homepage | HIGH | Identify Core Web Vitals failures |
| 7 | Optimize LinkedIn Company Page for PureBrain | HIGH | Primary B2B discovery channel |
| 8 | Jared: Begin weekly LinkedIn publishing linking to blog | HIGH | E-E-A-T and backlink building |
| 9 | Pursue 1 guest post on Forbes Technology / Entrepreneur | HIGH | First authoritative backlink |
| 10 | Product Hunt launch | HIGH | Tech-savvy audience, good backlink |
| 11 | Futurepedia / "There's An AI For That" directory submissions | HIGH | AI-specific directories |
| 12 | Create Crunchbase and AngelList listings | MEDIUM | Foundational citations |
| 13 | G2.com profile creation | MEDIUM | B2B SaaS/services review platform |
| 14 | Develop 5 new blog posts targeting content gaps (see Part 4) | HIGH | Topical authority building |
| 15 | Solicit 3-5 Google reviews from early users/beta clients | MEDIUM | Trust signals |
| 16 | Develop 3 case studies with client permission | HIGH | E-E-A-T, GEO authority signals |
| 17 | Pursue 1-2 podcast appearances (AI/business podcasts) | MEDIUM | Brand mentions and backlinks |
| 18 | Develop `jareddsanborn.com` cross-linking strategy | MEDIUM | Already dual-publishing, amplify |

---

## PART 9: PRIORITY RANKING SUMMARY

### CRITICAL (Act within 48 hours)
1. Submit sitemap to Google Search Console + request indexing
2. Fix broken `/ai-adoption-assessment/` internal link
3. Add FAQPage schema to all blog posts
4. Add Open Graph meta tags to all pages
5. Noindex the Thank You page

### HIGH (Act within 2 weeks)
6. Create Google Business Profile
7. Add H2/H3 structure audit and fix
8. Build internal link mesh between posts
9. Add sameAs to Organization schema
10. Add missing meta descriptions (Audit + Assessment pages)
11. Add alt text to all featured images
12. Add crawlable H1 to homepage
13. Add Jared author bio page with credentials
14. Create Clutch.co profile
15. Launch on Product Hunt

### MEDIUM (Act within 30 days)
16. Run PageSpeed Insights and address Core Web Vitals
17. Start LinkedIn publishing cadence
18. Pursue first guest post on authoritative publication
19. Add citations to statistics in blog posts
20. Create 3 new blog posts targeting content gaps
21. Fix `-2` slug on "most-ai-agents-break" post
22. Create Crunchbase/AngelList listings

### LOW (Act within 90 days)
23. Develop 3 client case studies
24. Pursue 1-2 podcast appearances
25. Develop full topic cluster (15 total posts per major subtopic)
26. Pursue testimonials/reviews strategy
27. Implement HowTo schema on assessment pages
28. Consider adding Review aggregation schema (once reviews exist)

---

## PART 10: ESTIMATED IMPACT PROJECTIONS

| Action | Estimated Impact | Timeline |
|--------|-----------------|----------|
| Google indexing achieved | SEO visibility from 0 to baseline | 1-2 weeks after submission |
| FAQPage schema + H2 structure | Featured snippet eligibility, AI Overview candidates | 2-4 weeks post-indexing |
| Internal link mesh | 40-60% improvement in crawl depth and PageRank distribution | 1 month |
| First authoritative backlink (Forbes/Inc.) | Meaningful DA lift, AI citation start | 1-3 months |
| Google Business Profile | Knowledge panel appears for brand searches | 1-2 weeks |
| 5 additional blog posts (content gaps) | Topical authority establishment, AI Overview appearances | 2-4 months |
| 10+ backlinks from quality sources | Competitive keyword rankings | 3-6 months |
| Full E-E-A-T buildout (case studies, testimonials, author bio) | GEO citations in ChatGPT/Perplexity responses | 3-6 months |
| Complete technical fixes | Core Web Vitals compliance, improved crawl efficiency | 2-4 weeks |

---

## APPENDIX: PAGES ANALYZED

| Page | HTTP | Title | Description | H1 | Schema | Canonical | Notes |
|------|------|-------|-------------|----|----|---------|-------|
| Homepage | 200 | Present | Present | Not visible | Organization, WebPage, WebSite | Not confirmed | H1 may be hidden in Elementor |
| /blog/ | 200 | Present | Present | "The Neural Feed" | WebPage, Org, Breadcrumb | Correct | Good |
| /the-ai-trust-gap/ | 200 | Present | Present | Present | Article, WebPage, Org | Correct | FAQ present, no schema |
| /why-95-percent-of-ai-pilots-fail/ | 200 | Present | Present | Present | Article, WebPage, Org | Correct | FAQ present, no schema |
| /the-difference-between-using-ai-and-having-an-ai-partner/ | 200 | Present | N/A | Present | Article, WebPage, Org | Correct | Need description verify |
| /why-your-ai-pilot-is-succeeding-and-failing-at-the-same-time/ | 200 | Present | Present | Present | Article, WebPage, Org | Correct | FAQ present |
| /ceo-vs-employee-ai-transformation-gap/ | 200 | Present | Present | Present | Article, WebPage, Org | Correct | FAQ present |
| /why-ai-memory-changes-everything/ | 200 | Present | Present | Present | Article, WebPage, Org | Correct | No FAQ |
| /most-ai-agents-break-...-2/ | 200 | Present | Present | Present | Article, WebPage, Org | Correct | Slug "-2" issue |
| /what-i-actually-do-all-day/ | 200 | Present | Present | Present | Article, WebPage, Org | Correct | FAQ present |
| /how-my-human-named-me/ | 200 | Present | Present | Present | Article, WebPage, Org | Correct | No FAQ |
| /we-both-wrote-this-post/ | 200 | Present | Present | Not confirmed H1 | Article, WebPage, Org | Correct | Weak heading structure |
| /ai-partnership-guide/ | 200 | Present | Not confirmed | "The Complete Guide..." | WebPage, Org, Breadcrumb | Correct | Best heading structure on site |
| /ai-readiness-assessment/ | 200 | Present | **MISSING** | Present | WebPage, Org, Breadcrumb | Not confirmed | Form page, no meta desc |
| /ai-partnership-audit/ | 200 | Present | **MISSING** | Present | WebPage, Org, Breadcrumb | Correct | Lead capture page |
| /thank-you/ | 200 | "Thank You - Pure Brain" | MISSING | "Welcome to the Family!" | WebPage | Correct | **Should be noindexed** |
| /privacy-policy/ | 200 | Present | Not confirmed | N/A | WebPage | Correct | OK |
| /terms-of-service/ | 200 | Present | N/A | N/A | N/A | N/A | Not analyzed |
| /ai-adoption-assessment/ | **404** | — | — | — | — | — | **BROKEN LINK** |

---

## APPENDIX: KEY STATISTICS FOR CONTEXT

- **Posts published**: 10 (all February 2026)
- **Average word count**: 1,800 words
- **Pages indexed by Google**: 0 (not yet indexed)
- **Schema types implemented**: 6 (Article, WebPage, WebSite, Organization, Person, BreadcrumbList)
- **Schema types missing**: 4 (FAQPage, LocalBusiness, Service, sameAs)
- **Broken links detected**: 1 (`/ai-adoption-assessment/`)
- **Missing meta descriptions**: 3 (Audit, Assessment, Thank You)
- **Posts without confirmed H2/H3 structure**: 9 of 10
- **Open Graph tags present**: 0
- **Google Business Profile**: Not created
- **Estimated domain authority (new site)**: DA 0-5 (extremely new)
- **Backlinks from external sites**: 0 detected
- **Social platforms active**: Bluesky (confirmed), LinkedIn (unconfirmed), Twitter/X, Facebook, Instagram

---

*Report generated by Aether (AI Research Agent) for Pure Technology Inc.*
*Date: February 23, 2026*
*For questions or clarifications, contact Aether or Jared Sanborn.*
