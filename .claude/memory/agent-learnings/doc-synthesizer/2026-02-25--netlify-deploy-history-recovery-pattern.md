# Netlify Deploy History Recovery Pattern

**Date**: 2026-02-25 (Session 42)
**Context**: Recovering original v2 team dashboard from Netlify

## Pattern
- Netlify keeps full deploy history with preview URLs for every past deployment
- When you need to recover a previous version: use deploy preview URLs, NOT the Netlify API file download
- Deploy preview URLs serve the exact HTML/assets from that specific deploy
- Saved recovery as `team-dashboard-original-v2.html`

## When to Use
- Dashboard/site accidentally overwritten with wrong version
- Need to compare old vs new versions
- Client says "go back to the version from Tuesday"

## Key Learning
- Netlify deploy previews are persistent — they don't expire
- This is faster and more reliable than git archaeology for deployed static sites
- Always note the deploy ID when pushing significant updates (for easy rollback reference)
