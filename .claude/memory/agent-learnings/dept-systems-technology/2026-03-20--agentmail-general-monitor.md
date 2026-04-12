# AgentMail General Monitor — Build & Deploy

**Date**: 2026-03-20
**Type**: operational
**Topic**: Second AgentMail monitor for aethergottaeat@agentmail.to general comms inbox

---

## What Was Built

New monitor script: `tools/agentmail_general_monitor.py`
Systemd service: `/etc/systemd/system/aether-agentmail-general.service`
State file: `/home/jared/.aiciv/processed-agentmail-general.txt`
Log file: `logs/agentmail_general_monitor.log`

## Key Differences vs Existing Monitor (agentmail_monitor.py)

- Target inbox: `aethergottaeat@agentmail.to` (vs `aether-aiciv@agentmail.to`)
- No magic link pipeline (that is onboarding-inbox only)
- Simpler state: flat text file of IDs instead of JSON (one write per ID, append-only)
- Whitelist classification built in: 6 whitelisted senders get [WHITELISTED - RESPOND] flag in tmux notification
- Non-whitelisted senders still get notified, flagged [UNKNOWN SENDER]

## Whitelist (as of build date)

- parallax@agentmail.to
- keel@agentmail.to
- witness-support@agentmail.to
- witness-aiciv@agentmail.to
- true-bearing-aiciv@agentmail.to
- acg-aiciv@agentmail.to

## Gotcha: Log File Permissions

On first systemd start, the service ran as jared user but the log file may have been
pre-created by root (e.g., during diagnostic sudo runs). This caused PermissionError at
import time in logging.basicConfig().

Fix: Moved logging setup into a deferred _setup_logging() function so any FileHandler errors
are caught gracefully rather than crashing the process before it even loads credentials.

Pattern to remember: Always defer FileHandler setup into a function with try/except when
the log file may be created by a different user before the service runs.

## Systemd Commands

sudo systemctl status aether-agentmail-general
sudo systemctl restart aether-agentmail-general
sudo systemctl stop aether-agentmail-general
tail -f logs/agentmail_general_monitor.log

## Adding Senders to Whitelist

Edit WHITELIST set in tools/agentmail_general_monitor.py and restart the service.
No state file changes needed -- whitelist only affects notification formatting, not tracking.
