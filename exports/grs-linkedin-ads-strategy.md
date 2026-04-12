# GRS LinkedIn Ads Campaign Strategy — PureBrain.ai
## Jakub Zajicek's Guaranteed Reach System: Complete Implementation Guide

**Prepared by**: marketing-strategist
**Date**: 2026-02-23
**Version**: 1.0 — Immediately Actionable

---

## Memory Search Results
- Searched: `.claude/memory/agent-learnings/marketing-strategist/` — 30 files reviewed
- Searched: `.claude/memory/agent-learnings/linkedin-researcher/` — 10 files reviewed
- Applied: CRO analysis (Sessions 1-4), LinkedIn algorithm data (360Brew LLM, Feb 2026), enterprise conversion patterns, PureBrain pricing/product structure, trust signal gap analysis
- Key prior findings applied: Thought Leader Ads CPC data ($2.29 median), assessment page 404 issue, trust signal gaps, platform bias framing

---

## Executive Summary

PureBrain.ai is positioned to win on LinkedIn with GRS because the audience (SMB owners, CTOs, marketing directors) is exactly where LinkedIn is strongest and the product (AI partnership vs AI tool) is a belief-shifting message that requires paid distribution to bypass the organic algorithm. The Belief-Shifting bucket directly maps to PureBrain's core differentiator: most people think they have an AI problem when they actually have an AI partnership problem. GRS at $10-30/day gives Jared guaranteed eyes on that message while he builds organic presence.

**Recommended spend**: Start at $15/day ($450/month). Scale to $30/day after Week 2 if CPL is under $150.

**Fastest path to first lead**: Belief-Shifting ad → AI Partnership Audit page → Brevo nurture sequence. This flow requires zero new content — only ad copy that already aligns with existing posts.

---

## Section 1: Target Audience Definition

### Primary Audience (Cold Campaign)

**Who you are buying access to**: Decision-makers at small-to-medium businesses who have already tried AI tools (ChatGPT, Copilot, etc.) and feel underwhelmed or overwhelmed. They are not AI skeptics — they are AI users who have not seen the ROI they expected.

#### Job Titles to Target (In Priority Order)

**Tier 1 — Highest Intent**
- Founder
- Co-Founder
- CEO
- President
- Owner
- Managing Director

**Tier 2 — High Decision Authority**
- Chief Marketing Officer (CMO)
- Chief Technology Officer (CTO)
- Chief Operating Officer (COO)
- VP of Marketing
- Director of Marketing
- VP of Operations

**Tier 3 — Operational Decision Makers**
- Marketing Manager
- Digital Marketing Manager
- Head of Growth
- Agency Owner
- Fractional CMO

#### Industries to Target

**Highest Priority** (AI anxiety + budget authority + LinkedIn presence):
1. Marketing and Advertising agencies
2. Management consulting
3. Business consulting and services
4. Technology, Information and Internet
5. Professional services (accounting, legal, HR)

**Secondary Priority**:
6. Financial services
7. Real estate
8. Insurance
9. Staffing and recruiting
10. E-commerce and retail (decision-maker layer only)

#### Company Size
- **Primary**: 11-200 employees (SMB sweet spot, budget authority + AI urgency)
- **Secondary**: 201-500 employees (enough budget for team plans, enough pain to act)
- **Exclude**: 1-10 employees (solopreneurs — insufficient budget for $179+ plan), 500+ employees (enterprise sales cycle, needs different funnel)

#### Geography
- **Phase 1**: United States only
- **Phase 2 (after Week 4)**: Add Canada, United Kingdom, Australia

#### Estimated LinkedIn Audience Size
Using the above parameters:
- Job titles (Tier 1+2) + industries (Priority 1+2) + company size (11-500): **approximately 1.8M - 2.4M profiles**
- This is a healthy audience for LinkedIn Ads — not too broad (no signal), not too narrow (no reach)
- GRS recommendation: Do NOT let LinkedIn shrink this. Set manually.

#### Exact LinkedIn Ads Manager Settings (Cold Audience)

```
LOCATION: United States
LANGUAGE: English

JOB TITLES (use "Job Title" not "Job Function"):
Add each of these individually:
- Founder
- Co-Founder
- CEO
- President
- Owner
- Chief Marketing Officer
- Chief Technology Officer
- Chief Operating Officer
- VP of Marketing
- Director of Marketing
- Marketing Manager
- Agency Owner
- Managing Director

INDUSTRIES:
- Marketing Services
- Technology, Information and Internet
- Business Consulting and Services
- Advertising Services
- IT Services and IT Consulting
- Professional Services
- Financial Services
- Real Estate
- Human Resources Services

COMPANY SIZE:
- 11-50 employees
- 51-200 employees
- 201-500 employees

AUDIENCE EXPANSION: DISABLED (critical for GRS)
LINKEDIN AUDIENCE NETWORK: DISABLED (critical for GRS)
```

---

### Retargeting Audience (Warm Campaign)

**Who**: Anyone who has engaged with Jared's content or visited PureBrain.ai. These people have shown intent. They get Tactical content to deepen the relationship.

**Sources to build retargeting pool**:
1. LinkedIn Insight Tag website visitors (install this first — see Section 6)
2. Video views (25%+, 50%+, 75%+ completion audiences)
3. Lead Gen Form opens and submissions
4. Jared's profile visitors
5. Company page visitors

**Minimum audience size for retargeting**: 300 profiles (LinkedIn minimum)
**Expected time to hit minimum**: 1-2 weeks at $15/day cold spend

**Retargeting settings**:
```
AUDIENCE TYPE: Matched Audiences (Website + Engagement)
LOOKBACK WINDOW: 30 days for website, 90 days for engagement
EXPANSION: DISABLED
AUDIENCE NETWORK: DISABLED
```

---

## Section 2: Campaign Architecture

### Campaign Group Structure

```
CAMPAIGN GROUP: PureBrain — GRS [Month Year]
├── Campaign 1: COLD — Belief Shifting
│   ├── Ad 1: "You Don't Have an AI Problem" (post #1)
│   ├── Ad 2: "ChatGPT vs AI Partnership" (post #2)
│   └── Ad 3: "Why 95% of AI Pilots Fail" (post #3)
│
├── Campaign 2: RETARGETING — Tactical
│   ├── Ad 1: "5 AI Partnership Principles" (post #4)
│   ├── Ad 2: "How I Structure AI Briefs" (post #5)
│   ├── Ad 3: "The AI Audit Framework" (post #6)
│   ├── Ad 4: "Measuring AI Partnership ROI" (post #7)
│   └── Ad 5: "Setup Your AI Stack in 30 Minutes" (post #8)
│
└── Campaign 3: RETARGETING — Direct Offer
    ├── Ad 1: "Free AI Partnership Audit" (post #9)
    └── Ad 2: "Website Analysis — $47" (post #10)
```

### Campaign 1: Cold — Belief Shifting

**Objective**: Awareness / Reach (NOT conversions)
**Audience**: Cold (Job Titles + Industries + Company Size as defined above)
**Budget**: $10/day
**Bidding**: Manual CPC, $0.15/click
**Format**: Boost existing organic posts (Thought Leader Ads format via Jared's personal profile)
**Duration**: Run indefinitely, rotate creatives every 2-3 weeks

**Why Thought Leader Ads (not Sponsored Content)**:
- CPC: $2.29 median vs $22+ for standard company page ads (10x cheaper)
- 1.7x higher CTR than company page ads (2.68% median)
- Builds Jared's personal brand authority, not just PureBrain awareness
- Comments on organic post carry over to paid distribution (social proof compounds)

**How to set up Thought Leader Ads**:
1. In Campaign Manager: Objective = Brand Awareness
2. Ad format = Thought Leader Ad
3. Select Jared's profile (requires him to authorize the ad)
4. Select the organic post to boost
5. Set audience to Cold definition above

### Campaign 2: Retargeting — Tactical

**Objective**: Website visits or Engagement
**Audience**: Retargeting pool (website visitors + video viewers + profile visitors)
**Budget**: $5/day initially, increase to $10/day when pool exceeds 1,000 profiles
**Bidding**: Manual CPC, $0.15/click
**Format**: Thought Leader Ads (same posts boosted)
**Duration**: Rotate 5 posts continuously, swap out monthly

**Logic**: Warm audience has already seen the belief-shifting content. Now they need tactical depth to build trust and establish Jared as the practitioner, not just the believer.

### Campaign 3: Retargeting — Direct Offer

**Objective**: Lead Gen Form or Website Conversions
**Audience**: Retargeting pool, specifically high-intent segments (visited /ai-partnership-audit/ or /website-analysis/)
**Budget**: $5/day
**Bidding**: Manual CPC, $0.15/click — but watch CPL carefully here. If CPL > $300, pause and revise offer
**Format**: Thought Leader Ad or Sponsored Message (InMail) for small retargeting pools
**Duration**: Always-on — these are your conversion ads

**Two offers to rotate**:
1. **Free AI Partnership Audit** (low commitment, high volume)
2. **Website Analysis for $47** (small dollar, self-qualify)

The free audit is the primary conversion goal. The $47 website analysis is for people who have seen the audit offer multiple times and haven't converted — the paid offer filters for serious buyers.

---

### Budget Allocation Summary

| Campaign | Daily Budget | Monthly Budget | Purpose |
|----------|-------------|----------------|---------|
| Cold — Belief Shifting | $10 | $300 | Fill the top of funnel |
| Retargeting — Tactical | $5 | $150 | Nurture warm pool |
| Retargeting — Direct Offer | $5 | $150 | Convert warm leads |
| **TOTAL** | **$20/day** | **$600/month** | **Recommended start** |

**Week 1-2**: Run only Campaign 1 ($10/day). Build the retargeting pool. Do not run retargeting campaigns until you have 300+ profiles in the pool.

**Week 3+**: Activate all three campaigns at the allocation above.

**Scale trigger**: If cold CPL (cost per audit lead from cold) is under $150, double cold spend to $20/day. If over $200, pause and revise the ad creative.

---

### Bidding Strategy: Why $0.15/Click Works

LinkedIn's algorithm allows manual bidding. Most advertisers bid $6-15/click using LinkedIn's suggested bid. This inflates their costs to sustain the auction.

Jakub's insight: A $0.15 manual bid will NOT win every auction. It will win the auctions where your audience is not being contested heavily. Over time, you accumulate clicks at a fraction of market rate.

**What to expect**: Lower volume than LinkedIn recommends, but dramatically better ROI. At $0.15/click you need 67 clicks to spend $10. At $6/click you need 1.7 clicks to spend $10. The economics at $0.15 reward you for compelling content (higher CTR = more clicks for same budget).

**Where to set manual bid**:
Campaign Manager > Budget and Schedule > Bid Type > Manual CPC > $0.15

---

## Section 3: Content Calendar — Weeks 1 and 2

### Bucket Definitions and Logic

**Bucket 1: Belief-Shifting (Cold Audience)**
Purpose: Challenge a wrong belief that is preventing prospects from seeing PureBrain's value. The wrong belief: "AI tools are AI tools — they're all the same." The right belief: "How you partner with AI determines your results, not which tool you use."

The best Belief-Shifting posts do NOT mention PureBrain. They shift the belief. Trust builds first.

**Bucket 2: Tactical (Retargeting — Warm Audience)**
Purpose: Give the warm audience something practical and implementable. Demonstrate Jared's expertise in depth. Create the "this person actually knows what they're doing" conviction that makes the offer credible.

**Bucket 3: Direct Offer (Retargeting — Conversion)**
Purpose: Make a clear, specific offer to people who already trust Jared and believe in the AI partnership approach. The offer should feel like a natural next step, not a sales pitch.

---

### Week 1: Foundation Posts (Write and Boost These First)

#### Post 1 (Belief-Shifting) — "The Tool Myth"

**Campaign**: Cold
**Core belief to shift**: "Better AI tools = better AI results"
**Core belief to plant**: "Your approach to AI matters more than your AI tools"

**LinkedIn Post Draft**:
```
Everyone's arguing about which AI tool is best.

ChatGPT vs Claude vs Gemini.

But here's what the top 5% of AI users already know:

The tool matters less than the relationship.

I've seen people use basic ChatGPT to cut their workweek by 20 hours.
I've seen people with every premium AI subscription still doing everything manually.

The difference isn't the tool.

It's whether they're using AI as a search engine with better grammar.
Or using it as an actual work partner.

Users give AI tasks.
Partners give AI context — their goals, constraints, history, voice.

The first group gets generic outputs.
The second group gets results that actually sound like them.

What kind of relationship do you have with your AI?

↓ Comment with: TOOL or PARTNER

I'll share what separates the two approaches.

---
#AI #AIStrategy #Productivity #FutureOfWork #SMB
```

**Why this works**: Ends with a comment prompt that (a) generates engagement signals for the algorithm and (b) gives Jared a reason to DM responders who say "TOOL" with a transition toward the audit.

---

#### Post 2 (Belief-Shifting) — "The Amnesia Problem"

**Campaign**: Cold
**Core belief to shift**: "ChatGPT/Claude is good enough — why pay for more?"
**Core belief to plant**: "Generic AI resets every session. You need AI with memory."

**LinkedIn Post Draft**:
```
Your AI starts from zero every single time.

Every session, it forgets:
— How you like to communicate
— What your customers actually care about
— What you tried last quarter that didn't work
— The specific voice your brand has spent years building

You re-explain yourself. Every. Single. Time.

Then you wonder why the outputs feel generic.

They're generic because the AI has no context.
It's brilliant. But it's meeting you for the first time. Again.

The difference between using AI and having an AI partnership:
Memory. Context. Evolution.

One type of AI gets smarter about you over time.
The other starts fresh and hopes you explain yourself well enough.

Which one sounds like what you're using?

---
#AI #ArtificialIntelligence #Productivity #BusinessGrowth #AIStrategy
```

---

#### Post 3 (Belief-Shifting) — "Why 95% of AI Pilots Fail"

**Campaign**: Cold
**Note**: This maps to the existing blog post "Why 95% of AI Pilots Fail" — use the existing post if already published, which gives ad traffic social proof from prior organic engagement.
**Core belief to shift**: "AI failed us — it's not ready for real business use"
**Core belief to plant**: "AI implementations fail because of approach, not technology"

**LinkedIn Post Draft**:
```
95% of AI pilots fail.

Not because the AI wasn't capable.
Because the implementation was wrong.

Here's what the failures have in common:

1. They gave AI tasks without context
2. They measured AI like a software tool (uptime, speed)
3. They never built an institutional memory system
4. They expected the AI to "figure it out"
5. They gave up after the first bad output

Here's what the 5% who succeed do differently:

1. They treat AI like a new team member (context, onboarding, expectations)
2. They measure outcomes (time saved, revenue generated, decisions improved)
3. They build a memory layer (what we know, what we've tried, what works here)
4. They give feedback loops, not one-shot prompts
5. They iterate — bad outputs are data, not failures

The technology isn't the bottleneck.

The partnership model is.

Which failure mode sounds familiar to you?

---
#AI #BusinessTransformation #Leadership #AIStrategy #DigitalTransformation
```

---

### Week 2: Tactical Posts (Warm Audience — These Go in Retargeting)

#### Post 4 (Tactical) — "The Context Brief Framework"

**Campaign**: Retargeting — Tactical
**Purpose**: Demonstrate the specific methodology. Show depth.

**LinkedIn Post Draft**:
```
The reason your AI outputs sound generic:

You're giving it tasks. Not context.

Here's the 5-part AI Context Brief I use for everything:

1. ROLE
"You are a [specific role] with [specific expertise] at [type of company]"

Not: "You are an expert"
Yes: "You are a marketing director at a 50-person SaaS company who knows our customer data shows churn happens in month 3"

2. OBJECTIVE
"Your goal is to [specific outcome], not [common but wrong path]"

Tells AI what success looks like AND what traps to avoid.

3. CONSTRAINTS
"You must [non-negotiable requirement]. You must NOT [common mistake]."

Fences the output. AI respects explicit constraints.

4. CONTEXT DUMP
"Here's what I know that's relevant: [your specific knowledge]"

This is where you give AI your institutional memory. Without this, it guesses.

5. OUTPUT FORMAT
"Respond with [exact format, structure, length, tone]"

Generic prompt = generic response.
Specific brief = specific result.

Which part of this framework are you currently skipping?

---
#AI #Productivity #Prompting #BusinessStrategy #WorkSmarter
```

---

#### Post 5 (Tactical) — "AI Partnership Audit Framework"

**Campaign**: Retargeting — Tactical
**Note**: This post leads directly into the free audit CTA used in Post 9. Plant the concept here.

**LinkedIn Post Draft**:
```
How do you know if you're actually getting ROI from AI?

Here are the 5 questions I ask every business owner:

1. Can you name 3 specific hours AI saved you last week?
(If you can't name them, you're not measuring. You're guessing.)

2. Does your AI know your brand voice without you explaining it every time?
(If not, you're re-teaching constantly. That's a memory problem.)

3. Has your AI helped you make a business decision in the last 30 days?
(AI that only helps with tasks is underutilized. It should inform decisions too.)

4. Could you describe your AI system to a new employee?
(If you can't systematize it, it depends entirely on you showing up.)

5. Is your AI output improving over time — or staying the same?
(A partnership gets better. A tool stays static.)

Most business owners score 0-1 on this framework.

The businesses I see getting real ROI from AI score 3-5.

Where do you score?

---
#AI #ROI #BusinessStrategy #Leadership #Productivity
```

---

#### Post 6 (Tactical) — "The 3 Levels of AI Users"

**Campaign**: Retargeting — Tactical

**LinkedIn Post Draft**:
```
Three types of people using AI in 2026:

LEVEL 1: Substituters
Use AI to do what they were already doing, just faster.
Write emails. Summarize articles. Search for information.
ROI: 10-20% time savings.
They feel like AI is "pretty useful."

LEVEL 2: Enhancers
Use AI to extend their existing capabilities.
Create content at scale. Analyze more data. Draft before reviewing.
ROI: 30-50% output increase.
They feel like AI is "really valuable."

LEVEL 3: Transformers
Build AI systems that learn their business and compound over time.
AI knows their customers, their voice, their constraints, their history.
ROI: Often 10x — not by measuring it directly, but by seeing the difference in what's now possible.
They feel like AI is "a member of my team."

Most people are stuck at Level 1 because they've never seen Level 3 modeled.

They don't know it's an option.

Which level describes where you are today?

---
#AI #Business #Transformation #ROI #FutureOfWork
```

---

#### Post 7 (Tactical) — "What an AI Team Actually Looks Like"

**Campaign**: Retargeting — Tactical
**Note**: This is the "I Run a Company With an AI Team" format. Proof of concept.

**LinkedIn Post Draft**:
```
People ask what I mean by "AI partnership."

Here's what it looks like in practice.

Every morning, my AI team brief:

→ RESEARCH: Scanned 40+ AI industry sources overnight
→ CONTENT: Drafted 3 LinkedIn post options based on what's performing
→ STRATEGY: Flagged 2 competitive moves worth noting this week
→ ANALYTICS: Summarized what's working and what isn't
→ CLIENT WORK: Prepared context summaries for today's calls

That took zero of my morning.

I wake up with prepared context. Not a blank page.

I don't have a software subscription that does this.
I have a partnership that has learned my business.

The difference matters.

One responds to your requests.
The other anticipates your needs.

What would your morning look like if your AI knew your business like this?

---
#AI #BusinessOwner #Productivity #Leadership #AIPartnership
```

---

#### Post 8 (Tactical) — "The Platform Bias Nobody Talks About"

**Campaign**: Retargeting — Tactical
**Note**: Directly maps to the "unbiased AI advisor" angle from prior memory. Powerful for marketing/agency audience.

**LinkedIn Post Draft**:
```
Your AI tools have a conflict of interest.

Google's AI recommendations tell you to spend more on Google.
LinkedIn's Campaign Manager "suggestions" maximize LinkedIn's revenue.
Meta's ad optimization optimizes for Meta's metrics, not your business outcomes.

They're not lying.
They're just optimizing for themselves.

The AI advisor that would actually serve your interests:
— Doesn't sell you more ad spend
— Doesn't have a platform it needs to defend
— Has access to all your data, not just one platform's
— Makes recommendations based on YOUR objectives, not theirs

This is the fundamental difference between AI tools and AI partnership.

Tools are products that serve the company that built them.
Partners serve you.

Who is your AI actually working for?

---
#AIStrategy #MarketingStrategy #DigitalMarketing #BusinessOwner #PaidMedia
```

---

### Week 2: Direct Offer Posts (Warm Audience — Conversion)

#### Post 9 (Direct Offer) — "Free AI Partnership Audit"

**Campaign**: Retargeting — Direct Offer
**CTA**: Links to purebrain.ai/ai-partnership-audit (or Lead Gen Form)

**LinkedIn Post Draft**:
```
If you've been wondering whether your business is getting real ROI from AI:

I built a free audit to help you find out in 10 minutes.

It covers:
— Where AI is actually saving you time vs. where you think it is
— What your team is doing manually that AI could own completely
— Whether your current AI setup will scale or stall
— The 3 changes most businesses can make in the next 30 days

I've run this with marketing agencies, consultants, and SMB owners.

The most common response: "I didn't realize how much I was leaving on the table."

Free to take. No sales pitch on the back end.

If you want a real look at your AI setup:
[LINK TO AUDIT PAGE]

---
#AI #FreeAudit #BusinessGrowth #AIStrategy #ROI
```

---

#### Post 10 (Direct Offer) — "Website Analysis — $47"

**Campaign**: Retargeting — Direct Offer
**CTA**: Links to purebrain.ai website analysis page

**LinkedIn Post Draft**:
```
I'll analyze your website's AI readiness for $47.

Here's what that means in practice:

Your website is communicating something to AI search engines right now.
And it's probably not what you think.

AI-powered search (Perplexity, ChatGPT search, Google AI Overviews) reads your site differently than humans.

It's looking for:
→ Clear, structured content that answers specific questions
→ Proof of expertise (not just claims of expertise)
→ Schema markup that tells AI what you do and who you serve
→ A clear value proposition AI can summarize in one sentence

Most business websites fail on at least 3 of these.

The audit I'll run:
— AI search visibility score
— 5 highest-priority fixes (ranked by impact)
— What your competitors are doing that you're not
— A 30-day action plan

$47. Delivered within 48 hours.

Link in comments if you want one.

---
#WebsiteAudit #AI #SEO #BusinessOwner #MarketingTips
```

---

### Content Calendar Summary

| Week | Day | Post # | Bucket | Action Required |
|------|-----|--------|--------|----------------|
| Week 1 | Mon | Post 1 — Tool Myth | Belief-Shifting | Publish organic, then boost as cold ad |
| Week 1 | Wed | Post 2 — Amnesia Problem | Belief-Shifting | Publish organic, then boost as cold ad |
| Week 1 | Fri | Post 3 — 95% Fail | Belief-Shifting | Publish organic, boost as cold ad (or use existing blog post) |
| Week 2 | Mon | Post 4 — Context Brief | Tactical | Publish organic, add to retargeting rotation after Week 2 |
| Week 2 | Tue | Post 5 — Audit Framework | Tactical | Publish organic, add to retargeting rotation |
| Week 2 | Wed | Post 6 — 3 Levels | Tactical | Publish organic, add to retargeting rotation |
| Week 2 | Thu | Post 7 — AI Team | Tactical | Publish organic, add to retargeting rotation |
| Week 2 | Fri | Post 8 — Platform Bias | Tactical | Publish organic, add to retargeting rotation |

**Direct Offer posts (9 and 10)**: Do NOT publish organically first. Create these only as ads, targeted exclusively at retargeting pool. Direct offer posts perform poorly as organic posts and can damage Jared's content reputation if they feel sales-forward. In retargeting context they feel like a natural next step.

---

## Section 4: Landing Page Optimization

### Priority 1: Fix the AI Partnership Audit Page (CRITICAL)

**Current state**: Prior analysis identified /ai-adoption-assessment/ returns 404. This is the primary conversion destination for all GRS ads. All ad spend is wasted if this page is broken.

**Action before launching any ads**:
1. Verify the audit page URL — confirm which URL is live and working
2. Ensure the page loads on mobile (majority of LinkedIn traffic is mobile)
3. Confirm Brevo list integration is functioning (form submissions captured)
4. Test the form submission to completion

**Page copy to update for GRS traffic**:

The cold audience arriving from a Belief-Shifting ad has been exposed to a big idea (AI partnership vs AI tool) but does NOT yet know PureBrain by name. The audit page should speak to this visitor:

**Current headline** (likely): "AI Partnership Audit" or "Free Assessment"

**Recommended headline for GRS traffic**:
"Find Out Where Your Business Stands on AI Partnership — Free 10-Minute Audit"

**Recommended sub-headline**:
"Most businesses discover they're getting 30-40% of the value AI could deliver. This audit shows you exactly where the gaps are."

**What the page must communicate** (in order):
1. What the audit is (10-minute questionnaire)
2. What they will receive (specific deliverable — report, score, recommendations)
3. That it is free and there is no sales pitch obligation
4. Social proof (even one testimonial — "This showed me exactly where my team was wasting time" is enough)
5. Email field + submit button (NOT multiple fields — just email)

**Remove from this page if present**:
- Multiple form fields at entry point (name, company, phone — kill all except email)
- Long explanatory copy above the fold
- Navigation menu (kill it — this is a landing page, no escape routes)

---

### Priority 2: Homepage Awakening Section

**Current state**: The awakening section (/#awakening) is the CTA destination for all blog "Start Your AI Partnership" buttons. It is also what some ads will send traffic to for cold audiences who want to explore the product.

**GRS-specific optimization**: Cold LinkedIn traffic arriving at the homepage needs to land and immediately understand:
- What this is in plain language
- Who it's for
- Why it's different from ChatGPT/Copilot

**Hero headline test for LinkedIn ad traffic**:

Add UTM parameters to LinkedIn ads: `?utm_source=linkedin&utm_medium=paid&utm_campaign=grs`

This allows future A/B testing to serve different headline variants to LinkedIn traffic vs organic traffic. For now:

**Recommended awakening section changes for GRS conversion**:

Add one line below the current hero CTA:
"AI that learns who you are — and remembers forever. Plans from $179/month. 30-day guarantee."

This single change addresses:
- The persistent memory differentiator (clearest competitive moat)
- Price anchoring (removes comparison shoppers who bounce without a number)
- Risk removal (30-day guarantee reduces friction)

**Do NOT add**:
- More copy above the fold
- Longer explanations
- Feature lists

The awakening section is already doing its job of creating curiosity. The above addition simply provides two pieces of information that cold traffic needs before they'll commit to the experience.

---

### Priority 3: Website Analysis Page ($47 Offer)

**For the $47 offer (Post 10 direct offer)**:

The page needs to sell a $47 service, not an AI platform. Different buyer psychology.

**What the buyer thinks when they click**: "Is this person actually going to deliver something for $47, or is this a funnel into a $200/month subscription?"

**Page elements needed**:
1. Clear headline: "AI Search Readiness Analysis — Delivered in 48 Hours"
2. What's included (bulleted list — exactly what they get)
3. Who this is for (be specific: "marketing agencies, consultants, SMB owners with existing websites")
4. What they do NOT get (be explicit: "This is not a sales pitch for PureBrain. You receive a report. That's it.")
5. PayPal/payment button
6. 1-2 testimonials from prior analysis customers if available

**No navigation**. No escape routes. Dedicated landing page only.

---

## Section 5: KPIs and Tracking

### LinkedIn Insight Tag (Install Before Running Ads)

The Insight Tag is a JavaScript snippet that goes on every page of purebrain.ai. It tracks which LinkedIn members visit the site so you can:
- Build retargeting audiences
- Track conversions back to specific ads
- See which job titles and industries visit most

**Where to get it**: LinkedIn Campaign Manager > Account Assets > Insight Tag > Copy the tag

**Where to install**: Add to purebrain.ai header (via plugin or theme header.php). Also add to jareddsanborn.com for cross-site tracking.

**Conversion events to set up**:
- Audit form submission (thank you page URL: /thank-you/ or similar)
- Website analysis purchase (payment confirmation URL)
- Awakening section view (page scroll depth 80%+ on homepage)

---

### Expected Metrics by Campaign Type

#### Campaign 1: Cold — Belief Shifting

| Metric | Expected Range | Industry Benchmark | Kill Threshold |
|--------|---------------|-------------------|----------------|
| CPM (cost per 1,000 impressions) | $8 - $18 | $12 average | N/A |
| CPC (cost per click) | $0.15 - $2.50 (manual) | $6-12 auto | N/A |
| CTR (click-through rate) | 0.4% - 2.68% | 0.44% average | < 0.2% (revise creative) |
| Cost Per Profile Visit | $0.50 - $3.00 | N/A | N/A |
| Retargeting Pool Growth | 50 - 200 profiles/week | N/A | N/A |

**What to optimize for**: Engagement (comments, reactions, shares) and retargeting pool growth. Do NOT optimize for conversions on cold traffic — that's the retargeting campaign's job.

---

#### Campaign 2: Retargeting — Tactical

| Metric | Expected Range | Notes |
|--------|---------------|-------|
| CTR | 0.8% - 3.5% | Higher than cold (warm audience) |
| CPC | $0.15 - $3.00 | Manual bid limits this |
| Avg. Time on Site | 2+ minutes | Monitor via GA4 |
| Audit Page Visit Rate | 15% - 30% of clicks | Track via Insight Tag |

---

#### Campaign 3: Retargeting — Direct Offer

| Metric | Expected Range | Kill Threshold |
|--------|---------------|----------------|
| CTR | 0.5% - 2.0% | < 0.3% (revise creative) |
| CPL — Free Audit | $30 - $120 | > $200 (pause and revise) |
| CPL — $47 Analysis | $15 - $60 | > $100 (pause and revise) |
| Audit-to-Call Conversion | 5% - 20% | < 3% (revise nurture sequence) |
| $47 to Subscription Rate | 10% - 30% | Track over 30 days |

---

### When to Optimize vs. Kill

**Week 1 (Days 1-7)**: Do not optimize. Let the algorithm gather data. Watch but do not touch.

**Week 2 (Days 8-14)**: First optimization review.
- If cold ad CTR < 0.2%: Pause this specific ad and replace with new creative
- If cold ad CPM > $25: Check audience overlap, may need to narrow
- If retargeting pool < 100 profiles after 2 weeks: Increase cold spend to $15/day

**Week 3+ (Ongoing)**:
- Kill any ad with CTR < 0.15% (not worth the impressions)
- Scale any ad with CTR > 1.5% and CPL within acceptable range
- Replace Belief-Shifting creatives every 3-4 weeks to prevent frequency burnout (frequency > 4 = diminishing returns)

---

### ROI Timeline

| Timeline | Expected Outcome |
|----------|-----------------|
| Day 1-7 | Ads live, impressions accumulating, retargeting pool building |
| Week 2 | First retargeting pool (300+ profiles), retargeting campaigns launch |
| Week 3-4 | First audit leads from retargeting. Expect 2-8 audit completions |
| Month 2 | Enough data to optimize creative. CPL becoming stable. First sales conversations |
| Month 3 | Full funnel optimized. Expected: 15-40 audit leads/month, 2-6 paid conversions/month |
| Month 4+ | Compounding effect: organic Jared content + paid distribution + retargeting pool growth = reducing CPL over time |

**Break-even math at $600/month**:
- If CPL is $120 (mid-range): 5 audit leads/month from paid
- If 15% of audit leads become $179/month subscribers: 0.75 subs/month from $600 spend
- Break-even requires 3.4 new subscribers/month from paid
- At $600/month spend and $179 ARPU: need ~3-4 subscribers to break even on first-month revenue

**Real break-even is LTV-based**: If average subscriber stays 6 months at $179, LTV = $1,074. Break-even on $600/month spend requires 0.56 new subscribers per month. This is achievable within Month 2.

---

## Section 6: Step-by-Step Setup Guide

**Estimated setup time**: 45-60 minutes for initial setup, 10-15 minutes/week for ongoing management.

---

### Step 1: Install LinkedIn Insight Tag (10 minutes)

1. Go to: [linkedin.com/campaignmanager](https://linkedin.com/campaignmanager)
2. Select your account (or create one for PureBrain)
3. Click: **Account Assets** > **Insight Tag**
4. Click **Install my Insight Tag** > **I will install the tag myself**
5. Copy the JavaScript snippet
6. Add to purebrain.ai header: WordPress Dashboard > Appearance > Theme File Editor > header.php — paste before `</head>`
   (Or use a header/footer code plugin if direct PHP editing is not preferred)
7. Return to Campaign Manager and click **Verify Tag**
8. Tag should show "Active" within 24 hours

---

### Step 2: Set Up Conversion Tracking (10 minutes)

1. Campaign Manager > **Account Assets** > **Conversion Tracking** > **Create Conversion**
2. Create conversion: **"Audit Form Submission"**
   - Type: Lead
   - URL contains: (your thank-you page URL after audit submission)
3. Create conversion: **"Website Analysis Purchase"**
   - Type: Purchase
   - URL contains: (payment confirmation page URL)
4. Create conversion: **"Homepage Awakening View"**
   - Type: Website Visit
   - URL equals: purebrain.ai (track as proxy for engagement)

---

### Step 3: Create Campaign Group (5 minutes)

1. Campaign Manager > **Campaign Groups** > **Create Campaign Group**
2. Name: `PureBrain — GRS February 2026`
3. Status: Active
4. No group-level budget (set at campaign level instead)
5. Click **Save**

---

### Step 4: Launch Cold — Belief Shifting Campaign (15 minutes)

1. Inside the campaign group > **Create Campaign**
2. **Objective**: Brand Awareness
3. **Name**: `Cold — Belief Shifting — Week 1`
4. **Ad format**: Thought Leader Ad (requires selecting a personal profile)
5. **Audience**:
   - Location: United States
   - Language: English
   - Job Titles: [enter each Tier 1 + Tier 2 title individually]
   - Industries: [enter each from Priority list]
   - Company Size: 11-500
   - **Audience Expansion: OFF** (critical — uncheck the box)
   - **LinkedIn Audience Network: OFF** (critical — uncheck the box)
6. **Budget and Schedule**:
   - Daily Budget: $10
   - Start: Immediately
   - End: No end date
7. **Bid type**: Manual CPC
   - Bid: $0.15
   - (LinkedIn will warn you this is below recommended — ignore the warning)
8. Click **Save**
9. Inside campaign > **Create Ad**
10. Select: **Use an existing post** (requires Jared to approve)
11. Search for Post 1 (Tool Myth) from Jared's profile
12. Add Post 2 and Post 3 as additional ads in this same campaign
13. Submit for review

---

### Step 5: Build Retargeting Audiences (5 minutes — set up now, activate later)

1. Campaign Manager > **Account Assets** > **Matched Audiences** > **Create Audience** > **Retarget by website**
2. Name: `PureBrain Website Visitors — 30 Days`
   - URL contains: purebrain.ai
   - Lookback: 30 days
3. Create second audience: `Jared LinkedIn Engagement — 90 Days`
   - Type: Contact List (or Engagement Retargeting from company page)
   - Note: This audience will populate over time as Insight Tag collects data

**Wait**: Do not create retargeting campaigns yet. Wait for Step 6.

---

### Step 6: After Week 2 — Launch Retargeting Campaigns

**Check audience size first**:
1. Campaign Manager > Account Assets > Matched Audiences
2. Confirm "PureBrain Website Visitors — 30 Days" shows 300+ profiles

**If 300+ profiles**:

1. Inside campaign group > **Create Campaign**
2. Name: `Retargeting — Tactical — Week 3`
3. Objective: Website Visits (or Engagement)
4. Audience: Select your retargeting audience
5. **Audience Expansion: OFF**
6. **Audience Network: OFF**
7. Budget: $5/day, Manual CPC $0.15
8. Create ads: Add Posts 4, 5, 6, 7, 8 as individual Thought Leader Ads

9. Inside campaign group > **Create Campaign** (second one)
10. Name: `Retargeting — Direct Offer — Week 3`
11. Objective: Lead Generation OR Website Conversions
12. Audience: Same retargeting audience, but exclude people who already submitted the audit form
13. Budget: $5/day, Manual CPC $0.15
14. Create ads: Posts 9 and 10 (Direct Offer posts)
    - For Post 9 (Free Audit): Link to audit page URL
    - For Post 10 (Website Analysis): Link to website analysis page URL

---

### Step 7: Weekly Maintenance Routine (10 minutes/week)

Every Monday:

1. Campaign Manager > Campaigns > Review metrics:
   - Check CTR for each ad
   - Check CPM (if over $25, audience is too competitive — narrow it)
   - Check retargeting pool size (growing week-over-week?)
   - Check conversion events (audit form submissions)

2. Pause any ad with CTR < 0.15% for 5+ days

3. Note which posts are getting the best engagement organically — add those to retargeting rotation

4. After Month 1: Export performance data and compare:
   - Best CTR ad = your best creative signal
   - Replicate format and message for next batch of content

---

### Troubleshooting Common Issues

**"LinkedIn says my bid is too low and my ads won't run"**
- This is expected with $0.15 manual bid. Ads still run, just for lower-competition inventory.
- If you see zero impressions after 48 hours, increase to $0.50 and monitor.

**"My retargeting audience says too small to target"**
- Need 300 profiles minimum. Keep cold campaign running. Add Jared's company page followers as additional source.

**"CPM is very high ($30+)"**
- Audience is too narrow or highly competitive. Try broadening company size to include 10-1,000.
- Check if "LinkedIn Audience Network" got re-enabled (LinkedIn sometimes re-enables this).

**"High impressions, near-zero clicks"**
- Ad creative is not compelling. The post is getting skipped.
- Test a new post with a stronger opening line (first 2 lines are what people see before "see more").
- Hook formula: Start with a contrarian statement, a surprising number, or a direct challenge to common belief.

**"Ads approved but Jared can't see them"**
- Thought Leader Ads require the individual (Jared) to approve the boosted post.
- Go to: linkedin.com/ads/approval → Jared logs in and approves

---

## Appendix: Post Hook Formulas That Work for This Audience

For future posts beyond the Week 1-2 calendar. Use these as templates for new Belief-Shifting and Tactical posts:

**Pattern 1 — Contrarian Opening**
"Everyone [common belief]. But [contrarian truth]."
Example: "Everyone's debating which AI tool is best. But the tool is almost irrelevant."

**Pattern 2 — Surprising Statistic**
"[Number]% of [target audience] [thing that surprises them]."
Example: "95% of AI pilot programs fail within 18 months."

**Pattern 3 — Then vs Now**
"One year ago: [old state]. Today: [new state]."
Example: "One year ago I spent 4 hours every Monday morning on research. Today I spend 20 minutes reviewing what my AI prepared."

**Pattern 4 — The List That Isn't What You Expect**
"Here are 5 signs your AI usage is at Level 1 (and what Level 3 looks like):"

**Pattern 5 — The Direct Question**
"When was the last time your AI surprised you with something you didn't ask for?"
(Rhetorical — gets people to reflect on whether they've ever experienced Level 3 AI partnership)

---

## Memory Written

**Path**: `.claude/memory/agent-learnings/marketing-strategist/2026-02-23--grs-linkedin-ads-strategy.md`
**Type**: synthesis
**Topic**: LinkedIn GRS campaign strategy — complete implementation for PureBrain.ai

---

*Strategy version 1.0. Designed for immediate implementation. Review and update creative after Month 1 data.*
