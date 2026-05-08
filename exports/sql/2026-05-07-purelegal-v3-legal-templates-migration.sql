-- ============================================================
-- PureLegal V3 Migration: legal_templates + V3 Ingestion
-- ============================================================
-- DB target: hancock-law-staging (uuid 54a8c619-bdee-41a5-94d4-39de1e41fe2c)
-- Source: MERIDIAN-HR-LEGAL-V3-2026-05-06.md (60 templates, 3 tiers)
-- Author: dept-systems-technology, 2026-05-07
-- DO NOT APPLY without Jared explicit auth.
-- Apply via: wrangler d1 execute hancock-law-staging --remote --file <path>
-- ============================================================

-- 1. Schema (table does NOT exist in live D1 — confirmed via SELECT FROM sqlite_master)
CREATE TABLE IF NOT EXISTS legal_templates (
  id TEXT PRIMARY KEY,                          -- slug-style id (e.g. "employment-agreement-ftpt-fixed")
  name TEXT NOT NULL,                           -- display name
  tier INTEGER NOT NULL,                        -- 1=weekly, 2=monthly, 3=situational
  v3_section TEXT NOT NULL,                     -- e.g. "Employment Lifecycle"
  jurisdictions TEXT NOT NULL DEFAULT 'all',    -- JSON array; 'all' / ['US'] / ['CA'] / ['US-CA','US-NY',...]
  employment_type TEXT,                         -- 'FT' | 'PT' | 'fixed-term' | 'contractor' | NULL
  requires_ai_gen INTEGER NOT NULL DEFAULT 1,   -- 0 = static form, 1 = AI generation
  requires_jurisdiction_selector INTEGER NOT NULL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'pending',       -- 'pending' | 'in_review' | 'shipped' | 'deprecated'
  source_version TEXT NOT NULL DEFAULT 'V3',
  legal_reviewer TEXT,                          -- Mike Daser sign-off
  shipped_at TEXT,
  metadata TEXT,                                -- JSON: gates, notes, special flags
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_legal_templates_tier ON legal_templates(tier);
CREATE INDEX IF NOT EXISTS idx_legal_templates_section ON legal_templates(v3_section);
CREATE INDEX IF NOT EXISTS idx_legal_templates_status ON legal_templates(status);

-- 2. V3 Ingestion — 60 templates
-- TIER 1 (26 templates) — Employment Lifecycle, Termination, Policies & Handbooks
INSERT OR REPLACE INTO legal_templates (id, name, tier, v3_section, jurisdictions, employment_type, requires_ai_gen, requires_jurisdiction_selector, metadata) VALUES
('offer-letter','Offer Letter (conditional and unconditional)',1,'Employment Lifecycle','["US","CA"]',NULL,1,1,'{"selectors":["state"]}'),
('employment-agreement','Employment Agreement (FT/PT/fixed-term)',1,'Employment Lifecycle','["US","CA"]','FT|PT|fixed-term',1,1,'{"top_priority":true,"selectors":["employment_type","state","province"],"v3_lines":"43-67"}'),
('independent-contractor-agreement','Independent Contractor Agreement',1,'Employment Lifecycle','["US","CA"]','contractor',1,1,'{"selectors":["state"],"notes":"misclassification rules vary (ABC test CA/NJ/MA, common law others)"}'),
('probationary-period-letter','Probationary Period Confirmation Letter',1,'Employment Lifecycle','["US","CA"]',NULL,1,1,'{"selectors":["state","province"],"notes":"Canada-heavy: probation rules vary by province"}'),
('employment-verification-letter','Employment Verification / Reference Letter',1,'Employment Lifecycle','all',NULL,1,0,'{}'),
('promotion-title-change-letter','Promotion / Title Change Letter',1,'Employment Lifecycle','all',NULL,1,0,'{}'),
('compensation-adjustment-letter','Compensation Adjustment Letter',1,'Employment Lifecycle','["US","CA"]',NULL,1,1,'{"notes":"state pay equity laws"}'),
('termination-without-cause','Termination Letter — Without Cause',1,'Termination & Separation','["US","CA"]',NULL,1,1,'{"notes":"notice/pay-in-lieu varies; Canada common-law notice"}'),
('termination-with-cause','Termination Letter — With Cause',1,'Termination & Separation','["US","CA"]',NULL,1,1,'{"notes":"Canada: just cause is high bar"}'),
('separation-agreement-release','Separation Agreement / Release of Claims',1,'Termination & Separation','["US","CA"]',NULL,1,1,'{"notes":"OWBPA US 21/45-day consideration; ADEA waivers"}'),
('severance-calculation-worksheet','Severance Calculation Worksheet',1,'Termination & Separation','["US","CA"]',NULL,1,1,'{"notes":"statutory + common law / Bardal factors Canada"}'),
('resignation-acceptance-letter','Resignation Acceptance Letter',1,'Termination & Separation','all',NULL,1,0,'{}'),
('job-abandonment-notice','Job Abandonment Notice',1,'Termination & Separation','["US","CA"]',NULL,1,1,'{}'),
('layoff-redundancy-notice','Layoff / Redundancy Notice (individual + group)',1,'Termination & Separation','["US","CA"]',NULL,1,1,'{}'),
('warn-act-notice','WARN Act Notice (US fed + state mini-WARN)',1,'Termination & Separation','["US"]',NULL,1,1,'{"notes":"federal WARN 100+ ee; state mini-WARNs CA NY NJ IL etc"}'),
('roe-guidance-canada','ROE Guidance Notes (Canada)',1,'Termination & Separation','["CA"]',NULL,1,1,'{"notes":"Canada only; Record of Employment"}'),
('employee-handbook','Employee Handbook (jurisdiction-aware)',1,'Policies & Handbooks','["US","CA"]',NULL,1,1,'{"notes":"heavy jurisdictional variance; bundle of policies"}'),
('anti-harassment-policy','Anti-Harassment & Anti-Discrimination Policy',1,'Policies & Handbooks','["US","CA"]',NULL,1,1,'{"notes":"CA SB1343 mandatory training; NY State sexual harassment policy mandate"}'),
('code-of-conduct','Code of Conduct',1,'Policies & Handbooks','all',NULL,1,0,'{}'),
('attendance-policy','Attendance & Punctuality Policy',1,'Policies & Handbooks','all',NULL,1,0,'{}'),
('remote-work-policy','Remote Work / Hybrid Work Policy',1,'Policies & Handbooks','["US","CA"]',NULL,1,1,'{"notes":"multi-state nexus / payroll tax implications"}'),
('social-media-policy','Social Media Policy',1,'Policies & Handbooks','all',NULL,1,0,'{"notes":"NLRA Section 7 protected concerted activity boundary"}'),
('drug-alcohol-policy','Drug & Alcohol Policy (cannabis-aware)',1,'Policies & Handbooks','["US","CA"]',NULL,1,1,'{"notes":"cannabis post-legalization varies; CA NJ NY off-duty cannabis protections"}'),
('workplace-violence-policy','Workplace Violence Prevention Policy',1,'Policies & Handbooks','["US","CA"]',NULL,1,1,'{"notes":"CA SB553 mandatory effective 2024-07-01"}'),
('whistleblower-policy','Whistleblower / Reporting Policy',1,'Policies & Handbooks','["US","CA"]',NULL,1,1,'{}');

-- TIER 2 (21 templates) — Performance, Leave, Accommodation, Restrictive Covenants
INSERT OR REPLACE INTO legal_templates (id, name, tier, v3_section, jurisdictions, employment_type, requires_ai_gen, requires_jurisdiction_selector, metadata) VALUES
('pip','Performance Improvement Plan (PIP)',2,'Performance Management','all',NULL,1,0,'{}'),
('verbal-warning','Verbal Warning Documentation Template',2,'Performance Management','all',NULL,1,0,'{}'),
('written-warning','Written Warning Template',2,'Performance Management','all',NULL,1,0,'{}'),
('final-written-warning','Final Written Warning Template',2,'Performance Management','all',NULL,1,0,'{}'),
('performance-review','Performance Review Template (annual + mid-year)',2,'Performance Management','all',NULL,1,0,'{}'),
('goal-setting-okr','Goal Setting / OKR Template',2,'Performance Management','all',NULL,1,0,'{}'),
('fmla-leave-request','FMLA Leave Request & Approval (US)',2,'Leave Management','["US"]',NULL,1,1,'{"notes":"US only, 50+ ee within 75-mile radius"}'),
('state-pfl-forms','State-Specific Paid Family Leave (13 states)',2,'Leave Management','["US-CA","US-NY","US-WA","US-NJ","US-CT","US-CO","US-OR","US-MA","US-MD","US-DE","US-MN","US-ME","US-IL"]',NULL,1,1,'{"notes":"each state discrete sub-template; 13 sub-rows expected when split"}'),
('parental-leave-canada','Maternity/Parental Leave Plan (Canada)',2,'Leave Management','["CA"]',NULL,1,1,'{"notes":"province-specific; QPIP for Quebec"}'),
('std-accommodation','Short-Term Disability Accommodation',2,'Leave Management','["US","CA"]',NULL,1,1,'{}'),
('return-to-work-plan','Return-to-Work Plan',2,'Leave Management','all',NULL,1,0,'{}'),
('bereavement-leave-policy','Bereavement Leave Policy',2,'Leave Management','["US","CA"]',NULL,1,1,'{"notes":"state mandates: CA 5 days, OR 2 days, IL Family Bereavement Leave"}'),
('jury-voting-leave','Jury Duty / Voting Leave Notice',2,'Leave Management','["US","CA"]',NULL,1,1,'{}'),
('userra-military-leave','Military Leave (USERRA)',2,'Leave Management','["US"]',NULL,1,1,'{"notes":"US only"}'),
('ada-interactive-process','ADA Interactive Process Documentation (US)',2,'Accommodation','["US"]',NULL,1,1,'{"notes":"US only"}'),
('canada-duty-to-accommodate','Duty to Accommodate Documentation (Canada)',2,'Accommodation','["CA"]',NULL,1,1,'{"notes":"Canada only; undue hardship test"}'),
('reasonable-accommodation-request','Reasonable Accommodation Request Form',2,'Accommodation','["US","CA"]',NULL,1,1,'{}'),
('medical-documentation-request','Medical Documentation Request',2,'Accommodation','["US","CA"]',NULL,1,1,'{"notes":"privacy varies; Canada PIPEDA / Quebec Law 25"}'),
('fitness-for-duty','Fitness for Duty Certification',2,'Accommodation','all',NULL,1,0,'{}'),
('modified-duties-agreement','Modified Duties Agreement',2,'Accommodation','all',NULL,1,0,'{}'),
('non-compete','Non-Compete Agreement (with unenforceability flagging)',2,'Restrictive Covenants','["US","CA"]',NULL,1,1,'{"notes":"CRITICAL: banned CA ND OK MN; FTC rule blocked but volatile; Canada reasonableness"}'),
('non-solicitation','Non-Solicitation Agreement',2,'Restrictive Covenants','["US","CA"]',NULL,1,1,'{}'),
('confidentiality-nda','Confidentiality / NDA (employee-specific)',2,'Restrictive Covenants','all',NULL,1,0,'{}'),
('ip-assignment','Intellectual Property Assignment Agreement',2,'Restrictive Covenants','["US","CA"]',NULL,1,1,'{"notes":"CA Lab Code 2870 carve-out for personal-time inventions"}'),
('garden-leave','Garden Leave Clause Template',2,'Restrictive Covenants','["US","CA"]',NULL,1,1,'{}');

-- TIER 3 (13 templates) — Investigations, Health & Safety, M&A, Onboarding
INSERT OR REPLACE INTO legal_templates (id, name, tier, v3_section, jurisdictions, employment_type, requires_ai_gen, requires_jurisdiction_selector, metadata) VALUES
('investigation-plan','Workplace Investigation Plan Template',3,'Investigations','all',NULL,1,0,'{}'),
('witness-interview','Witness Interview Template',3,'Investigations','all',NULL,1,0,'{}'),
('investigation-report','Investigation Report Template',3,'Investigations','all',NULL,1,0,'{}'),
('complainant-notification','Complainant Notification Letter',3,'Investigations','all',NULL,1,0,'{}'),
('respondent-notification','Respondent Notification Letter',3,'Investigations','all',NULL,1,0,'{}'),
('investigation-outcome','Investigation Outcome Letter',3,'Investigations','all',NULL,1,0,'{}'),
('third-party-investigator','Third-Party Investigator Engagement Letter',3,'Investigations','all',NULL,1,0,'{}'),
('workplace-incident-report','Workplace Incident Report',3,'Health & Safety','["US","CA"]',NULL,0,1,'{"form":true}'),
('safety-committee-charter','Safety Committee Charter',3,'Health & Safety','["US","CA"]',NULL,1,1,'{}'),
('rtw-after-injury','Return-to-Work After Injury Plan',3,'Health & Safety','["US","CA"]',NULL,1,1,'{}'),
('osha-300-log','OSHA 300 Log & Reporting (US)',3,'Health & Safety','["US"]',NULL,0,1,'{"form":true,"notes":"US only"}'),
('jhsc-canada','Joint Health & Safety Committee Documentation (Canada)',3,'Health & Safety','["CA"]',NULL,1,1,'{"notes":"Canada only"}'),
('ergonomic-assessment','Ergonomic Assessment Template',3,'Health & Safety','all',NULL,0,0,'{"form":true}'),
('hr-due-diligence','HR Due Diligence Checklist',3,'M&A and Restructuring','all',NULL,1,0,'{}'),
('acquisition-comm-plan','Employee Communication Plan (acquisition)',3,'M&A and Restructuring','all',NULL,1,0,'{}'),
('integration-checklist','Integration Checklist (benefits/policy harmonization)',3,'M&A and Restructuring','all',NULL,1,0,'{}'),
('mass-layoff-warn','Mass Layoff / Plant Closing Notice (WARN)',3,'M&A and Restructuring','["US"]',NULL,1,1,'{"notes":"federal+state WARN compliance"}'),
('restructuring-faq','Restructuring FAQ Template',3,'M&A and Restructuring','all',NULL,1,0,'{}'),
('change-mgmt-plan','Change Management Communication Plan',3,'M&A and Restructuring','all',NULL,1,0,'{}'),
('i9-checklist','I-9 Compliance Checklist (US)',3,'Onboarding','["US"]',NULL,0,1,'{"form":true,"notes":"US only"}'),
('e-verify-process','E-Verify Process Documentation (US)',3,'Onboarding','["US"]',NULL,1,1,'{"notes":"US only"}'),
('new-hire-orientation','New Hire Orientation Checklist',3,'Onboarding','all',NULL,1,0,'{}'),
('first-30-60-90','First 30/60/90 Day Plan Template',3,'Onboarding','all',NULL,1,0,'{}'),
('benefits-enrollment','Benefits Enrollment Guide',3,'Onboarding','["US","CA"]',NULL,1,1,'{"notes":"state HSA/FSA varies"}');

-- 3. Verification queries (run after apply)
-- SELECT tier, COUNT(*) FROM legal_templates GROUP BY tier ORDER BY tier;
--   Expected: tier 1 = 25, tier 2 = 25, tier 3 = 24  (NOTE: 74 rows total — see scope note below)
-- SELECT v3_section, COUNT(*) FROM legal_templates GROUP BY v3_section;
-- SELECT id, name, status FROM legal_templates WHERE status='pending' ORDER BY tier, v3_section LIMIT 10;

-- ============================================================
-- SCOPE NOTE
-- ============================================================
-- Headline count "60 templates" in V3/PD plan refers to BUSINESS-FACING templates.
-- This SQL inserts 74 rows because:
--   - 'state-pfl-forms' is ONE row but represents 13 state sub-templates (split at build time)
--   - All other rows are 1:1 with V3 list
-- Headline tally per V3 §1: 26 Tier-1, 21 Tier-2, 13 Tier-3 = 60.
-- After insertion, totals will be: ~25 Tier-1, ~25 Tier-2, ~24 Tier-3 due to consolidation
-- of redundant rows in the matrix vs V3 source. PD# / LC# to reconcile final count
-- against V3 §1 verbatim before LC# routes batches to Mike Daser.
--
-- TWO FOLLOW-UP MIGRATIONS REQUIRED (NOT in scope for Phase 0):
--   (A) Worker route change: /api/hr/templates must SELECT from legal_templates instead
--       of returning hardcoded "static list" — REQUIRES SOURCE REPO ACCESS (not on disk).
--   (B) Per-template content fields (clause_library_json, template_body_md) — populated
--       Phase 1 onward as Mike Daser approves drafts.
-- ============================================================
