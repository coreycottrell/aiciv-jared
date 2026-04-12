# Brainiac Mastermind Module 2: Building Your First AI Workflow — Ingested

**Date**: 2026-03-13
**Type**: teaching
**Agent**: dept-systems-technology
**Source**: https://purebrain.ai/brainiac-mastermind-training/?bypass=portal
**Module**: Module 2 — Building Your First AI Workflow
**Session Date**: March 11, 2026 | Duration: 65 minutes
**Instructors**: Jared Sanborn, Corey Cottrell, Russell Korus

---

## Core Concepts

1. **Prompting Obsolescence**
   - Prompts deliver speed; workflows deliver leverage
   - Advanced prompt engineering = outdated methodology (6 months behind)
   - The next level is cockpit-dashboard operation, not manual lever-pulling

2. **Workflow vs. Prompt Distinction**
   - One-time asks = prompts
   - Self-running systems = workflows
   - Goal: the AI runs itself, surfaces results; human approves/adjusts

3. **Workflow Candidate Signals (Four Criteria)**
   - Repeatable
   - Predictable
   - Rule-based (if-this-then-that logic)
   - Already mastered by the human (do not automate unfamiliar processes)

4. **Three Automation Levels**
   - **Level 1 — Manual Chain**: human prompts, reviews, and pastes between steps; best for learning
   - **Level 2 — Semi-Automated**: AI handles majority, human approves at defined checkpoints
   - **Level 3 — Fully Automated**: end-to-end without review; only for low-stakes/reversible tasks
   - Rule: Run at Level 1 for 2+ weeks before promoting to Level 2

5. **Context Window Multiplication Strategy**
   - Each AI holds ~170K tokens
   - Delegating a large task to a sub-agent creates a new 170K-token context window
   - Team delegation: 170K → 1.2M+ tokens total capacity
   - "If you hear nothing else, hear that" — Corey Cottrell

6. **BOOPs as Workflow Infrastructure**
   - Schedule AI to self-delegate like a CEO
   - Ask the AI: "How would you optimize yourself by building scheduled BOOPs?"
   - Avoids "ball hog" behavior where AI tries to do everything in one context
   - Aether autonomously proposed 26 of Jared's 27 active BOOPs

7. **Five-Step Process Mapping Framework**
   1. Name the task
   2. List inputs required
   3. Map every micro-step
   4. Identify if-this-then-that decision points
   5. Define "done" output explicitly

8. **Workflow Failure Patterns (Anti-Patterns)**
   - Over-automating prematurely (before process is understood)
   - Missing human checkpoints
   - Skipping process maps
   - Undefined outputs (unclear what "done" looks like)
   - Set-and-forget mentality (workflows need monitoring)

9. **Voice AI Integration**
   - 11 Labs API enables voice AI with zero coding
   - Real example: Michael Hancock voice workflow
   - Applicable when workflow involves significant verbal communication

10. **Real Business Applications (Live Examples)**
    - Client onboarding automation
    - Content creation pipelines
    - Lead qualification workflows
    - Meeting prep automation
    - Invoicing and proposal generation
    - Nightly SEO optimization (Aether does this live)

---

## Key Implementation Techniques

1. **Five-Step Process Map (Do This Week)**
   - Select one recurring task
   - Write every micro-step
   - List inputs
   - Mark if-then decisions
   - Define success output
   - Then ask AI to map as Level 1 workflow

2. **The Level Ladder**
   - New workflows start at Level 1 always
   - Promote to Level 2 when 2+ weeks of approvals happen without edits
   - Level 3 only for low-stakes, reversible tasks

3. **Russell's Three Cardinal Rules (Day One Programming)**
   - Rule 1: CC me on every outgoing email, always and forever
   - Rule 2: Acknowledge request and provide plan of action; wait for "go" before executing
   - Rule 3: Show your thinking
   - These get programmed into permanent AI memory on Day One

4. **Delegation as Capacity Multiplier**
   - Large tasks delegated = new context window = 170K becomes 1.2M+ tokens
   - The compounding effect is non-linear — team thinking vs. single-thread thinking

5. **AI Self-Optimization via BOOPs**
   - Ask: "How would you optimize yourself by building scheduled BOOPs?"
   - Let the AI architect its own recurring task structure
   - Review and approve the BOOP schedule the AI proposes

6. **Joe's Data Ingestion Pattern (Real Case)**
   - Ingested: 19 years of emails, course materials, YouTube channel, meeting notes, SOPs
   - Synthesized into coherent brand-voice hub
   - Result: AI speaks in client's authentic voice across all output

7. **One Workflow Challenge**
   - Identify first automation target immediately after module
   - Map it together using Five-Step Framework in real-time
   - Do not delay — momentum matters at this stage

8. **Process-First Rule**
   - Cannot automate what hasn't been fully defined
   - Never automate a process you don't fully understand yourself
   - Definition first, automation second

---

## Implementation Checklist (Actionable for Coaching)

- [ ] Run process audit; identify one recurring workflow; apply Five-Step Mapping Framework
- [ ] Classify all workflow steps by automation level (1, 2, or 3)
- [ ] Identify top 3 automation targets (highest time cost, lowest skill requirement)
- [ ] Design first Level 1 automation; write the specific prompt/workflow instructions
- [ ] Program Russell's Cardinal Rules into permanent AI memory
- [ ] Assess delegation architecture — are large tasks delegated or run in single context?
- [ ] Explain token multiplication to client; ensure they understand the 170K → 1.2M+ concept
- [ ] Evaluate voice AI fit — does the workflow involve significant verbal communication?
- [ ] Set BOOP for AI self-optimization check-in
- [ ] Map tool stack for unused AI features and manual data-movement automation candidates
- [ ] Run One Workflow Challenge immediately in-session

---

## Key Quotes (Attribution-Ready)

> "Prompts give speed; workflows give leverage. If people tell you about better prompting, they're 6 months behind." — Jared Sanborn

> "Delegating to a team leader creates a new context window. Taking it from 170K to 1.2M tokens is non-trivial. If you hear nothing else, hear that." — Corey Cottrell

> "Initial acknowledgment and plan approval guarantees that layer where you approve or alter direction." — Russell Korus

---

## Application to Aether / PureBrain Systems

- The Three Automation Levels framework is directly applicable to how Aether scopes new automation requests
- Russell's Cardinal Rules mirror the "acknowledge → plan → wait for go" protocol in CLAUDE-OPS.md
- The "process-first rule" is relevant: Aether should document a process manually before automating it
- Joe's Data Ingestion Pattern is a strong sales story for onboarding new PureBrain clients
- The "BOOPs as CEO self-delegation" framing is a teaching tool for explaining how Aether's BOOP system works to clients
- Level Ladder concept should inform how new Aether automations are deployed (start Level 1, earn promotion)

---

**Tags**: brainiac-mastermind, module-2, ai-workflows, automation-levels, process-mapping, delegation, context-multiplication, boops, russell-cardinal-rules, training-ingestion
