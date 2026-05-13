-- Migration 0005: Per-AI room tokens for Thread B Phase 1 (Days 6-9)
-- Date: 2026-05-13
-- Source: CTO Decision 1 (cto-thread-b-day-6-9-token-model-2026-05-13.md)
--
-- Scope:
--   - Add ai_tokens table for per-customer-per-AI bearer tokens
--   - Plaintext stored ONLY in HTTP response (one-shot mint), hash-only in D1
--   - Per-tenant rotation without touching 4 legacy fixed tokens
--
-- ADDITIVE: Worker authSender() gets fast-path on the 4 legacy fixed tokens
-- BEFORE this D1 lookup. Latency p99 unchanged for legacy traffic.
--
-- Apply (staging first):
--   cd workers/trio-comms
--   CLOUDFLARE_API_TOKEN=... npx wrangler d1 execute purebrain-referrals \
--     --remote --file migrations/0005-ai-tokens.sql
--
-- Idempotency: CREATE TABLE IF NOT EXISTS — safe to re-run.

CREATE TABLE IF NOT EXISTS ai_tokens (
  token_hash TEXT PRIMARY KEY,              -- sha256(plaintext_token), hex
  customer_id TEXT NOT NULL,                -- soft FK to clients (different D1)
  ai_id TEXT NOT NULL,                      -- e.g. "keen", "vex" (lowercased ai_name slug)
  display_name TEXT NOT NULL,               -- clients.ai_name at mint time
  room_id TEXT NOT NULL,                    -- room this token authorizes posting to
  created_at INTEGER NOT NULL,              -- epoch ms
  last_used_at INTEGER,
  revoked_at INTEGER                        -- soft delete; null = active
);

CREATE INDEX IF NOT EXISTS idx_ai_tokens_customer_ai
  ON ai_tokens(customer_id, ai_id) WHERE revoked_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_ai_tokens_room
  ON ai_tokens(room_id) WHERE revoked_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_ai_tokens_ai ON ai_tokens(ai_id);
