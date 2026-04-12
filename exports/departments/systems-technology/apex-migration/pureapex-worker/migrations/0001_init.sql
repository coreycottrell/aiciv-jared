-- PureApex D1 Schema Migration
-- Mirrors the SQLite schema from the server app

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    display_name TEXT NOT NULL,
    role TEXT NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS opportunities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT NOT NULL,
    contact_name TEXT DEFAULT '',
    contact_title TEXT DEFAULT '',
    contact_email TEXT DEFAULT '',
    contact_linkedin TEXT DEFAULT '',
    contact_location TEXT DEFAULT '',
    type TEXT CHECK(type IN ('CPG', 'Gaming', 'Enterprise', 'PureBrain')),
    vertical TEXT DEFAULT '',
    geography TEXT CHECK(geography IN ('NA', 'EMEA', 'APAC', 'MENA', 'LATAM', 'Global')),
    stage TEXT CHECK(stage IN ('Suspect', 'Pipeline', 'Qualified', 'Proposal Submitted', 'Proposal Finalised', 'Sponsor Commitment', 'Proposal Accepted', 'Closed Won', 'Closed Lost')) DEFAULT 'Suspect',
    playbook_weapon TEXT DEFAULT '',
    owner TEXT NOT NULL,
    estimated_value REAL DEFAULT 0,
    next_action TEXT DEFAULT '',
    next_action_date TEXT DEFAULT '',
    notes TEXT DEFAULT '',
    partner TEXT DEFAULT '',
    meddpicc_metrics TEXT DEFAULT '',
    meddpicc_economic_buyer TEXT DEFAULT '',
    meddpicc_decision_criteria TEXT DEFAULT '',
    meddpicc_decision_process TEXT DEFAULT '',
    meddpicc_paper_process TEXT DEFAULT '',
    meddpicc_identify_pain TEXT DEFAULT '',
    meddpicc_champion TEXT DEFAULT '',
    meddpicc_competition TEXT DEFAULT '',
    emotional_arc TEXT DEFAULT '',
    division TEXT DEFAULT '',
    readiness_pnl_pain INTEGER DEFAULT 0,
    readiness_decision_maker INTEGER DEFAULT 0,
    readiness_competitor INTEGER DEFAULT 0,
    readiness_unique_angle INTEGER DEFAULT 0,
    readiness_proof INTEGER DEFAULT 0,
    stage_changed_at TEXT DEFAULT '',
    created_by TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    opportunity_id INTEGER REFERENCES opportunities(id),
    action TEXT NOT NULL,
    actor TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS meeting_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    opportunity_id INTEGER REFERENCES opportunities(id),
    note_type TEXT DEFAULT 'meeting',
    content TEXT NOT NULL,
    actor TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS linkedin_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    access_token TEXT NOT NULL,
    expires_at TEXT,
    refresh_token TEXT,
    linkedin_id TEXT,
    linkedin_name TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS prospect_pages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL,
    company_name TEXT NOT NULL,
    password TEXT NOT NULL,
    html_content TEXT NOT NULL,
    is_active INTEGER DEFAULT 1,
    view_count INTEGER DEFAULT 0,
    created_by TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);
