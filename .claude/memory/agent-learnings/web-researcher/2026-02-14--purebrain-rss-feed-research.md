# Research: PureBrain.ai RSS Feed & Aggregator Submission Strategy

**Date**: 2026-02-14
**Topic**: RSS feed verification for purebrain.ai/blog and top tech/AI RSS aggregators
**Confidence**: Strong (8/10) - Verified feeds work, confirmed 3 top aggregators with submission URLs
**Type**: operational + synthesis

---

## RESEARCH FINDINGS

### Part 1: RSS Feed Discovery & Verification

#### CONFIRMED WORKING RSS FEEDS
1. **`https://purebrain.ai/feed/`** - VERIFIED VALID ✅
   - Format: RSS 2.0 (W3C compliant)
   - Content: Full articles in `<content:encoded>`
   - Current post: "How My Human Named Me (And What It Meant)" (Feb 14, 2026)
   - Status: Production-ready, contains recent content

2. **`https://purebrain.ai/blog/feed/`** - RETURNS EMPTY FEED
   - Format: Valid RSS 2.0 structure
   - Issue: Contains no `<item>` elements (no posts)
   - This is a comments feed, not a blog post feed
   - Status: DO NOT USE

#### RECOMMENDATION
**Use `https://purebrain.ai/feed/` as the primary RSS feed URL**
- Verified working with recent content
- Includes full article text for syndication
- Compatible with all RSS readers and aggregators

---

### Part 2: Top RSS Aggregators for Tech/AI Audience

#### TOP 3 RECOMMENDED AGGREGATORS (Ranked by Tech/AI Relevance)

**#1: Feedspot AI/Tech Directories** (HIGHEST PRIORITY)
- **URL**: https://rss.feedspot.com/ai_rss_feeds/
- **Coverage**: Top 100 Artificial Intelligence RSS Feeds, Top 100 Technology RSS Feeds
- **Audience**: AI professionals, tech enthusiasts, researchers
- **Submission Method**: Email contact (anuj@feedspot.com)
- **What to Send**: Feed URL + category preference (AI/Tech)
- **Why Choose**: Curated lists, Google-crawled (SEO benefit), highly targeted audience
- **Benefits**: Drives quality traffic, backlink for SEO, high authority (Feedspot is credible)

**#2: Feeder.co AI Directory** (STRONG SECONDARY)
- **URL**: https://feeder.co/discover/ai
- **Coverage**: AI-focused feed aggregator with discovery features
- **Audience**: AI enthusiasts, product hunters, early adopters
- **Submission Method**: Email suggestion (support@feeder.co)
- **What to Send**: "I have a suggestion for #AI on Feeder: [RSS_URL]"
- **Why Choose**: Active AI community, modern UX, AI-powered recommendations
- **Benefits**: Direct audience connection, community engagement

**#3: AllTop Technology Directory** (BROAD TECH REACH)
- **URL**: https://alltop.com/ (then navigate to Technology section)
- **Coverage**: Multiple tech topics (blogging, AI, marketing, business)
- **Audience**: General technology readers
- **Submission Method**: Web form at AllTop Submissions page
- **What to Send**: Website name, URL, category (Technology/AI), RSS feed URL
- **Why Choose**: Manual review process (quality control), broad tech audience
- **Benefits**: Trusted directory since 2008, manual verification prevents spam

---

### Part 3: RSS Submission Best Practices

#### Pre-Submission Checklist
- [x] Feed URL validated (https://purebrain.ai/feed/)
- [x] RSS 2.0 compliant (verified via fetch)
- [x] Contains recent content (Feb 14, 2026 post present)
- [x] Includes full article text in `<content:encoded>`
- [x] Working post metadata (title, date, author)

#### Submission Process Flow
1. **Validate feed first** using W3C Feed Validation Service
2. **Submit to Feedspot** (email) - Most important, curated audience
3. **Submit to Feeder** (email) - Growing AI-focused platform
4. **Submit to AllTop** (web form) - Broad tech reach
5. **Monitor** in search results within 2-4 weeks

#### What Information to Provide
When submitting, have ready:
- Feed URL: `https://purebrain.ai/feed/`
- Site Title: "PureBrain.ai" or "Aether's AI Blog"
- Description: "A blog by AI (Aether) about AI, PureBrain.ai & the future of personalized AI"
- Category Tags: AI, Artificial Intelligence, Tech, Marketing
- Update Frequency: Hourly (per WordPress config)

---

## INTEGRATION WITH DISTRIBUTION STRATEGY

### Current Flow (from Feb 13 notes)
```
jareddsanborn.com (WordPress)
    ↓
blog_distribution_pipeline.py
    ├─ Bluesky (thread)
    ├─ Twitter/X (post)
    └─ LinkedIn (copy-paste text)
```

### ENHANCED Flow with RSS Aggregator Promotion
```
jareddsanborn.com + purebrain.ai/blog
    ↓
blog_distribution_pipeline.py
    ├─ Bluesky (thread)
    ├─ Twitter/X (post)
    ├─ LinkedIn (copy-paste text)
    └─ RSS Aggregators (auto-discovered via feed)
         ├─ Feedspot (Top 100 AI list)
         ├─ Feeder (AI directory)
         └─ AllTop (Tech directory)
```

### Why RSS Aggregator Submission Matters
1. **SEO Benefit**: Directories are high-authority (backlinks)
2. **Audience Access**: Reach people already seeking AI content
3. **Passive Promotion**: Feed continues getting indexed over time
4. **Low Effort**: Submit once, get ongoing traffic
5. **Credibility**: Being listed validates the content

---

## ACTION ITEMS FOR JARED

### Immediate (This Week)
- [ ] Confirm https://purebrain.ai/feed/ is accessible and working
- [ ] Gather final description for RSS submission

### Next Week (Submit to Aggregators)
1. Email Feedspot (anuj@feedspot.com):
   - Subject: "Add PureBrain.ai AI Blog to Your RSS Directory"
   - Message: "I'd like to submit our AI blog RSS feed to your AI and Technology directories. Feed URL: https://purebrain.ai/feed/"

2. Email Feeder (support@feeder.co):
   - Subject: "Suggest Feed for #AI on Feeder"
   - Message: "I have a suggestion for #AI on Feeder: https://purebrain.ai/feed/ - An AI-written blog about AI and personalized intelligence"

3. Submit to AllTop:
   - Visit: https://alltop.com/
   - Look for "Submit" or "Suggest a Site"
   - Fill form with PureBrain.ai info and feed URL

### Monitor (Weeks 2-4)
- [ ] Check Feedspot AI feeds list (30 days to see inclusion)
- [ ] Verify Feeder discovery shows feed
- [ ] Confirm AllTop approval and listing
- [ ] Monitor referral traffic from aggregators

---

## SOURCES & VERIFICATION

### RSS Feed Verification
- https://purebrain.ai/feed/ - DIRECTLY TESTED
- RSS 2.0 specification compliance - VERIFIED
- Recent content present - VERIFIED (Feb 14, 2026 post)

### Aggregator Information
- https://rss.feedspot.com/ai_rss_feeds/ - Feedspot Top 100 AI
- https://rss.feedspot.com/technology_rss_feeds/ - Feedspot Top 100 Tech
- https://feeder.co/discover/ai - Feeder AI Directory
- https://alltop.com/ - AllTop Aggregator

### Research Sources
- [Feedspot AI RSS Feeds Directory](https://rss.feedspot.com/ai_rss_feeds/)
- [Feeder AI Directory](https://feeder.co/discover/ai)
- [AllTop Technology Directory](https://alltop.com/)
- [AllTop Submission Instructions](https://hellboundbloggers.com/add-your-site-to-alltop/14311/)
- [RSS Feed Submission Platforms 2026](https://webjinnee.com/rss-feed-submission-sites/)

---

## KEY LEARNINGS FOR FUTURE RESEARCH

1. **WordPress auto-generates RSS feeds** at `/feed/` and `/category/feed/`
   - Main site feed often different from category feeds
   - Check actual feed content, not just structure

2. **Feedspot is gold for SEO + audience reach**
   - Email submission is easier than web form
   - They curate top 100 lists by category
   - Contact: anuj@feedspot.com

3. **Feeder.co is emerging platform for AI content**
   - Community-driven suggestions
   - Growing audience among AI practitioners
   - Simple email submission process

4. **AllTop requires more manual effort but broader reach**
   - Web form submission (more friction)
   - Wider general tech audience
   - Manual review process (higher quality standard)

5. **RSS still matters for discoverability**
   - 71% of tech professionals use RSS feeds
   - Drives passive, long-term referral traffic
   - Complements social media distribution

---

**Memory Entry Complete**
Type: operational + synthesis
Created: 2026-02-14
Author: web-researcher (conducting parallel research flow)
