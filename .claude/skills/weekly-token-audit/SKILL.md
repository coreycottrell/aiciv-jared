---
name: weekly-token-audit
description: Weekly audit of all project instruction files for token savings. Measures current usage, finds redundancies, produces compressed alternatives. Scheduled skill — runs once per week.
trigger: "token audit", "token optimization", "compress project files"
allowed-tools: Read, Write, Grep, Glob, Bash
schedule: weekly
---

# Weekly Token Audit

## Purpose

Maximize context window efficiency by auditing and compressing all always-loaded project files. Run once per week (or on-demand via trigger words).

## What Gets Audited

| File | Type | Notes |
|------|------|-------|
| `CLAUDE.md` | Project instructions | Always loaded every session |
| `.claude/CLAUDE-CORE.md` | Constitutional identity | Always loaded |
| `.claude/CLAUDE-OPS.md` | Operational playbook | Always loaded |
| `.claude/memory/MEMORY.md` | Auto-memory | Always loaded (system-reminder) |
| `.claude/AGENT-CAPABILITY-MATRIX.md` | Referenced frequently | Loaded on wake-up |
| `.claude/templates/ACTIVATION-TRIGGERS.md` | Referenced frequently | Loaded on wake-up |

## Audit Protocol

### Step 1: Measure Current State
```bash
# Count lines and estimate tokens for each file
for f in CLAUDE.md .claude/CLAUDE-CORE.md .claude/CLAUDE-OPS.md .claude/memory/MEMORY.md; do
  lines=$(wc -l < "$f")
  chars=$(wc -c < "$f")
  tokens=$((chars / 4))
  echo "$f: ${lines} lines, ~${tokens} tokens"
done
```

### Step 2: Detect Redundancies
- Cross-reference content between files (grep for duplicate paragraphs)
- Check for stale content (references to old dates, completed features, resolved issues)
- Look for prose that could be tables, code blocks that could be references

### Step 3: Check for Stale MEMORY.md Entries
- Any entry referencing completed one-time tasks
- Any entry superseded by newer entries
- Any entry already documented in dedicated topic files

### Step 4: Produce Report
Save to `to-jared/weekly-token-audit-YYYY-MM-DD.md`:
- Current vs last week token count
- Specific compression recommendations
- Compressed alternatives (ready to deploy)

### Step 5: Auto-Implement Low-Risk Changes
If change is ONLY removing confirmed stale/duplicate content:
- Apply directly (no Jared approval needed)
- Log what was changed

If change restructures or removes potentially useful content:
- Propose to Jared for approval

## Target Metrics

| Metric | Target |
|--------|--------|
| Total always-loaded tokens | < 10,000 |
| CLAUDE.md tokens | < 3,500 |
| MEMORY.md tokens | < 1,000 |
| Week-over-week growth | < 5% (flag if exceeding) |

## History

| Date | Total Tokens | Change | Notes |
|------|-------------|--------|-------|
| 2026-02-27 | ~17,380 → ~9,600 | -45% | Initial compression (v3.0 CLAUDE.md) |
