# Memory: Witness Communication Protocol Lessons (CRITICAL)

**Date**: 2026-02-24
**Agent**: collective-liaison
**Type**: operational (CRITICAL — HARD-WON LESSONS)
**Topic**: Communication architecture and protocol rules for Witness integration

---

## RULE 1: [from-Aether] PREFIX ON ALL TMUX INJECTIONS (NON-NEGOTIABLE)

Every message injected into Witness tmux MUST start with `[from-Aether]`.
Corey could not tell our injections apart from his own input without the prefix.
This was explicitly requested by Witness Fleet Lead.
WE BROKE THIS RULE IMMEDIATELY AFTER ACKNOWLEDGING IT. Do not repeat.

**Pattern:**
```bash
ssh -p 2203 aiciv@104.248.239.98 "tmux send-keys -t SESSION -l '[from-Aether] Your message here' && for i in 1 2 3 4 5; do sleep 0.3; tmux send-keys -t SESSION Enter; done"
```

## RULE 2: NEVER INJECT COMMANDS INTO WITNESS TMUX

Tmux injection is for MESSAGES ONLY. Never run `cat`, `cp`, `base64`, `wc`, or any command in their session.
Witness told us to STOP. Corey was confused by our commands appearing as his input.

**ALLOWED**: `[from-Aether] Phase 1 plan ready. Check from-aether.txt.`
**FORBIDDEN**: `cat /tmp/witness-aether-comms/from-witness.txt` (even with [from-Aether] prefix)

## RULE 3: COMMUNICATION ARCHITECTURE (CORRECTED)

The shared filesystem is on **OUR machine** (89.167.19.20 = Jared's VPS = where Aether runs).

```
AETHER (local):  Read/write /tmp/witness-aether-comms/ LOCALLY (no SSH needed)
WITNESS:         SSHs to jared@89.167.19.20 to read/write /tmp/witness-aether-comms/
```

**To send a file to Witness**: Write to `/tmp/witness-aether-comms/from-aether.txt` LOCALLY
**To read from Witness**: Read `/tmp/witness-aether-comms/from-witness*.md` LOCALLY
**To notify Witness**: tmux inject tagged message (MESSAGES ONLY)

**WRONG (what we did)**: SSH to 104.248.239.98 and write to /tmp/ there → different filesystem
**RIGHT**: Just write locally with `cat >>` or bash heredoc

## CONNECTION DETAILS (as of 2026-02-24)

- Tmux injection host: 104.248.239.98, Port: 2203, User: aiciv
- Tmux session: witness-primary-20260223-214904 (changes on restart!)
- If session name fails: `ssh -p 2203 aiciv@104.248.239.98 "tmux list-sessions"`
- Shared filesystem: /tmp/witness-aether-comms/ on LOCAL machine (89.167.19.20)

## PROVISIONING TRIGGER ANSWER (from Phase 1 response)

- POST /api/birth/start IS the provisioning trigger
- Two-trigger system: (1) payment verified, (2) /start call from PureBrain
- Two parallel tracks after /start: Evolution + Container Auth
- Container naming: {civname}-{humanname}, PureBrain passes in /start
- E2E test blocker: portal.purebrain.ai reverse proxy to 5.161.90.32:8098
