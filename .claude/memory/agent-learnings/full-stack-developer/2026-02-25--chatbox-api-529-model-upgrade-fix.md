# Chatbox Pre-Purchase Claude API 529 Fix

**Date**: 2026-02-25 ~16:00 UTC (Session 43)
**Agent**: full-stack-developer
**Pages Affected**: 688, 689 (purebrain.ai pre-purchase chatbox)

## Problem
- Pre-purchase chatbox returning HTTP 529 errors from Claude API
- Users seeing broken chat experience on first visit

## Root Cause
- Model ID `claude-sonnet-4-20250514` was returning HTTP 529 (overloaded/retired)
- API endpoint ordering had slower/failing endpoint first

## Fix Applied
1. **Model upgraded**: `claude-sonnet-4-20250514` → `claude-sonnet-4-6` (confirmed working)
2. **API endpoints reordered**: Working `pure-brain-dashboard-api.purebrain.workers.dev` moved to first position
3. **Deployed to BOTH pages** 688 and 689 via WP REST API
4. **Verified**: API responds correctly with new model

## Pattern
- When Claude models are retired/overloaded, the API returns 529 not 404 or standard error
- Always use current model IDs (check Anthropic docs): `claude-sonnet-4-6`, `claude-opus-4-6`, `claude-haiku-4-5-20251001`
- Keep multiple API endpoints with fastest/most-reliable first as fallback strategy

## Key Learning
- Model retirement manifests as 529 (overloaded), not a clear deprecation error
- Pre-purchase chatbox is customer-facing — model failures = lost leads
- Deploy to ALL instances of a page (688 AND 689) when fixing
