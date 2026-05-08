---
date: 2026-05-02
type: collective-health-audit
flow: great-audit (BOOP variant)
auditors: [pattern-detector, integration-auditor, security-auditor]
synthesized-by: health-auditor
---

# Great Audit — BOOP Cycle Findings (2026-05-02)

## Meta-Pattern (pattern-detector)
**"Constitutional Inflation"** — Aether is enforcing coordination invariants through prose rules in agent manifests rather than executable contracts. The 3-week burst (Apr 14 → May 1) of 6 new constitutional rules + 6 new skills (greenlit-execute, independent-pair-verification, cross-boop-convergence-escalation, etc.) all share one shape: prior failures where "agent judgment in the moment" replaced "structural guarantees."

**The tell**: `greenlit-execute` exists specifically to *suspend* `verification-before-completion` and `dept-routing-hook` because they calcified into paralysis. When meta-rules override your rules, they aren't rules — they're hopes.

## Critical Findings

### P0 — Payment data leaked to git (security-auditor)
- `.gitignore:26` covers `logs/*.log` only. `logs/*.jsonl` is NOT covered.
- 5 sensitive operational files currently tracked: `purebrain_payments.jsonl` (61 entries, in 3 commits), `birth_completions.jsonl`, `governance_challenges.jsonl`, `investor_inquiries.jsonl`, `payment_webhook_delivery.jsonl`, `onboarding-session.jsonl`.
- **Action required (needs Jared approval — destructive git ops)**:
  1. Add `logs/*.jsonl` to `.gitignore`
  2. `git rm --cached logs/*.jsonl` for the 5+ tracked files
  3. Decide on history rewrite (BFG / `git filter-repo`) given remote exposure
- **Owner**: ST# (security-engineer-tech) + Jared sign-off

### P0 — CF Pages target binding has zero code enforcement (integration-auditor)
- Apr 15 incident: full day of /refer/ fixes landed only on staging because `cf-deploy.py` defaults to `purebrain-staging`. Customers saw WP fallback.
- Constitutional rule documented in MEMORY.md but never wired into the tool.
- `tools/cf-deploy.py:56` — `DEFAULT_PROJECT_NAME = "purebrain-staging"`. No warning/block when customer-visible paths deploy to non-prod target.
- **Action**: Add prod-target check that fails-closed for customer-facing path patterns (`/`, `/refer/`, `/insiders/`, `/blog/`) unless `purebrain-production` explicit.
- **Owner**: ST# (ptt-fullstack)

### P1 — Wrangler ban not enforced (integration-auditor)
- 3 active shell scripts still execute the banned `wrangler pages deploy`:
  - `tools/auto_deploy_cf_pages.sh:154`
  - `tools/auto-deploy-cf-pages.sh:32`
  - `tools/deploy_headline_fix.sh:46`
- Constitutional rule says wrangler "deletes pages not in local folder" (lost 30hr investor build).
- **Action**: Replace shells with cf-deploy.py calls or add `set -e; echo "BANNED" && exit 1` guard.
- **Owner**: ST#

### P1 — Customer container isolation depends on agent discipline (security-auditor)
- `tools/cts_provision_keys.py` provisions keys to customer containers (intentional, CTS team).
- But: no header-level guard reminding "PROVISION ONLY, NO TMUX INJECTION" referencing the Apr 23 leak incident (trio messages → Thread Mark customer portal).
- `tools/overnight_2026_03_06.sh` — needs review for legacy injection patterns.
- **Action**: Header guards + legacy script audit.
- **Owner**: fleet-security

## Activated (No Action Needed)
- ✅ PayPal auto-split (60/40 hardcoded in tool, approval flow present)
- ✅ Lyra-pmg whitelist (in `tools/agentmail_general_monitor.py:73`)
- ✅ Welcome email AI-name guard (`purebrain_log_server.py:2155-2172`, returns 422 if missing)
- ✅ PayPal idempotency (D1 + in-memory dedup in `workers/paypal-webhook/src/worker.js`)

## Strategic Recommendation (synthesis)
**Stop adding constitutional prose rules until the existing rules have executable enforcement.**

Convert the next 30 days to building `tools/preflight/`:
1. Greenlit-check (dispatch metadata, not vibes)
2. Deploy-target-check (fail-closed for customer URLs)
3. Container-environment-check (block at tool layer)
4. Cross-BOOP convergence detector (auto-escalate on 2nd flag)
5. Verifier ≠ fixer enforcement

Otherwise the May / June rules will need their own override skills by July.

## Status
- 3 P0/P1 items routed to ST# + fleet-security via this report
- 1 P0 (payment data leak) needs Jared approval before action
- Telegram summary sent
