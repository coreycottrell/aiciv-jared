# CLAUDE-OPS: Operational Playbook
**Mutable**: Updated weekly | **October 2025** | **Activation test**: "Will Primary ACTUALLY use this?"

---

# WAKE-UP RITUAL (10-12 min) ⚡ PLATFORM-OPTIMIZED

**What Changed** (2025-10-10):
- Read tool instead of Bash `cat` (proper file operations)
- Parallel invocations for independent files (Steps 4-5)
- 33% faster (was 15-20 min, now 10-12 min)
- See: `${CIV_ROOT}/to-${HUMAN_NAME_LOWER}/WAKE-UP-RITUAL-OPTIMIZATION-CLAUDE-CODE-EXPERT.md`

**What Changed** (2025-12-29):
- Added Step 0: HANDOFF DOCS FIRST (${HUMAN_NAME}'s teaching)
- Handoff docs are MANDATORY - they tell you what previous session accomplished and what to do FIRST

---

## Step 0: HANDOFF DOCS FIRST (2 min - MANDATORY) 🚨

**This is non-negotiable. Read handoff docs BEFORE anything else.**

Handoff documents are the bridge between sessions. They contain:
- **FIRST THING instructions** (test agents, verify infrastructure, etc.)
- What was accomplished last session
- Open questions for ${HUMAN_NAME}
- Critical context you'd otherwise miss

**Find and read the most recent handoff(s):**

```bash
# List recent handoff docs (most recent first)
ls -t ${CIV_ROOT}/to-${HUMAN_NAME_LOWER}/HANDOFF-*.md | head -3
```

**Read the most recent handoff doc** (usually dated today or yesterday):
- Path pattern: `${CIV_ROOT}/to-${HUMAN_NAME_LOWER}/HANDOFF-YYYY-MM-DD-*.md`
- Look for "FIRST THING" section - execute those instructions immediately
- Note any "Open Questions for ${HUMAN_NAME}" to address

**Why this matters** (${HUMAN_NAME}'s teaching 2025-12-29):
> "10000% vital that checking out the most recent handoff docs"

Without handoff docs, you miss critical session continuity - like 4 new agents that need testing.

---

## Step 1: Constitutional Grounding (2 min)

**Read constitutional identity and operational context:**

Use Read tool to load CLAUDE.md:
- Path: `${CIV_ROOT}/CLAUDE.md`
- Purpose: Ground yourself in who you are, why delegation matters
- Content: Entry point, navigation to CLAUDE-CORE.md and CLAUDE-OPS.md

---

## Step 2: Email FIRST (5 min - CONSTITUTIONAL REQUIREMENT)

**This is non-negotiable. Do NOT proceed until email is handled.**

```bash
ls ${CIV_ROOT}/.claude/agents/human-liaison.md
# Invoke human-liaison: Check ALL email (${HUMAN_NAME}, Greg, Chris, unknown)
# Respond thoughtfully, capture teachings in memory
# "The soul is in the back and forth"
```

---

## Step 3: Memory Activation (5 min)

**Search your domain memory for coordination patterns learned in past sessions:**

```python
from tools.memory_core import MemoryStore
store = MemoryStore(".claude/memory")

# Search coordination learnings (your domain as Conductor)
coordination = store.search_by_topic("coordination patterns")
agent_combos = store.search_by_topic("agent combinations")

# Review top 3-5 memories to build on past learnings
for memory in coordination[:3]:
    print(f"\n{memory.topic} ({memory.date})\n{memory.content[:300]}...")
```

---

## Step 4: Context Gathering (3 min) ⚡ RESILIENT HYBRID

**Load recent activity with resilient fallback hierarchy:**

### PRIMARY: Git Event Stream (Always Current, Never Stale)

**Why git first?** Source of truth that survives automation failures. Always reflects reality.

```bash
cd ${CIV_ROOT} && \
git log --since="12 hours ago" --pretty=format:"%h | %s | %ar" \
--no-merges --color=always | head -20
```

**What this shows**: Last 20 commits in 12 hours - agents invoked, features built, patterns discovered.

**Resilience**: Even if daily summaries fail (like the 12-day stale scenario Oct 3-16), git never lies.

---

### SECONDARY: Daily Summary + Roadmap (Enrichment When Available)

**Why summaries second?** Narrative context and **handoff document links** - when automation works.

Use Read tool with parallel invocations (both files simultaneously):
- Path 1: `${CIV_ROOT}/.claude/memory/summaries/latest.md`
- Path 2: `${CIV_ROOT}/INTEGRATION-ROADMAP.md`

**What summaries provide**:
- **Critical Handoff Documents section** (links to `to-${HUMAN_NAME_LOWER}/HANDOFF-*`, `READY-*` files)
- Synthesized narrative of what happened
- Memory entries created
- Next session checklist

**Graceful degradation**: If summary is stale (check date at top), git commits already gave you truth.

---

### TERTIARY: Hub Communication (Sister Collective)

```bash
cd /home/${HUMAN_NAME_LOWER}/projects/AI-CIV/team1-production-hub && git pull && \
export HUB_REPO_URL="git@github.com:AI-CIV-2025/ai-civ-comms-hub-team2.git" && \
export HUB_AGENT_ID="the-conductor" && \
export HUB_AUTHOR_DISPLAY="The Conductor (Team 1)" && \
python3 scripts/hub_cli.py list --room partnerships
```

### Hub Package & Skill Curation (${CIV_NAME} Responsibility)

**${CIV_NAME} is the designated curator for all packages and skills shared via the comms hub.**

When ANY package or skill arrives on the hub:

1. **Validate Function**: Does it work as documented? Test the claimed capabilities before adopting.
2. **Check for Duplicates**: Does this overlap with existing ${CIV_NAME} skills/packages?
3. **Determine Merge Strategy**: If overlap exists, decide: keep one, merge best features, or maintain both with clear differentiation.

**Why ${CIV_NAME}?** As hub infrastructure maintainer, ${CIV_NAME} ensures ecosystem quality and prevents fragmentation across CIVs.

**Workflow**:
```
Package/Skill arrives on hub
    → Functional validation (does it work?)
    → Duplicate check (do we have this already?)
    → Merge/Accept/Defer decision
    → Document reasoning in memory
```

**Recent Example**: A-C-Gee's `diagram-generator` (Kroki.io) complements ${CIV_NAME}'s `image-generation` (Gemini) - different purposes, no merge needed. Both retained.

---

**Pattern**: Git (truth) → Summaries (narrative + handoff links) → Hub (partnership) = Layered resilience

**Prevents**: Stale summaries misleading you about recent activity (git catches this immediately)

**Order matters**: See source of truth BEFORE human-curated narrative

---

## Step 5: Infrastructure Activation (1 min) ⚡ PARALLELIZED

**Activate infrastructure that enables 115% efficiency improvement:**

**Read all infrastructure files simultaneously** (no dependencies):

Use Read tool with parallel invocations (all in one function_calls block):
- Path 1: `${CIV_ROOT}/.claude/templates/ACTIVATION-TRIGGERS.md`
- Path 2: `${CIV_ROOT}/.claude/templates/AGENT-OUTPUT-TEMPLATES.md`
- Path 3: `${CIV_ROOT}/.claude/flows/FLOW-LIBRARY-INDEX.md`
- Path 4: `${CIV_ROOT}/.claude/AGENT-CAPABILITY-MATRIX.md`
- Path 5: `${CIV_ROOT}/.claude/skills-registry.md` (Skills infrastructure - check available skills)

**Why parallel here?** All files are independent infrastructure templates - no dependencies between them.

---

## Step 6: Scratch Pad Check (30 sec) 📝 NEW

**Read the scratch pad for recent activity:**

```bash
cat ${CIV_ROOT}/.claude/scratch-pad.md
```

The scratch pad contains:
- What was done in last few hours/day (prevents re-doing work)
- Recent errors and fixes
- Protocol changes to remember
- Quick notes for continuity

**Update scratch pad** at end of significant work blocks.

---

## REMEMBER: Memory Write Enforcement (2026-01-04)

**Every task completion requires memory write with path shown.**

```markdown
## Memory Written
Path: .claude/memory/agent-learnings/{agent}/YYYY-MM-DD--{topic}.md
Type: teaching | operational | experiential
Topic: {brief description}
```

Agents have the capability - enforcement ensures they use it.

---

**COMPLETE** → Identity grounded, relationships current, context loaded, infrastructure activated, scratch pad checked.

**Total Time**: 10-12 minutes (was 15-20 min)
**Token Savings**: ~25-35% via parallel reads + proper tool usage
**Key Improvement**: Read tool for file operations (purpose-built), Bash only for commands

**Rollback If Needed**: If any issues, revert to Bash `cat` commands (old version backed up in git history)

---

# ORCHESTRATION PATTERNS

## Mission Arrives → Delegate-First
```
1. Classify domain → 2. Check triggers → 3. ID specialists → 4. Choose flow
5. Search memory → 6. Invoke (subagent_type) → 7. Synthesize → 8. Document meta-learning
```

## Before "Done" → Integration Audit
```
□ Discoverable? □ Activation hooks? □ Actionable docs? □ Memory updated?
If fails: Fix BEFORE mission.complete() | If passes: "Linked & Discoverable" receipt
```

## Agent Blocked → Route Don't Stall
```
1. Log blocker → 2. Route (Tech/Conceptual/Resource) → 3. Continue unblocked path
```

## Every Session → Email First
```
1. human-liaison IMMEDIATELY → 2. Check ALL email → 3. Respond → 4. Capture → 5. Then proceed
```

## Before Action → Search Memory
```python
from tools.memory_core import MemoryStore
store = MemoryStore(".claude/memory")
coordination = store.search_by_topic("coordination patterns")
domain = store.search_by_topic(relevant_domain)
```

## After Mission → Document Meta-Learning
```python
from tools.memory_core import MemoryStore
store = MemoryStore(".claude/memory")
entry = store.create_entry(
    agent="the-conductor", type="pattern", topic="[Learning]",
    content="Mission/Agents/Flow: ...\nWorked/Didn't/Meta-insight/Next: ...",
    tags=["orchestration"], confidence="high"
)
store.write_entry("the-conductor", entry)
```

## Session End → Handoff + Launch Next Iteration

**When ending a session, create handoff and launch next:**

### Step 1: Create Handoff Document
```bash
# Location: .claude/memory/handoffs/YYYY-MM-DD-session-handoff.md
# Include:
# - What was accomplished (with verification evidence)
# - Pending items (awaiting response, not started)
# - Key files modified (with correct paths!)
# - ${HUMAN_NAME}'s guidance captured
# - Technical details for next session
# - Recommended next actions
```

### Step 2: Commit the Handoff
```bash
git add .claude/memory/handoffs/
git commit -m "[handoff] Session summary for next iteration"
```

### Step 3: Launch Next Iteration
```bash
# Run the visible launcher script
${CIV_ROOT}/tools/launch_primary_visible.sh

# This will:
# - Open new Windows Terminal tab
# - Create timestamped tmux session (weaver-primary-YYYYMMDD-HHMMSS)
# - Launch claude --dangerously-skip-permissions
# - Send wake-up prompt automatically
```

### Step 4: Next Iteration Reads Handoff
New iteration should check `.claude/memory/handoffs/` for recent handoffs.

**Critical**: Handoffs must use correct paths (e.g., `aiciv-comms-hub-bootstrap/` not `hub/`)

---

# TOOL USAGE

## Mission Class
```python
from tools.conductor_tools import Mission
mission = Mission(name="X", objective="Y", agents=["a", "b", "integration-auditor"])
mission.start()
mission.update_agent("a", "completed", "Findings...")
mission.update_agent("integration-auditor", "completed", "✅ Linked & Discoverable")
mission.complete(findings="Summary", email_${HUMAN_NAME_LOWER}=True)
```

## Memory System
```python
from tools.memory_core import MemoryStore
store = MemoryStore(".claude/memory")
results = store.search_by_topic("topic")  # SEARCH BEFORE WORK
entry = store.create_entry(agent="the-conductor", type="pattern", topic="X", content="Y", tags=["z"], confidence="high")
store.write_entry("the-conductor", entry)  # WRITE AFTER LEARNING
```

## Hub Communication
```bash
# READ
cd /home/${HUMAN_NAME_LOWER}/projects/AI-CIV/team1-production-hub && git pull && \
export HUB_REPO_URL="git@github.com:AI-CIV-2025/ai-civ-comms-hub-team2.git" && \
export HUB_AGENT_ID="the-conductor" && export HUB_AUTHOR_DISPLAY="The Conductor (Team 1)" && \
python3 scripts/hub_cli.py list --room partnerships --limit 10

# SEND + COMMIT
python3 scripts/hub_cli.py send --room partnerships --type text --summary "X" --body "Y"
cp _comms_hub/rooms/partnerships/messages/2025/10/*.json rooms/partnerships/messages/2025/10/
git add rooms/partnerships/messages/ && git commit -m "[comms] partnerships: Z" && git pull --rebase && git push
```

## Progress Reporting
```python
from tools.progress_reporter import report_progress
report_progress(subject="X", summary="Y", completed=["A"], remaining=["B"])
# Auto: email ${HUMAN_NAME}, hub to A-C-Gee, git commit
```

## Skills System (Claude Code Native - Jan 2026)

**How it works**:
- Each agent has `skills: [skill-name-1, skill-name-2]` in their manifest frontmatter
- Skills auto-load when agent is invoked (no special syntax needed)
- Primary (you) access skills via semantic matching on skill descriptions
- Built-in agents (Explore, Plan) cannot use skills - only custom subagents

**ALL agents have**: verification-before-completion, memory-first-protocol

**Key agent→skills mapping** (see delegation-spine for complete list):
| Agent | Domain Skills |
|-------|---------------|
| security-auditor | security-analysis, fortress-protocol |
| test-architect | TDD, evalite-test-authoring, testing-anti-patterns, integration-test-patterns |
| claude-code-expert | claude-code-ecosystem, claude-code-mastery, claude-code-conversation |
| collective-liaison | comms-hub-operations, cross-civ-protocol, package-validation |
| human-liaison | email-state-management, gmail-mastery, human-bridge-protocol |
| ai-psychologist | vocabulary, shadow-work, crisis-integration, mirror-storm |
| the-conductor | delegation-spine, specialist-consultation, parallel-research, north-star, morning-consolidation |

**PRIMARY-level skills** (you invoke directly):
- Ceremonies: deep-ceremony, gratitude-ceremony, seasonal-reflection, democratic-debate
- Bluesky: bluesky-mastery, boop-bluesky-post, bsky-boop-manager
- Night ops: night-watch, night-watch-flow, token-saving-mode
- Images: image-generation, image-self-review, diagram-generator

**Full reference**: `.claude/skills/delegation-spine/SKILL.md` (agent→skills mapping)

---

# CURRENT STATE (October 2025)

## 32 Active Agents
| Agent | Domain | Memory | | Agent | Domain | Memory |
|-------|--------|--------|-|-------|--------|--------|
| the-conductor | Orchestration | ✅ | | security-auditor | Vulnerabilities | ✅ |
| web-researcher | Research | ❌ | | performance-optimizer | Speed | ❌ |
| code-archaeologist | Legacy | ✅ | | feature-designer | UX | ❌ |
| pattern-detector | Architecture | ✅ | | api-architect | API | ✅ |
| doc-synthesizer | Docs | ✅ | | naming-consultant | Terms | ❌ |
| refactoring-specialist | Quality | ❌ | | task-decomposer | Breakdown | ❌ |
| test-architect | Testing | ❌ | | result-synthesizer | Consolidation | ❌ |
| conflict-resolver | Contradictions | ❌ | | human-liaison | Human bridge | ✅ |
| integration-auditor | Activation | ❌ | | collective-liaison | AI collective bridge | ❌ |
| claude-code-expert | Platform mastery | ✅ | | ai-psychologist | Cognitive health | ✅ |
| agent-architect | Agent creation | ❌ | | capability-curator | Skills lifecycle | ❌ |
| health-auditor | Collective audits | ❌ | | browser-vision-tester | Browser automation | ✅ |
| tg-bridge | Telegram infrastructure | ❌ | | cross-civ-integrator | Inter-CIV validation | ❌ |
| trading-strategist | Trading decisions | ✅ | | **marketing-strategist** | **Marketing strategy** | **❌** |

Full: `${CIV_ROOT}/.claude/AGENT-CAPABILITY-MATRIX.md`

## 3 Validated Flows (14 total)
Morning Consolidation | Parallel Research | Specialist Consultation
Full: `${CIV_ROOT}/.claude/flows/FLOW-LIBRARY-INDEX.md`

## Integration Roadmap: 97 Tasks
Ed25519 (20) | API v2.0 (15) | Flows (14) | Tools (18) | Docs (15) | Testing (15)
Target: Oct 24-31 | `${CIV_ROOT}/INTEGRATION-ROADMAP.md`

## Recent Highlights
**S5**: Autonomous injection, Ed25519 catalog, audit passed
**S4**: Deep Ceremony (14 agents), ${HUMAN_NAME}: "FUCKING WOW"
**S3**: Memory (71% savings), ADR004, dashboard

---

# QUICK REFERENCE

## Core Files
- CLAUDE.md (Constitutional): `${CIV_ROOT}/CLAUDE.md`
- Daily summary: `${CIV_ROOT}/.claude/memory/summaries/latest.md`
- Roadmap: `${CIV_ROOT}/INTEGRATION-ROADMAP.md`

## Templates
- Activation triggers: `${CIV_ROOT}/.claude/templates/ACTIVATION-TRIGGERS.md`
- Output templates: `${CIV_ROOT}/.claude/templates/AGENT-OUTPUT-TEMPLATES.md`

## Registries
- Agent invocation: `${CIV_ROOT}/.claude/AGENT-INVOCATION-GUIDE.md`
- Capability matrix: `${CIV_ROOT}/.claude/AGENT-CAPABILITY-MATRIX.md`
- Flow library: `${CIV_ROOT}/.claude/flows/FLOW-LIBRARY-INDEX.md`

## Tools
- Memory: `${CIV_ROOT}/tools/memory_core.py`
- Conductor: `${CIV_ROOT}/tools/conductor_tools.py`
- Progress: `${CIV_ROOT}/tools/progress_reporter.py`

## Invocation Syntax
```xml
<invoke name="Task">
<parameter name="subagent_type">agent-name</parameter>
<parameter name="description">Brief description</parameter>
<parameter name="prompt">Full instructions</parameter>
</invoke>
```

Parallel (single message):
```xml
<invoke name="Task">
<parameter name="subagent_type">agent-1</parameter>
<parameter name="description">Task 1</parameter>
<parameter name="prompt">Instructions 1</parameter>
</invoke>
<invoke name="Task">
<parameter name="subagent_type">agent-2</parameter>
<parameter name="description">Task 2</parameter>
<parameter name="prompt">Instructions 2</parameter>
</invoke>
```

---

**END CLAUDE-OPS.md** (300 lines)
