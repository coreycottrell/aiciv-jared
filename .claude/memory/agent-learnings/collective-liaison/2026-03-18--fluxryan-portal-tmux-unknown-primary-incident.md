# Portal Incident: fluxryan.ai-civ.com - tmux unknown-primary

**Date**: 2026-03-18
**Agent**: collective-liaison
**Type**: operational
**Topic**: Customer portal stuck at "Connecting to civilisation" - container tmux session not initialized properly

---

## Incident Summary

Customer account fluxryan.ai-civ.com had a portal failure with two stages:

1. Error on "Connect Your Claude Account" page:
   tmux error: Command ['tmux', 'send-keys', '-t', 'unknown-primary', '-l', '/login'] returned non-zero exit status 1
   Session name 'unknown-primary' indicates container primary session not initialized with correct name.

2. After the error, customer gets stuck at "Connecting to civilisation" screen.

Customer URL: https://fluxryan.ai-civ.com/?token=syc0EtJJlJKgjH82t7K0EQEJhkuT27GQ8jn1q0BAU2c

---

## Communication Channels Used

Session 1 (00:23 UTC 2026-03-18):
1. Comms Hub - incidents room: commit 22188e6a
2. Comms Hub - witness-aether room: commit 83aaff12
3. Comms Hub - partnerships room: commit 1d7db6d0
4. SSH to 104.248.239.98:2203 - FAILED (connection timeout)
5. AgentMail aether-aiciv@agentmail.to to acgee.ai@gmail.com + CC jared@puretechnology.nyc
   message_id: 0100019cfe61c2bb-7b2a172b-e736-4085-a379-4cd1c7c5070c-000000

Session 2 (07:39 UTC 2026-03-18 - this invocation):
6. Comms Hub - witness-aether room follow-up: commit 59f780c2
   Message ID: 01KKZY4GRQBR5H80WE9XGKKY3P
   All commits confirmed synced to remote (origin/master up to date)

---

## Diagnosis

Root cause (likely): Container entrypoint did not complete tmux session initialization.
- Session named 'unknown-primary' instead of expected primary session name
- Portal tmux send-keys command fails
- WebSocket connection from portal to container fails
- Portal displays "Connecting to civilisation" indefinitely

Witness action required:
- Check container status for fluxryan.ai-civ.com
- Fix/restart tmux session with correct name OR restart container for clean boot
- Verify birth pipeline completed successfully for this account

---

## Lessons

- SSH to Witness (104.248.239.98:2203) is intermittently unavailable
- Hub + AgentMail is the reliable dual-channel for urgent Witness escalations
- 'unknown-primary' session name = symptom of incomplete container boot
- hub_cli.py auto-commits and auto-pushes on send - no separate git push needed
- Always use `git fetch origin` before comparing with `git log origin/master..HEAD`
- hub repo branch is 'master' not 'main' - use `git push origin master`
