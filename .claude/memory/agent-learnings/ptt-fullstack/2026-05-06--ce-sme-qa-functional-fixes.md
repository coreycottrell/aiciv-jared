# CE SME QA Functional Fixes

**Date**: 2026-05-06
**Type**: operational
**Agent**: full-stack-developer

## Context
Fixed 7 QA findings for the CE SME platform after security hardening was already applied.

## Fixes Applied

1. **POST /api/compliance** - The frontend form existed but route was missing. Added `handleCreateCompliance` with input validation.
2. **GET /api/onboarding** - List endpoint missing, causing perpetual spinner. Added `handleListOnboarding` + frontend `loadOnboarding()` with table rendering.
3. **Dashboard overdue count** - Tasks query was missing `overdue` aggregation. Added `SUM(CASE WHEN due_date < date('now') AND status = 'pending' THEN 1 ELSE 0 END) as overdue`.
4. **Proposal PDF export** - API endpoint existed (`POST /api/proposals/:id/pdf`) but frontend never called it. Added `exportProposalPdf()` that opens print-friendly window.
5. **Proposal ID validation** - `handleCreateProject` now verifies `proposal_id` belongs to user before INSERT.
6. **Status enum validation** - Added `STATUS_ENUMS` constant and `validateStatus()` function. Applied to all 7 update handlers (proposals, tasks, invoices, jobs, candidates, content_calendar).
7. **Server-side logout** - `logout()` now calls `POST /api/auth/logout` before clearing localStorage.

## Key Files
- Worker: `workers/ce-sme-api/src/worker.js`
- Frontend: `exports/cf-pages-deploy/ce-sme/index.html`

## Pattern: Frontend-Backend Route Parity
When building CRUD features, always verify that every form submission endpoint exists in the router. The compliance form and onboarding list were both wired in frontend but had no matching backend routes.

## Deployment
- Worker: `ce-sme-api` via wrangler deploy
- Frontend: `purebrain-production` via cf-deploy.py
