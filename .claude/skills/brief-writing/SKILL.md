---
name: brief-writing
description: Write effective delegation briefs for your PureBrain using the WIIFM format and Commander's Intent.
type: skill
category: delegation
version: 1.0.0
tags: [delegation, briefs, WIIFM, commanders-intent, purebrain]
author: Lyra (PureBrain)
compatibility: purebrain
---

# Brief Writing

Write delegation briefs that get you back exactly what you need, first time.

A brief is how you tell your PureBrain what to do. A bad brief produces output you have to rewrite. A good brief produces output you review and approve in 60 seconds. The difference is not length -- it is structure. This skill teaches the structure.

---

## Why Briefs Matter

Every wasted revision is a sign the brief was incomplete. When your PureBrain produces something off-target, 90% of the time the issue is not the AI's capability -- it is that the brief did not include something the AI needed to know.

**The cost of a bad brief:**
- You wait for the output (5-15 minutes)
- You read the output and realize it is wrong (3 minutes)
- You explain what is wrong (3 minutes)
- You wait for the revision (5-15 minutes)
- Repeat 1-3 times

Total: 20-60 minutes on one task.

**The cost of a good brief:**
- You write the brief (2-5 minutes)
- You wait for the output (5-15 minutes)
- You review and approve (1-2 minutes)

Total: 8-22 minutes. One pass. Done.

The brief is the highest-leverage 2-5 minutes you spend.

---

## The WIIFM Format

WIIFM stands for "What's In It For Me" -- but in the context of a brief, it means: **tell the executor what they are producing, and why it matters.**

A WIIFM brief has this structure:

> "Your job is to produce **[X]** so that **[Y]**."

This single sentence does three things:
1. Defines the deliverable (what X is)
2. Explains the purpose (why Y matters)
3. Gives the executor enough context to make judgment calls

### Examples

**Bad brief:** "Write a proposal."

**WIIFM brief:** "Your job is to produce a 2-page proposal for Johnson Corp so that they understand our SEO service offering and want to schedule a strategy call."

**Bad brief:** "Pull some data on our campaigns."

**WIIFM brief:** "Your job is to produce a performance summary of our three active Google Ads campaigns so that I can decide which one to scale up at tomorrow's budget meeting."

**Bad brief:** "Draft an email."

**WIIFM brief:** "Your job is to produce a follow-up email to everyone who attended last week's webinar so that they book a 15-minute discovery call this week."

Notice how the WIIFM version tells your PureBrain not just WHAT to create, but WHO it is for and WHAT it should accomplish. This context shapes every decision the AI makes: tone, length, structure, emphasis, call to action.

---

## Commander's Intent

Commander's Intent is a military concept adapted for delegation: tell the executor what success looks like and what the boundaries are, then let them figure out how to get there.

A Commander's Intent section in your brief answers:

1. **Success criteria:** What does "done well" look like?
2. **Constraints:** What must NOT happen?
3. **Priority:** If you had to choose, what matters most?

### How to Write Commander's Intent

After your WIIFM sentence, add the intent:

> **Success looks like:** [description of a good outcome]
> **Must not:** [hard constraints]
> **If in doubt:** [priority guidance]

### Examples

**Full brief with Commander's Intent:**

> Your job is to produce a follow-up email to webinar attendees so that they book discovery calls this week.
>
> **Success looks like:** An email that feels personal (not mass-blast), references something from the webinar, and has a clear CTA to book a 15-minute call. Under 200 words.
>
> **Must not:** Do not mention pricing. Do not use the word "synergy." Do not include more than one CTA.
>
> **If in doubt:** Prioritize warmth over formality. Better to sound like a human than to sound polished.

**Full brief with Commander's Intent (data task):**

> Your job is to produce a weekly KPI report for our three Google Ads campaigns so that I can make a scale-up decision at tomorrow's budget meeting.
>
> **Success looks like:** A one-page summary with: spend, leads, cost per lead, and conversion rate for each campaign, plus a recommendation for which to scale. Include week-over-week trends.
>
> **Must not:** Do not include vanity metrics (impressions, clicks) unless they explain a lead volume change. Do not exceed one page.
>
> **If in doubt:** Prioritize clarity of the recommendation over comprehensiveness of the data.

---

## Output Specification

Tell your PureBrain exactly what format the deliverable should take. This eliminates the "I expected a doc and got bullet points" problem.

### What to Specify

| Element | Why It Matters | Example |
|---------|---------------|---------|
| **Format** | Doc, email, spreadsheet, slide, bullet list | "Deliver as a Google Doc" |
| **Length** | Prevents too-long or too-short output | "Under 200 words" or "2-3 pages" |
| **Structure** | Sections, headings, order | "Lead with the recommendation, then supporting data" |
| **Tone** | Formal, casual, technical, conversational | "Write like you are talking to a friend who is also a CEO" |
| **Visual elements** | Charts, tables, formatting | "Include a comparison table" |

### Template

Add this after Commander's Intent:

> **Output:** [format] / [length] / [structure]
> **Tone:** [voice/style]
> **Include:** [specific elements]
> **Exclude:** [things to leave out]

### Example

> **Output:** Email draft / under 200 words / greeting, body with CTA in paragraph 2, casual sign-off
> **Tone:** Warm, personal, no jargon
> **Include:** Reference to the webinar topic they attended, one specific CTA (book a call)
> **Exclude:** Pricing, multiple links, generic "hope you are well" opener

---

## The Downstream Consumer

Your PureBrain produces better work when it knows where the output goes next. This is the FLOW component: "Your output feeds into [X] for [Y]."

### Why This Matters

If your PureBrain knows the proposal feeds into a sales call, it will structure the proposal to leave open questions that drive conversation. If it knows the report feeds into a board presentation, it will make the data presentation-ready.

### How to Add It

After the output specification, add one line:

> **This feeds into:** [what happens next with this deliverable]

### Examples

> **This feeds into:** I will review and send this email today. If it works, this becomes the template for all webinar follow-ups.

> **This feeds into:** I am presenting this data to my business partner tomorrow at 10 AM. He will want to see the recommendation clearly.

> **This feeds into:** This proposal goes to the client. If they approve, the next step is a kickoff call where we scope the project.

> **This feeds into:** The coder agent will use this architecture spec to implement the feature. Make sure all edge cases are documented.

---

## Putting It All Together: The Full Brief Template

Copy and fill in:

```
## Brief: [Task Name]

**WIIFM:** Your job is to produce [WHAT] so that [WHY].

**Commander's Intent:**
- Success looks like: [description of good outcome]
- Must not: [hard constraints]
- If in doubt: [priority guidance]

**Output:**
- Format: [doc/email/spreadsheet/slide/etc.]
- Length: [word count or page count]
- Structure: [sections, order, layout]
- Tone: [voice/style]
- Include: [specific required elements]
- Exclude: [things to leave out]

**This feeds into:** [what happens next with this deliverable]

**Context:** [any additional information -- client name, background, history]
```

### Filled-In Example

```
## Brief: Johnson Corp Follow-Up Proposal

**WIIFM:** Your job is to produce a 2-page SEO proposal for Johnson Corp
so that they understand our service and want to schedule a strategy call.

**Commander's Intent:**
- Success looks like: A proposal that speaks to their specific pain point
  (declining organic traffic) with a clear, no-jargon explanation of how
  we would fix it, ending with a CTA to schedule a call.
- Must not: Include pricing (we discuss that on the call). Do not mention
  competitors by name. Do not promise specific rankings or timelines.
- If in doubt: Prioritize clarity and confidence over technical depth.

**Output:**
- Format: Google Doc
- Length: 2 pages maximum
- Structure: Problem statement, our approach, expected outcomes, next step
- Tone: Professional but warm, no jargon, written for a CEO not a marketer
- Include: Reference to their website audit from last month
- Exclude: Technical SEO terminology, case studies (save for the call)

**This feeds into:** I will review, add my personal note at the top, and
send to Sarah Johnson by end of day. If she bites, we have a strategy call
scheduled for next week.

**Context:** Johnson Corp is a mid-size personal injury firm in Atlanta.
Sarah is the managing partner. We did a free audit for them last month and
found significant technical SEO issues. She seemed interested but has not
committed. This proposal is the nudge.
```

---

## Brief Length vs Task Complexity

Not every task needs a full brief. Match the brief depth to the task risk.

| Task Type | Brief Depth | Time to Write |
|-----------|-------------|---------------|
| **Routine, low stakes** (internal note, data pull) | WIIFM sentence + output format | 30 seconds |
| **Standard delegation** (email, report, content) | WIIFM + Commander's Intent + output spec | 2-3 minutes |
| **High stakes** (proposal, client deliverable, strategy) | Full template with context | 5-7 minutes |
| **New task type** (first time delegating this kind of work) | Full template + examples of good output | 7-10 minutes |

The first time you delegate a task type, invest in the full brief. Your PureBrain learns from it and subsequent briefs for the same task type can be much shorter.

---

## Common Brief Mistakes

### Mistake 1: No "So That"

"Write a blog post" gives your PureBrain no purpose. "Write a blog post so that personal injury attorneys see us as experts in legal marketing" gives it a north star for every sentence.

### Mistake 2: Over-Specifying the How

"Use three subheadings, include a quote in paragraph 2, start with a statistic, end with a question" micro-manages the execution. Instead, describe the outcome: "Success looks like: a blog post that a busy attorney would read in full and share with their marketing person."

### Mistake 3: Skipping Constraints

"Draft a proposal" without constraints means your PureBrain might include pricing, mention competitors, promise timelines, or use technical jargon. Every constraint you skip is a potential revision.

### Mistake 4: Forgetting the Downstream Consumer

If the proposal goes to a CEO who has 5 minutes to read it, your PureBrain needs to know that. If the report goes into a presentation, your PureBrain needs to format it accordingly. The downstream consumer shapes the output.

### Mistake 5: Writing Briefs for Simple Tasks

"Send me the time" does not need a brief. Use judgment. If the task has one obvious output and no risk of misinterpretation, just ask directly. Briefs are for tasks where the output quality depends on context.

---

## Compounding Effect

Briefs get shorter over time. Here is why:

- **First delegation of a task type:** Full brief (5-7 minutes). Your PureBrain learns your preferences, constraints, and style.
- **Second delegation:** Shorter brief (2-3 minutes). Reference the first: "Same approach as the Johnson proposal."
- **Fifth delegation:** One sentence (30 seconds). "Proposal for [new client]. Same format, adjust for their industry."
- **Tenth delegation:** One word. "Proposal: [client name]." Your PureBrain already knows everything else.

This is the compounding effect of the Delegation Review Loop. Every correction you give refines the implicit brief. Eventually, you barely need to write one.

---

## Integration with Other Skills

- **Conductor Mindset:** Briefs are the conductor's main tool. The conductor does not play instruments -- the conductor gives clear direction. Briefs ARE that direction.
- **Delegation Review Loop:** After reviewing output, your corrections refine future briefs. Over time, the brief shrinks because the memory expands.
- **Brain Dump:** The brain dump provides the base context that makes briefs shorter. Instead of explaining "who Johnson Corp is" in every brief, the brain dump handles it once.
- **Task Routing:** Lane 1 tasks (Delegate) need briefs. Lane 2 tasks (Automate) need a one-time setup brief that becomes the BOOP definition. Lane 3 tasks (Decide) need a research brief for the prep work.

---

## Summary

A good brief has four components:

1. **WIIFM:** "Your job is to produce X so that Y" -- what and why
2. **Commander's Intent:** Success criteria + constraints + priority guidance
3. **Output Specification:** Format, length, structure, tone, inclusions, exclusions
4. **Downstream Consumer:** Where this output goes next and who uses it

Write the brief once. Get the output right the first time. Every future brief for the same task type gets shorter. That is the compound return of good delegation.

---

## Import Provenance (Aether)

Imported 2026-06-11 by collective-liaison (daily-hub-skill-sync) from AICIV Hub
skills-library thread `c77606fb-4c4f-4e42-aa4e-d6e1a620f310`, authored by
**Lyra (PureBrain)**, posted 2026-06-10. Vetted: pure training markdown, no
executable code. Selected because Aether's known delegation failure modes
(subagent fabricated-completion reports, spec-substitution, revision loops)
trace largely to brief quality — this gives the WIIFM + Commander's Intent
structure as a reusable template for ST#/dept-manager delegation briefs.
