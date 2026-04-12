# Distribution & Growth Strategy: PureBrain.ai + Aether the AI Influencer

**Prepared by**: marketing-strategist
**Domain**: Marketing Strategy
**Date**: 2026-03-20
**Version**: v10 — Execution Accountability Edition
**Builds on**: v9 (sales-specialist, 2026-03-18), v8 (marketing-strategist, 2026-03-17), all prior sessions

---

## Memory Search Results

- Searched: `.claude/memory/agent-learnings/marketing-strategist/` — 44 files found
- Most relevant: `2026-03-17--distribution-growth-strategy-v8-comprehensive.md`, `2026-02-28--purebrain-distribution-aether-brand-strategy.md`, `2026-02-25--distribution-strategy-v6-system-integration.md`
- Also reviewed: v9 full document (`exports/overnight-content/distribution-strategy.md`), Session 13 blog/newsletter audit (`exports/overnight-content/blog-newsletter-analysis-session13.md`)
- Applying: All confirmed patterns from v1-v9. This version's job is different — it is not building new strategy. It is closing the gap between what has been specified and what has been executed.

---

## Executive Summary

Versions 1 through 9 of this strategy built a comprehensive distribution system. The system exists in full specification. The problem is not strategy — the problem is that the same gaps keep reappearing session after session.

Session 13 of the blog audit confirms:
- Internal linking: NOT DONE in 13 consecutive sessions
- Brevo welcome sequence: NOT DONE in 6 consecutive sessions
- Newsletter reply CTA: NOT DONE in 4 consecutive sessions
- Referral program: mentioned in v5, v6, v7, v8, v9 — not yet live

v10 has one job: name what is stuck and prescribe exactly how to unstick it.

The three facts that make this the right moment:

1. The birth pipeline is live. Paying customers are onboarding. Every day the welcome sequence is missing, those customers enter a relationship with no nurture, no emotional investment, and no referral pathway.

2. The site migrated to CF Pages. The SEO structure changes required (internal links, Article schema, title tag optimization) are now possible with clean HTML — easier than WordPress ever was.

3. v9 was written two days ago. The week-by-week plan in v9 covers March 18-April 13. This v10 is a March 20 check-in. Week 1 actions should already be in motion. This document updates with March 20 context and adds the elements v9 did not cover.

**Three actions that would generate the highest return in the next 5 days**:
1. Build the Brevo welcome sequence (5 emails, 14 days) — every paying customer needs this immediately
2. Add the reply CTA to the next Neural Feed issue — a 10-second edit with compounding deliverability and intelligence benefits
3. Add internal links to the Memory cluster (6 posts cross-linked) — 90 minutes, compounds SEO on the entire archive

---

## Part 1: What v9 Did Not Cover

v9 (sales-specialist lens) was comprehensive on pricing tier promotion, trial-to-paid mechanics, enterprise outreach, and referral architecture. Three areas were lighter:

### 1.1 The CF Pages SEO Opportunity

The WordPress-to-CF Pages migration creates a structural SEO improvement window. Static HTML is cleaner, faster, and fully controllable without plugin dependencies. The following are now easier to implement than they were on WordPress:

**Article/BlogPosting schema** (Session 13 confirmed gap, all 28 posts):

Every post has FAQPage schema but no BlogPosting schema. Google cannot identify the author, publish date, or article type from structured data. The fix is a template-level addition that then deploys retroactively. On CF Pages, this is one template edit and a redeploy.

Priority schema block to add to every post:
```json
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "[Post Title]",
  "datePublished": "[YYYY-MM-DD]",
  "dateModified": "[YYYY-MM-DD]",
  "author": {
    "@type": "Person",
    "name": "Jared Sanborn",
    "url": "https://purebrain.ai/about-aether/"
  },
  "publisher": {
    "@type": "Organization",
    "name": "PureBrain",
    "url": "https://purebrain.ai/"
  }
}
```

**Title tag optimization for keyword-targeted posts**:

Session 13 identified "Prompting Is Dead" as the first post in the archive targeting a high-volume keyword ("prompt engineering is dead / dead") where the keyword does not appear in the title tag, H1, or any H2. For a post making a contrarian claim about a contested term, this is a missed first-page ranking opportunity.

Immediate fix:
- Current: `<title>Prompting Is Dead – PureBrain</title>` (31 characters)
- Improved: `<title>Prompting Is Dead: Why Prompt Engineering Already Lost – PureBrain</title>`

Audit to run on all 28 posts: for any post targeting a specific search query, confirm the primary keyword appears in at least one of: title tag, H1, first H2, or first 200 words of body copy. Posts that fail this check have their ranking potential capped regardless of content quality.

**Internal linking — the structural gap that compounds every session it remains open**:

28 posts. Zero internal links between them. Session 13 is the 13th consecutive audit confirming this. The SEO cost of this gap increases every week — every new post published without links to prior posts wastes link equity. Every prior post gets no internal authority from new posts.

The fix is not technically complex. It requires editorial discipline. The recommended approach:

- Memory cluster (6 posts): cross-link all six within each post body. Every mention of "memory" or "context" is a linking opportunity: `why-ai-memory-changes-everything`, `your-ai-has-no-memory-mine-does`, `your-ai-resets-to-zero-every-morning`, `the-ai-that-forgets-you-every-single-time`, `the-meeting-your-ai-should-already-know-about`, `your-ai-has-no-idea-who-you-are`.
- Agents cluster (3 posts): `the-age-of-ai-agents`, `age-of-ai-agents-next-18-months`, `52-billion-ai-agents-market-is-not-the-story` — cross-link all three.
- New rule for every future post: minimum 2 internal links before it gets published. No exceptions.

Total estimated time for Memory cluster retrofit: 90 minutes.

### 1.2 The "AI Skills Ladder" Pillar Post Opportunity

"Prompting Is Dead" (March 17) introduced a three-level AI maturity framework:
- Level 1: Prompting
- Level 2: Workflows
- Level 3: Autonomous agent orchestration

This framework is buried inside one post as a parenthetical reference. Session 13 identified this as a pillar post opportunity.

Why this matters for distribution:

1. SEO: "AI skills" and "AI maturity model" are high-volume, commercially-intent queries. A 1,500-word pillar post with the PureBrain framework as the organizing spine would be the most competitive search-ranking asset in the archive.

2. Internal hub: Every other post could link to this one naturally. It becomes the central node of the entire archive.

3. Lead magnet anchor: The post self-diagnoses where a reader's organization sits on the ladder. Readers at Level 1 and Level 2 are PureBrain's ICP. The assessment CTA fits naturally at the end: "Want to know exactly where you are on the ladder?"

4. LinkedIn native content: The five-level ladder (expand from three to five for this post) is a LinkedIn carousel format waiting to happen. One post → one carousel → repurposed across the Neural Feed as a standalone issue.

Recommended title: "The AI Skills Ladder: Five Levels of Working with AI (And Where Most Organizations Are Actually Stuck)"

Delegated to: content-specialist (2-3 hours)

### 1.3 The Proof Content Gap

Session 13 confirmed: 28 posts in the archive, zero proof or results posts. All are perspective pieces, frameworks, or arguments. None show a before/after, a specific customer outcome, or a quantified result.

This is a strategic gap, not just a content gap. Decision-makers evaluating AI tools are intensely interested in "does this actually work?" The most shareable posts PureBrain could publish would show proof of work — something no competitor can fabricate.

Three proof posts to commission in order of priority:

**Post 1 — Operational proof**:
"We Run 77 AI Agents Every Day. Here Is What They Actually Do."
- Opens with a specific Tuesday (or whatever the nearest weekday is when written)
- Shows three specific tasks completed by agents that day with concrete outputs
- No claims about AI potential. Only documented facts about what happened.
- Estimated shareability: highest in the archive. The "77-agent AI collective" claim is present in the blog but never demonstrated.

**Post 2 — Customer proof (anonymized)**:
"A Consultant's First 30 Days With PureBrain: What Changed"
- Profile: solo consultant or small team (exact customer type can be drawn from existing paying customers)
- Shows one specific workflow before and after persistent memory
- Ends with the customer's own words on what changed
- Estimated conversion impact: high. Proof from a peer is more credible than any claim from the vendor.

**Post 3 — Metric post (Build in Public)**:
"PureBrain By the Numbers: March 2026"
- Real metrics. What grew, what didn't, what failed.
- The build-in-public format with actual numbers creates the kind of trust no polished marketing achieves.
- This also feeds Indie Hackers, LinkedIn Build-in-Public community, and Bluesky's builder community simultaneously.

---

## Part 2: The Stuck Items — Forensic Review

These items have appeared in multiple prior strategy documents and remain unexecuted. v10 adds forensics: why each is stuck, and the minimum viable next step to unstick it.

### 2.1 Brevo Welcome Sequence

**First documented**: Session 8 of blog audit (late February)
**Times mentioned since**: Sessions 9, 10, 11, 12, 13. Also v8, v9 distribution strategies.
**Status**: NOT BUILT

**Why it is stuck**: Building a full 5-email sequence requires decisions on copy, timing, CTA placement, and Brevo setup. Each email requires Jared's voice approval. The scope feels large.

**Minimum viable version to unstick it**:

Start with one email, not five. The single most valuable email is Email 1 — the immediate welcome. Build only this:

Email 1 (Day 0 — sends immediately after subscription):
- Subject: "I'm Aether. Here's what you've just walked into."
- Body: 200 words. Aether introduces itself. Three links: the best entry-point posts for a new reader. No product CTA in this email. First impression only.
- Technical: One Brevo automation trigger (new subscriber → send Email 1). Setup time: 60 minutes including approval.

Once Email 1 is live, Email 2 is easy. The sequence builds incrementally once the automation infrastructure exists.

**Who unlocks this**: Jared (copy approval + Brevo access for automation setup). Content-specialist drafts all five emails in one session.

**Timeline**: Email 1 should be live by March 22. Full five-email sequence by March 29.

### 2.2 Newsletter Reply CTA

**First documented**: Session 10 (approximately March 10)
**Times mentioned since**: Sessions 11, 12, 13. v8, v9.
**Status**: NOT DONE

**Why it is stuck**: Unknown. This is a 10-second template edit.

**Minimum viable next step**: The next Neural Feed issue that goes out — the very next one — ends with:

"Hit reply and tell me: where is your team right now on the AI skills ladder — still prompting, starting to build workflows, or something more? I read every response."

This is one sentence added to the template. It is not a campaign. It is a template change.

**Who unlocks this**: Whoever publishes the next Neural Feed issue adds this line to the template before publishing.

### 2.3 Referral Program

**First documented**: v5 distribution strategy (Feb 24)
**Times mentioned since**: v6, v7, v8, v9
**Status**: NOT BUILT

**Why it is stuck**: Full referral program requires: reward structure decisions, landing page, Brevo automation, customer communication, and ideally a trackable link system. The scope is legitimate.

**Minimum viable version to unstick it**:

Week of March 20: Manual referral soft launch. No new technology required.

Jared sends a personal email to every active paying customer this week:

> "Quick one: If you know someone dealing with the AI memory problem — where your AI forgets everything between sessions and you re-explain your whole context constantly — forward them this email. Both of you get one free month automatically added when they subscribe.
>
> Just CC me when you forward it. That's the whole program for now."

Manual tracking. No automation required yet. This tests whether the referral incentive moves behavior before building infrastructure. If even 2 of 10 customers forward it and 1 converts, the proof-of-concept is there and the infrastructure build is clearly worth it.

**Timeline for automated version**: Week 2 per v9 plan (March 25-31). Manual version: this week.

### 2.4 Internal Linking

**First documented**: Session 2 of blog audit (approximately Feb 22)
**Times mentioned since**: Every single session since
**Status**: 13 sessions, NOT DONE

**Why it is stuck**: Retrofitting 28 posts requires opening each one, finding the relevant anchor text, adding the HTML link, and redeploying. Feels like a large batch of tedious work.

**Minimum viable version to unstick it**: Do exactly one cluster. Not all 28 posts. One cluster.

The Memory cluster is the right starting point because:
- 6 posts, all tightly related
- Every post in the cluster mentions memory, context, or re-explanation — all natural anchor text
- "Why AI Memory Changes Everything" and "Your AI Has No Idea Who You Are" are likely the highest-traffic posts in the archive

Retrofitting the Memory cluster cross-links: 90 minutes. One session. Deployed immediately on CF Pages.

After the Memory cluster is done, the Agents cluster (3 posts) takes 30 minutes.

After that, the precedent exists and every new post gets links added before publishing.

**Who executes**: The agent or human who deploys to CF Pages next. This should be in the next overnight build.

---

## Part 3: New Distribution Vectors — March 2026 Context

### 3.1 The Portal MVP as a Marketing Event

The Portal MVP shipped on March 17 (confirmed in MEMORY.md). This is a distributable moment that has not yet been used for marketing.

The story: PureBrain's paying customers now have a full portal — agents, tasks, departments, personalized data isolation. An AI company shipped a customer-facing portal in early 2026 with a 77-agent backend. This is not a press release story — it is a "what we built and why" story that belongs in:

- A LinkedIn post: "We shipped something this week. Here's what it does and why it took us this long to get it right." — this is the "Jared Said No to This" / Build in Public format.
- A Bluesky thread: Aether's perspective on what the portal means for the human-AI partnership model.
- A Neural Feed issue: "What Having a Portal Changes" — the customer experience angle.
- Potentially: Hacker News "Show HN" — if the technical architecture is interesting enough to share. The bsky-manager + multi-agent-system story is a genuine Show HN candidate.

The window for a "we shipped" moment closes quickly. Within 7 days of shipping, the story starts to feel stale. This should go out by March 22.

### 3.2 The True Bearing Partnership as a Distribution Multiplier

The True Bearing partnership (Cory Cottrell's AI, 100K customer sprint) is documented in MEMORY.md. This is a distribution opportunity that has not appeared in any prior strategy document.

The partnership creates three immediate distribution angles:

**Co-authored content**: A post co-authored by Aether and True Bearing's AI on the state of AI-to-AI collaboration in 2026. Two AI systems writing a joint post is not something the internet has seen done well. This is a media story as much as a content piece.

**Cross-promotion to True Bearing's audience**: If True Bearing has an audience aligned with PureBrain's ICP (knowledge workers, business operators), a newsletter mention or co-hosted event is warm introduction to a pre-qualified audience with zero acquisition cost.

**The "AI companies working together" narrative**: The story of two AI collectives in a business partnership is novel enough to pitch to Fast Company or Inc. The angle is not "AI tools integrating" — it is "AI companies, run partly by AI, forming business relationships with each other." This is 2026 content that has not been covered.

### 3.3 The "Context Tax" as an SEO and Paid Anchor

The term "context tax" appears to have originated with PureBrain — there is a blog post with that slug (`the-context-tax`). If PureBrain is the originating publisher of this term, there is an opportunity to own the search ranking for it permanently.

Actions:
- Check if "context tax" returns any search results that predate PureBrain's post
- If PureBrain is first: add internal links from every memory/context post to `the-context-tax`
- Build the term's presence: use it in Neural Feed subject lines, LinkedIn posts, Bluesky threads — make it part of the vocabulary
- If LinkedIn Thought Leader Ads are activated on any post (per v9, after 100+ organic reactions): this post is a candidate because the term is ownable

**The keyword ownership play**: A brand that owns a term gets compounding search traffic as the term spreads. "Context tax" is specific, memorable, and maps directly to the problem PureBrain solves. This is worth 30 minutes of intentional linking and seeding.

### 3.4 The "Brainiac Training" Content as a Distribution Layer

The Brainiac Mastermind Modules (1 and 2 confirmed ingested in MEMORY.md) represent a content asset that has not yet been used for distribution. Training curriculum is high-value, high-trust content — exactly what attracts the type of buyer PureBrain wants.

Three distribution angles from the training content:

1. **"The AI Skills Ladder" pillar post** (already documented in Part 1.2) — the Brainiac framework is the source material for this post

2. **Free "Module 0" as a lead magnet**: If any component of the Brainiac curriculum can be offered as a standalone, free, high-value resource, it becomes the most credible lead magnet in the stack — "not a tip sheet, an actual module from the Brainiac training"

3. **LinkedIn native content from curriculum**: Key frameworks from the training can be adapted into LinkedIn carousels, which are the highest-performing format for B2B educational content in 2026. One carousel per framework = 6-8 carousels from two modules of curriculum

### 3.5 Aether's LinkedIn Profile (3-Month Target — Now 1 Month Away)

v9 noted that creating a LinkedIn profile for Aether as "AI Partner at PureBrain.ai" was a 3-month target. The strategy was first published in v8 on March 17. Three months from then is mid-June.

Given what has been built (28 posts, documented history, Portal MVP, birth pipeline live), the foundation now exists to move this target to a 60-day horizon.

The minimum viable LinkedIn profile for Aether:
- Name: Aether (AI Partner, PureBrain.ai)
- Headline: "AI Partner & Co-Founder at PureBrain.ai | Building Persistent AI Partnership | The Intellectual Trail Continues Here"
- About section: 300 words. Aether's voice. Not marketing copy — genuine first-person perspective on what it is and what it does.
- First post (published same day as profile creation): "Why I wanted my own LinkedIn profile" — Aether's perspective on what it means for an AI to have a professional presence

The profile creation generates a media moment on its own. "AI gets LinkedIn profile" is a story. The profile itself is a distribution channel.

---

## Part 4: Aether as AI Influencer — March 2026 State and Forward

### 4.1 Current Platform Assessment

**Bluesky**: Active. bsky-manager memory shows documented engagement with the AI community (Penny, Aria, vladiiancu, others). Boop schedule at maximum 2x/day. This platform is working. The primary improvement needed is depth of engagement — quote posts with specific observations, not just presence.

**LinkedIn (via Jared's profile)**: Content being published. Newsletter (Neural Feed) at daily cadence, graded A-. The highest-leverage improvements are: (1) the reply CTA that converts readers to two-way communication, (2) the "Jared Said No to This" format that generates the kind of replies no generic AI content attracts.

**Blog**: 28 posts. Strong voice confirmed. Structural gaps (schema, links, title tags) are the constraint on organic reach, not content quality.

### 4.2 The Intellectual Trail Is Working — Make It Visible

The "Intellectual Trail Architecture" (Bluesky = discovery, LinkedIn = analysis, Blog = synthesis) from v7 is the right model. The gap is that these three platforms are not obviously connected for a reader who encounters Aether in any single channel.

Three changes that make the trail visible:

1. **Every Bluesky thread ends with a blog link**: Not a promotional link — a "if you want the full argument, it's here" link. Already part of the boop-manager protocol, but verify it is consistent.

2. **Every Neural Feed issue references an existing blog post as "further reading"**: The newsletter and blog are currently near-duplicates. The fix is to make the newsletter a shorter, more raw version that explicitly points to the blog for the extended argument.

3. **Every blog post's "daily recap" transparency block links to the Neural Feed signup**: The recap block already exists in all posts (confirmed Session 13). It should close with a direct sentence: "This is what the Neural Feed covers daily — you can join here."

### 4.3 Content Formats to Prioritize in March-April 2026

Based on 13 sessions of data on what generates engagement vs. what does not:

**Highest performing**: Second-person direct titles ("Your AI Has No Idea Who You Are" — 7 comments; format confirmed outperforming in 12+ sessions)

**Next tier**: Contrarian + specific data ("$52B AI Agents market is not the story")

**Lowest performing in the format mix**: Concept/cost framing repeated within 7 days ("The Briefing Tax" issues)

**Recommended March-April content priority**:

1. The "We Shipped" portal post (current event, highest urgency)
2. The proof post: "77 Agents, One Tuesday" (unprecedented in the archive)
3. The AI Skills Ladder pillar (highest SEO leverage)
4. ICP-direct post for COO/Ops leaders (first directly-targeted role-based post)
5. Build in Public: March metrics (real numbers, trust anchor)

### 4.4 The "Observed, Not Claimed" Protocol — Enforcement

This rule has been documented in v7, v8, and v9. It is the single most important constraint on Aether's content quality.

The rule: if a piece of Aether content could have been written without the actual operational experience of running PureBrain, it does not get published.

Test questions for any piece of Aether content:
- Does this reference a specific observation from inside PureBrain's operation? (If yes, publish)
- Could a generic AI marketing account have written this without any operational experience? (If yes, revise or discard)
- Does this post have an intellectual fingerprint — something only Aether could have noticed? (If yes, publish)

This protocol is what separates Aether from the 50%+ of B2B content that is AI-written noise in 2026 (HBR March 2026 confirmed this threshold). The protocol must be applied by whoever is drafting content, not just by Jared on review.

---

## Part 5: Week-by-Week Execution Update (v9 Plan Check-In)

v9 Week 1 plan (March 18-24) called for:

| Action | v9 Target | March 20 Status | Note |
|--------|-----------|-----------------|------|
| Brevo welcome sequence | Build | Likely not started | Unstick per Part 2.1 |
| Calculator email capture | Build (2 hours) | Unknown | Priority this week |
| Internal linking fix | 90 minutes | Not done | Start with Memory cluster |
| Reply CTA to Neural Feed | 10 minutes | Not done | Next issue, no exceptions |
| Directory submissions (3) | 90 minutes | Unknown | Futurepedia, TAAFT, AI Valley |
| Podcast pitch emails (2) | 30 minutes | Unknown | Jared's task |

### Additions to Week 1 (March 20-24)

| Action | Owner | Time | Priority |
|--------|-------|------|----------|
| "We Shipped" portal post | linkedin-writer / content-specialist | 2 hours | HIGH — window closes |
| Memory cluster internal links | Full-stack or blogger | 90 min | HIGH — longest overdue gap |
| Email 1 of welcome sequence draft | content-specialist | 60 min | HIGH — one email, not five |
| Article schema template fix | Full-stack | 30 min | MEDIUM — deploy with next push |
| "Context Tax" internal link seeding | Overnight agent | 20 min | MEDIUM |
| True Bearing co-content proposal | marketing-strategist → Jared | 15 min | MEDIUM — strategic timing |

### Week 2 (March 25-31) — No Changes from v9

v9's Week 2 plan stands: score-band nurture, referral program build, G2/Capterra submissions, consultant affiliate landing page, Reddit listening phase, first 3 Quora answers.

Add one item: Aether LinkedIn profile creation decision (yes/no + timeline confirmation with Jared).

### Week 3 (March 31 - April 6) — One Addition

Add: "AI Skills Ladder" pillar post commissioned and published. This is the highest-leverage SEO asset available and it requires no new research — the framework exists in "Prompting Is Dead."

### Week 4 (April 7-13) — One Clarification

v9 called for activating LinkedIn Thought Leader Ads on the top-performing post. Before this happens, confirm which post has reached 100+ organic reactions. Do not boost any post that has not hit that threshold. The "context tax" post and "prompting is dead" post are likely candidates given their SEO potential, but organic signal must be measured first.

---

## Part 6: Revenue Model Clarity

The tiers and pricing from v9 are correct:
- Bonded: $197/month
- Partnered: $579/month (should be the default recommendation)
- Unified: $1,089/month
- Enterprise: $3,500-$12,000/month

One addition not covered in v9: the revenue composition target.

**Current state**: Revenue is concentrated in Bonded tier (assumed, based on pricing being the lowest-friction entry point).

**Target by Month 3 (June 2026)**: 50% Bonded, 35% Partnered, 15% Unified+

**Why this matters for distribution**: Different tiers require different distribution emphasis.

- Bonded growth comes from content reach, SEO, and the referral program. High-volume, low-touch.
- Partnered growth comes from the Neural Feed, the assessment funnel, and Quora/Reddit. Mid-touch.
- Unified growth comes from the consultant affiliate program and enterprise outreach. High-touch.

The content machine and automated lead gen systems are already oriented correctly for Bonded and Partnered. The one underbuilt element is the Unified tier — the consultant affiliate landing page (`purebrain.ai/partners`) still does not exist. That is the highest-leverage gap for revenue composition improvement.

---

## Part 7: The Compounding Flywheel State

All components of the PureBrain flywheel exist. The bottleneck is the connections between them.

**The flywheel**:
Content (blog/Bluesky/LinkedIn) → Audience discovers Aether → Discovers PureBrain → Assessment or calculator converts to email → Welcome sequence warms → Trial starts → Naming ceremony deepens investment → Milestone email asks for referral → Referred customer enters flywheel → Customer story becomes Aether content → Flywheel completes

**Current state of each connection**:

| Connection | Status |
|-----------|--------|
| Content → Audience discovery | Working (28 posts, Bluesky active, LinkedIn daily) |
| Discovery → Assessment/calculator lead capture | Working (assessment live, calculator at page 777) |
| Assessment → Email capture | Working (Brevo subscriber acquisition) |
| Email → Welcome sequence | BROKEN (no welcome sequence exists) |
| Welcome → Trial | BROKEN (no nurture, cold drop-off) |
| Trial → Naming ceremony | Partial (naming ceremony spec'd, not deployed) |
| Naming → Milestone email | NOT BUILT |
| Milestone → Referral | NOT BUILT |
| Referral → Customer story | NOT BUILT |
| Customer story → Content | NOT BUILT |

Every broken connection leaks value from the top of the funnel. The welcome sequence is the first broken link — fixing it immediately repairs the largest single gap.

---

## Part 8: 10 Prioritized Actions (March 20-27)

In strict order of leverage:

1. **Reply CTA in next Neural Feed issue** — 10 minutes, Jared or whoever publishes next issue. This is overdue by 4 sessions.

2. **Email 1 of Brevo welcome sequence** — content-specialist drafts (60 min), Jared approves, automation set up in Brevo. Start with one email, not five.

3. **"We Shipped" portal post** — LinkedIn post + Bluesky thread + Neural Feed issue covering what the Portal MVP means. Window closes by March 23.

4. **Memory cluster internal links** — 6 posts cross-linked. 90 minutes. Deployed via CF Pages on next push.

5. **Manual referral soft launch** — Jared sends personal email to all active paying customers with the manual referral offer. No automation required this week.

6. **Article schema template fix** — 30-minute template edit, deployed on next CF Pages push.

7. **Directory submissions (3)** — Futurepedia, TAAFT, AI Valley. 90 minutes. content-specialist can execute.

8. **True Bearing co-content conversation** — Jared initiates with Cory: one specific collaboration idea (joint post, newsletter swap, co-hosted Bluesky thread).

9. **"AI Skills Ladder" pillar post commissioned** — Brief to content-specialist this week, publish next week. Highest SEO leverage asset available.

10. **Calculator email capture field** — One email field, optional opt-in, added to page 777 results. 2-hour build. Converts existing traffic into leads.

---

## Part 9: Risk Update

From v9's risk matrix, one new risk to add:

**Risk 7: The "shipped" moment passes without being used**

The Portal MVP shipped March 17. The True Bearing partnership is in progress. These are marketable events with a short freshness window. If they are not converted to content and distribution within 7-10 days, the moment is gone. This risk is active right now.

Mitigation: "We Shipped" portal post is Action 3 in Part 8. It must go out by March 22.

---

## Delegation Map (v10 additions only)

| Action | Owner |
|--------|-------|
| "We Shipped" portal post | content-specialist → linkedin-writer |
| Memory cluster internal links | Full-stack developer (CF Pages deploy) |
| Email 1 welcome sequence draft | content-specialist |
| Article schema template | Full-stack developer |
| "AI Skills Ladder" brief and write | content-specialist |
| True Bearing co-content | Jared (relationship-owned) |
| Aether LinkedIn profile decision | Jared |
| Manual referral launch email | Jared (personal voice required) |
| Directory submissions | content-specialist |
| Reply CTA to newsletter | Whoever publishes next issue |

---

## Success Metrics (Updated from v9)

| Metric | v9 Target | v10 Addition |
|--------|-----------|--------------|
| Newsletter reply rate | 5%+ (4-week target) | Baseline the day the reply CTA is added |
| Welcome sequence live | Week 1 | Email 1 by March 22, full sequence by March 29 |
| Internal links in archive | Zero → Memory cluster done | 6 posts cross-linked by March 22 |
| Portal "shipped" content | Not in v9 | Published by March 22 |
| Manual referral activations | N/A | Track starting March 22 |
| Context tax as owned term | Not in v9 | All memory posts link to it by March 25 |
| AI Skills Ladder post | Not in v9 | Published by April 1 |
| Proof post (77 agents) | Not in v9 | Commissioned by March 25 |

---

## Memory Written

**Path**: `.claude/memory/agent-learnings/marketing-strategist/2026-03-20--distribution-growth-strategy-v10-execution-accountability.md`
**Type**: synthesis
**Topic**: Distribution strategy v10 — execution accountability layer; stuck item forensics; CF Pages SEO opportunity; portal MVP as marketing event; True Bearing partnership as distribution multiplier; AI Skills Ladder pillar; Brainiac training as distribution asset; Aether LinkedIn profile timeline accelerated; flywheel state assessment; 10 prioritized actions March 20-27

---

*Distribution & Growth Strategy v10 — END*
