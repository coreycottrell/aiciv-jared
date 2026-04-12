# Incident: Joy Container — claude doctor Stuck + Portal LOG_ROOT Mismatch

**Date**: 2026-03-23
**Customer**: Joy (Linda Rosanio)
**Container**: 37.27.237.109 port 2243, user aiciv
**Agent**: client-tech-support-team

---

## Issues Found and Fixed

### Issue 1: claude doctor stuck (PID 3897359)

**Root cause**: Joy's Claude Code session ran `claude doctor` in response to a user message, but `claude doctor` cannot execute inside an existing Claude Code session (returns exit code 144). Claude then retried with `env -u CLAUDECODE claude doctor` which also hung, spawning a new subprocess that ran for 33+ minutes.

**Fix**:
- Killed the stuck subprocess: `kill 3897359`
- Claude spawned a second one (3905944) immediately — killed that too
- Sent Escape + C-c to the joy-primary tmux pane to interrupt Claude's current task
- Sent instruction via tmux: "The claude doctor command does not work inside an existing Claude session. Please ignore the auto-update warning — it is cosmetic only. You are running fine."
- Claude acknowledged and stood down from retrying.

**Prevention**: Do NOT send "claude doctor" as a portal message to a Claude Code session. It cannot run inside an existing session. The auto-update warning at the bottom of the Claude Code UI is cosmetic only.

---

### Issue 2: Claude session recovery

After killing the stuck process and interrupting, Claude was at the prompt awaiting instruction. Sent the corrective message via tmux and Claude confirmed it was operational. No restart needed.

---

### Issue 3: Portal message bridge not showing Claude responses

**Root cause**: `portal_server.py` derives `LOG_ROOT` by encoding `Path.home()` (-> `-home-aiciv`). But Claude was launched from `/home/aiciv/civ` as its project directory, so it writes JSONL to `-home-aiciv-civ`. The portal was reading from the stale `-home-aiciv` directory (files 4448 minutes old) and returning 0 messages.

**Evidence**:
- `/home/aiciv/.claude/projects/-home-aiciv/` — 5 files, all 74 hours old
- `/home/aiciv/.claude/projects/-home-aiciv-civ/` — 1 file (active session), updated every few minutes
- `history.jsonl` confirmed all sessions use `project: /home/aiciv/civ`

**Fix**: Patched `portal_server.py` around line 52-57 to dynamically find the active LOG_ROOT by scanning all subdirectories in `.claude/projects/` and selecting the one with the most recently modified JSONL file. Falls back to the home-encoded path if none found.

**Portal restarted** via tmux Ctrl+C + restart command. New process PID 3907207.

---

## Verification

- `curl http://localhost:8097/health` -> `{"status":"ok","civ":"joy","uptime":132}`
- `/api/chat/history?n=200` -> 100 messages returned (conversation history present)
- Test message sent via portal: `[CTS-support-test] ... please reply with: BRIDGE OK`
- Claude received message in tmux pane and responded: `BRIDGE OK`
- No claude doctor subprocesses running post-fix
- Portal server running as PID 3907207

---

## Important Notes for Future Incidents

1. `claude doctor` inside Claude Code session always fails with exit code 144. Never send this as a portal message. The auto-update warning at the bottom of Claude Code UI is cosmetic.

2. LOG_ROOT mismatch will happen any time Claude is launched from a non-home project directory (e.g. `/home/aiciv/civ`). The fix in `portal_server.py` makes this self-healing going forward.

3. The fix needs to be applied to the canonical `portal_server.py` in the main codebase so future fleet deployments inherit it. Route to dept-systems-technology: `ST# Fix portal_server.py LOG_ROOT to dynamically scan active JSONL directory`.

4. `/api/context` endpoint returns token usage (context window %). Chat messages endpoint is `/api/chat/history`. Do not confuse them in diagnostics.

---

## Time to Resolution

~45 minutes (diagnosis + fix + verification)

---

## Escalation Needed

The `portal_server.py` LOG_ROOT fix should be propagated to the main codebase. This is a systemic issue that will affect any fleet container where Claude is launched from a subdirectory.
