# Background Research Pattern

**Purpose**: Prevent research output from permanently bloating conductor's context window.

## Problem

Research agents return 3,000-5,000 token responses that enter the conductor's context permanently. 3-5 research tasks/session = 10,000-25,000 tokens of research output for the entire session.

## Pattern

### Step 1: Invoke with File-Write Instruction

```
Task(
  prompt="Research [TOPIC]. Write complete findings to /tmp/research-[topic]-YYYY-MM-DD.md.
          Return ONLY: DONE|path=/tmp/research-[topic]-YYYY-MM-DD.md|summary=[3-line-gist]",
  subagent_type="web-researcher",
  run_in_background=true  # Optional: truly async
)
```

### Step 2: Receive Compressed Response

What enters conductor context (~50 tokens):
```
DONE|path=/tmp/research-pricing-2026-02-27.md|summary=Found 5 sources. Competitor X raised prices 50%. Market avg $120/mo. Our position strong.
```

### Step 3: Read On-Demand

Only read the full research file when you need it for implementation:
```
Read(file_path="/tmp/research-pricing-2026-02-27.md")
```

## Token Math

| Pattern | Tokens in Context | When |
|---------|------------------|------|
| Normal | 3,000-5,000 per task | Always (permanent) |
| Background | ~50 per task + full read when needed | On-demand |
| Savings | 2,950-4,950 per task | |

## Best Agents for This Pattern

| Agent | Typical Output Size | Savings |
|-------|-------------------|---------|
| web-researcher | 3,000-5,000 tok | High |
| code-archaeologist | 2,000-4,000 tok | High |
| pattern-detector | 1,500-3,000 tok | Medium |
| doc-synthesizer | 2,000-5,000 tok | High |
| content-specialist | 1,000-3,000 tok | Medium |

## When NOT to Use

- Quick specialist consultations (< 500 token responses)
- Agents whose output you need immediately for the next step
- Human-facing deliverables (blog posts, reports for Jared)

## File Naming Convention

```
/tmp/research-[topic]-YYYY-MM-DD.md
/tmp/audit-[type]-YYYY-MM-DD.md
/tmp/analysis-[subject]-YYYY-MM-DD.md
```

Temp files auto-clean on reboot. For persistent results, write to `to-jared/` or `memories/`.
