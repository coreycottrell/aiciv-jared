CREATE TABLE IF NOT EXISTS ara_brands (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  url TEXT NOT NULL,
  industry TEXT,
  owner_email TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS ara_scores (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  brand_id INTEGER NOT NULL REFERENCES ara_brands(id),
  dimension TEXT NOT NULL,
  score REAL NOT NULL DEFAULT 0,
  signals TEXT,
  scanned_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS ara_synthetic_queries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  brand_id INTEGER NOT NULL REFERENCES ara_brands(id),
  model TEXT NOT NULL,
  query TEXT NOT NULL,
  brand_appeared INTEGER DEFAULT 0,
  rank_position INTEGER,
  confidence REAL,
  response_text TEXT,
  scanned_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS ara_scans (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  brand_id INTEGER NOT NULL REFERENCES ara_brands(id),
  total_score REAL NOT NULL DEFAULT 0,
  tier TEXT,
  dimensions TEXT,
  scanned_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS ara_nuggets (
  brand_id INTEGER PRIMARY KEY REFERENCES ara_brands(id),
  nuggets TEXT NOT NULL,
  updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_ara_brands_url ON ara_brands(url);
CREATE INDEX IF NOT EXISTS idx_ara_scores_brand ON ara_scores(brand_id);
CREATE INDEX IF NOT EXISTS idx_ara_scans_brand ON ara_scans(brand_id);
