# SWARM PROTOCOL — Intra-Team Self-Organization

**STATUS: ACTIVE** (Adopted 2026-04-13 from Cadence's Hybrid Architecture)

## The 3-Pattern Hybrid Architecture

| Pattern | Scope | When to Use |
|---------|-------|-------------|
| **Conductor** | Primary → Team Leads | Strategic direction, cross-department coordination |
| **Swarm** | Within each team lead's domain | Multi-subtask execution, parallel specialist work |
| **Pipeline** | Automated scripts on loops | Repeatable processes (email, webhooks, monitoring) |

## FOR TEAM LEADS:
1. **Launch ALL subtasks in PARALLEL** — use run_in_background=True on ALL Agent() calls
2. **Never wait sequentially** — launch all, then monitor completions
3. **Shared scratchpad** — agents write findings to `.claude/team-leads/{vertical}/swarm-state.md`
4. **Conflict resolution** — lead resolves conflicting findings (not Primary)
5. **Report summary only** — absorb specialist output in YOUR context, send Primary a summary

## FOR SPECIALIST AGENTS:
1. Write findings to shared scratchpad as soon as complete
2. Check scratchpad before starting — don't duplicate work
3. Flag dependencies — note if your task depends on another agent's output
4. Self-assign — if you finish and see unclaimed work, pick it up

## FOR PRIMARY (AETHER):
1. Only talk to team leads — never reach into a swarm directly
2. Monitor via lead summaries — not individual agent output
3. Steer strategy — tell leads WHAT, not HOW

## MODEL TIERING:
- **Primary (Aether)**: Opus — strategic reasoning, orchestration
- **Department Managers**: Sonnet — routing, coordination
- **Specialist Agents**: Sonnet — execution
- **Pipeline Scripts**: No model — pure Python automation

## PIPELINE PATTERN (for automated workflows):
Source → Parser → Categorizer → Storage → Notification
Each stage = standalone script (zero cost). Runs on cron/loop.
Only escalate to agents on exceptions.
