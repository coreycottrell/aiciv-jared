# CTO Memory: Full Engineering Pipeline - All 12 Agents

**Date**: 2026-02-21
**Type**: teaching
**Agent**: cto
**Confidence**: high
**Tags**: engineering-pipeline, workflow, agent-roles, architecture, delegation

---

## Context

Jared requested a full review of the engineering pipeline to use ALL engineering agents
like a real dev team. This memory captures the definitive pipeline architecture.

---

## The 12 Engineering Agents and Their Exact Roles

1. **cto** - Architecture BEFORE builds. Makes ADRs. Never writes code.
2. **full-stack-developer** - The builder. Frontend to backend. Has TDD skill.
3. **ai-ml-engineer** - AI/ML features only. LLM integration, RAG, prompt engineering.
4. **data-scientist** - Insight from data. Analysis, A/B testing, KPI definition.
5. **data-engineer** - Data infrastructure. ETL pipelines, warehouses, data quality.
6. **security-engineer-tech** - Proactive security in builds. OWASP, threat modeling, secure code review.
7. **devops-engineer** - Deployment automation. CI/CD, infrastructure, monitoring.
8. **qa-engineer** - Test execution. Bug hunting, release sign-off.
9. **test-architect** - Test STRATEGY design (before qa-engineer executes).
10. **refactoring-specialist** - Code quality. Invoke at quantified thresholds, not continuously.
11. **performance-optimizer** - Bottleneck finding. Analysis only, not implementation.
12. **pattern-detector** - Pre-build pattern scan. Prevents reinventing existing solutions.

---

## The 10-Step Pipeline

```
Step 1: CTO Gate → ADR (for architecture/integration decisions)
Step 2: Pattern Scan → pattern-detector (parallel with Step 1)
Step 3: Test Strategy → test-architect
Step 4: Build → full-stack-developer (+ ai-ml-engineer and/or data-engineer in parallel if needed)
Step 5: Security Review → security-engineer-tech (mandatory gate)
Step 6: QA Testing → qa-engineer (mandatory gate)
Step 7: Performance Check → performance-optimizer (user-facing features)
Step 8: Deploy → devops-engineer
Step 9: Post-Ship Measurement → data-scientist
Step 10: Code Health → refactoring-specialist (bi-weekly, not per-feature)
```

---

## Key Insights

### CTO is Front-Loaded
CTO must be invoked BEFORE any build starts, not during or after.
Architecture discovered through implementation = architectural debt.

### Parallel Full-Stack Developers
Multiple full-stack-developer instances can run in parallel when:
- CTO defines interface contracts in the ADR
- Features touch different parts of the codebase
- File ownership is explicitly assigned per feature

Security and QA stay SEQUENTIAL (they need the full integrated system).

### Underutilized Agents (as of 2026-02-21)
- test-architect: Not invoked before builds (QA runs without a strategy)
- pattern-detector: Not invoked pre-build (patterns rediscovered each time)
- refactoring-specialist: Only reactive, never proactive
- performance-optimizer: No systematic benchmarking post-deploy
- cto: Being bypassed entirely for architectural decisions

### Data Intelligence Layer (separate from app layer)
data-engineer → data-scientist → ai-ml-engineer flow:
- data-engineer collects and pipes events
- data-scientist finds patterns and defines what to optimize
- ai-ml-engineer builds AI features based on those insights
- full-stack-developer implements the UI around all of it

### Current PureBrain Data Gap
The .jsonl log files (payments, web conversations) are raw events with no ETL.
data-engineer should build a pipeline to make them queryable.
data-scientist can then analyze conversion funnels and user behavior.

---

## Parallel Developer Pattern

```
CTO: defines interface contracts in ADR
  ↓
full-stack-developer (A): Feature A (e.g., frontend/auth)
full-stack-developer (B): Feature B (e.g., backend API)   ← parallel
  ↓
security-engineer-tech: Reviews integrated system (sequential)
qa-engineer: Tests integrated system (sequential)
devops-engineer: Single coordinated deploy
```

---

## Security/QA Distinction

security-engineer-tech + qa-engineer are both GATES.
Nothing ships if either rejects. Findings return to full-stack-developer for fixes.
Only after both sign off does devops-engineer deploy.
