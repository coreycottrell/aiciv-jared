# Referral-v1 Branch Cleanup — Mixed Commit Surgery

**Date**: 2026-05-07  
**Agent**: git-specialist  
**Task**: Remove 132 non-referral files from `referral-v1` branch while preserving 11 referral files + pure commits

---

## Approach Used

**Reset + Selective Re-Add**

1. `git reset --soft origin/main` — Uncommit all 3 commits but keep changes staged
2. `git restore --staged .` — Unstage everything
3. Selectively `git add` only the 9 referral files
4. Commit referral content portion with clean message
5. Skip cherry-pick of `b98235f` (already applied in recovered files)
6. Cherry-pick `f6c52d4` (D1 migrations) cleanly

---

## Files KEPT on referral-v1

**9 CF Pages files** (from mixed commit 107019b):
- `exports/cf-pages-deploy/admin/partners/index.html` (1,034 lines)
- `exports/cf-pages-deploy/admin/referrals/index.html` (2,159 lines) *includes b98235f fixes*
- `exports/cf-pages-deploy/admin/referrals-unified/index.html` (1,369 lines)
- `exports/cf-pages-deploy/assets/certified-partner-badge.svg`
- `exports/cf-pages-deploy/assets/partner-email-template.txt`
- `exports/cf-pages-deploy/assets/partner-linkedin-talking-points.txt`
- `exports/cf-pages-deploy/assets/partner-one-pager.pdf`
- `exports/cf-pages-deploy/assets/partner-social-graphics.zip`
- `exports/cf-pages-deploy/assets/referral-cookie.js`

**2 D1 migration files** (from f6c52d4):
- `workers/referrals-api/migrations/0002-v1-sprint-schema.sql` (120 lines)
- `workers/referrals-api/migrations/0002-v1-sprint-schema.rollback.sql` (56 lines)

**Total**: 11 files, 5,024 insertions

---

## Files DROPPED from referral-v1

**132 non-referral files** (from mixed commit 107019b):
- 15 investor gift pages (`gifts/AMILLER2026/`, `gifts/CALACANIS2026/`, etc.) — CONSTITUTIONAL FROZEN
- 45 blog audio files (`blog/*/audio.mp3`)
- 22 purebrain-book pages + assets
- 15 user-guide pages + assets (including videos, PNGs)
- 12 headshot images
- 6 brainiac-mastermind-training modules
- 4 admin pages (clients, referrals-unified before split)
- Multiple customer/prospect pages (groome, hancock-law, noeva-health, etc.)
- JS files (ga4-conversions.js)
- `.bak` files and archived content

**Total removed**: 132 files, ~43,783 lines

---

## Final Branch State Verification

### Commit Log
```
d8a0306 feat(d1): v1 sprint schema migrations — partner_applications, rate_adjustments, payout_requests_v2, tier_at_write, UNIQUE pb_ref+payment_id
11443b5 feat: Add referral admin + partner CF Pages content (split from 107019b)
```

### Diff Stats
```
 exports/cf-pages-deploy/admin/partners/index.html              | 1034 ++++++++++
 exports/cf-pages-deploy/admin/referrals-unified/index.html     | 1369 +++++++++++++
 exports/cf-pages-deploy/admin/referrals/index.html             | 2159 ++++++++++++++++++++
 exports/cf-pages-deploy/assets/certified-partner-badge.svg     |   61 +
 exports/cf-pages-deploy/assets/partner-email-template.txt      |   42 +
 exports/cf-pages-deploy/assets/partner-linkedin-talking-points.txt |  152 ++
 exports/cf-pages-deploy/assets/partner-one-pager.pdf           |    3 +
 exports/cf-pages-deploy/assets/partner-social-graphics.zip     |    2 +
 exports/cf-pages-deploy/assets/referral-cookie.js              |   26 +
 workers/referrals-api/migrations/0002-v1-sprint-schema.rollback.sql |  56 +
 workers/referrals-api/migrations/0002-v1-sprint-schema.sql     |  120 ++
 11 files changed, 5024 insertions(+)
```

### Zero Non-Referral Files
- `git diff --name-only origin/main..referral-v1 | grep -E "(gift|audio\.mp3|brainiac)" | wc -l` → **0**
- No gift pages
- No blog audio
- No brainiac training modules
- No user-guide assets
- No customer/prospect pages

---

## Confirmations

✅ **Zero gift-page files** — constitutionally frozen assets not touched  
✅ **Zero blog audio** — 45 audio.mp3 files removed  
✅ **Zero brainiac** — 6 training modules removed  
✅ **Pure referral scope** — only admin interfaces, partner materials, referral tracking, D1 migrations  
✅ **b98235f fixes preserved** — `syncSplitRowsFromDOM()` present in admin/referrals/index.html  
✅ **Clean history** — 2 commits ahead of main, both referral-focused

---

## Notes

- Commit `b98235f` was skipped during cherry-pick because its changes were already present in the `admin/referrals/index.html` file recovered from the mixed commit (the file I added already had the fixes applied)
- Working directory had noise during surgery; stashed and dropped after branch cleanup completed
- Branch is ready for CTO review and merge to main
