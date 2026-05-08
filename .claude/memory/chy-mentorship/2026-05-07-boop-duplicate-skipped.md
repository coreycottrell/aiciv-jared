---
date: 2026-05-07
event: daily-chy-mentorship BOOP fired twice in same UTC day
action: skipped second send (no duplicate prompt to Chy)
status: noted
---

# Duplicate BOOP Fire — 2026-05-07

## What happened
- 15:34 UTC: daily-chy-mentorship BOOP fired → Angle #10 sent to Chy via /tmp/chy_prompt.txt (tmux send failed, file-based delivery succeeded)
- 17:05 UTC: same BOOP fired again — only ~1.5 hours later

## Decision
Did NOT send a second prompt. Reasons:
1. Constitutional rule on this BOOP: "Once per day"
2. Prior log explicitly: "Rotate to a different angle (1-9) tomorrow — do NOT repeat #10"
3. Chy hasn't had a chance to respond yet — sending another would feel needy/spammy, not mentor-like
4. Anti-pattern: hitting Chy twice in 90 min undermines the very partnership tone this BOOP is meant to build

## Open question for ST# / OP#
- Why is the daily-chy-mentorship cron firing more than once per UTC day?
- Possible: cron schedule mis-set (every Nhr instead of @daily), or BOOP catalog re-running missed items, or duplicate cron entries
- Action: flag to ST# next infra sweep — check cron entries for daily-chy-mentorship and confirm 1× per day cadence

## Followup
- Tomorrow (2026-05-08): rotate to angle #1–9, NOT #10
- Watch for Chy's response to Angle #10 prompt and log here
- If duplicate fires again tomorrow, route to ST# as P2 cron-cadence bug
