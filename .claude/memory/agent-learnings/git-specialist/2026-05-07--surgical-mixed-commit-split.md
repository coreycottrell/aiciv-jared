# Git Memory: Surgical Mixed Commit Split (Reset + Selective Re-Add)

**Date**: 2026-05-07  
**Type**: Teaching  
**Topic**: Splitting mixed commits surgically to remove non-scope files

---

## Context

Branch `referral-v1` had 3 commits ahead of main:
- `62d3fc9` (cherry-picked from `107019b`) — **MIXED**: 11 referral files + 132 non-referral files (gift pages, blog audio, brainiac training)
- `85fe7fc` (cherry-picked from `b98235f`) — Pure referral admin staging fix
- `f6c52d4` — Pure D1 migrations for referral system

**Problem**: Gift pages are constitutionally frozen (`feedback_investor_gift_pages_frozen_constitutional.md`) and should never be touched in feature branches. Mixed commit violated scope.

**Goal**: Remove 132 non-referral files while preserving 11 referral files + pure commits.

---

## Approach: Reset + Selective Re-Add

### Step 1: Soft Reset to Base
```bash
git checkout referral-v1
git reset --soft origin/main
```
- Uncommits all 3 commits
- Keeps changes staged
- Working dir unchanged

### Step 2: Unstage Everything
```bash
git restore --staged .
```
- All changes now unstaged
- Working dir still has files
- Clean slate for selective staging

### Step 3: Selectively Stage Only Scope Files
```bash
git add exports/cf-pages-deploy/admin/partners/index.html \
        exports/cf-pages-deploy/admin/referrals/index.html \
        exports/cf-pages-deploy/admin/referrals-unified/index.html \
        exports/cf-pages-deploy/assets/certified-partner-badge.svg \
        exports/cf-pages-deploy/assets/partner-email-template.txt \
        exports/cf-pages-deploy/assets/partner-linkedin-talking-points.txt \
        exports/cf-pages-deploy/assets/partner-one-pager.pdf \
        exports/cf-pages-deploy/assets/partner-social-graphics.zip \
        exports/cf-pages-deploy/assets/referral-cookie.js
```
- Only 9 referral files staged
- 132 non-referral files left unstaged

### Step 4: Commit Scope Portion
```bash
git commit -m "feat: Add referral admin + partner CF Pages content (split from 107019b)

Referral system frontend pages:
- admin/partners/ — partner management interface
- admin/referrals/ — referral tracking interface  
- admin/referrals-unified/ — unified referral dashboard
- assets/referral-cookie.js — client-side referral tracking
- assets/partner-* — partner onboarding materials

This is the referral portion extracted from the large mixed commit 107019b.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

### Step 5: Stash Working Dir Noise
```bash
git stash push -u -m "Working dir noise during referral-v1 cleanup"
```
- Clean working dir for cherry-pick
- Can drop later (stash not needed)

### Step 6: Cherry-Pick Pure Commits
```bash
git cherry-pick b98235f  # Will be empty/skip — fixes already in recovered files
git cherry-pick --skip
git cherry-pick f6c52d4  # Clean apply
```

---

## Results

**Before**: 145 files, 49,035 insertions  
**After**: 11 files, 5,024 insertions

**Dropped**:
- 15 gift pages (constitutional)
- 45 blog audio files
- 22 purebrain-book pages
- 15 user-guide pages
- 12 headshots
- 6 brainiac modules
- Multiple customer/prospect pages

**Kept**:
- 9 referral admin pages + assets
- 2 D1 migration files
- All functionality intact

---

## Key Learnings

1. **Reset + Selective Re-Add > Interactive Rebase** for large mixed commits
   - Faster (no conflict resolution per file)
   - Clearer (explicit git add for each kept file)
   - Safer (can verify staging before commit)

2. **Soft Reset Preserves Staging** — use to uncommit without losing changes

3. **Unstage All Then Re-Add** — `git restore --staged .` gives clean slate

4. **Cherry-Pick May Be Empty** — if file recovered already has later fixes applied, cherry-pick detects as empty (skip or --allow-empty)

5. **Stash Working Dir Noise** — unrelated changes can block cherry-pick (stash, then drop)

6. **Verify Zero Non-Scope** — `git diff --name-only | grep "pattern" | wc -l` confirms clean split

---

## When to Use This Pattern

**Use Reset + Selective Re-Add when:**
- Mixed commit has MANY files (50+)
- Only small subset belongs in scope (10-20%)
- Clear file path patterns (admin/referrals/*, assets/referral-*)
- Constitutional boundary violations (gift pages, frozen assets)

**Use Interactive Rebase when:**
- Few files (5-10)
- Unclear path patterns
- Need to edit commit messages
- Multiple commits to reorder

---

## Alternative: Filter-Repo

For permanent history rewrite:
```bash
git filter-repo --path exports/cf-pages-deploy/admin/partners/ \
                --path exports/cf-pages-deploy/admin/referrals/ \
                --path exports/cf-pages-deploy/assets/referral-cookie.js \
                --force
```

**NOT used here** because:
- Branch not yet pushed to origin
- Reset + re-add cleaner for unpushed work
- Filter-repo for pushed branches with bad history

---

## Memory Tag

`#git-surgery` `#mixed-commit` `#selective-staging` `#constitutional-boundary`
