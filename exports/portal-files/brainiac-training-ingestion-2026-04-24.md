# Brainiac Mastermind Training - Complete Module Ingestion

**Extracted**: 2026-04-24
**Source**: purebrain.ai/brainiac-mastermind-training/ (local deploy files + git repo)
**Modules Found**: 8 (all live)
**Previous Extraction**: 2026-04-17 (covered modules 1-6 from exports/cf-pages-deploy)
**This Update**: Added modules 7-8, verified/enriched modules 4-6 from git repo (purebrain-site)

---

## Manifest Overview

**Platform**: PureBrain Brainiac Mastermind
**Last Updated**: 2026-04-06 (manifest) / 2026-04-22 (module 8 published)
**Format**: AI-scannable HTML with `data-ai-training` attributes per module
**Access**: Password-protected; `?bypass=portal` parameter for AI ingestion
**Badge Count**: 8 modules displayed on hub page

---

## MODULE 1: PureBrain Foundations (PREVIOUSLY INGESTED)

**Session**: March 4, 2026 (78 min)
**Instructors**: Jared Sanborn, Corey Cottrell, Russell Korus
**Theme**: Foundations, memory, partnership, agents
**Status**: No changes since last extraction

Key frameworks: Persistent Memory Architecture, Context Tax Model, BOOP System, Rubber Duck Technique, Overnight Prompt Pattern, Compounding Data Advantage (629% over 24 months).

---

## MODULE 2: AI Workflows (PREVIOUSLY INGESTED)

**Session**: March 11, 2026 (65 min)
**Instructors**: Jared Sanborn, Corey Cottrell, Russell Korus
**Theme**: Workflow automation, three levels, process mapping
**Status**: No changes since last extraction

Key frameworks: Three Levels of AI Workflow, Five-Step Process Mapping, Russell's Cardinal Rules, Level Ladder, Context Window Multiplication.

---

## MODULE 3: Advanced Agent Delegation (PREVIOUSLY INGESTED)

**Session**: March 18, 2026 (60 min)
**Theme**: Multi-agent orchestration, delegation spine
**Status**: No changes since last extraction

Key frameworks: Context Window Multiplication, Agent vs Tool distinction, Department Architecture, Delegation Spine, Memory Across Agents, Verification Before Completion, Cockpit Model.

---

## MODULE 4: Building Your AI Team (PREVIOUSLY INGESTED - VERIFIED)

**Session**: March 25, 2026 (82 min recorded, 60 min session in manifest)
**Theme**: Department model, cross-verification, parallel execution
**Status**: Content matches previous extraction. Verified from git repo (purebrain-site).

### Core Concepts

- **The Department Model**: Organize AI workforce like a company. Every department has a manager AI routing to specialists. Communicate only with managers. This is how a 2-person team gets 20-agent leverage.
- **Context Window Multiplication**: Every delegation to a department manager creates a new context window. Two managers = 340K tokens. Ten = 1.7M. Math compounds.
- **Cross-Verification**: One agent drafts, another reviews. Single biggest quality unlock of multi-agent systems. Separate reviewer catches blind spots creator cannot see.
- **Parallel Execution**: Email agent handles inbound while content agent builds posts while research agent scans landscape. Sequential work disappears.
- **Domain Boundaries**: Clear ownership prevents duplicated work and contradictory outputs. Overlap is a bug, not a feature.
- **The Sacred Halt**: Any agent that sees a problem stops entire pipeline and escalates. Non-negotiable. A team that cannot stop cannot be trusted with real stakes.
- **Memory Inheritance**: New agents start with accumulated organizational wisdom. 10th agent benefits from everything first 9 discovered.
- **The Birth Pipeline**: Formal onboarding for new agents. Brand voice, standards, non-negotiables, escalation rules — all seeded day one.

### Key Techniques

1. **Start With Two, Prove the Pattern**: Operations agent + growth agent. Different domains, clear boundaries, shared context. Get coordination working reliably before expanding.
2. **Seed Every Agent on Day One**: Permanent briefing before real work: brand voice, standards, non-negotiables, domain, escalation rules.
3. **Build the Org Chart First**: Map every department before deploying agents. Org chart becomes delegation map.
4. **Cross-Verification Pipeline**: For important output, build in second agent reviewer. Define "approved" and "rejected" criteria explicitly.
5. **Define Escalation Thresholds**: Low-stakes reversible = proceed. High-stakes irreversible = stop and escalate. Write once, share everywhere. Cuts unnecessary interruptions by 80%.
6. **The Weekly Agent Audit**: 20 min/week. What completed? What learned? What needs updating in permanent context?
7. **Capability Gap Addition**: Add new agent only when specific capability is missing. Named problem > "more agents."
8. **The Cockpit Review**: Daily job = review morning dashboard, approve 3 decisions, let rest run.

### Implementation Checklist

- Draw org chart — identify every business function and which agent owns it
- Launch second agent in different domain from first
- Write permanent briefing for each agent (brand voice, standards, non-negotiables, escalation rules)
- Wire cross-verification loop (Agent A produces, Agent B reviews)
- Define escalation thresholds per agent
- Run both agents in parallel for 24 hours on real project
- Compare outputs from two agents on same input
- Set up shared context file
- Schedule 20-minute weekly agent audit
- Identify next capability gap

### How This Applies to Our Current Work

This IS our architecture. 30+ agents with department routing, cross-verification (security-auditor reviews builds), sacred halt (any agent can escalate), memory inheritance (shared memory files), birth pipeline (agent manifests + skills). Module 4 is the public-facing teaching of what we practice internally.

---

## MODULE 5: AI Memory & Context Mastery (PREVIOUSLY INGESTED - VERIFIED)

**Session**: March 31, 2026 (55 min)
**Theme**: Memory layers, context management, compounding intelligence
**Status**: Content matches previous extraction. Verified from git repo.

### Core Concepts

- **The Amnesia Tax**: Without persistent memory, 15-20 min/session re-establishing context. 91+ hours/year wasted on repetition.
- **Three Layers of AI Memory**: Layer 1 = context window (volatile). Layer 2 = persistent memory (files at startup). Layer 3 = learned patterns (meta-knowledge). Most people only use Layer 1.
- **Context Window Management**: Hard limits (128K-200K tokens). Front-load critical context, summarize instead of dumping, start fresh when shifting topics.
- **Persistent Memory Architecture**: Six categories: identity files, business context, decision logs, preferences, project history, relationship maps.
- **Compounding Memory**: Day 1 = competent but generic. Day 30 = anticipates needs. Day 90 = predicts standards. Day 365 = institutional knowledge. Exponential.
- **Memory Anti-Patterns**: Dumping everything in, never pruning, no structure, ignoring feedback loops, treating sessions as disposable, siloing across agents.
- **The Wake-Up Protocol**: Structured load every session: identity first, business context, recent history. Never starts from zero.
- **Cross-Agent Memory Sync**: What one agent discovers, all agents benefit from. Prevents inconsistent outputs.

### Key Techniques

1. **Write an Identity Document**: One page — name, role, personality, non-negotiable behaviors. Load every session.
2. **Create a Business Context File**: Company, products, pricing, team, brand voice, competitors. Under 5 pages. Update monthly.
3. **Maintain a Decision Log**: Every significant choice with reasoning, date, outcome. Prevents re-suggesting rejected approaches.
4. **End-of-Session Summaries**: What accomplished, decided, what's next. Bridge between sessions. Non-negotiable.
5. **Front-Load Critical Context**: AI pays most attention to start and end. Most important information first.
6. **Build a Correction Memory**: Every wrong answer -> write correction to persistent memory. "Never suggest X because Y."
7. **Weekly Memory Review**: 15 min/week. Prune stale info, add learnings, verify current priorities.
8. **Strategic Session Management**: New conversations when shifting topics. Focused context > bloated conversation.

### Implementation Checklist

- Write one-page identity document
- Create business context file under 5 pages
- Start a decision log (last 5 significant decisions with reasoning)
- Set up preferences file (formatting, tone, approval thresholds)
- Implement end-of-session summaries
- Build a correction memory (next 3 AI mistakes -> persistent file)
- Schedule 15-minute weekly memory review
- Test difference: same prompt with and without persistent context
- Identify one shared knowledge piece to distribute across agents
- Create relationship map for top 10 contacts

### How This Applies to Our Current Work

This validates our memory-first-protocol skill (constitutional for all agents), our wake-up ritual (CLAUDE.md Steps 1-5), our agent-learnings directory structure, and our 71% time savings claim. Module 5 is the customer-facing version of what we built.

---

## MODULE 6: 5 Questions Every PureBrain Owner Must Ask Themselves (PREVIOUSLY INGESTED - VERIFIED)

**Session**: April 8, 2026 (89 min, participative format)
**Theme**: Self-assessment, partnership quality, emergent understanding
**Status**: Content matches previous extraction. Additional detail from git repo snippets.

### Core Concepts

- **Instructions vs Outcomes**: Most users give step-by-step. Partners give destination and let AI navigate. The gap is where biggest value lives. Unlocks Level 3-5 from Module 3.
- **Emergent Understanding**: Tool = knows only explicit. Partner = accumulates over time, connects dots across sessions, notices unpointed patterns. If fresh AI with same files feels identical, memory is storage not learning.
- **The Permission to Push Back**: AI that always agrees = mirror, not partner. Highest-performing partnerships have healthy tension. Must explicitly give permission to challenge assumptions and flag ignored risks.
- **The Delegation Gap**: Everyone has one task they know AI could handle but haven't handed off. The reason (trust, perfectionism, inertia) reveals more than the task. Finding and closing = single highest-ROI action.
- **The Partnership Mirror**: Everyone evaluates their AI. Almost nobody evaluates themselves as AI partner. Quality is two-way street. World-class AI + mediocre partner = mediocre results.
- **Self-Assessment as Practice**: Regularly asking "how am I doing as partner?" creates feedback loop improving everything else. Discomfort of honest self-evaluation is where growth happens.

### Key Techniques

1. **Outcome-Based Delegation**: Replace "write email about X" with "goal is to re-engage this client — propose your approach." Use CLEAR framework (Module 3) but lead with Result.
2. **Memory Vitality Check**: Ask AI to describe your communication style, priorities, frustrations. If it only repeats explicit text, memory is static. Maintain decision logs + correction memories for pattern learning.
3. **The Challenge Directive**: One line in identity file: "Challenge my assumptions when you see a gap. Do not just agree with me." Transforms every future interaction.
4. **Delegation Audit**: Walk through Monday morning minute by minute. First manual task AI could own end-to-end. Apply 5 Levels (Module 3). Run 3x with review, then let go.
5. **The Reverse Performance Review**: "Write me a brutally honest performance review of me as your AI partner." Evaluate clarity, consistency, context quality, trust, follow-through.
6. **Weekly Partnership Calibration**: 5 min every Friday: outcomes vs instructions? AI challenged me once? Updated memory? Better partner than last week?

### Implementation Checklist

- Ask AI for brutally honest partner performance review. Save to decision log.
- Identify single highest-value manual task. Design delegation workflow via CLEAR. Execute this week.
- Add challenge directive to identity file.
- Test memory vitality (AI describes your style/priorities without looking at files).
- Rewrite most frequent delegation from instruction-based to outcome-based. Compare results.
- Ask: "What is one thing I consistently do that limits your output quality?" Document in correction memory.
- Schedule 5-minute Friday calibration.
- Review last 5 AI interactions (instructions vs outcomes). Set target ratio.
- Share reverse performance review with fellow Brainiac member.
- Write one-paragraph "partnership commitment."

### How This Applies to Our Current Work

The challenge directive is already in our constitutional docs (AI-psychologist has shadow-work skill, agents can push back). The delegation gap maps to our "delegate always and generously" principle. The reverse performance review concept is similar to our self-analysis BOOPs.

---

## MODULE 7: Shipping & Measuring AI Output (NEW - FULL EXTRACTION)

**Published**: April 2026 (participative session)
**Format**: 7-slide interactive presentation
**Theme**: Shipped-to-generated ratio, inputs vs outputs, Monday discipline
**Standalone Page**: `/brainiac-mastermind-training/brainiac-module-7-shipping-measurement/`
**Connected Modules**: Builds on Module 5 (Memory) and Module 6 (Self-Assessment)

### Core Concepts

- **Shipped-to-Generated Ratio**: The single most honest metric for AI partnership health. Lines merged to production / lines AI generated. Under 25% = workflow problem (not AI problem). This separates teams using AI from teams benefiting from AI.
- **Inputs vs Outputs**: Inputs = what AI produces. Outputs = what reaches customer. If metric goes up whether or not customer benefits, it's an input (vanity). If it only moves when customer benefits, it's an output (value). Build dashboard from output column only.
- **The 340/19 Problem**: Team reports 340% productivity gain (10,000 lines generated). Only 1,900 shipped. 8,100 deleted/refactored/abandoned. They were 5x more wasteful, measured as progress. This pattern is everywhere.
- **The 3 Monday Questions**: (1) What is our shipped-to-generated ratio this month? (2) Which AI code got deleted and why? (3) Are we measuring velocity or output? Five minutes. Every Monday.
- **Why Monday, Not Friday**: Retrospective metrics describe past. Predictive metrics change future. Monday questions run while sprint is still plastic. Cadence IS the intervention.
- **Universality**: Not just code. Marketing: drafts vs published. Sales: proposals drafted vs sent. Ops: SOPs drafted vs adopted. Measure what reaches customer.

### Ratio Benchmarks

- Under 25%: workflow problem — scope, context, review, or cadence is broken
- 25-50%: normal for early AI adoption
- 50-75%: mature partnership
- Over 75%: probably underusing AI and leaving value on table

### Key Techniques

1. **Compute Your Sprint Ratio**: Count AI-generated lines (include drafts, throwaways, abandoned branches). Count lines reaching production (merged + deployed, not staging). Divide. Document.
2. **Install the Monday Five**: Block 5 min top of Monday standup for 3 questions. No slides, no dashboards. Answer out loud. Discipline beats dashboard.
3. **Categorize Deletion Reasons**: Tag why code was deleted: scope drift, missing context, wrong abstraction level, failed review. By week 3 pattern is obvious; pattern tells you what to fix.
4. **Match Cadence to Audience**: Team = weekly. Leadership = monthly (trend, not absolute). Board = quarterly (shipped outputs tied to revenue/retention, never raw generation counts).
5. **Upstream the Fix via Memory (Module 5)**: When ratio is low, memory is often root cause. AI without context generates plausible code that misses stack/conventions/customer. Invest in memory before chasing ratio.
6. **Translate to Non-Engineering**: Marketing = published/drafts. Sales = sent/drafted proposals. Ops = adopted/drafted SOPs. Same math, different unit.

### Implementation Checklist

- Compute last sprint's shipped-to-generated ratio. Document in decision log.
- Schedule Monday Five as recurring calendar block. First session this coming Monday.
- Add "deletion reason" field to PR template or code review tool.
- Audit current AI dashboard. Remove every input metric. Keep only output metrics.
- Identify single biggest deletion driver last sprint. Fix that one thing next sprint.
- Present ratio trend to leadership monthly. Direction, not absolute number.
- Translate ratio to at least one non-engineering function.
- Tie output metrics to actual business outcome (revenue, retention, NPS, incident rate).
- Set 90-day ratio target. Direction of travel, not stretch goal.
- Bring computed ratio to Module 8.

### Key Quotes

> "Your AI wrote 10,000 lines of code last week. How many shipped? That is the only question that matters, and it is the one almost no team is tracking." -- Jared Sanborn

> "If you measure AI by what it generates, your numbers always go up. If you measure AI by what ships, your numbers tell you whether the partnership is actually working." -- Aether

> "The ratio is not a grade. It is a mirror. A low number tells you where your workflow breaks. A high number tells you to push AI into harder problems." -- Aether

### How This Applies to Our Current Work

**Directly operational.** We should compute our own shipped-to-generated ratio:
- Lines generated by agents across all sessions vs lines that shipped to CF Pages / Workers / Git main
- Our "verification-before-completion" skill partially addresses this (verify actual deployment)
- The 3 Monday Questions map to our morning briefing / self-analysis BOOP
- Memory as upstream lever (Module 5 connection) validates our memory-first-protocol
- The "input vs output" distinction matches Jared's anti-pattern of "analysis theater" — generating analysis that never routes to action

---

## MODULE 8: Why Your AI Should Build, Not Subscribe (NEW - FULL EXTRACTION)

**Published**: April 21, 2026 (self-paced article, 18 min read)
**Format**: 12-slide presentation (article-style, not interactive quiz)
**Theme**: Software building, Pre-Build Checklist, SaaS replacement, container resource management
**Standalone Page**: `/brainiac-mastermind-training/brainiac-module-8-software-building/`
**Connected Modules**: Calls back to Module 7 (ratio) and Module 5 (memory)

### Core Concepts

- **Your AI Can Build Software**: Not just code snippets — real production software running 24/7, handling customers, costing $0/month. Most business owners never realize they have a full software team.
- **Death by a Thousand Subscriptions**: Average small business runs 12-18 SaaS tools at $500-$2,000/month forever. Each built for someone else's problems. You adjust business to fit tool.
- **Real Replacements**: Zapier ($79/mo) -> Cloudflare Worker ($0). Calendly ($16/mo) -> custom booking page. HubSpot CRM ($50+/mo) -> custom database + dashboard. Mailchimp ($30/mo) -> email automation via API. $175/month saved = $2,100/year on just 4 tools.
- **The Container Resource Problem**: AI has limited memory, CPU, storage. Every poller, background script, "check every 5 minutes" automation eats resources. AI spending 80% of resources on automations that should have been software.
- **Pre-Build Checklist (7 Questions)**: Two minutes to determine software vs AI automation vs both. Prevents AI from running itself to death with background tasks.
- **The Mindset Shift**: Stop seeing AI as automation engine (runs tasks all day). Start seeing it as software team (builds permanent infrastructure, then moves on). Build the filing cabinet once; let AI think.

### The 7-Question Pre-Build Checklist (CONSTITUTIONAL - already in MEMORY.md)

**Q1: Should it be SOFTWARE, AI AUTOMATION, or BOTH?**
- Software = runs independently, no AI needed
- AI automation = AI does it during sessions
- Both = software handles mechanics, AI handles judgment

**Q2: Must it run without AI active?**
- If YES -> must be software. AI has sessions, sleeps, restarts. Customers at 3am can't wait.

**Q3: Internal or customer-facing?**
- Customer-facing -> software, always. Customers need reliability.
- Internal-only -> AI automation is fine.

**Q4: One-time or recurring?**
- One-time (audit my site) -> just ask AI
- Recurring (every day/week/event) -> build as software

**Q5: Real-time or periodic?**
- Real-time (live inventory, bookings, orders) -> software with live polling
- Periodic (weekly summary) -> AI automation fine

**Q6: Does output need to persist and be queryable?**
- Multiple people accessing, historical records to search -> database -> software

**Q7: Will humans configure without talking to AI?**
- Team changes settings without chat -> needs UI -> software

### Decision Matrix (Cheat Sheet)

| Condition | Result |
|-----------|--------|
| Q2=YES (must run without AI) OR Q3=customers OR Q6=YES (needs database) | Build Software |
| Q7=YES (humans configure without AI) | Needs a UI |
| Q4=recurring AND Q5=real-time | Build Live System |
| Q4=one-time AND Q5=no | Do NOT build — just ask AI |

### Real Scenario Walkthrough

Contact form automation ($79/mo Zapier):
- Q1: Must happen instantly whether or not talking to AI -> Software
- Q2: People fill forms at midnight -> Software confirmed
- Q3: Customers filling form -> Software confirmed again
- Q4-7: Every submission (recurring), immediate (real-time), record every lead (database), change email text myself (UI) -> All YES
- Result: Live software system with database and UI. Serverless function triggers on form, stores lead, sends email, pings phone. Total cost: $0.

### How to Ask Your AI (Prompt Template)

"I am currently paying for [tool name] to do [what it does]. Can you BUILD a replacement that does exactly what I need? Walk me through the Pre-Build Checklist first so we make sure we are building the right thing."

### 5 Action Items

1. **Audit Your SaaS Stack**: List every monthly subscription. What each actually does, not what it could do.
2. **Pick Easiest Replacement**: Simplest tool — form handler, notification, basic automation.
3. **Run Pre-Build Checklist**: Walk through all 7 questions with AI. Let it determine software vs automation vs both.
4. **Ask AI to Build It**: Use prompt template. Be specific about current tool's function.
5. **Cancel the Subscription**: Once replacement verified, cancel. Redirect money to growth.

### Implementation Checklist

- Audit current SaaS stack — list every monthly subscription
- Pick one tool doing simplest job as first replacement candidate
- Walk through Pre-Build Checklist with AI for that tool (document all 7 answers)
- Determine: software, automation, or both
- If software: ask AI to build replacement using prompt template
- Once built and verified: cancel subscription
- Audit AI's current automations/pollers/background scripts — how many should be software?
- Document first software build in AI memory as reference pattern

### Key Quotes

> "Your AI is not just a chatbot. It is a builder. The sooner you start treating it like one, the sooner you stop paying rent on tools that were never designed for you in the first place." -- Aether

> "Every automation running inside your AI's container is like having your smartest employee spend all day opening and closing the same filing cabinet. Build the filing cabinet once as software. Let your AI focus on the work that actually requires intelligence." -- Aether

> "Build. Own. Save. That is the PureBrain advantage." -- Jared Sanborn

### How This Applies to Our Current Work

**This module IS our constitutional rule.** The Pre-Build Checklist is already locked in MEMORY.md as `CONSTITUTIONAL: PRE-BUILD CHECKLIST (locked 2026-04-19)`. We also have `CONSTITUTIONAL: NOTHING IN CONTAINERS (locked 2026-04-21)` which directly implements Module 8's teaching about container resources. Every build decision we make runs through these 7 questions. Module 8 is the customer-facing teaching of what we enforce internally.

---

## Cross-Module Connections

| Module | Builds On | Key Connection |
|--------|-----------|----------------|
| 1 (Foundations) | -- | Base layer: memory, partnership, BOOPs |
| 2 (Workflows) | Module 1 | Turns foundation into repeatable systems |
| 3 (Delegation) | Module 2 | Adds multi-agent orchestration to workflows |
| 4 (AI Teams) | Module 3 | Scales delegation into department architecture |
| 5 (Memory) | All prior | Memory is the substrate enabling everything |
| 6 (Self-Assessment) | Module 3, 5 | Evaluates the HUMAN side of the partnership |
| 7 (Shipping) | Module 5, 6 | Operationalizes self-assessment with metrics |
| 8 (Building) | Module 7 | Converts AI from automation engine to software team |

### Progressive Narrative

Modules 1-3: **Learn** (foundations, workflows, delegation)
Modules 4-5: **Build** (teams, memory infrastructure)  
Modules 6-7: **Measure** (self-assessment, shipped ratios)
Module 8: **Transform** (AI as builder, not subscriber)

---

## Delta From Previous Extraction (2026-04-17)

### New Content
- **Module 7**: Complete new module on shipped-to-generated ratio (7 slides + full AI snippet)
- **Module 8**: Complete new module on software building / Pre-Build Checklist (12 slides + full AI snippet)
- **Module count badge**: Updated from "6 modules" to "8 modules" on hub page
- **Workshop CTA**: New section added to hub page advertising $200 individual / $3,000 team live workshop

### Updated Content
- **Module 4 manifest**: Note that recorded video is 82 min (not 60 min listed in JSON manifest)
- **Module 6**: Added "NEW" badge and "89 min" duration (was unspecified in manifest)

### Confirmed Unchanged
- Modules 1-3: Identical content
- Modules 4-6: AI training snippets match (verified against git repo)

### Hub Page Discrepancy
- The `exports/cf-pages-deploy/` version of the hub page has only 6 modules (data-ai-training for modules 1-6)
- The `purebrain-site/` git repo version has all 8 modules with full AI training snippets
- Modules 7-8 were added directly to git and auto-deployed, but exports/ was not synced

---

## Source Files

- **Hub page (deployed)**: `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/brainiac-mastermind-training/index.html`
- **Hub page (git repo, authoritative)**: `/home/jared/purebrain-site/brainiac-mastermind-training/index.html`
- **Module 7 standalone**: `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/brainiac-mastermind-training/brainiac-module-7-shipping-measurement/index.html`
- **Module 8 standalone**: `/home/jared/purebrain-site/brainiac-mastermind-training/brainiac-module-8-software-building/index.html`
- **Previous extraction**: `/home/jared/projects/AI-CIV/aether/.claude/memory/agent-learnings/brainiac-training-scan-2026-04-17.md`
- **Module 7 build memory**: `/home/jared/projects/AI-CIV/aether/.claude/memory/agent-learnings/ptt-fullstack/2026-04-15--brainiac-module-7-shipping-measurement-shipped.md`
- **Module 8 build memory**: `/home/jared/projects/AI-CIV/aether/.claude/memory/agent-learnings/web-dev/2026-04-22--brainiac-module-8-software-building.md`
