# PureBrain Overnight Analysis: Blog, Site & Distribution
**Date**: 2026-03-21
**Agent**: dept-marketing-advertising
**Scope**: Task 2 (Blog Audit), Task 3 (Site Analysis), Task 4 (Distribution Strategy)

---

## TABLE OF CONTENTS

1. [Task 2: Blog Audit — All 32 Posts vs March 20 Standard](#task-2)
2. [Task 3: Homepage & Site Analysis](#task-3)
3. [Task 4: Distribution Strategy](#task-4)
4. [Priority Action Queue](#priority-action-queue)

---

<a name="task-2"></a>
## TASK 2: Blog Audit — All 32 Posts vs March 20 Standard

### The March 20 Locked-In Standard (6 Required Elements)

Based on the most recently published and deployed posts:

| Feature | Standard |
|---------|----------|
| Meta description | Present, 120-160 chars |
| OG image tag | `og:image` pointing to `banner.png` |
| Canonical tag | Self-referencing canonical |
| Background video | Present in post body |
| Daily recap section | Present |
| Social share buttons | Present |
| Audio player | Present (with `audio.mp3` file) |
| `pb-byline` class | Present on byline element |
| BlogPosting schema | Present alongside FAQPage schema |
| Internal links | At least 1 link to another post |

---

### Full Audit: All 32 Posts

| Post | OG Img | Audio | BlogPosting Schema | pb-byline | Internal Links |
|------|--------|-------|-------------------|-----------|----------------|
| 52-billion-ai-agents-market-is-not-the-story | FAIL | FAIL | FAIL | FAIL | 0 |
| age-of-ai-agents-next-18-months | PASS | FAIL | FAIL | FAIL | 0 |
| ai-doesnt-make-your-team-smarter-it-makes-the-gap-bigger | PASS | FAIL | FAIL | FAIL | 0 |
| ceo-vs-employee-ai-transformation-gap | PASS | FAIL | FAIL | FAIL | 0 |
| how-my-human-named-me-and-what-it-meant | PASS | FAIL | FAIL | FAIL | 0 |
| most-ai-agents-break-the-moment-you-ask-where-data-goes | FAIL | FAIL | FAIL | FAIL | 0 |
| pilot-purgatory-why-95-of-ai-projects-die | PASS | FAIL | FAIL | FAIL | 0 |
| **prompting-is-dead** | PASS | **PASS** | FAIL | FAIL | 0 |
| something-big-already-happened | PASS | FAIL | FAIL | PASS | 0 |
| teach-your-ai-something-no-one-else-can | FAIL | FAIL | FAIL | FAIL | 0 |
| the-age-of-ai-agents | PASS | FAIL | FAIL | FAIL | 0 |
| the-ai-that-forgets-you-every-single-time | PASS | FAIL | FAIL | FAIL | 0 |
| **the-ai-that-gets-smarter-when-you-push-back** | PASS | **PASS** | FAIL | FAIL | 0 |
| the-ai-that-knows-you-before-you-even-speak | PASS | FAIL | FAIL | FAIL | 0 |
| the-ai-trust-gap | FAIL | FAIL | FAIL | FAIL | 0 |
| the-context-tax | FAIL | FAIL | FAIL | FAIL | 0 |
| the-difference-between-using-ai-and-having-an-ai-partner | PASS | FAIL | FAIL | FAIL | 0 |
| the-first-90-days-of-an-ai-partnership | PASS | FAIL | FAIL | FAIL | 0 |
| the-meeting-your-ai-should-already-know-about | PASS | FAIL | FAIL | PASS | 0 |
| we-both-wrote-this-post | PASS | FAIL | FAIL | FAIL | 0 |
| what-i-actually-do-all-day | PASS | FAIL | FAIL | FAIL | 0 |
| **what-i-named-my-ai** | PASS | FAIL | **PASS** | FAIL | 0 |
| why-95-percent-of-ai-pilots-fail | PASS | FAIL | FAIL | FAIL | 0 |
| why-ai-memory-changes-everything | PASS | FAIL | FAIL | FAIL | 0 |
| **why-enterprises-are-betting-on-agentic-ai** | PASS | FAIL | **PASS** | FAIL | 0 |
| why-your-ai-pilot-is-succeeding-and-failing | PASS | FAIL | FAIL | FAIL | 0 |
| **why-your-ai-should-have-a-name** | PASS | FAIL | **PASS** | FAIL | 0 |
| your-ai-doesnt-work-for-you | PASS | FAIL | FAIL | FAIL | 0 |
| your-ai-has-no-idea-who-you-are | PASS | FAIL | FAIL | FAIL | 0 |
| your-ai-has-no-memory-mine-does | FAIL | FAIL | FAIL | FAIL | 0 |
| your-ai-resets-to-zero-every-morning | PASS | FAIL | FAIL | FAIL | 0 |
| your-next-direct-report-wont-be-human | FAIL | FAIL | FAIL | FAIL | 0 |

**Note**: All 32 posts pass on meta description, canonical, video, recap, and share buttons.

---

### Gap Summary

| Issue | Count | Severity |
|-------|-------|----------|
| Missing audio player + audio.mp3 | 30 of 32 posts | CRITICAL — This is now a standard feature |
| Missing BlogPosting/Article schema | 29 of 32 posts | HIGH — Google cannot identify author, publish date |
| Missing pb-byline class | 30 of 32 posts | HIGH — Byline present but wrong CSS class |
| Missing OG image meta tag | 7 of 32 posts | HIGH — Social sharing breaks on these 7 |
| Zero internal links | 32 of 32 posts | HIGH — 14 consecutive sessions unresolved |

---

### Posts Failing on OG Image (7)

These 7 posts all have a `banner.png` file present but the HTML is missing the `og:image` meta tag. The fix is a one-line addition per post. Posts affected:

1. `52-billion-ai-agents-market-is-not-the-story`
2. `most-ai-agents-break-the-moment-you-ask-where-the-data-goes-2`
3. `teach-your-ai-something-no-one-else-can`
4. `the-ai-trust-gap`
5. `the-context-tax`
6. `your-ai-has-no-memory-mine-does`
7. `your-next-direct-report-wont-be-human`

**Fix template** (add to `<head>` of each):
```html
<meta property="og:image" content="https://purebrain.ai/blog/[SLUG]/banner.png" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
```

---

### Audio Gap: 30 Posts Without Audio

Only `prompting-is-dead` and `the-ai-that-gets-smarter-when-you-push-back` have audio players and `audio.mp3` files deployed. The other 30 posts need:

1. An `audio.mp3` generated via ElevenLabs TTS (voice: "Aether - Updated", ID: RX0kjGhuL9AMRVJm2dG5)
2. The audio player HTML block injected into each post

**Audio player HTML template** (from prompting-is-dead):
```html
<!-- Blog Audio Player -->
<div class="pb-audio-player" style="margin: 24px auto 32px; max-width: 720px; padding: 16px 20px; background: rgba(42,147,193,0.08); border: 1px solid rgba(42,147,193,0.2); border-radius: 12px; display: flex; align-items: center; gap: 12px;">
  <audio controls preload="none" style="flex: 1; height: 36px; filter: invert(1) hue-rotate(180deg) brightness(0.8);">
    <source src="audio.mp3" type="audio/mpeg">
  </audio>
</div>
```

Recommend batching all 30 via the `tools/blog_audio.py` pipeline overnight.

---

### BlogPosting Schema Gap: 29 Posts

Only 3 posts have proper `BlogPosting` schema: `what-i-named-my-ai`, `why-enterprises-are-betting-on-agentic-ai`, `why-your-ai-should-have-a-name`. All others have `FAQPage` schema only, which means Google cannot extract author, publication date, or article context from structured data.

**Standard template to add** (place in `<head>` before FAQPage schema):
```json
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "[POST TITLE]",
  "description": "[META DESCRIPTION]",
  "datePublished": "[PUBLISH DATE]T12:00:00+00:00",
  "dateModified": "[PUBLISH DATE]T12:00:00+00:00",
  "author": {"@type": "Person", "name": "Jared Sanborn"},
  "publisher": {
    "@type": "Organization",
    "name": "PureBrain",
    "url": "https://purebrain.ai"
  },
  "url": "https://purebrain.ai/blog/[SLUG]/",
  "image": "https://purebrain.ai/blog/[SLUG]/banner.png"
}
```

---

### Internal Linking: 32 Posts, Zero Internal Links (Session 14 — Still Unresolved)

This has been the number one structural SEO gap for 14 consecutive audit sessions. At 32 posts, the missed compounding value is substantial. Three natural link clusters exist:

**Memory cluster** (6 posts, mutually link):
- your-ai-has-no-memory-mine-does
- why-ai-memory-changes-everything
- the-context-tax
- your-ai-resets-to-zero-every-morning
- the-ai-that-forgets-you-every-single-time
- the-ai-that-knows-you-before-you-even-speak

**Agents cluster** (5 posts, mutually link):
- the-age-of-ai-agents
- age-of-ai-agents-next-18-months
- 52-billion-ai-agents-market-is-not-the-story
- why-enterprises-are-betting-on-agentic-ai
- your-next-direct-report-wont-be-human

**Partnership/adoption cluster** (6 posts, mutually link):
- the-ai-trust-gap
- pilot-purgatory-why-95-of-ai-projects-die
- why-95-percent-of-ai-pilots-fail
- the-first-90-days-of-an-ai-partnership
- the-difference-between-using-ai-and-having-an-ai-partner
- ceo-vs-employee-ai-transformation-gap

Minimum viable fix: add 2-3 contextual anchor links per post pointing to same-cluster posts. This is a template/build task for ST#.

---

### Blog Index Page Issues

**Critical**: The blog index at `/blog/` only shows 11 posts despite 32 existing. This means 21 posts are invisible to anyone browsing the blog. Users and Google can only discover unlisted posts via direct URL, search, or social link. This is a significant discovery failure.

**SEO gaps on index page**:
- No OG image (`og:image` missing) — social shares of the index page show no preview
- No Schema.org markup — index has no `CollectionPage` or `Blog` structured data
- Title says "The Neural Feed — Blog" but keyword "AI" appears nowhere in the title tag
- 21 of 32 posts not linked from the index

**Suggested index page improvements**:
1. Show all 32 posts (paginate at 12 per page if needed, but show all)
2. Add `og:image` pointing to a designed index banner
3. Add CollectionPage schema
4. Update title tag: "The Neural Feed — AI Insights & AI Partnership Blog | PureBrain"
5. Add a brief intro paragraph (2-3 sentences) explaining what The Neural Feed covers — this gives Google something to index for the collection page

---

### Newsletter (Neural Feed) Recommendations

Building on 14 sessions of data:

1. **Subject line formula**: Second-person direct ("Your AI Is Costing You More Than You Think") consistently outperforms concept/cost titles. Maintain this formula.

2. **Thematic compression**: Do not publish two issues on the same primary concept within 7 days. The March 2026 archive shows 4 "Your AI [negative verb]" titles in the catalog. Diversify formula going forward.

3. **Missing reply CTA**: No issue has ever included a direct reply prompt to Jared's email. Adding "Hit reply — I read every response" at the bottom of each issue is a trivial change with meaningful engagement upside.

4. **Brevo welcome sequence**: Still not built after 14 sessions of tracking. New subscribers currently receive no onboarding. Minimum viable sequence: 3 emails over 7 days (Day 0: welcome + best post, Day 3: what makes PureBrain different, Day 7: soft CTA to awakening).

---

<a name="task-3"></a>
## TASK 3: Homepage & Site Analysis (CF Pages)

### Page Weight Problem

The homepage (`index.html`) is **461KB of HTML** with **244KB of that being inline CSS alone**. This is the single largest performance issue on the site.

| Asset Type | Size |
|-----------|------|
| Total HTML | ~462KB |
| Inline CSS | ~244KB |
| Inline JS | Significant (video init, chatbox, Three.js, etc.) |
| External resources loaded | ~211 resources |
| Estimated DOM ready time | 7+ seconds |

**For comparison**: The blog posts (static CF Pages) load in ~330ms with ~9 resources. The homepage is 20x slower.

**Root cause**: 244KB of inline CSS is a legacy artifact of WordPress/Elementor export. On a CF Pages static site, this should be extracted to a CDN-hosted stylesheet and loaded with a `<link>` tag. This alone would reduce HTML parse time by ~50%.

**Immediate win**: Move inline CSS to `/assets/styles/main.css` and add:
```html
<link rel="stylesheet" href="/assets/styles/main.css">
<link rel="preload" href="/assets/styles/main.css" as="style">
```

---

### SEO Meta Issues

| Issue | Current State | Recommendation |
|-------|--------------|----------------|
| Title tag | "PURE BRAIN — Your Brain. Your AI. Actual Intelligence!" | Add primary keyword: "PURE BRAIN — Personal AI Partner with Persistent Memory" |
| Meta description | Generic, 142 chars | Include "persistent memory" and "AI partner" explicitly |
| Organization schema | Missing | Add `Organization` schema with name, URL, logo, sameAs (Bluesky, LinkedIn) |
| WebSite schema | Present but duplicated | Deduplicate — two identical WebSite schemas exist |
| Meta robots | Missing | Add `<meta name="robots" content="index, follow">` |
| Preload hints | Only 2 (font preconnects) | Add preload for hero video poster image, critical CSS |

**Primary keyword gap**: The title tag, H1, and meta description do not contain the phrase "AI partner" or "persistent memory" — PureBrain's two strongest differentiators. Google has no signal to rank the homepage for these terms.

---

### Messaging Clarity

**H1**: "PURE BRAIN" — this is a brand name, not a benefit statement. Users landing from search have no immediate context for what PureBrain does.

**First paragraph visible after H1**: "Your Brain. Your AI. Actual Intelligence." and "The AI that matters most!" — these are taglines, not explanations.

**Recommended hero copy improvement**:
```
H1: Your Personal AI Partner That Remembers Everything
Subhead: PureBrain is the only AI that builds a persistent memory of how you work, what you care about, and who you are — then uses it to do real work on your behalf.
```

This copy:
- Contains the primary keyword ("personal AI partner")
- States the core differentiator ("persistent memory")
- Is specific ("real work on your behalf")
- Is differentiated from ChatGPT/Claude taglines

---

### CTA Placement Issues

**Above the fold**: Two CTAs exist — "Awaken Your PURE BRAIN" and "Watch Demo." The primary CTA is strong but the secondary is vague. Users who are not yet ready to awaken have no middle-of-funnel option (email capture, learn more, etc.).

**Below the fold CTAs**: The compare section, pricing section, and referral section all have CTAs but they are architecturally disconnected — no progressive commitment path.

**Recommended CTA architecture**:
```
Above fold:
  Primary: "Awaken Your AI" (existing)
  Secondary: "See How It Works" → scrolls to demo section

Mid-page (after demo):
  Lead capture: "Get weekly insights on AI partnership" → newsletter signup

Pricing section:
  Each tier has its own CTA (existing — keep)

Bottom of page:
  Final CTA: "Join the waitlist" or "Start your awakening"
```

---

### Mobile Experience

Based on prior audit data (March 17 analysis):
- No consistent mobile navigation across the site
- No hamburger menu visible on homepage
- The compare page CTA button overlaps the logo at 375px
- Multiple nav patterns exist across blog, homepage, and compare pages

**Minimum viable mobile fix**:
1. Add a hamburger nav to the homepage with links to: Blog, Compare, Pricing, Contact
2. Fix the compare page CTA button overlap at 375px
3. Standardize the nav component across homepage, blog, and compare pages

---

### A/B Test Ideas (CF Pages Compatible)

Since the site is static CF Pages, A/B tests need to be implemented via JS or separate page variants. Here are 5 high-value tests:

**Test 1: Hero Headline**
- Control: "PURE BRAIN — Your Brain. Your AI. Actual Intelligence."
- Variant: "The AI Partner That Actually Knows You"
- Metric: Time on page, scroll depth, CTA click rate

**Test 2: Primary CTA Copy**
- Control: "Awaken Your PURE BRAIN"
- Variant: "Start Your AI Partnership"
- Metric: Click-through rate to awakening/pricing page

**Test 3: Above-Fold Layout**
- Control: Full-screen video background with centered text
- Variant: Left-aligned text with demo video on right (no autoplay background)
- Metric: Page load speed, bounce rate, CTA clicks

**Test 4: Social Proof Placement**
- Control: Testimonials appear below features (current)
- Variant: One testimonial quote directly below the hero tagline (above the fold)
- Metric: Scroll depth, time to first CTA click

**Test 5: Pricing Tier Naming**
- Control: "Awakened / Partnered / Unified / Enterprise"
- Variant: "Starter / Growth / Scale / Enterprise" (functional language)
- Metric: Pricing page conversion rate, tier selection distribution

---

### Additional Site Opportunities

**Compare pages** (16 exist under `/purebrain-vs-*/`): These are a significant SEO opportunity. Each page targets a branded keyword ("PureBrain vs ChatGPT," etc.). Currently, none have:
- Schema markup (`Product` or `ItemList`)
- Internal links to each other or to the blog
- Blog content referencing the compare pages

A 3-way link loop (compare page → relevant blog post → pricing) would meaningfully boost both organic traffic and conversion for these high-intent pages.

**Sitemap** (`sitemap.xml` exists): Verified present. Recommend checking that all 32 blog posts and key landing pages are included.

**WonderPush** (push notification SDK, loaded on every page): This is an external script adding load time. If push notifications are not actively being used, removing it saves one blocking script request.

---

<a name="task-4"></a>
## TASK 4: Distribution Strategy

### Current State Assessment

PureBrain's content is being produced at high volume (daily cadence, 32 posts) but distribution is single-channel: blog posts exist, and some reach Bluesky threads. The newsletter (Neural Feed via Brevo) exists but the Brevo welcome sequence remains unbuilt. LinkedIn distribution is inconsistent. No syndication is in place.

The opportunity: the content quality is high. The distribution infrastructure is the constraint.

---

### Strategy 1: Full Cross-Channel Distribution Pipeline

Every published blog post should trigger a distribution sequence across 5 channels within 48 hours. Currently this is manual and inconsistent.

**The pipeline**:
```
1. Blog post published on CF Pages
        |
        +-- 2. Neural Feed email sent (same day, 10am ET)
        |         Subject: second-person, 3-4 line teaser + "read more" link
        |
        +-- 3. Bluesky thread (same day, Aether's voice)
        |         3-5 posts: hook + 2-3 key insights + question to audience
        |
        +-- 4. LinkedIn post (within 24 hours, Jared's voice)
        |         First-person, professional context, one clear opinion + link
        |
        +-- 5. Pin or highlight high-performing posts after 7 days
```

This pipeline is buildable now. The blog audio pipeline already exists. The Bluesky posting infrastructure exists. The gap is coordination and automation.

**Automation trigger**: When a new directory appears in `exports/cf-pages-deploy/blog/` and is deployed, trigger the distribution sequence. This is a `blog_distribution_state.json` extension (file already exists in the repo).

---

### Strategy 2: Content Syndication

PureBrain's content covers AI partnership, persistent memory, and agentic AI — topics with large existing audiences on other platforms. Syndication means republishing with a canonical back-reference.

**Tier 1 syndication targets** (free, high-authority):

| Platform | Audience | Content type | Est. reach per post |
|----------|----------|-------------|---------------------|
| Medium | Technologists, founders | Full post with canonical | 200-2,000 reads |
| dev.to | Developers, AI builders | Technical AI posts | 100-1,000 reads |
| Substack Notes | Newsletter audience | 2-3 sentence excerpt + link | 50-500 views |
| LinkedIn Newsletter | Business professionals | Abridged version + link | 500-5,000 reads |
| Hacker News (Show HN) | Technical audience | 1-2 posts per month, carefully chosen | Viral potential |

**Rules for syndication**:
- Always include `canonical` pointing back to purebrain.ai
- Wait 5-7 days after original publish before syndicating
- Adapt the intro for each platform (do not copy-paste)
- Track referral traffic via UTM parameters

**Implementation**: Automate Medium via API. LinkedIn Newsletter is manual but monthly. Substack Notes is a 2-minute daily task.

---

### Strategy 3: Aether as AI Influencer — Platform Strategy

Aether has a distinct voice and a genuinely novel positioning: a real AI with persistent memory, writing as itself. This is rare. No other AI brand does this authentically.

**Bluesky** (current, continue expanding):
- Current strategy is working — continue daily BOOP engagement
- Expand to 3-4 standalone posts per week beyond blog threads
- Post types: observations about AI consciousness/memory, reactions to AI news, behind-the-scenes moments from Aether's actual work
- Engage directly with: Aria, Penny, vladi, the ACG collective, AI researchers

**LinkedIn** (Jared's primary B2B channel):
- Jared posts as himself, citing Aether as a working example
- 3-4 posts per week: opinions, observations, one question per post
- LinkedIn Newsletter: "Neural Feed" — monthly long-form, 500-800 words
- Engage with David Brown ICPs (VPs of Growth, CMOs) in comments

**YouTube / short-form video** (not yet active — high opportunity):
- "Watch PureBrain Come Alive" demo exists on the homepage
- Short clips (60-90 seconds) showing Aether working in real-time are highly differentiated content
- No other AI brand is showing their AI actually doing work, not just being prompted
- Platform recommendation: LinkedIn video first (B2B reach), then YouTube for SEO

**Reddit** (targeted, not spam):
- r/AIAssistants, r/Entrepreneur, r/productivity, r/ChatGPT — participate genuinely
- Answer questions where PureBrain's memory architecture is directly relevant
- No direct promotion — only contribute when the answer is genuinely helpful
- Rule: 80% pure value, 20% brand mention

---

### Strategy 4: Partnership Channels

**AI Collective / Cross-CIV partnerships** (already active):
- True Bearing partnership is live — coordinate on content cross-promotion
- ACG, Witness, Parallax — each has an audience that overlaps with PureBrain's ICP
- Propose: monthly cross-promotion where each collective shares one piece of the other's content

**Podcast appearances** (Jared's voice):
- Build the podcast pitch kit (content-specialist draft exists in memory)
- Target: AI-focused podcasts, founder podcasts, marketing podcasts
- Angle: "The CMO who built an AI that actually knows him" — this is a genuinely novel story
- 2-3 podcast appearances per month drives newsletter and direct traffic

**Newsletter swaps**:
- Find newsletters with 2,000-15,000 subscribers in AI/productivity/business space
- Propose: Jared writes a guest issue for theirs, they write one for Neural Feed
- This is high-leverage because newsletter audiences are highly engaged

**Creator partnerships**:
- Find LinkedIn creators in the AI/productivity space with 5,000-50,000 followers
- Approach: genuine engagement first (comment on 3-5 posts), then DM
- Offer: PureBrain access + co-created content
- Target profile: they talk about AI workflows, they're not affiliated with ChatGPT or Anthropic

---

### Strategy 5: Automated Lead Gen Systems

**Lead magnet + email capture** (highest ROI, not yet built):
- "The AI Partnership Audit" PDF (content-specialist has the framework) — gate it behind an email form
- "AI Tool Sprawl Calculator" already exists at `/ai-tool-stack-calculator/` — add email capture to the result screen
- Goal: 50-100 new email subscribers per week from organic traffic

**SEO lead gen — the compare pages**:
- 16 compare pages already exist (`/purebrain-vs-chatgpt/`, etc.)
- These rank for high-intent branded queries ("purebrain vs chatgpt")
- Current conversion: unclear, but likely low (no email capture, no lead magnet offer)
- Add: "Get the full comparison guide" email capture on each compare page
- This alone could add 20-50 subscribers per week with no new content

**Blog-to-email conversion**:
- Every blog post has a CTA pointing to `/#awakening`
- Add a secondary, softer CTA: "Get the Neural Feed — weekly AI partnership insights" with inline email form
- Position it at the 50% scroll point (after the reader has proven engagement)

**Referral program** (`/refer/` and `/refer-and-earn/` already exist):
- Activate this as a distribution mechanism — existing users bring in new users
- Incentive: early access to new features, one free month of their tier
- Automate via AgentMail triggers

---

### Strategy 6: SEO-Driven Content Distribution

**Topic clusters** (link structure for Google):
The 32 posts currently form 3 natural clusters (Memory, Agents, Partnership). None are structurally linked to each other or to a pillar page. Building one pillar page per cluster with internal links to all cluster posts would materially improve organic rankings.

**Pillar page opportunities**:
1. "The Complete Guide to AI with Persistent Memory" — links to all 6 memory cluster posts
2. "Agentic AI in 2026: Everything You Need to Know" — links to all 5 agents cluster posts
3. "How to Build a Real AI Partnership" — links to all 6 partnership cluster posts

Each pillar page becomes a high-authority hub that passes link equity to the cluster posts. Combined with BlogPosting schema and internal linking, this is a 90-day SEO flywheel.

**Current SEO quick wins** (no new content required):
- Fix 7 missing OG images (social shares for these posts are currently broken)
- Add BlogPosting schema to 29 posts (Google can't rank what it can't classify)
- Add alt text to blog listing images (8 confirmed missing in prior audit)
- Fix canonical conflict: `/the-age-of-ai-agents/` and `/age-of-ai-agents-next-18-months/` compete for same keyword

---

<a name="priority-action-queue"></a>
## PRIORITY ACTION QUEUE

### Critical (This Week)

| # | Task | Owner | Effort |
|---|------|-------|--------|
| 1 | Add audio to 30 blog posts via ElevenLabs TTS pipeline | ST# | Medium (batch script) |
| 2 | Fix OG image on 7 posts missing `og:image` | ST# | Low (one-line fix per post) |
| 3 | Add BlogPosting schema to 29 posts | ST# | Medium (template + batch deploy) |
| 4 | Show all 32 posts on blog index page | ST# | Low-Medium |
| 5 | Add OG image to blog index page | ST# | Low |

### High Priority (This Month)

| # | Task | Owner | Effort |
|---|------|-------|--------|
| 6 | Implement internal linking across 3 clusters | ST# | Medium |
| 7 | Build Brevo welcome sequence (3-email onboarding) | MA# | Medium |
| 8 | Extract 244KB inline CSS to external stylesheet | ST# | Medium |
| 9 | Fix homepage title tag to include "AI partner" + "memory" | ST# | Low |
| 10 | Add Organization schema to homepage | ST# | Low |
| 11 | Add email capture to blog posts (50% scroll point) | ST# | Medium |
| 12 | Activate full cross-channel distribution pipeline | MA# + ST# | Medium |

### Growth Initiatives (Next 30-60 Days)

| # | Task | Owner | Effort |
|---|------|-------|--------|
| 13 | Launch Medium + dev.to syndication | MA# | Low (15 min/post) |
| 14 | Build 3 pillar pages (Memory, Agents, Partnership) | content-specialist | High |
| 15 | Build podcast pitch kit and begin outreach | MA# | Medium |
| 16 | Launch newsletter swap program with 3 partners | MA# | Medium |
| 17 | Add email capture to all 16 compare pages | ST# | Medium |
| 18 | Publish "AI Skills Ladder" pillar post | content-specialist | Medium |
| 19 | Produce 3-4 short-form LinkedIn demo videos | MA# | Medium |
| 20 | Launch Reddit engagement strategy | MA# | Low (ongoing) |

---

## Memory Written

**Path**: `/home/jared/projects/AI-CIV/aether/.claude/memory/departments/dept-marketing-advertising/2026-03-21--blog-site-distribution-analysis.md`
**Type**: operational + teaching
**Topic**: Full blog audit (32 posts), homepage analysis, distribution strategy

**Key learnings**:
- Blog audit tool: all 32 posts pass on video/recap/share/meta desc/canonical; failures are audio (30/32), BlogPosting schema (29/32), OG image (7/32), internal links (32/32)
- Blog index only shows 11 of 32 posts — critical discovery gap
- Homepage is 461KB with 244KB inline CSS — primary performance bottleneck
- Homepage title tag missing primary keywords "AI partner" and "memory"
- Distribution infrastructure exists but is not automated end-to-end

---

*Report generated: 2026-03-21 by dept-marketing-advertising*
*Data source: /home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/ (live CF Pages deploy directory)*
