# CO# Memory: Department Activation and Tech Team Restructure

**Date**: 2026-03-18
**Type**: governance decision + org structure
**Topic**: Jared directed departments to be ACTIVE and tech teams to be restructured

## What Was Decided

1. Three tech teams formalized: WTT (Witness), PTT (PureBrain site), CTS (Client Support)
2. Each team gets its own full-stack developer and QA engineer (wtt-fullstack, wtt-qa, ptt-fullstack, ptt-qa, cts-fullstack, cts-qa)
3. Security-auditor is now a mandatory gate on all portal code changes — code cannot ship without PASS
4. Performance-optimizer runs post-deploy on every PTT deployment
5. CF Pages deploy is automated via `tools/auto-deploy-cf-pages.sh`
6. Department usage tracking is now required — each dept manager writes to usage-log.md
7. Knowledge compounding system documented — agents write learnings, dept managers synthesize weekly, shared registry accumulates cross-team patterns

## Files Created

- `/home/jared/projects/AI-CIV/aether/.claude/DEPARTMENT-ACTIVATION-PROTOCOL.md` — the full protocol
- `/home/jared/projects/AI-CIV/aether/.claude/TECH-TEAM-ROSTER.md` — team structure and routing
- `/home/jared/projects/AI-CIV/aether/tools/auto-deploy-cf-pages.sh` — auto-deploy script (chmod +x done)
- `/home/jared/projects/AI-CIV/aether/exports/departments/systems-technology/knowledge/SHARED-KNOWLEDGE-REGISTRY.md` — knowledge compounding registry

## Key Pattern

Jared's core insight: separate developers per team compounds correctly. Each developer's memory deepens in one domain rather than spreading thin across three. By month 3, WTT developer has 90 days of birth pipeline pattern memory. That is what Jared means by compounding.

## Open Items for Jared

- CF_ZONE_ID needs to be added to .env if cache flush automation is wanted (currently the script skips cache flush if zone ID is missing)
- Agent manifests for wtt-fullstack, wtt-qa, ptt-fullstack, ptt-qa, cts-fullstack, cts-qa should be created in `.claude/agents/` — this was designed but not yet built (need ST# to execute)
- Git post-commit hook install is optional — can be installed with the one-liner in the protocol doc
