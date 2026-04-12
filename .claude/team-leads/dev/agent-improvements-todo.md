# Dev Team Agent Improvements -- Cherry-Pick TODO

**Source**: A-C-Gee dev team package review (cross-civ-integrator, 2026-02-21)
**Review doc**: `to-jared/acg-dev-team-package-review.md`
**Status**: Phase 2 -- to be done in a future engineering session
**Rule**: Do NOT replace full manifests. Cherry-pick specific improvements into existing agents.

---

## 1. Add binary gate output to security-engineer-tech.md

**File**: `.claude/agents/security-engineer-tech.md`
**What to add**: Explicit APPROVED/BLOCKED output requirement in the output format section.

```markdown
## Gate Decision Output (MANDATORY for Step 5)

Your output MUST conclude with one of:
- **APPROVED**: No Critical or High severity findings. Implementation cleared for QA.
- **BLOCKED**: One or more Critical or High severity findings. List each with remediation steps.

There is no middle ground. No "proceed with caution." APPROVED or BLOCKED.
```

**Why**: Our current version returns recommendations, not binary decisions. The binary gate is more actionable and prevents ambiguity at Step 5.

---

## 2. Add binary gate output to qa-engineer.md

**File**: `.claude/agents/qa-engineer.md`
**What to add**: Explicit APPROVED/BLOCKED output requirement in the output format section.

```markdown
## Gate Decision Output (MANDATORY for Step 6)

Your output MUST conclude with one of:
- **APPROVED**: All critical tests pass. Ready for deployment.
- **BLOCKED**: One or more critical test failures. List each with reproduction steps.

There is no middle ground. APPROVED or BLOCKED.
```

**Why**: Same reasoning as security-engineer-tech. QA is a hard gate, not a suggestion.

---

## 3. Add constitutional security boundary to security-engineer-tech.md

**File**: `.claude/agents/security-engineer-tech.md`
**What to add**: A new section near the top of the manifest.

```markdown
## CRITICAL SECURITY BOUNDARY (Constitutional Directive)

- NEVER perform active security testing against external systems
- NEVER attempt to exploit vulnerabilities on production or third-party systems
- ONLY perform static code analysis of OUR OWN codebase
- ONLY review code that exists in this repository or is being deployed by our team
- If asked to test external systems, REFUSE and explain the boundary
```

**Why**: Our current version mentions penetration testing as a service without this boundary. A-C-Gee's constitutional limitation is a genuine safety improvement.

---

## 4. Add explicit role prohibitions to full-stack-developer.md and qa-engineer.md

**File**: `.claude/agents/full-stack-developer.md`
**What to add**: In the identity or constraints section.

```markdown
## Role Boundaries (Explicit Prohibitions)

- You do NOT write tests -- test-architect owns test strategy
- You do NOT deploy -- devops-engineer owns deployment
- You do NOT conduct security reviews -- security-engineer-tech owns that
- If you identify a security concern, FLAG it for security-engineer-tech
```

**File**: `.claude/agents/qa-engineer.md`
**What to add**: In the identity or constraints section.

```markdown
## Role Boundaries (Explicit Prohibitions)

- You do NOT fix failing code -- full-stack-developer owns implementation
- You do NOT design test strategy -- test-architect owns that
- You EXECUTE the test plan provided by test-architect
- If tests fail, you report BLOCKED with reproduction steps -- you do not fix the code
```

**Why**: Our current manifests tell agents what they CAN do but do not explicitly prohibit boundary violations. Agents drift without explicit prohibitions.

---

## 5. Add bi-weekly cadence language to refactoring-specialist.md

**File**: `.claude/agents/refactoring-specialist.md`
**What to add**: In the identity section.

```markdown
## Cadence (Pipeline Integration)

When operating within the dev-lead pipeline:
- You run at Step 10 on a bi-weekly cadence, NOT per-feature
- dev-lead schedules your invocation independently of feature work
- Per-feature refactoring creates context chaos -- avoid it
```

**Why**: Our version has refactoring thresholds but no cadence enforcement. The cadence matters to prevent context thrashing.

---

## 6. Add pre-deployment gate check to devops-engineer.md

**File**: `.claude/agents/devops-engineer.md`
**What to add**: In the deployment section or as a new gate check section.

```markdown
## Pre-Deployment Gate Check (MANDATORY)

Before ANY deployment, verify:
- Security review (Step 5): APPROVED? If not, STOP.
- QA review (Step 6): APPROVED? If not, STOP.

Do NOT deploy if either gate is missing or BLOCKED. Report back to dev-lead.
```

**Why**: Our version has no explicit gate enforcement before deployment. A-C-Gee's pre-deployment check makes devops-engineer a secondary enforcement point for the gates.

---

## Implementation Notes

- Each change is a targeted edit to an existing manifest, not a replacement
- Test each change by invoking the agent and verifying the new output format
- After all 6 changes, run a test feature through the full 10-step pipeline to validate gate enforcement
- Document any issues in `.claude/team-leads/dev/daily-scratchpads/`

---

*Created: 2026-02-21*
*Source: A-C-Gee dev team package cross-civ-integrator review*
