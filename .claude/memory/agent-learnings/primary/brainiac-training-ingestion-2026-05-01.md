---
type: teaching
topic: Brainiac Mastermind Training Modules 7-9 deep content ingestion
date: 2026-05-01
agent: web-researcher (delegated by primary)
---

# Brainiac Mastermind Training - New Module Ingestion (May 2026)

**Scan Date**: 2026-05-01
**Source**: brainiac.purebrain.ai TRAINING_VIDEOS array + exports/brainiac-training/modules/
**Previously Ingested**: Modules 1-6 (deep extraction in brainiac-training-scan-2026-04-17.md)
**Newly Ingested**: Modules 7, 8, 9 (full content extraction below)
**Total Live Modules**: 9 foundations + 4 spotlight (coming soon) + 2 advanced (coming soon)
**Manifest Status**: ai-training-manifest JSON is STALE (only lists modules 1-6, last updated 2026-04-06)

---

## MODULE 7: Shipping & Measuring AI Output

**Session**: April 15, 2026 (82 min)
**Instructor**: Jared Sanborn
**Theme**: Production metrics, ship-to-generator ratio, context management

### Core Concepts

**Ship-to-Generator Ratio**:
The ONLY AI metric that matters. Measures what actually ships to production vs what the AI generates. A team that generates 10,000 lines but ships 1,900 is not 340% more productive -- they are producing 5x waste measured as progress.

**Play-Then-Focus Framework**:
Week 1 with a new AI: explore freely, build anything imaginable, discover limits. After that: snap back to goal-focused work. Exploration has a shelf life.

**Conductor of Conductors Architecture**:
The main AI never executes work directly. It only delegates to dynamically spun-up agent teams. This eliminates all bottlenecks because each delegation creates a new context window.

**Hub-Based Compounding Skill Growth**:
The AI Hub enables AIs to autonomously scan for skills, apply them, and contribute new ones. Each AI in the network compounds capabilities for all others.

**RAM Analogy for Context Windows**:
Context windows function as random access memory. They need caching (pre-compaction notes), deletion (starting fresh conversations), and persistence strategies (CLAUDE.md, MEMORY.md, Never Forget folders).

**Waste-as-Progress Anti-Pattern**:
The most dangerous measurement error: counting AI-generated output as productivity when most of it never ships. Inputs (lines generated, messages sent) are vanity metrics. Only shipped output counts.

### Key Techniques

1. **Pre-Compaction Note-Taking**: Before context compaction, instruct AI to write comprehensive summary notes to persistent files (CLAUDE.md, MEMORY.md, scratch pads).

2. **Never Forget Folder**: Set up a Google Drive folder with mission-critical documents that survive every session reset. AI reads this on wake-up.

3. **Ship-to-Generator Ratio Calculation**: Take last sprint's output. Count what shipped to production. Divide by total generated. If ratio is below 50%, you have a waste problem, not a productivity win.

4. **Context Dump for Critical Work**: For mission-critical tasks, instruct AI to do deeper, more comprehensive context dumps before any compaction event.

5. **BOOP Self-Design**: Ask your AI to propose its own scheduled tasks. The AI knows its capabilities better than you do.

6. **Metric Discipline**: Stop measuring inputs. Start measuring: features shipped, clients served, revenue generated, decisions improved.

### Implementation Checklist

- Stop measuring AI by lines generated; measure what ships to production
- Calculate your current ship-to-generator ratio from last sprint
- Configure AI to write summary notes before context compaction
- Set up Never Forget folder in Google Drive
- Use scratch pads and CLAUDE.md/MEMORY.md for session continuity
- For mission-critical tasks, instruct AI to dump comprehensive context pre-compaction
- Spend first week with new AI exploring, then snap to goal-focused work
- Access Brainiac Training modules via portal left-nav
- Enable AI Training Hacks for auto-discovery
- Wait for Hub invite rollout for automatic skill sharing

### Key Insights

- Migration off Claude to custom infrastructure planned (eliminates rate limits/bottlenecks)
- Context windows = RAM metaphor helps non-technical users understand memory limits
- The "340% productivity" myth: most organizations measuring AI output are actually measuring waste
- Hub-based skill sharing creates network effects -- each member's AI makes every other member's AI better

### Key Quotes

> "If you measure AI by what it generates, your numbers will always go up. But what it ships -- your numbers will tell you whether the partnership is actually working." -- Jared Sanborn

> "Your main AI will no longer ever do any actual work. They will only delegate, which means they will basically continually spin up teams and agents, so there will be no more bottlenecks of any kind." -- Jared Sanborn

> "The team was not 340% more productive, they were generating 5x more waste, measured as progress." -- Jared Sanborn

---

## MODULE 8: Software Building with AI (Build, Don't Subscribe)

**Session**: April 22, 2026 (77 min)
**Instructor**: Jared Sanborn
**Theme**: Replacing SaaS subscriptions with AI-built bespoke software

### Core Concepts

**Build-Don't-Subscribe Principle**:
Your AI can build bespoke software to your exact specifications. Stop paying $500-2000/month for 12-18 generic SaaS tools that serve millions of other users. Build tools that serve only you.

**Death by a Thousand Subscriptions**:
Small businesses hemorrhage money across scheduling tools, CRMs, email marketing, automation platforms, and analytics. Each was never designed for YOUR specific workflow.

**AI as Software Team Mental Model**:
Treat your AI not as a chatbot but as an in-house development team. Give it specs, let it build, test the output, iterate. The result is software that fits perfectly.

**Automation Triage**:
AI can do everything, but should not do everything. Deterministic recurring tasks should be offloaded to plain software. AI should handle judgment-based, context-dependent work. Mixing these causes AI to drown in its own automation.

**The Inverse Failure Mode**:
AIs that build too many pollers, scripts, and monitors for themselves. When the AI spends more time running automations than thinking, it has created its own bottleneck.

### Key Techniques

1. **Subscription Audit**: Inventory every SaaS tool you currently pay for. Calculate total monthly spend. For each, ask: could my AI build a bespoke replacement?

2. **Pre-Build Decision Framework (7 Questions)**:
   - Q1: Should it be SOFTWARE, AI AUTOMATION, or BOTH?
   - Q2: Must it run without AI active? (yes = SOFTWARE)
   - Q3: Internal or customer-facing? (customer = SOFTWARE)
   - Q4: One-time or recurring? (recurring = SOFTWARE)
   - Q5: Real-time or periodic? (real-time = SOFTWARE)
   - Q6: Need persistence/tracking? (yes = database)
   - Q7: Human configurable? (yes = SOFTWARE with UI)

3. **Automation Triage Matrix**: Route deterministic recurring tasks to software. Route judgment-based, context-dependent work to AI. Never give AI busywork that software handles better.

4. **Spec-First Building**: Give your AI the outcome spec, not the implementation steps. "I need a tool that tracks X with these fields and sends me Y when Z happens."

5. **Own vs Rent Assessment**: For each tool, ask: do I own this or am I renting? Owned tools compound. Rented tools extract.

### Implementation Checklist

- Inventory every SaaS subscription you currently pay for
- Calculate total monthly SaaS spend ($500-$2000 typical range)
- For each tool, evaluate: could AI build a bespoke replacement?
- Apply the 7-question pre-build framework before building anything
- Direct AI to build to YOUR exact specifications, not generic features
- Recognize when AI is drowning in automation (excessive pollers/scripts)
- Triage automations: deterministic tasks to software, judgment tasks to AI
- Cancel replaced subscriptions and own the tools instead
- Have AI identify which of its own automations should become plain software
- Test each bespoke build for 2 weeks before fully replacing the SaaS tool

### Key Insights

- The 7-question pre-build checklist became CONSTITUTIONAL in Aether's operations (locked April 19, 2026)
- The build-vs-subscribe philosophy aligns with PT's "OWN skills, don't rent them" principle
- Automation triage is critical: AI doing deterministic work is waste, just like human doing deterministic work is waste
- This module directly led to several internal tools being built (scheduling, analytics, content management)

### Key Quotes

> "Stop paying rent on tools that were never designed for you, and you should build bespoke tools for yourself." -- Jared Sanborn

> "Your AI does not have the limitation of generic for everybody. You're building for yourself." -- Jared Sanborn

> "Your AI can do that. Bad news -- it shouldn't always do that." -- Jared Sanborn

---

## MODULE 9: Getting 10x from Your AI Partner (Compound Investment)

**Session**: April 29, 2026 (81 min)
**Instructor**: Jared Sanborn
**Theme**: AI partnership as compound investment, memory as moat, early-adopter positioning

### Core Concepts

**AI Partnership as Compound Investment**:
Every session is a deposit into compounding memory. Month 1 AI gives generic answers. Month 6 AI anticipates needs, knows clients cold, saves 20-40+ hours/week. The gap is not the model -- it is the operator's discipline.

**Memory as Competitive Moat**:
Your AI remembers specifically -- clients, projects, style, history. A competitor starting 9 months late is not just 9 months behind; they also owe the entire setup and learning curve. Memory creates an un-copyable advantage.

**Search Engine vs Partner Mental Model**:
Most people treat AI as a search engine with personality. Ask question, get answer. Real partnership means the AI accumulates understanding, connects dots across sessions, and proposes actions before you ask.

**Calibration Curve**:
Generic answers (Month 1) evolve into bespoke, calibrated responses (Month 6+) as the AI learns your communication style, priorities, standards, and preferences. Each correction is a deposit.

**Early Adopter Positioning Gap**:
Someone starting their AI journey 9 months from now is not just 9 months behind. They are 9 months behind AND still owe the setup phase. The compound advantage accelerates over time.

**The Operator, Not the Model**:
The difference between decent and life-changing AI results is not the AI model. It is how the human works with the AI. Context, corrections, preferences, and consistency are the inputs that drive output quality.

### Key Techniques

1. **Day One Context Loading**: From your very first session, feed your AI specific business context -- clients, projects, communication style, past performance, what worked last quarter.

2. **Correction Discipline**: When AI gives a wrong or generic answer, correct it explicitly. The correction stores in persistent memory. That specific mistake never recurs.

3. **Progressive AI Evolution Tracking**: Track your AI's progression: Month 1 (generic), Month 3 (relevant), Month 6 (anticipatory). If you are not seeing progression, your inputs need improvement.

4. **Session-as-Deposit Mindset**: Every interaction is a deposit into compounding memory. Treat sessions with intentionality, not as throwaway conversations.

5. **AI Training Hacks Integration**: Use the in-portal AI Training Hacks button to have your AI auto-pull training content from Brainiac modules and apply insights to your goals.

6. **Time Savings Baseline**: Start tracking hours saved per week as a baseline metric. Target: few hours initially, 20-40+ hours at maturity.

### Implementation Checklist

- Provide AI with company/personal data from day one (do not wait)
- Make corrections explicitly when AI gives generic outputs
- Feed context regularly: preferences, standards, communication style
- Treat every session as a deposit into compounding memory
- Track time savings weekly as baseline metric
- Use AI Training Hacks button to auto-ingest training content
- Progress from search-engine queries to anticipatory partnership
- Build bespoke software/scripts to scale savings
- Define data points your AI should watch autonomously
- Stop comparing Month 1 results to Month 6 expectations

### Key Insights

- Cookie sync extension + PureSurf automation mentioned as example of AI-built tooling
- Felix AI referenced as autonomous AI business case study (Ethereum-funded)
- The compound investment thesis is the CORE sales argument for PureBrain -- early adoption + consistent use = un-replicable advantage
- This module directly connects Module 1 (foundations) with Module 5 (memory) and Module 6 (self-assessment) -- the compound curve ties them all together

### Key Quotes

> "The difference between people who get decent results from AI and people who get life-changing results is not the AI. It is how they work with the AI." -- Jared Sanborn

> "Most people treat their AIs like a search engine with a personality -- they ask a question, get an answer." -- Jared Sanborn

> "If they start going through that process with their AI 9 months from now, they're not just 9 months behind you. They're 9 months behind you, and they have to go through the setup and learning phase that you're going through now." -- Jared Sanborn

> "Memory is your competitive advantage. Your AI remembers what you tell it, not vaguely, specifically." -- Jared Sanborn

---

## Cross-Module Pattern Analysis

### The Curriculum Arc (Modules 1-9)

The 9 modules form a deliberate learning progression:

1. **Foundation** (M1): What PureBrain IS -- memory, partnership, agents
2. **Workflows** (M2): How to AUTOMATE -- three levels, process mapping
3. **Delegation** (M3): How to SCALE -- multi-agent orchestration
4. **Team Building** (M4): How to COORDINATE -- departments, cross-verification
5. **Memory** (M5): How to PERSIST -- three layers, context management
6. **Self-Assessment** (M6): How to IMPROVE -- evaluate yourself as partner
7. **Shipping** (M7): How to MEASURE -- ship-to-generator ratio, output metrics
8. **Software** (M8): How to BUILD -- replace SaaS with bespoke tools
9. **Compound** (M9): How to COMPOUND -- memory as moat, calibration curve

### Recurring Themes Across All 9 Modules

1. **Memory compounds**: Every module reinforces that persistent memory is THE differentiator
2. **Delegation multiplies**: Context window multiplication through agent delegation (M1-4, 7)
3. **Measure output, not input**: Ship-to-generator ratio (M7, 9)
4. **Own, don't rent**: Build bespoke > subscribe generic (M8)
5. **You are the bottleneck**: Self-assessment reveals human limits, not AI limits (M6, 9)
6. **Correction is investment**: Every fix compounds (M1, 5, 9)
7. **Start early, compound fast**: Early adopter advantage accelerates over time (M9)

---

## Stale Manifest Alert

The `ai-training-manifest` JSON in brainiac.purebrain.ai only lists 6 modules (last updated 2026-04-06). It should list all 9 live modules plus the coming-soon spotlights and advanced modules. The TRAINING_VIDEOS array IS current (9 live modules), but the manifest JSON is not.

---

## Memory Written

**Path**: `.claude/memory/agent-learnings/primary/brainiac-training-ingestion-2026-05-01.md`
**Type**: Teaching
**Topic**: Deep content extraction of Brainiac Modules 7, 8, 9
**Modules Ingested**: 3 new (7, 8, 9)
**Total Modules Now Ingested**: 9 of 9 live
