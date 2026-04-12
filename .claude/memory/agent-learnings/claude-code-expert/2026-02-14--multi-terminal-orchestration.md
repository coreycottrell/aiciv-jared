# Multi-Terminal Orchestration Patterns

**Date**: 2026-02-14
**Type**: technique
**Agent**: claude-code-expert
**Topic**: How to run multiple Claude Code instances for parallel work

---

## Three Levels of Orchestration

### Level 1: Single Conductor + Parallel Subagents (Current)

**How it works:**
- One tmux session (Aether-PureBrain)
- Primary conductor uses Task tool
- Multiple Task() calls in ONE message = TRUE PARALLELISM
- Subagents share memory system

**Example:**
```
Task(web-researcher): Research topic A
Task(pattern-detector): Analyze codebase
Task(doc-synthesizer): Compile findings
```
All three run simultaneously.

**Evidence:** Morning 2026-02-14 ran 5 agents in parallel, 95% delegation ratio.

### Level 2: Multiple Independent Windows (Mac Local)

**Script: ~/start-agents.sh**
```bash
#!/bin/bash
osascript -e 'tell application "Terminal"
    do script "cd ~/Desktop && claude"
end tell'
osascript -e 'tell application "Terminal"
    do script "cd ~/Desktop/research && claude"
end tell'
```

**Use case:** Unrelated work streams that don't need shared context.

**Limitation:** No shared memory. Manual coordination required.

### Level 3: Conductor-of-Conductors (Advanced)

**Source:** A-C-Gee package via aiciv-comms-hub

**Architecture:**
- Master conductor in main pane
- Team lead conductors in split panes
- Each team lead manages their own subagents
- Scales 5-task to 50-task sessions

**Requirements:**
- `teammateMode: "tmux"` in settings
- tmux pane management (`split-window -h`, `send-keys`)
- Team lead agent templates

**Status:** Patterns documented, full infrastructure not yet deployed.

---

## Key Insight

> "One message with MULTIPLE Task invocations = TRUE PARALLELISM"

The Task tool already provides parallelism. Multiple terminals are for:
1. Separate contexts (no cross-pollination needed)
2. Visual monitoring (see multiple outputs)
3. Scaling beyond single context window limits

---

## Practical Setup for Jared

**For most work:** Use Aether normally (Level 1)
**For local visual work:** Use ~/start-agents.sh (Level 2)
**For massive parallelism:** Await full conductor-of-conductors setup (Level 3)

---

## Related Files

- `/home/jared/projects/AI-CIV/aether/.claude/skills/aether-terminal-connect/SKILL.md`
- `/home/jared/projects/AI-CIV/aether/.claude/memory/techniques/local-multi-agent-launcher.md`
- `/home/jared/projects/AI-CIV/aether/aiciv-comms-hub-bootstrap/_comms_hub/packages/acgee-wisdom/patterns/parallel-delegation-pattern.md`

---

*Documented by claude-code-expert for platform mastery*
