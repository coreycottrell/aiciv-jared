# Memory: cc.purebrain.ai Command Center Dashboard Diagnostic

**Date**: 2026-02-28
**Type**: operational + teaching
**Topic**: Full diagnostic audit of cc.purebrain.ai login + dashboard tabs

---

## Summary

Complete diagnostic audit of https://cc.purebrain.ai/auth/login run via Playwright headless Chromium.
Zero console errors. All 4 tabs found and clickable. Most data populated. Key issues documented below.

---

## Login Page

- URL: https://cc.purebrain.ai/auth/login
- Page title: "PureBrain Command Center"
- HTTP status: 200
- Visual: Dark background with neural canvas animation (orange/blue rotating rings)
- Form fields:
  - Name: `input[placeholder*="name" i]` — placeholder "Start typing your name..."
  - Email: `input[name="email"]`
  - Password: `input[type="password"]`
  - Submit: `button[type="submit"]` — text "ACCESS DASHBOARD"
- Autocomplete dropdown appeared for Name field (showed "Jared Sanborn / CEO" from browser memory)
- Login succeeded: redirected to https://cc.purebrain.ai/dashboard

---

## Dashboard Structure

- Page built as SPA (Single Page Application)
- Body children: neural-canvas CANVAS, login-screen DIV, app DIV, task-modal, backend-modal, calendar-view, email-view, toast, 2 SCRIPT tags
- `#app` div has class `visible` after login
- Neural canvas animation persists on dashboard background (not removed post-login)

---

## Tab Results

### Tasks Tab
- DATA POPULATED: 35 tasks in table
- Table headers: Title | Assigned To | A/B/C | Priority | Status | Deadline | Actions
- First row: "GCP Deployment — app.purebrain.ai | Timothy DeVore (CTO) | A | High | Awaiting Jared | Mar 2"
- 34 task rows total (tableRows = 38 including header + subheaders)
- Status types seen: "Awaiting Jared", "Open", "In Progress"
- Task categories: TASKS view + TEAM tab both render same task list
- Create Task button present
- Search filter present: `input[placeholder="Search tasks..."]`
- Backend modal has Supabase connection fields (placeholder: "https://xxxxxxxxxxxx.supabase.co")
- Status badge: "Local Only" — indicates NOT synced to backend/Supabase

### Team Tab
- Shows neural radar visualization (full screen, no team member cards visible)
- DOM reports: 50 team members, 35 tasks
- Stats: Total Assigned: 35, In Progress: 11, Pending: 0, Completed: 0, High Priority: 17
- "Card View" button in nav is orange/active — suggests Card View toggle should show cards
- But screenshot shows ONLY the radar visualization — no cards visible
- `team-view` div has class `visible`
- A/B/C guide displayed: A=Aether handles automatically, B=Jared reviews, C=Team member executes
- ISSUE: Team member cards not rendering in Card View (shows radar instead)

### Calendar Tab
- DATA POPULATED: 1017 calendar events loaded
- Events from Google Calendar (Pure Technology account)
- Today (2026-02-28) shows: "Family day" (all day), "Get Ready for Bed" 1:45AM, "Bed Time" 2:00AM, "Add Quotes to Database" 2:25PM, "Family Financial Review" 2:30PM
- Calendar renders as list view (gw-events-container), NOT a calendar grid
- No FullCalendar library present
- Section subtitle: "Google Calendar events for Pure Technology to Load Events 2026-02-28"
- Visual: tiny text list, barely readable at 1440x900 (full-page screenshot is very compressed)

### Email Tab
- Shows inbox for jared@puretechnology.nyc
- Status: "No messages — Inbox is empty or email not yet connected"
- NOT connected to Gmail yet
- Has "Sync Setup" button in nav bar
- Email view children: gw-section-title, gw-section-sub, gw-date-bar, gw-events-container (same structure as calendar)

---

## Console Errors

NONE. Zero console errors, warnings, or network failures across entire session.

---

## Key Issues Found

1. **"Local Only" badge in nav** — data is stored locally, not synced to Supabase backend. Backend modal exists with Supabase URL/key fields.
2. **Team tab shows radar instead of team member cards** — despite "Card View" being selected (orange), no cards render.
3. **Email not connected** — inbox shows "No messages / not yet connected"
4. **Calendar renders as list, not grid** — no FullCalendar library, custom event list renderer

---

## Selector Reference (cc.purebrain.ai)

- Name input: `input[placeholder*="name" i]`
- Email input: `input[name="email"]`
- Password: `input[type="password"]`
- Submit: `button[type="submit"]`
- Tasks tab: `button:has-text("Tasks")`
- Team tab: `button:has-text("Team")`
- Calendar tab: `button:has-text("Calendar")`
- Email tab: `button:has-text("Email")`
- Task table: `table`
- Create task: `button:has-text("Create Task")` or `+ Create Task`
- Sync Setup: `button:has-text("Sync Setup")` (nav bar)
- Card View: `button:has-text("Card View")` (nav bar)

---

## Screenshots

Dir: `/home/jared/projects/AI-CIV/aether/exports/screenshots/cc-diagnostic-20260228/`
- 001-login-page.png — login form initial state
- 002-form-filled.png — form filled with credentials
- 003-post-login.png — immediately after login (Tasks view)
- 004-tab-tasks.png — Tasks tab
- 005-tab-team.png — Team tab
- 006-tab-calendar.png — Calendar tab (full page, compressed)
- 007-tab-email.png — Email tab (no messages)
- 010-tasks-detail.png — Tasks detailed capture
- 011-team-detail.png — Team detailed capture
- 012-calendar-detail.png — Calendar detailed capture

**Tags**: cc.purebrain.ai, command-center, dashboard, login, tasks, team, calendar, email, diagnostic, no-errors, local-only, supabase
