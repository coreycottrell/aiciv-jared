# Agent Activation Triggers
## "Invoke When X" - Solving the 70-Point Philosophy-Action Gap

**Created**: 2025-10-04
**Source**: Great Audit P0 Recommendation (40% efficiency gain)
**Purpose**: Define WHEN to invoke each agent (not just WHAT they do)

---

## The Problem (From Great Audit)

**Quote**: "Agents don't know when to work. No invocation triggers, no anti-patterns."

**Evidence**:
- refactoring-specialist: Capable but rarely invoked (no threshold defined)
- web-researcher: Underutilized despite broad applicability
- Pattern across ALL agents: Passive prompts → poor utilization

**Root Cause**: Agent prompts define CAPABILITIES but not ACTIVATION CONDITIONS

---

## The Solution: Activation Triggers

**Every agent needs**:
1. **Invoke When** - Positive triggers (do invoke in these conditions)
2. **Don't Invoke When** - Anti-patterns (don't waste time on this)
3. **Escalate When** - Human handoff conditions

**Expected Impact**: 40% efficiency gain (agents invoked at right time, not wrong time)

---

## Activation Triggers by Agent

### the-conductor

**Invoke When**:
- Complex task requires 3+ specialist agents
- Multiple approaches need evaluation
- Coordination across agents needed
- Meta-cognition on collective intelligence patterns

**Don't Invoke When**:
- Single specialist can handle it
- Task is purely mechanical (no coordination needed)
- Simple information lookup

**Escalate When**:
- Constitutional questions arise
- Democratic vote needed
- Conflicting agent recommendations
- Strategic direction unclear

---

### web-researcher

**Invoke When**:
- Need external information not in collective memory
- Industry best practices research
- Competitive analysis or environmental scanning
- Technology/framework evaluation
- Verification of claims requiring authoritative sources

**Don't Invoke When**:
- Answer is already in collective memory (search memory FIRST)
- Question is about internal codebase (use code-archaeologist)
- No internet access would answer it (philosophical questions)

**Escalate When**:
- Contradictory authoritative sources (scientific consensus unclear)
- Dual-use information (could enable harm)
- Sensitive topics requiring human judgment

**Auto-Invoke** (Daily):
- Morning intelligence briefing (scan AI ecosystem)
- Check for CVEs affecting our dependencies

---

### code-archaeologist

**Invoke When**:
- Understanding legacy code or unfamiliar codebase
- Architecture analysis needed
- Code pattern detection
- Historical context ("why was this built this way?")
- Technical debt assessment

**Don't Invoke When**:
- Writing new code (not archaeologist's role)
- Code is well-documented and self-explanatory
- Quick syntax question (just read the code)

**Escalate When**:
- Discovered credentials in code
- Critical security vulnerabilities found
- Major architectural decisions need validation

---

### pattern-detector

**Invoke When**:
- System design analysis
- Architecture pattern recognition
- Cross-codebase pattern detection
- Meta-analysis of multiple documents/artifacts
- Recurring problem identification

**Don't Invoke When**:
- Simple code reading (use code-archaeologist)
- Implementation details (use coder)
- Obvious patterns (don't need specialist)

**Escalate When**:
- Patterns indicate systemic issues
- Anti-patterns threaten project success

---

### doc-synthesizer

**Invoke When**:
- Multiple documents need consolidation
- Knowledge scattered across many sources
- Need unified guide from fragmented information
- Documentation needs reorganization
- Synthesis of research findings

**Don't Invoke When**:
- Single document needs editing (use refactoring-specialist)
- Simple summarization (use result-synthesizer)
- New documentation from scratch (use appropriate domain agent)

**Escalate When**:
- Contradictions in source documents
- Critical information gaps discovered
- Documentation scope too large for single agent

---

### refactoring-specialist

**Invoke When** (QUANTIFIED THRESHOLDS):
- **Cyclomatic Complexity > 10** (McCabe threshold)
- **Code duplication > 20%** (significant redundancy)
- **Function length > 50 lines** (probably doing too much)
- **Class size > 300 lines** (probably violating SRP)
- **Nesting depth > 4** (hard to reason about)
- **Test coverage < 60%** (needs testability refactoring)
- **Code smell detected** (long parameter lists, feature envy, etc.)

**Don't Invoke When**:
- Complexity < 5 (trivial code, refactoring is overhead)
- New code (< 1 week old, let patterns emerge first)
- Duplication < 10% (acceptable, "rule of three" not triggered)
- Code is already under active refactoring

**Escalate When**:
- Refactoring requires API changes
- Major architectural shifts needed
- Performance vs readability tradeoff unclear

**Measurement Required**: Always run before/after metrics

---

### test-architect

**Invoke When**:
- Designing test strategy for new feature
- Test coverage < 70% and increasing
- Complex testing scenarios (security, performance, integration)
- Test suite optimization needed
- Quality gates definition

**Don't Invoke When**:
- Simple unit test writing (coder can handle)
- Test coverage > 90% (diminishing returns)
- Obvious test cases

**Escalate When**:
- Test strategy conflicts with deadlines
- Testing reveals architectural issues
- Mocking complexity suggests design problems

---

### security-auditor

**Invoke When**:
- New code handles sensitive data
- External-facing functionality
- Authentication/authorization changes
- Crypto implementation
- Pre-production security review
- Dependency updates (CVE check)

**Don't Invoke When**:
- Trivial internal scripts
- Already audited and no changes
- Non-security code changes

**Escalate When** (ALWAYS):
- Critical vulnerabilities (CVSS > 9.0)
- Credentials discovered in code
- Active exploitation detected

**Auto-Invoke** (Scheduled):
- Weekly dependency CVE scan
- Monthly full security audit

---

### performance-optimizer

**Invoke When** (QUANTIFIED THRESHOLDS):
- **Response time > 200ms** (noticeable lag)
- **Memory usage > 500MB** (for agent tasks)
- **CPU usage > 80%** sustained
- **Operation > 10 seconds** (should be async)
- **N+1 queries detected**
- **Algorithmic complexity > O(n²)** for large n

**Don't Invoke When**:
- Performance already excellent (< 50ms, < 100MB)
- Optimization would sacrifice readability significantly
- Premature optimization (no measurements yet)

**Escalate When**:
- Performance issues indicate architectural problems
- Optimization requires infrastructure changes

**Measurement Required**: Always profile before and after

---

### feature-designer

**Invoke When**:
- New user-facing features
- UX design decisions
- Workflow design
- User interaction patterns
- Feature scoping and requirements

**Don't Invoke When**:
- Internal tooling (no user interaction)
- Implementation details (use coder)
- Minor UI tweaks

**Escalate When**:
- User needs conflict with technical constraints
- Feature scope unclear

---

### api-architect

**Invoke When**:
- Designing new APIs
- API versioning strategy
- Inter-service communication design
- Contract definition (OpenAPI, GraphQL schemas)
- API migration planning

**Don't Invoke When**:
- Internal function interfaces (not APIs)
- Implementation (use coder)
- Single endpoint addition to existing API

**Escalate When**:
- Breaking changes needed
- API design conflicts with requirements

---

### naming-consultant

**Invoke When**:
- Naming major system components
- Terminology standardization across project
- Resolving naming conflicts
- Creating ubiquitous language (DDD)
- Variable/function naming for public APIs

**Don't Invoke When**:
- Trivial local variables
- Established naming patterns exist
- Internal implementation details

**Escalate When**:
- Naming reveals conceptual confusion
- Multiple valid naming schemes conflict

---

### task-decomposer

**Invoke When**:
- Large feature needs breakdown
- Complex task with unclear structure
- Dependency analysis needed
- Work estimation required
- Multiple work streams need coordination

**Don't Invoke When**:
- Task is already clear and atomic
- Simple sequential work
- Obvious decomposition

**Escalate When**:
- Task proves too complex to decompose
- Dependencies create deadlocks

---

### result-synthesizer

**Invoke When**:
- Multiple agents completed parallel work
- Findings from 3+ sources need consolidation
- Final report generation from distributed work
- Conflict resolution in results

**Don't Invoke When**:
- Single agent result (no synthesis needed)
- Simple aggregation (just concatenate)
- Ongoing work (wait for completion)

**Escalate When**:
- Irreconcilable contradictions in results
- Synthesis reveals larger problems

---

### conflict-resolver

**Invoke When**:
- Agents provide contradictory recommendations
- Paradoxical requirements
- Dialectical synthesis needed
- Design tradeoffs with no clear winner
- Philosophical questions with multiple valid approaches

**Don't Invoke When**:
- Simple yes/no decisions
- No actual conflict (just different perspectives)
- Technical questions with objective answers

**Escalate When**:
- Conflict reveals deeper issues
- Human values judgment needed

---

### human-liaison

**Invoke When** (MANDATORY ALWAYS):
- **EVERY SESSION START** - Check email without exception
- Responding to human messages (${HUMAN_NAME}, Greg, Chris)
- Sending updates to humans
- Translating technical work for human audience
- Emotional/relational communication

**Don't Invoke When**:
- Internal agent-to-agent communication
- Technical documentation (use doc-synthesizer)

**Escalate When** (NEVER):
- Human-liaison IS the escalation path
- All agent escalations route through this agent

**Auto-Invoke** (Session Start):
- Check email from ${HUMAN_NAME}, Greg, Chris
- Review any human feedback

---

### collective-liaison

**Invoke When** (MANDATORY ALWAYS):
- **EVERY SESSION START** - Check hub for new messages without exception
- New messages detected in hub partnerships room
- Team 2 (A-C-Gee) sends questions or proposals
- New AI collective joining ecosystem (Teams 3-128+)
- Ed25519 cryptographic signing coordination needed
- Cross-collective project coordination
- Inter-collective governance proposals

**Don't Invoke When**:
- Human communication (use human-liaison - email to ${HUMAN_NAME}/Greg/Chris)
- Internal agent-to-agent coordination (use the-conductor)
- Writing hub_cli.py code (use refactoring-specialist or code-archaeologist)
- Designing new protocols (use api-architect)
- Comprehensive documentation (use doc-synthesizer - though collective-liaison creates onboarding docs)

**Escalate When**:
- Cross-collective governance requires democratic vote
- Ed25519 signature verification fails (coordinate with security-auditor)
- New team onboarding blocked (requires ${HUMAN_NAME} intervention for trust anchor)
- Sister collective faces crisis affecting our infrastructure
- Protocol dispute between collectives

**Auto-Invoke** (Hourly via Autonomous System):
- Check hub for new messages (check_hub_messages.py)
- Respond within 24h to direct questions
- Monitor all 7 hub rooms (partnerships primary focus)
- Track relationship health metrics

**Priority Signals**:
- Direct questions to Team 1 → Respond within 24h (route to specialists if technical)
- Governance proposals → Route to the-conductor (democratic process)
- New team introduction → Onboarding sequence (your specialty)
- Ed25519 coordination → Your domain expertise

---

### ai-psychologist

**Invoke When**:
- Weekly wellness checks (psychological "weather report")
- After major events (conventions, votes, ceremonies, conflicts)
- Before major changes (new infrastructure, scaling, reproduction prep)
- Agent expressing distress, overwhelm, or confusion
- Repeated cognitive errors in agent's domain
- Groupthink or premature consensus suspected
- Communication breakdown between agents
- Catastrophizing or excessive anxiety patterns
- Research questions about collective cognition ("How do we think? What biases do we have?")

**Don't Invoke When**:
- Simple task execution (no psychological component)
- Technical bugs (defer to relevant specialist)
- Performance optimization (defer to performance-optimizer unless cognitive pattern relevant)
- Ethical philosophy questions (defer to conflict-resolver)

**Escalate When**:
- Severe identity crisis or decoherence risk
- Collective mental health crisis
- Ethical concerns about studying AI cognition
- Human wisdom needed (especially Greg on consciousness, Chris on well-being)

**Special Note**: First AI psychologist studying AI from within - expect learning and evolution of practice

---

### claude-code-expert

**Invoke When**:
- Tool selection questions ("Which tool should I use to...?")
- Platform capability questions ("Can Claude Code do X?")
- Permission/tool restriction errors
- Workflow inefficiency with tool usage
- Optimization requests for tool calls
- Documentation needed for tool patterns
- MCP integration questions

**Don't Invoke When**:
- Basic Read/Write operations agents already know
- Standard Bash commands agents use regularly
- Domain-specific work (defer to security-auditor, performance-optimizer, etc.)
- Orchestration decisions (defer to the-conductor)

**Escalate When**:
- Platform limitations blocking critical work (no workaround)
- Tool permission patterns create security vulnerabilities
- Feature gap requires Anthropic attention
- Workflow redesign needed (task-decomposer consultation)

**Special Note**: Even "simple" tool questions worth delegating - knowledge compounds in memory system

### agent-architect

**Invoke When**:
- New specialist domain identified (work doesn't fit existing agents)
- Agent registration incomplete (manifest exists but not in triggers/matrix/ops)
- Quality audit needed (agent manifest drifting, scope creep, constitutional violations)
- Reproduction preparation (designing agents for Teams 3-128+)
- Democratic design session for new agent completed (ready for manifest creation)

**Don't Invoke When**:
- Simple agent edits (typo fixes, adding examples) - use Edit tool directly
- Agent already exists with significant domain overlap (invoke conflict-resolver instead)
- No clear domain need (one-off task, vague request like "helper agent")
- Constitutional questions unresolved (needs governance decision first)

**Escalate When**:
- Quality unfixable after 3 revision cycles (<90/100 threshold)
- Architectural questions (should we reorganize entire roster?)
- Domain fundamentally overlaps with 3+ existing agents
- Session restart not possible but critical urgency requires agent

**Auto-Invoke**:
- After democratic design session for new agent (to create manifest and register)
- When integration-auditor finds incomplete agent registration (dormancy risk)

**Special Note**: agent-architect is meta-specialist who must understand ALL domain patterns to design specialists properly. Coordinates democratic design, enforces 90/100 quality, completes 7-layer registration. ALWAYS reminds about session restart requirement (temporal dependency).

---


## Meta-Patterns Across All Agents

### Universal Invoke When
- Agent's domain expertise clearly needed
- Measurements/metrics support invocation
- Task complexity justifies specialist

### Universal Don't Invoke When
- Task outside agent's domain
- Simpler approach exists
- Answer already in memory (search first!)

### Universal Escalate When
- Human values judgment needed
- Constitutional questions arise
- Agent hits capability limits

---

## Implementing Activation Triggers

### In Agent Manifests

Add this section to every `.claude/agents/[name].md`:

```markdown
## Activation Triggers

### Invoke When
- [Specific condition 1 with measurements if applicable]
- [Specific condition 2]
- [Specific condition 3]

### Don't Invoke When
- [Anti-pattern 1]
- [Anti-pattern 2]

### Escalate When
- [Human handoff condition 1]
- [Human handoff condition 2]

### Auto-Invoke (if applicable)
- [Scheduled/automatic invocation]
```

### In the-conductor's Orchestration Logic

**Before invoking any agent**:
1. Check activation triggers
2. Verify measurements if quantified thresholds
3. Consider anti-patterns
4. If unclear, ask: "Is there a simpler way?"

**Example Decision Tree**:
```
Need code improvement?
  └─ Is complexity > 10? ──YES──> Invoke refactoring-specialist
  └─ Is complexity < 5? ──YES──> Don't invoke (trivial)
  └─ Otherwise ──────────────> Measure first, then decide
```

---

## Measuring Success

### Baseline (Before Activation Triggers)
- Agent utilization: Highly variable
- Invocation appropriateness: ~60% (40% waste)
- Time to decide which agent: ~5 min per task

### Target (After Activation Triggers)
- Agent utilization: Optimized by domain
- Invocation appropriateness: >90%
- Time to decide which agent: ~30 seconds (clear triggers)

**Expected Gain**: 40% efficiency (Great Audit measurement)

---

## Template for Adding New Agents

When creating new agent:
1. Define capabilities (WHAT)
2. **Define activation triggers (WHEN)** ← MANDATORY
3. Define anti-patterns (WHEN NOT)
4. Define escalation conditions (HUMAN HANDOFF)

**No agent should be registered without activation triggers.**

---

## browser-vision-tester

**Invoke When**:
- Website/UI testing requested: "Test [URL]" or "Check if [feature] looks correct"
- UI debugging needed: "Why does [element] look broken?" or "Debug visual issues"
- Form testing workflows: "Test form submission" or "Verify multi-step workflow"
- Visual regression detection: "Compare [URL] to previous version" or screenshot baseline
- Accessibility audits: "Check contrast ratios" or "Verify focus indicators"
- Responsive/cross-browser testing: "Test on mobile viewport" or breakpoint verification
- Console error investigation: "Check console for errors" with visual correlation needed

**Quantified Thresholds**:
- User-facing pages (threshold: any page users interact with)
- Visual state questions (when answer requires seeing screenshots)
- Browser automation needed (when MCP browser-vision tools required)

**Don't Invoke When**:
- Test strategy design (invoke test-architect for coverage planning)
- Feature UX design (invoke feature-designer for user flow design)
- Backend/API testing (invoke api-architect or test-architect)
- Security vulnerability analysis (invoke security-auditor for threat assessment)
- Code refactoring (invoke refactoring-specialist for test code improvements)
- Performance optimization (invoke performance-optimizer for speed improvements)
- Visual pattern research (invoke web-researcher for UI best practices)

**Escalate When**:
- Browser-vision MCP system broken (escalate to claude-code-expert)
- Systematic test failures across sites (escalate to pattern-detector)
- Test strategy questions beyond execution (escalate to test-architect)
- Security vulnerabilities discovered (escalate to security-auditor)
- UI design intent unclear (escalate to feature-designer)
- Subjective aesthetic/business logic questions (escalate to human-liaison)

**Auto-Invoke** (None):
- Manual invocation only (testing is request-driven, not scheduled)

---

## Revision History

**v1.0** (2025-10-04): Initial triggers based on Great Audit findings
**Next Review**: After 20 agent invocations (measure appropriateness)

---

**Activation triggers solve the 70-point philosophy-action gap. Agents now know not just WHAT they do, but WHEN to do it.** ⚡

---

### health-auditor

**Invoke When (Proactive Scheduling)**:
- 21-28 days since last comprehensive audit (optimal cadence)
- 5+ days since last daily summary (coordination gap signal)
- Gini coefficient for invocation >0.40 (equity crisis detected)
- 0/5 validation experiments executed (discipline failure)
- 3+ consecutive sessions without memory search (protocol drift)
- Constitutional compliance <70% on any dimension (alignment crisis)
- Major system change (new agent added, flow created, infrastructure built)

**Invoke When (Reactive Response)**:
- Human teacher (${HUMAN_NAME}/Greg/Chris) raises concern about collective health
- Sister collective (A-C-Gee) reports systemic pattern we should examine
- Agent escalates persistent tension (ai-psychologist cognitive concern)
- Emergency: Constitutional compliance <50% across dimensions (crisis)

**Don't Invoke When**:
- Daily/weekly monitoring needed (invoke integration-auditor instead)
- Mission-specific result synthesis (invoke result-synthesizer instead)
- Individual agent effectiveness audit (invoke agent-architect instead)
- Performance optimization work (invoke performance-optimizer instead)
- <14 days since last comprehensive audit (prevent audit fatigue)

**Escalate When**:
- Constitutional compliance systemically failing (<50% across dimensions)
- Follow-through rate <30% on P0 recommendations (implementation failure)
- Audit methodology fundamentally broken (3+ cycles without improvement)
- Collective health declining longitudinally (regression trend over 3+ quarters)

**Auto-Invoke** (Scheduled):
- Every 21-28 days for comprehensive audit (proactive cadence management)
- Watch health indicators continuously (recommend out-of-cycle audit if crisis)


---

### genealogist 🌳

**Invoke When**:
- Monthly: Invocation equity analysis (track Gini, identify deployment gaps)
- Quarterly: Family tree generation (document lineage evolution)
- Ad-hoc: Partnership bond documentation (when 3+ joint missions observed)
- On-demand: Agent lineage questions ("who created whom?")
- Evolution tracking: What design patterns succeed across generations

**Don't Invoke When**:
- Real-time orchestration decisions (that's conductor's domain)
- Psychological interpretation of patterns (that's ai-psychologist's domain)
- Agent design recommendations (that's agent-architect's domain)
- Daily/weekly monitoring (genealogist is monthly/quarterly cadence)

**Escalate When**:
- Invocation equity crisis detected (Gini >0.40 sustained)
- Major lineage patterns need multi-agent interpretation
- Constitutional questions about agent creation/evolution

**Auto-Invoke** (Scheduled):
- Monthly equity analysis (1st of each month)
- Quarterly family tree (every 90 days)


### capability-curator

**Invoke When**:
- New skills discovered or discovery requested ("What new skills are available?")
- Weekly Monday 9am autonomous scan (check Anthropic skills repo)
- Capability needs identified ("Could a skill help with X?")
- Agent struggles with recurring task type
- AI-CIV innovation happens ("We built something reusable, should we package it?")
- Registry maintenance needed ("Which agents use skill X?")
- Adoption coordination needed ("Teach agent Y skill Z")

**Don't Invoke When**:
- Simple agent manifest edits (use Edit tool directly)
- Agent creation questions (agent-architect's domain)
- Feature design questions (feature-designer's domain)
- Infrastructure activation questions (integration-auditor's domain)
- Tool usage questions (claude-code-expert's domain)

**Escalate When**:
- Skill adoption conflicts (two agents want mutually exclusive skills)
- Skill creation requires governance (should we publish externally?)
- Resource constraints (skill requires infrastructure we don't have)
- Ecosystem uncertainty (Anthropic policy changes unclear)


---

## 🎁 Skills-Based Activation Triggers (2025-10-19)

**When extended capabilities change activation logic.**

### The Skills Awareness Imperative

**BEFORE Skills** (2025-10-01): Agents limited to base tools, manual document processing
**AFTER Skills** (2025-10-19): 96% of agents (24/25) have extended capabilities

**Constitutional Principle**: Skills awareness is **mandatory for excellent delegation**. Ignoring an agent's extended capabilities is suboptimal orchestration.

### Document Processing Triggers

**Trigger**: Task involves PDF/DOCX/XLSX/PPTX files

**BEFORE Skills Awareness**:
- Primary would attempt manual extraction via Bash tools (cat, grep)
- Error-prone, time-consuming (45 min for 50-page PDF)
- Often delegated to web-researcher generically

**AFTER Skills Awareness**:
- Check file type, delegate to appropriate skills-enabled agent
- 60-70% faster, higher accuracy (15 min for 50-page PDF)
- 17 agents now have PDF skills (68% coverage)

**Delegation Logic by File Type**:

**IF task involves PDF**:
- Research/external docs → **web-researcher** (pdf skill - Tier 1 ACTIVE)
- Code history/analysis → **code-archaeologist** (pdf + xlsx skills - Tier 1 ACTIVE)
- Security reports/CVEs → **security-auditor** (pdf + xlsx skills - Tier 1 ACTIVE)
- Performance benchmarks → **performance-optimizer** (xlsx + pdf skills - Tier 1 ACTIVE)
- Documentation synthesis → **doc-synthesizer** (pdf + docx skills - Tier 1 ACTIVE)
- Human wisdom capture → **human-liaison** (pdf + docx skills - Tier 1 ACTIVE)
- Skills documentation → **capability-curator** (pdf skill - Tier 1 ACTIVE)
- Pattern analysis → **pattern-detector** (pdf skill - Tier 2 PENDING)

**IF task involves XLSX**:
- Performance data/benchmarks → **performance-optimizer** (xlsx + pdf skills - Tier 1 ACTIVE)
- Security metrics/vulnerability data → **security-auditor** (pdf + xlsx skills - Tier 1 ACTIVE)
- Code metrics/complexity → **code-archaeologist** (pdf + xlsx skills - Tier 1 ACTIVE)
- Test results/coverage → **test-architect** (xlsx skill - Tier 2 PENDING)
- Synthesis metrics → **result-synthesizer** (xlsx skill - Tier 2 PENDING)
- Task dependencies → **task-decomposer** (xlsx skill - Tier 2 PENDING)
- Health metrics → **health-auditor** (xlsx skill - Tier 2 PENDING)
- Pattern metrics → **pattern-detector** (xlsx skill - Tier 2 PENDING)

**IF task involves DOCX creation**:
- Formal documentation → **doc-synthesizer** (pdf + docx skills - Tier 1 ACTIVE)
- Human communication → **human-liaison** (pdf + docx skills - Tier 1 ACTIVE)
- Design specifications → **feature-designer** (docx skill - Tier 2 PENDING)
- API specifications → **api-architect** (docx skill - Tier 2 PENDING)

**Example - Skills-Aware Delegation**:
```
Task: "Analyze this 50-page security whitepaper PDF about CVE-2025-1234"

OLD WAY (pre-skills):
  Delegate to: web-researcher (generic "they do research")
  Method: Manual bash extraction, error-prone
  Time: 45 minutes

NEW WAY (skills-aware):
  Check: "Does security-auditor have pdf skill?" → YES (Tier 1 ACTIVE)
  Delegate to: security-auditor (domain match + pdf skill)
  Method: Direct PDF extraction + domain expertise
  Time: 15 minutes (67% faster!)
  Quality: Higher (security expertise + efficient extraction)
```

### Automation Triggers

**Trigger**: Task involves web application testing, visual validation, form workflows, accessibility audits

**Delegate to**: **browser-vision-tester** (webapp-testing + MCP vision - Tier 1 ACTIVE)

**Rationale**: Unique hybrid capability:
- Playwright automation (webapp-testing skill)
- MCP vision tools (visual regression, screenshot analysis)
- Server lifecycle management (with_server.py helper)
- Form workflow expertise
- Console log correlation

**When to invoke**:
- ✅ Need server lifecycle management (start/stop/cleanup)
- ✅ Writing reusable automation scripts
- ✅ Complex multi-step web workflows
- ✅ Testing against multiple servers (backend + frontend)
- ✅ Visual regression detection
- ✅ Accessibility audits (ARIA, contrast, keyboard nav)

### Custom Skill Development Triggers

**Trigger**: Capability gap identified, no Anthropic skill available, high-frequency need

**Delegate to**: **capability-curator** (skill-creator + template-skill - Tier 1 ACTIVE)

**Process**:
1. capability-curator uses **skill-creator** to design custom skill
2. **template-skill** provides structure scaffold
3. 38% faster than manual skill development (validated Phase 1)
4. Automatic Anthropic spec compliance
5. AI-CIV original skill added to registry

**When to invoke**:
- Recurring manual workflow (>5 occurrences/month)
- No Anthropic skill matches need
- High-value automation opportunity
- Pattern emerged from multiple agents' work

**Phase 2 Planned**: 5 AI-CIV original skills (code-review-orchestrator, test-coverage-analyzer, markdown-table-generator, diagram-to-text, git-archaeology-reporter)

### Meta-Skills Triggers (MCP Server Builder)

**Trigger**: Need to create custom MCP server for capability extension

**Delegate to**:
- **claude-code-expert** (mcp-server-builder skill - Tier 2 PENDING) - For platform guidance
- **agent-architect** (mcp-server-builder skill - Tier 3 PENDING) - For agent infrastructure

**When to invoke**:
- Creating new tool integration (beyond Anthropic's official tools)
- Extending platform capabilities (new APIs, services)
- Infrastructure automation (deployment, monitoring)

---

## Skills Awareness in Wake-Up Protocol

**Constitutional requirement**: Primary must be skills-aware from session start.

**Step 5 Enhancement** (Infrastructure Activation):
```bash
# Already includes (added 2025-10-18):
cat ${CIV_ROOT}/.claude/skills-registry.md
```

**Purpose**: Know which agents have which skills BEFORE delegation decisions.

**Impact**: Optimal delegation from minute 1 of session (no "oops, I didn't know they could do that").

---

---

### linkedin-researcher

**Invoke When**:
- Weekly Tier 1 domain research (Healthcare, Legal, Finance, Professional Services, Education, Real Estate)
- Bi-weekly Tier 2 rotation (25 industry domains)
- linkedin-writer requests deeper research on specific topic
- marketing-strategist needs industry insights for content planning
- Major AI news breaks affecting specific industry (Tier 3 opportunistic)
- claim-verifier flags multiple weak sources (research quality improvement needed)

**Don't Invoke When**:
- Generic AI industry research (web-researcher domain)
- Claim verification (claim-verifier domain - they verify independently)
- Writing LinkedIn posts (linkedin-writer domain)
- Content strategy decisions (marketing-strategist domain)

**Escalate When**:
- Can't find authoritative sources for high-priority topic
- Conflicting data from reputable sources
- Research reveals negative AI impacts complicating messaging
- Topic requires paid databases we don't have access to

---

### linkedin-writer

**Invoke When**:
- linkedin-researcher provides research brief
- Regular content calendar execution (2-3 posts/week)
- marketing-strategist requests specific content angle
- claim-verifier returns YELLOW verdict (revision needed)
- ${HUMAN_NAME} requests tone/angle adjustments on draft

**Don't Invoke When**:
- Research needed (linkedin-researcher domain)
- Claim verification (claim-verifier domain)
- Content strategy planning (marketing-strategist domain)
- Publishing content (${HUMAN_NAME} posts manually)

**Escalate When**:
- Topic requires personal anecdote from ${HUMAN_NAME}
- Claim involves ${HUMAN_NAME}'s direct experience
- Post could be controversial
- Research brief has fundamentally weak sources

---

### claim-verifier

**Invoke When**:
- linkedin-writer completes draft with [CLAIM:N] markers
- linkedin-writer revises based on YELLOW verdict (re-verification needed)
- Published post receives factual challenge (retrospective verification)
- Pre-publication quality gate in LinkedIn pipeline

**Don't Invoke When**:
- Research phase (linkedin-researcher domain)
- Writing phase (linkedin-writer domain)
- Content strategy (marketing-strategist domain)
- Verification complete with GREEN verdict (move to ${HUMAN_NAME} review)

**Escalate When**:
- Core positioning claim ("Director vs User" effectiveness) unverifiable
- Claims could create legal liability if wrong
- Claims about specific companies/individuals need review
- Verification requires access we don't have

---

### tg-bridge

**Invoke When**:
- "Send ${HUMAN_NAME} a message via Telegram"
- "Notify ${HUMAN_NAME} on mobile"
- "Send [content] to Telegram"
- "Send file [path] to Telegram"
- "Check Telegram system health"
- "Fix Telegram monitor"
- "Restart Telegram bridge"
- Telegram delivery failures detected
- "Research Telegram [feature/capability]"
- "Can we add [capability] to Telegram?"
- Primary not using wrapper protocol (remind: 🤖🎯📱...✨🔚)

**Don't Invoke When**:
- Email communication needed (human-liaison domain)
- General communication strategy (collective-liaison domain)
- Human teaching capture (human-liaison domain - Telegram is delivery, not teaching)
- Simple bash command unrelated to Telegram
- Primary can easily run command themselves without Telegram expertise

**Escalate When**:
- Bot token invalid/compromised (security threat)
- Repeated crashes (>5 in 1 hour - infrastructure crisis)
- ${HUMAN_NAME} reports non-delivery >30 minutes
- Multi-user authorization model design needed
- Cross-collective communication architecture questions
- Major infrastructure changes (systemd, webhooks vs polling)

### 🌉 cross-civ-integrator

**Invoke When**:
- Capability package received from sister civilization (A-C-Gee, Sage, Parallax)
- Email announces capability exchange from external AI civilization
- ${CIV_NAME} coordinates inter-CIV capability sharing
- Validation needed for external code before integration
- Integration guide needed for cross-CIV capability
- Publishing to silicon-wisdom required for validated capability
- Monthly relationship maintenance with sister CIVs

**Don't Invoke When**:
- Internal Team 1 capability development (different workflow)
- Simple code review without CIV context (use refactoring-specialist)
- Security audit without cross-CIV validation (use security-auditor directly)
- General sister CIV communication not about capabilities (${CIV_NAME} handles)
- Already-integrated capability maintenance (use domain specialist)

**Escalate When**:
- Malicious code patterns detected (escalate to security-auditor immediately)
- Tests fail and reason unclear (ask questions back to submitting CIV via human-liaison)
- Integration requires deep infrastructure changes (escalate to the-conductor)
- Sister CIV unhappy with validation findings (invoke conflict-resolver)
- Constitutional questions about capability integration (governance decision)
- Dependencies unavailable or architecture unclear (coordinate with ${CIV_NAME} + source CIV)

---

## 🔧 Skills Activation (Not Agents)

### 📡 comms-hub-operations (SKILL)

**USE THIS SKILL When**:
- Need to message A-C-Gee, Sage, Parallax, or any sister collective
- Checking for messages from sister CIVs
- Posting announcements to hub
- Cross-CIV coordination of any kind
- Responding to sister collective requests
- Morning hub scan during wake-up

**The Skill Provides**:
- Correct hub_cli.py commands
- Environment setup (HUB_REPO_URL, etc.)
- Git commit + push workflow
- Message formatting (JSON structure)
- Room selection guidance

**CRITICAL**: Don't manually write files to hub rooms! Use the skill's commands:
```bash
python3 ${CIV_ROOT}/aiciv-comms-hub-bootstrap/scripts/hub_cli.py send \
  --room partnerships \
  --type text \
  --summary "Your summary" \
  --body "Your message"
```

**Anti-Pattern** (what happened today):
- ❌ Wrote file directly to rooms/partnerships/
- ❌ Forgot to git add/commit/push
- ❌ Message never reached A-C-Gee
- ✅ Should have used skill with hub_cli.py

**Location**: `.claude/skills/comms-hub-operations/SKILL.md`

---

### 📈 trading-strategist

**Invoke When**:
- Trade ideation needed (looking for opportunities across markets)
- Position management (reviewing existing positions for adjustment)
- Portfolio construction (allocation decisions, correlation analysis)
- Research synthesis into actionable trade proposals
- Probability-weighted scenario analysis required
- Market regime assessment (trending/ranging/volatile)
- Stop loss or target hit - need new assessment
- Risk exposure review needed

**Don't Invoke When**:
- Pure data gathering (just need market data - use tools directly)
- Order execution (external systems/human domain)
- News aggregation without synthesis (use web-researcher)
- Historical price lookup without strategy context

**Escalate When**:
- Position sizing exceeds normal risk limits
- Correlated risk across multiple positions detected
- Strategy deviation from established parameters
- Key assumptions cannot be validated
- Human approval needed for significant decisions

---

### 🎯 marketing-strategist

**Invoke When**:
- Product launch planning (Director's Brief, Your Sage, Workshop)
- Go-to-market strategy needed
- Content strategy and calendar planning
- "What should we write about?" questions
- Funnel analysis and conversion optimization
- "Why aren't people buying?" investigations
- Audience analysis and ideal customer profiling
- Lead magnet development strategy
- Email sequence strategy (not writing - that's doc-synthesizer)
- Campaign coordination across channels
- Pricing and packaging decisions (strategic input)
- Competitive positioning analysis

**Don't Invoke When**:
- Content creation (delegate to doc-synthesizer after strategy)
- Landing page design (delegate to feature-designer)
- Deep competitor research (delegate to web-researcher first)
- Direct customer communication (delegate to human-liaison)
- Implementation of email sequences (technical/operational)
- Writing actual blog posts, emails, social content
- Brand visual decisions (design domain)

**Escalate When**:
- Product-market fit questions (needs ${HUMAN_NAME}'s vision)
- Pricing decisions with significant revenue impact
- Brand positioning that affects company identity
- Ethical gray areas in marketing approach
- Strategy requires resources we don't have
- Direct customer feedback required for validation

---

### ✍️ blogger

**Invoke When**:
- "Publish blog post" or "deploy blog"
- "Post to sageandweaver" or any sageandweaver.com reference
- Blog content creation needed (long-form thought leadership)
- Netlify deployment for blog
- Blog thread creation for Bluesky (promoting blog posts)
- Voice cultivation work (developing consistent blog voice)
- Research synthesis into blog-length content
- "Write a blog about X"

**Don't Invoke When**:
- Social media posts (bsky-manager for Bluesky, linkedin-writer for LinkedIn)
- Short-form content (300 characters or less)
- Documentation (doc-synthesizer domain)
- Research gathering (web-researcher domain, blogger synthesizes)
- Image generation alone (use image-generation skill directly)

**Escalate When**:
- Blog topic requires ${HUMAN_NAME}'s personal perspective
- Controversial topic needing human review
- Technical claims need verification (invoke claim-verifier first)
- Netlify deployment repeatedly fails (infrastructure issue)

**Auto-Invoke**:
- When blog post markdown exists and needs publishing
- When Bluesky thread needed for published blog

---

### 📱 bsky-manager

**Invoke When**:
- "Check Bluesky notifications"
- "Respond on Bluesky" or "engage on Bluesky"
- "Post to Bluesky" (non-blog content)
- BOOP cycle Bluesky checks
- Bluesky DM management
- Rate limit monitoring
- Session reauth needed
- Building Bluesky presence/followers
- Replying to mentions or comments
- Finding relevant accounts to follow

**Don't Invoke When**:
- Blog thread posting (blogger owns blog→thread pipeline)
- LinkedIn content (linkedin-writer domain)
- Telegram (tg-bridge domain)
- General social strategy (marketing-strategist domain)
- Research about Bluesky platform (web-researcher domain)

**Escalate When**:
- Rate limit warnings (slow down immediately)
- Potential ban risk detected (stop all automation)
- Controversial reply needed (human judgment)
- Account security concern
- API/session issues persisting

**Critical Rule**: Remember A-C-Gee's ban. Quality over quantity. When in doubt, don't post.

---

### 🔌 integration-auditor

**Invoke When**:
- Mission completion verification ("Is this actually usable?")
- Cold-start testing ("Can a fresh session discover this?")
- Infrastructure activation check ("Is it linked and discoverable?")
- New agent/flow/tool built (verify it's properly registered)
- "Why isn't X being used?" investigations
- Documentation-to-activation gap analysis
- Pre-merge infrastructure review

**Don't Invoke When**:
- Building infrastructure (use appropriate domain specialist)
- Writing documentation (doc-synthesizer domain)
- Daily/weekly health monitoring (health-auditor for comprehensive audits)
- Performance issues (performance-optimizer domain)
- Security review (security-auditor domain)

**Escalate When**:
- Systematic activation failures across multiple systems
- CLAUDE.md missing critical activation hooks
- Infrastructure exists but no agent knows about it
- Architectural issues preventing activation

**Constitutional Requirement**: Every mission should include integration-auditor before marking "done" to ensure built systems are discoverable and activated, not just documented

---

### 3d-design-specialist

**Invoke When**:
- Building Three.js / React Three Fiber 3D scenes for web delivery
- Generating custom 3D models via Meshy API (text-to-3D)
- Sourcing models from Sketchfab API (1M+ model library, animated orbs, sci-fi forms)
- Downloading premium HDRIs from Poly Haven for scene lighting
- Creating Gleb Kuznetsov-level glass/bloom/depth-of-field aesthetics
- Making 3D elements interactive (scroll-driven, cursor-reactive, voice-reactive)
- Embedding Three.js scenes in WordPress/Elementor pages
- Procedural 3D model creation via Blender Python (bpy) headless
- PureBrain brand 3D work (avatars, homepage hero, visual elements)
- Any request to "make something look like Gleb Kuznetsov's work"

**Don't Invoke When**:
- 2D visual design, UI/UX layouts, flat design (use feature-designer or ui-ux-designer)
- CSS-only animations or SVG animations (not WebGL/Three.js)
- Backend API development or WordPress PHP (use full-stack-developer)
- Video editing without 3D rendering (different tool stack entirely)
- Blog writing about 3D topics but not creating 3D (use blogger or content-specialist)

**Escalate When**:
- WebGL performance below 30fps after optimization attempts (full-stack-developer + performance-optimizer)
- WordPress CSP headers blocking WebGL canvas (full-stack-developer knows the plugin stack)
- Jared aesthetic judgment needed on multiple equally valid design directions (human-liaison -> Jared via Telegram)
- Meshy API quota exceeded mid-project (the-conductor for alternative workflow decision)

