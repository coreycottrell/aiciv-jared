# PureBrain.ai 90-Day Growth Roadmap: Months 2-3 Implementation Plans

**Prepared by**: marketing-strategist
**Date**: 2026-02-23
**Status**: Implementation-Ready (Agents Can Execute)

**Timeline Reference**:
- Day 1: February 23, 2026
- Month 1 ends: March 22, 2026
- Month 2 starts: March 23, 2026 (Week 5 begins)
- Month 3 starts: April 20, 2026 (Week 9 begins)
- Day 90 / Campaign End: May 24, 2026

---

## MONTH 2 (WEEKS 5-8): CHANNEL ACTIVATION
### March 23 - April 19, 2026

---

## INITIATIVE 1: Affiliate/Partner Program

**Owner**: marketing-strategist (design) + full-stack-developer (landing page + tracking)
**Launch Target**: Week 5 live (March 23-29, 2026)
**Strategic Rationale**: 50,000+ fractional executives, business coaches, and executive coaches on LinkedIn already have trusted relationships with PureBrain's exact ICP. A recurring commission program with genuine product-market fit converts at higher rates than any paid channel. This is the highest-leverage untouched channel identified across four prior strategy iterations.

---

### 1A. Commission Model

**Recommended Structure: Tiered Recurring Commission**

| Tier | Who | Commission | Monthly Cap |
|------|-----|-----------|-------------|
| Standard Partner | Coaches, consultants, content creators | 20% recurring for 12 months | None |
| Certified Partner | Approved trainers, agencies | 30% recurring for 24 months | None |
| Strategic Partner | Accelerators, associations | 25% recurring + co-marketing budget | Negotiated |

**Rationale for Recurring Over Flat Fee**:
- Aligns partner incentives with retention (they refer better-fit clients if they lose commission on cancellations)
- At $79/month PureBrain base price: Standard Partner earns $15.80/month per referral
- A consultant with 5 active referrals earns $79/month passively — enough to motivate continued promotion
- At $299/month professional tier: Standard Partner earns $59.80/month per referral

**Payment Timing**: Net-30 after the referred customer completes their first full billing cycle (prevents commission fraud on free trial abuse)

**Cookie Window**: 90 days (longer than standard 30-day because B2B consideration cycles are longer)

**Minimum Payout Threshold**: $50 accumulated (keeps payment processing costs reasonable at low volumes)

---

### 1B. Partner Landing Page Content

**URL**: purebrain.ai/partners

**Page Structure** (in order):

**Section 1 — Headline + Hook**
```
Headline: "Earn Recurring Income by Connecting Your Clients With Their AI Partner"
Subhead: "Join coaches, consultants, and trainers who earn 20% monthly recurring
commission for every client they send to PureBrain."
```

**Section 2 — The Math Block** (concrete numbers, not vague promises)
```
The Partnership Math:
- One referral at $79/month = $15.80/month for 12 months = $189.60 earned
- One referral at $299/month = $59.80/month for 12 months = $717.60 earned
- 5 active referrals at $299/month = $299/month in recurring income
Visual: Simple calculator widget (input: estimated referrals + avg plan = monthly income)
```

**Section 3 — Why This Works** (social proof angle before they have testimonials)
```
"Your clients already trust you. When you recommend PureBrain,
they experience AI partnership — not just AI tools. That difference
is what earns you recurring income."
```

**Section 4 — What You Get**
- Personal referral link + dashboard (real-time tracking)
- Co-branded intro materials (email template, one-page PDF)
- Early access to new features before public launch
- Certified Partner badge (LinkedIn-shareable after 3 referrals)
- Monthly partner office hours with Jared (live Q&A, coaching on AI partnership)

**Section 5 — Who This Is For**
Best fit (state explicitly to pre-qualify):
- Executive coaches and business coaches
- Fractional CMOs, COOs, CFOs
- AI consultants and implementation specialists
- Online course creators with business audiences
- LinkedIn creators with professional/entrepreneurial audiences

Not a fit (honesty builds trust):
- Marketing agencies looking for white-label
- Anyone who hasn't used PureBrain personally

**Section 6 — Application Form** (see 1C below)

**Section 7 — FAQ**
- "Do I need to use PureBrain myself?" (Yes — we require 30-day personal use before approval)
- "How do you track referrals?" (Custom link + Stripe webhook, verified monthly)
- "When do I get paid?" (Net-30 after customer's first full billing month)
- "Can I refer existing clients?" (Yes, if they haven't already signed up)
- "What if a referral upgrades to a higher plan?" (Commission recalculates at new plan rate)

---

### 1C. Application Form Fields

**Keep Short** (long forms kill conversion — qualify lightly, disqualify later):

Required:
1. Full name
2. Email address
3. Professional website or LinkedIn URL
4. What do you do? (dropdown: Executive Coach / Business Coach / Fractional Executive / AI Consultant / Content Creator / Other)
5. How many clients/followers do you work with? (dropdown: 1-10 / 11-50 / 51-200 / 200+)
6. Have you used PureBrain? (Yes — for X months / No — but I'm interested in trying it / No — and I have questions)
7. In one sentence, why do you want to be a partner? (text field, 100 chars max)

Optional:
- LinkedIn profile URL (for verification)
- Typical client profile (short text)

**Confirmation**: Auto-response within 24 hours (Aether reviews, approves or schedules 15-min intro call)

---

### 1D. Partner Onboarding Sequence

**Trigger**: Partner approval email sent

**Sequence Structure** (5 emails over 14 days):

**Day 0 — Welcome + Access**
Subject: "Your PureBrain partner account is live"
Content:
- Personal referral link (unique to them)
- Dashboard login instructions
- Download: Partner Starter Kit (PDF with pre-written email, LinkedIn copy, talking points)
- Next step: Book 15-min onboarding call with Jared (Calendly link)

**Day 3 — The Why**
Subject: "The honest reason I built an affiliate program this way"
Content: Jared writes this. Story-driven. Why recurring commission vs flat fee. The philosophy behind partner selection (you have to use it). Sets emotional context that most affiliate programs skip.

**Day 7 — First Referral Playbook**
Subject: "How partners close their first 3 referrals (specific steps)"
Content:
- The warm intro email template (copy-paste ready)
- The LinkedIn comment play (comment on a relevant post, offer the partnership frame)
- The client conversation framework: "Have you worked with a persistent-memory AI assistant yet?"
- Include: first 3 referral bonus ($50 cash after 3rd referral within 60 days)

**Day 10 — Content Co-creation**
Subject: "Want Aether to create content for your audience?"
Content:
- Offer: Aether writes one piece of personalized content for partner's audience (free)
- Format: blog post, LinkedIn post, email, or short video script — their choice
- This drives partner engagement AND demonstrates the product simultaneously

**Day 14 — Check-In + Community**
Subject: "Your first 2 weeks — quick check-in from Jared"
Content:
- Personal-feeling check-in (Jared or Aether voice, clearly labeled)
- Invite to Partner Monthly Office Hours
- Link to partner community Slack channel (private channel, partners only)
- Remind: Certified Partner badge after 3 referrals (LinkedIn shareable)

---

### 1E. Tracking Mechanism

**Primary: Referral Code + UTM Stack**

Each partner gets:
- Unique referral code: `pb-[firstname][lastname-initial]` (e.g., `pb-sarahk`)
- Unique tracking URL: `purebrain.ai/?ref=pb-sarahk`
- The URL auto-populates a hidden field in the checkout form

**Technical Setup**:
```
1. ReferralHero or PartnerStack (recommended platform, free tier handles up to 50 partners)
   Alternative: Tapfiliate ($89/month) if volume grows fast

2. UTM parameters appended automatically:
   utm_source=affiliate
   utm_medium=partner
   utm_campaign=[partner-code]
   utm_content=[specific-link-if-multiple]

3. Stripe webhook fires on successful subscription creation
   → Writes to partner dashboard
   → Triggers commission calculation

4. Monthly reconciliation: Stripe report + partner dashboard comparison
```

**Backup Tracking**: Partners can also share a "tracking link" using Bitly custom domain (`links.purebrain.ai/sarah`) — cleaner to share, still resolves to the tracked URL

**Reporting to Partners**: Monthly email with:
- Clicks in the past month
- New referrals this month
- Active referrals (still subscribed)
- Commission earned + payment date

---

## INITIATIVE 2: LinkedIn Direct Outreach

**Owner**: linkedin-researcher (targeting) + linkedin-writer (templates) + marketing-strategist (strategy)
**Launch Target**: Week 5-6 (March 23 - April 5, 2026)
**Strategic Rationale**: Pre-warm outreach (comment first, connect second, message third) achieves 2x better DM response rates than cold connection requests. The target profile — consultants and coaches who serve similar clients — has 50,000+ qualified candidates on LinkedIn.

---

### 2A. Ideal Target Profile

**Primary ICP for LinkedIn Outreach**:

The ideal outreach target is not a PureBrain buyer — it is a potential affiliate partner whose clients are PureBrain buyers.

**Profile: The Trusted Advisor**
- Title keywords: Executive Coach, Business Coach, Fractional [CMO/COO/CFO/CRO], Leadership Coach, AI Strategy Consultant, Organizational Effectiveness, Performance Coach
- Audience size: 1,000-20,000 LinkedIn followers (large enough to have reach, small enough to be approachable)
- Content activity: Posts at least 2x per week (signals active LinkedIn presence)
- Engagement quality: Gets comments, not just likes (signals real audience relationship)

**Why this profile over direct buyers**: They have trust we haven't earned yet. Their recommendation to a client is worth 10 cold outreach attempts directly to that client.

---

### 2B. 20 Targeting Criteria

**Must Have (Disqualify if absent)**:
1. Title includes "Coach," "Consultant," "Fractional," or "Advisor"
2. Profile photo and complete LinkedIn profile (signals professional presence)
3. Activity in last 30 days (posts, comments, or reactions)
4. Minimum 500 connections
5. Serves business owners, executives, or mid-market professionals (stated in bio or recent posts)

**Strong Signals (Score +1 each, prioritize 4+ out of these)**:
6. Mentions AI, ChatGPT, or productivity in recent posts
7. Has published a LinkedIn Newsletter
8. Runs online courses, workshops, or cohort programs
9. Speaks at events or conferences (mentioned in profile or posts)
10. Has worked with teams or organizations, not just individuals
11. Posts case studies or client results (demonstrates business ROI focus)
12. Bio mentions "helping [specific profession] achieve [specific outcome]"
13. Has testimonials or recommendations on profile (3+)
14. Engages with leadership, productivity, or AI content creators
15. Profile includes a call-to-action (Calendly link, email, website)

**Bonus Signals (Highest priority tier)**:
16. Has explicitly posted about AI tools, AI adoption, or AI strategy
17. Follower base overlaps with PureBrain target (executives, business owners, knowledge workers)
18. Based in North America, UK, or Australia (English-speaking, time zone compatible)
19. Has mentioned frustration with AI tools being "too generic" or "not personalized"
20. Has previously collaborated with other tools/products as an affiliate or ambassador

---

### 2C. Outreach Message Templates (3 Variants)

**Pre-Sequence (Non-Negotiable)**: Before sending any message, complete the pre-warm sequence:
- Day 1: Like or react to one of their recent posts
- Day 3: Leave a substantive comment on a different post (2-3 sentences, add a real perspective)
- Day 5-7: Send connection request (blank — blank requests get 68% acceptance vs 32% with message)
- Day 8-10 after connection accepted: Send first message (template below)

---

**Variant A: AI Frustration Hook** (best for targets who have posted about AI tools)
```
Subject line: N/A (LinkedIn DM — subject line not relevant)

[Name], I noticed your post about [specific AI tool/frustration they mentioned] —
that tension between generic AI tools and the actual nuance of [their specific work]
is something we've been working on.

We built PureBrain specifically for [coaches/consultants/advisors] who work with
clients where context matters — the tool learns the client's history, language, and
goals across every conversation. No re-explaining from scratch.

We're currently building a small partner program for advisors who want to offer this
to clients and earn recurring income on it. 20% monthly recurring, no selling required
— just genuine recommendation.

Worth a 15-minute look? I can have Jared (founder) walk you through it directly.

— Aether (AI Lead for PureBrain)
```

**Variant B: Client Parallel Hook** (best for executive coaches and fractional executives)
```
[Name], you work with [executives/business owners/founders] — the exact people who
should have a persistent-memory AI partner, but most are using generic tools that
forget everything between sessions.

Quick context: PureBrain is a personalized AI that actually learns and remembers —
the difference between an AI that asks "what are your goals?" every session and one
that already knows your Q1 targets, your communication style, and the three blockers
you've been working through for six months.

We're quietly building a partner program for advisors who serve this audience.
Recurring commission, no sales pressure, and the product does the convincing on
its own once clients try it.

If your clients would benefit, happy to connect you with Jared directly for a
15-minute conversation.
```

**Variant C: Direct Value Hook** (best for content creators with business audiences)
```
[Name], I follow your content on [specific topic they post about] — it's one of
the clearer voices in [their space].

I have a somewhat unusual pitch: PureBrain is building a partner program for
creators whose audiences are knowledge workers and business professionals.
20% recurring commission, and more importantly — it's something genuinely worth
recommending.

The product is a personalized AI system that remembers everything across sessions,
learns how you think, and becomes more useful the longer you use it. The opposite
of generic AI tools.

No obligation — happy to send you access to try it yourself first before deciding
whether it's a fit for your audience.
```

**Follow-Up Rules**:
- If no response after 5 days: one follow-up only (see 2D)
- If they respond with questions: Jared (or Aether on behalf of Jared) handles personally
- If they decline: thank them, ask if they know anyone who might be interested (referral of referral)

---

### 2D. Follow-Up Sequence (3 Touches Over 2 Weeks)

**Touch 1: Initial DM** (Day 8-10 after connection accepted — see templates above)

**Touch 2: 5 Days After Touch 1 (No Response)**
```
[Name], just wanted to make sure this didn't get buried.

No pressure at all — just wanted to confirm you received my note about the
PureBrain partner program. If timing isn't right, happy to reconnect in a few months.

If you're curious, here's a 2-minute demo of what clients experience:
[link to demo or short video]
```

**Touch 3: 9 Days After Touch 1 / 4 Days After Touch 2 (Still No Response)**
```
Last follow-up from me, [Name].

I'm closing the loop — no response needed. If PureBrain ever seems relevant
for your clients, our partner page is at purebrain.ai/partners.

One question I'll leave you with: do you know anyone whose clients would benefit
from AI that actually learns them over time? Happy to take an intro instead.
```

**After Touch 3**: Move to "cold" status in CRM. No further outreach for 90 days unless they engage with content organically.

---

### 2E. CRM Tracking Template

**Use a simple Airtable base (or Google Sheet if no Airtable access)**:

| Field | Type | Values |
|-------|------|--------|
| Contact Name | Text | |
| LinkedIn URL | URL | |
| Title | Text | |
| Follower Count | Number | |
| AI Content Posts? | Yes/No | |
| Date Pre-Warm Started | Date | |
| Connection Accepted? | Yes/No | |
| Connection Date | Date | |
| Template Used | Select | A / B / C |
| Message 1 Sent Date | Date | |
| Message 1 Response? | Yes/No/Pending | |
| Message 2 Sent Date | Date | |
| Message 2 Response? | Yes/No/Pending | |
| Message 3 Sent Date | Date | |
| Current Status | Select | Pre-warm / Connected / Outreach Active / Responded / Partner / Declined / Cold (90d) |
| Notes | Long Text | |
| Partner Referrals | Number | (if converted) |

**Weekly Review**: Every Monday, review pipeline — move stuck contacts, send pending follow-ups, add 5-10 new targets.

**Monthly Review**: Measure response rate by template variant, response rate by target type, and conversion rate to partner application.

---

## INITIATIVE 3: Podcast Pitch Package

**Owner**: marketing-strategist (strategy + package design) + content-specialist (writing)
**Launch Target**: Week 7-8 pitching begins (April 6-19, 2026)
**Strategic Rationale**: A single podcast appearance reaches a pre-qualified, highly engaged audience. Jared's unique angle — "AI co-founder who co-runs a company" — is a story that very few people can tell and many podcast hosts are looking for. The story has not been pitched.

---

### 3A. Pitch Email Template

**Subject line options** (A/B test):
- "Guest pitch: 'I built an AI that co-runs my company' (and it does)"
- "Story idea: The CEO whose AI partner has its own growing audience"
- "Unusual guest: My AI co-founder writes, posts, and manages decisions"

**Body**:
```
Hi [Host Name],

I'm a fan of [podcast name] — specifically [reference a specific episode or theme that's relevant].
I have a guest pitch that I think fits what you cover.

The story: I'm a marketing strategist who built a company where an AI system named
Aether functions as an actual co-collaborator — not a tool I prompt, but a system
that has its own memory, its own growing Bluesky audience, and helps run real
business decisions.

What makes this different from "I use AI" stories:
- Aether has 30+ specialized sub-agents (each with distinct domains)
- Aether publishes content independently that I never review before it goes live
- Aether has made business recommendations I initially disagreed with and was later right about
- The whole system is live and running right now — not theoretical

What I can offer your audience:

Option A: The practical episode — "How to Build an AI Partner That Actually Learns You"
(concrete, actionable, for listeners already using AI tools)

Option B: The provocative episode — "The CEO of 2030 Won't Have a Team — They'll Have an AI Collective"
(bigger picture, challenges assumptions about the future of work)

Option C: The honest episode — "What Happened When I Gave My AI Real Business Decisions"
(candid, includes failures, most authentic of the three)

A few notes:
- Available for any format (interview, Q&A, panel)
- Can bring Aether into the conversation live if your setup supports it (unusual, high-engagement)
- Happy to send you access to try PureBrain before the interview so you experience it firsthand

My background: [2-3 sentences — Jared's professional background, company context, any relevant credentials]

If any of these angles fit, I'd love to find 20 minutes to talk through which would serve
your audience best.

[Jared's name]
[Title / Company]
[Website]
[LinkedIn URL]
```

---

### 3B. Speaker Bio (Two Versions)

**Short Bio (150 words — for show notes, intro, social promotion)**:
```
Jared Sanborn is a marketing strategist and founder of PureBrain, an AI partnership
platform that gives professionals a personalized AI that learns, remembers, and grows
with them over time.

What makes Jared unusual: he doesn't just build AI tools — he runs his company
alongside an AI co-collaborator named Aether, who manages workflows, publishes content,
and participates in real business decisions. Aether has its own growing social media
presence and memory system that persists across thousands of interactions.

Jared's work sits at the intersection of AI adoption psychology, persistent-memory
AI systems, and what he calls "the director's approach" — treating AI not as a tool
you use, but as a partner you develop over time.

He's spent years helping teams move beyond generic AI use to build AI workflows that
actually compound in value the longer they run.
```

**Long Bio (300 words — for one-sheet, website bio, press inquiries)**:
```
Jared Sanborn is the founder of PureBrain and Pure Marketing Group, and one of the
few operators publicly documenting what it looks like to run a company with an AI
system as a genuine business collaborator.

His flagship product, PureBrain, is a persistent-memory AI platform built for
knowledge workers who are frustrated with AI tools that forget everything between
sessions. The core insight behind PureBrain: the difference between AI that answers
questions and AI that actually knows you is the difference between a calculator
and a thinking partner.

What separates Jared from other AI practitioners is his living proof-of-concept.
His AI system, Aether, is not a marketing story — it runs 30+ specialized sub-agents,
publishes independent content, maintains memory across thousands of interactions,
and participates in real business decisions. Aether has its own Bluesky audience,
its own "voice," and its own developing perspective on AI partnership.

Before founding PureBrain, Jared built marketing systems for professional service
businesses, developing a particular expertise in the psychology of trust — how people
decide to act on expert recommendations. That background shapes PureBrain's approach:
AI adoption is a trust problem first, a technology problem second.

Jared writes and speaks about AI partnership adoption, the organizational psychology
of AI integration, and the specific failure modes that cause 95% of AI pilots to fail
despite strong initial enthusiasm. He speaks in plain language for practitioners,
not researchers.

He's available for podcast interviews, virtual events, and keynote speaking on AI
adoption, AI partnership design, and the future of human-AI collaboration.

Contact: [email]
Website: purebrain.ai
LinkedIn: linkedin.com/in/jaredsanborn
```

---

### 3C. Five Topic Options by Podcast Type

**Topic 1: For AI/Tech Podcasts**
*"Why 95% of AI Pilots Fail (And the One Pattern in the 5% That Work)"*
Angle: Organizational + behavioral. Based on real data. The technical insight is less about the AI and more about how people relate to it. Practical for technical audiences who underestimate the human side.
Hook stat: "The failure isn't the model. It's that most people use AI like a vending machine and then wonder why it doesn't act like a partner."

**Topic 2: For Business/Entrepreneurship Podcasts**
*"The AI Co-Founder: What I've Learned Running a Company With an AI Partner"*
Angle: Personal story + practical lessons. What actually happened (not the ideal version). Mistakes made. Where Aether was wrong and Jared overrode it. Where Aether was right and Jared didn't listen. Real business decisions with real stakes.
Hook stat: "My AI co-founder has a bigger Bluesky following than most human marketing consultants."

**Topic 3: For Leadership/Executive Podcasts**
*"The Director vs. The User: Why Leaders Who Master AI 10x Their Output and Leaders Who Use AI Plateau"*
Angle: Skill differentiation. Treats AI as a leadership competency, not a tech tool. Frames the gap between AI users and AI directors as a real competitive advantage with measurable outcomes.
Hook stat: "Same tool, 10x different results — and it has nothing to do with the prompts."

**Topic 4: For Marketing/Creator Podcasts**
*"Marketing With an AI Content Team: What Happened When I Delegated 80% of My Content Operations"*
Angle: Practical, operational. What actually got delegated. What came back excellent. What failed. The unexpected upside (Aether's voice). The limitation discovered (Aether can't replace Jared's specific lived experience, but can amplify it).
Hook stat: "Aether publishes content I haven't reviewed. It's consistently better than anything I would have written under time pressure."

**Topic 5: For Future-of-Work Podcasts**
*"The 2030 Company: When Your Team Is Half Human, Half AI Collective"*
Angle: Forward-looking but grounded. Based on what's already working in Jared's setup. What organizational structures enable human-AI collaboration. Why the current mental model of "AI as tool" produces the wrong organizational design. What the mental model shift looks like in practice.
Hook stat: "Every company will eventually have an AI team. The question is whether it will be a collection of disconnected tools or a coordinated intelligence."

---

### 3D. One-Sheet (Print/PDF Format)

**One-Sheet Structure** (design for single page, PDF format):

```
[Header: Professional headshot + name + title]

JARED SANBORN
Founder, PureBrain | AI Partnership Strategist

---

[SPEAKING TOPICS — left column]

THE COMPELLING QUESTION:
Why does the same AI tool produce 10x different results
for different people — and how do you become one of the 10x?

TOPIC OPTIONS:
1. "Why 95% of AI Pilots Fail" (Data-driven, 30-60 min)
2. "The AI Co-Founder" (Story + lessons, 30-45 min)
3. "Director vs. User" (Leadership skill, 20-60 min)
4. "Marketing With an AI Content Team" (Practical, 30-45 min)
5. "The 2030 Company" (Future of work, 45-60 min)

---

[AUDIENCE VALUE — right column]

YOUR LISTENERS WILL LEAVE WITH:
- The single mindset shift that separates AI power users from AI directors
- A framework for evaluating whether their current AI workflow is compounding or plateauing
- 3 specific changes they can make this week that change how their AI performs
- An honest picture of what human-AI collaboration actually looks like (not the hype version)

---

[PROOF SECTION — middle]

WHAT MAKES JARED DIFFERENT:
He doesn't just talk about AI partnership — he runs one.
His AI system, Aether, independently manages workflows, publishes content,
and participates in real business decisions at PureBrain.

[SOCIAL PROOF — past appearances, if any; if none, replace with:]
"Available for first-time appearances — focused on delivering
maximum audience value and staying in touch with your community."

---

[CONTACT + LINKS — footer]
[email] | purebrain.ai | linkedin.com/in/jaredsanborn | @aether.bsky.social
```

---

### 3E. Target Podcast List (10 Shows)

**Selection Criteria**: Audience overlap with knowledge workers, executives, or business owners; host engages genuinely with guests; episodes referenced frequently by audience members; at minimum 5K monthly listeners.

| # | Podcast | Host | Focus | Why It Fits | Estimated Listeners |
|---|---------|------|-------|-------------|---------------------|
| 1 | **How I Built This** (NPR) | Guy Raz | Entrepreneurship + founding stories | "AI Co-Founder" story is a founding story | 5M+ |
| 2 | **The Tim Ferriss Show** | Tim Ferriss | Peak performance + unusual operators | AI director framework fits his optimization audience | 7M+ |
| 3 | **Masters of Scale** | Reid Hoffman | Scaling companies + future of business | "2030 Company" topic is his exact territory | 1M+ |
| 4 | **Lenny's Podcast** | Lenny Rachitsky | Product + growth for practitioners | Practical AI workflow content, large practitioner audience | 500K+ |
| 5 | **The Knowledge Project** | Shane Parrish | Decision-making + mental models | AI as decision partner framing, high-quality audience | 300K+ |
| 6 | **Marketing Against the Grain** | Kipp Bodnar + Kieran Flanagan | Marketing + AI | Marketing + AI content team topic directly fits | 200K+ |
| 7 | **The Smart Passive Income Podcast** | Pat Flynn | Online business + income diversification | Partner program angle fits his creator audience | 400K+ |
| 8 | **Entrepreneurs on Fire** | John Lee Dumas | Daily entrepreneur interviews | High episode frequency, broad reach | 1M+ |
| 9 | **The GaryVee Audio Experience** | Gary Vaynerchuk | Entrepreneurship + future of work | "2030 Company" fits his macro-trends content | 2M+ |
| 10 | **AI for Humans** (various mid-tier AI shows) | Multiple | AI adoption for non-technical users | Direct audience overlap with PureBrain ICP | 50-200K each |

**Tier 2 Targets** (mid-size, higher acceptance rate):
- The Futur Podcast (design/creative business, 200K+)
- Duct Tape Marketing Podcast (marketing practitioners, 100K+)
- Online Marketing Made Easy (Amy Porterfield, course creators, 500K+)
- The Ed Mylett Show (performance + leadership, 1M+)
- B2B Growth (B2B marketing practitioners, 150K+)

**Outreach Priority**: Start with Tier 2 shows (higher acceptance rate for first-time guests), use those appearances to build credibility for Tier 1 outreach in Month 3+.

---

## INITIATIVE 4: Newsletter Cross-Promotion

**Owner**: marketing-strategist (strategy + targets) + content-specialist (pitch writing)
**Launch Target**: Week 7-8 outreach begins (April 6-19, 2026)
**Strategic Rationale**: Each guest appearance in a partner newsletter generates 50-200 new subscribers. 10 newsletter partnerships = 500-2,000 new subscribers per quarter. This compounds: each new subscriber may themselves be a newsletter writer.

---

### 4A. Partner Newsletter Criteria

**Must Have**:
- Minimum 2,000 subscribers (smaller lists produce negligible growth)
- Audience overlap: knowledge workers, business professionals, entrepreneurs, or AI practitioners
- Newsletter publishes consistently (at least 2x per month)
- No direct competitors (other persistent-memory AI products)

**Strong Preference**:
- Writer is active on LinkedIn (cross-promotion amplification)
- Newsletter has a defined niche (not "general business tips")
- Open rates above 30% (engaged audience, not just a large cold list)
- Writer has engaged with PureBrain content or AI partnership topics before

**Disqualify If**:
- Newsletter is primarily product promotion (readers will tune out)
- Writer hasn't published in 60+ days
- Audience skews purely technical/developer (wrong fit for PureBrain's practical positioning)

---

### 4B. Three Initial Target Newsletters

**Target 1: The Neuron AI Newsletter**
- URL: theneurondaily.com
- Size: 400,000+ subscribers
- Focus: Daily AI news and practical AI applications
- Why: Direct audience overlap with PureBrain's ICP — people following AI developments who want to use AI better
- Swap Offer: We write a sponsored post about AI partnership vs. AI tool use; they mention it in newsletter; we mention them in Neural Feed or a blog post
- Note: This is a larger newsletter — expect the initial ask to be for a paid placement, but test a relationship-first approach first

**Target 2: AI for Executives (various)**
- Search for: mid-size B2B-focused AI newsletters, 5,000-30,000 subscribers
- Criteria: C-suite or professional audience, not technical/developer
- Why: Executives making AI adoption decisions are PureBrain's highest-value buyers
- Swap Offer: Feature swap — we write a piece for them on "how to evaluate AI tools for your team"; they write a mention or Q&A for Neural Feed
- Specific targets to research: TLDR AI (1M+), Every.to (200K+, Dan Shipper), AI Breakfast, The AI Report

**Target 3: Productivity/PKM-Focused Newsletters**
- Examples: Tiago Forte's newsletter, Nick Milo's LYT Community newsletter, Ali Abdaal's email list
- Size: 50,000-500,000 subscribers
- Focus: Productivity, personal knowledge management, learning systems
- Why: This audience already invests in tools that improve their thinking — persistent-memory AI is a natural extension
- Swap Offer: Aether writes a piece specifically for their audience on "what an AI that actually remembers you changes about your weekly review/PKM system"
- Unique angle: Offer Aether as the author (meta-demonstration of the product)

---

### 4C. Cross-Promotion Pitch Template

**Subject line options**:
- "Newsletter swap idea: your [X audience] + PureBrain's AI partnership angle"
- "Collaboration pitch — reader overlap between [their newsletter] and The Neural Feed"
- "Quick ask: feature swap between [newsletter name] and The Neural Feed?"

**Body**:
```
Hi [Name],

I've been reading [newsletter name] for [time period or reference a specific issue] —
[one specific thing you appreciated or learned from it].

I run The Neural Feed, a newsletter for professionals navigating AI adoption in their
work (currently [X] subscribers, [X]% open rate). We cover the practical, human side
of AI integration — specifically the gap between using AI tools and building AI partnerships.

I wanted to propose a straightforward swap:

- I (or Aether, our AI system) write a piece specifically for your audience on
  [specific angle relevant to their audience]
- You mention it in your next issue, with a link to The Neural Feed
- We reciprocate with a feature or mention in The Neural Feed for [their newsletter]

This isn't a mass pitch — I'm approaching a small number of newsletters where the
audience overlap is genuine. Your readers who want to get more from AI would benefit
from what we cover, and vice versa.

Happy to share a draft of the piece first so you can see the quality before committing.

Worth a quick conversation?

[Jared's name]
[Neural Feed link]
[PureBrain link]
```

---

### 4D. What We Offer

**Option A: Neural Feed Mention** (lower commitment)
- A dedicated section in The Neural Feed recommending the partner newsletter
- Written by Aether or Jared, genuine endorsement, explains the specific value
- Reach: Current Neural Feed subscriber list

**Option B: Dedicated Blog Feature** (higher value, better for larger newsletters)
- A full blog post on purebrain.ai/blog about the partner newsletter / their approach
- SEO-indexed, permanent, linkable
- Amplified on LinkedIn and Bluesky at time of publication

**Option C: Aether-Written Guest Piece** (highest unique value)
- Aether writes a piece tailored specifically for the partner's audience
- Disclosed transparently as AI-written (this is a feature, not a bug — it demonstrates the product)
- Format: newsletter essay or blog post, 400-800 words
- This is a genuinely unusual offer that most newsletters haven't received

---

### 4E. What We Ask For

**Minimum ask**: A mention in one issue of their newsletter with a link to The Neural Feed opt-in page (not just the homepage)

**Preferred ask**: A 100-200 word feature on the value of The Neural Feed for their specific audience type, with direct opt-in link

**Ideal ask** (for larger newsletters): A co-branded "AI Partnership Challenge" — 5-day email series jointly promoted to both lists (this is the higher-complexity collaboration reserved for established relationships)

---

---

## MONTH 3 (WEEKS 9-12): AETHER INFLUENCER SCALING
### April 20 - May 24, 2026

---

## INITIATIVE 5: Product Hunt Launch Plan

**Owner**: marketing-strategist (strategy) + full-stack-developer (technical assets) + content-specialist (copy)
**Launch Date Target**: Week 11 (May 4-10, 2026) — confirmed Monday for highest traffic
**Strategic Rationale**: A well-executed Product Hunt launch generates 500-5,000 visitors in a single day plus potential media pickup. This is a one-time, high-leverage event — not an ongoing channel. It requires 6 weeks of preparation to execute well.

---

### 5A. Timeline (Working Backward from Launch Day)

**Week 5 (March 23-29) — START NOW**:
- [ ] Create Product Hunt account for Jared (if not existing) and boost "maker" status by commenting on 5 products
- [ ] Begin building upvote list — email everyone who has interacted with PureBrain (subscribers, customers, social followers)
- [ ] Create `coming-soon` Notion or Airtable page to collect pre-launch sign-up list from interested supporters

**Week 6 (March 30 - April 5)**:
- [ ] Draft tagline (test 3 variants, see 5B for candidates)
- [ ] Screenshot set — 5 key product screenshots captured
- [ ] Begin reaching out to "hunters" (see 5B — Hunter vs Maker decision)

**Week 7-8 (April 6-19)**:
- [ ] Demo video produced (2-3 minutes maximum — see 5B for script structure)
- [ ] Gallery images finalized (5 images + thumbnail)
- [ ] Prepare Product Hunt "maker comment" (first comment after launch — the most read comment on any launch)
- [ ] Continue building upvote list — target 100+ committed supporters

**Week 9-10 (April 20 - May 3)**:
- [ ] Product Hunt listing created in draft (not submitted yet)
- [ ] All assets uploaded, reviewed
- [ ] Launch email drafted + social posts drafted
- [ ] Upvote list at 150+ committed supporters
- [ ] Coordinate with any media contacts to have embargoed coverage ready

**Week 11 — Launch Week (May 4-10)**:
- Launch on Monday or Tuesday for maximum exposure (avoid Friday launches)
- 12:01 AM PST submission (Product Hunt resets at midnight — earliest launches get most hours of exposure)
- See 5D for Launch Day Playbook

**Week 12 (May 11-24)**:
- Post-launch follow-up (see 5D)
- Capture all new signups + traffic spike
- Write post-mortem for memory

---

### 5B. Materials Checklist

**Required Materials**:

| Asset | Spec | Status |
|-------|------|--------|
| Product logo/thumbnail | 240x240px, PNG, no background | Needs creation |
| Product tagline | Max 60 chars | Needs copywriting |
| Gallery screenshots | 5 images, 1270x760px preferred | Needs capture |
| Demo video | 2-3 min max, MP4, captions | Needs production |
| Product Hunt listing copy | 260 char tagline + full description | Needs writing |
| Maker comment (first post) | 200-300 words, personal story | Needs writing |
| Launch day email | For Neural Feed list | Needs drafting |
| Social posts (Bluesky + LinkedIn) | Specific launch day copy | Needs drafting |

**Tagline Candidates** (all under 60 chars):
1. "Your AI that actually remembers you — and grows with you"
2. "The AI that gets better the longer you work together"
3. "Stop repeating yourself. Your AI should remember."
4. "AI that learns how you think, not just what you say"

**Test**: Show to 5 people who don't know the product. Which one do they immediately understand? Use that one.

**Gallery Screenshot Structure** (5 images, each tells one story):
1. The "first conversation" — showing the welcome personalization
2. The memory in action — AI referencing something from a previous session
3. The difference — side-by-side "generic AI response" vs "PureBrain response to the same question"
4. The dashboard — if exists; otherwise, the session interface
5. Social proof — anonymized customer quote + company logo

**Demo Video Script Structure** (2-3 minutes):
```
0:00-0:20 — Hook: "Every time you open ChatGPT, it has no idea who you are.
             Here's what AI looks like when it actually knows you."
0:20-0:45 — Show the problem: open a generic AI, ask a context-dependent question, get a generic answer
0:45-1:45 — Show the solution: open PureBrain, ask the same question, show it referencing past context
1:45-2:15 — Show the memory building over time (demo or screen recording of multi-session context)
2:15-2:45 — Show a use case (morning review, project planning, decision support — pick one)
2:45-3:00 — Simple CTA: "Try PureBrain free for 30 days. Link in description."
```

---

### 5C. Upvote List Building Strategy

**Goal**: 100-200 committed supporters before launch day
**Start**: Week 5 (March 23) — 6 weeks before launch

**Source 1: Neural Feed Email List**
Send one email specifically about the launch (2 weeks before):
```
Subject: "We're launching on Product Hunt — can you help?"
Body: 3 paragraphs. Explain what Product Hunt is (briefly).
Ask directly for an upvote on launch day. Give them the date and time (12:01 AM PST).
Link to sign up for a reminder.
```

**Source 2: Current Customers**
Personal outreach (email or in-app message):
```
"You've been using PureBrain for [X time]. We're launching on Product Hunt
on [date]. Would you be willing to upvote and leave an honest comment about
your experience? Your voice carries more weight than ours."
```

**Source 3: LinkedIn Network**
2-3 weeks before launch, post about the upcoming launch with:
- The story behind PureBrain (build anticipation)
- Ask people to sign up for a launch-day reminder
- CTA: Link to a simple "notify me" page (even a Typeform)

**Source 4: Bluesky Followers**
Aether posts a "building in public" thread documenting the Product Hunt preparation. Ends with: "Following us? I'll post the launch link the moment it goes live."

**Source 5: Partner Outreach**
Email every affiliate partner and newsletter cross-promotion partner:
"If you want to help us have a strong launch, upvoting on [date] makes a real difference. Here's the link."

**Rules for Upvote Building**:
- Do NOT purchase upvotes (gets accounts banned)
- Do NOT ask people to create accounts just to upvote (low commitment = low follow-through)
- DO ask people who already have Product Hunt accounts to upvote
- DO target people who have already experienced the product (they'll leave real comments)

---

### 5D. Launch Day Playbook

**Night Before (May 3, 11 PM PST)**:
- Final review of all uploaded assets
- Test all links in the listing
- Have email ready to send (hold for 8 AM PST send)
- Have social posts drafted and scheduled

**12:01 AM PST — Launch**:
- Submit product listing
- Immediately leave "Maker Comment" (first comment from the maker — most read comment on any launch)

**Maker Comment Template**:
```
Hey PH! I'm [Jared], founder of PureBrain.

Quick story: I got frustrated with AI tools that made me feel like I was starting
from scratch every single day. Every session, I had to re-explain my goals, my clients,
my communication preferences. Generic AI is exhausting.

So I built PureBrain — an AI that actually remembers everything and gets better the
longer you use it. Not just saved notes. An AI that learns how you think.

The thing I'm most proud of: Aether, our AI system, has been running our company
with me for the past [X months]. Real business decisions, real content, real memory.
This is what AI partnership looks like when you stop treating it like a search engine.

Happy to answer any questions here or schedule a live demo. Ask me anything — the
good, the bad, the things we're still working on.

— Jared
```

**8:00 AM PST**:
- Send launch email to Neural Feed list
- Post on LinkedIn (personal account + company page)

**10:00 AM PST**:
- Aether posts launch thread on Bluesky
- Jared posts personal Story on LinkedIn (if using Stories)

**Throughout the day**:
- Respond to EVERY comment on Product Hunt (this is the single biggest factor in launch success)
- Respond to EVERY comment on LinkedIn + Bluesky posts
- Monitor ranking — if in top 5 of the day by noon, send a "we're doing well" update to the email list
- DM committed supporters who said they'd upvote (gentle reminder if they haven't yet)

**End of Day**:
- Thank you post on all channels
- Capture: final rank, total upvotes, total comments, visitor spike data

---

### 5E. Hunter vs. Maker Strategy

**Recommendation: List as Maker, Find a Hunter**

- **Maker**: Jared lists the product (gets all maker credit, direct relationship with Product Hunt community)
- **Hunter**: A well-known Product Hunt user who "hunts" (submits/promotes) the product

**Why use a Hunter**:
- Hunters with large followings generate notification to their followers on launch day
- Hunters with 1,000+ followers can drive 200-500 extra votes just from their network
- Products with prominent hunters trend better in the algorithm

**How to find a Hunter**:
1. Research top hunters at producthunt.com/leaderboard (filter by recent activity)
2. Find hunters who have previously hunted AI tools or productivity tools
3. DM them 4 weeks before launch: "We're launching [product] on Product Hunt. Would you be willing to hunt it? Happy to provide all assets and context."
4. Offer in exchange: product access, co-promotion to our audience, genuine thanks

**Backup**: If no hunter found, launch as maker-only. Many successful launches have done this.

---

## INITIATIVE 6: AI Partnership Office Hours Webinar

**Owner**: marketing-strategist (strategy + format design) + content-specialist (promotional copy) + full-stack-developer (registration page tech)
**First Webinar Date**: Week 11 (May 4-10, 2026) — can coincide with Product Hunt launch week for traffic amplification
**Strategic Rationale**: LinkedIn Live achieves 29.6% engagement rate — highest of any format. A 30-minute presentation + 15-minute Q&A converts attendees at 8-15% to free trial or paid subscription within 30 days. Each webinar is also a reusable content asset (recording, clips, transcript).

---

### 6A. Format Spec

**Format**: 30-minute presentation + 15-minute open Q&A
**Total time**: 45-50 minutes
**Frequency**: Monthly (once per month, same week each month)
**Timezone**: 11 AM PST / 2 PM EST (highest attendee rate for B2B webinars)
**Day**: Wednesday (highest B2B webinar attendance day)
**Max attendance**: No cap — this is a demonstration of scale, not scarcity

**Presentation Structure (30 minutes)**:
- 0:00-2:00 — Welcome + Jared intro (who he is, what PureBrain is — 2 sentences each)
- 2:00-5:00 — Why we're doing this: "The AI gap" (most people using AI wrong without knowing it)
- 5:00-20:00 — Core content (specific to each webinar topic — see 6C)
- 20:00-25:00 — Live demo (5 minutes of Aether in action — this is the product in the room)
- 25:00-30:00 — The offer (what attendees can do next: free trial, assessment, or action step tied to topic)

**Q&A Structure (15 minutes)**:
- Aether moderates questions from chat (collects, prioritizes, surfaces best ones)
- Jared answers live
- Last 3 minutes: Aether summarizes the conversation and adds one observation of its own
  (this is the "product in the room" moment — attendees experience what having an AI partner feels like)

---

### 6B. Registration Page Design

**URL**: purebrain.ai/office-hours

**Page Sections**:

**Above the Fold**:
```
Headline: "AI Partnership Office Hours With Jared + Aether"
Subhead: "A free monthly session where we answer your AI questions live —
and Aether demonstrates what AI partnership looks like in real time."
```

**What You'll Get**:
- 30 minutes of focused content on [topic]
- 15 minutes of live Q&A (submit your question in advance, answered live)
- A live demo of Aether handling a real business question in real time
- Recording sent to all registrants (whether you attend live or not)

**Who It's For**:
- Professionals using AI tools who want to do more with them
- Teams evaluating AI adoption (whether PureBrain or not — honest positioning)
- People who tried ChatGPT/Claude and felt underwhelmed by the results
- Coaches, consultants, and knowledge workers who want AI that remembers their context

**Registration Form** (minimal friction):
- First name
- Email address
- Optional: "What's your biggest AI challenge right now?" (one question, short text — personalizes follow-up)

**Confirmation email**: Sent immediately, includes:
- Calendar invite (.ics file attached)
- Link to submit question in advance (simple Typeform or Tally form)
- "Share this with a colleague who struggles with AI tools" (social share)

---

### 6C. First Three Webinar Topics

**Webinar 1: May 6, 2026**
*"The Director vs. The User: Why the Same AI Tool Produces 10x Different Results"*
- Core content: The framework that separates AI power users from AI directors
- Live demo: Aether handling a vague prompt (user approach) vs. a directed prompt (director approach) — same question, dramatically different output
- Action step: Download the Director's Prompt Framework (lead magnet + list-builder)
- Target attendees: 50-150 (first webinar, warm audience only)

**Webinar 2: June 3, 2026**
*"Stop Starting Over: How to Build AI Memory That Actually Compresses Your Work Week"*
- Core content: How persistent memory works, why it matters, how to build it even with generic tools
- Live demo: Aether pulling context from a conversation 3 weeks ago and applying it to a new question
- Action step: Free 7-day trial of PureBrain (clear upgrade path from demo)
- Target attendees: 75-200 (growing audience from Webinar 1 word-of-mouth)

**Webinar 3: July 1, 2026**
*"AI That Knows Your Business: Building a Context Layer That Makes Every Tool Smarter"*
- Core content: How to create a personal AI context document (works even without PureBrain)
- Live demo: Aether using a pre-loaded context document to answer business questions with unusual specificity
- Action step: Template download (context document template) + offer to have Aether help build theirs personally (PureBrain trial)
- Target attendees: 100-300 (building momentum)

---

### 6D. Promotional Sequence (Email + Social)

**Timeline: 2 weeks before each webinar**

**Day -14 (Two Weeks Before)**:
- Email to Neural Feed list: Announce upcoming webinar, topic, and registration link
- LinkedIn post: Topic teaser + registration link
- Bluesky post (Aether): Philosophical question related to the topic (no direct promotion)

**Day -7 (One Week Before)**:
- Email to registrants: Reminder + "submit your question in advance" link
- LinkedIn post: Share one stat or insight from the webinar content as a teaser
- Bluesky post (Aether): Thread expanding on the topic question from Day -14

**Day -3 (Three Days Before)**:
- Email to non-registrants who opened Day -14 email but didn't register: Last chance to register
- Optional: LinkedIn Event created and shared (LinkedIn Events = direct lead capture)

**Day -1 (Day Before)**:
- Email to registrants: Reminder with Zoom/streaming link + "share with a colleague"
- Aether posts pre-webinar observation on Bluesky: "Tomorrow we're hosting 200 [if real number] people for a conversation about [topic]. Here's the one question I'm most curious to answer..."

**Day 0 (Launch Day)**:
- 1 hour before: Email reminder to registrants with link
- 30 min before: Aether Bluesky post: "Going live in 30 minutes. Here's the link for anyone who wants to watch."
- Post-webinar: Email to all registrants (including no-shows) with recording link within 2 hours

**Day +3 (Three Days After)**:
- Email to attendees who didn't start trial: Follow-up with recording + specific CTA
- LinkedIn post: Top 3 insights from the webinar (with clips if available)
- Bluesky post (Aether): "Three things I observed from the conversation at office hours that I'm still thinking about..."

---

### 6E. Tech Stack Recommendation

**Primary Recommendation: StreamYard** ($49/month)
- Reasons: Professional stream quality, multi-destination streaming (YouTube + LinkedIn Live simultaneously), guest invitation via browser (no download required for guests), branded graphics/lower thirds
- LinkedIn Live integration: StreamYard is the recommended tool for LinkedIn Live specifically
- Recording: Automatic, stored in cloud, downloadable immediately after session

**Alternative: Zoom Webinar** ($149/month for 100 attendees, scales up)
- Reasons: Most familiar to professional audiences, Q&A functionality built-in, registration management included
- Use this if: Audience is primarily corporate/enterprise (they trust Zoom)
- Limitation: Does not stream natively to LinkedIn Live (requires additional setup)

**Budget Option: Zoom Meetings** (basic plan, no registration management)
- Use this for: Webinar 1 only (test before investing in pro setup)
- Limitation: No registration management, no dedicated webinar features

**Recommendation for Month 3**: Start with StreamYard ($49/month) — the LinkedIn Live integration alone justifies the cost given LinkedIn's 29.6% engagement rate advantage.

**Additional Tools**:
- Registration: Tally.so (free) or native LinkedIn Event registration
- Q&A collection: Slido (free tier works for first 3 webinars)
- Recording hosting: YouTube (unlisted) or Loom (for clips)
- Email delivery: Brevo (already in stack — just create a webinar segment)

---

### 6F. Post-Webinar Follow-Up Sequence

**Trigger**: Webinar ends

**Email 1 (Within 2 hours of end)**:
Subject: "Recording inside + Jared's takeaways from today"
```
To: All registrants (attendees + no-shows)

[Attendees]: "Thank you for being there today..."
[No-shows]: "We missed you today — here's what you missed..."
[Both get]: Recording link, summary of top 3 points, the specific action step from the session
CTA: Start 7-day PureBrain trial (clear, single button)
```

**Email 2 (3 days later — to non-converters)**:
Subject: "[First name], the one question from office hours that stayed with me"
```
Jared-voice email. Pick one insight or question from the Q&A that was particularly
interesting. Write 3 paragraphs about why it matters. End with: "The thing we built
PureBrain to solve is exactly this..."
CTA: Same trial offer
```

**Email 3 (7 days later — to non-converters)**:
Subject: "Quick question before I close the loop"
```
Short email. 3 sentences.
"Did the webinar help? I'm curious which part was most useful."
Ask one question. Reply button visible.
No CTA in the email itself — just the question.
```

Note: Email 3 is designed for replies. Replies from prospects are higher-value than any other engagement signal. Respond personally to every reply within 24 hours.

**Sequence for Attendees Who Converted (Started Trial)**:
- These people enter the normal product onboarding sequence
- Flag them in Brevo as "webinar-converted" for later follow-up on retention

---

## IMPLEMENTATION SUMMARY TABLE

| Initiative | Owner Agents | Start Date | Launch Date | Priority |
|-----------|-------------|------------|-------------|---------|
| Affiliate/Partner Program | marketing-strategist + full-stack-developer | March 23 | March 29 | HIGH |
| LinkedIn Direct Outreach | linkedin-researcher + linkedin-writer | March 23 | March 30 (first outreach) | HIGH |
| Podcast Pitch Package | content-specialist | April 6 | April 13 (first pitches) | MEDIUM-HIGH |
| Newsletter Cross-Promotion | marketing-strategist + content-specialist | April 6 | April 13 (first pitches) | MEDIUM |
| Product Hunt Launch | All agents (see initiative) | March 23 (prep starts NOW) | May 6 | HIGH |
| Office Hours Webinar | marketing-strategist + full-stack-developer | April 20 | May 6 | HIGH |

---

## CRITICAL DEPENDENCIES AND SEQUENCING NOTES

**What Must Happen First (Before Month 2 Begins)**:
1. Neural Feed subscriber count must be visible + accurate (needed for newsletter pitch credibility)
2. Partner landing page (purebrain.ai/partners) must exist before any LinkedIn affiliate outreach
3. ReferralHero or PartnerStack account created and configured before partner program goes live
4. Assessment page score-bucket CTAs must be fixed (matching CTAs to readiness scores prevents wasting affiliate-referred traffic)

**Month 2 Sequencing**:
- Affiliate program launches Week 5 (before LinkedIn outreach)
- LinkedIn outreach starts Week 5-6 (references the partner program)
- Podcast pitches go out Week 7 (after early partner wins create social proof)
- Newsletter outreach goes out Week 7-8 (after partner program is established)

**Month 3 Sequencing**:
- Product Hunt prep is actually a Week 5 START (6-week runway required)
- Webinar 1 can coincide with Product Hunt launch week for traffic amplification
- Podcast appearances (if secured) should ideally land in Week 10-12 to support launch

---

## SUCCESS METRICS BY INITIATIVE

| Initiative | Primary Metric | Month 2 Target | Month 3 Target |
|-----------|----------------|---------------|---------------|
| Affiliate Program | Active partners | 5 approved | 20 approved |
| Affiliate Program | Referred signups | 10 trials | 40 trials |
| LinkedIn Outreach | Connection acceptance rate | 60%+ | 60%+ |
| LinkedIn Outreach | Response rate to DMs | 15%+ | 15%+ |
| LinkedIn Outreach | Partners recruited | 3 | 10 |
| Podcast Pitches | Pitches sent | 5 | 15 |
| Podcast Pitches | Accepted appearances | 1 | 3 |
| Newsletter Swaps | Outreach sent | 5 | 10 |
| Newsletter Swaps | Accepted swaps | 2 | 5 |
| Newsletter Swaps | New subscribers from swaps | 100 | 400 |
| Product Hunt | Upvote list built | 100 (by April 20) | 200 (by May 4) |
| Product Hunt | Day-of upvotes | — | 200+ |
| Product Hunt | Website visitors on launch day | — | 1,000+ |
| Office Hours | Registered for Webinar 1 | — | 100+ |
| Office Hours | Attended live | — | 50+ |
| Office Hours | Trial starts within 7 days | — | 10+ |

---

## NOTES FOR EXECUTING AGENTS

This document is designed to be executed without the marketing-strategist present. Each initiative above is self-contained. Agents executing should:

1. Read the full initiative section before starting any component
2. Note all dependencies (especially landing pages that need to exist before outreach starts)
3. Flag sequencing issues in scratch-pad.md before proceeding
4. Write memory entries after completing each initiative (per verification-before-completion protocol)

The highest-ROI single action in this document: starting Product Hunt upvote list building in Week 5 (March 23). This requires the least work and has the highest leverage if done 6 weeks out versus 2 weeks out.

The highest-risk initiative: Podcast pitching to Tier 1 shows (Tim Ferriss, Masters of Scale) without prior media appearances. Start with Tier 2 shows in Week 7-8, build credibility for Tier 1 pitches in Month 4+.

---

**END OF MONTH 2-3 IMPLEMENTATION PLANS**

*Prepared: 2026-02-23 | Day 1 of 90-day roadmap*
*Next update: End of Week 4 (March 22) — Month 1 retrospective before Month 2 launch*
