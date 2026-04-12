# Incident: Joy (Linda Rosanio) Portal — Claude Blocked at Login Prompt

**Date**: 2026-03-20
**Customer**: Joy (Linda Rosanio)
**Email**: lrosanio@think-traffic.com
**AI CIV Name**: Joy
**Type**: operational | incident-resolved
**Resolution Time**: ~10 minutes

---

## Incident Summary

Joy's PureBrain portal (joy-linda-rosanio.app.purebrain.ai) was reported as not responding.
The portal server itself was alive and returning 200 OK. The issue was that the Claude Code
session in tmux pane joy-primary:0.0 was stuck at a /login confirmation prompt:
"Login successful. Press Enter to continue..."

The login had been re-run at some point (likely automatically or manually), succeeded, but
the Enter keypress needed to dismiss the confirmation screen never came. Claude was alive
as a process but paused at the TUI login confirmation dialog — unable to accept chat input
from the portal WebSocket.

---

## Container Facts

| Field | Value |
|-------|-------|
| SSH Port | 2243 |
| Host | 37.27.237.109 |
| SSH User | aiciv |
| Portal Port | 8097 |
| Host Port Mapping | 8143 → 8097 |
| Container Name | joy-linda-rosanio |
| Claude Auth Email | lrosanio@think-traffic.com |
| Claude Auth Type | claude.ai / Pro |
| Public URL | joy-linda-rosanio.app.purebrain.ai |
| tmux session | joy-primary (2 windows) + portal-server |

---

## Root Cause

Claude Code TUI ran /login (possibly an automated reauth attempt) and showed the
"Login successful. Press Enter to continue..." confirmation dialog. The process was alive
but blocked — it would not accept chat WebSocket input until Enter was pressed.

Portal server was healthy throughout. Health endpoint, /api/status, and WebSocket all
responded. Only Claude input was blocked.

---

## Diagnostic Steps Taken

1. Container confirmed running and healthy via docker ps: Up 7 days (healthy)
2. SSH in via port 2243 — connection worked
3. Processes confirmed: portal_server.py (pid 12755, since Mar14), claude (2 instances)
4. Portal health: {"status":"ok","civ":"joy","uptime":584278} — 200 OK
5. External URL: 200 OK with and without token
6. Claude auth: {"loggedIn": true, "subscriptionType": "pro"} — auth valid
7. tmux capture of joy-primary:0.0 revealed: blocked at /login "Press Enter to continue"
8. tmux capture of joy-primary:1.0: Claude active in different window
9. joy-primary:1.1: bash shell, showed portal injection attempts going to wrong pane

---

## Fix Applied

ssh -p 2243 aiciv@37.27.237.109 "tmux send-keys -t joy-primary:0.0 '' Enter"

Sent Enter keystroke to the blocked pane. Claude session resumed.
/api/status confirmed: {"tmux_alive":true,"claude_running":true}

---

## Verification

- Portal health (external): HTTP 200
- /api/status with token: tmux_alive: true, claude_running: true
- Claude pane joy-primary:0.0: at normal prompt, ready for input

---

## Key Learnings

1. Portal CAN report 200 OK while Claude is functionally blocked. The portal server
   and Claude process are decoupled. Health check does not verify Claude accepts input.

2. The /login TUI has a blocking confirmation screen. "Login successful. Press Enter
   to continue" hangs until dismissed. If this runs unattended, Claude freezes.

3. Always capture tmux panes during diagnosis. Process listing shows Claude is "running"
   but does not reveal it is stuck at a prompt. tmux capture-pane is the diagnostic tool.

4. joy-primary has 2 windows. Window 0 is the main Claude session, window 1 has a second
   Claude instance and a bash shell. The portal routes to window 0, pane 0.

5. joy-primary:1.1 was receiving portal injection attempts when primary pane was blocked.
   The bash shell showed [portal] /login and [portal] Joy are you there? — portal injected
   into the wrong pane. Flag to Witness as a pane routing issue.

---

## Follow-Up Items

1. CTS support keypair not yet provisioned for Joy / port 2243. Add to SSH key registry.
2. Notify Witness: portal pane routing may target wrong pane when primary pane is blocked.
3. Pattern: login-prompt-blocked is a recurring class of issue. Witness should add a
   watchdog that auto-dismisses login confirmations or detects blocked TUI state.

---

## Fleet Map Update (Joy Container)

| Port | CIV Name | Human | Email |
|------|----------|-------|-------|
| 2243 | Joy | Linda Rosanio | lrosanio@think-traffic.com |
