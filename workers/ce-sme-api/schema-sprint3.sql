-- Sprint 3: Content/Website module
-- Run: CLOUDFLARE_API_TOKEN=... npx wrangler d1 execute ce-sme-db --file=schema-sprint3.sql --remote

CREATE TABLE IF NOT EXISTS content_calendar (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  type TEXT NOT NULL DEFAULT 'blog',
  title TEXT NOT NULL,
  topic TEXT,
  audience TEXT,
  brand_voice TEXT,
  ai_draft TEXT,
  status TEXT DEFAULT 'idea',
  scheduled_date TEXT,
  published_date TEXT,
  channel TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS website_pages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  page_name TEXT NOT NULL,
  content TEXT,
  seo_title TEXT,
  seo_description TEXT,
  status TEXT DEFAULT 'draft',
  last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
