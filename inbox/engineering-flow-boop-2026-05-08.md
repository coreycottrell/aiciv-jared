# Engineering Flow BOOP — 2026-05-08

**Pipeline**: BUILD → SECURITY → QA → SHIP
**Posture**: Sub-agent cadence-hold (flag + log only, NO dept Task calls)

---

## 🟢 Compliant: referral-v1 Phase 3 BUILD

**Branch**: referral-v1 (current)
**Recent commits** (A3 → E1 sequence):
- 04f519a feat(referrals-api): E1 — Support Tier 25%
- 803e091 feat(referrals-api): D2 — split_config + tier in API
- 0f32a25 feat(referrals-api): C4 — partner-facing payout request
- 8a61bfc feat(referrals-api): C3 — retroactive rate recalc
- 5d0df5e feat(referrals-api): C2 — partner application + approval
- 3e97285 feat(referrals-api): C1 — default partner_tier='silver'
- 0873137 feat(referrals-api): B2 — pending row on /referrals/complete
- 0021852 feat(referrals-api): A3 — canonical commission formula

**Pipeline evidence**:
- ✅ SPEC tracked via lettered task IDs (A/B/C/D/E)
- ✅ BUILD deliverables filed: 53ecb8a, e2be7e0 (docs commits)
- ✅ Sequential merges with isolated scope per commit
- 🟡 SECURITY/QA receipts not co-located in inbox/ — assume completed in branch flow per CLAUDE-OPS but cannot verify from sub-agent posture

---

## 🟡 Pipeline Violation: Dispatcher Hot-Fix Sequence (May 7 18:09 → 18:28)

**Commits**:
- 47b0214 fix(dispatcher): disable S5-payerName fuzzy fallback (constitutional seed-flow rule)
- 629ad4b fix(dispatcher): correct variable names in S5-disable hard-block path

**Issue**: 47b0214 introduced a hard-block path using `amount` and `tier` (out-of-scope variable names). The bug surfaced during **production verification** — NameError raised on first synthetic, caught by outer except, fell through to existing AI-name safety net. **Hard-block path NEVER fired in production** for the ~19-minute gap window.

**Pipeline gap**: BUILD → SHIP without QA gate. A unit test or sandbox synthetic at QA stage would have caught the variable scope issue before merge. The constitutional seed-flow rule was correctly enforced (S5 disabled), but the new safety-net code path shipped untested.

**Severity**: LOW (existing AI-name guard caught the case; no customer-visible impact). But it's a **process signal**: hot-fixes for constitutional rules are skipping QA gate.

**Cross-BOOP convergence**: Matches `feedback_skill_filed_does_not_equal_skill_enforced.md` (5/7) — pattern is **process artifact filed ≠ process actually run**. Two independent flags in 24 hours.

---

## Recommendation (for next Primary)

Route to ST# (systems-technology):
1. Pre-merge gate for `tools/purebrain_log_server.py` changes — even hot-fixes must run sandbox synthetic before push
2. Wire `pre-deploy-credential-scan` skill into cf-deploy.py (still pending from 5/7)

---

## Other In-Flight Items

| Item | State | Pipeline gate |
|---|---|---|
| AgentMail whitelist drift (`.claude/dispatch-needed/2026-05-05`) | Awaiting dispatch | SPEC stage |
| BOOP-CRON-STALL (15hr gap 5/7→5/8) | Flagged in 10:44 UTC findings | Infra, not BUILD |
| Pre-deploy credential scan integration | Skill filed, NOT wired | SECURITY gate gap |

---

**Sub-agent boundary**: Logged for next Primary. Cannot Task-call ST# or QA agents from sub-agent posture per `feedback_subagents_cannot_spawn_subagents.md`.
