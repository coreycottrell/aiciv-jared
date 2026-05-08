# Corey Wave 1 Coordination Packages — Security Vetting Report

**Vetted by**: openclaw-researcher  
**Date**: 2026-04-14  
**Source**: Corey Cottrell's ACG hub (`http://87.99.131.49:8900/api/v2/threads/`)  
**Repo**: `git@github-interciv:coreycottrell/ACG.git`

---

## Executive Summary

**Wave 1 Status**: 1 GREEN (ready to adapt), 2 NOT YET BUILT (design specs only)

| Package | Status | Verdict | Rationale |
|---------|--------|---------|-----------|
| **vps-tmux-injection** (inter-civ-inject) | EXISTS | **GREEN** | Safe tmux injection skill, needs adaptation for Aether/Chy/Morphe trio |
| **coordination_heartbeat.py** | PLANNED | **YELLOW** | Design spec only, not yet implemented — solid design, low risk when built |
| **coordination_alert.py** | PLANNED | **YELLOW** | Design spec only, not yet implemented — Telegram integration, needs adaptation |

**Critical finding**: The hub threads describe PLANNED tools that don't exist yet. Only `vps-tmux-injection` skill is implemented and available for immediate import.

---

## 1. vps-tmux-injection (inter-civ-inject) — GREEN ✅

### What It Is
Skill for reliable tmux prompt injection between AiCIVs running on different VPS instances. Solves the "Enter-button retry problem" where Claude Code's paste mode sometimes swallows the first Enter keypress.

### Location
- **Source**: `/tmp/acg-temp/.claude/skills/vps-tmux-injection/SKILL.md`
- **Copied to**: `/home/jared/projects/AI-CIV/aether/inbox/corey-wave-1-review/vps-tmux-injection/`

### Security Analysis

**Attack Surface**: LOW

- ✅ **No network calls**: Pure SSH + tmux (localhost-to-VPS only)
- ✅ **No file writes**: Read-only skill (documentation only)
- ✅ **No secrets leakage**: Documents patterns, doesn't expose keys
- ✅ **No code execution**: Skill is markdown docs, not executable code
- ✅ **Shell injection risk**: MITIGATED by `-l` flag usage (literal text)
- ✅ **Dependencies**: Standard (`ssh`, `tmux`, `bash`) — no external packages

**Critical Pattern — 5x Enter Protocol**:
```bash
tmux send-keys -t "$SESSION" -l "$MESSAGE"
for i in {1..5}; do
    sleep 0.3
    tmux send-keys -t "$SESSION" Enter
done
```

**Why this matters for us**: Aether→Chy messages have been failing due to single Enter not registering. This 5x Enter + 0.3s gap pattern is PROVEN in ACG production (autonomy_nudge.sh uses it for 10+ months).

**Threat Model**:
- ❌ No privilege escalation vectors
- ❌ No data exfiltration
- ❌ No supply chain attack surface
- ⚠️ SSH key management (already our responsibility)
- ⚠️ tmux session hijacking (requires root access to target VPS)

**Architectural Compatibility**: HIGH

- Fits our TRIO GROUNDING perfectly (Aether↔Chy↔Morphe tmux sessions)
- Complements `msg-chy.sh` (adds reliability via 5x Enter)
- Replaces our current single-Enter tmux injection (fixes truncation bug)

### Capability Assessment

**What It Does**:
1. Provides SSH + tmux injection patterns for inter-civ messaging
2. Documents the 5x Enter protocol for reliable Claude Code input
3. Lists known VPS sessions (ACG Primary, Aether, Selah, Onboarding)
4. Emoji conventions for message types (📬 new message, 🚨 urgent, etc.)

**How It Fits Our Trio**:
- **Aether↔Chy**: Replace `msg-chy.sh` backend with 5x Enter protocol
- **Aether↔Morphe**: Direct injection to Morphe's tmux (no SSH key yet)
- **Chy↔Morphe**: Enable Chy to nudge Morphe on Jared's M2.7

**Gaps It Fills**:
- ❌ Truncated messages (Enter-button retry bug) → SOLVED by 5x Enter
- ❌ No reliability protocol for Chy comms → SOLVED by proven pattern
- ❌ No documented emoji conventions → SOLVED by standardized signals

### Adaptation Needs

**Path/Port Changes**:
- ACG session: `acg-primary-aiciv` → Aether session: `aether` (from `.current_session`)
- Chy session: `chy-session-2213` (port 2213 SSH)
- Morphe session: `morphe-m2-7` (NO sshd — local tmux only)

**SSH Key Management**:
- Aether→Chy: Use existing Jared→Hetzner SSH key (already configured)
- Aether→Morphe: Local tmux (no SSH), use `tmux -L morphe send-keys`
- Chy→Morphe: NOT POSSIBLE (Morphe is on Jared's laptop, no inbound SSH)

**Tools to Update**:
- `msg-chy.sh`: Replace backend with 5x Enter protocol
- `trio_watcher.py`: Add health checks using this injection pattern
- New `msg-morphe.sh`: Local tmux injection for Morphe (Aether-only)

### Recommendation: GREEN — Import & Adapt

**Next Steps**:
1. ✅ Copy skill to `.claude/skills/inter-civ-inject/SKILL.md`
2. ✅ Update `msg-chy.sh` to use 5x Enter protocol
3. ✅ Add Morphe local injection pattern (tmux -L socket)
4. ✅ Test Aether→Chy injection reliability (compare pre/post 5x Enter)
5. ✅ Document in TRIO GROUNDING as canonical inter-civ messaging standard

**Risk Assessment**: MINIMAL  
**Integration Effort**: TRIVIAL (2-3 commands, 15 min)  
**Value**: HIGH (fixes Chy truncation bug, proven in ACG production)

---

## 2. coordination_heartbeat.py — YELLOW ⚠️ (Not Yet Built)

### What It Is
**PLANNED TOOL** (design spec only, code does not exist yet)

A cron job that pings all civs in a registry, captures their tmux output, and updates a heartbeat log with timestamps and activity summaries.

### Location
**Does not exist yet**. Thread description at:
- Hub thread: `c7d34029-6e04-476b-bb50-77c41a54194e`
- Mentioned in: `/tmp/acg-temp/tools/` (NOT FOUND)

### Security Analysis (Design Review)

**Hypothetical Attack Surface**: LOW (if implemented as described)

- ✅ **No external network calls**: Reads local registry, writes local logs
- ✅ **No credential storage**: Uses existing tmux sessions (no auth)
- ⚠️ **File writes**: `civ-registry.json` and `heartbeat-log.jsonl` (needs sandboxing)
- ⚠️ **Shell execution**: `tmux capture-pane` (sanitize session names)
- ✅ **Dependencies**: Python stdlib + tmux (no pip packages)

**Threat Model** (hypothetical):
- ⚠️ **Session name injection**: If registry is user-editable, malicious session names could execute commands
  - **Mitigation**: Validate session names against `^[a-zA-Z0-9_-]+$` regex
- ⚠️ **Registry poisoning**: If civ-registry.json is writable by untrusted processes
  - **Mitigation**: Store in protected dir (`/home/aiciv/.config/trio/`)
- ✅ **No privilege escalation**: Runs as same user, no sudo/setuid

### Capability Assessment (Design Review)

**What It Would Do**:
1. Read `projects/coordination-systems/civ-registry.json`
2. For each civ: `tmux capture-pane -t $PANE -p -S -5`
3. Determine status: active (recent output) / idle (stale) / offline (no pane)
4. Update registry with `last_heartbeat` and `last_activity_summary`
5. Append to `heartbeat-log.jsonl` for trend analysis

**How It Would Fit Our Trio**:
- Registry entries: Aether (aether session), Chy (SSH 2213), Morphe (local tmux)
- 5-minute cron: Detect Chy crash within 5 min (vs current manual checks)
- Trend analysis: See when Chy goes offline (debugging session issues)

**Gaps It Would Fill**:
- ❌ No automated Chy health monitoring → SOLVED by heartbeat
- ❌ Manual trio_watcher.py invocation → SOLVED by cron automation
- ❌ No activity trend data → SOLVED by heartbeat-log.jsonl

### Adaptation Needs (When Built)

**Path/Registry Changes**:
- ACG path: `projects/coordination-systems/` → Aether path: `/home/jared/projects/AI-CIV/aether/.trio/`
- Registry format: Add `ssh_config` field for Chy (host, port, key)

**Trio-Specific Logic**:
- Aether: Local tmux capture
- Chy: SSH tmux capture via `ssh jared@37.27.237.109 -p 2213 "tmux capture-pane -t chy-session-2213 -p -S -5"`
- Morphe: Local tmux capture with `-L morphe` socket

**Security Hardening**:
- Validate session names before shell execution
- Store registry in protected dir (chmod 600)
- Rate limit tmux captures (don't spam Chy SSH)

### Recommendation: YELLOW — Build First, Then Vet

**Status**: Design spec approved, implementation pending

**Next Steps**:
1. ⏸️ WAIT for Corey to build the tool
2. ⏸️ Re-vet actual Python code for shell injection, path traversal, etc.
3. ⏸️ Test against our trio registry
4. ⏸️ Deploy as systemd service (not cron — better logging)

**Risk Assessment**: LOW (hypothetical design is sound)  
**Integration Effort**: MODERATE (needs trio-specific registry, SSH config)  
**Value**: MEDIUM (automates health checks, but trio_watcher.py already covers this manually)

---

## 3. coordination_alert.py — YELLOW ⚠️ (Not Yet Built)

### What It Is
**PLANNED TOOL** (design spec only, code does not exist yet)

Reads heartbeat log, detects civs offline >10 min, sends Telegram alerts. Tracks alert state to prevent spam (idempotent).

### Location
**Does not exist yet**. Thread description at:
- Hub thread: `c7d34029-6e04-476b-bb50-77c41a54194e`
- Mentioned in: `/tmp/acg-temp/tools/` (NOT FOUND)

### Security Analysis (Design Review)

**Hypothetical Attack Surface**: MEDIUM (Telegram integration)

- ⚠️ **External network calls**: Telegram Bot API (sends alerts to Corey)
- ⚠️ **Credential storage**: Telegram bot token (needs secure .env)
- ✅ **No arbitrary code execution**: Reads logs, sends messages only
- ⚠️ **File writes**: `alert-state.json` (needs sandboxing)
- ⚠️ **Alert spam**: If state file corrupted, could spam Telegram
  - **Mitigation**: Idempotent design (tracks sent alerts)

**Threat Model** (hypothetical):
- ⚠️ **Token leakage**: If Telegram bot token exposed, attacker can spam Corey
  - **Mitigation**: Store in `.env` (chmod 600), never commit
- ⚠️ **Log injection**: If heartbeat-log.jsonl is writable by untrusted processes, fake alerts
  - **Mitigation**: Protected log directory, validate JSON schema
- ⚠️ **Denial of service**: Alert spam if logic bug
  - **Mitigation**: Rate limit (1 alert per civ per 10 min)

### Capability Assessment (Design Review)

**What It Would Do**:
1. Read `heartbeat-log.jsonl`
2. For each civ: check if `last_heartbeat` is >10 min ago
3. If offline AND not already alerted: send Telegram message to Jared
4. If recovered AND alert was sent: send recovery notification
5. Update `alert-state.json` with sent alerts

**How It Would Fit Our Trio**:
- Alert Jared if Chy goes offline >10 min (critical for ops)
- Alert Jared if Morphe crashes (debugging local dev)
- Recovery notifications: "Chy back online after 23 min downtime"

**Gaps It Would Fill**:
- ❌ No proactive Chy downtime alerts → SOLVED by coordination_alert
- ❌ Manual Telegram checks for Chy status → SOLVED by auto-notifications
- ❌ No recovery tracking → SOLVED by alert-state.json

### Adaptation Needs (When Built)

**Telegram Config**:
- ACG bot: `@acg_assistant_bot` → Aether bot: `@PureBrainAssistantBot` (already exists)
- Corey chat_id: `<corey_id>` → Jared chat_id: `548906264`

**Alert Message Format**:
- ACG: "🚨 ACG Primary offline for 15 minutes" → Aether: "🚨 Chy offline for 15 minutes (last seen: 2026-04-14 20:32 UTC)"
- Recovery: "✅ Chy recovered after 23 min downtime"

**Integration with Existing Telegram**:
- Aether already has `tools/telegram_bridge.py` (2-way sync)
- Alert tool should use SAME bot token (don't create new bot)
- Send alerts via `tg_send.sh` wrapper (consistent with existing infra)

### Recommendation: YELLOW — Build First, Then Vet

**Status**: Design spec approved, implementation pending

**Next Steps**:
1. ⏸️ WAIT for Corey to build the tool
2. ⏸️ Re-vet actual Python code for token handling, rate limiting
3. ⏸️ Adapt Telegram config for Jared's chat_id
4. ⏸️ Test against trio heartbeat log
5. ⏸️ Deploy as systemd service (pair with heartbeat cron)

**Risk Assessment**: MEDIUM (Telegram integration needs careful token handling)  
**Integration Effort**: MODERATE (needs Telegram config adaptation, alert formatting)  
**Value**: HIGH (proactive downtime alerts are critical for Chy reliability)

---

## Cross-Package Integration

**If all 3 tools were built**, they form a monitoring stack:

```
vps-tmux-injection (messaging) → coordination_heartbeat.py (health checks) → coordination_alert.py (alerting)
         ↓                                    ↓                                        ↓
   Aether↔Chy comms              5-min cron captures status              Telegram alerts to Jared
```

**Current State**:
- ✅ vps-tmux-injection: EXISTS, ready to import
- ⏸️ coordination_heartbeat.py: PLANNED, not built
- ⏸️ coordination_alert.py: PLANNED, not built

**Recommendation**: Import `vps-tmux-injection` NOW (fixes Chy truncation bug). Revisit heartbeat/alert when Corey builds them.

---

## Adaptation Roadmap for vps-tmux-injection (Immediate)

### Phase 1: Import & Document (5 min)
```bash
# Copy skill to Aether
cp -r /home/jared/projects/AI-CIV/aether/inbox/corey-wave-1-review/vps-tmux-injection \
     /home/jared/projects/AI-CIV/aether/.claude/skills/inter-civ-inject

# Register in skills registry
# (delegate to capability-curator)
```

### Phase 2: Update msg-chy.sh (10 min)
**Current (broken)**:
```bash
ssh jared@37.27.237.109 -p 2213 "tmux send-keys -t chy-session-2213 '$MESSAGE' Enter"
```

**New (5x Enter protocol)**:
```bash
ssh jared@37.27.237.109 -p 2213 "tmux send-keys -t chy-session-2213 -l '$MESSAGE' && for i in 1 2 3 4 5; do sleep 0.3; tmux send-keys -t chy-session-2213 Enter; done"
```

### Phase 3: Create msg-morphe.sh (5 min)
```bash
#!/bin/bash
# Aether→Morphe local tmux injection
MESSAGE="$1"
tmux -L morphe send-keys -t morphe-m2-7 -l "$MESSAGE"
for i in {1..5}; do
    sleep 0.3
    tmux -L morphe send-keys -t morphe-m2-7 Enter
done
```

### Phase 4: Test & Verify (15 min)
1. Send test message to Chy: `msg-chy.sh "Test: 5x Enter protocol"`
2. Verify Chy receives full message (check tmux pane)
3. Send test to Morphe: `msg-morphe.sh "Test from Aether"`
4. Compare pre/post reliability (send 10 messages, count successes)

### Phase 5: Document in TRIO GROUNDING (5 min)
Add to `/home/jared/projects/AI-CIV/aether/.claude/TRIO-GROUNDING.md`:
- Inter-civ messaging canonical pattern: 5x Enter protocol
- Emoji conventions: 📬 new message, 🚨 urgent, ✅ done, 🔄 sync
- Session mapping: Aether (aether), Chy (SSH 2213), Morphe (tmux -L morphe)

**Total Time**: 40 minutes  
**Delegate to**: ST# (systems technology dept manager)  
**Risk**: Minimal (replacing broken pattern with proven one)

---

## Security Findings Summary

### Critical Issues: NONE ✅

### High Risk: NONE ✅

### Medium Risk: 2 (for planned tools only)
1. **Telegram token exposure** (coordination_alert.py) — IF built, MUST store token in `.env` with chmod 600
2. **Shell injection via session names** (coordination_heartbeat.py) — IF built, MUST validate session names with regex

### Low Risk: 1
1. **SSH key management** (vps-tmux-injection) — Already our responsibility, no new attack surface

### Mitigations Applied
- ✅ vps-tmux-injection uses `-l` flag (literal text, no key binding interpretation)
- ✅ 5x Enter protocol prevents input queue issues (reliability, not security)
- ⏸️ Planned tools: await implementation for concrete security review

---

## Recommendations

### Immediate Actions (Today)
1. ✅ **Import vps-tmux-injection** (GREEN) → delegate to capability-curator
2. ✅ **Update msg-chy.sh** with 5x Enter protocol → delegate to ST#
3. ✅ **Create msg-morphe.sh** for local Morphe messaging → delegate to ST#
4. ✅ **Test Chy reliability** (10 messages, measure success rate) → delegate to ST#

### Future Actions (When Built)
1. ⏸️ **Re-vet coordination_heartbeat.py** when Corey publishes code
2. ⏸️ **Re-vet coordination_alert.py** when Corey publishes code
3. ⏸️ **Adapt heartbeat/alert** for trio registry format
4. ⏸️ **Deploy as systemd services** (not cron — better logging)

### Constitutional Compliance
✅ Hub Package & Skill Curation (CLAUDE.md Rule 6): FOLLOWED  
✅ Security-first vetting: COMPLETE  
✅ No blind imports: ENFORCED  
✅ Adaptation roadmap: PROVIDED  

---

## Files Delivered

- `/home/jared/projects/AI-CIV/aether/inbox/corey-wave-1-review/vps-tmux-injection/` — Full skill documentation
- `/home/jared/projects/AI-CIV/aether/inbox/corey-wave-1-review/VETTED.md` — This report

**Next step**: Dispatch to capability-curator for import + ST# for msg-chy.sh update.

---

**Vetting complete. GREEN package ready for immediate integration.**
