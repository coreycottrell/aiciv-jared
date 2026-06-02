# COO Firewall Flow

**Status**: Phase-2 (aiciv-native-org integration). Flag-gated, default OFF.
**Source**: architect spec — `.claude/memory/agent-learnings/architect/20260601-aiciv-native-org-federation-integration.md`
**Owner pattern**: result-synthesizer agent + boop_executor prompt gate

---

## Problem It Solves

The analysis-to-action plateau. Primary reads large raw multi-agent reports and
converts near-zero findings into operational changes. Measured at 8.5/10 for 4
consecutive days (latest.md consolidation 2026-06-01).

## The Pattern

```
Default (flag OFF):
  BOOP task -> launched agent does work -> agent self-reports (raw) -> Primary

COO Firewall (coo_firewall: true):
  BOOP task -> launched agent does work, sub-agent outputs -> /tmp/coo-firewall/{task_id}/
            -> result-synthesizer compresses to a digest (3 bullets + YES/NO + action queue)
            -> ONLY the digest reaches the Primary inbox
            -> raw outputs stay on disk for audit, NOT surfaced to Primary
```

The binary-decision format forces conversion: a YES/NO list with explicit
defaults cannot be read-and-forgotten the way an 8000-token report can.

## How It Is Wired (executor reality)

`boop_executor.py` does not collect sub-agent outputs in-process. Each BOOP is a
single fire-and-forget `claude --print` agent that does all work (including any
delegation) and self-reports. Therefore the firewall is applied at the ONE
surface the executor controls: the prompt handed to the launched agent.

When a task carries `"coo_firewall": true`, `build_boop_prompt()` appends the COO
Firewall discipline (from `.claude/templates/coo-firewall-prompt.md`) to the
agent's prompt. The agent then self-enforces: route sub-agent outputs through
result-synthesizer, write only the digest to the Primary inbox, keep raw on disk.

- Flag absent/false  => prompt is byte-identical to today. Zero behavior change.
- Flag true          => firewall discipline appended; ~15-25 lines of additive code.

No executor restart is needed — the running daemon reads task definitions and
templates fresh each cycle, so the next natural cycle picks it up.

## Task Definition Example

```json
"some-multi-agent-task": {
  "frequency": "daily",
  "status": "active",
  "agent": "the-conductor",
  "category": "intelligence",
  "coo_firewall": true,
  "description": "..."
}
```

## Audit Trail

Raw sub-agent outputs: `/tmp/coo-firewall/{task_id}/{agent_name}.md`
Primary digest:        `inbox/conductor-boop-{task_id}-{UTC_TIMESTAMP}.md`

## Rollout Note

Pilot on ONE non-critical BOOP first (architect spec: start with an intelligence
digest task, not the main overnight V3). Default OFF for all existing tasks.
