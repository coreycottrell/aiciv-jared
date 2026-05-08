-- Migrate R2 public domain URLs to proxy URLs in content_items.media_refs
-- Problem: pub-8f8cf3b34e354e108283ed11c59db125.r2.dev returns 404 for all objects
-- Fix: Use social.purebrain.ai/media/{key} proxy (Worker-based, reads from R2 binding)
-- Date: 2026-05-04
--
-- Run via: python3 tools/migrate_d1_r2_urls.py
-- Or manually via CF D1 HTTP API

-- Preview affected rows:
SELECT id, status, content_type, SUBSTR(media_refs, 1, 120) as media_preview
FROM content_items
WHERE media_refs LIKE '%pub-8f8cf3b34e354e108283ed11c59db125.r2.dev%';

-- Execute migration:
UPDATE content_items
SET media_refs = REPLACE(
    media_refs,
    'https://pub-8f8cf3b34e354e108283ed11c59db125.r2.dev/',
    'https://social.purebrain.ai/media/'
)
WHERE media_refs LIKE '%pub-8f8cf3b34e354e108283ed11c59db125.r2.dev%';

-- Verify:
SELECT COUNT(*) as remaining
FROM content_items
WHERE media_refs LIKE '%pub-8f8cf3b34e354e108283ed11c59db125.r2.dev%';
-- Expected: 0
