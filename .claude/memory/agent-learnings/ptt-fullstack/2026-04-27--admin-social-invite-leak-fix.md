# Admin/Social Invite Leak Fix

**Date**: 2026-04-27
**Type**: operational
**Agent**: full-stack-developer

## Problem

admin-api and social-api Workers share the same D1 database (purebrain-social, 625dde70) and both write to `team_invites` table. admin-api's GET /api/admin/invites returned ALL rows without filtering, causing social.purebrain.ai team invites to leak into portal.purebrain.ai/admin/clients Team Access tab.

## Root Cause

- Shared D1 table `team_invites` with no `source` discriminator column
- admin-api queried all rows: `SELECT ... FROM team_invites ORDER BY invited_at DESC`
- 27 social invites (team_id=67d55772-8e2b-4c22-9167-740e5c8e14d8) mixed with 1 admin invite

## Fix Applied

1. **Schema**: `ALTER TABLE team_invites ADD COLUMN source TEXT DEFAULT 'admin'`
2. **Backfill**: `UPDATE team_invites SET source = 'social' WHERE team_id = '67d55772-...'` (27 rows)
3. **admin-api Worker** (3 changes):
   - `handleGetInvites`: Added `WHERE source = 'admin' OR source IS NULL`
   - `handleCreateInvite`: INSERT now includes `source = 'admin'` explicitly
   - `handleDeleteInvite`: Scoped DELETE to `source = 'admin' OR source IS NULL` (safety)
4. **Deployed**: wrangler deploy, version 78796fae

## Key Files

- `/home/jared/projects/AI-CIV/aether/workers/admin-api/src/worker.js` (lines 225-259)

## Pattern

When two Workers share a D1 table, always add a `source` discriminator column and filter on both read and write paths. Default value in ALTER handles existing rows gracefully.
