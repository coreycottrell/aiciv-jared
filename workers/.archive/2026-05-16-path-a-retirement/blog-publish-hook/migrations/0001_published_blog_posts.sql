-- Migration 0001: published_blog_posts + worker_metadata
-- D1: purebrain-social (database_id 625dde70-0a60-45e7-bf81-e18e5ac4d854)
-- Owner: blog-publish-hook Worker
-- Spec: .claude/memory/departments/systems-technology/2026-05-02--bsky-publish-hook-spec.md (v2.4)
-- Amendments applied: A1 (TEXT FK to content_items.id UUID), A5 (worker_metadata for backfill rule)
--
-- Rationale for staying in purebrain-social DB (CTO sign-off, amendment context):
--   thread_queued_content_item_id is a foreign key to content_items.id; cross-DB FK breaks
--   referential integrity. One D1 binding per worker is cleaner.

CREATE TABLE IF NOT EXISTS published_blog_posts (
  slug                          TEXT PRIMARY KEY,
  url                           TEXT NOT NULL,
  title                         TEXT NOT NULL,
  published_at                  TEXT NOT NULL,            -- ISO 8601 from blog index <time datetime=...>
  detected_at                   TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
  thread_queued_content_item_id TEXT,                     -- A1: TEXT (UUID), nullable, FK -> content_items.id
  thread_queued_at              TEXT,
  status                        TEXT NOT NULL DEFAULT 'detected', -- detected | queued | failed | skipped
  retry_count                   INTEGER NOT NULL DEFAULT 0,
  last_error                    TEXT
);

CREATE INDEX IF NOT EXISTS idx_pbp_status      ON published_blog_posts(status);
CREATE INDEX IF NOT EXISTS idx_pbp_detected_at ON published_blog_posts(detected_at);

-- A5: deterministic backfill rule via worker_first_deploy_timestamp.
-- On first cron tick we INSERT a single row keyed 'first_deploy_timestamp' with the current ISO time.
-- Thereafter every blog-post row whose published_at < first_deploy_timestamp inserts as 'skipped';
-- newer ones insert as 'detected' and proceed to queue. Pure-function, idempotent under DB rebuild.
CREATE TABLE IF NOT EXISTS worker_metadata (
  key   TEXT PRIMARY KEY,
  value TEXT NOT NULL
);
