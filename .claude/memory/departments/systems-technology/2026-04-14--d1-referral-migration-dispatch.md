# D1 Referral Migration — ST# Dispatch Tracking
**Date**: 2026-04-14
**Type**: operational
**Specialist**: ptt-fullstack (primary), full-stack-developer (fallback)
**Budget**: 3hr hard cutoff

## Context
- Quick-fix landed 20:20 UTC — 4 rows corrected on chy-jared SQLite
- Two SQLite DBs drifted since Apr 6 → D1 is the permanent fix
- Previous PTT agent balked claiming "needs ST# trigger" — this IS the ST# dispatch
- Dept manager has constitutional authority to re-dispatch if specialist punts again

## Artifacts Verified
- Spec: /home/jared/projects/AI-CIV/aether/docs/D1-REFERRAL-MIGRATION-WEEK2.md
- Endpoints: exports/cf-pages-deploy/functions/api/referral/*.js (14 files)
- Schema: exports/cf-pages-deploy/d1-migrations/0001-referral-schema.sql
- Both portal_server.py instances: local + chy-jared@37.27.237.109:2213

## Anti-Punt Rules
1. Specialist executes, doesn't produce another runbook
2. If specialist asks for routing clarification → re-dispatch immediately
3. If specialist reports real technical blocker → escalate to Aether
4. Backup-first, staging-before-prod, rollback-on-regression

## Success Criteria
- D1 endpoints live (un-deprecated)
- Both portal_server.py instances calling D1 Worker via HTTP
- /refer/ + /admin/referrals show identical data
- Both SQLite files chmod 444 (locked, not deleted)
- Zero Jared-view regression during cutover
