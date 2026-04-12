# Chatbox v4.7 — Message Persistence + Birth/Start Retry

**Date**: 2026-02-25 ~16:25 UTC (Session 43)

## What Happened
- Pre-purchase chatbox had API 529 errors — root cause was outdated model string
- Fixed by switching to `claude-sonnet-4-6` and reordering API endpoints
- v4.7 deployed with two key improvements:
  1. **Message box never disappears** — input area stays visible throughout entire flow
  2. **Birth/start retry flow** — if container provisioning times out, chatbox retries gracefully

## Key Technical Details
- Model upgrade: old model ID → `claude-sonnet-4-6` fixed 529 cascade
- Jared live-tested Q1-Q4 flow and confirmed WORKING
- Birth/start fired successfully to Witness server

## Root Cause Pattern
API 529 errors often mask a simple model ID staleness problem. When Anthropic deprecates model strings, the error response is generic (529 overloaded) rather than descriptive. Always check model ID freshness first.
