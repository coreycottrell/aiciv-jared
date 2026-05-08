# Admin Clients Dashboard Full Rebuild

**Date**: 2026-04-21
**Type**: operational
**Agent**: full-stack-developer

## What Was Built

Complete admin clients dashboard at `/home/jared/purebrain-site/admin/clients/index.html` (721 lines). Single HTML file, no external deps except Google Fonts Inter.

## Architecture

- Auth: POST `/api/login` with email/password, token in localStorage as `pb_admin_token`
- Data: GET `/api/admin/clients` (with optional `?show_hidden=1`)
- Updates: PATCH `/api/admin/clients/{id}` for individual and bulk edits
- All API calls use Bearer token auth with auto-redirect to login on 401/403

## Key Features

1. Login gate with email/password
2. Stats bar (total, active, onboarding, churned, revenue, MRR)
3. Client table with sorting (click column headers), filtering (search + tier/status/payment dropdowns)
4. Hide/unhide clients (X/check buttons, hidden rows at 40% opacity)
5. Expandable detail panel per row with editable fields + save
6. Bulk actions (select all, bulk set status/tier)
7. CSV export
8. Mobile responsive

## Critical Constraints Followed

- `esc()` function exact match per spec (XSS safety)
- Zero escaped quotes (`\"`) in the entire file
- Token key = `pb_admin_token` (not `pb_admin_session` from prior iteration)
- Brand colors: bg #080a12, blue #2a93c1, orange #f1420b
- Tier chips: insiders=blue, awakened=green, partnered=orange, unified=gold
- Branch: `admin-rebuild` on purebrain-site repo
