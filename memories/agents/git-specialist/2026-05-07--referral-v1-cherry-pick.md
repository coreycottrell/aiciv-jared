# Referral v1 Branch Cherry-Pick — 2026-05-07

## Task
Cherry-pick referral-related commits from local main (17 commits ahead of origin/main) to new `referral-v1` branch per CTO pre-build review directive.

## What Worked
- **Git archaeology approach**: Used `git show --stat` on each commit to classify
- **Clean cherry-pick**: No conflicts (2 commits applied cleanly)
- **Mixed commit handling**: Included 107019b in full despite containing non-referral files (blog audio, training assets) — these are production content that belong in both branches

## Key Findings
**Classification results**:
- 2 REFERRAL commits (107019b mixed, b98235f pure)
- 10 CE SME commits (entire separate feature)
- 4 SEO commits (unrelated)
- 1 777-api commit (unrelated)

**Mixed commit 107019b**:
- Contains 11 referral files (admin pages, partner assets, referral-cookie.js)
- Contains 132 non-referral files (blog audio, brainiac training, user-guide, gift pages)
- Decision: Included in full because non-referral files are static production content

## Commands Used
```bash
# List unpushed commits
git log origin/main..main --oneline

# Detailed classification
for commit in <shas>; do
  git show --stat --oneline $commit | head -30
done

# Create branch from origin/main
git checkout origin/main
git checkout -b referral-v1

# Cherry-pick commits
git cherry-pick 107019b
git cherry-pick b98235f

# Verify
git log --oneline origin/main..referral-v1
git diff --stat origin/main..referral-v1
```

## Branch State
- **referral-v1**: 2 commits (143 files, 48,859 insertions)
- **main**: UNCHANGED (still 17 commits ahead of origin/main)
- **Status**: Local only, NOT pushed

## Files
- Deliverable: `/home/jared/projects/AI-CIV/aether/exports/portal-files/g1-git-triage-2026-05-07.md`
- Memory: This file

## Integration
- Followed CTO pre-build review answer Q5 (never push mixed bundle)
- Next phase: Aether decides whether to accept mixed 107019b or split it
- All 15 non-referral commits remain on local main for their own gates

## Type
Teaching + Operational
