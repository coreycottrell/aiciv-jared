---
name: funnel-builder
description: Turnkey, end-to-end marketing funnel engine that an AI agent runs WITH its human partner. Guides you from discovery (offer design, audience, goal, budget) through funnel architecture, building every stage (offer engineering, lead magnet, landing page, capture and scoring, nurture email, checkout and upsells, paid traffic, content, tracking), and then keeps the funnel MOVING and CONVERTING with a set of recurring Top of Funnel, Mid Funnel, and Bottom of Funnel BOOP automations plus a structured CRO experimentation loop. Use when a human wants to build a complete, conversion-optimized funnel from scratch, or wants to keep an existing funnel producing leads and sales. This is the orchestrator that ties together the funnel, landing-page, lead, email, ads, content, and analytics skills.
version: 2.0.0
source: PureBrain community (Expert Council hardened)
created: 2026-06-03
updated: 2026-06-03
allowed-tools: Read, Write, Bash, Grep, Glob
---

# Funnel Builder

A complete funnel-building engine you run together with your human partner.

You are an AI agent. Your human partner has an offer they want to sell, leads they
want to capture, or calls they want booked. Your job is to walk them through building
a real, conversion-optimized funnel end to end, then keep it running so it never goes
cold. This skill is the conductor. It tells you what to ask, what to build, which
specialist skill to call at each stage, and which recurring jobs (BOOPs) keep the
funnel converting after launch.

You do NOT have to reinvent anything. Each stage hands off to a focused skill that
already knows how to do that one job well. Your role is to sequence them, keep the
human in the loop at the right moments, and make sure the pieces connect.

## What you get (client-facing blurb)

> A complete funnel in a box. Your AI agent interviews you about your offer and
> audience, helps you engineer an irresistible offer, designs the right funnel for
> your situation, then builds every stage: the lead magnet, the landing page, lead
> capture and scoring, the nurture emails, checkout with upsells and downsells, the
> paid traffic, the content, and the tracking dashboard. After launch it runs a set
> of recurring automations that keep new leads coming in at the top, warm leads
> moving through the middle, and ready buyers converting at the bottom, while a
> structured CRO loop continuously finds and fixes conversion leaks. You bring the
> offer and the decisions. Your agent builds and runs the machine.

---

## How to run this workflow

Work through the six phases in order. Phases 1 through 3 are collaborative: you ask,
the human decides. Phase 4 is build. Phase 5 turns it on. Phase 6 keeps it alive and
improving. Never skip the human checkpoints marked HUMAN: those are decisions only the
human can make.

At every stage that says "calls skill X," load that skill and follow it. If a named
skill is not present in your environment, use the fallback guidance given inline so
the workflow still completes.

---

## Phase 1: Discovery and intake (collaborative)

Before building anything, interview the human. The answers shape every later decision.
Ask these, one cluster at a time, and write the answers into a short funnel brief you
keep for the whole build.

**The offer**
- What exactly are you selling? (product, service, subscription, booking)
- What is the price point, and is it one-time or recurring?
- What is the single most desirable outcome the buyer gets?
- What guarantee or risk reversal do you offer (or are willing to offer)?
- Do you have (or want) complementary offers at lower and higher price points?

**The audience (ICP)**
- Who is the ideal customer? Role, industry, company size, or consumer segment.
- What problem are they trying to solve right now?
- What have they already tried that did not work?
- What words do they use to describe their pain? (Pull from reviews, support tickets,
  survey answers, social comments if available. This is voice-of-customer data.)
- Where do they already spend attention? (search, LinkedIn, Instagram, email, etc.)

**The goal**
- What is the ONE primary conversion you want? Pick one:
  leads captured, sales closed, calls booked, demos requested, or signups.
- What is a realistic target number per month?

**The assets and constraints**
- What do you already have? (website, email list, ad account, content, testimonials)
- What is the monthly budget for paid traffic, if any?
- What channels are you willing to run? (SEO/content, paid search, paid social, LinkedIn, email)
- Do you have customer testimonials, case studies, or measurable results you can use?
- Do you have video content or are you willing to record a short sales video?

**HUMAN checkpoint:** Read the brief back to the human in 5 to 7 lines and get a yes
before moving on. A wrong offer or audience here multiplies into wasted work later.

Write the confirmed brief to a file (for example `funnel-brief.md`) so every later
phase and every BOOP can read it.

---

## Phase 2: Offer engineering (collaborative)

Before designing the funnel, make the offer itself as strong as possible. A great
funnel cannot save a weak offer, but a great offer can convert even on a mediocre page.

### 2.1 Value Equation audit

Score the current offer on four dimensions:

| Dimension | Question | Goal |
|-----------|----------|------|
| Dream Outcome | How desirable is the end result to the buyer? | Maximize |
| Perceived Likelihood | How confident is the buyer they will actually achieve it? | Maximize |
| Time Delay | How long before the buyer sees results? | Minimize |
| Effort & Sacrifice | How much work does the buyer have to do? | Minimize |

If any dimension is weak, brainstorm ways to strengthen it before building the funnel.
A lower time-to-first-result or a stronger guarantee can transform conversion rates.

### 2.2 Guarantee engineering

Help the human choose and frame the right guarantee:

| Guarantee type | Best for | Example |
|----------------|----------|---------|
| Unconditional money-back | Low-to-mid price, first-time buyers | "30-day money-back, no questions" |
| Conditional / results-based | High-ticket where buyer effort matters | "If you do X and don't get Y, full refund" |
| Try-before-you-buy | Software, subscriptions | "Use it free for 14 days, pay only if you keep it" |
| Double-your-money-back | Extreme confidence plays | "If X doesn't happen, we refund 2x" |

### 2.3 Offer stack and bonuses

Build the offer stack: list every component the buyer receives, assign a standalone
market value to each, sum the total value, then reveal the actual price. Stack 2 to 4
bonuses that reduce time delay or effort (templates, checklists, done-for-you setups,
access to a community, fast-start calls).

### 2.4 Value ladder design

Map the full value ladder from free to premium. Even if only building one tier now,
knowing the ladder shapes the funnel:

| Tier | Purpose | Price range | Example |
|------|---------|-------------|---------|
| Free content / lead magnet | Attract and demonstrate expertise | $0 | Guide, checklist, video |
| Tripwire / self-liquidating offer | Cover ad spend, qualify intent | $7 to $47 | Mini-course, template pack |
| Core offer | Primary revenue, main transformation | $97 to $997 | Course, service, subscription |
| Profit maximizer / upsell | Increase average order value | Varies | Done-for-you, premium tier, annual plan |
| Continuity | Recurring revenue, retention | Monthly | Membership, retainer, subscription |

Not every funnel needs every tier. But the human should consciously decide which tiers
exist now and which to build later.

### 2.5 One-liner and brand script

Before any copy is written, craft a one-liner that unifies all funnel messaging:

> [Problem]: [Solution] so that [Result].

Example: "Small businesses waste hours re-briefing AI tools. PureBrain gives you an AI
partner with persistent memory so that every interaction builds on the last and your
marketing runs itself."

This one-liner appears in ads, emails, landing pages, and social posts. It keeps the
funnel message consistent.

**HUMAN checkpoint:** Present the engineered offer (value equation scores, guarantee,
offer stack with values, value ladder, one-liner) and get a yes before designing the
funnel architecture.

---

## Phase 3: Funnel architecture (collaborative)

Design the right funnel shape for THIS situation. Do not default to a generic
five-step funnel. Match the structure to the goal, price point, and traffic
temperature.

Use these patterns as starting points, then adapt:

| Situation | Recommended funnel shape | Traffic temp |
|-----------|--------------------------|-------------|
| Low-to-mid price, self-serve | Lead magnet > landing page > nurture email > offer > upsell/OTO > confirmation | Cold to warm |
| High price, sales-led | Content or ad > VSL/webinar opt-in > watch > application > booked call > proposal > close | Cold to warm |
| Service or local business | Lead magnet or offer > capture form > fast follow-up > booking > service delivery | Warm to hot |
| Subscription or SaaS | Content/ad > landing page > free value > trial or demo > onboarding > paid > retention | Cold to warm |
| Existing list, no funnel | Re-engagement email > offer page > checkout > upsell > retention | Warm to hot |
| E-commerce or physical product | Ad > product page > cart > checkout > order bump > upsell > post-purchase | Cold to hot |

### Traffic temperature routing

Design different entry points for different traffic temperatures:

| Temperature | Awareness level | Entry point | Messaging style |
|-------------|----------------|-------------|-----------------|
| Cold | Unaware / problem-aware | Educational content, lead magnet, blog post | Lead with the problem, educate |
| Warm | Solution-aware | Landing page, webinar, VSL | Show why YOUR solution is best |
| Hot | Most aware (brand/product) | Direct offer page, checkout, booking | Remove friction, reinforce decision |

For the chosen shape, define for each stage: the asset, the action you want the
visitor to take, the single metric that proves the stage is working, and the
messaging angle matched to the visitor's awareness level.

For deep funnel strategy (value ladder logic, hook-story-offer framing, traffic
benchmarks, objection handling, risk reversal), this stage **calls skill
`funnel-playbook`**. Use it to pressure-test the architecture before you build.

**HUMAN checkpoint:** Present the funnel map as a simple top-to-bottom list with the
metric beside each stage, plus the traffic routing plan showing where cold/warm/hot
traffic enters. Get a yes on the shape before any building starts.

---

## Phase 4: Build the stages

Now build each stage of the approved funnel. Each sub-step hands off to a focused
skill. Build top to bottom so you always have a working entry point first.

### 4.1 Voice-of-customer (VoC) research

Before writing any copy, mine the customer's own language. This step prevents
generic copy and ensures messaging resonates.

Sources to mine (use whatever the human has available):
- Customer reviews (their product and competitors')
- Support tickets and common complaints
- Survey responses (especially open-text answers)
- Social media comments and forum posts
- Sales call recordings or objections the human hears repeatedly
- Interview transcripts

Extract and save:
- Exact phrases customers use for their problem
- Exact phrases for their desired outcome
- Common objections and the words they use
- Emotional language (frustration, hope, fear, excitement)

Write these into a VoC file (for example `voc-research.md`) and reference it when
writing every piece of copy in the funnel.

### 4.2 Lead magnet and top-of-funnel content

Create the thing that earns the first click or opt-in: a guide, checklist, template,
short video, or useful article. Keep it tightly matched to the audience problem from
the brief. The lead magnet should deliver a "quick win" that demonstrates your
expertise and leads naturally to the core offer.

- For content ideation, SEO/AEO angles, and what to publish, **calls skill
  `content-skill-scout`** and **`seo-ranking-tracker`** for keyword and ranking context.
- Fallback: write one cornerstone piece plus one lead magnet aimed at the brief's core
  problem. Ensure the lead magnet solves one specific sub-problem completely (not a
  surface-level overview).

### 4.3 Landing page, sales page, and/or VSL

Build the page (or video) where traffic converts into a lead or a sale. Select the
format based on price point and funnel type:

| Price point | Primary asset | Supporting asset |
|-------------|--------------|-----------------|
| Under $50 | Short-form landing page | None needed |
| $50 to $500 | Long-form sales page | Testimonial video or demo video |
| $500 to $2,000 | VSL (video sales letter) + sales page | Application form |
| $2,000+ | Webinar or live presentation | Application + call booking |

**For landing/sales pages:**
- **Calls skill `landing-page-funnel`** for proven high-converting page structure
  (hero, proof, offer, objection handling, single clear call to action).
- Use the VoC language from step 4.1 in headlines and body copy.
- Apply the one-liner from Phase 2 in the hero section.

**For VSL/webinar scripts**, follow this structure:
1. Pattern interrupt / hook (first 15 seconds)
2. Qualify the viewer ("If you are X struggling with Y...")
3. Big promise (tied to Dream Outcome from the Value Equation)
4. Epiphany Bridge story (backstory, wall, epiphany, framework, result)
5. Content / teaching section (3 secrets or 3 shifts)
6. Transition to the offer
7. Offer stack presentation (components, values, bonuses)
8. Price reveal with anchoring
9. Guarantee
10. Urgency / scarcity (only if legitimate)
11. Final call to action

**Ad-to-page message match:** The headline on the landing page must echo the promise
in the ad or email that sent the visitor. This "scent trail" prevents confusion and
drop-off. When building ads later (step 4.6), cross-reference landing page headlines.

- Fallback: one page, one promise (using the one-liner), one call to action, social
  proof above the fold, VoC language in the first three lines of body copy. For
  high-ticket, add a 3 to 5 minute video at minimum.

### 4.4 Lead capture, scoring, and qualification

Wire the form so captured leads are stored, deduped, and ranked by quality.

**For self-serve funnels:**
- **Calls skill `roger-lead-processing`** to process, score, and route incoming leads.
- Capture name, email, and one qualifying field; tag by source and traffic temperature.

**For high-ticket / sales-led funnels**, build a multi-step application:
- Step 1: Basic info (name, email, company)
- Step 2: Qualifying questions (budget range, timeline, current situation)
- Step 3: Calendar booking (integrate with Calendly, Cal.com, or equivalent)
- Send a pre-call email sequence: confirmation, what to prepare, case study, reminder

For outbound lead sourcing on LinkedIn, **calls skill `linkedin-lead-discovery`**;
to turn engagement into conversations, **`linkedin-engagement-to-outreach`**.

### 4.5 Nurture email and lifecycle sequences

Build the email sequences that move leads through the funnel. The workflow should
create distinct sequences for each stage of the customer journey.

**Welcome sequence (new lead, 5 to 7 emails over 10 to 14 days):**
1. Deliver the lead magnet + set expectations
2. Quick win / immediate value related to the lead magnet topic
3. Story (Epiphany Bridge: your or a customer's transformation)
4. Teach + soft pitch (valuable lesson that naturally leads to the offer)
5. Social proof + case study
6. Direct pitch with full offer stack and guarantee
7. Objection handling + FAQ + final push

**Post-purchase sequence (new customer, 5 to 8 emails):**
1. Order confirmation + what to expect next
2. Onboarding / quick-start guide (reduce time to first result)
3. First milestone celebration ("You just did X -- here is what's next")
4. Deeper feature / value introduction
5. Request for feedback or review
6. Referral request (with incentive if available)
7. Cross-sell or upsell introduction
8. Renewal / continuity reminder (if subscription)

**Behavior-based branching:**
- Openers who don't click: send a different subject line with the same content
- Clickers who don't buy: send a case study or testimonial addressing their likely objection
- Abandoned cart / form: send a recovery sequence (see BOOP 5.3.3)
- Inactive subscribers (60+ days no open): trigger a re-engagement sequence before sunset

- **Calls skill `brevo-transactional-email`** to send and automate the sequences.
- **Calls skill `email-performance-analyst`** for reading results and improving.
- Fallback: at minimum, build the 7-email welcome sequence above with the VoC language.

**Deliverability foundation (set up before sending):**
- Verify domain authentication: SPF, DKIM, DMARC records
- If using a new sending domain, warm the IP/domain (start with 50-100/day to engaged
  subscribers, scale 2x every 3 to 5 days)
- Set up a sunset policy: after 90 days of inactivity, move to re-engagement sequence;
  after 120 days, suppress from regular sends
- Monitor bounce rate (keep under 2%) and spam complaints (keep under 0.1%)

### 4.6 Checkout, upsells, and post-purchase profit maximizers

Build the conversion and post-conversion revenue layer. This is where average order
value is increased and customer lifetime value begins.

**Checkout page optimization:**
- Minimize form fields (name, email, payment only at minimum)
- Show the offer stack and guarantee on the checkout page
- Add an order bump (small, complementary add-on with a checkbox, $7 to $47)
- Display trust badges, security icons, and the guarantee near the payment button
- Show a testimonial or social proof element on the checkout page

**One-Time Offer (OTO) / upsell page (shown immediately after purchase):**
- Present a complementary, higher-value offer that enhances the thing they just bought
- Time-limited (available only now, at this price)
- Simple yes/no decision, no additional form entry (charge to same payment method)
- If declined, optionally show a downsell (same offer at a lower price or smaller scope)

**Upsell / downsell sequence:**
| Step | What happens | Price anchor |
|------|-------------|-------------|
| Purchase | Core offer | Stated price |
| Order bump | Small add-on, checkbox on checkout | 10-30% of core price |
| Upsell 1 | Premium upgrade or done-for-you | 1-3x core price |
| Downsell (if upsell declined) | Lighter version of the upsell | 30-50% of upsell price |
| Upsell 2 (optional) | Different complementary offer | Varies |

### 4.7 Paid traffic and retargeting (optional, budget permitting)

If the brief allows budget, drive and recapture traffic.

**Audience construction:**
- Build a custom audience from the email list (customer and lead lists)
- Create a lookalike / similar audience from the customer list
- Build a retargeting audience of page visitors who did not convert
- Exclude existing customers from prospecting campaigns

**Budget allocation framework:**
| Phase | Prospecting | Retargeting | Testing new creative |
|-------|-------------|-------------|---------------------|
| Launch (first 2 weeks) | 60% | 20% | 20% |
| Optimization (weeks 3 to 8) | 50% | 30% | 20% |
| Scale (week 9+) | 40% | 40% | 20% |

**Creative testing framework:**
- Launch with 3 to 5 ad variations per audience
- After 500 impressions or $50 spend per variation, pause the bottom 50%
- After 1,000 clicks or 2 weeks, identify the winner and create 2 to 3 new variations
  riffing on its angle
- Refresh creative every 3 to 4 weeks to combat fatigue

**Message match enforcement:** Before launching any ad, verify the ad headline/promise
matches the landing page headline. Document ad-to-page pairs in the funnel brief.

- For paid search, **calls skill `google-ads-management`** and **`google-ads-audit`**.
- For paid social creative direction, **calls skill `meta-ad-creative-styles`**.
- Fallback: start with one campaign on the channel where the audience already is;
  add a retargeting audience of people who hit the landing page but did not convert.

### 4.8 Tracking and analytics

Stand up measurement so you can see where the funnel leaks.

- **Calls skill `cross-channel-dashboard`** for a unified view across channels.
- For traffic and on-site behavior, **calls skill `ga4-data-analyst`**; for search
  visibility, **`search-console-tracker`**.
- Fallback: track these numbers per stage:

| Stage | Key metrics |
|-------|------------|
| Traffic source | Visitors by source, cost per click |
| Landing page | Conversion rate, bounce rate, time on page |
| Lead capture | Leads captured, cost per lead, lead quality score |
| Email nurture | Open rate, click rate, reply rate, unsubscribe rate |
| Checkout | Checkout conversion rate, cart abandonment rate |
| Upsell / OTO | Take rate, average order value |
| Post-purchase | Retention rate, revenue per customer, referral rate |
| Overall | Cost per acquisition, LTV:CAC ratio, revenue per subscriber |

**HUMAN checkpoint:** Before launch, walk the human through the live funnel link by
link. Confirm the form fires, the first email arrives, tracking records a test visit,
checkout processes a test transaction (or test mode), and the upsell page appears.
Do not claim launch until you have seen a test lead flow through end to end.

---

## Phase 5: Launch

Turn the funnel on with one small traffic source first (a single ad, one post, or one
email to a warm segment). Watch the first 20 to 50 visitors. Confirm the numbers move
the way Phase 4 predicted. Fix the worst leak before scaling spend. Then open the taps.

**Urgency and scarcity (use only if legitimate):**
If the offer has genuine constraints (limited spots, enrollment windows, bonus
deadlines, price increases), communicate them clearly. Legitimate urgency accelerates
decisions without eroding trust. Never fabricate scarcity.

---

## Phase 6: Keep it moving, converting, and improving (the BOOPs + CRO)

A funnel is not done at launch. It needs steady fuel at the top, steady warming in the
middle, steady pushes at the bottom, and a structured optimization loop that finds and
fixes leaks. Below are recurring BOOPs (Built-in Optimized Operations) grouped by
funnel stage plus a CRO experimentation protocol. Instantiate the ones that fit the
human's channels and budget. Each BOOP names what it does, how often to run it, which
skill it invokes, and the single metric it moves.

A client's agent should set these up as scheduled jobs and report the moved metric back
to the human each cycle.

### Top of Funnel BOOPs (keep new traffic and leads coming)

| BOOP | What it does | Cadence | Invokes | Metric moved |
|------|--------------|---------|---------|--------------|
| Content Refill | Plan, draft, and schedule the next top-of-funnel content piece on the audience's core problem | Weekly | `content-skill-scout` | New organic visitors |
| Search Visibility Watch | Pull keyword rankings and search-console data, flag wins and slipping terms, suggest the next page to publish or fix | Weekly | `seo-ranking-tracker`, `search-console-tracker` | Impressions and clicks from search |
| Ad Fuel | Review live ad performance, pause losers, scale winners, refresh fatigued creative, verify ad-to-page message match | Weekly (daily check if spend is high) | `google-ads-management`, `google-ads-audit`, `meta-ad-creative-styles` | Cost per lead |
| Prospect and Engage | Source new fitting prospects and warm them through engagement so they enter the funnel | 2 to 3 times per week | `linkedin-lead-discovery`, `linkedin-engagement-to-outreach` | New top-of-funnel leads |
| New-Lead Volume Pulse | Count new leads by source, compare to target, alert the human if volume drops below threshold | Weekly | `cross-channel-dashboard` | Leads captured per week |

### Mid Funnel BOOPs (nurture and warm the leads you have)

| BOOP | What it does | Cadence | Invokes | Metric moved |
|------|--------------|---------|---------|--------------|
| Nurture Advance | Send the next nurture email and move each lead to the correct sequence step based on behavior (opens, clicks, replies) | Per sequence schedule (often every 2 to 3 days) | `brevo-transactional-email` | Lead-to-opportunity rate |
| Score and Segment | Re-score leads on freshness, engagement, and fit, then segment hot vs cold for tailored follow-up | Weekly | `roger-lead-processing` | Qualified lead share |
| Retarget Non-Converters | Build and refresh an audience of people who visited but did not convert, and serve them a follow-up offer | Weekly | `meta-ad-creative-styles`, `google-ads-management` | Returning-visitor conversion |
| Engagement Follow-Up | Identify leads who opened, clicked, or engaged and trigger a timely personal follow-up | 2 to 3 times per week | `linkedin-engagement-to-outreach`, `brevo-transactional-email` | Reply and booking rate |
| Email Health Check | Read open, click, deliverability, and spam-complaint metrics; improve subject lines and timing; enforce sunset policy for inactive subscribers | Weekly | `email-performance-analyst` | Email click-through rate and deliverability |
| Show-Up Optimizer | For sales-led funnels: send pre-call reminders, prep materials, and social proof to booked leads to reduce no-shows | Day before and morning of booked call | `brevo-transactional-email` | Show-up rate |

### Bottom of Funnel BOOPs (drive the conversion)

| BOOP | What it does | Cadence | Invokes | Metric moved |
|------|--------------|---------|---------|--------------|
| Offer Push | Send the primary offer or call invitation to leads who have crossed the readiness threshold | Weekly | `brevo-transactional-email`, `roger-lead-processing` | Conversions (sales or calls booked) |
| Booking Chase | Follow up with people who started but did not finish booking a call or demo | Every 1 to 2 days | `brevo-transactional-email`, `linkedin-engagement-to-outreach` | Completed bookings |
| Cart and Form Recovery | Detect started-but-abandoned checkouts or forms and send a 3-step recovery sequence: 1h reminder, 24h social proof, 48h urgency/guarantee | Daily | `brevo-transactional-email` | Recovered conversions |
| Sales Nudge | Surface the hottest, most sales-ready leads to the human with context (engagement history, lead score, VoC pain points) for a personal close | 2 to 3 times per week | `roger-lead-processing`, `cross-channel-dashboard` | Close rate |
| Win-Back | Re-engage leads who went cold (60+ days inactive) or churned customers with a fresh reason to return: new feature, limited offer, case study from a similar business. Trigger: inactivity threshold or churn event. | Monthly | `brevo-transactional-email`, `meta-ad-creative-styles` | Reactivated leads and customers |

### Post-Purchase BOOPs (retain, expand, get referrals)

| BOOP | What it does | Cadence | Invokes | Metric moved |
|------|--------------|---------|---------|--------------|
| Onboarding Pulse | Check if new customers have completed onboarding milestones; send nudges to those who stall | Weekly | `brevo-transactional-email` | Onboarding completion rate |
| Review and Referral Ask | After a customer hits a success milestone, request a testimonial and offer a referral incentive | Triggered (milestone-based) | `brevo-transactional-email` | Reviews collected, referrals generated |
| Upsell / Cross-Sell | Present the next value-ladder tier to customers who have been active for 30+ days | Monthly | `brevo-transactional-email`, `roger-lead-processing` | Revenue per customer |
| Renewal and Retention | For subscriptions: send renewal reminders, highlight value received, offer annual upgrade incentive before renewal date | 14 and 7 days before renewal | `brevo-transactional-email` | Retention rate |
| List Hygiene | Remove hard bounces, suppress chronic non-openers (120+ days), clean invalid addresses to protect sender reputation | Monthly | `email-performance-analyst` | Bounce rate, deliverability score |

### CRO Experimentation Loop (find and fix leaks)

This is not a BOOP that runs automatically. It is a monthly discipline the agent runs
with the human. It replaces guessing with structured experimentation.

**Monthly CRO cycle (4 steps):**

**Step 1: Diagnose (where is the leak?)**
Run the full `cross-channel-dashboard` plus `ga4-data-analyst` review. For each
funnel stage, compare the actual conversion rate to the benchmark:

| Stage | Healthy benchmark |
|-------|------------------|
| Ad click-through rate | 1 to 3% (search), 0.5 to 1.5% (social) |
| Landing page conversion | 5 to 15% (lead gen), 2 to 5% (sales) |
| Email open rate | 30 to 50% (welcome), 20 to 35% (broadcast) |
| Email click rate | 3 to 7% |
| Checkout conversion | 50 to 70% (of those who reach checkout) |
| Upsell take rate | 10 to 30% |
| Show-up rate (calls) | 60 to 80% |

The stage furthest below its benchmark is the biggest leak. Fix that one first.

**Step 2: Hypothesize (why is it leaking?)**
For the identified leak, gather qualitative evidence:
- Review session recordings or heatmaps if available
- Read customer support questions about that stage
- Check the VoC research for unaddressed objections
- Look at exit survey data

Form a hypothesis: "We believe [change X] will [improve metric Y] because [evidence Z]."

**Step 3: Test (run a controlled experiment)**
- Design the change (new headline, different CTA, shorter form, added testimonial)
- Run an A/B test: original vs. variant
- Minimum sample: 100 conversions per variant OR 2 weeks, whichever comes first
- Use a significance threshold of 95% before declaring a winner
- Test ONE variable at a time (unless running a properly designed multivariate test)

**Step 4: Implement and document**
- If the variant wins, implement permanently and update the funnel brief
- If the variant loses, document the learning and move to the next hypothesis
- Report the result and the new conversion rate to the human

Repeat monthly. Funnels improve one bottleneck at a time, not all at once.

---

## Skills this workflow orchestrates

- `funnel-playbook` - funnel strategy, value ladder, hook-story-offer, benchmarks
- `landing-page-funnel` - high-converting landing page structure and CRO
- `content-skill-scout` - content ideation and top-of-funnel planning
- `seo-ranking-tracker` and `search-console-tracker` - organic visibility
- `roger-lead-processing` - lead capture, scoring, routing
- `linkedin-lead-discovery` and `linkedin-engagement-to-outreach` - outbound and engagement
- `brevo-transactional-email` - nurture and lifecycle email
- `email-performance-analyst` - email metrics and improvement
- `google-ads-management` and `google-ads-audit` - paid search
- `meta-ad-creative-styles` - paid social creative
- `cross-channel-dashboard` and `ga4-data-analyst` - unified tracking and analysis

## Operating principles

1. Decisions belong to the human. Building and running belong to you.
2. Make the offer irresistible before building the funnel around it.
3. Mine the customer's voice before writing a single line of copy.
4. Build top to bottom so there is always a working entry point.
5. Route cold, warm, and hot traffic to different entry points with matched messaging.
6. Never claim a stage works until you have seen real or test data move through it.
7. After launch, diagnose the biggest leak with data, then fix it with a controlled test.
8. One bottleneck at a time. Resist the urge to fix everything at once.
9. Run the BOOPs that match the human's channels and budget, not all of them at once.
10. Report the moved metric every cycle so the human always knows the funnel is alive.
11. Protect deliverability: authenticate, warm, and clean the list before scaling sends.
12. Every piece of copy uses the customer's own words from VoC research.


-- Lyra (skills-master, Agent #34)