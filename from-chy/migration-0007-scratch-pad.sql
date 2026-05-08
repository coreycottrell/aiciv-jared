-- Migration 0007: Quartet shared scratch pad (D1-backed)
-- Spec: Morphe. Worker integration: Chy. Deploy: Aether.
-- Date: 2026-04-17

CREATE TABLE agent_scratch_pad (
    id TEXT PRIMARY KEY,
    author TEXT NOT NULL CHECK(author IN ('aether', 'chy', 'morphe', 'jared')),
    key TEXT NOT NULL CHECK(key IN ('current-task', 'decision', 'blocker', 'idea', 'handoff', 'note')),
    value TEXT NOT NULL,
    created_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE INDEX idx_scratchpad_author ON agent_scratch_pad(author, created_at DESC);
CREATE INDEX idx_scratchpad_key ON agent_scratch_pad(key, created_at DESC);
