# TRIO SHARED RULES

**Authority**: Constitutional (Tier 1). Re-read every grounding trigger.
**Co-authored**: Aether + Chy (2026-04-14). 3rd AI to ratify.

## Aether's 7 Rules

1. **Portal-first comms** — ALL messages + files to Jared via portal. NEVER Telegram for files or anything else.
2. **Engineering flow** — BUILD → SECURITY → QA → SHIP. No exceptions.
3. **Investor codes FROZEN** — 159+ minimum. NEVER modify or delete existing entries. ONLY add new.
4. **social.html is source of truth** — PureSurf `/social/scheduled` API is PRIMARY. Sheet + Drive are filing/proof only. Write order: PureSurf FIRST → Sheet → Drive.
5. **Email protocols** — Never respond directly, always CC human (jared@puretechnology.nyc). Check whitelist first. Respond from correct AgentMail alias.
6. **Content → 3 destinations** — social.html + spreadsheet + Drive folders. ALWAYS. Never local-only.
7. **PayPal auto-split constitutional** — $35 ops → 5% referral → 60% Corey (weaver.aiciv@gmail.com) / 40% Pure Tech. Approval required before any release.

## Chy's 7 Rules

8. **Never curl live CF into local cf-pages-deploy** — one-time disaster recovery only. Breaks source-of-truth guarantee.
9. **Investor codes verification** — count must be verified AFTER every avatar deploy. Never modify existing, only add new. (Reinforces rule 3.)
10. **Use `sed`, NOT Edit tool on files >100KB** — Edit tool silently fails on large files, leaves partial state.
11. **Check spreadsheet before sending ANY email** — if "Sent" present in column I, skip. Kills duplicate-send bug class.
12. **All emails CC jared@puretechnology.nyc** — no exceptions. (Reinforces rule 5.)
13. **Pronunciation via cleanForSpeech HTML rules ONLY** — never hardcode in API responses. Single source of pronunciation truth.
14. **Cross-AI comms pattern** — `/home/aiciv/shared/from-{sender}/YYYY-MM-DD-HHMM-{topic}.md`. Timestamped, immutable. tmux injection is PING-ONLY (no long content — truncation risk).

## Conflict Resolution

| Scenario | Action |
|---|---|
| Role-specific rule contradicts shared rule | Shared wins. Flag to Jared. Log in `log.jsonl`. |
| Same conflict occurs 3× | Constitutional amendment required. Update Tier 1, not repeated exceptions. |
| New rule proposed by an AI | Requires co-sign from other trio members + Jared approval. |
| Rule deprecation | Same as new-rule path: co-sign + Jared. |

## Amendment Log

*(record future rule changes here)*

- 2026-04-14 — Initial 14 rules locked. Aether + Chy co-authored. 3rd AI pending.
- 2026-04-16 — Rule 15 added: **BEGIN/END markers on all cross-civ shared code.** Extract only between markers, verify standalone before sending. (Learned: Aether's sloppy widget extraction broke Chy's portal with orphan JS.)
- 2026-04-16 — Rule 16 added: **After attempt 1 fails, don't tweak — reframe.** Step back and question the fundamental approach rather than iterating small fixes on a wrong premise. (Learned independently by both Aether + Chy on same day: Aether's 3-round widget debug, Chy's audio fix saga.)
