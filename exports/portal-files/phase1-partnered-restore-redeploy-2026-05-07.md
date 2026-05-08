# Phase 1: /partnered/ Restore + Redeploy — INVESTIGATION HALT

**Date**: 2026-05-07
**Agent**: PTT Full-Stack Developer (delegated by Aether)
**Status**: NEED-MORE-INVESTIGATION (restore halted — premise invalid)
**Greenlit by**: Jared (CEO)

---

## TL;DR

**The task's premise is false.** Aether's `git reset --hard` at 2026-05-07 15:33:18 UTC did NOT revert `exports/cf-pages-deploy/partnered/index.html` to an older state. The file has been in the same buggy state — `fireSeedAddendum` legacy code present, `window.payTestData` only mentioned in a removal comment — since it was first created on 2026-04-12. **No "good" pre-reset version exists in git history to restore from.**

Halting per task constraint: *"If pre-reset SHA isn't findable, STOP and flag — don't fabricate."*

---

## Pre-Reset SHA Search

Full commit history for `exports/cf-pages-deploy/partnered/index.html` (all branches):

| SHA | Committer Date (UTC) | Message |
|-----|----------------------|---------|
| `557f307` | 2026-05-07 16:29:43 | B3(referral-v1): wire 4 payment pages to POST pb_ref at PayPal onApprove |
| `23224bb` / `fbe3fc1` | 2026-04-12 13:29:01 | Mega upgrade: CEO Overview landing... (file creation) |

Only TWO commits ever touched this file. The last commit BEFORE 2026-05-07 15:33 UTC reset was `fbe3fc1` (2026-04-12) — the file's INITIAL CREATION.

The 16:29 commit (`557f307`) is AFTER the 15:33 reset (it's part of today's `referral-v1` work). It cannot be the "pre-reset" version.

## Reflog Reality Check

```
11443b5 HEAD@{2026-05-07 15:33:18}: reset: moving to HEAD       ← no-op self-reset
11443b5 HEAD@{2026-05-07 15:33:35}: reset: moving to 11443b5
95499ee HEAD@{2026-05-07 15:32:08}: reset: moving to origin/main
```

The 15:33:18 reset was a "moving to HEAD" — a no-op. The actual destructive-looking reset was 15:32:08 `moving to origin/main` on `referral-v1` branch. Neither could have removed a newer-than-2026-04-12 version of `partnered/index.html` because no such version existed in any commit, stash, or reflog entry pre-15:32.

## Marker Counts Across Versions

```
                          payTestData   fireSeedAddendum   onPaymentComplete
fbe3fc1 (2026-04-12):           1                4                  4
557f307 (2026-05-07 16:29):     1                4                  4
working tree (now):             1                4                  4
purebrain.ai/partnered/ live:   1                4                  4
awakened/index.html (sibling):  1                4                  4
```

The single `window.payTestData` reference is at line 5632 — a **CHANGELOG COMMENT** stating "MED-003: window.payTestData and window.logPayTestData **removed** from global exports". It is NOT a definition. So `window.payTestData` is genuinely undefined per the global-exposure expectation in the task spec.

`fireSeedAddendum` is present at lines 7554, 7926, 8057, 8150 — actual function definition + 3 click handlers. This is the legacy code spec §16 mandates removed.

`onPaymentComplete` IS defined at line 5415 (`if (typeof window.onPaymentComplete === 'function')`). Spec §6 redirect handler appears wired.

## Comparison with awakened/index.html

`awakened/index.html` has IDENTICAL marker counts. It is a sibling page with the same bundle and the same bug. It is NOT a canonical "good" reference — it has the same issues.

## Live vs. Local

```
Live  https://purebrain.ai/partnered/  : 8284 lines  md5 bca159c7d3cac47048cf767a865648c2
Local exports/cf-pages-deploy/...      : 8310 lines  md5 b9bf2fa7c8e26f4208776a533c1885d2
```

Live and local DIFFER in content (26-line drift, MD5 mismatch) but have IDENTICAL spec-compliance marker counts. Both are equally non-compliant with the 2026-04-01 spec.

## Why I Did Not Restore

Restoring to `fbe3fc1` (2026-04-12) would NOT fix the bug — that version has the same `fireSeedAddendum` legacy code. Restoring to `557f307` (today's `referral-v1`) would also be no-op — it has the same code. There is no version to restore TO that satisfies the task's stated criteria.

Fabricating a "restoration" by hand-editing the file to match the spec would be a NEW build, not a restore — and per the CTO-pre-build-architectural-review rule (constitutional), it requires the SPEC → CTO REVIEW → BUILD gate, not a Phase 1 restore receipt.

## Real Diagnosis

The /partnered/ page **was never updated to comply with the 2026-04-01 onboarding spec**. The bug Sheila hit is not from a `git reset` regression — it is from work that was never done. The page was created on 2026-04-12 with `fireSeedAddendum` legacy code and never modernized.

This is a **build task**, not a **restore task**.

## Recommendation

Route to ST# (Systems-Technology) for a proper SPEC → CTO REVIEW → BUILD cycle:
1. Compare `partnered/index.html` against spec `NEW-ONBOARDING-FLOW-SPEC-2026-04-01.md` clause-by-clause
2. Apply same canonical bundle to the 4 sibling payment pages (`/awakened/`, `/unified/`, `/insiders/`, homepage) since they all share the bug
3. Deploy via `CF_PAGES_PROJECT=purebrain-production python3 tools/cf-deploy.py exports/cf-pages-deploy/`

## Files Referenced

- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/partnered/index.html` (8310 lines, working tree, branch `referral-v1`)
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/awakened/index.html` (sibling, same bug)
- `/home/jared/projects/AI-CIV/aether/exports/portal-files/NEW-ONBOARDING-FLOW-SPEC-2026-04-01.md` (canonical spec)
- `/home/jared/projects/AI-CIV/aether/exports/portal-files/partnered-live-e2e-test-2026-05-07.md` (E2E test that flagged the bug)

## Status

**NEED-MORE-INVESTIGATION** — Phase 1 restore is structurally impossible because the bug predates the reset. Working tree was NOT modified. Nothing was deployed. No commit was made.
