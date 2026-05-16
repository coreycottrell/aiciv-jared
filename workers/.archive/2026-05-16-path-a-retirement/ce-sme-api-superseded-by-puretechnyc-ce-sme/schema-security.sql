CREATE TABLE IF NOT EXISTS rate_limits (key TEXT PRIMARY KEY, count INTEGER DEFAULT 1, window_start TEXT DEFAULT (datetime('now')));
