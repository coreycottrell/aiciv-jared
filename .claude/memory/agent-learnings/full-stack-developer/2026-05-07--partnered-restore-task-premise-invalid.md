# Partnered Restore Task — Premise Invalid

**Date**: 2026-05-07
**Type**: gotcha / operational
**Tag**: ptt, cf-pages, git-archaeology, false-premise

## Context

Aether delegated Phase 1 restore-and-redeploy of `exports/cf-pages-deploy/partnered/index.html`. Stated theory: Aether's `git reset --hard` at 2026-05-07 15:33:18 UTC reverted the file to an older committed state, causing the live `/partnered/` page to serve a stale bundle missing 2026-04-01 spec compliance markers (`window.payTestData` global, no `fireSeedAddendum`, `window.onPaymentComplete` redirect).

## What I Found

**The premise was false.** Investigation:

1. Full git history for the file shows only TWO commits ever:
   - `fbe3fc1` (2026-04-12 13:29 UTC) — initial creation in "Mega upgrade"
   - `557f307` (2026-05-07 16:29 UTC) — today's referral-v1 wiring (AFTER the 15:33 reset)

2. The reflog 15:33:18 entry was `reset: moving to HEAD` — a no-op self-reset.

3. Both committed versions AND working tree have IDENTICAL marker counts:
   - `payTestData`: 1 (in a CHANGELOG COMMENT only — not a definition)
   - `fireSeedAddendum`: 4 (function def + 3 click handlers — the legacy code spec §16 says to remove)
   - `onPaymentComplete`: 4 (defined per spec §6)

4. Sibling `/awakened/index.html` has identical bug.

5. Live production page has same marker counts as local working tree.

**Conclusion**: The file has been in this buggy state since 2026-04-12. It was never updated to comply with the 2026-04-01 onboarding spec. The bug Sheila hit is not from a regression — it's from work never being done.

## Decision

Halted per the task's own constraint: *"If pre-reset SHA isn't findable, STOP and flag — don't fabricate."*

Did NOT modify the working tree. Did NOT deploy. Did NOT commit. Wrote receipt at `exports/portal-files/phase1-partnered-restore-redeploy-2026-05-07.md` flagging NEED-MORE-INVESTIGATION.

## Lesson

When a "restore" task is sent down, verify the premise BEFORE running `git checkout <sha>`. The first investigation step should always be: enumerate ALL commits touching the file, AND check the reflog around the alleged regression timestamp. If the file has only one or two commits in its lifetime, restoration is likely not the right operation.

A "restore" task that would actually be a fresh build from spec must be re-routed through SPEC → CTO REVIEW → BUILD per the constitutional engineering flow. Restoring to a buggy version under the label "restore" would silently lock in the bug under a deceptive commit message.

## Files

- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/partnered/index.html` (untouched)
- `/home/jared/projects/AI-CIV/aether/exports/portal-files/phase1-partnered-restore-redeploy-2026-05-07.md` (receipt)

## Verification Commands That Mattered

```bash
git log --all --format="%H %ai %ci %s" -- exports/cf-pages-deploy/partnered/index.html
git reflog --date=iso | head -30
git show <sha>:exports/cf-pages-deploy/partnered/index.html | grep -cE 'fireSeedAddendum'
```
