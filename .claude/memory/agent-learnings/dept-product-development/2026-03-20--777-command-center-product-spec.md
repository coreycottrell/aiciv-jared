# 777 Command Center — Product Spec Memory

**Date**: 2026-03-20
**Type**: operational
**Topic**: 777 Command Center product scope — personal to business to platform

## Current State (as of 2026-03-20)

- Hosted on Vercel (pure-marketing-groups-projects team)
- 5 pages: index.html, mandala-chart.html, mandala-business.html, exercises.html, thinking-exercises.html
- Data pipeline: Google Sheets manual export to data.json (not live)
- Auth: Client-side password gate only (no real auth)
- AI coaching: Working via Vercel serverless + Claude Haiku
- Mandala: 9x9 grid, localStorage only

## Architecture Decided

- Frontend: React + Vite on CF Pages (migration from Vercel)
- Backend: Cloudflare Workers + D1
- Auth Phase 1: Cloudflare Access + Google OAuth
- Sheets: API v4 service account, 60s Cron Trigger sync
- Storage: D1 for goal state, KV for sessions/cache

## Key Bets

1. Sheets is data SOURCE not replacement
2. CF Pages migration needed before Phase 2
3. Cloudflare Access for Phase 1 = zero code path
4. Mandala drill-down is P0 for Phase 1
5. Live sheet sync highest value unlock

## File Location

exports/departments/product-development/specs/2026-03-20--777-command-center-product-spec.md
