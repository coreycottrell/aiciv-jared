-- Migration 0002: add content_items.metadata column (TEXT, JSON-stringified)
-- D1: purebrain-social
-- Reason: handleCreateContent (workers/social-api/src/worker.js) accepts a `metadata`
-- field from the kanban UI (worker.js:1752) but the column does not exist on
-- content_items per shared/social-api-schema.sql:50. The field is silently dropped
-- on insert today. Adding it explicitly so the blog-publish-hook can persist
-- {source, slug, blog_url} for traceability.
--
-- Idempotent: D1's SQLite supports `ALTER TABLE ... ADD COLUMN`. If the column already
-- exists in production (e.g. added out-of-band), the migration will error and should
-- be skipped manually. Confirm with `wrangler d1 execute purebrain-social --command "PRAGMA table_info(content_items)"` before applying.

ALTER TABLE content_items ADD COLUMN metadata TEXT;

-- Same treatment for `title` if missing (worker.js:4000 lists it in `allowed` for UPDATE
-- but it's also not in the canonical schema). Skip if production already has it.
-- ALTER TABLE content_items ADD COLUMN title TEXT;
