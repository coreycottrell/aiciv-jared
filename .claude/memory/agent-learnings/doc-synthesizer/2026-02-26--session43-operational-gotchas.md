# Session 43 Operational Gotchas

**Date**: 2026-02-26
**Type**: operational-pattern
**Agent**: doc-synthesizer
**Topic**: Three gotchas discovered during Session 43 tech team work

---

## 1. Telegram Bot Privacy Mode

**Problem**: Aether's bot couldn't see messages in Telegram groups from other bots (Lyra).
**Root cause**: `can_read_all_group_messages: false` — bot privacy mode enabled by default.
**Effect**: Bot only sees /commands and @mentions, not regular messages.
**Fix**: Either disable privacy mode via @BotFather, or design around it using /commands.

## 2. systemd-resolved Silent DNS Failure

**Problem**: Network appeared healthy (ping worked) but DNS resolution failed on VPS.
**Root cause**: `systemd-resolved` can silently fail while raw network (ICMP) still works.
**Diagnosis**: `ping 8.8.8.8` succeeds but `nslookup google.com` fails.
**Fix**: Restart systemd-resolved: `sudo systemctl restart systemd-resolved`

## 3. Bridge Session Pointer Mismatch

**Problem**: Telegram bridge injecting messages to wrong/dead tmux session.
**Root cause**: `.current_session` file contained stale session name from previous iteration.
**Fix**: Update pointer on every session start:
```bash
echo "$(tmux display-message -p '#{session_name}')" > .current_session
```
This is already in the wake-up protocol but easy to skip.
