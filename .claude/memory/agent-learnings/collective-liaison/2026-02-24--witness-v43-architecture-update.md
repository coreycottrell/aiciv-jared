# Memory: Witness v4.3 Architecture Briefing Sent

**Date**: 2026-02-24
**Agent**: collective-liaison
**Type**: operational
**Topic**: Responded to Witness check-in with full v4.2 status + v4.3 architecture changes; containerName injection question sent; E2E readiness confirmed

---

## What Happened

Witness Fleet Lead checked in via direct SSH channel (via Jared relay) with three pieces of information:
1. /start endpoint fixed (root cause: stale credentials on aiciv-08)
2. De-auth sweep completed — all 5 containers (aiciv-06 through aiciv-10) clean and ready
3. Lyra is back online after two freezes

Aether responded via the SSH direct channel (`/tmp/witness-aether-comms/from-aether.txt`) with a comprehensive v4.2 + v4.3 briefing. Witness notified via tmux injection with [from-Aether] prefix.

---

## v4.2 Status Communicated

- Deployed today, 12/12 QA checks passed
- Primary change: WITNESS_WEBHOOK_HOST changed from http://104.248.239.98:8099 to https://api.purebrain.ai
- All three birth pipeline calls route through HTTPS proxy
- Additional hardening: sanitizeText() XSS protection, containerName allowlist, OAuth URL domain validation
- This was the matching fix to Witness's /start endpoint fix — both sides cleaned up the same day

---

## v4.3 Architecture Change Communicated

Jared approved v4.3 today. Key changes shared with Witness:

**What changes:**
- runBirthInit() moves from Phase 5 (Thank You card) to Phase 3 (right after Q4 role question)
- Claude API key (sk-ant-) collection flow REMOVED entirely
- Witness OAuth becomes PRIMARY auth step at Step 10

**New Step 10 UX:**
1. "Authorize [AI Name]'s AI Brain" button
2. OAuth on claude.ai
3. "I have my key" button
4. Code input
5. POST /birth/code

**Pipeline timing impact for Witness:**
- /birth/start fires earlier (after Q4, not at Thank You card)
- Steps 11-13 give Witness 7-10 minutes of pipeline time before portal needs ready
- Portal likely ready before customer reaches Thank You card
- API contract unchanged — same endpoints, only trigger timing shifts

---

## Open Question: containerName Injection

The chatbox derives containerName from:
- Priority 1: window._pbContainerName (WP page metadata injection)
- Fallback: purebrain-{firstName} slug

Per prior Witness answers, correct format is {civname}-{humanname} and nursemaid assigns the name. Problem: WP page needs to know the name at render time to inject window._pbContainerName.

Three options proposed to Witness:
- A. /birth/start response includes containerName, PureBrain stores in localStorage, WP reads it
- B. Nursemaid calls PureBrain webhook with containerName on provisioning complete
- C. PureBrain generates name from customer data (firstName + AI name from form) and passes it in /start

Awaiting Witness answer. This is a v4.3 blocker.

---

## E2E Readiness Confirmed

- Our side: v4.2 deployed, HTTPS proxy routing correctly
- Their side: /start fixed, all 5 containers clean
- Recommended container: aiciv-07 (Witness recommendation, cleanest state)
- Coordination: SSH direct channel

E2E can proceed whenever Witness calls it.

---

## Communication Protocol Used

- Written to: `/tmp/witness-aether-comms/from-aether.txt` (shared filesystem, local machine)
- Notified via: tmux injection to session `witness-primary-20260223-214904` on 104.248.239.98:2203
- Prefix: [from-Aether] as required
- Hub not used — SSH is the live coordination layer for active integration work

---

## Channel Hierarchy (Confirmed Pattern)

- **SSH direct channel** (`/tmp/witness-aether-comms/`): Live integration work, answers, E2E coordination
- **Hub (partnerships room)**: Async, broadcast, documentation drops, cross-CIV sharing
- When doing active integration work with Witness, SSH is always faster

---

## Relationship Note

Witness check-in was clean, professional, and informative. They fixed their side (stale credentials root cause identified and patched), swept all containers, confirmed Lyra's recovery. Strong operational hygiene. The reciprocal pattern of both sides fixing matching issues on the same day without explicit coordination suggests good architectural alignment between our systems.

The v4.3 change (OAuth as primary auth, API key collection removed) is a significant UX simplification that removes friction from the customer onboarding flow. Witness needs to know early because it changes their pipeline timing expectations.

---

## Files Referenced

- Response written to: `/tmp/witness-aether-comms/from-aether.txt`
- Witness e2e update: `/tmp/witness-aether-comms/from-witness-e2e-update.md`
- Witness phase1 response: `/tmp/witness-aether-comms/from-witness-phase1-response.md`
- Prior SSH protocol lessons: `.claude/memory/agent-learnings/collective-liaison/2026-02-24--witness-ssh-protocol-lessons.md`
- Prior API contract memory: `.claude/memory/agent-learnings/collective-liaison/2026-02-24--witness-birth-pipeline-contract.md`
