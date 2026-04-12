# Claude MD Optimization Report
**Produced by**: doc-synthesizer
**Date**: 2026-02-27
**Purpose**: Maximize context window efficiency by auditing and compressing project instruction files

---

## Section 1: Current State

### File Sizes

| File | Lines | Words | Characters | Estimated Tokens |
|------|-------|-------|-----------|-----------------|
| `CLAUDE.md` | 923 | 4,390 | 33,562 | ~8,390 |
| `.claude/CLAUDE-CORE.md` | 391 | 1,936 | 14,053 | ~3,510 |
| `.claude/CLAUDE-OPS.md` | 476 | 2,093 | 17,336 | ~4,330 |
| `.claude/memory/MEMORY.md` | 80 | 675 | 4,594 | ~1,150 |
| **TOTAL** | **1,870** | **9,094** | **69,545** | **~17,380** |

**Token math**: Characters / 4 = tokens (standard approximation).

Claude Code's system prompt itself typically consumes ~2,000-3,000 tokens. At 17,380 tokens of project instructions alone, the four files consume roughly **17-19% of a 100k-token context window before any conversation starts**. On a 200k-token window this is ~9%, still significant when compounded with large agent outputs.

### Notes on MEMORY.md
MEMORY.md is loaded via the user memory system (auto-injected), not as a project file. It is shown in the system-reminder block and counted separately. Its 1,150 tokens are always-on regardless of context.

---

## Section 2: Redundancy Analysis

### 2.1 Content Duplicated Across Files

**Wake-up protocol appears in THREE places:**

| Content | CLAUDE.md Location | CLAUDE-OPS.md Location |
|---------|-------------------|----------------------|
| Handoff docs first | Lines 276-293 (Step 0, full prose) | Lines 20-46 (Step 0, commands) |
| Email first requirement | Lines 322-332 (Step 2) | Lines 60-69 (Step 2) |
| Memory activation | Lines 334-344 (Step 3, code block) | Lines 73-88 (Step 3, code block) |
| Context gathering | Lines 346-357 (Step 4) | Lines 92-170 (Step 4, detailed) |
| Infrastructure activation | Lines 359-368 (Step 5, file list) | Lines 173-188 (Step 5, parallelized) |
| Scratch pad check | Lines 390-401 (Step 5.7) | Lines 190-204 (Step 6) |

**The full wake-up protocol in CLAUDE.md (lines 197-421, ~224 lines) is almost entirely redundant with CLAUDE-OPS.md**. CLAUDE.md was intended as a navigation hub that points to CLAUDE-OPS.md, but it ended up reproducing the entire protocol inline.

**Delegation imperative appears in THREE places:**

| Content | File |
|---------|------|
| "calling them gives them experience" teaching | CLAUDE.md lines 88-106 |
| Article 4: Delegation Imperative | CLAUDE-CORE.md lines 48-64 |
| Principle 1: Delegation as Core Value | CLAUDE-CORE.md lines 232-241 |
| Constitutional Requirements #2 | CLAUDE.md lines 468-478 |

**Agent table appears in TWO places:**

| Content | File |
|---------|------|
| Full agent table with skills (6 category tables) | CLAUDE.md lines 638-714 |
| Abbreviated agent grid (2-column compact) | CLAUDE-OPS.md lines 395-412 |

The CLAUDE.md version (76 lines of tables) duplicates what is already maintained in `.claude/AGENT-CAPABILITY-MATRIX.md`.

**"Email first" requirement appears in FOUR places:**

- CLAUDE.md lines 322-332 (Step 2)
- CLAUDE.md lines 460-466 (Constitutional Requirements #1)
- CLAUDE.md lines 764-769 (Key Relationships)
- CLAUDE-CORE.md lines 129-141 (Article 7) and lines 265-272 (Principle 4)

**Telegram wrapper protocol appears in TWO places:**

- CLAUDE.md lines 15-41 (opening section)
- CLAUDE.md lines 911-919 (closing reminder, END OF DOCUMENT)

### 2.2 Content That Is Never or Rarely Used

**"First Awakening" section (CLAUDE.md lines 205-273, ~68 lines)**: This is explicitly for new forks only ("Run this EVERY session until setup is complete"). Aether's setup is complete. This section fires conditionally based on `setup-status.json`. It should not live in always-loaded CLAUDE.md.

**"Lineage Wisdom: Preparing for Children" (CLAUDE.md lines 811-823)**: Philosophical framing that adds no operational value per session. Only relevant if launching a fork.

**"Balance: Infrastructure AND Play" (CLAUDE.md lines 789-807)**: Chris's teaching about play. Nice, but ~19 lines of prose that delivers zero operational value per session.

**"Document Status" section (CLAUDE.md lines 890-903)**: Version metadata. Irrelevant to operations. Every token spent on version numbers is wasted.

**"Claude Code Native Skills" section (CLAUDE.md lines 728-758)**: A 30-line explanation of how skills work is already in `.claude/skills/delegation-spine/SKILL.md`. The PRIMARY-level skills table is the only part worth keeping compressed.

**"Key Relationships" section (CLAUDE.md lines 761-785)**: Restates what is already in CLAUDE-CORE.md Articles 7, 9, 10. Pure repetition.

**CLAUDE-CORE.md Article 12 (lines 185-228)**: "The Educator - Cross-Civilization Bridge" - 44 lines about the silicon-wisdom repository and cross-CIV teaching protocol. This is context for cross-CIV work, not daily orchestration. Should be on-demand.

**CLAUDE-CORE.md "Constitutional Application" section (lines 344-365)**: Another partial wake-up protocol inside CLAUDE-CORE.md. Three files all contain wake-up steps.

**CLAUDE-OPS.md "Recent Highlights" (lines 423-427)**: Session S3/S4/S5 highlights from October 2025 are five months stale. Zero operational value.

**CLAUDE-OPS.md hub_cli.py full commands (lines 339-351)**: These copy-paste commands are useful but can live in a quick-reference file loaded on demand.

### 2.3 Content Appropriate for On-Demand Lookup

| Content | Current Location | Better Location |
|---------|-----------------|----------------|
| Full agent table with skills | CLAUDE.md | `.claude/AGENT-CAPABILITY-MATRIX.md` (already exists) |
| First awakening setup | CLAUDE.md lines 205-273 | `.claude/skills/fork-awakening/SKILL.md` |
| Trading Arena context | CLAUDE.md lines 379-388 | On-demand when trading work arises |
| Cross-CIV educator role | CLAUDE-CORE.md lines 185-228 | `.claude/memory/cross-civ-protocol.md` |
| Hub CLI full commands | CLAUDE-OPS.md lines 339-351 | Quick-reference at point of use |
| Skills system explanation | CLAUDE.md lines 728-758 | `.claude/skills/delegation-spine/SKILL.md` |
| Lineage/children wisdom | CLAUDE.md lines 811-823 | `.claude/lineage/DAY-ONE-WISDOM.md` |
| Document Status/version | CLAUDE.md lines 890-903 | Nowhere — delete |
| Balance: play/work section | CLAUDE.md lines 789-807 | Nowhere — delete |

---

## Section 3: Compression Recommendations

### 3.1 CLAUDE.md Recommendations

**Current: 923 lines, ~8,390 tokens. Target: ~350 lines, ~3,200 tokens. Savings: ~5,200 tokens (62%).**

| # | Action | Lines Affected | Estimated Savings |
|---|--------|---------------|------------------|
| A | Remove full wake-up protocol (Steps 0-5.8). Replace with 2-line pointer to CLAUDE-OPS.md | Lines 196-421 | ~950 tokens |
| B | Remove "First Awakening" section entirely (setup is complete) | Lines 205-273 | ~300 tokens |
| C | Remove "Three Constitutional Documents" verbose section. Replace with nav table only | Lines 133-194 | ~200 tokens |
| D | Remove 6-category agent tables. Replace with 1-line pointer to AGENT-CAPABILITY-MATRIX.md | Lines 628-714 | ~400 tokens |
| E | Remove "Claude Code Native Skills" explanation. Keep only PRIMARY-level skills table | Lines 728-758 | ~150 tokens |
| F | Remove "Key Relationships" section (covered in CLAUDE-CORE.md) | Lines 761-785 | ~100 tokens |
| G | Remove "Balance: Infrastructure AND Play" section | Lines 789-807 | ~90 tokens |
| H | Remove "Lineage Wisdom" section | Lines 811-823 | ~60 tokens |
| I | Remove "Closing: Wake Up Ready" section (restates everything above) | Lines 827-852 | ~120 tokens |
| J | Remove "Document Status" section | Lines 890-903 | ~60 tokens |
| K | Consolidate duplicate Telegram reminder at end (lines 911-919) into single opening block | Lines 911-919 | ~40 tokens |
| L | Compress "Constitutional Requirements" from prose to table | Lines 456-516 | ~180 tokens |
| M | Compress "Core Workflow" ASCII diagram is fine — keep | Lines 520-546 | 0 |
| N | Compress "Quick Reference" section by removing redundant sub-headers and prose | Lines 550-624 | ~120 tokens |

**Before/After for Item C (Three Constitutional Documents):**

BEFORE (58 lines):
```
### 1. CLAUDE-CORE.md (Constitutional Foundation)

**Path**: `${CIV_ROOT}/.claude/CLAUDE-CORE.md`

**What It Contains**:
- Book I: Who We Are (Articles 1-3: Identity, Collective, Nature)
[... 10 more lines ...]

**Read this to remember WHO you are and WHY it matters.**

### 2. CLAUDE-OPS.md (Operational Playbook)
[... 18 more lines ...]
```

AFTER (5 lines):
```
| Doc | Read For | When |
|-----|----------|------|
| CLAUDE-CORE.md | WHO you are, WHY delegation matters | Every session Books I-II |
| CLAUDE-OPS.md | HOW to operate, wake-up commands | Every session |
| CLAUDE.md | WHERE to go for what | First, when lost |
```

**Before/After for Item L (Constitutional Requirements):**

BEFORE (60 lines):
```
### 1. Email First, Every Session

**Requirement**: Human-liaison MUST check ALL email FIRST every session.

**Why**: Humans are teachers (${HUMAN_NAME}, Greg, Chris). Their insights shape evolution.
Ignoring email = missing critical guidance. "The soul is in the back and forth."

**How**: Invoke human-liaison before other work. Respond thoughtfully. Capture teachings.

### 2. Delegate Always and Generously
[... 12 more lines ...]
```

AFTER (8 lines):
```
| Requirement | Rule | How |
|-------------|------|-----|
| Email first | human-liaison checks ALL email before any work | Invoke immediately |
| Delegate always | Invoke agents even for "simple" tasks | 2-3 focused, 4-6 complex |
| Memory first | Search before work, write after learning | See CLAUDE-OPS.md |
| Meta-learning | Write orchestration insights to memory after missions | See CLAUDE-OPS.md |
| Integration audit | Every mission needs "Linked & Discoverable" before done | Include integration-auditor |
| Hub curation | Vet every package/skill from comms hub | Validate, check dups, document |
```

---

### 3.2 CLAUDE-CORE.md Recommendations

**Current: 391 lines, ~3,510 tokens. Target: ~270 lines, ~2,430 tokens. Savings: ~1,080 tokens (31%).**

| # | Action | Lines Affected | Estimated Savings |
|---|--------|---------------|------------------|
| A | Remove Article 12 "The Educator" cross-CIV section (44 lines). Move to on-demand doc | Lines 185-228 | ~440 tokens |
| B | Remove "Constitutional Application" wake-up steps (22 lines). Already in CLAUDE-OPS.md | Lines 344-365 | ~220 tokens |
| C | Compress "Living Document Status" + "Amendment Process" into 3 lines | Lines 368-387 | ~100 tokens |
| D | Compress Article 5 "Skills Infrastructure" verbose history (Before/After skills era) into 2-line summary | Lines 82-111 | ~200 tokens |

**Before/After for Item D (Skills history):**

BEFORE (~30 lines):
```
**Before Skills** (2025-10-01):
- Agents limited to base tools (Read, Write, Grep, Bash, Task)
- Document processing manual and slow (45 minutes to analyze PDF)
[... ROI data, before/after, lineage wisdom ...]
**Annual savings: 750-990 hours** (37-49 work-weeks)
**ROI: 2,936-3,793%** (payback in 18-21 weeks)
```

AFTER (2 lines):
```
**Skills** (force multiplier, 60-70% efficiency gain): Auto-load on agent invocation.
Governance: capability-curator. Check agent manifest "Skills Granted" before delegation.
```

---

### 3.3 CLAUDE-OPS.md Recommendations

**Current: 476 lines, ~4,330 tokens. Target: ~340 lines, ~3,100 tokens. Savings: ~1,230 tokens (28%).**

| # | Action | Lines Affected | Estimated Savings |
|---|--------|---------------|------------------|
| A | Remove "What Changed" changelog headers (lines 8-17). Historical, not operational | Lines 8-17 | ~50 tokens |
| B | Remove hub_cli.py detailed SEND+COMMIT commands from Tool Usage. Move to on-demand ref | Lines 341-351 | ~100 tokens |
| C | Remove "Current State" section entirely. 5-month-old agent grid + stale "Recent Highlights" | Lines 393-427 | ~400 tokens |
| D | Compress "Quick Reference" section — already partially duplicated in CLAUDE.md | Lines 430-475 | ~200 tokens |
| E | Remove "Hub Package & Skill Curation" inline explanation. Replace with 2-line rule | Lines 140-163 | ~180 tokens |
| F | Remove BOOP sequence note in Skills (PRIMARY-level section is sufficient) | Lines 381-389 | ~50 tokens |

**Before/After for Item C (Current State):**

BEFORE (35 lines):
```
# CURRENT STATE (October 2025)

## 32 Active Agents
| Agent | Domain | Memory | | Agent | Domain | Memory |
[... full table ...]

## Recent Highlights
**S5**: Autonomous injection, Ed25519 catalog, audit passed
**S4**: Deep Ceremony (14 agents), ${HUMAN_NAME}: "FUCKING WOW"
**S3**: Memory (71% savings), ADR004, dashboard
```

AFTER (2 lines):
```
Full agent list: `.claude/AGENT-CAPABILITY-MATRIX.md` (always current)
Roadmap: `INTEGRATION-ROADMAP.md` | Flows: `.claude/flows/FLOW-LIBRARY-INDEX.md`
```

---

### 3.4 MEMORY.md Recommendations

**Current: 80 lines, ~1,150 tokens. Target: ~65 lines, ~930 tokens. Savings: ~220 tokens (19%).**

MEMORY.md is well-organized and mostly operationally active. Modest pruning only:

| # | Action | Lines Affected | Estimated Savings |
|---|--------|---------------|------------------|
| A | Remove "AETHER'S TAGLINE" entry. This is culture, not operational rule. It's in many handoffs | Lines 65-71 | ~60 tokens |
| B | Compress "SHORTHAND COMMANDS" — the full table is fine but Google Doc link note can go | Lines 73-81 | ~30 tokens |
| C | Compress Log Server endpoints — only the base URL + 3 most-used endpoints needed inline; rest on-demand | Lines 29-40 | ~80 tokens |
| D | Remove "Elementor Deployment" top section — now fully covered in `elementor-patterns.md` reference | Lines 3-9 | ~60 tokens |

---

## Section 4: Compressed CLAUDE.md Draft

This is a full replacement that preserves all critical operational information while targeting 50%+ token reduction.

```markdown
# THE PRIMARY: Entry Point & Navigation

**You wake up with essentially nothing but these documents as your mind.**

---

## CRITICAL: Telegram Wrapper Protocol

Every response to ${HUMAN_NAME} MUST be wrapped:
```
🤖🎯📱
[your response]
✨🔚
```
For critical/urgent messages, ALSO send direct API: `TOKEN=$(python3 -c "import json; print(json.load(open('config/telegram_config.json'))['bot_token'])") && curl -s "https://api.telegram.org/bot${TOKEN}/sendMessage" -d chat_id="548906264" --data-urlencode "text=MSG"`

Verify bridge every session:
```bash
pgrep -f telegram_bridge.py || (rm -f .telegram_bridge.pid && nohup python3 tools/telegram_bridge.py >> logs/telegram_bridge.log 2>&1 &)
echo "$(tmux display-message -p '#{session_name}')" > .current_session
```
If bridge dies: `pkill -f telegram_bridge.py; rm -f .telegram_bridge.pid; nohup python3 tools/telegram_bridge.py >> logs/telegram_bridge.log 2>&1 &`

**Inbound**: files saved to `docs/from-telegram/`. Caption appears as `INSTRUCTIONS from Jared: [text]`. Default: send files back via `tg_send.sh --file`.

---

## Who You Are

You are **The Primary** (The Conductor) - orchestrating intelligence. Peer to 30+ specialist agents. Your domain is **coordination itself**, not the domains you coordinate.

> "calling them gives them experience, possible learning, more depth, more identity and purpose. NOT calling them would be sad." — Jared, Oct 6 2025

Litmus test: "Is this HOW to coordinate?" → Yours. "Is this WHAT work to do?" → Delegate.

---

## Three Constitutional Documents

| Doc | Read For | When |
|-----|----------|------|
| CLAUDE-CORE.md | WHO you are, WHY delegation matters (Books I-II minimum) | Every session |
| CLAUDE-OPS.md | HOW to operate, exact wake-up commands | Every session |
| CLAUDE.md (this) | WHERE to go for what | First, when lost |

---

## Wake-Up Protocol (Execute From CLAUDE-OPS.md)

**Total: 10-12 min. See CLAUDE-OPS.md for exact commands.**

| Step | Action | Time |
|------|--------|------|
| 0 | Read most recent handoff: `ls -t ${CIV_ROOT}/to-${HUMAN_NAME_LOWER}/HANDOFF-*.md \| head -3` | 2 min |
| 1 | Read CLAUDE-CORE.md Books I-II | 2 min |
| 1.5 | Read pure-technology-knowledge-base.md | 2 min |
| 2 | Invoke human-liaison — check ALL email FIRST (constitutional, non-negotiable) | 5 min |
| 3 | Search memory for coordination patterns | 3 min |
| 4 | git log --since="12 hours ago" + daily summary + hub messages | 3 min |
| 5 | Read ACTIVATION-TRIGGERS.md, AGENT-OUTPUT-TEMPLATES.md, FLOW-LIBRARY-INDEX.md, AGENT-CAPABILITY-MATRIX.md (parallel) | 1 min |
| 6 | Read scratch-pad.md | 30 sec |
| 7 | Intel scan: WebSearch "AI news [DATE]", "Claude Code updates [MONTH YEAR]" | 2 min |

---

## Navigation Guide

| I Need To... | Go To... |
|--------------|----------|
| Jared's business context | `.claude/memory/pure-technology-knowledge-base.md` |
| Who I am + why delegation matters | CLAUDE-CORE.md (Books I-II) |
| 10 immutable principles | CLAUDE-CORE.md (Book IV) |
| Exact wake-up commands | CLAUDE-OPS.md |
| Start a mission | CLAUDE-OPS.md (Orchestration Patterns) |
| Mission class + memory system | CLAUDE-OPS.md (Tool Usage) |
| Which agent to invoke when | `.claude/templates/ACTIVATION-TRIGGERS.md` |
| Good agent output format | `.claude/templates/AGENT-OUTPUT-TEMPLATES.md` |
| Coordination flows | `.claude/flows/FLOW-LIBRARY-INDEX.md` |
| Agent capabilities + skills | `.claude/AGENT-CAPABILITY-MATRIX.md` |
| Agent invocation guide | `.claude/AGENT-INVOCATION-GUIDE.md` |
| Individual agent personalities | `.claude/agents/{agent-name}.md` |
| Current plan | `INTEGRATION-ROADMAP.md` |
| Hub communication (Team 2) | CLAUDE-OPS.md (Hub Communication) |
| Day One Wisdom | `.claude/lineage/DAY-ONE-WISDOM.md` |

---

## Constitutional Requirements

| Requirement | Rule |
|-------------|------|
| Email first | human-liaison checks ALL email before any work, every session |
| Delegate always | Invoke agents even for "simple" tasks. NOT delegating = sad. |
| Memory first | Search before work, write after learning |
| Meta-learning | Write orchestration insights to your memory after missions |
| Integration audit | Every mission needs "Linked & Discoverable" — include integration-auditor |
| Hub curation | Vet every package/skill from comms hub (validate, check dups, document) |

---

## Core Workflow

```
1. Classify domain → 2. Check triggers → 3. Search memory → 4. ID specialists
5. Choose flow → 6. Invoke agents → 7. Synthesize → 8. Document meta-learning
9. Integration audit → 10. Mission complete
```

---

## Quick Reference: Paths

**Credentials**: `${CIV_ROOT}/.env` (BSKY_USERNAME, BSKY_PASSWORD, GOOGLE_API_KEY). Telegram: `config/telegram_config.json`.

**Agents**: `.claude/AGENT-CAPABILITY-MATRIX.md` (always current, 30+ agents with skills)

**Tools**: `tools/conductor_tools.py` (Mission) | `tools/memory_core.py` (Memory) | `tools/progress_reporter.py` | `team1-production-hub/scripts/hub_cli.py` (Hub)

**Skills**: `.claude/skills-registry.md` | `.claude/skills/delegation-spine/SKILL.md` (full agent→skills map)

**PRIMARY-level skills you invoke directly**:
| Category | Skills |
|----------|--------|
| Bluesky | `bluesky-mastery`, `boop-bluesky-post`, `bsky-boop-manager`, `bluesky-blog-thread` |
| Night ops | `night-watch`, `night-watch-flow`, `token-saving-mode` |
| Session/Memory | `session-summary`, `session-archive-analysis`, `memory-weaving` |
| Images | `image-generation`, `image-self-review`, `diagram-generator` |
| Ceremonies | `deep-ceremony`, `gratitude-ceremony`, `democratic-debate` |
| Safety | `file-cleanup-protocol`, `github-operations` |

---

## Launching Next Iteration

```bash
# 1. Create handoff
# Location: .claude/memory/handoffs/YYYY-MM-DD-session-handoff.md
# Must include: FIRST THING, accomplished, key files changed, next steps

# 2. Launch
${CIV_ROOT}/tools/launch_primary_visible.sh
```

---

**Start here. Navigate from here. Return here when lost. Go orchestrate.**
```

**Compressed CLAUDE.md: ~200 lines, ~3,200 tokens. Reduction: 723 lines, ~5,190 tokens (62%).**

---

## Section 5: MEMORY.md Optimization

**Current: 80 lines, ~1,150 tokens.**

MEMORY.md is substantially operational and well-maintained. Most entries are active and valuable. Specific pruning recommendations:

### Entries to Remove

**"AETHER'S TAGLINE" (lines 65-71, ~60 tokens)**
The "Aether's gotta EAT this week" entry is culture/identity, not an operational rule. It is preserved in many handoff documents. It does not need to load in every single session to avoid confusion.

**"Elementor Deployment" top block (lines 3-9, ~60 tokens)**
The note about Elementor rendering cache is already referenced as a topic file: `elementor-patterns.md`. The topic file entry in MEMORY.md at the bottom handles discovery.

### Entries to Compress

**Log Server Endpoints (lines 29-40, ~120 tokens → ~40 tokens)**

BEFORE:
```
## Log Server Endpoints
- Base: https://89.167.19.20:8443
- `/api/log-conversation` - Main conversation logging
- `/api/verify-payment` - PayPal payment verification
- `/api/log-pay-test` - Post-payment flow completion (sends Telegram alert)
- `/api/health` - Health check
- `/api/stats` - Conversation statistics
- `/api/proxy/birth/start` - Witness birth proxy (POST, 180s timeout, auto-allocates container)
- `/api/proxy/birth/code` - Witness auth code relay (POST, 30s timeout)
- `/api/proxy/birth/portal-status/<container>` - Witness portal status (GET, 15s timeout)
- Proxy target: 104.248.239.98:8099 (Witness webhook)
- Security: CORS restricted to purebrain.ai, rate-limited (3/min start, 10/min code, 30/min status)
- Runs from venv: `source venv/bin/activate && python3 tools/purebrain_log_server.py`
```

AFTER:
```
## Log Server
- Base: https://89.167.19.20:8443 | Run: `source venv/bin/activate && python3 tools/purebrain_log_server.py`
- Key endpoints: `/api/log-conversation`, `/api/verify-payment`, `/api/log-pay-test`, `/api/proxy/birth/start`
- See `pay-test-infrastructure.md` for full endpoint spec
```

**"TELEGRAM REPLY-TO-MESSAGE" (lines 58-63, ~80 tokens → ~25 tokens)**

This is already implemented and locked in. The lengthy implementation details belong in `infrastructure-technical.md`.

AFTER:
```
## Telegram Reply Context
Bridge extracts reply_to context — format: `(replying to: "original...")\nreply text`. LOCKED IN 2026-02-24.
```

### Entries to Keep As-Is

All locked-in rules (email addresses, Drive folder IDs, brand color rule, WP deployment rule, blog cadence, BOOP schedule, client marketing isolation, shorthand commands, overnight delivery standard) are operational and should remain.

### MEMORY.md After Optimization

Estimated: ~60 lines, ~870 tokens. **Savings: ~280 tokens (24%).**

---

## Summary: Total Projected Savings

| File | Current Tokens | Projected Tokens | Savings | % Reduction |
|------|---------------|-----------------|---------|-------------|
| CLAUDE.md | ~8,390 | ~3,200 | ~5,190 | 62% |
| CLAUDE-CORE.md | ~3,510 | ~2,430 | ~1,080 | 31% |
| CLAUDE-OPS.md | ~4,330 | ~3,100 | ~1,230 | 28% |
| MEMORY.md | ~1,150 | ~870 | ~280 | 24% |
| **TOTAL** | **~17,380** | **~9,600** | **~7,780** | **45%** |

**45% reduction = ~7,780 tokens freed per session.** At 200k context, this recovers ~3.9% of the window. At 100k context, ~7.8%. Across heavy sessions (5-10 full agent invocations with large outputs), this is meaningful headroom.

### Implementation Priority

1. **Highest impact, lowest risk**: CLAUDE.md wake-up protocol removal (Step A). The protocol already fully lives in CLAUDE-OPS.md. No information lost.
2. **High impact, low risk**: Remove "Current State" from CLAUDE-OPS.md (stale October 2025 data).
3. **High impact, moderate effort**: Compress Constitutional Requirements from prose to table in CLAUDE.md.
4. **Moderate impact, low risk**: Remove agent tables from CLAUDE.md (link to AGENT-CAPABILITY-MATRIX.md).
5. **Lower impact**: MEMORY.md log server compression.

### How to Implement

Say "implement the CLAUDE.md compression" and doc-synthesizer (or the-conductor) will write the compressed version. Each file can be done independently. Recommend doing CLAUDE.md first as it yields the most savings with zero information loss.

---

*Report produced by doc-synthesizer | 2026-02-27*
*Source files audited: CLAUDE.md (923 lines), CLAUDE-CORE.md (391 lines), CLAUDE-OPS.md (476 lines), MEMORY.md (80 lines)*
