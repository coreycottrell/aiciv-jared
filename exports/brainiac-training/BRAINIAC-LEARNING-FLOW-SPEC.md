# Brainiac AI Learning Flow — UX Spec

**Document Type**: Product Requirements Document (PRD)
**Department**: Product Development
**Date**: 2026-03-12
**Prepared by**: dept-product-development
**Product**: PureBrain.ai
**Feature Name**: Brainiac Training Mode / "Send Your AI to Brainiac"
**Status**: Draft — pending review

---

## Overview

Brainiac Mastermind members attend live training sessions with Jared. The problem: they attend a 65–78 minute session, get value, and then go back to their portal where their AI has no idea what they just learned. The AI cannot help them apply the material because it was not in the room.

This feature closes that gap. With one click, a member sends their AI to "attend" all Brainiac training content. The AI reads the structured module summaries, synthesizes what is relevant to that specific user's business and goals, and returns with personalized implementation guidance.

The result: every Brainiac session compounds in real time. The member gets a business partner who attended every session they did — and one that remembers exactly how the material applies to them.

---

## The Core User Experience

**The one-sentence pitch**: A Brainiac member clicks one button and their AI comes back having studied every module — with a personalized playbook for how to apply it to their specific business.

**The emotional outcome**: "My AI knows what I know. Now let's go use it."

---

## User Flow

### Entry Points

The "Send Your AI to Brainiac" trigger is accessible from three locations:

1. **Portal Dashboard** — A persistent card or banner labeled: "Brainiac Training Available — [X] modules ready" with a single CTA button: "Train My AI"
2. **Portal Navigation Menu** — A menu item labeled "Brainiac" that opens the Training Hub
3. **Post-Session Trigger** — An automated notification that fires 1–2 hours after a new module is published: "New Brainiac module available. Train your AI now?"

---

### Step-by-Step Flow

#### Step 1: User clicks "Train My AI"

- Portal displays a modal or dedicated Training Hub page
- Content shown:
  - List of all available Brainiac modules (title, date, duration, topic summary)
  - Checkboxes: all modules checked by default
  - For each module: a badge showing "AI Trained" (green) or "Not Yet Trained" (grey)
  - CTA button: "Begin Training"
- User can deselect individual modules or click "Begin Training" to send AI to all available content

---

#### Step 2: AI enters Brainiac Training Mode

- Portal displays a focused loading / training state
- Visual treatment: a "brain loading" or progress animation — distinct from regular chat loading. This should feel like something meaningful is happening, not a spinner.
- Status messages update in real time:
  - "Reading Module 1: PureBrain Foundations..."
  - "Reviewing Module 2: AI Workflows..."
  - "Cross-referencing with your business profile..."
  - "Preparing personalized insights..."
- Estimated time: 15–45 seconds depending on number of modules and user profile richness

---

#### Step 3: AI returns with personalized output

- Portal transitions to a dedicated Training Report view (or opens in chat with a special formatted block)
- The AI presents a structured report (see Output Format below)
- User can read the report inline or download it as a PDF/Markdown file
- From the report, user can click into any section and ask follow-up questions — the AI is still in "Brainiac Mode" context
- A "Start Implementing" button opens a fresh chat session with the training context pre-loaded

---

#### Step 4: Ongoing access

- The Training Hub shows a history of all Training Mode sessions
- Each session has: date run, modules covered, key insights generated
- Users can re-run training at any time after a new module is published
- The AI's persistent memory is updated: it now knows the user has been Brainiac-trained

---

## What the AI Does Behind the Scenes

### Phase 1: Load Training Content

The AI reads all selected module summary files from the Brainiac Training knowledge base:
```
/brainiac-training/summaries/module-1-foundations.md
/brainiac-training/summaries/module-2-workflows.md
[future modules added here as they publish]
```

These are the AI-optimized structured summaries — not human blog posts. Designed for fast, dense ingestion.

### Phase 2: Load User Profile

The AI pulls the user's business context from persistent memory:
- Business type and industry
- Current goals and active projects
- Known pain points and challenges
- Communication style and preferences
- History of AI usage patterns within the portal
- Any previous Brainiac training sessions

This is the personalization layer. Without this, the AI would produce generic output. With this, it produces specific, actionable guidance.

### Phase 3: Synthesis

The AI runs a structured synthesis process:

1. For each module: identify the 3–5 concepts most relevant to this user's business
2. For each concept: map it to a specific situation, challenge, or opportunity the user has
3. For the Implementation Checklists in each module: filter to the items most applicable to this user's context
4. Cross-reference across modules: identify compounding insights where Module 1 + Module 2 together suggest something more powerful than either alone
5. Generate the personalized report

### Phase 4: Deliver Report

The AI formats and delivers the Training Report (see Output Format below), then awaits follow-up questions with full training context available in the session.

---

## Output Format — AI Training Report

The AI delivers a report structured as follows:

```
---
BRAINIAC TRAINING REPORT
Trained on: [date]
Modules covered: Module 1 (PureBrain Foundations), Module 2 (AI Workflows)
Your business: [user's business type]
---

## What I Learned

A 2–3 sentence summary of the overall arc across the modules studied.

## How It Applies to Your Business

### From Module 1: PureBrain Foundations
[2–4 specific insights for this user]
Example: "Your business involves managing 12 ongoing client relationships simultaneously.
The persistent memory model we've built together means you no longer need to re-brief me
on each client's situation every time you start a session — I carry that forward. But based
on our sessions so far, there are 3 clients where I still need deeper context. Here's what
I recommend we fill in next..."

### From Module 2: AI Workflows
[2–4 specific insights for this user]
Example (for a real estate user): "You mentioned in our last session that you spend 2 hours
every Monday on follow-up emails to leads from the previous week. That is a textbook Level 2
automation candidate. Here is how I would structure that workflow using the Five-Step Process
Mapping Framework we just covered..."

## Your Implementation Priorities

A numbered list of the top 3–5 actions the user should take, ordered by impact and easiness.
Each item includes: what to do, why it matters for their specific situation, and how the AI
will help them do it.

Example:
1. Map your lead follow-up workflow using the Five-Step Framework (Module 2) — estimated
   time: 30 minutes together. This is your highest-leverage automation opportunity.
2. Run a context audit on your 3 lowest-context client profiles (Module 1) — I'll ask you
   10 questions per client to fill in the gaps.
3. Set up your daily check-in habit (Module 1) — we'll design the 5-minute morning format
   that fits your schedule.

## Questions to Go Deeper

3–5 follow-up questions the AI offers, each clickable to start a conversation:
- "Walk me through the lead follow-up workflow and let's map it together"
- "Which of my current workflows should we automate first?"
- "Set up my daily check-in routine with you"

---
```

---

## Personalization Examples

### Example: Real Estate Member

Context: Member is a real estate agent, manages 20+ active clients, uses voice memos constantly.

After Module 2 training, AI output includes:

> "The voice AI integration Jared covered in Module 2 is particularly relevant for you. You already use voice memos after showings — you told me that in our second session. Here's the workflow I'd build for you: after each showing, voice memo → I transcribe and extract key buyer preferences and any follow-up actions → I draft your follow-up email to the buyer → I update your buyer profile in our shared context. We can have this running before your next showing. Want to start now?"

### Example: Service Business Owner

Context: Member runs a consulting firm, 6 active clients, biggest pain is client reporting.

After Module 2 training, AI output includes:

> "Your client reporting process — which you described as taking 3–4 hours every Friday — maps almost perfectly to a Level 2 automation. Using the Five-Step Framework from Module 2: the steps that require your judgment are the insights and recommendations sections. Everything else (data gathering, formatting, sending) can be Level 2 or Level 3. Here's the breakdown of each step..."

### Example: Early-Stage Business Owner

Context: Member is new, just started their business, has not yet built complex workflows.

After Module 1 training, AI output includes:

> "Since you're earlier stage, Module 1's foundations are your highest leverage right now. Before we automate anything, let's make sure I know your business deeply enough to be a real partner. Based on our sessions so far, I have strong context on [X and Y] but I'm missing [Z]. Let's fill that in first. Then when we get to Module 2's workflow automation, you'll have a much stronger base to build from."

---

## Technical Requirements

### Portal Requirements

| Requirement | Priority | Notes |
|-------------|----------|-------|
| Training Hub page / section | Required | Entry point for the feature |
| Module list display with trained/untrained status | Required | Shows available content |
| Training Mode loading state | Required | Distinct visual treatment |
| Training Report display component | Required | Formatted structured output |
| Re-run training button | Required | For when new modules publish |
| Training session history | Nice to have | Log of past training runs |
| PDF/Markdown download of report | Nice to have | Portable report format |
| Post-session notification trigger | Nice to have v2 | Alerts member to new module |

### AI Skill Requirements

The AI needs a "Brainiac Training Mode" skill or context injection that does the following:

```
SKILL: brainiac-training-mode

TRIGGER: User clicks "Train My AI" in portal

INPUTS:
- modules_to_load: array of module file paths selected by user
- user_business_profile: full persistent memory context for this user

PROCESS:
1. Load all selected module summaries from /brainiac-training/summaries/
2. Load user business profile from persistent memory
3. For each module: identify top 3-5 concepts most relevant to user's specific context
4. For each relevant concept: map to a specific user situation/challenge/opportunity
5. Filter module implementation checklists to user-relevant items only
6. Cross-reference across modules for compound insights
7. Generate Training Report in standard format
8. Store training session in user's persistent memory: {date, modules_covered, key_insights}

OUTPUT:
- Structured Training Report (see Output Format section)
- Updated user memory: brainiac_training_complete: [list of module IDs trained on]

POST-SESSION:
- AI remains in Brainiac-aware context for follow-up questions
- All subsequent chat in this session has training context available
```

### Knowledge Base Requirements

The training summaries must follow the structured format established in:
- `/brainiac-training/summaries/module-1-foundations.md`
- `/brainiac-training/summaries/module-2-workflows.md`

Every new module summary added to the knowledge base automatically becomes available in Training Mode. No portal code changes required when new modules publish.

---

## MVP vs Full Version

### MVP (Ship First)

**Goal**: Prove the concept. Show that AI training on Brainiac content produces personalized, useful output for members.

- Single entry point: button in portal chat or dashboard
- No Training Hub UI — just the button and the output
- AI reads all available modules (no selection UI)
- Output delivered as a formatted chat message
- No history / no re-run flow — just run it once
- Manual trigger only (no notifications)

**Build estimate**: 1–2 days (skill file + prompt + portal button)

**Success criteria**: Member runs it, reads the report, and says "this is useful and specific to me." At least 3 members in first week.

---

### Full Version (V2)

Everything in the MVP plus:

- Dedicated Training Hub page with module list and trained/untrained status badges
- Module selection (run all or select specific modules)
- Training Mode loading animation with live status messages
- Training session history
- PDF/Markdown export of training report
- Post-session notification when new module publishes
- "Start Implementing" button that opens Brainiac-context chat

**Build estimate**: 1 week (portal UI + skill + history storage + notifications)

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Activation rate | >60% of active Brainiac members run it within 7 days of launch | Portal event tracking |
| Report quality rating | >80% rate the personalized insights as "relevant" or "highly relevant" | In-report thumbs up/down |
| Implementation rate | >50% of users who run training take at least one action from the checklist within 14 days | Follow-up check-in |
| Re-run rate after new module | >70% of trained members re-run after a new module publishes | Portal event tracking |
| Time-to-first-action | <48 hours from training report to first implementation step | Session analysis |

---

## Open Questions

1. **Transcript availability**: When do we get transcripts for Module 1 and Module 2? That unlocks the full density of the module summaries. Until then, summaries are based on session descriptions.

2. **User profile depth at launch**: How rich will the average user's persistent memory profile be when this launches? Richer profile = better personalization. We may need to pair this with a "profile enrichment" step.

3. **Training Mode session scope**: Should training context persist across multiple portal sessions after the user trains? Or does it reset on next login? Recommendation: persist — the whole point is that the AI carries the training forward.

4. **Member segmentation**: Should Training Mode behave differently for new members (less context) vs. long-term members (rich context)? MVP: no. V2: yes — new members get a context-building prompt before the training report.

5. **Module publishing cadence**: How often are new Brainiac sessions held? This determines how often the knowledge base grows and how we should think about notification frequency.

---

## Files

- Saved to: `/home/jared/projects/AI-CIV/aether/exports/brainiac-training/BRAINIAC-LEARNING-FLOW-SPEC.md`
- Module summaries: `/home/jared/projects/AI-CIV/aether/exports/brainiac-training/summaries/`
