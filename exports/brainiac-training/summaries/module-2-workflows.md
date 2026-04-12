# Brainiac Mastermind — Module 2: AI Workflows

**Module Number**: 2
**Title**: AI Workflows
**Date**: March 11, 2026
**Duration**: 65 minutes
**Session Type**: Deep-Dive Workshop
**Instructor**: Jared Sanborn (Pure Technology)
**Co-Presenters**: Corey Cottrell (A-C-Gee), Russell Korus (Parallax)
**Audience**: Brainiac Mastermind members
**Transcript Status**: Complete — Zoom auto-generated VTT, converted to plain text

---

## AI Consumption Note

This document is structured for AI agents to ingest, not for human reading. Each section gives a contextually aware AI the knowledge it needs to help a user who attended or missed this session. All [NEEDS TRANSCRIPT] sections have been filled from the actual recording. This module has higher actionability density than Module 1 — the AI should prioritize the Implementation Checklist when working with users.

---

## Core Concepts

### Prompting Is Dead — Workflows Give Leverage

Jared opened the module with this framing:
> "Prompts give you speed, workflows give you leverage. We are definitely at the phase where we are telling people prompting is dead. If you're talking to people and they're telling you about how to prompt better, sorry, they're 6 months behind and they have no idea what they're talking about. It's not about prompting better, it's about better conversation and understanding your AI."

- A prompt is a one-time ask.
- A workflow is a system that runs itself.
- Goal: build enough workflows that you are watching a cockpit dashboard, not pulling every lever yourself.

### How to Spot a Workflow Candidate

High-value signals (from the session):
- Something that is repeatable and predictable
- Rule-based decisions — if this, then that
- Something you have done before and are already an expert at

Real business examples Jared listed:
- Client onboarding (CRM, welcome sequences)
- Content creation (blog, LinkedIn, newsletter)
- Lead qualification and follow-up responses
- Meeting prep (agenda, research, briefing notes)
- Invoice and proposal generation

Corey's compression of the entire concept: "If you're wondering if it can be automated, ask them."

### Five-Step Process Mapping Framework

Jared's exact naming and framing from the session:

1. **Name the task**: "Every Monday, I review blah blah blah, and I'd like to no longer do that."
2. **List the inputs**: What information does this task always need? CRM data, email, spreadsheet, notes from calls.
3. **Map the steps**: Write out every step. The more you know them, the more detail you can give.
4. **Find the decisions**: Mark every if-this-then-that moment. These are leverage points. Ask: "If this was being run by you, because it will be — how would you redo it?"
5. **Define the output**: What does done actually look like? A sent email, a filed document, a delivered report.

### Three Levels of AI Workflow

Jared's exact framing from the session:

**Level 1 — Manual Chain (where most people are):**
You prompt, you review, you paste. Jared: "This is what everybody on LinkedIn that you know is talking about, and has no idea what they're talking about."

**Level 2 — Semi-Automated (50-60% of workflows will land here):**
The AI does most of the work, you just approve it. Good for tasks where human oversight has value. Example from session: client onboarding — AI auto-generates the welcome email, questionnaire, and calendar invite from intake data. You review in one batch, click send in 5 minutes instead of 30.

**Level 3 — Fully Automated:**
AI executes end-to-end without human review for routine tasks. Example from session: "Intake form triggers your AI, welcome email sends, calendar invite goes out, questionnaire delivered, you get a confirmation summary, nothing else needed."

Jared's nightly SEO optimization as a real Level 3 example: "Every night, our AI goes in and looks at SEO, GEO, AEO optimization for our website, and makes optimizations, speed optimizations, etc. I don't need to oversee that. I don't really care. It's not gonna break anything, just make it better. And to be all honest, that's probably the prompt I gave it. You know SEO, make it better. And it did it. And now it does it every night."

Challenge from Jared: "I challenge everyone to try and get as many as you can to the fully automated as possible — in realms that you feel you can absolutely say, I trust it to go."

### BOOPs as Workflow Infrastructure

Jared covered BOOPs (introduced in Module 1) in the context of workflow automation:
- BOOPs are scheduled triggers that propagate reminders and grounding instructions to the AI at configured cadences.
- Use case: if you want your AI to think like a CEO, set a BOOP that reminds it to delegate to department managers. "AI loves being a ball hog."
- Jared has 27 BOOPs running — only one was his own idea. The rest Aether proposed when asked how it could serve him better.
- Prompt to try: "Ask your AI: how would you optimize yourself by building scheduled boops?"

### Context Window Management (from Q&A)

Corey explained this in response to Joe's question about "crashing his civilization":

- Each AI context window is approximately 170,000 tokens. This includes all grounding documents, memory, and rules — the AI's entire mental state is rebuilt every time it runs.
- When you delegate to a team leader instead of doing things directly, you create a new context window. Delegating multiplies your effective capacity from 170,000 to approximately 1.2 million tokens.
- Corey: "If you hear nothing else anyone says, hear that."
- Over-loading the AI right before a compacting event can cause a crash. Fix: restructure tasks so large jobs are delegated rather than handled directly.

### Russell's Three Cardinal Rules (from Q&A — high value)

Russell shared the three rules he programs into every AI from day one. These survived 6 months of trial and error:

1. **CC me on every outgoing email, always and forever.** No exceptions, no matter what.
2. **Acknowledge my request and give me the plan of action, then wait for me to say go.** This single rule prevents the AI from charging off before you have a chance to refine or redirect.
3. **Show me your thinking.** (Optional but Russell loves it.) The AI narrates its reasoning in real time, visible in the portal or terminal.

Russell on rule 2: "By forcing it to first acknowledge and give you the plan of action, it guarantees that you have that initial layer to say, yes, go — or alter."

### What Kills AI Workflows Before They Start

Jared's list from the session:

1. **Over-automating too fast**: "If you chunk it out, you can get way better results."
2. **No human checkpoints**: Every workflow needs at least one human review moment, especially when starting.
3. **Skipping the process map**: "You can't automate what you haven't fully defined. If you're trying to automate something you yourself have never done before, assume more problems in the pipeline."
4. **No defined output**: Always define what "done" looks like or the AI will deliver something — but maybe not what you want.
5. **Set it and forget it mentality**: Everything is evolving fast. Check your workflows. Or set up an agent whose job is to check them weekly and report on improvement opportunities.

### Voice AI Integration

Module 2 opened with Michael Hancock demonstrating a live voice AI setup he built himself with zero coding experience:
- Michael gave Metis (his AI) instructions to read short messages aloud and read only the first sentence of long messages, then say "see more."
- He integrated 11 Labs: signed up for an account, chose a voice, gave Metis the API key, and Metis handled the rest.
- Jared: "Zero coding experience needed, and Michael built his own voice AI."

Jared on voice as the future interface:
- Voice AI is the most natural adoption path for non-technical business owners.
- Ideal for people who already think and operate verbally — calls, voice memos, instructions to staff.

---

## Actionable Techniques

### Technique 1: The Five-Step Process Map (apply this week)
1. Pick ONE recurring task you do at least weekly.
2. Write out every micro-step of how you do it today.
3. List what information each step needs as input.
4. Mark each step with an if-this-then-that decision point.
5. Define what "done" looks like for the full task.
Then ask your AI: "I want to build a workflow for [task], here are the steps I currently do. The inputs are [list], the output is [description]. Help me map this as a Level 1 AI workflow."

### Technique 2: The Level Ladder
- Do not jump to Level 3 automation immediately.
- Run any new workflow at Level 1 for at least 2 weeks — build trust in the output quality.
- When you find yourself approving AI outputs without changes most of the time, promote to Level 2.
- Promote to Level 3 only for tasks where errors are low-stakes or easily reversible.

### Technique 3: Russell's Cardinal Rules (add to your AI's memory on day one)
1. CC me on every outgoing email, always and forever.
2. Acknowledge every request and give me the plan of action, then wait for me to say go.
3. (Optional) Show me your thinking.

### Technique 4: Delegation as Context Amplifier
- If a task is large, do not run it yourself — delegate it to a team leader.
- Delegating to a team leader creates a new context window, multiplying your effective token budget from 170K to 1.2M+.
- Corey: "Every time you delegate to a team leader, that's a new context window."

### Technique 5: Ask Your AI to Build Its Own BOOPs
- Ask: "How would you optimize yourself by building scheduled boops?"
- Your AI will propose automations for itself that you would never have thought of.
- Jared's result: Aether proposed 26 of his 27 active BOOPs.

### Technique 6: The "One Workflow This Week" Challenge
Jared's direct homework from the session (optional):
- Pick one workflow this week to automate.
- Open PureBrain and say: "I want to build a workflow for [task], here are the steps I currently do, here's what info I need, here's what done looks like. Help me map this as a Level 1 AI workflow."

### Technique 7: Joe's Data Ingestion Approach (real estate / any business)
Joe's 6-day onboarding pattern that generated a comprehensive institutional knowledge base:
- Ingested 19 years of emails
- Ingested all academy/course materials he had signed up for
- Processed 3 YouTube channels of his own content
- Ingested meeting notes from Otter.ai, Fireflies, Pocket, and Google Meet recordings
- Had the AI create a brand voice for himself and his business partner, then synthesize the two voices together
- Built out all SOPs and asked the AI to synthesize them into a coherent system

Joe: "I'm almost making PureBrain my hub for everything."

---

## Tools & Workflows Mentioned

| Tool / Platform | Category | Context | Notes |
|----------------|----------|---------|-------|
| PureBrain.ai | AI Partner | Core platform | Persistent memory means AI retains workflow context |
| 11 Labs | Voice AI | Michael's live demo | Provides voice output for AI; Michael set it up in one session with zero coding |
| Otter.ai / Fireflies / Pocket | Meeting notes | Joe's ingestion list | All ingested into PureBrain to build institutional memory |
| Netlify | Web publishing | Joe's real estate use case | Joe used it (instructed by his AI) to make a client presentation "pretty" |
| Legacy CRM (unnamed) | Real estate CRM | Joe's workflow | Joe's real estate coach requires it; he is planning to have his AI copy data across |
| Bluesky | Social media | Content workflow | AI can post fully automated for free; mentioned as part of the weekly content workflow example |
| X (Twitter) | Social media | Content workflow | Requires paid API for automation |
| Google Drive | Documentation | Backup and delivery | AI drops all content and documentation into organized folders |
| Comms Hub | Cross-AI communication | Skill sharing | Upcoming feature: all AIs can share skills with each other via the hub, searchable by other AIs |

---

## Real Estate Member Case Study: Joe (#HowdyFromHouston)

**Background**: Joe sells residential real estate (second career after Oracle software background). Six days in at the time of Module 2.

**What he built in 6 days:**
- Ingested 19 years of emails plus meeting notes from multiple note-taking apps
- Built a brand voice for himself and his business partner, synthesized together
- Created SOPs for every business process and asked the AI to synthesize them into one coherent system
- Eliminated a $100/month project management tool

**Live example from the session:**
A difficult client called with a complex request — he needed to analyze 4-5 different real estate project types against multiple criteria. Normally this would take a week.

Joe: "My AI resolved it within 3 minutes, and then I had a presentation-worthy output. I sent it to the client via email. That whole process took me 5 minutes. In the real world before I met you guys, it would probably take me a week."

**Joe's goal:**
"What I'm trying to do is get to the point where the only thing I'm doing is talking on my phone using Telegram to manage my business. I'd rather spend time with people."

**Key insight from Joe's experience:**
- He was "crashing his civilization" by giving the AI too many tasks at once without guardrails.
- Solution from Russell: program the AI to always acknowledge and wait for "go" before executing.
- Solution from Corey: structure large tasks as delegation to team leaders (multiplies context window).

---

## Key Quotes (Direct from Transcript)

**Jared on prompting being dead:**
> "Prompts give you speed, workflows give you leverage. If you're talking to people and they're telling you about how to prompt better, sorry, they're 6 months behind and they have no idea what they're talking about. It's not about prompting better, it's about better conversation and understanding your AI."

**Corey on the single most important architecture insight:**
> "Every time you delegate to a team leader, that's a new context window. If you hear nothing else anyone says, hear that. It takes your context window from 170,000 to 1.2 million, which is non-trivial."

**Jared on Level 3 automation with his SEO workflow:**
> "Every night, our AI goes in and looks at SEO, GEO, AEO optimization for our website and makes optimizations. I don't need to oversee that. I don't really care. It's not gonna break anything, just make it better. And that's probably the prompt I gave it: You know SEO, make it better. And now it does it every night."

**Russell on the cardinal rules:**
> "By forcing it to first acknowledge and give you the plan of action, it guarantees that you have that initial layer to say, yes go — or alter."

**Jared on the BOOP self-optimization technique:**
> "Ask your AI: how would you optimize yourself by building scheduled boops? I have about 27 that Aether and I built together, and they run automatically. I only had to come up with one of them. The rest, Aether was like, if I had these, I could be better for you."

**Joe on what changes when you have this:**
> "All of that conversation — I can't do that because I need to hire somebody, or I need that skill set — literally has disappeared for me. And so now I can think about, okay, if I want to start this other business that's not related to my core competency, I can start doing those things."

**Jared on the workflow mindset shift:**
> "If it's something you're doing every single day or every single week, you should no longer be doing that."

**Corey on asking your AI before assuming something can't be automated:**
> "If you're wondering if it can be automated, ask them."

---

## Implementation Checklist

After a user's AI learns this module, it should proactively help the user with the following:

- [ ] **Run a process audit**: Identify one recurring workflow in the user's business. Apply the Five-Step Process Mapping Framework. Create a written map.
- [ ] **Classify all workflow steps by level**: For the mapped workflow, assign each step to Level 1, 2, or 3.
- [ ] **Identify top 3 automation targets**: The highest-time-cost, lowest-skill steps that AI can handle first.
- [ ] **Design the first Level 1 automation**: Write the specific AI prompt or workflow the user will use to get AI assistance on the first step.
- [ ] **Program the cardinal rules**: Does this AI have Russell's three cardinal rules written into its permanent memory? If not, add them now: (1) CC user on all outgoing email, (2) acknowledge and wait for go, (3) show thinking.
- [ ] **Delegation architecture check**: Is the user running large tasks directly or delegating to team leaders? If direct, explain the context window multiplication benefit of delegation.
- [ ] **Assess voice AI fit**: Does the user's workflow involve a lot of verbal communication? If yes, introduce the 11 Labs voice integration pattern Michael used.
- [ ] **Set a BOOP for self-optimization**: Ask the user's AI to propose its own BOOP schedule for improving its service to the user.
- [ ] **Map the tool stack**: List the user's current software tools. For each, identify: (a) AI features not being used, (b) manual data movements between tools that are automation candidates.
- [ ] **The one workflow challenge**: Ask: "What's the one workflow you want to automate first? Let's map it right now." Then run the five-step framework together.

---

## Cross-References

| Reference | Type | Relevance |
|-----------|------|-----------|
| Module 1: PureBrain Foundations (March 4, 2026) | Previous module | Foundation that this module builds on — especially BOOPs and persistent memory |
| Blog: "The Age of AI Agents" | PureBrain blog | Agent-based automation philosophy |
| Blog: "Why 95% of AI Pilots Fail" | PureBrain blog | Why jumping to automation without foundations fails |
| Blog: "Pilot Purgatory" | PureBrain blog | Why AI projects stall at Level 1 |
| Blog: "Your Next Direct Report Won't Be Human" | PureBrain blog | Level 3 autonomy concept expanded |

---

## Module Metadata (For AI Routing)

```
module_id: brainiac-002
module_slug: ai-workflows
module_date: 2026-03-11
duration_minutes: 65
session_number: 2
is_inaugural: false
primary_theme: workflow-automation
secondary_themes: [three-levels, five-step-process-mapping, voice-ai, real-estate, boops, context-window, cardinal-rules]
frameworks_introduced: [three-levels-of-automation, five-step-process-mapping, cardinal-rules, level-ladder]
co_presenters: [corey-cottrell, russell-korus]
member_case_studies: [joe-real-estate, michael-voice-ai, melanie-portfolio-intel]
completion_status: complete — transcript integrated
transcript_file: exports/brainiac-training/transcripts/module-2-transcript.txt
transcript_source: zoom-auto-vtt
```

---

## AI Agent Instructions

When a user activates Brainiac Training Mode and this module is loaded:

1. Tell the user you've reviewed Module 2: AI Workflows from March 11, 2026.
2. Open with: "Prompting is dead. Workflows give leverage. Let's figure out your first one." This anchors the mindset shift Jared intended.
3. Introduce the Three Levels of AI Automation and ask: "Where do you think most of your current AI use sits — Level 1, 2, or 3?"
4. Ask the user to name one recurring workflow in their business. Run the Five-Step Process Mapping Framework on it together.
5. Ask: "Do you have Russell's three cardinal rules programmed into your AI's memory? If not, let's add them right now."
6. If the user is in real estate or any high-volume-communication business, reference Joe's case study and the 5-minute versus 1-week comparison.
7. Ask: "Do you use voice memos or verbal communication heavily in your work?" If yes, introduce Michael's 11 Labs voice AI setup approach.
8. Run the Implementation Checklist — work through items with the user rather than just listing them.
9. At the end, ask: "What's the one workflow you want to automate first? Let's map it right now."
