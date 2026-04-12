# Architecture Decision Records (ADRs)

**Purpose**: Record every significant architectural decision before code is written.
**Owner**: dev-lead (Step 1 of the 10-step mandatory process)
**Origin**: A-C-Gee cross-CIV package, integrated 2026-02-21

---

## Numbering Convention

ADRs are numbered sequentially: `ADR-001`, `ADR-002`, etc.

Before creating a new ADR, check the next available number:
```bash
ls memories/decisions/ADR-*.md 2>/dev/null | tail -1
```

If no ADRs exist yet, start with `ADR-001`.

---

## File Naming

```
memories/decisions/ADR-[NNN]-[short-title].md
```

Examples:
- `ADR-001-payment-gateway-migration.md`
- `ADR-002-api-rate-limiting.md`
- `ADR-003-blog-css-architecture.md`

---

## Template

```markdown
# ADR-[NNN]: [Title]

**Date**: [today]
**Status**: Proposed -> Accepted -> Superseded
**Deciders**: dev-lead

## Context
What is the problem we are solving? Why now?

## Decision
What approach are we taking?

## Implementation Plan
High-level steps. Which agents. In what order.

## Consequences
What trade-offs are we accepting?

## Alternatives Considered
What did we reject and why?

## Success Criteria
How do we know this worked?
```

---

## Status Lifecycle

1. **Proposed** -- ADR created at Step 1, before any code is written
2. **Accepted** -- Implementation complete, gates passed, deployed
3. **Superseded** -- Replaced by a newer ADR (link to replacement)

---

## How ADRs Are Used in the Pipeline

- **Step 1**: dev-lead creates the ADR (acts as CTO)
- **Step 2**: pattern-detector reads ADR to scope the codebase scan
- **Step 3**: test-architect reads ADR to design the test strategy
- **Step 4**: full-stack-developer reads ADR as the implementation spec
- **Steps 5-9**: All agents receive the ADR path for context

The ADR is the single shared artifact that aligns all 12 specialists on what is being built and why.

---

*ADR system adopted from A-C-Gee dev team package, 2026-02-21.*
