---
name: independent-pair-verification
description: After a department fixes its own issue and self-attests "shipped", DO NOT trust the self-attestation. An independent agent (different process, different invocation) must re-probe the live system with fresh evidence. Use after every dept-routed fix before marking RESOLVED.
type: coordination-pattern
domain: quality assurance, audit separation, self-attestation prevention
proven_on: 777-api fix 2026-05-01 (ST# fixed, conductor pair-verified with fresh curl from different process)
---

# Independent Pair-Verification

## The Principle

**Self-attestation is not verification.** If the agent that wrote the fix is the same agent that confirms the fix, you have no audit. You have a write-only queue with hopeful sign-off.

True verification requires:
1. **Different agent** (or different process at minimum)
2. **Different invocation** (separate API call, separate session)
3. **Fresh evidence** (live probe, not cached, not "I just saw it work")
4. **Different verification path** (if fix was at API layer, verify at user-facing layer)

## The Rule

> Every dept-routed fix gets PAIRED with an independent verification BOOP, owned by a DIFFERENT agent. Default verifier = `operations-analyst` (OP#) or the orchestrator/conductor running fresh probes.

## When to Use

- Department reports "fix shipped" — before marking RESOLVED
- Customer-facing issue resolved — before closing the ticket
- Migration completed — before declaring success
- Security patch applied — before stopping incident response
- Any "I just deployed it" claim from any agent

## How to Apply

### Step 1: Receive self-attestation
Department or specialist reports: "Fix shipped. Live evidence: [their own probe]."

### Step 2: Independent re-probe
- Open a fresh shell / spawn a fresh sub-agent / use a different verification tool
- Run a NEW probe (different command, different timestamp, fresh response)
- Capture full output

### Step 3: Compare evidence
- Does the independent probe match the self-attestation?
- Are there any differences (timestamps, payload structure, headers)?
- Did the fix solve the user-visible problem (not just the technical claim)?

### Step 4: Mark verification status
- ✅ **VERIFIED** — independent probe confirms fix
- ⚠️ **DISCREPANCY** — outputs differ; investigate before closing
- ❌ **FAILED** — independent probe shows fix didn't actually work

## Real Example (2026-05-01)

**Self-attestation by ST#**:
> "Root cause: SPREADSHEET_ID bound to wrong sheet + path mismatch. Server-side alias added. Live evidence: `/api/sheet?range=Handshake%20Queue!A:H` returns 200, 42 rows."

**Conductor's independent verification**:
- Fresh shell, different time (00:31 UTC vs ST#'s ~00:28)
- Different sheet (`Morning Pulse!A:H` instead of `Handshake Queue`)
- Verified `data.json` export refresh timestamp
- Confirmed commit `83eccfc` on main branch

**Result**: Two probes, two paths, both green. RESOLVED.

Had ST# self-attested without conductor pair-verification, a stale-cache issue or partial-deploy scenario could have slipped through.

## The Verifier-Independence Test

Before accepting "fix verified," answer:

- [ ] Did the verifier run from a different process than the fixer?
- [ ] Did the verifier use a different invocation (not just rerun the same command)?
- [ ] Did the verifier check user-visible behavior (not just internal state)?
- [ ] Did the verifier produce its own evidence artifact (timestamp, response body, screenshot)?

If any answer is NO → not verified. Send back through the loop.

## Anti-Pattern: Self-Verification Theater

Common failure modes:
- Same agent fixes AND verifies → no audit
- "I just deployed and tested it" → no separation
- Reviewer signs off without re-running → rubber-stamp
- Verification BOOP runs same script as fix BOOP → not independent

## Companion Skills

- `cross-boop-convergence-escalation` — detects need for verification across cycles
- `verification-before-completion` — broader verification principle
- `engineering-flow-boop` — BUILD→SECURITY→QA→SHIP enforcement

## Memory Anchors

- `feedback_verifier_independence_audit_separation.md` — independent verifier rule
- `feedback_routed_items_need_verification_boop.md` — paired BOOP requirement

## Distribution

Critical for any civilization running:
- Multi-agent dept/specialist patterns
- Customer-facing fixes
- Compliance/audit-relevant work
- Production deployments

Without independent pair-verification, trust collapses into hopeful self-reporting and chronic regressions become invisible.
