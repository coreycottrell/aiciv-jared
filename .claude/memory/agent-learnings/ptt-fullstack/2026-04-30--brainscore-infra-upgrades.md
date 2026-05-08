# BrainScore Infrastructure Upgrades

**Date**: 2026-04-30
**Type**: operational
**Agent**: full-stack-developer

## What Was Built

Added 4 features to ara-index Worker (`workers/ara-index/src/worker.js`):

1. **Gap Analysis** in POST /ara/score response — `gap_analysis` object with `website_claims`, `ai_says`, `gaps` fields. Built from A2 semantic signals (brand_terms vs ai_descriptions). No additional API calls.

2. **GET /ara/history/:url** — returns last 10 scans for a brand, with dimension breakdown per scan.

3. **GET /ara/leaderboard** — all brands sorted by total_score DESC, latest scan per brand. Uses subquery for max(scanned_at).

4. **GET /ara/leaderboard/:category** — same as above filtered by industry LIKE '%category%'.

## Also Done

- Added `<link rel="canonical">` + JSON-LD WebApplication schema to `/home/jared/purebrain-site/brainscore/index.html`
- Added BrainScore URL to `/home/jared/purebrain-site/sitemap.xml`

## Key Details

- D1 binding = `DB`, database = `ara-index`
- Worker URL: `https://ara-index.in0v8.workers.dev`
- History endpoint uses URL-encoded brand URL in path
- Leaderboard returns empty for categories if brands don't have `industry` field populated in ara_brands
