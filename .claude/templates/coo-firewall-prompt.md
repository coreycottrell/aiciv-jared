# COO Firewall Prompt Template

**Purpose**: When a BOOP task is flagged `coo_firewall: true`, the launched agent
must NOT surface raw sub-agent outputs to Primary. Instead it routes every
sub-agent output it collects through the `result-synthesizer` agent using the
discipline below, and surfaces ONLY a compressed digest to the Primary inbox.

This format forces analysis -> action conversion (the measured plateau). Binary
YES/NO decisions and an executable action queue cannot be "read and forgotten" —
they demand a response.

---

## Firewall Discipline (the launched agent MUST follow this)

1. Do the task's work. If you delegate to sub-agents, write each raw sub-agent
   output to disk under:

       /tmp/coo-firewall/{task_id}/{agent_name}.md

   These raw files are kept for audit. Do NOT paste them into your final report.

2. After all sub-agent outputs are collected, invoke the `result-synthesizer`
   agent over those raw outputs with the COMPRESSION CONTRACT below.

3. Write ONLY the synthesizer's digest to the Primary inbox:

       /home/jared/projects/AI-CIV/aether/inbox/conductor-boop-{task_id}-{UTC_TIMESTAMP}.md

4. Your Telegram summary line stays as instructed by the BOOP prompt (1-2
   sentences). The digest is the inbox artifact; Telegram is the ping.

---

## COMPRESSION CONTRACT (what result-synthesizer must emit — nothing else)

The digest is <= ~500 tokens and contains EXACTLY these three sections, in order,
and nothing else (no preamble, no raw quotes, no restated context):

```
## SUMMARY (3 bullets max)
- <bullet 1>
- <bullet 2>
- <bullet 3>

## DECISIONS (YES/NO)
- [ ] <binary question Primary must answer YES or NO> (default if no answer: <YES|NO>)
- [ ] <binary question> (default: <YES|NO>)

## ACTION QUEUE (executable)
1. <imperative action — a command, a delegation, or a file edit — not an observation>
2. <imperative action>
```

### Rules for the synthesizer
- SUMMARY: at most 3 bullets. Each bullet is a finding, not a narrative.
- DECISIONS: every item is answerable with YES or NO only. No open questions.
  Every decision has an explicit default so inaction still resolves it.
- ACTION QUEUE: every item is executable — a shell command, an agent delegation,
  or a concrete file change. No "consider", "review", "investigate" verbs unless
  they name the exact next executable step.
- Emit NOTHING outside these three sections. No raw sub-agent text. No apologies.

---

**Why this exists**: Primary reading 4 x 8000-token reports produced zero
operational changes for 4 consecutive days (analysis-to-action plateau, 8.5/10).
A 500-token digest whose middle section is binary decisions converts because the
format demands a response.
