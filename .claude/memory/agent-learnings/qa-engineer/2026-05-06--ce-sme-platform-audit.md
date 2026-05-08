# CE SME Platform QA Audit

**Date**: 2026-05-06
**Type**: operational
**Topic**: Comprehensive QA audit of CE SME platform (API + Frontend)

## Key Findings

### Critical
1. **No compliance POST endpoint** - Frontend form submits to `/api/compliance` POST but API only has GET handler. Form silently fails.
2. **Unsalted SHA-256 passwords** - `hashPassword()` uses plain SHA-256 without salt, vulnerable to rainbow table attacks.
3. **Proposal items lack user_id scoping** - `proposal_items` queried by `proposal_id` only (lines 201, 305), without joining to verify the parent proposal belongs to the requesting user.
4. **Milestones lack user_id scoping** - `milestones` queried by `project_id` only (lines 502, 580). If attacker guesses project_id, milestone data leaks. Same for milestone updates (line 547).

### High
5. **No onboarding list endpoint or frontend loader** - HR > Onboarding tab shows perpetual spinner. No `GET /api/onboarding` route exists. No `loadOnboarding()` function.
6. **Dashboard references `d.tasks?.overdue`** but API never returns `overdue` field in task stats.
7. **Session accumulation** - Sessions never cleaned up. 30-day tokens accumulate in D1 forever.
8. **Logout doesn't invalidate server session** - Only clears localStorage. Token remains valid until expiry.
9. **PDF export is stub** - Returns JSON placeholder, not actual PDF. Frontend has no handler for the PDF endpoint.

### Medium
10. **`SELECT * FROM users`** in AI generation endpoints (lines 246, 1069) returns `password_hash` to application code unnecessarily.
11. **Markdown renderer XSS risk** - `renderMarkdown()` escapes first via `esc()` then applies regex, which is safe. But the `<ul>` wrapping regex `(<li>.*<\/li>)` with `/s` flag only wraps the first list block.
12. **No DELETE endpoints for any entity** - Users cannot delete proposals, SOPs, tasks, vendors, invoices, expenses, jobs, candidates, content, etc.
13. **Status values not validated** - Update endpoints accept any string for `status` field. No enum enforcement.
14. **No rate limiting on AI generation endpoints** - Could be abused to burn Anthropic API credits.
15. **No rate limiting on auth endpoints** - Login/register vulnerable to brute force.

### Low
16. **CORS defaults to first allowed origin for unknown origins** - Not a security bug per se, but `corsHeaders` returns `allowed[0]` for unrecognized origins rather than denying.
17. **`toLocaleString()` in server-side status email** (line 594) - CF Workers may not have locale data, could produce inconsistent formatting.
18. **No pagination on list endpoints** - All queries return full result sets.
19. **`proposal_id` field on projects not validated** - Can pass any integer without verifying the proposal belongs to the user.

## Files
- API: `/home/jared/projects/AI-CIV/aether/workers/ce-sme-api/src/worker.js`
- Frontend: `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/ce-sme/index.html`
