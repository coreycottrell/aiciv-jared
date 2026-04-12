# Capability Gap Analysis — April 7, 2026

**Agent**: agent-architect | **Type**: BOOP scheduled task

---

## Fleet Status
- **161 agent manifests** registered
- **64 skills** available
- Last high-performance session: Apr 5 evening (9/10, 80+ deliverables, 20+ agents, 9.1:1 leverage)

---

## Identified Gaps

### 1. CRITICAL: Email Welcome Sequence — No Owner (Flagged 12+ Times)
**Evidence**: Scratch pad lists "Email welcome sequence (flagged 12+ times, still not built)" as PENDING since at least Mar 31. Multiple agents *describe* email sequence capability (MA#, marketing-strategist, marketing-automation-specialist) but none have actually built it.

**Root Cause**: Capability exists in theory across multiple agents, but no single agent OWNS the deliverable. Diffusion of responsibility.

**Recommendation**: NOT a new agent. Route explicitly to `MA#` with a concrete spec: "Build the post-payment welcome email sequence using Brevo. 3 emails: immediate welcome, Day 2 getting started, Day 7 check-in." Track as a project deliverable, not a BOOP.

### 2. HIGH: Heavy ST# Concentration (70% of delegations)
**Evidence**: Self-analysis Apr 5 evening notes "Heavy ST# reliance (70% of delegations)" and recommends "Reduce ST# load — route to PI6# and PD# where appropriate."

**Root Cause**: Most active work is CF Pages deployment, site fixes, and portal engineering — all naturally ST# domain. But some work (product decisions, infrastructure provisioning) could go to PD# and PI6#.

**Recommendation**: No new agent needed. Enforce routing discipline: product UX decisions → PD#, hosting/server provisioning → PI6#, only code changes → ST#.

### 3. MEDIUM: LinkedIn Automation Gap (Commenting Still Manual)
**Evidence**: Self-analysis notes "LinkedIn commenting never worked via automation (cookies/429/IP mismatch)." Jared accepted manual commenting as current state.

**Root Cause**: Platform anti-bot measures defeat browser automation. The linkedin-specialist agent exists but lacks a reliable execution path.

**Recommendation**: Accept manual commenting as permanent for now. The linkedin-specialist should focus on *content preparation* (draft comments, identify targets, schedule queue) rather than attempting automated posting. Consider: the 3d-design-specialist + linkedin-writer pipeline works well for *posts*; apply same human-in-the-loop pattern to comments.

### 4. MEDIUM: No Dedicated Onboarding QA Agent
**Evidence**: Memory file `feedback_onboarding_real_user_march22.md` notes "AI refused to search ('afraid to get it wrong') — capability gap, bad UX." The onboarding flow is CONSTITUTIONAL but QA is spread across payment-flow-qa, wtt-qa, and ptt-qa with no unified owner.

**Root Cause**: Onboarding spans multiple systems (payment pages, seed pipeline, Witness containers, magic links) — no single QA agent covers the full E2E flow.

**Recommendation**: NOT a new agent. Instead, create an **onboarding-e2e-qa skill** that chains payment-flow-qa → wtt-qa → ptt-qa in sequence, with a unified pass/fail report. Assign to `wtt-qa` as primary owner since they already cover birth pipeline + container launch.

### 5. LOW: Underutilized Agents
**Evidence**: 161 agent manifests but typical sessions invoke 15-20. Department managers like LC#, PR#, PI6#, PDA#, PL#, BOA#, IR# see near-zero invocations.

**Root Cause**: Most daily work is engineering + marketing + sales. Legal, R&D, infrastructure, and advisory departments have valid agents but insufficient trigger conditions.

**Recommendation**: No new agents. Instead, create lightweight trigger conditions in existing BOOPs:
- LC# → trigger on any new contract/agreement mention
- PR# → trigger on "R&D" keyword (already partially exists)
- PI6# → trigger on server/hosting/VPS mentions
- IR# → trigger when fundraise work surfaces

---

## What We Do NOT Need

| Temptation | Why Not |
|-----------|---------|
| More QA agents | Already have 4 (ptt-qa, wtt-qa, cts-qa, payment-flow-qa). Need coordination, not more agents. |
| Dedicated TTS agent | Chatterbox TTS is infrastructure, not a domain. ST# handles it fine. |
| More marketing agents | Already have 8+ marketing-adjacent agents. Execution > agent count. |
| AI-to-AI protocol agent | collective-liaison + cross-civ-integrator already cover this. |

---

## Summary

**Fleet is mature at 161 agents.** The gaps are not missing agents — they're:
1. **Ownership clarity** (welcome email has 4 potential owners, zero actual owners)
2. **Routing discipline** (ST# overloaded, sister departments underused)
3. **Skill composition** (onboarding QA needs a chained skill, not a new agent)
4. **Acceptance of limits** (LinkedIn automation is a platform constraint, not our gap)

**Net recommendation: 0 new agents, 1 new skill (onboarding-e2e-qa), 3 routing fixes.**
