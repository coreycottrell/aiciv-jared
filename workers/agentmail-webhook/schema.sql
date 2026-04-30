-- schema.sql
-- Run once via: wrangler d1 execute purebrain-social --file=workers/agentmail-webhook/schema.sql

CREATE TABLE IF NOT EXISTS magic_links (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_uuid TEXT,
  ai_name TEXT,
  human_name TEXT,
  human_email TEXT,
  paypal_email TEXT,
  container TEXT,
  magic_link TEXT NOT NULL,
  original_link TEXT,
  status TEXT DEFAULT 'ready',
  received_at TEXT DEFAULT (datetime('now')),
  welcome_sent INTEGER DEFAULT 0,
  welcome_sent_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_magic_links_session ON magic_links(session_uuid);
CREATE INDEX IF NOT EXISTS idx_magic_links_email ON magic_links(human_email);
