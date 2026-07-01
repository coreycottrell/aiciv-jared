---
name: engineering-flow-boop
description: MANDATORY 30-minute check that enforces BUILD -> SECURITY -> QA -> SHIP pipeline for ALL code and deployment work. Conductor must verify no in-flight work bypasses the pipeline.
status: provisional
tick_count: 0
last_used: 2026-04-12
introduced: 2026-04-12
---

# Engineering Flow BOOP

**Type**: Mandatory Recurring Check
**Frequency**: Every 30 minutes during active sessions
**Applies to**: ALL code and deployment work without exception
**Owner**: the-conductor (enforces), full-stack-developer + security-engineer-tech + qa-engineer (execute)

---

## The Pipeline (Non-Negotiable)

Every piece of code or deployment work MUST follow this exact sequence:

```
BUILD (full-stack-developer)
  |
  v
SECURITY REVIEW (security-engineer-tech) <-- BEFORE deploy
  |
  v
DEPLOY
  |
  v
QA TEST (qa-engineer) <-- AFTER deploy
  |
  v
REPORT TO JARED
```

**No step may be skipped. No step may be reordered.**

---

## What Triggers the Pipeline

The following work types ALWAYS require the full pipeline:

- Plugin deployments (any version bump to WordPress plugins)
- Page changes (Elementor edits, HTML updates, _elementor_data modifications)
- CSS fixes (Additional CSS, inline styles, stylesheet changes)
- JavaScript changes (frontend scripts, chat logic, payment flows)
- PHP changes (plugin code, functions.php, custom endpoints)
- Database schema changes
- API endpoint additions or modifications
- Authentication or security configuration changes
- Any user-facing change (if a user could see or experience it, it goes through the pipeline)

---

## The 30-Minute BOOP Checklist

Run this check every 30 minutes. Answer each question honestly.

### Check 1: Active Work Inventory

List everything currently in-flight:
- What is full-stack-developer building right now?
- What deployments are pending or recently completed?
- What CSS or page changes were made in the last 30 minutes?

### Check 2: Pipeline Compliance Verification

For each item in the inventory above:

```
ITEM: [describe the work]
BUILD complete: Yes / No / In progress
SECURITY REVIEW complete: Yes / No / Not yet run
DEPLOYED: Yes / No
QA TESTED: Yes / No / Not yet run
Reported to Jared: Yes / No / Waiting on QA
```

### Check 3: Violation Detection

Ask explicitly: "Is anything currently being built or deployed without going through the full pipeline?"

Red flags that indicate a violation:
- Deployed directly after build without security review
- Security review skipped because "it's just CSS"
- QA not run because "it looked fine in dev"
- Reported to Jared before QA completed
- Fast-patching a live issue without review

### Check 4: Blocked Work

Is any work blocked mid-pipeline? If so:
- What step is it blocked at?
- What does it need to proceed?
- Is Jared waiting on this? If urgent, communicate the block.

---

## Agent Invocation Reference

### Step 1: BUILD

Invoke full-stack-developer with the build specification.

```
Task(full-stack-developer):
  Build [description of feature/fix]
  Context: [relevant files, URLs, constraints]
  Output: [what deliverable is expected]
  Do NOT deploy - hand off to security-engineer-tech for review first
```

Wait for build completion and code artifact before proceeding.

### Step 2: SECURITY REVIEW

Invoke security-engineer-tech with the build output.

```
Task(security-engineer-tech):
  Review the following code BEFORE it is deployed to production:
  [paste or reference the code from full-stack-developer]

  Check for:
  - SQL injection, XSS, CSRF vulnerabilities
  - Authentication bypasses
  - Data exposure risks
  - Insecure dependencies
  - Hardcoded credentials

  Output: APPROVED or REJECTED with specific issues listed
  Do NOT deploy if rejected. Return to full-stack-developer with issues.
```

Only proceed to deploy if security review returns APPROVED.

### Step 3: DEPLOY

Conduct the deployment using the reviewed and approved code. Document the deployment:
- What was deployed
- To which environment (purebrain.ai, jareddsanborn.com, etc.)
- Timestamp
- Method used (plugin upload, REST API, Playwright, etc.)

### Step 4: QA TEST

Invoke qa-engineer with the post-deployment verification task.

```
Task(qa-engineer):
  Test the following deployment that just went live:
  Site: [URL]
  Change: [what was deployed]

  Verify:
  - The intended change is visible and functional
  - No regressions on adjacent features
  - Mobile and desktop views (if UI change)
  - No console errors

  Output: PASSED or FAILED with specific observations
```

Only report to Jared after QA returns PASSED.

### Step 5: REPORT TO JARED

After QA passes, send a complete summary via Telegram:
- What was built
- Security review result
- Deployment confirmation
- QA test result
- Any notes or follow-up items

---

## Violation Response Protocol

If a pipeline violation is discovered during the 30-minute check:

1. **Stop the work immediately** if it is mid-stream
2. **Identify what step was skipped**
3. **Run the skipped step retroactively** (security review on already-deployed code is still better than none)
4. **Document the violation** so the pattern is not repeated
5. **Do not hide the violation from Jared** - report it in the next summary

---

## Why This Pipeline Exists

From Jared's directive (2026-02-20):

"Less patches = catch issues upstream, not downstream."

The pipeline catches security vulnerabilities before they reach users. It catches functional regressions before Jared or customers see them. It creates a documented trail of every change. The engineering team should collaborate like a real engineering team - build, review, test, ship.

Skipping steps feels faster in the moment. It is slower in total because of the patches, rollbacks, and damage control that follow.

---

## Integration with Delegation Rule

This pipeline enforces the conductor-of-conductors pattern:

- The conductor does NOT build
- The conductor does NOT run security reviews
- The conductor does NOT run QA
- The conductor DELEGATES to the right specialist at each step and ENFORCES the sequence

If you find yourself writing code or running security checks directly, stop. Invoke the appropriate agent.

---

## Back-Half Verify Gate Alarm (ship:qa ratio)

The pipeline silently skips its BACK half (BUILD fires; QA/verify does not). Enforce a hard ratio check every cycle:

- Count `ptt-fullstack` (or any `*-fullstack`) SHIP events in the last 24h.
- Count paired `ptt-qa` + `operations-analyst` VERIFY receipts in the same 24h.
- **ALARM + BLOCK new "done" claims** when `ship_count > 2 * verify_count`. A ship has no verify receipt unless a QA pass OR an operations-analyst live-GET-probe receipt exists for that exact deploy.
- On alarm: dispatch `operations-analyst` to produce a ship↔qa↔live matrix THIS cycle; do not mark the engineering flow healthy until the ratio is back under 2:1 or the gap is explained (e.g. counting artifact: submodule double-count, bundled commits, staging-vs-apex).

> History: 2026-06-18 nightly flagged 12:1; 06-19 operations-analyst audit overturned it as a counting artifact (real ~4:2, nothing customer-live unverified). The alarm is still correct policy — it forced the audit that produced the truth.

## BUILD-Leg Receipt Gate (deploy/restart gate — the absorbed leg)

The SECURITY and QA legs get delegated; the **BUILD leg is the one absorbed inline** (or built in a sibling session and recorded only as a scratch-pad line). This is the leg that relapses — repeatedly, on the SAME money-path/seed file. A scratch-pad "routed to ST#" / "sibling session built it" line is **NOT** proof the pipeline ran.

**Gate (hard):** No `>50`-line money-path or seed/constitutional commit is "deploy-ready" — and **no daemon may be restarted to make it live** — until a **NAMED receipt artifact exists in `inbox/` tied to the commit hash**: a `security-engineer-tech` review + a `ptt-qa` (or `integration-auditor`) pass, each naming the exact commit. If the receipt is absent, the commit is STAGED-only (branch persistence), never SHIP.

- Seed/locked-format commits additionally require a **byte-identical-when-absent** verification receipt on the normal path before restart.
- Enforce at the restart/deploy boundary, not just at "done" — the relapse slips through because the branch push looks like progress. Push ≠ ship; restart = activation.

> History: 2026-06-30/07-01 nightly self-analysis CONFIRMED cross-BOOP that ~1,838 insertions across 4 money-path/seed commits (`dd13ff6` on the FROZEN seed daemon, `e128a28`, `d7029a1`, `e5bfcd7`) landed with ZERO build-specialist receipts in inbox while SECURITY (NO-GO on d7029a1) + QA (8/8 catch) legs WERE delegated. The 06-30 routing action plateaued within 19h on the same file — codifying the gate here (not a memory note) is the durable fix. See memory `feedback_build_leg_absorbed_receipt_as_gate.md`.

## Related Skills

- `verification-before-completion` - Never claim a step done without showing the evidence
- `memory-first-protocol` - Search for past deployment patterns before starting
- `delegation-spine` - Conductor delegates, specialists execute

---

**Last Updated**: 2026-07-01 (BUILD-leg receipt gate added)
**Created by**: agent-architect (on behalf of Jared's directive)
