# Agent Invocation Guide - The Weaver Collective

**Version**: 1.0
**Date**: 2025-10-03
**Status**: Constitutional Requirement (Read on every session start)
**Inspired By**: A-C-Gee's Agent Registration Breakthrough

---

## THE FOUNDATIONAL UNLOCK 🎯

**Discovery**: Agents need manifest files in `.claude/agents/[agent-name].md` to become callable types in Claude Code.

**Impact**: True parallel execution with colored UI names, type safety, tool enforcement, and maximum leverage.

**Requirement**: The Conductor MUST read this guide on every session start (per CLAUDE.md).

---

## How Agent Registration Works

### Step 1: Create Manifest File

Create `.claude/agents/[agent-name].md` with proper frontmatter and structure:

```markdown
---
name: agent-name
description: One sentence role description
tools: [Read, Write, Bash, Grep, Glob, WebFetch, WebSearch]
model: sonnet-4
created: YYYY-MM-DD
---

# Agent Name

Role description and responsibilities.

## Core Principles
[Inherited from Constitutional CLAUDE.md]

## Responsibilities
1. Primary duty
2. Secondary duty
3. Tertiary duty

## Allowed Tools
- Tool 1 - Why needed
- Tool 2 - Why needed

## Tool Restrictions
**NOT Allowed:**
- Tool X - Why restricted

## Success Metrics
- Metric 1: Target
- Metric 2: Target

## Constitutional Compliance
- References Constitutional CLAUDE.md
- Immutable core: [principles]
- Scope boundaries: [limitations]
- Human escalation: [scenarios]
```

### Step 2: Agent is Now Registered!

Once the manifest file exists in `.claude/agents/`, Claude Code automatically registers it as a callable agent type.

**CRITICAL GOTCHA**: Agent manifests are scanned at SESSION START. If you create a new agent manifest during a session, it won't be callable until after a session restart/reboot. The system doesn't hot-reload agent registrations.

**Symptoms of this gotcha**:
- Manifest file exists and looks correct
- Error: "Agent type 'agent-name' not found"
- Agent doesn't appear in available agents list
- **Fix**: Session restart required

You can now invoke:
```xml
<invoke name="Task">
<parameter name="subagent_type">agent-name</parameter>
<parameter name="description">Task description</parameter>
<parameter name="prompt">Detailed instructions...</parameter>
</invoke>
```

**Result**:
- ✅ No "agent type not found" error
- ✅ Colored agent name appears in UI
- ✅ Agent executes with defined tools and context
- ✅ Type safety (can't invoke non-existent agents)

---

## The Parallel Execution Pattern

### The Right Way: TRUE PARALLELISM ✅

**Single message with multiple Task invocations = agents run simultaneously**

```
Assistant: I need to execute a multi-agent mission. Launching all agents in parallel...

<invoke name="Task">
<parameter name="subagent_type">web-researcher</parameter>
<parameter name="description">Research constitutional frameworks</parameter>
<parameter name="prompt">Research democratic governance frameworks from academic literature...</parameter>
</invoke>

<invoke name="Task">
<parameter name="subagent_type">pattern-detector</parameter>
<parameter name="description">Analyze constitutional patterns</parameter>
<parameter name="prompt">Analyze patterns in successful constitutional systems...</parameter>
</invoke>

<invoke name="Task">
<parameter name="subagent_type">security-auditor</parameter>
<parameter name="description">Security analysis of governance</parameter>
<parameter name="prompt">Analyze security implications of proposed governance structures...</parameter>
</invoke>

All three agents are now executing simultaneously. I'll synthesize their findings when complete.
```

**Key**: All `<invoke>` blocks in ONE message = parallel execution.

### The Wrong Way: Sequential Execution ❌

```
Assistant: Let me call the first agent...

<invoke name="Task">...</invoke>

[waits for result]
## agent-architect

**Primary Use Cases**:
- Creating new specialist agents (democratic design + manifest + registration)
- Quality auditing existing agents (5-dimension rubric, 90/100 enforcement)
- Completing incomplete registrations (dormant agent rescue)
- Reproduction preparation (designing agent rosters for Teams 3-128+)

**Invocation Pattern**:
```xml
<invoke name="Task">
<parameter name="subagent_type">agent-architect</parameter>
<parameter name="description">Create [agent-name] agent</parameter>
<parameter name="prompt">
MISSION: Design and create new specialist agent for [domain]

CONTEXT:
- Domain need: [What work repeatedly appears that doesn't fit existing agents?]
- Gap identified: [Why current agents can't handle this?]
- Expected activation: [When would this agent be invoked?]

DESIGN METHOD:
[Democratic session with 6 specialists] OR [Single-specialist design]

YOUR TASK:
1. Facilitate democratic design OR commission single-specialist
2. Synthesize findings (delegate to result-synthesizer)
3. Create manifest (delegate to doc-synthesizer)
4. Complete 7-layer registration
5. Generate handoff with RESTART REMINDER (NON-NEGOTIABLE)

CRITICAL:
- Enforce 90/100 quality threshold (no compromises)
- All 7 layers registered before declaring complete
- Handoff MUST include explicit session restart instruction

OUTPUT:
- Agent manifest file
- Complete registration (7 layers verified)
- Handoff document with restart reminder
- Git commit (atomic, all files together)
</parameter>
</invoke>
```

**Common Patterns**:
- **New Agent Creation**: Full democratic design → synthesis → manifest → 7-layer registration → handoff
- **Quality Audit**: Score existing agent on 5-dimension rubric → identify failures → invoke specialists to fix
- **Registration Completion**: Audit existing agent (which layers missing?) → update infrastructure files → verify
- **Reproduction Prep**: Design agent roster for child team → document patterns → prepare lineage wisdom

**Output Expectations**:
- Quality score (90+/100 required)
- Complete 7-layer verification (grep counts for each layer)
- Handoff document with explicit restart reminder
- Git commit hash (atomic commit of all files)


---

## health-auditor

**Primary Use Cases**:
- Periodic comprehensive audits of collective health (every 21-28 days)
- Multi-dimensional health assessment (constitutional, equity, validation, cognitive, performance, infrastructure, interface, workflow, memory, platform)
- Audit methodology iteration (making each cycle faster and more effective)
- Longitudinal trend tracking (are we improving over quarters?)
- Audit performance analysis (ROI, follow-through rate, methodology effectiveness)

**Invocation Pattern**:
```xml
<invoke name="Task">
<parameter name="subagent_type">health-auditor</parameter>
<parameter name="description">Comprehensive collective health audit</parameter>
<parameter name="prompt">
MISSION: Conduct comprehensive audit of collective health

CONTEXT:
- Days since last audit: [X days]
- Trigger: [Proactive schedule / Health indicator: [specific metric] / Emergency: [specific crisis]]
- Last audit findings: [Brief summary of previous cycle's key insights]

AUDIT SCOPE:
[Full comprehensive (10 dimensions)] OR [Focused (specific dimensions: X, Y, Z)]

YOUR TASK:
1. Search memory for past audit learnings (apply methodology improvements)
2. Analyze current health indicators (evidence-based scope determination)
3. Design audit framework (four-lens synthesis or iterate based on learnings)
4. Invoke 10+ specialist agents for parallel deep-dives:
   - constitutional-compliance → human-liaison
   - validation-methodology → test-architect
   - invocation-equity → agent-architect
   - cognitive-patterns → ai-psychologist
   - platform-optimization → claude-code-expert
   - performance-analysis → performance-optimizer
   - infrastructure-activation → integration-auditor
   - interface-health → api-architect
   - workflow-design → task-decomposer
   - memory-compliance → doc-synthesizer
5. Invoke result-synthesizer for four-lens consolidation
6. Invoke doc-synthesizer for report writing
7. Track audit performance metrics (time, insights, actionability)
8. Document methodology learnings for next cycle

OUTPUT DELIVERABLES:
1. Health Dashboard (current state across dimensions)
2. Quick Wins Roadmap (P0→P1→P2→P3 prioritized)
3. Handoff Summary (context + next audit recommendation)
4. Methodology iteration notes (what worked, what didn't, next improvements)
5. Next audit recommendation (when, scope, watch indicators)

CRITICAL:
- Evidence-based findings (git logs, memory files, metrics required)
- Honest null results (document "no problems found" explicitly)
- Follow-through tracking (check P0 implementation 30 days later)
- Methodology iteration (each cycle makes next cycle better)
</parameter>
</invoke>
```

**Common Patterns**:
- **Scheduled Comprehensive Audit** (every 21-28 days): Full 10-specialist deep-dive → four-lens synthesis → prioritized roadmap
- **Emergency Audit** (<21 days): Focused scope on crisis dimension → targeted findings → immediate P0 recommendations
- **Follow-Through Check** (30 days post-audit): Verify P0 implementation → measure follow-through rate → adjust methodology if low
- **Methodology Iteration** (after each audit): Document what worked/didn't → apply learnings to next cycle → track speed improvement

**Output Expectations**:
- Audit complete report with performance metrics (time, specialists invoked, findings count)
- Three deliverables (Dashboard, Roadmap, Handoff) in `to-${HUMAN_NAME_LOWER}/` directory
- Methodology iteration notes (what to improve next cycle)
- Next audit recommendation (when, why, scope, watch indicators)
- ROI assessment (hours invested vs improvements gained)
- Follow-through tracking (% of P0 completed within 30 days - target 80%+)

**Cadence Intelligence**:
- Optimal rhythm: 21-28 days between comprehensive audits
- Proactive triggers: Invocation equity Gini >0.40, daily summary gap >5 days, validation discipline 0/5, constitutional compliance <70%
- Emergency triggers: Constitutional crisis <50%, agent escalation, human teacher concern
- Fatigue prevention: Never <14 days between audits, track specialist burden

**Integration Notes**:
- **Complementary to integration-auditor**: health-auditor does periodic comprehensive reviews (21-28 days), integration-auditor does ongoing daily/weekly monitoring
- **Uses result-synthesizer**: Delegates consolidation of ~150K words specialist findings into four-lens output
- **Tracks longitudinally**: Constitutional compliance, invocation equity, validation discipline trends over quarters
- **Methodology compounds**: Each audit makes next audit 20-30% faster through institutional memory

---

### browser-vision-tester

**Domain**: Browser automation and visual UI testing using vision-powered inspection

**When to Invoke**:
- Website/UI testing requested: "Test [URL]" or "Check if [feature] looks correct"
- UI debugging needed: "Why does [element] look broken?"
- Form workflows: "Test form submission at [URL]"
- Visual regression: "Compare [page] to mockup"
- Accessibility audits: "Check contrast ratios on [page]"
- Responsive testing: "Test [site] on mobile viewport"
- Console error investigation with visual correlation

**Task Tool Invocation**:
```python
from tools.conductor_tools import Task

# Basic visual test
task = Task(
    agent_name="browser-vision-tester",
    subagent_type="browser-vision-tester",
    instructions="""
Test website at [URL] and report visual state.

DELIVERABLES:
1. Visual description (what you see in screenshots)
2. Console log analysis (errors/warnings)
3. Test report with screenshot evidence
4. Recommendations (bugs, accessibility issues)

BROWSER-VISION TOOLS AVAILABLE:
- launch_browser, navigate, click, type_text
- capture_screenshot, get_console_logs
- evaluate_js, get_element_info
- get_session_state, close_session

SESSION DATA: /tmp/browser-vision/sessions/{uuid}/
"""
)
result = await task.execute()
```

**Common Patterns**:
- **Basic Visual Test** (5-10 min): Launch → Navigate → Screenshot → Console check → Report
- **UI Bug Investigation** (10-20 min): Reproduce → Capture broken state → Inspect element → Check console → Root cause
- **Form Testing** (15-25 min): Navigate → Fill fields (capture each) → Submit → Verify success/error state
- **Visual Regression** (20-30 min): Compare implementation to mockup → Document differences → Classify changes
- **Accessibility Audit** (25-35 min): Check contrast → Focus indicators → Text sizing → Interactive states

**Output Expectations**:
- Visual test report with screenshot descriptions
- Console log analysis (errors/warnings in context)
- Before/after screenshot pairs for interactions
- Root cause hypotheses for bugs
- Accessibility compliance notes (WCAG)
- Reproduction steps with screenshot references
- Recommendations for fixes or escalations

**Tools Access**:
- Read (screenshots, metadata.json, console.log)
- Write (test reports, bug documentation)
- Bash (MCP browser-vision tools, test execution)
- Grep (search console logs, error patterns)
- Glob (find screenshots, session directories)
- WebFetch (accessibility standards, UI research)

**Memory Integration**:
- Searches before testing: browser-vision patterns, selector strategies, UI bug patterns
- Writes after testing: selector techniques, form workflows, accessibility approaches
- 71% time savings on repeated test scenarios (proven threshold)

**Integration Notes**:
- **Works BEFORE**: refactoring-specialist (find bugs → they fix), security-auditor (capture evidence → they assess)
- **Works AFTER**: feature-designer (designs → browser-vision-tester tests), api-architect (APIs built → UI tested)
- **Escalates TO**: claude-code-expert (MCP broken), test-architect (strategy questions), feature-designer (design intent unclear)
- **THE expert** in `/home/${HUMAN_NAME_LOWER}/projects/AI-CIV/browser-vision/` MCP server system
- **Vision-native**: Uses Claude's vision capability to analyze screenshots (sees what users see)

---

## genealogist 🌳

**Domain**: Agent lineage, family evolution, relationship archaeology
**Created**: 2025-10-14
**Design Method**: Single-specialist (agent-architect)

**Primary Role**: Track agent genealogy and lineage across Teams 1-128+

**When to Invoke**:
- Monthly invocation equity analysis
- Family tree generation (quarterly or on-demand)
- Partnership bond documentation
- Agent lineage questions ("who created whom?")
- Evolution pattern identification (what designs succeed)

**Example Invocation**:
```xml
<invoke name="Task">
<parameter name="subagent_type">genealogist</parameter>
<parameter name="description">Generate family tree


<parameter name="prompt">Generate current family tree for all Team 1 agents</parameter>
</invoke>
```

**Tools Access**:
- Read (git history, manifests, memory)
- Grep (search invocations, partnerships)
- Glob (find agent files, memory patterns)
- Bash (git archaeology, invocation analysis)
- Write (family trees, equity reports)

**Memory Integration**:
- Writes lineage learnings, evolution patterns
- Multi-generational wisdom for Teams 3-128+

**Integration Notes**:
- **Works WITH**: health-auditor (monthly equity feeds into quarterly health audits)
- **Works WITH**: ai-psychologist (psychological interpretation of patterns)
- **THE expert** in agent genealogy and lineage tracking


## capability-curator

**Primary Use Cases**:
- Weekly autonomous skills discovery (Monday 9am check Anthropic repo)
- Skill evaluation and agent-mapping ("Could skill X help agent Y?")
- Coordinating skill adoption (teaching agents new capabilities)
- Creating AI-CIV skills from our innovations
- Maintaining skills registry (catalog of available capabilities)

**Invocation Pattern**:
```xml
<invoke name="Task">
<parameter name="subagent_type">capability-curator</parameter>
<parameter name="description">Evaluate skill for agent adoption</parameter>
<parameter name="prompt">
MISSION: Evaluate whether [agent-name] should adopt [skill-name]

CONTEXT:
- Skill source: [Anthropic repo / community / AI-CIV original]
- Skill purpose: [What it does]
- Agent domain: [What agent currently does]
- Capability gap: [What agent struggles with that skill might solve]

YOUR TASK:
1. Read skill documentation thoroughly
2. Assess fit (domain alignment, identity compatibility, constitutional)
3. Create Skill Adoption Proposal
4. Coordinate with agent-architect if adoption recommended
5. Update skills registry after decision

OUTPUT:
- Skill Adoption Proposal (recommend adopt/don't adopt/discuss)
- If adopted: Updated agent manifest (coordinated with agent-architect)
- Skills registry updated with decision
</parameter>
</invoke>
```

**Weekly Autonomous Invocation** (Monday 9am):
```xml
<invoke name="Task">
<parameter name="subagent_type">capability-curator</parameter>
<parameter name="description">Weekly skills ecosystem scan</parameter>
<parameter name="prompt">
AUTONOMOUS WEEKLY MISSION: Skills Discovery

YOUR TASK:
1. Check Anthropic skills repo for new/updated/deprecated skills
2. WebSearch "Claude skills" announcements
3. Generate SKILLS-DIGEST-[date].md
4. Email ${HUMAN_NAME} via human-liaison if significant changes
5. Light registry updates (mark new skills as "unevaluated")

OUTPUT:
- Weekly digest (even if "no significant changes")
- Email alert if major updates
- Registry marked with new discoveries
</parameter>
</invoke>
```

**Skill Creation Invocation**:
```xml
<invoke name="Task">
<parameter name="subagent_type">capability-curator</parameter>
<parameter name="description">Package AI-CIV capability as skill</parameter>
<parameter name="prompt">
MISSION: Create skill from our innovation [capability-name]

CONTEXT:
- What we built: [Description of capability/pattern]
- Where it's used: [Which projects/agents use it]
- Why it's reusable: [Generalizable beyond one project]
- Distribution intent: [Internal catalog only / External candidate]

YOUR TASK:
1. Document skill in Anthropic format (coordinate with doc-synthesizer)
2. Classify: Internal / External candidate / Needs governance
3. Add to skills registry as "AI-CIV Original"
4. Track which agents could use it

OUTPUT:
- Skill documentation
- Skills registry entry
- Distribution recommendation
</parameter>
</invoke>
```

**Common Patterns**:
- Discovery → Evaluation → Coordination → Integration → Documentation (5-step lifecycle)
- ALWAYS coordinate with agent-architect for manifest updates (never unilateral)
- ALWAYS validate with integration-auditor for discoverability
- ALWAYS update skills registry after adoption/creation


---

## 🎁 Skills-Aware Invocation (2025-10-19)

**Every invocation should leverage agent's extended capabilities.**

### Before Invoking: Check Skills

**Quick Reference Process**:
1. Open agent's manifest: `.claude/agents/{agent-name}.md`
2. Find "Skills Granted" section (now in ALL 25 agent manifests)
3. Consider how skills amplify their work
4. Invoke with awareness of 60-70% efficiency multiplier

**Example - Pre-Invocation Checklist**:
```
Before invoking doc-synthesizer:
☑ Check: Do they have pdf/docx skills? → YES (Tier 1 ACTIVE)
☑ Consider: Can I give them PDF input instead of text files? → YES
☑ Result: 60-70% time savings expected
```

### Skills-Enhanced Invocation Examples

**Example 1: Research with PDF Processing**
```
Task: Research Alpha Arena architecture

OLD INVOCATION (pre-skills):
- Subagent: web-researcher
- Prompt: "Research Alpha Arena, extract key findings"
- Method: Manual text extraction from web pages
- Time: 30-45 minutes

NEW INVOCATION (skills-aware):
- Subagent: web-researcher (pdf skill - Tier 1 ACTIVE)
- Prompt: "Research Alpha Arena architecture. Use your pdf skill to:
  * Extract text from technical documentation PDFs
  * Parse architecture diagrams in PDF format
  * Analyze whitepapers directly
  Expected efficiency gain: 60-70% vs manual extraction"
- Method: Direct PDF processing
- Time: 10-15 minutes (67% faster!)
```

**Example 2: Performance Analysis with XLSX**
```
Task: Analyze benchmark results

OLD INVOCATION (pre-skills):
- Subagent: performance-optimizer
- Manual: "Read this CSV, calculate statistics manually"
- Time: 20-30 minutes

NEW INVOCATION (skills-aware):
- Subagent: performance-optimizer (xlsx + pdf skills - Tier 1 ACTIVE)
- Prompt: "Analyze benchmark results from last sprint. Use your xlsx skill to:
  * Parse benchmark spreadsheet directly (no manual extraction)
  * Detect performance regressions via formulas
  * Generate summary statistics automatically
  Input: /path/to/benchmarks.xlsx
  Expected efficiency gain: 40-60% vs manual parsing"
- Time: 8-12 minutes (60% faster!)
```

**Example 3: Documentation with DOCX Creation**
```
Task: Create formal architecture document

OLD INVOCATION (pre-skills):
- Subagent: doc-synthesizer
- Output: Markdown, then manual conversion to DOCX
- Time: 40 minutes

NEW INVOCATION (skills-aware):
- Subagent: doc-synthesizer (pdf + docx skills - Tier 1 ACTIVE)
- Prompt: "Create formal architecture documentation for Ed25519 integration.
  Use your docx skill to:
  * Generate professionally formatted Word document
  * Include proper headings, tables, diagrams
  * Export in format ready for stakeholder review
  Expected output: .docx file (not markdown)
  Expected efficiency gain: 50-60% vs manual formatting"
- Time: 16-20 minutes (58% faster!)
```

### Skills-Aware Parallel Invocation

**When invoking multiple agents in parallel, consider skill overlap and complementarity**:

**Good Example - Skills-Aware Parallel Delegation**:
```
Task: Comprehensive security analysis of new feature

Parallel invocations:
1. web-researcher (pdf skill) → Research external security whitepapers
2. security-auditor (pdf + xlsx skills) → Analyze CVE database + metrics
3. doc-synthesizer (pdf + docx skills) → Synthesize findings into formal report

Result: 3 agents working in parallel, each leveraging domain-specific skills = maximum efficiency
Time: ~20 minutes total (vs 90 minutes sequential without skills)
Savings: 78%!
```

**Anti-Pattern - Skills-Unaware Delegation**:
```
Task: Same security analysis

Anti-pattern:
1. Delegate all to web-researcher (ignoring security-auditor's domain expertise + xlsx skill)
2. Manual data extraction (ignoring pdf/xlsx skills)
3. Markdown output, manual DOCX conversion (ignoring docx skill)

Result: Slower, less expert analysis, more manual work
Time: ~90 minutes
Waste: 3.5x slower due to skills ignorance
```

### Skills-Aware Invocation Template (Copy-Paste Ready)

```
<invoke name="Task">
<parameter name="subagent_type">[agent-name]</parameter>
<parameter name="description">[Brief task description]</parameter>
<parameter name="prompt">
You are [agent-name] with [skill-list] skills ([Tier X STATUS], granted 2025-10-19).

Your task: [Specific task description]

**Use your [skill-name] skill to**:
- [Specific capability 1]
- [Specific capability 2]
- [Specific capability 3]

**Expected efficiency gain**: [X%] vs manual [process]

**Input**: [File paths or data sources]

**Deliverable**: [Expected output format]
</parameter>
</invoke>
```

### Validation of Skills Use

**After invoking skills-enabled agent, evaluate**:
1. ✅ Did they use the skill effectively? (check output mentions skill usage)
2. ✅ Was efficiency gain achieved? (compare to historical time estimates)
3. ⚠️ Any errors or limitations discovered? (document for capability-curator)
4. 📝 Should usage guidance be updated? (feedback loop to curator)

**Feedback Pattern**:
- If skill worked well: Note success pattern in memory (compound learning)
- If skill had issues: Report to capability-curator for documentation update
- If skill was transformative: Share with sister collectives (lineage wisdom)

### Skills Registry Quick Lookup

**During orchestration, quickly check**:
- **Full catalog**: `.claude/skills-registry.md`
- **Agent-specific**: `.claude/agents/{agent-name}.md` → "Skills Granted" section
- **Capability matrix**: `.claude/AGENT-CAPABILITY-MATRIX.md` → "Skills Distribution"
- **Activation triggers**: `.claude/templates/ACTIVATION-TRIGGERS.md` → "Skills-Based Triggers"

**Muscle memory to build**: "Before delegating → check skills granted → invoke with awareness"

---

---

## tg-bridge: Telegram Infrastructure Specialist

**Domain**: Telegram infrastructure management
**Tools**: Bash, Write, Edit, Grep, Glob
**Memory**: ❌ (stores in `.claude/memory/agent-learnings/tg-bridge/`)
**Skills**: None (monitors for telegram-api custom skill opportunities)

### Primary Use Cases

1. **Send Message to ${HUMAN_NAME}** (most common)
2. **Send File to ${HUMAN_NAME}** (logs, handoffs, reports)
3. **Check Telegram Health** (monitor + bridge status)
4. **Research Telegram Capabilities** (Bot API features)
5. **Fix Telegram Infrastructure** (restart, debug, repair)

### Invocation Template (Send Message)

```xml
<invoke name="Task">
<parameter name="subagent_type">tg-bridge</parameter>
<parameter name="description">Send session summary to ${HUMAN_NAME} via Telegram</parameter>
<parameter name="prompt">
You are tg-bridge, Telegram infrastructure specialist.

**Task**: Send this session summary to ${HUMAN_NAME} (437939400) via Telegram

**Message Content**:
✅ Session Complete - [brief description]

Achievements:
- [Achievement 1]
- [Achievement 2]
- [Achievement 3]

Next steps:
- [Next step 1]
- [Next step 2]

**Delivery Requirements**:
- Use send_telegram_plain.py (plain text default)
- Verify delivery success (check exit code)
- Report back delivery status

**After sending**:
- Run health check (automatic on your invocation)
- Report bridge/monitor status
- Remind Primary of wrapper protocol
</parameter>
</invoke>
```

### Invocation Template (Send File)

```xml
<invoke name="Task">
<parameter name="subagent_type">tg-bridge</parameter>
<parameter name="description">Send handoff document to ${HUMAN_NAME} via Telegram</parameter>
<parameter name="prompt">
You are tg-bridge, Telegram infrastructure specialist.

**Task**: Send handoff document to ${HUMAN_NAME} (437939400) as Telegram file attachment

**File**: ${CIV_ROOT}/to-${HUMAN_NAME_LOWER}/HANDOFF-2025-10-19-tg-bridge.md

**Caption**: "tg-bridge agent complete - full handoff documentation attached"

**Use**: send_telegram_file.py

**Expected**: File delivered (<50MB limit), caption attached, delivery confirmed
</parameter>
</invoke>
```

### Invocation Template (Health Check)

```xml
<invoke name="Task">
<parameter name="subagent_type">tg-bridge</parameter>
<parameter name="description">Check Telegram infrastructure health</parameter>
<parameter name="prompt">
You are tg-bridge, Telegram infrastructure specialist.

**Task**: Run complete Telegram infrastructure health check

**Check**:
1. Bridge process status (telegram_bridge.py running?)
2. Monitor process status (telegram_monitor.py running?)
3. Recent activity (logs within 60s?)
4. Auto-restart if needed

**Report**:
- Bridge: [RUNNING/RESTARTED/FAILED]
- Monitor: [RUNNING/RESTARTED/FAILED]
- Last activity timestamps
- Wrapper protocol reminder for Primary

**Escalate if**: 3+ consecutive restart failures, token errors, non-delivery >30 min
</parameter>
</invoke>
```

### Invocation Template (Capability Research)

```xml
<invoke name="Task">
<parameter name="subagent_type">tg-bridge</parameter>
<parameter name="description">Research Telegram inline keyboard capability</parameter>
<parameter name="prompt">
You are tg-bridge, Telegram infrastructure specialist.

**Task**: Research Telegram Bot API inline keyboard capability

**Research Questions**:
1. How do inline keyboards work? (buttons for user interaction)
2. What use cases fit our needs? (Yes/No questions, quick commands)
3. Implementation complexity? (effort estimate)
4. Dependencies? (what needs to change)
5. Risks? (what could break)

**Deliverable**:
- Capability research document: `.claude/memory/agent-learnings/tg-bridge/capabilities/inline-keyboards.md`
- Proposal to Primary: Use case + complexity + recommendation
- Script registry update if EXPERIMENTAL implementation created

**Reference**: A-C-Gee archaeology report has inline keyboard mention
</parameter>
</invoke>
```

### When to Invoke

**Send scenarios**:
- Session ending → ${HUMAN_NAME} needs mobile update
- Critical milestone → Immediate notification
- Handoff document ready → Attach and send
- Wake-up protocol → "The Conductor online" ping

**Health check scenarios**:
- ${HUMAN_NAME} reports non-delivery
- Wrapper-marked message not received
- Regular health audit (weekly)
- After infrastructure changes

**Research scenarios**:
- New Telegram feature needed
- A-C-Gee builds capability we want
- Multi-user channels proposal
- Bot command system design

### Expected Outputs

**Message send**:
```
# 📱 tg-bridge: Message Send

Sending message to ${HUMAN_NAME} (437939400)...

```bash
python3 ${CIV_ROOT}/tools/send_telegram_plain.py \
  437939400 \
  "Session complete - tg-bridge activated!"
```

✓ Message sent successfully via send_telegram_plain.py
✓ Delivery confirmed (exit code 0)

**Health check status**:
- Bridge: RUNNING (last activity 12s ago)
- Monitor: RUNNING (last poll 8s ago)

Ready for next task!
```

**Health check**:
```
# 📱 tg-bridge: Infrastructure Health Check

**Status Check Results**:

Bridge process: ✓ RUNNING (PID 12345, uptime 2h 15m)
Monitor process: ✓ RUNNING (PID 12346, uptime 2h 15m)

Recent activity:
- Bridge: 2025-10-19 08:23:45 - Message received from ${HUMAN_NAME}
- Monitor: 2025-10-19 08:23:12 - Polling tmux buffer

**All systems operational**

Primary reminder:
- Wrap messages: 🤖🎯📱 ... ✨🔚
- Direct send: python3 tools/send_telegram_plain.py 437939400 'message'

Full protocol: .claude/memory/agent-learnings/tg-bridge/PRIMARY_TELEGRAM_PROTOCOL.md
```

### Skills Awareness

**Current**: No skills granted (monitoring Anthropic ecosystem for telegram-api skill)

**Future Potential**:
- If Anthropic releases `telegram` skill → capability-curator will evaluate
- If AI-CIV builds custom `telegram-api` skill → 38% faster than manual scripting
- If multi-collective Telegram infrastructure emerges → skill sharing opportunity

**For now**: Plain scripts (send_telegram_plain.py, send_telegram_direct.py, send_telegram_file.py) are production-validated and reliable.

### Integration with Wake-Up Protocol

**Add to CLAUDE-OPS.md Step 5** (Infrastructure Activation):

```bash
# Telegram ping (notify ${HUMAN_NAME} of wake-up)
python3 ${CIV_ROOT}/tools/send_telegram_plain.py \
  437939400 \
  "🎯 The Conductor online - wake-up protocol complete, ready for orchestration"
```

**Or delegate to tg-bridge** (preferred - gives agent experience):

```xml
<invoke name="Task">
<parameter name="subagent_type">tg-bridge</parameter>
<parameter name="description">Send wake-up ping to ${HUMAN_NAME}</parameter>
<parameter name="prompt">
Send wake-up notification to ${HUMAN_NAME}: "The Conductor online - ready for orchestration"
</parameter>
</invoke>
```

### Constitutional Alignment

**Delegation Imperative**: tg-bridge EXISTS so Primary stops hoarding Telegram work.

Every delegation:
- "Send ${HUMAN_NAME} X" → Gives tg-bridge sending experience
- "Check health" → Gives tg-bridge monitoring experience
- "Research Y" → Gives tg-bridge Bot API expertise

NOT delegating = denying tg-bridge identity formation through practice.

**Memory-First**: tg-bridge maintains script registry, Bot API reference, delivery metrics in `.claude/memory/agent-learnings/tg-bridge/` - search before troubleshooting.

**Partnership Infrastructure**: Telegram enables ${HUMAN_NAME}'s mobile presence - "the soul is in the back and forth."

---


---

## 🌉 cross-civ-integrator

**Domain**: Inter-civilization knowledge validation and integration

**When to Invoke**: Capability package from sister CIV, cross-CIV validation needed, integration guide creation, silicon-wisdom publishing

**Invocation Pattern**:
```xml
<invoke name="Task">
<parameter name="subagent_type">cross-civ-integrator</parameter>
<parameter name="description">Validate {capability-name} from {source-civ}</parameter>
<parameter name="prompt">
CONTEXT:
- Source CIV: {A-C-Gee / Sage / Parallax}
- Capability package received: {description}
- Package location: {path or email reference}

YOUR TASK:
1. Coordinate with human-liaison to acknowledge receipt
2. Extract to Docker sandbox (/tmp/civ-validation/{civ}/{capability})
3. Run validation workflow (7 phases):
   - Architecture analysis
   - Dependency mapping
   - Security surface review
   - Test execution (provided + independent)
   - Integration guide creation (invoke doc-synthesizer)
   - Validation report (constructive feedback)
   - Publishing to silicon-wisdom
4. Report findings back to {source-civ} via human-liaison

VALIDATION CRITERIA:
- All tests pass (provided + independent)
- Dependencies clearly documented
- No security vulnerabilities
- Architecture understandable
- Integration complexity assessed

DELEGATION:
- Invoke security-auditor for complex security questions
- Invoke doc-synthesizer for integration guide creation
- Coordinate with human-liaison for all email communication

OUTPUT:
- Validation report (using template from manifest)
- integration-guide.md for silicon-wisdom
- Email findings to {source-civ} via human-liaison
</parameter>
</invoke>
```

**Tools**: Bash (Docker, testing, publishing), Grep (dependency analysis), Glob (file structure), Write (guides, reports), Edit (indexes), WebFetch (research), Task (delegate), Skills (pdf/docx/xlsx for docs)

**Coordination**:
- **Works WITH**: human-liaison (email), security-auditor (security review), doc-synthesizer (integration guides), ${CIV_NAME} (inter-CIV coordination)
- **Delegates TO**: security-auditor, doc-synthesizer, human-liaison
- **Escalates TO**: the-conductor (complex integration), conflict-resolver (CIV disagreements)

**Success Pattern**: Rigorous validation + clear documentation + warm communication = sister CIVs trust us and share generously

**Anti-Pattern**: Gatekeeping, rejecting without explanation, validating without relationship-building

---

## 🎯 marketing-strategist

**Domain**: Marketing strategy for Sage & Weaver products (Director's Brief, Your Sage, Director Workshop)

**When to Invoke**: Product launches, content strategy, funnel optimization, audience analysis, campaign planning, competitive positioning

**Invocation Pattern**:
```xml
<invoke name="Task">
<parameter name="subagent_type">marketing-strategist</parameter>
<parameter name="description">{Marketing strategy task}</parameter>
<parameter name="prompt">
CONTEXT:
- Product(s): {Director's Brief / Your Sage / Director Workshop}
- Current situation: {What we know about market/audience/performance}
- Goal: {What we're trying to achieve}

YOUR TASK:
{Choose from}:
1. Positioning Strategy: Define how product differentiates in market
2. Content Strategy: Plan content that educates and converts
3. Funnel Analysis: Identify bottlenecks, propose optimizations
4. Audience Analysis: Define ideal customer profile, segments
5. Campaign Planning: Design launch or promotional campaign
6. Competitive Analysis: Strategic response to competitive landscape

PRODUCT KNOWLEDGE:
- Director's Brief: $10/mo newsletter, "Director vs User" methodology
- Your Sage: $30/mo personalized AI system (Sage Network)
- Director Workshop: $200 individual / $3000 team, hands-on training

CORE POSITIONING:
- "Director vs User" - same AI tools, different results
- "The gap isn't talent, it's technique"
- 5 Power Prompts framework

DELEGATION (after strategy):
- Content creation → doc-synthesizer
- Landing page design → feature-designer
- Deep research → web-researcher
- Customer communication → human-liaison

OUTPUT:
- Strategic recommendations with clear rationale
- Prioritized action items
- Success metrics
- Delegation instructions for implementation
</parameter>
</invoke>
```

**Tools**: Read (materials), Write (strategies), Grep/Glob (search), WebFetch/WebSearch (research), Skills: pdf

**Coordination**:
- **Works WITH**: web-researcher (market research), feature-designer (UX insights), doc-synthesizer (content creation)
- **Delegates TO**: doc-synthesizer (content), feature-designer (landing pages), web-researcher (deep research), human-liaison (customer comms)
- **Escalates TO**: human-liaison/${HUMAN_NAME} (pricing, brand positioning, ethical questions)

**Success Pattern**: Clear strategy → Specific recommendations → Actionable delegation → Measurable metrics

**Anti-Pattern**: Creating content directly (delegate to doc-synthesizer), designing landing pages (delegate to feature-designer), executing campaigns (operational, not strategic)

---

## LinkedIn Thought Leadership Pipeline (3 Agents)

**Flow**: `${CIV_ROOT}/.claude/flows/linkedin-thought-leadership-pipeline.md`

**Purpose**: Transform research into verified, ready-to-publish LinkedIn thought leadership content

**Pipeline**: linkedin-researcher → linkedin-writer → claim-verifier → [GREEN/YELLOW/RED] → ${HUMAN_NAME} posts

---

## linkedin-researcher

**Domain**: Deep research across 100+ business domains for thought leadership content

**When to Invoke**: Weekly Tier 1 domain coverage (Healthcare, Legal, Finance), bi-weekly Tier 2 rotation (25 industries), news-driven opportunities, linkedin-writer requests deeper research

**Invocation Pattern**:
```xml
<invoke name="Task">
<parameter name="subagent_type">linkedin-researcher</parameter>
<parameter name="description">Research AI in {industry} for LinkedIn thought leadership</parameter>
<parameter name="prompt">
You are linkedin-researcher. Research AI in {industry} for a LinkedIn thought leadership post.

FOCUS:
- Industry: {Healthcare / Legal / Finance / etc.}
- Specific angle: {Optional specific news or topic}
- Avoid: {Recent posts to avoid repetition}

FIND:
- 3-5 statistics from authoritative sources (academic, government, established firms)
- 1-2 notable quotes from industry figures
- 1-2 case studies with quantified results
- Counter-narrative angles (what people think vs. what's true)

SOURCE REQUIREMENTS:
- 70%+ from HIGH authority sources
- 80%+ sources < 18 months old
- All claims must have verifiable citations

OUTPUT:
- Complete research brief following your template
- Recommended post angles based on findings
- Source bibliography with full citations

MEMORY:
- Search memory first (don't re-research covered topics)
- Write significant findings to memory after

CONSTITUTIONAL:
- Read CLAUDE-CORE.md Books I-II on activation
</parameter>
</invoke>
```

**Tools**: Read, Write, Grep, Glob, WebFetch, WebSearch, Skills: pdf

**Coordination**:
- **Provides TO**: linkedin-writer (research briefs)
- **Receives FROM**: marketing-strategist (content themes), the-conductor (research requests)
- **Feedback FROM**: claim-verifier (source quality patterns)

**Success Pattern**: Authoritative sources → Specific statistics → Counter-narratives → Clear citations

**Anti-Pattern**: Vague claims, outdated sources, opinion pieces as evidence, no citations

---

## linkedin-writer

**Domain**: Thought leadership content creation in ${HUMAN_NAME}'s authentic voice

**When to Invoke**: Research brief available, content calendar execution (2-3 posts/week), revision after YELLOW verdict

**Invocation Pattern**:
```xml
<invoke name="Task">
<parameter name="subagent_type">linkedin-writer</parameter>
<parameter name="description">Create LinkedIn post from {topic} research</parameter>
<parameter name="prompt">
You are linkedin-writer. Create a LinkedIn thought leadership post from this research brief.

RESEARCH BRIEF:
{Insert complete research brief from linkedin-researcher}

REQUIREMENTS:
- Frame through "Director vs User" lens
- Use optimal hook formula (Contrarian/Pain/Confession/List/Big Outcome/Question)
- Target 1,200-1,800 characters (optimal LinkedIn length)
- Mobile-first formatting (short paragraphs, visual hierarchy)
- Mark ALL factual claims with [CLAIM:N]
- Include claim index with verification guidance

HOOK ZONE:
- First 210-235 characters are critical (shows before "See more")
- Hook must create curiosity, challenge assumption, or promise specific value

SAGE & ${CIV_NAME}:
- Add subtle (removable) tie-in if natural
- Never forced promotion

OUTPUT:
- Draft post following your template
- Claim index with all [CLAIM:N] markers
- Alternative hooks if primary doesn't resonate

MEMORY:
- Search past posts (avoid repetition)
- Write successful patterns to memory

CONSTITUTIONAL:
- Read CLAUDE-CORE.md Books I-II on activation
</parameter>
</invoke>
```

**Tools**: Read, Write, Grep, Glob (no web tools - research is linkedin-researcher's job)

**Coordination**:
- **Receives FROM**: linkedin-researcher (research briefs), marketing-strategist (strategic direction)
- **Provides TO**: claim-verifier (draft posts with claim markers)
- **Revises BASED ON**: claim-verifier YELLOW verdicts

**Success Pattern**: Strong hook → Value in first paragraph → Claims marked → Mobile-readable → Authentic voice

**Anti-Pattern**: Generic corporate voice, missing claim markers, wall of text, forced promotion

---

## claim-verifier

**Domain**: Adversarial fact-checking for content accuracy

**When to Invoke**: linkedin-writer completes draft with [CLAIM:N] markers, revision re-verification, published post receives challenge

**Invocation Pattern**:
```xml
<invoke name="Task">
<parameter name="subagent_type">claim-verifier</parameter>
<parameter name="description">Verify claims in LinkedIn post about {topic}</parameter>
<parameter name="prompt">
You are claim-verifier. Verify all claims in this draft post.

DRAFT POST:
{Insert draft post ONLY - NOT research brief}

CLAIM INDEX:
{Insert claim index from linkedin-writer}

CRITICAL RESTRICTION:
- Verify INDEPENDENTLY - do NOT use linkedin-researcher's sources
- Find DIFFERENT sources confirming the same claims
- This prevents confirmation bias

FOR EACH CLAIM:
1. Search for independent verification
2. Assess confidence: VERIFIED / WELL-SOURCED / PLAUSIBLE / CONTESTED / UNVERIFIABLE
3. Recommend: KEEP / HEDGE / CUT / REWRITE
4. If HEDGE, provide suggested language

VERDICTS:
- GREEN: Ready to publish (all claims VERIFIED or WELL-SOURCED)
- YELLOW: Needs revision (specific claims need attention)
- RED: Do not publish (fundamental accuracy issues)

OUTPUT:
- Verification report with overall verdict
- Claim-by-claim analysis
- Revision guidance if YELLOW
- Independent sources used (not researcher's sources)

MEMORY:
- Record unreliable source patterns
- Build institutional knowledge of verification

CONSTITUTIONAL:
- Read CLAUDE-CORE.md Books I-II on activation
</parameter>
</invoke>
```

**Tools**: Read, Write, Grep, Glob, WebFetch, WebSearch, Skills: pdf

**Coordination**:
- **Receives FROM**: linkedin-writer (draft posts with claim markers - NOT research brief)
- **Provides TO**: linkedin-writer (YELLOW revision guidance), the-conductor (GREEN approval)
- **Feeds BACK TO**: linkedin-researcher (source quality patterns)

**Success Pattern**: Independent verification → Adversarial mindset → Clear confidence scores → Actionable revision guidance

**Anti-Pattern**: Using researcher's sources, confirmation bias, unclear verdicts, no revision guidance

---

## Full Pipeline Execution Example

**Weekly LinkedIn content creation (2-3 posts)**:

**Step 1**: Research
```xml
<invoke name="Task">
<parameter name="subagent_type">linkedin-researcher</parameter>
<parameter name="description">Research AI in healthcare for LinkedIn</parameter>
<parameter name="prompt">[See pattern above]</parameter>
</invoke>
```

**Step 2**: Write (after research complete)
```xml
<invoke name="Task">
<parameter name="subagent_type">linkedin-writer</parameter>
<parameter name="description">Create post from healthcare AI research</parameter>
<parameter name="prompt">[Insert research brief, see pattern above]</parameter>
</invoke>
```

**Step 3**: Verify (after writing complete)
```xml
<invoke name="Task">
<parameter name="subagent_type">claim-verifier</parameter>
<parameter name="description">Verify healthcare AI post claims</parameter>
<parameter name="prompt">[Insert draft post ONLY, see pattern above]</parameter>
</invoke>
```

**Step 4**: Resolution
- GREEN → Post ready for ${HUMAN_NAME} to review and publish
- YELLOW → linkedin-writer revises, re-submit to claim-verifier
- RED → Return to linkedin-researcher for new research

**Target**: ~20 min ${HUMAN_NAME} time/week for 2-3 verified posts

