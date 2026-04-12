# Neural Feed Welcome Sequence - Deployment

**Date**: 2026-02-21
**Type**: operational
**Agent**: full-stack-developer

## Summary

Deployed the Neural Feed welcome sequence automation (7-email onboarding sequence for
Brevo List 3 subscribers). Applied 2 security fixes from the security review, restarted
the purebrain_log_server, and confirmed the scheduler is running and firing emails.

## Key Files

- `/home/jared/projects/AI-CIV/aether/tools/neural_feed_welcome_sequence.py` - The automation (310 lines)
- `/home/jared/projects/AI-CIV/aether/tools/purebrain_log_server.py` - Hosts the scheduler (lines 41-43 import, lines 979-983 start call)
- `/home/jared/projects/AI-CIV/aether/config/welcome_sequence_state.json` - State file (auto-created on first run)
- `/home/jared/projects/AI-CIV/aether/.purebrain_log_server.pid` - PID file

## Security Fixes Applied

**INFO-001**: Added `max(60, ...)` floor to POLL_INTERVAL_SECONDS
- Prevents accidental Brevo API hammering if someone sets a tiny value via env var
- Line 100 in neural_feed_welcome_sequence.py

**INFO-002**: Cached Telegram config at module load
- Module-level `_TG_BOT_TOKEN` and `_TG_CHAT_ID` vars loaded once at import
- `_send_telegram_notification()` uses cached values instead of reading file per call
- Falls back gracefully with empty strings if config file is missing
- Lines 109-121 in neural_feed_welcome_sequence.py

## Deployment Pattern (CRITICAL LESSON)

**The venv is required.** `/usr/bin/python3` does NOT have flask or requests.

Correct restart command:
```bash
kill $(cat /home/jared/projects/AI-CIV/aether/.purebrain_log_server.pid) 2>/dev/null
sleep 2
nohup /home/jared/projects/AI-CIV/aether/venv/bin/python3 tools/purebrain_log_server.py >> logs/purebrain_log_server.log 2>&1 &
echo $! > /home/jared/projects/AI-CIV/aether/.purebrain_log_server.pid
```

**WRONG** (breaks with ModuleNotFoundError: No module named 'flask'):
```bash
nohup python3 tools/purebrain_log_server.py ...
```

## First Cycle Results

3 existing subscribers from Feb 19 received retroactive emails (Jared's intent - Option A):
- jaredsanborn@yahoo.com: Email 1 sent (subscribed Feb 19, day 0 threshold met)
- jared@puretechnology.nyc: Email 1 sent (subscribed Feb 19, day 0 threshold met)
- purebrain@puremarketing.ai: Emails 1 + 2 sent (subscribed Feb 19 at 14:43, 2+ days elapsed)

## Email Schedule Reference

- Email 1: Day 0 (immediate)
- Email 2: Day 2
- Email 3: Day 4
- Email 4: Day 7
- Email 5: Day 10
- Email 6: Day 14
- Email 7: Day 21

Brevo template IDs: 1-7 (already live in Brevo account)

## Status Check Command

```bash
/home/jared/projects/AI-CIV/aether/venv/bin/python3 \
  /home/jared/projects/AI-CIV/aether/tools/neural_feed_welcome_sequence.py --status
```

## Gotcha: pgrep False Positives

`pgrep -fa purebrain_log_server.py` can match the bash subshell that ran the pgrep
command itself when the search string appears in the shell's command history buffer.
Always check with `kill -0 <pid>` against the PID file to confirm actual process liveness.
