# Social API Frontend-Backend Wiring Audit

**Date**: 2026-04-20
**Type**: operational
**Agent**: full-stack-developer

## Key Findings

### BROKEN: DELETE /api/content/:id
- Frontend `confirmDelete()` sends DELETE to `/api/content/:id`
- Backend has NO delete route or handler for content items
- Users cannot delete posts - this is the highest priority fix

### PARTIAL: Feedback System (3 endpoints missing, fallback works)
- `POST /api/content/:id/feedback` - no route (fallback: stores in routing_decision via PATCH)
- `GET /api/content/:id/feedback` - no route (fallback: reads from cached post's routing_decision)
- `PUT /api/content/:id/feedback/:feedbackId/resolve` - no route (fallback: updates routing_decision via PATCH)

### WORKING (14 features)
- Kanban drag-and-drop status change (PATCH status)
- Save Changes in edit modal (PATCH body/title/status/scheduled_at/media)
- Post Now from compose (POST /api/content)
- Post Now from modal (PATCH status+scheduled_at)
- Replace Image upload (media_base64 in PATCH, saved to R2)
- Title field save (PATCH title)
- Schedule date/time change (PATCH scheduled_at)
- Status dropdown (PATCH status)
- Character count validation (client-side only)
- Quality gate (client-side BANNED_WORDS check)
- Platform filter tabs (client-side filter)
- Search (client-side text filter)
- Calendar drag-and-drop reschedule (PATCH scheduled_at)
- Approve/Post Now by ID (PATCH status)

## Backend Architecture Notes
- All content mutations go through `handleUpdateContent()` (line 452)
- Allowed PATCH fields: body, media_refs, scheduled_at, status, rejection_reason, last_error, retry_count, routing_decision, posted_at, post_url, verification_status, performance_metrics, title
- Base64 image upload handled inline in PATCH (saves to R2, writes media_refs)
- Frontend HTML is embedded in worker.js as `FRONTEND_HTML` constant (line 102)

## Files
- Frontend: `/home/jared/projects/AI-CIV/aether/from-chy/DEPLOY-THIS-MOBILE-FIX.html`
- Backend: `/home/jared/projects/AI-CIV/aether/workers/social-api/src/worker.js`
