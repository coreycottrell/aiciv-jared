-- CE SME Sprint 2: Billing/Invoicing + HR Management tables

CREATE TABLE IF NOT EXISTS invoices (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  project_id INTEGER,
  milestone_id INTEGER,
  client_name TEXT NOT NULL,
  amount REAL NOT NULL,
  status TEXT DEFAULT 'draft',
  due_date TEXT,
  paid_date TEXT,
  notes TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS expenses (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  category TEXT NOT NULL,
  amount REAL NOT NULL,
  description TEXT,
  receipt_url TEXT,
  expense_date TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS jobs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  requirements TEXT,
  salary_range TEXT,
  status TEXT DEFAULT 'open',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS candidates (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  job_id INTEGER NOT NULL,
  name TEXT NOT NULL,
  email TEXT,
  phone TEXT,
  resume_text TEXT,
  ai_screening TEXT,
  status TEXT DEFAULT 'applied',
  rating INTEGER,
  notes TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS onboarding (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  candidate_id INTEGER,
  employee_name TEXT NOT NULL,
  position TEXT,
  start_date TEXT,
  checklist TEXT,
  status TEXT DEFAULT 'pending',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS reviews (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  employee_name TEXT NOT NULL,
  position TEXT,
  review_period TEXT,
  rating INTEGER,
  strengths TEXT,
  improvements TEXT,
  goals TEXT,
  ai_draft TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
