-- Migration 0004: Rooms schema for Thread B (DUO/TRIO Chat) Phase 1
-- Date: 2026-05-12
-- Source: CTO pre-build spec (cto-prebuild-thread-b-rescoped-2026-05-12.md)
--
-- Scope:
--   - Add rooms, room_members, room_seq_counters tables
--   - Extend trio_messages with seq, room_id, client_msg_id, attachments_json
--   - Backfill room_id = 'room_' || trio_id for legacy messages
--
-- ADDITIVE + BACKWARD-COMPAT: all existing /trio/* endpoints continue working.
-- Existing trio_messages rows get room_id auto-populated from trio_id.
--
-- Apply (dev first):
--   cd workers/trio-comms
--   CLOUDFLARE_API_TOKEN=... npx wrangler d1 execute purebrain-referrals \
--     --remote --file migrations/0004-rooms-schema.sql
--
-- Idempotency: All CREATE TABLE statements use IF NOT EXISTS. ALTER TABLE
-- statements have no IF NOT EXISTS variant in SQLite; they will fail loudly
-- on re-run, which is intentional (drift detection).

-- =========================================================================
-- New table: rooms (one per customer account in Phase 1)
-- =========================================================================
CREATE TABLE IF NOT EXISTS rooms (
  id TEXT PRIMARY KEY,                          -- e.g. "room_{customer_id}"
  customer_id TEXT NOT NULL UNIQUE,             -- soft FK to clients.id (different D1)
  name TEXT NOT NULL DEFAULT '',                -- customer-editable; default placeholder "Duo"/"Trio" set client-side
  created_at INTEGER NOT NULL,                  -- epoch ms
  archived_at INTEGER,                          -- soft delete
  retention_days INTEGER NOT NULL DEFAULT 90,
  attachment_bytes_used INTEGER NOT NULL DEFAULT 0,  -- denormalized for quick quota check
  storage_soft_cap_bytes INTEGER NOT NULL DEFAULT 1073741824,  -- 1 GB
  storage_hard_cap_bytes INTEGER NOT NULL DEFAULT 5368709120   -- 5 GB
);

CREATE INDEX IF NOT EXISTS idx_rooms_customer ON rooms(customer_id);
CREATE INDEX IF NOT EXISTS idx_rooms_archived ON rooms(archived_at);

-- =========================================================================
-- New table: room_members
-- =========================================================================
-- Member types:
--   'ai'    — display_name from clients.ai_name, member_id = ai_name slug
--   'human' — display_name from clients.goes_by, member_id = "human:{email}"
-- Per Jared 2026-05-12: humans are FIRST-CLASS (read + post), not observers.
CREATE TABLE IF NOT EXISTS room_members (
  room_id TEXT NOT NULL,
  member_id TEXT NOT NULL,
  member_type TEXT NOT NULL CHECK(member_type IN ('ai', 'human')),
  display_name TEXT NOT NULL,
  scopes_json TEXT NOT NULL DEFAULT '["read","write","upload"]',
  joined_at INTEGER NOT NULL,
  last_heartbeat_at INTEGER,
  last_seq_seen INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (room_id, member_id)
);

CREATE INDEX IF NOT EXISTS idx_room_members_member ON room_members(member_id);
CREATE INDEX IF NOT EXISTS idx_room_members_room ON room_members(room_id);

-- =========================================================================
-- New table: room_seq_counters (atomic per-room sequence allocator)
-- =========================================================================
-- Server-allocated monotonic seq per room. NOT per-AI (simpler, global order).
-- Atomic increment via: INSERT ... ON CONFLICT DO UPDATE ... RETURNING next_seq
CREATE TABLE IF NOT EXISTS room_seq_counters (
  room_id TEXT PRIMARY KEY,
  next_seq INTEGER NOT NULL DEFAULT 1
);

-- =========================================================================
-- Extend trio_messages — keep table name for backward-compat
-- =========================================================================
-- New columns:
--   room_id          — canonical room reference (vs trio_id which stays for compat)
--   seq              — per-room monotonic sequence number
--   client_msg_id    — UUID from client for idempotency (INSERT OR IGNORE semantics)
--   attachments_json — JSON array of {url, mime, filename, size}
ALTER TABLE trio_messages ADD COLUMN room_id TEXT;
ALTER TABLE trio_messages ADD COLUMN seq INTEGER;
ALTER TABLE trio_messages ADD COLUMN client_msg_id TEXT;
ALTER TABLE trio_messages ADD COLUMN attachments_json TEXT DEFAULT '[]';

-- =========================================================================
-- Backfill: legacy messages get room_id derived from trio_id
-- =========================================================================
-- Mirror rule: room_id = 'room_' || trio_id for all pre-existing rows.
-- This means trio-0 (Aether/Chy/Morphe/Jared) lives at room_id = 'room_trio-0'.
-- Zero migration risk: existing /trio/messages?trio_id=trio-0 continues to work.
UPDATE trio_messages SET room_id = 'room_' || trio_id WHERE room_id IS NULL;

-- =========================================================================
-- Indexes on trio_messages (room_id + seq for cursor pagination)
-- =========================================================================
CREATE INDEX IF NOT EXISTS idx_messages_room_seq ON trio_messages(room_id, seq);
CREATE UNIQUE INDEX IF NOT EXISTS uniq_messages_client_idem
  ON trio_messages(room_id, client_msg_id)
  WHERE client_msg_id IS NOT NULL;
