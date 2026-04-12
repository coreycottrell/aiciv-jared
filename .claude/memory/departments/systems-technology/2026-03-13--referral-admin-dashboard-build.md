# Referral Admin Dashboard Build

**Date**: 2026-03-13
**Type**: build
**Status**: complete

## What Was Built

Two HTML dashboard pages + two new API endpoints for the PureBrain referral/affiliate program.

## Files Created

- `/home/jared/purebrain_portal/admin-referrals.html` — Admin dashboard (Jared only)
- `/home/jared/purebrain_portal/affiliate-portal.html` — Affiliate self-service portal

## API Endpoints Added to portal_server.py

- `GET /api/admin/affiliates` — all affiliates with full stats, requires bearer token auth
- `GET /api/admin/payouts` — all payout requests, requires bearer token auth
- `GET /admin/referrals` — serves admin dashboard HTML (no auth on page load, JS prompts for token)
- `GET /affiliate` — serves affiliate portal HTML

## Auth Pattern

Portal uses bearer token auth (file: `.portal-token`, check_auth() function).
Admin HTML pages store token in localStorage after user enters it — no server-side session needed.
Affiliate portal uses referral code as identity (no password — codes are unguessable PB-XXXX format).

## Design Decisions

- No external JS dependencies — vanilla HTML/CSS/JS only
- Dark theme: #080a12 bg, #2a93c1 blue, #f1420b orange (PureBrain brand)
- Admin dashboard: token gate on page load → Overview / Affiliates / Payouts / Leaderboard tabs
- Affiliate portal: lookup by code OR register new → stats + link + payout request
- Token stored in localStorage for admin, referral code stored in localStorage for affiliates
- Auto-refresh every 60s on admin dashboard

## Verification

All endpoints tested locally via curl:
- /api/admin/affiliates returns Jared Sanborn affiliate record
- /api/admin/payouts returns 1 paid payout (test record from 2026-03-06)
- /admin/referrals serves HTML (200)
- /affiliate serves HTML (200)
- No-token request returns {"error":"unauthorized"}
- Python syntax check: PASS
- Portal restart: healthy on port 8097
