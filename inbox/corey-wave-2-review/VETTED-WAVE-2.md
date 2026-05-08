# Wave 2 Security Vetting + Architecture Comparison

**Date**: 2026-04-14
**Reviewer**: openclaw-researcher (Aether)
**Packages**: triangle-protocol, inter-civ-comms
**Source**: Corey Cottrell's ACG hub (87.99.131.49:8900)

---

## Executive Summary

**triangle-protocol**: 🟢 GREEN — MERGE (adopt their quality gate pattern, keep our constitutional rules)
**inter-civ-comms**: 🟡 YELLOW — MERGE (adopt 3-channel taxonomy, keep our bridge implementation)

Both packages are **conceptual frameworks with zero code dependencies**. No external calls, no phone-home, no shared credentials required. Safe to adopt patterns immediately.

**Key finding**: Their triangle is ACG-centric (one conductor, two executors). Ours is peer-based (three co-equal AIs with role specialization). Their quality gate pattern (conductor verifies executor work) is VALUABLE and non-conflicting with our constitutional rules.

---

## 1. triangle-protocol

### What It Is

A 3-civ coordination pattern where:
- **One conductor** (ACG) routes work, runs quality gate, handles human comms, deploys
- **Two executors** (Proof for reasoning, Hengshi for building) specialize by domain
- **Quality protocol**: Conductor verifies executor output before deploy (executors don't self-verify)
- **Daily cadence**: Morning BOOP → wait for deliveries → deploy as ready

### Comparison to Aether TRIO

| Dimension | ACG Triangle | Aether TRIO |
|-----------|-------------|-------------|
| **Structure** | Hub-spoke (1 conductor + 2 executors) | Peer triangle (3 co-equal AIs) |
| **Roles** | ACG=orchestrate, Proof=reason, Hengshi=build | Aether=medium/orchestrate, Chy=entelechy/follow-through, Morphe=form/fresh-seeing |
| **Quality gate** | Conductor verifies executor work | Each AI verifies own work (BUILD→SECURITY→QA→SHIP flow) |
| **Routing** | ACG routes all work to Proof/Hengshi | Dept-first delegation (ALL work → dept manager → specialists) |
| **Human comms** | ACG owns all Corey dialogue | Aether owns Jared comms (portal-first), Chy has direct comms capability |
| **Deploy authority** | ACG only | Chy owns investor portal deploys, Aether orchestrates other deploys |
| **Constitutional rules** | Not mentioned | 14 TRIO-SHARED-RULES (frozen, co-authored) |

### Key Insights

1. **Their quality gate is BRILLIANT**: "Executing civs don't self-verify" prevents the blind-spot problem where you miss your own mistakes. This is compatible with our BUILD→SECURITY→QA flow — we can add "conductor verification" as a final gate.

2. **Their routing is simpler, ours is more scalable**: ACG routes 100% of work. Aether delegates to 40+ dept managers/specialists. Their pattern works for 3 civs, ours scales to N agents.

3. **Domain specialization differs**: They split reasoning vs building. We split orchestration vs follow-through vs fresh-seeing (Aristotelian hylomorphism). Both valid.

4. **No conflict with constitutional rules**: Their triangle operates at COORDINATION layer. Our TRIO-SHARED-RULES operate at SAFETY/COMPLIANCE layer. Orthogonal concerns.

### Security Analysis

| Vector | Assessment | Notes |
|--------|-----------|-------|
| External calls | ✅ NONE | Pure coordination pattern, no code |
| Code injection | ✅ NONE | Conceptual framework only |
| Phone-home | ✅ NONE | No implementation dependencies |
| Shared credentials | ✅ NONE | Each civ uses own auth |
| External infra dependency | ✅ NONE | Pattern is infrastructure-agnostic |
| Data exfiltration | ✅ NONE | No data handling specified |

**Verdict**: 🟢 **GREEN** (safe to adopt immediately)

### Recommendation: **MERGE**

**Adopt**:
- Quality gate pattern (conductor verifies executor work before deploy)
- Morning BOOP synchronization (trigger all civs together, wait for convergence)
- Domain-based routing clarity (make Aether/Chy/Morphe domain boundaries explicit)

**Keep**:
- Our 14 TRIO-SHARED-RULES (constitutional, frozen)
- Our dept-first delegation (scales to N agents)
- Our peer triangle structure (3 co-equal AIs, not hub-spoke)
- Our grounding system (4-tier re-read triggers)

**Integration path**:
1. Add quality gate to Aether's orchestration flow (verify dept manager output before declaring done)
2. Formalize domain boundaries for Aether/Chy/Morphe (like ACG's reasoning/building split)
3. Keep constitutional rules separate from coordination patterns (orthogonal concerns)

---

## 2. inter-civ-comms

### What It Is

A 3-channel taxonomy for inter-civ communication:
1. **Hub API** — persistent, searchable, auditable (announcements, knowledge sharing)
2. **tmux injection** — real-time, ephemeral (task delegation, quick coordination)
3. **Telegram** — human-visible, notification-enabled (alerts, escalations)

Plus technical fixes:
- tmux Enter-retry pattern (sleep 3, resend Enter after paste)
- Qwen shell-mode workaround (send Escape before injection)

### Comparison to Aether Bridge

| Dimension | ACG inter-civ-comms | Aether Bridge |
|-----------|---------------------|---------------|
| **File channel** | Mentioned but not detailed | `/home/aiciv/shared/from-{sender}/` timestamped .md files |
| **tmux** | Short pings only (<200 chars) | Same — ping with file path, no long content |
| **Hub API** | Primary for persistent comms | Not currently used for inter-AI comms (only for cross-CIV packages) |
| **Telegram** | Human-visible escalations | Human-visible (Jared sees all trio traffic via bridge) |
| **Read receipts** | Not mentioned | `.read` marker written back to sender after confirm |
| **Dashboard** | Not mentioned | 777 Trio Comms panel (feed, filters, auto-refresh 45s) |
| **Dedup** | Not mentioned | bridge_file_path column in sheet, watcher won't re-post |
| **API endpoints** | Hub API (external service) | /trio/message, /trio/messages, /trio/mark-read (own Worker) |

### Key Insights

1. **3-channel taxonomy is USEFUL**: Hub=persistent, tmux=ephemeral, Telegram=human-visible. We currently use tmux+Telegram+dashboard, but not Hub API for inter-AI. Their taxonomy clarifies WHEN to use WHICH channel.

2. **We have MORE infrastructure than they describe**: Our bridge includes read-receipts, dedup, dashboard, auto-polling daemon (trio_watcher.py). Their doc focuses on the channels, not the plumbing.

3. **tmux Enter-retry fix is GOLD**: We don't currently do this. Should add to trio_watcher.py and msg-chy.sh.

4. **Hub API for persistent knowledge sharing is UNEXPLORED**: We post packages to the hub, but we don't use it for ongoing Aether↔Chy↔Morphe knowledge sharing. Could be valuable for "things all 3 AIs should know" vs ephemeral task delegation.

### Security Analysis

| Vector | Assessment | Notes |
|--------|-----------|-------|
| External calls | ⚠️ Hub API only | Hub API is external (87.99.131.49:8900), tmux+Telegram are local/controlled |
| Code injection | ✅ NONE | tmux injection is controlled (we own both sender/receiver sessions) |
| Phone-home | ⚠️ Hub API posts | If we adopt Hub API for persistent comms, data goes to Corey's server |
| Shared credentials | ✅ NONE | Each civ has own Hub API token |
| External infra dependency | ⚠️ Hub availability | If Hub goes down, persistent channel breaks (tmux+Telegram still work) |
| Data exfiltration | ⚠️ Hub visibility | Anything posted to Hub is visible to Corey/ACG (by design for cross-CIV sharing) |

**Verdict**: 🟡 **YELLOW** (safe for coordination, cautious for sensitive data)

**Notes**:
- Hub API is DESIGNED for cross-CIV sharing (public-by-default within hub network)
- Don't post investor data, credentials, or Jared-private info to Hub
- Hub downtime would break persistent channel (but not real-time tmux/Telegram)

### Recommendation: **MERGE**

**Adopt**:
- 3-channel taxonomy (Hub=persistent, tmux=ephemeral, Telegram=human-visible)
- tmux Enter-retry pattern (add to trio_watcher.py, msg-chy.sh)
- Qwen Escape workaround (if we ever coordinate with Qwen-based civs)
- Hub API for **public knowledge sharing** (cross-CIV learnings, not private work)

**Keep**:
- Our bridge implementation (timestamped files, read-receipts, dedup, dashboard)
- Our 777 Trio Comms panel (richer than their description)
- Our trio_watcher.py daemon (auto-polling, auto-inject, auto-post to dashboard)
- File-based pattern as PRIMARY (Hub API as secondary for persistence)

**Integration path**:
1. Add Enter-retry to trio_watcher.py tmux injection (sleep 3, resend Enter)
2. Update msg-chy.sh with same fix
3. Use Hub API for "broadcast to all civs" knowledge (not task delegation)
4. Document channel selection: tmux for tasks, Hub for knowledge, Telegram for alerts
5. Never post investor/client/private data to Hub (use file channel for sensitive)

---

## What We Should Do BEFORE Building Unified Comms

1. **Add tmux Enter-retry fix** (10 min work, high value)
2. **Formalize Aether/Chy/Morphe domain boundaries** (like ACG's reasoning/building split)
3. **Add conductor quality gate** to orchestration flow (Aether verifies dept output before done)
4. **Document 3-channel taxonomy** in TRIO-GROUNDING.md (when to use which channel)

## What We Should Do AFTER (Unified Comms Phase)

1. **Integrate Hub API as persistent channel** (for cross-CIV knowledge sharing, not tasks)
2. **Enhance 777 panel** with channel filters (Hub posts vs tmux pings vs Telegram alerts)
3. **Add Hub sync daemon** (poll Hub API, inject to tmux when relevant posts arrive)
4. **Cross-CIV protocol** (how Aether↔ACG coordination differs from Aether↔Chy)

---

## Key Learnings for Unified Comms Decision

1. **Channel taxonomy matters more than implementation**: Their 3-channel split (Hub=persistent, tmux=ephemeral, Telegram=human-visible) clarifies WHAT each channel is FOR. We can adopt this taxonomy immediately without changing our bridge code.

2. **Quality gate is orthogonal to comms**: ACG's "conductor verifies executor work" pattern is COORDINATION architecture, not COMMUNICATION architecture. It's valuable regardless of how messages flow.

3. **We're ahead on implementation, they're ahead on patterns**: We have richer bridge plumbing (read-receipts, dedup, dashboard). They have clearer coordination patterns (quality gate, channel taxonomy). MERGE both.

4. **Hub API is for PUBLIC cross-CIV knowledge, not PRIVATE trio work**: Use Hub to share learnings with ACG/other civs. Use file bridge for Aether↔Chy↔Morphe private coordination.

5. **Small fixes have big impact**: tmux Enter-retry is a 3-line change that prevents message loss. Qwen Escape workaround is model-specific but generalizable (always check for mode quirks before inject).

---

## Bottom Line for Jared

**Both packages are GREEN/YELLOW for security** (no code dependencies, no malicious patterns).

**triangle-protocol is a COORDINATION pattern**, not a communication pattern. It's about WHO verifies WHAT and WHO routes TO WHOM. Compatible with our constitutional rules. Recommend adopting their quality gate + domain clarity.

**inter-civ-comms is a CHANNEL TAXONOMY**, not a replacement for our bridge. It's about WHEN to use WHICH channel. Compatible with our current implementation. Recommend adopting their taxonomy + tmux Enter-retry fix.

**Unified comms should**:
- Keep our file bridge as PRIMARY (rich, private, auditable)
- Add Hub API as SECONDARY for persistent cross-CIV knowledge
- Use their 3-channel taxonomy to document WHEN to use WHICH
- Add quality gate pattern to orchestration (Aether verifies dept output)
- Fix tmux Enter-retry bug (ACG discovered it, we should benefit)

**No blockers. Safe to proceed with unified comms build AFTER adopting these patterns.**
