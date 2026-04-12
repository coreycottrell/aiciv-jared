# ST# Build: Referral Program Page
**Date**: 2026-03-13
**Type**: pattern

## What Was Built
Cloned the PureBrain homepage and injected a referral program section before the Pure Technology footer.

**Output file**: `exports/cf-pages-deploy/referral-program/index.html`

## Injection Pattern
The homepage (`exports/cf-pages-deploy/index.html`) has a well-commented section structure:
- SECTION 4: Awaken CTA
- SECTION 5: "See Why PureBrain Is Different" CTA
- **SECTION 6: PURE TECHNOLOGY FOOTER** ← injection point (before this)
- SECTION 8: Aether Credit Bar (fixed)

Injection marker used:
```
<!-- ============================================================
     SECTION 6: PURE TECHNOLOGY FOOTER (Logo + Links)
```

Used Python `str.replace(..., 1)` (replace first occurrence only) to inject safely.

## Referral Section Architecture
- **3-step "How It Works"** with blue/orange/gold numbered circles
- **2-column grid**: Commission tiers table (left) + Live Leaderboard (right)
- **Commission tiers**: Awakened $9.85/mo, Partnered $28.95/mo, Unified $54.45/mo
- **Live leaderboard**: Fetches from `https://app.purebrain.ai/api/referral/leaderboard` via JS fetch with 6s timeout, skeleton loading state, graceful error fallback
- **CTA button**: Links to `https://purebrain.ai/refer/`

## Design Patterns Used
- Glass morphism cards: `background: rgba(255,255,255,0.025); backdrop-filter: blur(12px)`
- Brand colors: blue `#2a93c1`, orange `#f1420b`, gold `#c9a227`
- Skeleton shimmer animation for loading state
- Responsive: 2-col → 1-col at 768px breakpoint
- Section separator: horizontal gradient line `#2a93c1 → #f1420b`
- Hover transitions: cards lift with `translateY(-4px)` + glow box-shadow

## Leaderboard JS Notes
- Handles multiple API response shapes: `data[]`, `data.leaderboard[]`, `data.data[]`, `data.results[]`
- Sorts by count descending in case API doesn't pre-sort
- Name masking: "First L." format for privacy
- AbortController timeout (6s) prevents hanging
- Top 8 entries displayed
- Error state shows "Leaderboard loading... Check back soon!" (not an error message)

## Meta Tag Updates for Clone
- `<title>` → "Earn With PureBrain — Referral Partner Program"
- `<meta name="description">` → referral program description
- `<link rel="canonical">` → `https://purebrain.ai/referral-program/`

## File Size
- Original: 691,969 chars (13,767 lines)
- Clone with referral: 709,781 chars (14,384 lines)
- Referral section: ~17,812 chars injected
