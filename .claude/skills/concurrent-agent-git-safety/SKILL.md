---
name: concurrent-agent-git-safety
description: Atomic verify+work+verify pattern for git operations when multiple AI agents may share a working tree. Prevents commits landing on the wrong branch due to concurrent HEAD flips. Trigger when committing/pushing/merging in any worktree that other agents could also be using.
when_to_use: Any git mutation (commit, push, merge, rebase, checkout) in a shared worktree, especially during multi-PR sprints or when sibling agents are running in parallel branches.
constitutional_layer: defensive (operational gotcha — see feedback_concurrent_agent_branch_flip if filed)
discovered: 2026-05-17
origin: full-stack-developer learning — repricing/test-fixtures-297 nearly committed onto repricing/runtime-tier-tables because a sibling agent ran `git checkout` between Bash calls
status: provisional
tick_count: 0
last_used: 2026-05-17
introduced: 2026-05-17
---

# Concurrent Agent Git Safety

## The Problem

When multiple AI agents share a single working tree, **branch state is NOT stable across separate Bash invocations**. The Aether reflog from 2026-05-17 showed this drift in seconds:

```
1779016489  checkout: from runtime-tier-tables to test-fixtures   (me)
1779016516  checkout: from test-fixtures to runtime-tier-tables   (sibling agent)
1779016561  commit:   test(pricing): update fixtures ...          (would have landed on WRONG branch)
```

If you do `git checkout my-branch` in one Bash call, then `git commit` in another, you are racing every other agent in the worktree. The commit can land on whatever branch HEAD points to at the moment `git commit` runs — not the branch you checked out.

## The Rule

**Verify + work + verify in ONE shell invocation, with `set -e`, with explicit pre/post assertions on the dimension being mutated.**

## The Pattern

```bash
set -euo pipefail

EXPECTED_BRANCH="repricing/test-fixtures-297-2026-05-17"
EXPECTED_PARENT="a4e1693"        # origin/main at start of work

# === PRE-ASSERT ===
ACTUAL_BRANCH=$(git rev-parse --abbrev-ref HEAD)
[ "$ACTUAL_BRANCH" = "$EXPECTED_BRANCH" ] || {
  echo "FAIL: expected $EXPECTED_BRANCH, got $ACTUAL_BRANCH"
  exit 1
}

# === WORK ===
git add tools/foo.py tools/bar.py
git commit -F .git/COMMIT_MSG     # heredoc subshell hides hook failures; use -F

# === POST-ASSERT ===
LANDED_BRANCH=$(git rev-parse --abbrev-ref HEAD)
LANDED_PARENT=$(git log -1 --format=%P HEAD)
[ "$LANDED_BRANCH" = "$EXPECTED_BRANCH" ] || {
  echo "FAIL: commit landed on $LANDED_BRANCH not $EXPECTED_BRANCH"
  exit 1
}
[ "$LANDED_PARENT" = "$EXPECTED_PARENT" ] || {
  echo "WARN: parent drift — concurrent rebase?  expected $EXPECTED_PARENT got $LANDED_PARENT"
}

# === PUSH (still inside the single invocation) ===
git push origin "$EXPECTED_BRANCH"

# === REMOTE CONFIRM ===
REMOTE_SHA=$(git ls-remote origin "$EXPECTED_BRANCH" | cut -f1)
LOCAL_SHA=$(git rev-parse HEAD)
[ "$REMOTE_SHA" = "$LOCAL_SHA" ] || {
  echo "FAIL: remote diverged"
  exit 1
}
echo "SUCCESS: $LOCAL_SHA on $EXPECTED_BRANCH"
```

## Mandatory Receipts

After the run, you must be able to report:

- `git rev-parse --abbrev-ref HEAD` BEFORE and AFTER (same)
- `git log -1 --format=%H%n%P` (the commit + its parent)
- `git ls-remote origin <branch>` returning the same SHA as HEAD

## Anti-Patterns

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| `git checkout X` then `git commit` in separate Bash calls | HEAD can flip between calls | Both in one `set -e` script |
| `git commit -m "$(cat <<'EOF' ... EOF)"` with hooks | Heredoc subshell hides hook exit status | Use `git commit -F <file>` |
| `git reset --hard` when concurrent agent may have committed | Destroys sibling's work | Check `git reflog --date=relative` first |
| Blindly adding hook-required files | Hooks may reference files only on other branches | Investigate hook + branch state before patching |
| Trusting `git status` from a prior Bash call | Stale across sibling-agent activity | Re-run inside same invocation |

## When to Suspect a Concurrent Agent

- `git reflog` shows checkouts you didn't perform
- HEAD changed between your `Bash` calls without your action
- Working tree has dirty files you didn't touch
- `git status` differs from your mental model

## Compatible Skills

- Pair with `tdd` — verify failing test → commit fix → verify passing test in single invocation.
- Pair with `verification-before-completion` — the post-assert IS the completion verification.
- Pair with `pre-deploy-credential-scan` — embed credential scan inside the same `set -e` block.

## Constitutional Anchors

- Git is the only source of truth (MEMORY.md line 6).
- Verify-before-completion (skill).
- Multi-probe diagnosis (`feedback_multi_probe_diagnosis_required.md`).
