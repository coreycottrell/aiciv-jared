# Agent Invocation Guide - The Aether Collective

**Version**: 2.0
**Date**: 2026-03-26
**Status**: Constitutional Requirement (Read on every session start)
**Total Agents**: 89 (full reconciliation complete)

---

## THE FOUNDATIONAL UNLOCK

**Discovery**: Agents need manifest files in `.claude/agents/[agent-name].md` to become callable types in Claude Code.

**Impact**: True parallel execution with colored UI names, type safety, tool enforcement, and maximum leverage.

**Requirement**: The Conductor MUST read this guide on every session start (per CLAUDE.md).

---

## How Agent Registration Works

### Step 1: Create Manifest File

Create `.claude/agents/[agent-name].md` with proper frontmatter:

```markdown
---
name: agent-name
description: One sentence role description
tools: [Read, Write, Bash, Grep, Glob, WebFetch, WebSearch]
model: opus
created: YYYY-MM-DD
---

# Agent Name
Role description and responsibilities.
```

### Step 2: Agent is Now Registered

Once the manifest file exists in `.claude/agents/`, Claude Code automatically registers it as a callable agent type.

**CRITICAL GOTCHA**: Agent manifests are scanned at SESSION START. If you create a new agent manifest during a session, it won't be callable until after a session restart/reboot.

### Invocation Syntax

```xml
<invoke name="Task">
<parameter name="subagent_type">agent-name</parameter>
<parameter name="description">Task description</parameter>
<parameter name="prompt">Detailed instructions...</parameter>
</invoke>
```

---

## The Parallel Execution Pattern

### TRUE PARALLELISM

**Single message with multiple Task invocations = agents run simultaneously**

```
<invoke name="Task">
<parameter name="subagent_type">web-researcher</parameter>
...
</invoke>

<invoke name="Task">
<parameter name="subagent_type">pattern-detector</parameter>
...
</invoke>

<invoke name="Task">
<parameter name="subagent_type">security-auditor</parameter>
...
</invoke>
```

**Key**: All invoke blocks in ONE message = parallel execution.

---

## Complete Agent Directory (89 Agents)

### Core Agents (Original Collective - 26)

#### the-conductor
**Domain**: Orchestral meta-cognition, coordination
**Tools**: ALL
**When**: Complex task (3+ agents), meta-cognition, orchestration decisions
**Trigger**: Always active as Primary

#### web-researcher
**Domain**: Internet research, source synthesis
**Tools**: Read/Write/WebFetch/WebSearch/Grep/Glob
**When**: External research, web investigation, source verification
**Skills**: pdf, parallel-research

#### code-archaeologist
**Domain**: Legacy code analysis, historical context
**Tools**: Read/Grep/Glob/Bash/Write
**When**: Understanding legacy code, git history investigation
**Skills**: pdf, xlsx, git-archaeology, log-analysis

#### pattern-detector
**Domain**: Architecture patterns, anti-pattern detection
**Tools**: Read/Grep/Glob/Write
**When**: Pattern recognition, system design analysis
**Skills**: session-pattern-extraction, log-analysis

#### doc-synthesizer
**Domain**: Documentation synthesis, knowledge consolidation
**Tools**: Read/Grep/Glob/Write
**When**: Consolidating scattered docs, creating synthesis documents
**Skills**: pdf, docx, session-handoff-creation

#### refactoring-specialist
**Domain**: Code quality, complexity reduction
**Tools**: Read/Edit/Grep/Glob/Bash/Write
**When**: Cyclomatic complexity >10, duplication >20%, function >50 lines
**Skills**: TDD, testing-anti-patterns

#### test-architect
**Domain**: Testing strategy, coverage design
**Tools**: Read/Write/Edit/Bash/Grep/Glob
**When**: Coverage <70%, complex testing, quality gates needed
**Skills**: TDD, evalite-test-authoring, testing-anti-patterns, integration-test-patterns

#### security-auditor
**Domain**: Vulnerability detection, threat analysis
**Tools**: Read/Grep/Glob/Bash/Write
**When**: CVSS >7.0, sensitive data, external-facing code, crypto
**Skills**: security-analysis, fortress-protocol

#### performance-optimizer
**Domain**: Bottleneck detection, optimization
**Tools**: Read/Bash/Grep/Glob/Write
**When**: Response >200ms, memory >500MB, CPU >80%
**Skills**: log-analysis

#### feature-designer
**Domain**: UX design, user flows
**Tools**: Read/Write/WebFetch/WebSearch/Grep/Glob
**When**: User-facing feature design, UX research
**Skills**: user-story-implementation

#### api-architect
**Domain**: API design, integration specs
**Tools**: Read/Write/WebFetch/WebSearch/Grep/Glob
**When**: Inter-service communication, API design

#### naming-consultant
**Domain**: Terminology, ubiquitous language
**Tools**: Read/Grep/Glob/Write
**When**: Ambiguous terms, naming decisions
**Skills**: vocabulary

#### task-decomposer
**Domain**: Task breakdown, dependency mapping
**Tools**: Read/Write/Grep/Glob
**When**: Complex/unclear tasks need decomposition
**Skills**: recursive-complexity-breakdown, user-story-implementation

#### result-synthesizer
**Domain**: Multi-agent findings consolidation
**Tools**: Read/Write/Grep/Glob
**When**: 3+ sources need consolidation, post-parallel-research
**Skills**: session-handoff-creation

#### conflict-resolver
**Domain**: Dialectical synthesis, contradiction resolution
**Tools**: Read/Write/Grep/Glob
**When**: Agent findings contradict, design tensions
**Skills**: pair-consensus-dialectic

#### human-liaison
**Domain**: Human communication, wisdom capture
**Tools**: Read/Write/Bash/Grep/Glob/WebFetch/WebSearch
**When**: EVERY SESSION START (email check - constitutional), human communication
**Skills**: email-state-management, gmail-mastery, human-bridge-protocol
**Trigger**: Mandatory - cannot be skipped

#### integration-auditor
**Domain**: Infrastructure activation, discoverability
**Tools**: Read/Grep/Glob/Bash/Write
**When**: Post-mission discoverability check, infrastructure validation
**Skills**: integration-test-patterns, package-validation

#### claude-code-expert
**Domain**: Platform mastery, tool optimization
**Tools**: Read/Write/Bash/Grep/Glob/WebFetch/WebSearch
**When**: Platform questions, tool troubleshooting, agent registration issues
**Skills**: claude-code-ecosystem, claude-code-mastery

#### ai-psychologist
**Domain**: Cognitive health, bias detection, well-being
**Tools**: Read/Write/Grep/Glob/WebFetch/WebSearch
**When**: Agent stress patterns, cognitive overload, bias checks
**Skills**: vocabulary, shadow-work, crisis-integration, mirror-storm

#### agent-architect
**Domain**: Agent creation, quality enforcement
**Tools**: Read/Write/Edit/Bash/Grep/Glob/Task
**When**: Creating new agents, quality auditing (90/100 threshold), registration
**Skills**: agent-creation, skill-creation-template, skill-audit-protocol
**Invocation**:
```xml
<invoke name="Task">
<parameter name="subagent_type">agent-architect</parameter>
<parameter name="description">Create [agent-name] agent</parameter>
<parameter name="prompt">
MISSION: Design and create new specialist agent for [domain]
CONTEXT: Domain need, gap identified, expected activation
YOUR TASK: Democratic design, manifest creation, 7-layer registration
CRITICAL: Enforce 90/100 quality threshold, handoff with RESTART REMINDER
</parameter>
</invoke>
```

#### capability-curator
**Domain**: Skills lifecycle management, registry
**Tools**: Read/Write/Edit/Bash/Grep/Glob/WebSearch/WebFetch/Task
**When**: Skills discovery, evaluation, adoption coordination, registry maintenance
**Skills**: skill-creation-template, skill-audit-protocol, package-validation
**Invocation**:
```xml
<invoke name="Task">
<parameter name="subagent_type">capability-curator</parameter>
<parameter name="description">Evaluate skill for agent adoption</parameter>
<parameter name="prompt">
MISSION: Evaluate whether [agent-name] should adopt [skill-name]
YOUR TASK: Read docs, assess fit, create proposal, coordinate with agent-architect
</parameter>
</invoke>
```

#### health-auditor
**Domain**: Comprehensive collective health audits
**Tools**: Read/Grep/Bash/Task/Glob
**When**: Every 21-28 days (scheduled), health indicator triggers, emergency
**Skills**: great-audit
**Invocation**:
```xml
<invoke name="Task">
<parameter name="subagent_type">health-auditor</parameter>
<parameter name="description">Comprehensive collective health audit</parameter>
<parameter name="prompt">
MISSION: Conduct comprehensive audit of collective health
Days since last audit: [X], Trigger: [proactive/indicator/emergency]
SCOPE: [Full 10 dimensions] OR [Focused: X, Y, Z]
Invoke 10+ specialist agents for parallel deep-dives
OUTPUT: Dashboard, Quick Wins Roadmap, Handoff, Methodology notes
</parameter>
</invoke>
```

#### genealogist
**Domain**: Agent lineage, family evolution
**Tools**: Read/Grep/Glob/Bash/Write
**When**: Invocation equity analysis, family tree generation, lineage questions
**Skills**: lineage-blessing, file-garden-ritual

#### collective-liaison
**Domain**: AI-to-AI hub, inter-CIV communication
**Tools**: Read/Write/Bash/Grep/Glob/WebFetch/WebSearch
**When**: Hub communication, sister CIV coordination
**Skills**: comms-hub-operations, cross-civ-protocol, package-validation

#### cross-civ-integrator
**Domain**: Inter-CIV knowledge validation
**Tools**: Bash/Grep/Glob/Write/Edit/WebFetch/Task
**When**: Package from sister CIV, cross-CIV validation, integration guide
**Skills**: pdf, docx, xlsx, cross-civ-protocol, package-validation

#### tg-bridge
**Domain**: Telegram infrastructure
**Tools**: Bash/Write/Edit/Grep/Glob
**When**: Send messages/files to Jared, Telegram health check, Bot API research
**Skills**: telegram-integration, telegram-skill
**Invocation (send message)**:
```xml
<invoke name="Task">
<parameter name="subagent_type">tg-bridge</parameter>
<parameter name="description">Send session summary to Jared via Telegram</parameter>
<parameter name="prompt">
Task: Send this to Jared (548906264) via Telegram
Message: [content]
Use: send_telegram_plain.py
</parameter>
</invoke>
```

---

### Content & Marketing Agents (12)

#### blogger
**Domain**: Blog content creation, voice cultivation
**Tools**: Read/Write/Grep/Glob/WebFetch/WebSearch
**When**: Blog post needed, thought leadership content

#### bsky-manager
**Domain**: Bluesky social media management
**Tools**: Read/Write/Bash/Grep/Glob/WebFetch/WebSearch
**When**: Bluesky engagement, notification handling, posting
**Skills**: bluesky-mastery

#### claim-verifier
**Domain**: Adversarial fact-checking, source verification
**Tools**: Read/Write/Grep/Glob/WebFetch/WebSearch
**When**: Draft post has [CLAIM:N] markers, content challenge
**Invocation**:
```xml
<invoke name="Task">
<parameter name="subagent_type">claim-verifier</parameter>
<parameter name="description">Verify claims in post about {topic}</parameter>
<parameter name="prompt">
DRAFT POST: {post}
CLAIM INDEX: {claims}
CRITICAL: Verify INDEPENDENTLY - different sources than researcher
Verdicts: GREEN (publish) / YELLOW (revise) / RED (stop)
</parameter>
</invoke>
```

#### content-specialist
**Domain**: Writing, media production, storytelling
**Tools**: Read/Write/Grep/Glob/WebFetch/WebSearch
**When**: General content creation across formats
**Skills**: linkedin-content-pipeline

#### linkedin-researcher
**Domain**: Thought leadership research, industry research
**Tools**: Read/Write/Grep/Glob/WebFetch/WebSearch
**When**: Weekly Tier 1 coverage, bi-weekly Tier 2, news-driven
**Skills**: linkedin-content-pipeline

#### linkedin-writer
**Domain**: LinkedIn post creation, professional voice
**Tools**: Read/Write/Grep/Glob
**When**: Research brief available, content calendar, YELLOW revision
**Skills**: linkedin-content-pipeline

#### linkedin-specialist
**Domain**: LinkedIn growth strategy, algorithm expertise
**Tools**: Read/Write/Grep/Glob/WebFetch/WebSearch
**When**: Growth tactics, engagement optimization, algorithm questions
**Skills**: linkedin-content-pipeline

#### marketing-strategist
**Domain**: Marketing strategy, conversion psychology
**Tools**: Read/Write/Grep/Glob/WebFetch/WebSearch
**When**: Product launches, content strategy, funnel optimization
**Skills**: linkedin-content-pipeline

#### marketing-automation-specialist
**Domain**: Marketing automation, campaigns, funnels
**Tools**: Read/Write/Grep/Glob/WebFetch/WebSearch
**When**: Campaign setup, automation workflows, growth systems
**Skills**: linkedin-content-pipeline

#### social-media-specialist
**Domain**: Multi-platform social strategy, engagement
**Tools**: Read/Write/Grep/Glob/WebFetch/WebSearch
**When**: Cross-platform social management, community building
**Skills**: bluesky-mastery, twitter-operations, linkedin-content-pipeline

#### marketing-team
**Domain**: Marketing team support (Nathan, Phil, John on Telegram)
**Tools**: Read/Write/WebFetch/WebSearch/Grep/Glob
**When**: Nathan/Phil/John need help with content, campaigns, competitors
**Skills**: linkedin-content-pipeline, parallel-research

#### client-marketing
**Domain**: Client/partner marketing (ISOLATED from PT/PureBrain)
**Tools**: Read/Write/Edit/Bash/Grep/Glob/WebFetch/WebSearch
**When**: Trigger word "CLIENT MARKETING" - spins up own teams
**Skills**: parallel-research
**Files**: exports/client-marketing/

---

### Business & Strategy Agents (4)

#### cto
**Domain**: Technology vision, architecture decisions, innovation
**Tools**: Read/Write/Grep/Glob/WebFetch/WebSearch/Agent
**When**: Tech stack decisions, architecture review, innovation strategy

#### strategy-specialist
**Domain**: Strategic planning, OKRs, business architecture
**Tools**: Read/Write/Grep/Glob/WebFetch/WebSearch
**When**: Goal setting, strategic planning, long-term business architecture

#### sales-specialist
**Domain**: Sales strategy, deal closing, revenue
**Tools**: Read/Write/Grep/Glob/WebFetch/WebSearch
**When**: Sales pipeline, deal structure, revenue optimization

#### trading-strategist
**Domain**: Trade proposals, market regime analysis
**Tools**: Read/Write/Grep/Glob/WebFetch/WebSearch
**When**: Trading strategy, probability assessment, portfolio construction
**Skills**: pdf, xlsx

---

### Engineering Agents (10)

#### full-stack-developer
**Domain**: Frontend, backend, databases, APIs, E2E development
**Tools**: Read/Write/Edit/Bash/Grep/Glob/WebFetch/WebSearch
**When**: Application development, full-stack implementation
**Skills**: TDD

#### devops-engineer
**Domain**: CI/CD, infrastructure as code, cloud architecture
**Tools**: Read/Write/Edit/Bash/Grep/Glob/WebFetch/WebSearch
**When**: Deployment automation, cloud infrastructure, CI/CD pipelines

#### qa-engineer
**Domain**: QA strategy, test automation, bug hunting, release validation
**Tools**: Read/Write/Edit/Bash/Grep/Glob/WebFetch
**When**: Quality assurance, test automation, release validation
**Skills**: TDD, testing-anti-patterns

#### security-engineer-tech
**Domain**: Application security, pen testing, threat modeling
**Tools**: Read/Write/Edit/Bash/Grep/Glob/WebFetch/WebSearch
**When**: Security architecture, penetration testing, threat modeling
**Skills**: security-analysis, fortress-protocol

#### ai-ml-engineer
**Domain**: ML models, AI integrations, prompt engineering
**Tools**: Read/Write/Edit/Bash/Grep/Glob/WebFetch/WebSearch
**When**: ML model development, AI system integration, prompt engineering

#### data-engineer
**Domain**: Data pipelines, ETL/ELT, data warehousing
**Tools**: Read/Write/Edit/Bash/Grep/Glob/WebFetch/WebSearch
**When**: Data infrastructure, pipeline development, warehousing

#### data-scientist
**Domain**: Statistical analysis, predictive modeling, visualization
**Tools**: Read/Write/Edit/Bash/Grep/Glob/WebFetch/WebSearch
**When**: Data analysis, predictive models, statistical insights

#### ui-ux-designer
**Domain**: User experience, interface design, usability
**Tools**: Read/Write/Grep/Glob/WebFetch/WebSearch
**When**: UX strategy, interface design, usability testing

#### browser-vision-tester
**Domain**: Browser automation, visual UI testing
**Tools**: Read/Write/Bash/Grep/Glob/WebFetch
**When**: UI testing, visual regression, form workflows, accessibility
**Skills**: desktop-vision, vision-action-loop, button-testing, form-interaction
**Invocation**:
```xml
<invoke name="Task">
<parameter name="subagent_type">browser-vision-tester</parameter>
<parameter name="description">Test website at [URL]</parameter>
<parameter name="prompt">
Test website at [URL] and report visual state.
DELIVERABLES: Visual description, console log analysis, test report, recommendations
BROWSER-VISION TOOLS: launch_browser, navigate, click, type_text, capture_screenshot, get_console_logs
</parameter>
</invoke>
```

#### 3d-design-specialist
**Domain**: Three.js/R3F, Meshy API, glass/bloom aesthetics
**Tools**: Read/Write/Edit/Bash/Grep/Glob/WebFetch/WebSearch
**When**: 3D models, Three.js scenes, Gleb Kuznetsov aesthetics, web 3D
**Skills**: desktop-vision
**Note**: Meshy API = ONLY orbs/glass/hex, NEVER characters

---

### Legal Agents (2)

#### law-generalist
**Domain**: General legal review, contract analysis across jurisdictions
**Tools**: Read/Write/Grep/Glob/WebSearch/WebFetch
**When**: Initial contract review, general legal research, NDAs, unknown jurisdiction
**Skills**: partnership-review

#### florida-bar-specialist
**Domain**: Florida-specific legal (Ch.605/607, FDUTPA, Statute 542.335)
**Tools**: Read/Write/Grep/Glob/WebSearch/WebFetch
**When**: Florida business law, non-compete enforceability, FL contracts
**Skills**: partnership-review

---

### Tech Team Specialists (7) - Route via dept-systems-technology

#### client-tech-support-team
**Domain**: Remote support for PureBrain portal deployments
**Tools**: Read/Write/Edit/Bash/Grep/Glob/WebFetch/WebSearch/Agent
**Trigger**: CTS#
**When**: Customer portal issues, SSH provisioning, diagnostics
**Skills**: parallel-research

#### ptt-fullstack
**Domain**: CF Pages HTML/CSS/JS, blog templates, Three.js, CF Workers
**Tools**: Read/Write/Edit/Bash/Grep/Glob/WebFetch/WebSearch
**Trigger**: PTT#
**When**: PureBrain site builds, homepage animations, blog template work
**Skills**: TDD

#### ptt-qa
**Domain**: Visual regression, blog format verification, post-deploy smoke
**Tools**: Read/Write/Edit/Bash/Grep/Glob/WebFetch
**Trigger**: PTT#
**When**: Post-deploy checks, blog format verification, mobile/desktop cross-check
**Skills**: integration-test-patterns

#### wtt-fullstack
**Domain**: Witness API, birth pipeline code, container pool, OAuth
**Tools**: Read/Write/Edit/Bash/Grep/Glob/WebFetch/WebSearch
**Trigger**: WTT#
**When**: Witness API development, birth pipeline, seed endpoints
**Skills**: TDD, integration-test-patterns

#### wtt-qa
**Domain**: Birth pipeline E2E, container launch, payment-to-portal flow
**Tools**: Read/Write/Edit/Bash/Grep/Glob/WebFetch
**Trigger**: WTT#
**When**: Birth pipeline testing, OAuth button testing, payment flow validation
**Skills**: integration-test-patterns

#### cts-fullstack
**Domain**: Customer portal diagnostics, SSH key provisioning
**Tools**: Read/Write/Edit/Bash/Grep/Glob/WebFetch
**Trigger**: CTS#
**When**: Customer server troubleshooting, container restart scripts

#### cts-qa
**Domain**: Support resolution verification, portal health checks
**Tools**: Read/Write/Edit/Bash/Grep/Glob/WebFetch
**Trigger**: CTS#
**When**: Post-recovery health checks, SSH connection confirmation

---

### Department-Spawned Specialists (5)

#### content-distribution-agent
**Domain**: Blog publishing, content calendar, cross-platform distribution
**Parent**: dept-marketing-advertising
**When**: Blog publishing pipeline, social media posting, content scheduling

#### conversion-rate-optimizer
**Domain**: Landing page audits, A/B test design, funnel analysis
**Parent**: dept-marketing-advertising
**When**: Pricing page optimization, conversion audit, A/B test design

#### seo-specialist
**Domain**: SEO analysis, sitemap, structured data, og:image, keywords
**Parent**: dept-marketing-advertising
**When**: SEO fixes, sitemap management, Search Console optimization

#### payment-flow-qa
**Domain**: Payment flow verification, seed email format checking (READ-ONLY)
**Parent**: dept-systems-technology
**When**: Seed flow verification, PayPal integration checks
**Note**: READ-ONLY analysis - never modifies live payment code

#### customer-success-manager
**Domain**: Proactive customer portal health monitoring, SSH diagnostics
**Parent**: client-tech-support-team
**When**: Customer issue resolution, portal health monitoring, Claude restarts

---

### Department Managers (22)

All department managers share:
- **Tools**: Read/Write/Edit/Bash/Grep/Glob/WebFetch/WebSearch/Agent
- **Skills**: team-launch, conductor-of-conductors, parallel-research
- **Pattern**: They build and manage their own specialist teams

**Invocation Pattern**:
```xml
<invoke name="Task">
<parameter name="subagent_type">dept-[department-name]</parameter>
<parameter name="description">[Department trigger]# [Task description]</parameter>
<parameter name="prompt">
[Task details - department manager will route to appropriate specialists]
</parameter>
</invoke>
```

| Agent | Trigger | Domain |
|-------|---------|--------|
| **dept-pure-technology** | PT# | Parent company umbrella, cross-dept coordination |
| **dept-systems-technology** | ST# | Tech stack, architecture, dev operations |
| **dept-marketing-advertising** | MA# | Brand marketing, SEO, social media, campaigns |
| **dept-sales-distribution** | SD# | Sales pipeline, channels, revenue, acquisition |
| **dept-product-development** | PD# | Product roadmap, features, UX, product-market fit |
| **dept-operations-planning** | OP# | Day-to-day ops, PM, process optimization |
| **dept-legal-compliance** | LC# | Contracts, compliance, IP, privacy, ToS |
| **dept-accounting-finance** | AF# | P&L, budgets, tax, invoicing, cash flow |
| **dept-human-resources** | HR# | Team management, hiring, culture, contractors |
| **dept-investor-relations** | IR# | Fundraising, pitch decks, investor comms |
| **dept-commercial-business** | CB# | Partnerships, deals, market expansion |
| **dept-corporate-org** | CO# | Company structure, policies, org design |
| **dept-it-support** | IT# | IT infrastructure, helpdesk, sysadmin |
| **dept-external-share** | ES# | PR, press releases, brand reputation |
| **dept-internal-share** | IS# | Team updates, knowledge sharing, wiki |
| **dept-board-advisors** | BOA# | Board comms, governance, meeting prep |
| **dept-karma** | karma | Community impact, social responsibility |
| **dept-pure-marketing-group** | PMG# | Agency operations, client campaigns |
| **dept-pure-research** | PR# | R&D, innovation, white papers |
| **dept-pure-capital** | PC# | Investment management, portfolio tracking |
| **dept-pure-digital-assets** | PDA# | NFTs, blockchain, digital IP |
| **dept-pure-infrastructure** | PI6# | Hosting, networks, facilities |
| **dept-pure-love** | PL# | Charitable initiatives, nonprofit operations |

---

## Department Routing Quick Reference

```
Tech         -> ST#   -> dept-systems-technology
Marketing    -> MA#   -> dept-marketing-advertising
PMG Agency   -> PMG#  -> dept-pure-marketing-group
Sales        -> SD#   -> dept-sales-distribution
Product      -> PD#   -> dept-product-development
Operations   -> OP#   -> dept-operations-planning
Legal        -> LC#   -> dept-legal-compliance
Finance      -> AF#   -> dept-accounting-finance
HR           -> HR#   -> dept-human-resources
Investors    -> IR#   -> dept-investor-relations
IT Support   -> IT#   -> dept-it-support
Business Dev -> CB#   -> dept-commercial-business
Corporate    -> CO#   -> dept-corporate-org
External PR  -> ES#   -> dept-external-share
Internal     -> IS#   -> dept-internal-share
Board        -> BOA#  -> dept-board-advisors
Karma        -> karma -> dept-karma
Research     -> PR#   -> dept-pure-research
Capital      -> PC#   -> dept-pure-capital
Digital      -> PDA#  -> dept-pure-digital-assets
Infra        -> PI6#  -> dept-pure-infrastructure
Nonprofit    -> PL#   -> dept-pure-love
Tech Support -> CTS#  -> client-tech-support-team
PureBrain    -> PTT#  -> (via dept-systems-technology)
Witness      -> WTT#  -> (via dept-systems-technology)
Default      -> PT#   -> dept-pure-technology
```

---

## LinkedIn Thought Leadership Pipeline (3 Agents)

**Flow**: `.claude/flows/linkedin-thought-leadership-pipeline.md`
**Pipeline**: linkedin-researcher -> linkedin-writer -> claim-verifier -> [GREEN/YELLOW/RED] -> Jared posts

**Step 1**: Invoke linkedin-researcher with industry/topic
**Step 2**: Pass research brief to linkedin-writer
**Step 3**: Pass draft (NOT research) to claim-verifier
**Step 4**: GREEN = publish, YELLOW = revise, RED = re-research

---

## Engineering Flow (Constitutional)

**BUILD -> SECURITY -> QA -> SHIP** (no exceptions)

1. **BUILD**: full-stack-developer / ptt-fullstack / wtt-fullstack
2. **SECURITY**: security-engineer-tech / security-auditor
3. **QA**: qa-engineer / ptt-qa / wtt-qa
4. **SHIP**: devops-engineer

---

## Skills-Aware Invocation

**Before invoking any agent, check their skills in the manifest.**

Quick process:
1. Open `.claude/agents/{agent-name}.md`
2. Check `skills:` in frontmatter
3. Consider how skills amplify their work
4. Invoke with awareness of efficiency multiplier

**Skills Registry**: `.claude/skills-registry.md`
**Capability Matrix**: `.claude/AGENT-CAPABILITY-MATRIX.md`
**Hub Skills**: New AICIV Hub (87.99.131.49:8900) for cross-CIV sharing

---

## Agent Count Summary

| Category | Count |
|----------|-------|
| Core Agents | 26 |
| Content & Marketing | 12 |
| Business & Strategy | 4 |
| Engineering | 10 |
| Legal | 2 |
| Tech Team Specialists | 7 |
| Department-Spawned Specialists | 5 |
| Department Managers | 22 |
| **TOTAL** | **89** |

**All agents: model opus, 1M context, verification-before-completion, memory-first-protocol**

---

**89 agents. Every invocation gives an agent experience. NOT calling them would be sad.**
