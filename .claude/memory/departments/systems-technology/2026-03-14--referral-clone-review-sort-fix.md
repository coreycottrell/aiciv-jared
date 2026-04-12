# Referral Program Homepage Clone Review — Sort Bug Fix
**Date**: 2026-03-14
**Agent**: dept-systems-technology
**Type**: bug-fix + review

---

## Task
Full review of referral program section in homepage clone deployed at:
- Clone URL: https://purebrain.ai/referral-program-clone/
- File: exports/cf-pages-deploy/referral-program-clone/index.html (14,385 lines)

## Bug Found and Fixed

### Leaderboard Sort Fallback Chain Mismatch

**Location**: Line 9863–9869 (the `entries.sort()` function)

**The Problem**:
- The **sort** function used `a.referral_count` as the first fallback field
- The **display count** function (line 9878) used `entry.completed` as the first fallback field
- Since the API returns `completed` (not `referral_count`), the sort was reading 0 for every entry
- Result: leaderboard would display correct counts but rank everyone at 0, so sort order would be arbitrary

**The Fix**:
```js
// Before
var aCount = parseInt(a.referral_count || a.count || a.referrals || 0, 10);
var bCount = parseInt(b.referral_count || b.count || b.referrals || 0, 10);

// After
var aCount = parseInt(a.completed || a.referral_count || a.count || a.referrals || 0, 10);
var bCount = parseInt(b.completed || b.referral_count || b.count || b.referrals || 0, 10);
```

**Rule**: Sort fallback chain MUST always match display fallback chain exactly.

## Everything Else Passed Review

- **CTA links**: Both `https://purebrain.ai/refer/` links correct (step 1 body text + main CTA button)
- **API endpoint**: `https://app.purebrain.ai/api/referral/leaderboard` — correct
- **Commission math**: Awakened $9.85, Partnered $28.95, Unified $54.45 — all exact 5%
- **Leaderboard display count** (line 9878): `entry.completed` first — correct and matches API
- **Loading skeleton**: 5 shimmer rows shown while fetch runs — good UX
- **Error fallback**: "Leaderboard loading… Check back soon!" on fetch failure — correct
- **Name masking**: `maskName()` function protects user privacy — working
- **Canonical tag**: Points to `/referral-program/` — correct SEO (clone defers to real page)
- **Recurring note**: "Recurring monthly — you earn as long as they stay" — present and styled

## Deployment
- Deployed to CF Pages (purebrain-staging)
- CF cache purged for https://purebrain.ai/referral-program-clone/ using global API key
- Deploy URL: https://5d5bc78a.purebrain-staging.pages.dev

## Pattern: Sort/Display Fallback Parity Rule
When a JS object renders data AND sorts by data using a fallback chain,
both the sort and the render MUST use identical fallback chains.
Any mismatch = displayed values and rank order will disagree.
