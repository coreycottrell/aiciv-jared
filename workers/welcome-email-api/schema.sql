-- schema.sql
-- Run once via: wrangler d1 execute purebrain-social --file=workers/welcome-email-api/schema.sql

CREATE TABLE IF NOT EXISTS email_templates (
  id           TEXT PRIMARY KEY,
  name         TEXT NOT NULL,
  subject_tmpl TEXT NOT NULL,
  html_tmpl    TEXT NOT NULL,
  text_tmpl    TEXT,
  created_at   TEXT DEFAULT (datetime('now')),
  updated_at   TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS email_delivery_log (
  id              TEXT PRIMARY KEY,
  template_id     TEXT,
  recipient_email TEXT NOT NULL,
  recipient_name  TEXT,
  ai_name         TEXT,
  magic_link      TEXT,
  tier            TEXT,
  status          TEXT DEFAULT 'sent',
  brevo_message_id TEXT,
  sent_at         TEXT DEFAULT (datetime('now')),
  error           TEXT
);
