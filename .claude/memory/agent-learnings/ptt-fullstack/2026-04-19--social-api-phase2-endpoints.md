# social-api Phase 2: 3 Backend Endpoints

**Date**: 2026-04-19
**Type**: operational
**Agent**: full-stack-developer

## What Was Built

3 backend endpoints added to `workers/social-api/src/worker.js`:

### 1. POST /api/analytics/best-times
- Queries up to 500 posted items, groups by platform+dow+hour
- Scores by avg engagement (if performance_metrics exists) or post count proxy
- Returns top 5 slots per platform

### 2. POST /api/content/bulk
- Accepts JSON array of posts (max 200)
- Inserts all as status=draft with generated_by=bulk_import
- Returns count + IDs, partial failure reporting per-item
- social_account_id required (D1 NOT NULL constraint)

### 3. PATCH /api/users/:id/role
- New roles: admin, editor, reviewer, viewer (alongside legacy owner/leader/member/system)
- ROLE_PERMISSIONS const + hasPermission() function added near top of file
- Permission enforcement on handleCreateContent, handleUpdateContent, handleBulkUpload
- Reviewer can only change status/rejection_reason on content (approve/reject)
- Safety: can't change own role, can't touch owner role

## Key Gotchas
- users table has NO `updated_at` column -- don't include it in UPDATE statements
- social_account_id is NOT NULL in content_items -- bulk upload must require it or validate
- Route ordering: exact path match (`===`) means `/api/content/bulk` won't collide with `/api/content`
- Reviewer ownership check: needed to expand the `canEditOthers` list to include reviewer role

## File
- `/home/jared/projects/AI-CIV/aether/workers/social-api/src/worker.js`
- Deployed to: `https://social-api.in0v8.workers.dev` / `https://social.purebrain.ai`
