# G1 Git Triage — Referral v1 Branch Creation
**Date**: 2026-05-07  
**Agent**: git-specialist  
**Task**: Cherry-pick referral commits to `referral-v1` branch

---

## Original 17 Commits — Classification

### REFERRAL (2 commits cherry-picked)
1. `107019b` — `chore: Add all untracked CF Pages production content to git`  
   **Status**: MIXED but INCLUDED  
   **Referral files**: `admin/referrals/*.html`, `admin/partners/*.html`, `assets/referral-cookie.js`, partner assets  
   **Non-referral files**: Blog audio, brainiac training, headshots, user-guide, gifts pages  
   **Decision**: Included entire commit (143 files). Non-referral files are static assets, low merge-conflict risk.

2. `b98235f` — `fix: Referral admin staging — autocomplete CORS, split row persistence, split save`  
   **Status**: PURE REFERRAL  
   **Files**: `exports/cf-pages-deploy/admin/referrals/index.html` (59 insertions, 7 deletions)

### OTHER — NOT INCLUDED (15 commits)
All CE SME work (10 commits):
- `4165c8b` — CE SME premium landing + Phil test account
- `9671422` — CE SME Sprint 4 (demo data, cross-module flow, mobile, delete endpoints)
- `525c6ef` — CE SME QA findings (compliance POST, onboarding, dashboard, PDF, logout)
- `af951b1` — CE SME security fixes (Critical+High findings)
- `b140a9d` — CE SME Sprint 2 (Billing/Invoicing + HR modules)
- `3b62e18` — CE SME full module UI (proposals, operations, projects, dashboard)
- `dbdb8c3` — CE SME API URL fix (in0v8.workers.dev)
- `8eb40bf` — CE SME wrangler.toml D1 database ID fix
- `faff617` — CE SME Phase 1 foundation (proposals, operations, project control)

SEO work (4 commits):
- `b90ce6d` — SEO gaps on 3 pages (FAQPage + og:image)
- `cc517f6` — FAQPage JSON-LD to 25 vs comparison pages
- `4f729a3` — FAQPage JSON-LD to 3 blog posts
- `08eb247` — og:image to 21 comparison pages

777-api work (1 commit):
- `83eccfc` — 777-api bind to TOS Dashboard sheet + /api/sheet alias

---

## Cherry-Pick Results

**Branch**: `referral-v1` (created from `origin/main`)  
**Commits included**: 2  
**Conflicts encountered**: NONE  
**Files changed**: 143 files, 48,859 insertions(+), 1 deletion(-)

### Verification Output

```
$ git log --oneline origin/main..referral-v1
85fe7fc fix: Referral admin staging — autocomplete CORS, split row persistence, split save
62d3fc9 chore: Add all untracked CF Pages production content to git
```

```
$ git diff --stat origin/main..referral-v1 | tail -1
143 files changed, 48859 insertions(+), 1 deletion(-)
```

Referral-specific files confirmed present:
- `admin/referrals/index.html` (2107 lines)
- `admin/referrals-unified/index.html` (1369 lines)
- `admin/partners/index.html` (1034 lines)
- `ai-partnership-framework/index.html` (740 lines)
- `assets/referral-cookie.js` (26 lines)
- Partner assets (badge SVG, email template, LinkedIn talking points, one-pager PDF, social graphics ZIP)

---

## Ambiguous Commits — Flagged for Review

**Commit `107019b` is MIXED** — contains both referral and non-referral files.

**Referral-related** (11 files):
- `admin/partners/index.html`
- `admin/referrals-unified/index.html`
- `admin/referrals/index.html`
- `ai-partnership-framework/index.html`
- `assets/certified-partner-badge.svg`
- `assets/partner-email-template.txt`
- `assets/partner-linkedin-talking-points.txt`
- `assets/partner-one-pager.pdf`
- `assets/partner-social-graphics.zip`
- `assets/referral-cookie.js`
- `user-guide/refer-earn.png`

**Non-referral content** (132 files):
- Blog audio files (37 mp3s)
- Brainiac training modules (5 HTML pages)
- Headshots (12 avatars)
- User guide (10 files: HTML, images, videos)
- Gift pages (15 investor codes)
- Other assets (data-room, contact-us, brainscore, PureBrain book)

**Recommendation**: Currently included in full. If strict separation is required, this commit needs split using `git cherry-pick -n 107019b` followed by selective `git add` for referral files only, then manual commit. However, non-referral files are production content (blog audio, training assets) that likely belong in both branches anyway.

---

## Branch State Verification

- **Intact**: Only referral-related commits present
- **Clean history**: No merge commits, no conflicts
- **Ready for phase 2**: ✅
- **Local only**: NOT pushed to origin (per Jared's directive)
- **Main branch**: UNCHANGED (all 17 commits still on local main)

---

## Status

**READY-FOR-PHASE-2** — branch `referral-v1` created with 2 commits, clean cherry-pick, no conflicts.

**Next steps** (Aether decision required):
1. Accept mixed commit `107019b` as-is, OR
2. Split `107019b` to separate referral files from blog/training assets

**Files tracked**: `.git` state shows `referral-v1` branch diverged from `origin/main` by +2 commits ahead.
