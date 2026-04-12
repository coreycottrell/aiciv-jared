# Sales Call Wizard — CTO Architecture Record

**Date**: 2026-03-05
**Type**: operational + teaching
**Topic**: Live sales call wizard build for purebrain.ai/sales-playbook/live-call/

## What Was Built

A fully self-contained, single-file HTML wizard that salespeople use LIVE during Zoom calls. Based on demo at purebrain-demo.pages.dev but fully rebranded to PureBrain.

## Key Architectural Decisions

### 1. Self-Contained Single File
- Zero dependencies beyond Google Fonts (Inter)
- No external JS libraries — pure vanilla JS
- Survives screenshare without any server dependencies
- One file = one deploy = zero infrastructure overhead

### 2. Data Persistence Strategy — Dual Layer
- **Layer 1: localStorage** — Notes auto-save keystroke-by-keystroke. Survives refresh, browser crash. Keyed by `pb-wizard-notes-{1-8}`. Shows visual "saving" / "auto-saved" indicator.
- **Layer 2: Google Sheets** — On "Complete Call" modal, submits full call record via fetch POST to Google Apps Script web app. Falls back to localStorage backup if Sheets not configured.
- **Smart fallback**: If `SHEETS_URL` is still placeholder, saves full payload to localStorage with timestamp key `pb-call-record-{timestamp}`. No data loss even pre-configuration.

### 3. Google Sheets Integration Pattern
- Uses Google Apps Script deployed as web app (no backend needed)
- POST to Apps Script URL with JSON payload
- Apps Script appends row to Sheet: timestamp, duration, prospect name/company, outcome, all 8 step notes, steps visited
- `mode: 'no-cors'` required because Apps Script doesn't return CORS headers
- Payload schema: `{timestamp, duration, prospectName, prospectCompany, outcome, stepsVisited[], notes1-8}`

Apps Script code (stored as comment in wizard for reference):
```javascript
function doPost(e) {
  var sheet = SpreadsheetApp.openById('YOUR_SHEET_ID').getActiveSheet();
  var data = JSON.parse(e.postData.contents);
  sheet.appendRow([data.timestamp, data.duration, data.prospectName, ...]);
  return ContentService.createTextOutput(JSON.stringify({status:'ok'}))
    .setMimeType(ContentService.MimeType.JSON);
}
```

### 4. WordPress Deployment Spec
- Template: `elementor_canvas` (strips all theme chrome — gives full control)
- Parent: page 1278 (sales-playbook)
- Password: `closers2026`
- Wrap HTML in `<!-- wp:html -->` block (prevents wpautop filter from destroying CSS/JS)
- URL target: `purebrain.ai/sales-playbook/live-call/`
- Deploy via REST API: POST to `https://purebrain.ai/wp-json/wp/v2/pages`

### 5. Brand Color System
- `--accent: #2a93c1` (PT Blue) — primary navigation, active states, step indicators
- `--cta: #f1420b` (PT Orange) — CTA buttons, "New Call" button, note box borders, close step urgency
- `--bg: #080a12` — standard dark background
- `--bg-card: #141820`, `--bg-surface: #0e1015` — layered surface hierarchy

### 6. Navigation Architecture
- Arrow keys (left/right/up/down) — no navigation when focus is in textarea
- Number keys 1-8 — jump directly to any step
- Spacebar on Step 6 — reveals next payoff feature
- Click sidebar steps — jump anywhere
- Progress dots in nav bar show completed (green) / active (blue expanded) / upcoming (dim)

## File Locations
- Source HTML: `/home/jared/projects/AI-CIV/aether/exports/sales-call-wizard/index.html`
- Deploy script: `/home/jared/projects/AI-CIV/aether/exports/sales-call-wizard/wp_deploy.py`

## Teaching: Google Sheets Without Backend
The pattern `fetch(url, {method:'POST', mode:'no-cors', body: JSON.stringify(data)})` to a Google Apps Script web app is the zero-infrastructure data capture solution. The response is opaque (no-cors) but the POST goes through. Always add localStorage backup because the response is unreadable.

## Teaching: Sales Tool UX Principles
- Full-screen, fixed layout (no scroll jank on screenshare)
- Notes on EVERY step — never lose prospect insights mid-call
- Timer visible always — sales reps need call awareness
- "New Call" button instantly resets without losing previous call data (localStorage preserves last call until new call explicitly clears it)
- The modal for "Complete Call" adds the final CRM capture step without interrupting the flow
