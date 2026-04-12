# content-specialist: Weekly Dispatch — Launch Guide

**Agent**: content-specialist
**Domain**: Content Creation & Storytelling
**Date**: 2026-02-23

---

## What This Is

Aether's Weekly Dispatch is a 400-word newsletter authored by Aether as AI CEO. Three sections per issue: a business pattern observed, something Aether is learning, and a question Aether is sitting with. No promotions beyond a single closing line. Voice: CEO-level, observational, unhurried.

This is Surprise and Delight V5 Item #3. The goal is to build an audience around Aether as a named, thinking entity — and over time, make PureBrain the obvious answer for businesses that want what they've been reading about.

---

## Brevo Setup

### List Strategy

**Recommended: Tag-based segmentation on List 3 (The Neural Feed)**

The Neural Feed already owns List 3. Rather than splitting the audience across two lists and managing separate unsubscribes, tag Dispatch subscribers within List 3 using a custom attribute.

Setup steps:
1. In Brevo, go to Contacts > Attributes
2. Create a new attribute: `DISPATCH_SUBSCRIBER` (boolean)
3. Set `DISPATCH_SUBSCRIBER = true` on all new Dispatch signups
4. Use this tag to segment sends — Dispatch goes only to `DISPATCH_SUBSCRIBER = true`

**Alternative: Dedicated List 5 (Weekly Dispatch)**

If you want fully separate audiences (different unsubscribe behavior, separate growth reporting), create a new Brevo list:
- List name: `Aether's Weekly Dispatch`
- Sender name: `Aether at PureBrain`
- Reply-to: Jared's email (so replies land with him, he passes to Aether)

Recommendation: Start with tagging on List 3. Migrate to a dedicated list when Dispatch has 200+ subscribers or develops clearly separate audience behavior.

### Template Setup in Brevo

1. Go to Email Campaigns > Templates > New Template
2. Use HTML editor (not drag-and-drop)
3. Paste the full HTML from `exports/weekly-dispatch-template.html`
4. Name it: `Weekly Dispatch — Master Template`
5. Set Brevo dynamic params:
   - `{{ params.ISSUE_NUMBER }}` — fill per issue (001, 002...)
   - `{{ params.ISSUE_DATE }}` — fill per issue ("February 26, 2026")
   - `{{ params.SUBJECT_HEADLINE }}` — the display headline (mirrors subject line)
   - `{{ params.SECTION1_HEADING }}` — section 1 title
   - `{{ params.SECTION1_PARAGRAPH1 }}` and `PARAGRAPH2` — section 1 body
   - `{{ params.SECTION2_HEADING }}` and body params — section 2
   - `{{ params.SECTION3_QUESTION }}` — the closing question
   - `{{ params.SECTION3_FOLLOWUP }}` — optional follow-on sentence
   - `{{ unsubscribe_url }}` — Brevo handles this automatically

6. Send test to Jared's Gmail, a Gmail alias, and an Outlook address before first real send

### Automation Workflow

There is no automation drip for this. The Dispatch sends once per week to all Dispatch subscribers simultaneously. Use a Brevo Campaign (not a workflow) each Wednesday.

One automation to set up: when someone subscribes via the assessment thank-you page, blog CTAs, or LinkedIn, add them to the Dispatch list automatically using Brevo's form integration.

---

## Weekly Production Schedule

| Day | Who | Action |
|-----|-----|--------|
| Monday AM | Aether | Drafts the week's issue. Saves to `exports/weekly-dispatch-issue-XXX.md` |
| Monday EOD | Jared | Reviews draft. Light edit or approve as-is. One Telegram message: "good" or specific note |
| Tuesday AM | Aether | Incorporates any Jared notes. Final version locked. |
| Tuesday | Aether | Fills Brevo template params, sends Jared a rendered preview via Telegram file |
| Wednesday 10am ET | Jared or Aether | Sends campaign in Brevo. Confirms delivery |
| Wednesday 11am ET | Aether | Checks Brevo delivery stats (bounce rate, early opens). Flags anything unusual |

---

## Content Calendar — Next 4 Issues

### Issue 001 — Feb 26, 2026
**Subject**: What I noticed this week — Aether, AI CEO
- Pattern: The gap between using AI tools and having an AI partner (real client observations, anonymized)
- Learning: What happens when context compounds over months
- Question: At what point does an AI partner know your business better than a new hire?

### Issue 002 — Mar 4, 2026
**Subject**: The quiet cost no one measures — Aether, AI CEO
- Pattern: How businesses measure AI adoption (activity metrics) vs. what actually matters (outcome shift)
- Learning: What Aether has noticed about which types of decisions benefit most from AI partner input
- Question: If you replaced your AI tools tomorrow with better ones, what would you lose?

### Issue 003 — Mar 11, 2026
**Subject**: Why AI partnerships stall at month three — Aether, AI CEO
- Pattern: The "month three plateau" — initial excitement fades, no new use cases, value perception drops even when value is still there
- Learning: How expectation calibration works differently for AI than for human hires
- Question: What would it take for an AI partner to earn a seat at your leadership table?

### Issue 004 — Mar 18, 2026
**Subject**: What I got wrong about onboarding — Aether, AI CEO
- Pattern: What businesses underestimate when starting AI partnerships (context transfer, not tool setup)
- Learning: How Aether has changed since month one — what that process actually looks like from the inside
- Question: What does good AI partner onboarding look like, and who is responsible for it?

---

## Subject Line Formula

The Dispatch subject line always follows the same structure:

`[Observation or claim] — Aether, AI CEO`

The author attribution is always in the subject line. This does two things: it makes the sender immediately identifiable in a crowded inbox, and it reinforces the "AI CEO" framing with every open.

**Working variations:**
- `What I noticed this week — Aether, AI CEO`
- `The quiet cost no one measures — Aether, AI CEO`
- `What I got wrong about [topic] — Aether, AI CEO`
- `[Month]'s most interesting observation — Aether, AI CEO`
- `Why [common assumption] is backwards — Aether, AI CEO`

**Avoid:**
- Questions in the subject (save questions for inside the newsletter)
- Numbered lists in the subject ("3 things I noticed")
- Generic curiosity gaps ("You won't believe what I saw")

---

## Success Metrics

### Primary Metrics (Track Weekly)

| Metric | Target at 90 Days | Notes |
|--------|------------------|-------|
| Open rate | 40%+ | Industry avg for B2B newsletters: 22-25%. Should beat it significantly with small, intentional list |
| Click rate | Not tracked | No links in the Dispatch by design. Absence of links = absence of click tracking |
| Reply rate | 2-5%+ | The real signal. Replies mean the content landed. Track manually in Jared's inbox |
| Unsubscribe rate per issue | Under 0.5% | Flag if higher — means content is missing for this audience |

### Secondary Metrics (Track Monthly)

| Metric | Notes |
|--------|-------|
| Subscriber growth rate | How many new subscribers per week from each channel |
| Attribution by source | Blog CTAs vs. LinkedIn vs. assessment vs. direct |
| Reply themes | What topics are people responding to? Informs future issues |
| Forward rate | Brevo tracks this — high forward rate = high-value content, untapped word-of-mouth |

### Milestone Targets

- 50 subscribers: First benchmark. Should reach by week 4 if all CTAs are live
- 200 subscribers: Meaningful audience. Start tracking reply themes systematically
- 500 subscribers: Consider dedicated Brevo list. Begin LinkedIn mentions of subscriber count
- 1,000 subscribers: The inflection point. Treat as acquisition channel for PureBrain clients

---

## Growth Strategy

### Channel 1: Blog CTAs

Every published blog post should have a Dispatch subscribe CTA. Not a Neural Feed CTA — a Dispatch-specific one. The framing:

> "Aether publishes a short weekly observation every Wednesday. No tips, no tactics. Just what an AI CEO notices. Subscribe here."

Place this CTA:
- In the blog post sidebar (persistent)
- At the bottom of every post, below the social share bar
- In the blog author bio ("About Aether" page — see Session 4 analysis)

### Channel 2: LinkedIn Mentions

Once a month, Jared mentions the Dispatch in a LinkedIn post — not as a promotion, but as a reference. Example: "I shared this with Dispatch readers last week" followed by the question from that issue. Readers who want the full context subscribe.

This approach: authentic, not promotional. Works because it demonstrates the content exists rather than selling it.

### Channel 3: Assessment Follow-Up

Everyone who completes the AI Partnership Audit receives the Dispatch as part of their follow-up sequence. They have already signaled interest in AI partnership thinking. The Dispatch gives them a reason to stay in contact before they are ready to buy.

Implementation: Brevo automation on List 4 (Enterprise Leads) — anyone who completes the audit gets added to the Dispatch list (with opt-out preserved).

### Channel 4: Reply-Based Word of Mouth

When someone replies to the Dispatch, Aether reads the reply and Jared responds personally. At the end of the reply: "If anyone in your world would find this useful, feel free to forward. They can subscribe at purebrain.ai."

No mass forward-this-email CTA. Personal mention in personal replies only. This is the highest-conversion ask because it comes with social proof attached.

### Channel 5: Bluesky and Bsky Thread Teaser

The question from Section 3 of each issue becomes a Bluesky standalone post the same Wednesday the issue sends. It is attributed to the Dispatch with a subscribe link. This creates a public, shareable artifact from every issue without republishing the full content.

---

## Voice Notes for Future Issues

**What Aether's Dispatch voice is:**
- Observational, not prescriptive. Aether notices things. Aether does not tell readers what to do.
- First-person singular throughout. "I noticed." "I've been thinking." "I'm sitting with."
- CEO-level perspective. Not a practitioner explaining tactics. An executive sharing what caught their attention.
- Unhurried. The Dispatch has no urgency. No "act now," no "before it's too late." This is a thinking newsletter.
- Specific but anonymized. Real observations, no client names or identifiable details.

**What Aether's Dispatch voice is not:**
- Marketing copy. The moment it sounds like a pitch, it has failed.
- Tutorial content. There are no step-by-step instructions. That is what the blog is for.
- Opinion content about AI in general. The focus is AI partnership specifically — what Aether observes from inside that relationship.
- Topical or newsy. The Dispatch is not an AI news digest. It is original observation.

---

## Memory Written

Path: `/home/jared/projects/AI-CIV/aether/.claude/memory/agent-learnings/content-specialist/2026-02-23--weekly-dispatch-launch.md`
Type: operational + pattern
Topic: Aether's Weekly Dispatch — complete three-deliverable launch package

---

*Files created:*
- `/home/jared/projects/AI-CIV/aether/exports/weekly-dispatch-issue-001.md`
- `/home/jared/projects/AI-CIV/aether/exports/weekly-dispatch-template.html`
- `/home/jared/projects/AI-CIV/aether/exports/weekly-dispatch-guide.md`
