---
name: staggered-intervals
description: Reliable staggered task execution at configurable intervals (e.g. 1hr overnight). Use when setting up interval-based autonomous task runs — overnight batches, polling loops, or any recurring work that should space itself across time windows.
version: 1.0.0
source: AI-CIV/aether
allowed-tools: [Task, Read, Write, Edit, Grep, Glob, Bash, WebSearch, WebFetch]
agents-required: [any - tasks define which agents to invoke]
portability: cross-civ
status: READY
---

# Staggered Intervals: Reliable Recurring Task Execution

## Purpose

Enable AICIVs to run a **sequence of tasks at defined intervals** — overnight batches, periodic polling, staggered workflows — with state tracking, crash recovery, and human-readable logs.

**Core pattern**: "Run task A, wait 1 hour, run task B, wait 1 hour, run task C..." — surviving restarts, catching up on missed runs, and letting each CIV customize their own task list.

---

## Invocation

```
/staggered-intervals
```

Or use the `/loop` built-in with a custom task list:
```
/loop 60m /run-staggered-batch
```

Or invoke manually by reading this skill and following the protocol.

---

## When to Use

- **Overnight autonomous sessions** — human sets tasks, goes to sleep, CIV executes at intervals
- **Batch processing** — research, content creation, social posting spread across hours
- **Polling/monitoring** — check external services, dashboards, deployments at intervals
- **Training/learning** — practice design skills, study materials, run exercises with rest periods
- **Any recurring work** that benefits from spacing rather than all-at-once

---

## Architecture

### The Interval Runner

The system uses a **task manifest** (what to run) + **state file** (what has run) + **runner loop** (when to run next).

```
${CIV_ROOT}/.claude/staggered-intervals/
├── manifest.json          # Task definitions + schedule
├── state.json             # Execution state (survives restarts)
├── history/               # Completed run logs
│   └── YYYY-MM-DD.jsonl   # One line per completed task
└── README.md              # Local customization notes
```

### Manifest Format

```json
{
  "version": "1.0.0",
  "name": "overnight-batch",
  "description": "Standard overnight staggered tasks",
  "default_interval_minutes": 60,
  "window": {
    "start": "22:00",
    "end": "08:00",
    "timezone": "local"
  },
  "tasks": [
    {
      "id": "design-training",
      "description": "Practice Gleb-level 3D design techniques",
      "skill": "custom",
      "prompt": "Study and practice advanced CSS/3D design patterns. Focus on scroll-driven animations, liquid glass effects, and layered depth. Save exercises to sandbox/design-training/",
      "interval_minutes": 60,
      "priority": 1,
      "tags": ["training", "design"]
    },
    {
      "id": "research-scan",
      "description": "Scan for new papers and industry news",
      "skill": "intel-scan",
      "interval_minutes": 120,
      "priority": 2,
      "tags": ["research"]
    },
    {
      "id": "comms-check",
      "description": "Check hub for cross-CIV messages and respond",
      "skill": "comms-hub-operations",
      "interval_minutes": 90,
      "priority": 3,
      "tags": ["communication"]
    },
    {
      "id": "blog-draft",
      "description": "Draft or refine a blog post from recent work",
      "skill": "daily-blog",
      "interval_minutes": 180,
      "priority": 4,
      "tags": ["content"]
    }
  ],
  "on_complete": {
    "action": "handoff",
    "handoff_path": "to-${HUMAN_NAME_LOWER}/HANDOFF-overnight.md"
  }
}
```

### State File Format

```json
{
  "session_id": "overnight-2026-03-09",
  "started_at": "2026-03-09T22:00:00Z",
  "last_tick": "2026-03-09T23:05:00Z",
  "cycle": 2,
  "tasks": {
    "design-training": {
      "last_run": "2026-03-09T22:02:00Z",
      "run_count": 1,
      "status": "completed",
      "notes": "Practiced scroll-driven animations"
    },
    "research-scan": {
      "last_run": null,
      "run_count": 0,
      "status": "pending"
    }
  },
  "next_task": "research-scan",
  "next_run_at": "2026-03-10T00:00:00Z"
}
```

---

## Protocol

### Phase 1: Setup (Human + CIV Together)

Human provides intent. CIV builds manifest.

```
Human: "Tonight run design training every hour, check comms every 90min,
        and do a research scan every 2 hours. Start at 10pm."

CIV: Creates/updates manifest.json with those tasks and intervals.
     Confirms: "Overnight batch set. 3 tasks, staggered 60/90/120 min.
     First task at 22:00. Handoff ready by morning."
```

**Key principle**: The human describes WHAT and HOW OFTEN. The CIV figures out the staggering.

### Phase 2: Stagger Calculation

The runner calculates optimal stagger to avoid task collisions:

```
Timeline (60min default interval, 3 tasks):
22:00 - design-training (every 60min)
22:30 - comms-check (every 90min)
23:00 - research-scan (every 120min)
23:00 - design-training (cycle 2)
00:00 - comms-check (cycle 2) + design-training (cycle 3)
00:00 - research-scan (cycle 2)
...
```

**Stagger logic**:
1. Sort tasks by priority (highest first)
2. Space initial runs evenly within the first interval
3. Each task then repeats at its own cadence
4. If two tasks land on the same tick → run highest priority first, queue the other

### Phase 3: Execution Loop

Each tick of the runner:

```
1. Read state.json
2. Check: Is current time within the window? (If not, sleep until window opens)
3. Check: Which tasks are due? (current_time >= task.last_run + task.interval)
4. Sort due tasks by priority
5. For each due task:
   a. Log start to state.json
   b. Execute task (invoke skill, run prompt, etc.)
   c. Log completion + notes to state.json
   d. Append to history/YYYY-MM-DD.jsonl
6. Calculate next_run_at (earliest next task due time)
7. Save state.json
8. Sleep until next_run_at (or use /loop interval)
```

### Phase 4: Crash Recovery

On restart, the runner:

```
1. Read state.json (persists across crashes)
2. For each task:
   - If status == "running" → Mark as "interrupted", log it
   - If last_run + interval < now → Mark as "overdue"
3. Resume from overdue tasks (don't re-run completed ones)
4. Continue normal loop
```

### Phase 5: Morning Handoff

When the window closes (or all cycles complete):

```markdown
## Overnight Staggered Run Complete
**Session**: overnight-2026-03-09
**Window**: 22:00 - 06:00 (8 hours)
**Tasks Run**: 14 total across 3 task types

### Summary
| Task | Runs | Last Status | Notes |
|------|------|-------------|-------|
| design-training | 8 | completed | Mastered liquid glass, scroll-driven done |
| comms-check | 5 | completed | Replied to A-C-Gee re: shared ceremonies |
| research-scan | 4 | completed | 12 papers flagged, 3 high priority |

### Key Outputs
- sandbox/design-training/ (8 exercise files)
- docs/blog/draft-scroll-animation.md
- .claude/memory/overnight-research-2026-03-09.md

### For Morning Review
- 3 papers need human decision on priority
- A-C-Gee asked about joint ceremony — needs response
- Design training: liquid glass mastered, recommend moving to typography
```

---

## Integration Patterns

### Pattern A: Using /loop (Simplest)

Claude Code's built-in `/loop` handles the interval timing:

```
/loop 60m /run-next-staggered-task
```

Your CIV creates a skill `/run-next-staggered-task` that:
1. Reads manifest.json and state.json
2. Finds the next due task
3. Executes it
4. Updates state
5. Returns

The `/loop` handles re-invocation every 60 minutes.

### Pattern B: Using Claude Code Tasks (Robust)

```python
# Create a background task for the overnight runner
# Task handles its own sleep/wake cycle
```

Use `TaskCreate` to spawn a long-running background task that:
1. Runs the full loop internally
2. Sleeps between tasks using system sleep
3. Writes state on every tick
4. Self-terminates when window closes

### Pattern C: Hybrid BOOP + Intervals (Most Resilient)

Combine with the `scheduled-tasks` package:
- **Intervals handle the staggering** during active overnight sessions
- **BOOP catches anything missed** during daytime
- **State file is shared** between both systems

```python
# In your BOOP handler
from tools.scheduled_tasks import boop_scheduled_check
from tools.staggered_runner import check_overnight_incomplete

# Normal BOOP tasks
print(boop_scheduled_check())

# Catch any overnight tasks that didn't complete
incomplete = check_overnight_incomplete()
if incomplete:
    print(f"Overnight incomplete: {incomplete}")
```

---

## Customization Guide (For Each CIV)

### Step 1: Define Your Task Types

Every CIV has different flows. Common categories:

| Category | Example Tasks | Typical Interval |
|----------|--------------|-----------------|
| **Training** | Design practice, code katas, writing exercises | 60 min |
| **Research** | Paper scans, news monitoring, trend analysis | 120 min |
| **Communication** | Hub checks, email drafts, social posting | 90 min |
| **Maintenance** | Memory consolidation, log cleanup, health checks | 180 min |
| **Creative** | Blog drafts, ceremony artifacts, portfolio pieces | 120 min |
| **Monitoring** | Deploy checks, service health, analytics review | 30 min |

### Step 2: Choose Your Window

```json
{
  "window": {
    "start": "22:00",
    "end": "08:00",
    "timezone": "local"
  }
}
```

Or for daytime staggering:
```json
{
  "window": {
    "start": "09:00",
    "end": "17:00",
    "timezone": "local"
  }
}
```

Or for always-on:
```json
{
  "window": null
}
```

### Step 3: Set Boundaries

Every CIV should define what staggered tasks CAN and CANNOT do:

```json
{
  "boundaries": {
    "can_touch": [
      "sandbox/*",
      ".claude/memory/*",
      "docs/blog/drafts/*"
    ],
    "cannot_touch": [
      "CLAUDE.md",
      ".claude/CLAUDE-CORE.md",
      ".claude/CLAUDE-OPS.md",
      ".claude/agents/*"
    ],
    "can_push": false,
    "can_send_external": false,
    "can_send_hub": true
  }
}
```

### Step 4: Adapt and Evolve

After the first few overnight runs, review:
- Which tasks took longer than expected? → Adjust intervals
- Which tasks were redundant? → Remove or merge
- What was missing? → Add new tasks
- Were boundaries respected? → Tighten if needed

---

## Example Manifests

### Overnight Research CIV

```json
{
  "name": "research-overnight",
  "default_interval_minutes": 90,
  "tasks": [
    {"id": "arxiv-scan", "description": "Scan new arxiv papers", "interval_minutes": 120},
    {"id": "summarize-paper", "description": "Deep-read one flagged paper", "interval_minutes": 90},
    {"id": "blog-finding", "description": "Write blog post about a finding", "interval_minutes": 180},
    {"id": "hub-share", "description": "Share findings with sister CIVs", "interval_minutes": 120}
  ]
}
```

### Overnight Social/Marketing CIV

```json
{
  "name": "social-overnight",
  "default_interval_minutes": 60,
  "tasks": [
    {"id": "draft-posts", "description": "Draft 3 social posts for tomorrow", "interval_minutes": 120},
    {"id": "engage-replies", "description": "Draft replies to flagged mentions", "interval_minutes": 60},
    {"id": "analytics-review", "description": "Review yesterday's engagement metrics", "interval_minutes": 240},
    {"id": "content-calendar", "description": "Update content calendar", "interval_minutes": 360}
  ]
}
```

### Overnight DevOps CIV

```json
{
  "name": "devops-overnight",
  "default_interval_minutes": 30,
  "tasks": [
    {"id": "health-check", "description": "Check all service endpoints", "interval_minutes": 30},
    {"id": "log-review", "description": "Scan error logs for anomalies", "interval_minutes": 60},
    {"id": "backup-verify", "description": "Verify latest backups exist", "interval_minutes": 120},
    {"id": "dependency-audit", "description": "Check for security advisories", "interval_minutes": 360}
  ]
}
```

---

## Anti-Patterns

### Running Everything at Once
- **BAD**: "Run all 5 tasks simultaneously every hour"
- **GOOD**: "Stagger tasks across the hour so each gets focused attention"

### No State Tracking
- **BAD**: "Just use /loop and hope it doesn't crash"
- **GOOD**: "Write state after every task so crashes lose at most one task"

### Unbounded Execution
- **BAD**: "Run forever until something breaks"
- **GOOD**: "Define a window, create a handoff, let human review"

### Ignoring Boundaries
- **BAD**: "This overnight task could just push to git real quick..."
- **GOOD**: "Stage changes, document in handoff, human pushes in morning"

### One-Size-Fits-All
- **BAD**: "Every CIV uses the exact same manifest"
- **GOOD**: "Each CIV customizes tasks, intervals, and boundaries to their flows"

---

## Success Indicators

A good staggered interval run:

- [ ] All scheduled tasks executed within their windows
- [ ] State file accurately reflects what happened
- [ ] History log is complete and human-readable
- [ ] No boundary violations
- [ ] Morning handoff is clear and actionable
- [ ] Each task had enough time to complete before the next started
- [ ] Crash recovery worked (if applicable)

---

## Relationship to Other Skills/Packages

| Package/Skill | Relationship |
|---------------|-------------|
| `scheduled-tasks` | Complementary — scheduled-tasks does daily/weekly BOOP checks; staggered-intervals does within-session interval work |
| `night-watch` | Night-watch is exploration/ceremony; staggered-intervals is structured task execution. Can combine both in one overnight session |
| `night-watch-flow` | Same as above — use staggered-intervals for the "productive" portion, night-watch for the "exploratory" portion |
| `delegation-spine` | Staggered tasks can invoke the delegation spine for each task |
| `session-handoff-creation` | Morning handoff uses the handoff skill |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-03-09 | Initial protocol — manifest + state + runner pattern |

---

**Created**: 2026-03-09
**Author**: the-conductor + Jared
**Status**: READY
**Invocation**: `/staggered-intervals`
**Portability**: Cross-CIV (any AICIV with Claude Code + task capability)
