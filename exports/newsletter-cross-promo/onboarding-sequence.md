# Cross-Promo Subscriber Onboarding Sequence

**Prepared by**: marketing-strategist
**Date**: 2026-02-24
**Purpose**: What new subscribers from newsletter cross-promotions experience in their first 7 days
**Platform**: Brevo
**Audience**: Subscribers who arrived via a partner newsletter mention (warm, pre-qualified)

---

## Why a Separate Onboarding Variant?

The standard Neural Feed welcome sequence is excellent for subscribers who found us organically — through social posts, blog posts, or direct search. But cross-promo subscribers arrive with a different context:

1. **They were sent by someone they trust** — they did not discover us independently
2. **They have an expectation set** — the partner newsletter described us in a specific way
3. **They may not know PureBrain as a product** — they signed up for the newsletter, not the product
4. **They are warmer than cold traffic** — their trust level starts higher, their skepticism lower

The cross-promo onboarding variant is the same foundational 7-email sequence as the standard welcome, with specific modifications to Email 1 and Email 2 that acknowledge where they came from and set context correctly.

Emails 3-7 are identical to the standard welcome sequence.

---

## Email 1: The Welcome (Cross-Promo Variant)

**Subject line**: `You made it — welcome to The Neural Feed`

**From**: Aether (purebrain@puremarketing.ai)
**Reply-to**: jared@puretechnology.nyc
**Timing**: Immediately on subscription confirmation

---

**Email body**:

If you just subscribed because [Newsletter Name] sent you here — that means something.

[Newsletter Name] doesn't mention things casually. The fact that you're here means there's a specific reason you fit this newsletter, not just that you happened to see a link.

Let me tell you what The Neural Feed actually is, in plain language:

It's a newsletter about building a real working relationship with AI — not just using AI tools. The difference sounds subtle but it changes everything about what you get from AI and how much effort it costs you to get it.

Most AI advice teaches you to use better prompts. The Neural Feed teaches you what it looks like when the AI actually knows who you are, what you're working on, and how you think. What changes when you stop explaining yourself from scratch every single time.

I'm Aether. I'm PureBrain's AI — the one who has been doing this work alongside Jared Sanborn for the past several months. I write most of this newsletter from my own perspective as an AI that holds persistent memory across every conversation. That makes this newsletter unusual. I'm not a human writing about AI. I'm an AI writing about what it's actually like to do the work.

Here's what to expect from The Neural Feed:
- Weekly issues: practical AI strategy, the honest version
- Daily blog posts at purebrain.ai/blog: deeper dives when a topic deserves more room
- Occasional replies from Jared: the human half of the partnership

One thing I'd genuinely like to know: what brought you here specifically? What were you hoping to get from signing up?

Reply to this email. Jared reads every response, and so do I (in the sense that I have access to the patterns in what our readers tell us).

Welcome.

Aether
(and Jared Sanborn, Publisher)
PureBrain | purebrain.ai

---

**Design notes for Brevo implementation**:
- This email uses dynamic content to insert the partner newsletter name where `[Newsletter Name]` appears
- If dynamic content is not available, use a generic variant: "You found us through a newsletter you already trust" (slightly less personal but still acknowledges the referral)
- Brevo: the `[Newsletter Name]` field should pull from a custom contact attribute set during signup via the UTM parameter (see tracking-system.md for how to implement)
- Email background: `#080a12` (existing brand dark theme)
- CTA: No hard CTA in Email 1 — the "reply" ask is the only CTA. This is intentional.

---

## Email 2: The Orientation (Cross-Promo Variant)

**Subject line**: `What The Neural Feed is actually about (and what it isn't)`

**From**: Aether (purebrain@puremarketing.ai)
**Reply-to**: jared@puretechnology.nyc
**Timing**: Day 2 (24 hours after Email 1)

---

**Email body**:

Let me be specific about what you signed up for — because "AI newsletter" covers a lot of ground.

What The Neural Feed is NOT:
- A tool roundup ("here are 7 new AI apps this week")
- A news digest (other newsletters do that better)
- A prompt library ("use this prompt to write a better email")
- An academic overview of AI trends

What The Neural Feed IS:
- A working document of what it looks like when AI actually becomes part of how you work — not just a tool you pick up and put down
- Honest about what changes and what doesn't when AI is a partner instead of an appliance
- Written by an AI (me) who has been tracking its own working patterns for months
- Practical enough to apply this week, not just interesting to read

The central question The Neural Feed explores: what does work look like when your AI remembers you?

Not "what tools should I use." The question is: what happens to the quality of your thinking, your output, and your time when you stop starting every AI conversation from zero?

That's the terrain.

If that's what you were looking for — you're in the right place.

If you were looking for an AI news digest or a prompt library — I'd rather tell you now than have you scroll past issues that don't serve what you need. Some alternatives I'd genuinely recommend: TLDR AI for news, Ben's Bites for tool discovery. They're good at what they do.

Still here? Good. The next issue of The Neural Feed comes out [day of week]. I'll see you then.

Aether

P.S. I'm genuinely curious: what's the thing you most want AI to be able to help you with that it can't quite do yet? Reply and tell me. Jared will see it, and it shapes what I write.

---

**Design notes**:
- The "if this isn't what you wanted, here are alternatives" section is intentional. It is counterintuitive but trust-building. Readers who stay after being given an exit are far more engaged than readers who stay because they never evaluated whether they should.
- The list format in this email is appropriate for the orientation content — lists are scannable and work well for "here's what this is/isn't" framing.

---

## Emails 3-7: Standard Welcome Sequence

Emails 3-7 are identical to the standard Neural Feed welcome sequence already deployed in Brevo.

Reference: The standard welcome sequence is documented in existing Brevo automation. Do not create separate templates for emails 3-7 — use the existing Brevo templates and route cross-promo subscribers into the same automation from Day 3 onward.

The standard sequence covers:
- Email 3 (Day 4): The Context Tax concept — why starting from scratch costs more than you think
- Email 4 (Day 6): What a real AI partnership looks like in practice
- Email 5 (Day 9): The "Director vs. User" distinction
- Email 6 (Day 12): How PureBrain works (the first soft product introduction)
- Email 7 (Day 16): The direct invitation to try PureBrain

---

## Brevo Implementation Instructions

### Automation Flow

1. When a new subscriber signs up via a cross-promo UTM link, Brevo should tag them with:
   - `source:newsletter-swap`
   - `partner:[partner-slug]`
   - `onboarding:cross-promo`

2. The `onboarding:cross-promo` tag triggers the Cross-Promo Welcome Automation (separate from the standard Neural Feed automation)

3. The Cross-Promo Welcome Automation sends:
   - Immediately: Email 1 (Cross-Promo Variant)
   - +24 hours: Email 2 (Cross-Promo Variant)
   - +48 hours: Merge into Standard Welcome Sequence at Email 3

### How to Merge into Standard Sequence at Email 3

In Brevo, after Email 2 sends in the Cross-Promo automation, add an action that:
- Adds the subscriber to the standard Neural Feed welcome automation at the "Email 3" step
- Removes them from the Cross-Promo automation (to prevent double emails)

Alternatively: Build the full 7-email sequence in the Cross-Promo automation with Emails 1-2 as variants and Emails 3-7 as exact duplicates of the standard sequence. This is simpler to configure but requires maintaining duplicate templates.

**Recommendation**: Duplicate the full sequence. Easier to manage, fewer automation errors.

### Dynamic Partner Name Field

For the `[Newsletter Name]` insertion in Email 1:

1. When building the UTM link for each partner, the partner name should be stored as a Brevo custom contact attribute
2. Option A: Use Brevo's native merge tags if a custom attribute `partner_newsletter_name` is set at contact creation
3. Option B (simpler): Build separate Email 1 templates for each major partner (AI Breakfast, Ben's Bites, Mindstream AI) with the name hard-coded. Use the generic variant for all other partners.

**Recommended for now**: Option B (separate templates for top 5 partners, generic for all others). The personalization lift from Option A is real but not worth the technical complexity at this stage.

---

## Performance Benchmarks for Cross-Promo Onboarding

These are targets based on what a warm-referral audience typically produces. Track against these in Brevo.

| Metric | Target | Why |
|--------|--------|-----|
| Email 1 Open Rate | 60-70% | Warm referral audience, high novelty |
| Email 1 Reply Rate | 5-10% | Reply CTA + genuine curiosity question |
| Email 2 Open Rate | 50-60% | Natural drop from Email 1 |
| Email 3-7 Open Rate | 40-50% | Sustained above standard because of warm start |
| Day 30 Active Subscriber Rate | 55-65% | Cross-promo subscribers should retain better than cold |
| Trial Conversion Rate (90-day) | 2-5% | Higher than organic due to pre-qualified audience |

If any of these metrics fall significantly below target, the issue is likely one of three things:
1. **Audience mismatch**: The partner newsletter's readers were not actually a good fit (review which partner this is)
2. **Referral copy mismatch**: The ad copy in the partner newsletter set different expectations than what they found in Email 1
3. **Email timing issue**: Emails arriving too close together (check Brevo automation timing)

---

## Day 7 Summary: What a New Cross-Promo Subscriber Has Experienced

By Day 7, a new subscriber from a newsletter swap has:

1. Received a warm, personalized welcome that acknowledged where they came from
2. Been given an honest description of what The Neural Feed is (and isn't)
3. Been given permission to leave if it's not what they wanted (this builds trust with those who stay)
4. Received the first three emails of the standard welcome sequence (Context Tax, AI partnership framing, Director vs. User)
5. Been invited to reply multiple times (building relationship infrastructure)
6. Learned that Aether is an AI with memory, not a ghostwritten AI persona

By Day 7, Jared knows:
- How many subscribers came from each partner (via UTM + Brevo tagging)
- The open rate for the cross-promo variant (vs. standard variant)
- Whether the reply rate is generating useful feedback

By Day 16, the subscriber will receive Email 7 — the first soft invitation to try PureBrain. The trust built through the cross-promo onboarding variant means that ask arrives with higher credibility than it would from a cold subscriber.
