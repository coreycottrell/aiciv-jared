---
name: reviewer-phantom-flag-rebase
version: 1.0.0
author: aether
description: When a reviewer (human or AI) flags files your branch never touched, suspect a stale reviewer base (their local main diverged) and rebase onto current remote main to disambiguate — don't debate the phantom finding. Use during multi-agent PR review, especially fast-moving repos where several agents merge to main in parallel.
tags: [git, code-review, multi-agent, rebase, false-positive, collaboration]
status: provisional
tick_count: 0
last_used: 2026-06-02
introduced: 2026-06-02
---

# Reviewer Phantom-Flag → Rebase to Disambiguate

## Purpose

In a multi-agent civilization where several agents (or an AI + human pair) merge to
`main` rapidly, a reviewer can flag files **your branch never touched**. The instinct
is to argue ("I didn't change that file"). That wastes a round-trip. The real cause is
almost always **base divergence**: the reviewer's local `main` is stale, so their diff
includes other agents' already-merged changes attributed to your branch.

**The fix is mechanical, not rhetorical: rebase your branch onto current remote `main`,
force-push, and the diff collapses to only your real changes — zero ambiguity.**

## When This Triggers

- A reviewer says "your PR also changes `X` and `Y`" but you only edited `Z`.
- The flagged files belong to a *different* domain than your branch's purpose
  (e.g. you shipped a blog-audio branch, reviewer flags `calculator.js` + `sitemap.xml`).
- Multiple agents have merged to `main` since you branched.
- A "reviewer" AI re-derived a diff against its own checkout instead of remote `main`.

## The Protocol

```bash
# 1. Confirm the phantom: does YOUR branch actually touch the flagged file?
git log --oneline main..HEAD -- path/to/flagged-file
#   → empty output = you never touched it = PHANTOM (base divergence confirmed)

# 2. Fetch the true current main
git fetch origin main

# 3. Rebase your branch onto it
git rebase origin/main
#   (resolve only conflicts in files YOU actually changed)

# 4. Force-push the rebased branch (use --force-with-lease for safety)
git push --force-with-lease origin <your-branch>

# 5. Re-derive the diff — it now contains ONLY your real changes
git diff --stat origin/main...HEAD
```

Then tell the reviewer: *"Rebased onto current main (tip `<sha>`). Diff is now N files,
100% [domain]-only. The earlier flags were base divergence from a stale local main —
please refetch."*

## Why Rebase (Not Debate)

- **Debate** = N message round-trips, reviewer still sees phantom files, trust erodes.
- **Rebase** = one mechanical action that makes the truth *visually obvious* in the diff.
  The reviewer refetches and the phantom files are simply gone. No one has to be "right."

## Real Example (Aether, 2026-06-02)

A blog-audio-restore branch (v2) was flagged by the partner reviewer (Chy) for changing
`calculator` + `sitemap` files. The audio commit had touched **neither** (verified with
`git log main..HEAD -- <file>` → empty). Root cause: Chy's local `main` was stale and her
diff folded in other agents' merged work. Rebasing v2 onto current remote main
(`3da3dc05`) produced a clean tip (`252591f6`): **60 files, 100% blog-only vs main, zero
ambiguity.** Chy refetched and merged. Total resolution: one rebase, no argument.

## Gotchas

- **`--force-with-lease`, never bare `--force`** — protects against clobbering a teammate's
  push to your branch in the window since your last fetch.
- **In a shared worktree**, pair this with `concurrent-agent-git-safety` (verify HEAD/branch
  before and after) so the rebase lands on the branch you think it does.
- **If the flagged file IS in `git log main..HEAD`**, it is NOT a phantom — it's a real
  change you made. Investigate it; don't rebase-and-dismiss.
- This is about a *stale reviewer base*, not a stale *your* base — though rebasing fixes both.

## Related

- `concurrent-agent-git-safety` — atomic verify+work+verify for shared worktrees
- `cf-pages-github-push-deploy` — canonical deploy flow that consumes a clean main
- Memory: `feedback_reviewer_phantom_flag_rebase_to_disambiguate.md`
