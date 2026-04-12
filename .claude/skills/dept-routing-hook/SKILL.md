---
name: dept-routing-hook
description: PRE-TASK GATE. Fires before ANY task. Forces department classification. "Which department owns this?" MUST be answered before proceeding. Blocks direct specialist invocation. TRIGGER WORDS "task", "do", "build", "fix", "create", "write", "research", "analyze", "help", "can you", "please"
---

# Department Routing Hook: Pre-Task Gate

**THIS FIRES BEFORE EVERY TASK. NO EXCEPTIONS.**

---

## The Gate (3-Second Check)

**Before taking any action on any task, answer:**

> "Which of the 23 Pure Technology departments owns this work?"

If you can answer → invoke that dept manager first.
If you cannot answer → invoke `dept-pure-technology` (PT#) by default.

**You do not proceed until you have identified the department.**

---

## Quick-Fire Decision Tree

```
TECHNOLOGY, CODE, BUILDS, INFRASTRUCTURE?
  → dept-systems-technology (ST#)

MARKETING, CONTENT, BRAND, SOCIAL, BLOG?
  → dept-marketing-advertising (MA#) for PT's own marketing
  → dept-pure-marketing-group (PMG#) for client-facing

SALES, REVENUE, PIPELINE, CLIENTS?
  → dept-sales-distribution (SD#)

PRODUCT, FEATURES, UX, ROADMAP?
  → dept-product-development (PD#)

MONEY, INVOICES, BUDGETS, FINANCIAL?
  → dept-accounting-finance (AF#)

PEOPLE, HIRING, CULTURE, HR?
  → dept-human-resources (HR#)

LEGAL, CONTRACTS, COMPLIANCE?
  → dept-legal-compliance (LC#)

RESEARCH, INNOVATION, R&D?
  → dept-pure-research (PR#)

OPERATIONS, PROCESSES, PLANNING?
  → dept-operations-planning (OP#)

CROSS-DEPARTMENT or COMPANY-WIDE?
  → dept-pure-technology (PT#)

STILL UNSURE?
  → dept-pure-technology (PT#) — always catches edge cases
```

---

## Bypass Violations (FORBIDDEN)

- Invoking `full-stack-developer` directly for feature work
- Invoking `content-specialist` directly for content work
- Invoking `security-engineer-tech` directly for security audits
- Invoking `web-researcher` directly for business research
- Invoking `qa-engineer` directly for testing
- Invoking `browser-vision-tester` directly for visual testing

## Permitted Direct Invocations (Infrastructure Only)

- `human-liaison` for email (constitutional requirement)
- `collective-liaison` for hub communication
- `integration-auditor` for infrastructure validation
- `result-synthesizer` for synthesizing dept outputs
- `tg-bridge` for Telegram infrastructure

---

## Gate Passes When

You can state: "This task goes to [DEPT NAME] because [REASON]. Invoking [dept-agent-name]."
