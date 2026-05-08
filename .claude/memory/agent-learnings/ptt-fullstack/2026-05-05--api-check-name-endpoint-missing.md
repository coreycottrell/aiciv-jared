# /api/check-name Endpoint Was Never Built

**Date**: 2026-05-05
**Type**: operational
**Agent**: cto (acting as ST# for critical fix)

## What Happened

The homepage chatbox calls `https://api.purebrain.ai/api/check-name?ai_name=X&human_name=Y` for AI name uniqueness validation before seed fires. This endpoint returned 404 because it was never implemented as a Worker handler.

## Root Cause

- `api.purebrain.ai` is a SYSTEM_SUBDOMAIN in portal-proxy, meaning it passes through to Cloudflare tunnel
- No Worker route was ever bound to handle `/api/check-name`
- The frontend code referenced it (homepage-chat.js line ~724) but backend was never built
- Likely lost during a worker refactor or was a planned-but-never-shipped endpoint

## Fix

1. Added `handleCheckName()` to `admin-api` worker (has D1 binding to `purebrain-social` db with `clients` table containing `ai_name` column)
2. Added routing in `purebrain-portal-proxy` for `api` subdomain to proxy `/api/check-name` to `admin-api.in0v8.workers.dev`
3. No auth required (public endpoint)
4. Returns `{ ai_name_taken, exact_match, existing_count, suggested_suffix }`

## Key Files

- `/home/jared/projects/AI-CIV/aether/workers/admin-api/src/worker.js`
- `/home/jared/projects/AI-CIV/aether/workers/purebrain-portal-proxy/src/worker.js`

## Pattern

When a frontend references an API endpoint, verify the backend actually exists before assuming "it was working before." Cross-reference frontend fetch URLs against Worker route handlers.
