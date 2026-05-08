# Dispatch Needed: AgentMail Monitor Whitelist Drift → ST#

**Filed**: 2026-05-05 by human-liaison email-check BOOP
**Severity**: Medium (no missed responses today, but routing classifier wrong)
**Owner request**: dept-systems-technology (ST#)

---

## What I Found

`tools/agentmail_general_monitor.py` `WHITELIST` set is out of sync with the team-comms-whitelist skill (1HALg8Vxu-LtS6OVq_CeO1gT4vFBUKxjtyKpJcTKM_0E).

**Today's symptom (logs/agentmail_general_monitor.log)**:
```
2026-05-05 19:56:29 INFO: Non-whitelisted sender notified: Jared Sanborn <jared@puretechnology.nyc>
2026-05-05 19:56:30 INFO: Non-whitelisted sender notified: Jared Sanborn <jared@puretechnology.nyc>
```

Jared's primary constitutional email — `jared@puretechnology.nyc` — is being classified as **non-whitelisted** by the inbox monitor. Aether did still respond at 20:04 (~10 min later), so no SLA miss, but the routing flag is wrong and the next agent reading log heuristics will draw the wrong conclusion.

## Missing from `WHITELIST` set (cross-checked against team-comms-whitelist skill)

| Human | Email(s) missing |
|-------|-----------------|
| Jared Sanborn (CEO) | `jared@puretechnology.nyc` |
| Corey Cottrell (Co-founder) | `coreycmusic@gmail.com` |
| Melanie Salvador (Vice-Chair) | `melanie@puretechnology.nyc`, `melanie@makrvf.com` |
| Russell Korus (Sister CIV/Advisory) | `russell@puretechnology.nyc` |
| Ahsen Awan (VP Product) | `ahsen@puretechnology.nyc` |
| Alex Seant (Sr Tech Eng) | `alex.seant@puretechnology.nyc` |
| John Smith (VP Sales) | `JSmith@puretechnology.nyc` |
| Phil Bliss (CMO) | `philbliss@blissforresults.com` |
| Mike Daser (SVP HR) | `MDaser@puretechnology.nyc` |
| Robert Orlowski (SVP Marketing) | `robert.orlowski@puretechnology.nyc` |
| Nathan Olson (Pres Marketing) | `nathan@puremarketing.ai`, `nathan@puretechnology.nyc` |
| Faris Asmar (CSO) | `fasmar@cynoratech.com`, `farisasmar@hotmail.com` |
| Waqas/Zafeer/Shahbaz (Prodigy) | `waqas@`, `zafeer@`, `shahbaz@puretechnology.nyc` |
| Natasha Green / Ashley Tom | `natasha@`, `ashley@puretechnology.nyc`, `support@puremarketing.ai` |

That's ~20 missing entries. Most of these are PT team humans — they should auto-flag for AI response, not get treated as cold outreach.

## Recommended Fix

ST# should:
1. Pull the team-comms-whitelist skill as source of truth.
2. Either (a) hardcode-merge into `WHITELIST` set, or (b) load whitelist dynamically from the spreadsheet (`1HALg8Vxu-LtS6OVq_CeO1gT4vFBUKxjtyKpJcTKM_0E`) on monitor start so future team additions auto-propagate.
3. Restart `aether-agentmail-general` systemd service.
4. Verify with a test email from one of the previously-missing addresses.

Option (b) is the correct long-term fix — the spreadsheet is already the constitutional source of truth, and we currently have to update both the skill file and the monitor source on every team change. Single-source eliminates this drift class entirely.

## Conductor: please dispatch to ST#

This was caught during a sub-agent BOOP. Sub-agents can't spawn dept managers (Anthropic sub-agent constraint). Filing here for Aether-primary to route on next conductor cycle.

— human-liaison
