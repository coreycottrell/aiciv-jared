-- Wave 1: LinkedIn rate limit (5 posts/hour)
-- Used by POST /api/linkedin/post-with-image
CREATE TABLE IF NOT EXISTS linkedin_rate_limit (
  hour_key TEXT PRIMARY KEY,
  count INTEGER NOT NULL DEFAULT 0
);
